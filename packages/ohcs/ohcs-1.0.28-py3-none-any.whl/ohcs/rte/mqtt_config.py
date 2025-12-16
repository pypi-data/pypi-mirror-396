# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

from dataclasses import dataclass
from typing import Optional

__all__ = ["SSLConfig", "MQTTConfig"]


@dataclass
class SSLConfig:
    ca: str
    cert: Optional[str] = None
    key: Optional[str] = None
    allowWeak: bool = False
    verify: bool = False


@dataclass
class MQTTConfig:
    host: str
    consumerGroup: str
    ssl: SSLConfig
    port: int = 443
    clientId: Optional[str] = None
    sessionExpirySeconds: int = 300
    keepAliveSeconds: int = 30
    qos: int = 1
