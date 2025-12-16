"""Tests for removing thin provisioning logical volumes.

This module contains pytest tests for removing thin pools, thin volumes,
and snapshots with various confirmation methods.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

from sts import lvm


@pytest.mark.parametrize('loop_devices', [{'count': 4, 'size_mb': 256}], indirect=True)
class TestLvremoveThinp:
    """Test cases for removing thin provisioning volumes."""

    def test_remove_pool_operations(self, setup_loopdev_vg: str) -> None:
        """Test various methods of removing thin pools."""
        vg_name = setup_loopdev_vg

        # Test removing pool with interactive confirmation
        pool1 = lvm.LogicalVolume(name='pool', vg=vg_name)
        assert pool1.create(extents='20', type='thin-pool')

        # Simulate interactive removal (automatically answered with yes)
        assert pool1.remove()

        # Test removing pool with -f flag
        pool2 = lvm.LogicalVolume(name='pool', vg=vg_name)
        assert pool2.create(extents='20', type='thin-pool')
        assert pool2.remove('-f')

        # Test removing pool with -ff flag
        pool3 = lvm.LogicalVolume(name='pool', vg=vg_name)
        assert pool3.create(extents='20', type='thin-pool')
        assert pool3.remove('-ff')

        # Test removing entire VG - remove pool manually
        pool4 = lvm.LogicalVolume(name='pool', vg=vg_name)
        assert pool4.create(extents='20', type='thin-pool')
        assert pool4.remove('-f')

    def test_remove_thin_volumes(self, setup_loopdev_vg: str) -> None:
        """Test removing individual thin volumes."""
        vg_name = setup_loopdev_vg

        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        lv1 = lvm.LogicalVolume(name='lv1', vg=vg_name)

        try:
            # Create pool first
            assert pool.create(extents='20', type='thin-pool')

            # Create thin volume in the pool
            assert lv1.create(virtualsize='100M', type='thin', thinpool='pool')

            # Remove thin volume
            assert lv1.remove('-f')

        finally:
            # Cleanup
            pool.remove('-f')

    def test_remove_multiple_thin_volumes(self, setup_loopdev_vg: str) -> None:
        """Test removing multiple thin volumes at once."""
        vg_name = setup_loopdev_vg

        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        lv1 = lvm.LogicalVolume(name='lv1', vg=vg_name)
        lv2 = lvm.LogicalVolume(name='lv2', vg=vg_name)
        lv3 = lvm.LogicalVolume(name='lv3', vg=vg_name)

        try:
            # Test 1: Remove multiple volumes at once (lv1 and two others)
            # Create pool
            assert pool.create(extents='20', type='thin-pool')

            # Create multiple thin volumes
            assert lv1.create(virtualsize='100M', type='thin', thinpool='pool')
            assert lv2.create(virtualsize='100M', type='thin', thinpool='pool')
            assert lv3.create(virtualsize='100M', type='thin', thinpool='pool')

            # Remove multiple volumes using updated remove method (removes lv1, lv2, lv3)
            assert lv1.remove(f'{vg_name}/lv2', f'{vg_name}/lv3', '-f')

            # Pool should still exist but be empty
            assert pool.remove('-f')

            # Test 2: Remove all volumes with -ff flag
            # Recreate pool (it was removed above)
            assert pool.create(extents='20', type='thin-pool')

            # Recreate thin volumes
            assert lv1.create(virtualsize='100M', type='thin', thinpool='pool')
            assert lv2.create(virtualsize='100M', type='thin', thinpool='pool')
            assert lv3.create(virtualsize='100M', type='thin', thinpool='pool')

            # Remove all three volumes with -ff flag
            assert lv1.remove(f'{vg_name}/lv2', f'{vg_name}/lv3', '-ff')

        finally:
            # Cleanup - remove pool if it still exists
            pool.remove('-f')

    def test_remove_snapshots(self, setup_loopdev_vg: str) -> None:
        """Test removing thin snapshots."""
        vg_name = setup_loopdev_vg

        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        lv1 = lvm.LogicalVolume(name='lv1', vg=vg_name)

        try:
            # Create pool and thin volume
            assert pool.create(extents='20', type='thin-pool')
            assert lv1.create(virtualsize='100M', type='thin', thinpool='pool')

            # Create snapshots using the correct method
            snap1 = lv1.create_snapshot('snap1')
            assert snap1 is not None

            snap2 = snap1.create_snapshot('snap2')
            assert snap2 is not None

            # Remove snapshots using updated remove method
            assert snap1.remove(f'{vg_name}/snap2', '-f')

        finally:
            # Cleanup remaining volumes
            lv1.remove('-f')
            pool.remove('-f')
