"""
Shared helpers for entity wrappers.
"""
from __future__ import annotations

from datetime import datetime, timezone
from collections.abc import Mapping
from typing import Any, Type, TypeVar, cast

from ..core.multilang import MultiLangList

T = TypeVar("T")


def ensure_model(parent: Any, attr: str, model_cls: Type[T]) -> T:
    """
    Ensure the given attribute on *parent* is an instance of *model_cls*.
    """
    value = getattr(parent, attr, None)
    if value is None:
        ctor = getattr(model_cls, "model_construct", None)
        value = cast(T, ctor()) if callable(ctor) else model_cls()
        setattr(parent, attr, value)
    elif isinstance(value, Mapping) and not isinstance(value, model_cls):
        # If a raw mapping slipped through, wrap it into the expected model.
        try:
            value = cast(T, model_cls.model_validate(value))
        except Exception:
            ctor = getattr(model_cls, "model_construct", None)
            value = cast(T, ctor(**value) if callable(ctor) else model_cls(**value))
        setattr(parent, attr, value)
    return cast(T, value)


def ensure_multilang(container: Any, attr: str) -> MultiLangList:
    """
    Guarantee that the attribute is a MultiLangList instance.
    """
    current = getattr(container, attr, None)
    if isinstance(current, MultiLangList):
        return current
    if isinstance(current, list):
        ml = MultiLangList(current)
    elif current:
        ml = MultiLangList([current])
    else:
        ml = MultiLangList()
    setattr(container, attr, ml)
    return ml


def default_timestamp() -> datetime:
    """
    Produce a timezone-aware timestamp for fields expecting `datetime`.
    """
    return datetime.now(tz=timezone.utc)
