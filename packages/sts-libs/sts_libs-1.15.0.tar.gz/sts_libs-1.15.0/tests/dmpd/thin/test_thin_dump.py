"""Tests for thin_dump DMPD tool.

This module contains pytest tests for the thin_dump command-line tool,
which is used to dump thin metadata to stdout or file.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from sts import dmpd


@pytest.mark.parametrize('loop_devices', [{'count': 1, 'size_mb': 4096}], indirect=True)
class TestThinDump:
    """Test cases for thin_dump command."""

    def test_thin_dump(self, setup_thin_metadata_for_dmpd: dict[str, str], tmp_path: Path) -> None:
        """Test various thin_dump operations that can share the same metadata setup."""
        vol_info = setup_thin_metadata_for_dmpd
        metadata_dev = vol_info['metadata_dev']

        # Test basic thin_dump without any extra parameters
        result_basic = dmpd.thin_dump(metadata_dev)
        assert result_basic.succeeded
        assert '<superblock uuid=' in result_basic.stdout
        assert '<device dev_id=' in result_basic.stdout
        assert 'mapped_blocks=' in result_basic.stdout
        assert 'transaction=' in result_basic.stdout
        assert 'creation_time=' in result_basic.stdout
        assert 'snap_time=' in result_basic.stdout
        assert '</device>' in result_basic.stdout
        assert '</superblock>' in result_basic.stdout
        assert 'range_mapping origin_begin=' in result_basic.stdout
        assert 'data_begin=' in result_basic.stdout
        assert 'length=' in result_basic.stdout
        assert 'time=' in result_basic.stdout
        assert '<single_mapping origin_block=' in result_basic.stdout

        # Test thin_dump without mappings
        result_skip_mappings = dmpd.thin_dump(metadata_dev, skip_mappings=True)
        assert result_skip_mappings.succeeded
        assert '<superblock uuid=' in result_skip_mappings.stdout
        assert '<device dev_id=' in result_skip_mappings.stdout
        assert 'mapped_blocks=' in result_skip_mappings.stdout
        assert '</device>' in result_skip_mappings.stdout
        assert '</superblock>' in result_skip_mappings.stdout
        # Should not contain mapping information when skip_mappings is True
        assert 'range_mapping origin_begin=' not in result_skip_mappings.stdout
        assert '<single_mapping origin_block=' not in result_skip_mappings.stdout

        # Test thin_dump in XML format
        result_xml = dmpd.thin_dump(metadata_dev, format='xml')
        assert result_xml.succeeded
        assert '<superblock uuid=' in result_xml.stdout
        assert '<device dev_id=' in result_xml.stdout
        assert '</device>' in result_xml.stdout
        assert '</superblock>' in result_xml.stdout
        assert 'range_mapping origin_begin=' in result_xml.stdout
        assert '<single_mapping origin_block=' in result_xml.stdout
        # Parse the XML output
        root = ET.fromstring(result_xml.stdout.strip())
        assert root.tag == 'superblock'
        assert root.find('device') is not None

        # Test thin_dump in human readable format
        result_human = dmpd.thin_dump(metadata_dev, format='human_readable')
        assert result_human.succeeded
        assert 'begin superblock:' in result_human.stdout
        assert 'device:' in result_human.stdout
        assert 'mapped_blocks:' in result_human.stdout
        assert 'transaction:' in result_human.stdout
        assert 'creation time:' in result_human.stdout
        assert 'snap time:' in result_human.stdout
        assert 'end superblock' in result_human.stdout

        # Test thin_dump from metadata snapshot
        result_snap = dmpd.thin_dump(metadata_dev, metadata_snap=True)
        assert result_snap.succeeded
        assert '<superblock uuid=' in result_snap.stdout
        assert '<device dev_id=' in result_snap.stdout
        assert '</device>' in result_snap.stdout
        assert '</superblock>' in result_snap.stdout
        assert 'range_mapping origin_begin=' in result_snap.stdout
        assert '<single_mapping origin_block=' in result_snap.stdout

        # Test thin_dump from specific device ID
        result_dev_id = dmpd.thin_dump(metadata_dev, dev_id=2)
        assert result_dev_id.succeeded
        assert '<superblock uuid=' in result_dev_id.stdout
        assert '<device dev_id=' in result_dev_id.stdout
        assert '</device>' in result_dev_id.stdout
        assert '</superblock>' in result_dev_id.stdout
        assert 'range_mapping origin_begin=' in result_dev_id.stdout
        assert '<single_mapping origin_block=' in result_dev_id.stdout

        # Test thin_dump with output to file
        output_file = tmp_path / 'thin_dump_output.xml'
        result_file = dmpd.thin_dump(metadata_dev, output=str(output_file))
        assert result_file.succeeded
        assert output_file.exists()
        # Check file contents
        output_content = output_file.read_text()
        assert '<superblock uuid=' in output_content
        assert '<device dev_id=' in output_content
        assert '</device>' in output_content
        assert '</superblock>' in output_content

        # Test thin_dump with repair flag
        result_repair = dmpd.thin_dump(metadata_dev, repair=True)
        assert result_repair.succeeded
        assert '<superblock uuid=' in result_repair.stdout
        assert '<device dev_id=' in result_repair.stdout
        assert '</device>' in result_repair.stdout
        assert '</superblock>' in result_repair.stdout
