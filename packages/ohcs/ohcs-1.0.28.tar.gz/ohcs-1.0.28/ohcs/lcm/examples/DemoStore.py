# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import json
import logging
import threading
from pathlib import Path
from typing import Dict, Optional

from ohcs.lcm.models import VmInfo

log = logging.getLogger(__name__)


class DemoStore:
    def __init__(self, storage_file: Optional[str] = ".demo-store"):
        self._storage_file = None if not storage_file else Path(storage_file)
        self._storage: Dict[str, Dict[str, VmInfo]] = {}
        self._lock = threading.Lock()
        self._load()

    def _load(self) -> None:
        if not self._storage_file or not self._storage_file.exists():
            return

        try:
            with open(self._storage_file, "r") as f:
                data = json.load(f)

            for pool_id, vms in data.items():
                self._storage[pool_id] = {}
                for vm_id, vm_data in vms.items():
                    self._storage[pool_id][vm_id] = VmInfo(**vm_data)

            log.info(f"Loaded {len(self._storage)} pools and {sum(len(vms) for vms in self._storage.values())} VMs")
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            log.error(f"Failed to load storage: {e}")
            self._storage = {}

    def _save(self) -> None:
        if not self._storage_file:
            return
        try:

            def _serialize(obj):
                if hasattr(obj, "__dict__"):
                    return {k: v for k, v in vars(obj).items() if not k.startswith("_")}
                return obj

            with open(self._storage_file, "w") as f:
                json.dump(self._storage, f, indent=4, default=_serialize)
        except (OSError, TypeError) as e:
            log.error(f"Failed to save storage: {e}")

    def add(self, pool_id: str, vm_id: str, vm_info: VmInfo) -> None:
        with self._lock:
            if pool_id not in self._storage:
                self._storage[pool_id] = {}
            self._storage[pool_id][vm_id] = vm_info
            self._save()

    def remove(self, pool_id: str, vm_id: str) -> Optional[VmInfo]:
        with self._lock:
            if pool_id not in self._storage or vm_id not in self._storage[pool_id]:
                return None
            vm_info = self._storage[pool_id].pop(vm_id)
            self._save()
            return vm_info

    def remove_pool(self, pool_id: str) -> None:
        with self._lock:
            if pool_id in self._storage:
                del self._storage[pool_id]
                self._save()

    def get(self, pool_id: str, vm_id: str) -> Optional[VmInfo]:
        with self._lock:
            if pool_id not in self._storage or vm_id not in self._storage[pool_id]:
                return None
            return self._storage[pool_id][vm_id]

    def list_vms(self, pool_id: str) -> list[VmInfo]:
        with self._lock:
            if pool_id not in self._storage:
                return []
            return list(self._storage[pool_id].values())

    def has_pool(self, pool_id: str) -> bool:
        with self._lock:
            return pool_id in self._storage

    def has_vm(self, pool_id: str, vm_id: str) -> bool:
        with self._lock:
            return pool_id in self._storage and vm_id in self._storage[pool_id]

    def get_state(self) -> dict:
        with self._lock:
            total_vm_count = sum(len(vms) for vms in self._storage.values())
            return {
                "pools": dict(self._storage),
                "vms": total_vm_count,
            }

    def clear(self) -> None:
        with self._lock:
            self._storage.clear()
            self._save()
