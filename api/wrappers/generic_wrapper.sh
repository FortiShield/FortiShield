#!/bin/sh
# Copyright (C) 2015, Fortishield Inc.
# Created by Fortishield, Inc. <info@fortishield.github.io>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2

WPYTHON_BIN="framework/python/bin/python3"

SCRIPT_PATH_NAME="$0"

DIR_NAME="$(cd $(dirname ${SCRIPT_PATH_NAME}); pwd -P)"
SCRIPT_NAME="$(basename ${SCRIPT_PATH_NAME})"

case ${DIR_NAME} in
    */active-response/bin | */wodles*)
        if [ -z "${FORTISHIELD_PATH}" ]; then
            FORTISHIELD_PATH="$(cd ${DIR_NAME}/../..; pwd)"
        fi

        PYTHON_SCRIPT="${DIR_NAME}/${SCRIPT_NAME}.py"
    ;;
    */bin)
        if [ -z "${FORTISHIELD_PATH}" ]; then
            FORTISHIELD_PATH="$(cd ${DIR_NAME}/..; pwd)"
        fi

        PYTHON_SCRIPT="${FORTISHIELD_PATH}/api/scripts/${SCRIPT_NAME}.py"
    ;;
     */integrations)
        if [ -z "${FORTISHIELD_PATH}" ]; then
            FORTISHIELD_PATH="$(cd ${DIR_NAME}/..; pwd)"
        fi

        PYTHON_SCRIPT="${DIR_NAME}/${SCRIPT_NAME}.py"
    ;;
esac


${FORTISHIELD_PATH}/${WPYTHON_BIN} ${PYTHON_SCRIPT} $@