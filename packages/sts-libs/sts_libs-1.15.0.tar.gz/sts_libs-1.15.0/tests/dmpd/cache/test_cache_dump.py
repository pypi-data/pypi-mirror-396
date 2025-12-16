"""Tests for cache_dump DMPD tool.

This module contains pytest tests for the cache_dump command-line tool,
which is used to dump cache metadata to stdout or file.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
from pathlib import Path

import pytest

from sts import dmpd
from sts.utils.cmdline import run


@pytest.mark.parametrize('loop_devices', [{'count': 1, 'size_mb': 4096}], indirect=True)
class TestCacheDump:
    """Test cases for cache_dump command."""

    def test_cache_dump_basic(self, setup_cache_metadata_for_dmpd: dict[str, str]) -> None:
        """Test basic cache_dump without any extra parameters."""
        cache_info = setup_cache_metadata_for_dmpd
        cache_metadata_dev = cache_info['cache_metadata_dev']

        result = dmpd.cache_dump(cache_metadata_dev)

        assert result.succeeded
        logging.info(result.stdout)

        # Verify expected cache metadata dump output structure
        expected_patterns = [
            '<superblock uuid=',
            'block_size=',
            'nr_cache_blocks=',
            'policy=',
            'hint_width=',
            '<mappings>',
            '<mapping cache_block=',
            'origin_block=',
            'dirty=',
            '</mappings>',
            '<hints>',
            '<hint cache_block=',
            'data=',
            '</hints>',
            '</superblock>',
        ]

        for pattern in expected_patterns:
            assert pattern in result.stdout, f"Expected pattern '{pattern}' not found in output"

    def test_cache_dump_repair(self, setup_cache_metadata_for_dmpd: dict[str, str]) -> None:
        """Test cache_dump with --repair flag."""
        cache_info = setup_cache_metadata_for_dmpd
        cache_metadata_dev = cache_info['cache_metadata_dev']

        result = dmpd.cache_dump(cache_metadata_dev, repair=True)

        assert result.succeeded
        logging.info(result.stdout)

        # Verify expected cache metadata dump output structure (same as basic)
        expected_patterns = [
            '<superblock uuid=',
            'block_size=',
            'nr_cache_blocks=',
            'policy=',
            'hint_width=',
            '<mappings>',
            '<mapping cache_block=',
            'origin_block=',
            'dirty=',
            '</mappings>',
            '<hints>',
            '<hint cache_block=',
            'data=',
            '</hints>',
            '</superblock>',
        ]

        for pattern in expected_patterns:
            assert pattern in result.stdout, f"Expected pattern '{pattern}' not found in output"

    def test_cache_dump_output_to_file(self, setup_cache_metadata_for_dmpd: dict[str, str]) -> None:
        """Test cache_dump with output to file."""
        cache_info = setup_cache_metadata_for_dmpd
        cache_metadata_dev = cache_info['cache_metadata_dev']
        output_file = Path('/var/tmp/cache_dump_test')

        try:
            # Pre-create empty file (matching setup logic)
            run(f'fallocate -l 5M {output_file!s}')

            result = dmpd.cache_dump(cache_metadata_dev, output=str(output_file))

            assert result.succeeded
            assert output_file.exists()
            assert output_file.stat().st_size > 0
            logging.info(f'Cache dump written to {output_file}, size: {output_file.stat().st_size}')

            # Verify content was written to file
            content = output_file.read_text()
            assert '<superblock uuid=' in content
            assert '</superblock>' in content

        finally:
            # Cleanup
            if output_file.exists():
                output_file.unlink()
