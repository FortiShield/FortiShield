# Copyright (C) 2015, Fortishield Inc.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License (version 2) as published by the FSF - Free Software
# Foundation.

$VERSION = Get-Content src/VERSION
[version]$VERSION = $VERSION -replace '[v]',''
$MAJOR=$VERSION.Major
$MINOR=$VERSION.Minor
$SHA= git rev-parse --short $args[0]

$TEST_ARRAY=@( 
              @("FORTISHIELD_MANAGER ", "1.1.1.1", "<address>", "</address>"), 
              @("FORTISHIELD_MANAGER_PORT ", "7777", "<port>", "</port>"),
              @("FORTISHIELD_PROTOCOL ", "udp", "<protocol>", "</protocol>"),
              @("FORTISHIELD_REGISTRATION_SERVER ", "2.2.2.2", "<manager_address>", "</manager_address>"),
              @("FORTISHIELD_REGISTRATION_PORT ", "8888", "<port>", "</port>"),
              @("FORTISHIELD_REGISTRATION_PASSWORD ", "password", "<password>", "</password>"),
              @("FORTISHIELD_KEEP_ALIVE_INTERVAL ", "10", "<notify_time>", "</notify_time>"),
              @("FORTISHIELD_TIME_RECONNECT ", "10", "<time-reconnect>", "</time-reconnect>"),
              @("FORTISHIELD_REGISTRATION_CA ", "/var/ossec/etc/testsslmanager.cert", "<server_ca_path>", "</server_ca_path>"),
              @("FORTISHIELD_REGISTRATION_CERTIFICATE ", "/var/ossec/etc/testsslmanager.cert", "<agent_certificate_path>", "</agent_certificate_path>"),
              @("FORTISHIELD_REGISTRATION_KEY ", "/var/ossec/etc/testsslmanager.key", "<agent_key_path>", "</agent_key_path>"),
              @("FORTISHIELD_AGENT_NAME ", "test-agent", "<agent_name>", "</agent_name>"),
              @("FORTISHIELD_AGENT_GROUP ", "test-group", "<groups>", "</groups>"),
              @("ENROLLMENT_DELAY ", "10", "<delay_after_enrollment>", "</delay_after_enrollment>")
)

function install_fortishield($vars)
{

    Write-Output "Testing the following variables $vars"
    Start-Process  C:\Windows\System32\msiexec.exe -ArgumentList  "/i fortishield-agent-$VERSION-0.commit$SHA.msi /qn $vars" -wait
    
}

function remove_fortishield
{

    Start-Process  C:\Windows\System32\msiexec.exe -ArgumentList "/x fortishield-agent-$VERSION-commit$SHA.msi /qn" -wait

}

function test($vars)
{

  For ($i=0; $i -lt $TEST_ARRAY.Length; $i++) {
    if($vars.Contains($TEST_ARRAY[$i][0])) {
      if ( ($TEST_ARRAY[$i][0] -eq "FORTISHIELD_MANAGER ") -OR ($TEST_ARRAY[$i][0] -eq "FORTISHIELD_PROTOCOL ") ) {
        $LIST = $TEST_ARRAY[$i][1].split(",")
        For ($j=0; $j -lt $LIST.Length; $j++) {
          $SEL = Select-String -Path 'C:\Program Files (x86)\ossec-agent\ossec.conf' -Pattern "$($TEST_ARRAY[$i][2])$($LIST[$j])$($TEST_ARRAY[$i][3])"
          if($SEL -ne $null) {
            Write-Output "The variable $($TEST_ARRAY[$i][0]) is set correctly"
          }
          if($SEL -eq $null) {
            Write-Output "The variable $($TEST_ARRAY[$i][0]) is not set correctly"
            exit 1
          }
        }
      }
      ElseIf ( ($TEST_ARRAY[$i][0] -eq "FORTISHIELD_REGISTRATION_PASSWORD ") ) {
        if (Test-Path 'C:\Program Files (x86)\ossec-agent\authd.pass'){
          $SEL = Select-String -Path 'C:\Program Files (x86)\ossec-agent\authd.pass' -Pattern "$($TEST_ARRAY[$i][1])"
          if($SEL -ne $null) {
            Write-Output "The variable $($TEST_ARRAY[$i][0]) is set correctly"
          }
          if($SEL -eq $null) {
            Write-Output "The variable $($TEST_ARRAY[$i][0]) is not set correctly"
            exit 1
          }
        }
        else
        {
          Write-Output "FORTISHIELD_REGISTRATION_PASSWORD is not correct"
          exit 1
        }
      }
      Else {
        $SEL = Select-String -Path 'C:\Program Files (x86)\ossec-agent\ossec.conf' -Pattern "$($TEST_ARRAY[$i][2])$($TEST_ARRAY[$i][1])$($TEST_ARRAY[$i][3])"
        if($SEL -ne $null) {
          Write-Output "The variable $($TEST_ARRAY[$i][0]) is set correctly"
        }
        if($SEL -eq $null) {
          Write-Output "The variable $($TEST_ARRAY[$i][0]) is not set correctly"
          exit 1
        }
      }
    }
  }

}

