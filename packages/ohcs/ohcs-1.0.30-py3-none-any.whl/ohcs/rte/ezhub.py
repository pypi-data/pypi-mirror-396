# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import json
import logging
import re
import ssl
import traceback
from threading import Event
from typing import Any, Callable, Dict, List

# pylint: disable=syntax-error,no-name-in-module
from paho.mqtt.client import (  # type: ignore
    CallbackAPIVersion,
    Client,
    ConnectFlags,
    DisconnectFlags,
    MQTTErrorCode,
    MQTTMessage,
    ReasonCode,
)
from paho.mqtt.enums import MQTTProtocolVersion
from paho.mqtt.properties import Properties

from .mqtt_config import MQTTConfig

log = logging.getLogger(__name__)


def _get_mqtt_error_description(error_code: int) -> str:
    """Convert MQTT error codes to human-readable descriptions."""
    error_messages: Dict[int, str] = {
        MQTTErrorCode.MQTT_ERR_INVAL: "Invalid parameters provided",
        MQTTErrorCode.MQTT_ERR_AGAIN: "Try again later",
        MQTTErrorCode.MQTT_ERR_NOMEM: "Out of memory",
        MQTTErrorCode.MQTT_ERR_PROTOCOL: "Protocol error",
        MQTTErrorCode.MQTT_ERR_NO_CONN: "No connection",
        MQTTErrorCode.MQTT_ERR_CONN_REFUSED: "Connection refused",
        MQTTErrorCode.MQTT_ERR_NOT_FOUND: "Not found",
        MQTTErrorCode.MQTT_ERR_CONN_LOST: "Connection lost",
        MQTTErrorCode.MQTT_ERR_TLS: "TLS error",
        MQTTErrorCode.MQTT_ERR_PAYLOAD_SIZE: "Payload too large",
        MQTTErrorCode.MQTT_ERR_NOT_SUPPORTED: "Not supported",
        MQTTErrorCode.MQTT_ERR_AUTH: "Authentication error",
        MQTTErrorCode.MQTT_ERR_ACL_DENIED: "ACL denied",
        MQTTErrorCode.MQTT_ERR_UNKNOWN: "Unknown error",
        MQTTErrorCode.MQTT_ERR_ERRNO: "System error",
    }
    return error_messages.get(error_code, f"Unknown error code: {error_code}")


def get_cert_cn(client_cert: str) -> str:
    # Print the CN (Common Name) of the client certificate
    try:
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend

        with open(client_cert, "rb") as f:
            cert_data = f.read()
        cert = x509.load_pem_x509_certificate(cert_data, default_backend())
        subject = cert.subject
        cn = subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
        return str(cn)
    except Exception as e:
        raise Exception("Failed to extract CN from client certificate: {}", e)


