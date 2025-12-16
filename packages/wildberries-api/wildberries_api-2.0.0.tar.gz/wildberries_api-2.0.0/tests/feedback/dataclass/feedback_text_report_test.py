from wb_api.feedback.dataclass.feedback_text_report import Request


class TestRequest:
	def test_as_request_payload(self):
		assert Request(id="feedback-id", supplier_feedback_valuation=512).as_request_payload() == {
			"id": "feedback-id",
			"supplierFeedbackValuation": 512,
		}