Write-Output "Download package: https://s3.us-west-1.amazonaws.com/fortishield.github.io/packages-dev/warehouse/pullrequests/$MAJOR.$MINOR/windows/fortishield-agent-$VERSION-0.commit$SHA.msi"
Invoke-WebRequest -Uri "https://s3.us-west-1.amazonaws.com/fortishield.github.io/packages-dev/warehouse/pullrequests/$MAJOR.$MINOR/windows/fortishield-agent-$VERSION-0.commit$SHA.msi" -OutFile "fortishield-agent-$VERSION-0.commit$SHA.msi"

install_fortishield "FORTISHIELD_MANAGER=1.1.1.1 FORTISHIELD_MANAGER_PORT=7777 FORTISHIELD_PROTOCOL=udp FORTISHIELD_REGISTRATION_SERVER=2.2.2.2 FORTISHIELD_REGISTRATION_PORT=8888 FORTISHIELD_REGISTRATION_PASSWORD=password FORTISHIELD_KEEP_ALIVE_INTERVAL=10 FORTISHIELD_TIME_RECONNECT=10 FORTISHIELD_REGISTRATION_CA=/var/ossec/etc/testsslmanager.cert FORTISHIELD_REGISTRATION_CERTIFICATE=/var/ossec/etc/testsslmanager.cert FORTISHIELD_REGISTRATION_KEY=/var/ossec/etc/testsslmanager.key FORTISHIELD_AGENT_NAME=test-agent FORTISHIELD_AGENT_GROUP=test-group ENROLLMENT_DELAY=10" 
test "FORTISHIELD_MANAGER FORTISHIELD_MANAGER_PORT FORTISHIELD_PROTOCOL FORTISHIELD_REGISTRATION_SERVER FORTISHIELD_REGISTRATION_PORT FORTISHIELD_REGISTRATION_PASSWORD FORTISHIELD_KEEP_ALIVE_INTERVAL FORTISHIELD_TIME_RECONNECT FORTISHIELD_REGISTRATION_CA FORTISHIELD_REGISTRATION_CERTIFICATE FORTISHIELD_REGISTRATION_KEY FORTISHIELD_AGENT_NAME FORTISHIELD_AGENT_GROUP ENROLLMENT_DELAY " 
remove_fortishield

install_fortishield "FORTISHIELD_MANAGER=1.1.1.1"
test "FORTISHIELD_MANAGER "
remove_fortishield

install_fortishield "FORTISHIELD_MANAGER_PORT=7777"
test "FORTISHIELD_MANAGER_PORT "
remove_fortishield

install_fortishield "FORTISHIELD_PROTOCOL=udp"
test "FORTISHIELD_PROTOCOL "
remove_fortishield

install_fortishield "FORTISHIELD_REGISTRATION_SERVER=2.2.2.2"
test "FORTISHIELD_REGISTRATION_SERVER "
remove_fortishield

install_fortishield "FORTISHIELD_REGISTRATION_PORT=8888"
test "FORTISHIELD_REGISTRATION_PORT "
remove_fortishield

install_fortishield "FORTISHIELD_REGISTRATION_PASSWORD=password"
test "FORTISHIELD_REGISTRATION_PASSWORD "
remove_fortishield

install_fortishield "FORTISHIELD_KEEP_ALIVE_INTERVAL=10"
test "FORTISHIELD_KEEP_ALIVE_INTERVAL "
remove_fortishield

install_fortishield "FORTISHIELD_TIME_RECONNECT=10"
test "FORTISHIELD_TIME_RECONNECT "
remove_fortishield

install_fortishield "FORTISHIELD_REGISTRATION_CA=/var/ossec/etc/testsslmanager.cert"
test "FORTISHIELD_REGISTRATION_CA "
remove_fortishield

install_fortishield "FORTISHIELD_REGISTRATION_CERTIFICATE=/var/ossec/etc/testsslmanager.cert"
test "FORTISHIELD_REGISTRATION_CERTIFICATE "
remove_fortishield

install_fortishield "FORTISHIELD_REGISTRATION_KEY=/var/ossec/etc/testsslmanager.key"
test "FORTISHIELD_REGISTRATION_KEY "
remove_fortishield

install_fortishield "FORTISHIELD_AGENT_NAME=test-agent"
test "FORTISHIELD_AGENT_NAME "
remove_fortishield

install_fortishield "FORTISHIELD_AGENT_GROUP=test-group"
test "FORTISHIELD_AGENT_GROUP "
remove_fortishield

install_fortishield "ENROLLMENT_DELAY=10"
test "ENROLLMENT_DELAY "
remove_fortishield
