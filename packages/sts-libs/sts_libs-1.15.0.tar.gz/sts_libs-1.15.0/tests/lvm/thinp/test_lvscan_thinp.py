"""Tests for lvscan command with thin provisioning.

This module contains pytest tests for the lvscan command showing information
about thin pools, thin volumes, and snapshots.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

import pytest

from sts import lvm


@pytest.mark.parametrize('loop_devices', [{'count': 4, 'size_mb': 128}], indirect=True)
class TestLvscanThinp:
    """Test cases for lvscan command with thin provisioning."""

    def _parse_lvscan_json(self, json_output: str, target_vg: str) -> dict[str, dict]:
        """Parse lvscan JSON output and extract LV information for the target VG.

        Args:
            json_output: JSON output from lvscan --reportformat json
            target_vg: Volume group name to filter by

        Returns:
            Dictionary mapping LV names to their information (status, message, device_path)
        """
        scan_data = json.loads(json_output)
        log_entries = scan_data.get('log', [])

        lv_info = {}
        for entry in log_entries:
            if entry.get('log_object_type') == 'lv':
                lv_name = entry.get('log_object_name')
                vg_name_from_log = entry.get('log_object_group')
                message = entry.get('log_message', '')

                if vg_name_from_log == target_vg:
                    # Extract status from message (ACTIVE or inactive)
                    status = 'ACTIVE' if 'ACTIVE' in message else 'inactive'
                    lv_info[lv_name] = {
                        'status': status,
                        'message': message,
                        'device_path': f'/dev/{target_vg}/{lv_name}',
                    }

        return lv_info

    def test_lvscan_thin_volumes(self, setup_loopdev_vg: str) -> None:
        """Test lvscan command with thin pools, volumes, and snapshots."""
        vg_name = setup_loopdev_vg

        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        lv1 = lvm.LogicalVolume(name='lv1', vg=vg_name)

        try:
            # Create thin pool with volume and snapshots
            assert pool.create(size='40M', type='thin-pool')
            assert lv1.create(virtualsize='100M', type='thin', thinpool='pool')
            snap1 = lv1.create_snapshot('snap1')
            assert snap1 is not None
            snap2 = snap1.create_snapshot('snap2')
            assert snap2 is not None

            # Run lvscan with JSON format
            result = pool.scan('--reportformat', 'json')
            assert result.succeeded

            # Parse JSON output to extract LV information
            lv_info = self._parse_lvscan_json(result.stdout, vg_name)

            # Verify expected volumes and their states
            assert 'pool' in lv_info, 'Pool should appear in lvscan'
            assert lv_info['pool']['status'] == 'ACTIVE', 'Pool should be ACTIVE'

            assert 'lv1' in lv_info, 'Thin volume should appear in lvscan'
            assert lv_info['lv1']['status'] == 'ACTIVE', 'Thin volume should be ACTIVE'

            assert 'snap1' in lv_info, 'First snapshot should appear in lvscan'
            assert lv_info['snap1']['status'] == 'inactive', 'First snapshot should be inactive'

            assert 'snap2' in lv_info, 'Second snapshot should appear in lvscan'
            assert lv_info['snap2']['status'] == 'inactive', 'Second snapshot should be inactive'

            # Hidden tdata and tmeta volumes should NOT appear in regular lvscan
            assert 'pool_tdata' not in lv_info, 'pool_tdata should not appear in regular lvscan'
            assert 'pool_tmeta' not in lv_info, 'pool_tmeta should not appear in regular lvscan'

        finally:
            # Cleanup LVs before VG cleanup
            lv1.remove('-f')
            pool.remove('-f')

    def test_lvscan_all_volumes(self, setup_loopdev_vg: str) -> None:
        """Test lvscan -a command showing all volumes including hidden ones."""
        vg_name = setup_loopdev_vg

        pool = lvm.LogicalVolume(name='pool', vg=vg_name)
        lv1 = lvm.LogicalVolume(name='lv1', vg=vg_name)

        try:
            # Create thin pool and volume
            assert pool.create(size='40M', type='thin-pool')
            assert lv1.create(virtualsize='100M', type='thin', thinpool='pool')

            # Run lvscan -a with JSON format to show hidden volumes
            result = pool.scan('-a', '--reportformat', 'json')
            assert result.succeeded

            # Parse JSON output to extract LV information
            lv_info = self._parse_lvscan_json(result.stdout, vg_name)

            # With -a flag, hidden volumes should appear
            assert 'pool_tdata' in lv_info, 'pool_tdata should appear in lvscan -a'
            assert lv_info['pool_tdata']['status'] == 'ACTIVE', 'pool_tdata should be ACTIVE'

            assert 'pool_tmeta' in lv_info, 'pool_tmeta should appear in lvscan -a'
            assert lv_info['pool_tmeta']['status'] == 'ACTIVE', 'pool_tmeta should be ACTIVE'

            assert 'pool' in lv_info, 'pool should appear in lvscan -a'
            assert lv_info['pool']['status'] == 'ACTIVE', 'pool should be ACTIVE'

            assert 'lv1' in lv_info, 'lv1 should appear in lvscan -a'
            assert lv_info['lv1']['status'] == 'ACTIVE', 'lv1 should be ACTIVE'

        finally:
            # Cleanup LVs before VG cleanup
            # Remove thin volume first, then pool
            lv1.remove()
            pool.remove()
