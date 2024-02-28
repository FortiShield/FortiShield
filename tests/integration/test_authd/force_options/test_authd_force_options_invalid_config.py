'''
copyright: Copyright (C) 2015-2022, Fortishield Inc.

           Created by Fortishield, Inc. <info@fortishield.com>.

           This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

type: integration

brief: These tests will check if a set of wrong configuration option values in the block force
       are warned in the logs file.

components:
    - authd

suite: force_options

targets:
    - manager

daemons:
    - fortishield-authd

os_platform:
    - linux

os_version:
    - Arch Linux
    - Amazon Linux 2
    - Amazon Linux 1
    - CentOS 8
    - CentOS 7
    - Debian Buster
    - Red Hat 8
    - Ubuntu Focal
    - Ubuntu Bionic

tags:
    - enrollment
    - authd
'''
import re
import pytest
from pathlib import Path

from fortishield_testing.utils.file import truncate_file
from fortishield_testing.utils.services import control_service
from fortishield_testing.constants.paths.logs import FORTISHIELD_LOG_PATH
from fortishield_testing.utils.configuration import load_configuration_template, get_test_cases_data
from fortishield_testing.constants.daemons import AUTHD_DAEMON
from fortishield_testing.tools.monitors.file_monitor import FileMonitor
from fortishield_testing.utils import callbacks
from fortishield_testing.modules.authd import PREFIX
from fortishield_testing.modules.authd.configuration import AUTHD_DEBUG_CONFIG

from . import CONFIGURATIONS_FOLDER_PATH, TEST_CASES_FOLDER_PATH

# Marks
pytestmark = [pytest.mark.linux, pytest.mark.tier(level=0), pytest.mark.server]

# Configurations
test_configuration_path = Path(CONFIGURATIONS_FOLDER_PATH, 'config_authd_force_options.yaml')
test_cases_path = Path(TEST_CASES_FOLDER_PATH, 'cases_authd_force_options_invalid_config.yaml')
test_configuration, test_metadata, test_cases_ids = get_test_cases_data(test_cases_path)
test_configuration = load_configuration_template(test_configuration_path, test_configuration, test_metadata)

local_internal_options = {AUTHD_DEBUG_CONFIG: '2'}
daemons_handler_configuration = {'daemons': [AUTHD_DAEMON], 'ignore_errors': True}

# Tests
@pytest.mark.parametrize('test_configuration,test_metadata', zip(test_configuration, test_metadata), ids=test_cases_ids)
def test_authd_force_options_invalid_config(test_configuration, test_metadata, set_fortishield_configuration,
                                            configure_local_internal_options, truncate_monitored_files,
                                            daemons_handler):
    '''
    description:
        Checks that every input with a wrong configuration option value
        matches the adequate output log. None force registration
        or response message is made.

    fortishield_min_version:
        4.3.0

    tier: 0

    parameters:
        - test_configuration:
            type: dict
            brief: Configuration loaded from `configuration_templates`.
        - test_metadata:
            type: dict
            brief: Test case metadata.
        - set_fortishield_configuration:
            type: fixture
            brief: Load basic fortishield configuration.
        - configure_local_internal_options:
            type: fixture
            brief: Handle the monitoring of a specified file.
        - truncate_monitored_files:
            type: fixture
            brief: Truncate all the log files and json alerts files before and after the test execution.
        - daemons_handler:
            type: fixture
            brief: Handler of Fortishield daemons.

    assertions:
        - The received output must match with expected due to wrong configuration options.

    input_description:
        Different test cases are contained in an external YAML file (invalid_config folder) which includes
        different possible wrong settings.

    expected_output:
        - Invalid configuration values error.
    '''

    fortishield_log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)
    log = re.escape(test_metadata['log'])
    fortishield_log_monitor.start(callback=callbacks.generate_callback(fr'{PREFIX}{log}'), timeout=10)
    assert fortishield_log_monitor.callback_result, f'Error event not detected'
