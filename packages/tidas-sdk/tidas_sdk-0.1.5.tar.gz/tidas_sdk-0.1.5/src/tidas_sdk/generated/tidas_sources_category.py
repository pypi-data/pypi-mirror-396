"""
Auto generated file. DO NOT EDIT.
Source: tidas_sources_category.json
"""
from __future__ import annotations

from typing import Literal, Union

from pydantic import Field
from tidas_sdk.core.base import TidasBaseModel

class SourceVariant0(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['0'] | None = Field(default=None, alias='@classId')
    text: Literal['Images'] | None = Field(default=None, alias='#text')

class SourceVariant1(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['1'] | None = Field(default=None, alias='@classId')
    text: Literal['Data set formats'] | None = Field(default=None, alias='#text')

class SourceVariant2(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['2'] | None = Field(default=None, alias='@classId')
    text: Literal['Databases'] | None = Field(default=None, alias='#text')

class SourceVariant3(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['3'] | None = Field(default=None, alias='@classId')
    text: Literal['Compliance systems'] | None = Field(default=None, alias='#text')

class SourceVariant4(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['4'] | None = Field(default=None, alias='@classId')
    text: Literal['Statistical classifications'] | None = Field(default=None, alias='#text')

class SourceVariant5(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['5'] | None = Field(default=None, alias='@classId')
    text: Literal['Publications and communications'] | None = Field(default=None, alias='#text')

class SourceVariant6(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['6'] | None = Field(default=None, alias='@classId')
    text: Literal['Other source types'] | None = Field(default=None, alias='#text')

class SourcesCategory(TidasBaseModel):
    pass

Source = Union[
    SourceVariant0,
    SourceVariant1,
    SourceVariant2,
    SourceVariant3,
    SourceVariant4,
    SourceVariant5,
    SourceVariant6,
]
