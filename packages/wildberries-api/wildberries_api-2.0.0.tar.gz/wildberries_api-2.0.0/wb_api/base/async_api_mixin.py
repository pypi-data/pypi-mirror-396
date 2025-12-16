from wb_api.exception import InvalidResponseError, AuthorizationError, NotFoundError
from wb_api.base.async_config import AsyncConfig

from http import HTTPStatus

from aiohttp.client import ClientSession, ClientResponse


class AsyncAPIMixin:
	config: AsyncConfig

	def __init__(self, config: AsyncConfig) -> None:
		super().__init__(config)

	@property
	def session(self) -> ClientSession:
		return self.config.session

	def validate_response(self, response: ClientResponse, expected_status: HTTPStatus = HTTPStatus.OK) -> None:
		if response.status != expected_status:
			if response.status == HTTPStatus.FORBIDDEN or response.status == HTTPStatus.UNAUTHORIZED:
				raise AuthorizationError("Unauthorized")
			elif response.status == HTTPStatus.NOT_FOUND:
				raise NotFoundError("Resource was not found")

			raise InvalidResponseError("Response is not valid")
