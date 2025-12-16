from wb_api.feedback.dataclass.question_get import Request


class TestRequest:
	def test_as_request_params(self):
		assert Request(id="question-id").as_request_params() == {"id": "question-id"}
