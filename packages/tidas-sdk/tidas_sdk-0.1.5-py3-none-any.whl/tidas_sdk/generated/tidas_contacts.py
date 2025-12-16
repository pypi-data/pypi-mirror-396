"""
Auto generated file. DO NOT EDIT.
Source: tidas_contacts.json
"""
from __future__ import annotations

from typing import Literal

from pydantic import Field
from tidas_sdk.core.base import TidasBaseModel
from tidas_sdk.core.multilang import MultiLangList

from .tidas_data_types import DateTime
from .tidas_data_types import GlobalReferenceType
from .tidas_data_types import LevelType
from .tidas_data_types import ST
from .tidas_data_types import String
from .tidas_data_types import UUID
from datetime import datetime

class CommonClassItemOption0(TidasBaseModel):
    level: LevelType = Field(default=..., alias='@level')
    class_id: str = Field(default=..., alias='@classId')
    text: str = Field(default=..., alias='#text')

class CommonClassItemOption1(TidasBaseModel):
    level: LevelType = Field(default=..., alias='@level')
    class_id: str = Field(default=..., alias='@classId')
    text: str = Field(default=..., alias='#text')

class CommonClassificationCommonClassOption1(TidasBaseModel):
    level: LevelType = Field(default=..., alias='@level')
    class_id: str = Field(default=..., alias='@classId')
    text: str = Field(default=..., alias='#text')

class DataSetInformationClassificationInformationCommonClassification(TidasBaseModel):
    """Optional statistical or other classification of the data set. Typically also used for structuring LCA databases."""
    common_class: CommonClassificationCommonClassOption1 | list[CommonClassItemOption0 | CommonClassItemOption1] = Field(default=..., alias='common:class')

class ContactInformationDataSetInformationClassificationInformation(TidasBaseModel):
    """Hierachical classification of the contact foreseen to be used to structure the contact content of the database. (Note: This entry is NOT required for the identification of the contact data set. It should nevertheless be avoided to use identical names for contacts in the same class."""
    common_classification: DataSetInformationClassificationInformationCommonClassification = Field(default=..., alias='common:classification', description='Optional statistical or other classification of the data set. Typically also used for structuring LCA databases.')
    common_other: str | None = Field(default=None, alias='common:other')

class ContactDataSetContactInformationDataSetInformation(TidasBaseModel):
    common_uuid: UUID = Field(default=..., alias='common:UUID', description="Automatically generated Universally Unique Identifier of this data set. Together with the 'Data set version', the UUID uniquely identifies each data set.")
    common_short_name: MultiLangList = Field(default_factory=MultiLangList, alias='common:shortName', description="Short name for the contact, that is used for display e.g. of links to this data set (especially in case the full name of the contact is rather long, e.g. 'FAO' for 'Food and Agriculture Organization').")
    common_name: MultiLangList = Field(default_factory=MultiLangList, alias='common:name', description='Name of the person, working group, organisation, or database network, which is represented by this contact data set.')
    classification_information: ContactInformationDataSetInformationClassificationInformation = Field(default=..., alias='classificationInformation', description='Hierachical classification of the contact foreseen to be used to structure the contact content of the database. (Note: This entry is NOT required for the identification of the contact data set. It should nevertheless be avoided to use identical names for contacts in the same class.')
    contact_address: MultiLangList = Field(default_factory=MultiLangList, alias='contactAddress', description="Mail address of the contact; specific for the person, working group, or department. [Note: A general contact point to the organisation is to be given in 'General contact point'.]")
    email: String | None = Field(default=None, alias='email')
    telephone: String | None = Field(default=None, alias='telephone')
    telefax: String | None = Field(default=None, alias='telefax')
    www_address: ST | None = Field(default=None, alias='WWWAddress', description='Web-address of the person, working group, organisation or database network.')
    central_contact_point: MultiLangList = Field(default_factory=MultiLangList, alias='centralContactPoint', description='Alternative address / contact details for the contact. Provides contact information in case e.g. the person or group represented by this contact has left the organisation or changed office/telephone. This alternative contact point can hence contain also a central telephone number, e-mail, www-address etc. of the organisation.')
    contact_description_or_comment: MultiLangList = Field(default_factory=MultiLangList, alias='contactDescriptionOrComment', description='Free text for additional description of the organisation or person of the contact, such as organisational profile, person responsibilities, etc.')
    reference_to_contact: GlobalReferenceType | None = Field(default=None, alias='referenceToContact', description='"Contact data set"s of working groups, organisations or database networks to which EITHER this person or entity OR this database, data set format, or compliance system belongs. [Note: This does not necessarily imply a legally binding relationship, but may also be a voluntary membership.]')
    reference_to_logo: GlobalReferenceType | None = Field(default=None, alias='referenceToLogo', description='"Source data set" of the logo of the organisation or source to be used in reports etc.')
    common_other: str | None = Field(default=None, alias='common:other')

