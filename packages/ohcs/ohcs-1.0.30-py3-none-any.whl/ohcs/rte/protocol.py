# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import dataclasses
import json
import logging
import zlib
from dataclasses import asdict, dataclass
from typing import Any

log = logging.getLogger(__name__)


def _serialize(o: Any) -> bytes:
    if dataclasses.is_dataclass(o) and not isinstance(o, type):
        o = {k: v for k, v in asdict(o).items() if v is not None and v != 0}

    text = json.dumps(o)
    log.debug(">> %s", text)
    return zlib.compress(text.encode())


def _deserialize(data: bytes, class_type):
    text = zlib.decompress(data).decode()
    log.debug("<< %s", text)
    try:
        data_dict = json.loads(text)
        if class_type is dict:
            return data_dict
        return class_type(**data_dict)
    except Exception as e:
        raise Exception("Fail parsing RTE data. Text: " + text) from e


"""
{
    "taskId": "db234b2c00356948",
    "traceId": "",
    "service": "com.vmware.horizon.sg.common.rte.RtePythonInteroperabilityTest$XpeSim",
    "method": "createVm",
    "args": [
        {
            "@class": "com.vmware.horizon.sg.common.rte.RtePythonInteroperabilityTest$Template",
            "id": "t1"
        },
        {
            "@class": "com.vmware.horizon.sg.common.rte.RtePythonInteroperabilityTest$VmSpec",
            "id": "vm1"
        },
        "string value",
        1,
        True
    ]
}
"""


@dataclass
class RteRequest:
    taskId: str
    traceId: str = None
    service: str = None
    method: str = None
    args: list = None

    def validate(self):
        if not self.taskId:
            raise Exception("Missing taskId")
        if not self.service:
            raise Exception("Missing service")
        if not self.method:
            raise Exception("Missing method")
        if self.method.startswith("_"):
            raise Exception(f"Invalid method name: {self.method}")

    def serialize(self) -> bytes:
        return _serialize(self)

    @staticmethod
    def deserialize(data: bytes) -> "RteRequest":
        return _deserialize(data, RteRequest)

    def _str_fields(self):
        return ", ".join(f"{k}={v!r}" for k, v in asdict(self).items() if v is not None)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._str_fields()})"

    def __str__(self):
        return f"{self.__class__.__name__}({self._str_fields()})"


@dataclass
class RteResponse:
    taskId: str
    traceId: str
    data: Any = None
    partial: bool = False
    error: dict = None

    def serialize(self) -> bytes:
        self.data = _adapt_to_jackson_typed_map(self.data)
        self.error = _adapt_to_jackson_typed_map(self.error)
        return _serialize(self)

    @staticmethod
    def deserialize(data: bytes) -> "RteResponse":
        resp = _deserialize(data, RteResponse)

        _adapt_to_jackson_typed_array(resp)
        return resp

    def _str_fields(self):
        return ", ".join(f"{k}={v!r}" for k, v in asdict(self).items() if v is not None)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._str_fields()})"

    def __str__(self):
        return f"{self.__class__.__name__}({self._str_fields()})"


def _adapt_to_jackson_typed_map(data):
    if data is None:
        return

    if isinstance(data, dict):
        if "@class" in data:
            return data
        _class = data.pop("_class", None)
        if _class:
            data["@class"] = _class
        else:
            data["@class"] = "java.util.HashMap"

        for k in list(data.keys()):
            v = data[k]
            if v is None:
                data.pop(k)
                continue
            data[k] = _adapt_to_jackson_typed_map(v)
        return data

    if isinstance(data, list):
        for i in range(len(data)):
            data[i] = _adapt_to_jackson_typed_map(data[i])

    if dataclasses.is_dataclass(data):
        data = vars(data).copy()
        return _adapt_to_jackson_typed_map(data)
    return data


def _adapt_to_jackson_typed_array(resp):
    data = resp.data
    # workaround jackson serialization of typed array.
    # e.g. ["[Lcom.vmware.horizon.sg.common.rte.XpeSim$VmInfo;",[]]
    if not data:
        return
    if not isinstance(data, list):
        return
    if len(data) != 2:
        return
    v0 = data[0]
    v1 = data[1]
    if not isinstance(v0, str):
        return
    if not v0.startswith("[L"):
        return
    if not isinstance(v1, list):
        return
    resp.data = v1
