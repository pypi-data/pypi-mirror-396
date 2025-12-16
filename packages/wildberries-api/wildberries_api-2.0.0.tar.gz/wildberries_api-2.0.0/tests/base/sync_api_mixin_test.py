from wb_api.base.sync_api_mixin import SyncAPIMixin
from wb_api.base.sync_config import SyncConfig
from wb_api.exception import InvalidResponseError, AuthorizationError, NotFoundError
from wb_api.const import BaseURL

from unittest.mock import Mock
from http import HTTPStatus
from typing import Optional, Type

import pytest
from requests.sessions import Session


class BaseClient:
	def __init__(self, config: SyncConfig) -> None:
		pass


class Client(SyncAPIMixin, BaseClient):
	pass


class TestSyncAPIMixin:
	@pytest.mark.asyncio()
	@pytest.mark.parametrize(
		"status, expected_error_type, expected_error_text",
		[
			(HTTPStatus.OK, None, None),
			(HTTPStatus.FORBIDDEN, None, None),
			(HTTPStatus.FORBIDDEN, AuthorizationError, "Unauthorized"),
			(HTTPStatus.UNAUTHORIZED, AuthorizationError, "Unauthorized"),
			(HTTPStatus.NOT_FOUND, NotFoundError, "Resource was not found"),
			(HTTPStatus.INTERNAL_SERVER_ERROR, InvalidResponseError, "Response is not valid"),
		],
	)
	async def test_validate_response(
		self,
		status: HTTPStatus,
		expected_error_type: Optional[Type[Exception]],
		expected_error_text: Optional[str],
	):
		session = Session()
		config = SyncConfig(session, BaseURL)
		api = Client(config)
		response = Mock()
		response.status_code = status

		if expected_error_type is None:
			assert api.validate_response(response, status) is None
		else:
			with pytest.raises(expected_error_type, match=expected_error_text):
				api.validate_response(response)
