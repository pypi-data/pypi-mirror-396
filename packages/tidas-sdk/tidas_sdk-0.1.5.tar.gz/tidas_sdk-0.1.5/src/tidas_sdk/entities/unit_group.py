"""
High level wrapper for UnitGroup datasets.
"""
from __future__ import annotations

from typing import Any, Mapping, cast
from uuid import uuid4

from ..core.base import TidasEntity
from ..generated.tidas_unitgroups import (
    UnitGroupDataSetAdministrativeInformationDataEntryBy,
    UnitGroupDataSetAdministrativeInformationPublicationAndOwnership,
    UnitGroupDataSetUnitGroupInformationDataSetInformation,
    Unitgroups,
    UnitgroupsUnitGroupDataSet,
    UnitgroupsUnitGroupDataSetAdministrativeInformation,
    UnitgroupsUnitGroupDataSetUnitGroupInformation,
)
from .utils import default_timestamp, ensure_model, ensure_multilang


class TidasUnitGroup(TidasEntity[Unitgroups]):
    schema_name = "tidas_unitgroups.json"

    def __init__(
        self,
        initial_data: dict[str, Any] | Unitgroups | None = None,
        *,
        validate_on_init: bool = False,
    ) -> None:
        super().__init__(Unitgroups, initial_data, validate_on_init=validate_on_init)

    @property
    def unit_group_data_set(self) -> UnitgroupsUnitGroupDataSet:
        return cast(UnitgroupsUnitGroupDataSet, getattr(self.model, "unit_group_data_set"))

    @unit_group_data_set.setter
    def unit_group_data_set(self, value: UnitgroupsUnitGroupDataSet | Mapping[str, Any]) -> None:
        TidasEntity.__setattr__(self, "unit_group_data_set", value)

    def ensure_defaults(self) -> None:
        dataset = ensure_model(self, "unit_group_data_set", UnitgroupsUnitGroupDataSet)
        dataset.xmlns = dataset.xmlns or "http://lca.jrc.it/ILCD/UnitGroup"
        dataset.xmlns_common = dataset.xmlns_common or "http://lca.jrc.it/ILCD/Common"
        dataset.xmlns_xsi = dataset.xmlns_xsi or "http://www.w3.org/2001/XMLSchema-instance"
        dataset.version = dataset.version or "1.1"
        dataset.xsi_schema_location = (
            dataset.xsi_schema_location
            or "http://lca.jrc.it/ILCD/UnitGroup ../../schemas/ILCD_UnitGroupDataSet.xsd"
        )

        info = ensure_model(
            dataset,
            "unit_group_information",
            UnitgroupsUnitGroupDataSetUnitGroupInformation,
        )
        data_info = ensure_model(
            info,
            "data_set_information",
            UnitGroupDataSetUnitGroupInformationDataSetInformation,
        )
        if not data_info.common_uuid:
            data_info.common_uuid = str(uuid4())
        ensure_multilang(data_info, "common_synonyms")
        ensure_multilang(data_info, "common_general_comment")

        admin = ensure_model(
            dataset,
            "administrative_information",
            UnitgroupsUnitGroupDataSetAdministrativeInformation,
        )
        data_entry = ensure_model(
            admin,
            "data_entry_by",
            UnitGroupDataSetAdministrativeInformationDataEntryBy,
        )
        if not data_entry.common_time_stamp:
            data_entry.common_time_stamp = default_timestamp()
        ensure_model(
            admin,
            "publication_and_ownership",
            UnitGroupDataSetAdministrativeInformationPublicationAndOwnership,
        )
