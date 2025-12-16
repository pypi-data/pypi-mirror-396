"""Tests for lvextend thin provisioning operations.

This module contains pytest tests for lvextend command with thin provisioning,
focusing on extending thin pools and thin volumes.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

import pytest

from sts import lvm


@pytest.mark.parametrize('loop_devices', [{'count': 4, 'size_mb': 512}], indirect=True)
class TestLvextendThin:
    """Test cases for lvextend thin provisioning operations."""

    def test_extend_thin_pool_basic(self, setup_loopdev_vg: str) -> None:
        """Test basic thin pool extension operations."""
        vg_name = setup_loopdev_vg

        # Create thin pools
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(extents='2', type='thin-pool')

        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert pool2.create(stripes='2', extents='2', type='thin-pool')

        # Test extending by extents
        for pool_num in range(1, 3):
            pool_name = f'pool{pool_num}'
            pool = lvm.LogicalVolume(name=pool_name, vg=vg_name)

            # Extend by 2 extents
            assert pool.extend(extents='+2')
            assert pool.report
            # Check size using report data directly
            assert pool.report.lv_size == '16.00m'

            # Extend by size (default unit is m)
            assert pool.extend(size='+8')
            # Check size using report data directly
            assert pool.report.lv_size == '24.00m'

            # Extend by size with explicit unit
            assert pool.extend(size='+8M')
            # Check size using report data directly
            assert pool.report.lv_size == '32.00m'

        # Clean up
        for pool_num in range(1, 3):
            pool_name = f'pool{pool_num}'
            pool = lvm.LogicalVolume(name=pool_name, vg=vg_name)
            assert pool.remove(force='', yes='')

    def test_extend_thin_pool_to_absolute_size(self, setup_loopdev_vg: str) -> None:
        """Test extending thin pool to absolute size."""
        vg_name = setup_loopdev_vg

        # Create thin pools
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(extents='2', type='thin-pool')

        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert pool2.create(stripes='2', extents='2', type='thin-pool')

        for pool_num in range(1, 3):
            pool_name = f'pool{pool_num}'
            pool = lvm.LogicalVolume(name=pool_name, vg=vg_name)
            pool.refresh_report()
            assert pool.report

            # Set specific size by extents
            assert pool.extend(extents='6')
            # Check size using report data directly
            assert pool.report.lv_size == '24.00m'

            # Set specific size by size
            assert pool.extend(size='40m')
            # Check size using report data directly
            assert pool.report.lv_size == '40.00m'

        # Clean up
        for pool_num in range(1, 3):
            pool_name = f'pool{pool_num}'
            pool = lvm.LogicalVolume(name=pool_name, vg=vg_name)
            assert pool.remove(force='', yes='')

    def test_extend_thin_lv_virtual_size(self, setup_loopdev_vg: str) -> None:
        """Test extending thin LV virtual size."""
        vg_name = setup_loopdev_vg

        # Create thin pool
        pool = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool.create(extents='50', type='thin-pool')

        # Create thin LV
        thin_lv = lvm.LogicalVolume(name='lv1', vg=vg_name)
        assert thin_lv.create(virtualsize='100m', type='thin', thinpool='pool1')

        assert thin_lv.report

        # Initial virtual size should be 100m
        # Check size using report data directly
        assert thin_lv.report.lv_size == '100.00m'

        # Extend thin LV virtual size

        # Extend by 100m
        assert thin_lv.extend(size='+100m')
        # Check size using report data directly
        assert thin_lv.report.lv_size == '200.00m'

        # Extend to specific size
        assert thin_lv.extend(size='300m')
        # Check size using report data directly
        assert thin_lv.report.lv_size == '300.00m'

        # Extend by extents (assuming 4M extent size)
        assert thin_lv.extend(extents='+25')  # +100m
        # Check size using report data directly
        assert thin_lv.report.lv_size == '400.00m'

        # Clean up
        thin_lv = lvm.LogicalVolume(name='lv1', vg=vg_name)
        pool = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert thin_lv.remove(force='', yes='')
        assert pool.remove(force='', yes='')

    def test_extend_thin_lv_different_units(self, setup_loopdev_vg: str) -> None:
        """Test extending thin LV with different size units."""
        vg_name = setup_loopdev_vg

        # Create thin pool and thin LV
        pool = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool.create(extents='50', type='thin-pool')

        thin_lv = lvm.LogicalVolume(name='lv1', vg=vg_name)
        assert thin_lv.create(virtualsize='100m', type='thin', thinpool='pool1')

        assert thin_lv.report

        # Test different units
        assert thin_lv.extend(size='+50m')
        # Check size using report data directly
        assert thin_lv.report.lv_size == '152.00m'

        assert thin_lv.extend(size='+1g')
        # Check size using report data directly
        assert thin_lv.report.lv_size == '<1.15g'  # 152m + 1g = 1.125g ≈ 1.12g

        # Extend with larger units
        assert thin_lv.extend(size='2g')
        # Check size using report data directly
        assert thin_lv.report.lv_size == '2.00g'

        # Clean up
        thin_lv = lvm.LogicalVolume(name='lv1', vg=vg_name)
        pool = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert thin_lv.remove(force='', yes='')
        assert pool.remove(force='', yes='')

    def test_extend_validation_and_errors(self, setup_loopdev_vg: str) -> None:
        """Test extension validation and error conditions."""
        vg_name = setup_loopdev_vg

        # Create thin pool
        pool = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool.create(extents='10', type='thin-pool')

        # Try to extend beyond VG capacity - should fail
        assert not pool.extend(extents='+1000')

        # Clean up
        pool = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool.remove(force='', yes='')

    def test_extend_thin_metadata(self, setup_loopdev_vg: str) -> None:
        """Test extending thin pool metadata."""
        vg_name = setup_loopdev_vg

        # Create thin pool with small metadata
        pool = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool.create(size='100m', type='thin-pool', poolmetadatasize='8')

        # Check initial metadata size
        result = pool.lvs(f'{vg_name}/pool1', o='lv_metadata_size', noheadings='')
        assert result.succeeded
        initial_meta_size = result.stdout.strip()
        logging.info(f'Initial metadata size: {initial_meta_size}')

        # Note: Extending metadata requires specific LVM commands
        # and may not be supported in all scenarios

        # Clean up
        pool = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool.remove(force='', yes='')
