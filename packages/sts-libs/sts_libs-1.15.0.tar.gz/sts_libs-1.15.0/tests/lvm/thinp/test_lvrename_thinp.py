"""Tests for renaming thin provisioning logical volumes.

This module contains pytest tests for renaming thin pools and thin volumes,
verifying that relationships are maintained correctly.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

from sts import lvm


@pytest.mark.parametrize('loop_devices', [{'count': 4, 'size_mb': 128}], indirect=True)
class TestLvrenameThinp:
    """Test cases for renaming thin provisioning volumes."""

    def test_rename_pools_and_volumes(self, setup_loopdev_vg: str) -> None:
        """Test renaming thin pools and thin volumes."""
        vg_name = setup_loopdev_vg

        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        lv1 = lvm.LogicalVolume(name='lv1', vg=vg_name)
        lv2 = lvm.LogicalVolume(name='lv2', vg=vg_name)

        try:
            # Create thin pools with thin volumes
            assert pool1.create(extents='20', type='thin-pool')
            assert lv1.create(virtualsize='100M', type='thin', thinpool='pool1')

            assert pool2.create(extents='20', type='thin-pool', stripes='2')
            assert lv2.create(virtualsize='100M', type='thin', thinpool='pool2')

            # Test renaming pools and verifying thin LV relationships
            for num in range(1, 3):
                old_pool_name = f'pool{num}'
                new_pool_name = f'bakpool{num}'
                old_lv_name = f'lv{num}'
                new_lv_name = f'baklv{num}'

                # Rename pool using LogicalVolume method
                pool = lvm.LogicalVolume(name=old_pool_name, vg=vg_name)
                assert pool.rename(new_pool_name), f'Failed to rename {old_pool_name} to {new_pool_name}'

                # Verify new pool exists and old doesn't
                all_lvs = lvm.LogicalVolume.get_all(vg=vg_name)
                assert any(lv.name == new_pool_name for lv in all_lvs), f'{new_pool_name} should exist'
                assert not any(lv.name == old_pool_name for lv in all_lvs), f'{old_pool_name} should not exist'

                # Verify thin LV now points to renamed pool
                # Find the thin LV in the existing list
                thin_lv = next(lv for lv in all_lvs if lv.name == old_lv_name)
                assert thin_lv.report
                assert thin_lv.report.pool_lv == new_pool_name, f'LV {old_lv_name} should point to {new_pool_name}'

                # Rename thin LV using LogicalVolume method
                assert thin_lv.rename(new_lv_name), f'Failed to rename {old_lv_name} to {new_lv_name}'

                # Verify new LV exists and old doesn't
                all_lvs = lvm.LogicalVolume.get_all(vg=vg_name)
                assert any(lv.name == new_lv_name for lv in all_lvs), f'{new_lv_name} should exist'
                assert not any(lv.name == old_lv_name for lv in all_lvs), f'{old_lv_name} should not exist'

                # Verify renamed LV still points to renamed pool
                new_lv = next(lv for lv in all_lvs if lv.name == new_lv_name)
                assert new_lv.report
                assert new_lv.report.pool_lv == new_pool_name, f'LV {new_lv_name} should point to {new_pool_name}'

        finally:
            # Cleanup LVs before VG cleanup
            # Remove thin volumes first, then pools
            for num in range(1, 3):
                lv_name = f'baklv{num}' if num <= 2 else f'lv{num}'
                pool_name = f'bakpool{num}' if num <= 2 else f'pool{num}'

                # Remove thin volume first
                lv = lvm.LogicalVolume(name=lv_name, vg=vg_name)
                lv.remove('-f')

                # Remove pool
                pool = lvm.LogicalVolume(name=pool_name, vg=vg_name)
                pool.remove('-f')
