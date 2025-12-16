from wb_api.base.config import Config

from aiohttp.client import ClientSession


class AsyncConfig(Config[ClientSession]):
	pass
