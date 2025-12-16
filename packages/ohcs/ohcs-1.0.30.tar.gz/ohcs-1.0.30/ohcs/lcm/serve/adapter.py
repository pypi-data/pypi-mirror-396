# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import builtins
import logging
import traceback
from dataclasses import fields
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Callable, Optional, Type, TypeVar

from yumako.lru import LRUDict

from ohcs.lcm.serve import factory
from ohcs.lcm.models import Pool, LifecycleManagement, VmInfo
from ohcs.common.utils import error_details, OhcsSdkException, PluginException

log = logging.getLogger(__name__)

_pool_cache = LRUDict[str, dict](capacity=500)

T = TypeVar("T")

# Color for KOP (Key Operation) log messages
KOP_COLOR = "magenta"


def _need_error_traceback(e):
    for type in [NotImplementedError, TimeoutError, OhcsSdkException, PluginException]:
        if isinstance(e, type):
            return False
    return True


def _check_optional(provider, name: str):
    if not hasattr(provider, name):
        raise NotImplementedError(
            f"{name} is not implemented in {provider.__name__}. This capability is optional so it's OK."
        )  # type: ignore[attr-defined]


def _fix_vm_info(vm: VmInfo) -> VmInfo:
    if vm is None:
        return None
    vm._class = "com.vmware.horizon.sg.clouddriver.base.model.VmInfo"  # type: ignore[attr-defined]
    return vm


def _build_kop_path(operation_name: str, args: tuple, kwargs: dict) -> str:
    """Extract identifiers from arguments and build KOP path for logging.

    Args:
        operation_name: Name of the operation (function name)
        args: Positional arguments from the wrapped function
        kwargs: Keyword arguments from the wrapped function

    Returns:
        KOP path string (e.g., "KOP/create/pool123/vm456")
    """
    # Extract pool and get its id
    pool = args[0] if args else kwargs.get("pool")
    pool_id = pool["id"]

    # Check if second parameter contains vmId
    vmId = None
    if len(args) > 1:
        second_arg = args[1]
        if isinstance(second_arg, str):
            # Second parameter is vmId directly
            vmId = second_arg
        elif isinstance(second_arg, dict) and "vmId" in second_arg:
            # Second parameter is spec dict containing vmId
            vmId = second_arg["vmId"]
    elif "vmId" in kwargs:
        vmId = kwargs["vmId"]
    elif "spec" in kwargs and isinstance(kwargs["spec"], dict):
        vmId = kwargs["spec"].get("vmId")

    # Build and return KOP path
    kop_path = f"KOP/{operation_name}/{pool_id}"
    if vmId:
        kop_path += f"/{vmId}"
    return kop_path


def kop_logger(func: Callable) -> Callable:
    """Decorator that adds KOP logging and error handling to lifecycle management functions.

    Automatically logs:
    - Start of operation with KOP path
    - Successful completion
    - Errors with details

    Expects first parameter to be 'pool' dict with 'id' key.
    If second parameter is 'vmId' (string), it will be included in the KOP path.
    If second parameter is 'spec' (dict with 'vmId' key), vmId will be extracted from it.
    """
    operation_name = func.__name__
    is_async = iscoroutinefunction(func)

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        kop_path = _build_kop_path(operation_name, args, kwargs)

        log.info(f"<{KOP_COLOR}>{kop_path}</{KOP_COLOR}> start")
        try:
            result = await func(*args, **kwargs)
            log.info(f"<{KOP_COLOR}>{kop_path}</{KOP_COLOR}> success")
            return result
        except Exception as e:
            log.error(f"{kop_path} error: {error_details(e)}")
            if _need_error_traceback(e):
                traceback.print_exc()
            raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        kop_path = _build_kop_path(operation_name, args, kwargs)

        log.info(f"<{KOP_COLOR}>{kop_path}</{KOP_COLOR}> start")
        try:
            result = func(*args, **kwargs)
            log.info(f"<{KOP_COLOR}>{kop_path}</{KOP_COLOR}> success")
            return result
        except Exception as e:
            log.error(f"{kop_path} error: {error_details(e)}")
            if _need_error_traceback(e):
                traceback.print_exc()
            raise

    return async_wrapper if is_async else sync_wrapper


def _dict_to_dataclass(data: dict, dataclass_type: Type[T]) -> T:
    field_names = {f.name for f in fields(dataclass_type)}  # type: ignore[arg-type]
    filtered_data = {k: data.get(k) for k in field_names}
    return dataclass_type(**filtered_data)


@kop_logger
def prepare(pool: dict, params: dict[str, Any]) -> Optional[dict[str, Any]]:
    provider, pool_obj = _handle_pool(pool)
    extension_name = pool_obj.extensionName or "lcm_plugin"
    log.info(f"Pool ID: {pool_obj.id}, name: {pool_obj.name}, extension: {extension_name}")
    return provider.prepare_pool(pool_obj, params)


