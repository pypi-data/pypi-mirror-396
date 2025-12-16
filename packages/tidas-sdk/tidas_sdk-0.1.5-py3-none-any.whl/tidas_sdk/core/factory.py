"""
Factory helpers for constructing TIDAS entities.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Type, TypeVar, cast

from .base import TidasEntity, ValidationMode
from ..entities.contact import TidasContact
from ..entities.flow import TidasFlow
from ..entities.flow_property import TidasFlowProperty
from ..entities.life_cycle_model import TidasLifeCycleModel
from ..entities.lcia_method import TidasLCIAMethod
from ..entities.process import TidasProcess
from ..entities.source import TidasSource
from ..entities.unit_group import TidasUnitGroup

EntityT = TypeVar("EntityT", bound=TidasEntity[Any])

__all__ = [
    "create_process",
    "create_process_from_json",
    "create_process_from_xml",
    "create_processes_batch",
    "create_contact",
    "create_contact_from_json",
    "create_contacts_batch",
    "create_flow",
    "create_flow_from_json",
    "create_flows_batch",
    "create_source",
    "create_source_from_json",
    "create_sources_batch",
    "create_flow_property",
    "create_flow_property_from_json",
    "create_flow_properties_batch",
    "create_unit_group",
    "create_unit_group_from_json",
    "create_unit_groups_batch",
    "create_lcia_method",
    "create_lcia_method_from_json",
    "create_lcia_methods_batch",
    "create_life_cycle_model",
    "create_life_cycle_model_from_json",
    "create_life_cycle_models_batch",
    "TidasProcess",
    "TidasContact",
    "TidasFlow",
    "TidasSource",
    "TidasFlowProperty",
    "TidasUnitGroup",
    "TidasLCIAMethod",
    "TidasLifeCycleModel",
]


# ---------------------------------------------------------------------------
# Process
# ---------------------------------------------------------------------------

def create_process(
    data: Mapping[str, Any] | None = None,
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> TidasProcess:
    return _create_entity(TidasProcess, data, validate, validation_mode)


def create_process_from_json(
    json_data: str | bytes | Path,
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> TidasProcess:
    return create_process(_parse_json_payload(json_data), validate=validate, validation_mode=validation_mode)


def create_process_from_xml(
    xml_data: str | bytes | Path,
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> TidasProcess:
    return create_process(_parse_xml_payload(xml_data), validate=validate, validation_mode=validation_mode)


def create_processes_batch(
    data_array: Iterable[Mapping[str, Any]],
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> list[TidasProcess]:
    return _create_batch(create_process, data_array, validate=validate, validation_mode=validation_mode)


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------

def create_contact(
    data: Mapping[str, Any] | None = None,
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> TidasContact:
    return _create_entity(TidasContact, data, validate, validation_mode)


def create_contact_from_json(
    json_data: str | bytes | Path,
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> TidasContact:
    return create_contact(_parse_json_payload(json_data), validate=validate, validation_mode=validation_mode)


def create_contacts_batch(
    data_array: Iterable[Mapping[str, Any]],
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> list[TidasContact]:
    return _create_batch(create_contact, data_array, validate=validate, validation_mode=validation_mode)


# ---------------------------------------------------------------------------
# Flow
# ---------------------------------------------------------------------------

def create_flow(
    data: Mapping[str, Any] | None = None,
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> TidasFlow:
    return _create_entity(TidasFlow, data, validate, validation_mode)


def create_flow_from_json(
    json_data: str | bytes | Path,
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> TidasFlow:
    return create_flow(_parse_json_payload(json_data), validate=validate, validation_mode=validation_mode)


def create_flows_batch(
    data_array: Iterable[Mapping[str, Any]],
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> list[TidasFlow]:
    return _create_batch(create_flow, data_array, validate=validate, validation_mode=validation_mode)


# ---------------------------------------------------------------------------
# Source
# ---------------------------------------------------------------------------

def create_source(
    data: Mapping[str, Any] | None = None,
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> TidasSource:
    return _create_entity(TidasSource, data, validate, validation_mode)


def create_source_from_json(
    json_data: str | bytes | Path,
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> TidasSource:
    return create_source(_parse_json_payload(json_data), validate=validate, validation_mode=validation_mode)


def create_sources_batch(
    data_array: Iterable[Mapping[str, Any]],
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> list[TidasSource]:
    return _create_batch(create_source, data_array, validate=validate, validation_mode=validation_mode)


# ---------------------------------------------------------------------------
# FlowProperty
# ---------------------------------------------------------------------------

def create_flow_property(
    data: Mapping[str, Any] | None = None,
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> TidasFlowProperty:
    return _create_entity(TidasFlowProperty, data, validate, validation_mode)


def create_flow_property_from_json(
    json_data: str | bytes | Path,
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> TidasFlowProperty:
    return create_flow_property(_parse_json_payload(json_data), validate=validate, validation_mode=validation_mode)


def create_flow_properties_batch(
    data_array: Iterable[Mapping[str, Any]],
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> list[TidasFlowProperty]:
    return _create_batch(create_flow_property, data_array, validate=validate, validation_mode=validation_mode)


# ---------------------------------------------------------------------------
# UnitGroup
# ---------------------------------------------------------------------------

def create_unit_group(
    data: Mapping[str, Any] | None = None,
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> TidasUnitGroup:
    return _create_entity(TidasUnitGroup, data, validate, validation_mode)


def create_unit_group_from_json(
    json_data: str | bytes | Path,
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> TidasUnitGroup:
    return create_unit_group(_parse_json_payload(json_data), validate=validate, validation_mode=validation_mode)


def create_unit_groups_batch(
    data_array: Iterable[Mapping[str, Any]],
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> list[TidasUnitGroup]:
    return _create_batch(create_unit_group, data_array, validate=validate, validation_mode=validation_mode)


# ---------------------------------------------------------------------------
# LCIAMethod
# ---------------------------------------------------------------------------

def create_lcia_method(
    data: Mapping[str, Any] | None = None,
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> TidasLCIAMethod:
    return _create_entity(TidasLCIAMethod, data, validate, validation_mode)


def create_lcia_method_from_json(
    json_data: str | bytes | Path,
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> TidasLCIAMethod:
    return create_lcia_method(_parse_json_payload(json_data), validate=validate, validation_mode=validation_mode)


def create_lcia_methods_batch(
    data_array: Iterable[Mapping[str, Any]],
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> list[TidasLCIAMethod]:
    return _create_batch(create_lcia_method, data_array, validate=validate, validation_mode=validation_mode)


# ---------------------------------------------------------------------------
# LifeCycleModel
# ---------------------------------------------------------------------------

def create_life_cycle_model(
    data: Mapping[str, Any] | None = None,
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> TidasLifeCycleModel:
    return _create_entity(TidasLifeCycleModel, data, validate, validation_mode)


def create_life_cycle_model_from_json(
    json_data: str | bytes | Path,
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> TidasLifeCycleModel:
    return create_life_cycle_model(_parse_json_payload(json_data), validate=validate, validation_mode=validation_mode)


def create_life_cycle_models_batch(
    data_array: Iterable[Mapping[str, Any]],
    *,
    validate: bool = False,
    validation_mode: ValidationMode = "pydantic",
) -> list[TidasLifeCycleModel]:
    return _create_batch(create_life_cycle_model, data_array, validate=validate, validation_mode=validation_mode)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_json_payload(json_data: str | bytes | Path) -> Mapping[str, Any]:
    if isinstance(json_data, Path):
        content = json_data.read_text(encoding="utf-8")
    elif isinstance(json_data, bytes):
        content = json_data.decode("utf-8")
    else:
        content = json_data
    return cast(Mapping[str, Any], json.loads(content))


def _parse_xml_payload(xml_data: str | bytes | Path) -> Mapping[str, Any]:
    from ..xml.parser import dataset_from_xml

    return dataset_from_xml(xml_data)


def _create_entity(
    entity_cls: Type[EntityT],
    data: Mapping[str, Any] | EntityT | None,
    validate: bool,
    validation_mode: ValidationMode,
) -> EntityT:
    payload: Any
    if isinstance(data, Mapping):
        payload = dict(data)
    else:
        payload = data

    entity = entity_cls(
        payload,
        validate_on_init=validate and validation_mode == "pydantic",
    )
    if validate:
        entity.validate(mode=validation_mode)
    return entity


def _create_batch(
    factory: Any,
    data_array: Iterable[Mapping[str, Any]],
    *,
    validate: bool,
    validation_mode: ValidationMode,
) -> list[Any]:
    return [
        factory(data, validate=validate, validation_mode=validation_mode)
        for data in data_array
    ]
