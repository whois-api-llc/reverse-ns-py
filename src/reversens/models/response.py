import copy

from .base import BaseModel
import sys

if sys.version_info < (3, 9):
    import typing


def _string_value(values: dict, key: str) -> str:
    if key in values and values[key]:
        return str(values[key])
    return ''


def _float_value(values: dict, key: str) -> float:
    if key in values and values[key]:
        return float(values[key])
    return 0.0


def _int_value(values: dict, key: str) -> int:
    if key in values and values[key]:
        return int(values[key])
    return 0


def _list_value(values: dict, key: str) -> list:
    if key in values and type(values[key]) is list:
        return copy.deepcopy(values[key])
    return []


def _list_of_objects(values: dict, key: str, classname: str) -> list:
    r = []
    if key in values and type(values[key]) is list:
        r = [globals()[classname](x) for x in values[key]]
    return r


def _bool_value(values: dict, key: str) -> bool:
    if key in values and values[key]:
        return bool(values[key])
    return False


class Result(BaseModel):
    name: str
    first_seen: int
    last_visit: int

    def __init__(self, values):
        super().__init__()

        self.name = ''
        self.first_seen = 0
        self.last_visit = 0

        if values:
            self.name = _string_value(values, 'name')
            self.first_seen = _int_value(values, 'first_seen')
            self.last_visit = _int_value(values, 'last_visit')


class Response(BaseModel):
    _PAGE_SIZE = 300

    size: int
    current_page: str
    if sys.version_info < (3, 9):
        result: typing.List[Result]
    else:
        result: [Result]

    def __init__(self, values):
        super().__init__()

        self.size = 0
        self.current_page = ''
        self.result = []

        if values is not None:
            self.size = _int_value(values, 'size')
            self.current_page = _string_value(values, 'current_page')
            self.result = _list_of_objects(
                values, 'result', 'Result')

    def has_next(self) -> bool:
        return self.size >= Response._PAGE_SIZE


class ErrorMessage(BaseModel):
    code: int
    message: str

    def __init__(self, values):
        super().__init__()

        self.code = 0
        self.message = ''

        if values is not None:
            self.code = _int_value(values, 'code')
            self.message = _string_value(values, 'messages')
