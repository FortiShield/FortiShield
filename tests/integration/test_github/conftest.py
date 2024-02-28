# Copyright (C) 2015-2021, Fortishield Inc.
# Created by Fortishield, Inc. <info@fortishield.github.io>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

import pytest

from fortishield_testing.constants.paths.logs import FORTISHIELD_LOG_PATH
from fortishield_testing.modules.modulesd import patterns
from fortishield_testing.tools.monitors.file_monitor import FileMonitor
from fortishield_testing.utils import callbacks


@pytest.fixture()
def wait_for_github_start():
    # Wait for module github starts
    fortishield_log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)
    fortishield_log_monitor.start(callback=callbacks.generate_callback(patterns.MODULESD_STARTED, {
                              'integration': 'GitHub'
                          }))
    assert (fortishield_log_monitor.callback_result == None), f'Error invalid configuration event not detected'
