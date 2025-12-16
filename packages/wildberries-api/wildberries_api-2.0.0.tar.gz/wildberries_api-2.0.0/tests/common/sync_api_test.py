from wb_api.common.sync_api import SyncCommonAPI
from wb_api.base.sync_config import SyncConfig
from wb_api.const import BaseURL

from unittest.mock import Mock, patch


class TestSyncCommonAPI:
	def test_ping(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "RAW DATA"
		config = SyncConfig(session, BaseURL)
		api = SyncCommonAPI(config)

		with patch("wb_api.common.sync_api.PingResponse") as PingResponseMock:
			PingResponseMock.model_validate_json = Mock()
			PingResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.ping() == "DESERIALIZED DATA"
				PingResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with("https://common-api.wildberries.ru/ping")
