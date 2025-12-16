# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""sg3_utils command wrappers.

This module provides Python wrappers for sg3_utils commands:
- Persistent Reservations (SCSI-3)
- Device inquiry and information
- Read/write operations
- Diagnostic commands
- Format and verify operations

sg3_utils is a collection of utilities for devices that use the SCSI command set:
- SCSI disks
- USB mass storage devices
- SATA devices (via SAT)
- NVMe devices (via NVMe-MI)
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, ClassVar, Final

from sts.utils.cmdline import run
from sts.utils.packages import ensure_installed

if TYPE_CHECKING:
    from pathlib import Path

    from testinfra.backend.base import CommandResult

logger = logging.getLogger(__name__)

# Package and command constants
PACKAGE_NAME: Final[str] = 'sg3_utils'

# Persistent Reservation type constants
PR_TYPE_WRITE_EXCLUSIVE = 1
PR_TYPE_EXCLUSIVE_ACCESS = 3
PR_TYPE_WRITE_EXCLUSIVE_REGISTRANTS_ONLY = 5
PR_TYPE_EXCLUSIVE_ACCESS_REGISTRANTS_ONLY = 6
PR_TYPE_WRITE_EXCLUSIVE_ALL_REGISTRANTS = 7
PR_TYPE_EXCLUSIVE_ACCESS_ALL_REGISTRANTS = 8

# PR type number to human-readable name mapping
PR_TYPE_NAMES: Final[dict[int, str]] = {
    PR_TYPE_WRITE_EXCLUSIVE: 'Write Exclusive',
    PR_TYPE_EXCLUSIVE_ACCESS: 'Exclusive Access',
    PR_TYPE_WRITE_EXCLUSIVE_REGISTRANTS_ONLY: 'Write Exclusive, registrants only',
    PR_TYPE_EXCLUSIVE_ACCESS_REGISTRANTS_ONLY: 'Exclusive Access, registrants only',
    PR_TYPE_WRITE_EXCLUSIVE_ALL_REGISTRANTS: 'Write Exclusive, all registrants',
    PR_TYPE_EXCLUSIVE_ACCESS_ALL_REGISTRANTS: 'Exclusive Access, all registrants',
}

# Reverse mapping for parsing sg_persist output
PR_NAME_TO_TYPE: Final[dict[str, str]] = {name.lower(): str(num) for num, name in PR_TYPE_NAMES.items()}


def get_pr_type_name(pr_type: int) -> str:
    """Get human-readable name for PR type.

    Args:
        pr_type: Persistent reservation type number

    Returns:
        Human-readable name for the PR type

    Example:
        ```python
        name = get_pr_type_name(PR_TYPE_WRITE_EXCLUSIVE)
        print(f'PR type: {name}')  # "PR type: Write Exclusive"
        ```
    """
    return PR_TYPE_NAMES.get(pr_type, f'Unknown type ({pr_type})')


