from wb_api.feedback.dataclass.feedback_order_return import Request


class TestRequest:
	def test_as_request_payload(self):
		assert Request(feedback_id="feedback-id").as_request_payload() == {"feedbackId": "feedback-id"}
