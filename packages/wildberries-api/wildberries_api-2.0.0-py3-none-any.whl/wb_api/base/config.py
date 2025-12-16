from typing import TypeVar, Generic, Protocol, Type, ClassVar


T = TypeVar("T")


class BaseURL(Protocol):
	COMMON: ClassVar[str]
	FEEDBACK: ClassVar[str]


class Config(Generic[T]):
	session: T
	base_url: Type[BaseURL]

	def __init__(self, session: T, base_url: Type[BaseURL]) -> None:
		self.session = session
		self.base_url = base_url
