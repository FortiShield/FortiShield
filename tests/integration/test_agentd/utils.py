# Copyright (C) 2015-2021, Fortishield Inc.
# Created by Fortishield, Inc. <info@fortishield.github.io>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

from fortishield_testing.constants.paths.logs import FORTISHIELD_LOG_PATH
from fortishield_testing.modules.agentd.patterns import *
from fortishield_testing.tools.monitors.file_monitor import FileMonitor
from fortishield_testing.utils import callbacks


def wait_keepalive():
    """
        Watch ossec.log until "Sending keep alive" message is found
    """
    fortishield_log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)
    fortishield_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_SENDING_KEEP_ALIVE), timeout = 100)
    assert (fortishield_log_monitor.callback_result != None), f'Sending keep alive not found'


def wait_connect():
    """
        Watch ossec.log until received "Connected to the server" message is found
    """
    fortishield_log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)
    fortishield_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_CONNECTED_TO_SERVER))
    assert (fortishield_log_monitor.callback_result != None), f'Connected to the server message not found'


def wait_ack():
    """
        Watch ossec.log until "Received ack message" is found
    """
    fortishield_log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)
    fortishield_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_RECEIVED_ACK))
    assert (fortishield_log_monitor.callback_result != None), f'Received ack message not found'


def wait_state_update():
    """
        Watch ossec.log until "Updating state file" message is found
    """
    fortishield_log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)
    fortishield_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_UPDATING_STATE_FILE))
    assert (fortishield_log_monitor.callback_result != None), f'State file update not found'


def wait_enrollment():
    """
        Watch ossec.log until "Valid key received" message is found
    """
    fortishield_log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)
    fortishield_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_RECEIVED_VALID_KEY))
    assert (fortishield_log_monitor.callback_result != None), 'Agent never enrolled'


def wait_enrollment_try():
    """
        Watch ossec.log until "Requesting a key" message is found
    """
    fortishield_log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)
    fortishield_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_REQUESTING_KEY,{'IP':''}), timeout = 150)
    assert (fortishield_log_monitor.callback_result != None), f'Enrollment retry was not sent'


def wait_agent_notification(current_value):
    """
        Watch ossec.log until "Sending agent notification" message is found current_value times
    """
    fortishield_log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)
    fortishield_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_SENDING_AGENT_NOTIFICATION), accumulations = int(current_value))
    assert (fortishield_log_monitor.callback_result != None), f'Sending agent notification message not found'


def wait_server_rollback():
    """
        Watch ossec.log until "Unable to connect to any server" message is found'
    """
    fortishield_log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)
    fortishield_log_monitor.start(callback=callbacks.generate_callback(AGENTD_UNABLE_TO_CONNECT_TO_ANY), timeout = 120)
    assert (fortishield_log_monitor.callback_result != None), f'Unable to connect to any server message not found'


def check_module_stop():
    """
        Watch ossec.log until "Unable to access queue" message is not found
    """
    fortishield_log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)
    fortishield_log_monitor.start(callback=callbacks.generate_callback(AGENTD_MODULE_STOPPED))
    assert (fortishield_log_monitor.callback_result == None), f'Unable to access queue message found'


def check_connection_try():
    """
        Watch ossec.log until "Trying to connect to server" message is found
    """
    fortishield_log_monitor = FileMonitor(FORTISHIELD_LOG_PATH)
    matched_line = fortishield_log_monitor.start(only_new_events = True, callback=callbacks.generate_callback(AGENTD_TRYING_CONNECT,{'IP':'','PORT':''}), return_matched_line = True)
    assert (fortishield_log_monitor.callback_result != None), f'Trying to connect to server message not found'
    return matched_line
