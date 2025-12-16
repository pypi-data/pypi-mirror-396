from wb_api.base.dataclass import BaseRequest, BaseResponse

from typing import Literal

from pydantic.main import BaseModel


class RequestAnswer(BaseModel):
	text: str


class Request(BaseRequest):
	id: str
	answer: RequestAnswer
	state: Literal["none"] = "none"

	@classmethod
	def create(cls, question_id: str, text: str) -> "Request":
		return cls(id=question_id, answer=RequestAnswer(text=text))

	def as_request_payload(self):
		return self.model_dump()


Response = BaseResponse
