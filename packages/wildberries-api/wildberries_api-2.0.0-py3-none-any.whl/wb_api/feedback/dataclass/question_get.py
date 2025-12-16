from wb_api.base.dataclass import BaseRequest, BaseResponse
from wb_api.feedback.dataclass.question import Question


class Request(BaseRequest):
	id: str

	def as_request_params(self):
		return self.model_dump()


class Response(BaseResponse):
	data: Question
