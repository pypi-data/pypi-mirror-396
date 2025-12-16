import logging
import time
from typing import Any, Optional
from ohcs.lcm.models import Pool, VmInfo
from ohcs.lcm.examples.DemoStore import DemoStore
from ohcs.common.utils import PluginException

log = logging.getLogger(__name__)

# -------- Demo Helpers --------

_demo = DemoStore()


def _get_vm(pool: Pool, vmId: str) -> VmInfo:
    vm = _demo.get(pool.id, vmId)
    if not vm:
        raise PluginException(f"VM not found: {pool.id}/{vmId}")
    return vm


# -------- Global functions --------


def init() -> Optional[dict[str, Any]]:
    """Initialize the lifecycle management plugin implementation.

    This method is called once during the initialization phase to set up
    any required resources, connections, or state.

    Returns:
        Optional[dict[str, Any]]: Initialization metadata or None if no metadata is needed.

    Raises:
        Exception: If the operation fails.
    """

    # TODO: this is a stub, and should be replaced with the actual implementation

    log.info("Initializing demo plugin")
    return None


# -------- Pool management functions --------


def health(pool: Pool, params: dict[str, Any]) -> dict[str, Any]:
    """Check the health status of the pool and its infrastructure.

    This method performs health checks on the pool's infrastructure and
    returns status information.

    Args:
        pool: The pool to check.
        params: Additional parameters for the operation.

    Returns:
        dict[str, Any]: Provider-specific health status information.

    Raises:
        Exception: If the operation fails.
    """

    # TODO: this is a stub, and should be replaced with the actual implementation

    return {
        "status": "Healthy",
    }.update(_demo.get_state())


