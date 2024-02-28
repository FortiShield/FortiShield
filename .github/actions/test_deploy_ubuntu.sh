#!/bin/bash

# Copyright (C) 2015, Fortishield Inc.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License (version 2) as published by the FSF - Free Software
# Foundation.

# Global variables
VERSION="$(sed 's/v//' src/VERSION)"
MAJOR=$(echo "${VERSION}" | cut -dv -f2 | cut -d. -f1)
MINOR=$(echo "${VERSION}" | cut -d. -f2)
SHA="$(git rev-parse --short=7 "$1")"

conf_path="/var/ossec/etc/ossec.conf"

VARS=( "FORTISHIELD_MANAGER" "FORTISHIELD_MANAGER_PORT" "FORTISHIELD_PROTOCOL" "FORTISHIELD_REGISTRATION_SERVER" "FORTISHIELD_REGISTRATION_PORT" "FORTISHIELD_REGISTRATION_PASSWORD" "FORTISHIELD_KEEP_ALIVE_INTERVAL" "FORTISHIELD_TIME_RECONNECT" "FORTISHIELD_REGISTRATION_CA" "FORTISHIELD_REGISTRATION_CERTIFICATE" "FORTISHIELD_REGISTRATION_KEY" "FORTISHIELD_AGENT_NAME" "FORTISHIELD_AGENT_GROUP" "ENROLLMENT_DELAY" )
VALUES=( "1.1.1.1" "7777" "udp" "2.2.2.2" "8888" "password" "10" "10" "/var/ossec/etc/testsslmanager.cert" "/var/ossec/etc/testsslmanager.cert" "/var/ossec/etc/testsslmanager.key" "test-agent" "test-group" "10" )
TAGS1=( "<address>" "<port>" "<protocol>" "<manager_address>" "<port>" "<password>" "<notify_time>" "<time-reconnect>" "<server_ca_path>" "<agent_certificate_path>" "<agent_key_path>" "<agent_name>" "<groups>" "<delay_after_enrollment>" )
TAGS2=( "</address>" "</port>" "</protocol>" "</manager_address>" "</port>" "</password>" "</notify_time>" "</time-reconnect>" "</server_ca_path>" "</agent_certificate_path>" "</agent_key_path>" "</agent_name>" "</groups>" "</delay_after_enrollment>" )
FORTISHIELD_REGISTRATION_PASSWORD_PATH="/var/ossec/etc/authd.pass"

function install_wazuh(){

  echo "Testing the following variables $*"
  eval "${*} apt install -y ./wazuh-agent_${VERSION}-0.commit${SHA}_amd64.deb > /dev/null 2>&1"
  
}

function remove_wazuh () {

  apt purge -y wazuh-agent > /dev/null 2>&1

}

function test() {

  for i in "${!VARS[@]}"; do
    if ( echo "${@}" | grep -q -w "${VARS[i]}" ); then
      if [ "${VARS[i]}" == "FORTISHIELD_MANAGER" ] || [ "${VARS[i]}" == "FORTISHIELD_PROTOCOL" ]; then
        LIST=( "${VALUES[i]//,/ }" )
        for j in "${!LIST[@]}"; do
          if ( grep -q "${TAGS1[i]}${LIST[j]}${TAGS2[i]}" "${conf_path}" ); then
            echo "The variable ${VARS[i]} is set correctly"
          else
            echo "The variable ${VARS[i]} is not set correctly"
            exit 1
          fi
        done
      elif [ "${VARS[i]}" == "FORTISHIELD_REGISTRATION_PASSWORD" ]; then
        if ( grep -q "${VALUES[i]}" "${FORTISHIELD_REGISTRATION_PASSWORD_PATH}" ); then
          echo "The variable ${VARS[i]} is set correctly"
        else
          echo "The variable ${VARS[i]} is not set correctly"
          exit 1
        fi
      else
        if ( grep -q "${TAGS1[i]}${VALUES[i]}${TAGS2[i]}" "${conf_path}" ); then
          echo "The variable ${VARS[i]} is set correctly"
        else
          echo "The variable ${VARS[i]} is not set correctly"
          exit 1
        fi
      fi
    fi
  done

}

