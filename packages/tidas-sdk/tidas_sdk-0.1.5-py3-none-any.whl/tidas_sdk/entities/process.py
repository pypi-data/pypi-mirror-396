"""
High level wrapper around the Process dataset.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, cast
from uuid import uuid4

from ..core.base import TidasEntity
from ..generated.tidas_processes import (
    ProcessDataSetAdministrativeInformationDataEntryBy,
    ProcessDataSetAdministrativeInformationPublicationAndOwnership,
    ProcessDataSetProcessInformationDataSetInformation,
    ProcessDataSetProcessInformationGeography,
    ProcessDataSetProcessInformationMathematicalRelations,
    ProcessDataSetProcessInformationQuantitativeReference,
    ProcessDataSetProcessInformationTechnology,
    ProcessDataSetProcessInformationTime,
    DataSetInformationClassificationInformationCommonClassification,
    ProcessInformationDataSetInformationClassificationInformation,
    ProcessInformationDataSetInformationName,
    Processes,
    ProcessesProcessDataSet,
    ProcessesProcessDataSetAdministrativeInformation,
    ProcessesProcessDataSetProcessInformation,
    ProcessesProcessDataSetModellingAndValidation,
)
from ..core.markdown import ensure_list, format_number, join_texts, pick_short_description, pick_text
from .utils import default_timestamp, ensure_model, ensure_multilang
from datetime import datetime, timezone


class TidasProcess(TidasEntity[Processes]):
    schema_name = "tidas_processes.json"

    def __init__(
        self,
        initial_data: dict[str, Any] | Processes | None = None,
        *,
        validate_on_init: bool = False,
    ) -> None:
        super().__init__(Processes, initial_data, validate_on_init=validate_on_init)

    @classmethod
    def from_xml(
        cls,
        xml_data: str | bytes | Path,
        *,
        validate_on_init: bool = False,
    ) -> "TidasProcess":
        """
        Construct a process entity from ILCD XML.
        """
        from tidas_sdk.xml.parser import dataset_from_xml

        payload = dataset_from_xml(xml_data)
        return cls(payload, validate_on_init=validate_on_init)

    @property
    def process_data_set(self) -> ProcessesProcessDataSet:
        return cast(ProcessesProcessDataSet, getattr(self.model, "process_data_set"))

    @process_data_set.setter
    def process_data_set(self, value: ProcessesProcessDataSet | Mapping[str, Any]) -> None:
        TidasEntity.__setattr__(self, "process_data_set", value)

    def ensure_defaults(self) -> None:
        dataset = ensure_model(self, "process_data_set", ProcessesProcessDataSet)
        if not getattr(dataset, "xmlns", None):
            dataset.xmlns = "http://lca.jrc.it/ILCD/Process"
        if not getattr(dataset, "xmlns_common", None):
            dataset.xmlns_common = "http://lca.jrc.it/ILCD/Common"
        if not getattr(dataset, "xmlns_xsi", None):
            dataset.xmlns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
        if not getattr(dataset, "version", None):
            dataset.version = "1.1"
        if not getattr(dataset, "locations", None):
            dataset.locations = "../ILCDLocations.xml"
        if not getattr(dataset, "xsi_schema_location", None):
            dataset.xsi_schema_location = "http://lca.jrc.it/ILCD/Process ../../schemas/ILCD_ProcessDataSet.xsd"

        process_info = ensure_model(dataset, "process_information", ProcessesProcessDataSetProcessInformation)
        data_info = ensure_model(
            process_info, "data_set_information", ProcessDataSetProcessInformationDataSetInformation
        )
        if not getattr(data_info, "common_uuid", None):
            data_info.common_uuid = str(uuid4())
        ensure_model(data_info, "name", ProcessInformationDataSetInformationName)
        ensure_model(
            data_info,
            "classification_information",
            ProcessInformationDataSetInformationClassificationInformation,
        )
        classification_info = getattr(data_info, "classification_information", None)
        if classification_info is not None:
            ensure_model(
                classification_info,
                "common_classification",
                DataSetInformationClassificationInformationCommonClassification,
            )
        for field_name in ("common_synonyms", "common_general_comment"):
            ensure_multilang(data_info, field_name)

        ensure_model(
            process_info,
            "quantitative_reference",
            ProcessDataSetProcessInformationQuantitativeReference,
        )
        ensure_model(process_info, "time", ProcessDataSetProcessInformationTime)
        ensure_model(process_info, "geography", ProcessDataSetProcessInformationGeography)
        ensure_model(process_info, "technology", ProcessDataSetProcessInformationTechnology)
        ensure_model(
            process_info,
            "mathematical_relations",
            ProcessDataSetProcessInformationMathematicalRelations,
        )

        admin = ensure_model(dataset, "administrative_information", ProcessesProcessDataSetAdministrativeInformation)
        data_entry = ensure_model(admin, "data_entry_by", ProcessDataSetAdministrativeInformationDataEntryBy)
        ts = getattr(data_entry, "common_time_stamp", None)
        if isinstance(ts, str):
            data_entry.common_time_stamp = self._parse_datetime(ts)
        if not getattr(data_entry, "common_time_stamp", None):
            data_entry.common_time_stamp = default_timestamp()
        ensure_model(admin, "publication_and_ownership", ProcessDataSetAdministrativeInformationPublicationAndOwnership)

        ensure_model(dataset, "modelling_and_validation", ProcessesProcessDataSetModellingAndValidation)

    def to_markdown(self, lang: str = "en") -> str:
        dataset = getattr(self, "process_data_set", None)
        process_info = getattr(dataset, "process_information", None) if dataset else None
        data_info = getattr(process_info, "data_set_information", None) if process_info else None
        quant_ref = getattr(process_info, "quantitative_reference", None) if process_info else None

        title = self._compose_title(data_info, lang)

        lines: list[str] = [f"# {title}", ""]
        lines.append("**Entity:** Process")

        if data_info and getattr(data_info, "common_uuid", None):
            lines.append(f"**UUID:** `{data_info.common_uuid}`")
        version = self._data_set_version(dataset)
        if version:
            lines.append(f"**Version:** {version}")

        loc_code, _ = self._geography(process_info, lang)
        if loc_code:
            lines.append(f"**Location:** {loc_code}")

        ref_flow_name, ref_amount = self._reference_flow_summary(dataset, quant_ref, lang)
        if ref_flow_name:
            lines.append(f"**Reference Flow:** {ref_flow_name}")
        if ref_amount:
            lines.append(f"**Amount:** {ref_amount}")
        if ref_flow_name or ref_amount:
            lines.append("")

        classification = self._classification_path(data_info)
        if classification:
            lines.append(f"**Classification:** {classification}")
            lines.append("")
        functional_unit = join_texts(getattr(quant_ref, "functional_unit_or_other", None), lang)
        if functional_unit:
            lines.append(f"**Functional Unit:** {functional_unit}")
        if lines and lines[-1] != "":
            lines.append("")

        description = join_texts(getattr(data_info, "common_general_comment", None), lang)
        if description:
            lines.extend(["## Description", "", description, ""])

        time_block = self._time_coverage(process_info, lang)
        if time_block:
            lines.extend(["## Time Coverage", "", time_block, ""])

        geography_desc = self._geography_description(process_info, lang)
        if geography_desc:
            lines.extend(["## Geography", "", geography_desc, ""])

        technology = self._technology(process_info, lang)
        if technology:
            lines.extend(["## Technology", "", technology, ""])

        methodology = self._methodology(dataset, lang)
        if methodology:
            lines.extend(["## Methodology", "", methodology, ""])

        data_sources = self._data_sources(dataset, lang)
        if data_sources:
            lines.extend(["## Data Sources", "", data_sources, ""])

        inputs, outputs = self._exchange_lists(dataset, lang)
        if inputs:
            lines.append("## Main Inputs")
            lines.append("")
            lines.extend(inputs)
            lines.append("")
        if outputs:
            lines.append("## Main Outputs")
            lines.append("")
            lines.extend(outputs)
            lines.append("")

        if lines and lines[-1] == "":
            lines.pop()
        return "\n".join(lines)

    def _compose_title(self, data_info: ProcessDataSetProcessInformationDataSetInformation | None, lang: str) -> str:
        if not data_info:
            return "Process"
        name_obj = getattr(data_info, "name", None)
        parts: list[str] = []
        for field in ("base_name", "mix_and_location_types", "treatment_standards_routes"):
            part = join_texts(getattr(name_obj, field, None), lang, sep=" | ") if name_obj else None
            if part:
                parts.append(part)
        return " | ".join(parts) if parts else "Process"

    def _reference_flow_summary(
        self,
        dataset: ProcessesProcessDataSet | None,
        quant_ref: ProcessDataSetProcessInformationQuantitativeReference | None,
        lang: str,
    ) -> tuple[str | None, str | None]:
        if not dataset or not quant_ref:
            return None, None
        ref_id = getattr(quant_ref, "reference_to_reference_flow", None)
        if ref_id is None:
            return None, None

        exchanges = getattr(dataset, "exchanges", None)
        exchange_items = ensure_list(getattr(exchanges, "exchange", None)) if exchanges else []
        ref_exchange = None
        for item in exchange_items:
            item_id = getattr(item, "data_set_internal_id", None) or getattr(item, "@dataSetInternalID", None)
            if item_id is not None and str(item_id) == str(ref_id):
                ref_exchange = item
                break

        if not ref_exchange:
            return None, None

        ref_flow = getattr(ref_exchange, "reference_to_flow_data_set", None)
        ref_name = pick_short_description(ref_flow, lang)
        amount = getattr(ref_exchange, "mean_amount", None)
        return ref_name, format_number(amount) if amount is not None else None

    def _classification_path(
        self, data_info: ProcessDataSetProcessInformationDataSetInformation | None
    ) -> str | None:
        if not data_info:
            return None
        classification_info = getattr(data_info, "classification_information", None)
        common_classification = getattr(classification_info, "common_classification", None) if classification_info else None
        classes = ensure_list(getattr(common_classification, "common_class", None)) if common_classification else []
        if not classes:
            return None

        def _level_value(item: Any) -> int | None:
            level = getattr(item, "level", None)
            try:
                return int(level)
            except Exception:
                return None

        sorted_classes = sorted(
            classes,
            key=lambda entry: (_level_value(entry) is None, _level_value(entry) or 0),
        )
        parts: list[str] = []
        for entry in sorted_classes:
            text = getattr(entry, "text", None)
            if text:
                parts.append(str(text))
                continue
            if isinstance(entry, dict) and entry.get("#text"):
                parts.append(str(entry["#text"]))
        return " > ".join(parts) if parts else None

    def _data_set_version(self, dataset: ProcessesProcessDataSet | None) -> str | None:
        if not dataset:
            return None
        admin = getattr(dataset, "administrative_information", None)
        publication = getattr(admin, "publication_and_ownership", None) if admin else None
        return getattr(publication, "common_data_set_version", None)

    def _time_coverage(
        self, process_info: ProcessesProcessDataSetProcessInformation | None, lang: str
    ) -> str | None:
        time_info = getattr(process_info, "time", None) if process_info else None
        if not time_info:
            return None
        year = getattr(time_info, "common_reference_year", None)
        until = getattr(time_info, "common_data_set_valid_until", None)
        description = join_texts(getattr(time_info, "common_time_representativeness_description", None), lang)

        parts: list[str] = []
        if year or until:
            parts.append(
                f"Reference Year: {year}" + (f" | Valid Until: {until}" if until else "")
            )
        if description:
            parts.append(description)
        return "\n".join(parts) if parts else None

    def _geography(
        self, process_info: ProcessesProcessDataSetProcessInformation | None, lang: str
    ) -> tuple[str | None, str | None]:
        geography = getattr(process_info, "geography", None) if process_info else None
        location = getattr(geography, "location_of_operation_supply_or_production", None) if geography else None
        if not location:
            return None, None
        code = getattr(location, "location", None)
        restrictions = join_texts(getattr(location, "description_of_restrictions", None), lang)
        return code, restrictions

    def _geography_description(
        self, process_info: ProcessesProcessDataSetProcessInformation | None, lang: str
    ) -> str | None:
        _, restrictions = self._geography(process_info, lang)
        return restrictions

    def _technology(
        self, process_info: ProcessesProcessDataSetProcessInformation | None, lang: str
    ) -> str | None:
        technology = getattr(process_info, "technology", None) if process_info else None
        if not technology:
            return None
        applicability = join_texts(getattr(technology, "technological_applicability", None), lang)
        description = join_texts(getattr(technology, "technology_description_and_included_processes", None), lang)
        parts = [part for part in (applicability, description) if part]
        return "\n\n".join(parts) if parts else None

    def _methodology(self, dataset: ProcessesProcessDataSet | None, lang: str) -> str | None:
        if not dataset:
            return None
        modelling = getattr(dataset, "modelling_and_validation", None)
        lci = getattr(modelling, "lci_method_and_allocation", None) if modelling else None
        if not lci:
            return None
        data_set_type = getattr(lci, "type_of_data_set", None)
        principle = getattr(lci, "lci_method_principle", None)
        approach = getattr(lci, "lci_method_approaches", None)

        parts: list[str] = []
        if data_set_type:
            parts.append(f"**Data Set Type:** {data_set_type}")
        if principle:
            parts.append(f"**LCI Method Principle:** {principle}")
        if approach:
            parts.append(f"**LCI Method Approach:** {approach}")
        return "\n".join(parts) if parts else None

    def _data_sources(self, dataset: ProcessesProcessDataSet | None, lang: str) -> str | None:
        if not dataset:
            return None
        modelling = getattr(dataset, "modelling_and_validation", None)
        data_sources = getattr(modelling, "data_sources_treatment_and_representativeness", None) if modelling else None
        if not data_sources:
            return None
        sampling = join_texts(getattr(data_sources, "sampling_procedure", None), lang)
        reference = getattr(data_sources, "reference_to_data_source", None)
        reference_text = pick_text(getattr(reference, "common_short_description", None), lang)
        parts: list[str] = []
        if sampling:
            parts.append(sampling)
        if reference_text:
            parts.append(reference_text)
        return "\n\n".join(parts) if parts else None

    def _exchange_lists(
        self, dataset: ProcessesProcessDataSet | None, lang: str
    ) -> tuple[list[str], list[str]]:
        if not dataset:
            return [], []
        exchanges = getattr(dataset, "exchanges", None)
        items = ensure_list(getattr(exchanges, "exchange", None)) if exchanges else []
        if not items:
            return [], []

        def _as_float(value: Any) -> float | None:
            try:
                return float(str(value))
            except Exception:
                return None

        def _label(item: Any) -> str:
            ref = getattr(item, "reference_to_flow_data_set", None)
            text = pick_short_description(ref, lang)
            return text or f"Flow {getattr(item, 'data_set_internal_id', '')}".strip()

        def _format_line(item: Any) -> str:
            amount = getattr(item, "mean_amount", None)
            return f"- {_label(item)}: {format_number(amount)}"

        sorted_items = sorted(
            enumerate(items),
            key=lambda pair: (
                _as_float(getattr(pair[1], "mean_amount", None)) is None,
                -_as_float(getattr(pair[1], "mean_amount", None)) if _as_float(getattr(pair[1], "mean_amount", None)) is not None else 0,
                pair[0],
            ),
        )
        sorted_entries = [item for _, item in sorted_items]
        inputs = [_format_line(item) for item in sorted_entries if getattr(item, "exchange_direction", None) == "Input"]
        outputs = [_format_line(item) for item in sorted_entries if getattr(item, "exchange_direction", None) == "Output"]
        return inputs[:10], outputs[:10]

    @staticmethod
    def _parse_datetime(value: str) -> datetime:
        text = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(text)
        except Exception:
            return datetime.now(timezone.utc)
