"""
Auto generated file. DO NOT EDIT.
Source: tidas_contacts_category.json
"""
from __future__ import annotations

from typing import Literal, Union

from pydantic import Field
from tidas_sdk.core.base import TidasBaseModel

class ContactVariant0(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['1'] | None = Field(default=None, alias='@classId')
    text: Literal['Group of organisations, project'] | None = Field(default=None, alias='#text')

class ContactVariant1(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['2'] | None = Field(default=None, alias='@classId')
    text: Literal['Organisations'] | None = Field(default=None, alias='#text')

class ContactVariant2(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['2.1'] | None = Field(default=None, alias='@classId')
    text: Literal['Private companies'] | None = Field(default=None, alias='#text')

class ContactVariant3(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['2.2'] | None = Field(default=None, alias='@classId')
    text: Literal['Governmental organisations'] | None = Field(default=None, alias='#text')

class ContactVariant4(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['2.3'] | None = Field(default=None, alias='@classId')
    text: Literal['Non-governmental organisations'] | None = Field(default=None, alias='#text')

class ContactVariant5(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['2.4'] | None = Field(default=None, alias='@classId')
    text: Literal['Other organisations'] | None = Field(default=None, alias='#text')

class ContactVariant6(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['3'] | None = Field(default=None, alias='@classId')
    text: Literal['Working groups within organisation'] | None = Field(default=None, alias='#text')

class ContactVariant7(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['4'] | None = Field(default=None, alias='@classId')
    text: Literal['Persons'] | None = Field(default=None, alias='#text')

class ContactVariant8(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['5'] | None = Field(default=None, alias='@classId')
    text: Literal['Other'] | None = Field(default=None, alias='#text')

class ContactsCategory(TidasBaseModel):
    pass

Contact = Union[
    ContactVariant0,
    ContactVariant1,
    ContactVariant2,
    ContactVariant3,
    ContactVariant4,
    ContactVariant5,
    ContactVariant6,
    ContactVariant7,
    ContactVariant8,
]
