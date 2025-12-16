from wb_api.base.api import API
from wb_api.base.config import BaseURL
from wb_api.common.router import CommonRouter

from typing import Type


class BaseCommonAPI(API[CommonRouter]):
	@staticmethod
	def make_router(base_url: Type[BaseURL]):
		return CommonRouter(base_url.COMMON)
