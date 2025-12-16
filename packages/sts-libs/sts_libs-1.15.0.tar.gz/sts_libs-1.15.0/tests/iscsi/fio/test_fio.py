# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
from os import getenv
from pathlib import Path
from typing import Callable

import pytest

from sts.fio.fio import FIO
from sts.iscsi.iscsiadm import IscsiAdm


@pytest.mark.usefixtures('_iscsi_offload_setup', 'with_multipath_disabled')
def test_fio_basic(get_test_device: Callable[[str], list[Path]]) -> None:
    """Test basic FIO I/O on all iSCSI devices.

    This test:
    1. Disable multipath to prevent device interference
    2. Get all test devices
    3. Run FIO test on each device
    4. Restore multipath if it was running

    Args:
        get_test_device: Fixture function to get test device paths
    """
    # Get all test devices
    iscsiadm = IscsiAdm()
    assert iscsiadm.node_login().rc == 0
    logging.info('Getting all test devices')
    device_paths = get_test_device('COMPELNT')
    logging.info(f'Found {len(device_paths)} devices: {device_paths}')

    fio_runtime = getenv('FIO_RUNTIME', '60')
    logging.info(f'Using FIO runtime: {fio_runtime} seconds')

    # Run FIO test on each device
    for i, device_path in enumerate(device_paths):
        logging.info(f'Running FIO test on device {i + 1}/{len(device_paths)}: {device_path}')
        fio = FIO(filename=str(device_path))
        fio.update_parameters({'runtime': fio_runtime})
        assert fio.run(), f'FIO test failed on device {device_path}'
        logging.info(f'FIO test completed successfully on device {device_path}')

    logging.info('All FIO tests completed successfully')
