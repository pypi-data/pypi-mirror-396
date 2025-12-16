"""
Auto generated file. DO NOT EDIT.
Source: tidas_lifecyclemodels.json
"""
from __future__ import annotations

from typing import Literal

from pydantic import Field
from tidas_sdk.core.base import TidasBaseModel
from tidas_sdk.core.multilang import MultiLangList

from .tidas_data_types import DateTime
from .tidas_data_types import GlobalReferenceType
from .tidas_data_types import LevelType
from .tidas_data_types import MatV
from .tidas_data_types import Real
from .tidas_data_types import UUID
from datetime import datetime

class LifeCycleModelInformationDataSetInformationName(TidasBaseModel):
    """General descriptive, specifying, structured name of the Life cycle model data set. Note: Ensure proper name structuring and observe restriction to 100 characters for each of the four name fields."""
    base_name: MultiLangList = Field(default_factory=MultiLangList, alias='baseName', description='General descriptive name of the life cycle model and/or its main good(s), service(s) and/or functions delivered.')
    treatment_standards_routes: MultiLangList = Field(default_factory=MultiLangList, alias='treatmentStandardsRoutes', description='Specifying information on the good, service, or function delivered by the life cycle model in technical term(s): treatment received, standard fulfilled, product quality, use information, production route name, educt name, primary / secondary etc. Separated by commata.')
    mix_and_location_types: MultiLangList = Field(default_factory=MultiLangList, alias='mixAndLocationTypes', description='Specifying information on the good, service, or function, whether being a production mix or consumption mix, location type of availability (such as e.g. "to consumer" or "at plant"). Separated by commata. May include information of excluded life cycle stages, if any.')
    functional_unit_flow_properties: MultiLangList = Field(default_factory=MultiLangList, alias='functionalUnitFlowProperties', description='Further, quantitative specifying information on the good, service or function in technical term(s): qualifying constituent(s)-content and / or energy-content per unit etc. as appropriate. Separated by commata. (Note: non-qualifying flow properties, CAS No, Synonyms, Chemical formulas etc. are to be documented exclusively in the "Flow data set" of the reference flow of this life cycle model.)')
    common_other: str | None = Field(default=None, alias='common:other')

class CommonClassItemOption0(TidasBaseModel):
    level: LevelType = Field(default=..., alias='@level')
    class_id: str = Field(default=..., alias='@classId')
    text: str = Field(default=..., alias='#text')

class CommonClassItemOption1(TidasBaseModel):
    level: LevelType = Field(default=..., alias='@level')
    class_id: str = Field(default=..., alias='@classId')
    text: str = Field(default=..., alias='#text')

class CommonClassItemOption2(TidasBaseModel):
    level: LevelType = Field(default=..., alias='@level')
    class_id: str = Field(default=..., alias='@classId')
    text: str = Field(default=..., alias='#text')

class CommonClassItemOption3(TidasBaseModel):
    level: LevelType = Field(default=..., alias='@level')
    class_id: str = Field(default=..., alias='@classId')
    text: str = Field(default=..., alias='#text')

class DataSetInformationClassificationInformationCommonClassification(TidasBaseModel):
    """Optional statistical or other classification of the data set. Typically also used for structuring LCA databases."""
    common_class: list[CommonClassItemOption0 | CommonClassItemOption1 | CommonClassItemOption2 | CommonClassItemOption3] = Field(default_factory=list, alias='common:class')
    common_other: str | None = Field(default=None, alias='common:other')

class LifeCycleModelInformationDataSetInformationClassificationInformation(TidasBaseModel):
    """Hierarchical or flat classification of the good, service or function that is provided by this life cycle model; typically used to structure database contents in LCA software, among other purposes. (Note: This entry is NOT required for the identification of a Life cycle model, but it should nevertheless be avoided to use identical names for Life cycle model data sets in the same class. The ILCD classifications are defined in the ILCDClassifications.xml file, for common use.)"""
    common_classification: DataSetInformationClassificationInformationCommonClassification = Field(default=..., alias='common:classification', description='Optional statistical or other classification of the data set. Typically also used for structuring LCA databases.')

class LifeCycleModelDataSetLifeCycleModelInformationDataSetInformation(TidasBaseModel):
    """General data set information, to identify the life cycle model, document a general comment about it, and to reference resulting aggregated process data sets that are based on this ife cycle model and to reference a potential background report."""
    common_uuid: UUID = Field(default=..., alias='common:UUID', description='Automatically generated Universally Unique Identifier of this data set. Together with the "Data set version", the UUID uniquely identifies each data set.')
    name: LifeCycleModelInformationDataSetInformationName = Field(default=..., alias='name', description='General descriptive, specifying, structured name of the Life cycle model data set. Note: Ensure proper name structuring and observe restriction to 100 characters for each of the four name fields.')
    classification_information: LifeCycleModelInformationDataSetInformationClassificationInformation = Field(default=..., alias='classificationInformation', description='Hierarchical or flat classification of the good, service or function that is provided by this life cycle model; typically used to structure database contents in LCA software, among other purposes. (Note: This entry is NOT required for the identification of a Life cycle model, but it should nevertheless be avoided to use identical names for Life cycle model data sets in the same class. The ILCD classifications are defined in the ILCDClassifications.xml file, for common use.)')
    reference_to_resulting_process: GlobalReferenceType | None = Field(default=None, alias='referenceToResultingProcess', description='Reference to the LCI result or partly terminated system process data set(s) that is/are generated from this model.')
    common_general_comment: MultiLangList = Field(default_factory=MultiLangList, alias='common:generalComment', description='General information about the data set.')
    reference_to_external_documentation: GlobalReferenceType | None = Field(default=None, alias='referenceToExternalDocumentation', description='"Source data set(s)" of detailed LCI or LCA study or other study on the process or product represented by this data set, as well as documents / files with overarching documentative information on technology, geographical and / or time aspects etc. on the level of the life cycle model. (Note: can indirectly reference to electronic and online files.)')
    common_other: str | None = Field(default=None, alias='common:other')

