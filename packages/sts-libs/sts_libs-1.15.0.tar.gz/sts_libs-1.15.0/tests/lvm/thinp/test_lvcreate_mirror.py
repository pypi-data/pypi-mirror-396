"""Tests for creating mirrored thin pools.

This module contains pytest tests for creating thin pools with RAID1 (mirroring)
for both data and metadata components.
"""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
import time

import pytest

from sts import lvm
from sts.utils.cmdline import run


@pytest.mark.parametrize('loop_devices', [{'count': 4, 'size_mb': 128}], indirect=True)
class TestLvcreateMirror:
    """Test cases for creating mirrored thin pools."""

    def test_mirror_thin_pool(self, setup_loopdev_vg: str) -> None:
        """Test creating thin pool with RAID1 mirroring."""
        vg_name = setup_loopdev_vg

        pool = lvm.LogicalVolume(name='pool', vg=vg_name)

        try:
            # Create thin pool
            assert pool.create(size='4M', type='thin-pool')

            assert pool.report

            # Verify initial stripe count from pool report
            assert pool.report.data_stripes == '1', 'Pool data component should have 1 stripe initially'

            # Get LVM2 version to handle behavior changes
            lvm2_version = self._get_lvm2_version()

            # Behavior changed in BZ1462712 - LV must be active to run lvconvert
            if lvm2_version >= '2.02.171-6':
                # Deactivate pool and try to convert (should fail)
                assert pool.deactivate()

                # Try to convert inactive pool data component (should fail)
                success = pool.convert_pool_data(type='raid1', mirrors='3')
                assert not success, 'lvconvert should fail on inactive pool'

                # Reactivate pool
                assert pool.activate()
            else:
                # Old behavior - should work without activation
                # Try to convert with insufficient devices (should fail)
                success = pool.convert_pool_data(type='raid1', mirrors='3')
                assert not success, 'lvconvert should fail without enough devices'

                # Deactivate for next step
                assert pool.deactivate()

            # Convert data to RAID1 with 3 mirrors (4 total devices)
            assert pool.convert_pool_data(type='raid1', mirrors='3'), 'Failed to convert tdata to RAID1'

            # Wait for sync
            time.sleep(5)

            # Convert metadata to RAID1 with 1 mirror (2 total devices)
            assert pool.convert_pool_metadata(type='raid1', mirrors='1'), 'Failed to convert tmeta to RAID1'
            # Reactivate pool
            assert pool.activate()

            # Show final state using LogicalVolume scan
            pool.scan()

        finally:
            # Cleanup LVs before VG cleanup
            pool.remove(force='')

    def _get_lvm2_version(self) -> str:
        """Get LVM2 version string."""
        result = run('rpm -q lvm2 --queryformat "%{VERSION}-%{RELEASE}"')
        if result.rc == 0:
            return result.stdout.strip()

        # Fallback to lvm version command
        result = run('lvm version')
        if result.rc == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'LVM version:' in line:
                    return line.split(':')[1].strip()

        return '0.0.0'
