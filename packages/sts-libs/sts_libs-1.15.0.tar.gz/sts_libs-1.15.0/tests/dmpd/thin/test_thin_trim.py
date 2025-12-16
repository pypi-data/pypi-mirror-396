"""Tests for thin_trim DMPD tool.

This module contains pytest tests for the thin_trim
command-line tool.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

import pytest

from sts import dmpd
from sts.utils.cmdline import run


@pytest.mark.parametrize('loop_devices', [{'count': 1, 'size_mb': 4096}], indirect=True)
class TestThinTrim:
    """Test cases for thin_trim command."""

    def test_thin_trim_basic(self, restored_thin_pool: dict[str, str]) -> None:
        """Test basic thin_trim functionality."""
        vol_info = restored_thin_pool
        vg_name = vol_info['vg_name']
        pool_name = vol_info['pool_name']

        # Create a metadata repair file for testing using the working metadata file
        repair_file = vol_info['metadata_repair_path']
        working_metadata = vol_info['metadata_working_path']
        result_repair = dmpd.thin_repair(input=str(working_metadata), output=str(repair_file))
        assert result_repair.succeeded

        # Activate the thin pool for trim operation (pool is now restorable)
        activate_result = run(f'lvchange -ay {vg_name}/{pool_name}')
        assert activate_result.succeeded, f'Failed to activate pool: {activate_result.stderr}'

        # Debug: Check what devices are available
        logging.info('Available device-mapper devices:')
        dm_devices = run('ls -la /dev/mapper/ | grep thinpool')
        logging.info(dm_devices.stdout)

        dmsetup_info = run('dmsetup ls | grep thinpool')
        logging.info(f'dmsetup output: {dmsetup_info.stdout}')

        # Test thin_trim - use the pool's data device (_tdata)
        data_dev = f'/dev/mapper/{vg_name}-{pool_name}_tdata'

        # Check if the data device exists before using it
        check_device = run(f'ls -la {data_dev}')
        if not check_device.succeeded:
            logging.error(f'Data device {data_dev} does not exist')
            logging.info('Available /dev/mapper devices:')
            logging.info(run('ls -la /dev/mapper/').stdout)
            pytest.fail(f'Data device {data_dev} not found')

        result = dmpd.thin_trim(data_dev=data_dev, metadata_dev=str(repair_file))

        logging.info(f'thin_trim result: {result.stdout}')

        assert result.succeeded
        # Verify the specific output format with correct transaction ID and metadata blocks
        assert 'TRANSACTION_ID=10' in result.stdout
        assert 'METADATA_FREE_BLOCKS=1208' in result.stdout

        # Deactivate pool again to maintain fixture state
        run(f'lvchange -an {vg_name}/{pool_name}')

    def test_thin_trim_with_repair_file(self, restored_thin_pool: dict[str, str]) -> None:
        """Test thin_trim with repair file input."""
        vol_info = restored_thin_pool
        vg_name = vol_info['vg_name']
        pool_name = vol_info['pool_name']

        # Create a metadata repair file for testing using the working metadata file
        repair_file = vol_info['metadata_repair_path']
        working_metadata = vol_info['metadata_working_path']
        result_repair = dmpd.thin_repair(input=str(working_metadata), output=str(repair_file))
        assert result_repair.succeeded

        # Activate the thin pool for trim operation (pool is now restorable)
        activate_result = run(f'lvchange -ay {vg_name}/{pool_name}')
        assert activate_result.succeeded, f'Failed to activate pool: {activate_result.stderr}'

        # Debug: Check what devices are available
        logging.info('Available device-mapper devices:')
        dm_devices = run('ls -la /dev/mapper/ | grep thinpool')
        logging.info(dm_devices.stdout)

        dmsetup_info = run('dmsetup ls | grep thinpool')
        logging.info(f'dmsetup output: {dmsetup_info.stdout}')

        # Test thin_trim with repair file - use the pool's data device (_tdata)
        data_dev = f'/dev/mapper/{vg_name}-{pool_name}_tdata'

        # Check if the data device exists before using it
        check_device = run(f'ls -la {data_dev}')
        if not check_device.succeeded:
            logging.error(f'Data device {data_dev} does not exist')
            logging.info('Available /dev/mapper devices:')
            logging.info(run('ls -la /dev/mapper/').stdout)
            pytest.fail(f'Data device {data_dev} not found')

        result = dmpd.thin_trim(data_dev=data_dev, metadata_dev=str(repair_file))
        logging.info(f'thin_trim result: {result.stdout}')

        assert result.succeeded
        # Verify the specific output format with correct transaction ID and metadata blocks
        assert 'TRANSACTION_ID=10' in result.stdout
        assert 'METADATA_FREE_BLOCKS=1208' in result.stdout

        # Deactivate pool again to maintain fixture state
        run(f'lvchange -an {vg_name}/{pool_name}')
