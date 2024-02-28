'''
copyright: Copyright (C) 2015-2022, Fortishield Inc.

           Created by Fortishield, Inc. <info@fortishield.github.io>.

           This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

type: integration

brief: The 'fortishield-logtest' tool allows the testing and verification of rules and decoders against provided log examples
       remotely inside a sandbox in 'fortishield-analysisd'. This functionality is provided by the manager, whose work
       parameters are configured in the ossec.conf file in the XML rule_test section. Test logs can be evaluated through
       the 'fortishield-logtest' tool or by making requests via RESTful API. These tests will check if the logtest
       configuration is valid. Also checks rules, decoders, decoders, alerts matching logs correctly.

components:
    - logtest

suite: configuration

targets:
    - manager

daemons:
    - fortishield-analysisd

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

references:
    - https://documentation.fortishield.github.io/current/user-manual/reference/tools/fortishield-logtest.html
    - https://documentation.fortishield.github.io/current/user-manual/capabilities/fortishield-logtest/index.html
    - https://documentation.fortishield.github.io/current/user-manual/reference/daemons/fortishield-analysisd.html

tags:
    - logtest_configuration
'''
from pathlib import Path
import pytest

from fortishield_testing import session_parameters
from fortishield_testing.constants.paths.logs import FORTISHIELD_LOG_PATH
from fortishield_testing.tools.monitors.file_monitor import FileMonitor
from fortishield_testing.utils import configuration
from fortishield_testing.utils.callbacks import generate_callback
from fortishield_testing.modules.analysisd import patterns

from . import CONFIGURATIONS_FOLDER_PATH, TEST_CASES_FOLDER_PATH


# Marks
pytestmark = [pytest.mark.linux, pytest.mark.tier(level=0), pytest.mark.server]

# Configuration
t_config_path = Path(CONFIGURATIONS_FOLDER_PATH, 'configuration_fortishield_conf.yaml')
t_cases_path = Path(TEST_CASES_FOLDER_PATH, 'cases_configuration_file.yaml')
t_config_parameters, t_config_metadata, t_case_ids = configuration.get_test_cases_data(t_cases_path)
t_configurations = configuration.load_configuration_template(t_config_path, t_config_parameters, t_config_metadata)

# Variables
fortishield_log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)

# Test daemons to restart.
daemons_handler_configuration = {'all_daemons': True}

# Test
@pytest.mark.parametrize('test_configuration, test_metadata', zip(t_configurations, t_config_metadata), ids=t_case_ids)
def test_configuration_file(test_configuration, test_metadata, set_fortishield_configuration, daemons_handler):
    '''
    description: Checks if `fortishield-logtest` works as expected under different predefined configurations that cause
                 `fortishield-logtest` to start correctly, to be disabled, or to register an error. To do this, it checks
                 some values in these configurations from 'fortishield_conf.yaml' file.

    fortishield_min_version: 4.2.0

    tier: 0

    parameters:
        - get_configuration:
            type: fixture
            brief: Get configuration from the module.
        - configure_environment:
            type: fixture
            brief: Configure a custom environment for testing
        - restart_fortishield:
            type: fixture
            brief: Restart fortishield, ossec.log and start a new monitor.

    assertions:
        - Verify that a valid configuration is loaded.
        - Verify that wrong loaded configurations lead to an error.

    input_description: Five test cases are defined in the module. These include some configurations stored in
                       the 'fortishield_conf.yaml'.

    expected_output:
        - r'.* Logtest started'
        - r'.* Logtest disabled'
        - r'.* Invalid value for element'
        - 'Event not found'

    tags:
        - settings
        - analysisd
    '''
    callback = None
    if 'valid_conf' == test_metadata['tags']:
        callback = patterns.LOGTEST_STARTED
    elif 'disabled_conf' == test_metadata['tags']:
        callback = patterns.LOGTEST_DISABLED
    else:
        callback = patterns.LOGTEST_CONFIG_ERROR

    fortishield_log_monitor.start(callback=generate_callback(callback), timeout=session_parameters.default_timeout)
    assert fortishield_log_monitor.callback_result, 'Event not found'
