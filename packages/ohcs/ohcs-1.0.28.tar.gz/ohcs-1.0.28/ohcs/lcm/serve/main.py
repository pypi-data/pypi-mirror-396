# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import atexit
import logging
import time
from datetime import datetime
from datetime import timezone
from typing import Any, Optional

import ohcs.lcm.serve.adapter as adapter
import ohcs.lcm.serve.factory as factory
from ohcs.lcm.config import load_config
from ohcs.common.logging_config import setup_logging
from ohcs.common import stats
from ohcs.rte import rte

log = logging.getLogger(__name__)


def _on_incoming_property(key: str, value: Any):
    log.info(f"_on_incoming_property: {key}={value}")


_rte_cleanup_done = False


def _cleanup_rte():
    """Cleanup RTE resources on exit"""
    global _rte_cleanup_done

    if _rte_cleanup_done:
        return

    _rte_cleanup_done = True

    try:
        rte.stop()
        log.info("RTE stopped")
    except Exception as e:
        log.warning(f"Error stopping RTE: {e}")


def serve(config_file: Optional[str] = None):
    stats.set("start_time_utc", datetime.now(timezone.utc).isoformat())
    try:
        config = load_config(config_file)
    except FileNotFoundError as e:
        log.error(f"Configuration file not found: {e}")
        return

    log.info("--------------------------------")
    log.info("ohcs.lcm start")
    log.info("--------------------------------")

    setup_logging(config.log)

    instance_map = {"com.vmware.horizon.sg.clouddriver.impl.edgeproxy.RteEdgeProxy": adapter}

    factory.init(config.plugin.path, config.plugin.name)

    rte.init(
        mqtt_config=config.mqtt,
        edge_id=config.hcs.edgeId,
        instance_map=instance_map,
        on_incoming_property=_on_incoming_property,
    )

    # Register cleanup for RTE
    atexit.register(_cleanup_rte)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("KeyboardInterrupt received")
    except Exception as e:
        log.error(f"Unexpected error in serve loop: {e}")
        raise
    finally:
        _cleanup_rte()
        log.info("ohcs.lcm exit")
