"""Tests for cache_check DMPD tool.

This module contains pytest tests for the cache_check command-line tool,
which is used to check cache metadata integrity.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

import pytest

from sts import dmpd


@pytest.mark.usefixtures('setup_cache_metadata_for_dmpd')
@pytest.mark.parametrize('loop_devices', [{'count': 1, 'size_mb': 4096}], indirect=True)
class TestCacheCheck:
    """Test cases for cache_check command."""

    def test_cache_check_basic(self, setup_cache_metadata_for_dmpd: dict[str, str]) -> None:
        """Test basic cache_check without any extra parameters."""
        cache_info = setup_cache_metadata_for_dmpd
        cache_metadata_dev = cache_info['cache_metadata_dev']

        result = dmpd.cache_check(cache_metadata_dev)

        assert result.succeeded
        logging.info(result.stdout)
        # Cache check should succeed with basic metadata validation

    def test_cache_check_super_block_only(self, setup_cache_metadata_for_dmpd: dict[str, str]) -> None:
        """Test cache_check with --super-block-only flag."""
        cache_info = setup_cache_metadata_for_dmpd
        cache_metadata_dev = cache_info['cache_metadata_dev']

        result = dmpd.cache_check(cache_metadata_dev, super_block_only=True)

        assert result.succeeded
        logging.info(result.stdout)
        # Should check only superblock information

    def test_cache_check_skip_hints(self, setup_cache_metadata_for_dmpd: dict[str, str]) -> None:
        """Test cache_check with --skip-hints flag."""
        cache_info = setup_cache_metadata_for_dmpd
        cache_metadata_dev = cache_info['cache_metadata_dev']

        result = dmpd.cache_check(cache_metadata_dev, skip_hints=True)

        assert result.succeeded
        logging.info(result.stdout)
        # Should skip hint validation

    def test_cache_check_skip_discards(self, setup_cache_metadata_for_dmpd: dict[str, str]) -> None:
        """Test cache_check with --skip-discards flag."""
        cache_info = setup_cache_metadata_for_dmpd
        cache_metadata_dev = cache_info['cache_metadata_dev']

        result = dmpd.cache_check(cache_metadata_dev, skip_discards=True)

        assert result.succeeded
        logging.info(result.stdout)
        # Should skip discard validation

    def test_cache_check_clear_needs_check_flag(self, setup_cache_metadata_for_dmpd: dict[str, str]) -> None:
        """Test cache_check with --clear-needs-check-flag."""
        cache_info = setup_cache_metadata_for_dmpd
        cache_metadata_dev = cache_info['cache_metadata_dev']

        result = dmpd.cache_check(cache_metadata_dev, clear_needs_check_flag=True)

        assert result.succeeded
        logging.info(result.stdout)
        # Should clear any needs check flag during validation
