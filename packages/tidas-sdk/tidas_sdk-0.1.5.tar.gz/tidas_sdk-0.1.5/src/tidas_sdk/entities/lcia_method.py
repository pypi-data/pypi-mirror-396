"""
High level wrapper for LCIAMethod datasets.
"""
from __future__ import annotations

from typing import Any, Mapping, cast
from uuid import uuid4

from ..core.base import TidasEntity
from ..generated.tidas_lciamethods import (
    LCIAMethodDataSetAdministrativeInformationDataEntryBy,
    LCIAMethodDataSetAdministrativeInformationPublicationAndOwnership,
    LCIAMethodDataSetLCIAMethodInformationDataSetInformation,
    Lciamethods,
    LciamethodsLCIAMethodDataSet,
    LciamethodsLCIAMethodDataSetAdministrativeInformation,
    LciamethodsLCIAMethodDataSetLCIAMethodInformation,
)
from .utils import default_timestamp, ensure_model, ensure_multilang


class TidasLCIAMethod(TidasEntity[Lciamethods]):
    schema_name = "tidas_lciamethods.json"

    def __init__(
        self,
        initial_data: dict[str, Any] | Lciamethods | None = None,
        *,
        validate_on_init: bool = False,
    ) -> None:
        super().__init__(Lciamethods, initial_data, validate_on_init=validate_on_init)

    @property
    def lcia_method_data_set(self) -> LciamethodsLCIAMethodDataSet:
        return cast(LciamethodsLCIAMethodDataSet, getattr(self.model, "lcia_method_data_set"))

    @lcia_method_data_set.setter
    def lcia_method_data_set(self, value: LciamethodsLCIAMethodDataSet | Mapping[str, Any]) -> None:
        TidasEntity.__setattr__(self, "lcia_method_data_set", value)

    def ensure_defaults(self) -> None:
        dataset = ensure_model(self, "lcia_method_data_set", LciamethodsLCIAMethodDataSet)
        dataset.xmlns = dataset.xmlns or "http://lca.jrc.it/ILCD/LCIAMethod"
        dataset.xmlns_common = dataset.xmlns_common or "http://lca.jrc.it/ILCD/Common"
        dataset.xmlns_xsi = dataset.xmlns_xsi or "http://www.w3.org/2001/XMLSchema-instance"
        dataset.version = dataset.version or "1.1"
        dataset.xsi_schema_location = (
            dataset.xsi_schema_location
            or "http://lca.jrc.it/ILCD/LCIAMethod ../../schemas/ILCD_LCIAMethodDataSet.xsd"
        )

        method_info = ensure_model(
            dataset,
            "lcia_method_information",
            LciamethodsLCIAMethodDataSetLCIAMethodInformation,
        )
        data_info = ensure_model(
            method_info,
            "data_set_information",
            LCIAMethodDataSetLCIAMethodInformationDataSetInformation,
        )
        if not data_info.common_uuid:
            data_info.common_uuid = str(uuid4())
        ensure_multilang(data_info, "common_name")
        ensure_multilang(data_info, "common_synonyms")
        ensure_multilang(data_info, "common_general_comment")

        admin = ensure_model(
            dataset,
            "administrative_information",
            LciamethodsLCIAMethodDataSetAdministrativeInformation,
        )
        data_entry = ensure_model(
            admin,
            "data_entry_by",
            LCIAMethodDataSetAdministrativeInformationDataEntryBy,
        )
        if not data_entry.common_time_stamp:
            data_entry.common_time_stamp = default_timestamp()
        ensure_model(
            admin,
            "publication_and_ownership",
            LCIAMethodDataSetAdministrativeInformationPublicationAndOwnership,
        )
