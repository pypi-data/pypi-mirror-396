from wb_api.generic.requests.auth import JWTTokenAuth

from requests.models import Request


class TestJWTTokenAuth:
	def test___init__(self):
		auth = JWTTokenAuth("ACCESS_TOKEN")
		assert auth.token == "ACCESS_TOKEN"
		assert auth.header_label == "Authorization"

		auth = JWTTokenAuth("ACCESS_TOKEN", "X-Authorization")
		assert auth.token == "ACCESS_TOKEN"
		assert auth.header_label == "X-Authorization"

	def test___call__(self):
		auth = JWTTokenAuth("ACCESS_TOKEN", "X-Authorization")
		request = Request()
		request = auth(request)
		assert request.headers["X-Authorization"] == "ACCESS_TOKEN"
