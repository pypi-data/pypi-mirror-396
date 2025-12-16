"""
High level wrapper for Contact datasets.
"""
from __future__ import annotations

from typing import Any, Mapping, cast
from uuid import uuid4

from ..core.base import TidasEntity
from ..generated.tidas_contacts import (
    ContactDataSetAdministrativeInformationDataEntryBy,
    ContactDataSetAdministrativeInformationPublicationAndOwnership,
    ContactDataSetContactInformationDataSetInformation,
    Contacts,
    ContactsContactDataSet,
    ContactsContactDataSetAdministrativeInformation,
    ContactsContactDataSetContactInformation,
)
from .utils import default_timestamp, ensure_model, ensure_multilang


class TidasContact(TidasEntity[Contacts]):
    schema_name = "tidas_contacts.json"

    def __init__(
        self,
        initial_data: dict[str, Any] | Contacts | None = None,
        *,
        validate_on_init: bool = False,
    ) -> None:
        super().__init__(Contacts, initial_data, validate_on_init=validate_on_init)

    @property
    def contact_data_set(self) -> ContactsContactDataSet:
        return cast(ContactsContactDataSet, getattr(self.model, "contact_data_set"))

    @contact_data_set.setter
    def contact_data_set(self, value: ContactsContactDataSet | Mapping[str, Any]) -> None:
        TidasEntity.__setattr__(self, "contact_data_set", value)

    def ensure_defaults(self) -> None:
        dataset = ensure_model(self, "contact_data_set", ContactsContactDataSet)
        dataset.xmlns = dataset.xmlns or "http://lca.jrc.it/ILCD/Contact"
        dataset.xmlns_common = dataset.xmlns_common or "http://lca.jrc.it/ILCD/Common"
        dataset.xmlns_xsi = dataset.xmlns_xsi or "http://www.w3.org/2001/XMLSchema-instance"
        dataset.version = dataset.version or "1.1"
        dataset.xsi_schema_location = (
            dataset.xsi_schema_location
            or "http://lca.jrc.it/ILCD/Contact ../../schemas/ILCD_ContactDataSet.xsd"
        )

        contact_info = ensure_model(dataset, "contact_information", ContactsContactDataSetContactInformation)
        data_info = ensure_model(
            contact_info,
            "data_set_information",
            ContactDataSetContactInformationDataSetInformation,
        )
        if not data_info.common_uuid:
            data_info.common_uuid = str(uuid4())
        for field_name in (
            "common_short_name",
            "common_name",
            "contact_address",
            "central_contact_point",
            "contact_description_or_comment",
        ):
            ensure_multilang(data_info, field_name)

        admin = ensure_model(
            dataset,
            "administrative_information",
            ContactsContactDataSetAdministrativeInformation,
        )
        data_entry = ensure_model(
            admin,
            "data_entry_by",
            ContactDataSetAdministrativeInformationDataEntryBy,
        )
        if not data_entry.common_time_stamp:
            data_entry.common_time_stamp = default_timestamp()
        ensure_model(
            admin,
            "publication_and_ownership",
            ContactDataSetAdministrativeInformationPublicationAndOwnership,
        )
