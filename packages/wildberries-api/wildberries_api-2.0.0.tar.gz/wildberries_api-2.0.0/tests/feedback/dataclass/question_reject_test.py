from wb_api.feedback.dataclass.question_reject import Request, RequestAnswer


class TestRequest:
	def test_create(self):
		request = Request.create("question-id", "reject-note")
		assert request.id == "question-id"
		assert isinstance(request.answer, RequestAnswer)
		assert request.answer.text == "reject-note"
		assert request.state == "none"

	def test_as_request_payload(self):
		assert Request.create("question-id", "answer-text").as_request_payload() == {
			"id": "question-id",
			"answer": {
				"text": "answer-text",
			},
			"state": "none",
		}

