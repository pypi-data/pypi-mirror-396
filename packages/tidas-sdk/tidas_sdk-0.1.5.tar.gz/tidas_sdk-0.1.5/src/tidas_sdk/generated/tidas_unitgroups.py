"""
Auto generated file. DO NOT EDIT.
Source: tidas_unitgroups.json
"""
from __future__ import annotations

from typing import Literal

from pydantic import Field
from tidas_sdk.core.base import TidasBaseModel
from tidas_sdk.core.multilang import MultiLangList

from .tidas_data_types import DateTime
from .tidas_data_types import GlobalReferenceType
from .tidas_data_types import Int5
from .tidas_data_types import LevelType
from .tidas_data_types import Real
from .tidas_data_types import String
from .tidas_data_types import UUID
from datetime import datetime

class ClassificationInformationCommonClassificationCommonClass(TidasBaseModel):
    level: LevelType = Field(default=..., alias='@level', description='If more than one class is specified in a hierachical classification system, the hierarchy level (1,2,...) could be specified with this attribute of class.')
    class_id: str = Field(default=..., alias='@classId', description="Unique identifier for the class. [Notes: If such identifiers are also defined in the referenced category file, they should be identical. Identifiers can be UUID's, but also other forms are allowed.]")
    text: str = Field(default=..., alias='#text')

class DataSetInformationClassificationInformationCommonClassification(TidasBaseModel):
    """Optional statistical or other classification of the data set. Typically also used for structuring LCA databases."""
    common_class: ClassificationInformationCommonClassificationCommonClass = Field(default=..., alias='common:class')
    common_other: str | None = Field(default=None, alias='common:other')

class UnitGroupInformationDataSetInformationClassificationInformation(TidasBaseModel):
    """Hierachical classification of the Unit groups; foreseen to be used to structure the Unit group content of the database. (Note: This entry is NOT required for the identification of the Unit group data set. It should nevertheless be avoided to use identical names for Unit groups in the same class."""
    common_classification: DataSetInformationClassificationInformationCommonClassification = Field(default=..., alias='common:classification', description='Optional statistical or other classification of the data set. Typically also used for structuring LCA databases.')

class UnitGroupDataSetUnitGroupInformationDataSetInformation(TidasBaseModel):
    common_uuid: UUID = Field(default=..., alias='common:UUID', description='Automatically generated Universally Unique Identifier of this data set. Together with the "Data set version", the UUID uniquely identifies each data set.')
    common_name: MultiLangList = Field(default_factory=MultiLangList, alias='common:name', description='Name of the unit group, typically indicating for which flow property or group of flow properties it is used. The individual units are named in the "Units" section of the "Unit group data set"')
    classification_information: UnitGroupInformationDataSetInformationClassificationInformation = Field(default=..., alias='classificationInformation', description='Hierachical classification of the Unit groups; foreseen to be used to structure the Unit group content of the database. (Note: This entry is NOT required for the identification of the Unit group data set. It should nevertheless be avoided to use identical names for Unit groups in the same class.')
    common_general_comment: MultiLangList = Field(default_factory=MultiLangList, alias='common:generalComment', description='Free text for general information about the data set. E.g. coverage of different unit systems, information sources used, etc.')
    common_other: str | None = Field(default=None, alias='common:other')

class UnitGroupDataSetUnitGroupInformationQuantitativeReference(TidasBaseModel):
    reference_to_reference_unit: Int5 = Field(default=..., alias='referenceToReferenceUnit')
    common_other: str | None = Field(default=None, alias='common:other')

class UnitgroupsUnitGroupDataSetUnitGroupInformation(TidasBaseModel):
    data_set_information: UnitGroupDataSetUnitGroupInformationDataSetInformation = Field(default=..., alias='dataSetInformation')
    quantitative_reference: UnitGroupDataSetUnitGroupInformationQuantitativeReference = Field(default=..., alias='quantitativeReference')
    common_other: str | None = Field(default=None, alias='common:other')

class ComplianceDeclarationsComplianceOption0(TidasBaseModel):
    common_reference_to_compliance_system: GlobalReferenceType = Field(default=..., alias='common:referenceToComplianceSystem')
    common_approval_of_overall_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:approvalOfOverallCompliance')
    common_other: str | None = Field(default=None, alias='common:other')

class ComplianceDeclarationsComplianceItem(TidasBaseModel):
    common_reference_to_compliance_system: GlobalReferenceType = Field(default=..., alias='common:referenceToComplianceSystem')
    common_approval_of_overall_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:approvalOfOverallCompliance')
    common_other: str | None = Field(default=None, alias='common:other')

class UnitGroupDataSetModellingAndValidationComplianceDeclarations(TidasBaseModel):
    compliance: ComplianceDeclarationsComplianceOption0 | list[ComplianceDeclarationsComplianceItem] = Field(default=..., alias='compliance', description='One compliance declaration. Multiple declarations may be provided.')
    common_other: str | None = Field(default=None, alias='common:other')

class UnitgroupsUnitGroupDataSetModellingAndValidation(TidasBaseModel):
    compliance_declarations: UnitGroupDataSetModellingAndValidationComplianceDeclarations = Field(default=..., alias='complianceDeclarations')
    common_other: str | None = Field(default=None, alias='common:other')

