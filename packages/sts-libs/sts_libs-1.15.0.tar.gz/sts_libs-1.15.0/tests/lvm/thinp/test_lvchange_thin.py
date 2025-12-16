"""Tests for lvchange thin provisioning operations.

This module contains pytest tests for lvchange command with thin provisioning,
focusing on changing thin pool and thin volume attributes.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import time

import pytest

from sts import lvm


@pytest.mark.parametrize('loop_devices', [{'count': 4, 'size_mb': 512}], indirect=True)
class TestLvchangeThin:
    """Test cases for lvchange thin provisioning operations."""

    def test_pool_discards_active(self, setup_loopdev_vg: str) -> None:
        """Test changing discards with active pool and active thin volume."""
        vg_name = setup_loopdev_vg

        pools = []
        thin_lvs = []

        # Create two thin pools with thin volumes and test them
        for pool_num in range(1, 3):
            pool_name = f'pool{pool_num}'
            lv_name = f'lv{pool_num}'

            # Create thin pool
            pool = lvm.LogicalVolume(name=pool_name, vg=vg_name)
            assert pool.create(size='50M', type='thin-pool')
            pools.append(pool)

            # Create thin volume
            thin_lv = lvm.LogicalVolume(name=lv_name, vg=vg_name)
            assert thin_lv.create(virtualsize='100M', type='thin', thinpool=pool_name)
            thin_lvs.append(thin_lv)

            # Test operations on this pool immediately
            # Initially should be passdown
            # Check discards setting using report data directly
            assert pool.report
            assert pool.report.discards == 'passdown'

            # Change passdown <-> ignore should not work with active pool
            assert not pool.change_discards('ignore')
            # Check discards setting using report data directly
            assert pool.report.discards == 'passdown'

            # Change passdown <-> nopassdown is supported with active pool
            assert pool.change_discards('nopassdown')
            # Check discards setting using report data directly
            assert pool.report.discards == 'nopassdown'

            # Change nopassdown <-> ignore should not work with active pool
            assert not pool.change_discards('ignore')
            # Check discards setting using report data directly
            assert pool.report.discards == 'nopassdown'

            # Change back to passdown
            assert pool.change_discards('passdown')
            # Check discards setting using report data directly
            assert pool.report.discards == 'passdown'

        # Clean up using stored objects
        for thin_lv in thin_lvs:
            assert thin_lv.remove(force='', yes='')
        for pool in pools:
            assert pool.remove(force='', yes='')

    def test_pool_discards_inactive(self, setup_loopdev_vg: str) -> None:
        """Test changing discards with inactive pool and inactive thin volume."""
        vg_name = setup_loopdev_vg

        pools = []
        thin_lvs = []

        # Create two thin pools with thin volumes
        for pool_num in range(1, 3):
            pool_name = f'pool{pool_num}'
            lv_name = f'lv{pool_num}'

            # Create thin pool
            pool = lvm.LogicalVolume(name=pool_name, vg=vg_name)
            assert pool.create(size='50M', type='thin-pool')
            pools.append(pool)

            # Create thin volume
            thin_lv = lvm.LogicalVolume(name=lv_name, vg=vg_name)
            assert thin_lv.create(virtualsize='100M', type='thin', thinpool=pool_name)
            thin_lvs.append(thin_lv)

        # For RHEL, since RHEL-6.7 the LVM attribute when active should be twi-aotz--
        expected_online_attr = 'twi-aotz--'

        # Test on both pools
        for pool_num in range(1, 3):
            pool_name = f'pool{pool_num}'
            lv_name = f'lv{pool_num}'
            pool = pools[pool_num - 1]  # Get the corresponding pool
            thin_lv = thin_lvs[pool_num - 1]  # Get the corresponding thin LV

            # Testing change discards with inactive pool and inactive thin volume
            # Change passdown <-> ignore is supported when inactive
            time.sleep(5)
            assert pool.deactivate()
            assert thin_lv.deactivate()
            time.sleep(5)
            # Check discards setting using report data directly
            assert pool.report
            assert pool.report.discards == 'passdown'
            # Check lv_attr using report data directly
            assert pool.report.lv_attr == 'twi---tz--'

            assert pool.change_discards('ignore')
            assert pool.activate()
            assert thin_lv.activate()
            time.sleep(5)

            # Check discards setting using report data directly
            assert pool.report.discards == 'ignore'
            # Check lv_attr using report data directly
            assert pool.report.lv_attr == expected_online_attr

            # Change ignore <-> nopassdown is supported
            assert pool.deactivate()
            assert thin_lv.deactivate()
            assert pool.change_discards('nopassdown')
            assert pool.activate()
            assert thin_lv.activate()
            # Check discards setting using report data directly
            assert pool.report.discards == 'nopassdown'

            assert pool.deactivate()
            assert thin_lv.deactivate()
            assert pool.change_discards('ignore')
            assert pool.activate()
            assert thin_lv.activate()
            # Check discards setting using report data directly
            assert pool.report.discards == 'ignore'

            # Change passdown <-> ignore is supported when inactive
            assert pool.deactivate()
            assert thin_lv.deactivate()
            assert pool.change_discards('passdown')
            assert pool.activate()
            assert thin_lv.activate()
            # Check discards setting using report data directly
            assert pool.report.discards == 'passdown'

        # Clean up using stored objects
        for thin_lv in thin_lvs:
            assert thin_lv.remove(force='', yes='')
        for pool in pools:
            assert pool.remove(force='', yes='')

    def test_thin_lv_activation(self, setup_loopdev_vg: str) -> None:
        """Test activation and deactivation of thin volumes."""
        vg_name = setup_loopdev_vg

        # Create thin pool
        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        assert pool.create(size='100M', type='thin-pool')

        thin_lvs = []

        # Create multiple thin volumes and test activation/deactivation
        for i in range(1, 4):
            lv_name = f'lv{i}'
            thin_lv = lvm.LogicalVolume(name=lv_name, vg=vg_name)
            assert thin_lv.create(virtualsize='50M', type='thin', thinpool='pool')
            thin_lvs.append(thin_lv)

            # Test activation/deactivation immediately
            assert thin_lv.deactivate()
            assert thin_lv.activate()

        # Clean up using stored objects
        for thin_lv in thin_lvs:
            assert thin_lv.remove(force='', yes='')
        assert pool.remove(force='', yes='')

    def test_pool_activation(self, setup_loopdev_vg: str) -> None:
        """Test activation and deactivation of thin pools."""
        vg_name = setup_loopdev_vg

        # Create thin pool
        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        assert pool.create(size='100M', type='thin-pool')

        # Create thin volume
        thin_lv = lvm.LogicalVolume(name='lv1', vg=vg_name)
        assert thin_lv.create(virtualsize='50M', type='thin', thinpool='pool')

        # Test pool activation/deactivation
        # Deactivate thin volume first
        assert thin_lv.deactivate()

        # Deactivate pool
        assert pool.deactivate()

        # Activate pool
        assert pool.activate()

        # Activate thin volume
        assert thin_lv.activate()

        # Clean up
        assert thin_lv.remove(force='', yes='')
        assert pool.remove(force='', yes='')

    def test_pool_attribute_verification(self, setup_loopdev_vg: str) -> None:
        """Test verification of thin pool attributes."""
        vg_name = setup_loopdev_vg

        # Create thin pool with specific discards setting
        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        assert pool.create(size='100M', type='thin-pool', discards='nopassdown')

        # Verify initial state
        # Check discards setting using report data directly
        assert pool.report
        assert pool.report.discards == 'nopassdown'

        # Test changing to other valid values
        assert pool.change_discards('passdown')
        # Check discards setting using report data directly
        assert pool.report.discards == 'passdown'

        # Clean up
        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        assert pool.remove(force='', yes='')

    def test_multiple_pools_concurrent(self, setup_loopdev_vg: str) -> None:
        """Test operations on multiple pools concurrently."""
        vg_name = setup_loopdev_vg

        pools = []
        thin_lvs = []

        # Create multiple pools and thin volumes in one loop
        for i in range(1, 4):
            pool_name = f'pool{i}'
            pool = lvm.LogicalVolume(name=pool_name, vg=vg_name)
            assert pool.create(size='30M', type='thin-pool')
            pools.append(pool)

            # Create thin volume in each pool
            lv_name = f'lv{i}'
            thin_lv = lvm.LogicalVolume(name=lv_name, vg=vg_name)
            assert thin_lv.create(virtualsize='50M', type='thin', thinpool=pool_name)
            thin_lvs.append(thin_lv)

            # Test operations on the pool immediately
            assert pool.change_discards('nopassdown')
            # Check discards setting using report data directly
            assert pool.report
            assert pool.report.discards == 'nopassdown'

        # Clean up using stored objects
        for thin_lv in thin_lvs:
            assert thin_lv.remove(force='', yes='')
        for pool in pools:
            assert pool.remove(force='', yes='')
