"""
 Copyright (C) 2015-2021, Fortishield Inc.
 Created by Fortishield, Inc. <info@fortishield.github.io>.
 This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
"""

import pytest

from pathlib import Path
from fortishield_testing.constants.paths.configurations import FORTISHIELD_CONF_PATH
from fortishield_testing.tools.monitors.file_monitor import FileMonitor
from fortishield_testing.utils.callbacks import generate_callback
from fortishield_testing.utils.configuration import get_test_cases_data, load_configuration_template
from fortishield_testing.constants.paths.logs import FORTISHIELD_LOG_PATH

from . import CONFIGS_PATH, TEST_CASES_PATH

from fortishield_testing.modules.remoted.configuration import REMOTED_DEBUG
from fortishield_testing.modules.remoted import patterns
from fortishield_testing.modules.api import utils
from fortishield_testing.utils.network import format_ipv6_long

# Set pytest marks.
pytestmark = [pytest.mark.server, pytest.mark.tier(level=1)]

# Cases metadata and its ids.
cases_path = Path(TEST_CASES_PATH, 'cases_syslog_no_allowed_ips.yaml')
config_path = Path(CONFIGS_PATH, 'config_syslog_no_allowed_ips.yaml')
test_configuration, test_metadata, cases_ids = get_test_cases_data(cases_path)
test_configuration = load_configuration_template(config_path, test_configuration, test_metadata)

daemons_handler_configuration = {'all_daemons': True}

local_internal_options = {REMOTED_DEBUG: '2'}

# Test function.
@pytest.mark.parametrize('test_configuration, test_metadata',  zip(test_configuration, test_metadata), ids=cases_ids)
def test_syslog_no_allowed_ips(test_configuration, test_metadata, configure_local_internal_options, truncate_monitored_files,
                            set_fortishield_configuration, restart_fortishield_expect_error):

    '''
    description: Check that 'fortishield-remoted' fails when 'allowed-ips' is not provided but syslog connection is used.
                 For this purpose, it uses the configuration from test cases, and check that fail info message has been
                 logged in 'ossec.log'.

    parameters:
        - test_configuration
            type: dict
            brief: Configuration applied to ossec.conf.
        - test_metadata:
            type: dict
            brief: Test case metadata.
        - truncate_monitored_files:
            type: fixture
            brief: Truncate all the log files and json alerts files before and after the test execution.
        - configure_local_internal_options:
            type: fixture
            brief: Configure the Fortishield local internal options using the values from `local_internal_options`.
        - daemons_handler:
            type: fixture
            brief: Starts/Restarts the daemons indicated in `daemons_handler_configuration` before each test,
                   once the test finishes, stops the daemons.
        - restart_fortishield_expect_error
            type: fixture
            brief: Restart service when expected error is None, once the test finishes stops the daemons.
    '''

    log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)
    log_monitor.start(callback=generate_callback(patterns.INFO_NO_ALLOWED_IPS))

    assert log_monitor.callback_result
