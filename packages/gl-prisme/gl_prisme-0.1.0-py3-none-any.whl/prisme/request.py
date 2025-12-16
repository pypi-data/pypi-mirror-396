from datetime import date, datetime
from typing import TypeVar


class PrismeRequest[PrismeResponseType]:

    @classmethod
    def method(cls) -> str:
        raise NotImplementedError("Must be implemented in subclass")  # pragma: no cover

    @property
    def xml(self):
        raise NotImplementedError("Must be implemented in subclass")  # pragma: no cover

    @classmethod
    def response_class(cls) -> type[PrismeResponseType]:
        raise NotImplementedError("Must be implemented in subclass")  # pragma: no cover

    @staticmethod
    def prepare(value: str | datetime | date | None) -> str:
        if value is None:
            return ""
        if isinstance(value, datetime):
            value = f"{value:%Y-%m-%dT%H:%M:%S}"
        if isinstance(value, date):
            value = f"{value:%Y-%m-%d}"
        return str(value)


PrismeRequestType = TypeVar("PrismeRequestType", bound=PrismeRequest)


class PrismeResponse[PrismeRequestType]:
    def __init__(self, request: PrismeRequestType, xml: str):
        self.request = request
        self.xml = xml


PrismeResponseType = TypeVar("PrismeResponseType", bound=PrismeResponse)