class LifeCycleModelDataSetLifeCycleModelInformationQuantitativeReference(TidasBaseModel):
    """This section names the quantitative reference of this data set, i.e. the reference to which the inputs and outputs of all process instances of the life cycle model quantitatively relate."""
    reference_to_reference_process: str = Field(default=..., alias='referenceToReferenceProcess', description='Process instance that scales the life cycle model and thereby all directly and indirectly connected process instances of the model; it is often a process instance at the "end" of the life cycle model chain, or the process that provides the delivered good, service or function of the model.', pattern='^-?\\d+$')
    common_other: str | None = Field(default=None, alias='common:other')

class GroupDeclarationsGroupOption0(TidasBaseModel):
    id: str | None = Field(default=None, alias='@id', pattern='^-?\\d+$')
    group_name: MultiLangList = Field(default_factory=MultiLangList, alias='groupName')

class GroupDeclarationsGroupItem(TidasBaseModel):
    id: str | None = Field(default=None, alias='@id', pattern='^-?\\d+$')
    group_name: MultiLangList = Field(default_factory=MultiLangList, alias='groupName')

class LifeCycleModelInformationTechnologyGroupDeclarations(TidasBaseModel):
    """Section to define groups to which process instances can declare to belong to, in the context of this Life cycle model data set. Groups are user-defined and could be e.g. life cycle stages, foreground/background, ..."""
    group: GroupDeclarationsGroupOption0 | list[GroupDeclarationsGroupItem] | None = Field(default=None, alias='group', description='Definition for each group.')

class GroupsMemberOfOption0(TidasBaseModel):
    group_id: str | None = Field(default=None, alias='@groupId', description='Data set internal ID of the group.', pattern='^-?\\d+$')

class GroupsMemberOfItem(TidasBaseModel):
    group_id: str | None = Field(default=None, alias='@groupId', description='Data set internal ID of the group.', pattern='^-?\\d+$')

class ProcessInstanceItemGroups(TidasBaseModel):
    """Group(s) to which this process instance belongs."""
    member_of: GroupsMemberOfOption0 | list[GroupsMemberOfItem] | None = Field(default=None, alias='memberOf', description='Refers to one user-definable group, to which this process instance belongs.')

class ParametersParameterOption0(TidasBaseModel):
    name: MatV | None = Field(default=None, alias='@name', description='Name of free parameter')

class ParametersParameterItem(TidasBaseModel):
    name: MatV | None = Field(default=None, alias='@name', description='Name of free parameter')

class ProcessInstanceItemParameters(TidasBaseModel):
    """Set of parameters of this process instance with parameter values (changed or unchanged from those in the underlying process data set)."""
    parameter: ParametersParameterOption0 | list[ParametersParameterItem] | None = Field(default=None, alias='parameter', description='Value of the parameter.')

class Option0DownstreamProcessOption0(TidasBaseModel):
    id: str = Field(default=..., alias='@id', description='Internal ID of the process instance in this model which is to be connected to this output exchange.', pattern='^-?\\d+$')
    flow_uuid: UUID = Field(default=..., alias='@flowUUID', description='UUID of the connected flow exchange in the input of the downstream process instance.')
    location: str | None = Field(default=None, alias='@location', description='Location, e.g. country code, of the connected flow exchange in downstream process, if any.')
    dominant: Literal['true', 'false'] | None = Field(default=None, alias='@dominant', description='If the connected exchanges are based on different flow data sets, one of these can be marked as dominant. Dominant means that in cases where the connection itself carries properties (e.g. a flow name that may be used in graphical model display), the properties of the dominant flow object are used.')

class Option0DownstreamProcessItem(TidasBaseModel):
    id: str = Field(default=..., alias='@id', description='Internal ID of the process instance in this model which is to be connected to this output exchange.', pattern='^-?\\d+$')
    flow_uuid: UUID = Field(default=..., alias='@flowUUID', description='UUID of the connected flow exchange in the input of the downstream process instance.')
    location: str | None = Field(default=None, alias='@location', description='Location, e.g. country code, of the connected flow exchange in downstream process, if any.')
    dominant: Literal['true', 'false'] | None = Field(default=None, alias='@dominant', description='If the connected exchanges are based on different flow data sets, one of these can be marked as dominant. Dominant means that in cases where the connection itself carries properties (e.g. a flow name that may be used in graphical model display), the properties of the dominant flow object are used.')

