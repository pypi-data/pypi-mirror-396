from wb_api.feedback.sync_api import SyncFeedbackAPI
from wb_api.feedback.dataclass import (
	QuestionCountRequest, QuestionListRequest, QuestionGetRequest, FeedbackCountRequest, FeedbackListRequest,
	FeedbackSupplierValuationsRequest, FeedbackGetRequest, FeedbackArchiveListRequest, QuestionMarkAsReadRequest,
	QuestionRejectRequest, QuestionAnswerAddRequest, QuestionAnswerUpdateRequest, FeedbackOrderReturnRequest,
	FeedbackTextReportRequest, FeedbackProductReportRequest, FeedbackAnswerAddRequest, FeedbackAnswerUpdateRequest,
)
from wb_api.base.sync_config import SyncConfig
from wb_api.const import BaseURL

from unittest.mock import Mock, patch
from http import HTTPStatus

from arrow import get


class TestSyncFeedbackAPI:
	def test_ping(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "RAW DATA"
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)

		with patch("wb_api.feedback.sync_api.PingResponse") as PingResponseMock:
			PingResponseMock.model_validate_json = Mock()
			PingResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.ping() == "DESERIALIZED DATA"
				PingResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with("https://feedbacks-api.wildberries.ru/ping")

	def test_check_new_feedbacks_questions(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "RAW DATA"
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)

		with patch("wb_api.feedback.sync_api.NewFeedbacksQuestionsResponse") as NewFeedbacksQuestionsResponseMock:
			NewFeedbacksQuestionsResponseMock.model_validate_json = Mock()
			NewFeedbacksQuestionsResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.check_new_feedbacks_questions() == "DESERIALIZED DATA"
				NewFeedbacksQuestionsResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with(
					"https://feedbacks-api.wildberries.ru/api/v1/new-feedbacks-questions",
				)

	def test_get_question_count_unanswered(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "RAW DATA"
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)

		with patch("wb_api.feedback.sync_api.QuestionCountUnansweredResponse") as QuestionCountUnansweredResponseMock:
			QuestionCountUnansweredResponseMock.model_validate_json = Mock()
			QuestionCountUnansweredResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_question_count_unanswered() == "DESERIALIZED DATA"
				QuestionCountUnansweredResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with("https://feedbacks-api.wildberries.ru/api/v1/questions/count-unanswered")

	def test_get_question_count(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "RAW DATA"
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)

		with patch("wb_api.feedback.sync_api.QuestionCountResponse") as QuestionCountResponseMock:
			QuestionCountResponseMock.model_validate_json = Mock()
			QuestionCountResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_question_count() == "DESERIALIZED DATA"
				QuestionCountResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with(
					"https://feedbacks-api.wildberries.ru/api/v1/questions/count",
					params=QuestionCountRequest().as_request_params(),
				)

				session.get.reset_mock()
				request = QuestionCountRequest(is_answered=True, date_from=get(2025, 1, 1))
				assert api.get_question_count(request) == "DESERIALIZED DATA"
				session.get.assert_called_once_with(
					"https://feedbacks-api.wildberries.ru/api/v1/questions/count",
					params=request.as_request_params(),
				)

	def test_get_question_list(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "RAW DATA"
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)
		request = QuestionListRequest(is_answered=False, take=100, skip=0)

		with patch("wb_api.feedback.sync_api.QuestionListResponse") as QuestionListResponseMock:
			QuestionListResponseMock.model_validate_json = Mock()
			QuestionListResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_question_list(request) == "DESERIALIZED DATA"
				QuestionListResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with(
					"https://feedbacks-api.wildberries.ru/api/v1/questions",
					params=request.as_request_params(),
				)

	def test_mark_question_as_read(self):
		session = Mock()
		session.patch = Mock()
		session.patch.return_value = Mock()
		session.patch.return_value.text = "RAW DATA"
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)
		request = QuestionMarkAsReadRequest(id="question-id", was_viewed=True)

		with patch("wb_api.feedback.sync_api.QuestionMarkAsReadResponse") as QuestionMarkAsReadResponseMock:
			QuestionMarkAsReadResponseMock.model_validate_json = Mock()
			QuestionMarkAsReadResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.mark_question_as_read(request) == "DESERIALIZED DATA"
				QuestionMarkAsReadResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.patch.return_value)
				session.patch.assert_called_once_with(
					"https://feedbacks-api.wildberries.ru/api/v1/questions",
					json=request.as_request_payload(),
				)

	def test_reject_question(self):
		session = Mock()
		session.patch = Mock()
		session.patch.return_value = Mock()
		session.patch.return_value.text = "RAW DATA"
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)
		request = QuestionRejectRequest.create("question-id", "question-answer")

		with patch("wb_api.feedback.sync_api.QuestionRejectResponse") as QuestionRejectResponseMock:
			QuestionRejectResponseMock.model_validate_json = Mock()
			QuestionRejectResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.reject_question(request) == "DESERIALIZED DATA"
				QuestionRejectResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.patch.return_value)
				session.patch.assert_called_once_with(
					"https://feedbacks-api.wildberries.ru/api/v1/questions",
					json=request.as_request_payload(),
				)

	def test_add_question_answer(self):
		session = Mock()
		session.patch = Mock()
		session.patch.return_value = Mock()
		session.patch.return_value.text = "RAW DATA"
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)
		request = QuestionAnswerAddRequest.create("question-id", "question-answer")

		with patch("wb_api.feedback.sync_api.QuestionAnswerAddResponse") as QuestionAnswerAddResponseMock:
			QuestionAnswerAddResponseMock.model_validate_json = Mock()
			QuestionAnswerAddResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.add_question_answer(request) == "DESERIALIZED DATA"
				QuestionAnswerAddResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.patch.return_value)
				session.patch.assert_called_once_with(
					"https://feedbacks-api.wildberries.ru/api/v1/questions",
					json=request.as_request_payload(),
				)

	def test_update_question_answer(self):
		session = Mock()
		session.patch = Mock()
		session.patch.return_value = Mock()
		session.patch.return_value.text = "RAW DATA"
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)
		request = QuestionAnswerUpdateRequest.create("question-id", "question-answer")

		with patch("wb_api.feedback.sync_api.QuestionAnswerUpdateResponse") as QuestionAnswerUpdateResponseMock:
			QuestionAnswerUpdateResponseMock.model_validate_json = Mock()
			QuestionAnswerUpdateResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.update_question_answer(request) == "DESERIALIZED DATA"
				QuestionAnswerUpdateResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.patch.return_value)
				session.patch.assert_called_once_with(
					"https://feedbacks-api.wildberries.ru/api/v1/questions",
					json=request.as_request_payload(),
				)

	def test_get_question(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "RAW DATA"
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)
		request = QuestionGetRequest(id="question-id")

		with patch("wb_api.feedback.sync_api.QuestionGetResponse") as QuestionGetResponseMock:
			QuestionGetResponseMock.model_validate_json = Mock()
			QuestionGetResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_question(request) == "DESERIALIZED DATA"
				QuestionGetResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with(
					"https://feedbacks-api.wildberries.ru/api/v1/question",
					params=request.as_request_params(),
				)

	def test_get_feedback_count_unanswered(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "RAW DATA"
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)

		with patch("wb_api.feedback.sync_api.FeedbackCountUnansweredResponse") as FeedbackCountUnansweredResponseMock:
			FeedbackCountUnansweredResponseMock.model_validate_json = Mock()
			FeedbackCountUnansweredResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_feedback_count_unanswered() == "DESERIALIZED DATA"
				FeedbackCountUnansweredResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with(
					"https://feedbacks-api.wildberries.ru/api/v1/feedbacks/count-unanswered",
				)

	def test_get_feedback_count(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "RAW DATA"
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)

		with patch("wb_api.feedback.sync_api.FeedbackCountResponse") as FeedbackCountResponseMock:
			FeedbackCountResponseMock.model_validate_json = Mock()
			FeedbackCountResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_feedback_count() == "DESERIALIZED DATA"
				FeedbackCountResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with(
					"https://feedbacks-api.wildberries.ru/api/v1/feedbacks/count",
					params=FeedbackCountRequest().as_request_params(),
				)

				session.get.reset_mock()
				request = FeedbackCountRequest(is_answered=False, date_from=get(2025, 1, 1))
				assert api.get_feedback_count(request) == "DESERIALIZED DATA"
				session.get.assert_called_once_with(
					"https://feedbacks-api.wildberries.ru/api/v1/feedbacks/count",
					params=request.as_request_params(),
				)

	def test_get_feedback_list(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "RAW DATA"
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)
		request = FeedbackListRequest(is_answered=True, take=100, skip=0)

		with patch("wb_api.feedback.sync_api.FeedbackListResponse") as FeedbackListResponseMock:
			FeedbackListResponseMock.model_validate_json = Mock()
			FeedbackListResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_feedback_list(request) == "DESERIALIZED DATA"
				FeedbackListResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with(
					"https://feedbacks-api.wildberries.ru/api/v1/feedbacks",
					params=request.as_request_params(),
				)

	def test_get_feedback_supplier_valuations(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "RAW DATA"
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)
		request = FeedbackSupplierValuationsRequest(locale="zh")

		with patch("wb_api.feedback.sync_api.FeedbackSupplierValuationsResponse") as FeedbackSupplierValuationsResponseMock:
			FeedbackSupplierValuationsResponseMock.model_validate_json = Mock()
			FeedbackSupplierValuationsResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_feedback_supplier_valuations() == "DESERIALIZED DATA"
				FeedbackSupplierValuationsResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with(
					"https://feedbacks-api.wildberries.ru/api/v1/supplier-valuations",
					headers=FeedbackSupplierValuationsRequest().as_request_headers(),
				)

				session.get.reset_mock()
				assert api.get_feedback_supplier_valuations(request) == "DESERIALIZED DATA"
				session.get.assert_called_once_with(
					"https://feedbacks-api.wildberries.ru/api/v1/supplier-valuations",
					headers=request.as_request_headers(),
				)

	def test_report_feedback_text(self):
		session = Mock()
		session.post = Mock()
		session.post.return_value = Mock()
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)
		request = FeedbackTextReportRequest(id="feedback-id", supplier_feedback_valuation=512)

		with patch.object(api, "validate_response") as validate_response_mock:
			assert api.report_feedback_text(request) is None
			validate_response_mock.assert_called_once_with(session.post.return_value, HTTPStatus.NO_CONTENT)
			session.post.assert_called_once_with(
				"https://feedbacks-api.wildberries.ru/api/v1/feedbacks/actions",
				json=request.as_request_payload(),
			)

	def test_report_feedback_product(self):
		session = Mock()
		session.post = Mock()
		session.post.return_value = Mock()
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)
		request = FeedbackProductReportRequest(id="feedback-id", supplier_product_valuation=512)

		with patch.object(api, "validate_response") as validate_response_mock:
			assert api.report_feedback_product(request) is None
			validate_response_mock.assert_called_once_with(session.post.return_value, HTTPStatus.NO_CONTENT)
			session.post.assert_called_once_with(
				"https://feedbacks-api.wildberries.ru/api/v1/feedbacks/actions",
				json=request.as_request_payload(),
			)

	def test_add_feedback_answer(self):
		session = Mock()
		session.post = Mock()
		session.post.return_value = Mock()
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)
		request = FeedbackAnswerAddRequest(id="feedback-id", text="feedback-answer")

		with patch.object(api, "validate_response") as validate_response_mock:
			assert api.add_feedback_answer(request) is None
			validate_response_mock.assert_called_once_with(session.post.return_value, HTTPStatus.NO_CONTENT)
			session.post.assert_called_once_with(
				"https://feedbacks-api.wildberries.ru/api/v1/feedbacks/answer",
				json=request.as_request_payload(),
			)

	def test_update_feedback_answer(self):
		session = Mock()
		session.patch = Mock()
		session.patch.return_value = Mock()
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)
		request = FeedbackAnswerUpdateRequest(id="feedback-id", text="feedback-answer")

		with patch.object(api, "validate_response") as validate_response_mock:
			assert api.update_feedback_answer(request) is None
			validate_response_mock.assert_called_once_with(session.patch.return_value, HTTPStatus.NO_CONTENT)
			session.patch.assert_called_once_with(
				"https://feedbacks-api.wildberries.ru/api/v1/feedbacks/answer",
				json=request.as_request_payload(),
			)

	def test_return_feedback_order(self):
		session = Mock()
		session.post = Mock()
		session.post.return_value = Mock()
		session.post.return_value.text = "RAW DATA"
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)
		request = FeedbackOrderReturnRequest(feedback_id="feedback-id")

		with patch("wb_api.feedback.sync_api.FeedbackOrderReturnResponse") as FeedbackOrderReturnResponseMock:
			FeedbackOrderReturnResponseMock.model_validate_json = Mock()
			FeedbackOrderReturnResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.return_feedback_order(request) == "DESERIALIZED DATA"
				FeedbackOrderReturnResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.post.return_value)
				session.post.assert_called_once_with(
					"https://feedbacks-api.wildberries.ru/api/v1/feedbacks/order/return",
					json=request.as_request_payload(),
				)

	def test_get_feedback(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "RAW DATA"
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)
		request = FeedbackGetRequest(id="feedback-id")

		with patch("wb_api.feedback.sync_api.FeedbackGetResponse") as FeedbackGetResponseMock:
			FeedbackGetResponseMock.model_validate_json = Mock()
			FeedbackGetResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_feedback(request) == "DESERIALIZED DATA"
				FeedbackGetResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with(
					"https://feedbacks-api.wildberries.ru/api/v1/feedback",
					params=request.as_request_params(),
				)

	def test_get_feedback_archive_list(self):
		session = Mock()
		session.get = Mock()
		session.get.return_value = Mock()
		session.get.return_value.text = "RAW DATA"
		config = SyncConfig(session, BaseURL)
		api = SyncFeedbackAPI(config)
		request = FeedbackArchiveListRequest(take=100, skip=0)

		with patch("wb_api.feedback.sync_api.FeedbackArchiveListResponse") as FeedbackArchiveListMockResponse:
			FeedbackArchiveListMockResponse.model_validate_json = Mock()
			FeedbackArchiveListMockResponse.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert api.get_feedback_archive_list(request) == "DESERIALIZED DATA"
				FeedbackArchiveListMockResponse.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.get.return_value)
				session.get.assert_called_once_with(
					"https://feedbacks-api.wildberries.ru/api/v1/feedbacks/archive",
					params=request.as_request_params(),
				)
