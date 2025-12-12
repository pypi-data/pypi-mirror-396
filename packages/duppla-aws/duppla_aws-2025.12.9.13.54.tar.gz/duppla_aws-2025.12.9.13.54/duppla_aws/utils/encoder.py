# pyright: reportUnknownVariableType=false
import dataclasses
import datetime
from collections import deque
from decimal import Decimal
from enum import Enum
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
import json
from pathlib import Path, PurePath
from re import Pattern
from types import GeneratorType
from typing import Any, Dict, Type, Union
from uuid import UUID

from collections.abc import Set, Sequence, Callable, Mapping
from pydantic import AnyUrl, BaseModel, NameEmail, SecretBytes, SecretStr
from pydantic_core import PydanticUndefinedType as UndefinedType, Url
from pydantic_extra_types.color import Color
from typing_extensions import TypeAlias

JSON: TypeAlias = Union[None, str, int, float, bool, Mapping[str, "JSON"], Sequence["JSON"]]  # fmt:skip


def jsonable_encoder(obj: Any, exclude_nulls: bool = False) -> JSON:
    if isinstance(obj, BaseModel):
        return jsonable_encoder(
            obj.model_dump(mode="json", exclude_none=exclude_nulls), exclude_nulls
        )
    if dataclasses.is_dataclass(obj):
        return jsonable_encoder(dataclasses.asdict(obj), exclude_nulls)  # type: ignore
    if isinstance(obj, (str, int, float, type(None))):
        return obj
    if isinstance(obj, (Sequence, Set, GeneratorType)):
        return [jsonable_encoder(v, exclude_nulls) for v in obj]
    if isinstance(obj, Mapping):
        return {k: jsonable_encoder(v, exclude_nulls) for k, v in obj.items()}
    for type_, encoder in ENCODERS_BY_TYPE.items():
        if isinstance(obj, type_):
            return encoder(obj)
    return str(obj)


def jsonable_dumps(obj: Any, exclude_nulls: bool = False) -> str:
    return json.dumps(jsonable_encoder(obj, exclude_nulls))


def decimal_encoder(dec_value: Decimal) -> Union[int, float]:
    if dec_value.as_tuple().exponent >= 0:  # type: ignore[operator]
        return int(dec_value)
    else:
        return float(dec_value)


ENCODERS_BY_TYPE: Dict[Type[Any], Callable[[Any], Any]] = {
    BaseModel: lambda o: o.model_dump(mode="json"),
    bytes: bytes.decode,
    Color: str,
    datetime.date: datetime.date.isoformat,
    datetime.datetime: datetime.datetime.isoformat,
    datetime.time: datetime.time.isoformat,
    datetime.timedelta: datetime.timedelta.total_seconds,
    Decimal: decimal_encoder,
    Enum: lambda o: o.value,
    frozenset: list,
    deque: list,
    GeneratorType: list,
    IPv4Address: str,
    IPv4Interface: str,
    IPv4Network: str,
    IPv6Address: str,
    IPv6Interface: str,
    IPv6Network: str,
    NameEmail: str,
    PurePath: str,
    Path: str,
    Pattern: lambda o: o.pattern,
    SecretBytes: str,
    SecretStr: str,
    set: list,
    UUID: str,
    Url: str,
    AnyUrl: str,
    UndefinedType: lambda _: None,
    tuple: list,
    Type: lambda o: o.__name__,
}