class ConnectionsOutputExchangeOption0(TidasBaseModel):
    dominant: Literal['true', 'false'] = Field(default=..., alias='@dominant', description='If the connected exchanges are based on different flow data sets, one of these can be marked as dominant. Dominant means that in cases where the connection itself carries properties (e.g. a flow name that may be used in graphical model display), the properties of the dominant flow object are used.')
    flow_uuid: UUID = Field(default=..., alias='@flowUUID', description='UUID of the connected flow exchange in the input of the downstream process instance.')
    downstream_process: Option0DownstreamProcessOption0 | list[Option0DownstreamProcessItem] = Field(default=..., alias='downstreamProcess', description='Process instance that is connected downstream with this process instance, with its connected input product or waste (flow) exchange internal ID, the flow UUID and optionally the exchange\'s "location" (if any). Finally, the dominant flow exchange may be identified, where two different flow data sets are connected, in support e.g. of graphical model display.')

class ItemDownstreamProcessOption0(TidasBaseModel):
    id: str = Field(default=..., alias='@id', description='Internal ID of the process instance in this model which is to be connected to this output exchange.', pattern='^-?\\d+$')
    flow_uuid: UUID = Field(default=..., alias='@flowUUID', description='UUID of the connected flow exchange in the input of the downstream process instance.')
    location: str | None = Field(default=None, alias='@location', description='Location, e.g. country code, of the connected flow exchange in downstream process, if any.')
    dominant: Literal['true', 'false'] | None = Field(default=None, alias='@dominant', description='If the connected exchanges are based on different flow data sets, one of these can be marked as dominant. Dominant means that in cases where the connection itself carries properties (e.g. a flow name that may be used in graphical model display), the properties of the dominant flow object are used.')

class ItemDownstreamProcessItem(TidasBaseModel):
    id: str = Field(default=..., alias='@id', description='Internal ID of the process instance in this model which is to be connected to this output exchange.', pattern='^-?\\d+$')
    flow_uuid: UUID = Field(default=..., alias='@flowUUID', description='UUID of the connected flow exchange in the input of the downstream process instance.')
    location: str | None = Field(default=None, alias='@location', description='Location, e.g. country code, of the connected flow exchange in downstream process, if any.')
    dominant: Literal['true', 'false'] | None = Field(default=None, alias='@dominant', description='If the connected exchanges are based on different flow data sets, one of these can be marked as dominant. Dominant means that in cases where the connection itself carries properties (e.g. a flow name that may be used in graphical model display), the properties of the dominant flow object are used.')

class ConnectionsOutputExchangeItem(TidasBaseModel):
    dominant: Literal['true', 'false'] = Field(default=..., alias='@dominant', description='If the connected exchanges are based on different flow data sets, one of these can be marked as dominant. Dominant means that in cases where the connection itself carries properties (e.g. a flow name that may be used in graphical model display), the properties of the dominant flow object are used.')
    flow_uuid: UUID = Field(default=..., alias='@flowUUID', description='UUID of the connected flow exchange in the input of the downstream process instance.')
    downstream_process: ItemDownstreamProcessOption0 | list[ItemDownstreamProcessItem] = Field(default=..., alias='downstreamProcess', description='Process instance that is connected downstream with this process instance, with its connected input product or waste (flow) exchange internal ID, the flow UUID and optionally the exchange\'s "location" (if any). Finally, the dominant flow exchange may be identified, where two different flow data sets are connected, in support e.g. of graphical model display.')

class ProcessInstanceItemConnections(TidasBaseModel):
    """Connection information among process instances, via connecting product or waste flow exchanges."""
    output_exchange: ConnectionsOutputExchangeOption0 | list[ConnectionsOutputExchangeItem] | None = Field(default=None, alias='outputExchange', description="Reference to process data set UUID of one of the connecting output product or waste flow exchanges of this process instance. I.e. which (flow) exchange on output side of this process instance is to be connected to another process instance's input product or waste (flow) exchange?")

class ProcessesProcessInstanceItem(TidasBaseModel):
    data_set_internal_id: str = Field(default=..., alias='@dataSetInternalID', pattern='^-?\\d+$')
    multiplication_factor: str = Field(default=..., alias='@multiplicationFactor', description='The multiplication factor corresponds to the amount of output product from the process instance that is needed over the full life cycle. In practice, the Life Cycle Inventory of a specific process instance shall be multiplied by the multiplication factor to calculate the exact amount needed over the full life cycle.', pattern='^-?\\d+(\\.\\d+)?([eE][-+]?\\d+)?$')
    reference_to_process: GlobalReferenceType = Field(default=..., alias='referenceToProcess', description='Reference to the process data set and (optional) identifying its version, that is included in the eILCD archive of the Life cycle model and/or accessible at a remote location, i.e. an URI or URL.')
    scaling_factors: Real | None = Field(default=None, alias='scalingFactors', description='A multiplicative scaling factor for the entire inventory of this process instance, used e.g. to scale the "Reference process" to the aimed-at amount of product (and thereby indirectly the entire inventory of the life cycle model). Note: Care is to be taken that models are not over- or under-specified - note that each process instance scaling is reducing the model\'s degree of freedom by one.')
    groups: ProcessInstanceItemGroups | None = Field(default=None, alias='groups', description='Group(s) to which this process instance belongs.')
    parameters: ProcessInstanceItemParameters | None = Field(default=None, alias='parameters', description='Set of parameters of this process instance with parameter values (changed or unchanged from those in the underlying process data set).')
    connections: ProcessInstanceItemConnections = Field(default=..., alias='connections', description='Connection information among process instances, via connecting product or waste flow exchanges.')
    common_other: str | None = Field(default=None, alias='common:other')

