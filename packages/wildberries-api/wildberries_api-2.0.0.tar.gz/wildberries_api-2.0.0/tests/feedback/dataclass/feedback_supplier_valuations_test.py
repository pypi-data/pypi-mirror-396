from wb_api.feedback.dataclass.feedback_supplier_valuations import Request
from wb_api.const import Header


class TestRequest:
	def test_as_request_headers(self):
		assert Request().as_request_headers() == {}
		assert Request(locale="zh").as_request_headers() == {Header.LOCALE.value: "zh"}
