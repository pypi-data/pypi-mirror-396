"""Tests for thin_check DMPD tool.

This module contains pytest tests for the thin_check command-line tool,
which is used to check thin provisioning metadata integrity.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

import pytest

from sts import dmpd


@pytest.mark.parametrize('loop_devices', [{'count': 1, 'size_mb': 4096}], indirect=True)
class TestThinCheck:
    """Test cases for thin_check command."""

    def test_thin_check_consolidated(self, setup_thin_metadata_for_dmpd: dict[str, str]) -> None:
        """Test various thin_check operations that can share the same metadata setup."""
        vol_info = setup_thin_metadata_for_dmpd
        metadata_dev = vol_info['metadata_dev']

        # Test basic thin_check without any extra parameters
        result_basic = dmpd.thin_check(metadata_dev)
        assert result_basic.succeeded
        logging.info(result_basic.stdout)
        assert 'TRANSACTION_ID=' in result_basic.stdout
        assert 'METADATA_FREE_BLOCKS=' in result_basic.stdout

        # Test thin_check with --super-block-only flag
        result_super_only = dmpd.thin_check(metadata_dev, super_block_only=True)
        assert result_super_only.succeeded
        assert 'TRANSACTION_ID=' in result_super_only.stdout
        assert 'METADATA_FREE_BLOCKS=' in result_super_only.stdout
        # Should not contain full check output when only checking superblock
        assert 'device details tree' not in result_super_only.stdout
        assert 'mapping tree' not in result_super_only.stdout

        # Test thin_check with --skip-mappings flag
        result_skip_mappings = dmpd.thin_check(metadata_dev, skip_mappings=True)
        assert result_skip_mappings.succeeded
        assert 'TRANSACTION_ID=' in result_skip_mappings.stdout
        assert 'METADATA_FREE_BLOCKS=' in result_skip_mappings.stdout

        # Test thin_check with --ignore-non-fatal-errors flag
        result_ignore_errors = dmpd.thin_check(metadata_dev, ignore_non_fatal_errors=True)
        assert result_ignore_errors.succeeded
        assert 'TRANSACTION_ID=' in result_ignore_errors.stdout
        assert 'METADATA_FREE_BLOCKS=' in result_ignore_errors.stdout

        # Test thin_check with --quiet flag
        result_quiet = dmpd.thin_check(metadata_dev, quiet=True)
        assert result_quiet.succeeded
        # Output should be minimal with quiet flag
        assert len(result_quiet.stdout.strip()) < 100  # Expect much less output

        # Test thin_check with --clear-needs-check-flag
        result_clear_flag = dmpd.thin_check(metadata_dev, clear_needs_check_flag=True)
        assert result_clear_flag.succeeded
