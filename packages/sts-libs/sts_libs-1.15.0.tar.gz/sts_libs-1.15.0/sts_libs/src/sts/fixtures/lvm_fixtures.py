# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""LVM test fixtures.

This module provides fixtures for testing LVM (Logical Volume Management):
- Package installation and cleanup
- Service management
- Device configuration
- VDO (Virtual Data Optimizer) support

Fixture Dependencies:
1. _lvm_test (base fixture)
   - Installs LVM packages
   - Manages volume cleanup
   - Logs system information

2. _vdo_test (depends on _lvm_test)
   - Installs VDO packages
   - Manages kernel module
   - Provides data reduction features

Common Usage:
1. Basic LVM testing:
   @pytest.mark.usefixtures('_lvm_test')
   def test_lvm():
       # LVM utilities are installed
       # Volumes are cleaned up after test

2. VDO-enabled testing:
   @pytest.mark.usefixtures('_vdo_test')
   def test_vdo():
       # VDO module is loaded
       # Data reduction is available

Error Handling:
- Package installation failures fail the test
- Module loading failures fail the test
- Volume cleanup runs even if test fails
- Service issues are logged
"""

from __future__ import annotations

import logging
from os import getenv
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from sts import dmpd, lvm
from sts.udevadm import udevadm_settle
from sts.utils.cmdline import run
from sts.utils.errors import ModuleInUseError
from sts.utils.files import Directory, fallocate, mkfs, mount, umount
from sts.utils.modules import ModuleManager
from sts.utils.packages import log_package_versions
from sts.utils.system import SystemManager

if TYPE_CHECKING:
    from collections.abc import Generator

    from sts.blockdevice import BlockDevice

# Constants
LVM_PACKAGE_NAME = 'lvm2'
VDO_PACKAGE_NAME = 'vdo'


@pytest.fixture(scope='class')
def _lvm_test() -> None:
    """Set up LVM environment.

    This fixture provides the foundation for LVM testing:
    - Installs LVM utilities (lvm2 package)
    - Logs system information for debugging

    Package Installation:
    - lvm2: Core LVM utilities
    - Required device-mapper modules

    System Information:
    - LVM version
    - Device-mapper status

    Example:
        ```python
        @pytest.mark.usefixtures('_lvm_test')
        def test_lvm():
            # Create and test LVM volumes
        ```
    """
    system = SystemManager()
    assert system.package_manager.install(LVM_PACKAGE_NAME)
    log_package_versions(LVM_PACKAGE_NAME)


@pytest.fixture(scope='class')
def load_vdo_module(_lvm_test: None) -> str:
    """Load the appropriate VDO kernel module based on kernel version.

    This fixture installs the VDO package and loads the correct VDO kernel module
    depending on the system's kernel version:
    - For kernel 6.9+: uses dm-vdo module (built into kernel)
    - For kernel 6.8 and earlier: uses kvdo module (from kmod-kvdo package)

    The fixture handles kernel version detection and falls back to dm-vdo if
    version parsing fails.

    Args:
        _lvm_test: LVM test fixture dependency (ensures LVM setup is complete)

    Returns:
        str: Name of the loaded VDO module ('dm-vdo' or 'kvdo')

    Raises:
        AssertionError: If VDO package installation or module loading fails
    """
    module = 'dm_vdo'
    system = SystemManager()
    assert system.package_manager.install(VDO_PACKAGE_NAME)
    log_package_versions(VDO_PACKAGE_NAME)
    try:
        k_version = system.info.kernel
        if k_version:
            k_version = k_version.split('.')
            # dm-vdo is available from kernel 6.9, for older version it's available
            # from kmod-kvdo package
            if int(k_version[0]) < 6 or (int(k_version[0]) == 6 and int(k_version[1]) <= 8):
                logging.info('Using kmod-kvdo')
                assert system.package_manager.install('kmod-kvdo')
                log_package_versions('kmod-kvdo')
                module = 'kvdo'
    except (ValueError, IndexError):
        # if we can't get kernel version, just try to load dm-vdo
        logging.warning('Unable to parse kernel version; defaulting to dm-vdo')

    kmod = ModuleManager()
    assert kmod.load(name=module)

    return module


@pytest.fixture(scope='class')
def _vdo_test(load_vdo_module: str) -> Generator[None, None, None]:
    """Set up VDO environment.

    Args:
       load_vdo_module: Load VDO module

    Features:
       - Automatic module loading/unloading

    Example:
       @pytest.mark.usefixtures('_vdo_test')
       def test_vdo():
           # Test VDO functionality
           pass
    """
    module = load_vdo_module

    yield

    kmod = ModuleManager()
    try:
        # ignore failures
        if not kmod.unload(name=module):
            logging.info(f'VDO module {module} could not be unloaded cleanly; continuing.')
    except (ModuleInUseError, RuntimeError):
        logging.info(f'Ignoring unload error for {module}.')


@pytest.fixture
def setup_vg(
    _lvm_test: None, ensure_minimum_devices_with_same_block_sizes: list[BlockDevice]
) -> Generator[str, None, None]:
    """Set up an LVM Volume Group (VG) with Physical Volumes (PVs) for testing.

    This fixture creates a Volume Group using the provided block devices. It handles the creation
    of Physical Volumes from the block devices and ensures proper cleanup after tests, even if
    they fail.

    Args:
        ensure_minimum_devices_with_same_block_sizes: List of BlockDevice objects with matching
            block sizes to be used for creating Physical Volumes.

    Yields:
        str: Name of the created Volume Group.

    Raises:
        AssertionError: If PV creation fails for any device.

    Example:
        def test_volume_group(setup_vg):
            vg_name = setup_vg
            # Use vg_name in your test...
    """
    vg_name = getenv('STS_VG_NAME', 'stsvg0')
    pvs = []

    try:
        # Create PVs
        for device in ensure_minimum_devices_with_same_block_sizes:
            device_name = str(device.path).replace('/dev/', '')
            device_path = str(device.path)

            pv = lvm.PhysicalVolume(name=device_name, path=device_path)
            assert pv.create(), f'Failed to create PV on device {device_path}'
            pvs.append(pv)

        # Create VG
        vg = lvm.VolumeGroup(name=vg_name, pvs=[pv.path for pv in pvs])
        assert vg.create(), f'Failed to create VG {vg_name}'

        yield vg_name

    finally:
        # Cleanup in reverse order
        vg = lvm.VolumeGroup(name=vg_name)
        if not vg.remove():
            logging.warning(f'Failed to remove VG {vg_name}')

        for pv in pvs:
            if not pv.remove():
                logging.warning(f'Failed to remove PV {pv.path}')


@pytest.fixture
def setup_loopdev_vg(_lvm_test: None, loop_devices: list[str]) -> Generator[str, None, None]:
    """Set up a volume group using loop devices.

    This fixture creates a volume group using the provided loop devices.
    The volume group name can be customized using the STS_VG_NAME environment
    variable, otherwise defaults to 'stsvg0'.

    Args:
        loop_devices: List of loop device paths to use as physical volumes.

    Yields:
        str: The name of the created volume group.

    Examples:
        Basic usage with custom loop device configuration:

        ```python
        @pytest.mark.parametrize('loop_devices', [{'count': 1, 'size_mb': 4096}], indirect=True)
        @pytest.mark.usefixtures('setup_loopdev_vg')
        def test_large_vg_operations(setup_loopdev_vg):
            vg_name = setup_loopdev_vg
            # Create logical volumes in the 4GB VG
            lv = lvm.LogicalVolume(name='testlv', vg=vg_name, size='1G')
            assert lv.create()
        ```

        Using with multiple loop devices:

        ```python
        @pytest.mark.parametrize('loop_devices', [{'count': 2, 'size_mb': 2048}], indirect=True)
        @pytest.mark.usefixtures('setup_loopdev_vg')
        def test_multi_pv_vg(setup_loopdev_vg):
            vg_name = setup_loopdev_vg
            vg = lvm.VolumeGroup(name=vg_name)
            assert vg.exists()
        ```
    """
    vg_name = getenv('STS_VG_NAME', 'stsvg0')
    pvs = []

    try:
        for device in loop_devices:
            pv = lvm.PhysicalVolume(name=device, path=device)
            assert pv.create(), f'Failed to create PV on device {device}'
            pvs.append(pv)

        vg = lvm.VolumeGroup(name=vg_name, pvs=[pv.path for pv in pvs])
        assert vg.create(), f'Failed to create VG {vg_name}'

        yield vg_name

    finally:
        vg = lvm.VolumeGroup(name=vg_name)
        if not vg.remove():
            logging.warning(f'Failed to remove VG {vg_name}')

        for pv in pvs:
            if not pv.remove():
                logging.warning(f'Failed to remove PV {pv.path}')


@pytest.fixture
def lv_quarter_of_vg(_lvm_test: None, setup_vg: str) -> Generator[str, None, None]:
    """Create a logical volume using 25% of a volume group.

    Creates:
    - Logical volume 'lv1' using 25% of VG space

    Yields:
        str: device path
    """
    lv_name = getenv('LV_NAME', 'stscow25vglv1')
    vg_name = setup_vg
    # Create LV
    lv = lvm.LogicalVolume(name=lv_name, vg=vg_name)
    assert lv.create(extents='25%vg')

    yield f'/dev/{vg_name}/{lv_name}'

    # Cleanup
    lv = lvm.LogicalVolume(name=lv_name, vg=vg_name)
    assert lv.remove()


@pytest.fixture
def thin_lv_quarter_of_vg(_lvm_test: None, setup_vg: str) -> Generator[str, None, None]:
    """Create a thin logical volume using a thin pool that uses 25% of a volume group.

    Creates:
    - Thin pool using 25% of the provided volume group space
    - Thin logical volume with 512MB virtual size

    Yields:
        str: Device path to the thin logical volume

    """
    lv_name = getenv('LV_NAME', 'ststhin25vglv1')
    vg_name = setup_vg
    pool_name = getenv('THIN_POOL_NAME', 'stspool1_25vg')

    # Create thin pool
    lv = lvm.LogicalVolume(name=lv_name, vg=vg_name)
    assert lv.create(
        type='thin',
        thinpool=pool_name,
        extents='25%VG',
        virtualsize='512M',
    )

    yield f'/dev/{vg_name}/{lv_name}'

    # Cleanup
    lv = lvm.LogicalVolume(name=lv_name, vg=vg_name)
    assert lv.remove()

    pool_lv = lvm.LogicalVolume(name=pool_name, vg=vg_name)
    assert pool_lv.remove()


@pytest.fixture
def mount_lv(lv_quarter_of_vg: str) -> Generator[Directory, None, None]:
    """Mount a logical volume on a test directory.

    Args:
        lv_quarter_of_vg: Fixture providing LV info

    Yields:
        Directory: Directory representation of mount point
    """
    dev_path = lv_quarter_of_vg
    mount_point = getenv('STS_LV_MOUNT_POINT', '/mnt/lvcowmntdir')

    # Create filesystem on the LV
    assert mkfs(device=dev_path, fs_type='xfs')

    # Create mount point directory using Directory class
    mnt_dir = Directory(Path(mount_point), create=True)
    assert mnt_dir.exists, f'Failed to create mount point directory {mount_point}'

    # Mount the LV
    assert mount(device=dev_path, mountpoint=mount_point)

    yield mnt_dir

    # Cleanup
    assert umount(mountpoint=mount_point)
    mnt_dir.remove_dir()


@pytest.fixture
def mount_thin_lv(thin_lv_quarter_of_vg: str) -> Generator[Directory, None, None]:
    """Mount a thin logical volume on a test directory.

    Args:
        thin_lv_quarter_of_vg: Fixture providing thin LV info

    Yields:
        Directory: Directory representation of mount point
    """
    dev_path = thin_lv_quarter_of_vg
    mount_point = getenv('STS_THIN_LV_MOUNT_POINT', '/mnt/thinlvmntdir')

    # Create filesystem on the thin LV
    assert mkfs(device=dev_path, fs_type='xfs')

    # Create mount point directory using Directory class
    mnt_dir = Directory(Path(mount_point), create=True)
    assert mnt_dir.exists, f'Failed to create mount point directory {mount_point}'

    # Mount the LV
    assert mount(device=dev_path, mountpoint=mount_point)

    yield mnt_dir

    # Cleanup
    assert umount(mountpoint=mount_point)
    mnt_dir.remove_dir()


def _create_multiple_lv_mntpoints(
    vg_name: str,
    lv_type: str = 'cow',
    lv_name: str | None = None,
    mount_point: str | None = None,
    pool_name: str | None = None,
    fs_type: str | None = None,
    num_of_mntpoints: int | None = None,
    virtualsize: str | None = None,
    percentage_of_vg_to_use: int | None = None,
) -> Generator[list[Directory], None, None]:
    """Creating multiple logical volumes with mounted filesystems.

    Args:
        vg_name: Volume group name
        lv_type: Type of logical volume ('cow' or 'thin')
        lv_name: Base name for logical volumes (defaults based on lv_type)
        mount_point: Base mount point path (defaults based on lv_type)
        pool_name: Base name for thin pools (only used for thin LVs)
        fs_type: Filesystem type (defaults to env var or 'xfs')
        num_of_mntpoints: Number of mount points (defaults to env var or 6)
        virtualsize: Virtual size for thin logical volumes (defaults to '512M')
        percentage_of_vg_to_use: Percentage of volume group to use across all LVs (defaults to 50)

    Yields:
        list[Directory]: List of Directory objects representing the mount points
    """
    # Set defaults based on lv_type
    if lv_type == 'thin':
        default_lv_name = 'ststhinmultiplemntpoints'
        default_mount_point = '/mnt/lvthinmntdir'
        default_pool_name = 'stspool1mutiplethin'
    else:  # cow
        default_lv_name = 'stscowmultiplemntpoints'
        default_mount_point = '/mnt/lvcowmntdir'
        default_pool_name = None
    percentage_of_vg_to_use = percentage_of_vg_to_use or 50
    default_virtualsize = '512M'
    # Use provided values or fall back to environment variables or defaults
    lv_name = lv_name or getenv('LV_NAME', default_lv_name)
    mount_point = mount_point or getenv('STS_LV_MOUNT_POINT', default_mount_point)
    fs_type = fs_type or getenv('STS_LV_FS_TYPE', 'xfs')
    virtualsize = virtualsize or getenv('STS_LV_VIRTUALSIZE', default_virtualsize)

    if lv_type == 'thin':
        pool_name = pool_name or getenv('STS_THIN_POOL_NAME', default_pool_name)

    if num_of_mntpoints is None:
        try:
            num_of_mntpoints = int(getenv('STS_COW_MNTPOINT_NUMBER', '6'))
        except (ValueError, TypeError):
            pytest.fail('STS_COW_MNTPOINT_NUMBER variable has incorrect value!')

    vg_percentage = int(percentage_of_vg_to_use / int(num_of_mntpoints))
    sources: list[Directory] = []
    logical_volumes: list[lvm.LogicalVolume] = []

    # Create LV
    for num in range(num_of_mntpoints):
        lv = lvm.LogicalVolume(name=f'{lv_name}{num}', vg=vg_name)
        logical_volumes.append(lv)

        # Create LV based on type
        if lv_type == 'thin':
            assert lv.create(
                type='thin',
                thinpool=f'{pool_name}{num}',
                extents=f'{vg_percentage}%vg',
                virtualsize=virtualsize,
            )
        elif lv_type == 'cow':
            assert lv.create(extents=f'{vg_percentage}%vg')
        else:
            pytest.fail(f'Invalid LV type: {lv_type}')

        dev_path = f'/dev/{vg_name}/{lv_name}{num}'
        assert mkfs(device=dev_path, fs_type=fs_type)

        mnt_dir = Directory(Path(f'{mount_point}{num}'), create=True)
        assert mnt_dir.exists, f'Failed to create mount point directory {mount_point}{num}'
        # Mount the LV
        assert mount(device=dev_path, mountpoint=f'{mount_point}{num}')
        sources.append(mnt_dir)

    yield sources

    # Cleanup
    for num in range(num_of_mntpoints):
        assert umount(mountpoint=f'{mount_point}{num}')
        mnt_dir = Directory(Path(f'{mount_point}{num}'), create=True)
        mnt_dir.remove_dir()
    for lv in logical_volumes:
        assert lv.remove()


@pytest.fixture
def prepare_multiple_cow_mntpoints(
    _lvm_test: None, setup_vg: str, request: pytest.FixtureRequest
) -> Generator[list[Directory], None, None]:
    """Create multiple COW logical volumes with mounted filesystems for testing.

    This fixture creates multiple logical volumes within a volume group, formats them
    with filesystems, and mounts them to separate mount points. It's designed for
    testing Copy-on-Write (COW) snapshots with multiple source volumes.

    Supports parameter customization via pytest.param or environment variables.

    Yields:
        list[Directory]: List of Directory objects representing the mount points
    """
    # Get parameters from request if provided, otherwise use environment variables
    params = getattr(request, 'param', {})

    yield from _create_multiple_lv_mntpoints(
        vg_name=setup_vg,
        lv_type='cow',
        **params,
    )


@pytest.fixture
def prepare_multiple_thin_mntpoints(
    _lvm_test: None, setup_vg: str, request: pytest.FixtureRequest
) -> Generator[list[Directory], None, None]:
    """Create multiple thin logical volumes with mounted filesystems for testing.

    This fixture creates multiple thin logical volumes within a volume group, each with
    its own thin pool, formats them with filesystems, and mounts them to separate mount
    points. It's designed for testing thin provisioning scenarios with multiple volumes.

    Supports parameter customization via pytest.param or environment variables.

    Yields:
        list[Directory]: List of Directory objects representing the mount points
    """
    # Get parameters from request if provided, otherwise use environment variables
    params = getattr(request, 'param', {})

    yield from _create_multiple_lv_mntpoints(
        vg_name=setup_vg,
        lv_type='thin',
        **params,
    )


@pytest.fixture
def prepare_multiple_cow_mntpoints_ext4(_lvm_test: None, setup_vg: str) -> Generator[list[Directory], None, None]:
    """Create multiple COW logical volumes with ext4 filesystems for testing.

    This is a convenience wrapper that configures COW logical volumes
    to use ext4 filesystem by default.

    Yields:
        list[Directory]: List of Directory objects representing the mount points
    """
    yield from _create_multiple_lv_mntpoints(vg_name=setup_vg, lv_type='cow', fs_type='ext4')


@pytest.fixture
def prepare_multiple_thin_mntpoints_ext4(_lvm_test: None, setup_vg: str) -> Generator[list[Directory], None, None]:
    """Create multiple thin logical volumes with ext4 filesystems for testing.

    This is a convenience wrapper that configures thin logical volumes
    to use ext4 filesystem by default.

    Yields:
        list[Directory]: List of Directory objects representing the mount points
    """
    yield from _create_multiple_lv_mntpoints(vg_name=setup_vg, lv_type='thin', fs_type='ext4')


@pytest.fixture(scope='class')
def install_dmpd(_lvm_test: None) -> None:
    """Install required packages for device-mapper-persistent-data tools.

    This fixture installs the device-mapper-persistent-data package which provides
    cache metadata tools like cache_check, cache_dump, cache_repair, etc.

    Example:
        ```python
        @pytest.mark.usefixtures('install_dmpd_packages')
        def test_cache_tools():
            # DMPD tools are now available
            pass
        ```
    """
    system = SystemManager()
    package = 'device-mapper-persistent-data'

    assert system.package_manager.install(package), f'Failed to install {package}'


# New modular fixtures for better reusability


@pytest.fixture
def basic_thin_pool(setup_loopdev_vg: str) -> Generator[dict[str, Any], None, None]:
    """Create a basic thin pool for testing.

    Creates a 3GB thin pool that can accommodate thin volumes with filesystem support.

    Args:
        setup_loopdev_vg: Volume group name from setup_loopdev_vg fixture

    Yields:
        dict: Information about the created thin pool
    """
    vg_name = setup_loopdev_vg
    pool_name = 'thinpool'

    # Create thin pool (3GB to accommodate 10x300MB thin volumes with filesystem support)
    pool_lv = lvm.LogicalVolume(name=pool_name, vg=vg_name)
    assert pool_lv.create(type='thin-pool', size='3G')

    pool_info = {
        'vg_name': vg_name,
        'pool_name': pool_name,
        'pool_path': f'/dev/{vg_name}/{pool_name}',
    }

    yield pool_info

    # Cleanup
    pool_lv.remove()


@pytest.fixture
def thin_volumes_with_lifecycle(basic_thin_pool: dict[str, Any]) -> Generator[dict[str, Any], None, None]:
    """Create thin volumes and perform filesystem lifecycle operations.

    Creates 10 thin volumes of 300MB each and performs filesystem operations
    (create, mount, unmount, deactivate) to generate metadata activity.

    Args:
        basic_thin_pool: Basic thin pool information from basic_thin_pool fixture

    Yields:
        dict: Extended pool information with thin volume details
    """
    pool_info = basic_thin_pool.copy()
    vg_name = pool_info['vg_name']
    pool_name = pool_info['pool_name']
    thin_base_name = 'thinvol'

    # Create 10 thin volumes of 300MB each (minimum size for filesystem support)
    thin_lvs = []
    for i in range(10):
        thin_name = f'{thin_base_name}{i}'
        thin_lv = lvm.LogicalVolume(name=thin_name, vg=vg_name)
        assert thin_lv.create(type='thin', thinpool=pool_name, virtualsize='300M')
        thin_lvs.append(thin_lv)

        # Create filesystem and mount/unmount to generate metadata activity
        # This matches the mount_lv/umount_lv logic from setup.py
        thin_path = f'/dev/{vg_name}/{thin_name}'
        mount_point = f'/mnt/{thin_name}'

        mnt_dir = Directory(Path(mount_point), create=True)
        assert mkfs(device=thin_path, fs_type='xfs')
        assert mount(device=thin_path, mountpoint=mount_point)
        assert umount(mountpoint=mount_point)
        mnt_dir.remove_dir()

        # Deactivate thin LV with verification
        assert thin_lv.deactivate()

    pool_info.update(
        {
            'thin_count': 10,
            'thin_base_name': thin_base_name,
            'thin_lvs': thin_lvs,
        }
    )

    yield pool_info

    # Cleanup thin volumes
    for thin_lv in thin_lvs:
        thin_lv.remove()


@pytest.fixture
def swap_volume(setup_loopdev_vg: str) -> Generator[dict[str, Any], None, None]:
    """Create a swap volume for metadata operations.

    Creates a 75MB swap logical volume that can be used for metadata swapping.

    Args:
        setup_loopdev_vg: Volume group name from setup_loopdev_vg fixture

    Yields:
        dict: Information about the created swap volume
    """
    vg_name = setup_loopdev_vg
    swap_name = 'swapvol'

    # Create swap LV (75MB as per original setup)
    swap_lv = lvm.LogicalVolume(name=swap_name, vg=vg_name)
    assert swap_lv.create(size='75M')

    swap_info = {
        'vg_name': vg_name,
        'swap_name': swap_name,
        'swap_path': f'/dev/{vg_name}/{swap_name}',
        'swap_lv': swap_lv,
    }

    yield swap_info

    # Cleanup
    swap_lv.remove()


@pytest.fixture
def metadata_snapshot(thin_volumes_with_lifecycle: dict[str, Any]) -> Generator[dict[str, Any], None, None]:
    """Create metadata snapshot for thin pool.

    Creates a metadata snapshot while the thin pool is active and handles
    the suspend/message/resume sequence for snapshot creation.

    Args:
        thin_volumes_with_lifecycle: Thin volumes setup from thin_volumes_with_lifecycle fixture

    Yields:
        dict: Pool information with snapshot status
    """
    pool_info = thin_volumes_with_lifecycle.copy()
    vg_name = pool_info['vg_name']
    pool_name = pool_info['pool_name']

    udevadm_settle()

    # Create metadata snapshot while pool is still active
    pool_device = f'/dev/mapper/{vg_name}-{pool_name}-tpool'

    # Suspend -> message -> resume sequence (matching metadata_snapshot from setup.py)
    suspend_result = run(f'dmsetup suspend {pool_device}')
    assert suspend_result.succeeded

    message_result = run(f'dmsetup message {pool_device} 0 reserve_metadata_snap')
    assert message_result.succeeded

    resume_result = run(f'dmsetup resume {pool_device}')
    assert resume_result.succeeded

    # Now deactivate thin volumes (matching deactivate_thinvols from setup)
    for i in range(int(pool_info['thin_count'])):
        thin_name = f'{pool_info["thin_base_name"]}{i}'
        thin_lv = lvm.LogicalVolume(name=thin_name, vg=vg_name)
        thin_lv.deactivate()

    udevadm_settle()

    pool_info.update(
        {
            'pool_device': pool_device,
            'has_snapshot': True,
        }
    )

    yield pool_info

    # Release metadata snapshot
    run(f'dmsetup message {pool_device} 0 release_metadata_snap')


@pytest.fixture
def metadata_swap(metadata_snapshot: dict[str, Any], swap_volume: dict[str, Any]) -> dict[str, Any]:
    """Perform metadata swap operation between thin pool and swap volume.

    Deactivates the thin pool and swap volume, then uses lvconvert to swap
    the metadata from the thin pool to the swap volume.

    Args:
        metadata_snapshot: Metadata snapshot setup from metadata_snapshot fixture
        swap_volume: Swap volume setup from swap_volume fixture

    Returns:
        dict: Combined information with metadata device details
    """
    pool_info = metadata_snapshot.copy()
    swap_info = swap_volume

    # Ensure both fixtures reference the same VG
    assert pool_info['vg_name'] == swap_info['vg_name'], 'Pool and swap must be in same VG'

    vg_name = pool_info['vg_name']
    pool_name = pool_info['pool_name']
    swap_name = swap_info['swap_name']

    # Deactivate pool and swap (matching swap_metadata logic from setup.py)
    pool_lv = lvm.LogicalVolume(name=pool_name, vg=vg_name)
    pool_lv.deactivate()
    swap_lv = lvm.LogicalVolume(name=swap_name, vg=vg_name)
    swap_lv.deactivate()

    logging.info(run('lvs').stdout)
    udevadm_settle()

    # Swap metadata using lv_convert --poolmetadata (exact logic from setup.py)
    # This converts the swap LV to hold the thin pool's metadata
    convert_cmd = f'lvconvert -y --thinpool {vg_name}/{pool_name} --poolmetadata {vg_name}/{swap_name}'
    convert_result = run(convert_cmd)
    assert convert_result.succeeded

    # Activate swap volume (now containing metadata)
    swap_lv = lvm.LogicalVolume(name=swap_name, vg=vg_name)
    swap_lv.activate()

    # Use swap LV as metadata device (it now contains the metadata)
    metadata_dev = f'/dev/{vg_name}/{swap_name}'

    # Combine information from both fixtures
    combined_info = pool_info.copy()
    combined_info.update(swap_info)
    combined_info.update(
        {
            'metadata_dev': metadata_dev,
        }
    )

    return combined_info


@pytest.fixture
def metadata_backup(metadata_swap: dict[str, Any]) -> Generator[dict[str, Any], None, None]:
    """Create metadata backup files for testing.

    Creates metadata backup using thin_dump and prepares repair file for testing.

    Args:
        metadata_swap: Metadata swap setup from metadata_swap fixture

    Yields:
        dict: Extended information with backup file paths
    """
    vol_info = metadata_swap.copy()
    metadata_dev = vol_info['metadata_dev']
    metadata_backup_path = Path('/var/tmp/metadata')
    metadata_repair_path = Path('/var/tmp/metadata_repair')

    # Create metadata backup using thin_dump (matching backup_metadata from main.fmf)
    backup_cmd = f'thin_dump --format xml --repair {metadata_dev} --output {metadata_backup_path}'
    backup_result = run(backup_cmd)
    assert backup_result.succeeded

    # Create proper metadata files for testing
    # 1. Create empty repair file with proper allocation (5MB should be enough)
    assert fallocate(metadata_repair_path, length='5M')

    # 2. Create a working metadata file that thin_repair can actually repair
    metadata_working_path = Path('/var/tmp/metadata_working')
    assert fallocate(metadata_working_path, length='5M')

    # 3. Populate the working metadata file with valid data from backup
    restore_working_cmd = f'thin_restore -i {metadata_backup_path} -o {metadata_working_path}'
    restore_working_result = run(restore_working_cmd)
    assert restore_working_result.succeeded, f'Failed to create working metadata: {restore_working_result.stderr}'

    # Update vol_info to include all metadata files
    vol_info.update(
        {
            'metadata_backup_path': metadata_backup_path,
            'metadata_repair_path': metadata_repair_path,
            'metadata_working_path': metadata_working_path,
        }
    )

    yield vol_info

    # Cleanup files
    run(f'rm -f {metadata_backup_path} {metadata_repair_path} {metadata_working_path}')


@pytest.fixture
def restored_thin_pool(metadata_backup: dict[str, Any]) -> Generator[dict[str, Any], None, None]:
    """Restore thin pool to a usable state after metadata operations.

    WARNING: Use this fixture ONLY for tests that specifically need an active thin pool
    (like thin_trim). Most DMPD tools are designed to work with "broken" metadata and
    should use setup_thin_metadata_for_dmpd instead, which preserves the intentionally
    inconsistent metadata state.

    This fixture uses thin_restore to repair the metadata and make the pool activatable.

    Args:
        metadata_backup: Metadata backup setup from metadata_backup fixture

    Yields:
        dict: Pool information with restored pool that can be activated
    """
    vol_info = metadata_backup.copy()
    vg_name = vol_info['vg_name']
    pool_name = vol_info['pool_name']
    swap_name = vol_info['swap_name']
    metadata_backup_path = vol_info['metadata_backup_path']
    metadata_dev = vol_info['metadata_dev']

    # Step 1: Use thin_restore to repair the metadata in the swap device
    logging.info(f'Restoring metadata to repair inconsistencies in {metadata_dev}')
    restore_cmd = f'thin_restore -i {metadata_backup_path} -o {metadata_dev}'
    restore_result = run(restore_cmd)
    assert restore_result.succeeded, f'Failed to restore metadata: {restore_result.stderr}'

    # Step 2: Deactivate both volumes before swapping metadata back
    pool_lv = lvm.LogicalVolume(name=pool_name, vg=vg_name)
    pool_lv.deactivate()  # Pool might already be deactivated
    swap_lv = lvm.LogicalVolume(name=swap_name, vg=vg_name)
    swap_lv.deactivate()
    udevadm_settle()

    # Step 3: "Swap back metadata" - restore the fixed metadata to the pool
    # This matches the "Swapping back metadata" step from python-stqe cleanup
    swap_back_cmd = f'lvconvert -y --thinpool {vg_name}/{pool_name} --poolmetadata {vg_name}/{swap_name}'
    swap_back_result = run(swap_back_cmd)
    assert swap_back_result.succeeded, f'Failed to swap metadata back to pool: {swap_back_result.stderr}'

    # Step 4: Reactivate the swap volume and verify device accessibility
    swap_lv = lvm.LogicalVolume(name=swap_name, vg=vg_name)
    activate_swap_result = swap_lv.activate()
    assert activate_swap_result, 'Failed to reactivate swap volume'
    udevadm_settle()

    # Verify the metadata device exists and update the path if needed
    metadata_dev_path = f'/dev/{vg_name}/{swap_name}'
    check_dev = run(f'ls -la {metadata_dev_path}')
    if not check_dev.succeeded:
        # Try alternative device path
        metadata_dev_path = f'/dev/mapper/{vg_name}-{swap_name}'
        check_dev_alt = run(f'ls -la {metadata_dev_path}')
        assert check_dev_alt.succeeded, f'Swap device not accessible at {metadata_dev_path}'

    # Update the metadata_dev path to the verified working path
    vol_info['metadata_dev'] = metadata_dev_path

    # Now the pool should have the fixed metadata and be activatable
    vol_info.update(
        {
            'pool_can_activate': True,
            'metadata_restored': True,
            'metadata_swapped_back': True,
        }
    )

    yield vol_info

    # Leave pool in deactivated state for cleanup
    pool_lv = lvm.LogicalVolume(name=pool_name, vg=vg_name)
    pool_lv.deactivate()  # Ignore errors


# Original fixtures refactored to use the new modular approach


@pytest.fixture
def setup_thin_pool_with_vols(
    thin_volumes_with_lifecycle: dict[str, str], swap_volume: dict[str, str]
) -> dict[str, str]:
    """Set up thin pool with thin volumes for DMPD testing.

    This is a backward-compatible fixture that combines the modular fixtures
    to recreate the original functionality. Uses the new modular approach internally.

    Args:
        thin_volumes_with_lifecycle: Thin volumes setup from thin_volumes_with_lifecycle fixture
        swap_volume: Swap volume setup from swap_volume fixture

    Returns:
        dict: Information about created volumes (compatible with original format)
    """
    pool_info = thin_volumes_with_lifecycle.copy()
    swap_info = swap_volume

    # Ensure both fixtures reference the same VG
    assert pool_info['vg_name'] == swap_info['vg_name'], 'Pool and swap must be in same VG'

    # Combine information from both fixtures to match original format
    volume_info = pool_info.copy()
    volume_info.update(
        {
            'swap_name': swap_info['swap_name'],
            'swap_path': swap_info['swap_path'],
        }
    )

    return volume_info


@pytest.fixture
def setup_thin_metadata_for_dmpd(install_dmpd: None, metadata_backup: dict[str, Any]) -> dict[str, Any]:
    """Set up thin metadata configuration for DMPD tool testing with snapshot support.

    This fixture creates the intended "broken" metadata state that DMPD tools are designed
    to detect, analyze, and repair. The metadata swap operation intentionally leaves the
    thin pool in an inconsistent state (transaction_id mismatch) to test that DMPD tools
    can properly handle corrupted/problematic metadata scenarios.

    Args:
        install_dmpd: DMPD package installation fixture
        metadata_backup: Metadata backup setup from metadata_backup fixture

    Returns:
        dict: Extended volume information with intentionally inconsistent metadata for testing
    """
    # DMPD packages are installed via install_dmpd fixture
    _ = install_dmpd

    # Use metadata_backup which preserves the "broken" metadata state for DMPD testing
    return metadata_backup.copy()


# Cache-specific fixtures


@pytest.fixture
def cache_volumes(setup_loopdev_vg: str) -> Generator[dict[str, Any], None, None]:
    """Create cache volumes for testing.

    Creates cache metadata, origin, and data logical volumes that can be used
    for creating cache pools and cached volumes.

    Args:
        setup_loopdev_vg: Volume group name from setup_loopdev_vg fixture

    Yields:
        dict: Information about the created cache volumes
    """
    vg_name = setup_loopdev_vg
    cache_meta_name = 'cache_meta'
    cache_origin_name = 'cache_origin'
    cache_data_name = 'cache_data'

    # Create cache metadata LV (12MB as per original setup)
    cache_meta_lv = lvm.LogicalVolume(name=cache_meta_name, vg=vg_name)
    assert cache_meta_lv.create(size='12M')

    # Create cache origin LV (300MB as per original setup)
    cache_origin_lv = lvm.LogicalVolume(name=cache_origin_name, vg=vg_name)
    assert cache_origin_lv.create(size='300M')

    # Create cache data LV (100MB as per original setup)
    cache_data_lv = lvm.LogicalVolume(name=cache_data_name, vg=vg_name)
    assert cache_data_lv.create(size='100M')

    cache_info = {
        'vg_name': vg_name,
        'cache_meta_name': cache_meta_name,
        'cache_origin_name': cache_origin_name,
        'cache_data_name': cache_data_name,
        'cache_meta_path': f'/dev/{vg_name}/{cache_meta_name}',
        'cache_origin_path': f'/dev/{vg_name}/{cache_origin_name}',
        'cache_data_path': f'/dev/{vg_name}/{cache_data_name}',
        'cache_meta_lv': cache_meta_lv,
        'cache_origin_lv': cache_origin_lv,
        'cache_data_lv': cache_data_lv,
    }

    yield cache_info

    # Cleanup
    cache_data_lv.remove()
    cache_origin_lv.remove()
    cache_meta_lv.remove()


@pytest.fixture
def cache_pool(cache_volumes: dict[str, Any]) -> dict[str, Any]:
    """Create cache pool by merging cache data and metadata volumes.

    Args:
        cache_volumes: Cache volumes setup from cache_volumes fixture

    Returns:
        dict: Extended cache information with pool details
    """
    cache_info = cache_volumes.copy()
    vg_name = cache_info['vg_name']
    cache_data_name = cache_info['cache_data_name']
    cache_meta_name = cache_info['cache_meta_name']

    # Use lvm convert to create cache pool (matching setup logic)
    convert_result = run(
        f'lvconvert -y --type cache-pool --cachemode writeback '
        f'--poolmetadata {vg_name}/{cache_meta_name} {vg_name}/{cache_data_name}'
    )
    assert convert_result.succeeded

    cache_info.update(
        {
            'cache_pool_created': True,
            'cache_pool_name': cache_data_name,  # Pool takes the name of data LV
            'cache_pool_path': f'/dev/{vg_name}/{cache_data_name}',
        }
    )

    return cache_info


@pytest.fixture
def cache_volume(cache_pool: dict[str, Any]) -> dict[str, Any]:
    """Create cached volume by adding origin to cache pool.

    Args:
        cache_pool: Cache pool setup from cache_pool fixture

    Returns:
        dict: Extended cache information with cached volume details
    """
    cache_info = cache_pool.copy()
    vg_name = cache_info['vg_name']
    cache_origin_name = cache_info['cache_origin_name']
    cache_pool_name = cache_info['cache_pool_name']

    # Convert origin LV to cached LV
    convert_result = run(
        f'lvconvert -y --type cache --cachepool {vg_name}/{cache_pool_name} {vg_name}/{cache_origin_name}'
    )
    assert convert_result.succeeded

    # Create ext4 filesystem on cached volume (matching setup logic)
    run(f'mkfs.ext4 /dev/{vg_name}/{cache_origin_name}')

    cache_info.update(
        {
            'cache_volume_created': True,
            'cached_lv_name': cache_origin_name,  # Origin LV becomes the cached LV
            'cached_lv_path': f'/dev/{vg_name}/{cache_origin_name}',
        }
    )

    return cache_info


@pytest.fixture
def cache_split(cache_volume: dict[str, Any]) -> dict[str, Any]:
    """Split cache volume to separate cache pool and origin.

    Args:
        cache_volume: Cache volume setup from cache_volume fixture

    Returns:
        dict: Extended cache information with split cache details
    """
    cache_info = cache_volume.copy()
    vg_name = cache_info['vg_name']
    cached_lv_name = cache_info['cached_lv_name']

    # Split cache (matching setup logic)
    split_result = run(f'lvconvert -y --splitcache {vg_name}/{cached_lv_name}')
    assert split_result.succeeded

    cache_info.update(
        {
            'cache_split': True,
        }
    )

    return cache_info


@pytest.fixture
def cache_metadata_swap(cache_split: dict[str, Any], swap_volume: dict[str, Any]) -> dict[str, Any]:
    """Perform cache metadata swap operation.

    Swaps cache metadata to the swap volume for DMPD testing.

    Args:
        cache_split: Cache split setup from cache_split fixture
        swap_volume: Swap volume setup from swap_volume fixture

    Returns:
        dict: Combined information with cache metadata device details
    """
    cache_info = cache_split.copy()
    swap_info = swap_volume

    # Ensure both fixtures reference the same VG
    assert cache_info['vg_name'] == swap_info['vg_name'], 'Cache and swap must be in same VG'

    vg_name = cache_info['vg_name']
    cache_pool_name = cache_info['cache_pool_name']
    swap_name = swap_info['swap_name']

    # Deactivate volumes before metadata swap
    cache_pool_lv = lvm.LogicalVolume(name=cache_pool_name, vg=vg_name)
    cache_pool_lv.deactivate()  # Ignore errors
    swap_lv = lvm.LogicalVolume(name=swap_name, vg=vg_name)
    swap_lv.deactivate()
    run('udevadm settle')

    # Swap cache metadata to swap volume (matching setup logic)
    convert_result = run(f'lvconvert -y --cachepool {vg_name}/{cache_pool_name} --poolmetadata {vg_name}/{swap_name}')
    assert convert_result.succeeded

    # Activate swap volume (now containing cache metadata)
    swap_lv = lvm.LogicalVolume(name=swap_name, vg=vg_name)
    swap_lv.activate()
    run('udevadm settle')

    # Use swap LV as cache metadata device
    cache_metadata_dev = f'/dev/{vg_name}/{swap_name}'

    # Combine information from both fixtures
    combined_info = cache_info.copy()
    combined_info.update(swap_info)
    combined_info.update(
        {
            'cache_metadata_dev': cache_metadata_dev,
            'cache_metadata_swapped': True,
        }
    )

    return combined_info


@pytest.fixture
def cache_metadata_backup(cache_metadata_swap: dict[str, Any]) -> Generator[dict[str, Any], None, None]:
    """Create cache metadata backup files for testing.

    Creates cache metadata dump and prepares repair files for testing.

    Args:
        cache_metadata_swap: Cache metadata swap setup from cache_metadata_swap fixture

    Yields:
        dict: Extended information with backup file paths
    """
    cache_info = cache_metadata_swap.copy()
    cache_metadata_dev = cache_info['cache_metadata_dev']
    cache_dump_path = Path('/var/tmp/cache_dump')
    cache_repair_path = Path('/var/tmp/cache_repair')

    # Create cache metadata dump (to match testing expectations)
    dump_result = dmpd.cache_dump(cache_metadata_dev, output=str(cache_dump_path))
    assert dump_result.succeeded

    # Create empty repair file with proper allocation (5MB should be enough)
    assert fallocate(cache_repair_path, length='5M')

    cache_info.update(
        {
            'cache_dump_path': cache_dump_path,
            'cache_repair_path': cache_repair_path,
        }
    )

    yield cache_info

    # Cleanup files
    run(f'rm -f {cache_dump_path} {cache_repair_path}')


@pytest.fixture
def setup_cache_metadata_for_dmpd(install_dmpd: None, cache_metadata_backup: dict[str, Any]) -> dict[str, Any]:
    """Set up cache metadata configuration for DMPD tool testing.

    This fixture creates the necessary cache metadata setup that DMPD cache tools
    can operate on. Unlike thin metadata which intentionally creates "broken" state,
    cache metadata swap creates a working metadata device that cache tools can analyze.

    Args:
        install_dmpd: DMPD package installation fixture
        cache_metadata_backup: Cache metadata backup setup from cache_metadata_backup fixture

    Returns:
        dict: Extended cache information for DMPD testing
    """
    # DMPD packages are installed via install_dmpd fixture
    _ = install_dmpd

    # Use cache_metadata_backup which provides working cache metadata for DMPD testing
    return cache_metadata_backup.copy()
