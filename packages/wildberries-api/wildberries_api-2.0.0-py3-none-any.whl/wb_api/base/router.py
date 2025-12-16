from abc import ABC


class Router(ABC):
	base_url: str

	def __init__(self, base_url: str) -> None:
		self.base_url = base_url
