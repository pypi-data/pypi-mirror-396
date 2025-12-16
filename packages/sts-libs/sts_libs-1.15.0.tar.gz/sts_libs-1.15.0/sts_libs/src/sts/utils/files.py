# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""File operations module.

This module provides functionality for file system operations:
- Directory validation
- File counting
- Path operations
- Mount management
- Filesystem operations
"""

from __future__ import annotations

import logging
import os
import re
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from shutil import rmtree
from typing import TYPE_CHECKING

from sts import get_sts_host
from sts.utils.cmdline import run
from sts.utils.errors import STSError

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator

    from testinfra.host import Host


host: Host = get_sts_host()


class DirectoryError(STSError):
    """Base class for directory-related errors."""


class DirNotFoundError(DirectoryError):
    """Directory does not exist."""


class DirTypeError(DirectoryError):
    """Path exists but is not a directory."""


class DirAccessError(DirectoryError):
    """Directory cannot be accessed."""


@dataclass
class Directory:
    """Directory representation.

    Provides functionality for directory operations including:
    - Existence checking
    - File counting
    - Path resolution

    Args:
        path: Directory path (optional, defaults to current directory)
        create: Create directory if it doesn't exist (optional)
        mode: Directory creation mode (optional)

    Example:
        ```python
        dir = Directory()  # Uses current directory
        dir = Directory('/tmp/test')  # Uses specific path
        dir = Directory('/tmp/test', create=True)  # Creates if needed
        ```
    """

    # Required parameters
    path: Path = field(default_factory=Path.cwd)

    # Optional parameters
    create: bool = False
    mode: int = 0o755

    def __post_init__(self) -> None:
        """Initialize directory.

        Creates directory if needed.
        """
        # Create directory if needed
        if self.create and not self.exists:
            try:
                self.path.mkdir(mode=self.mode, parents=True, exist_ok=True)
            except OSError:
                logging.exception('Failed to create directory')

    @property
    def exists(self) -> bool:
        """Check if directory exists and is a directory."""
        return self.path.is_dir()

    def validate(self) -> None:
        """Validate directory exists and is accessible.

        Raises:
            DirNotFoundError: If directory does not exist
            DirTypeError: If path exists but is not a directory
        """
        if not self.path.exists():
            raise DirNotFoundError(f'Directory not found: {self.path}')
        if not self.exists:
            raise DirTypeError(f'Not a directory: {self.path}')

    def iter_files(self, *, recursive: bool = False) -> Iterator[Path]:
        """Iterate over files in directory.

        Args:
            recursive: If True, recursively iterate through subdirectories

        Yields:
            Path objects for each file

        Raises:
            DirAccessError: If directory cannot be accessed
        """
        try:
            if recursive:
                for item in self.path.rglob('*'):
                    if item.is_file():
                        yield item
            else:
                for item in self.path.iterdir():
                    if item.is_file():
                        yield item
        except PermissionError as e:
            logging.exception(f'Permission denied accessing {self.path}')
            raise DirAccessError(f'Permission denied: {self.path}') from e
        except OSError as e:
            logging.exception(f'Error accessing {self.path}')
            raise DirAccessError(f'Error accessing directory: {e}') from e

    @staticmethod
    def should_remove_file_with_pattern(file: Path, pattern: str) -> bool:
        """Check if file should be removed because it contains pattern.

        Args:
            file: File to check
            pattern: Pattern to match in file contents

        Returns:
            True if file contains pattern and should be removed
        """
        try:
            content = file.read_text()
        except (OSError, UnicodeDecodeError):
            logging.exception(f'Error reading {file}')
            return False
        return pattern in content

    @staticmethod
    def should_remove_file_without_pattern(file: Path, pattern: str) -> bool:
        """Check if file should be removed because it does not contain pattern.

        Args:
            file: File to check
            pattern: Pattern to match in file contents

        Returns:
            True if file does not contain pattern and should be removed
        """
        try:
            content = file.read_text()
        except (OSError, UnicodeDecodeError):
            logging.exception(f'Error reading {file}')
            return False
        return pattern not in content

    @staticmethod
    def remove_file(file: Path) -> None:
        """Remove file safely.

        Args:
            file: File to remove
        """
        try:
            file.unlink()
        except OSError:
            logging.exception(f'Error removing {file}')

    def count_files(self) -> int:
        """Count number of files in directory.

        Returns:
            Number of files in directory (excluding directories)

        Raises:
            DirNotFoundError: If directory does not exist
            DirTypeError: If path exists but is not a directory
            DirAccessError: If directory cannot be accessed

        Example:
            ```python
            Directory('/etc').count_files()
            42
            ```
        """
        self.validate()
        return sum(1 for _ in self.iter_files())

    def rm_files_containing(self, pattern: str, *, invert: bool = False) -> None:
        """Delete files containing (or not containing) specific pattern.

        Args:
            pattern: Pattern to match in file contents
            invert: Delete files NOT containing pattern

        Raises:
            DirNotFoundError: If directory does not exist
            DirTypeError: If path exists but is not a directory
            DirAccessError: If directory cannot be accessed

        Example:
            ```python
            Directory('/tmp').rm_files_containing('error')  # Remove files containing 'error'
            Directory('/tmp').rm_files_containing('error', invert=True)  # Remove files NOT containing 'error'
            ```
        """
        self.validate()
        check_func = self.should_remove_file_without_pattern if invert else self.should_remove_file_with_pattern
        for file in self.iter_files():
            if check_func(file, pattern):
                self.remove_file(file)

    def remove_dir(self) -> None:
        """Remove directory and all its contents using shutil.rmtree.

        Raises:
            DirNotFoundError: If directory does not exist
            DirTypeError: If path exists but is not a directory
            DirAccessError: If directory cannot be accessed

        Example:
            ```python
            Directory(Path('/tmp/test')).remove_dir()
            ```
        """
        self.validate()
        try:
            rmtree(self.path)
        except (OSError, PermissionError):
            logging.exception(f'Error removing {self.path}')


@contextmanager
def change_directory(path: Path) -> Generator[None, None, None]:
    """Context manager to temporarily change working directory.

    Changes to the specified directory and automatically restores
    the original working directory when exiting the context, even
    if an exception occurs.

    Args:
        path: Directory to change to

    Yields:
        None

    Example:
        ```python
        with change_directory(Path('/tmp')):
            # Working directory is now /tmp
            result = run('pwd')  # Shows /tmp
        # Working directory is restored to original
        ```
    """
    original_cwd = Path.cwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_cwd)


def count_files(directory: str | Path | None = None) -> int:
    """Count number of files in directory.

    Args:
        directory: Path to directory to count files in (optional)

    Returns:
        Number of files in directory (excluding directories)

    Raises:
        DirNotFoundError: If directory does not exist
        DirTypeError: If path exists but is not a directory
        DirAccessError: If directory cannot be accessed

    Example:
        ```python
        count_files()  # Count files in current directory
        count_files('/etc')  # Count files in specific directory
        ```
    """
    path = Path(directory) if directory else Path.cwd()
    return Directory(path).count_files()


def rm_files_containing(directory: str | Path | None = None, pattern: str = '', *, invert: bool = False) -> None:
    """Delete files containing (or not containing) specific pattern.

    Args:
        directory: Directory to search in (optional)
        pattern: Pattern to match in file contents (optional)
        invert: Delete files NOT containing pattern (optional)

    Raises:
        DirNotFoundError: If directory does not exist
        DirTypeError: If path exists but is not a directory
        DirAccessError: If directory cannot be accessed

    Example:
        ```python
        rm_files_containing()  # Remove all files in current directory
        rm_files_containing('/tmp', 'error')  # Remove files containing 'error'
        rm_files_containing('/tmp', 'error', invert=True)  # Remove files NOT containing 'error'
        ```
    """
    path = Path(directory) if directory else Path.cwd()
    Directory(path).rm_files_containing(pattern, invert=invert)


def is_mounted(device: str | Path | None = None, mountpoint: str | Path | None = None) -> bool:
    """Check if device or mountpoint is mounted.

    Args:
        device: Device to check (optional) - accepts str or Path
        mountpoint: Mountpoint to check (optional) - accepts str or Path

    Returns:
        True if mounted, False otherwise

    Example:
        ```python
        is_mounted(device='/dev/sda1')  # Check device with string
        is_mounted(device=Path('/dev/sda1'))  # Check device with Path
        is_mounted(mountpoint='/mnt')  # Check mountpoint with string
        is_mounted(mountpoint=Path('/mnt'))  # Check mountpoint with Path
        ```
    """
    if device:
        return run(f'mount | grep {device!s}').succeeded
    if mountpoint:
        return run(f'mount | grep {mountpoint!s}').succeeded
    return False


def mount(
    device: str | Path | None = None,
    mountpoint: str | Path | None = None,
    fs_type: str | None = None,
    options: str | None = None,
) -> bool:
    """Mount device at mountpoint.

    Args:
        device: Device to mount (optional) - accepts str or Path
        mountpoint: Mountpoint to mount at (optional) - accepts str or Path
        fs_type: Filesystem type (optional)
        options: Mount options (optional)

    Returns:
        True if successful, False otherwise

    Example:
        ```python
        mount('/dev/sda1', '/mnt')  # Basic mount with strings
        mount(Path('/dev/sda1'), Path('/mnt'))  # Mount with Path objects
        mount('/dev/sda1', '/mnt', 'ext4', 'ro')  # Mount with options
        ```
    """
    cmd = ['mount']
    if fs_type:
        cmd.extend(['-t', fs_type])
    if options:
        cmd.extend(['-o', options])
    if device:
        cmd.append(str(device))
    if mountpoint:
        mountpoint_path = Path(mountpoint)
        Directory(mountpoint_path, create=True)
        cmd.append(str(mountpoint_path))

    result = run(' '.join(cmd))
    if result.failed:
        logging.error(f'Failed to mount device: {result.stderr}')
        return False
    return True


def umount(device: str | Path | None = None, mountpoint: str | Path | None = None) -> bool:
    """Unmount device or mountpoint.

    Args:
        device: Device to unmount (optional) - accepts str or Path
        mountpoint: Mountpoint to unmount (optional) - accepts str or Path

    Returns:
        True if successful, False otherwise

    Example:
        ```python
        umount('/dev/sda1')  # Unmount device with string
        umount(device=Path('/dev/sda1'))  # Unmount device with Path
        umount(mountpoint='/mnt')  # Unmount mountpoint with string
        umount(mountpoint=Path('/mnt'))  # Unmount mountpoint with Path
        ```
    """
    if device and not is_mounted(device=str(device)):
        return True
    if mountpoint and not is_mounted(mountpoint=str(mountpoint)):
        return True

    cmd = ['umount']
    if device:
        cmd.append(str(device))
    if mountpoint:
        cmd.append(str(mountpoint))

    result = run(' '.join(cmd))
    if result.failed:
        logging.error(f'Failed to unmount device: {result.stderr}')
        return False
    return True


def mkfs(device: str | Path | None = None, fs_type: str | None = None, *args: str, **kwargs: str) -> bool:
    """Create filesystem on device.

    Args:
        device: Device to create filesystem on (optional) - accepts str or Path
        fs_type: Filesystem type (optional)
        force: Force creation even if filesystem exists (optional)

    Returns:
        True if successful, False otherwise

    Example:
        ```python
        mkfs('/dev/sda1', 'ext4')  # Create ext4 filesystem with string
        mkfs(Path('/dev/sda1'), 'ext4')  # Create ext4 filesystem with Path
        mkfs('/dev/sda1', 'ext4', force=True)  # Force creation
        ```
    """
    if not device or not fs_type:
        logging.error('Device and filesystem type required')
        return False

    device_str = str(device)
    cmd = [f'mkfs.{fs_type}']

    if kwargs.pop('force', False):
        force_option = '-F' if fs_type != 'xfs' else '-f'
        cmd.append(force_option)

    if args:
        cmd.extend(str(arg) for arg in args if arg)
    if kwargs:
        cmd.extend(f'-{k.replace("_", "-")}={v}' for k, v in kwargs.items() if v)
    cmd.append(device_str)

    result = run(' '.join(cmd))
    if result.failed:
        logging.error(f'Failed to create {fs_type} filesystem on {device_str}: {result.stderr}')
        return False
    return True


def get_free_space(path: str | Path | None = None) -> int | None:
    """Get free space in bytes.

    Args:
        path: Path to check free space for (optional)

    Returns:
        Free space in bytes or None if error

    Example:
        ```python
        get_free_space()  # Check current directory
        get_free_space('/mnt')  # Check specific path
        ```
    """
    path_str = str(path) if path else '.'
    result = run(f'df -B 1 {path_str}')
    if result.failed:
        logging.error('Failed to get free space')
        return None

    # Parse output like:
    # Filesystem     1B-blocks       Used   Available Use% Mounted on
    # /dev/sda1    1073741824   10485760  1063256064   1% /mnt
    if match := re.search(r'\S+\s+\d+\s+\d+\s+(\d+)', result.stdout):
        return int(match.group(1))

    return None


def fallocate(path: str | Path, *args: str, **kwargs: str) -> bool:
    """Preallocate space to, or deallocate space from a file.

    Args:
        path: Path to create sparse file
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        True if successful, False otherwise

    Example:
        ```python
        fallocate('/tmp/test', '-l 10M')  # Create 10MB sparse file
        fallocate('/tmp/test', length='10M')  # Create 10MB sparse file
        ```
    """
    cmd = ['fallocate']
    if args:
        cmd.extend(str(arg) for arg in args if arg)
    if kwargs:
        cmd.extend(f'--{k.replace("_", "-")}={v}' for k, v in kwargs.items() if v)
    cmd.append(str(path))
    result = run(' '.join(cmd))
    return result.succeeded


def write_data(
    target: str | Path,
    source: str | Path,
    *,
    sync: bool = True,
    **kwargs: str | int,
) -> bool:
    """Write data to a file using dd command with flexible options.

    Args:
        target: Target file path - accepts str or Path
        source: Source to read data from (optional, default: '/dev/urandom')
        size_mb: Size in megabytes to write (optional, default: 1)
        block_size: Block size for dd operation (optional, default: '1M')
        sync: Whether to sync after writing (default: True)
        **kwargs: Additional dd options (e.g., conv='notrunc', seek=10, skip=5)

    Returns:
        True if successful, False otherwise

    Example:
        ```python
        write_data('/tmp/testfile', size_mb=5)  # Write 5MB of random data
        write_data(Path('/tmp/testfile'), source='/dev/zero', size_mb=10)  # Write 10MB of zeros
        write_data('/tmp/testfile', size_mb=100, block_size='4K')  # Write with 4K blocks
        write_data('/tmp/testfile', count=50, bs='1M', conv='notrunc')  # Custom dd options
        write_data('/tmp/testfile', source='/dev/zero', conv='fdatasync')  # Source and kwargs
        ```
    """
    # Build dd command with defaults and kwargs
    cmd_parts = ['dd']

    cmd_parts.append(f'if={source!s}')

    # Handle output file (target)
    cmd_parts.append(f'of={target!s}')

    # Add any remaining kwargs as dd options
    for key, value in kwargs.items():
        # Handle special cases where key might be a Python keyword
        dd_key = key.rstrip('_')  # Remove trailing underscore if present
        cmd_parts.append(f'{dd_key}={value}')

    cmd = ' '.join(cmd_parts)
    result = run(cmd)

    if result.failed:
        logging.error(f'dd command failed: {result.stderr}')
        logging.error(f'Command: {cmd}')
        return False

    if sync:
        sync_result = run('sync')
        if sync_result.failed:
            logging.warning('Sync operation failed but file write succeeded')

    return True
