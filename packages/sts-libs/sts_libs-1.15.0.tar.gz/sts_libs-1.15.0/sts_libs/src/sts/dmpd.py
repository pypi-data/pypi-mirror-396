# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""Device Mapper Persistent Data (DMPD) tools management.

This module provides functionality for managing Device Mapper Persistent Data tools.
Each tool is a separate command-line utility for managing metadata of device-mapper targets:

Cache Tools:
- cache_check: Check cache metadata integrity
- cache_dump: Dump cache metadata to file or stdout
- cache_repair: Repair corrupted cache metadata
- cache_restore: Restore cache metadata from backup
- cache_metadata_size: Calculate cache metadata size requirements

Thin Tools:
- thin_check: Check thin provisioning metadata integrity
- thin_dump: Dump thin metadata to file or stdout
- thin_repair: Repair corrupted thin metadata
- thin_restore: Restore thin metadata from backup
- thin_metadata_size: Calculate thin metadata size requirements
- thin_trim: Trim thin metadata

Era Tools:
- era_check: Check era metadata integrity
- era_dump: Dump era metadata to file or stdout
- era_repair: Repair corrupted era metadata
- era_restore: Restore era metadata from backup

Each tool operates independently and can work with various device sources:
- Block devices (/dev/sdX, /dev/mapper/*, /dev/vg/lv)
- Regular files (metadata dumps)
- Device mapper devices
"""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, ClassVar, Optional, Union

from sts.utils.cmdline import CommandResult, run

if TYPE_CHECKING:
    from pathlib import Path

# Type alias for command options
CommandOption = Optional[Union[bool, str, int, float]]


class DmpdTool(ABC):
    """Base class for DMPD command-line tools.

    Each DMPD tool is a separate command-line utility that can operate on:
    - Block devices (LVM logical volumes, raw devices)
    - Regular files (metadata dump files)
    - Device mapper devices
    """

    # Tool name (must be set by subclasses)
    TOOL_NAME: ClassVar[str]

    @staticmethod
    def _build_command(cmd: str, device_or_file: str | Path | None = None, **options: CommandOption) -> str:
        """Build DMPD command string with options.

        Args:
            cmd: Command name (e.g., 'cache_check')
            device_or_file: Device path or file path
            **options: Command options

        Returns:
            Complete command string
        """
        command_parts = [cmd]

        # Add device/file path if provided
        if device_or_file:
            command_parts.append(str(device_or_file))

        # Add options
        for option_key, value in options.items():
            if value is not None:
                key = option_key.replace('_', '-')
                if isinstance(value, bool) and value:
                    command_parts.append(f'--{key}')
                else:
                    command_parts.append(f'--{key}={value!s}')

        return ' '.join(command_parts)

    @classmethod
    def run(cls, device_or_file: str | Path | None = None, **options: CommandOption) -> CommandResult:
        """Run the DMPD tool with specified options.

        Args:
            device_or_file: Device path or file path to operate on
            **options: Tool-specific options

        Returns:
            Command result
        """
        cmd = cls._build_command(cls.TOOL_NAME, device_or_file, **options)
        return run(cmd)

    @classmethod
    def help(cls) -> CommandResult:
        """Get help information for the tool."""
        return run(f'{cls.TOOL_NAME} --help')

    @classmethod
    def version(cls) -> CommandResult:
        """Get version information for the tool."""
        return run(f'{cls.TOOL_NAME} --version')


# Cache Tools


class CacheCheck(DmpdTool):
    """Check cache metadata integrity.

    Usage: cache_check [options] {device|file}

    For available options, see: cache_check --help
    """

    TOOL_NAME = 'cache_check'


class CacheDump(DmpdTool):
    """Dump cache metadata to stdout or file.

    Usage: cache_dump [options] {device|file}

    For available options, see: cache_dump --help
    """

    TOOL_NAME = 'cache_dump'


class CacheRepair(DmpdTool):
    """Repair corrupted cache metadata.

    Usage: cache_repair [options] --input {device|file} --output {device|file}

    For available options, see: cache_repair --help
    """

    TOOL_NAME = 'cache_repair'


class CacheRestore(DmpdTool):
    """Restore cache metadata from backup.

    Usage: cache_restore [options] --input <file> --output {device|file}

    For available options, see: cache_restore --help
    """

    TOOL_NAME = 'cache_restore'


class CacheMetadataSize(DmpdTool):
    """Calculate cache metadata size requirements.

    Usage: cache_metadata_size [options]

    For available options, see: cache_metadata_size --help
    """

    TOOL_NAME = 'cache_metadata_size'


# Thin Tools


class ThinCheck(DmpdTool):
    """Check thin provisioning metadata integrity.

    Usage: thin_check [options] {device|file}

    For available options, see: thin_check --help
    """

    TOOL_NAME = 'thin_check'


class ThinDump(DmpdTool):
    """Dump thin metadata to stdout or file.

    Usage: thin_dump [options] {device|file}

    For available options, see: thin_dump --help
    """

    TOOL_NAME = 'thin_dump'


class ThinRepair(DmpdTool):
    """Repair corrupted thin metadata.

    Usage: thin_repair [options] --input {device|file} --output {device|file}

    For available options, see: thin_repair --help
    """

    TOOL_NAME = 'thin_repair'


class ThinRestore(DmpdTool):
    """Restore thin metadata from backup.

    Usage: thin_restore [options] --input <file> --output {device|file}

    For available options, see: thin_restore --help
    """

    TOOL_NAME = 'thin_restore'


class ThinMetadataSize(DmpdTool):
    """Calculate thin metadata size requirements.

    Usage: thin_metadata_size [options]

    For available options, see: thin_metadata_size --help
    """

    TOOL_NAME = 'thin_metadata_size'


class ThinTrim(DmpdTool):
    """Trim thin metadata.

    Usage: thin_trim [options] --data-dev {device} --metadata-dev {device}

    For available options, see: thin_trim --help
    """

    TOOL_NAME = 'thin_trim'


class ThinLs(DmpdTool):
    """List thin devices.

    Usage: thin_ls [options] {device|file}

    For available options, see: thin_ls --help
    """

    TOOL_NAME = 'thin_ls'


class ThinDelta(DmpdTool):
    """Print differences between thin devices.

    Usage: thin_delta [options] <input>

    For available options, see: thin_delta --help
    """

    TOOL_NAME = 'thin_delta'


# Era Tools


class EraCheck(DmpdTool):
    """Check era metadata integrity.

    Usage: era_check [options] {device|file}

    For available options, see: era_check --help
    """

    TOOL_NAME = 'era_check'


class EraDump(DmpdTool):
    """Dump era metadata to stdout or file.

    Usage: era_dump [options] {device|file}

    For available options, see: era_dump --help
    """

    TOOL_NAME = 'era_dump'


class EraRepair(DmpdTool):
    """Repair corrupted era metadata.

    Usage: era_repair [options] --input {device|file} --output {device|file}

    For available options, see: era_repair --help
    """

    TOOL_NAME = 'era_repair'


class EraRestore(DmpdTool):
    """Restore era metadata from backup.

    Usage: era_restore [options] --input <file> --output {device|file}

    For available options, see: era_restore --help
    """

    TOOL_NAME = 'era_restore'


# Convenience functions for common use cases


def cache_check(device_or_file: str | Path, **options: CommandOption) -> CommandResult:
    """Check cache metadata integrity."""
    return CacheCheck.run(device_or_file, **options)


def cache_dump(device_or_file: str | Path, **options: CommandOption) -> CommandResult:
    """Dump cache metadata."""
    return CacheDump.run(device_or_file, **options)


def cache_repair(**options: CommandOption) -> CommandResult:
    """Repair cache metadata."""
    return CacheRepair.run(None, **options)


def cache_restore(**options: CommandOption) -> CommandResult:
    """Restore cache metadata."""
    return CacheRestore.run(None, **options)


def cache_metadata_size(**options: CommandOption) -> CommandResult:
    """Calculate cache metadata size."""
    return CacheMetadataSize.run(None, **options)


def thin_check(device_or_file: str | Path, **options: CommandOption) -> CommandResult:
    """Check thin metadata integrity."""
    return ThinCheck.run(device_or_file, **options)


def thin_dump(device_or_file: str | Path, **options: CommandOption) -> CommandResult:
    """Dump thin metadata."""
    return ThinDump.run(device_or_file, **options)


def thin_repair(**options: CommandOption) -> CommandResult:
    """Repair thin metadata."""
    return ThinRepair.run(None, **options)


def thin_restore(**options: CommandOption) -> CommandResult:
    """Restore thin metadata."""
    return ThinRestore.run(None, **options)


def thin_metadata_size(**options: CommandOption) -> CommandResult:
    """Calculate thin metadata size."""
    return ThinMetadataSize.run(None, **options)


def thin_trim(**options: CommandOption) -> CommandResult:
    """Trim thin metadata."""
    return ThinTrim.run(None, **options)


def thin_ls(device_or_file: str | Path, **options: CommandOption) -> CommandResult:
    """List thin devices."""
    return ThinLs.run(device_or_file, **options)


def thin_delta(device_or_file: str | Path, **options: CommandOption) -> CommandResult:
    """Print differences between thin devices."""
    return ThinDelta.run(device_or_file, **options)


def era_check(device_or_file: str | Path, **options: CommandOption) -> CommandResult:
    """Check era metadata integrity."""
    return EraCheck.run(device_or_file, **options)


def era_dump(device_or_file: str | Path, **options: CommandOption) -> CommandResult:
    """Dump era metadata."""
    return EraDump.run(device_or_file, **options)


def era_repair(**options: CommandOption) -> CommandResult:
    """Repair era metadata."""
    return EraRepair.run(None, **options)


def era_restore(**options: CommandOption) -> CommandResult:
    """Restore era metadata."""
    return EraRestore.run(None, **options)


def get_help(tool_name: str) -> CommandResult:
    """Get help for any DMPD tool."""
    return run(f'{tool_name} --help')


def get_version(tool_name: str) -> CommandResult:
    """Get version for any DMPD tool."""
    return run(f'{tool_name} --version')
