"""
Auto generated file. DO NOT EDIT.
Source: tidas_unitgroups_category.json
"""
from __future__ import annotations

from typing import Literal

from pydantic import Field
from tidas_sdk.core.base import TidasBaseModel

class UnitGroupVariant0(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['1'] | None = Field(default=None, alias='@classId')
    text: Literal['Technical unit groups'] | None = Field(default=None, alias='#text')

class UnitGroupVariant1(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['2'] | None = Field(default=None, alias='@classId')
    text: Literal['Chemical composition unit groups'] | None = Field(default=None, alias='#text')

class UnitGroupVariant2(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['3'] | None = Field(default=None, alias='@classId')
    text: Literal['Economic unit groups'] | None = Field(default=None, alias='#text')

class UnitGroupVariant3(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['4'] | None = Field(default=None, alias='@classId')
    text: Literal['Other unit groups'] | None = Field(default=None, alias='#text')

class UnitgroupsCategory(TidasBaseModel):
    pass

UnitGroup = UnitGroupVariant0 | UnitGroupVariant1 | UnitGroupVariant2 | UnitGroupVariant3
