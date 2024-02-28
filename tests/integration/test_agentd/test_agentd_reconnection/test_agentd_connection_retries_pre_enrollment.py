'''
copyright: Copyright (C) 2015-2022, Fortishield Inc.

           Created by Fortishield, Inc. <info@fortishield.github.io>.

           This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

type: integration

brief: The 'fortishield-agentd' program is the client-side daemon that communicates with the server.
       The objective is to check that, with different states in the 'clients.keys' file,
       the agent successfully enrolls after losing connection with the 'fortishield-remoted' daemon.
       The fortishield-remoted program is the server side daemon that communicates with the agents.

components:
    - agentd

targets:
    - agent

daemons:
    - fortishield-agentd
    - fortishield-authd
    - fortishield-remoted

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
    - https://documentation.fortishield.github.io/current/user-manual/registering/index.html

tags:
    - enrollment
'''
import pytest
from pathlib import Path
import sys

from fortishield_testing.constants.platforms import WINDOWS
from fortishield_testing.modules.agentd.configuration import AGENTD_DEBUG, AGENTD_WINDOWS_DEBUG, AGENTD_TIMEOUT
from fortishield_testing.modules.agentd.patterns import *
from fortishield_testing.tools.simulators.remoted_simulator import RemotedSimulator
from fortishield_testing.utils.configuration import get_test_cases_data, load_configuration_template

from . import CONFIGS_PATH, TEST_CASES_PATH
from utils import wait_keepalive

# Marks
pytestmark = pytest.mark.tier(level=0)

# Configuration and cases data.
configs_path = Path(CONFIGS_PATH, 'fortishield_conf.yaml')
cases_path = Path(TEST_CASES_PATH, 'cases_reconnection_protocol.yaml')

# Test configurations.
config_parameters, test_metadata, test_cases_ids = get_test_cases_data(cases_path)
test_configuration = load_configuration_template(configs_path, config_parameters, test_metadata)

if sys.platform == WINDOWS:
    local_internal_options = {AGENTD_WINDOWS_DEBUG: '2'}
else:
    local_internal_options = {AGENTD_DEBUG: '2'}
local_internal_options.update({AGENTD_TIMEOUT: '5'})

daemons_handler_configuration = {'all_daemons': True}

# Tests
@pytest.mark.parametrize('test_configuration, test_metadata', zip(test_configuration, test_metadata), ids=test_cases_ids)
def test_agentd_connection_retries_pre_enrollment(test_metadata, set_fortishield_configuration, configure_local_internal_options,
                                                  truncate_monitored_files, clean_keys, add_keys, daemons_handler):
    '''
    description: Check how the agent behaves when the 'fortishield-remoted' daemon is not available
                 and performs multiple connection attempts to it. For this, the agent starts
                 with keys but the 'fortishield-remoted' daemon is not available for several seconds,
                 then the agent performs multiple connection retries before requesting a new enrollment.

                 This test covers and check the scenario of Agent starting with keys but Remoted is not
                 reachable during some seconds and multiple connection retries are required prior to
                 requesting a new enrollment

    fortishield_min_version: 4.2.0

    tier: 0

    parameters:
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
        - clean_keys:
            type: fixture
            brief: Cleans keys file content
        - add_keys:
            type: fixture
            brief: Adds keys to keys file
        - daemons_handler:
            type: fixture
            brief: Handler of Fortishield daemons.

    assertions:
        - Verify that the agent enrollment is successful.

    input_description: An external YAML file (fortishield_conf.yaml) includes configuration settings for the agent.
                       Two test cases are found in the test module and include parameters
                       for the environment setup using the TCP and UDP protocols.

    expected_output:
        - r'Sending keep alive'

    tags:
        - simulator
        - ssl
        - keys
    '''
    # Start RemotedSimulator
    remoted_server = RemotedSimulator(protocol = test_metadata['PROTOCOL'])
    remoted_server.start()

    # Start hearing logs
    wait_keepalive()

    # Reset simulator
    remoted_server.destroy()
