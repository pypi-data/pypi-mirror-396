"""Tests for lvcreate thin provisioning linear creation.

This module contains pytest tests for lvcreate command with thin provisioning,
focusing on linear logical volume creation with various options.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

import pytest

from sts import lvm
from sts.utils.cmdline import run


@pytest.mark.parametrize('loop_devices', [{'count': 4, 'size_mb': 512}], indirect=True)
class TestLvcreateLinear:
    """Test cases for lvcreate thin provisioning linear creation."""

    def test_thin_pool_creation_basic(self, setup_loopdev_vg: str) -> None:
        """Test basic thin pool creation with different options."""
        vg_name = setup_loopdev_vg

        pools = []
        thin_lvs = []

        # Test thin pool creation with different options
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create('--thin', extents='1')
        pools.append(pool1)

        pool_lv2 = lvm.LogicalVolume(name='lvol0', vg=vg_name)
        assert pool_lv2.create(extents='1', type='thin-pool')
        pools.append(pool_lv2)

        pool_lv3 = lvm.LogicalVolume(name='lvol1', vg=vg_name)
        assert pool_lv3.create(extents='1', type='thin-pool')
        pools.append(pool_lv3)

        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert pool2.create(size='4M', type='thin-pool')
        pools.append(pool2)

        pool3 = lvm.LogicalVolume(name='pool3', vg=vg_name)
        assert pool3.create(size='4M', type='thin-pool')
        pools.append(pool3)

        pool4 = lvm.LogicalVolume(name='pool4', vg=vg_name)
        assert pool4.create(size='4M', type='thin-pool')
        pools.append(pool4)

        # Store thin volumes created by pool3 and pool4
        lv1 = lvm.LogicalVolume(name='lv1', vg=vg_name)
        assert lv1.create(virtualsize='2G', type='thin', thinpool='pool3')

        lv2 = lvm.LogicalVolume(name='lv2', vg=vg_name)
        assert lv2.create(virtualsize='2G', type='thin', thinpool='pool4')
        thin_lvs.extend([lv1, lv2])

        # Clean up using stored objects
        for thin_lv in thin_lvs:
            assert thin_lv.remove(force='', yes='')
        for pool in pools:
            assert pool.remove(force='', yes='')

    def test_thin_lv_in_existing_pool(self, setup_loopdev_vg: str) -> None:
        """Test creating thin LV in existing pool."""
        vg_name = setup_loopdev_vg
        thin_lvs = []

        # Create thin pool first
        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        assert pool.create(size='4M', type='thin-pool')

        # Create thin LVs with 2G, LVM will name the LV
        thin_lv1 = lvm.LogicalVolume(name='lvol0', vg=vg_name)
        assert thin_lv1.create(virtualsize='2G', type='thin', thinpool='pool')
        thin_lvs.append(thin_lv1)

        thin_lv2 = lvm.LogicalVolume(name='lv1', vg=vg_name)
        assert thin_lv2.create(virtualsize='2G', type='thin', thinpool='pool')
        thin_lvs.append(thin_lv2)

        thin_lv3 = lvm.LogicalVolume(name='lv2', vg=vg_name)
        assert thin_lv3.create(virtualsize='2G', type='thin', thinpool='pool')
        thin_lvs.append(thin_lv3)

        for lv in thin_lvs:
            lv.remove(force='', yes='')

        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        assert pool.remove(force='', yes='')

    def test_thin_type_options(self, setup_loopdev_vg: str) -> None:
        """Test --type thin|thin-pool options."""
        vg_name = setup_loopdev_vg
        pools = []

        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(extents='1', type='thin', virtualsize='1G')
        pools.append(pool1)

        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert pool2.create(extents='1', type='thin-pool')
        pools.append(pool2)

        # Test RHEL6.6 --type thin bug 1176006 - should fail
        pool3 = lvm.LogicalVolume(name='pool', vg=vg_name)
        assert not pool3.create(extents='1', type='thin')

        for pool in pools:
            pool.remove(force='', yes='')

    def test_thinpool_name_options(self, setup_loopdev_vg: str) -> None:
        """Test --thinpool name/path options."""
        vg_name = setup_loopdev_vg
        pools = []

        pool3 = lvm.LogicalVolume(name='pool3', vg=vg_name)
        assert pool3.create(extents='1', type='thin-pool')
        pools.append(pool3)

        pool4 = lvm.LogicalVolume(name='pool4', vg=vg_name)
        assert pool4.create(extents='1', type='thin-pool')
        pools.append(pool4)

        pool5 = lvm.LogicalVolume(name='pool5', vg=vg_name)
        assert pool5.create(extents='1', type='thin-pool')
        pools.append(pool5)

        for pool in pools:
            pool.remove(force='', yes='')

    def test_lv_metadata_size(self, setup_loopdev_vg: str) -> None:
        """Test if LVM lv_metadata_size is correct."""
        vg_name = setup_loopdev_vg

        # Create pool with specific chunk size and verify metadata size
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(size='8M', chunksize='256', type='thin-pool')

        assert pool1.report

        # Check metadata size using report data directly
        assert pool1.report.lv_metadata_size == '4.00m'

        # Create pool with specific metadata size
        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert pool2.create(size='16M', poolmetadatasize='8', type='thin-pool')

        # Check metadata size using report data directly
        assert pool2.report
        assert pool2.report.lv_metadata_size == '8.00m'

    def test_chunksize_options(self, setup_loopdev_vg: str) -> None:
        """Test --chunksize, -c options."""
        vg_name = setup_loopdev_vg

        # Small chunk size (min is 64KB)
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(chunksize='64', extents='1', type='thin-pool')

        assert pool1.report

        # Check chunk size using report data directly
        assert pool1.report.chunk_size == '64.00k'

        # Test chunk size too small - should fail
        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert not pool2.create(chunksize='32', extents='1', type='thin-pool')

        # Big chunk size (max is 1048576 - 1G)
        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert pool2.create(chunksize='1048576', size='1g', type='thin-pool')

        assert pool2.report

        # Check chunk size using report data directly
        assert pool2.report.chunk_size == '1.00g'

        # Test chunk size too big - should fail
        pool3 = lvm.LogicalVolume(name='pool3', vg=vg_name)
        assert not pool3.create(chunksize='2097152', size='2g', type='thin-pool')

        # Check if chunk size is correct for 512k
        pool3 = lvm.LogicalVolume(name='pool3', vg=vg_name)
        assert pool3.create(extents='1', chunksize='512', type='thin-pool')

        assert pool3.report

        # Check chunk size using report data directly
        assert pool3.report.chunk_size == '512.00k'

        # Clean up - remove all LVs from this VG
        result = run(f'lvs {vg_name} --noheadings -o lv_name')
        if result.succeeded:
            lv_names = result.stdout.strip().split('\n')
            for lv_name in lv_names:
                if lv_name.strip():
                    lv = lvm.LogicalVolume(name=lv_name.strip(), vg=vg_name)
                    assert lv.remove(force='', yes='')

    def test_extents_percentage(self, setup_loopdev_vg: str) -> None:
        """Test --extents -l %FREE, VG, PVS."""
        vg_name = setup_loopdev_vg

        # Test percentage allocations
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(extents='10%VG', type='thin-pool')

        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert pool2.create(extents='10%PVS', type='thin-pool')

        pool4 = lvm.LogicalVolume(name='pool4', vg=vg_name)
        assert pool4.create(extents='10%PVS', type='thin-pool')

        pool3 = lvm.LogicalVolume(name='pool3', vg=vg_name)
        assert pool3.create(extents='10%FREE', type='thin-pool')

        pool5 = lvm.LogicalVolume(name='pool5', vg=vg_name)
        assert pool5.create(extents='100%FREE', type='thin-pool')

        # Verify VG state
        assert run('vgs').succeeded

        # Clean up - remove all LVs from this VG
        result = run(f'lvs {vg_name} --noheadings -o lv_name')
        if result.succeeded:
            lv_names = result.stdout.strip().split('\n')
            for lv_name in lv_names:
                if lv_name.strip():
                    lv = lvm.LogicalVolume(name=lv_name.strip(), vg=vg_name)
                    assert lv.remove(force='', yes='')

        # Test 100% allocations
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(extents='100%VG', type='thin-pool')
        assert pool1.remove(force='', yes='')

        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(extents='100%PVS', type='thin-pool')
        assert pool1.remove(force='', yes='')

        # Test with invalid option - should fail
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert not pool1.create(extents='10%test', type='thin-pool')

        # Since RHEL-6.6 LVM improved usage of percentage allocation
        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert pool2.create(extents='110%FREE', type='thin-pool')

        # Clean up - remove all LVs from this VG
        result = run(f'lvs {vg_name} --noheadings -o lv_name')
        if result.succeeded:
            lv_names = result.stdout.strip().split('\n')
            for lv_name in lv_names:
                if lv_name.strip():
                    lv = lvm.LogicalVolume(name=lv_name.strip(), vg=vg_name)
                    assert lv.remove(force='', yes='')

    def test_virtualsize_units(self, setup_loopdev_vg: str) -> None:
        """Test -virtualsize -V (using different size units)."""
        vg_name = setup_loopdev_vg

        # Create thin pool first
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(extents='90%FREE', type='thin-pool')

        # Test different size units
        thin_lv1 = lvm.LogicalVolume(name='thin1', vg=vg_name)
        assert thin_lv1.create(virtualsize='4096B', type='thin', thinpool='pool1')

        logging.info(f'{pool1.report}')

        thin_lv2 = lvm.LogicalVolume(name='thin2', vg=vg_name)
        assert thin_lv2.create(virtualsize='4096K', type='thin', thinpool='pool1')

        thin_lv3 = lvm.LogicalVolume(name='thin3', vg=vg_name)
        assert thin_lv3.create(virtualsize='4096M', type='thin', thinpool='pool1')

        thin_lv4 = lvm.LogicalVolume(name='thin4', vg=vg_name)
        assert thin_lv4.create(virtualsize='1G', type='thin', thinpool='pool1')

        thin_lv5 = lvm.LogicalVolume(name='thin5', vg=vg_name)
        assert thin_lv5.create(virtualsize='1T', type='thin', thinpool='pool1')

        thin_lv6 = lvm.LogicalVolume(name='thin6', vg=vg_name)
        assert thin_lv6.create(virtualsize='15P', type='thin', thinpool='pool1')

        # Exceed maximum size - should fail
        thin_lv7 = lvm.LogicalVolume(name='thin7', vg=vg_name)
        assert not thin_lv7.create(virtualsize='16P', type='thin', thinpool='pool1')

    def test_discards_option(self, setup_loopdev_vg: str) -> None:
        """Test --discards option."""
        vg_name = setup_loopdev_vg

        # Default discards is passdown
        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        assert pool.create(size='92m', type='thin-pool')
        assert pool.report
        # Check discards setting using report data directly
        assert pool.report.discards == 'passdown'

        # Test different discard options
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(size='16m', type='thin-pool', discards='nopassdown')
        assert pool1.report
        # Check discards setting using report data directly
        assert pool1.report.discards == 'nopassdown'

        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert pool2.create(size='16m', type='thin-pool', discards='ignore')

        assert pool2.report

        # Check discards setting using report data directly
        assert pool2.report.discards == 'ignore'

        pool3 = lvm.LogicalVolume(name='pool3', vg=vg_name)
        assert pool3.create(size='16m', type='thin-pool', discards='passdown')
        assert pool3.report
        # Check discards setting using report data directly
        assert pool3.report.discards == 'passdown'

        # Clean up - remove all LVs from this VG
        result = run(f'lvs {vg_name} --noheadings -o lv_name')
        if result.succeeded:
            lv_names = result.stdout.strip().split('\n')
            for lv_name in lv_names:
                if lv_name.strip():
                    lv = lvm.LogicalVolume(name=lv_name.strip(), vg=vg_name)
                    assert lv.remove(force='', yes='')

    def test_percentage_extents(self, setup_loopdev_vg: str) -> None:
        """Test --extents -l %FREE, VG, PVS options."""
        vg_name = setup_loopdev_vg

        # Test percentage-based extent allocation
        pools = []

        # Test various percentage allocations
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(extents='10%VG', type='thin-pool')
        pools.append(pool1)

        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert pool2.create(extents='10%PVS', type='thin-pool')
        pools.append(pool2)

        pool3 = lvm.LogicalVolume(name='pool3', vg=vg_name)
        assert pool3.create(extents='10%FREE', type='thin-pool')
        pools.append(pool3)

        pool4 = lvm.LogicalVolume(name='pool4', vg=vg_name)
        assert pool4.create(extents='10%PVS', type='thin-pool')
        pools.append(pool4)

        # Clean up phase 1
        for pool in pools:
            assert pool.remove(force='', yes='')

        # Test 100% allocations
        pool5 = lvm.LogicalVolume(name='pool5', vg=vg_name)
        assert pool5.create(extents='100%FREE', type='thin-pool')
        assert pool5.remove(force='', yes='')

        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(extents='100%VG', type='thin-pool')
        assert pool1.remove(force='', yes='')

        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(extents='100%PVS', type='thin-pool')
        assert pool1.remove(force='', yes='')

        # Test invalid option - should fail
        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert not pool1.create(extents='10%test', type='thin-pool')

        # Since RHEL-6.6 LVM improved percentage allocation
        # lvcreate man page: When expressed as a percentage, the number is treated
        # as an approximate upper limit for the total number of physical extents to
        # be allocated (including extents used by any mirrors, for example).
        pool2 = lvm.LogicalVolume(name='pool2', vg=vg_name)
        assert pool2.create(extents='110%FREE', type='thin-pool')
        assert pool2.remove(force='', yes='')

        pool1 = lvm.LogicalVolume(name='pool1', vg=vg_name)
        assert pool1.create(extents='90%FREE', type='thin-pool')
        assert pool1.remove(force='', yes='')

    def test_invalid_options(self, setup_loopdev_vg: str) -> None:
        """Test invalid options."""
        vg_name = setup_loopdev_vg

        # Thin pool mirror is not supported
        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        assert not pool.create(extents='1', mirrors='1', type='thin-pool')

        # Create pool first and test mirror conversion
        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        assert pool.create(size='4M', type='thin-pool')

        # Converting to mirror should fail
        assert not pool.convert('-m 1')

        # Clean up - remove all LVs from this VG
        pool.remove(force='')