class EzHub:
    def __init__(self, config: MQTTConfig, handlers: Dict[str, Callable[[bytes], Any]] = None):
        self._config = config
        self._client: Client = None
        self._topic_handler_map: Dict[str, Callable[[bytes], Any]] = {}
        self._flag_connect_state_changed = Event()
        self._flag_init_subscription_completed = Event()

        self._init_handlers(handlers)

    def _init_handlers(self, handlers: Dict[str, Callable[[bytes], Any]]):
        self._handlers = {}
        self._regex_handlers = {}

        if not handlers:
            return
        for topic, handler in handlers.items():
            self._handlers[topic] = handler

            # if the topic is a group topic, e.g. "$share/group1/topic", convert it to non-group topic, "/topic"
            if topic.startswith("$share/"):
                # Remove "$share/group/" prefix
                topic = topic.split("/", 2)[-1]

            if "+" in topic:
                regex = topic.replace("+", ".+?")
                self._regex_handlers[regex] = handler
            else:
                if topic not in self._handlers:
                    self._handlers[topic] = handler

    def _find_handler(self, topic: str) -> Callable[[bytes], Any]:
        h = self._handlers.get(topic)
        if h:
            return h
        for regex, handler in self._regex_handlers.items():
            if re.match(regex, topic):
                return handler
        return None

    def _on_connect(
        self,
        _client: Client,
        _userdata,
        connect_flags: ConnectFlags,
        reason_code: ReasonCode,
        properties: Properties,
    ):
        log.info(
            f"on_connect: reason_code={reason_code.value}, description={reason_code}, connect_flags={connect_flags}"
        )
        if properties and not properties.isEmpty():
            log.debug("Connect properties: %s", properties)
        self._flag_connect_state_changed.set()
        self._subscribe()

    def _on_connect_fail(self, _client: Client, _userdata):
        log.warning("on_connect_fail")
        self._flag_connect_state_changed.set()

    def _on_disconnect(
        self,
        _client: Client,
        _userdata,
        disconnect_flags: DisconnectFlags,
        reason_code: ReasonCode,
        properties: Properties,
    ):
        log_level = log.error if reason_code.is_failure else log.info

        log_level(
            f"on_disconnect: reason_code={reason_code.value}, description='{reason_code}', disconnect_flags={disconnect_flags}"
        )

        if properties and not properties.isEmpty():
            log.debug("Disconnect properties: %s", properties)

        self._flag_connect_state_changed.set()

    def _on_subscribe(
        self,
        _client: Client,
        _userdata,
        mid,
        reason_code_list: List[ReasonCode],
        properties: Properties,
    ):
        log.info(f"on_subscribe: mid={mid}, reason_codes={reason_code_list}")

        if properties and not properties.isEmpty():
            log.debug("Subscribe properties: %s", properties)

        self._flag_init_subscription_completed.set()

    def _on_unsubscribe(
        self,
        _client: Client,
        _userdata,
        mid,
        reason_code_list: List[ReasonCode],
        properties: Properties,
    ):
        log.info(f"on_unsubscribe: mid={mid}, rc={reason_code_list}")
        if properties and not properties.isEmpty():
            log.debug("Unsubscribe properties: %s", properties)

    def _on_publish(
        self,
        _client: Client,
        _userdata,
        mid,
        reason_code: ReasonCode,
        properties: Properties,
    ):
        log.debug(f"on_publish: mid={mid}, rc={reason_code}")
        if properties and not properties.isEmpty():
            log.debug("Publish properties: %s", properties)

    def _on_message(self, _client: Client, _userdata, msg: MQTTMessage):
        log_msg = f"_on_message: topic={msg.topic}, QoS={msg.qos}, timestamp={msg.timestamp}, dup={msg.dup}, retain={msg.retain}, mid={msg.mid}, info={msg.info}, payload length={len(msg.payload)}"
        log.debug(log_msg)

        handler = self._find_handler(msg.topic)
        if not handler:
            log.error(f"No handler registered for topic: {msg.topic}")
            return

        try:
            handler(msg.payload)
        except Exception as e:
            log.error("Unexpected error in custom handler: %s", e)
            traceback.print_exc()

    def _create_client(self):
        log.info(f"MQTT server: {self._config.host}:{self._config.port}")
        ssl_config = self._config.ssl
        if ssl_config:
            ca_certs = self._config.ssl.ca
            client_cert = self._config.ssl.cert
            client_key = self._config.ssl.key
            log.debug("ca: " + ca_certs)
            log.debug("cert: " + client_cert)
            log.debug("key: " + client_key)
        client_id = self._config.clientId

        self._client = Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=client_id,
            protocol=MQTTProtocolVersion.MQTTv5,
        )

        if ssl_config:
            if ssl_config.allowWeak:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.set_ciphers("ALL:@SECLEVEL=0")
                if ssl_config.verify:
                    context.verify_mode = ssl.CERT_REQUIRED
                else:
                    context.verify_mode = ssl.CERT_NONE
                    context.check_hostname = False
                context.load_verify_locations(cafile=ca_certs)
                context.load_cert_chain(certfile=client_cert, keyfile=client_key)
                self._client.tls_set_context(context)
            else:
                self._client.tls_set(
                    ca_certs=ca_certs,
                    certfile=client_cert,
                    keyfile=client_key,
                    cert_reqs=ssl.CERT_REQUIRED if ssl_config.verify else ssl.CERT_NONE,
                )

        self._client.on_connect = self._on_connect
        self._client.on_connect_fail = self._on_connect_fail
        self._client.on_disconnect = self._on_disconnect
        self._client.on_subscribe = self._on_subscribe
        self._client.on_unsubscribe = self._on_unsubscribe
        self._client.on_publish = self._on_publish
        self._client.on_message = self._on_message

    def _connect(self):
        host = self._config.host
        port = self._config.port
        log.info(f"Connecting to MQTT broker at {host}:{port}...")

        code = self._client.connect(host=host, port=port, keepalive=self._config.keepAliveSeconds)
        if code != MQTTErrorCode.MQTT_ERR_SUCCESS:
            error_desc = _get_mqtt_error_description(code)
            msg = f"Failed to initiate MQTT connection: {code} ({error_desc})"
            log.error(msg)
            log.error(f"Connection details - Host: {host}, Port: {port}, Keepalive: {self._config.keepAliveSeconds}")
            raise Exception(msg)

        rc = self._client.loop_start()
        try:
            if rc != MQTTErrorCode.MQTT_ERR_SUCCESS:
                error_desc = _get_mqtt_error_description(rc)
                raise Exception(f"Failed to start MQTT loop: {rc} ({error_desc})")

            self._flag_connect_state_changed.wait(30)
            if not self._client.is_connected:
                raise Exception("Connection failed - client is not connected after connection attempt")
            log.info("MQTT connection established successfully")
        except Exception as e:
            log.error("Connection failed: %s", e)
            self._client.loop_stop()
            raise e

    def _subscribe(self):
        if not self._handlers:
            return

        subscription_list = []
        for topic, handler in self._handlers.items():
            qos = self._config.qos
            subscription_list.append((topic, qos))
            self._topic_handler_map[topic] = handler

        result, mid = self._client.subscribe(subscription_list)
        if result == MQTTErrorCode.MQTT_ERR_SUCCESS:
            log.info(f"Subscribing to topics: {subscription_list}. result={result}, mid={mid}")
        else:
            error_desc = _get_mqtt_error_description(result)
            msg = f"Subscribe failed for topic '{topic}': code={result} ({error_desc}), mid={mid}. error_desc={error_desc}"
            log.error("%s", msg)
            raise Exception(msg)

    def start(self):
        self._create_client()
        self._connect()

        # must wait here, not in anything of the callback, which will block the event loop.
        self._flag_init_subscription_completed.wait(30)
        if not self._flag_init_subscription_completed.is_set():
            raise Exception("Subscription failed - client is not subscribed after subscription attempt")

    def stop(self):
        log.info("Stopping client")
        self._client.loop_stop()
        self._client.disconnect()
        self._client = None

    def publish(
        self,
        topic: str,
        payload,
        wait: int = 0,
        on_complete: Callable[[str], Any] = None,
    ):
        if not self._client:
            log.info("Client not initialized, creating and connecting...")
            self._create_client()
            self._connect()
        if not self._client.is_connected:
            raise Exception("Client not connected")

        if isinstance(payload, dict) or isinstance(payload, list):
            payload = json.dumps(payload).encode()

        msg = f">> '{topic}': payload length={len(payload)}, QoS={self._config.qos}, wait={wait}"
        try:
            msg_info = self._client.publish(topic=topic, payload=payload, qos=self._config.qos, retain=False)
        except Exception as e:
            log.error("Publish failed: %s", e)
            raise e

        if msg_info.rc == MQTTErrorCode.MQTT_ERR_SUCCESS:
            msg = msg + f", mid={msg_info.mid}, rc={msg_info.rc}"
            log.debug(msg)
        else:
            error_desc = _get_mqtt_error_description(msg_info.rc)
            msg = msg + f", mid={msg_info.mid}, rc={msg_info.rc}, error_desc={error_desc}"
            log.error("%s", msg)

        if wait:
            err_msg = None
            try:
                msg_info.wait_for_publish(wait)
                if not msg_info.is_published():
                    raise Exception("Publish not confirmed within wait time")
                if msg_info.rc != MQTTErrorCode.MQTT_ERR_SUCCESS:
                    err_msg = _get_mqtt_error_description(msg_info.rc)
            except Exception as e:
                err_msg = str(e)
            if on_complete:
                on_complete(err_msg)
            else:
                if err_msg:
                    log.error("Publish wait failed: %s", err_msg)

        return msg_info
