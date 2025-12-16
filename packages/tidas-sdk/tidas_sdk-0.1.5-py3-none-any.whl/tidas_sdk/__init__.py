"""
TIDAS Python SDK public interface.

The package exposes high-level factory helpers (e.g. ``create_process``)
as well as entity classes that wrap generated models. The actual factories
and entities will be populated as the SDK generation workflow is completed.
"""

from .core.factory import (  # noqa: F401
    create_contact,
    create_contact_from_json,
    create_contacts_batch,
    create_flow,
    create_flow_from_json,
    create_flows_batch,
    create_flow_property,
    create_flow_property_from_json,
    create_flow_properties_batch,
    create_lcia_method,
    create_lcia_method_from_json,
    create_lcia_methods_batch,
    create_life_cycle_model,
    create_life_cycle_model_from_json,
    create_life_cycle_models_batch,
    create_process,
    create_process_from_json,
    create_process_from_xml,
    create_processes_batch,
    create_source,
    create_source_from_json,
    create_sources_batch,
    create_unit_group,
    create_unit_group_from_json,
    create_unit_groups_batch,
)

from .core.factory import (  # noqa: F401
    TidasContact,
    TidasFlow,
    TidasFlowProperty,
    TidasLCIAMethod,
    TidasLifeCycleModel,
    TidasProcess,
    TidasSource,
    TidasUnitGroup,
)

__all__ = [
    "create_contact",
    "create_contact",
    "create_contact_from_json",
    "create_contacts_batch",
    "create_flow",
    "create_flow_from_json",
    "create_flows_batch",
    "create_flow_property",
    "create_flow_property_from_json",
    "create_flow_properties_batch",
    "create_lcia_method",
    "create_lcia_method_from_json",
    "create_lcia_methods_batch",
    "create_life_cycle_model",
    "create_life_cycle_model_from_json",
    "create_life_cycle_models_batch",
    "create_process",
    "create_process_from_json",
    "create_process_from_xml",
    "create_processes_batch",
    "create_source",
    "create_source_from_json",
    "create_sources_batch",
    "create_unit_group",
    "create_unit_group_from_json",
    "create_unit_groups_batch",
    "TidasFlowProperty",
    "TidasLCIAMethod",
    "TidasLifeCycleModel",
    "TidasProcess",
    "TidasSource",
    "TidasUnitGroup",
    "TidasContact",
    "TidasFlow",
]
