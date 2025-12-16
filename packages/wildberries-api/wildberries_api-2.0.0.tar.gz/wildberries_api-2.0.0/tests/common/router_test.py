from wb_api.common.router import CommonRouter


class TestCommonRouter:
	def test_ping(self):
		router = CommonRouter("")
		assert router.ping() == "/ping"

