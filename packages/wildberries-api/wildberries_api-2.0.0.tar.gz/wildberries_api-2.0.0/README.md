# wildberries-api [![codecov](https://codecov.io/gh/Kirill-Lekhov/wildberries-api/graph/badge.svg?token=PTPIWKPMQI)](https://codecov.io/gh/Kirill-Lekhov/wildberries-api)
Wildberries API client

## Installation
```shell
# Sync only mode
pip install wildberries-api[sync]
# Async only mode
pip install wildberries-api[async]
# All modes
pip install wildberries-api[all]
```

## Instantiating
There are several ways to work with the API (synchronous and asynchronous). Both interfaces have the same signatures, the only difference is the need to use async/await keywords.

```python
from wb_api.sync_api import SyncAPI		# Sync mode
from wb_api.async_api import AsyncAPI		# Async mode
from wb_api.const import BaseURL


def main() -> None:
	api = SyncAPI.build(
		token="...",
		base_url=BaseURL,		# (optional) may be used for test circuits
	)

	# Do things here...


async def main() -> None:
	api = await AsyncAPI.build(
		token="...",
		base_url=BaseURL,		# (optional) may be used for test circuits
	)

	# Do things here...

	await api.close()
```


## Where can I get token?
See [official docs](https://dev.wildberries.ru/openapi/api-information#tag/Avtorizaciya/Kak-sozdat-token).

## Common API
### Check connection
```python
# Sync mode
from wb_api.sync_api import SyncAPI


api = SyncAPI.build(...)
response = api.common.ping()
```

Docs: https://dev.wildberries.ru/openapi/api-information#tag/Proverka-podklyucheniya-k-WB-API

## Feedback API
### Check connection
```python
# Sync mode
from wb_api.sync_api import SyncAPI


api = SyncAPI.build(...)
response = api.feedback.ping()
```

Docs: https://dev.wildberries.ru/openapi/api-information#tag/Proverka-podklyucheniya-k-WB-API

### Check new questions and feedbacks existing
```python
# Sync mode
from wb_api.sync_api import SyncAPI


api = SyncAPI.build(...)
response = api.feedback.check_new_feedbacks_questions()
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Voprosy/paths/~1api~1v1~1new-feedbacks-questions/get

### Get count of unanswered questions
```python
# Sync mode
from wb_api.sync_api import SyncAPI


api = SyncAPI.build(...)
response = api.feedback.get_question_count_unanswered()
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Voprosy/paths/~1api~1v1~1questions~1count-unanswered/get

### Get count of questions
```python
# Sync mode
from wb_api.sync_api import SyncAPI
from wb_api.feedback.dataclass import QuestionCountRequest


api = SyncAPI.build(...)
response = api.feedback.get_question_count()
# or
request = QuestionCountRequest(is_answered=False, ...)
response = api.feedback.get_question_count(request)
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Voprosy/paths/~1api~1v1~1questions~1count/get

### Get question list
```python
# Sync mode
from wb_api.sync_api import SyncAPI
from wb_api.feedback.dataclass import QuestionListRequest


api = SyncAPI.build(...)
request = QuestionListRequest(is_answered=False, take=100, skip=0)
response = api.feedback.get_question_list(request)
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Voprosy/paths/~1api~1v1~1questions/get

### Mark question as read
```python
# Sync mode
from wb_api.sync_api import SyncAPI
from wb_api.feedback.dataclass import QuestionMarkAsReadRequest


api = SyncAPI.build(...)
request = QuestionMarkAsReadRequest(id="question-id", was_viewed=True)
response = api.feedback.mark_question_as_read(request)
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Voprosy/paths/~1api~1v1~1questions/patch

### Reject question
```python
# Sync mode
from wb_api.sync_api import SyncAPI
from wb_api.feedback.dataclass import QuestionRejectRequest


api = SyncAPI.build(...)
request = QuestionRejectRequest.create("question-id", "reject-reason")
response = api.feedback.reject_question(request)
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Voprosy/paths/~1api~1v1~1questions/patch

### Add question answer
```python
# Sync mode
from wb_api.sync_api import SyncAPI
from wb_api.feedback.dataclass import QuestionAnswerAddRequest


api = SyncAPI.build(...)
request = QuestionAnswerAddRequest.create("question-id", "question-answer")
response = api.feedback.add_question_answer(request)
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Voprosy/paths/~1api~1v1~1questions/patch

### Update question answer
```python
# Sync mode
from wb_api.sync_api import SyncAPI
from wb_api.feedback.dataclass import QuestionAnswerUpdateRequest


api = SyncAPI.build(...)
request = QuestionAnswerUpdateRequest.create("question-id", "question-answer")
response = api.feedback.update_question_answer(request)
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Voprosy/paths/~1api~1v1~1questions/patch

### Get question
```python
# Sync mode
from wb_api.sync_api import SyncAPI
from wb_api.feedback.dataclass import QuestionGetRequest


api = SyncAPI.build(...)
request = QuestionGetRequest(id="question-id")
response = api.feedback.get_question(request)
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Voprosy/paths/~1api~1v1~1question/get

### Get count of unanswered feedbacks
```python
# Sync mode
from wb_api.sync_api import SyncAPI


api = SyncAPI.build(...)
response = api.feedback.get_feedback_count_unanswered()
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Otzyvy/paths/~1api~1v1~1feedbacks~1count-unanswered/get

### Get count of feedbacks
```python
# Sync mode
from wb_api.sync_api import SyncAPI
from wb_api.feedback.dataclass import FeedbackCountRequest


api = SyncAPI.build(...)
response = api.feedback.get_feedback_count()
# or
request = FeedbackCountRequest(is_answered=False)
response = api.feedback.get_feedback_count(request)
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Otzyvy/paths/~1api~1v1~1feedbacks~1count/get

### Get feedback list
```python
# Sync mode
from wb_api.sync_api import SyncAPI
from wb_api.feedback.dataclass import FeedbackListRequest


api = SyncAPI.build(...)
request = FeedbackListRequest(is_answered=False, take=100, skip=0)
response = api.feedback.get_feedback_list(request)
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Otzyvy/paths/~1api~1v1~1feedbacks/get

### Get feedback supplier valuations
```python
# Sync mode
from wb_api.sync_api import SyncAPI
from wb_api.feedback.dataclass import FeedbackSupplierValuationsRequest


api = SyncAPI.build(...)
response = api.feedback.get_feedback_supplier_valuations()
# or
request = FeedbackSupplierValuationsRequest(locale="zh")
response = api.feedback.get_feedback_supplier_valuations(request)
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Otzyvy/paths/~1api~1v1~1supplier-valuations/get

### Report feedback text
```python
# Sync mode
from wb_api.sync_api import SyncAPI
from wb_api.feedback.dataclass import FeedbackTextReportRequest


api = SyncAPI.build(...)
request = FeedbackTextReportRequest(id="feedback-id", supplier_feedback_valuation=1024)
response = api.feedback.report_feedback_text(request)
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Otzyvy/paths/~1api~1v1~1feedbacks~1actions/post

### Report feedback product
```python
# Sync mode
from wb_api.sync_api import SyncAPI
from wb_api.feedback.dataclass import FeedbackProductReportRequest


api = SyncAPI.build(...)
request = FeedbackProductReportRequest(id="feedback-id", supplier_product_valuation=1024)
response = api.feedback.report_feedback_product(request)
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Otzyvy/paths/~1api~1v1~1feedbacks~1actions/post

### Add feedback answer
```python
# Sync mode
from wb_api.sync_api import SyncAPI
from wb_api.feedback.dataclass import FeedbackAnswerAddRequest


api = SyncAPI.build(...)
request = request = FeedbackAnswerAddRequest(id="feedback-id", text="feedback-answer")
response = api.feedback.add_feedback_answer(request)
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Otzyvy/paths/~1api~1v1~1feedbacks~1answer/post

### Update feedback answer
```python
# Sync mode
from wb_api.sync_api import SyncAPI
from wb_api.feedback.dataclass import FeedbackAnswerUpdateRequest


api = SyncAPI.build(...)
request = FeedbackAnswerUpdateRequest(id="feedback-id", text="feedback-answer")
response = api.feedback.update_feedback_answer(request)
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Otzyvy/paths/~1api~1v1~1feedbacks~1answer/patch

### Return order by feedback id
```python
# Sync mode
from wb_api.sync_api import SyncAPI
from wb_api.feedback.dataclass import FeedbackOrderReturnRequest


api = SyncAPI.build(...)
request = FeedbackOrderReturnRequest(feedback_id="feedback-id")
response = api.feedback.return_feedback_order(request)
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Otzyvy/paths/~1api~1v1~1feedbacks~1order~1return/post

### Get feedback
```python
# Sync mode
from wb_api.sync_api import SyncAPI
from wb_api.feedback.dataclass import FeedbackGetRequest


api = SyncAPI.build(...)
request = FeedbackGetRequest(id="feedback-id")
response = api.feedback.get_feedback(request)
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Otzyvy/paths/~1api~1v1~1feedback/get

### Get archive feedback list
```python
# Sync mode
from wb_api.sync_api import SyncAPI
from wb_api.feedback.dataclass import FeedbackArchiveListRequest


api = SyncAPI.build(...)
request = FeedbackArchiveListRequest(take=100, skip=0)
response = api.feedback.get_feedback_archive_list(request)
```

Docs: https://dev.wildberries.ru/openapi/user-communication#tag/Otzyvy/paths/~1api~1v1~1feedbacks~1archive/get
