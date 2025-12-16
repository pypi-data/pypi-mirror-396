from wb_api.base.dataclass.base_request import BaseRequest


class TestBaseRequest:
	def test_as_request_params(self):
		request = BaseRequest()
		assert request.as_request_params() == {}

	def test_as_request_payload(self):
		request = BaseRequest()
		assert request.as_request_payload() == {}

	def test_as_request_headers(self):
		request = BaseRequest()
		assert request.as_request_headers() == {}
