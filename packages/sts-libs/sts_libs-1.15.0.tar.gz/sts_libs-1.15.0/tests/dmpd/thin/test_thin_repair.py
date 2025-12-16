"""Tests for thin_repair DMPD tools.

This module contains pytest tests for the thin_repair command-line tool.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
from pathlib import Path
from typing import Any

import pytest

from sts import dmpd


@pytest.mark.parametrize('loop_devices', [{'count': 1, 'size_mb': 4096}], indirect=True)
class TestThinRepair:
    """Test cases for thin_repair command."""

    def test_thin_repair(self, setup_thin_metadata_for_dmpd: dict[str, Any]) -> None:
        """Test various thin_repair operations that can share the same metadata setup."""
        vol_info = setup_thin_metadata_for_dmpd
        metadata_dev = vol_info['metadata_dev']
        repair_file = Path(vol_info['metadata_repair_path'])
        logging.info(f'Repairing metadata to file: {repair_file}')

        # Test repairing metadata to file
        result_to_file = dmpd.thin_repair(input=metadata_dev, output=str(repair_file))
        assert result_to_file.succeeded
        assert repair_file.exists()
        assert repair_file.stat().st_size > 0

        # Test repairing metadata from file to device
        result_from_file = dmpd.thin_repair(input=str(repair_file), output=metadata_dev)
        assert result_from_file.succeeded
