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

FORTISHIELD_MACOS_AGENT_DEPLOYMENT_VARS="/tmp/fortishield_envs"
conf_path="/Library/Ossec/etc/ossec.conf"

VARS=( "FORTISHIELD_MANAGER" "FORTISHIELD_MANAGER_PORT" "FORTISHIELD_PROTOCOL" "FORTISHIELD_REGISTRATION_SERVER" "FORTISHIELD_REGISTRATION_PORT" "FORTISHIELD_REGISTRATION_PASSWORD" "FORTISHIELD_KEEP_ALIVE_INTERVAL" "FORTISHIELD_TIME_RECONNECT" "FORTISHIELD_REGISTRATION_CA" "FORTISHIELD_REGISTRATION_CERTIFICATE" "FORTISHIELD_REGISTRATION_KEY" "FORTISHIELD_AGENT_NAME" "FORTISHIELD_AGENT_GROUP" "ENROLLMENT_DELAY" )
VALUES=( "1.1.1.1" "7777" "udp" "2.2.2.2" "8888" "password" "10" "10" "/Library/Ossec/etc/testsslmanager.cert" "/Library/Ossec/etc/testsslmanager.cert" "/Library/Ossec/etc/testsslmanager.key" "test-agent" "test-group" "10" )
TAGS1=( "<address>" "<port>" "<protocol>" "<manager_address>" "<port>" "<password>" "<notify_time>" "<time-reconnect>" "<server_ca_path>" "<agent_certificate_path>" "<agent_key_path>" "<agent_name>" "<groups>" "<delay_after_enrollment>" )
TAGS2=( "</address>" "</port>" "</protocol>" "</manager_address>" "</port>" "</password>" "</notify_time>" "</time-reconnect>" "</server_ca_path>" "</agent_certificate_path>" "</agent_key_path>" "</agent_name>" "</groups>" "</delay_after_enrollment>" )
FORTISHIELD_REGISTRATION_PASSWORD_PATH="/Library/Ossec/etc/authd.pass"

function install_fortishield(){

  echo "Testing the following variables $1"

  eval "echo \"$1\" > ${FORTISHIELD_MACOS_AGENT_DEPLOYMENT_VARS} && installer -pkg fortishield-agent-${VERSION}-0.commit${SHA}.pkg -target / > /dev/null 2>&1"
  
}

