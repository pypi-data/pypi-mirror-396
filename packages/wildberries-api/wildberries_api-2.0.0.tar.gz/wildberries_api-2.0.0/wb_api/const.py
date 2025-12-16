from enum import Enum
from typing import ClassVar


class BaseURL:
	COMMON: ClassVar[str] = "https://common-api.wildberries.ru"
	FEEDBACK: ClassVar[str] = "https://feedbacks-api.wildberries.ru"


class Header(Enum):
	AUTHORIZATION = "Authorization"
	LOCALE = "X-Locale"