class Sg3UtilsCommand:
    """Base class for all sg3_utils commands.

    Provides common functionality:
    - Package installation verification
    - Command execution
    - Error handling
    - Common output parsing utilities
    """

    PACKAGE_NAME: ClassVar[str] = PACKAGE_NAME

    def __init__(self) -> None:
        """Initialize sg3_utils command wrapper."""
        ensure_installed(self.PACKAGE_NAME)

    def _run_command(self, *args: str | None, **kwargs: str | None) -> CommandResult:
        """Run sg3_utils command with common error handling.

        Args:
            *args: Command arguments (None values are filtered out)
            **kwargs: Additional command arguments as key=value pairs (None values are filtered out)

        Returns:
            CommandResult from command execution

        Example:
            ```python
            # Basic usage:
            # self._run_command('sg_persist', '--in', '--read-keys', '/dev/sda')
            ```
        """
        # Filter out None values from positional arguments
        filtered_args = [arg for arg in args if arg is not None]

        # Build base command string
        command_str = ' '.join(filtered_args)

        # Handle kwargs by converting to key=value arguments
        if kwargs:
            # Filter out None values from kwargs
            filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
            if filtered_kwargs:
                kwargs_str = ' '.join([f'{key}={value}' for key, value in filtered_kwargs.items()])
                command_str = f'{command_str} {kwargs_str}'

        logger.debug(f'Running sg3_utils command: {command_str}')
        result = run(command_str)

        if result.failed:
            logger.warning(f'Command failed: {command_str}, stderr: {result.stderr}')

        return result

    # ==========================================================================
    # Common Output Parsing Utilities
    # ==========================================================================

    @staticmethod
    def parse_key_value_pairs(output: str, separators: str = '=:') -> dict[str, str]:
        r"""Parse 'key=value' or 'key: value' lines from output.

        Args:
            output: Raw command output
            separators: Characters to treat as key-value separators

        Returns:
            Dictionary of key-value pairs found in output

        Example:
            ```python
            output = 'Vendor identification: Samsung\nKey=0x1234'
            pairs = Sg3UtilsCommand.parse_key_value_pairs(output)
            # {'Vendor identification': 'Samsung', 'Key': '0x1234'}
            ```
        """
        pairs = {}
        for line in output.split('\n'):
            stripped_line = line.strip()
            if not stripped_line:
                continue

            # Find first separator in the line
            separator_pos = -1
            for sep in separators:
                pos = stripped_line.find(sep)
                if pos != -1 and (separator_pos == -1 or pos < separator_pos):
                    separator_pos = pos

            if separator_pos != -1:
                key = stripped_line[:separator_pos].strip()
                value = stripped_line[separator_pos + 1 :].strip()
                if key and value:
                    pairs[key] = value

        return pairs

    @staticmethod
    def extract_section_lines(output: str, section_header: str) -> list[str]:
        r"""Extract lines that appear after a section header.

        Args:
            output: Raw command output
            section_header: Header text to look for (case-insensitive)

        Returns:
            List of lines that appear after the header until next section or end

        Example:
            ```python
            output = 'PR generation=0x6, Reservation follows:\n  Key=0x1234\n  scope: LU_SCOPE'
            lines = Sg3UtilsCommand.extract_section_lines(output, 'Reservation follows:')
            # ['Key=0x1234', 'scope: LU_SCOPE']
            ```
        """
        lines = output.split('\n')
        section_lines = []
        in_section = False

        for line in lines:
            line_stripped = line.strip()

            # Check if this line contains the section header
            if section_header.lower() in line.lower():
                in_section = True
                continue

            # If we're in the section, collect non-empty lines
            if in_section:
                # Stop at next section (lines ending with ':') or empty lines that might indicate new section
                if line_stripped.endswith(':') and not line_stripped.startswith(' '):
                    break
                if line_stripped:  # Only add non-empty lines
                    section_lines.append(line_stripped)

        return section_lines

    @staticmethod
    def extract_hex_keys(output: str) -> list[str]:
        r"""Extract all hex keys (0x1234 format) from output.

        Args:
            output: Raw command output

        Returns:
            List of hex keys found in output

        Example:
            ```python
            output = 'registered reservation key follows:\n  0x1234\n  0xabcd'
            keys = Sg3UtilsCommand.extract_hex_keys(output)
            # ['0x1234', '0xabcd']
            ```
        """
        hex_pattern = re.compile(r'0x[0-9a-fA-F]+')
        return hex_pattern.findall(output)

    @staticmethod
    def clean_line(line: str) -> str:
        """Clean and normalize a line (strip whitespace, remove extra spaces).

        Args:
            line: Raw line to clean

        Returns:
            Cleaned line with normalized whitespace

        Example:
            ```python
            cleaned = Sg3UtilsCommand.clean_line('  Key=0x1234   ')
            # "Key=0x1234"
            ```
        """
        return ' '.join(line.strip().split())

    @staticmethod
    def find_line_containing(output: str, pattern: str, *, case_sensitive: bool = False) -> str | None:
        """Find first line containing a specific pattern.

        Args:
            output: Raw command output
            pattern: Text pattern to search for
            case_sensitive: Whether search should be case sensitive

        Returns:
            First line containing the pattern, or None if not found

        Example:
            ```python
            line = Sg3UtilsCommand.find_line_containing(output, 'NO reservation held')
            # "PR generation=0x4, there is NO reservation held"
            ```
        """
        search_pattern = pattern if case_sensitive else pattern.lower()

        for line in output.split('\n'):
            search_line = line if case_sensitive else line.lower()
            if search_pattern in search_line:
                return line.strip()

        return None


