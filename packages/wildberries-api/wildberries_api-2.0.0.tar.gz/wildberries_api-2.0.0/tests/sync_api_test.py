from wb_api.sync_api import SyncAPI
from wb_api.common.sync_api import SyncCommonAPI
from wb_api.feedback.sync_api import SyncFeedbackAPI
from wb_api.generic.requests.auth import JWTTokenAuth
from wb_api.const import Header, BaseURL
from wb_api.base.sync_config import SyncConfig

from requests.sessions import Session


class TestSyncAPI:
	def test___init__(self):
		session = Session()
		config = SyncConfig(session, BaseURL)
		api = SyncAPI(config)
		assert api.config is config
		assert isinstance(api.common, SyncCommonAPI)
		assert api.common.session is session
		assert isinstance(api.feedback, SyncFeedbackAPI)
		assert api.feedback.session is session

	def test_build(self):
		api = SyncAPI.build("ACCESS_TOKEN")
		assert isinstance(api.config.session.auth, JWTTokenAuth)
		assert api.config.session.auth.token == "ACCESS_TOKEN"
		assert api.config.session.auth.header_label == Header.AUTHORIZATION.value

	def test_make_session(self):
		session = SyncAPI.make_session("ACCESS_TOKEN")
		assert isinstance(session, Session)
		assert isinstance(session.auth, JWTTokenAuth)
		assert session.auth.token == "ACCESS_TOKEN"
		assert session.auth.header_label == Header.AUTHORIZATION.value
