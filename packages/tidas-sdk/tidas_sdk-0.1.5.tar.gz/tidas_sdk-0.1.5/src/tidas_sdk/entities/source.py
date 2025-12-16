"""
High level wrapper for Source datasets.
"""
from __future__ import annotations

from typing import Any, Mapping, cast
from uuid import uuid4

from ..core.base import TidasEntity
from ..generated.tidas_sources import (
    SourceDataSetAdministrativeInformationDataEntryBy,
    SourceDataSetAdministrativeInformationPublicationAndOwnership,
    SourceDataSetSourceInformationDataSetInformation,
    Sources,
    SourcesSourceDataSet,
    SourcesSourceDataSetAdministrativeInformation,
    SourcesSourceDataSetSourceInformation,
)
from .utils import default_timestamp, ensure_model, ensure_multilang


class TidasSource(TidasEntity[Sources]):
    schema_name = "tidas_sources.json"

    def __init__(
        self,
        initial_data: dict[str, Any] | Sources | None = None,
        *,
        validate_on_init: bool = False,
    ) -> None:
        super().__init__(Sources, initial_data, validate_on_init=validate_on_init)

    @property
    def source_data_set(self) -> SourcesSourceDataSet:
        return cast(SourcesSourceDataSet, getattr(self.model, "source_data_set"))

    @source_data_set.setter
    def source_data_set(self, value: SourcesSourceDataSet | Mapping[str, Any]) -> None:
        TidasEntity.__setattr__(self, "source_data_set", value)

    def ensure_defaults(self) -> None:
        dataset = ensure_model(self, "source_data_set", SourcesSourceDataSet)
        dataset.xmlns = dataset.xmlns or "http://lca.jrc.it/ILCD/Source"
        dataset.xmlns_common = dataset.xmlns_common or "http://lca.jrc.it/ILCD/Common"
        dataset.xmlns_xsi = dataset.xmlns_xsi or "http://www.w3.org/2001/XMLSchema-instance"
        dataset.version = dataset.version or "1.1"
        dataset.xsi_schema_location = (
            dataset.xsi_schema_location
            or "http://lca.jrc.it/ILCD/Source ../../schemas/ILCD_SourceDataSet.xsd"
        )

        source_info = ensure_model(
            dataset,
            "source_information",
            SourcesSourceDataSetSourceInformation,
        )
        data_info = ensure_model(
            source_info,
            "data_set_information",
            SourceDataSetSourceInformationDataSetInformation,
        )
        if not data_info.common_uuid:
            data_info.common_uuid = str(uuid4())
        ensure_multilang(data_info, "common_short_name")
        ensure_multilang(data_info, "source_description_or_comment")

        admin = ensure_model(
            dataset,
            "administrative_information",
            SourcesSourceDataSetAdministrativeInformation,
        )
        data_entry = ensure_model(
            admin,
            "data_entry_by",
            SourceDataSetAdministrativeInformationDataEntryBy,
        )
        if not data_entry.common_time_stamp:
            data_entry.common_time_stamp = default_timestamp()
        ensure_model(
            admin,
            "publication_and_ownership",
            SourceDataSetAdministrativeInformationPublicationAndOwnership,
        )
