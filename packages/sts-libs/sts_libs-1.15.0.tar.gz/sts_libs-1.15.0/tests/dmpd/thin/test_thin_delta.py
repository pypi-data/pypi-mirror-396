"""Tests for thin_delta DMPD tool.

This module contains pytest tests for the thin_delta command-line tool.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

from sts import dmpd


@pytest.mark.parametrize('loop_devices', [{'count': 1, 'size_mb': 4096}], indirect=True)
class TestThinDelta:
    """Test cases for thin_delta command."""

    def test_thin_delta(self, setup_thin_metadata_for_dmpd: dict[str, str]) -> None:
        """Test various thin_delta operations that can share the same metadata setup."""
        vol_info = setup_thin_metadata_for_dmpd
        metadata_dev = vol_info['metadata_dev']

        # Test basic thin_delta getting differences in thin metadata for LVs
        result_basic = dmpd.thin_delta(metadata_dev, thin1=1, thin2=9)
        assert result_basic.succeeded
        assert '<superblock uuid=' in result_basic.stdout
        assert 'time=' in result_basic.stdout
        assert 'transaction=' in result_basic.stdout
        assert 'data_block_size=' in result_basic.stdout
        assert 'nr_data_blocks=' in result_basic.stdout
        assert 'diff left=' in result_basic.stdout
        assert 'right=' in result_basic.stdout
        assert 'different begin=' in result_basic.stdout
        assert 'length=' in result_basic.stdout
        assert '</diff>' in result_basic.stdout
        assert '</superblock>' in result_basic.stdout

        # Test thin_delta with --verbose
        result_verbose = dmpd.thin_delta(metadata_dev, thin1=1, thin2=9, verbose=True)
        assert result_verbose.succeeded
        assert '<superblock uuid=' in result_verbose.stdout
        assert 'time=' in result_verbose.stdout
        assert 'transaction=' in result_verbose.stdout
        assert 'data_block_size=' in result_verbose.stdout
        assert 'nr_data_blocks=' in result_verbose.stdout
        assert 'diff left=' in result_verbose.stdout
        assert 'right=' in result_verbose.stdout
        assert 'different' in result_verbose.stdout
        assert 'range begin=' in result_verbose.stdout
        assert 'left_data_begin=' in result_verbose.stdout
        assert 'right_data_begin=' in result_verbose.stdout
        assert 'length=' in result_verbose.stdout
        assert '</diff>' in result_verbose.stdout
        assert '</superblock>' in result_verbose.stdout

        # Test thin_delta for the same LV (should show 'same' blocks)
        result_same = dmpd.thin_delta(metadata_dev, thin1=1, thin2=1)
        assert result_same.succeeded
        assert '<superblock uuid=' in result_same.stdout
        assert 'time=' in result_same.stdout
        assert 'transaction=' in result_same.stdout
        assert 'data_block_size=' in result_same.stdout
        assert 'nr_data_blocks=' in result_same.stdout
        assert 'diff left=' in result_same.stdout
        assert 'right=' in result_same.stdout
        assert 'same begin=' in result_same.stdout
        assert 'length=' in result_same.stdout
        assert '</diff>' in result_same.stdout
        assert '</superblock>' in result_same.stdout

        # Test thin_delta with metadata snapshot
        result_snap = dmpd.thin_delta(metadata_dev, thin1=1, thin2=9, metadata_snap=True)
        assert result_snap.succeeded
        assert '<superblock uuid=' in result_snap.stdout
        assert 'time=' in result_snap.stdout
        assert 'transaction=' in result_snap.stdout
        assert 'data_block_size=' in result_snap.stdout
        assert 'nr_data_blocks=' in result_snap.stdout
        assert 'diff left=' in result_snap.stdout
        assert 'right=' in result_snap.stdout
        assert 'different begin=' in result_snap.stdout
        assert 'length=' in result_snap.stdout
        assert '</diff>' in result_snap.stdout
        assert '</superblock>' in result_snap.stdout
