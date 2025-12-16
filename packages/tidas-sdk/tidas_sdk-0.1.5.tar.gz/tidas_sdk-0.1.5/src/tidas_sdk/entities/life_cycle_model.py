"""
High level wrapper for LifeCycleModel datasets.
"""
from __future__ import annotations

from typing import Any, Mapping, cast
from uuid import uuid4

from ..core.base import TidasEntity
from ..generated.tidas_lifecyclemodels import (
    LifeCycleModelDataSetAdministrativeInformationDataEntryBy,
    LifeCycleModelDataSetAdministrativeInformationPublicationAndOwnership,
    LifeCycleModelDataSetLifeCycleModelInformationDataSetInformation,
    Lifecyclemodels,
    LifecyclemodelsLifeCycleModelDataSet,
    LifecyclemodelsLifeCycleModelDataSetAdministrativeInformation,
    LifecyclemodelsLifeCycleModelDataSetLifeCycleModelInformation,
)
from .utils import default_timestamp, ensure_model, ensure_multilang


class TidasLifeCycleModel(TidasEntity[Lifecyclemodels]):
    schema_name = "tidas_lifecyclemodels.json"

    def __init__(
        self,
        initial_data: dict[str, Any] | Lifecyclemodels | None = None,
        *,
        validate_on_init: bool = False,
    ) -> None:
        super().__init__(Lifecyclemodels, initial_data, validate_on_init=validate_on_init)

    @property
    def life_cycle_model_data_set(self) -> LifecyclemodelsLifeCycleModelDataSet:
        return cast(LifecyclemodelsLifeCycleModelDataSet, getattr(self.model, "life_cycle_model_data_set"))

    @life_cycle_model_data_set.setter
    def life_cycle_model_data_set(
        self,
        value: LifecyclemodelsLifeCycleModelDataSet | Mapping[str, Any],
    ) -> None:
        TidasEntity.__setattr__(self, "life_cycle_model_data_set", value)

    def ensure_defaults(self) -> None:
        dataset = ensure_model(self, "life_cycle_model_data_set", LifecyclemodelsLifeCycleModelDataSet)
        dataset.xmlns = dataset.xmlns or "http://eplca.jrc.ec.europa.eu/ILCD/LifeCycleModel/2017"
        dataset.xmlns_acme = dataset.xmlns_acme or "http://acme.com/custom"
        dataset.xmlns_common = dataset.xmlns_common or "http://lca.jrc.it/ILCD/Common"
        dataset.xmlns_xsi = dataset.xmlns_xsi or "http://www.w3.org/2001/XMLSchema-instance"
        dataset.version = dataset.version or "1.1"
        dataset.locations = dataset.locations or "../ILCDLocations.xml"
        dataset.xsi_schema_location = (
            dataset.xsi_schema_location
            or "http://eplca.jrc.ec.europa.eu/ILCD/LifeCycleModel/2017 ../../schemas/ILCD_LifeCycleModelDataSet.xsd"
        )

        info = ensure_model(
            dataset,
            "life_cycle_model_information",
            LifecyclemodelsLifeCycleModelDataSetLifeCycleModelInformation,
        )
        data_info = ensure_model(
            info,
            "data_set_information",
            LifeCycleModelDataSetLifeCycleModelInformationDataSetInformation,
        )
        if not data_info.common_uuid:
            data_info.common_uuid = str(uuid4())
        ensure_multilang(data_info, "common_name")
        ensure_multilang(data_info, "common_synonyms")
        ensure_multilang(data_info, "common_general_comment")

        admin = ensure_model(
            dataset,
            "administrative_information",
            LifecyclemodelsLifeCycleModelDataSetAdministrativeInformation,
        )
        data_entry = ensure_model(
            admin,
            "data_entry_by",
            LifeCycleModelDataSetAdministrativeInformationDataEntryBy,
        )
        if not data_entry.common_time_stamp:
            data_entry.common_time_stamp = default_timestamp()
        ensure_model(
            admin,
            "publication_and_ownership",
            LifeCycleModelDataSetAdministrativeInformationPublicationAndOwnership,
        )
