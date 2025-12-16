"""Tests for thin_metadata_size DMPD tool.

This module contains pytest tests for the thin_metadata_size command-line tool.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from sts import dmpd


class TestThinMetadataSize:
    """Test cases for thin_metadata_size command."""

    def test_thin_metadata_size(self) -> None:
        """Test various thin_metadata_size operations that don't require any setup."""
        # Test basic thin_metadata_size calculation
        result_basic = dmpd.thin_metadata_size(block_size='64k', pool_size='100m', max_thins=1)
        assert result_basic.succeeded
        assert 'sectors' in result_basic.stdout.lower()
        # Should contain a numeric value
        assert '120 sectors' in result_basic.stdout.lower()

        # Test thin_metadata_size with numeric only output
        result_numeric = dmpd.thin_metadata_size(block_size='64k', pool_size='100m', max_thins=1, numeric_only=True)
        assert result_numeric.succeeded
        # Should not contain unit text with numeric_only
        assert 'mebibytes' not in result_numeric.stdout.lower()
        # Should contain a numeric value
        assert any(char.isdigit() for char in result_numeric.stdout)
        assert int(result_numeric.stdout.strip()) == 120

        # Test thin_metadata_size with different block and pool sizes
        result_diff_units = dmpd.thin_metadata_size(block_size='128k', pool_size='1g', max_thins=5)
        assert result_diff_units.succeeded
        assert '576 sectors' in result_diff_units.stdout.lower()

        # Test thin_metadata_size with larger pool configuration
        result_large = dmpd.thin_metadata_size(block_size='64k', pool_size='10g', max_thins=100)
        assert result_large.succeeded
        assert '11216 sectors' in result_large.stdout.lower()

        # Test thin_metadata_size with sector-based sizes
        # 64k = 128 sectors, 100MB = ~204800 sectors
        result_sectors = dmpd.thin_metadata_size(
            block_size='128',  # sectors
            pool_size='204800',  # sectors
            max_thins=1,
        )
        assert result_sectors.succeeded
        assert '120 sectors' in result_sectors.stdout.lower()