class ContactsContactDataSetContactInformation(TidasBaseModel):
    data_set_information: ContactDataSetContactInformationDataSetInformation = Field(default=..., alias='dataSetInformation')
    common_other: str | None = Field(default=None, alias='common:other')

class ContactDataSetAdministrativeInformationDataEntryBy(TidasBaseModel):
    common_time_stamp: DateTime = Field(default=..., alias='common:timeStamp', description="Date and time stamp of data set generation, typically an automated entry ('last saved').")
    common_reference_to_data_set_format: GlobalReferenceType = Field(default=..., alias='common:referenceToDataSetFormat', description='"Source data set" of the used version of the ILCD format. If additional data format fields have been integrated into the data set file, using the "namespace" option, the used format namespace(s) are to be given. This is the case if the data sets carries additional information as specified by other, particular LCA formats, e.g. of other database networks or LCA softwares.')
    common_other: str | None = Field(default=None, alias='common:other')

class ContactDataSetAdministrativeInformationPublicationAndOwnership(TidasBaseModel):
    common_data_set_version: str = Field(default=..., alias='common:dataSetVersion', description="Version number of data set. First two digits refer to major updates, the second two digits to minor revisions and error corrections etc. The third three digits are intended for automatic and internal counting of versions during data set development. Together with the data set's UUID, the 'Data set version' uniquely identifies each data set.")
    common_reference_to_preceding_data_set_version: GlobalReferenceType | None = Field(default=None, alias='common:referenceToPrecedingDataSetVersion', description='Last preceding data set, which was replaced by this version. Either a URI of that data set (i.e. an internet address) or its UUID plus version number is given (or both).')
    common_permanent_data_set_uri: str | None = Field(default=None, alias='common:permanentDataSetURI', description="URI (i.e. an internet address) of the original of this data set. [Note: This equally globally unique identifier supports users and software tools to identify and retrieve the original version of a data set via the internet or to check for available updates. The URI must not represent an existing WWW address, but it should be unique and point to the data access point, e.g. by combining the data owner's www path with the data set's UUID, e.g. http://www.mycompany.com/lca/processes/50f12420-8855-12db-b606-0900210c9a66.]")
    common_reference_to_ownership_of_data_set: GlobalReferenceType = Field(default=..., alias='common:referenceToOwnershipOfDataSet', description='"Contact data set" of the person or entity who owns this data set. (Note: this is not necessarily the publisher of the data set.)')
    common_other: str | None = Field(default=None, alias='common:other')

class ContactsContactDataSetAdministrativeInformation(TidasBaseModel):
    data_entry_by: ContactDataSetAdministrativeInformationDataEntryBy = Field(default=..., alias='dataEntryBy')
    publication_and_ownership: ContactDataSetAdministrativeInformationPublicationAndOwnership = Field(default=..., alias='publicationAndOwnership')
    common_other: str | None = Field(default=None, alias='common:other')

class ContactsContactDataSet(TidasBaseModel):
    xmlns: Literal['http://lca.jrc.it/ILCD/Contact'] = Field(default=..., alias='@xmlns')
    xmlns_common: Literal['http://lca.jrc.it/ILCD/Common'] = Field(default=..., alias='@xmlns:common')
    xmlns_xsi: Literal['http://www.w3.org/2001/XMLSchema-instance'] = Field(default=..., alias='@xmlns:xsi')
    version: Literal['1.1'] = Field(default=..., alias='@version', description='Indicates, which version of the ILCD format is used')
    xsi_schema_location: Literal['http://lca.jrc.it/ILCD/Contact ../../schemas/ILCD_ContactDataSet.xsd'] = Field(default=..., alias='@xsi:schemaLocation')
    contact_information: ContactsContactDataSetContactInformation = Field(default=..., alias='contactInformation')
    administrative_information: ContactsContactDataSetAdministrativeInformation = Field(default=..., alias='administrativeInformation')
    common_other: str | None = Field(default=None, alias='common:other')

class Contacts(TidasBaseModel):
    contact_data_set: ContactsContactDataSet = Field(default=..., alias='contactDataSet')
    common_other: str | None = Field(default=None, alias='common:other')
