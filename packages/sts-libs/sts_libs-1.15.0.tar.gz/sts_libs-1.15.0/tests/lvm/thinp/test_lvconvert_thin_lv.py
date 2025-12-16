"""Tests for lvconvert operations to convert LV to thin LV.

This module contains pytest tests for converting regular logical volumes to thin LVs
while preserving data and creating origin snapshots.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from pathlib import Path

import pytest

from sts import lvm
from sts.utils.cmdline import run
from sts.utils.files import Directory, mkfs, mount, umount, write_data


@pytest.mark.parametrize('loop_devices', [{'count': 4, 'size_mb': 256}], indirect=True)
class TestLvconvertThinLv:
    """Test cases for converting LV to thin LV operations."""

    def test_convert_lv_to_thin(self, setup_loopdev_vg: str) -> None:
        """Test converting regular LV to thin LV with data preservation."""
        vg_name = setup_loopdev_vg
        mount_point = Path('/mnt/thin')
        file_path = Path(f'{mount_point!s}/5m')

        thin_lv = lvm.LogicalVolume(name='thin', vg=vg_name)
        pool = lvm.LogicalVolume(name='pool', vg=vg_name)

        # Create directory object for reuse in cleanup
        mount_dir = Directory(mount_point, create=True)

        try:
            # Create regular LV and put data on it
            assert thin_lv.create(extents='75')

            # Create directory and filesystem
            fs = 'ext4'  # Use ext4 for better compatibility

            thin_device = Path(f'/dev/mapper/{vg_name}-thin')
            assert mkfs(thin_device, fs, force='')
            assert mount(thin_device, mount_point)

            # Create test data and checksum
            assert write_data(source='/dev/urandom', target=file_path, bs='1M', count=5)
            run(f'md5sum {file_path!s} > /tmp/pre_md5')

            # Create thin pool
            assert pool.create(size='150M', type='thin-pool')

            # Convert LV to thin LV with origin
            success, origin_lv = thin_lv.convert_originname(
                thinpool=f'{vg_name}/pool',
                origin_name='thin_origin',
            )

            assert success
            assert origin_lv

            run('sync')

            # Verify data integrity
            run(f'md5sum {file_path!s} > /tmp/post_md5')
            result = run('diff /tmp/pre_md5 /tmp/post_md5')
            assert result.succeeded, 'Data corruption detected after conversion'

            # Verify thin LV properties
            assert thin_lv.report
            assert thin_lv.report.lv_size == '300.00m'
            assert thin_lv.report.pool_lv == 'pool'
            assert thin_lv.report.lv_attr == 'Vwi-aotz--'
            assert thin_lv.report.origin == 'thin_origin'

            # Verify readonly origin LV was created
            assert origin_lv.report
            assert origin_lv.report.lv_attr == 'ori-------'

            # Test that new data goes to the pool
            pre_thin_dp = float(thin_lv.report.data_percent or '0') if thin_lv.report else 0.0
            pre_pool_dp = float(pool.report.data_percent or '0') if pool.report else 0.0

            assert write_data(source='/dev/urandom', target=mount_point / '10m', bs='1M', count=10)

            thin_lv.refresh_report()
            pool.refresh_report()
            post_thin_dp = float(thin_lv.report.data_percent or '0') if thin_lv.report else 0.0
            post_pool_dp = float(pool.report.data_percent or '0') if pool.report else 0.0

            assert post_thin_dp > pre_thin_dp, 'Thin LV data percentage should increase'
            assert post_pool_dp > pre_pool_dp, 'Pool data percentage should increase'

            # Test deleting the thin LV and checking origin integrity
            file_path.unlink()
            umount(mount_point)

            # Remove thin LV and activate origin
            assert thin_lv.remove()
            assert origin_lv
            assert origin_lv.activate()

            # For XFS, we need writable device for journal
            if fs == 'xfs':
                assert origin_lv.change('-prw')

            # Mount origin and verify original data
            thin_origin_device = Path(f'/dev/mapper/{vg_name}-thin_origin')
            assert mount(thin_origin_device, mount_point)

            run(f'md5sum {file_path!s} > /tmp/origin_md5')
            result = run('diff /tmp/pre_md5 /tmp/origin_md5')
            assert result.succeeded, 'Original data not preserved in origin'

        finally:
            # Cleanup
            umount(mount_point)
            if mount_dir.exists:
                mount_dir.remove_dir()
            run('rm -f /tmp/pre_md5 /tmp/post_md5 /tmp/origin_md5')
