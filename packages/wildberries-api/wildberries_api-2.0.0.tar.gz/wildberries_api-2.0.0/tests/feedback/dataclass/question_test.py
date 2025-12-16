from wb_api.feedback.dataclass.question import QuestionAnswer, Question

from arrow import get


class TestQuestionAnswer:
	def test_dates_must_be_arrow(self):
		assert QuestionAnswer.dates_must_be_arrow("2025-01-01T12:30:30+00:00") == get(2025, 1, 1, 12, 30, 30)


class TestQuestion:
	def test_dates_must_be_arrow(self):
		assert Question.dates_must_be_arrow("2025-01-01T12:30:30+00:00") == get(2025, 1, 1, 12, 30, 30)
