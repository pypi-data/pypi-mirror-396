"""
High level wrapper for Flow datasets.
"""
from __future__ import annotations

from typing import Any, Mapping, cast
from uuid import uuid4

from ..core.base import TidasEntity
from ..generated.tidas_flows import (
    FlowDataSetAdministrativeInformationDataEntryBy,
    FlowDataSetAdministrativeInformationPublicationAndOwnership,
    FlowDataSetFlowInformationDataSetInformation,
    Flows,
    FlowsFlowDataSet,
    FlowsFlowDataSetAdministrativeInformation,
    FlowsFlowDataSetFlowInformation,
    FlowsFlowDataSetFlowProperties,
)
from ..core.markdown import (
    ensure_list,
    format_number,
    join_texts,
    pick_short_description,
    pick_text,
)
from .utils import default_timestamp, ensure_model, ensure_multilang
from datetime import datetime, timezone


class TidasFlow(TidasEntity[Flows]):
    schema_name = "tidas_flows.json"

    def __init__(
        self,
        initial_data: dict[str, Any] | Flows | None = None,
        *,
        validate_on_init: bool = False,
    ) -> None:
        super().__init__(Flows, initial_data, validate_on_init=validate_on_init)

    @property
    def flow_data_set(self) -> FlowsFlowDataSet:
        return cast(FlowsFlowDataSet, getattr(self.model, "flow_data_set"))

    @flow_data_set.setter
    def flow_data_set(self, value: FlowsFlowDataSet | Mapping[str, Any]) -> None:
        TidasEntity.__setattr__(self, "flow_data_set", value)

    def ensure_defaults(self) -> None:
        dataset = ensure_model(self, "flow_data_set", FlowsFlowDataSet)
        if not getattr(dataset, "xmlns", None):
            dataset.xmlns = "http://lca.jrc.it/ILCD/Flow"
        if not getattr(dataset, "xmlns_common", None):
            dataset.xmlns_common = "http://lca.jrc.it/ILCD/Common"
        if not getattr(dataset, "xmlns_ecn", None):
            dataset.xmlns_ecn = "http://eplca.jrc.ec.europa.eu/ILCD/Extensions/2018/ECNumber"
        if not getattr(dataset, "xmlns_xsi", None):
            dataset.xmlns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
        if not getattr(dataset, "version", None):
            dataset.version = "1.1"
        if not getattr(dataset, "locations", None):
            dataset.locations = "../ILCDLocations.xml"
        if not getattr(dataset, "xsi_schema_location", None):
            dataset.xsi_schema_location = "http://lca.jrc.it/ILCD/Flow ../../schemas/ILCD_FlowDataSet.xsd"

        flow_info = ensure_model(
            dataset,
            "flow_information",
            FlowsFlowDataSetFlowInformation,
        )
        data_info = ensure_model(
            flow_info,
            "data_set_information",
            FlowDataSetFlowInformationDataSetInformation,
        )
        if not data_info.common_uuid:
            data_info.common_uuid = str(uuid4())
        ensure_multilang(data_info, "common_synonyms")
        ensure_multilang(data_info, "common_general_comment")

        admin = ensure_model(
            dataset,
            "administrative_information",
            FlowsFlowDataSetAdministrativeInformation,
        )
        data_entry = ensure_model(
            admin,
            "data_entry_by",
            FlowDataSetAdministrativeInformationDataEntryBy,
        )
        if not data_entry.common_time_stamp:
            data_entry.common_time_stamp = default_timestamp()
        elif isinstance(data_entry.common_time_stamp, str):
            data_entry.common_time_stamp = self._parse_datetime(data_entry.common_time_stamp)
        ensure_model(
            admin,
            "publication_and_ownership",
            FlowDataSetAdministrativeInformationPublicationAndOwnership,
        )
        ensure_model(dataset, "flow_properties", FlowsFlowDataSetFlowProperties)

    def to_markdown(self, lang: str = "en") -> str:
        dataset = getattr(self, "flow_data_set", None)
        flow_info = getattr(dataset, "flow_information", None) if dataset else None
        data_info = getattr(flow_info, "data_set_information", None) if flow_info else None

        title = self._compose_title(data_info, lang)

        lines: list[str] = [f"# {title}", ""]
        lines.append("**Entity:** Flow")

        if data_info and data_info.common_uuid:
            lines.append(f"**UUID:** `{data_info.common_uuid}`")

        version = self._data_set_version(dataset)
        if version:
            lines.append(f"**Version:** {version}")

        ref_prop_name, ref_prop_value = self._reference_property_summary(dataset, lang)
        if ref_prop_name or ref_prop_value:
            lines.append(f"**Reference Property:** {ref_prop_name or 'N/A'}")
        if ref_prop_value:
            lines.append(f"**Property Mean:** {ref_prop_value}")

        methodology = self._methodology(dataset)
        if methodology:
            lines.append(methodology)

        cas_number = getattr(data_info, "cas_number", None) if data_info else None
        if cas_number:
            lines.append(f"**CAS:** {cas_number}")

        ec_number = self._ec_number(data_info)
        if ec_number:
            lines.append(f"**EC Number:** {ec_number}")

        classification = self._classification_path(data_info)
        if classification:
            lines.append(f"**Classification:** {classification}")
            lines.append("")

        synonyms = join_texts(getattr(data_info, "common_synonyms", None), lang)
        if synonyms:
            lines.append(f"**Synonyms:** {synonyms}")

        if lines and lines[-1] != "":
            lines.append("")

        description = join_texts(getattr(data_info, "common_general_comment", None), lang)
        if description:
            lines.extend(["## Description", "", description, ""])

        geography = self._geography(flow_info, lang)
        if geography:
            lines.extend(["## Geography", "", geography, ""])

        technology = self._technology(flow_info, lang)
        if technology:
            lines.extend(["## Technology", "", technology, ""])

        flow_properties = self._flow_properties(dataset, lang)
        if flow_properties:
            lines.append("## Flow Properties")
            lines.append("")
            lines.extend(flow_properties)
            lines.append("")

        if lines and lines[-1] == "":
            lines.pop()
        return "\n".join(lines)

    def _compose_title(self, data_info: FlowDataSetFlowInformationDataSetInformation | None, lang: str) -> str:
        if not data_info:
            return "Flow"
        name_obj = getattr(data_info, "name", None)
        parts: list[str] = []
        for field in ("base_name", "mix_and_location_types", "treatment_standards_routes"):
            part = join_texts(getattr(name_obj, field, None), lang, sep=" | ") if name_obj else None
            if part:
                parts.append(part)
        return " | ".join(parts) if parts else "Flow"

    def _reference_property_summary(
        self, dataset: FlowsFlowDataSet | None, lang: str
    ) -> tuple[str | None, str | None]:
        if not dataset:
            return None, None
        flow_info = getattr(dataset, "flow_information", None)
        quant_ref = getattr(flow_info, "quantitative_reference", None) if flow_info else None
        ref_id = getattr(quant_ref, "reference_to_reference_flow_property", None) if quant_ref else None
        properties = getattr(dataset, "flow_properties", None)
        prop_items = ensure_list(getattr(properties, "flow_property", None)) if properties else []

        ref_item = None
        for item in prop_items:
            item_id = getattr(item, "data_set_internal_id", None)
            if item_id is None and isinstance(item, dict):
                item_id = item.get("@dataSetInternalID")
            if item_id is not None and ref_id is not None and str(item_id) == str(ref_id):
                ref_item = item
                break

        if not ref_item:
            return None, None

        if isinstance(ref_item, dict):
            ref_info = ref_item.get("referenceToFlowPropertyDataSet")
            mean_value = ref_item.get("meanValue")
        else:
            ref_info = getattr(ref_item, "reference_to_flow_property_data_set", None)
            mean_value = getattr(ref_item, "mean_value", None)

        name = pick_short_description(ref_info, lang)
        return name, format_number(mean_value) if mean_value is not None else None

    def _classification_path(self, data_info: FlowDataSetFlowInformationDataSetInformation | None) -> str | None:
        if not data_info:
            return None
        classification = getattr(data_info, "classification_information", None)

        categories: list[Any] = []
        if isinstance(classification, dict):
            container = classification.get("common:elementaryFlowCategorization") or classification.get(
                "common:classification"
            )
            if isinstance(container, dict):
                categories = ensure_list(container.get("common:category"))
        else:
            container = getattr(classification, "common_elementary_flow_categorization", None)
            categories = ensure_list(getattr(container, "common_category", None)) if container else []

        if not categories:
            return None

        def _level_value(item: Any) -> int | None:
            level = None
            if isinstance(item, dict):
                level = item.get("@level")
            else:
                level = getattr(item, "level", None)
            try:
                return int(level)
            except Exception:
                return None

        # Build nested bullet-like strings using level info when present.
        sorted_categories = sorted(
            categories,
            key=lambda entry: (_level_value(entry) is None, _level_value(entry) or 0),
        )
        parts: list[str] = []
        for entry in sorted_categories:
            text = entry.get("#text") if isinstance(entry, dict) else getattr(entry, "text", None)
            if text:
                parts.append(str(text))
        return " > ".join(parts) if parts else None

    def _ec_number(self, data_info: FlowDataSetFlowInformationDataSetInformation | None) -> str | None:
        if not data_info:
            return None
        other = getattr(data_info, "common_other", None)
        if isinstance(other, dict):
            ec_container = other.get("ecn:ECNumber")
            if isinstance(ec_container, str):
                return ec_container
            if isinstance(ec_container, dict) and "#text" in ec_container:
                return str(ec_container.get("#text"))
        return None

    def _data_set_version(self, dataset: FlowsFlowDataSet | None) -> str | None:
        if not dataset:
            return None
        admin = getattr(dataset, "administrative_information", None)
        publication = getattr(admin, "publication_and_ownership", None) if admin else None
        return getattr(publication, "common_data_set_version", None)

    def _geography(self, flow_info: FlowsFlowDataSetFlowInformation | None, lang: str) -> str | None:
        geography = getattr(flow_info, "geography", None) if flow_info else None
        if not geography:
            return None
        location = getattr(geography, "location_of_supply", None)
        if not location:
            return None
        return f"**Location of Supply:** {location}"

    def _technology(self, flow_info: FlowsFlowDataSetFlowInformation | None, lang: str) -> str | None:
        technology = getattr(flow_info, "technology", None) if flow_info else None
        if not technology:
            return None
        applicability = join_texts(getattr(technology, "technological_applicability", None), lang)
        return applicability

    def _flow_properties(self, dataset: FlowsFlowDataSet | None, lang: str) -> list[str]:
        if not dataset:
            return []
        props = getattr(dataset, "flow_properties", None)
        items = ensure_list(getattr(props, "flow_property", None)) if props else []
        lines: list[str] = []
        for item in items:
            if isinstance(item, dict):
                ref = item.get("referenceToFlowPropertyDataSet")
                mean_value = format_number(item.get("meanValue", None))
            else:
                ref = getattr(item, "reference_to_flow_property_data_set", None)
                mean_value = format_number(getattr(item, "mean_value", None))
            name = pick_short_description(ref, lang) or "Flow property"
            lines.append(f"- {name}: {mean_value}")
        return lines

    @staticmethod
    def _parse_datetime(value: str) -> datetime:
        text = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(text)
        except Exception:
            return datetime.now(timezone.utc)

    def _methodology(self, dataset: FlowsFlowDataSet | None) -> str | None:
        if not dataset:
            return None
        modelling = getattr(dataset, "modelling_and_validation", None)
        lci = getattr(modelling, "lci_method", None) if modelling else None
        if not lci:
            return None
        data_set_type = getattr(lci, "type_of_data_set", None)
        return f"**Data Set Type:** {data_set_type}" if data_set_type else None
