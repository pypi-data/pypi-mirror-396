"""Tests for lvconvert operations to create thin pools.

This module contains pytest tests for converting logical volumes to thin pools
with various parameters and configurations.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

from sts import lvm


@pytest.mark.parametrize('loop_devices', [{'count': 4, 'size_mb': 128}], indirect=True)
class TestLvconvertThinpool:
    """Test cases for lvconvert to thin pool operations."""

    def test_convert_to_thinpool(self, setup_loopdev_vg: str) -> None:
        """Test converting regular LV to thin pool."""
        vg_name = setup_loopdev_vg

        pool = lvm.LogicalVolume(name='pool', vg=vg_name)

        try:
            # Create regular LV first
            assert pool.create(extents='20')

            # Convert to thin pool
            assert pool.convert_to_thinpool()

            # Verify it's a thin pool
            assert pool.report
            assert pool.report.lv_attr
            assert pool.report.lv_attr.startswith('twi-a-tz')

        finally:
            # Cleanup LVs before VG cleanup
            pool.remove()

    def test_convert_inactive_to_thinpool(self, setup_loopdev_vg: str) -> None:
        """Test converting inactive LV to thin pool."""
        vg_name = setup_loopdev_vg

        pool = lvm.LogicalVolume(name='pool', vg=vg_name)

        try:
            # Create inactive LV
            assert pool.create('-an', extents='20', zero='n')

            # Convert to thin pool
            assert pool.convert_to_thinpool()

            # Verify it's an inactive thin pool with passdown discards
            assert pool.report
            assert pool.report.lv_attr
            assert pool.report.lv_attr.startswith('twi---tz')
            assert pool.report.discards == 'passdown'

        finally:
            # Cleanup LVs before VG cleanup
            pool.remove()

    def test_convert_with_parameters(self, setup_loopdev_vg: str) -> None:
        """Test converting to thin pool with specific parameters."""
        vg_name = setup_loopdev_vg

        pool = lvm.LogicalVolume(name='pool', vg=vg_name)

        try:
            # Create regular LV first
            assert pool.create(extents='20')

            # Convert with specific parameters
            assert pool.convert_to_thinpool(
                chunksize='256k', zero='y', discards='nopassdown', poolmetadatasize='4M', readahead='16'
            )

            # Verify parameters
            assert pool.report
            assert pool.report.chunk_size == '256.00k'
            assert pool.report.discards == 'nopassdown'
            assert pool.report.lv_metadata_size == '4.00m'
            assert pool.report.lv_size == '80.00m'

        finally:
            # Cleanup LVs before VG cleanup
            pool.remove()

    def test_convert_with_separate_metadata(self, setup_loopdev_vg: str) -> None:
        """Test converting with separate metadata LV."""
        vg_name = setup_loopdev_vg

        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        metadata = lvm.LogicalVolume(name='metadata', vg=vg_name)

        try:
            # Create data and metadata LVs
            assert pool.create(extents='20')
            assert metadata.create(extents='10')

            # Convert with separate metadata
            assert metadata.name
            assert pool.convert_to_thinpool(poolmetadata=metadata.name)

            # Verify sizes
            assert pool.report
            assert pool.report.lv_size == '80.00m'
            assert pool.report.lv_metadata_size == '40.00m'

        finally:
            # Cleanup LVs before VG cleanup
            # Note: pool conversion may consume metadata LV, so only remove what exists
            pool.remove()
            metadata.remove()
