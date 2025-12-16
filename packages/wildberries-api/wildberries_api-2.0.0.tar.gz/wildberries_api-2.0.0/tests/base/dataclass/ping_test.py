from wb_api.base.dataclass.ping import Response

from arrow import get


class TestResponse:
	def test_ts_is_arrow(self):
		assert Response.ts_is_arrow("2025-01-01T12:30:30+00:00") == get(2025, 1, 1, 12, 30, 30)