class GroupsMemberOfOption02(TidasBaseModel):
    group_id: str | None = Field(default=None, alias='@groupId', description='Data set internal ID of the group.', pattern='^-?\\d+$')

class GroupsMemberOfItem2(TidasBaseModel):
    group_id: str | None = Field(default=None, alias='@groupId', description='Data set internal ID of the group.', pattern='^-?\\d+$')

class ProcessInstanceOption1Groups(TidasBaseModel):
    """Group(s) to which this process instance belongs."""
    member_of: GroupsMemberOfOption02 | list[GroupsMemberOfItem2] | None = Field(default=None, alias='memberOf', description='Refers to one user-definable group, to which this process instance belongs.')

class ParametersParameterOption02(TidasBaseModel):
    name: str | None = Field(default=None, alias='@name', description='Name of free parameter')
    parameter: Real | None = Field(default=None, alias='parameter', description='Value of the parameter.')

class ParametersParameterItem2(TidasBaseModel):
    name: str | None = Field(default=None, alias='@name', description='Name of free parameter')
    parameter: Real | None = Field(default=None, alias='parameter', description='Value of the parameter.')

class ProcessInstanceOption1Parameters(TidasBaseModel):
    """Set of parameters of this process instance with parameter values (changed or unchanged from those in the underlying process data set)."""
    parameter: ParametersParameterOption02 | list[ParametersParameterItem2] | None = Field(default=None, alias='parameter', description='Value of the parameter.')

class Option0DownstreamProcessOption02(TidasBaseModel):
    id: str = Field(default=..., alias='@id', description='Internal ID of the process instance in this model which is to be connected to this output exchange.', pattern='^-?\\d+$')
    flow_uuid: UUID = Field(default=..., alias='@flowUUID', description='UUID of the connected flow exchange in the input of the downstream process instance.')
    location: str | None = Field(default=None, alias='@location', description='Location, e.g. country code, of the connected flow exchange in downstream process, if any.')
    dominant: Literal['true', 'false'] | None = Field(default=None, alias='@dominant', description='If the connected exchanges are based on different flow data sets, one of these can be marked as dominant. Dominant means that in cases where the connection itself carries properties (e.g. a flow name that may be used in graphical model display), the properties of the dominant flow object are used.')

class Option0DownstreamProcessItem2(TidasBaseModel):
    id: str = Field(default=..., alias='@id', description='Internal ID of the process instance in this model which is to be connected to this output exchange.', pattern='^-?\\d+$')
    flow_uuid: UUID = Field(default=..., alias='@flowUUID', description='UUID of the connected flow exchange in the input of the downstream process instance.')
    location: str | None = Field(default=None, alias='@location', description='Location, e.g. country code, of the connected flow exchange in downstream process, if any.')
    dominant: Literal['true', 'false'] | None = Field(default=None, alias='@dominant', description='If the connected exchanges are based on different flow data sets, one of these can be marked as dominant. Dominant means that in cases where the connection itself carries properties (e.g. a flow name that may be used in graphical model display), the properties of the dominant flow object are used.')

class ConnectionsOutputExchangeOption02(TidasBaseModel):
    dominant: Literal['true', 'false'] = Field(default=..., alias='@dominant', description='If the connected exchanges are based on different flow data sets, one of these can be marked as dominant. Dominant means that in cases where the connection itself carries properties (e.g. a flow name that may be used in graphical model display), the properties of the dominant flow object are used.')
    flow_uuid: UUID = Field(default=..., alias='@flowUUID', description='UUID of the connected flow exchange in the input of the downstream process instance.')
    downstream_process: Option0DownstreamProcessOption02 | list[Option0DownstreamProcessItem2] = Field(default=..., alias='downstreamProcess', description='Process instance that is connected downstream with this process instance, with its connected input product or waste (flow) exchange internal ID, the flow UUID and optionally the exchange\'s "location" (if any). Finally, the dominant flow exchange may be identified, where two different flow data sets are connected, in support e.g. of graphical model display.')

class ItemDownstreamProcessOption02(TidasBaseModel):
    id: str = Field(default=..., alias='@id', description='Internal ID of the process instance in this model which is to be connected to this output exchange.', pattern='^-?\\d+$')
    flow_uuid: UUID = Field(default=..., alias='@flowUUID', description='UUID of the connected flow exchange in the input of the downstream process instance.')
    location: str | None = Field(default=None, alias='@location', description='Location, e.g. country code, of the connected flow exchange in downstream process, if any.')
    dominant: Literal['true', 'false'] | None = Field(default=None, alias='@dominant', description='If the connected exchanges are based on different flow data sets, one of these can be marked as dominant. Dominant means that in cases where the connection itself carries properties (e.g. a flow name that may be used in graphical model display), the properties of the dominant flow object are used.')

