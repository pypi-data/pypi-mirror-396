"""
Auto generated file. DO NOT EDIT.
Source: tidas_lciamethods_category.json
"""
from __future__ import annotations

from typing import Literal, Union

from pydantic import Field
from tidas_sdk.core.base import TidasBaseModel

class LCIAMethodVariant0(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['1'] | None = Field(default=None, alias='@classId')
    text: Literal['Damage level LCIA methods'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant1(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.1'] | None = Field(default=None, alias='@classId')
    text: Literal['Total impact across areas of protection'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant2(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.2'] | None = Field(default=None, alias='@classId')
    text: Literal['Human health'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant3(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.2.1'] | None = Field(default=None, alias='@classId')
    text: Literal['Total human health, combined'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant4(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.2.2'] | None = Field(default=None, alias='@classId')
    text: Literal['Human health, toxicity'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant5(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.2.3'] | None = Field(default=None, alias='@classId')
    text: Literal['Human health, climate change'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant6(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.2.4'] | None = Field(default=None, alias='@classId')
    text: Literal['Human health, ionising radiation'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant7(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.2.5'] | None = Field(default=None, alias='@classId')
    text: Literal['Human health, ozone depletion'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant8(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.2.6'] | None = Field(default=None, alias='@classId')
    text: Literal['Human health, photooxidant creation'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant9(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.2.7'] | None = Field(default=None, alias='@classId')
    text: Literal['Human health, other'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant10(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.3'] | None = Field(default=None, alias='@classId')
    text: Literal['Natural environment'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant11(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.3.1'] | None = Field(default=None, alias='@classId')
    text: Literal['Total natural environment, combined'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant12(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.3.2'] | None = Field(default=None, alias='@classId')
    text: Literal['Natural environment, climate change'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant13(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.3.3'] | None = Field(default=None, alias='@classId')
    text: Literal['Natural environment, ozone depletion'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant14(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.3.4'] | None = Field(default=None, alias='@classId')
    text: Literal['Natural environment, land use'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant15(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.3.5'] | None = Field(default=None, alias='@classId')
    text: Literal['Natural environment, freshwater ecotoxicity'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant16(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.3.6'] | None = Field(default=None, alias='@classId')
    text: Literal['Natural environment, seawater ecotoxicity'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant17(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.3.7'] | None = Field(default=None, alias='@classId')
    text: Literal['Natural environment, terrestric ecotoxicity'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant18(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.3.8'] | None = Field(default=None, alias='@classId')
    text: Literal['Natural environment, acidification'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant19(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.3.9'] | None = Field(default=None, alias='@classId')
    text: Literal['Natural environment, eutrophication'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant20(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.3.10'] | None = Field(default=None, alias='@classId')
    text: Literal['Natural environment, photooxidant creation'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant21(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.3.11'] | None = Field(default=None, alias='@classId')
    text: Literal['Natural environment, ionising radiation'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant22(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.3.12'] | None = Field(default=None, alias='@classId')
    text: Literal['Natural environment, other'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant23(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.4'] | None = Field(default=None, alias='@classId')
    text: Literal['Man-made environment'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant24(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.4.1'] | None = Field(default=None, alias='@classId')
    text: Literal['Total man-made environment, combined'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant25(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.4.2'] | None = Field(default=None, alias='@classId')
    text: Literal['Man-made environment, acidification'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant26(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.4.3'] | None = Field(default=None, alias='@classId')
    text: Literal['Man-made environment, climate change'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant27(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.4.4'] | None = Field(default=None, alias='@classId')
    text: Literal['Man-made environment, eutrophication'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant28(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.4.5'] | None = Field(default=None, alias='@classId')
    text: Literal['Man-made environment, other'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant29(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.5'] | None = Field(default=None, alias='@classId')
    text: Literal['Resource availability'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant30(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.5.1'] | None = Field(default=None, alias='@classId')
    text: Literal['Total resource depletion, combined'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant31(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.5.2'] | None = Field(default=None, alias='@classId')
    text: Literal['Resource depletion, minerals and metals'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant32(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.5.3'] | None = Field(default=None, alias='@classId')
    text: Literal['Resource depletion, non-renewable energy resourcess'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant33(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.5.4'] | None = Field(default=None, alias='@classId')
    text: Literal['Resource depletion, land use'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant34(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.5.5'] | None = Field(default=None, alias='@classId')
    text: Literal['Resource depletion, renewable energy resources'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant35(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.5.6'] | None = Field(default=None, alias='@classId')
    text: Literal['Resource depletion, renewable non-energy resources'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant36(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['1.5.6'] | None = Field(default=None, alias='@classId')
    text: Literal['Resource depletion, other'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant37(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['2'] | None = Field(default=None, alias='@classId')
    text: Literal['Midpoint level LCIA methods'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant38(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['2.1'] | None = Field(default=None, alias='@classId')
    text: Literal['Combined methods'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant39(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['2.2'] | None = Field(default=None, alias='@classId')
    text: Literal['Climate change'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant40(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['2.3'] | None = Field(default=None, alias='@classId')
    text: Literal['Ozone depletion'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant41(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['2.4'] | None = Field(default=None, alias='@classId')
    text: Literal['Land use'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant42(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['2.5'] | None = Field(default=None, alias='@classId')
    text: Literal['Ecotoxicity'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant43(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['2.6'] | None = Field(default=None, alias='@classId')
    text: Literal['Acidification'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant44(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['2.7'] | None = Field(default=None, alias='@classId')
    text: Literal['Eutrophication'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant45(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['2.8'] | None = Field(default=None, alias='@classId')
    text: Literal['Photooxidant creation'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant46(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['2.9'] | None = Field(default=None, alias='@classId')
    text: Literal['Nuclear radiation'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant47(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['2.10'] | None = Field(default=None, alias='@classId')
    text: Literal['Human toxicity'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant48(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['2.11'] | None = Field(default=None, alias='@classId')
    text: Literal['Respiratory effects'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant49(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['2.12'] | None = Field(default=None, alias='@classId')
    text: Literal['Noise'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant50(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['2.13'] | None = Field(default=None, alias='@classId')
    text: Literal['Resource depletion'] | None = Field(default=None, alias='#text')

class LCIAMethodVariant51(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['2.14'] | None = Field(default=None, alias='@classId')
    text: Literal['Other midpoint categories'] | None = Field(default=None, alias='#text')

class LciamethodsCategory(TidasBaseModel):
    pass

LCIAMethod = Union[
    LCIAMethodVariant0,
    LCIAMethodVariant1,
    LCIAMethodVariant2,
    LCIAMethodVariant3,
    LCIAMethodVariant4,
    LCIAMethodVariant5,
    LCIAMethodVariant6,
    LCIAMethodVariant7,
    LCIAMethodVariant8,
    LCIAMethodVariant9,
    LCIAMethodVariant10,
    LCIAMethodVariant11,
    LCIAMethodVariant12,
    LCIAMethodVariant13,
    LCIAMethodVariant14,
    LCIAMethodVariant15,
    LCIAMethodVariant16,
    LCIAMethodVariant17,
    LCIAMethodVariant18,
    LCIAMethodVariant19,
    LCIAMethodVariant20,
    LCIAMethodVariant21,
    LCIAMethodVariant22,
    LCIAMethodVariant23,
    LCIAMethodVariant24,
    LCIAMethodVariant25,
    LCIAMethodVariant26,
    LCIAMethodVariant27,
    LCIAMethodVariant28,
    LCIAMethodVariant29,
    LCIAMethodVariant30,
    LCIAMethodVariant31,
    LCIAMethodVariant32,
    LCIAMethodVariant33,
    LCIAMethodVariant34,
    LCIAMethodVariant35,
    LCIAMethodVariant36,
    LCIAMethodVariant37,
    LCIAMethodVariant38,
    LCIAMethodVariant39,
    LCIAMethodVariant40,
    LCIAMethodVariant41,
    LCIAMethodVariant42,
    LCIAMethodVariant43,
    LCIAMethodVariant44,
    LCIAMethodVariant45,
    LCIAMethodVariant46,
    LCIAMethodVariant47,
    LCIAMethodVariant48,
    LCIAMethodVariant49,
    LCIAMethodVariant50,
    LCIAMethodVariant51,
]
