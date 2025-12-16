from wb_api.exception import InvalidResponseError, AuthorizationError, NotFoundError
from wb_api.base.sync_config import SyncConfig

from http import HTTPStatus

from requests.sessions import Session
from requests.models import Response


class SyncAPIMixin:
	config: SyncConfig

	def __init__(self, config: SyncConfig) -> None:
		super().__init__(config)

	@property
	def session(self) -> Session:
		return self.config.session

	def validate_response(self, response: Response, expected_status: HTTPStatus = HTTPStatus.OK) -> None:
		if response.status_code != expected_status:
			if response.status_code == HTTPStatus.FORBIDDEN or response.status_code == HTTPStatus.UNAUTHORIZED:
				raise AuthorizationError("Unauthorized")
			elif response.status_code == HTTPStatus.NOT_FOUND:
				raise NotFoundError("Resource was not found")

			raise InvalidResponseError("Response is not valid")
