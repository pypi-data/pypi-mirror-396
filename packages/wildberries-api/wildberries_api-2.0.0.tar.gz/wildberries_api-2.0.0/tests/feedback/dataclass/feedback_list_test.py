from wb_api.feedback.dataclass.feedback_list import Request

import pytest
from arrow import get
from pydantic import ValidationError


class TestRequest:
	def test_optional_dates_must_be_optional_int(self):
		request = Request(is_answered=True, take=100, skip=0)
		assert request.optional_dates_must_be_optional_int(None) is None
		assert request.optional_dates_must_be_optional_int(get(2025, 1, 1, 12, 30, 30)) == 1735734630

	def test_optional_bool_must_be_optional_str(self):
		request = Request(is_answered=True, take=100, skip=0)
		assert request.optional_bool_must_be_optional_str(None) is None
		assert request.optional_bool_must_be_optional_str(True) == "true"
		assert request.optional_bool_must_be_optional_str(False) == "false"

	def test_verify_pagination(self):
		Request(is_answered=True, take=5000, skip=5000)

		with pytest.raises(ValidationError):
			Request(is_answered=True, take=5000, skip=5001)

	def test_as_request_params(self):
		assert Request(is_answered=True, take=5000, skip=5000).as_request_params() == {
			"isAnswered": "true",
			"take": 5000,
			"skip": 5000,
		}