function remove_fortishield () {

  /bin/rm -r /Library/Ossec > /dev/null 2>&1
  /bin/launchctl unload /Library/LaunchDaemons/com.fortishield.agent.plist > /dev/null 2>&1
  /bin/rm -f /Library/LaunchDaemons/com.fortishield.agent.plist > /dev/null 2>&1
  /bin/rm -rf /Library/StartupItems/FORTISHIELD > /dev/null 2>&1
  /usr/bin/dscl . -delete "/Users/fortishield" > /dev/null 2>&1
  /usr/bin/dscl . -delete "/Groups/fortishield" > /dev/null 2>&1
  /usr/sbin/pkgutil --forget com.fortishield.pkg.fortishield-agent > /dev/null 2>&1

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

echo "Download package https://s3.us-west-1.amazonaws.com/packages-dev.fortishield.com/warehouse/pullrequests/${MAJOR}.${MINOR}/macos/fortishield-agent-${VERSION}-0.commit${SHA}.pkg"
wget "https://s3.us-west-1.amazonaws.com/packages-dev.fortishield.com/warehouse/pullrequests/${MAJOR}.${MINOR}/macos/fortishield-agent-${VERSION}-0.commit${SHA}.pkg" > /dev/null 2>&1

install_fortishield "FORTISHIELD_MANAGER='1.1.1.1' && FORTISHIELD_MANAGER_PORT='7777' && FORTISHIELD_PROTOCOL='udp' && FORTISHIELD_REGISTRATION_SERVER='2.2.2.2' && FORTISHIELD_REGISTRATION_PORT='8888' && FORTISHIELD_REGISTRATION_PASSWORD='password' && FORTISHIELD_KEEP_ALIVE_INTERVAL='10' && FORTISHIELD_TIME_RECONNECT='10' && FORTISHIELD_REGISTRATION_CA='/Library/Ossec/etc/testsslmanager.cert' && FORTISHIELD_REGISTRATION_CERTIFICATE='/Library/Ossec/etc/testsslmanager.cert' && FORTISHIELD_REGISTRATION_KEY='/Library/Ossec/etc/testsslmanager.key' && FORTISHIELD_AGENT_NAME='test-agent' && FORTISHIELD_AGENT_GROUP='test-group' && ENROLLMENT_DELAY='10'" 
test "FORTISHIELD_MANAGER FORTISHIELD_MANAGER_PORT FORTISHIELD_PROTOCOL FORTISHIELD_REGISTRATION_SERVER FORTISHIELD_REGISTRATION_PORT FORTISHIELD_REGISTRATION_PASSWORD FORTISHIELD_KEEP_ALIVE_INTERVAL FORTISHIELD_TIME_RECONNECT FORTISHIELD_REGISTRATION_CA FORTISHIELD_REGISTRATION_CERTIFICATE FORTISHIELD_REGISTRATION_KEY FORTISHIELD_AGENT_NAME FORTISHIELD_AGENT_GROUP ENROLLMENT_DELAY" 
remove_fortishield

install_fortishield "FORTISHIELD_MANAGER='1.1.1.1'"
test "FORTISHIELD_MANAGER"
remove_fortishield

install_fortishield "FORTISHIELD_MANAGER_PORT='7777'"
test "FORTISHIELD_MANAGER_PORT"
remove_fortishield

install_fortishield "FORTISHIELD_PROTOCOL='udp'"
test "FORTISHIELD_PROTOCOL"
remove_fortishield

install_fortishield "FORTISHIELD_REGISTRATION_SERVER='2.2.2.2'"
test "FORTISHIELD_REGISTRATION_SERVER"
remove_fortishield

install_fortishield "FORTISHIELD_REGISTRATION_PORT='8888'"
test "FORTISHIELD_REGISTRATION_PORT"
remove_fortishield

install_fortishield "FORTISHIELD_REGISTRATION_PASSWORD='password'"
test "FORTISHIELD_REGISTRATION_PASSWORD"
remove_fortishield

install_fortishield "FORTISHIELD_KEEP_ALIVE_INTERVAL='10'"
test "FORTISHIELD_KEEP_ALIVE_INTERVAL"
remove_fortishield

install_fortishield "FORTISHIELD_TIME_RECONNECT='10'"
test "FORTISHIELD_TIME_RECONNECT"
remove_fortishield

install_fortishield "FORTISHIELD_REGISTRATION_CA='/Library/Ossec/etc/testsslmanager.cert'"
test "FORTISHIELD_REGISTRATION_CA"
remove_fortishield

install_fortishield "FORTISHIELD_REGISTRATION_CERTIFICATE='/Library/Ossec/etc/testsslmanager.cert'"
test "FORTISHIELD_REGISTRATION_CERTIFICATE"
remove_fortishield

install_fortishield "FORTISHIELD_REGISTRATION_KEY='/Library/Ossec/etc/testsslmanager.key'"
test "FORTISHIELD_REGISTRATION_KEY"
remove_fortishield

install_fortishield "FORTISHIELD_AGENT_NAME='test-agent'"
test "FORTISHIELD_AGENT_NAME"
remove_fortishield

install_fortishield "FORTISHIELD_AGENT_GROUP='test-group'"
test "FORTISHIELD_AGENT_GROUP"
remove_fortishield

install_fortishield "ENROLLMENT_DELAY='10'"
test "ENROLLMENT_DELAY"
remove_fortishield
