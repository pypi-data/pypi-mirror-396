from wb_api.feedback.dataclass.feedback_archive_list import Request


class TestRequest:
	def test_as_request_params(self):
		assert Request(take=100, skip=0).as_request_params() == {
			"take": 100,
			"skip": 0,
		}
		assert Request(take=100, skip=0, nm_id=512, order="dateAsc").as_request_params() == {
			"take": 100,
			"skip": 0,
			"nmId": 512,
			"order": "dateAsc",
		}
