from tests.fake_async_session import FakeAsyncSession
from wb_api.feedback.async_api import AsyncFeedbackAPI
from wb_api.feedback.dataclass import (
	QuestionCountRequest, QuestionListRequest, QuestionGetRequest, FeedbackCountRequest, FeedbackListRequest,
	FeedbackSupplierValuationsRequest, FeedbackGetRequest, FeedbackArchiveListRequest, QuestionMarkAsReadRequest,
	QuestionRejectRequest, QuestionAnswerAddRequest, QuestionAnswerUpdateRequest, FeedbackTextReportRequest,
	FeedbackProductReportRequest, FeedbackAnswerAddRequest, FeedbackAnswerUpdateRequest, FeedbackOrderReturnRequest,
)
from wb_api.base.async_config import AsyncConfig
from wb_api.const import BaseURL

from unittest.mock import patch, Mock
from http import HTTPStatus

import pytest
from arrow import get


class TestAsyncFeedbackAPI:
	@pytest.mark.asyncio()
	async def test_ping(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)

		with patch("wb_api.feedback.async_api.PingResponse") as PingResponseMock:
			PingResponseMock.model_validate_json = Mock()
			PingResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.ping() == "DESERIALIZED DATA"
				PingResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/ping"
				assert session.last_call_params is None

	@pytest.mark.asyncio()
	async def test_check_new_feedbacks_questions(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)

		with patch("wb_api.feedback.async_api.NewFeedbacksQuestionsResponse") as NewFeedbacksQuestionsResponseMock:
			NewFeedbacksQuestionsResponseMock.model_validate_json = Mock()
			NewFeedbacksQuestionsResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.check_new_feedbacks_questions() == "DESERIALIZED DATA"
				NewFeedbacksQuestionsResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/new-feedbacks-questions"
				assert session.last_call_params is None

	@pytest.mark.asyncio()
	async def test_get_question_count_unanswered(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)

		with patch("wb_api.feedback.async_api.QuestionCountUnansweredResponse") as QuestionCountUnansweredResponseMock:
			QuestionCountUnansweredResponseMock.model_validate_json = Mock()
			QuestionCountUnansweredResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_question_count_unanswered() == "DESERIALIZED DATA"
				QuestionCountUnansweredResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/questions/count-unanswered"
				assert session.last_call_params is None

	@pytest.mark.asyncio()
	async def test_get_question_count(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)

		with patch("wb_api.feedback.async_api.QuestionCountResponse") as QuestionCountResponseMock:
			QuestionCountResponseMock.model_validate_json = Mock()
			QuestionCountResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_question_count() == "DESERIALIZED DATA"
				QuestionCountResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/questions/count"
				assert session.last_call_params == QuestionCountRequest().as_request_params()

				session.reset()
				request = QuestionCountRequest(is_answered=True, date_from=get(2025, 1, 1))
				assert await api.get_question_count(request) == "DESERIALIZED DATA"
				assert session.last_call_method == "GET"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/questions/count"
				assert session.last_call_params == request.as_request_params()

	@pytest.mark.asyncio()
	async def test_get_question_list(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = QuestionListRequest(is_answered=True, take=100, skip=0)

		with patch("wb_api.feedback.async_api.QuestionListResponse") as QuestionListResponseMock:
			QuestionListResponseMock.model_validate_json = Mock()
			QuestionListResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_question_list(request) == "DESERIALIZED DATA"
				QuestionListResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/questions"
				assert session.last_call_params == request.as_request_params()

	@pytest.mark.asyncio()
	async def test_mark_question_as_read(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = QuestionMarkAsReadRequest(id="question-id", was_viewed=True)

		with patch("wb_api.feedback.async_api.QuestionMarkAsReadResponse") as QuestionMarkAsReadResponseMock:
			QuestionMarkAsReadResponseMock.model_validate_json = Mock()
			QuestionMarkAsReadResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.mark_question_as_read(request) == "DESERIALIZED DATA"
				QuestionMarkAsReadResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "PATCH"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/questions"
				assert session.last_call_json == request.as_request_payload()

	@pytest.mark.asyncio()
	async def test_reject_question(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = QuestionRejectRequest.create("question-id", "question-answer")

		with patch("wb_api.feedback.async_api.QuestionRejectResponse") as QuestionRejectResponseMock:
			QuestionRejectResponseMock.model_validate_json = Mock()
			QuestionRejectResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.reject_question(request) == "DESERIALIZED DATA"
				QuestionRejectResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "PATCH"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/questions"
				assert session.last_call_json == request.as_request_payload()

	@pytest.mark.asyncio()
	async def test_add_question_answer(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = QuestionAnswerAddRequest.create("question-id", "question-answer")

		with patch("wb_api.feedback.async_api.QuestionAnswerAddResponse") as QuestionAnswerAddResponseMock:
			QuestionAnswerAddResponseMock.model_validate_json = Mock()
			QuestionAnswerAddResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.add_question_answer(request) == "DESERIALIZED DATA"
				QuestionAnswerAddResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "PATCH"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/questions"
				assert session.last_call_json == request.as_request_payload()

	@pytest.mark.asyncio()
	async def test_update_question_answer(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = QuestionAnswerUpdateRequest.create("question-id", "question-answer")

		with patch("wb_api.feedback.async_api.QuestionAnswerUpdateResponse") as QuestionAnswerUpdateResponseMock:
			QuestionAnswerUpdateResponseMock.model_validate_json = Mock()
			QuestionAnswerUpdateResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.update_question_answer(request) == "DESERIALIZED DATA"
				QuestionAnswerUpdateResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "PATCH"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/questions"
				assert session.last_call_json == request.as_request_payload()

	@pytest.mark.asyncio()
	async def test_get_question(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = QuestionGetRequest(id="question-id")

		with patch("wb_api.feedback.async_api.QuestionGetResponse") as QuestionGetResponseMock:
			QuestionGetResponseMock.model_validate_json = Mock()
			QuestionGetResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_question(request) == "DESERIALIZED DATA"
				QuestionGetResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/question"
				assert session.last_call_params == request.as_request_params()

	@pytest.mark.asyncio()
	async def test_get_feedback_count_unanswered(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)

		with patch("wb_api.feedback.async_api.FeedbackCountUnansweredResponse") as FeedbackCountUnansweredResponseMock:
			FeedbackCountUnansweredResponseMock.model_validate_json = Mock()
			FeedbackCountUnansweredResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_feedback_count_unanswered() == "DESERIALIZED DATA"
				FeedbackCountUnansweredResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/count-unanswered"
				assert session.last_call_params is None

	@pytest.mark.asyncio()
	async def test_get_feedback_count(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)

		with patch("wb_api.feedback.async_api.FeedbackCountResponse") as FeedbackCountResponseMock:
			FeedbackCountResponseMock.model_validate_json = Mock()
			FeedbackCountResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_feedback_count() == "DESERIALIZED DATA"
				FeedbackCountResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/count"
				assert session.last_call_params == FeedbackCountRequest().as_request_params()

				session.reset()
				request = FeedbackCountRequest(is_answered=True, date_from=get(2025, 1, 1))
				assert await api.get_feedback_count(request) == "DESERIALIZED DATA"
				assert session.last_call_method == "GET"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/count"
				assert session.last_call_params == request.as_request_params()

	@pytest.mark.asyncio()
	async def test_get_feedback_list(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = FeedbackListRequest(is_answered=True, take=100, skip=0)

		with patch("wb_api.feedback.async_api.FeedbackListResponse") as FeedbackListResponseMock:
			FeedbackListResponseMock.model_validate_json = Mock()
			FeedbackListResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_feedback_list(request) == "DESERIALIZED DATA"
				FeedbackListResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks"
				assert session.last_call_params == request.as_request_params()

	@pytest.mark.asyncio()
	async def test_get_feedback_supplier_valuations(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = FeedbackSupplierValuationsRequest(locale="zh")

		with patch("wb_api.feedback.async_api.FeedbackSupplierValuationsResponse") as FeedbackSupplierValuationsResponseMock:
			FeedbackSupplierValuationsResponseMock.model_validate_json = Mock()
			FeedbackSupplierValuationsResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_feedback_supplier_valuations() == "DESERIALIZED DATA"
				FeedbackSupplierValuationsResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/supplier-valuations"
				assert session.last_call_headers == FeedbackSupplierValuationsRequest().as_request_params()

				session.reset()
				assert await api.get_feedback_supplier_valuations(request) == "DESERIALIZED DATA"
				assert session.last_call_method == "GET"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/supplier-valuations"
				assert session.last_call_headers == request.as_request_headers()

	@pytest.mark.asyncio()
	async def test_report_feedback_text(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = FeedbackTextReportRequest(id="question-id", supplier_feedback_valuation=512)

		with patch.object(api, "validate_response") as validate_response_mock:
			assert await api.report_feedback_text(request) is None
			validate_response_mock.assert_called_once_with(session.response, HTTPStatus.NO_CONTENT)
			assert session.last_call_method == "POST"
			assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/actions"
			assert session.last_call_json == request.as_request_payload()

	@pytest.mark.asyncio()
	async def test_report_feedback_product(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = FeedbackProductReportRequest(id="question-id", supplier_product_valuation=512)

		with patch.object(api, "validate_response") as validate_response_mock:
			assert await api.report_feedback_product(request) is None
			validate_response_mock.assert_called_once_with(session.response, HTTPStatus.NO_CONTENT)
			assert session.last_call_method == "POST"
			assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/actions"
			assert session.last_call_json == request.as_request_payload()

	@pytest.mark.asyncio()
	async def test_add_feedback_answer(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = FeedbackAnswerAddRequest(id="feedback-id", text="feedback-answer")

		with patch.object(api, "validate_response") as validate_response_mock:
			assert await api.add_feedback_answer(request) is None
			validate_response_mock.assert_called_once_with(session.response, HTTPStatus.NO_CONTENT)
			assert session.last_call_method == "POST"
			assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/answer"
			assert session.last_call_json == request.as_request_payload()

	@pytest.mark.asyncio()
	async def test_update_feedback_answer(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = FeedbackAnswerUpdateRequest(id="feedback-id", text="feedback-answer")

		with patch.object(api, "validate_response") as validate_response_mock:
			assert await api.update_feedback_answer(request) is None
			validate_response_mock.assert_called_once_with(session.response, HTTPStatus.NO_CONTENT)
			assert session.last_call_method == "PATCH"
			assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/answer"
			assert session.last_call_json == request.as_request_payload()

	@pytest.mark.asyncio()
	async def test_return_feedback_order(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = FeedbackOrderReturnRequest(feedback_id="feedback-id")

		with patch("wb_api.feedback.async_api.FeedbackOrderReturnResponse") as FeedbackOrderReturnResponseMock:
			FeedbackOrderReturnResponseMock.model_validate_json = Mock()
			FeedbackOrderReturnResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.return_feedback_order(request) == "DESERIALIZED DATA"
				FeedbackOrderReturnResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "POST"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/order/return"
				assert session.last_call_json == request.as_request_payload()

	@pytest.mark.asyncio()
	async def test_get_feedback(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = FeedbackGetRequest(id="feedback-id")

		with patch("wb_api.feedback.async_api.FeedbackGetResponse") as FeedbackGetResponseMock:
			FeedbackGetResponseMock.model_validate_json = Mock()
			FeedbackGetResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_feedback(request) == "DESERIALIZED DATA"
				FeedbackGetResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/feedback"
				assert session.last_call_params == request.as_request_params()

	@pytest.mark.asyncio()
	async def test_get_feedback_archive_list(self):
		session = FakeAsyncSession("RAW DATA")
		config = AsyncConfig(session, BaseURL)		# type: ignore - for testing purposes
		api = AsyncFeedbackAPI(config)
		request = FeedbackArchiveListRequest(take=100, skip=0)

		with patch("wb_api.feedback.async_api.FeedbackArchiveListResponse") as FeedbackArchiveListResponseMock:
			FeedbackArchiveListResponseMock.model_validate_json = Mock()
			FeedbackArchiveListResponseMock.model_validate_json.return_value = "DESERIALIZED DATA"

			with patch.object(api, "validate_response") as validate_response_mock:
				assert await api.get_feedback_archive_list(request) == "DESERIALIZED DATA"
				FeedbackArchiveListResponseMock.model_validate_json.assert_called_once_with("RAW DATA")
				validate_response_mock.assert_called_once_with(session.response)
				assert session.last_call_method == "GET"
				assert session.last_call_url == "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/archive"
				assert session.last_call_params == request.as_request_params()
