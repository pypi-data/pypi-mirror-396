from wb_api.const import Header, BaseURL
from wb_api.common.async_api import AsyncCommonAPI
from wb_api.feedback.async_api import AsyncFeedbackAPI
from wb_api.base.async_config import AsyncConfig
from wb_api.base.config import BaseURL as BaseURLProto

from typing import Type

from aiohttp.client import ClientSession


class AsyncAPI:
	config: AsyncConfig
	common: AsyncCommonAPI
	feedback: AsyncFeedbackAPI

	def __init__(self, config: AsyncConfig) -> None:
		self.config = config
		self.common = AsyncCommonAPI(config)
		self.feedback = AsyncFeedbackAPI(config)

	async def close(self) -> None:
		await self.config.session.close()

	@classmethod
	async def build(cls, token: str, *, base_url: Type[BaseURLProto] = BaseURL) -> "AsyncAPI":
		config = AsyncConfig(
			await cls.make_session(token),
			base_url,
		)

		return cls(config)

	@staticmethod
	async def make_session(token: str) -> ClientSession:
		session = ClientSession(headers={Header.AUTHORIZATION.value: token})
		return session
