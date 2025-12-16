from wb_api.feedback.dataclass.feedback import Feedback

from arrow import get


class TestFeedback:
	def test_dates_must_be_arrow(self):
		assert Feedback.dates_must_be_arrow("2025-01-01T12:30:30+00:00") == get(2025, 1, 1, 12, 30, 30)

	def test_optional_dates_must_be_optional_arrow(self):
		assert Feedback.optional_dates_must_be_optional_arrow(None) is None
		assert Feedback.optional_dates_must_be_optional_arrow("2025-01-01T12:30:30+00:00") == get(2025, 1, 1, 12, 30, 30)
