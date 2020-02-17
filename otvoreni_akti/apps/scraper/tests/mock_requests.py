from unittest.mock import patch


def requests_patcher(parent_module, function_to_patch, payload):
    with patch.object(parent_module, 'requests_retry_session') as mocked_session:
        mocked_get = mocked_session.return_value.get
        mocked_get.return_value.content = payload
        return function_to_patch('dummyvalue')
