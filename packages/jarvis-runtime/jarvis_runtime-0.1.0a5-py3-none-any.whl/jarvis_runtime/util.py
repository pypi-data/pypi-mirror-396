from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional, TypeVar, cast, overload


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


JsonObject = dict[str, Any]
JsonArray = list[Any]
T = TypeVar("T")


@overload
def as_type(value: Any, typ: type[dict], *, default: JsonObject) -> JsonObject: ...


@overload
def as_type(value: Any, typ: type[dict], *, default: None) -> Optional[JsonObject]: ...


@overload
def as_type(value: Any, typ: type[list], *, default: JsonArray) -> JsonArray: ...


@overload
def as_type(value: Any, typ: type[list], *, default: None) -> Optional[JsonArray]: ...


@overload
def as_type(value: Any, typ: type[str], *, default: str) -> str: ...


@overload
def as_type(value: Any, typ: type[str], *, default: None) -> Optional[str]: ...


@overload
def as_type(value: Any, typ: type[T], *, default: T) -> T: ...


def as_type(value: Any, typ: type[Any], *, default: Any) -> Any:
    if isinstance(value, typ):
        if typ is dict:
            return cast(JsonObject, value)
        if typ is list:
            return cast(JsonArray, value)
        return value
    return default


@overload
def get_as(mapping: Any, key: str, typ: type[dict], *, default: JsonObject) -> JsonObject: ...


@overload
def get_as(mapping: Any, key: str, typ: type[dict], *, default: None) -> Optional[JsonObject]: ...


@overload
def get_as(mapping: Any, key: str, typ: type[list], *, default: JsonArray) -> JsonArray: ...


@overload
def get_as(mapping: Any, key: str, typ: type[list], *, default: None) -> Optional[JsonArray]: ...


@overload
def get_as(mapping: Any, key: str, typ: type[str], *, default: str) -> str: ...


@overload
def get_as(mapping: Any, key: str, typ: type[str], *, default: None) -> Optional[str]: ...


@overload
def get_as(mapping: Any, key: str, typ: type[T], *, default: T) -> T: ...


def get_as(mapping: Any, key: str, typ: type[Any], *, default: Any) -> Any:
    if not isinstance(mapping, dict):
        return default
    return as_type(mapping.get(key), typ, default=default)
