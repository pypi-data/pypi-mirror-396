"""Tests for thin pool capacity management.

This module contains pytest tests for thin pool capacity management,
focusing on behavior when pool capacity is exceeded with different filesystems.
"""
#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
from pathlib import Path

import pytest

from sts import lvm
from sts.utils.cmdline import run
from sts.utils.files import Directory, mkfs, mount, umount


@pytest.mark.parametrize('loop_devices', [{'count': 1, 'size_mb': 1024}], indirect=True)
class TestPoolCapacity:
    """Test cases for thin pool capacity management."""

    @pytest.mark.parametrize('filesystem', ['ext4', 'xfs'])
    def test_exceed_pool_capacity(self, setup_loopdev_vg: str, filesystem: str) -> None:
        """Test exceeding thin pool capacity with different filesystems.

        Args:
            setup_loopdev_vg: Volume group setup fixture
            filesystem: Filesystem type to test (ext4, xfs)
        """
        vg_name = setup_loopdev_vg
        pool_name = 'test_pool'
        thin1_name = 'thin1'
        thin2_name = 'thin2'
        mnt_point_thin1 = '/mnt/thin1'
        mnt_point_thin2 = '/mnt/thin2'

        logging.info(f'Testing filesystem={filesystem}')

        # Create LogicalVolume objects outside try block for cleanup access
        pool = lvm.LogicalVolume(name=pool_name, vg=vg_name)
        thin1 = lvm.LogicalVolume(name=thin1_name, vg=vg_name)
        thin2 = lvm.LogicalVolume(name=thin2_name, vg=vg_name)

        try:
            # Create thin pool with 800M size (from 1G VG)
            # Note: errorwhenfull is not a valid option for thin pool creation
            assert pool.create(size='800M', type='thin-pool')

            # Create two 1G thin volumes (overprovisioned)
            assert thin1.create(virtualsize='1G', type='thin', thinpool=pool_name)
            assert thin2.create(virtualsize='1G', type='thin', thinpool=pool_name)

            # Display LVs for debugging
            assert run('lvs -a -o +devices').succeeded

            # Check device mapper table
            assert run('dmsetup table').succeeded

            # Create filesystem on first thin volume
            thin1_device = f'/dev/mapper/{vg_name}-{thin1_name}'
            logging.info(f'Creating {filesystem} filesystem on {thin1_device}')
            assert mkfs(thin1_device, filesystem)

            # Mount first thin volume
            mnt_dir1 = Directory(Path(mnt_point_thin1), create=True)
            if not mnt_dir1.exists:
                logging.error(f'Failed to create mount directory: {mnt_point_thin1}')
                pytest.skip(f'Cannot create mount directory: {mnt_point_thin1}')
            assert mount(thin1_device, mnt_point_thin1)

            # Create filesystem on second thin volume
            thin2_device = f'/dev/mapper/{vg_name}-{thin2_name}'
            logging.info(f'Creating {filesystem} filesystem on {thin2_device}')
            assert mkfs(thin2_device, filesystem)

            # Mount second thin volume
            mnt_dir2 = Directory(Path(mnt_point_thin2), create=True)
            if not mnt_dir2.exists:
                logging.error(f'Failed to create mount directory: {mnt_point_thin2}')
                pytest.skip(f'Cannot create mount directory: {mnt_point_thin2}')
            assert mount(thin2_device, mnt_point_thin2)

            # Fill up the thin volumes to exceed pool capacity
            logging.info('Starting to fill thin volumes to exceed pool capacity...')

            # Write data to both thin volumes simultaneously
            # Use dd to write in parallel to trigger pool full condition

            # Start writing to first volume (400M should be safe)
            dd_cmd1 = f'dd if=/dev/zero of={mnt_point_thin1}/testfile bs=1M count=400 oflag=sync'
            result1 = run(dd_cmd1)
            logging.info(f'Write to thin1 result: {result1.rc}')

            # Try to write to second volume to exceed pool capacity
            dd_cmd2 = f'dd if=/dev/zero of={mnt_point_thin2}/testfile bs=1M count=400 oflag=sync'
            result2 = run(dd_cmd2)
            logging.info(f'Write to thin2 result: {result2.rc}')

            # Check pool status
            pool_result = run(f'lvs {vg_name}/{pool_name} -o data_percent --noheadings')
            if pool_result.succeeded:
                data_percent = pool_result.stdout.strip()
                logging.info(f'Pool data usage: {data_percent}')

            # Verify filesystem behavior after pool stress
            # Different filesystems may behave differently when underlying storage fails
            df_result1 = run(f'df {mnt_point_thin1}')
            logging.info(f'df result for thin1: {df_result1.rc}')

            df_result2 = run(f'df {mnt_point_thin2}')
            logging.info(f'df result for thin2: {df_result2.rc}')

        finally:
            # Cleanup - ensure unmounting even if test fails
            umount_result1 = umount(mnt_point_thin1)
            umount_result2 = umount(mnt_point_thin2)

            logging.info(f'Unmount results: thin1={umount_result1}, thin2={umount_result2}')

            # Remove mount point directories
            mnt_dir1 = Directory(Path(mnt_point_thin1))
            mnt_dir2 = Directory(Path(mnt_point_thin2))
            if mnt_dir1.exists:
                mnt_dir1.remove_dir()
            if mnt_dir2.exists:
                mnt_dir2.remove_dir()

            # Clean up LVM volumes
            assert thin1.remove(force='', yes='')
            assert thin2.remove(force='', yes='')
            assert pool.remove(force='', yes='')

    def test_pool_data_usage_monitoring(self, setup_loopdev_vg: str) -> None:
        """Test monitoring pool data usage during filling."""
        vg_name = setup_loopdev_vg
        pool_name = 'monitor_pool'
        thin_name = 'monitor_thin'

        # Create LogicalVolume objects outside try block for cleanup access
        pool = lvm.LogicalVolume(name=pool_name, vg=vg_name)
        thin = lvm.LogicalVolume(name=thin_name, vg=vg_name)

        # Create thin pool
        assert pool.create(size='500M', type='thin-pool')

        # Create thin volume
        assert thin.create(virtualsize='1G', type='thin', thinpool=pool_name)

        # Create filesystem
        thin_device = f'/dev/mapper/{vg_name}-{thin_name}'
        assert mkfs(thin_device, 'ext4')

        # Mount and monitor usage
        mnt_point = '/mnt/monitor_test'
        mnt_dir = Directory(Path(mnt_point), create=True)
        if not mnt_dir.exists:
            logging.error(f'Failed to create mount directory: {mnt_point}')
            pytest.skip(f'Cannot create mount directory: {mnt_point}')
        assert mount(thin_device, mnt_point)

        try:
            # Write data in increments and monitor usage
            for i in range(1, 6):  # Write 5 x 100M = 500M total
                write_size = 100
                dd_cmd = f'dd if=/dev/zero of={mnt_point}/testfile{i} bs=1M count={write_size} oflag=sync'
                result = run(dd_cmd)

                # Check pool usage after each write
                pool_result = run(f'lvs {vg_name}/{pool_name} -o data_percent --noheadings')
                if pool_result.succeeded:
                    data_percent = pool_result.stdout.strip()
                    logging.info(f'After writing {i * write_size}M: Pool usage {data_percent}')

                # If pool is getting full, writes may start failing
                if not result.succeeded:
                    logging.info(f'Write {i} failed, pool likely full')
                    break

        finally:
            umount(mnt_point)
            if mnt_dir.exists:
                mnt_dir.remove_dir()
            assert thin.remove(force='', yes='')
            assert pool.remove(force='', yes='')

    def test_metadata_usage_monitoring(self, setup_loopdev_vg: str) -> None:
        """Test monitoring pool metadata usage."""
        vg_name = setup_loopdev_vg
        pool_name = 'meta_pool'

        # Create LogicalVolume object outside try block for cleanup access
        pool = lvm.LogicalVolume(name=pool_name, vg=vg_name)

        # Create thin pool
        assert pool.create(size='800M', type='thin-pool')

        # Create many small thin volumes to consume metadata
        for i in range(20):
            thin_name = f'thin{i}'
            thin = lvm.LogicalVolume(name=thin_name, vg=vg_name)
            assert thin.create(virtualsize='100M', type='thin', thinpool=pool_name)

            # Check metadata usage periodically
            if i % 5 == 0:
                meta_result = run(f'lvs {vg_name}/{pool_name} -o metadata_percent --noheadings')
                if meta_result.succeeded:
                    meta_percent = meta_result.stdout.strip()
                    logging.info(f'After creating {i + 1} thin volumes: Metadata usage {meta_percent}')

        # Clean up - remove all thin volumes created in the loop
        for i in range(20):
            thin_name = f'thin{i}'
            thin = lvm.LogicalVolume(name=thin_name, vg=vg_name)
            thin.remove(force='', yes='')  # Don't assert since some might already be removed

        # Remove the pool (this will be the last thin variable from the loop above)
        assert pool.remove(force='', yes='')

    def test_pool_autoextend_behavior(self, setup_loopdev_vg: str) -> None:
        """Test thin pool autoextend configuration behavior."""
        vg_name = setup_loopdev_vg
        pool_name = 'autoextend_pool'
        thin_name = 'autoextend_thin'

        # Create LogicalVolume objects outside try block for cleanup access
        pool = lvm.LogicalVolume(name=pool_name, vg=vg_name)
        thin = lvm.LogicalVolume(name=thin_name, vg=vg_name)

        # Create thin pool with specific size
        assert pool.create(size='400M', type='thin-pool')

        # Create thin volume
        assert thin.create(virtualsize='1G', type='thin', thinpool=pool_name)

        # Check initial pool size
        size_result = run(f'lvs {vg_name}/{pool_name} -o lv_size --noheadings')
        assert size_result.succeeded
        initial_size = size_result.stdout.strip()
        logging.info(f'Initial pool size: {initial_size}')

        # Create filesystem and write data
        thin_device = f'/dev/mapper/{vg_name}-{thin_name}'
        assert mkfs(thin_device, 'ext4')

        mnt_point = '/mnt/autoextend_test'
        mnt_dir = Directory(Path(mnt_point), create=True)
        if not mnt_dir.exists:
            logging.error(f'Failed to create mount directory: {mnt_point}')
            pytest.skip(f'Cannot create mount directory: {mnt_point}')
        assert mount(thin_device, mnt_point)

        try:
            # Write data that should fit in the pool
            dd_cmd = f'dd if=/dev/zero of={mnt_point}/testfile bs=1M count=200 oflag=sync'
            result = run(dd_cmd)
            assert result.succeeded

            # Check pool size after write (should be same unless autoextend is configured)
            size_result = run(f'lvs {vg_name}/{pool_name} -o lv_size --noheadings')
            assert size_result.succeeded
            final_size = size_result.stdout.strip()
            logging.info(f'Final pool size: {final_size}')

        finally:
            umount(mnt_point)
            if mnt_dir.exists:
                mnt_dir.remove_dir()
            assert thin.remove(force='', yes='')
            assert pool.remove(force='', yes='')