def prepare_pool(pool: Pool, params: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Prepare a pool for use.

    This method performs any necessary setup or validation for a pool
    before VMs can be created from it. This may include provisioning infrastructure,
    validating configurations, or preparing cloud resources.

    This function should only return after the operation is fully completed.

    Args:
        pool: The pool.
        params: Additional parameters for the operation.

    Returns:
        Optional[dict[str, Any]]: Provider-specific results for the operation or None if no results are needed.

    Raises:
        Exception: If the operation fails.
    """

    # TODO: this is a stub, and should be replaced with the actual implementation
    log.info(f"Preparing pool: {pool.name} ({pool.id}).")
    log.info(f"  customVarariables = {pool.customVariables}")
    log.info(f"  customTemplate    = {pool.customTemplate}")
    return None


def destroy_pool(pool: Pool, params: dict[str, Any]) -> None:
    """Destroy a pool and clean up associated resources.

    This method removes the pool and cleans up any infrastructure or resources
    that were provisioned for it. This method must also delete all VMs.

    This function should only return after the operation is fully completed.

    Args:
        pool: The pool.
        params: Additional parameters for the operation.

    Returns:
        None: The operation does not return a value.

    Raises:
        Exception: If the operation fails.
    """

    # TODO: this is a stub, and should be replaced with the actual implementation

    _demo.remove_pool(pool.id)


def list_vms(pool: Pool, params: dict[str, Any]) -> list[VmInfo]:
    """List all virtual machines associated with a pool.

    Args:
        pool: The pool.
        params: Additional parameters for the operation.

    Returns:
        list[VmInfo]: A list of VM information objects for all VMs in the pool.

    Raises:
        Exception: If the operation fails.
    """

    # TODO: this is a stub, and should be replaced with the actual implementation

    return _demo.list_vms(pool.id)


# -------- VM management functions (required) --------


def get_vm(pool: Pool, vmId: str) -> Optional[VmInfo]:
    """Get information about a virtual machine.

    Args:
        pool: The pool the VM belongs to.
        vmId: The unique identifier of the VM.

    Returns:
        VmInfo: Information about the VM.
        None: If the VM does not exist.

    Raises:
        Exception: If the operation fails.
    """

    # TODO: this is a stub, and should be replaced with the actual implementation

    return _get_vm(pool, vmId)


def create_vm(pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
    """Create a new virtual machine from a pool.

    This method provisions a new VM based on the given pool and specification.
    The created VM must have the specified machine name (computer name) as vmId.
    The created VM must have the LCM custom data injected into the VM.
    The created VM must be in powered-on state.

    This function should only return after the operation is fully completed.

    Args:
        pool: The pool to use.
        vmId: The unique identifier of the VM.
        params: Additional parameters for the operation.

    Returns:
        VmInfo: Information about the newly created VM.

    Raises:
        Exception: If VM creation fails.
    """

    # TODO: this is a stub, and should be replaced with the actual implementation

    vm = VmInfo(id=vmId, cloudId=vmId, powerState="PoweredOn")

    # With real deployment, the following custom_data must be properly placed in the guest OS as:
    #   file: C:\AzureData\CustomData.bin
    #   Owner of the file: SYSTEM
    custom_data = params["customData"]  # noqa: F841

    # simulate long running operation
    time.sleep(10)

    _demo.add(pool.id, vmId, vm)
    return vm


def delete_vm(pool: Pool, vmId: str, params: dict[str, Any]) -> None:
    """Delete a virtual machine.

    This method removes a VM and cleans up its associated resources.
    The VM must be deleted from the infrastructure provider.

    This function should only return after the operation is fully completed.

    Args:
        pool: The pool the VM belongs to.
        vmId: The unique identifier of the VM.
        params: Additional parameters for the operation.

    Returns:
        None: The operation does not return a value.

    Raises:
        Exception: If the operation fails.
    """

    # TODO: this is a stub, and should be replaced with the actual implementation

    _demo.remove(pool.id, vmId)


def power_on_vm(pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
    """Power on a virtual machine.

    This function should only return after the operation is fully completed, and the VM is in powered-on state.

    Args:
        pool: The pool the VM belongs to.
        vmId: The unique identifier of the VM.
        params: Additional parameters for the operation.

    Returns:
        VmInfo: Updated information about the VM after the operation.

    Raises:
        Exception: If the operation fails.
    """

    # TODO: this is a stub, and should be replaced with the actual implementation

    vm = _get_vm(pool, vmId)
    vm.powerState = "PoweredOn"
    return vm


def power_off_vm(pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
    """Power off a virtual machine forcefully, similar to pulling the power plug.
    For a graceful shutdown, use shutdown_vm instead.

    This function should only return after the operation is fully completed, and the VM is in powered-off state.

    Args:
        pool: The pool the VM belongs to.
        vmId: The unique identifier of the VM.
        params: Additional parameters for the operation.

    Returns:
        VmInfo: Updated information about the VM after the operation.

    Raises:
        Exception: If the operation fails.
    """

    # TODO: this is a stub, and should be replaced with the actual implementation

    vm = _get_vm(pool, vmId)
    vm.powerState = "PoweredOff"
    return vm


def shutdown_vm(pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
    """Gracefully shutdown a virtual machine.

    This sends a shutdown signal to the guest OS, allowing it to shutdown cleanly.
    For a forced power-off, use power_off_vm instead.

    This function should only return after the operation is fully completed.

    Args:
        pool: The pool the VM belongs to.
        vmId: The unique identifier of the VM.
        params: Additional parameters for the operation.

    Returns:
        VmInfo: Updated information about the VM after the operation.

    Raises:
        Exception: If the operation fails.
    """

    # TODO: this is a stub, and should be replaced with the actual implementation

    vm = _get_vm(pool, vmId)
    vm.powerState = "PoweredOff"
    return vm


# -------- VM management functions (optional) --------

# Optional functions are omitted in this example.
# Refer to the LifecycleManagement.pyi file and ohcs.lcm.models.py file for the complete list of optional functions.

# def restart_vm(self, pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo: ...
# def snapshot_vm(self, pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo: ...
# def restore_vm(self, pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo: ...
# def hibernate_vm(self, pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo: ...
# def resize_vm(self, pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo: ...