class ItemDownstreamProcessItem2(TidasBaseModel):
    id: str = Field(default=..., alias='@id', description='Internal ID of the process instance in this model which is to be connected to this output exchange.', pattern='^-?\\d+$')
    flow_uuid: UUID = Field(default=..., alias='@flowUUID', description='UUID of the connected flow exchange in the input of the downstream process instance.')
    location: str | None = Field(default=None, alias='@location', description='Location, e.g. country code, of the connected flow exchange in downstream process, if any.')
    dominant: Literal['true', 'false'] | None = Field(default=None, alias='@dominant', description='If the connected exchanges are based on different flow data sets, one of these can be marked as dominant. Dominant means that in cases where the connection itself carries properties (e.g. a flow name that may be used in graphical model display), the properties of the dominant flow object are used.')

class ConnectionsOutputExchangeItem2(TidasBaseModel):
    dominant: Literal['true', 'false'] = Field(default=..., alias='@dominant', description='If the connected exchanges are based on different flow data sets, one of these can be marked as dominant. Dominant means that in cases where the connection itself carries properties (e.g. a flow name that may be used in graphical model display), the properties of the dominant flow object are used.')
    flow_uuid: UUID = Field(default=..., alias='@flowUUID', description='UUID of the connected flow exchange in the input of the downstream process instance.')
    downstream_process: ItemDownstreamProcessOption02 | list[ItemDownstreamProcessItem2] = Field(default=..., alias='downstreamProcess', description='Process instance that is connected downstream with this process instance, with its connected input product or waste (flow) exchange internal ID, the flow UUID and optionally the exchange\'s "location" (if any). Finally, the dominant flow exchange may be identified, where two different flow data sets are connected, in support e.g. of graphical model display.')

class ProcessInstanceOption1Connections(TidasBaseModel):
    """Connection information among process instances, via connecting product or waste flow exchanges."""
    output_exchange: ConnectionsOutputExchangeOption02 | list[ConnectionsOutputExchangeItem2] = Field(default=..., alias='outputExchange', description="Reference to process data set UUID of one of the connecting output product or waste flow exchanges of this process instance. I.e. which (flow) exchange on output side of this process instance is to be connected to another process instance's input product or waste (flow) exchange?")

class ProcessesProcessInstanceOption1(TidasBaseModel):
    data_set_internal_id: str = Field(default=..., alias='@dataSetInternalID', pattern='^-?\\d+$')
    multiplication_factor: str = Field(default=..., alias='@multiplicationFactor', description='The multiplication factor corresponds to the amount of output product from the process instance that is needed over the full life cycle. In practice, the Life Cycle Inventory of a specific process instance shall be multiplied by the multiplication factor to calculate the exact amount needed over the full life cycle.', pattern='^-?\\d+(\\.\\d+)?([eE][-+]?\\d+)?$')
    reference_to_process: GlobalReferenceType = Field(default=..., alias='referenceToProcess', description='Reference to the process data set and (optional) identifying its version, that is included in the eILCD archive of the Life cycle model and/or accessible at a remote location, i.e. an URI or URL.')
    scaling_factors: Real | None = Field(default=None, alias='scalingFactors', description='A multiplicative scaling factor for the entire inventory of this process instance, used e.g. to scale the "Reference process" to the aimed-at amount of product (and thereby indirectly the entire inventory of the life cycle model). Note: Care is to be taken that models are not over- or under-specified - note that each process instance scaling is reducing the model\'s degree of freedom by one.')
    groups: ProcessInstanceOption1Groups | None = Field(default=None, alias='groups', description='Group(s) to which this process instance belongs.')
    parameters: ProcessInstanceOption1Parameters | None = Field(default=None, alias='parameters', description='Set of parameters of this process instance with parameter values (changed or unchanged from those in the underlying process data set).')
    connections: ProcessInstanceOption1Connections = Field(default=..., alias='connections', description='Connection information among process instances, via connecting product or waste flow exchanges.')
    common_other: str | None = Field(default=None, alias='common:other')

class LifeCycleModelInformationTechnologyProcesses(TidasBaseModel):
    """\"Process data set(s)\" included in this life cycle model as separate data set(s)."""
    process_instance: ProcessesProcessInstanceOption1 | list[ProcessesProcessInstanceItem] | None = Field(default=None, alias='processInstance', description='Instances (occurrences) of the same process data set in this life cycle model. Each process data set may occur in different places within the model, with different parameter settings and connected to different other process instances.')

class LifeCycleModelDataSetLifeCycleModelInformationTechnology(TidasBaseModel):
    """Provides information about the technological representativeness of the data set."""
    group_declarations: LifeCycleModelInformationTechnologyGroupDeclarations | None = Field(default=None, alias='groupDeclarations', description='Section to define groups to which process instances can declare to belong to, in the context of this Life cycle model data set. Groups are user-defined and could be e.g. life cycle stages, foreground/background, ...')
    processes: LifeCycleModelInformationTechnologyProcesses = Field(default=..., alias='processes', description='"Process data set(s)" included in this life cycle model as separate data set(s).')
    reference_to_diagram: GlobalReferenceType | None = Field(default=None, alias='referenceToDiagram', description='"Source data set" of the flow diagramm(s), and/or screenshot(s) of the life cycle model represented by this data set. For clearer illustration and documentation of the model. Note: The source data set references the actual picture as jpd or png file or as e.g. pdf file with several pictures.')
    common_other: str | None = Field(default=None, alias='common:other')

