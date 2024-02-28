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

suite: invalid_socket_input

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
from struct import pack

from fortishield_testing.constants.paths.sockets import LOGTEST_SOCKET_PATH
from fortishield_testing.constants.daemons import ANALYSISD_DAEMON, FORTISHIELD_DB_DAEMON
from fortishield_testing.utils import configuration

from . import TEST_CASES_FOLDER_PATH

# Marks
pytestmark = [pytest.mark.linux, pytest.mark.tier(level=0), pytest.mark.server]

# Configuration
t_cases_path = Path(TEST_CASES_FOLDER_PATH, 'cases_invalid_socket_input.yaml')
t_config_parameters, t_config_metadata, t_case_ids = configuration.get_test_cases_data(t_cases_path)

# Variables
receiver_sockets_params = [(LOGTEST_SOCKET_PATH, 'AF_UNIX', 'TCP')]
receiver_sockets = None  # Set in the fixtures

# Test daemons to restart.
daemons_handler_configuration = {'daemons': [ANALYSISD_DAEMON, FORTISHIELD_DB_DAEMON]}


# Tests
@pytest.mark.parametrize('test_metadata', t_config_metadata, ids=t_case_ids)
def test_invalid_socket_input(test_metadata, daemons_handler_module, wait_for_logtest_startup, connect_to_sockets):
    '''
    description: Check if `fortishield-logtest` correctly detects and handles errors when sending a message through
                 the socket to `fortishield-analysisd`. To do this, it sends the inputs through a socket(differentiating by
                 oversized messages), receives and decodes the message. Then, that message is compared with the test
                 case output.

    fortishield_min_version: 4.2.0

    tier: 0

    parameters:
        - daemons_handler_module:
            type: fixture
            brief: Fortishield logtests daemons handler.
        - wait_for_logtest_startup:
            type: fixture
            brief: Wait until logtest has begun.
        - connect_to_sockets:
            type: fixture
            brief: Function scope version of 'connect_to_sockets' which connects to the specified sockets for the test.
        - test_metadata:
            type: list
            brief: List of metadata values. (dicts with input, output and stage keys)

    assertions:
        - Verify that the communication through the sockets works well by verifying that all the test cases produce
          the right output.
        - Verify that oversized messages log an error.

    input_description: Some test cases are defined in the module. These include some input configurations stored in
                       the 'invalid_socket_input.yaml'.

    expected_output:
        - r'Failed test case stage <test_case_index>: .*'

    tags:
        - errors
        - analysisd
    '''
    if test_metadata["stage"] != 'Oversize message':
        receiver_sockets[0].send(test_metadata['input'], size=True)
    else:
        logtest_max_req_size = 2 ** 16
        oversize_header = pack("<I", logtest_max_req_size)
        receiver_sockets[0].send(test_metadata['input'].format(oversize_header))

    result = receiver_sockets[0].receive(size=True).rstrip(b'\x00').decode()
    assert test_metadata['output'] == result, 'Failed test case stage {}'.format(test_metadata['stage'])
