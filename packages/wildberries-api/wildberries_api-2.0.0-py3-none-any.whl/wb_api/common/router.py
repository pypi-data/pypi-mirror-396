from wb_api.base.router import Router
from wb_api.generic.functools import cache


class CommonRouter(Router):
	@cache
	def ping(self):
		return f"{self.base_url}/ping"
