"""
High level wrapper for FlowProperty datasets.
"""
from __future__ import annotations

from typing import Any, Mapping, cast
from uuid import uuid4

from ..core.base import TidasEntity
from ..generated.tidas_flowproperties import (
    FlowPropertyDataSetAdministrativeInformationDataEntryBy,
    FlowPropertyDataSetAdministrativeInformationPublicationAndOwnership,
    FlowPropertyDataSetFlowPropertiesInformationDataSetInformation,
    Flowproperties,
    FlowpropertiesFlowPropertyDataSet,
    FlowpropertiesFlowPropertyDataSetAdministrativeInformation,
    FlowpropertiesFlowPropertyDataSetFlowPropertiesInformation,
)
from .utils import default_timestamp, ensure_model, ensure_multilang


class TidasFlowProperty(TidasEntity[Flowproperties]):
    schema_name = "tidas_flowproperties.json"

    def __init__(
        self,
        initial_data: dict[str, Any] | Flowproperties | None = None,
        *,
        validate_on_init: bool = False,
    ) -> None:
        super().__init__(Flowproperties, initial_data, validate_on_init=validate_on_init)

    @property
    def flow_property_data_set(self) -> FlowpropertiesFlowPropertyDataSet:
        return cast(FlowpropertiesFlowPropertyDataSet, getattr(self.model, "flow_property_data_set"))

    @flow_property_data_set.setter
    def flow_property_data_set(
        self,
        value: FlowpropertiesFlowPropertyDataSet | Mapping[str, Any],
    ) -> None:
        TidasEntity.__setattr__(self, "flow_property_data_set", value)

    def ensure_defaults(self) -> None:
        dataset = ensure_model(self, "flow_property_data_set", FlowpropertiesFlowPropertyDataSet)
        dataset.xmlns = dataset.xmlns or "http://lca.jrc.it/ILCD/FlowProperty"
        dataset.xmlns_common = dataset.xmlns_common or "http://lca.jrc.it/ILCD/Common"
        dataset.xmlns_xsi = dataset.xmlns_xsi or "http://www.w3.org/2001/XMLSchema-instance"
        dataset.version = dataset.version or "1.1"
        dataset.xsi_schema_location = (
            dataset.xsi_schema_location
            or "http://lca.jrc.it/ILCD/FlowProperty ../../schemas/ILCD_FlowPropertyDataSet.xsd"
        )

        info = ensure_model(
            dataset,
            "flow_properties_information",
            FlowpropertiesFlowPropertyDataSetFlowPropertiesInformation,
        )
        data_info = ensure_model(
            info,
            "data_set_information",
            FlowPropertyDataSetFlowPropertiesInformationDataSetInformation,
        )
        if not data_info.common_uuid:
            data_info.common_uuid = str(uuid4())
        ensure_multilang(data_info, "common_name")
        ensure_multilang(data_info, "common_synonyms")
        ensure_multilang(data_info, "common_general_comment")

        admin = ensure_model(
            dataset,
            "administrative_information",
            FlowpropertiesFlowPropertyDataSetAdministrativeInformation,
        )
        data_entry = ensure_model(
            admin,
            "data_entry_by",
            FlowPropertyDataSetAdministrativeInformationDataEntryBy,
        )
        if not data_entry.common_time_stamp:
            data_entry.common_time_stamp = default_timestamp()
        ensure_model(
            admin,
            "publication_and_ownership",
            FlowPropertyDataSetAdministrativeInformationPublicationAndOwnership,
        )