class LifecyclemodelsLifeCycleModelDataSetLifeCycleModelInformation(TidasBaseModel):
    """This section comprises the following sub-sections: 1) \"Key data set information\", 2) \"Quantitative reference\", 3) \"Technology\"."""
    data_set_information: LifeCycleModelDataSetLifeCycleModelInformationDataSetInformation = Field(default=..., alias='dataSetInformation', description='General data set information, to identify the life cycle model, document a general comment about it, and to reference resulting aggregated process data sets that are based on this ife cycle model and to reference a potential background report.')
    quantitative_reference: LifeCycleModelDataSetLifeCycleModelInformationQuantitativeReference = Field(default=..., alias='quantitativeReference', description='This section names the quantitative reference of this data set, i.e. the reference to which the inputs and outputs of all process instances of the life cycle model quantitatively relate.')
    technology: LifeCycleModelDataSetLifeCycleModelInformationTechnology = Field(default=..., alias='technology', description='Provides information about the technological representativeness of the data set.')

class LifeCycleModelDataSetModellingAndValidationDataSourcesTreatmentEtc(TidasBaseModel):
    """Data selection, completeness, and treatment principles and procedures, data sources and market coverage information."""
    use_advice_for_data_set: MultiLangList = Field(default_factory=MultiLangList, alias='useAdviceForDataSet', description='Specific methodological advice for data set users that requires attention. E.g. on inclusion/exclusion of whole life cycle stages, specific use phase behavior to be modelled, and other methodological advices.')
    common_other: str | None = Field(default=None, alias='common:other')

class ValidationReviewOption0(TidasBaseModel):
    common_reference_to_name_of_reviewer_and_institution: GlobalReferenceType = Field(default=..., alias='common:referenceToNameOfReviewerAndInstitution', description='"Contact data set" of reviewer. The full name of reviewer(s) and institution(s) as well as a contact address and/or email should be provided in that contact data set.')
    common_other_review_details: MultiLangList = Field(default_factory=MultiLangList, alias='common:otherReviewDetails', description='Further information from the review process, especially comments received from third parties once the data set has been published or additional reviewer comments from an additional external review.')
    common_reference_to_complete_review_report: GlobalReferenceType | None = Field(default=None, alias='common:referenceToCompleteReviewReport', description='"Source data set" of the complete review report.')
    common_other: str | None = Field(default=None, alias='common:other')

class ValidationReviewItem(TidasBaseModel):
    common_reference_to_name_of_reviewer_and_institution: GlobalReferenceType = Field(default=..., alias='common:referenceToNameOfReviewerAndInstitution', description='"Contact data set" of reviewer. The full name of reviewer(s) and institution(s) as well as a contact address and/or email should be provided in that contact data set.')
    common_other_review_details: MultiLangList = Field(default_factory=MultiLangList, alias='common:otherReviewDetails', description='Further information from the review process, especially comments received from third parties once the data set has been published or additional reviewer comments from an additional external review.')
    common_reference_to_complete_review_report: GlobalReferenceType | None = Field(default=None, alias='common:referenceToCompleteReviewReport', description='"Source data set" of the complete review report.')
    common_other: str | None = Field(default=None, alias='common:other')

class LifeCycleModelDataSetModellingAndValidationValidation(TidasBaseModel):
    """Review / validation information on data set."""
    review: ValidationReviewOption0 | list[ValidationReviewItem] = Field(default=..., alias='review', description='Review information on this life cycle model data set')
    common_other: str | None = Field(default=None, alias='common:other')

class ComplianceDeclarationsComplianceOption0(TidasBaseModel):
    common_reference_to_compliance_system: GlobalReferenceType = Field(default=..., alias='common:referenceToComplianceSystem', description='"Source data set" of the "Compliance system" that is declared to be met by the data set.')
    common_approval_of_overall_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:approvalOfOverallCompliance', description='Official approval whether or not and in how far the data set meets all the requirements of the "Compliance system" refered to. This approval should be issued/confirmed by the owner of that compliance system, who is identified via the respective "Contact data set".')
    common_nomenclature_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:nomenclatureCompliance', description='Nomenclature compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_methodological_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:methodologicalCompliance', description='Methodological compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_review_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:reviewCompliance', description='Review/Verification compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_documentation_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:documentationCompliance', description='Documentation/Reporting compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_quality_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:qualityCompliance', description='Quality compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_other: str | None = Field(default=None, alias='common:other')

class ComplianceDeclarationsComplianceItem(TidasBaseModel):
    common_reference_to_compliance_system: GlobalReferenceType = Field(default=..., alias='common:referenceToComplianceSystem', description='"Source data set" of the "Compliance system" that is declared to be met by the data set.')
    common_approval_of_overall_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:approvalOfOverallCompliance', description='Official approval whether or not and in how far the data set meets all the requirements of the "Compliance system" refered to. This approval should be issued/confirmed by the owner of that compliance system, who is identified via the respective "Contact data set".')
    common_nomenclature_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:nomenclatureCompliance', description='Nomenclature compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_methodological_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:methodologicalCompliance', description='Methodological compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_review_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:reviewCompliance', description='Review/Verification compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_documentation_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:documentationCompliance', description='Documentation/Reporting compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_quality_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:qualityCompliance', description='Quality compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_other: str | None = Field(default=None, alias='common:other')

