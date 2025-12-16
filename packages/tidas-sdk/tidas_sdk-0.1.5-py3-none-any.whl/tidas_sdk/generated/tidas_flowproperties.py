"""
Auto generated file. DO NOT EDIT.
Source: tidas_flowproperties.json
"""
from __future__ import annotations

from typing import Literal

from pydantic import Field
from tidas_sdk.core.base import TidasBaseModel
from tidas_sdk.core.multilang import MultiLangList

from .tidas_data_types import GlobalReferenceType
from .tidas_data_types import LevelType
from .tidas_data_types import UUID
from datetime import datetime

class ClassificationInformationCommonClassificationCommonClass(TidasBaseModel):
    level: LevelType = Field(default=..., alias='@level')
    class_id: str = Field(default=..., alias='@classId')
    text: str = Field(default=..., alias='#text')

class DataSetInformationClassificationInformationCommonClassification(TidasBaseModel):
    """Optional statistical or other classification of the data set. Typically also used for structuring LCA databases."""
    common_class: ClassificationInformationCommonClassificationCommonClass = Field(default=..., alias='common:class')
    common_other: str | None = Field(default=None, alias='common:other')

class FlowPropertiesInformationDataSetInformationClassificationInformation(TidasBaseModel):
    """Hierachical classification of the Flow property foreseen to be used to structure the Flow property content of the database. (Note: This entry is NOT required for the identification of the Flow property data set. It should nevertheless be avoided to use identical names for Flow properties in the same class."""
    common_classification: DataSetInformationClassificationInformationCommonClassification = Field(default=..., alias='common:classification', description='Optional statistical or other classification of the data set. Typically also used for structuring LCA databases.')

class FlowPropertyDataSetFlowPropertiesInformationDataSetInformation(TidasBaseModel):
    common_uuid: UUID = Field(default=..., alias='common:UUID', description='Automatically generated Universally Unique Identifier of this data set. Together with the "Data set version", the UUID uniquely identifies each data set.')
    common_name: MultiLangList = Field(default_factory=MultiLangList, alias='common:name', description='Name of flow property.')
    common_synonyms: MultiLangList = Field(default_factory=MultiLangList, alias='common:synonyms', description='Synonyms are alternative names for the "Name" of the Flow property.')
    classification_information: FlowPropertiesInformationDataSetInformationClassificationInformation = Field(default=..., alias='classificationInformation', description='Hierachical classification of the Flow property foreseen to be used to structure the Flow property content of the database. (Note: This entry is NOT required for the identification of the Flow property data set. It should nevertheless be avoided to use identical names for Flow properties in the same class.')
    common_general_comment: MultiLangList = Field(default_factory=MultiLangList, alias='common:generalComment', description='Free text for general information about the data set. It may contain comments on e.g. information sources used as well as general (internal, not reviewed) quality statements.')
    common_other: str | None = Field(default=None, alias='common:other')

class FlowPropertyDataSetFlowPropertiesInformationQuantitativeReference(TidasBaseModel):
    """This section allows to refer to the Flow property's quantitative reference, which is always a unit (i.e. that unit, in which the property is measured, e.g. \"MJ\" for energy-related Flow properties)."""
    reference_to_reference_unit_group: GlobalReferenceType = Field(default=..., alias='referenceToReferenceUnitGroup', description='"Unit group data set" and its reference unit, in which the Flow property is measured.')
    common_other: str | None = Field(default=None, alias='common:other')

class FlowpropertiesFlowPropertyDataSetFlowPropertiesInformation(TidasBaseModel):
    data_set_information: FlowPropertyDataSetFlowPropertiesInformationDataSetInformation = Field(default=..., alias='dataSetInformation')
    quantitative_reference: FlowPropertyDataSetFlowPropertiesInformationQuantitativeReference = Field(default=..., alias='quantitativeReference', description='This section allows to refer to the Flow property\'s quantitative reference, which is always a unit (i.e. that unit, in which the property is measured, e.g. "MJ" for energy-related Flow properties).')
    common_other: str | None = Field(default=None, alias='common:other')

