# Copyright (C) 2015, Fortishield Inc.
# Created by Fortishield, Inc. <info@fortishield.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2

import sys
from unittest.mock import ANY, AsyncMock, MagicMock, call, patch

import pytest
from aiohttp import web_response

from api.controllers.test.utils import CustomAffectedItems

with patch('fortishield.common.fortishield_uid'):
    with patch('fortishield.common.fortishield_gid'):
        sys.modules['fortishield.rbac.orm'] = MagicMock()
        import fortishield.rbac.decorators
        from api.controllers.security_controller import (
            add_policy, add_role, add_rule, create_user,
            delete_security_config, delete_users, edit_run_as, get_policies,
            get_rbac_actions, get_rbac_resources, get_roles, get_rules,
            get_security_config, get_user_me, get_user_me_policies, get_users,
            login_user, logout_user, put_security_config, remove_policies,
            remove_role_policy, remove_role_rule, remove_roles, remove_rules,
            remove_user_role, revoke_all_tokens, run_as_login,
            security_revoke_tokens, set_role_policy, set_role_rule,
            set_user_role, update_policy, update_role, update_rule,
            update_user)
        from fortishield import security
        from fortishield.core.exception import FortishieldException, FortishieldPermissionError
        from fortishield.core.results import AffectedItemsFortishieldResult
        from fortishield.rbac import preprocessor
        from fortishield.tests.util import RBAC_bypasser

        fortishield.rbac.decorators.expose_resources = RBAC_bypasser
        del sys.modules['fortishield.rbac.orm']


