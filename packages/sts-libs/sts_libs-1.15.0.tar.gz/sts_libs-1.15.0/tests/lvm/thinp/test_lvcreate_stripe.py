"""Tests for lvcreate thin provisioning stripe creation.

This module contains pytest tests for lvcreate command with thin provisioning,
focusing on striped logical volume creation with various stripe options.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

from sts import lvm


@pytest.mark.parametrize('loop_devices', [{'count': 4, 'size_mb': 512}], indirect=True)
class TestLvcreateStripe:
    """Test cases for lvcreate thin provisioning stripe creation."""

    def test_stripes_option(self, setup_loopdev_vg: str) -> None:
        """Test -i|--stripes option."""
        vg_name = setup_loopdev_vg

        pools = []

        # Test different stripe counts
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create('-T', '-i1', extents='1')
        # Check stripe count using data component for thin pools
        assert pool1.get_data_stripes() == '1'
        pools.append(pool1)

        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert pool2.create('-T', stripes='2', size='4M')
        # Check stripe count using data component for thin pools
        assert pool2.get_data_stripes() == '2'
        pools.append(pool2)

        pool3 = lvm.LogicalVolume(name='pool3', vg=vg_name)
        assert pool3.create('--thin', stripes='3', size='4M')
        # Check stripe count using data component for thin pools
        assert pool3.get_data_stripes() == '3'
        pools.append(pool3)

        pool4 = lvm.LogicalVolume(name='pool4', vg=vg_name)
        assert pool4.create('-T', stripes='4', size='4M')
        # Check stripe count using data component for thin pools
        assert pool4.get_data_stripes() == '4'
        pools.append(pool4)

        # Test stripe count too high - should fail (only 4 PVs available)
        pool5 = lvm.LogicalVolume(name='pool5', vg=vg_name)
        assert not pool5.create('-T', stripes='5', size='4M')

        # Clean up using stored objects
        for pool in pools:
            assert pool.remove(force='', yes='')

    def test_stripe_size_option(self, setup_loopdev_vg: str) -> None:
        """Test -I|--stripesize option."""
        vg_name = setup_loopdev_vg

        # Phase 1: Test smaller stripe sizes
        pools_phase1 = []

        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(stripes='2', stripesize='4', size='8M', type='thin-pool')
        # Check stripe size using data component for thin pools
        data_stripe_size = pool1.get_data_stripe_size()
        assert data_stripe_size
        assert data_stripe_size.strip() == '4.00k'
        pools_phase1.append(pool1)

        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert pool2.create(stripes='2', stripesize='8', size='8M', type='thin-pool')
        # Check stripe size using report data directly
        data_stripe_size = pool2.get_data_stripe_size()
        assert data_stripe_size
        assert data_stripe_size.strip() == '8.00k'
        pools_phase1.append(pool2)

        pool3 = lvm.LogicalVolume(name='pool3', vg=vg_name)
        assert pool3.create(stripes='2', stripesize='16', size='8M', type='thin-pool')
        # Check stripe size using report data directly
        data_stripe_size = pool3.get_data_stripe_size()
        assert data_stripe_size
        assert data_stripe_size.strip() == '16.00k'
        pools_phase1.append(pool3)

        pool4 = lvm.LogicalVolume(name='pool4', vg=vg_name)
        assert pool4.create(stripes='2', stripesize='32', size='8M', type='thin-pool')
        # Check stripe size using report data directly
        data_stripe_size = pool4.get_data_stripe_size()
        assert data_stripe_size
        assert data_stripe_size.strip() == '32.00k'
        pools_phase1.append(pool4)

        pool5 = lvm.LogicalVolume(name='pool5', vg=vg_name)
        assert pool5.create(stripes='2', stripesize='64', size='8M', type='thin-pool')
        # Check stripe size using report data directly
        data_stripe_size = pool5.get_data_stripe_size()
        assert data_stripe_size
        assert data_stripe_size.strip() == '64.00k'
        pools_phase1.append(pool5)

        # Clean up phase 1
        for pool in pools_phase1:
            assert pool.remove(force='', yes='')

        # Phase 2: Test larger stripe sizes
        pools_phase2 = []

        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(stripes='2', stripesize='128', size='16M', type='thin-pool')
        # Check stripe size using data component for thin pools
        data_stripe_size = pool1.get_data_stripe_size()
        assert data_stripe_size
        assert data_stripe_size.strip() == '128.00k'
        pools_phase2.append(pool1)

        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert pool2.create(stripes='2', stripesize='256', size='16M', type='thin-pool')
        # Check stripe size using report data directly
        data_stripe_size = pool2.get_data_stripe_size()
        assert data_stripe_size
        assert data_stripe_size.strip() == '256.00k'
        pools_phase2.append(pool2)

        pool3 = lvm.LogicalVolume(name='pool3', vg=vg_name)
        assert pool3.create(stripes='2', stripesize='512', size='32M', type='thin-pool')
        data_stripe_size = pool3.get_data_stripe_size()
        assert data_stripe_size
        # Check stripe size using report data directly
        assert data_stripe_size.strip() == '512.00k'
        pools_phase2.append(pool3)

        pool4 = lvm.LogicalVolume(name='pool4', vg=vg_name)
        assert pool4.create(stripes='2', stripesize='1024', size='64M', type='thin-pool')
        # Check stripe size using report data directly
        data_stripe_size = pool4.get_data_stripe_size()
        assert data_stripe_size
        assert data_stripe_size.strip() == '1.00m'
        pools_phase2.append(pool4)

        # Clean up phase 2
        for pool in pools_phase2:
            assert pool.remove(force='', yes='')

    def test_stripe_size_units(self, setup_loopdev_vg: str) -> None:
        """Test stripe size with different units."""
        vg_name = setup_loopdev_vg

        # Test stripe size with 'k' suffix
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(stripes='2', stripesize='4k', size='8M', type='thin-pool')
        # Check stripe size using data component for thin pools
        data_stripe_size = pool1.get_data_stripe_size()
        assert data_stripe_size
        assert data_stripe_size.strip() == '4.00k'

        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert pool2.create(stripes='2', stripesize='128k', size='16M', type='thin-pool')
        # Check stripe size using report data directly
        data_stripe_size = pool2.get_data_stripe_size()
        assert data_stripe_size
        assert data_stripe_size.strip() == '128.00k'

        # Test stripe size with 'm' suffix
        pool3 = lvm.LogicalVolume(name='pool3', vg=vg_name)
        assert pool3.create(stripes='2', stripesize='1m', size='64M', type='thin-pool')
        # Check stripe size using report data directly
        data_stripe_size = pool3.get_data_stripe_size()
        assert data_stripe_size
        assert data_stripe_size.strip() == '1.00m'

        # Clean up
        for i in range(1, 4):  # pool1 through pool3
            pool = lvm.LogicalVolume(name=f'pool{i}', vg=vg_name)
            assert pool.remove(force='', yes='')

    def test_stripe_size_validation(self, setup_loopdev_vg: str) -> None:
        """Test stripe size validation (power of 2, within limits)."""
        vg_name = setup_loopdev_vg

        pools = []

        # Valid stripe sizes (power of 2)
        valid_sizes = ['4', '8', '16', '32', '64', '128', '256', '512']
        for i, size in enumerate(valid_sizes):
            pool_name = f'pool{i + 1}'
            pool = lvm.LogicalVolume(name=pool_name, vg=vg_name)
            assert pool.create(stripes='2', stripesize=size, size='8M', type='thin-pool')
            pools.append(pool)

        # Clean up using stored objects
        for pool in pools:
            assert pool.remove(force='', yes='')

        # Invalid stripe sizes (not power of 2) - should fail
        invalid_sizes = ['3', '5', '6', '7', '9', '10', '15']
        for i, size in enumerate(invalid_sizes):
            pool_name = f'pool{i + 1}'
            pool = lvm.LogicalVolume(name=pool_name, vg=vg_name)
            assert not pool.create(stripes='2', stripesize=size, size='8M', type='thin-pool')

    def test_stripe_size_limits(self, setup_loopdev_vg: str) -> None:
        """Test stripe size limits."""
        vg_name = setup_loopdev_vg

        # Test minimum stripe size (4k)
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(stripes='2', stripesize='4', size='8M', type='thin-pool')
        # Check stripe size using data component for thin pools
        data_stripe_size = pool1.get_data_stripe_size()
        assert data_stripe_size
        assert data_stripe_size.strip() == '4.00k'

        # Test stripe size too small - should fail
        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert not pool2.create(stripes='2', stripesize='2', size='8M', type='thin-pool')

        # Clean up
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.remove(force='', yes='')

    def test_combined_stripe_options(self, setup_loopdev_vg: str) -> None:
        """Test combining stripe count and stripe size options."""
        vg_name = setup_loopdev_vg

        pools = []

        # Test various combinations
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(stripes='2', stripesize='64', size='16M', type='thin-pool')
        # Check stripe count and size using data component for thin pools
        stripes = pool1.get_data_stripes()
        assert stripes
        assert stripes == '2'
        data_stripe_size = pool1.get_data_stripe_size()
        assert data_stripe_size
        assert data_stripe_size.strip() == '64.00k'
        pools.append(pool1)

        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert pool2.create(stripes='3', stripesize='128', size='24M', type='thin-pool')
        # Check stripe count and size using data component for thin pools
        stripes = pool2.get_data_stripes()
        assert stripes
        assert stripes == '3'
        data_stripe_size = pool2.get_data_stripe_size()
        assert data_stripe_size
        assert data_stripe_size.strip() == '128.00k'
        pools.append(pool2)

        pool3 = lvm.LogicalVolume(name='pool3', vg=vg_name)
        assert pool3.create(stripes='4', stripesize='256', size='32M', type='thin-pool')
        stripes = pool3.get_data_stripes()
        assert stripes
        # Check stripe count and size using data component for thin pools
        assert stripes == '4'
        data_stripe_size = pool3.get_data_stripe_size()
        assert data_stripe_size
        assert data_stripe_size.strip() == '256.00k'
        pools.append(pool3)

        # Clean up using stored objects
        for pool in pools:
            assert pool.remove(force='', yes='')

    def test_stripe_with_percentage_size(self, setup_loopdev_vg: str) -> None:
        """Test striping with percentage-based size allocation."""
        vg_name = setup_loopdev_vg

        pools = []

        # Test striping with percentage allocations
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(stripes='2', extents='10%VG', type='thin-pool')
        # Check stripe count using data component for thin pools
        assert pool1.get_data_stripes() == '2'
        pools.append(pool1)

        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert pool2.create(stripes='3', extents='20%PVS', type='thin-pool')
        # Check stripe count using data component for thin pools
        assert pool2.get_data_stripes() == '3'
        pools.append(pool2)

        pool3 = lvm.LogicalVolume(name='pool3', vg=vg_name)
        assert pool3.create(stripes='4', extents='30%FREE', type='thin-pool')
        # Check stripe count using data component for thin pools
        assert pool3.get_data_stripes() == '4'
        pools.append(pool3)

        # Clean up using stored objects
        for pool in pools:
            assert pool.remove(force='', yes='')
