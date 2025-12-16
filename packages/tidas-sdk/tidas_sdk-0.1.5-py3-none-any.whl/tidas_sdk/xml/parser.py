"""
XML parsing helpers that convert ILCD XML into the JSON-like structure
used by the SDK.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
from xml.dom import minidom
from xml.dom.minidom import Node

__all__ = ["dataset_from_xml"]


def dataset_from_xml(data: str | bytes | Path) -> Mapping[str, Any]:
    """
    Parse an ILCD XML payload and return a JSON-style mapping.
    """
    xml_text = _read_payload(data)
    try:
        document = minidom.parseString(xml_text)
    except Exception as exc:  # pragma: no cover - minidom type varies
        raise ValueError("Failed to parse ILCD XML payload.") from exc

    root = document.documentElement
    if root is None:
        raise ValueError("XML payload does not contain a root element.")

    payload = {root.tagName: _node_to_mapping(root)}
    document.unlink()
    return payload


def _read_payload(data: str | bytes | Path) -> str:
    if isinstance(data, Path):
        return data.read_text(encoding="utf-8")
    if isinstance(data, bytes):
        return data.decode("utf-8")
    return data


def _node_to_mapping(node: Node) -> Any:
    if node.nodeType != Node.ELEMENT_NODE:
        return None

    element = node  # preserve minidom typing info
    result: dict[str, Any] = {}

    if element.attributes:
        for index in range(element.attributes.length):
            attr = element.attributes.item(index)
            if attr is None:
                continue
            result[f"@{attr.name}"] = attr.value

    child_elements: list[Node] = []
    text_parts: list[str] = []

    for child in element.childNodes:
        if child.nodeType == Node.ELEMENT_NODE:
            child_elements.append(child)
        elif child.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
            data = child.data.strip()
            if data:
                text_parts.append(data)

    if child_elements:
        grouped: dict[str, list[Any]] = {}
        for child in child_elements:
            grouped.setdefault(child.tagName, []).append(_node_to_mapping(child))
        for tag, items in grouped.items():
            result[tag] = items[0] if len(items) == 1 else items

    text_value = " ".join(text_parts).strip()
    if text_value:
        result["#text"] = text_value

    if not result:
        return None

    if (
        "#text" in result
        and len(result) == 1
        and not child_elements
        and not (element.attributes and element.attributes.length)
    ):
        return result["#text"]

    return result
