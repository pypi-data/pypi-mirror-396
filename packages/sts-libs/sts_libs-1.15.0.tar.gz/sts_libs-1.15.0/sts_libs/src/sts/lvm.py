# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""LVM device management.

This module provides functionality for managing LVM devices:
- Physical Volume (PV) operations
- Volume Group (VG) operations
- Logical Volume (LV) operations

LVM (Logical Volume Management) provides flexible disk space management:
1. Physical Volumes (PVs): Physical disks or partitions
2. Volume Groups (VGs): Pool of space from PVs
3. Logical Volumes (LVs): Virtual partitions from VG space

Key benefits:
- Resize filesystems online
- Snapshot and mirror volumes
- Stripe across multiple disks
- Move data between disks
"""

from __future__ import annotations

import json
import logging
import re
import time
from abc import abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, TypedDict

from sts.base import StorageDevice
from sts.udevadm import udevadm_settle
from sts.utils.cmdline import run

if TYPE_CHECKING:
    from sts.utils.cmdline import CommandResult


class LvmOptions(TypedDict, total=False):
    """LVM command options.

    Common options:
    - size: Volume size (e.g. '1G', '500M')
    - extents: Volume size in extents (e.g. '100%FREE')
    - permission: Volume permission (rw/r)
    - persistent: Make settings persistent across reboots
    - monitor: Monitor volume for events
    - autobackup: Auto backup metadata after changes

    Size can be specified in:
    - Absolute size (1G, 500M)
    - Percentage of VG (80%VG)
    - Percentage of free space (100%FREE)
    - Physical extents (100)
    """

    size: str
    extents: str
    permission: str
    persistent: str
    monitor: str
    autobackup: str


@dataclass
class LVReport:
    """Logical Volume report data.

    This class provides detailed information about a Logical Volume from 'lvs -o lv_all --reportformat json'.
    Contains all available LV attributes that can be queried.

    Args:
        name: LV name (optional, used for fetching, can be discovered)
        vg: Volume group name (optional, used for fetching, can be discovered)
        prevent_update: Flag to prevent updates from report (defaults to False)

        All lv_* fields: LV attributes from lvs output
        raw_data: Complete raw data from lvs output
    """

    # Control fields
    name: str | None = None
    vg: str | None = None
    prevent_update: bool = field(default=False)

    # Core LV identification
    lv_uuid: str | None = None
    lv_name: str | None = None
    lv_full_name: str | None = None
    lv_path: str | None = None
    lv_dm_path: str | None = None
    vg_name: str | None = None

    # Size and layout information
    lv_size: str | None = None
    lv_metadata_size: str | None = None
    seg_count: str | None = None
    lv_layout: str | None = None
    lv_role: str | None = None

    # Status and attributes
    lv_attr: str | None = None
    lv_active: str | None = None
    lv_active_locally: str | None = None
    lv_active_remotely: str | None = None
    lv_active_exclusively: str | None = None
    lv_permissions: str | None = None
    lv_suspended: str | None = None

    # Device information
    lv_major: str | None = None
    lv_minor: str | None = None
    lv_kernel_major: str | None = None
    lv_kernel_minor: str | None = None
    lv_read_ahead: str | None = None
    lv_kernel_read_ahead: str | None = None

    # Pool and thin provisioning
    pool_lv: str | None = None
    pool_lv_uuid: str | None = None
    data_lv: str | None = None
    data_lv_uuid: str | None = None
    metadata_lv: str | None = None
    metadata_lv_uuid: str | None = None
    data_percent: str | None = None
    metadata_percent: str | None = None

    # Snapshot information
    origin: str | None = None
    origin_uuid: str | None = None
    origin_size: str | None = None
    snap_percent: str | None = None

    # RAID information
    raid_mismatch_count: str | None = None
    raid_sync_action: str | None = None
    raid_write_behind: str | None = None
    raid_min_recovery_rate: str | None = None
    raid_max_recovery_rate: str | None = None

    # Cache information
    cache_total_blocks: str | None = None
    cache_used_blocks: str | None = None
    cache_dirty_blocks: str | None = None
    cache_read_hits: str | None = None
    cache_read_misses: str | None = None
    cache_write_hits: str | None = None
    cache_write_misses: str | None = None
    kernel_cache_settings: str | None = None
    kernel_cache_policy: str | None = None

    # VDO information
    vdo_operating_mode: str | None = None
    vdo_compression_state: str | None = None
    vdo_index_state: str | None = None
    vdo_used_size: str | None = None
    vdo_saving_percent: str | None = None

    # Write cache information
    writecache_block_size: str | None = None
    writecache_total_blocks: str | None = None
    writecache_free_blocks: str | None = None
    writecache_writeback_blocks: str | None = None
    writecache_error: str | None = None

    # Configuration and policy
    lv_allocation_policy: str | None = None
    lv_allocation_locked: str | None = None
    lv_autoactivation: str | None = None
    lv_when_full: str | None = None
    lv_skip_activation: str | None = None
    lv_fixed_minor: str | None = None

    # Timing and host information
    lv_time: str | None = None
    lv_time_removed: str | None = None
    lv_host: str | None = None

    # Health and status checks
    lv_health_status: str | None = None
    lv_check_needed: str | None = None
    lv_merge_failed: str | None = None
    lv_snapshot_invalid: str | None = None

    # Miscellaneous
    lv_tags: str | None = None
    lv_profile: str | None = None
    lv_lockargs: str | None = None
    lv_modules: str | None = None
    lv_historical: str | None = None
    kernel_discards: str | None = None
    copy_percent: str | None = None
    sync_percent: str | None = None

    # Device table status
    lv_live_table: str | None = None
    lv_inactive_table: str | None = None
    lv_device_open: str | None = None

    # Hierarchical relationships
    lv_parent: str | None = None
    lv_ancestors: str | None = None
    lv_full_ancestors: str | None = None
    lv_descendants: str | None = None
    lv_full_descendants: str | None = None

    # Conversion and movement
    lv_converting: str | None = None
    lv_merging: str | None = None
    move_pv: str | None = None
    move_pv_uuid: str | None = None
    convert_lv: str | None = None
    convert_lv_uuid: str | None = None

    # Mirror information
    mirror_log: str | None = None
    mirror_log_uuid: str | None = None

    # Synchronization
    lv_initial_image_sync: str | None = None
    lv_image_synced: str | None = None

    # Integrity
    raidintegritymode: str | None = None
    raidintegrityblocksize: str | None = None
    integritymismatches: str | None = None
    kernel_metadata_format: str | None = None

    # Segment information (from seg_all)
    segtype: str | None = None
    stripes: str | None = None
    data_stripes: str | None = None
    stripe_size: str | None = None
    region_size: str | None = None
    chunk_size: str | None = None
    seg_start: str | None = None
    seg_start_pe: str | None = None
    seg_size: str | None = None
    seg_size_pe: str | None = None
    seg_tags: str | None = None
    seg_pe_ranges: str | None = None
    seg_le_ranges: str | None = None
    seg_metadata_le_ranges: str | None = None
    devices: str | None = None
    metadata_devices: str | None = None
    seg_monitor: str | None = None

    # Additional segment fields
    reshape_len: str | None = None
    reshape_len_le: str | None = None
    data_copies: str | None = None
    data_offset: str | None = None
    new_data_offset: str | None = None
    parity_chunks: str | None = None
    thin_count: str | None = None
    discards: str | None = None
    cache_metadata_format: str | None = None
    cache_mode: str | None = None
    zero: str | None = None
    transaction_id: str | None = None
    thin_id: str | None = None
    cache_policy: str | None = None
    cache_settings: str | None = None
    integrity_settings: str | None = None

    # VDO segment settings
    vdo_compression: str | None = None
    vdo_deduplication: str | None = None
    vdo_minimum_io_size: str | None = None
    vdo_block_map_cache_size: str | None = None
    vdo_block_map_era_length: str | None = None
    vdo_use_sparse_index: str | None = None
    vdo_index_memory_size: str | None = None
    vdo_slab_size: str | None = None
    vdo_ack_threads: str | None = None
    vdo_bio_threads: str | None = None
    vdo_bio_rotation: str | None = None
    vdo_cpu_threads: str | None = None
    vdo_hash_zone_threads: str | None = None
    vdo_logical_threads: str | None = None
    vdo_physical_threads: str | None = None
    vdo_max_discard: str | None = None
    vdo_header_size: str | None = None
    vdo_use_metadata_hints: str | None = None
    vdo_write_policy: str | None = None

    # Raw data storage for any additional fields
    raw_data: dict[str, Any] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        """Initialize the report."""
        # If name and vg are provided, fetch the report data
        if self.name and self.vg:
            self.refresh()

    def refresh(self) -> bool:
        """Refresh LV report data from system.

        Updates all fields with the latest information from lvs command.

        Returns:
            bool: True if refresh was successful, False otherwise
        """
        # If prevent_update is True, skip refresh
        if self.prevent_update:
            logging.debug('Refresh skipped due to prevent_update flag')
            return True

        if not self.name or not self.vg:
            logging.error('LV name and VG name required for refresh')
            return False

        # Run lvs command with JSON output including segment information
        result = run(f'lvs -a -o lv_all,seg_all {self.vg}/{self.name} --reportformat json')
        if result.failed or not result.stdout:
            logging.error(f'Failed to get LV report data for {self.vg}/{self.name}')
            return False

        try:
            report_data = json.loads(result.stdout)
            return self._update_from_report(report_data)
        except json.JSONDecodeError:
            logging.exception('Failed to parse LV report JSON')
            return False

    def _update_from_report(self, report_data: dict[str, Any]) -> bool:
        """Update LV information from report data.

        Args:
            report_data: Complete report data from lvs JSON

        Returns:
            bool: True if update was successful, False otherwise
        """
        if self.prevent_update:
            logging.debug('Update from report skipped due to prevent_update flag')
            return True

        if not isinstance(report_data, dict) or 'report' not in report_data:
            logging.error('Invalid LV report format')
            return False

        reports = report_data.get('report', [])
        if not isinstance(reports, list) or not reports:
            logging.error('No reports found in LV data')
            return False

        # Get the first report
        report = reports[0]
        if not isinstance(report, dict) or 'lv' not in report:
            logging.error('Invalid report structure')
            return False

        lvs = report.get('lv', [])
        if not isinstance(lvs, list) or not lvs:
            logging.warning(f'No LV data found for {self.vg}/{self.name}')
            return False

        # Get the first (and should be only) LV
        lv_data = lvs[0]
        if not isinstance(lv_data, dict):
            logging.error('Invalid LV data structure')
            return False

        # Update all fields from the data
        self.raw_data = lv_data.copy()

        # Map all known fields
        for field_name in self.__dataclass_fields__:
            if field_name not in ('raw_data', 'name', 'vg', 'prevent_update') and field_name in lv_data:
                setattr(self, field_name, lv_data[field_name])

        # Update our name and vg from the data if not set
        if not self.name and self.lv_name:
            self.name = self.lv_name
        if not self.vg and self.vg_name:
            self.vg = self.vg_name

        # Extract VG name from full name if available
        if self.lv_full_name and not self.vg_name and '/' in self.lv_full_name:
            self.vg_name = self.lv_full_name.split('/')[0]

        return True

    @classmethod
    def get_all(cls, vg: str | None = None) -> list[LVReport]:
        """Get reports for all logical volumes.

        Args:
            vg: Optional volume group to filter by

        Returns:
            List of LVReport instances
        """
        reports: list[LVReport] = []

        # Build command
        cmd = 'lvs -o lv_all,seg_all --reportformat json'
        if vg:
            cmd += f' {vg}'

        result = run(cmd)
        if result.failed or not result.stdout:
            return reports

        try:
            report_data = json.loads(result.stdout)

            if 'report' in report_data and isinstance(report_data['report'], list):
                for report in report_data['report']:
                    if not isinstance(report, dict) or 'lv' not in report:
                        continue

                    for lv_data in report.get('lv', []):
                        if not isinstance(lv_data, dict):
                            continue

                        # Create report with prevent_update=True to avoid double refresh
                        lv_report = cls(prevent_update=True)
                        lv_report.raw_data = lv_data.copy()

                        # Map all known fields
                        for field_name in cls.__dataclass_fields__:
                            if field_name not in ('raw_data', 'name', 'vg', 'prevent_update') and field_name in lv_data:
                                setattr(lv_report, field_name, lv_data[field_name])

                        # Set name and vg from the data
                        lv_report.name = lv_report.lv_name
                        lv_report.vg = lv_report.vg_name

                        # Extract VG name from full name if needed
                        if lv_report.lv_full_name and not lv_report.vg_name and '/' in lv_report.lv_full_name:
                            lv_report.vg_name = lv_report.lv_full_name.split('/')[0]
                            if not lv_report.vg:
                                lv_report.vg = lv_report.vg_name

                        reports.append(lv_report)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logging.warning(f'Failed to parse LV reports: {e}')

        return reports


@dataclass
class PVInfo:
    """Physical Volume information.

    Stores key information about a Physical Volume:
    - Volume group membership
    - Format type (lvm2)
    - Attributes (allocatable, exported, etc)
    - Size information (total and free space)

    Args:
        vg: Volume group name (None if not in a VG)
        fmt: PV format (usually 'lvm2')
        attr: PV attributes (e.g. 'a--' for allocatable)
        psize: PV size (e.g. '1.00t')
        pfree: PV free space (e.g. '500.00g')
    """

    vg: str | None
    fmt: str
    attr: str
    psize: str
    pfree: str


@dataclass
class LvmDevice(StorageDevice):
    """Base class for LVM devices.

    Provides common functionality for all LVM device types:
    - Command execution with standard options
    - Configuration management
    - Basic device operations

    Args:
        name: Device name (optional)
        path: Device path (optional, defaults to /dev/<name>)
        size: Device size in bytes (optional, discovered from device)
        model: Device model (optional)
        yes: Automatically answer yes to prompts
        force: Force operations without confirmation

    The yes and force options are useful for automation:
    - yes: Skip interactive prompts
    - force: Ignore warnings and errors
    """

    # Optional parameters from parent classes
    name: str | None = None
    path: Path | str | None = None
    size: int | None = None
    model: str | None = None
    validate_on_init = False

    # Optional parameters for this class
    yes: bool = True  # Answer yes to prompts
    force: bool = False  # Force operations

    # Internal fields
    _config_path: Path = field(init=False, default=Path('/etc/lvm/lvm.conf'))

    def __post_init__(self) -> None:
        """Initialize LVM device."""
        # Set path based on name if not provided
        if not self.path and self.name:
            self.path = f'/dev/{self.name}'

        # Initialize parent class
        super().__post_init__()

    def _run(self, cmd: str, *args: str | Path | None, **kwargs: str) -> CommandResult:
        """Run LVM command.

        Builds and executes LVM commands with standard options:
        - Adds --yes for non-interactive mode
        - Adds --force to ignore warnings
        - Converts Python parameters to LVM options

        Args:
            cmd: Command name (e.g. 'pvcreate')
            *args: Command arguments
            **kwargs: Command parameters

        Returns:
            Command result
        """
        command = [cmd]
        if self.yes:
            command.append('--yes')
        if self.force:
            command.append('--force')
        if args:
            command.extend(str(arg) for arg in args if arg)
        if kwargs:
            command.extend(f'--{k.replace("_", "-")}={v}' for k, v in kwargs.items() if v)

        return run(' '.join(command))

    @abstractmethod
    def create(self, **options: str) -> bool:
        """Create LVM device.

        Args:
            **options: Device options (see LvmOptions)

        Returns:
            True if successful, False otherwise
        """

    @abstractmethod
    def remove(self, **options: str) -> bool:
        """Remove LVM device.

        Args:
            **options: Device options (see LvmOptions)

        Returns:
            True if successful, False otherwise
        """


@dataclass
class PhysicalVolume(LvmDevice):
    """Physical Volume device.

    A Physical Volume (PV) is a disk or partition used by LVM.
    PVs provide the storage pool for Volume Groups.

    Key features:
    - Initialize disks/partitions for LVM use
    - Track space allocation
    - Handle bad block management
    - Store LVM metadata

    Args:
        name: Device name (optional)
        path: Device path (optional, defaults to /dev/<name>)
        size: Device size in bytes (optional, discovered from device)
        model: Device model (optional)
        yes: Automatically answer yes to prompts
        force: Force operations without confirmation
        vg: Volume group name (optional, discovered from device)
        fmt: PV format (optional, discovered from device)
        attr: PV attributes (optional, discovered from device)
        pfree: PV free space (optional, discovered from device)

    Example:
        ```python
        pv = PhysicalVolume(name='sda1')  # Discovers other values
        pv = PhysicalVolume.create('/dev/sda1')  # Creates new PV
        ```
    """

    # Optional parameters for this class
    vg: str | None = None  # Volume Group membership
    fmt: str | None = None  # PV format (usually lvm2)
    attr: str | None = None  # PV attributes
    pfree: str | None = None  # Free space

    # Available PV commands
    COMMANDS: ClassVar[list[str]] = [
        'pvchange',  # Modify PV attributes
        'pvck',  # Check PV metadata
        'pvcreate',  # Initialize PV
        'pvdisplay',  # Show PV details
        'pvmove',  # Move PV data
        'pvremove',  # Remove PV
        'pvresize',  # Resize PV
        'pvs',  # List PVs
        'pvscan',  # Scan for PVs
    ]

    # Discover PV info if path is available
    def discover_pv_info(self) -> None:
        """Discovers PV information if path is available.

        Volume group membership.
        Format and attributes.
        Size information.
        """
        result = run(f'pvs {self.path} --noheadings --separator ","')
        if result.succeeded:
            # Parse PV info line
            # Format: PV,VG,Fmt,Attr,PSize,PFree
            parts = result.stdout.strip().split(',')
            if len(parts) == 6:
                _, vg, fmt, attr, _, pfree = parts
                if not self.vg:
                    self.vg = vg or None
                if not self.fmt:
                    self.fmt = fmt
                if not self.attr:
                    self.attr = attr
                if not self.pfree:
                    self.pfree = pfree

    def create(self, **options: str) -> bool:
        """Create Physical Volume.

        Initializes a disk or partition for use with LVM:
        - Creates LVM metadata area
        - Prepares device for VG membership

        Args:
            **options: PV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pv = PhysicalVolume(path='/dev/sda1')
            pv.create()
            True
            ```
        """
        if not self.path:
            logging.error('Device path required')
            return False

        result = self._run('pvcreate', str(self.path), **options)
        if result.succeeded:
            self.discover_pv_info()
        return result.succeeded

    def remove(self, **options: str) -> bool:
        """Remove Physical Volume.

        Removes LVM metadata from device:
        - Device must not be in use by a VG
        - Data on device is not erased

        Args:
            **options: PV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            pv = PhysicalVolume(path='/dev/sda1')
            pv.remove()
            True
            ```
        """
        if not self.path:
            logging.error('Device path required')
            return False

        result = self._run('pvremove', str(self.path), **options)
        return result.succeeded

    @classmethod
    def get_all(cls) -> dict[str, PVInfo]:
        """Get all Physical Volumes.

        Returns:
            Dictionary mapping PV names to their information

        Example:
            ```python
            PhysicalVolume.get_all()
            {'/dev/sda1': PVInfo(vg='vg0', fmt='lvm2', ...)}
            ```
        """
        result = run('pvs --noheadings --separator ","')
        if result.failed:
            logging.debug('No Physical Volumes found')
            return {}

        # Format: PV,VG,Fmt,Attr,PSize,PFree
        pv_info_regex = r'\s+(\S+),(\S+)?,(\S+),(.*),(.*),(.*)$'
        pv_dict = {}

        for line in result.stdout.splitlines():
            if match := re.match(pv_info_regex, line):
                pv_dict[match.group(1)] = PVInfo(
                    vg=match.group(2) or None,  # VG can be empty
                    fmt=match.group(3),
                    attr=match.group(4),
                    psize=match.group(5),
                    pfree=match.group(6),
                )

        return pv_dict


@dataclass
class VolumeGroup(LvmDevice):
    """Volume Group device.

    A Volume Group (VG) combines Physical Volumes into a storage pool.
    This pool can then be divided into Logical Volumes.

    Key features:
    - Combine multiple PVs
    - Manage storage pool
    - Track extent allocation
    - Handle PV addition/removal

    Args:
        name: Device name (optional)
        path: Device path (optional, defaults to /dev/<name>)
        size: Device size in bytes (optional, discovered from device)
        model: Device model (optional)
        yes: Automatically answer yes to prompts
        force: Force operations without confirmation
        pvs: List of Physical Volumes (optional, discovered from device)

    Example:
        ```python
        vg = VolumeGroup(name='vg0')  # Discovers other values
        vg = VolumeGroup.create('vg0', ['/dev/sda1'])  # Creates new VG
        ```
    """

    # Optional parameters for this class
    pvs: list[str] = field(default_factory=list)  # Member PVs

    # Available VG commands
    COMMANDS: ClassVar[list[str]] = [
        'vgcfgbackup',  # Backup VG metadata
        'vgcfgrestore',  # Restore VG metadata
        'vgchange',  # Change VG attributes
        'vgck',  # Check VG metadata
        'vgconvert',  # Convert VG metadata format
        'vgcreate',  # Create VG
        'vgdisplay',  # Show VG details
        'vgexport',  # Make VG inactive
        'vgextend',  # Add PVs to VG
        'vgimport',  # Make VG active
        'vgimportclone',  # Import cloned PVs
        'vgimportdevices',  # Import PVs into VG
        'vgmerge',  # Merge VGs
        'vgmknodes',  # Create VG special files
        'vgreduce',  # Remove PVs from VG
        'vgremove',  # Remove VG
        'vgrename',  # Rename VG
        'vgs',  # List VGs
        'vgscan',  # Scan for VGs
        'vgsplit',  # Split VG into two
    ]

    def discover_pvs(self) -> list[str] | None:
        """Discover PVs if name is available."""
        if self.name:
            result = run(f'vgs {self.name} -o pv_name --noheadings')
            if result.succeeded:
                self.pvs = result.stdout.strip().splitlines()
                return self.pvs
        return None

    def create(self, **options: str) -> bool:
        """Create Volume Group.

        Creates a new VG from specified PVs:
        - Initializes VG metadata
        - Sets up extent allocation
        - Creates device mapper devices

        Args:
            **options: VG options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            vg = VolumeGroup(name='vg0', pvs=['/dev/sda1'])
            vg.create()
            True
            ```
        """
        if not self.name:
            logging.error('Volume group name required')
            return False
        if not self.pvs:
            logging.error('Physical volumes required')
            return False

        result = self._run('vgcreate', self.name, *self.pvs, **options)
        return result.succeeded

    def remove(self, **options: str) -> bool:
        """Remove Volume Group.

        Removes VG and its metadata:
        - All LVs must be removed first
        - PVs are released but not removed

        Args:
            **options: VG options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            vg = VolumeGroup(name='vg0')
            vg.remove()
            True
            ```
        """
        if not self.name:
            logging.error('Volume group name required')
            return False

        result = self._run('vgremove', self.name, **options)
        return result.succeeded

    def activate(self, **options: str) -> bool:
        """Activate Volume Group.

        Makes the VG and all its LVs available for use.

        Args:
            **options: VG options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            vg = VolumeGroup(name='vg0')
            vg.activate()
            ```
        """
        if not self.name:
            logging.error('Volume group name required')
            return False

        result = self._run('vgchange', '-a', 'y', self.name, **options)
        return result.succeeded

    def deactivate(self, **options: str) -> bool:
        """Deactivate Volume Group.

        Makes the VG and all its LVs unavailable.

        Args:
            **options: VG options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            vg = VolumeGroup(name='vg0')
            vg.deactivate()
            ```
        """
        if not self.name:
            logging.error('Volume group name required')
            return False

        result = self._run('vgchange', '-a', 'n', self.name, **options)
        return result.succeeded


@dataclass
class LogicalVolume(LvmDevice):
    """Logical Volume device.

    A Logical Volume (LV) is a virtual partition created from VG space.
    LVs appear as block devices that can be formatted and mounted.

    Key features:
    - Flexible sizing
    - Online resizing
    - Snapshots
    - Striping and mirroring
    - Thin provisioning

    Args:
        name: Device name (optional)
        path: Device path (optional, defaults to /dev/<vg>/<name>)
        size: Device size in bytes (optional, discovered from device)
        model: Device model (optional)
        yes: Automatically answer yes to prompts
        force: Force operations without confirmation
        vg: Volume group name (optional, discovered from device)
        report: LV report instance (optional, created automatically)
        prevent_report_updates: Prevent automatic report updates (defaults to False)

    The LogicalVolume class now includes integrated report functionality:
    - Automatic report creation when name and vg are provided
    - Automatic report refresh after state-changing operations
    - Access to detailed LV information directly via report attributes
    - Prevention of updates via prevent_report_updates flag

    Example:
        ```python
        # Basic usage with automatic report
        lv = LogicalVolume(name='lv0', vg='vg0')
        lv.create(size='100M')
        print(lv.report.lv_size)

        # Prevent automatic updates
        lv = LogicalVolume(name='lv0', vg='vg0', prevent_report_updates=True)

        # Manual report refresh
        lv.refresh_report()
        ```
    """

    # Optional parameters for this class
    vg: str | None = None  # Parent VG
    pool_name: str | None = None
    report: LVReport | None = field(default=None, repr=False)
    prevent_report_updates: bool = False

    # Available LV commands
    COMMANDS: ClassVar[list[str]] = [
        'lvchange',  # Change LV attributes
        'lvcreate',  # Create LV
        'lvconvert',  # Convert LV type
        'lvdisplay',  # Show LV details
        'lvextend',  # Increase LV size
        'lvreduce',  # Reduce LV size
        'lvremove',  # Remove LV
        'lvrename',  # Rename LV
        'lvresize',  # Change LV size
        'lvs',  # List LVs
        'lvscan',  # Scan for LVs
    ]

    def __post_init__(self) -> None:
        """Initialize Logical Volume.

        - Sets device path from name and VG
        - Discovers VG membership
        - Creates and updates from report
        """
        # Set path based on name and vg if not provided
        if not self.path and self.name and self.vg:
            self.path = f'/dev/{self.vg}/{self.name}'

        # Initialize parent class
        super().__post_init__()

    def refresh_report(self) -> bool:
        """Refresh LV report data.

        Creates or updates the LV report with the latest information.

        Returns:
            bool: True if refresh was successful
        """
        # Create new report if needed
        if not self.report:
            # Do not provide name and vg during init to prevent update
            self.report = LVReport()
            self.report.name = self.name
            self.report.vg = self.vg

        # Refresh the report data
        return self.report.refresh()

    def discover_vg(self) -> str | None:
        """Discover VG if name is available."""
        if self.name and not self.vg:
            result = run(f'lvs {self.name} -o vg_name --noheadings')
            if result.succeeded:
                self.vg = result.stdout.strip()
                return self.vg
        return None

    def create(self, *args: str, **options: str) -> bool:
        """Create Logical Volume.

        Creates a new LV in the specified VG:
        - Allocates space from VG
        - Creates device mapper device
        - Initializes LV metadata

        Args:
            **options: LV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            lv = LogicalVolume(name='lv0', vg='vg0')
            lv.create(size='1G')
            True
            ```
        """
        if not self.name:
            logging.error('Logical volume name required')
            return False
        if not self.vg:
            logging.error('Volume group required')
            return False

        result = self._run('lvcreate', '-n', self.name, self.vg, *args, **options)
        if result.succeeded:
            self.refresh_report()
        return result.succeeded

    def remove(self, *args: str, **options: str) -> bool:
        """Remove Logical Volume.

        Removes LV and its data:
        - Data is permanently lost
        - Space is returned to VG
        - Device mapper device is removed

        Args:
            *args: Additional volume paths to remove (for removing multiple volumes)
            **options: LV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            # Remove single volume
            lv = LogicalVolume(name='lv0', vg='vg0')
            lv.remove()
            True

            # Remove multiple volumes
            lv = LogicalVolume(name='lv1', vg='vg0')
            lv.remove('vg0/lv2', 'vg0/lv3')
            True
            ```
        """
        if not self.name:
            logging.error('Logical volume name required')
            return False
        if not self.vg:
            logging.error('Volume group required')
            return False

        # Start with this LV
        targets = [f'{self.vg}/{self.name}']

        # Add any additional volumes from args
        if args:
            targets.extend(args)

        result = self._run('lvremove', *targets, **options)
        return result.succeeded

    def change(self, *args: str, **options: str) -> bool:
        """Change Logical Volume attributes.

        Change a general LV attribute:

        Args:
            *args: LV options (see LVMOptions)
            **options: LV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            lv = LogicalVolume(name='lv0', vg='vg0')
            lv.change('-an', 'vg0/lv0')
            True
            ```
        """
        result = self._run('lvchange', *args, **options)
        if result.succeeded:
            self.refresh_report()
        return result.succeeded

    def extend(self, **options: str) -> bool:
        """Extend Logical volume.

        - LV must be initialized (using lvcreate)
        - VG must have sufficient usable space

        Args:
            **options: LV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            lv = LogicalVolume(name='lvol0', vg='vg0')
            lv.extend(extents='100%vg')
            True
            ```
        """
        if not self.vg:
            logging.error('Volume group name required')
            return False
        if not self.name:
            logging.error('Logical volume name required')
            return False

        result = self._run('lvextend', f'{self.vg}/{self.name}', **options)
        if result.succeeded:
            self.refresh_report()
        return result.succeeded

    def lvs(self, *args: str, **options: str) -> CommandResult:
        """Get information about logical volumes.

        Executes the 'lvs' command with optional filtering to display
        information about logical volumes.

        Args:
            *args: Positional args passed through to `lvs` (e.g., LV selector, flags).
            **options: LV command options (see LvmOptions).

        Returns:
            CommandResult object containing command output and status

        Example:
            ```python
            lv = LogicalVolume()
            result = lv.lvs()
            print(result.stdout)
            ```
        """
        return self._run('lvs', *args, **options)

    def convert(self, *args: str, **options: str) -> bool:
        """Convert Logical Volume type.

        Converts LV type (linear, striped, mirror, snapshot, etc):
        - Can change between different LV types
        - May require additional space or devices
        - Some conversions are irreversible

        Args:
            *args: LV conversion arguments
            **options: LV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            lv = LogicalVolume(name='lv0', vg='vg0')
            lv.convert('--type', 'mirror')
            True
            ```
        """
        if not self.vg:
            logging.error('Volume group name required')
            return False
        if not self.name:
            logging.error('Logical volume name required')
            return False

        result = self._run('lvconvert', f'{self.vg}/{self.name}', *args, **options)
        if result.succeeded:
            self.refresh_report()
        return result.succeeded

    def convert_splitmirrors(self, count: int, new_name: str, **options: str) -> tuple[bool, LogicalVolume | None]:
        """Split images from a raid1 or mirror LV and create a new LV.

        Splits the specified number of images from a raid1 or mirror LV and uses them
        to create a new LV with the specified name.

        Args:
            count: Number of mirror images to split
            new_name: Name for the new LV created from split images
            **options: Additional LV options (see LvmOptions)

        Returns:
            Tuple of (success, new_lv) where:
            - success: True if successful, False otherwise
            - new_lv: LogicalVolume object for the new split LV, or None if failed

        Example:
            ```python
            lv = LogicalVolume(name='mirror_lv', vg='vg0')
            success, split_lv = lv.convert_splitmirrors(1, 'split_lv')
            if success:
                print(f'Created new LV: {split_lv.name}')
            ```
        """
        if not self.vg:
            logging.error('Volume group name required')
            return False, None
        if not self.name:
            logging.error('Logical volume name required')
            return False, None

        result = self._run(
            'lvconvert', '--splitmirrors', str(count), '--name', new_name, f'{self.vg}/{self.name}', **options
        )
        success = result.succeeded

        if success:
            self.refresh_report()

        # Create LogicalVolume object for the new split LV
        new_lv = None
        if success:
            try:
                new_lv = LogicalVolume(name=new_name, vg=self.vg)
                if not new_lv.refresh_report():
                    logging.warning(f'Failed to refresh report for new LV {new_name}')
            except (ValueError, OSError) as e:
                logging.warning(f'Failed to create LogicalVolume object for {new_name}: {e}')
                new_lv = None

        return success, new_lv

    def convert_to_thinpool(self, **options: str) -> bool:
        """Convert logical volume to thin pool.

        Converts an existing LV to a thin pool using lvconvert --thinpool.
        The LV must already exist and have sufficient space.

        Args:
            **options: Conversion options including:
                - chunksize: Chunk size for the thin pool (e.g., '256k')
                - zero: Whether to zero the first 4KiB ('y' or 'n')
                - discards: Discard policy ('passdown', 'nopassdown', 'ignore')
                - poolmetadatasize: Size of pool metadata (e.g., '4M')
                - poolmetadata: Name of existing LV to use as metadata
                - readahead: Read-ahead value
                - Other lvconvert options

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            # Basic conversion
            lv = LogicalVolume(name='pool', vg='vg0')
            lv.create(size='100M')
            lv.convert_to_thinpool()

            # Conversion with parameters
            lv.convert_to_thinpool(chunksize='256k', zero='y', discards='nopassdown', poolmetadatasize='4M')

            # Conversion with separate metadata LV
            lv.convert_to_thinpool(poolmetadata='metadata_lv')
            ```
        """
        if not self.vg:
            logging.error('Volume group name required')
            return False
        if not self.name:
            logging.error('Logical volume name required')
            return False

        # Build the lvconvert command
        args = ['--thinpool', f'{self.vg}/{self.name}']

        # Handle special parameter mappings
        if 'chunksize' in options:
            args.extend(['-c', options.pop('chunksize')])
        if 'zero' in options:
            zero_val = options.pop('zero')
            # Convert boolean to string if needed
            if isinstance(zero_val, bool):
                zero_val = 'y' if zero_val else 'n'
            args.extend(['-Z', zero_val])
        if 'readahead' in options:
            readahead_val = options.pop('readahead')
            # Convert numeric to string if needed
            args.extend(['-r', str(readahead_val)])

        result = self._run('lvconvert', *args, **options)
        if result.succeeded:
            self.refresh_report()
        return result.succeeded

    def convert_pool_data(self, **options: str) -> bool:
        """Convert thin pool data component to specified type.

        Converts the thin pool's data component (e.g., from linear to RAID1).
        This is typically used to add mirroring or change the RAID level of the pool's data.

        Args:
            **options: Conversion options including:
                - type: Target type (e.g., 'raid1')
                - mirrors: Number of mirrors for RAID1
                - Other lvconvert options

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            # Convert pool data to RAID1 with 3 mirrors
            pool.convert_pool_data(type='raid1', mirrors='3')
            ```
        """
        if not self.vg:
            logging.error('Volume group name required')
            return False
        if not self.name:
            logging.error('Logical volume name required')
            return False
        if not self.report or not self.report.data_lv:
            logging.error('Pool data LV not found - is this a thin pool?')
            return False

        # Convert the pool's data component
        result = self._run('lvconvert', f'{self.vg}/{self.name}_tdata', **options)
        if result.succeeded:
            self.refresh_report()
        return result.succeeded

    def convert_pool_metadata(self, **options: str) -> bool:
        """Convert thin pool metadata component to specified type.

        Converts the thin pool's metadata component (e.g., from linear to RAID1).
        This is typically used to add mirroring or change the RAID level of the pool's metadata.

        Args:
            **options: Conversion options including:
                - type: Target type (e.g., 'raid1')
                - mirrors: Number of mirrors for RAID1
                - Other lvconvert options

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            # Convert pool metadata to RAID1 with 1 mirror
            pool.convert_pool_metadata(type='raid1', mirrors='1')
            ```
        """
        if not self.vg:
            logging.error('Volume group name required')
            return False
        if not self.name:
            logging.error('Logical volume name required')
            return False
        if not self.report or not self.report.metadata_lv:
            logging.error('Pool metadata LV not found - is this a thin pool?')
            return False

        # Convert the pool's metadata component
        result = self._run('lvconvert', f'{self.vg}/{self.name}_tmeta', **options)
        if result.succeeded:
            self.refresh_report()
        return result.succeeded

    def convert_originname(self, thinpool: str, origin_name: str, **options: str) -> tuple[bool, LogicalVolume | None]:
        """Convert LV to thin LV with named external origin.

        Converts the LV to a thin LV in the specified thin pool, using the original LV
        as an external read-only origin with the specified name.

        Args:
            thinpool: Name of the thin pool (format: vg/pool or just pool if same VG)
            origin_name: Name for the external origin LV
            **options: Additional LV options (see LvmOptions)

        Returns:
            Tuple of (success, origin_lv) where:
            - success: True if successful, False otherwise
            - origin_lv: LogicalVolume object for the read-only origin LV, or None if failed

        Example:
            ```python
            lv = LogicalVolume(name='data_lv', vg='vg0')
            success, origin_lv = lv.convert_originname('vg0/thin_pool', 'data_origin')
            if success:
                print(f'Created origin LV: {origin_lv.name}')
                print(f'Original LV converted to thin LV')
            ```
        """
        if not self.vg:
            logging.error('Volume group name required')
            return False, None
        if not self.name:
            logging.error('Logical volume name required')
            return False, None

        # Ensure thinpool has VG prefix if not provided
        if '/' not in thinpool:
            thinpool = f'{self.vg}/{thinpool}'

        result = self._run(
            'lvconvert',
            '--type',
            'thin',
            '--thinpool',
            thinpool,
            '--originname',
            origin_name,
            f'{self.vg}/{self.name}',
            **options,
        )
        success = result.succeeded

        if success:
            self.refresh_report()

        # Create LogicalVolume object for the origin LV
        origin_lv = None
        if success:
            try:
                origin_lv = LogicalVolume(name=origin_name, vg=self.vg)
                if not origin_lv.refresh_report():
                    logging.warning(f'Failed to refresh report for origin LV {origin_name}')
            except (ValueError, OSError) as e:
                logging.warning(f'Failed to create LogicalVolume object for {origin_name}: {e}')
                origin_lv = None

        return success, origin_lv

    def display(self, **options: str) -> CommandResult:
        """Display Logical Volume details.

        Shows detailed information about the LV:
        - Size and allocation
        - Attributes and permissions
        - Segment information
        - Device mapper details

        Args:
            **options: LV options (see LvmOptions)

        Returns:
            CommandResult object containing command output and status

        Example:
            ```python
            lv = LogicalVolume(name='lv0', vg='vg0')
            result = lv.display()
            print(result.stdout)
            ```
        """
        if not self.vg or not self.name:
            return self._run('lvdisplay', **options)
        return self._run('lvdisplay', f'{self.vg}/{self.name}', **options)

    def reduce(self, *args: str, **options: str) -> bool:
        """Reduce Logical Volume size.

        Reduces LV size (shrinks the volume):
        - Filesystem must be shrunk first
        - Data loss risk if not done carefully
        - Cannot reduce below used space

        Args:
            *args: Additional lvreduce arguments
            **options: LV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            lv = LogicalVolume(name='lv0', vg='vg0')
            lv.reduce(size='500M')
            True

            # With additional arguments
            lv.reduce('--test', size='500M')
            True
            ```
        """
        if not self.vg:
            logging.error('Volume group name required')
            return False
        if not self.name:
            logging.error('Logical volume name required')
            return False
        result = self._run('lvreduce', f'{self.vg}/{self.name}', *args, **options)
        if result.succeeded:
            self.refresh_report()
        return result.succeeded

    def rename(self, new_name: str, **options: str) -> bool:
        """Rename Logical Volume.

        Changes the LV name:
        - Must not conflict with existing LV names
        - Updates device mapper devices
        - May require remounting if mounted

        Args:
            new_name: New name for the LV
            **options: LV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            lv = LogicalVolume(name='lv0', vg='vg0')
            lv.rename('new_lv')
            True
            ```
        """
        if not self.vg:
            logging.error('Volume group name required')
            return False
        if not self.name:
            logging.error('Logical volume name required')
            return False
        if not new_name:
            logging.error('New name required')
            return False

        result = self._run('lvrename', f'{self.vg}/{self.name}', new_name, **options)
        if result.succeeded:
            self.name = new_name
            self.path = f'/dev/{self.vg}/{self.name}'
            self.refresh_report()
        return result.succeeded

    def resize(self, *args: str, **options: str) -> bool:
        """Resize Logical Volume.

        Changes LV size (can grow or shrink):
        - Combines extend and reduce functionality
        - Safer than lvreduce for shrinking
        - Can resize filesystem simultaneously

        Args:
            *args: Additional lvresize arguments (e.g., '-l+2', '-t', '--test')
            **options: LV options (see LvmOptions)

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            lv = LogicalVolume(name='lv0', vg='vg0')
            lv.resize(size='2G')
            True

            # With additional arguments
            lv.resize('-l+2', size='2G')
            True

            # With test flag
            lv.resize('--test', size='2G')
            True
            ```
        """
        if not self.vg:
            logging.error('Volume group name required')
            return False
        if not self.name:
            logging.error('Logical volume name required')
            return False

        result = self._run('lvresize', f'{self.vg}/{self.name}', *args, **options)
        if result.succeeded:
            self.refresh_report()
        return result.succeeded

    def scan(self, *args: str, **options: str) -> CommandResult:
        """Scan for Logical Volumes.

        Scans all devices for LV information:
        - Discovers new LVs
        - Updates device mapper
        - Useful after system changes

        Args:
            **options: LV options (see LvmOptions)

        Returns:
            CommandResult object containing command output and status

        Example:
            ```python
            lv = LogicalVolume()
            result = lv.scan()
            print(result.stdout)
            ```
        """
        return self._run('lvscan', *args, **options)

    def deactivate(self) -> bool:
        """Deactivate Logical Volume."""
        udevadm_settle()
        result = self.change('-an', f'{self.vg}/{self.name}')
        udevadm_settle()
        if result:
            return self.wait_for_lv_deactivation()
        return result

    def activate(self) -> bool:
        """Activate Logical Volume."""
        return self.change('-ay', f'{self.vg}/{self.name}')

    def wait_for_lv_deactivation(self, timeout: int = 30) -> bool:
        """Wait for logical volume to be fully deactivated.

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            True if deactivated successfully, False if timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check LV status using lvs command
            result = self.lvs(f'{self.vg}/{self.name}', '--noheadings', '-o lv_active')
            if result.succeeded and 'active' not in result.stdout.lower():
                # LV is inactive - also verify device node is gone
                if self.path is not None:
                    device_path = Path(self.path)
                    if not device_path.exists():
                        return True
                else:
                    return True  # If no path, consider it deactivated
            time.sleep(2)  # Poll every 2 seconds

        logging.warning(f'LV {self.vg}/{self.name} deactivation timed out after {timeout}s')
        return False

    def change_discards(self, discards_value: str) -> bool:
        """Change discards setting for logical volume.

        Args:
            discards_value: New discards value ('passdown', 'nopassdown', 'ignore')

        Returns:
            True if change succeeded
        """
        if not self.vg or not self.name:
            logging.error('Volume group and logical volume name required')
            return False

        return self.change('--discards', discards_value, f'{self.vg}/{self.name}')

    def create_snapshot(self, snapshot_name: str, *args: str, **options: str) -> LogicalVolume | None:
        """Create snapshot of this LV.

        Creates a snapshot of the current LV (self) with the given snapshot name.
        For thin LVs, creates thin snapshots. For regular LVs, creates COW snapshots.

        Args:
            snapshot_name: Name for the new snapshot LV
            *args: Additional command-line arguments (e.g., '-K', '-k', '--test')
            **options: Snapshot options (see LvmOptions)

        Returns:
            LogicalVolume instance representing the created snapshot, or None if failed

        Example:
            ```python
            # Create origin LV and then snapshot it
            origin_lv = LogicalVolume(name='thin_lv', vg='vg0')
            # ... create the origin LV ...
            # Create thin snapshot (no size needed)
            snap1 = origin_lv.create_snapshot('snap1')

            # Create COW snapshot with ignore activation skip
            snap2 = origin_lv.create_snapshot('snap2', '-K', size='100M')
            ```
        """
        if not self.name:
            logging.error('Origin LV name required')
            return None
        if not self.vg:
            logging.error('Volume group required')
            return None
        if not snapshot_name:
            logging.error('Snapshot name required')
            return None

        # Build snapshot command
        cmd_args = ['-s']

        # Add any additional arguments
        if args:
            cmd_args.extend(args)

        # Add origin (this LV)
        cmd_args.append(f'{self.vg}/{self.name}')

        # Add snapshot name
        cmd_args.extend(['-n', snapshot_name])

        result = self._run('lvcreate', *cmd_args, **options)
        if result.succeeded:
            self.refresh_report()
            # Return new LogicalVolume instance representing the snapshot
            snap = LogicalVolume(name=snapshot_name, vg=self.vg)
            snap.refresh_report()
            return snap
        return None

    def get_pool_usage(self) -> tuple[str, str]:
        """Get thin pool data and metadata usage percentages.

        Returns:
            Tuple of (data_percent, metadata_percent) as strings
        """
        if not self.vg or not self.name:
            logging.error('Volume group and logical volume name required')
            return 'unknown', 'unknown'

        # Get data usage
        data_result = self.lvs(f'{self.vg}/{self.name}', o='data_percent', noheadings='')
        data_percent = data_result.stdout.strip() if data_result.succeeded else 'unknown'

        # Get metadata usage
        meta_result = self.lvs(f'{self.vg}/{self.name}', o='metadata_percent', noheadings='')
        meta_percent = meta_result.stdout.strip() if meta_result.succeeded else 'unknown'

        return data_percent, meta_percent

    @classmethod
    def create_thin_pool(cls, pool_name: str, vg_name: str, **options: str) -> LogicalVolume:
        """Create thin pool with specified options.

        Args:
            pool_name: Pool name
            vg_name: Volume group name
            **options: Pool creation options

        Returns:
            LogicalVolume object for the created pool

        Raises:
            AssertionError: If pool creation fails
        """
        pool = cls(name=pool_name, vg=vg_name)
        options['type'] = 'thin-pool'
        assert pool.create(**options), f'Failed to create thin pool {pool_name}'
        return pool

    @classmethod
    def create_thin_volume(
        cls, lv_name: str, vg_name: str, pool_name: str, virtualsize: str, **options: str
    ) -> LogicalVolume:
        """Create thin volume in specified pool.

        Args:
            lv_name: Thin volume name
            vg_name: Volume group name
            pool_name: Parent pool name
            virtualsize: Virtual size for thin volume
            **options: Thin volume creation options

        Returns:
            LogicalVolume object for the created thin volume

        Raises:
            AssertionError: If volume creation fails
        """
        thin_lv = cls(name=lv_name, pool_name=pool_name, vg=vg_name)
        assert thin_lv.create(virtualsize=virtualsize, type='thin', thinpool=pool_name, **options), (
            f'Failed to create thin volume {lv_name}'
        )
        return thin_lv

    @classmethod
    def from_report(cls, report: LVReport) -> LogicalVolume | None:
        """Create LogicalVolume from LVReport.

        Args:
            report: LV report data

        Returns:
            LogicalVolume instance or None if invalid

        Example:
            ```python
            lv = LogicalVolume.from_report(report)
            ```
        """
        if not report.name or not report.vg:
            return None

        # Create LogicalVolume with report already attached
        return cls(
            name=report.name,
            vg=report.vg,
            path=report.lv_path,
            report=report,  # Attach the report directly
            prevent_report_updates=True,  # Avoid double refresh since report is already fresh
        )

    @classmethod
    def get_all(cls, vg: str | None = None) -> list[LogicalVolume]:
        """Get all Logical Volumes.

        Args:
            vg: Optional volume group to filter by

        Returns:
            List of LogicalVolume instances

        Example:
            ```python
            LogicalVolume.get_all()
            [LogicalVolume(name='lv0', vg='vg0', ...), LogicalVolume(name='lv1', vg='vg1', ...)]
            ```
        """
        logical_volumes: list[LogicalVolume] = []

        # Get all reports
        reports = LVReport.get_all(vg)

        # Create LogicalVolumes from reports
        logical_volumes.extend(lv for report in reports if (lv := cls.from_report(report)))

        return logical_volumes

    def get_data_stripes(self) -> str | None:
        """Get stripe count for thin pool data component.

        For thin pools, the actual stripe information is stored in the data component (_tdata),
        not in the main pool LV. This method returns the stripe count from the data component.

        Returns:
            String representing stripe count, or None if not a thin pool or stripes not found

        Example:
            ```python
            pool = LogicalVolume(name='pool', vg='vg0')
            pool.create(stripes='2', size='100M', type='thin-pool')
            stripe_count = pool.get_data_stripes()  # Returns '2'
            ```
        """
        if not self.report or not self.report.data_lv:
            # Not a thin pool or no data component
            return None

        # Get the data component name (usually pool_name + '_tdata')
        data_lv_name = self.report.data_lv
        if not data_lv_name:
            return None

        # Remove brackets if present (e.g., [pool1_tdata] -> pool1_tdata)
        data_lv_name = data_lv_name.strip('[]')

        # Create LogicalVolume for the data component and get its stripes
        try:
            data_lv = LogicalVolume(name=data_lv_name, vg=self.vg)
            if data_lv.refresh_report() and data_lv.report:
                return data_lv.report.stripes
        except (ValueError, OSError) as e:
            logging.warning(f'Failed to get stripe info from data component {data_lv_name}: {e}')

        return None

    def get_data_stripe_size(self) -> str | None:
        """Get stripe size for thin pool data component.

        For thin pools, the actual stripe size information is stored in the data component (_tdata),
        not in the main pool LV. This method returns the stripe size from the data component.

        Returns:
            String representing stripe size, or None if not a thin pool or stripe size not found

        Example:
            ```python
            pool = LogicalVolume(name='pool', vg='vg0')
            pool.create(stripes='2', stripesize='64k', size='100M', type='thin-pool')
            stripe_size = pool.get_data_stripe_size()  # Returns '64.00k'
            ```
        """
        if not self.report or not self.report.data_lv:
            # Not a thin pool or no data component
            return None

        # Get the data component name (usually pool_name + '_tdata')
        data_lv_name = self.report.data_lv
        if not data_lv_name:
            return None

        # Remove brackets if present (e.g., [pool1_tdata] -> pool1_tdata)
        data_lv_name = data_lv_name.strip('[]')

        # Create LogicalVolume for the data component and get its stripe size
        try:
            data_lv = LogicalVolume(name=data_lv_name, vg=self.vg)
            if data_lv.refresh_report() and data_lv.report:
                return data_lv.report.stripe_size
        except (ValueError, OSError) as e:
            logging.warning(f'Failed to get stripe size info from data component {data_lv_name}: {e}')

        return None

    def __eq__(self, other: object) -> bool:
        """Compare two LogicalVolume instances for equality.

        Two LogicalVolume instances are considered equal if they have the same:
        - name
        - volume group (vg)
        - pool_name (if both have a pool_name)

        For thin LVs that belong to a pool, the pool_name must also match.
        For regular LVs or when either LV has no pool_name, only name and vg are compared.

        Args:
            other: Object to compare with

        Returns:
            True if the LogicalVolume instances are equal, False otherwise

        Example:
            ```python
            lv1 = LogicalVolume(name='lv0', vg='vg0')
            lv2 = LogicalVolume(name='lv0', vg='vg0')
            lv3 = LogicalVolume(name='lv1', vg='vg0')

            assert lv1 == lv2  # Same name and vg
            assert lv1 != lv3  # Different name

            # For thin LVs with pools
            thin1 = LogicalVolume(name='thin1', vg='vg0')
            thin1.pool_name = 'pool'
            thin2 = LogicalVolume(name='thin1', vg='vg0')
            thin2.pool_name = 'pool'
            thin3 = LogicalVolume(name='thin1', vg='vg0')
            thin3.pool_name = 'other_pool'

            assert thin1 == thin2  # Same name, vg, and pool
            assert thin1 != thin3  # Different pool
            ```
        """
        if not isinstance(other, LogicalVolume):
            return False
        if self.pool_name is None or other.pool_name is None:
            return self.name == other.name and self.vg == other.vg
        return self.name == other.name and self.vg == other.vg and self.pool_name == other.pool_name

    def __hash__(self) -> int:
        """Generate hash for LogicalVolume instance.

        The hash is based on the combination of name, volume group (vg), and pool_name.
        This allows LogicalVolume instances to be used in sets and as dictionary keys.
        The hash is consistent with the equality comparison in __eq__.

        Returns:
            int: Hash value based on (name, vg, pool_name) tuple

        Example:
            ```python
            lv1 = LogicalVolume(name='lv0', vg='vg0')
            lv2 = LogicalVolume(name='lv0', vg='vg0')

            # Can be used in sets
            lv_set = {lv1, lv2}  # Only one instance since they're equal

            # Can be used as dictionary keys
            lv_dict = {lv1: 'some_value'}
            ```
        """
        return hash((self.name, self.vg, self.pool_name))
