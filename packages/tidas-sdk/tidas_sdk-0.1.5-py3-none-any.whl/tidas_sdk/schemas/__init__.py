"""
Utilities for accessing packaged JSON Schema resources.
"""
from __future__ import annotations

import json
from importlib import resources
from typing import Any, cast

__all__ = ["load_schema", "schema_exists"]

SchemaType = dict[str, Any]
_SCHEMA_CACHE: dict[str, SchemaType] = {}


def load_schema(name: str) -> SchemaType:
    """
    Load a JSON schema bundled with the SDK, caching it for repeated use.
    """
    if name in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[name]

    schema_file = resources.files(__name__) / name
    if not schema_file.is_file():
        raise FileNotFoundError(f"Schema '{name}' is not packaged with the SDK.")

    with schema_file.open("r", encoding="utf-8") as handle:
        schema = cast(SchemaType, json.load(handle))

    _SCHEMA_CACHE[name] = schema
    return schema


def schema_exists(name: str) -> bool:
    """
    Check whether the given schema resource is bundled with the SDK.
    """
    schema_file = resources.files(__name__) / name
    return schema_file.is_file()