@kop_logger
def destroy(pool: dict, params: dict[str, Any]) -> None:
    provider, tmpl = _handle_pool(pool)
    provider.destroy_pool(tmpl, params)


@kop_logger
def list(pool: dict, params: dict[str, Any]) -> builtins.list[VmInfo]:
    provider, tmpl = _handle_pool(pool)
    ret = provider.list_vms(tmpl, params)
    return builtins.list(map(_fix_vm_info, ret))


@kop_logger
def create(pool: dict, vmId: str, params: dict[str, Any]) -> VmInfo:
    provider, tmpl = _handle_pool(pool)
    vm_info = provider.create_vm(tmpl, vmId, params)
    return _fix_vm_info(vm_info)


@kop_logger
def delete(pool: dict, vmId: str, params: dict[str, Any]) -> None:
    provider, tmpl = _handle_pool(pool)
    return provider.delete_vm(tmpl, vmId, params)


@kop_logger
def powerOn(pool: dict, vmId: str, params: dict[str, Any]) -> VmInfo:
    provider, tmpl = _handle_pool(pool)
    vm_info = provider.power_on_vm(tmpl, vmId, params)
    return _fix_vm_info(vm_info)


@kop_logger
def powerOff(pool: dict, vmId: str, params: dict[str, Any]) -> VmInfo:
    provider, tmpl = _handle_pool(pool)
    vm_info = provider.power_off_vm(tmpl, vmId, params)
    return _fix_vm_info(vm_info)


@kop_logger
def shutdown(pool: dict, vmId: str, params: dict[str, Any]) -> VmInfo:
    provider, tmpl = _handle_pool(pool)
    vm_info = provider.shutdown_vm(tmpl, vmId, params)
    return _fix_vm_info(vm_info)


@kop_logger
def restart(pool: dict, vmId: str, params: dict[str, Any]) -> VmInfo:
    provider, tmpl = _handle_pool(pool)
    _check_optional(provider, "restart_vm")
    vm_info = provider.restart_vm(tmpl, vmId, params)
    return _fix_vm_info(vm_info)


@kop_logger
def snapshot(pool: dict, vmId: str, params: dict[str, Any]) -> VmInfo:
    provider, tmpl = _handle_pool(pool)
    _check_optional(provider, "snapshot_vm")
    vm_info = provider.snapshot_vm(tmpl, vmId, params)
    return _fix_vm_info(vm_info)


@kop_logger
def restore(pool: dict, vmId: str, params: dict[str, Any]) -> VmInfo:
    provider, tmpl = _handle_pool(pool)
    _check_optional(provider, "restore_vm")
    vm_info = provider.restore_vm(tmpl, vmId, params)
    return _fix_vm_info(vm_info)


@kop_logger
def hibernate(pool: dict, vmId: str, params: dict[str, Any]) -> VmInfo:
    provider, tmpl = _handle_pool(pool)
    _check_optional(provider, "hibernate_vm")
    vm_info = provider.hibernate_vm(tmpl, vmId, params)
    return _fix_vm_info(vm_info)


@kop_logger
def get(pool: dict, vmId: str) -> Optional[VmInfo]:
    provider, tmpl = _handle_pool(pool)
    vm_info = provider.get_vm(tmpl, vmId)
    if vm_info is None:
        return None
    return _fix_vm_info(vm_info)


@kop_logger
def health(pool: dict, params: dict[str, Any]) -> dict[str, Any]:
    provider, tmpl = _handle_pool(pool)
    return provider.health(tmpl, params)


def _handle_pool(data: dict) -> tuple[LifecycleManagement, Pool]:
    pool_id = data["id"]
    existing = _pool_cache.get(pool_id)
    if existing:
        existing.update(data)
        data = existing
    else:
        _pool_cache[pool_id] = data

    tmpl = _dict_to_dataclass(data, Pool)

    if not tmpl.extensionName:
        plugin_name = "lcm_plugin"
    else:
        plugin_name = tmpl.extensionName

    provider = factory.get_lifecycle_manager(plugin_name)
    return provider, tmpl


# Pool operations
health.timeout = 60  # type: ignore[attr-defined]
prepare.timeout = 600  # type: ignore[attr-defined]
destroy.timeout = 1200  # type: ignore[attr-defined]
list.timeout = 60  # type: ignore[attr-defined]

# VM operations - required
get.timeout = 60  # type: ignore[attr-defined]
create.timeout = 1800  # type: ignore[attr-defined]
delete.timeout = 300  # type: ignore[attr-defined]
powerOn.timeout = 120  # type: ignore[attr-defined]
powerOff.timeout = 120  # type: ignore[attr-defined]
shutdown.timeout = 120  # type: ignore[attr-defined]

# VM operations - optional
restart.timeout = 120  # type: ignore[attr-defined]
snapshot.timeout = 120  # type: ignore[attr-defined]
restore.timeout = 120  # type: ignore[attr-defined]
hibernate.timeout = 120  # type: ignore[attr-defined]
