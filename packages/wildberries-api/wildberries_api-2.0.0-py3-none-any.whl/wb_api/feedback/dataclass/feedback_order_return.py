from wb_api.base.dataclass import BaseRequest, BaseResponse

from pydantic.fields import Field


class Request(BaseRequest):
	feedback_id: str = Field(serialization_alias="feedbackId")

	def as_request_payload(self):
		return self.model_dump(by_alias=True)


Response = BaseResponse