# =============================================================================
# Persistent Reservations
# =============================================================================


class SgPersist(Sg3UtilsCommand):
    """SCSI Persistent Reservations using sg_persist.

    Persistent Reservations provide a mechanism for coordinating access to
    shared SCSI devices between multiple initiators (hosts).

    Key concepts:
    - Registration: Initiators register with a reservation key
    - Reservation: One initiator holds exclusive or shared access
    - Preemption: Ability to remove other initiators' registrations
    """

    COMMAND: ClassVar[str] = 'sg_persist'

    # ==========================================================================
    # Command-Specific Parser Methods
    # ==========================================================================

    def _parse_keys_from_output(self, output: str) -> list[str]:
        """Parse registered keys from sg_persist --read-keys output.

        Args:
            output: Raw sg_persist output

        Returns:
            List of registered keys found in output (preserves duplicates as reported by device)
        """
        keys = []
        lines = output.split('\n')
        found_keys_section = False

        for line in lines:
            stripped_line = line.strip()
            # Look for the keys section header
            if 'registered reservation key' in stripped_line.lower():
                found_keys_section = True
                continue
            # Parse keys (lines starting with 0x after the header)
            if found_keys_section and stripped_line.startswith('0x'):
                keys.append(stripped_line)

        # Return keys exactly as reported by the device (including duplicates)
        return keys

    def _parse_reservation_from_output(self, output: str) -> tuple[str | None, str | None]:
        """Parse reservation holder and type from sg_persist --read-reservation output.

        Args:
            output: Raw sg_persist output

        Returns:
            Tuple of (holder_key, reservation_type) or (None, None) if no reservation
        """
        holder = None
        res_type = None

        # Check if there's actually a reservation
        if self.find_line_containing(output, 'NO reservation held'):
            return None, None

        # Look for reservation section
        if 'Reservation follows:' in output:
            reservation_lines = self.extract_section_lines(output, 'Reservation follows:')

            for line in reservation_lines:
                # Parse Key=0x1234 format
                if line.startswith('Key='):
                    holder = line.split('=')[1].strip()

                # Parse type from scope/type line
                elif 'type:' in line:
                    type_part = line.split('type:')[1].strip()
                    res_type = self._parse_pr_type_from_text(type_part)

        return holder, res_type

    def _parse_pr_type_from_text(self, text: str) -> str | None:
        """Convert PR type text to number using centralized mapping.

        Args:
            text: Type text from sg_persist output (e.g., "Write Exclusive, all registrants")

        Returns:
            PR type number as string, or None if not found
        """
        if not text:
            return None

        # Use centralized mapping for type names to numbers
        # Sort by length (longest first) to match most specific patterns first
        sorted_mappings = sorted(PR_NAME_TO_TYPE.items(), key=lambda x: len(x[0]), reverse=True)
        for type_name_lower, type_num in sorted_mappings:
            if type_name_lower in text.lower():
                return type_num

        # If no exact mapping found, return the raw type
        return text.split(',')[0].strip()

    def _parse_full_status_from_output(self, output: str) -> dict[str, str]:
        """Parse full status information from sg_persist --read-full-status output.

        Args:
            output: Raw sg_persist output

        Returns:
            Dictionary of parsed status information
        """
        return self.parse_key_value_pairs(output)

    def _parse_transport_ids_from_output(self, output: str) -> list[dict[str, str]]:
        """Parse transport IDs from sg_persist --read-full-status output.

        Args:
            output: Raw sg_persist output

        Returns:
            List of transport ID dictionaries with 'type', 'id', and 'key' fields
        """
        transport_ids = []
        lines = output.split('\n')
        current_key = None

        # Transport type keywords (order matters for specificity)
        transport_keywords = [
            ('iscsi', 'iscsi'),
            ('sas', 'sas address'),
            ('fc', 'fc n_port_id'),
            ('fc', 'fibre channel'),
        ]

        for i, line in enumerate(lines):
            stripped_line = line.strip()

            if stripped_line.startswith('Key='):
                current_key = stripped_line.split('=')[1].strip()
            elif 'Transport Id of initiator:' in stripped_line and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if ':' not in next_line:
                    continue

                transport_id = next_line.split(':', 1)[1].strip()
                transport_type = 'unknown'

                # Find transport type by keyword matching
                for t_type, keyword in transport_keywords:
                    if keyword in next_line.lower():
                        transport_type = t_type
                        break

                transport_ids.append({'type': transport_type, 'id': transport_id, 'key': current_key or 'unknown'})

        return transport_ids

    # ==========================================================================
    # Public Methods
    # ==========================================================================

    def read_keys(self, device: str | Path) -> list[str]:
        """Read all registered keys for a device.

        Args:
            device: Device path (e.g., '/dev/sda')

        Returns:
            List of registered keys (empty list on error)
        """
        result = self._run_command(self.COMMAND, '--in', '--read-keys', str(device))

        if result.succeeded:
            return self._parse_keys_from_output(result.stdout)
        logger.warning(f'Failed to read keys for {device}: {result.stderr}')
        return []

    def read_reservation(self, device: str | Path) -> tuple[str | None, str | None]:
        """Read current reservation holder for a device.

        Args:
            device: Device path (e.g., '/dev/sda')

        Returns:
            Tuple of (holder_key, reservation_type) or (None, None) if no reservation or error

        Example output formats:
            # Specific key holder:
            PR generation=0x6, Reservation follows:
              Key=0x1234
              scope: LU_SCOPE,  type: Write Exclusive

            # All registrants reservation:
            PR generation=0x6, Reservation follows:
              Key=0x0
              scope: LU_SCOPE,  type: Exclusive Access, all registrants

            # No reservation:
            PR generation=0x4, there is NO reservation held
        """
        result = self._run_command(self.COMMAND, '--in', '--read-reservation', str(device))

        if result.succeeded:
            return self._parse_reservation_from_output(result.stdout)
        logger.warning(f'Failed to read reservation for {device}: {result.stderr}')
        return (None, None)

    def read_full_status(self, device: str | Path) -> dict[str, str]:
        """Read full status (keys and reservation) for a device.

        Args:
            device: Device path (e.g., '/dev/sda')

        Returns:
            Dictionary with complete status information (empty dict on error)
        """
        result = self._run_command(self.COMMAND, '--in', '--read-full-status', str(device))

        if result.succeeded:
            return self._parse_full_status_from_output(result.stdout)
        logger.warning(f'Failed to read full status for {device}: {result.stderr}')
        return {}

    def get_transport_ids(self, device: str | Path) -> list[dict[str, str]]:
        """Get transport IDs of all registered initiators.

        Args:
            device: Device path (e.g., '/dev/sda')

        Returns:
            List of transport ID dictionaries, each containing:
            - 'type': Transport type ('iscsi', 'sas', 'fc', or 'unknown')
            - 'id': Transport identifier string
            - 'key': Associated registration key

        Example:
            ```python
            transport_ids = sg_persist.get_transport_ids('/dev/sda')
            for tid in transport_ids:
                logger.info(f'Key {tid["key"]}: {tid["type"]} - {tid["id"]}')
            ```
        """
        result = self._run_command(self.COMMAND, '--in', '--read-full-status', str(device))

        if result.succeeded:
            return self._parse_transport_ids_from_output(result.stdout)
        logger.warning(f'Failed to read transport IDs for {device}: {result.stderr}')
        return []

    def register(self, device: str | Path, key: str, transport_id: str | None = None) -> bool:
        """Register a key for persistent reservations.

        Args:
            device: Device path (e.g., '/dev/sda')
            key: Registration key (e.g., '0x2')
            transport_id: Transport-specific identifier (e.g., 'sas,5001405f31c32fa2')

        Returns:
            True if registration succeeded, False otherwise

        Examples:
            ```python
            # Simple registration: sg_persist --out --register --param-sark 0xaaaa /dev/sdb
            persist.register('/dev/sdb', '0xaaaa')

            # With transport ID: sg_persist --out --register --param-sark 0x2 -X "sas,5001405f31c32fa2" /dev/sda
            persist.register('/dev/sda', '0x2', transport_id='sas,5001405f31c32fa2')
            ```
        """
        result = self._run_command(
            self.COMMAND,
            '--out',
            '--register',
            '--param-sark',
            key,
            '-X' if transport_id else None,
            transport_id,
            str(device),
        )

        if not result.succeeded:
            logger.warning(f'Failed to register key {key} for {device}: {result.stderr}')

        return result.succeeded

    def unregister(self, device: str | Path, key_to_remove: str) -> bool:
        """Delete an existing registration.

        Args:
            device: Device path (e.g., '/dev/sdb')
            key_to_remove: Registration key to delete (e.g., '0xAAAA')

        Returns:
            True if unregistration succeeded, False otherwise

        Example:
            ```python
            # Delete Host A's registration
            persist.unregister('/dev/sdb', '0xAAAA')
            # Executes: sg_persist --out --register --param-rk=0xAAAA --param-sark=0 /dev/sdb
            ```
        """
        result = self._run_command(
            self.COMMAND, '--out', '--register', f'--param-rk={key_to_remove}', '--param-sark=0', str(device)
        )

        if not result.succeeded:
            logger.warning(f'Failed to unregister key {key_to_remove} for {device}: {result.stderr}')

        return result.succeeded

    def reserve(self, device: str | Path, key: str, prout_type: int | str = 1) -> bool:
        """Create a reservation on a device.

        Args:
            device: Device path (e.g., '/dev/sda')
            key: Reservation key (must be previously registered, e.g., '0x2')
            prout_type: Persistent reservation type,

        Returns:
            True if reservation succeeded, False otherwise

        Example:
            ```python
            # Reserve with write-exclusive: sg_persist --out --reserve --param-rk=0x2 --prout-type=1 /dev/sda
            persist.reserve('/dev/sda', '0x2', prout_type=1)
            ```
        """
        result = self._run_command(
            self.COMMAND, '--out', '--reserve', f'--param-rk={key}', f'--prout-type={prout_type}', str(device)
        )

        if not result.succeeded:
            logger.warning(f'Failed to reserve {device} with key {key}: {result.stderr}')

        return result.succeeded

    def release(self, device: str | Path, key: str, prout_type: int | str = 1) -> bool:
        """Release a reservation on a device.

        Args:
            device: Device path (e.g., '/dev/sda')
            key: Reservation key (e.g., '0x2')
            prout_type: Persistent reservation type to release,

        Returns:
            True if release succeeded, False otherwise

        Example:
            ```python
            # Release write-exclusive: sg_persist --out --release --param-rk=0x2 --prout-type=1 /dev/sda
            persist.release('/dev/sda', '0x2', prout_type=1)
            ```
        """
        result = self._run_command(
            self.COMMAND, '--out', '--release', f'--param-rk={key}', f'--prout-type={prout_type}', str(device)
        )

        if not result.succeeded:
            logger.warning(f'Failed to release reservation on {device} with key {key}: {result.stderr}')

        return result.succeeded

    def report_capabilities(self, device: str | Path) -> bool:
        """Report persistent reservation capabilities for a device.

        Args:
            device: Device path (e.g., '/dev/sda')

        Returns:
            True if device supports PR operations, False otherwise

        Example:
            ```python
            # Check PR support: sg_persist --in --report-capabilities /dev/sda
            if persist.report_capabilities('/dev/sda'):
                print('Device supports persistent reservations')
            ```
        """
        result = self._run_command(self.COMMAND, '--in', '--report-capabilities', str(device))

        if not result.succeeded:
            logger.warning(f'Failed to check PR capabilities for {device}: {result.stderr}')

        return result.succeeded


