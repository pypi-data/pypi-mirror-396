# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol


@dataclass
class VmInfo:
    id: str
    powerState: str
    snapshotId: Optional[str] = None
    cloudId: Optional[str] = None
    error: Optional[str] = None
    properties: Optional[Dict] = None


@dataclass
class Pool:
    id: str
    orgId: str
    location: str
    name: str
    providerType: str
    provider: dict
    sparePolicy: dict
    powerPolicy: dict
    properties: dict
    agentCustomization: dict
    extensionName: str
    customVariables: str
    customTemplate: str


class LifecycleManagement(Protocol):
    """Protocol defining the lifecycle management interface.

    This protocol defines the contract that all lifecycle management implementations
    must satisfy.
    """

    def init(self) -> Optional[dict[str, Any]]:
        """Initialize the lifecycle management plugin implementation.

        This method is called once during the initialization phase to set up
        any required resources, connections, or state.

        Returns:
            Optional[dict[str, Any]]: Initialization metadata or None if no metadata is needed.

        Raises:
            Exception: If the operation fails.
        """
        ...

    # -------- Pool management functions --------

    def health(self, pool: Pool, params: dict[str, Any]) -> dict[str, Any]:
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
        ...

    def prepare_pool(self, pool: Pool, params: dict[str, Any]) -> Optional[dict[str, Any]]:
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
        ...

    def destroy_pool(self, pool: Pool, params: dict[str, Any]) -> None:
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
        ...

    def list_vms(self, pool: Pool, params: dict[str, Any]) -> list[VmInfo]:
        """List all virtual machines associated with a pool.

        Args:
            pool: The pool.
            params: Additional parameters for the operation.

        Returns:
            list[VmInfo]: A list of VM information objects for all VMs in the pool.

        Raises:
            Exception: If the operation fails.
        """
        ...

    # -------- VM management functions (required) --------

    def get_vm(self, pool: Pool, vmId: str) -> Optional[VmInfo]:
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
        ...

    def create_vm(self, pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
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
        ...

    def delete_vm(self, pool: Pool, vmId: str, params: dict[str, Any]) -> None:
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
        ...

    def power_on_vm(self, pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
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
        ...

    def power_off_vm(self, pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
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
        ...

    def shutdown_vm(self, pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
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
        ...

    # -------- VM management functions (optional) --------

    def restart_vm(self, pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
        """Restart a virtual machine forcefully, without graceful shutdown.

        This function is optional.
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
        ...

    def snapshot_vm(self, pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
        """Take snapshot of a virtual machine.

        This method takes a snapshot of the VM and returns the snapshot information in the VmInfo object.

        This function is optional.
        This function should only return after the operation is fully completed.

        Args:
            pool: The pool the VM belongs to.
            vmId: The unique identifier of the VM to take snapshot of.
            params: Additional parameters for the operation.

        Returns:
            VmInfo: Updated information about the VM after the operation.

        Raises:
            Exception: If the operation fails.
        """
        ...

    def restore_vm(self, pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
        """Restore a virtual machine from a snapshot.

        This method restores a VM from a snapshot and returns the restored VM information.

        This function is optional.
        This function should only return after the operation is fully completed.

        Args:
            pool: The pool the VM belongs to.
            vmId: The unique identifier of the VM to restore from a snapshot.
            params: Additional parameters for the operation.

        Returns:
            VmInfo: Updated information about the VM after the operation.

        Raises:
            Exception: If the operation fails.
        """
        ...

    def hibernate_vm(self, pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
        """Hibernate a virtual machine.

        This function is optional.
        This function should only return after the operation is fully completed.

        Args:
            pool: The pool the VM belongs to.
            vmId: The unique identifier of the VM to hibernate.
            params: Additional parameters for the operation.

        Returns:
            VmInfo: Updated information about the VM after the operation.

        Raises:
            Exception: If the operation fails.
        """
        ...

    def resize_vm(self, pool: Pool, vmId: str, params: dict[str, Any]) -> VmInfo:
        """Resize a virtual machine.

        This function is optional.
        This function should only return after the operation is fully completed.

        Args:
            pool: The pool the VM belongs to.
            vmId: The unique identifier of the VM to resize.
            params: Additional parameters for the operation.

        Returns:
            VmInfo: Updated information about the VM after the operation.

        Raises:
            Exception: If the operation fails.
        """
        ...
