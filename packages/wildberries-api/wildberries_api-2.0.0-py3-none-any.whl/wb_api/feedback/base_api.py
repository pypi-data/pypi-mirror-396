from wb_api.base.api import API
from wb_api.base.config import BaseURL
from wb_api.feedback.router import FeedbackRouter

from typing import Type


class BaseFeedbackAPI(API[FeedbackRouter]):
	@staticmethod
	def make_router(base_url: Type[BaseURL]):
		return FeedbackRouter(base_url.FEEDBACK)
