from wb_api.base.config import Config

from requests.sessions import Session


class SyncConfig(Config[Session]):
	pass
