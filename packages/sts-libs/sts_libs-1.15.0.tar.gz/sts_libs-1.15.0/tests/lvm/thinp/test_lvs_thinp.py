"""Tests for lvs command with thin provisioning.

This module contains pytest tests for the lvs command displaying information
about thin pools, thin volumes, and their attributes.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

from sts import lvm
from sts.utils.cmdline import run


@pytest.mark.parametrize('loop_devices', [{'count': 4, 'size_mb': 128}], indirect=True)
class TestLvsThinp:
    """Test cases for lvs command with thin provisioning."""

    def test_lvs_thin_attributes(self, setup_loopdev_vg: str) -> None:
        """Test lvs command showing thin pool and volume attributes."""
        vg_name = setup_loopdev_vg

        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        lv1 = lvm.LogicalVolume(name='lv1', vg=vg_name)

        try:
            # Create thin pool
            assert pool1.create(size='4M', type='thin-pool')
            assert pool1.report
            # Check initial thin count
            assert pool1.report.thin_count == '0'
            # Create thin LV
            assert lv1.create(virtualsize='100M', type='thin', thinpool='pool1')
            assert lv1.report

            assert pool1.refresh_report()
            # Verify pool attributes
            assert pool1.report.thin_count == '1'
            assert pool1.report.lv_name == 'pool1'
            assert pool1.report.lv_size == '4.00m'
            assert pool1.report.lv_metadata_size == '4.00m'

            # Since RHEL6.7 lvm2 package, adding 'device (o)pen' bit for lv_attr
            # The attr can be 'twi-aotz--' (with open bit) or 'twi-a-tz--' (without)
            assert pool1.report.lv_attr in ['twi-aotz--', 'twi-a-tz--']

            # Verify thin volume attributes
            assert lv1.report.lv_name == 'lv1'
            assert lv1.report.lv_size == '100.00m'
            assert lv1.report.pool_lv == 'pool1'
            assert lv1.report.lv_attr in ['Vwi-aotz--', 'Vwi-a-tz--']

        finally:
            # Cleanup LVs before VG cleanup
            lv1.remove('-f')
            pool1.remove('-f')

    def test_lvs_stripe_attributes(self, setup_loopdev_vg: str) -> None:
        """Test lvs command showing stripe information for thin pools."""
        vg_name = setup_loopdev_vg

        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        lv1 = lvm.LogicalVolume(name='lv1', vg=vg_name)
        lv2 = lvm.LogicalVolume(name='lv2', vg=vg_name)

        try:
            # Create linear pool
            assert pool1.create(size='4M', type='thin-pool')
            assert lv1.create(virtualsize='100M', type='thin', thinpool='pool1')
            assert pool1.report
            assert lv1.report

            # Verify linear attributes - use pool's data stripe method
            data_stripes = pool1.get_data_stripes()
            assert data_stripes
            assert data_stripes == '1'

            # For metadata, get the metadata LV and check its stripes
            metadata_lv_name = pool1.report.metadata_lv.strip('[]') if pool1.report.metadata_lv else None
            assert metadata_lv_name is not None
            tmeta_lv = lvm.LogicalVolume(name=metadata_lv_name, vg=vg_name)
            assert tmeta_lv.refresh_report()
            assert tmeta_lv.report
            assert tmeta_lv.report.stripes == '1'

            # Create striped pool
            assert pool2.create(size='4M', type='thin-pool', stripes='2')
            assert lv2.create(virtualsize='100M', type='thin', thinpool='pool2')

            # Verify striped attributes - use pool's data stripe method
            data_stripes = pool2.get_data_stripes()
            assert data_stripes
            assert data_stripes == '2'

            # For metadata, get the metadata LV and check its stripes
            assert pool2.report
            metadata_lv_name = pool2.report.metadata_lv.strip('[]') if pool2.report.metadata_lv else None
            assert metadata_lv_name is not None
            tmeta_lv = lvm.LogicalVolume(name=metadata_lv_name, vg=vg_name)
            assert tmeta_lv.refresh_report()
            assert tmeta_lv.report
            assert tmeta_lv.report.stripes == '1'  # metadata is always linear

        finally:
            # Cleanup LVs before VG cleanup
            pool1.remove()

    def test_lvs_all_volumes(self, setup_loopdev_vg: str) -> None:
        """Test lvs -a command showing all logical volumes including hidden ones."""
        vg_name = setup_loopdev_vg

        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        lv1 = lvm.LogicalVolume(name='lv1', vg=vg_name)

        try:
            # Create thin pool and volume
            assert pool.create(size='4M', type='thin-pool')
            assert lv1.create(virtualsize='100M', type='thin', thinpool='pool')

            # Run lvs -a to show all volumes including hidden metadata
            result = run(f'lvs -a {vg_name}')
            assert result.succeeded

            # Verify that hidden volumes are shown
            assert '[pool_tdata]' in result.stdout
            assert '[pool_tmeta]' in result.stdout
            assert 'pool' in result.stdout
            assert 'lv1' in result.stdout

            # Run regular lvs (should not show hidden volumes)
            result = run(f'lvs {vg_name}')
            assert result.succeeded

            # Verify that hidden volumes are not shown
            assert '[pool_tdata]' not in result.stdout
            assert '[pool_tmeta]' not in result.stdout
            assert 'pool' in result.stdout
            assert 'lv1' in result.stdout

        finally:
            # Cleanup LVs before VG cleanup
            pool.remove()

    def test_lvs_with_snapshots(self, setup_loopdev_vg: str) -> None:
        """Test lvs command with thin snapshots."""
        vg_name = setup_loopdev_vg

        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        lv1 = lvm.LogicalVolume(name='lv1', vg=vg_name)
        snap1 = None

        try:
            # Create thin pool, volume, and snapshot
            assert pool.create(size='4M', type='thin-pool')
            assert pool.report
            assert lv1.create(virtualsize='100M', type='thin', thinpool='pool')
            snap1 = lv1.create_snapshot('snap1')
            assert snap1 is not None
            assert snap1.report

            # Verify snapshot attributes
            assert snap1.report.lv_attr
            assert snap1.report.lv_attr.startswith('Vwi')
            assert snap1.report.pool_lv == 'pool'
            assert snap1.report.origin == 'lv1'

            assert pool.refresh_report()
            # Verify pool thin count increased
            assert pool.report.thin_count == '2'

        finally:
            # Cleanup LVs before VG cleanup
            # Remove thin volumes first, then pool
            if snap1:
                snap1.remove()
            lv1.remove()
            pool.remove()
