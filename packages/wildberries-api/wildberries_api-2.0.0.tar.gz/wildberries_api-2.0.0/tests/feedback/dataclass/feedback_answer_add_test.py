from wb_api.feedback.dataclass.feedback_answer_add import Request


class TestRequest:
	def test_as_request_payload(self):
		assert Request(id="feedback-id", text="feedback-text").as_request_payload() == {
			"id": "feedback-id",
			"text": "feedback-text",
		}