# =============================================================================
# Device Inquiry and Information
# =============================================================================


class SgInq(Sg3UtilsCommand):
    """SCSI INQUIRY command using sg_inq.

    The INQUIRY command returns basic information about a SCSI device:
    - Vendor identification
    - Product identification
    - Product revision level
    - Device type
    """

    COMMAND: ClassVar[str] = 'sg_inq'

    def inquiry(self, device: str | Path, *, vpd: bool = False) -> CommandResult:
        """Perform SCSI INQUIRY on a device.

        Args:
            device: Device path (e.g., '/dev/sda')
            vpd: Request Vital Product Data pages

        Returns:
            CommandResult with inquiry information
        """
        return self._run_command(self.COMMAND, '--vpd' if vpd else None, str(device))


class SgVpd(Sg3UtilsCommand):
    """SCSI Vital Product Data using sg_vpd.

    VPD pages provide additional device information beyond standard INQUIRY:
    - Serial numbers
    - Device identification
    - Supported VPD pages
    - Block limits
    """

    COMMAND: ClassVar[str] = 'sg_vpd'

    def get_vpd_page(self, device: str | Path, page: str) -> CommandResult:
        """Get a specific VPD page from a device.

        Args:
            device: Device path (e.g., '/dev/sda')
            page: VPD page identifier (e.g., 'sn', 'di', 'bl')

        Returns:
            CommandResult with VPD page data
        """
        return self._run_command(self.COMMAND, f'--page={page}', str(device))


