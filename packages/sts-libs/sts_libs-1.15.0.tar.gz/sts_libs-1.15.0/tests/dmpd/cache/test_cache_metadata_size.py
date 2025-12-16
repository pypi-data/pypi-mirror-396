"""Tests for cache_metadata_size DMPD tool.

This module contains pytest tests for the cache_metadata_size command-line tool,
which is used to calculate cache metadata size requirements.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from sts import dmpd


class TestCacheMetadataSize:
    """Test cases for cache_metadata_size command."""

    def test_cache_metadata_size_basic(self) -> None:
        """Test cache_metadata_size with basic parameters."""
        # Test basic calculation with block_size and device_size
        # Block size must be multiple of 32 KiB, using '64k' for 64 KiB
        result = dmpd.cache_metadata_size(block_size='64k', device_size='1024k', max_hint_width=4)

        assert result.succeeded
        logging.info(result.stdout)

        # Verify expected output format (should show sector count)
        assert 'sectors' in result.stdout

    def test_cache_metadata_size_with_nr_blocks(self) -> None:
        """Test cache_metadata_size with nr_blocks parameter."""
        # Test calculation using number of blocks instead of device size
        result = dmpd.cache_metadata_size(nr_blocks=100, max_hint_width=4)

        assert result.succeeded
        logging.info(result.stdout)

        # Verify expected output format (should show sector count)
        assert 'sectors' in result.stdout

    def test_cache_metadata_size_various_parameters(self) -> None:
        """Test cache_metadata_size with various parameter combinations."""
        # Test with different block sizes (must be multiples of 32 KiB)
        for block_size in ['32k', '64k', '128k']:
            result = dmpd.cache_metadata_size(block_size=block_size, device_size='2048k', max_hint_width=4)

            assert result.succeeded
            assert 'sectors' in result.stdout
            logging.info(f'Block size {block_size}: {result.stdout.strip()}')

    def test_cache_metadata_size_different_hint_widths(self) -> None:
        """Test cache_metadata_size with different hint widths."""
        # Test with different hint widths
        for hint_width in [2, 4, 8]:
            result = dmpd.cache_metadata_size(block_size='64k', device_size='1024k', max_hint_width=hint_width)

            assert result.succeeded
            assert 'sectors' in result.stdout
            logging.info(f'Hint width {hint_width}: {result.stdout.strip()}')