@pytest.mark.asyncio
@pytest.mark.parametrize('raw', [True, False])
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
@patch('api.controllers.security_controller.generate_token', return_value='token')
async def test_login_user(mock_token, mock_exc, mock_dapi, mock_remove, mock_dfunc, raw):
    """Verify 'login_user' endpoint is working as expected."""
    result = await login_user(user='001',
                              raw=raw)
    f_kwargs = {'user_id': '001'
                }
    mock_dapi.assert_called_once_with(f=preprocessor.get_permissions,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY
                                      )
    mock_remove.assert_called_once_with(f_kwargs)
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_token.assert_called_once_with(user_id=f_kwargs['user_id'], data=mock_exc.return_value.dikt)
    assert isinstance(result, web_response.Response)
    assert result.content_type == 'text/plain' if raw else result.content_type == 'application/json'


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
@patch('api.controllers.security_controller.generate_token', return_value='token')
@pytest.mark.parametrize('mock_bool', [True, False])
async def test_login_user_ko(mock_token, mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_bool):
    """Verify 'login_user' endpoint is handling FortishieldException as expected."""
    mock_token.side_effect = FortishieldException(999)
    result = await login_user(user='001',
                              raw=mock_bool)
    f_kwargs = {'user_id': '001'
                }
    mock_dapi.assert_called_once_with(f=preprocessor.get_permissions,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY
                                      )
    mock_exc.assert_has_calls([call(mock_dfunc.return_value), call(mock_token.side_effect)])
    assert mock_exc.call_count == 2
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@pytest.mark.parametrize('raw', [True, False])
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
@patch('api.controllers.security_controller.generate_token', return_value='token')
async def test_run_as_login(mock_token, mock_exc, mock_dapi, mock_remove, mock_dfunc, raw, mock_request=AsyncMock()):
    """Verify 'run_as_login' endpoint is working as expected."""
    result = await run_as_login(request=mock_request,
                                user='001',
                                raw=raw)
    auth_context = await mock_request.json()
    f_kwargs = {'user_id': '001',
                'auth_context': auth_context
                }
    mock_dapi.assert_called_once_with(f=preprocessor.get_permissions,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY
                                      )
    mock_remove.assert_called_once_with(f_kwargs)
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_token.assert_called_once_with(user_id=f_kwargs['user_id'], data=mock_exc.return_value.dikt,
                                       auth_context=auth_context)
    assert isinstance(result, web_response.Response)
    assert result.content_type == 'text/plain' if raw else result.content_type == 'application/json'


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
@patch('api.controllers.security_controller.generate_token', return_value='token')
@pytest.mark.parametrize('mock_bool', [True, False])
async def test_run_as_login_ko(mock_token, mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_bool,
                               mock_request=AsyncMock()):
    """Verify 'run_as_login' endpoint is handling FortishieldException as expected."""
    mock_token.side_effect = FortishieldException(999)
    result = await run_as_login(request=mock_request,
                                user='001',
                                raw=mock_bool)
    f_kwargs = {'user_id': '001',
                'auth_context': await mock_request.json()
                }
    mock_dapi.assert_called_once_with(f=preprocessor.get_permissions,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY
                                      )
    mock_exc.assert_has_calls([call(mock_dfunc.return_value), call(mock_token.side_effect)])
    assert mock_exc.call_count == 2
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_get_user_me(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'get_user_me' endpoint is working as expected."""
    result = await get_user_me(request=mock_request)
    f_kwargs = {'token': mock_request['token_info']
                }
    mock_dapi.assert_called_once_with(f=security.get_user_me,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=False,
                                      current_user=mock_request['token_info']['sub'],
                                      rbac_permissions=mock_request['token_info']['rbac_policies']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
async def test_get_user_me_policies(mock_request=MagicMock()):
    """Verify 'get_user_me_policies' endpoint is working as expected."""
    with patch('api.controllers.security_controller.FortishieldResult', return_value='mock_wr_result') as mock_wr:
        result = await get_user_me_policies(request=mock_request)
        mock_wr.assert_called_once_with({'data': mock_request['token_info']['rbac_policies'],
                                         'message': "Current user processed policies information was returned"})
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_logout_user(mock_exc, mock_dapi, mock_dfunc, mock_request=MagicMock()):
    """Verify 'logout_user' endpoint is working as expected."""
    result = await logout_user(request=mock_request)
    mock_dapi.assert_called_once_with(f=security.revoke_current_user_tokens,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=False,
                                      current_user=mock_request['token_info']['sub']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_get_users(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'get_users' endpoint is working as expected."""
    result = await get_users(request=mock_request)
    f_kwargs = {'user_ids': None,
                'offset': 0,
                'limit': None,
                'select': None,
                'sort_by': ['id'],
                'sort_ascending': True,
                'search_text': None,
                'complementary_search': None,
                'q': None,
                'distinct': False
                }
    mock_dapi.assert_called_once_with(f=security.get_users,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=False,
                                      rbac_permissions=mock_request['token_info']['rbac_policies']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_edit_run_as(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'edit_run_as' endpoint is working as expected."""
    result = await edit_run_as(request=mock_request,
                               user_id='001',
                               allow_run_as=False)
    f_kwargs = {'user_id': '001',
                'allow_run_as': False
                }
    mock_dapi.assert_called_once_with(f=security.edit_run_as,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=False,
                                      current_user=mock_request['token_info']['sub'],
                                      rbac_permissions=mock_request['token_info']['rbac_policies']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_create_user(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'create_user' endpoint is working as expected."""
    with patch('api.controllers.security_controller.Body.validate_content_type'):
        with patch('api.controllers.security_controller.CreateUserModel.get_kwargs',
                   return_value=AsyncMock()) as mock_getkwargs:
            result = await create_user(request=mock_request)
            mock_dapi.assert_called_once_with(f=security.create_user,
                                              f_kwargs=mock_remove.return_value,
                                              request_type='local_master',
                                              is_async=False,
                                              logger=ANY,
                                              wait_for_complete=False,
                                              rbac_permissions=mock_request['token_info']['rbac_policies']
                                              )
            mock_exc.assert_called_once_with(mock_dfunc.return_value)
            mock_remove.assert_called_once_with(mock_getkwargs.return_value)
            assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_update_user(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'update_user' endpoint is working as expected."""
    with patch('api.controllers.security_controller.Body.validate_content_type'):
        with patch('api.controllers.security_controller.CreateUserModel.get_kwargs',
                   return_value=AsyncMock()) as mock_getkwargs:
            result = await update_user(request=mock_request,
                                       user_id='001')
            mock_dapi.assert_called_once_with(f=security.update_user,
                                              f_kwargs=mock_remove.return_value,
                                              request_type='local_master',
                                              is_async=False,
                                              logger=ANY,
                                              wait_for_complete=False,
                                              rbac_permissions=mock_request['token_info']['rbac_policies']
                                              )
            mock_exc.assert_called_once_with(mock_dfunc.return_value)
            mock_remove.assert_called_once_with(mock_getkwargs.return_value)
            assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
@pytest.mark.parametrize('mock_uids', ['001', 'all'])
async def test_delete_users(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_uids, mock_request=MagicMock()):
    """Verify 'delete_users' endpoint is working as expected."""
    result = await delete_users(request=mock_request,
                                user_ids=mock_uids)
    if 'all' in mock_uids:
        mock_uids = None
    f_kwargs = {'user_ids': mock_uids
                }
    mock_dapi.assert_called_once_with(f=security.remove_users,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=False,
                                      current_user=mock_request['token_info']['sub'],
                                      rbac_permissions=mock_request['token_info']['rbac_policies']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_get_roles(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'get_roles' endpoint is working as expected."""
    result = await get_roles(request=mock_request)
    f_kwargs = {'role_ids': None,
                'offset': 0,
                'limit': None,
                'select': None,
                'sort_by': ['id'],
                'sort_ascending': True,
                'search_text': None,
                'complementary_search': None,
                'q': None,
                'distinct': False
                }
    mock_dapi.assert_called_once_with(f=security.get_roles,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=False,
                                      rbac_permissions=mock_request['token_info']['rbac_policies']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_add_role(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'add_role' endpoint is working as expected."""
    with patch('api.controllers.security_controller.Body.validate_content_type'):
        with patch('api.controllers.security_controller.RoleModel.get_kwargs',
                   return_value=AsyncMock()) as mock_getkwargs:
            result = await add_role(request=mock_request)
            mock_dapi.assert_called_once_with(f=security.add_role,
                                              f_kwargs=mock_remove.return_value,
                                              request_type='local_master',
                                              is_async=False,
                                              logger=ANY,
                                              wait_for_complete=False,
                                              rbac_permissions=mock_request['token_info']['rbac_policies']
                                              )
            mock_exc.assert_called_once_with(mock_dfunc.return_value)
            mock_remove.assert_called_once_with(mock_getkwargs.return_value)
            assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
@pytest.mark.parametrize('mock_uids', ['001', 'all'])
async def test_remove_roles(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_uids, mock_request=MagicMock()):
    """Verify 'remove_roles' endpoint is working as expected."""
    result = await remove_roles(request=mock_request,
                                role_ids=mock_uids)
    if 'all' in mock_uids:
        mock_uids = None
    f_kwargs = {'role_ids': mock_uids
                }
    mock_dapi.assert_called_once_with(f=security.remove_roles,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=False,
                                      rbac_permissions=mock_request['token_info']['rbac_policies']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_update_role(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'update_role' endpoint is working as expected."""
    with patch('api.controllers.security_controller.Body.validate_content_type'):
        with patch('api.controllers.security_controller.RoleModel.get_kwargs',
                   return_value=AsyncMock()) as mock_getkwargs:
            result = await update_role(request=mock_request,
                                       role_id='001')
            mock_dapi.assert_called_once_with(f=security.update_role,
                                              f_kwargs=mock_remove.return_value,
                                              request_type='local_master',
                                              is_async=False,
                                              logger=ANY,
                                              wait_for_complete=False,
                                              rbac_permissions=mock_request['token_info']['rbac_policies']
                                              )
            mock_exc.assert_called_once_with(mock_dfunc.return_value)
            mock_remove.assert_called_once_with(mock_getkwargs.return_value)
            assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_get_rules(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'get_rules' endpoint is working as expected."""
    result = await get_rules(request=mock_request)
    f_kwargs = {'rule_ids': None,
                'offset': 0,
                'limit': None,
                'select': None,
                'sort_by': ['id'],
                'sort_ascending': True,
                'search_text': None,
                'complementary_search': None,
                'q': '',
                'distinct': False
                }
    mock_dapi.assert_called_once_with(f=security.get_rules,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=False,
                                      rbac_permissions=mock_request['token_info']['rbac_policies']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_add_rule(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'add_rule' endpoint is working as expected."""
    with patch('api.controllers.security_controller.Body.validate_content_type'):
        with patch('api.controllers.security_controller.RuleModel.get_kwargs',
                   return_value=AsyncMock()) as mock_getkwargs:
            result = await add_rule(request=mock_request)
            mock_dapi.assert_called_once_with(f=security.add_rule,
                                              f_kwargs=mock_remove.return_value,
                                              request_type='local_master',
                                              is_async=False,
                                              logger=ANY,
                                              wait_for_complete=False,
                                              rbac_permissions=mock_request['token_info']['rbac_policies']
                                              )
            mock_exc.assert_called_once_with(mock_dfunc.return_value)
            mock_remove.assert_called_once_with(mock_getkwargs.return_value)
            assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_update_rule(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'update_rule' endpoint is working as expected."""
    with patch('api.controllers.security_controller.Body.validate_content_type'):
        with patch('api.controllers.security_controller.RuleModel.get_kwargs',
                   return_value=AsyncMock()) as mock_getkwargs:
            result = await update_rule(request=mock_request,
                                       rule_id='001')
            mock_dapi.assert_called_once_with(f=security.update_rule,
                                              f_kwargs=mock_remove.return_value,
                                              request_type='local_master',
                                              is_async=False,
                                              logger=ANY,
                                              wait_for_complete=False,
                                              rbac_permissions=mock_request['token_info']['rbac_policies']
                                              )
            mock_exc.assert_called_once_with(mock_dfunc.return_value)
            mock_remove.assert_called_once_with(mock_getkwargs.return_value)
            assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
@pytest.mark.parametrize('mock_rids', ['001', 'all'])
async def test_remove_rules(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_rids, mock_request=MagicMock()):
    """Verify 'remove_rules' endpoint is working as expected."""
    result = await remove_rules(request=mock_request,
                                rule_ids=mock_rids)
    if 'all' in mock_rids:
        mock_rids = None
    f_kwargs = {'rule_ids': mock_rids
                }
    mock_dapi.assert_called_once_with(f=security.remove_rules,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=False,
                                      rbac_permissions=mock_request['token_info']['rbac_policies']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_get_policies(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'get_policies' endpoint is working as expected."""
    result = await get_policies(request=mock_request)
    f_kwargs = {'policy_ids': None,
                'offset': 0,
                'limit': None,
                'select': None,
                'sort_by': ['id'],
                'sort_ascending': True,
                'search_text': None,
                'complementary_search': None,
                'q': None,
                'distinct': False
                }
    mock_dapi.assert_called_once_with(f=security.get_policies,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=False,
                                      rbac_permissions=mock_request['token_info']['rbac_policies']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_add_policy(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'add_policy' endpoint is working as expected."""
    with patch('api.controllers.security_controller.Body.validate_content_type'):
        with patch('api.controllers.security_controller.PolicyModel.get_kwargs',
                   return_value=AsyncMock()) as mock_getkwargs:
            result = await add_policy(request=mock_request)
            mock_dapi.assert_called_once_with(f=security.add_policy,
                                              f_kwargs=mock_remove.return_value,
                                              request_type='local_master',
                                              is_async=False,
                                              logger=ANY,
                                              wait_for_complete=False,
                                              rbac_permissions=mock_request['token_info']['rbac_policies']
                                              )
            mock_exc.assert_called_once_with(mock_dfunc.return_value)
            mock_remove.assert_called_once_with(mock_getkwargs.return_value)
            assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
@pytest.mark.parametrize('mock_pids', ['001', 'all'])
async def test_remove_policies(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_pids, mock_request=MagicMock()):
    """Verify 'remove_policies' endpoint is working as expected."""
    result = await remove_policies(request=mock_request,
                                   policy_ids=mock_pids)
    if 'all' in mock_pids:
        mock_pids = None
    f_kwargs = {'policy_ids': mock_pids}
    mock_dapi.assert_called_once_with(f=security.remove_policies,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=False,
                                      rbac_permissions=mock_request['token_info']['rbac_policies']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_update_policy(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'update_policy' endpoint is working as expected."""
    with patch('api.controllers.security_controller.Body.validate_content_type'):
        with patch('api.controllers.security_controller.PolicyModel.get_kwargs',
                   return_value=AsyncMock()) as mock_getkwargs:
            result = await update_policy(request=mock_request,
                                         policy_id='001')
            mock_dapi.assert_called_once_with(f=security.update_policy,
                                              f_kwargs=mock_remove.return_value,
                                              request_type='local_master',
                                              is_async=False,
                                              logger=ANY,
                                              wait_for_complete=False,
                                              rbac_permissions=mock_request['token_info']['rbac_policies']
                                              )
            mock_exc.assert_called_once_with(mock_dfunc.return_value)
            mock_remove.assert_called_once_with(mock_getkwargs.return_value)
            assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_set_user_role(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'set_user_role' endpoint is working as expected."""
    result = await set_user_role(request=mock_request,
                                 user_id='001',
                                 role_ids='001')
    f_kwargs = {'user_id': '001',
                'role_ids': '001',
                'position': None
                }
    mock_dapi.assert_called_once_with(f=security.set_user_role,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=False,
                                      rbac_permissions=mock_request['token_info']['rbac_policies']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
@pytest.mark.parametrize('mock_rids', ['001', 'all'])
async def test_remove_user_role(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_rids, mock_request=MagicMock()):
    """Verify 'remove_user_role' endpoint is working as expected."""
    result = await remove_user_role(request=mock_request,
                                    user_id='001',
                                    role_ids=mock_rids)
    if 'all' in mock_rids:
        mock_rids = None
    f_kwargs = {'user_id': '001',
                'role_ids': mock_rids
                }
    mock_dapi.assert_called_once_with(f=security.remove_user_role,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=False,
                                      rbac_permissions=mock_request['token_info']['rbac_policies']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_set_role_policy(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'set_role_policy' endpoint is working as expected."""
    result = await set_role_policy(request=mock_request,
                                   role_id='001',
                                   policy_ids='001')
    f_kwargs = {'role_id': '001',
                'policy_ids': '001',
                'position': None
                }
    mock_dapi.assert_called_once_with(f=security.set_role_policy,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=False,
                                      rbac_permissions=mock_request['token_info']['rbac_policies']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
@pytest.mark.parametrize('mock_rids', ['001', 'all'])
async def test_remove_role_policy(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_rids, mock_request=MagicMock()):
    """Verify 'remove_role_policy' endpoint is working as expected."""
    result = await remove_role_policy(request=mock_request,
                                      role_id='001',
                                      policy_ids=mock_rids)
    if 'all' in mock_rids:
        mock_rids = None
    f_kwargs = {'role_id': '001',
                'policy_ids': mock_rids
                }
    mock_dapi.assert_called_once_with(f=security.remove_role_policy,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=False,
                                      rbac_permissions=mock_request['token_info']['rbac_policies']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_set_role_rule(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'set_role_rule' endpoint is working as expected."""
    result = await set_role_rule(request=mock_request,
                                 role_id='001',
                                 rule_ids='001')
    f_kwargs = {'role_id': '001',
                'rule_ids': '001',
                'run_as': {
                    'user': mock_request['token_info']['sub'],
                    'run_as': mock_request['token_info']['run_as']
                }
                }
    mock_dapi.assert_called_once_with(f=security.set_role_rule,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=False,
                                      rbac_permissions=mock_request['token_info']['rbac_policies']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
@pytest.mark.parametrize('mock_rids', ['001', 'all'])
async def test_remove_role_rule(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_rids, mock_request=MagicMock()):
    """Verify 'remove_role_rule' endpoint is working as expected."""
    result = await remove_role_rule(request=mock_request,
                                    role_id='001',
                                    rule_ids=mock_rids)
    if 'all' in mock_rids:
        mock_rids = None
    f_kwargs = {'role_id': '001',
                'rule_ids': mock_rids
                }
    mock_dapi.assert_called_once_with(f=security.remove_role_rule,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=False,
                                      rbac_permissions=mock_request['token_info']['rbac_policies']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_get_rbac_resources(mock_exc, mock_dapi, mock_remove, mock_dfunc):
    """Verify 'get_rbac_resources' endpoint is working as expected."""
    result = await get_rbac_resources()
    f_kwargs = {'resource': None
                }
    mock_dapi.assert_called_once_with(f=security.get_rbac_resources,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_any',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=True
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_get_rbac_actions(mock_exc, mock_dapi, mock_remove, mock_dfunc):
    """Verify 'get_rbac_actions' endpoint is working as expected."""
    result = await get_rbac_actions()
    f_kwargs = {'endpoint': None
                }
    mock_dapi.assert_called_once_with(f=security.get_rbac_actions,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_any',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=True
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with(f_kwargs)
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
@patch('api.controllers.security_controller.isinstance')
@pytest.mark.parametrize('mock_snodes', [None, AsyncMock()])
async def test_revoke_all_tokens(mock_isins, mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_snodes,
                                 mock_request=MagicMock()):
    """Verify 'revoke_all_tokens' endpoint is working as expected."""
    mock_isins.return_value = True if not mock_snodes else False
    with patch('api.controllers.security_controller.get_system_nodes', return_value=mock_snodes):
        result = await revoke_all_tokens(request=mock_request)
        if not mock_snodes:
            mock_isins.assert_called_once()
        mock_dapi.assert_called_once_with(f=security.wrapper_revoke_tokens,
                                          f_kwargs=mock_remove.return_value,
                                          request_type='distributed_master' if mock_snodes is not None else 'local_any',
                                          is_async=False,
                                          broadcasting=mock_snodes is not None,
                                          logger=ANY,
                                          wait_for_complete=True,
                                          rbac_permissions=mock_request['token_info']['rbac_policies'],
                                          nodes=mock_snodes
                                          )
        mock_exc.assert_called_once_with(mock_dfunc.return_value)
        mock_remove.assert_called_once_with({})
        assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
@patch('api.controllers.security_controller.type', return_value=AffectedItemsFortishieldResult)
@patch('api.controllers.security_controller.len', return_value=0)
async def test_revoke_all_tokens_ko(mock_type, mock_len, mock_exc, mock_dapi, mock_remove, mock_dfunc,
                                    mock_request=MagicMock()):
    """Verify 'revoke_all_tokens' endpoint is handling FortishieldPermissionError as expected."""
    with patch('api.controllers.security_controller.get_system_nodes', return_value=AsyncMock()) as mock_snodes:
        result = await revoke_all_tokens(request=mock_request)
        mock_dapi.assert_called_once_with(f=security.wrapper_revoke_tokens,
                                          f_kwargs=mock_remove.return_value,
                                          request_type='distributed_master',
                                          is_async=False,
                                          broadcasting=True,
                                          logger=ANY,
                                          wait_for_complete=True,
                                          rbac_permissions=mock_request['token_info']['rbac_policies'],
                                          nodes=mock_snodes.return_value
                                          )
        mock_exc.assert_has_calls([call(mock_dfunc.return_value),
                                   call(FortishieldPermissionError(4000, mock_exc.return_value.message))])
        assert mock_exc.call_count == 2
        mock_remove.assert_called_once_with({})
        assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_get_security_config(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'get_security_config' endpoint is working as expected."""
    result = await get_security_config(request=mock_request)
    mock_dapi.assert_called_once_with(f=security.get_security_config,
                                      f_kwargs=mock_remove.return_value,
                                      request_type='local_master',
                                      is_async=False,
                                      logger=ANY,
                                      wait_for_complete=False,
                                      rbac_permissions=mock_request['token_info']['rbac_policies']
                                      )
    mock_exc.assert_called_once_with(mock_dfunc.return_value)
    mock_remove.assert_called_once_with({})
    assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
@patch('api.controllers.security_controller.isinstance')
@pytest.mark.parametrize('mock_snodes', [None, AsyncMock()])
async def test_security_revoke_tokens(mock_isins, mock_exc, mock_dapi, mock_dfunc, mock_snodes):
    """Verify 'security_revoke_tokens' endpoint is working as expected."""
    mock_isins.return_value = True if not mock_snodes else False
    with patch('api.controllers.security_controller.get_system_nodes', return_value=mock_snodes):
        await security_revoke_tokens()
        mock_dapi.assert_called_once_with(f=security.revoke_tokens,
                                          request_type='distributed_master' if mock_snodes is not None else 'local_any',
                                          is_async=False,
                                          wait_for_complete=True,
                                          broadcasting=mock_snodes is not None,
                                          logger=ANY,
                                          nodes=mock_snodes
                                          )
        mock_exc.assert_called_once_with(mock_dfunc.return_value)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_put_security_config(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'put_security_config' endpoint is working as expected."""
    with patch('api.controllers.security_controller.Body.validate_content_type'):
        with patch('api.controllers.security_controller.SecurityConfigurationModel.get_kwargs',
                   return_value=AsyncMock()) as mock_getkwargs:
            with patch('api.controllers.security_controller.security_revoke_tokens', return_value=AsyncMock()):
                result = await put_security_config(request=mock_request)
                f_kwargs = {'updated_config': mock_getkwargs.return_value
                            }
                mock_dapi.assert_called_once_with(f=security.update_security_config,
                                                  f_kwargs=mock_remove.return_value,
                                                  request_type='local_master',
                                                  is_async=False,
                                                  logger=ANY,
                                                  wait_for_complete=False,
                                                  rbac_permissions=mock_request['token_info']['rbac_policies'],
                                                  )
                mock_exc.assert_called_once_with(mock_dfunc.return_value)
                mock_remove.assert_called_once_with(f_kwargs)
                assert isinstance(result, web_response.Response)


@pytest.mark.asyncio
@patch('api.controllers.security_controller.DistributedAPI.distribute_function', return_value=AsyncMock())
@patch('api.controllers.security_controller.remove_nones_to_dict')
@patch('api.controllers.security_controller.DistributedAPI.__init__', return_value=None)
@patch('api.controllers.security_controller.raise_if_exc', return_value=CustomAffectedItems())
async def test_delete_security_config(mock_exc, mock_dapi, mock_remove, mock_dfunc, mock_request=MagicMock()):
    """Verify 'delete_security_config' endpoint is working as expected."""
    with patch('api.controllers.security_controller.SecurityConfigurationModel.get_kwargs',
               return_value=AsyncMock()) as mock_getkwargs:
        with patch('api.controllers.security_controller.security_revoke_tokens', return_value=AsyncMock()):
            result = await delete_security_config(request=mock_request)
            f_kwargs = {'updated_config': mock_getkwargs.return_value
                        }
            mock_dapi.assert_called_once_with(f=security.update_security_config,
                                              f_kwargs=mock_remove.return_value,
                                              request_type='local_master',
                                              is_async=False,
                                              logger=ANY,
                                              wait_for_complete=False,
                                              rbac_permissions=mock_request['token_info']['rbac_policies']
                                              )
            mock_exc.assert_called_once_with(mock_dfunc.return_value)
            mock_remove.assert_called_once_with(f_kwargs)
            assert isinstance(result, web_response.Response)