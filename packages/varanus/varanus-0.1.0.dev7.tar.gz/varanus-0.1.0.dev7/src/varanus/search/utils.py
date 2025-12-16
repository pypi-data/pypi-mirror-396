import datetime
from typing import Mapping, TypeAlias

from django.utils.datastructures import MultiValueDict
from django.utils.dateparse import parse_date

StringValues: TypeAlias = dict[str, list[str]]


def string_data(data) -> StringValues:
    if isinstance(data, MultiValueDict):
        return {str(key): [str(v) for v in values] for key, values in data.lists()}
    elif isinstance(data, Mapping):
        return {
            str(key): (
                [str(v) for v in values]
                if isinstance(values, (list, tuple))
                else ([] if values is None else [str(values)])
            )
            for key, values in data.items()
        }
    return {}


def date_value(field_data: StringValues, name: str) -> datetime.date | None:
    if name not in field_data:
        return None
    if not field_data[name]:
        return None
    return parse_date(field_data[name][0])


class Namer:
    def __init__(self, prefix: str):
        self.prefix = prefix

    def __getitem__(self, key) -> str:
        return f"{self.prefix}{key}"
