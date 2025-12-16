# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""udevadm command management.

This module provides functionality for managing udevadm operations.
udevadm is a command-line tool for controlling systemd-udevd and monitoring
udev events. It provides various subcommands for device management and
monitoring.

Available subcommands:
- info: Query sysfs or the udev database
- trigger: Request events from the kernel
- settle: Wait for pending udev events
- control: Control the udev daemon
- monitor: Listen to kernel and udev events
- test: Test an event run
- test-builtin: Test a built-in command
- wait: Wait for device or device symlink
- lock: Lock a block device
"""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, ClassVar, Optional, Union

from sts.utils.cmdline import CommandResult, run

if TYPE_CHECKING:
    from pathlib import Path

# Type alias for command options
CommandOption = Optional[Union[bool, str, int, float]]


class UdevadmCommand(ABC):
    """Base class for udevadm subcommands.

    udevadm is a single tool with multiple subcommands for device management:
    - info: Query sysfs or the udev database
    - trigger: Request events from the kernel
    - settle: Wait for pending udev events
    - control: Control the udev daemon
    - monitor: Listen to kernel and udev events
    - test: Test an event run
    - test-builtin: Test a built-in command
    - wait: Wait for device or device symlink
    - lock: Lock a block device
    """

    # Subcommand name (must be set by subclasses)
    SUBCOMMAND: ClassVar[str]

    @staticmethod
    def _build_command(subcommand: str, target: str | Path | None = None, **options: CommandOption) -> str:
        """Build udevadm command string with subcommand and options.

        Args:
            subcommand: udevadm subcommand (e.g., 'settle', 'info')
            target: Device path, file path, or other target (if applicable)
            **options: Subcommand-specific options

        Returns:
            Complete command string
        """
        command_parts = ['udevadm', subcommand]

        # Add target if provided
        if target:
            command_parts.append(str(target))

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
    def run(cls, target: str | Path | None = None, **options: CommandOption) -> CommandResult:
        """Run the udevadm subcommand with specified options.

        Args:
            target: Device path, file path, or other target (if applicable)
            **options: Subcommand-specific options

        Returns:
            Command result
        """
        cmd = cls._build_command(cls.SUBCOMMAND, target, **options)
        return run(cmd)

    @classmethod
    def help(cls) -> CommandResult:
        """Get help information for the subcommand."""
        return run(f'udevadm {cls.SUBCOMMAND} --help')


class UdevadmSettle(UdevadmCommand):
    """Wait for pending udev events.

    Usage: udevadm settle [options]

    Wait for udev to finish processing all currently pending events and ensure
    that all device nodes have been created. This is useful for ensuring that
    device creation is complete before proceeding with operations that depend
    on the devices being available.

    For available options, see: udevadm settle --help or man udevadm
    """

    SUBCOMMAND = 'settle'


# Convenience functions for common use cases


def udevadm_settle(**options: CommandOption) -> CommandResult:
    """Wait for pending udev events.

    This function waits for udev to finish processing all currently pending
    events and ensures that all device nodes have been created.

    Args:
        **options: Command options such as:
            - timeout: Timeout in seconds (default: 120)
            - exit_if_exists: Exit if specified file exists
            - quiet: Suppress output

    Returns:
        Command result

    Example:
        # Wait with default timeout
        settle()

        # Wait with custom timeout
        settle(timeout=60)

        # Wait but exit early if file exists
        settle(exit_if_exists="/dev/sda1")

        # Wait quietly
        settle(quiet=True)
    """
    return UdevadmSettle.run(target=None, **options)
