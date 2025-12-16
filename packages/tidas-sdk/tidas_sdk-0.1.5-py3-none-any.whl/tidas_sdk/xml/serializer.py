"""
XML serialization helpers.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
from xml.sax.saxutils import escape

__all__ = ["dataset_to_xml"]

INDENT = "  "


def dataset_to_xml(dataset: Mapping[str, Any]) -> str:
    """
    Convert a dataset dictionary into ILCD-compatible XML.
    """
    if not dataset:
        raise ValueError("Cannot serialise an empty dataset.")

    if len(dataset) != 1:
        raise ValueError(
            "Expected a single root element in the dataset. "
            f"Received keys: {', '.join(dataset.keys())}"
        )

    root_tag, root_value = next(iter(dataset.items()))
    builder: list[str] = ['<?xml version="1.0" encoding="UTF-8"?>']
    _serialize_element(root_tag, root_value, builder, 0)
    return "\n".join(builder)


def _serialize_element(name: str, value: Any, builder: list[str], depth: int) -> None:
    """
    Recursively walk structures and append XML lines.
    """
    if isinstance(value, (str, int, float, bool)) or value is None:
        builder.append(_render_scalar(name, value, depth))
        return

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            _serialize_element(name, item, builder, depth)
        return

    if isinstance(value, Mapping):
        _render_mapping(name, value, builder, depth)
        return

    # Fallback for unexpected types
    builder.append(_render_scalar(name, value, depth))


def _render_scalar(name: str, value: Any, depth: int) -> str:
    text = _escape_text(value)
    indent = INDENT * depth
    if text == "":
        return f"{indent}<{name}/>"
    return f"{indent}<{name}>{text}</{name}>"


def _render_mapping(name: str, value: Mapping[str, Any], builder: list[str], depth: int) -> None:
    attributes: dict[str, str] = {}
    children: list[tuple[str, Any]] = []
    text_content: str | None = None

    for key, item in value.items():
        if key.startswith("@"):
            attr_name = key[1:]
            attributes[attr_name] = _escape_attribute(item)
        elif key == "#text":
            text_content = _escape_text(item)
        else:
            children.append((key, item))

    indent = INDENT * depth
    attr_str = "".join(f' {attr}="{val}"' for attr, val in attributes.items())

    if not children:
        if text_content is None or text_content == "":
            builder.append(f"{indent}<{name}{attr_str}/>")
        else:
            builder.append(f"{indent}<{name}{attr_str}>{text_content}</{name}>")
        return

    builder.append(f"{indent}<{name}{attr_str}>")
    if text_content not in (None, ""):
        builder.append(f"{INDENT * (depth + 1)}{text_content}")

    for child_name, child_value in children:
        _serialize_element(child_name, child_value, builder, depth + 1)

    builder.append(f"{indent}</{name}>")


def _escape_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return escape(str(value), {"'": "&apos;", '"': "&quot;"})


def _escape_attribute(value: Any) -> str:
    return _escape_text(value)
