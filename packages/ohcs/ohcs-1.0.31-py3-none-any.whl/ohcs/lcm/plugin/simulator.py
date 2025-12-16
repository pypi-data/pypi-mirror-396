# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

"""
Simulator implementation of LifecycleManagement interface.
"""

from typing import Any, Optional


from ohcs.lcm.models import Pool, VmInfo
from ohcs.lcm.examples.DemoStore import DemoStore
from ohcs.common.utils import PluginException

_demo = DemoStore()


def _get_vm(pool: Pool, vmId: str) -> VmInfo:
    vm = _demo.get(pool.id, vmId)
    if not vm:
        raise PluginException(f"VM not found: {pool.id}/{vmId}")
    return vm


def init() -> Optional[dict[str, Any]]:
    pass


def health(pool: Pool, params: dict[str, Any]) -> dict[str, Any]:
    return _demo.get_state()


def prepare_pool(pool: Pool, params: dict[str, Any]) -> Optional[dict[str, Any]]:
    pass


def destroy_pool(pool: Pool, params: dict[str, Any]) -> None:
    _demo.remove_pool(pool.id)


def list_vms(pool: Pool, params: dict[str, Any]) -> list[VmInfo]:
    return _demo.list_vms(pool.id)


def get_vm(pool: Pool, vmId: str) -> Optional[VmInfo]:
    return _demo.get(pool.id, vmId)


def create_vm(pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
    vm = VmInfo(id=vmId, cloudId=vmId, powerState="PoweredOn")
    _demo.add(pool.id, vmId, vm)
    return vm


def delete_vm(pool: Pool, vmId: str, params: dict[str, Any]) -> None:
    _demo.remove(pool.id, vmId)


def power_on_vm(pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
    vm = _get_vm(pool, vmId)
    vm.powerState = "PoweredOn"
    _demo._save()
    return vm


def power_off_vm(pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
    vm = _get_vm(pool, vmId)
    vm.powerState = "PoweredOff"
    _demo._save()
    return vm


def restart_vm(pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
    vm = _get_vm(pool, vmId)
    vm.powerState = "PoweredOn"
    _demo._save()
    return vm


def shutdown_vm(pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
    vm = _get_vm(pool, vmId)
    vm.powerState = "PoweredOff"
    _demo._save()
    return vm


def snapshot_vm(pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
    vm = _get_vm(pool, vmId)
    current_snapshot = int(vm.snapshotId) if vm.snapshotId else 0
    vm.snapshotId = str(current_snapshot + 1)
    power_off_vm(pool, vmId, params)
    return vm


def restore_vm(pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
    vm = _get_vm(pool, vmId)
    if vm.snapshotId is None:
        raise PluginException(f"No snapshot found for VM: {pool.id}/{vmId}")
    return vm


def hibernate_vm(pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
    vm = _get_vm(pool, vmId)
    vm.powerState = "PoweredOff"
    _demo._save()
    return vm


def resize_vm(pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
    vm = _get_vm(pool, vmId)
    return vm


def _reset_simulator():
    _demo.clear()
