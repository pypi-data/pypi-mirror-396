"""Tests for thin_ls DMPD tools.

This module contains pytest tests for the thin_ls command-line tool.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

from sts import dmpd


@pytest.mark.parametrize('loop_devices', [{'count': 1, 'size_mb': 4096}], indirect=True)
class TestThinLs:
    """Test cases for thin_ls command."""

    def test_thin_ls(self, setup_thin_metadata_for_dmpd: dict[str, str]) -> None:
        """Test various thin_ls operations that can share the same metadata setup."""
        vol_info = setup_thin_metadata_for_dmpd
        metadata_dev = vol_info['metadata_dev']

        # Test basic thin_ls without any extra parameters
        result_basic = dmpd.ThinLs.run(metadata_dev)
        assert result_basic.succeeded
        assert 'DEV' in result_basic.stdout
        assert 'MAPPED' in result_basic.stdout
        assert 'CREATE_TIME' in result_basic.stdout
        assert 'SNAP_TIME' in result_basic.stdout

        # Test thin_ls without headers
        result_no_headers = dmpd.ThinLs.run(metadata_dev, no_headers=True)
        assert result_no_headers.succeeded
        # Should not contain headers when no_headers is True
        assert 'DEV' not in result_no_headers.stdout
        assert 'MAPPED' not in result_no_headers.stdout
        assert 'CREATE_TIME' not in result_no_headers.stdout
        assert 'SNAP_TIME' not in result_no_headers.stdout

        # Test thin_ls from metadata snapshot
        result_snap = dmpd.ThinLs.run(metadata_dev, metadata_snap=True)
        assert result_snap.succeeded
        assert 'DEV' in result_snap.stdout
        assert 'MAPPED' in result_snap.stdout
        assert 'CREATE_TIME' in result_snap.stdout
        assert 'SNAP_TIME' in result_snap.stdout
