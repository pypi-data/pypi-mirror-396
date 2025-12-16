"""Test VDO upgrade scenarios.

This module tests VDO upgrade functionality using different scenarios:
- VDO Manager with VDO create (RHEL-8)
- VDO Manager on existing LV (RHEL-8)
- VDO LV direct creation (RHEL-8)
"""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from sts import lvm
from sts.utils.cmdline import run
from sts.utils.files import Directory, mkfs, mount, umount
from sts.utils.modules import ModuleManager
from sts.utils.system import SystemManager

if TYPE_CHECKING:
    from sts.blockdevice import BlockDevice


class TestVdoUpgrade:
    """Test class for VDO upgrade scenarios."""

    disk: BlockDevice
    pv: lvm.PhysicalVolume
    vg: lvm.VolumeGroup
    lv: lvm.LogicalVolume
    vdo_path: Path
    vg_name: str = 'vdo_vg'
    lv_name: str = 'vdo_lv'
    pool_name: str = 'vdo_pool'
    vdo_name: str = 'vdo1'
    mount_point: str = '/mnt/vdo'
    flag: Path = Path(f'{mount_point}/vdo_test_file')
    mnt_dir: Directory | None = None

    def vdomanager_vdo_create(self) -> None:
        """Create VDO using vdo command and import with lvm_import_vdo (RHEL-8 scenario 1)."""
        logging.info(f'Creating VDO {self.vdo_name} on device {self.disk.path}')
        assert run(f'vdo create --name={self.vdo_name} --device={self.disk.path} --vdoLogicalSize=100G').succeeded
        self.vdo_path = Path(f'/dev/mapper/{self.vdo_name}')
        self.write_flag()
        ret = run(f'lvm_import_vdo -y --name {self.vg_name}/{self.lv_name} {self.disk.path!s}')
        assert ret.succeeded, f'Failed to import VDO: {ret.stderr}'
        logging.info(run('lsblk').stdout)
        logging.info(ret.stdout)

    def vdomanager_on_lv(self) -> None:
        """Import existing VDO device with lvm_import_vdo (RHEL-8 scenario 2)."""
        logging.info(f'Importing VDO on device {self.disk.path} into LVM')
        assert self.pv.create()
        assert self.vg.create()
        assert self.lv.create(size='8G')
        assert run(
            f'vdo create --name={self.vdo_name} --device=/dev/{self.vg_name}/{self.lv_name} --vdoLogicalSize=100G'
        ).succeeded
        self.vdo_path = Path(f'/dev/mapper/{self.vdo_name}')
        self.write_flag()
        assert run(f'lvm_import_vdo -y /dev/{self.vg_name}/{self.lv_name}').succeeded

    def vdo_lv_create(self) -> None:
        """Create VDO logical volume directly with LVM (RHEL-8 scenario 3)."""
        logging.info(f'Creating VDO LV {self.lv_name} in VG {self.vg_name}')
        logging.info(run('lsblk').stdout)
        assert self.pv.create()
        assert self.vg.create()
        assert self.lv.create(type='vdo', vdopool=self.pool_name, size='8G')
        logging.info(run('lsblk').stdout)
        if self.lv.path is None:
            pytest.fail('LV path is None')
        self.vdo_path = Path(self.lv.path) if isinstance(self.lv.path, str) else self.lv.path
        self.write_flag()

    def remove_vdo_lv(self) -> None:
        """Remove VDO logical volume and cleanup LVM structures."""
        logging.info(f'Removing VDO LV {self.lv_name} and cleaning up')
        assert self.lv.remove()
        assert self.vg.remove()
        assert self.pv.remove()

    def write_flag(self) -> None:
        assert mkfs(device=str(self.vdo_path), fs_type='xfs')
        if self.mnt_dir is None:
            self.mnt_dir = Directory(Path(self.mount_point), create=True)
        assert self.mnt_dir.exists, f'Failed to create mount point directory {self.mount_point}'
        assert mount(device=str(self.vdo_path), mountpoint=self.mount_point)
        self.flag.write_text('VDO_FLAG')
        assert umount(mountpoint=self.mount_point)

    def read_flag(self) -> None:
        assert mount(device=str(self.lv.path), mountpoint=self.mount_point)
        assert self.flag.exists()
        logging.info(f'Flag file exists: {self.flag.read_text()}')
        assert self.flag.read_text() == 'VDO_FLAG'
        assert umount(mountpoint=self.mount_point)

    @pytest.mark.usefixtures('load_vdo_module', 'prepare_1minutetip_disk')
    def test_vdo_upgrade(self, load_vdo_module: str, prepare_1minutetip_disk: list[BlockDevice]) -> None:
        """
        Test VDO upgrade scenarios.

        This test supports different VDO creation scenarios for RHEL-8:
        - VDO Manager with VDO create
        - VDO Manager on existing LV
        - VDO LV direct creation
        """
        module = load_vdo_module
        self.disk = prepare_1minutetip_disk[0]
        phase = os.getenv('IN_PLACE_UPGRADE', None)
        if phase is None:
            pytest.skip('IN_PLACE_UPGRADE is not set')

        logging.info(f'VDO upgrade phase: {phase}')
        self.pv = lvm.PhysicalVolume(name=str(self.disk.path).split('/')[-1], path=self.disk.path)
        self.vg = lvm.VolumeGroup(name=self.vg_name, pvs=[str(self.disk.path)])
        self.lv = lvm.LogicalVolume(name=self.lv_name, vg=self.vg_name, pool_name=self.pool_name)
        system = SystemManager()

        if phase == 'old':
            # RHEL-8 scenarios (can be extended to test different scenarios)
            if system.info.version.major == 8:
                # Default to vdomanager_vdo_create scenario
                # Other scenarios can be selected via environment variables
                scenario = os.getenv('VDO_SCENARIO', 'vdomanager_vdo_create')

                if scenario == 'vdomanager_vdo_create':
                    self.vdomanager_vdo_create()
                elif scenario == 'vdomanager_on_lv':
                    self.vdomanager_on_lv()
                elif scenario == 'vdo_lv_create':
                    self.vdo_lv_create()
                else:
                    pytest.skip(f'Unknown VDO scenario: {scenario}')
            elif system.info.version.major == 9:
                self.vdomanager_vdo_create()
            else:
                pytest.skip(f'VDO upgrade test only supports RHEL-8/9, current version: {system.info.version.major}')

        elif phase == 'new':
            # Cleanup phase
            logging.info(run('lsblk').stdout)
            self.read_flag()
            self.remove_vdo_lv()
            ModuleManager().unload(name=module)
