"""Test Stratis upgrade scenarios."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from sts.stratis.filesystem import StratisFilesystem
from sts.stratis.pool import StratisPool
from sts.utils.cmdline import run
from sts.utils.files import Directory, mount, umount

if TYPE_CHECKING:
    from sts.blockdevice import BlockDevice


class TestStratisUpgrade:
    """Test class for Stratis upgrade scenarios."""

    disk: BlockDevice
    pool: StratisPool
    fs: StratisFilesystem
    pool_name: str = 'sts-stratis-test-pool'
    fs_name: str = 'sts-stratis-test-fs'
    mount_point: str = '/mnt/stratis'
    flag: Path = Path(f'{mount_point}/stratis_test_file')
    mnt_dir: Directory | None = None
    stratis_path: str = f'/dev/stratis/{pool_name}/{fs_name}'

    def basic_pool_create(self) -> None:
        """Create basic Stratis pool and filesystem (default scenario)."""
        logging.info(f'Creating Stratis pool {self.pool_name} on device {self.disk.path}')

        # Create pool and filesystem
        self.pool.blockdevs = [str(self.disk.path)]
        assert self.pool.create(), f'Failed to create pool {self.pool_name}'
        assert self.fs.create(), f'Failed to create filesystem {self.fs_name}'

        self.write_flag()

    def pool_with_cache_create(self) -> None:
        """Create Stratis pool with cache configuration (future scenario)."""
        # This is a placeholder for future cache scenarios
        logging.info(f'Creating Stratis pool {self.pool_name} with cache on device {self.disk.path}')
        # Implementation would go here for cache-enabled pools
        self.basic_pool_create()  # Fallback to basic for now

    def pool_binding_create(self) -> None:
        """Create Stratis pool with binding configuration (future scenario)."""
        # This is a placeholder for future binding scenarios
        logging.info(f'Creating Stratis pool {self.pool_name} with binding on device {self.disk.path}')
        # Implementation would go here for pool binding
        self.basic_pool_create()  # Fallback to basic for now

    def remove_stratis_pool(self) -> None:
        """Remove Stratis filesystem and pool, cleanup resources."""
        logging.info(f'Removing Stratis filesystem {self.fs_name} and pool {self.pool_name}')

        # Unmount if still mounted
        umount(mountpoint=self.mount_point)

        # Remove filesystem and pool
        assert self.fs.destroy(), f'Failed to destroy filesystem {self.fs_name}'
        assert self.pool.destroy(), f'Failed to destroy pool {self.pool_name}'

        # Cleanup mount directory
        if self.mnt_dir and self.mnt_dir.exists:
            self.mnt_dir.remove_dir()

    def write_flag(self) -> None:
        """Write test flag file to Stratis filesystem."""

        if self.mnt_dir is None:
            self.mnt_dir = Directory(Path(self.mount_point), create=True)
        assert self.mnt_dir.exists, f'Failed to create mount point directory {self.mount_point}'

        assert mount(device=self.stratis_path, mountpoint=self.mount_point), f'Failed to mount {self.stratis_path}'

        # Create a file in the mount point
        self.flag.write_text('STRATIS_FLAG')
        logging.info(f'Created flag file: {self.flag}')
        assert umount(mountpoint=self.mount_point), f'Failed to unmount {self.mount_point}'

    def read_flag(self) -> None:
        """Read and verify test flag file from Stratis filesystem."""

        assert mount(device=self.stratis_path, mountpoint=self.mount_point), f'Failed to mount {self.stratis_path}'
        assert self.flag.exists()
        text = self.flag.read_text()
        assert text == 'STRATIS_FLAG'
        logging.info(f'Flag file verified: {text}')
        assert umount(mountpoint=self.mount_point), f'Failed to unmount {self.mount_point}'

    @pytest.mark.usefixtures('_install_stratis', 'prepare_1minutetip_disk')
    def test_stratis_upgrade(self, prepare_1minutetip_disk: list[BlockDevice]) -> None:
        """
        Test Stratis upgrade scenarios.

        This test supports different Stratis creation scenarios:
        - Basic pool and filesystem creation
        - Pool with cache configuration (future)
        - Pool binding scenarios (future)
        """
        self.disk = prepare_1minutetip_disk[0]
        phase = os.getenv('IN_PLACE_UPGRADE', None)
        if phase is None:
            pytest.skip('IN_PLACE_UPGRADE is not set')

        # Allow environment variable overrides for pool and filesystem names
        self.pool_name = os.getenv('STRATIS_POOL_NAME', self.pool_name)
        self.fs_name = os.getenv('STRATIS_FS_NAME', self.fs_name)
        self.stratis_path = f'/dev/stratis/{self.pool_name}/{self.fs_name}'

        logging.info(f'Stratis upgrade phase: {phase}')

        # Initialize Stratis objects
        self.pool = StratisPool()
        self.pool.name = self.pool_name

        self.fs = StratisFilesystem()
        self.fs.name = self.fs_name
        self.fs.pool_name = self.pool_name

        if phase == 'old':
            # Creation phase - can be extended to test different scenarios
            scenario = os.getenv('STRATIS_SCENARIO', 'basic_pool_create')

            if scenario == 'basic_pool_create':
                self.basic_pool_create()
            elif scenario == 'pool_with_cache_create':
                self.pool_with_cache_create()
            elif scenario == 'pool_binding_create':
                self.pool_binding_create()
            else:
                pytest.skip(f'Unknown Stratis scenario: {scenario}')

        elif phase == 'new':
            # Verification and cleanup phase
            logging.info(run('lsblk').stdout)
            self.read_flag()
            self.remove_stratis_pool()