# =============================================================================
# Read/Write Operations
# =============================================================================


class SgRead(Sg3UtilsCommand):
    """SCSI READ commands using sg_read."""

    COMMAND: ClassVar[str] = 'sg_read'

    def read_blocks(self, device: str | Path, lba: int, count: int, block_size: int = 512) -> CommandResult:
        """Read blocks from a SCSI device.

        Args:
            device: Device path (e.g., '/dev/sda')
            lba: Logical Block Address to start reading from
            count: Number of blocks to read
            block_size: Block size in bytes (default: 512)

        Returns:
            CommandResult with read operation result
        """
        return self._run_command(self.COMMAND, f'--lba={lba}', f'--num={count}', f'--bs={block_size}', str(device))


class SgReadcap(Sg3UtilsCommand):
    """SCSI READ CAPACITY commands using sg_readcap."""

    COMMAND: ClassVar[str] = 'sg_readcap'

    def get_capacity(self, device: str | Path, *, long_format: bool = False) -> CommandResult:
        """Get device capacity information.

        Args:
            device: Device path (e.g., '/dev/sda')
            long_format: Use READ CAPACITY(16) instead of READ CAPACITY(10)

        Returns:
            CommandResult with capacity information
        """
        return self._run_command(self.COMMAND, '--16' if long_format else None, str(device))


