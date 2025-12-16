from wb_api.feedback.dataclass.feedback_get import Request


class TestRequest:
	def test_as_request_params(self):
		assert Request(id="feedback-id").as_request_params() == {"id": "feedback-id"}
