# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml
from ohcs.common.logging_config import LogConfig

from ohcs.rte.mqtt_config import MQTTConfig, SSLConfig

log = logging.getLogger(__name__)


@dataclass
class HCSConfig:
    orgId: str
    providerId: str
    edgeId: str


@dataclass
class PluginConfig:
    path: str
    name: str


@dataclass
class Config:
    mqtt: MQTTConfig
    hcs: HCSConfig
    plugin: PluginConfig
    clientId: Optional[str] = None
    log: LogConfig = None


def _from_dict(cls, data: dict, **overrides):
    filtered_data = {k: v for k, v in data.items() if k in data}
    return cls(**{**filtered_data, **overrides})


def load_config(file_path: Optional[str] = None, log_path: bool = True) -> Config:
    if file_path is None:
        file_path = "config.yml"

    config_path = Path(file_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path.absolute()}")

    if log_path:
        log.info(f"Config file: {config_path.absolute()}")

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    ssl_config = _from_dict(SSLConfig, config_data["mqtt"]["ssl"])
    mqtt_config = _from_dict(MQTTConfig, config_data["mqtt"], ssl=ssl_config)
    log_config = _from_dict(LogConfig, config_data["log"])
    hcs_config = _from_dict(HCSConfig, config_data["hcs"])
    plugin_config = _from_dict(PluginConfig, config_data["plugin"])

    return _from_dict(Config, config_data, mqtt=mqtt_config, log=log_config, hcs=hcs_config, plugin=plugin_config)


def save_config(config: Config, file_path: str):
    json_config = json.dumps(config, default=vars)
    config_data = json.loads(json_config)
    with open(file_path, "w") as file:
        yaml.safe_dump(config_data, file)