class UnitGroupDataSetAdministrativeInformationDataEntryBy(TidasBaseModel):
    common_time_stamp: DateTime = Field(default=..., alias='common:timeStamp', description='Date and time stamp of data set generation, typically an automated entry ("last saved").')
    common_reference_to_data_set_format: GlobalReferenceType = Field(default=..., alias='common:referenceToDataSetFormat', description='"Source data set" of the used version of the ILCD format. If additional data format fields have been integrated into the data set file, using the "namespace" option, the used format namespace(s) are to be given. This is the case if the data sets carries additional information as specified by other, particular LCA formats, e.g. of other database networks or LCA softwares.')
    common_other: str | None = Field(default=None, alias='common:other')

class UnitGroupDataSetAdministrativeInformationPublicationAndOwnership(TidasBaseModel):
    common_data_set_version: str = Field(default=..., alias='common:dataSetVersion', description='Version number of data set. First two digits refer to major updates, the second two digits to minor revisions and error corrections etc. The third three digits are intended for automatic and internal counting of versions during data set development. Together with the data set\'s UUID, the "Data set version" uniquely identifies each data set.')
    common_reference_to_preceding_data_set_version: GlobalReferenceType | None = Field(default=None, alias='common:referenceToPrecedingDataSetVersion', description='Last preceding data set, which was replaced by this version. Either a URI of that data set (i.e. an internet address) or its UUID plus version number is given (or both).')
    common_permanent_data_set_uri: str | None = Field(default=None, alias='common:permanentDataSetURI', description="URI (i.e. an internet address) of the original of this data set. [Note: This equally globally unique identifier supports users and software tools to identify and retrieve the original version of a data set via the internet or to check for available updates. The URI must not represent an existing WWW address, but it should be unique and point to the data access point, e.g. by combining the data owner's www path with the data set's UUID, e.g. http://www.mycompany.com/lca/processes/50f12420-8855-12db-b606-0900210c9a66.]")
    common_reference_to_ownership_of_data_set: GlobalReferenceType = Field(default=..., alias='common:referenceToOwnershipOfDataSet', description='"Contact data set" of the person or entity who owns this data set. (Note: this is not necessarily the publisher of the data set.)')
    common_other: str | None = Field(default=None, alias='common:other')

class UnitgroupsUnitGroupDataSetAdministrativeInformation(TidasBaseModel):
    data_entry_by: UnitGroupDataSetAdministrativeInformationDataEntryBy = Field(default=..., alias='dataEntryBy')
    publication_and_ownership: UnitGroupDataSetAdministrativeInformationPublicationAndOwnership = Field(default=..., alias='publicationAndOwnership')
    common_other: str | None = Field(default=None, alias='common:other')

class UnitsUnitOption0(TidasBaseModel):
    data_set_internal_id: Int5 | None = Field(default=None, alias='@dataSetInternalID')
    name: String | None = Field(default=None, alias='name')
    mean_value: Real | None = Field(default=None, alias='meanValue')
    general_comment: MultiLangList = Field(default_factory=MultiLangList, alias='generalComment', description='General comment on each single unit, typically giving the long name and unit system from which this unit stems, and (if necessary) referring to specifc data sources used, or for workflow purposes about status of "finalisation" of an entry etc.')
    common_other: str | None = Field(default=None, alias='common:other')

class UnitsUnitItem(TidasBaseModel):
    data_set_internal_id: Int5 | None = Field(default=None, alias='@dataSetInternalID')
    name: String | None = Field(default=None, alias='name')
    mean_value: Real | None = Field(default=None, alias='meanValue')
    general_comment: MultiLangList = Field(default_factory=MultiLangList, alias='generalComment', description='General comment on each single unit, typically giving the long name and unit system from which this unit stems, and (if necessary) referring to specifc data sources used, or for workflow purposes about status of "finalisation" of an entry etc.')

class UnitgroupsUnitGroupDataSetUnits(TidasBaseModel):
    unit: UnitsUnitOption0 | list[UnitsUnitItem] | None = Field(default=None, alias='unit')
    common_other: str | None = Field(default=None, alias='common:other')

class UnitgroupsUnitGroupDataSet(TidasBaseModel):
    xmlns: Literal['http://lca.jrc.it/ILCD/UnitGroup'] = Field(default=..., alias='@xmlns')
    xmlns_common: Literal['http://lca.jrc.it/ILCD/Common'] = Field(default=..., alias='@xmlns:common')
    xmlns_xsi: Literal['http://www.w3.org/2001/XMLSchema-instance'] = Field(default=..., alias='@xmlns:xsi')
    version: Literal['1.1'] = Field(default=..., alias='@version')
    xsi_schema_location: Literal['http://lca.jrc.it/ILCD/UnitGroup ../../schemas/ILCD_UnitGroupDataSet.xsd'] = Field(default=..., alias='@xsi:schemaLocation')
    unit_group_information: UnitgroupsUnitGroupDataSetUnitGroupInformation = Field(default=..., alias='unitGroupInformation')
    modelling_and_validation: UnitgroupsUnitGroupDataSetModellingAndValidation = Field(default=..., alias='modellingAndValidation')
    administrative_information: UnitgroupsUnitGroupDataSetAdministrativeInformation = Field(default=..., alias='administrativeInformation')
    units: UnitgroupsUnitGroupDataSetUnits | None = Field(default=None, alias='units')
    common_other: str | None = Field(default=None, alias='common:other')

class Unitgroups(TidasBaseModel):
    unit_group_data_set: UnitgroupsUnitGroupDataSet = Field(default=..., alias='unitGroupDataSet')