class SgWrite(Sg3UtilsCommand):
    """SCSI WRITE commands using sg_write_*."""

    COMMAND: ClassVar[str] = 'sg_write_same'

    def write_same(self, device: str | Path, lba: int, count: int, data_pattern: str = '0x00') -> CommandResult:
        """Write same data pattern to multiple blocks.

        Args:
            device: Device path (e.g., '/dev/sda')
            lba: Starting Logical Block Address
            count: Number of blocks to write
            data_pattern: Data pattern to write (default: all zeros)

        Returns:
            CommandResult with write operation result
        """
        return self._run_command(self.COMMAND, f'--lba={lba}', f'--num={count}', f'--in={data_pattern}', str(device))


# =============================================================================
# Diagnostic Commands
# =============================================================================


class SgLogs(Sg3UtilsCommand):
    """SCSI LOG SENSE commands using sg_logs."""

    COMMAND: ClassVar[str] = 'sg_logs'

    def get_log_page(self, device: str | Path, page: str) -> CommandResult:
        """Get a log page from a device.

        Args:
            device: Device path (e.g., '/dev/sda')
            page: Log page identifier (e.g., 'temp', 'ie', 'sp')

        Returns:
            CommandResult with log page data
        """
        return self._run_command('sg_logs', f'--page={page}', str(device))


