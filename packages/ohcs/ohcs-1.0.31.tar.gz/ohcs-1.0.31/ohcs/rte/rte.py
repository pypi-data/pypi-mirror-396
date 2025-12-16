# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import logging
import sys
import traceback
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from ohcs import __version__ as VERSION
from ohcs.common.utils import OhcsSdkException, PluginException, error_details
from ohcs.common.executor import safe_invoke
from ohcs.rte.ezhub import EzHub, get_cert_cn
from ohcs.rte.mqtt_config import MQTTConfig
from ohcs.rte.protocol import RteRequest, RteResponse, _deserialize, _serialize
from ohcs.common.stats_logger import start_stats_logging, stop_stats_logging

log = logging.getLogger(__name__)


_hub_client: Optional[EzHub] = None
_instance_map: dict[str, Any] = {}

_outgoing: dict[str, Any] = {}
_incoming: dict[str, Any] = {}
_on_incoming_property: Callable[[str, Any], None] = None

_topic_reported: Optional[str] = None
_topic_desired: Optional[str] = None
_topic_request: Optional[str] = None
_topic_reply: Optional[str] = None
_topic_event: Optional[str] = None


def _on_incoming(payload: bytes):
    properties = _deserialize(payload, dict)
    removed = []
    added = []
    updated = []
    for key, value in properties.items():
        if value is None:
            if key in _incoming:
                removed.append(key)
                del _incoming[key]
                log.debug("INCOMING: -%s", key)
                if _on_incoming_property:
                    _on_incoming_property(key, None)
            continue
        if key not in _incoming:
            added.append(key)
            _incoming[key] = value
            log.debug("INCOMING: +%s=%s", key, value)
            if _on_incoming_property:
                _on_incoming_property(key, value)
            continue

        existing = _incoming[key]
        if existing != value:
            updated.append(key)
            _incoming[key] = value
            log.debug("INCOMING: *%s=%s", key, value)
            if _on_incoming_property:
                _on_incoming_property(key, value)


def _log_error(e):
    log.error("ERROR: %s", error_details(e))
    traceback.print_exc()


def _on_request(payload: bytes):
    req = _deserialize(payload, RteRequest)
    method = req.method
    log.debug("REQUEST: %s", req)
    resp = RteResponse(req.taskId, req.traceId, None)
    # GpeRequest_v0(r='dykcfr5h', c=None, d={'taskId': 'ee0d4138a7d090ce', 'service': 'rte.demo.api.MyInterface', 'args': ['mortal@1758755629803']}, method='hello')
    try:
        req.validate()

        instance = _instance_map.get(req.service)
        if not instance:
            raise Exception("Service not found: {}", req.service)

        if not hasattr(instance, method):
            raise ValueError(f"Unknown method: {instance.__name__}.{method}")
        method_obj = getattr(instance, method)
        if not callable(method_obj):
            raise ValueError(f"Method {instance.__name__}.{method} is not callable")
        timeout = getattr(method_obj, "timeout", 60)

        _sanity_report(req.taskId, req.traceId)

        task_name = f"{instance.__name__}.{method}"
        task = safe_invoke(req.taskId, task_name, timeout, method_obj, *req.args)

        def _on_complete(t):
            if t.error:
                _check_print_stack_trace(t.error)
                resp.error = {"message": error_details(t.error)}
            else:
                resp.data = t.result
                # workaround for RTE mandates data not null
                if resp.data is None:
                    resp.data = {}
            _report_response(resp)

        task.on_complete(_on_complete)

    except Exception as e:
        _log_error(e)
        resp.error = {"message": error_details(e)}
        _report_response(resp)


def _check_print_stack_trace(e):
    if not isinstance(e, Exception):
        return
    no_stack_trace_exceptions = (OhcsSdkException, PluginException, KeyboardInterrupt, SystemExit, NotImplementedError)
    if isinstance(e, no_stack_trace_exceptions):
        return

    traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)


def _report_response(resp: RteResponse):
    log.debug("RESPONSE: %s", resp)
    _hub_client.publish(_topic_reply, resp.serialize())


def _sanity_report(task_id: str, trace_id: str):
    resp = RteResponse(task_id, trace_id, None, True)
    log.debug("SANITY: %s", resp)
    _hub_client.publish(_topic_reply, resp.serialize())


def report(data: dict, force: bool = False):
    if not _hub_client:
        log.error("EzHub client not initialized")
        return

    delta = {}
    info = []
    for key, value in data.items():
        if value is None:
            if key in _outgoing:
                info.append(f"-{key}")
            else:
                if not force:
                    continue
                info.append(f"-!{key}")
        else:
            if key not in _outgoing:
                info.append(f"+{key}={value}")
            else:
                existing = _outgoing[key]
                if existing == value:
                    if not force:
                        continue
                    info.append(f"*!{key}={value}")
                else:
                    info.append(f"*{key}={value} (old={existing})")
        delta[key] = value

    msg = "OUTGOING: " + ", ".join(info)

    def on_complete(error):
        if error:
            log.error("%s, error=%s", msg, error)
            return
        log.debug(msg)
        for key, value in delta.items():
            if value is None:
                _outgoing.pop(key, None)
            else:
                _outgoing[key] = value

    _hub_client.publish(_topic_reported, _serialize(delta), wait=10, on_complete=on_complete)


def incoming():
    return dict(_incoming)


def outgoing():
    return dict(_outgoing)


def event(data: dict):
    _hub_client.publish(_topic_event, data)


def init(
    mqtt_config: MQTTConfig,
    edge_id: str,
    instance_map: dict[str, Any] = {},
    on_incoming_property: Callable[[str, Any], None] = None,
) -> EzHub:
    global _hub_client
    global _on_incoming_property
    global _instance_map
    _on_incoming_property = on_incoming_property
    _instance_map = instance_map

    ssl_config = mqtt_config.ssl
    if ssl_config:
        client_id = get_cert_cn(ssl_config.cert)
        log.info("Client certificate CN: %s", client_id)
        if mqtt_config.clientId:
            log.warning("clientId must not be specified with mTLS. Leave it empty.")
        mqtt_config.clientId = client_id
    else:
        client_id = mqtt_config.clientId
    log.info("Client ID: %s", client_id)

    global _topic_reported, _topic_desired, _topic_request, _topic_reply, _topic_event
    _topic_reported = f"rte/e/{edge_id}/c/{client_id}/reported"
    _topic_desired = f"rte/e/{edge_id}/c/{client_id}/desired"
    _topic_request = f"rte/e/{edge_id}/c/{client_id}/request"
    _topic_reply = f"rte/e/{edge_id}/c/{client_id}/reply"
    _topic_event = f"rte/e/{edge_id}/c/{client_id}/events"

    handlers: Dict[str, Callable[[bytes], Any]] = {
        _topic_desired: _on_incoming,
        _topic_request: _on_request,
    }
    _hub_client = EzHub(config=mqtt_config, handlers=handlers)
    _hub_client.start()

    # Start daily statistics logging
    start_stats_logging()

    info = {
        "version": VERSION,
        "edgeId": edge_id,
        "clientId": client_id,
        "startedAt": datetime.now().isoformat(),
    }
    report(info)
    event(
        {
            "event": "CONNECT",
            "name": "lcm-plugin",
            "version": VERSION,
            "edgeId": edge_id,
            "clientId": client_id,
        }
    )

    return _hub_client


def stop():
    global _hub_client

    # Stop statistics logging
    stop_stats_logging()

    if _hub_client:
        _hub_client.stop()
        _hub_client = None
