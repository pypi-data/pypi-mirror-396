"""Tests for resizing thin provisioning logical volumes.

This module contains pytest tests for resizing thin pools and thin volumes,
including extending pools, extending thin volumes, and filesystem operations.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from pathlib import Path

import pytest

from sts import lvm
from sts.utils.cmdline import run
from sts.utils.files import Directory, mkfs, mount, umount


@pytest.mark.parametrize('loop_devices', [{'count': 4, 'size_mb': 256}], indirect=True)
class TestLvresizeThinp:
    """Test cases for resizing thin provisioning volumes."""

    def test_extend_pool(self, setup_loopdev_vg: str, loop_devices: list) -> None:
        """Test extending thin pools with various options."""
        vg_name = setup_loopdev_vg

        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)

        try:
            # Create thin pools
            assert pool1.create(extents='2', type='thin-pool')  # 2 extents
            assert pool2.create(extents='2', type='thin-pool', stripes='2')

            pvs = loop_devices

            # Test extending both pools
            for pool_num in range(1, 3):
                pool = lvm.LogicalVolume(name=f'pool{pool_num}', vg=vg_name)
                pool.refresh_report()
                assert pool.report

                # Extend by extents
                assert pool.extend(extents='+2')
                assert pool.report.lv_size == '16.00m'

                # Extend by size (default unit is m)
                assert pool.extend(size='+8')
                assert pool.report.lv_size == '24.00m'

                # Extend by size with explicit unit
                assert pool.extend(size='+8M')
                assert pool.report.lv_size == '32.00m'

                # Extend to specific device (pool1 only to avoid complexity)
                if pool_num == 1:
                    # Extend using arbitrary device
                    assert pool.resize('-l+2', pvs[3])
                    assert pool.report.lv_size == '40.00m'

                    # Extend using specific PE range
                    assert pool.resize('-l+2', f'{pvs[2]}:40:41')
                    assert pool.report.lv_size == '48.00m'

                    # Verify device allocation
                    result = run(f'pvs -ovg_name,lv_name,devices {pvs[2]} | grep "{pvs[2]}(40)"')
                    assert result.succeeded

                    assert pool.resize('-l+2', f'{pvs[1]}:35:37')
                    assert pool.report.lv_size == '56.00m'

                    result = run(f'pvs -ovg_name,lv_name,devices {pvs[1]} | grep "{pvs[1]}(35)"')
                    assert result.succeeded
                else:
                    # Extend using multiple devices
                    assert pool.resize('-l+2', pvs[1], pvs[2])
                    assert pool.report.lv_size == '40.00m'

                    assert pool.resize('-l+2', f'{pvs[1]}:30-41', f'{pvs[2]}:20-31')
                    assert pool.report.lv_size == '48.00m'

                    result = run(f'pvs -ovg_name,lv_name,devices {pvs[1]} | grep "{pvs[1]}(30)"')
                    assert result.succeeded
                    result = run(f'pvs -ovg_name,lv_name,devices {pvs[2]} | grep "{pvs[2]}(20)"')
                    assert result.succeeded

                # Set specific size (original: lvresize -l16 and lvresize -L72m)
                assert pool.resize(extents='16')
                assert pool.report.lv_size == '64.00m'

                assert pool.resize(size='72m')
                assert pool.report.lv_size == '72.00m'

                # Test with --test option (should not change size)
                original_size = pool.report.lv_size
                assert pool.resize('-l+100%FREE', '--test'), 'Test resize should succeed'
                assert pool.report.lv_size == original_size

                assert pool.resize('-l+10%PVS', '--test'), 'Test resize should succeed'
                assert pool.report.lv_size == original_size

                assert pool.resize('-l+10%VG', '-t'), 'Test resize should succeed'
                assert pool.report.lv_size == original_size

                # This should fail - can't extend to 100% of VG
                assert not pool.resize('-l+100%VG', '-t'), 'This resize should fail'

        finally:
            # Cleanup LVs before VG cleanup
            pool2.remove()
            pool1.remove()

    def test_extend_thin_lv(self, setup_loopdev_vg: str) -> None:
        """Test extending thin volumes."""
        vg_name = setup_loopdev_vg

        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        lv1 = lvm.LogicalVolume(name='lv1', vg=vg_name)
        lv2 = lvm.LogicalVolume(name='lv2', vg=vg_name)

        try:
            # Create pools and thin volumes
            assert pool1.create(extents='85', type='thin-pool')  # 85 extents
            assert lv1.create(virtualsize='308M', type='thin', thinpool='pool1')

            assert pool2.create(extents='85', type='thin-pool', stripes='2')
            assert lv2.create(virtualsize='308M', type='thin', thinpool='pool2')

            # Test extending both thin volumes
            for lv_num in range(1, 3):
                lv = lvm.LogicalVolume(name=f'lv{lv_num}', vg=vg_name)
                lv.refresh_report()
                assert lv.report

                # Extend to 79 extents (original: lvextend -l79)
                assert lv.extend(extents='79')
                assert lv.report.lv_size == '316.00m'

                # Extend to 324M size (original: lvextend -L324)
                assert lv.extend(size='324')
                assert lv.report.lv_size == '324.00m'

                # Extend by +2 extents (original: lvextend -l+2 -r)
                assert lv.extend(extents='+2')
                assert lv.report.lv_size == '332.00m'

                # Extend to 340M size (original: lvextend -L348 -rf)
                assert lv.resize(size='340m')
                assert lv.report.lv_size == '340.00m'

                assert lv.resize(size='348m')
                assert lv.report.lv_size == '348.00m'

                # Test with --test option (original: lvextend -l+100%FREE --test and lvextend -l+100%PVS --test)
                original_size = lv.report.lv_size
                assert lv.resize('-l+100%FREE', '--test'), 'Test resize should succeed'
                assert lv.report.lv_size == original_size

                assert lv.resize('-l+100%PVS', '--test'), 'Test resize should succeed'
                assert lv.report.lv_size == original_size

        finally:
            # Cleanup LVs before VG cleanup
            lv1.remove('-f')
            lv2.remove('-f')
            pool1.remove('-f')
            pool2.remove('-f')

    def test_resize_with_filesystem(self, setup_loopdev_vg: str) -> None:
        """Test resizing thin volumes with filesystems."""
        vg_name = setup_loopdev_vg
        lv_mnt = Path('/mnt/lv')
        snap_mnt = Path('/mnt/snap')

        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        lv1 = lvm.LogicalVolume(name='lv1', vg=vg_name)

        snap_dir = Directory(snap_mnt, create=True)
        lv_dir = Directory(lv_mnt, create=True)

        try:
            # Create pool and thin volume
            assert pool.create(size='200M', type='thin-pool')
            assert lv1.create(virtualsize='100M', type='thin', thinpool='pool')
            assert lv1.report
            assert pool.report

            # Create and mount filesystem
            lv_device = f'/dev/mapper/{vg_name}-lv1'

            # Use ext4 for resize testing
            fs = 'ext4'
            assert mkfs(lv_device, fs, force='')
            assert mount(lv_device, lv_mnt)

            # Add some data
            run(f'dd if=/dev/urandom of={lv_mnt!s}/lv1 bs=1M count=5')

            # Extend with filesystem resize
            assert lv1.resize('-rf', '-l+2'), 'LV resize with filesystem should succeed'
            assert lv1.report.lv_size == '108.00m'

            run(f'df -h {lv_mnt!s}')

            # Create snapshot and test resizing it
            snap1 = lv1.create_snapshot('snap1', '-K')
            assert snap1 is not None
            assert snap1.report is not None

            snap_device = f'/dev/mapper/{vg_name}-snap1'

            assert mkfs(snap_device, fs, force='')
            assert mount(snap_device, snap_mnt)

            # Add data to snapshot and extend it
            run(f'dd if=/dev/urandom of={snap_mnt!s}/lv1 bs=1M count=5')

            assert snap1.resize('-rf', '-l+2'), 'Snapshot resize with filesystem should succeed'
            assert snap1.report.lv_size == '116.00m'

            run(f'df -h {snap_mnt!s}')

            assert snap1.resize('-rf', '-L120'), 'Snapshot resize with filesystem should succeed'
            assert snap1.report.lv_size == '120.00m'

            run(f'df -h {snap_mnt!s}')

        finally:
            # Cleanup
            umount(lv_mnt)
            umount(snap_mnt)
            snap_dir.remove_dir()
            lv_dir.remove_dir()

    def test_resize_pool_metadata(self, setup_loopdev_vg: str) -> None:
        """Test resizing thin pool metadata."""
        vg_name = setup_loopdev_vg

        pool = lvm.LogicalVolume(name='pool', vg=vg_name)

        try:
            # Create pool with custom metadata size
            assert pool.create(size='40M', type='thin-pool', poolmetadatasize='8M')

            assert pool.report
            # Verify initial metadata size
            assert pool.report.lv_metadata_size == '8.00m'

            # Extend metadata
            assert pool.resize(poolmetadatasize='+4M'), 'Pool metadata resize should succeed'
            assert pool.report.lv_metadata_size == '12.00m'

            # Set absolute metadata size
            assert pool.resize(poolmetadatasize='16M'), 'Pool metadata resize should succeed'
            assert pool.report.lv_metadata_size == '16.00m'

        finally:
            # Cleanup LVs before VG cleanup
            pool.remove()
