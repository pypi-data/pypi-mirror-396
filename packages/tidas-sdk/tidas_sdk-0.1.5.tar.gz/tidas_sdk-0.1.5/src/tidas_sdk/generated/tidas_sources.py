"""
Auto generated file. DO NOT EDIT.
Source: tidas_sources.json
"""
from __future__ import annotations

from typing import Literal

from pydantic import Field
from tidas_sdk.core.base import TidasBaseModel
from tidas_sdk.core.multilang import MultiLangList

from .tidas_data_types import DateTime
from .tidas_data_types import GlobalReferenceType
from .tidas_data_types import LevelType
from .tidas_data_types import UUID
from datetime import datetime

class ClassificationInformationCommonClassificationCommonClass(TidasBaseModel):
    level: LevelType = Field(default=..., alias='@level')
    class_id: str = Field(default=..., alias='@classId')
    text: str = Field(default=..., alias='#text')

class DataSetInformationClassificationInformationCommonClassification(TidasBaseModel):
    common_class: ClassificationInformationCommonClassificationCommonClass = Field(default=..., alias='common:class')
    common_other: str | None = Field(default=None, alias='common:other')

class SourceInformationDataSetInformationClassificationInformation(TidasBaseModel):
    """Hierachical classification of the Source foreseen to be used to structure the Source content of the database. (Note: This entry is NOT required for the identification of a Source. It should nevertheless be avoided to use identical names for Source in the same class."""
    common_classification: DataSetInformationClassificationInformationCommonClassification = Field(default=..., alias='common:classification')

class SourceInformationDataSetInformationReferenceToDigitalFile(TidasBaseModel):
    """Link to a digital file of the source (www-address or intranet-path; relative or absolue path). (Info: Allows direct access to e.g. complete reports of further documentation, which may also be digitally attached to this data set and exchanged jointly with the XML file.)"""
    uri: str | None = Field(default=None, alias='@uri')

class SourceDataSetSourceInformationDataSetInformation(TidasBaseModel):
    common_uuid: UUID = Field(default=..., alias='common:UUID', description='Automatically generated Universally Unique Identifier of this data set. Together with the "Data set version", the UUID uniquely identifies each data set.')
    common_short_name: MultiLangList = Field(default_factory=MultiLangList, alias='common:shortName', description='Short name for the "Source citation", i.e. for the bibliographical reference or reference to internal data sources used.')
    classification_information: SourceInformationDataSetInformationClassificationInformation = Field(default=..., alias='classificationInformation', description='Hierachical classification of the Source foreseen to be used to structure the Source content of the database. (Note: This entry is NOT required for the identification of a Source. It should nevertheless be avoided to use identical names for Source in the same class.')
    source_citation: str | None = Field(default=None, alias='sourceCitation', description='Bibliographical reference or reference to internal data source. Also used in order to reference to databases and tools, data set formats, conformity systems, pictures etc..')
    publication_type: Literal['Undefined', 'Article in periodical', 'Chapter in anthology', 'Monograph', 'Direct measurement', 'Oral communication', 'Personal written communication', 'Questionnaire', 'Software or database', 'Other unpublished and grey literature'] | None = Field(default=None, alias='publicationType', description='Bibliographic publication type of the source.')
    source_description_or_comment: MultiLangList = Field(default_factory=MultiLangList, alias='sourceDescriptionOrComment', description='Free text for additional description of the source. In case of use of published data it may contain a brief summary of the publication and the kind of medium used (e.g. CD-ROM, hard copy).')
    reference_to_digital_file: SourceInformationDataSetInformationReferenceToDigitalFile | None = Field(default=None, alias='referenceToDigitalFile', description='Link to a digital file of the source (www-address or intranet-path; relative or absolue path). (Info: Allows direct access to e.g. complete reports of further documentation, which may also be digitally attached to this data set and exchanged jointly with the XML file.)')
    reference_to_contact: GlobalReferenceType | None = Field(default=None, alias='referenceToContact', description='"Contact data set"s of working groups, organisations or database networks to which EITHER this person or entity OR this database, data set format, or compliance system belongs. [Note: This does not necessarily imply a legally binding relationship, but may also be a voluntary membership.]')
    reference_to_logo: GlobalReferenceType | None = Field(default=None, alias='referenceToLogo', description='"Source data set" of the logo of the organisation or source to be used in reports etc.')
    common_other: str | None = Field(default=None, alias='common:other')

