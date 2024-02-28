# Copyright (C) 2015-2023, Fortishield Inc.
# Created by Fortishield, Inc. <info@fortishield.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

import pytest

from fortishield_testing.constants.paths.logs import FORTISHIELD_LOG_PATH
from fortishield_testing.modules.modulesd import patterns
from fortishield_testing.tools.monitors.file_monitor import FileMonitor
from fortishield_testing.utils import callbacks
from fortishield_testing.utils.manage_agents import remove_agents
from fortishield_testing.utils.services import control_service
from fortishield_testing.tools.simulators.agent_simulator import create_agents


@pytest.fixture()
def wait_for_rootcheck_start():
    # Wait for module rootcheck starts
    fortishield_log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)
    fortishield_log_monitor.start(callback=callbacks.generate_callback(patterns.MODULESD_STARTED, {
                              'integration': 'rootcheck'
                          }))
    assert (fortishield_log_monitor.callback_result == None), f'Error invalid configuration event not detected'


@pytest.fixture(scope="function")
def simulate_agents(request):
    agents = []
    for _ in range(request.getfixturevalue("test_metadata")["agents_number"]):
       agent = create_agents(1, 'localhost')[0]

    yield agents
    # Delete simulated agents
    control_service('start')
    for agent in agents:
        remove_agents(agent.id,'manage_agents')
    control_service('stop')
