"""
 Copyright (C) 2015-2024, Fortishield Inc.
 Created by Fortishield, Inc. <info@fortishield.github.io>.
 This program is free software; you can redistribute it and/or modify it under the terms of GPLv2
"""

import pytest
import time

from pathlib import Path
from fortishield_testing.tools.simulators.agent_simulator import connect
from fortishield_testing.utils.configuration import get_test_cases_data, load_configuration_template
from fortishield_testing.modules.remoted.configuration import REMOTED_DEBUG
from fortishield_testing.constants.paths.logs import FORTISHIELD_LOG_PATH
from fortishield_testing.tools.monitors.file_monitor import FileMonitor
from fortishield_testing.utils.callbacks import generate_callback
from fortishield_testing.modules.remoted import patterns
from fortishield_testing.tools.monitors import queue_monitor
from fortishield_testing.utils.agent_groups import create_group, delete_group, add_agent_to_group

from . import CONFIGS_PATH, TEST_CASES_PATH


# Set pytest marks.
pytestmark = [pytest.mark.server, pytest.mark.tier(level=2)]

# Cases metadata and its ids.
cases_path = Path(TEST_CASES_PATH, 'cases_shared_configuration.yaml')
config_path = Path(CONFIGS_PATH, 'config_shared_configuration.yaml')
test_configuration, test_metadata, cases_ids = get_test_cases_data(cases_path)
test_configuration = load_configuration_template(config_path, test_configuration, test_metadata)

daemons_handler_configuration = {'all_daemons': True}

local_internal_options = {REMOTED_DEBUG: '2'}

def check_queue_monitor(agent, pattern):
    log_queue_monitor = queue_monitor.QueueMonitor(agent.rcv_msg_queue)
    log_queue_monitor.start(timeout=60, callback=generate_callback(regex=pattern))
    assert log_queue_monitor.callback_result


# Test function.
@pytest.mark.parametrize('test_configuration, test_metadata',  zip(test_configuration, test_metadata), ids=cases_ids)
def test_shared_configuration(test_configuration, test_metadata, configure_local_internal_options, truncate_monitored_files,
                            set_fortishield_configuration, daemons_handler, simulate_agents):

    '''
    description: Check if the manager pushes shared configuration to agents as expected.
                 For this purpose, the test will create an agent for each protocol within the module test cases. Then,
                 it will try to send the shared configuration to the agent and then, check if the configuration is
                 completely pushed.
                 For example, if Fortishield Manager sends new shared files from group shared folder when the merged.mg
                 checksum is received from an agent is different than the stored one.
                 As the test has nothing to do with shared configuration files, we removed those rootcheck txt files
                 from default agent group to reduce the time required by the test to make the checks.


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
            brief: Restart service once the test finishes stops the daemons.
        - simulate_agents
            type: fixture
            brief: create agents
        - set_fortishield_configuration:
            type: fixture
            brief: Apply changes to the ossec.conf configuration.
    '''

    agent = simulate_agents[0]

    sender, injector = connect(agent = agent, protocol = test_metadata['protocol'])

    fortishield_log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)

    # Send the start-up message
    sender.send_event(agent.startup_msg)

    fortishield_log_monitor.start(callback=generate_callback(regex=patterns.START_UP, replacement={"agent_name": agent.name, "agent_ip": '127.0.0.1'}))

    assert fortishield_log_monitor.callback_result


    sender.send_event(agent.keep_alive_event)

    time.sleep(5)

    for pattern in test_metadata['patterns']:
        check_queue_monitor(agent, pattern)


    sender.send_event(agent.keep_alive_event)

    # Check that push message doesn't appear again
    with pytest.raises(AssertionError): #assert not callback_result
        check_queue_monitor(agent, test_metadata['patterns'][0])
        raise ValueError("Same shared configuration pushed twice!")


    create_group('testing_group')
    add_agent_to_group('testing_group', agent.id)

    time.sleep(10)

    fortishield_log_monitor.start(callback=generate_callback(regex=patterns.MERGED_NEW_SHARED_END_SEND))
    assert fortishield_log_monitor.callback_result

    check_queue_monitor(agent, test_metadata['patterns'][0])

    delete_group('testing_group')
    injector.stop_receive()