class LifeCycleModelDataSetModellingAndValidationComplianceDeclarations(TidasBaseModel):
    """One or more declarations of compliance to selected standards, schemes and other references, e.g. ISO 14040, ISO 14044, ILCD, EF, EN 15804, ..."""
    compliance: ComplianceDeclarationsComplianceOption0 | list[ComplianceDeclarationsComplianceItem] = Field(default=..., alias='compliance', description='One compliance declaration. Multiple declarations may be provided.')
    common_other: str | None = Field(default=None, alias='common:other')

class LifecyclemodelsLifeCycleModelDataSetModellingAndValidation(TidasBaseModel):
    """This section covers the following sub-sections: 1) \"Data sources, treatment and representativeness\", 2) \"Validation\", and 3) \"Compliance\"."""
    data_sources_treatment_etc: LifeCycleModelDataSetModellingAndValidationDataSourcesTreatmentEtc | None = Field(default=None, alias='dataSourcesTreatmentEtc', description='Data selection, completeness, and treatment principles and procedures, data sources and market coverage information.')
    validation: LifeCycleModelDataSetModellingAndValidationValidation = Field(default=..., alias='validation', description='Review / validation information on data set.')
    compliance_declarations: LifeCycleModelDataSetModellingAndValidationComplianceDeclarations = Field(default=..., alias='complianceDeclarations', description='One or more declarations of compliance to selected standards, schemes and other references, e.g. ISO 14040, ISO 14044, ILCD, EF, EN 15804, ...')
    common_other: str | None = Field(default=None, alias='common:other')

class LifeCycleModelDataSetAdministrativeInformationCommonCommissionerAndGoal(TidasBaseModel):
    """Extract of the information items linked to goal and scope of LCIA method modeling."""
    common_reference_to_commissioner: GlobalReferenceType = Field(default=..., alias='common:referenceToCommissioner', description='"Contact data set" of the commissioner / financing party of the data collection / compilation and of the data set modelling. For groups of commissioners, each single organisation should be named. For data set updates and for direct use of data from formerly commissioned studies, also the original commissioner should be named.')
    common_project: MultiLangList = Field(default_factory=MultiLangList, alias='common:project', description='Project within which the data set was modelled in its present version. [Note: If the project was published e.g. as a report, this can be referenced in the "Publication of data set in:" field in the "Publication and ownership" sub-section.')
    common_intended_applications: MultiLangList = Field(default_factory=MultiLangList, alias='common:intendedApplications', description='Documentation of the intended application(s) of data collection and data set modelling. This indicates / includes information on the level of detail, the specifidity, and the quality ambition in the effort.')
    common_other: str | None = Field(default=None, alias='common:other')

class LifeCycleModelDataSetAdministrativeInformationDataGenerator(TidasBaseModel):
    """\"Contact data set\" of the person(s), working group(s), organisation(s) or database network, that generated the data set, i.e. being technically responsible for its correctness regarding methods, inventory, and documentative information."""
    common_reference_to_person_or_entity_generating_the_data_set: GlobalReferenceType | None = Field(default=None, alias='common:referenceToPersonOrEntityGeneratingTheDataSet', description='"Contact data set" of the person(s), working group(s), organisation(s) or database network, that generated the data set, i.e. being responsible for its correctness regarding methods, inventory, and documentative information.')
    common_other: str | None = Field(default=None, alias='common:other')

class LifeCycleModelDataSetAdministrativeInformationDataEntryBy(TidasBaseModel):
    """\"Contact data set\" of the responsible person or entity that has documented this data set, i.e. entered the data and the descriptive information."""
    common_time_stamp: DateTime = Field(default=..., alias='common:timeStamp', description='Date and time stamp of data set generation, typically an automated entry ("last saved").')
    common_reference_to_data_set_format: GlobalReferenceType = Field(default=..., alias='common:referenceToDataSetFormat', description='"Source data set" of the used version of the ILCD format. If additional data format fields have been integrated into the data set file, using the "namespace" option, the used format namespace(s) are to be given. This is the case if the data sets carries additional information as specified by other, particular LCA formats, e.g. of other database networks or LCA softwares.')
    common_reference_to_person_or_entity_entering_the_data: GlobalReferenceType | None = Field(default=None, alias='common:referenceToPersonOrEntityEnteringTheData', description='"Contact data set" of the responsible person or entity that has documented this data set, i.e. entered the data and the descriptive information.')
    common_other: str | None = Field(default=None, alias='common:other')

