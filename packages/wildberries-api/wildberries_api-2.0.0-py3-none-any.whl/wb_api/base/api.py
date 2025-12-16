from wb_api.base.router import Router
from wb_api.base.config import Config, BaseURL

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type


RouterT = TypeVar("RouterT", bound=Router)


class API(ABC, Generic[RouterT]):
	config: Config
	router: RouterT

	def __init__(self, config: Config) -> None:
		self.router = self.make_router(config.base_url)
		self.config = config

	@staticmethod
	@abstractmethod
	def make_router(base_url: Type[BaseURL]) -> RouterT: ...
