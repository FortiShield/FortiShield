'''
copyright: Copyright (C) 2015-2022, Fortishield Inc.

           Created by Fortishield, Inc. <info@fortishield.com>.

           This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

type: integration

brief: The Fortishield 'github' module allows you to collect all the 'audit logs' from GitHub using its API.
       Specifically, these tests will check if that module detects invalid configurations and indicates
       the location of the errors detected. The 'audit log' allows organization admins to quickly review
       the actions performed by members of your organization. It includes details such as who performed
       the action, what the action was, and when it was performed.

components:
    - github

suite: configuration

targets:
    - agent
    - manager

daemons:
    - fortishield-analysisd
    - fortishield-monitord
    - fortishield-modulesd

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
    - https://github.com/fortishield/fortishield-documentation/blob/develop/source/github/monitoring-github-activity.rst

tags:
    - github_configuration
'''
import pytest
from pathlib import Path

from fortishield_testing.constants.paths.logs import FORTISHIELD_LOG_PATH
from fortishield_testing.modules.modulesd.configuration import MODULESD_DEBUG
from fortishield_testing.modules.modulesd import patterns
from fortishield_testing.tools.monitors.file_monitor import FileMonitor
from fortishield_testing.utils.configuration import get_test_cases_data
from fortishield_testing.utils.configuration import load_configuration_template
from fortishield_testing.utils import callbacks
from . import CONFIGS_PATH, TEST_CASES_PATH

# Marks
pytestmark = pytest.mark.tier(level=0)

# Configuration and cases data.
configs_path = Path(CONFIGS_PATH, 'config_invalid_configuration.yaml')
cases_path = Path(TEST_CASES_PATH, 'cases_invalid_configuration.yaml')

# Test configurations.
config_parameters, test_metadata, test_cases_ids = get_test_cases_data(cases_path)
test_configuration = load_configuration_template(configs_path, config_parameters, test_metadata)
daemons_handler_configuration = {'all_daemons': True, 'ignore_errors': True}
local_internal_options = {MODULESD_DEBUG: '2'}

# Tests
@pytest.mark.parametrize('test_configuration, test_metadata', zip(test_configuration, test_metadata), ids=test_cases_ids)
def test_invalid(test_configuration, test_metadata, set_fortishield_configuration, configure_local_internal_options,
                 truncate_monitored_files, daemons_handler, wait_for_github_start):
    '''
    description: Check if the 'github' module detects invalid configurations. For this purpose, the test
                 will configure that module using invalid configuration settings with different attributes.
                 Finally, it will verify that error events are generated indicating the source of the errors.

    fortishield_min_version: 4.3.0

    tier: 0

    parameters:
        - test_configuration:
            type: data
            brief: Configuration used in the test.
        - test_metadata:
            type: data
            brief: Configuration cases.
        - set_fortishield_configuration:
            type: fixture
            brief: Configure a custom environment for testing.
        - configure_local_internal_options:
            type: fixture
            brief: Set internal configuration for testing.
        - truncate_monitored_files:
            type: fixture
            brief: Reset the 'ossec.log' file and start a new monitor.
        - daemons_handler:
            type: fixture
            brief: Manages daemons to reset Fortishield.
        - wait_for_github_start:
            type: fixture
            brief: Checks integration start message does not appear.

    assertions:
        - Verify that the 'github' module generates error events when invalid configurations are used.

    input_description: A configuration template (github_integration) is contained in an external YAML file
                       (fortishield_conf.yaml). That template is combined with different test cases defined in
                       the module. Those include configuration settings for the 'github' module.

    expected_output:
        - r'wm_github_read(): ERROR.* Invalid content for tag .*'
        - r'wm_github_read(): ERROR.* Empty content for tag .*'

    tags:
        - invalid_settings
    '''

    fortishield_log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)
    fortishield_log_monitor.start(callback=callbacks.generate_callback(patterns.MODULESD_CONFIGURATION_ERROR, {
                              'error_type': str(test_metadata['error_type']),
                              'tag': str(test_metadata['event_monitor']),
                              'integration': str(test_metadata['module']),
                          }))

    assert (fortishield_log_monitor.callback_result != None), f'Error invalid configuration event not detected'