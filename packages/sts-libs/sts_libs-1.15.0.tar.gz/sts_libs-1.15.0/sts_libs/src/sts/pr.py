# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Persistent Reservation device management.

This module provides functionality for managing SCSI Persistent Reservations:
- Device registration with reservation keys
- Reservation creation and management
- Reservation status monitoring
- Multi-initiator coordination

Persistent Reservations provide a mechanism for coordinating access to
shared SCSI devices between multiple initiators (hosts):
- Registration: Initiators register with a unique reservation key
- Reservation: One initiator holds exclusive or shared access
- Preemption: Ability to remove other initiators' registrations
- Release: Voluntary release of reservations

Common use cases:
- Cluster storage coordination
- High availability failover
- Storage virtualization
- Backup and disaster recovery
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from sts.base import StorageDevice
from sts.sg3_utils import (
    PR_TYPE_NAMES,
    PR_TYPE_WRITE_EXCLUSIVE,
    SgPersist,
    get_pr_type_name,
)
from sts.utils.errors import DeviceError

if TYPE_CHECKING:
    from typing_extensions import Self

logger = logging.getLogger(__name__)

# Default timeout for PR operations
DEFAULT_PR_TIMEOUT = 30


@dataclass
class PRDevice(StorageDevice):
    """Persistent Reservation capable device.

    This class extends StorageDevice with SCSI Persistent Reservation functionality
    for coordinating shared access between multiple initiators.

    Persistent Reservations provide a standard mechanism for:
    - Registering initiators with unique keys
    - Creating exclusive or shared reservations
    - Monitoring reservation status
    - Coordinating access in multi-host environments

    Args:
        path: Device path (e.g., '/dev/sda')
        register_key: Current registration key for this initiator
        transport_id: Transport-specific identifier (optional)
        auto_register: Automatically register key on initialization

    Raises:
        DeviceError: If device does not support persistent reservations

    Example:
        ```python
        # Create PR device and register key
        pr_device = PRDevice('/dev/sda', register_key='0x1234')

        # Create write-exclusive reservation
        pr_device.create_reservation(PR_TYPE_WRITE_EXCLUSIVE)

        # Check reservation status
        if pr_device.is_reservation_holder():
            print('This host holds the reservation')

        # Release reservation when done
        pr_device.release_reservation()
        ```
    """

    # PR-specific attributes
    register_key: str | None = None
    transport_id: str | None = None
    auto_register: bool = field(default=False)

    # Internal state management
    _sg_persist: SgPersist = field(init=False, repr=False)
    _current_reservation_type: int | None = field(init=False, default=None, repr=False)
    _registered_keys: list[str] = field(init=False, default_factory=list, repr=False)
    _reservation_holder: str | None = field(init=False, default=None, repr=False)
    _supports_pr: bool | None = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        """Initialize PR device.

        Sets up sg3_utils interface and optionally registers the key.
        """
        # Initialize parent class
        super().__post_init__()

        # Initialize sg3_utils interface
        self._sg_persist = SgPersist()

        # Validate PR capability
        if not self.supports_pr:
            raise DeviceError(f'Device {self.path} does not support persistent reservations')

        # Auto-register key if requested
        if self.auto_register and self.register_key:
            success = self.register_key_on_device(self.register_key, self.transport_id)
            if not success:
                logger.warning(f'Failed to auto-register key {self.register_key}')

        # Load initial state
        self._refresh_state()

    def _check_pr_support(self) -> bool:
        """Check if device supports persistent reservations.

        Returns:
            True if device supports PR operations
        """
        if not self.path:
            return False
        try:
            # report_capabilities returns bool directly
            return self._sg_persist.report_capabilities(self.path)
        except (OSError, RuntimeError, ValueError) as e:
            logger.debug(f'PR support check failed: {e}')
            return False

    def _refresh_state(self) -> None:
        """Refresh internal state from device."""
        if not self.path:
            return

        # Get current keys - read_keys returns list[str] directly
        self._registered_keys = self._sg_persist.read_keys(self.path)

        # Get current reservation - read_reservation returns tuple
        holder_key, reservation_type = self._sg_persist.read_reservation(self.path)

        if reservation_type:
            try:
                self._current_reservation_type = int(reservation_type)
            except ValueError:
                self._current_reservation_type = None
        else:
            self._current_reservation_type = None

        self._reservation_holder = holder_key

    # Core PR Operations

    def register_key_on_device(self, key: str, transport_id: str | None = None) -> bool:
        """Register a key for persistent reservations.

        Registration is required before a host can create reservations.
        Each initiator should use a unique key.

        Args:
            key: Registration key (e.g., '0x1234')
            transport_id: Transport-specific identifier (optional)

        Returns:
            True if registration succeeded

        Example:
            ```python
            # Simple registration
            success = pr_device.register_key_on_device('0x1234')

            # Registration with transport ID for SAS devices
            success = pr_device.register_key_on_device('0x1234', 'sas,5001405f31c32fa2')
            ```
        """
        if not self.path:
            logger.error('Device path not set')
            return False

        logger.info(f'Registering PR key {key} for {self.path}')

        # register returns bool directly
        success = self._sg_persist.register(self.path, key, transport_id)

        if success:
            self.register_key = key
            self.transport_id = transport_id
            self._refresh_state()
            logger.info(f'Successfully registered key {key}')
        else:
            logger.error(f'Failed to register key {key}')

        return success

    def unregister_key_from_device(self, key: str | None = None) -> bool:
        """Unregister a key from persistent reservations.

        Args:
            key: Key to unregister (defaults to current register_key)

        Returns:
            True if unregistration succeeded

        Example:
            ```python
            # Unregister current key
            success = pr_device.unregister_key_from_device()

            # Unregister specific key
            success = pr_device.unregister_key_from_device('0x1234')
            ```
        """
        if not self.path:
            logger.error('Device path not set')
            return False

        target_key = key or self.register_key
        if not target_key:
            logger.error('No key specified for unregistration')
            return False

        logger.info(f'Unregistering PR key {target_key} for {self.path}')

        # unregister returns bool directly
        success = self._sg_persist.unregister(self.path, target_key)

        if success:
            if target_key == self.register_key:
                self.register_key = None
                self.transport_id = None
            self._refresh_state()
            logger.info(f'Successfully unregistered key {target_key}')
        else:
            logger.error(f'Failed to unregister key {target_key}')

        return success

    def create_reservation(self, pr_type: int = PR_TYPE_WRITE_EXCLUSIVE, key: str | None = None) -> bool:
        """Create a persistent reservation.

        The initiator must be registered before creating a reservation.

        Args:
            pr_type: Persistent reservation type (default: write exclusive)
            key: Reservation key (defaults to current register_key)

        Returns:
            True if reservation creation succeeded

        Example:
            ```python
            # Create write-exclusive reservation
            success = pr_device.create_reservation(PR_TYPE_WRITE_EXCLUSIVE)

            # Create exclusive access reservation
            success = pr_device.create_reservation(PR_TYPE_EXCLUSIVE_ACCESS)
            ```
        """
        if not self.path:
            logger.error('Device path not set')
            return False

        target_key = key or self.register_key
        if not target_key:
            logger.error('No key specified for reservation')
            return False

        if pr_type not in PR_TYPE_NAMES:
            logger.error(f'Unsupported PR type: {pr_type}')
            return False

        logger.info(f'Creating {get_pr_type_name(pr_type)} reservation with key {target_key}')

        # reserve returns bool directly
        success = self._sg_persist.reserve(self.path, target_key, pr_type)

        if success:
            self._current_reservation_type = pr_type
            self._reservation_holder = target_key
            logger.info(f'Successfully created reservation type {pr_type}')
        else:
            logger.error('Failed to create reservation')

        return success

    def release_reservation(self, pr_type: int | None = None, key: str | None = None) -> bool:
        """Release a persistent reservation.

        Args:
            pr_type: Reservation type to release (defaults to current type)
            key: Reservation key (defaults to current register_key)

        Returns:
            True if reservation release succeeded

        Example:
            ```python
            # Release current reservation
            success = pr_device.release_reservation()

            # Release specific reservation type
            success = pr_device.release_reservation(PR_TYPE_WRITE_EXCLUSIVE)
            ```
        """
        if not self.path:
            logger.error('Device path not set')
            return False

        target_key = key or self.register_key
        if not target_key:
            logger.error('No key specified for release')
            return False

        target_type = pr_type or self._current_reservation_type
        if target_type is None:
            logger.error('No reservation type specified for release')
            return False

        logger.info(f'Releasing reservation type {target_type} with key {target_key}')

        # release returns bool directly
        success = self._sg_persist.release(self.path, target_key, target_type)

        if success:
            self._current_reservation_type = None
            self._reservation_holder = None
            self._refresh_state()
            logger.info('Successfully released reservation')
        else:
            logger.error('Failed to release reservation')

        return success

    # Status and State Methods

    def get_reservation_status(self) -> tuple[str | None, str | None]:
        """Get current reservation status.

        Returns:
            Tuple of (holder_key, reservation_type) or (None, None) if no reservation

        Example:
            ```python
            holder, res_type = pr_device.get_reservation_status()
            if holder and res_type:
                print(f'Reservation holder: {holder}')
                print(f'Reservation type: {res_type}')
            ```
        """
        if not self.path:
            return (None, None)

        return self._sg_persist.read_reservation(self.path)

    def get_registered_keys(self) -> list[str]:
        """Get list of all registered keys.

        Returns:
            List of registered reservation keys

        Example:
            ```python
            keys = pr_device.get_registered_keys()
            print(f'Registered keys: {keys}')
            ```
        """
        if not self.path:
            return []

        return self._sg_persist.read_keys(self.path)

    def get_full_status(self) -> dict[str, Any]:
        """Get complete reservation status including all keys.

        Returns:
            Dictionary with complete status information

        Example:
            ```python
            status = pr_device.get_full_status()
            if status:
                for key, value in status.items():
                    print(f'{key}: {value}')
            ```
        """
        if not self.path:
            return {}

        return self._sg_persist.read_full_status(self.path)

    def is_reservation_holder(self) -> bool:
        """Check if this device is the current reservation holder.

        Returns:
            True if this device holds the reservation

        Example:
            ```python
            if pr_device.is_reservation_holder():
                print('This host has exclusive access')
            else:
                print('Another host holds the reservation')
            ```
        """
        if not self.register_key:
            return False

        return self.reservation_holder == self.register_key

    def is_registered(self, key: str | None = None) -> bool:
        """Check if a key is registered.

        Args:
            key: Key to check (defaults to current register_key)

        Returns:
            True if key is registered

        Example:
            ```python
            if pr_device.is_registered():
                print('Current key is registered')

            if pr_device.is_registered('0x5678'):
                print('Key 0x5678 is registered')
            ```
        """
        target_key = key or self.register_key
        if not target_key:
            return False

        return target_key in self.all_registered_keys

    def has_reservation(self) -> bool:
        """Check if device currently has any reservation.

        Returns:
            True if device has an active reservation

        Example:
            ```python
            if pr_device.has_reservation():
                print('Device has an active reservation')
            ```
        """
        return self.reservation_holder is not None

    # ==========================================================================
    # Properties - Organized for clarity and convenience
    # ==========================================================================

    # Core Device State Properties (direct access to internal state)
    # ----------------------------------------------------------------

    @property
    def supports_pr(self) -> bool:
        """Check if device supports PR operations.

        This property caches the PR support check to avoid repeated expensive operations.

        Returns:
            True if device supports persistent reservations

        Example:
            ```python
            if pr_device.supports_pr:
                print('Device supports PR operations')
            ```
        """
        if self._supports_pr is None:
            self._supports_pr = self._check_pr_support()
        return self._supports_pr

    @property
    def reservation_holder(self) -> str | None:
        """Get current reservation holder key.

        Auto-refreshes state if no cached holder information is available.

        Returns:
            Key of current reservation holder or None if no reservation

        Example:
            ```python
            holder = pr_device.reservation_holder
            if holder:
                print(f'Reservation held by: {holder}')
            ```
        """
        if self._reservation_holder is None:
            self._refresh_state()
        return self._reservation_holder

    @property
    def reservation_type(self) -> int | None:
        """Get current reservation type number.

        Auto-refreshes state if no cached type information is available.

        Returns:
            Current reservation type or None if no reservation

        Example:
            ```python
            res_type = pr_device.reservation_type
            if res_type:
                print(f'Reservation type: {res_type}')
            ```
        """
        if self._current_reservation_type is None:
            self._refresh_state()
        return self._current_reservation_type

    @property
    def all_registered_keys(self) -> list[str]:
        """Get cached list of all registered keys.

        Returns a copy to prevent external modification of internal state.
        Auto-refreshes if cache is empty.

        Returns:
            List of all registered keys (safe copy)

        Example:
            ```python
            keys = pr_device.all_registered_keys
            print(f'All keys: {keys}')
            ```
        """
        if not self._registered_keys:
            self._refresh_state()
        return self._registered_keys.copy()

    @property
    def transport_ids(self) -> list[dict[str, str]]:
        """Get transport IDs of all registered initiators.

        Returns:
            List of transport ID dictionaries, each containing:
            - 'type': Transport type ('iscsi', 'sas', 'fc', or 'unknown')
            - 'id': Transport identifier string
            - 'key': Associated registration key

        Example:
            ```python
            for tid in pr_device.transport_ids:
                logger.info(f'Key {tid["key"]}: {tid["type"]} - {tid["id"]}')
            ```
        """
        if not self.path:
            return []

        return self._sg_persist.get_transport_ids(self.path)

    # Derived State Properties (computed from core state)
    # ---------------------------------------------------

    @property
    def current_reservation_type_name(self) -> str | None:
        """Get human-readable name of current reservation type.

        Returns:
            Human-readable name or None if no reservation

        Example:
            ```python
            type_name = pr_device.current_reservation_type_name
            print(f'Current reservation: {type_name}')
            # Output: "Current reservation: write exclusive"
            ```
        """
        if self.reservation_type is not None:
            return get_pr_type_name(self.reservation_type)
        return None

    @property
    def num_registered_keys(self) -> int:
        """Count of registered keys on the device.

        Returns:
            Number of keys currently registered

        Example:
            ```python
            count = pr_device.num_registered_keys
            print(f'Number of registered keys: {count}')
            ```
        """
        return len(self.all_registered_keys)

    # Boolean Status Properties (convenient checks)
    # ---------------------------------------------

    @property
    def is_key_registered(self) -> bool:
        """Check if current register_key is registered on the device.

        Returns:
            True if current register_key is registered

        Example:
            ```python
            if pr_device.is_key_registered:
                print('Current key is registered')
            ```
        """
        return self.is_registered()

    @property
    def can_create_reservation(self) -> bool:
        """Check if conditions allow creating a new reservation.

        Verifies that:
        - Current key is registered
        - No existing reservation exists
        - Register key is set

        Returns:
            True if reservation can be created

        Example:
            ```python
            if pr_device.can_create_reservation:
                print('Ready to create reservation')
                pr_device.create_reservation()
            ```
        """
        return self.is_key_registered and not self.has_reservation() and self.register_key is not None

    # Summary Properties (aggregated information)
    # ------------------------------------------

    @property
    def pr_status_summary(self) -> dict[str, Any]:
        """Get concise summary dict of current PR status.

        Provides quick overview of the most important PR state information.

        Returns:
            Dictionary with current PR status information

        Example:
            ```python
            status = pr_device.pr_status_summary
            print(f'Status: {status}')
            # {'has_reservation': True, 'holder': '0x1234', 'type': 1, 'num_keys': 2}
            ```
        """
        return {
            'has_reservation': self.has_reservation(),
            'holder': self.reservation_holder,
            'type': self.reservation_type,
            'type_name': self.current_reservation_type_name,
            'num_keys': self.num_registered_keys,
            'is_holder': self.is_reservation_holder(),
            'is_registered': self.is_key_registered,
            'can_create': self.can_create_reservation,
        }

    @property
    def reservation_info(self) -> dict[str, Any]:
        """Get comprehensive reservation information dict.

        Provides complete view of device configuration and state for debugging
        and monitoring purposes.

        Returns:
            Dictionary with detailed reservation information

        Example:
            ```python
            info = pr_device.reservation_info
            print(f'Complete info: {info}')
            ```
        """
        return {
            'device_path': str(self.path) if self.path else None,
            'register_key': self.register_key,
            'transport_id': self.transport_ids,
            'reservation_holder': self.reservation_holder,
            'reservation_type': self.reservation_type,
            'reservation_type_name': self.current_reservation_type_name,
            'registered_keys': self.all_registered_keys,
            'num_registered_keys': self.num_registered_keys,
            'is_reservation_holder': self.is_reservation_holder(),
            'is_key_registered': self.is_key_registered,
            'has_reservation': self.has_reservation(),
            'supports_pr': self.supports_pr,
            'can_create_reservation': self.can_create_reservation,
        }

    # Utility Methods

    @classmethod
    def from_device(cls, device: StorageDevice, **kwargs: dict[str, Any]) -> Self:
        """Create PRDevice from existing StorageDevice.

        Args:
            device: Existing StorageDevice instance
            **kwargs: Additional arguments for PRDevice

        Returns:
            New PRDevice instance

        Example:
            ```python
            scsi_device = ScsiDevice('/dev/sda')
            pr_device = PRDevice.from_device(scsi_device, register_key='0x1234')
            ```
        """
        # Copy relevant attributes from source device
        pr_kwargs = {
            'path': device.path,
            'name': device.name,
            'size': device.size,
            'model': device.model,
        }
        pr_kwargs.update(kwargs)

        return cls(**pr_kwargs)

    def __str__(self) -> str:
        """Return string representation of PR device."""
        status_parts = []

        if self.register_key:
            status_parts.append(f'key={self.register_key}')

        if self.reservation_type is not None:
            type_name = get_pr_type_name(self.reservation_type)
            status_parts.append(f'reservation={type_name}')

        status = f'({", ".join(status_parts)})' if status_parts else '(unregistered)'

        return f'PRDevice({self.path or "unknown"}) {status}'
