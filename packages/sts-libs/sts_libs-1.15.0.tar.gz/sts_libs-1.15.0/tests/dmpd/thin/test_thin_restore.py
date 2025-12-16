"""Tests for thin_restore DMPD tool.

This module contains pytest tests for the thin_restore
command-line tool.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from pathlib import Path
from typing import Any

import pytest

from sts import dmpd


@pytest.mark.parametrize('loop_devices', [{'count': 1, 'size_mb': 4096}], indirect=True)
class TestThinRestore:
    """Test cases for thin_restore command."""

    def test_thin_restore(self, setup_thin_metadata_for_dmpd: dict[str, Any]) -> None:
        """Test various thin_restore operations that can share the same metadata setup."""
        vol_info = setup_thin_metadata_for_dmpd
        metadata_dev = vol_info['metadata_dev']
        backup_file = Path(vol_info['metadata_backup_path'])
        restore_file = Path(vol_info['metadata_repair_path'])

        # Test basic thin_restore from backup file
        result_basic = dmpd.thin_restore(input=str(backup_file), output=metadata_dev)
        assert result_basic.succeeded

        # Test thin_restore with quiet flag
        result_quiet = dmpd.thin_restore(input=str(backup_file), output=metadata_dev, quiet=True)
        assert result_quiet.succeeded
        # Should have minimal output with quiet flag
        assert len(result_quiet.stdout.strip()) < 50

        # Test thin_restore to file instead of device
        result_to_file = dmpd.thin_restore(input=str(backup_file), output=str(restore_file))
        assert result_to_file.succeeded
        assert restore_file.exists()
        assert restore_file.stat().st_size > 0
