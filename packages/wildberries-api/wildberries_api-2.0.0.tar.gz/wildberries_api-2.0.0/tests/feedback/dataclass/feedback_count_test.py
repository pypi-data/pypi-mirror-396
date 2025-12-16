from wb_api.feedback.dataclass.feedback_count import Request

from arrow import get


class TestRequest:
	def test_optional_dates_must_be_optional_int(self):
		request = Request()
		assert request.optional_dates_must_be_optional_int(None) is None
		assert request.optional_dates_must_be_optional_int(get(2025, 1, 1, 12, 30, 30)) == 1735734630

	def test_optional_bool_must_be_optional_str(self):
		request = Request()
		assert request.optional_bool_must_be_optional_str(None) is None
		assert request.optional_bool_must_be_optional_str(True) == "true"
		assert request.optional_bool_must_be_optional_str(False) == "false"

	def test_as_request_params(self):
		assert Request().as_request_params() == {}
		assert Request(date_from=get(2025, 1, 1, 12, 30, 30), is_answered=True).as_request_params() == {
			"dateFrom": 1735734630,
			"isAnswered": "true",
		}