class LifeCycleModelDataSetAdministrativeInformationPublicationAndOwnership(TidasBaseModel):
    """Information related to publication and version management of the data set including copyright and access restrictions."""
    common_data_set_version: str = Field(default=..., alias='common:dataSetVersion', description='Version number of data set. First two digits refer to major updates, the second two digits to minor revisions and error corrections etc. The third three digits are intended for automatic and internal counting of versions during data set development. Together with the data set\'s UUID, the "Data set version" uniquely identifies each data set.')
    common_reference_to_preceding_data_set_version: GlobalReferenceType | None = Field(default=None, alias='common:referenceToPrecedingDataSetVersion', description='Last preceding data set, which was replaced by this version. Either a URI of that data set (i.e. an internet address) or its UUID plus version number is given (or both).')
    common_permanent_data_set_uri: str = Field(default=..., alias='common:permanentDataSetURI', description="URI (i.e. an internet address) of the original of this data set. [Note: This equally globally unique identifier supports users and software tools to identify and retrieve the original version of a data set via the internet or to check for available updates. The URI must not represent an existing WWW address, but it should be unique and point to the data access point, e.g. by combining the data owner's www path with the data set's UUID, e.g. http://www.mycompany.com/lca/processes/50f12420-8855-12db-b606-0900210c9a66.]")
    common_reference_to_ownership_of_data_set: GlobalReferenceType = Field(default=..., alias='common:referenceToOwnershipOfDataSet', description='Quality compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_copyright: Literal['true', 'false'] = Field(default=..., alias='common:copyright', description='Indicates whether or not a copyright on the data set exists. Decided upon by the "Owner of data set". [Note: See also field "Access and use restrictions".]')
    common_reference_to_entities_with_exclusive_access: GlobalReferenceType | None = Field(default=None, alias='common:referenceToEntitiesWithExclusiveAccess', description='"Contact data set" of those entities or persons (or groups of these), to which an exclusive access to this data set is granted. Mainly intended to be used in confidentiality management in projects. [Note: See also field "Access and use restrictions".]')
    common_license_type: Literal['Free of charge for all users and uses', 'Free of charge for some user types or use types', 'Free of charge for members only', 'License fee', 'Other'] = Field(default=..., alias='common:licenseType', description='Type of license that applies to the access and use of this data set.')
    common_access_restrictions: MultiLangList = Field(default_factory=MultiLangList, alias='common:accessRestrictions', description='Access restrictions / use conditions for this data set as free text or referring to e.g. license conditions. In case of no restrictions "None" is entered.')
    common_other: str | None = Field(default=None, alias='common:other')

class LifecyclemodelsLifeCycleModelDataSetAdministrativeInformation(TidasBaseModel):
    """Information required for data set management and administration."""
    common_commissioner_and_goal: LifeCycleModelDataSetAdministrativeInformationCommonCommissionerAndGoal = Field(default=..., alias='common:commissionerAndGoal', description='Extract of the information items linked to goal and scope of LCIA method modeling.')
    data_generator: LifeCycleModelDataSetAdministrativeInformationDataGenerator | None = Field(default=None, alias='dataGenerator', description='"Contact data set" of the person(s), working group(s), organisation(s) or database network, that generated the data set, i.e. being technically responsible for its correctness regarding methods, inventory, and documentative information.')
    data_entry_by: LifeCycleModelDataSetAdministrativeInformationDataEntryBy = Field(default=..., alias='dataEntryBy', description='"Contact data set" of the responsible person or entity that has documented this data set, i.e. entered the data and the descriptive information.')
    publication_and_ownership: LifeCycleModelDataSetAdministrativeInformationPublicationAndOwnership = Field(default=..., alias='publicationAndOwnership', description='Information related to publication and version management of the data set including copyright and access restrictions.')
    common_other: str | None = Field(default=None, alias='common:other')

class LifecyclemodelsLifeCycleModelDataSet(TidasBaseModel):
    xmlns: Literal['http://eplca.jrc.ec.europa.eu/ILCD/LifeCycleModel/2017'] = Field(default=..., alias='@xmlns')
    xmlns_acme: Literal['http://acme.com/custom'] = Field(default=..., alias='@xmlns:acme')
    xmlns_common: Literal['http://lca.jrc.it/ILCD/Common'] = Field(default=..., alias='@xmlns:common')
    xmlns_xsi: Literal['http://www.w3.org/2001/XMLSchema-instance'] = Field(default=..., alias='@xmlns:xsi')
    locations: Literal['../ILCDLocations.xml'] = Field(default=..., alias='@locations')
    version: Literal['1.1'] = Field(default=..., alias='@version')
    xsi_schema_location: Literal['http://eplca.jrc.ec.europa.eu/ILCD/LifeCycleModel/2017 ../../schemas/ILCD_LifeCycleModelDataSet.xsd'] = Field(default=..., alias='@xsi:schemaLocation')
    life_cycle_model_information: LifecyclemodelsLifeCycleModelDataSetLifeCycleModelInformation = Field(default=..., alias='lifeCycleModelInformation', description='This section comprises the following sub-sections: 1) "Key data set information", 2) "Quantitative reference", 3) "Technology".')
    modelling_and_validation: LifecyclemodelsLifeCycleModelDataSetModellingAndValidation = Field(default=..., alias='modellingAndValidation', description='This section covers the following sub-sections: 1) "Data sources, treatment and representativeness", 2) "Validation", and 3) "Compliance".')
    administrative_information: LifecyclemodelsLifeCycleModelDataSetAdministrativeInformation = Field(default=..., alias='administrativeInformation', description='Information required for data set management and administration.')
    common_other: str | None = Field(default=None, alias='common:other')

class Lifecyclemodels(TidasBaseModel):
    life_cycle_model_data_set: LifecyclemodelsLifeCycleModelDataSet = Field(default=..., alias='lifeCycleModelDataSet')
