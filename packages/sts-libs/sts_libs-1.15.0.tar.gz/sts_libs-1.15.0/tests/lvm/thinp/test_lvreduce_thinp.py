"""Tests for reducing thin provisioning logical volumes.

This module contains pytest tests for reducing thin pools and thin volumes,
including filesystem reduction and snapshot handling.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from pathlib import Path

import pytest

from sts import lvm
from sts.utils.cmdline import run
from sts.utils.files import Directory, mkfs, mount, umount


@pytest.mark.parametrize('loop_devices', [{'count': 4, 'size_mb': 256}], indirect=True)
class TestLvreduceThinp:
    """Test cases for reducing thin provisioning volumes."""

    def test_reduce_pool_not_allowed(self, setup_loopdev_vg: str) -> None:
        """Test that reducing thin pools is not allowed."""
        vg_name = setup_loopdev_vg

        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        lv1 = lvm.LogicalVolume(name='lv1', vg=vg_name)
        lv2 = lvm.LogicalVolume(name='lv2', vg=vg_name)

        try:
            # Create thin pools with thin volumes
            assert pool1.create(size='100M', type='thin-pool')
            assert lv1.create(virtualsize='100M', type='thin', thinpool='pool1')

            assert pool2.create(size='100M', type='thin-pool', stripes='2')
            assert lv2.create(virtualsize='100M', type='thin', thinpool='pool2')

            # Try to reduce pool1 - should fail
            reduce_success = pool1.reduce(extents='-1', force='')
            assert not reduce_success, 'Reducing thin pool should fail'

        finally:
            # Cleanup LVs before VG cleanup
            lv1.remove()
            lv2.remove()
            pool1.remove()
            pool2.remove()

    def test_reduce_thin_volumes(self, setup_loopdev_vg: str) -> None:
        """Test reducing thin volumes with various options."""
        vg_name = setup_loopdev_vg

        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        lv1 = lvm.LogicalVolume(name='lv1', vg=vg_name)
        lv2 = lvm.LogicalVolume(name='lv2', vg=vg_name)

        try:
            # Create thin pools with thin volumes
            assert pool1.create(size='100M', type='thin-pool')
            assert lv1.create(virtualsize='100M', type='thin', thinpool='pool1')

            assert pool2.create(size='100M', type='thin-pool', stripes='2')
            assert lv2.create(virtualsize='100M', type='thin', thinpool='pool2')

            # Test reducing both thin volumes
            for lv_num in range(1, 3):
                lv = lvm.LogicalVolume(name=f'lv{lv_num}', vg=vg_name)
                lv.refresh_report()
                assert lv.report
                # Reduce by extents
                assert lv.reduce(extents='-2', force='')
                lv.refresh_report()
                assert lv.report.lv_size == '92.00m'

                # Reduce by size (default unit is m)
                assert lv.reduce(size='-8m', force='')
                lv.refresh_report()
                assert lv.report.lv_size == '84.00m'

                # Reduce by size with explicit unit
                assert lv.reduce(size='-8m', force='')
                lv.refresh_report()
                assert lv.report.lv_size == '76.00m'

                # Set specific size
                assert lv.reduce(size='72m', force='')
                lv.refresh_report()
                assert lv.report.lv_size == '72.00m'

                # Set specific size
                assert lv.reduce(size='64m', force='')
                lv.refresh_report()
                assert lv.report.lv_size == '64.00m'

                # Test with --test option (should not change size)
                original_size = lv.report.lv_size

                # Test dry-run with percentage FREE
                assert lv.reduce('--test', extents='-1%FREE', force='')
                lv.refresh_report()
                assert lv.report.lv_size == original_size

                assert lv.reduce('--test', extents='-1%PVS', force='')
                lv.refresh_report()
                assert lv.report.lv_size == original_size

                assert lv.reduce('-t', extents='-1%VG', force='')
                lv.refresh_report()
                assert lv.report.lv_size == original_size

        finally:
            # Cleanup LVs before VG cleanup
            lv1.remove()
            lv2.remove()
            pool1.remove()
            pool2.remove()

    def test_reduce_with_filesystem_and_snapshots(self, setup_loopdev_vg: str) -> None:
        """Test reducing thin volumes with filesystems and snapshots."""
        vg_name = setup_loopdev_vg
        lv_mnt = Path('/mnt/lv')
        snap_mnt = Path('/mnt/snap')
        lv_dir = Directory(lv_mnt, create=True)
        snap_dir = Directory(snap_mnt, create=True)

        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        lv1 = lvm.LogicalVolume(name='lv1', vg=vg_name)
        snap1 = None

        try:
            # Create thin pool and volume
            assert pool.create(size='200M', type='thin-pool')
            assert lv1.create(virtualsize='100M', type='thin', thinpool='pool')

            # Create filesystem (use ext4 since xfs doesn't support reduction)
            fs = 'ext4'
            lv_device = Path(f'/dev/mapper/{vg_name}-lv1')

            assert mkfs(lv_device, fs, force='')
            assert mount(lv_device, lv_mnt)

            # Add some data
            run(f'dd if=/dev/urandom of={lv_mnt!s}/lv1 bs=1M count=5')
            assert lv1.report
            # Reduce with filesystem
            assert lv1.reduce('-f', '--resizefs', extents='-2')
            lv1.refresh_report()
            assert lv1.report.lv_size == '92.00m'

            # Create snapshot
            snap1 = lv1.create_snapshot('snap1', '-K')
            assert snap1 is not None

            snap_device = Path(f'/dev/mapper/{vg_name}-snap1')

            assert mkfs(snap_device, fs, force='')
            assert mount(snap_device, snap_mnt)

            # Add data to snapshot
            run(f'dd if=/dev/urandom of={snap_mnt!s}/lv1 bs=1M count=5')

            # Reduce snapshot with filesystem
            assert snap1.reduce('-f', '--resizefs', extents='-2')
            snap1.refresh_report()
            assert snap1.report
            assert snap1.report.lv_size == '84.00m'

            run(f'df -h {snap_mnt!s}')

            assert snap1.reduce('-f', '--resizefs', size='40m')
            snap1.refresh_report()
            assert snap1.report.lv_size == '40.00m'

            run(f'df -h {snap_mnt!s}')

        finally:
            # Cleanup
            umount(lv_mnt)
            umount(snap_mnt)
            lv_dir.remove_dir()
            snap_dir.remove_dir()
            # Clean up LVs
            if snap1:
                snap1.remove()
            lv1.remove()
            pool.remove()
