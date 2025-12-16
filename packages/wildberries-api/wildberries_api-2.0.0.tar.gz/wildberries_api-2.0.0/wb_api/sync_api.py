from wb_api.generic.requests.auth import JWTTokenAuth
from wb_api.common.sync_api import SyncCommonAPI
from wb_api.feedback.sync_api import SyncFeedbackAPI
from wb_api.const import Header, BaseURL
from wb_api.base.config import BaseURL as BaseURLProto
from wb_api.base.sync_config import SyncConfig

from typing import Type

from requests.sessions import Session


class SyncAPI:
	config: SyncConfig
	common: SyncCommonAPI
	feedback: SyncFeedbackAPI

	def __init__(self, config: SyncConfig) -> None:
		self.config = config
		self.common = SyncCommonAPI(config)
		self.feedback = SyncFeedbackAPI(config)

	@classmethod
	def build(cls, token: str, *, base_url: Type[BaseURLProto] = BaseURL) -> "SyncAPI":
		config = SyncConfig(
			cls.make_session(token),
			base_url,
		)

		return cls(config)

	@staticmethod
	def make_session(token: str) -> Session:
		session = Session()
		session.auth = JWTTokenAuth(token, Header.AUTHORIZATION.value)

		return session
