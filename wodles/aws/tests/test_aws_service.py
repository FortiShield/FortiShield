# Copyright (C) 2015, Fortishield Inc.
# Created by Fortishield, Inc. <info@fortishield.com>.
# This program is free software; you can redistribute it and/or modify it under the terms of GPLv2

import copy
import os
import sys
from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '.'))
import aws_utils as utils

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
import fortishield_integration

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'services'))
import aws_service

TEST_DATETIME = datetime.now()
TEST_DATETIME_STR = datetime.strftime(TEST_DATETIME, '%Y-%m-%dT%H:%M:%SZ')


@patch('fortishield_integration.FortishieldIntegration.get_sts_client')
@patch('fortishield_integration.FortishieldAWSDatabase.check_metadata_version')
@patch('fortishield_integration.sqlite3.connect')
@patch('fortishield_integration.FortishieldIntegration.get_client')
@patch('fortishield_integration.utils.find_fortishield_path', return_value=utils.TEST_FORTISHIELD_PATH)
@patch('fortishield_integration.utils.get_fortishield_version')
@patch('fortishield_integration.FortishieldIntegration.__init__', side_effect=fortishield_integration.FortishieldIntegration.__init__)
def test_aws_service_initializes_properly(mock_fortishield_integration, mock_version, mock_path, mock_client, mock_connect,
                                         mock_metadata, mock_sts):
    """Test if the instances of 'AWSService' are created properly."""
    mock_client = MagicMock()
    mock_sts.return_value = mock_client
    kwargs = utils.get_aws_service_parameters(db_table_name=utils.TEST_TABLE_NAME,
                                              service_name=utils.TEST_SERVICE_NAME, reparse=True,
                                              profile=utils.TEST_AWS_PROFILE, iam_role_arn=utils.TEST_IAM_ROLE_ARN,
                                              only_logs_after=utils.TEST_ONLY_LOGS_AFTER, region=utils.TEST_REGION,
                                              discard_field=utils.TEST_DISCARD_FIELD,
                                              discard_regex=utils.TEST_DISCARD_REGEX,
                                              sts_endpoint=utils.TEST_STS_ENDPOINT,
                                              service_endpoint=utils.TEST_SERVICE_ENDPOINT,
                                              iam_role_duration=utils.TEST_IAM_ROLE_DURATION)
    instance = aws_service.AWSService(**kwargs)
    mock_fortishield_integration.assert_called_with(instance, service_name=utils.TEST_SERVICE_NAME,
                                              profile=kwargs["profile"], iam_role_arn=kwargs["iam_role_arn"],
                                              region=kwargs["region"], discard_field=kwargs["discard_field"],
                                              discard_regex=kwargs["discard_regex"],
                                              sts_endpoint=kwargs["sts_endpoint"],
                                              service_endpoint=kwargs["service_endpoint"],
                                              iam_role_duration=kwargs["iam_role_duration"], external_id=None,
                                              skip_on_error=False)
    assert instance.service_name == utils.TEST_SERVICE_NAME
    assert instance.reparse
    assert instance.region == utils.TEST_REGION
    assert instance.only_logs_after == utils.TEST_ONLY_LOGS_AFTER
    mock_sts.assert_called_with(kwargs["profile"])
    mock_client.get_caller_identity.assert_called_once()


def test_aws_service_check_region():
    """Test 'check_region' function raises exception when an incorrect region is passed."""
    with pytest.raises(ValueError) as e:
        aws_service.AWSService.check_region('no-region')


@patch('fortishield_integration.FortishieldIntegration.get_sts_client')
@patch('fortishield_integration.FortishieldAWSDatabase.__init__')
@patch('fortishield_integration.FortishieldIntegration.__init__', side_effect=fortishield_integration.FortishieldIntegration.__init__)
def test_aws_service_get_last_log_date(mock_fortishield_integration, mock_fortishield_aws_database, mock_sts):
    """Test 'get_last_log_date' function returns a date with the expected format."""
    instance = utils.get_mocked_service(only_logs_after=utils.TEST_ONLY_LOGS_AFTER)
    assert instance.get_last_log_date() == utils.TEST_ONLY_LOGS_AFTER_WITH_FORMAT


@patch('fortishield_integration.FortishieldIntegration.get_sts_client')
@patch('fortishield_integration.FortishieldAWSDatabase.__init__')
@patch('fortishield_integration.FortishieldIntegration.__init__', side_effect=fortishield_integration.FortishieldIntegration.__init__)
def test_aws_service_format_message(mock_fortishield_integration, mock_fortishield_aws_database, mock_sts):
    """Test 'format_message' function updates the expected fields of an event."""
    input_msg = {'service': 'service_name', 'createdAt': TEST_DATETIME, 'updatedAt': TEST_DATETIME, 'key': 'value'}
    output_msg = {'source': 'service_name', 'createdAt': TEST_DATETIME_STR, 'updatedAt': TEST_DATETIME_STR,
                  'key': 'value'}
    instance = utils.get_mocked_service(only_logs_after=utils.TEST_ONLY_LOGS_AFTER)
    expected_msg = copy.deepcopy(aws_service.AWS_SERVICE_MSG_TEMPLATE)
    expected_msg['aws'] = output_msg
    assert instance.format_message(input_msg) == expected_msg