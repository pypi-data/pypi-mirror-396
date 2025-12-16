"""Tests for cache_restore DMPD tool.

This module contains pytest tests for the cache_restore command-line tool.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
from pathlib import Path

import pytest

from sts import dmpd
from sts.utils.cmdline import run


@pytest.mark.parametrize('loop_devices', [{'count': 1, 'size_mb': 4096}], indirect=True)
class TestCacheRestore:
    """Test cases for cache_restore command."""

    def test_cache_restore_from_file_v1(self, setup_cache_metadata_for_dmpd: dict[str, str]) -> None:
        """Test restoring cache metadata from file with metadata version 1."""
        cache_info = setup_cache_metadata_for_dmpd
        cache_dump_path = cache_info['cache_dump_path']

        # Create a temporary destination device for restore
        restore_device = Path('/var/tmp/cache_restore_v1')
        try:
            run(f'fallocate -l 5M {restore_device!s}')

            result = dmpd.cache_restore(input=str(cache_dump_path), output=str(restore_device), metadata_version=1)

            assert result.succeeded
            assert restore_device.exists()
            assert restore_device.stat().st_size > 0
            logging.info('Successfully restored cache metadata with version 1')

        finally:
            if restore_device.exists():
                restore_device.unlink()

    def test_cache_restore_from_file_v2(self, setup_cache_metadata_for_dmpd: dict[str, str]) -> None:
        """Test restoring cache metadata from file with metadata version 2."""
        cache_info = setup_cache_metadata_for_dmpd
        cache_dump_path = cache_info['cache_dump_path']

        # Create a temporary destination device for restore
        restore_device = Path('/var/tmp/cache_restore_v2')
        try:
            run(f'fallocate -l 5M {restore_device!s}')

            result = dmpd.cache_restore(input=str(cache_dump_path), output=str(restore_device), metadata_version=2)

            assert result.succeeded
            assert restore_device.exists()
            assert restore_device.stat().st_size > 0
            logging.info('Successfully restored cache metadata with version 2')

        finally:
            if restore_device.exists():
                restore_device.unlink()

    def test_cache_restore_basic(self, setup_cache_metadata_for_dmpd: dict[str, str]) -> None:
        """Test basic cache restore operation without specifying metadata version."""
        cache_info = setup_cache_metadata_for_dmpd
        cache_dump_path = cache_info['cache_dump_path']

        # Create a temporary destination device for restore
        restore_device = Path('/var/tmp/cache_restore_basic')
        try:
            run(f'fallocate -l 5M {restore_device!s}')

            result = dmpd.cache_restore(input=str(cache_dump_path), output=str(restore_device))

            assert result.succeeded
            assert restore_device.exists()
            assert restore_device.stat().st_size > 0
            logging.info('Successfully restored cache metadata (default version)')

        finally:
            if restore_device.exists():
                restore_device.unlink()
