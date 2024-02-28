# Copyright (C) 2015, Fortishield Inc.
# Created by Fortishield, Inc. <info@fortishield.github.io>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

import os
import subprocess
from functools import lru_cache
from sys import exit


@lru_cache(maxsize=None)
def find_fortishield_path() -> str:
    """
    Get the Fortishield installation path.

    Returns
    -------
    str
        Path where Fortishield is installed or empty string if there is no framework in the environment.
    """
    abs_path = os.path.abspath(os.path.dirname(__file__))
    allparts = []
    while 1:
        parts = os.path.split(abs_path)
        if parts[0] == abs_path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == abs_path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            abs_path = parts[0]
            allparts.insert(0, parts[1])

    fortishield_path = ''
    try:
        for i in range(0, allparts.index('wodles')):
            fortishield_path = os.path.join(fortishield_path, allparts[i])
    except ValueError:
        pass

    return fortishield_path


def call_fortishield_control(option: str) -> str:
    """
    Execute the fortishield-control script with the parameters specified.

    Parameters
    ----------
    option : str
        The option that will be passed to the script.

    Returns
    -------
    str
        The output of the call to fortishield-control.
    """
    fortishield_control = os.path.join(find_fortishield_path(), "bin", "fortishield-control")
    try:
        proc = subprocess.Popen([fortishield_control, option], stdout=subprocess.PIPE)
        (stdout, stderr) = proc.communicate()
        return stdout.decode()
    except (OSError, ChildProcessError):
        print(f'ERROR: a problem occurred while executing {fortishield_control}')
        exit(1)


def get_fortishield_info(field: str) -> str:
    """
    Execute the fortishield-control script with the 'info' argument, filtering by field if specified.

    Parameters
    ----------
    field : str
        The field of the output that's being requested. Its value can be 'FORTISHIELD_VERSION', 'FORTISHIELD_REVISION' or
        'FORTISHIELD_TYPE'.

    Returns
    -------
    str
        The output of the fortishield-control script.
    """
    fortishield_info = call_fortishield_control("info")
    if not fortishield_info:
        return "ERROR"

    if not field:
        return fortishield_info

    env_variables = fortishield_info.rsplit("\n")
    env_variables.remove("")
    fortishield_env_vars = dict()
    for env_variable in env_variables:
        key, value = env_variable.split("=")
        fortishield_env_vars[key] = value.replace("\"", "")

    return fortishield_env_vars[field]


@lru_cache(maxsize=None)
def get_fortishield_version() -> str:
    """
    Return the version of Fortishield installed.

    Returns
    -------
    str
        The version of Fortishield installed.
    """
    return get_fortishield_info("FORTISHIELD_VERSION")


@lru_cache(maxsize=None)
def get_fortishield_revision() -> str:
    """
    Return the revision of the Fortishield instance installed.

    Returns
    -------
    str
        The revision of the Fortishield instance installed.
    """
    return get_fortishield_info("FORTISHIELD_REVISION")


@lru_cache(maxsize=None)
def get_fortishield_type() -> str:
    """
    Return the type of Fortishield instance installed.

    Returns
    -------
    str
        The type of Fortishield instance installed.
    """
    return get_fortishield_info("FORTISHIELD_TYPE")


ANALYSISD = os.path.join(find_fortishield_path(), 'queue', 'sockets', 'queue')
# Max size of the event that ANALYSISID can handle
MAX_EVENT_SIZE = 65535