class SgSenddiag(Sg3UtilsCommand):
    """SCSI SEND DIAGNOSTIC commands using sg_senddiag."""

    COMMAND: ClassVar[str] = 'sg_senddiag'

    def send_diagnostic(self, device: str | Path, test_type: str = 'default') -> CommandResult:
        """Send diagnostic command to device.

        Args:
            device: Device path (e.g., '/dev/sda')
            test_type: Type of diagnostic test

        Returns:
            CommandResult with diagnostic result
        """
        return self._run_command(
            'sg_senddiag',
            '--test' if test_type != 'default' else None,
            test_type if test_type != 'default' else None,
            str(device),
        )


# =============================================================================
# Format and Verify Operations
# =============================================================================


class SgFormat(Sg3UtilsCommand):
    """SCSI FORMAT UNIT commands using sg_format."""

    COMMAND: ClassVar[str] = 'sg_format'

    def format_device(
        self, device: str | Path, block_size: int | None = None, *, dry_run: bool = True
    ) -> CommandResult:
        """Format a SCSI device.

        Args:
            device: Device path (e.g., '/dev/sda')
            block_size: Block size for formatting (optional)
            dry_run: Perform dry run without actual formatting (default: True for safety)

        Returns:
            CommandResult with format operation result
        """
        return self._run_command(
            'sg_format',
            '--dry-run' if dry_run else None,
            '--size' if block_size else None,
            str(block_size) if block_size else None,
            str(device),
        )


class SgVerify(Sg3UtilsCommand):
    """SCSI VERIFY commands using sg_verify."""

    COMMAND: ClassVar[str] = 'sg_verify'

    def verify_blocks(self, device: str | Path, lba: int, count: int) -> CommandResult:
        """Verify blocks on a SCSI device.

        Args:
            device: Device path (e.g., '/dev/sda')
            lba: Starting Logical Block Address
            count: Number of blocks to verify

        Returns:
            CommandResult with verify operation result
        """
        return self._run_command('sg_verify', f'--lba={lba}', f'--num={count}', str(device))


# =============================================================================
# Additional Utility Commands
# =============================================================================


class SgScan(Sg3UtilsCommand):
    """SCSI device scanning using sg_scan."""

    COMMAND: ClassVar[str] = 'sg_scan'

    def scan_devices(self) -> CommandResult:
        """Scan for SCSI devices.

        Returns:
            CommandResult with list of detected SCSI devices
        """
        return self._run_command('sg_scan')


class SgMap(Sg3UtilsCommand):
    """SCSI device mapping using sg_map."""

    COMMAND: ClassVar[str] = 'sg_map'

    def map_devices(self) -> CommandResult:
        """Map SCSI generic devices to block devices.

        Returns:
            CommandResult with device mapping information
        """
        return self._run_command('sg_map')
