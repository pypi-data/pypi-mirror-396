"""
Auto generated file. DO NOT EDIT.
Source: tidas_flowproperties_category.json
"""
from __future__ import annotations

from typing import Literal

from pydantic import Field
from tidas_sdk.core.base import TidasBaseModel

class FlowPropertyVariant0(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['1'] | None = Field(default=None, alias='@classId')
    text: Literal['Technical flow properties'] | None = Field(default=None, alias='#text')

class FlowPropertyVariant1(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['2'] | None = Field(default=None, alias='@classId')
    text: Literal['Chemical composition of flows'] | None = Field(default=None, alias='#text')

class FlowPropertyVariant2(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['3'] | None = Field(default=None, alias='@classId')
    text: Literal['Economic flow properties'] | None = Field(default=None, alias='#text')

class FlowPropertyVariant3(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['4'] | None = Field(default=None, alias='@classId')
    text: Literal['Other flow properties'] | None = Field(default=None, alias='#text')

class FlowpropertiesCategory(TidasBaseModel):
    pass

FlowProperty = FlowPropertyVariant0 | FlowPropertyVariant1 | FlowPropertyVariant2 | FlowPropertyVariant3
