from wb_api.feedback.dataclass.question_answer_add import Request, RequestAnswer


class TestRequest:
	def test_create(self):
		request = Request.create("question-id", "answer-text")
		assert request.id == "question-id"
		assert isinstance(request.answer, RequestAnswer)
		assert request.answer.text == "answer-text"
		assert request.state == "wbRu"

	def test_as_request_payload(self):
		assert Request.create("question-id", "answer-text").as_request_payload() == {
			"id": "question-id",
			"answer": {
				"text": "answer-text",
			},
			"state": "wbRu",
		}
