"""Tests for cache_repair DMPD tool.

This module contains pytest tests for the cache_repair command-line tool.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
from pathlib import Path
from typing import Any

import pytest

from sts import dmpd
from sts.utils.cmdline import run


@pytest.mark.parametrize('loop_devices', [{'count': 1, 'size_mb': 4096}], indirect=True)
class TestCacheRepair:
    """Test cases for cache_repair command."""

    def test_cache_repair_to_file(self, setup_cache_metadata_for_dmpd: dict[str, Any]) -> None:
        """Test repairing cache metadata to file."""
        cache_info = setup_cache_metadata_for_dmpd
        cache_metadata_dev = cache_info['cache_metadata_dev']
        repair_file = Path(cache_info['cache_repair_path'])

        logging.info(f'Repairing cache metadata to file: {repair_file}')

        result = dmpd.cache_repair(input=cache_metadata_dev, output=str(repair_file))

        assert result.succeeded
        assert repair_file.exists()
        assert repair_file.stat().st_size > 0
        logging.info(f'Repair file created with size: {repair_file.stat().st_size}')

    def test_cache_repair_from_file(self, setup_cache_metadata_for_dmpd: dict[str, Any]) -> None:
        """Test repairing cache metadata from file to device."""
        cache_info = setup_cache_metadata_for_dmpd
        cache_metadata_dev = cache_info['cache_metadata_dev']
        repair_file = Path(cache_info['cache_repair_path'])

        # First create a repair file
        result1 = dmpd.cache_repair(input=cache_metadata_dev, output=str(repair_file))
        assert result1.succeeded
        assert repair_file.exists()

        # Create a temporary destination device file for the repair operation
        temp_device = Path('/var/tmp/cache_repair_dest')
        try:
            run(f'fallocate -l 5M {temp_device!s}')

            # Now repair from file to temporary device
            result2 = dmpd.cache_repair(input=str(repair_file), output=str(temp_device))
            assert result2.succeeded
            logging.info('Successfully repaired from file to device')

        finally:
            # Cleanup temporary device file
            if temp_device.exists():
                temp_device.unlink()
