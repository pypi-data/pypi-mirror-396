"""Tests for thin pool metadata spare creation.

This module contains pytest tests for creating thin pools with and without
pool metadata spare volumes and managing their sizes.
"""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
import logging
import time

import pytest

from sts import lvm


@pytest.mark.parametrize('loop_devices', [{'count': 4, 'size_mb': 128}], indirect=True)
class TestLvcreatePoolmetadataspare:
    """Test cases for thin pool metadata spare operations."""

    def test_poolmetadataspare_management(self, setup_loopdev_vg: str) -> None:
        """Test creating pools with and without metadata spare."""
        vg_name = setup_loopdev_vg

        pool0 = lvm.LogicalVolume(name='pool0', vg=vg_name)
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        pmspare_name = 'lvol0_pmspare'

        try:
            # Step 1: Create pool without spare
            assert pool0.create(extents='10', type='thin-pool', poolmetadataspare='n')

            # Verify spare doesn't exist
            all_lvs = lvm.LogicalVolume.get_all(vg_name)
            assert not any(lv.name == pmspare_name for lv in all_lvs), 'lvol0_pmspare should not exist'

            # Step 2: Create pool with poolmetadatasize 4m (should create spare)
            assert pool1.create(extents='10', type='thin-pool', poolmetadatasize='4M')

            # Verify spare exists and has correct size
            spare_lv = lvm.LogicalVolume(name=pmspare_name, vg=vg_name)
            assert spare_lv.refresh_report(), 'lvol0_pmspare should exist'

            assert spare_lv.report
            assert spare_lv.report.lv_size == '4.00m', f'Expected 4.00m, got {spare_lv.report.lv_size}'
        finally:
            # Remove all LVs for next test
            pool1.remove(force='', yes='')
            pool0.remove(force='', yes='')
            # Remove spare if it exists
            spare_lv = lvm.LogicalVolume(name=pmspare_name, vg=vg_name)
            spare_lv.remove(force='', yes='')

        time.sleep(2)  # Give time for cleanup

    def test_poolmetadataspare_size_updates(self, setup_loopdev_vg: str) -> None:
        """Test that metadata spare size gets updated when larger pools are created."""
        vg_name = setup_loopdev_vg

        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        pmspare_name = 'lvol0_pmspare'

        try:
            # Step 1: Create pool with 4M metadata
            assert pool1.create(extents='10', type='thin-pool', poolmetadatasize='4M')

            # Verify spare exists and has 4M size
            spare_lv = lvm.LogicalVolume(name=pmspare_name, vg=vg_name)
            assert spare_lv.refresh_report(), 'lvol0_pmspare should exist'
            assert spare_lv.report
            assert spare_lv.report.lv_size == '4.00m', f'Expected 4.00m, got {spare_lv.report.lv_size}'

            # Step 2: Create pool with 8M metadata - should update spare size to 8M
            assert pool2.create(extents='10', type='thin-pool', poolmetadatasize='8M')

            # Verify spare size updated to 8M
            spare_lv.refresh_report()
            assert spare_lv.report.lv_size == '8.00m', f'Expected 8.00m, got {spare_lv.report.lv_size}'

        finally:
            # Remove all LVs for next test
            pool2.remove(force='', yes='')
            pool1.remove(force='', yes='')
            # Remove spare if it exists
            spare_lv = lvm.LogicalVolume(name=pmspare_name, vg=vg_name)
            spare_lv.remove(force='', yes='')

        time.sleep(2)  # Give time for cleanup

    def test_poolmetadataspare_explicit_control(self, setup_loopdev_vg: str) -> None:
        """Test explicit control over pool metadata spare creation."""
        vg_name = setup_loopdev_vg

        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        pmspare_name = 'lvol0_pmspare'

        try:
            # Step 1: Create pool without spare explicitly
            assert pool1.create(extents='10', type='thin-pool', poolmetadataspare='n')

            # Verify spare doesn't exist
            all_lvs = lvm.LogicalVolume.get_all(vg_name)
            assert not any(lv.name == pmspare_name for lv in all_lvs), 'lvol0_pmspare should not exist'

            # Step 2: Create pool with spare explicitly
            assert pool2.create(extents='10', type='thin-pool', poolmetadataspare='y')

            # Verify spare exists with default size (4M)
            spare_lv = lvm.LogicalVolume(name=pmspare_name, vg=vg_name)
            assert spare_lv.refresh_report(), 'lvol0_pmspare should exist'
            assert spare_lv.report
            assert spare_lv.report.lv_size == '4.00m', f'Expected 4.00m, got {spare_lv.report.lv_size}'

            # Step 3: Create thin volumes in the pools to verify they work
            thin1 = lvm.LogicalVolume(name='thin1', vg=vg_name)
            thin2 = lvm.LogicalVolume(name='thin2', vg=vg_name)

            assert thin1.create(virtualsize='100M', type='thin', thinpool='pool1')
            assert thin2.create(virtualsize='100M', type='thin', thinpool='pool2')

            # Log all LVs for debugging
            for lv in lvm.LogicalVolume.get_all(vg_name):
                logging.info(f'LV: {lv.name}')

        finally:
            # Cleanup LVs before VG cleanup
            thin2_lv = lvm.LogicalVolume(name='thin2', vg=vg_name)
            thin1_lv = lvm.LogicalVolume(name='thin1', vg=vg_name)
            spare_lv = lvm.LogicalVolume(name=pmspare_name, vg=vg_name)

            thin2_lv.remove(force='', yes='')
            thin1_lv.remove(force='', yes='')
            pool2.remove(force='', yes='')
            pool1.remove(force='', yes='')
            spare_lv.remove(force='', yes='')
