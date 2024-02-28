# Copyright (C) 2015-2021, Fortishield Inc.
# Created by Fortishield, Inc. <info@fortishield.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

import pytest

from fortishield_testing.modules.analysisd.patterns import LOGTEST_STARTED
from fortishield_testing.tools.monitors.file_monitor import FileMonitor
from fortishield_testing.utils.callbacks import generate_callback
from fortishield_testing.constants.paths.logs import FORTISHIELD_LOG_PATH

@pytest.fixture(scope='module')
def wait_for_logtest_startup(request):
    """Wait until logtest has begun."""
    log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)
    log_monitor.start(callback=generate_callback(LOGTEST_STARTED), timeout=40, only_new_events=True)