class SourcesSourceDataSetSourceInformation(TidasBaseModel):
    data_set_information: SourceDataSetSourceInformationDataSetInformation = Field(default=..., alias='dataSetInformation')
    common_other: str | None = Field(default=None, alias='common:other')

class SourceDataSetAdministrativeInformationDataEntryBy(TidasBaseModel):
    common_time_stamp: DateTime = Field(default=..., alias='common:timeStamp', description="Date and time stamp of data set generation, typically an automated entry ('last saved').")
    common_reference_to_data_set_format: GlobalReferenceType = Field(default=..., alias='common:referenceToDataSetFormat', description='"Source data set" of the used version of the ILCD format. If additional data format fields have been integrated into the data set file, using the "namespace" option, the used format namespace(s) are to be given. This is the case if the data sets carries additional information as specified by other, particular LCA formats, e.g. of other database networks or LCA softwares.')
    common_other: str | None = Field(default=None, alias='common:other')

class SourceDataSetAdministrativeInformationPublicationAndOwnership(TidasBaseModel):
    """Information related to publication and version management of the data set including copyright and access restrictions."""
    common_data_set_version: str = Field(default=..., alias='common:dataSetVersion', description='Version number of data set. First two digits refer to major updates, the second two digits to minor revisions and error corrections etc. The third three digits are intended for automatic and internal counting of versions during data set development. Together with the data set\'s UUID, the "Data set version" uniquely identifies each data set.')
    common_reference_to_preceding_data_set_version: GlobalReferenceType | None = Field(default=None, alias='common:referenceToPrecedingDataSetVersion', description='Last preceding data set, which was replaced by this version. Either a URI of that data set (i.e. an internet address) or its UUID plus version number is given (or both).')
    common_permanent_data_set_uri: str | None = Field(default=None, alias='common:permanentDataSetURI', description="URI (i.e. an internet address) of the original of this data set. [Note: This equally globally unique identifier supports users and software tools to identify and retrieve the original version of a data set via the internet or to check for available updates. The URI must not represent an existing WWW address, but it should be unique and point to the data access point, e.g. by combining the data owner's www path with the data set's UUID, e.g. http://www.mycompany.com/lca/processes/50f12420-8855-12db-b606-0900210c9a66.]")
    common_reference_to_ownership_of_data_set: GlobalReferenceType = Field(default=..., alias='common:referenceToOwnershipOfDataSet', description='"Contact data set" of the person or entity who owns this data set. (Note: this is not necessarily the publisher of the data set.)')
    common_other: str | None = Field(default=None, alias='common:other')

class SourcesSourceDataSetAdministrativeInformation(TidasBaseModel):
    """Information on data set management and administration."""
    data_entry_by: SourceDataSetAdministrativeInformationDataEntryBy = Field(default=..., alias='dataEntryBy')
    publication_and_ownership: SourceDataSetAdministrativeInformationPublicationAndOwnership = Field(default=..., alias='publicationAndOwnership', description='Information related to publication and version management of the data set including copyright and access restrictions.')
    common_other: str | None = Field(default=None, alias='common:other')

class SourcesSourceDataSet(TidasBaseModel):
    xmlns_common: Literal['http://lca.jrc.it/ILCD/Common'] = Field(default=..., alias='@xmlns:common')
    xmlns: Literal['http://lca.jrc.it/ILCD/Source'] = Field(default=..., alias='@xmlns')
    xmlns_xsi: Literal['http://www.w3.org/2001/XMLSchema-instance'] = Field(default=..., alias='@xmlns:xsi')
    version: Literal['1.1'] = Field(default=..., alias='@version')
    xsi_schema_location: Literal['http://lca.jrc.it/ILCD/Source ../../schemas/ILCD_SourceDataSet.xsd'] = Field(default=..., alias='@xsi:schemaLocation')
    source_information: SourcesSourceDataSetSourceInformation = Field(default=..., alias='sourceInformation')
    administrative_information: SourcesSourceDataSetAdministrativeInformation = Field(default=..., alias='administrativeInformation', description='Information on data set management and administration.')
    common_other: str | None = Field(default=None, alias='common:other')

class Sources(TidasBaseModel):
    source_data_set: SourcesSourceDataSet = Field(default=..., alias='sourceDataSet')