class FlowPropertyDataSetModellingAndValidationDataSourcesTreatmentAndRepresentativeness(TidasBaseModel):
    reference_to_data_source: GlobalReferenceType | None = Field(default=None, alias='referenceToDataSource', description='"Source data set" of data source(s) used for the data set e.g. a paper, a questionnaire, a monography etc. The main raw data sources should be named, too. [Note: relevant especially for market price data.]')
    common_other: str | None = Field(default=None, alias='common:other')

class ComplianceDeclarationsComplianceOption0(TidasBaseModel):
    common_reference_to_compliance_system: GlobalReferenceType = Field(default=..., alias='common:referenceToComplianceSystem', description='"Source data set" of the "Compliance system" that is declared to be met by the data set.')
    common_approval_of_overall_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:approvalOfOverallCompliance', description='Official approval whether or not and in how far the data set meets all the requirements of the "Compliance system" refered to. This approval should be issued/confirmed by the owner of that compliance system, who is identified via the respective "Contact data set".')

class ComplianceDeclarationsComplianceItem(TidasBaseModel):
    common_reference_to_compliance_system: GlobalReferenceType = Field(default=..., alias='common:referenceToComplianceSystem', description='"Source data set" of the "Compliance system" that is declared to be met by the data set.')
    common_approval_of_overall_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:approvalOfOverallCompliance', description='Official approval whether or not and in how far the data set meets all the requirements of the "Compliance system" refered to. This approval should be issued/confirmed by the owner of that compliance system, who is identified via the respective "Contact data set".')

class FlowPropertyDataSetModellingAndValidationComplianceDeclarations(TidasBaseModel):
    """Statements on compliance of several data set aspects with compliance requirements as defined by the referenced compliance system (e.g. an EPD scheme, handbook of a national or international data network such as the ILCD, etc.)."""
    compliance: ComplianceDeclarationsComplianceOption0 | list[ComplianceDeclarationsComplianceItem] = Field(default=..., alias='compliance', description='One compliance declaration. Multiple declarations may be provided.')
    common_other: str | None = Field(default=None, alias='common:other')

class FlowpropertiesFlowPropertyDataSetModellingAndValidation(TidasBaseModel):
    """Covers the five sub-sections 1) LCI method (not used), 2) Data sources, treatment and representativeness (only 3 fields), 3) Completeness (not used), 4) Validation, and 5) Compliance."""
    data_sources_treatment_and_representativeness: FlowPropertyDataSetModellingAndValidationDataSourcesTreatmentAndRepresentativeness | None = Field(default=None, alias='dataSourcesTreatmentAndRepresentativeness')
    compliance_declarations: FlowPropertyDataSetModellingAndValidationComplianceDeclarations = Field(default=..., alias='complianceDeclarations', description='Statements on compliance of several data set aspects with compliance requirements as defined by the referenced compliance system (e.g. an EPD scheme, handbook of a national or international data network such as the ILCD, etc.).')
    common_other: str | None = Field(default=None, alias='common:other')

class FlowPropertyDataSetAdministrativeInformationDataEntryBy(TidasBaseModel):
    """Staff or entity, that documented the generated data set, entering the information into the database; plus administrative information linked to the data entry activity."""
    common_time_stamp: datetime = Field(default=..., alias='common:timeStamp', description='Date and time stamp of data set generation, typically an automated entry ("last saved").')
    common_reference_to_data_set_format: GlobalReferenceType = Field(default=..., alias='common:referenceToDataSetFormat', description='"Source data set" of the used version of the ILCD format. If additional data format fields have been integrated into the data set file, using the "namespace" option, the used format namespace(s) are to be given. This is the case if the data sets carries additional information as specified by other, particular LCA formats, e.g. of other database networks or LCA softwares.')
    common_other: str | None = Field(default=None, alias='common:other')

