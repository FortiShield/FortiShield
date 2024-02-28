'''
copyright: Copyright (C) 2015-2022, Fortishield Inc.

           Created by Fortishield, Inc. <info@fortishield.github.io>.

           This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

type: integration

brief: These tests will check if the 'fortishield-authd' daemon correctly handles the enrollment requests,
       generating consistent responses to the requests received on its IP v4 network socket.
       The 'fortishield-authd' daemon can automatically add a Fortishield agent to a Fortishield manager and provide
       the key to the agent. It is used along with the 'agent-auth' application.

components:
    - authd

targets:
    - manager

daemons:
    - fortishield-authd
    - fortishield-db
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
    - https://documentation.fortishield.github.io/current/user-manual/reference/daemons/fortishield-authd.html
    - https://documentation.fortishield.github.io/current/user-manual/reference/tools/agent_groups.html

tags:
    - enrollment
'''
import time

import pytest
from pathlib import Path

from . import CONFIGURATIONS_FOLDER_PATH, TEST_CASES_FOLDER_PATH
from fortishield_testing.constants.ports import DEFAULT_SSL_REMOTE_ENROLLMENT_PORT
from fortishield_testing.constants.daemons import AUTHD_DAEMON, FORTISHIELD_DB_DAEMON, MODULES_DAEMON
from fortishield_testing.utils.configuration import get_test_cases_data, load_configuration_template

# Marks

pytestmark = [pytest.mark.linux, pytest.mark.tier(level=0), pytest.mark.server]

# Paths
test_configuration_path = Path(CONFIGURATIONS_FOLDER_PATH, 'config_authd_common.yaml')
test_cases_path = Path(TEST_CASES_FOLDER_PATH, 'cases_authd.yaml')

# Configurations
test_configuration, test_metadata, test_cases_ids = get_test_cases_data(test_cases_path)
test_configuration = load_configuration_template(test_configuration_path, test_configuration, test_metadata)

# Variables
log_monitor_paths = []

receiver_sockets_params = [(("localhost", DEFAULT_SSL_REMOTE_ENROLLMENT_PORT), 'AF_INET', 'SSL_TLSv1_2')]

monitored_sockets_params = [(MODULES_DAEMON, None, True), (FORTISHIELD_DB_DAEMON, None, True), (AUTHD_DAEMON, None, True)]

receiver_sockets, monitored_sockets = None, None  # Set in the fixtures

# Test daemons to restart.
daemons_handler_configuration = {'all_daemons': True}


# Tests
@pytest.mark.parametrize('test_configuration,test_metadata', zip(test_configuration, test_metadata), ids=test_cases_ids)
def test_ossec_auth_messages(test_configuration, test_metadata, set_fortishield_configuration,
                             truncate_monitored_files, configure_sockets_environment, daemons_handler,
                             wait_for_authd_startup, connect_to_sockets, set_up_groups):
    '''
    description:
        Checks if when the `fortishield-authd` daemon receives different types of enrollment requests,
        it responds appropriately to them. In this case, the enrollment requests are sent to
        an IP v4 network socket.

    fortishield_min_version:
        4.2.0

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
        - truncate_monitored_files:
            type: fixture
            brief: Truncate all the log files and json alerts files before and after the test execution.
        - set_up_groups:
            type: fixture
            brief: Create a testing group for agents and provide the test case list.
        - configure_sockets_environment:
            type: fixture
            brief: Configure environment for sockets and MITM.
        - daemons_handler:
            type: fixture
            brief: Restarts fortishield or a specific daemon passed.
        - wait_for_authd_startup:
            type: fixture
            brief: Waits until Authd is accepting connections.
        - connect_to_sockets:
            type: fixture
            brief: Module scope version of 'connect_to_sockets' fixture.


    assertions:
        - Verify that the response messages are consistent with the enrollment requests received.

    input_description:
        Different test cases are contained in an external `YAML` file (enroll_messages.yaml)
        that includes enrollment events and the expected output.

    expected_output:
        - Multiple values located in the `enroll_messages.yaml` file.

    tags:
        - keys
        - ssl
    '''
    test_case = test_metadata['stages']
    for stage in test_case:
        # Reopen socket (socket is closed by manager after sending message with client key)
        receiver_sockets[0].open()
        expected = stage['output']
        message = stage['input']
        receiver_sockets[0].send(message, size=False)
        timeout = time.time() + 10
        response = ''
        while response == '':
            response = receiver_sockets[0].receive().decode()
            if time.time() > timeout:
                assert response != '', 'The manager did not respond to the message sent.'
        assert response[:len(expected)] == expected, \
            'Failed test case {}: Response was: {} instead of: {}'.format(set_up_groups['name'], response, expected)
