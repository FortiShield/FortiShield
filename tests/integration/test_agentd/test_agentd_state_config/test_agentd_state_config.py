'''
copyright: Copyright (C) 2015-2022, Fortishield Inc.

           Created by Fortishield, Inc. <info@fortishield.com>.

           This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

type: integration

brief: The 'fortishield-agentd' program is the client-side daemon that communicates with the server.
       These tests will check if the configuration options related to the statistics file of
       the 'fortishield-agentd' daemon are working properly. The statistics files are documents that
       show real-time information about the Fortishield environment.

components:
    - agentd

targets:
    - agent

daemons:
    - fortishield-agentd

os_platform:
    - linux
    - windows

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
    - Windows 10
    - Windows Server 2019
    - Windows Server 2016

references:
    - https://documentation.fortishield.com/current/user-manual/reference/statistics-files/fortishield-agentd-state.html

tags:
    - stats_file
'''
import os
import pytest
from pathlib import Path
import sys
import time

from fortishield_testing.constants.daemons import AGENT_DAEMON
from fortishield_testing.constants.paths.logs import FORTISHIELD_LOG_PATH
from fortishield_testing.constants.paths.variables import AGENTD_STATE
from fortishield_testing.constants.platforms import WINDOWS
from fortishield_testing.modules.agentd.configuration import AGENTD_DEBUG, AGENTD_WINDOWS_DEBUG
from fortishield_testing.tools.monitors.file_monitor import FileMonitor
from fortishield_testing.utils.configuration import get_test_cases_data
from fortishield_testing.utils.configuration import load_configuration_template
from fortishield_testing.utils import callbacks
from fortishield_testing.utils.services import check_if_process_is_running

from . import CONFIGS_PATH, TEST_CASES_PATH

# Marks
pytestmark = pytest.mark.tier(level=0)

# Configuration and cases data.
configs_path = Path(CONFIGS_PATH, 'fortishield_conf.yaml')
cases_path = Path(TEST_CASES_PATH, 'fortishield_state_config_tests.yaml')

# Test configurations.
config_parameters, test_metadata, test_cases_ids = get_test_cases_data(cases_path)

test_configuration = load_configuration_template(configs_path, config_parameters, test_metadata)

if sys.platform == WINDOWS:
    local_internal_options = {AGENTD_WINDOWS_DEBUG: '2'}
else:
    local_internal_options = {AGENTD_DEBUG: '2'}

daemons_handler_configuration = {'all_daemons': True, 'ignore_errors': True}


@pytest.mark.parametrize('test_configuration, test_metadata', zip(test_configuration, test_metadata), ids=test_cases_ids)
def test_agentd_state_config(test_configuration, test_metadata, remove_state_file, set_fortishield_configuration, configure_local_internal_options,
                             truncate_monitored_files, daemons_handler):

    '''
    description: Check that the 'fortishield-agentd.state' statistics file is created
                 automatically and verify that it is updated at the set intervals.

    fortishield_min_version: 4.2.0

    tier: 0

    parameters:
        - test_configuration:
            type: data
            brief: Configuration used in the test.
        - test_metadata:
            type: data
            brief: Configuration cases.
        - remove_state_file:
            type: fixture
            brief: Removes fortishield-agentd.state file.
        - set_fortishield_configuration:
            type: fixture
            brief: Configure a custom environment for testing.
        - configure_local_internal_options:
            type: fixture
            brief: Set internal configuration for testing.
        - truncate_monitored_files:
            type: fixture
            brief: Reset the 'ossec.log' file and start a new monitor.

    assertions:
        - Verify that the 'fortishield-agentd.state' statistics file has been created.
        - Verify that the 'fortishield-agentd.state' statistics file is updated at the specified intervals.

    input_description: An external YAML file (fortishield_conf.yaml) includes configuration settings for the agent.
                       Different test cases that are contained in an external YAML file (fortishield_state_config_tests.yaml)
                       that includes the parameters and their expected responses.

    expected_output:
        - '.*Invalid definition for agent.state_interval.*'
        - '.*State file is disabled.*'
        - '.*State file updating thread started.*'
    '''

    if sys.platform != WINDOWS:
        time.sleep(1)
        assert (test_metadata['agentd_ends']is not check_if_process_is_running(AGENT_DAEMON))

    # Check if the test requires checking state file existence
    if test_metadata['state_file_exist']:
        time.sleep(int(test_metadata['local_internal_options']['agent.state_interval']))
    assert test_metadata['state_file_exist'] == os.path.exists(AGENTD_STATE)

    # Follow ossec.log to find desired messages by a callback
    fortishield_log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)
    fortishield_log_monitor.start(callback=callbacks.generate_callback(str(test_metadata['event_monitor'])))
    assert (fortishield_log_monitor.callback_result != None), f'Error invalid configuration event not detected'