echo "Download package: https://s3.us-west-1.amazonaws.com/packages-dev.wazuh.com/warehouse/pullrequests/${MAJOR}.${MINOR}/deb/var/wazuh-agent_${VERSION}-0.commit${SHA}_amd64.deb"
wget "https://s3.us-west-1.amazonaws.com/packages-dev.wazuh.com/warehouse/pullrequests/${MAJOR}.${MINOR}/deb/var/wazuh-agent_${VERSION}-0.commit${SHA}_amd64.deb" > /dev/null 2>&1

install_wazuh "FORTISHIELD_MANAGER=1.1.1.1 FORTISHIELD_MANAGER_PORT=7777 FORTISHIELD_PROTOCOL=udp FORTISHIELD_REGISTRATION_SERVER=2.2.2.2 FORTISHIELD_REGISTRATION_PORT=8888 FORTISHIELD_REGISTRATION_PASSWORD=password FORTISHIELD_KEEP_ALIVE_INTERVAL=10 FORTISHIELD_TIME_RECONNECT=10 FORTISHIELD_REGISTRATION_CA=/var/ossec/etc/testsslmanager.cert FORTISHIELD_REGISTRATION_CERTIFICATE=/var/ossec/etc/testsslmanager.cert FORTISHIELD_REGISTRATION_KEY=/var/ossec/etc/testsslmanager.key FORTISHIELD_AGENT_NAME=test-agent FORTISHIELD_AGENT_GROUP=test-group ENROLLMENT_DELAY=10" 
test "FORTISHIELD_MANAGER FORTISHIELD_MANAGER_PORT FORTISHIELD_PROTOCOL FORTISHIELD_REGISTRATION_SERVER FORTISHIELD_REGISTRATION_PORT FORTISHIELD_REGISTRATION_PASSWORD FORTISHIELD_KEEP_ALIVE_INTERVAL FORTISHIELD_TIME_RECONNECT FORTISHIELD_REGISTRATION_CA FORTISHIELD_REGISTRATION_CERTIFICATE FORTISHIELD_REGISTRATION_KEY FORTISHIELD_AGENT_NAME FORTISHIELD_AGENT_GROUP ENROLLMENT_DELAY" 
remove_wazuh

install_wazuh "FORTISHIELD_MANAGER=1.1.1.1"
test "FORTISHIELD_MANAGER"
remove_wazuh

install_wazuh "FORTISHIELD_MANAGER_PORT=7777"
test "FORTISHIELD_MANAGER_PORT"
remove_wazuh

install_wazuh "FORTISHIELD_PROTOCOL=udp"
test "FORTISHIELD_PROTOCOL"
remove_wazuh

install_wazuh "FORTISHIELD_REGISTRATION_SERVER=2.2.2.2"
test "FORTISHIELD_REGISTRATION_SERVER"
remove_wazuh

install_wazuh "FORTISHIELD_REGISTRATION_PORT=8888"
test "FORTISHIELD_REGISTRATION_PORT"
remove_wazuh

install_wazuh "FORTISHIELD_REGISTRATION_PASSWORD=password"
test "FORTISHIELD_REGISTRATION_PASSWORD"
remove_wazuh

install_wazuh "FORTISHIELD_KEEP_ALIVE_INTERVAL=10"
test "FORTISHIELD_KEEP_ALIVE_INTERVAL"
remove_wazuh

install_wazuh "FORTISHIELD_TIME_RECONNECT=10"
test "FORTISHIELD_TIME_RECONNECT"
remove_wazuh

install_wazuh "FORTISHIELD_REGISTRATION_CA=/var/ossec/etc/testsslmanager.cert"
test "FORTISHIELD_REGISTRATION_CA"
remove_wazuh

install_wazuh "FORTISHIELD_REGISTRATION_CERTIFICATE=/var/ossec/etc/testsslmanager.cert"
test "FORTISHIELD_REGISTRATION_CERTIFICATE"
remove_wazuh

install_wazuh "FORTISHIELD_REGISTRATION_KEY=/var/ossec/etc/testsslmanager.key"
test "FORTISHIELD_REGISTRATION_KEY"
remove_wazuh

install_wazuh "FORTISHIELD_AGENT_NAME=test-agent"
test "FORTISHIELD_AGENT_NAME"
remove_wazuh

install_wazuh "FORTISHIELD_AGENT_GROUP=test-group"
test "FORTISHIELD_AGENT_GROUP"
remove_wazuh

install_wazuh "ENROLLMENT_DELAY=10"
test "ENROLLMENT_DELAY"
remove_wazuh
