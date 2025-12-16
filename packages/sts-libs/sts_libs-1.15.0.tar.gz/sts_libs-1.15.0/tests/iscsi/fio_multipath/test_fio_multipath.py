# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import time
from os import getenv
from pathlib import Path
from typing import Callable

import pytest

from sts.fio.fio import FIO
from sts.iscsi.iscsiadm import IscsiAdm


@pytest.mark.usefixtures('_iscsi_offload_setup', 'with_multipath_enabled')
def test_fio_basic_multipath(get_test_device: Callable[[], list[Path]]) -> None:
    """Test basic FIO I/O on all iSCSI multipath devices.

    This test:
    1. Login to iSCSI targets
    2. Get multipath devices
    3. Run FIO test on each multipath device

    Args:
        get_test_device: Fixture function to get test device paths
    """
    # Login to iSCSI targets first
    iscsiadm = IscsiAdm()
    assert iscsiadm.node_login().rc == 0

    time.sleep(6)  # Wait for devices to settle

    device_paths = get_test_device()
    assert device_paths, 'No test devices found'

    logging.info(f'Found {len(device_paths)} test devices')

    # Cache FIO_RUNTIME once and log it
    fio_runtime = getenv('FIO_RUNTIME', '60')
    logging.info(f'FIO runtime set to {fio_runtime} seconds')

    # Run FIO test on each device
    for i, device_path in enumerate(device_paths):
        logging.info(f'Running FIO test on device {i + 1}/{len(device_paths)}: {device_path}')
        fio = FIO(filename=str(device_path))
        fio.update_parameters({'runtime': fio_runtime})
        assert fio.run(), f'FIO test failed on device {device_path}'
        logging.info(f'FIO test completed successfully on device {device_path}')

    logging.info('All FIO multipath tests completed successfully')
