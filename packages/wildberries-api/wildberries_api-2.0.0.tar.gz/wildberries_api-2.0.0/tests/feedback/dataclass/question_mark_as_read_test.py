from wb_api.feedback.dataclass.question_mark_as_read import Request


class TestRequest:
	def test_as_request_payload(self):
		assert Request(id="question-id", was_viewed=False).as_request_payload() == {
			"id": "question-id",
			"wasViewed": False,
		}