class FlowPropertyDataSetAdministrativeInformationPublicationAndOwnership(TidasBaseModel):
    """Information related to publication and version management of the data set including copyright and access restrictions."""
    common_data_set_version: str = Field(default=..., alias='common:dataSetVersion', description='Version number of data set. First two digits refer to major updates, the second two digits to minor revisions and error corrections etc. The third three digits are intended for automatic and internal counting of versions during data set development. Together with the data set\'s UUID, the "Data set version" uniquely identifies each data set.')
    common_reference_to_preceding_data_set_version: GlobalReferenceType | None = Field(default=None, alias='common:referenceToPrecedingDataSetVersion', description='Last preceding data set, which was replaced by this version. Either a URI of that data set (i.e. an internet address) or its UUID plus version number is given (or both).')
    common_permanent_data_set_uri: str | None = Field(default=None, alias='common:permanentDataSetURI', description="URI (i.e. an internet address) of the original of this data set. [Note: This equally globally unique identifier supports users and software tools to identify and retrieve the original version of a data set via the internet or to check for available updates. The URI must not represent an existing WWW address, but it should be unique and point to the data access point, e.g. by combining the data owner's www path with the data set's UUID, e.g. http://www.mycompany.com/lca/processes/50f12420-8855-12db-b606-0900210c9a66.]")
    common_reference_to_ownership_of_data_set: GlobalReferenceType = Field(default=..., alias='common:referenceToOwnershipOfDataSet', description='"Contact data set" of the person or entity who owns this data set. (Note: this is not necessarily the publisher of the data set.)')
    common_other: str | None = Field(default=None, alias='common:other')

class FlowpropertiesFlowPropertyDataSetAdministrativeInformation(TidasBaseModel):
    """Information on data set management and administration."""
    data_entry_by: FlowPropertyDataSetAdministrativeInformationDataEntryBy = Field(default=..., alias='dataEntryBy', description='Staff or entity, that documented the generated data set, entering the information into the database; plus administrative information linked to the data entry activity.')
    publication_and_ownership: FlowPropertyDataSetAdministrativeInformationPublicationAndOwnership = Field(default=..., alias='publicationAndOwnership', description='Information related to publication and version management of the data set including copyright and access restrictions.')
    common_other: str | None = Field(default=None, alias='common:other')

class FlowpropertiesFlowPropertyDataSet(TidasBaseModel):
    xmlns: Literal['http://lca.jrc.it/ILCD/FlowProperty'] = Field(default=..., alias='@xmlns')
    xmlns_common: Literal['http://lca.jrc.it/ILCD/Common'] = Field(default=..., alias='@xmlns:common')
    xmlns_xsi: Literal['http://www.w3.org/2001/XMLSchema-instance'] = Field(default=..., alias='@xmlns:xsi')
    version: Literal['1.1'] = Field(default=..., alias='@version')
    xsi_schema_location: Literal['http://lca.jrc.it/ILCD/FlowProperty ../../schemas/ILCD_FlowPropertyDataSet.xsd'] = Field(default=..., alias='@xsi:schemaLocation')
    flow_properties_information: FlowpropertiesFlowPropertyDataSetFlowPropertiesInformation = Field(default=..., alias='flowPropertiesInformation')
    modelling_and_validation: FlowpropertiesFlowPropertyDataSetModellingAndValidation | None = Field(default=None, alias='modellingAndValidation', description='Covers the five sub-sections 1) LCI method (not used), 2) Data sources, treatment and representativeness (only 3 fields), 3) Completeness (not used), 4) Validation, and 5) Compliance.')
    administrative_information: FlowpropertiesFlowPropertyDataSetAdministrativeInformation = Field(default=..., alias='administrativeInformation', description='Information on data set management and administration.')
    common_other: str | None = Field(default=None, alias='common:other')

class Flowproperties(TidasBaseModel):
    flow_property_data_set: FlowpropertiesFlowPropertyDataSet = Field(default=..., alias='flowPropertyDataSet')
