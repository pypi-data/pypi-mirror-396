"""
Auto generated file. DO NOT EDIT.
Source: tidas_processes_category.json
"""
from __future__ import annotations

from typing import Literal, Union

from pydantic import Field
from tidas_sdk.core.base import TidasBaseModel

class ProcessesCategoryVariant0(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['A'] | None = Field(default=None, alias='@classId')
    text: Literal['Agriculture, forestry and fishing'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant1(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['01'] | None = Field(default=None, alias='@classId')
    text: Literal['Crop and animal production, hunting and related service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant2(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['011'] | None = Field(default=None, alias='@classId')
    text: Literal['Growing of non-perennial crops'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant3(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0111'] | None = Field(default=None, alias='@classId')
    text: Literal['Growing of cereals (except rice), leguminous crops and oil seeds'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant4(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0112'] | None = Field(default=None, alias='@classId')
    text: Literal['Growing of rice'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant5(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0113'] | None = Field(default=None, alias='@classId')
    text: Literal['Growing of vegetables and melons, roots and tubers'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant6(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0114'] | None = Field(default=None, alias='@classId')
    text: Literal['Growing of sugar cane'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant7(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0115'] | None = Field(default=None, alias='@classId')
    text: Literal['Growing of tobacco'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant8(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0116'] | None = Field(default=None, alias='@classId')
    text: Literal['Growing of fibre crops'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant9(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0119'] | None = Field(default=None, alias='@classId')
    text: Literal['Growing of other non-perennial crops'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant10(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['012'] | None = Field(default=None, alias='@classId')
    text: Literal['Growing of perennial crops'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant11(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0121'] | None = Field(default=None, alias='@classId')
    text: Literal['Growing of grapes'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant12(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0122'] | None = Field(default=None, alias='@classId')
    text: Literal['Growing of tropical and subtropical fruits'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant13(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0123'] | None = Field(default=None, alias='@classId')
    text: Literal['Growing of citrus fruits'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant14(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0124'] | None = Field(default=None, alias='@classId')
    text: Literal['Growing of pome fruits and stone fruits'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant15(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0125'] | None = Field(default=None, alias='@classId')
    text: Literal['Growing of other tree and bush fruits and nuts'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant16(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0126'] | None = Field(default=None, alias='@classId')
    text: Literal['Growing of oleaginous fruits'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant17(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0127'] | None = Field(default=None, alias='@classId')
    text: Literal['Growing of beverage crops'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant18(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0128'] | None = Field(default=None, alias='@classId')
    text: Literal['Growing of spices, aromatic, drug and pharmaceutical crops'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant19(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0129'] | None = Field(default=None, alias='@classId')
    text: Literal['Growing of other perennial crops'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant20(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['013'] | None = Field(default=None, alias='@classId')
    text: Literal['Plant propagation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant21(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0130'] | None = Field(default=None, alias='@classId')
    text: Literal['Plant propagation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant22(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['014'] | None = Field(default=None, alias='@classId')
    text: Literal['Animal production'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant23(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0141'] | None = Field(default=None, alias='@classId')
    text: Literal['Raising of cattle and buffaloes'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant24(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0142'] | None = Field(default=None, alias='@classId')
    text: Literal['Raising of horses and other equines'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant25(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0143'] | None = Field(default=None, alias='@classId')
    text: Literal['Raising of camels and camelids'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant26(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0144'] | None = Field(default=None, alias='@classId')
    text: Literal['Raising of sheep and goats'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant27(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0145'] | None = Field(default=None, alias='@classId')
    text: Literal['Raising of swine and pigs'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant28(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0146'] | None = Field(default=None, alias='@classId')
    text: Literal['Raising of poultry'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant29(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0149'] | None = Field(default=None, alias='@classId')
    text: Literal['Raising of other animals'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant30(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['015'] | None = Field(default=None, alias='@classId')
    text: Literal['Mixed farming'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant31(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0150'] | None = Field(default=None, alias='@classId')
    text: Literal['Mixed farming'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant32(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['016'] | None = Field(default=None, alias='@classId')
    text: Literal['Support activities to agriculture and post-harvest crop activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant33(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0161'] | None = Field(default=None, alias='@classId')
    text: Literal['Support activities for crop production'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant34(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0162'] | None = Field(default=None, alias='@classId')
    text: Literal['Support activities for animal production'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant35(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0163'] | None = Field(default=None, alias='@classId')
    text: Literal['Post-harvest crop activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant36(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0164'] | None = Field(default=None, alias='@classId')
    text: Literal['Seed processing for propagation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant37(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['017'] | None = Field(default=None, alias='@classId')
    text: Literal['Hunting, trapping and related service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant38(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0170'] | None = Field(default=None, alias='@classId')
    text: Literal['Hunting, trapping and related service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant39(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['02'] | None = Field(default=None, alias='@classId')
    text: Literal['Forestry and logging'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant40(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['021'] | None = Field(default=None, alias='@classId')
    text: Literal['Silviculture and other forestry activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant41(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0210'] | None = Field(default=None, alias='@classId')
    text: Literal['Silviculture and other forestry activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant42(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['022'] | None = Field(default=None, alias='@classId')
    text: Literal['Logging'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant43(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0220'] | None = Field(default=None, alias='@classId')
    text: Literal['Logging'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant44(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['023'] | None = Field(default=None, alias='@classId')
    text: Literal['Gathering of non-wood forest products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant45(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0230'] | None = Field(default=None, alias='@classId')
    text: Literal['Gathering of non-wood forest products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant46(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['024'] | None = Field(default=None, alias='@classId')
    text: Literal['Support services to forestry'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant47(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0240'] | None = Field(default=None, alias='@classId')
    text: Literal['Support services to forestry'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant48(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['03'] | None = Field(default=None, alias='@classId')
    text: Literal['Fishing and aquaculture'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant49(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['031'] | None = Field(default=None, alias='@classId')
    text: Literal['Fishing'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant50(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0311'] | None = Field(default=None, alias='@classId')
    text: Literal['Marine fishing'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant51(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0312'] | None = Field(default=None, alias='@classId')
    text: Literal['Freshwater fishing'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant52(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['032'] | None = Field(default=None, alias='@classId')
    text: Literal['Aquaculture'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant53(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0321'] | None = Field(default=None, alias='@classId')
    text: Literal['Marine aquaculture'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant54(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0322'] | None = Field(default=None, alias='@classId')
    text: Literal['Freshwater aquaculture'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant55(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['033'] | None = Field(default=None, alias='@classId')
    text: Literal['Support activities for fishing and aquaculture'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant56(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0330'] | None = Field(default=None, alias='@classId')
    text: Literal['Support activities for fishing and aquaculture'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant57(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['B'] | None = Field(default=None, alias='@classId')
    text: Literal['Mining and quarrying'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant58(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['05'] | None = Field(default=None, alias='@classId')
    text: Literal['Mining of coal and lignite'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant59(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['051'] | None = Field(default=None, alias='@classId')
    text: Literal['Mining of hard coal'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant60(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0510'] | None = Field(default=None, alias='@classId')
    text: Literal['Mining of hard coal'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant61(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['052'] | None = Field(default=None, alias='@classId')
    text: Literal['Mining of lignite'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant62(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0520'] | None = Field(default=None, alias='@classId')
    text: Literal['Mining of lignite'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant63(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['06'] | None = Field(default=None, alias='@classId')
    text: Literal['Extraction of crude petroleum and natural gas'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant64(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['061'] | None = Field(default=None, alias='@classId')
    text: Literal['Extraction of crude petroleum'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant65(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0610'] | None = Field(default=None, alias='@classId')
    text: Literal['Extraction of crude petroleum'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant66(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['062'] | None = Field(default=None, alias='@classId')
    text: Literal['Extraction of natural gas'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant67(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0620'] | None = Field(default=None, alias='@classId')
    text: Literal['Extraction of natural gas'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant68(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['07'] | None = Field(default=None, alias='@classId')
    text: Literal['Mining of metal ores'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant69(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['071'] | None = Field(default=None, alias='@classId')
    text: Literal['Mining of iron ores'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant70(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0710'] | None = Field(default=None, alias='@classId')
    text: Literal['Mining of iron ores'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant71(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['072'] | None = Field(default=None, alias='@classId')
    text: Literal['Mining of non-ferrous metal ores'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant72(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0721'] | None = Field(default=None, alias='@classId')
    text: Literal['Mining of uranium and thorium ores'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant73(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0729'] | None = Field(default=None, alias='@classId')
    text: Literal['Mining of other non-ferrous metal ores'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant74(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['08'] | None = Field(default=None, alias='@classId')
    text: Literal['Other mining and quarrying'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant75(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['081'] | None = Field(default=None, alias='@classId')
    text: Literal['Quarrying of stone, sand and clay'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant76(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0810'] | None = Field(default=None, alias='@classId')
    text: Literal['Quarrying of stone, sand and clay'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant77(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['089'] | None = Field(default=None, alias='@classId')
    text: Literal['Mining and quarrying n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant78(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0891'] | None = Field(default=None, alias='@classId')
    text: Literal['Mining of chemical and fertilizer minerals'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant79(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0892'] | None = Field(default=None, alias='@classId')
    text: Literal['Extraction of peat'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant80(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0893'] | None = Field(default=None, alias='@classId')
    text: Literal['Extraction of salt'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant81(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0899'] | None = Field(default=None, alias='@classId')
    text: Literal['Other mining and quarrying n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant82(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['09'] | None = Field(default=None, alias='@classId')
    text: Literal['Mining support service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant83(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['091'] | None = Field(default=None, alias='@classId')
    text: Literal['Support activities for petroleum and natural gas extraction'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant84(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0910'] | None = Field(default=None, alias='@classId')
    text: Literal['Support activities for petroleum and natural gas extraction'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant85(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['099'] | None = Field(default=None, alias='@classId')
    text: Literal['Support activities for other mining and quarrying'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant86(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['0990'] | None = Field(default=None, alias='@classId')
    text: Literal['Support activities for other mining and quarrying'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant87(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['C'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacturing'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant88(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['10'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of food products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant89(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['101'] | None = Field(default=None, alias='@classId')
    text: Literal['Processing and preserving of meat'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant90(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1010'] | None = Field(default=None, alias='@classId')
    text: Literal['Processing and preserving of meat'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant91(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['102'] | None = Field(default=None, alias='@classId')
    text: Literal['Processing and preserving of fish, crustaceans and molluscs'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant92(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1020'] | None = Field(default=None, alias='@classId')
    text: Literal['Processing and preserving of fish, crustaceans and molluscs'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant93(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['103'] | None = Field(default=None, alias='@classId')
    text: Literal['Processing and preserving of fruit and vegetables'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant94(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1030'] | None = Field(default=None, alias='@classId')
    text: Literal['Processing and preserving of fruit and vegetables'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant95(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['104'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of vegetable and animal oils and fats'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant96(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1040'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of vegetable and animal oils and fats'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant97(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['105'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of dairy products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant98(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1050'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of dairy products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant99(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['106'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of grain mill products, starches and starch products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant100(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1061'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of grain mill products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant101(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1062'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of starches and starch products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant102(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['107'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other food products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant103(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1071'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of bakery products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant104(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1072'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of sugar'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant105(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1073'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of cocoa, chocolate and sugar confectionery'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant106(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1074'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of macaroni, noodles, couscous and similar farinaceous products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant107(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1075'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of prepared meals and dishes'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant108(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1076'] | None = Field(default=None, alias='@classId')
    text: Literal['Processing of coffee and tea'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant109(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1079'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other food products n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant110(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['108'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of prepared animal feeds'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant111(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1080'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of prepared animal feeds'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant112(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['11'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of beverages'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant113(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['110'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of beverages'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant114(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1101'] | None = Field(default=None, alias='@classId')
    text: Literal['Distilling, rectifying and blending of spirits'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant115(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1102'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of wines'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant116(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1103'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of beer'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant117(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1104'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of malt'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant118(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1105'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of soft drinks; production of mineral waters and other bottled waters'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant119(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['12'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of tobacco products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant120(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['120'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of tobacco products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant121(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1200'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of tobacco products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant122(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['13'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of textiles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant123(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['131'] | None = Field(default=None, alias='@classId')
    text: Literal['Spinning, weaving and finishing of textiles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant124(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1311'] | None = Field(default=None, alias='@classId')
    text: Literal['Preparation and spinning of textile fibres'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant125(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1312'] | None = Field(default=None, alias='@classId')
    text: Literal['Weaving of textiles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant126(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1313'] | None = Field(default=None, alias='@classId')
    text: Literal['Finishing of textiles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant127(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['139'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other textiles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant128(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1391'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of knitted and crocheted fabrics'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant129(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1392'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of made-up textile articles, except apparel'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant130(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1393'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of carpets and rugs'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant131(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1394'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of cordage, rope, twine and netting'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant132(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1399'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other textiles n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant133(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['14'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of wearing apparel'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant134(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['141'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of wearing apparel, except fur apparel'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant135(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1410'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of wearing apparel, except fur apparel'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant136(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['142'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of articles of fur'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant137(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1420'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of articles of fur'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant138(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['143'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of knitted and crocheted apparel'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant139(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1430'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of knitted and crocheted apparel'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant140(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['15'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of leather and related products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant141(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['151'] | None = Field(default=None, alias='@classId')
    text: Literal['Tanning, dyeing, dressing of leather and fur; manufacture of luggage, handbags, saddlery and harness'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant142(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1511'] | None = Field(default=None, alias='@classId')
    text: Literal['Tanning and dressing of leather; dressing and dyeing of fur'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant143(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1512'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of luggage, handbags and the like, saddlery and harness of any material'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant144(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['152'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of footwear'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant145(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1520'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of footwear'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant146(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['16'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of wood and of products of wood and cork, except furniture; manufacture of articles of straw and plaiting materials'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant147(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['161'] | None = Field(default=None, alias='@classId')
    text: Literal['Sawmilling and planing of wood'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant148(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1610'] | None = Field(default=None, alias='@classId')
    text: Literal['Sawmilling and planing of wood'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant149(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['162'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of products of wood, cork, straw and plaiting materials'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant150(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1621'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of veneer sheets and wood-based panels'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant151(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1622'] | None = Field(default=None, alias='@classId')
    text: Literal["Manufacture of builders' carpentry and joinery"] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant152(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1623'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of wooden containers'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant153(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1629'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other products of wood; manufacture of articles of cork, straw and plaiting materials'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant154(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['17'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of paper and paper products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant155(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['170'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of paper and paper products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant156(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1701'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of pulp, paper and paperboard'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant157(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1702'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of corrugated paper and paperboard and of containers of paper and paperboard'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant158(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1709'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other articles of paper and paperboard'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant159(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['18'] | None = Field(default=None, alias='@classId')
    text: Literal['Printing and reproduction of recorded media'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant160(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['181'] | None = Field(default=None, alias='@classId')
    text: Literal['Printing and service activities related to printing'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant161(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1811'] | None = Field(default=None, alias='@classId')
    text: Literal['Printing'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant162(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1812'] | None = Field(default=None, alias='@classId')
    text: Literal['Service activities related to printing'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant163(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['182'] | None = Field(default=None, alias='@classId')
    text: Literal['Reproduction of recorded media'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant164(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1820'] | None = Field(default=None, alias='@classId')
    text: Literal['Reproduction of recorded media'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant165(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['19'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of coke and refined petroleum products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant166(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['191'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of coke oven products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant167(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1910'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of coke oven products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant168(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['192'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of refined petroleum products; manufacture of fossil fuel products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant169(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['1920'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of refined petroleum products; manufacture of fossil fuel products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant170(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['20'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of chemicals and chemical products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant171(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['201'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of basic chemicals, fertilizers and nitrogen compounds, plastics and synthetic rubber in primary forms'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant172(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2011'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of basic chemicals'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant173(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2012'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of fertilizers and nitrogen compounds'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant174(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2013'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of plastics and synthetic rubber in primary forms'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant175(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['202'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other chemical products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant176(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2021'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of pesticides and other agrochemical products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant177(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2022'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of paints, varnishes and similar coatings, printing ink and mastics'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant178(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2023'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of soap and detergents, cleaning and polishing preparations, perfumes and toilet preparations'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant179(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2029'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other chemical products n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant180(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['203'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of man-made fibres'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant181(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2030'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of man-made fibres'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant182(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['21'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of basic pharmaceutical products and pharmaceutical preparations'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant183(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['210'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of pharmaceuticals, medicinal chemical and botanical products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant184(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2100'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of pharmaceuticals, medicinal chemical and botanical products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant185(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['22'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of rubber and plastic products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant186(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['221'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of rubber products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant187(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2211'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of rubber tyres and tubes; retreading and rebuilding of rubber tyres'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant188(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2219'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other rubber products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant189(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['222'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of plastics products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant190(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2220'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of plastics products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant191(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['23'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other non-metallic mineral products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant192(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['231'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of glass and glass products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant193(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2310'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of glass and glass products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant194(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['239'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of non-metallic mineral products n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant195(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2391'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of refractory products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant196(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2392'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of clay building materials'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant197(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2393'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other porcelain and ceramic products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant198(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2394'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of cement, lime and plaster'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant199(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2395'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of articles of concrete, cement and plaster'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant200(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2396'] | None = Field(default=None, alias='@classId')
    text: Literal['Cutting, shaping and finishing of stone'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant201(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2399'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other non-metallic mineral products n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant202(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['24'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of basic metals'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant203(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['241'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of basic iron and steel'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant204(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2410'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of basic iron and steel'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant205(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['242'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of basic precious and other non-ferrous metals'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant206(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2420'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of basic precious and other non-ferrous metals'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant207(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['243'] | None = Field(default=None, alias='@classId')
    text: Literal['Casting of metals'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant208(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2431'] | None = Field(default=None, alias='@classId')
    text: Literal['Casting of iron and steel'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant209(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2432'] | None = Field(default=None, alias='@classId')
    text: Literal['Casting of non-ferrous metals'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant210(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['25'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of fabricated metal products, except machinery and equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant211(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['251'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of structural metal products, tanks, reservoirs and steam generators'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant212(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2511'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of structural metal products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant213(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2512'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of tanks, reservoirs and containers of metal'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant214(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2513'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of steam generators, except central heating hot water boilers'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant215(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['252'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of weapons and ammunition'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant216(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2520'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of weapons and ammunition'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant217(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['259'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other fabricated metal products; metalworking service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant218(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2591'] | None = Field(default=None, alias='@classId')
    text: Literal['Forging, pressing, stamping and roll-forming of metal; powder metallurgy'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant219(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2592'] | None = Field(default=None, alias='@classId')
    text: Literal['Treatment and coating of metals; machining'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant220(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2593'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of cutlery, hand tools and general hardware'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant221(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2599'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other fabricated metal products n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant222(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['26'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of computer, electronic and optical products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant223(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['261'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of electronic components and boards'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant224(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2611'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of solar cells, solar panels and photovoltaic inverters'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant225(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2619'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other electronic components and boards'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant226(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['262'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of computers and peripheral equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant227(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2620'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of computers and peripheral equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant228(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['263'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of communication equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant229(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2630'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of communication equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant230(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['264'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of consumer electronics'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant231(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2640'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of consumer electronics'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant232(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['265'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of measuring, testing, navigating and control equipment; watches and clocks'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant233(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2651'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of measuring, testing, navigating and control equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant234(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2652'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of watches and clocks'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant235(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['266'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of irradiation, electromedical and electrotherapeutic equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant236(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2660'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of irradiation, electromedical and electrotherapeutic equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant237(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['267'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of optical instruments and photographic equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant238(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2670'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of optical instruments and photographic equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant239(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['268'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of magnetic and optical media'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant240(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2680'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of magnetic and optical media'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant241(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['27'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of electrical equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant242(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['271'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of electric motors, generators, transformers and electricity distribution and control apparatus'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant243(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2710'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of electric motors, generators, transformers and electricity distribution and control apparatus'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant244(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['272'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of batteries and accumulators'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant245(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2720'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of batteries and accumulators'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant246(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['273'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of wiring and wiring devices'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant247(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2731'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of fibre optic cables'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant248(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2732'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other electronic and electric wires and cables'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant249(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2733'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of wiring devices'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant250(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['274'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of lighting equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant251(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2740'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of lighting equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant252(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['275'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of domestic appliances'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant253(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2750'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of domestic appliances'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant254(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['279'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other electrical equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant255(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2790'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other electrical equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant256(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['28'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of machinery and equipment n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant257(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['281'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of general-purpose machinery'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant258(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2811'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of engines and turbines, except aircraft, vehicle and cycle engines'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant259(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2812'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of fluid power equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant260(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2813'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other pumps, compressors, taps and valves'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant261(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2814'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of bearings, gears, gearing and driving elements'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant262(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2815'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of ovens, furnaces and permanent household heating equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant263(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2816'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of lifting and handling equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant264(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2817'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of office machinery and equipment (except computers and peripheral equipment)'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant265(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2818'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of power-driven hand tools'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant266(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2819'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other general-purpose machinery'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant267(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['282'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of special-purpose machinery'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant268(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2821'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of agricultural and forestry machinery'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant269(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2822'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of metal-forming machinery and machine tools'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant270(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2823'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of machinery for metallurgy'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant271(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2824'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of machinery for mining, quarrying and construction'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant272(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2825'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of machinery for food, beverage and tobacco processing'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant273(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2826'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of machinery for textile, apparel and leather production'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant274(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2829'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other special-purpose machinery'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant275(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['29'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of motor vehicles, trailers and semi-trailers'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant276(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['291'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of motor vehicles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant277(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2910'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of motor vehicles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant278(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['292'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of bodies (coachwork) for motor vehicles; manufacture of trailers and semi-trailers'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant279(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2920'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of bodies (coachwork) for motor vehicles; manufacture of trailers and semi-trailers'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant280(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['293'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of parts and accessories for motor vehicles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant281(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['2930'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of parts and accessories for motor vehicles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant282(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['30'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other transport equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant283(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['301'] | None = Field(default=None, alias='@classId')
    text: Literal['Building of ships and boats'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant284(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3011'] | None = Field(default=None, alias='@classId')
    text: Literal['Building of ships and floating structures'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant285(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3012'] | None = Field(default=None, alias='@classId')
    text: Literal['Building of pleasure and sporting boats'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant286(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['302'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of railway locomotives and rolling stock'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant287(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3020'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of railway locomotives and rolling stock'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant288(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['303'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of air and spacecraft and related machinery'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant289(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3030'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of air and spacecraft and related machinery'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant290(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['304'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of military fighting vehicles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant291(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3040'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of military fighting vehicles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant292(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['309'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of transport equipment n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant293(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3091'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of motorcycles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant294(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3092'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of bicycles and invalid carriages'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant295(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3099'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other transport equipment n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant296(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['31'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of furniture'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant297(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['310'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of furniture'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant298(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3101'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of wooden furniture'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant299(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3102'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of other furniture'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant300(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['32'] | None = Field(default=None, alias='@classId')
    text: Literal['Other manufacturing'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant301(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['321'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of jewellery, bijouterie and related articles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant302(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3211'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of jewellery and related articles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant303(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3212'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of imitation jewellery and related articles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant304(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['322'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of musical instruments'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant305(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3220'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of musical instruments'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant306(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['323'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of sports goods'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant307(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3230'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of sports goods'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant308(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['324'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of games and toys'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant309(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3240'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of games and toys'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant310(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['325'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of medical and dental instruments and supplies'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant311(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3250'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of medical and dental instruments and supplies'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant312(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['329'] | None = Field(default=None, alias='@classId')
    text: Literal['Other manufacturing n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant313(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3290'] | None = Field(default=None, alias='@classId')
    text: Literal['Other manufacturing n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant314(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['33'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair, maintenance and installation of machinery and equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant315(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['331'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of fabricated metal products, machinery and equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant316(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3311'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of fabricated metal products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant317(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3312'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of machinery'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant318(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3313'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of electronic and optical equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant319(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3314'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of electrical equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant320(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3315'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of transport equipment, except motor vehicles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant321(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3319'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of other equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant322(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['332'] | None = Field(default=None, alias='@classId')
    text: Literal['Installation of industrial machinery and equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant323(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3320'] | None = Field(default=None, alias='@classId')
    text: Literal['Installation of industrial machinery and equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant324(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['D'] | None = Field(default=None, alias='@classId')
    text: Literal['Electricity, gas, steam and air conditioning supply'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant325(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['35'] | None = Field(default=None, alias='@classId')
    text: Literal['Electricity, gas, steam and air conditioning supply'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant326(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['351'] | None = Field(default=None, alias='@classId')
    text: Literal['Electric power generation, transmission and distribution activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant327(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3511'] | None = Field(default=None, alias='@classId')
    text: Literal['Electric power generation activities from non-renewable sources'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant328(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3512'] | None = Field(default=None, alias='@classId')
    text: Literal['Electric power generation activities from renewable sources'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant329(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3513'] | None = Field(default=None, alias='@classId')
    text: Literal['Electric power transmission and distribution activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant330(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['352'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of gas; distribution of gaseous fuels through mains'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant331(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3520'] | None = Field(default=None, alias='@classId')
    text: Literal['Manufacture of gas; distribution of gaseous fuels through mains'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant332(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['353'] | None = Field(default=None, alias='@classId')
    text: Literal['Steam and air conditioning supply'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant333(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3530'] | None = Field(default=None, alias='@classId')
    text: Literal['Steam and air conditioning supply'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant334(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['354'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of brokers and agents for electric power and natural gas'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant335(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3540'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of brokers and agents for electric power and natural gas'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant336(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['E'] | None = Field(default=None, alias='@classId')
    text: Literal['Water supply; sewerage, waste management and remediation activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant337(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['36'] | None = Field(default=None, alias='@classId')
    text: Literal['Water collection, treatment and supply'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant338(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['360'] | None = Field(default=None, alias='@classId')
    text: Literal['Water collection, treatment and supply'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant339(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3600'] | None = Field(default=None, alias='@classId')
    text: Literal['Water collection, treatment and supply'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant340(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['37'] | None = Field(default=None, alias='@classId')
    text: Literal['Sewerage'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant341(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['370'] | None = Field(default=None, alias='@classId')
    text: Literal['Sewerage'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant342(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3700'] | None = Field(default=None, alias='@classId')
    text: Literal['Sewerage'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant343(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['38'] | None = Field(default=None, alias='@classId')
    text: Literal['Waste collection, treatment and disposal, and recovery activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant344(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['381'] | None = Field(default=None, alias='@classId')
    text: Literal['Waste collection activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant345(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3811'] | None = Field(default=None, alias='@classId')
    text: Literal['Collection of non-hazardous waste'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant346(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3812'] | None = Field(default=None, alias='@classId')
    text: Literal['Collection of hazardous waste'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant347(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['382'] | None = Field(default=None, alias='@classId')
    text: Literal['Waste treatment and disposal'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant348(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3821'] | None = Field(default=None, alias='@classId')
    text: Literal['Treatment and disposal of non-hazardous waste'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant349(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3822'] | None = Field(default=None, alias='@classId')
    text: Literal['Treatment and disposal of hazardous waste'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant350(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['383'] | None = Field(default=None, alias='@classId')
    text: Literal['Materials and other waste recovery'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant351(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3830'] | None = Field(default=None, alias='@classId')
    text: Literal['Materials and other waste recovery'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant352(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['39'] | None = Field(default=None, alias='@classId')
    text: Literal['Remediation and other waste management service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant353(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['390'] | None = Field(default=None, alias='@classId')
    text: Literal['Remediation and other waste management service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant354(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['3900'] | None = Field(default=None, alias='@classId')
    text: Literal['Remediation and other waste management service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant355(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['F'] | None = Field(default=None, alias='@classId')
    text: Literal['Construction'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant356(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['41'] | None = Field(default=None, alias='@classId')
    text: Literal['Construction of residential and non-residential buildings'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant357(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['410'] | None = Field(default=None, alias='@classId')
    text: Literal['Construction of residential and non-residential buildings'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant358(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4100'] | None = Field(default=None, alias='@classId')
    text: Literal['Construction of residential and non-residential buildings'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant359(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['42'] | None = Field(default=None, alias='@classId')
    text: Literal['Civil engineering'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant360(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['421'] | None = Field(default=None, alias='@classId')
    text: Literal['Construction of roads and railways'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant361(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4210'] | None = Field(default=None, alias='@classId')
    text: Literal['Construction of roads and railways'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant362(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['422'] | None = Field(default=None, alias='@classId')
    text: Literal['Construction of utility projects'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant363(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4220'] | None = Field(default=None, alias='@classId')
    text: Literal['Construction of utility projects'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant364(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['429'] | None = Field(default=None, alias='@classId')
    text: Literal['Construction of other civil engineering projects'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant365(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4290'] | None = Field(default=None, alias='@classId')
    text: Literal['Construction of other civil engineering projects'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant366(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['43'] | None = Field(default=None, alias='@classId')
    text: Literal['Specialized construction activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant367(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['431'] | None = Field(default=None, alias='@classId')
    text: Literal['Demolition and site preparation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant368(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4311'] | None = Field(default=None, alias='@classId')
    text: Literal['Demolition'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant369(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4312'] | None = Field(default=None, alias='@classId')
    text: Literal['Site preparation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant370(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['432'] | None = Field(default=None, alias='@classId')
    text: Literal['Electrical, plumbing and other construction installation activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant371(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4321'] | None = Field(default=None, alias='@classId')
    text: Literal['Electrical installation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant372(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4322'] | None = Field(default=None, alias='@classId')
    text: Literal['Plumbing, heat and air-conditioning installation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant373(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4329'] | None = Field(default=None, alias='@classId')
    text: Literal['Other construction installation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant374(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['433'] | None = Field(default=None, alias='@classId')
    text: Literal['Building completion and finishing'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant375(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4330'] | None = Field(default=None, alias='@classId')
    text: Literal['Building completion and finishing'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant376(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['434'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for specialized construction services'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant377(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4340'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for specialized construction services'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant378(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['439'] | None = Field(default=None, alias='@classId')
    text: Literal['Other specialized construction activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant379(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4390'] | None = Field(default=None, alias='@classId')
    text: Literal['Other specialized construction activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant380(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['G'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale and retail trade'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant381(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['46'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale trade'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant382(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['461'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale on a fee or contract basis'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant383(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4610'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale on a fee or contract basis'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant384(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['462'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of agricultural raw materials and live animals'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant385(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4620'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of agricultural raw materials and live animals'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant386(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['463'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of food, beverages and tobacco'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant387(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4630'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of food, beverages and tobacco'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant388(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['464'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of household goods'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant389(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4641'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of textiles, clothing and footwear'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant390(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4642'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of household, office and shop furniture, carpets and lighting equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant391(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4649'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of other household goods'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant392(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['465'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of machinery, equipment and supplies'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant393(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4651'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of computers, computer peripheral equipment and software'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant394(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4652'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of electronic and telecommunications equipment and parts'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant395(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4653'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of agricultural machinery, equipment and supplies'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant396(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4659'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of other machinery and equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant397(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['466'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of motor vehicles, motorcycles and related parts and accessories'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant398(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4661'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of motor vehicles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant399(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4662'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of motor vehicle parts and accessories'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant400(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4663'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of motorcycles, motorcycle parts and accessories'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant401(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['467'] | None = Field(default=None, alias='@classId')
    text: Literal['Other specialized wholesale'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant402(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4671'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of solid, liquid and gaseous fuels and related products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant403(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4672'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of metals and metal ores'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant404(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4673'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of construction materials, hardware, plumbing and heating equipment and supplies'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant405(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4679'] | None = Field(default=None, alias='@classId')
    text: Literal['Wholesale of chemicals, waste and scrap and other products n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant406(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['469'] | None = Field(default=None, alias='@classId')
    text: Literal['Non-specialized wholesale trade'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant407(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4690'] | None = Field(default=None, alias='@classId')
    text: Literal['Non-specialized wholesale trade'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant408(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['47'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail trade'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant409(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['471'] | None = Field(default=None, alias='@classId')
    text: Literal['Non-specialized retail sale'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant410(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4711'] | None = Field(default=None, alias='@classId')
    text: Literal['Non-specialized retail sale with food, beverages or tobacco predominating'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant411(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4719'] | None = Field(default=None, alias='@classId')
    text: Literal['Other non-specialized retail sale'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant412(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['472'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of food, beverages and tobacco'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant413(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4721'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of food'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant414(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4722'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of beverages'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant415(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4723'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of tobacco products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant416(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['473'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of automotive fuel'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant417(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4730'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of automotive fuel'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant418(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['474'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of information and communication equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant419(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4740'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of information and communication equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant420(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['475'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of other household equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant421(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4751'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of textiles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant422(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4752'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of hardware, building materials, paints and glass'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant423(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4753'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of carpets, rugs, wall and floor coverings'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant424(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4759'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of electrical household appliances, furniture, lighting equipment and other household articles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant425(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['476'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of cultural and recreational goods'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant426(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4761'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of books, newspapers, stationery and office supplies'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant427(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4762'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of sporting equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant428(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4763'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of games and toys'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant429(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4769'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of cultural and recreational goods n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant430(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['477'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of other goods, except motor vehicles and motorcycles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant431(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4771'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of clothing, footwear and leather articles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant432(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4772'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of pharmaceutical and medical goods, cosmetic and toilet articles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant433(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4773'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of other new goods n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant434(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4774'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of second-hand goods'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant435(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['478'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of motor vehicles, motorcycles and related parts and accessories'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant436(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4781'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of motor vehicles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant437(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4782'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of motor vehicle parts and accessories'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant438(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4783'] | None = Field(default=None, alias='@classId')
    text: Literal['Retail sale of motorcycles, motorcycles parts and accessories'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant439(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['479'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for retail sale'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant440(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4790'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for retail sale'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant441(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['H'] | None = Field(default=None, alias='@classId')
    text: Literal['Transportation and storage'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant442(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['49'] | None = Field(default=None, alias='@classId')
    text: Literal['Land transport and transport via pipelines'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant443(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['491'] | None = Field(default=None, alias='@classId')
    text: Literal['Transport via railways'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant444(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4911'] | None = Field(default=None, alias='@classId')
    text: Literal['Passenger rail transport, interurban'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant445(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4912'] | None = Field(default=None, alias='@classId')
    text: Literal['Freight rail transport'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant446(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['492'] | None = Field(default=None, alias='@classId')
    text: Literal['Other land transport'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant447(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4921'] | None = Field(default=None, alias='@classId')
    text: Literal['Urban and suburban passenger land transport'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant448(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4922'] | None = Field(default=None, alias='@classId')
    text: Literal['Other passenger land transport'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant449(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4923'] | None = Field(default=None, alias='@classId')
    text: Literal['Freight transport by road'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant450(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['493'] | None = Field(default=None, alias='@classId')
    text: Literal['Transport via pipeline'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant451(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['4930'] | None = Field(default=None, alias='@classId')
    text: Literal['Transport via pipeline'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant452(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['50'] | None = Field(default=None, alias='@classId')
    text: Literal['Water transport'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant453(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['501'] | None = Field(default=None, alias='@classId')
    text: Literal['Sea and coastal water transport'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant454(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5011'] | None = Field(default=None, alias='@classId')
    text: Literal['Sea and coastal passenger water transport'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant455(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5012'] | None = Field(default=None, alias='@classId')
    text: Literal['Sea and coastal freight water transport'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant456(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['502'] | None = Field(default=None, alias='@classId')
    text: Literal['Inland water transport'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant457(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5021'] | None = Field(default=None, alias='@classId')
    text: Literal['Inland passenger water transport'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant458(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5022'] | None = Field(default=None, alias='@classId')
    text: Literal['Inland freight water transport'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant459(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['51'] | None = Field(default=None, alias='@classId')
    text: Literal['Air transport'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant460(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['511'] | None = Field(default=None, alias='@classId')
    text: Literal['Passenger air transport'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant461(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5110'] | None = Field(default=None, alias='@classId')
    text: Literal['Passenger air transport'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant462(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['512'] | None = Field(default=None, alias='@classId')
    text: Literal['Freight air transport'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant463(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5120'] | None = Field(default=None, alias='@classId')
    text: Literal['Freight air transport'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant464(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['52'] | None = Field(default=None, alias='@classId')
    text: Literal['Warehousing and support activities for transportation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant465(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['521'] | None = Field(default=None, alias='@classId')
    text: Literal['Warehousing and storage'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant466(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5210'] | None = Field(default=None, alias='@classId')
    text: Literal['Warehousing and storage'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant467(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['522'] | None = Field(default=None, alias='@classId')
    text: Literal['Support activities for transportation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant468(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5221'] | None = Field(default=None, alias='@classId')
    text: Literal['Service activities incidental to land transportation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant469(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5222'] | None = Field(default=None, alias='@classId')
    text: Literal['Service activities incidental to water transportation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant470(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5223'] | None = Field(default=None, alias='@classId')
    text: Literal['Service activities incidental to air transportation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant471(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5224'] | None = Field(default=None, alias='@classId')
    text: Literal['Cargo handling'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant472(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5229'] | None = Field(default=None, alias='@classId')
    text: Literal['Other support activities for transportation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant473(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['523'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for transportation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant474(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5231'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for freight transportation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant475(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5232'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for passenger transportation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant476(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['53'] | None = Field(default=None, alias='@classId')
    text: Literal['Postal and courier activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant477(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['531'] | None = Field(default=None, alias='@classId')
    text: Literal['Postal activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant478(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5310'] | None = Field(default=None, alias='@classId')
    text: Literal['Postal activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant479(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['532'] | None = Field(default=None, alias='@classId')
    text: Literal['Courier activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant480(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5320'] | None = Field(default=None, alias='@classId')
    text: Literal['Courier activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant481(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['533'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for postal and courier activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant482(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5330'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for postal and courier activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant483(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['I'] | None = Field(default=None, alias='@classId')
    text: Literal['Accommodation and food service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant484(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['55'] | None = Field(default=None, alias='@classId')
    text: Literal['Accommodation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant485(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['551'] | None = Field(default=None, alias='@classId')
    text: Literal['Hotels and similar accommodation activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant486(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5510'] | None = Field(default=None, alias='@classId')
    text: Literal['Hotels and similar accommodation activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant487(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['552'] | None = Field(default=None, alias='@classId')
    text: Literal['Other short term accommodation activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant488(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5520'] | None = Field(default=None, alias='@classId')
    text: Literal['Other short term accommodation activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant489(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['553'] | None = Field(default=None, alias='@classId')
    text: Literal['Camping grounds, recreational vehicle parks and trailer parks'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant490(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5530'] | None = Field(default=None, alias='@classId')
    text: Literal['Camping grounds, recreational vehicle parks and trailer parks'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant491(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['554'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for accommodation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant492(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5540'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for accommodation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant493(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['559'] | None = Field(default=None, alias='@classId')
    text: Literal['Other accommodation n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant494(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5590'] | None = Field(default=None, alias='@classId')
    text: Literal['Other accommodation n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant495(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['56'] | None = Field(default=None, alias='@classId')
    text: Literal['Food and beverage service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant496(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['561'] | None = Field(default=None, alias='@classId')
    text: Literal['Restaurants and mobile food service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant497(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5610'] | None = Field(default=None, alias='@classId')
    text: Literal['Restaurants and mobile food service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant498(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['562'] | None = Field(default=None, alias='@classId')
    text: Literal['Event catering and other food service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant499(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5621'] | None = Field(default=None, alias='@classId')
    text: Literal['Event catering activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant500(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5629'] | None = Field(default=None, alias='@classId')
    text: Literal['Other food service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant501(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['563'] | None = Field(default=None, alias='@classId')
    text: Literal['Beverage serving activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant502(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5630'] | None = Field(default=None, alias='@classId')
    text: Literal['Beverage serving activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant503(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['564'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for food and beverage services activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant504(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5640'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for food and beverage services activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant505(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['J'] | None = Field(default=None, alias='@classId')
    text: Literal['Publishing, broadcasting, and content production and distribution activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant506(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['58'] | None = Field(default=None, alias='@classId')
    text: Literal['Publishing activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant507(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['581'] | None = Field(default=None, alias='@classId')
    text: Literal['Publishing of books, newspapers, periodicals and other publishing activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant508(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5811'] | None = Field(default=None, alias='@classId')
    text: Literal['Publishing of books'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant509(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5812'] | None = Field(default=None, alias='@classId')
    text: Literal['Publishing of newspapers'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant510(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5813'] | None = Field(default=None, alias='@classId')
    text: Literal['Publishing of journals and periodicals'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant511(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5819'] | None = Field(default=None, alias='@classId')
    text: Literal['Other publishing activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant512(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['582'] | None = Field(default=None, alias='@classId')
    text: Literal['Software publishing'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant513(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5821'] | None = Field(default=None, alias='@classId')
    text: Literal['Publishing of video games'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant514(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5829'] | None = Field(default=None, alias='@classId')
    text: Literal['Other software publishing'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant515(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['59'] | None = Field(default=None, alias='@classId')
    text: Literal['Motion picture, video and television programme production, sound recording and music publishing activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant516(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['591'] | None = Field(default=None, alias='@classId')
    text: Literal['Motion picture, video and television programme activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant517(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5911'] | None = Field(default=None, alias='@classId')
    text: Literal['Motion picture, video and television programme production activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant518(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5912'] | None = Field(default=None, alias='@classId')
    text: Literal['Motion picture, video and television programme post-production activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant519(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5913'] | None = Field(default=None, alias='@classId')
    text: Literal['Motion picture, video and television programme distribution activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant520(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5914'] | None = Field(default=None, alias='@classId')
    text: Literal['Motion picture projection activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant521(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['592'] | None = Field(default=None, alias='@classId')
    text: Literal['Sound recording and music publishing activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant522(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['5920'] | None = Field(default=None, alias='@classId')
    text: Literal['Sound recording and music publishing activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant523(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['60'] | None = Field(default=None, alias='@classId')
    text: Literal['Programming, broadcasting, news agency and other content distribution activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant524(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['601'] | None = Field(default=None, alias='@classId')
    text: Literal['Radio broadcasting and audio distribution activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant525(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6010'] | None = Field(default=None, alias='@classId')
    text: Literal['Radio broadcasting and audio distribution activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant526(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['602'] | None = Field(default=None, alias='@classId')
    text: Literal['Television programming, broadcasting and video distribution activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant527(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6020'] | None = Field(default=None, alias='@classId')
    text: Literal['Television programming, broadcasting and video distribution activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant528(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['603'] | None = Field(default=None, alias='@classId')
    text: Literal['News agency and other content distribution activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant529(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6031'] | None = Field(default=None, alias='@classId')
    text: Literal['News agency activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant530(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6039'] | None = Field(default=None, alias='@classId')
    text: Literal['Social network sites and other content distribution activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant531(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['K'] | None = Field(default=None, alias='@classId')
    text: Literal['Telecommunications, computer programming, consultancy, computing infrastructure, and other information service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant532(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['61'] | None = Field(default=None, alias='@classId')
    text: Literal['Telecommunications'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant533(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['611'] | None = Field(default=None, alias='@classId')
    text: Literal['Wired, wireless, and satellite telecommunication activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant534(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6110'] | None = Field(default=None, alias='@classId')
    text: Literal['Wired, wireless, and satellite telecommunication activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant535(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['612'] | None = Field(default=None, alias='@classId')
    text: Literal['Telecommunication reselling\xa0activities\xa0and intermediation service\xa0activities\xa0for telecommunication'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant536(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6120'] | None = Field(default=None, alias='@classId')
    text: Literal['Telecommunication reselling\xa0activities\xa0and intermediation service\xa0activities\xa0for telecommunication'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant537(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['619'] | None = Field(default=None, alias='@classId')
    text: Literal['Other telecommunication activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant538(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6190'] | None = Field(default=None, alias='@classId')
    text: Literal['Other telecommunication activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant539(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['62'] | None = Field(default=None, alias='@classId')
    text: Literal['Computer programming, consultancy and related activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant540(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['621'] | None = Field(default=None, alias='@classId')
    text: Literal['Computer programming activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant541(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6211'] | None = Field(default=None, alias='@classId')
    text: Literal['Development of video games, video game software, and video game software tools'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant542(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6219'] | None = Field(default=None, alias='@classId')
    text: Literal['Other computer programming activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant543(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['622'] | None = Field(default=None, alias='@classId')
    text: Literal['Computer consultancy and computer facilities management activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant544(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6220'] | None = Field(default=None, alias='@classId')
    text: Literal['Computer consultancy and computer facilities management activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant545(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['629'] | None = Field(default=None, alias='@classId')
    text: Literal['Other information technology and computer service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant546(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6290'] | None = Field(default=None, alias='@classId')
    text: Literal['Other information technology and computer service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant547(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['63'] | None = Field(default=None, alias='@classId')
    text: Literal['Computing infrastructure, data processing, hosting, and other information service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant548(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['631'] | None = Field(default=None, alias='@classId')
    text: Literal['Computing infrastructure, data processing, hosting and related activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant549(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6310'] | None = Field(default=None, alias='@classId')
    text: Literal['Computing infrastructure, data processing, hosting and related activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant550(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['639'] | None = Field(default=None, alias='@classId')
    text: Literal['Web search portals activities and other information service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant551(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6390'] | None = Field(default=None, alias='@classId')
    text: Literal['Web search portals activities and other information service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant552(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['L'] | None = Field(default=None, alias='@classId')
    text: Literal['Financial and insurance activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant553(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['64'] | None = Field(default=None, alias='@classId')
    text: Literal['Financial service activities, except insurance and pension funding'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant554(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['641'] | None = Field(default=None, alias='@classId')
    text: Literal['Monetary intermediation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant555(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6411'] | None = Field(default=None, alias='@classId')
    text: Literal['Central banking'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant556(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6419'] | None = Field(default=None, alias='@classId')
    text: Literal['Other monetary intermediation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant557(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['642'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of holding companies and financing conduits'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant558(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6421'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of holding companies'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant559(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6422'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of financing conduits'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant560(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['643'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of trusts, funds and similar financial entities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant561(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6431'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of money market funds'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant562(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6432'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of non-money market investments funds'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant563(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6433'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of trust, estate and agency accounts'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant564(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['649'] | None = Field(default=None, alias='@classId')
    text: Literal['Other financial service activities, except insurance and pension funding activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant565(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6491'] | None = Field(default=None, alias='@classId')
    text: Literal['Financial leasing activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant566(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6492'] | None = Field(default=None, alias='@classId')
    text: Literal['International trade financing activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant567(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6493'] | None = Field(default=None, alias='@classId')
    text: Literal['Factoring activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant568(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6494'] | None = Field(default=None, alias='@classId')
    text: Literal['Securitisation activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant569(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6495'] | None = Field(default=None, alias='@classId')
    text: Literal['Other credit granting activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant570(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6499'] | None = Field(default=None, alias='@classId')
    text: Literal['Other financial service activities n.e.c., except insurance and pension funding activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant571(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['65'] | None = Field(default=None, alias='@classId')
    text: Literal['Insurance, reinsurance and pension funding, except compulsory social security'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant572(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['651'] | None = Field(default=None, alias='@classId')
    text: Literal['Insurance'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant573(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6511'] | None = Field(default=None, alias='@classId')
    text: Literal['Life insurance'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant574(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6512'] | None = Field(default=None, alias='@classId')
    text: Literal['Non-life insurance'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant575(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['652'] | None = Field(default=None, alias='@classId')
    text: Literal['Reinsurance'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant576(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6520'] | None = Field(default=None, alias='@classId')
    text: Literal['Reinsurance'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant577(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['653'] | None = Field(default=None, alias='@classId')
    text: Literal['Pension funding'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant578(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6530'] | None = Field(default=None, alias='@classId')
    text: Literal['Pension funding'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant579(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['66'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities auxiliary to financial service and insurance activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant580(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['661'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities auxiliary to financial services, except insurance and pension funding'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant581(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6611'] | None = Field(default=None, alias='@classId')
    text: Literal['Administration of financial markets'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant582(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6612'] | None = Field(default=None, alias='@classId')
    text: Literal['Security and commodity contracts brokerage'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant583(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6619'] | None = Field(default=None, alias='@classId')
    text: Literal['Other activities auxiliary to financial service activities, except insurance and pension funding'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant584(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['662'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities auxiliary to insurance and pension funding'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant585(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6621'] | None = Field(default=None, alias='@classId')
    text: Literal['Risk and damage evaluation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant586(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6622'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of insurance agents and brokers'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant587(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6629'] | None = Field(default=None, alias='@classId')
    text: Literal['Other activities auxiliary to insurance and pension funding'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant588(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['663'] | None = Field(default=None, alias='@classId')
    text: Literal['Fund management activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant589(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6630'] | None = Field(default=None, alias='@classId')
    text: Literal['Fund management activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant590(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['M'] | None = Field(default=None, alias='@classId')
    text: Literal['Real estate activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant591(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['68'] | None = Field(default=None, alias='@classId')
    text: Literal['Real estate activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant592(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['681'] | None = Field(default=None, alias='@classId')
    text: Literal['Real estate activities with own or leased property'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant593(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6810'] | None = Field(default=None, alias='@classId')
    text: Literal['Real estate activities with own or leased property'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant594(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['682'] | None = Field(default=None, alias='@classId')
    text: Literal['Real estate activities on a fee or contract basis'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant595(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6821'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for real estate'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant596(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6829'] | None = Field(default=None, alias='@classId')
    text: Literal['Other real estate activities on a fee or contract basis'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant597(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['N'] | None = Field(default=None, alias='@classId')
    text: Literal['Professional, scientific and technical activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant598(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['69'] | None = Field(default=None, alias='@classId')
    text: Literal['Legal and accounting activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant599(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['691'] | None = Field(default=None, alias='@classId')
    text: Literal['Legal activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant600(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6910'] | None = Field(default=None, alias='@classId')
    text: Literal['Legal activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant601(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['692'] | None = Field(default=None, alias='@classId')
    text: Literal['Accounting, bookkeeping and auditing activities; tax consultancy'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant602(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['6920'] | None = Field(default=None, alias='@classId')
    text: Literal['Accounting, bookkeeping and auditing activities; tax consultancy'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant603(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['70'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of head offices; management consultancy activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant604(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['701'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of head offices'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant605(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7010'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of head offices'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant606(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['702'] | None = Field(default=None, alias='@classId')
    text: Literal['Business and other management consultancy activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant607(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7020'] | None = Field(default=None, alias='@classId')
    text: Literal['Business and other management consultancy activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant608(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['71'] | None = Field(default=None, alias='@classId')
    text: Literal['Architectural and engineering activities; technical testing and analysis'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant609(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['711'] | None = Field(default=None, alias='@classId')
    text: Literal['Architectural and engineering, and related technical consultancy activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant610(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7110'] | None = Field(default=None, alias='@classId')
    text: Literal['Architectural and engineering, and related technical consultancy activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant611(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['712'] | None = Field(default=None, alias='@classId')
    text: Literal['Technical testing and analysis'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant612(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7120'] | None = Field(default=None, alias='@classId')
    text: Literal['Technical testing and analysis'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant613(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['72'] | None = Field(default=None, alias='@classId')
    text: Literal['Scientific research and development'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant614(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['721'] | None = Field(default=None, alias='@classId')
    text: Literal['Research and experimental development on natural sciences and engineering'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant615(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7210'] | None = Field(default=None, alias='@classId')
    text: Literal['Research and experimental development on natural sciences and engineering'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant616(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['722'] | None = Field(default=None, alias='@classId')
    text: Literal['Research and experimental development on social sciences and humanities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant617(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7220'] | None = Field(default=None, alias='@classId')
    text: Literal['Research and experimental development on social sciences and humanities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant618(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['73'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of advertising, market research and public relations'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant619(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['731'] | None = Field(default=None, alias='@classId')
    text: Literal['Advertising activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant620(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7310'] | None = Field(default=None, alias='@classId')
    text: Literal['Advertising activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant621(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['732'] | None = Field(default=None, alias='@classId')
    text: Literal['Market research and public opinion polling activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant622(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7320'] | None = Field(default=None, alias='@classId')
    text: Literal['Market research and public opinion polling activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant623(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['733'] | None = Field(default=None, alias='@classId')
    text: Literal['Public relations activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant624(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7330'] | None = Field(default=None, alias='@classId')
    text: Literal['Public relations activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant625(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['74'] | None = Field(default=None, alias='@classId')
    text: Literal['Other professional, scientific and technical activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant626(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['741'] | None = Field(default=None, alias='@classId')
    text: Literal['Specialized design activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant627(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7410'] | None = Field(default=None, alias='@classId')
    text: Literal['Specialized design activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant628(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['742'] | None = Field(default=None, alias='@classId')
    text: Literal['Photographic activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant629(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7420'] | None = Field(default=None, alias='@classId')
    text: Literal['Photographic activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant630(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['743'] | None = Field(default=None, alias='@classId')
    text: Literal['Translation and interpretation activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant631(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7430'] | None = Field(default=None, alias='@classId')
    text: Literal['Translation and interpretation activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant632(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['749'] | None = Field(default=None, alias='@classId')
    text: Literal['Other professional, scientific and technical activities n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant633(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7491'] | None = Field(default=None, alias='@classId')
    text: Literal['Patent brokering and marketing service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant634(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7499'] | None = Field(default=None, alias='@classId')
    text: Literal['All other professional, scientific and technical activities n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant635(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['75'] | None = Field(default=None, alias='@classId')
    text: Literal['Veterinary activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant636(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['750'] | None = Field(default=None, alias='@classId')
    text: Literal['Veterinary activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant637(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7500'] | None = Field(default=None, alias='@classId')
    text: Literal['Veterinary activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant638(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['O'] | None = Field(default=None, alias='@classId')
    text: Literal['Administrative and support service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant639(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['77'] | None = Field(default=None, alias='@classId')
    text: Literal['Rental and leasing activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant640(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['771'] | None = Field(default=None, alias='@classId')
    text: Literal['Rental and leasing of motor vehicles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant641(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7710'] | None = Field(default=None, alias='@classId')
    text: Literal['Rental and leasing of motor vehicles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant642(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['772'] | None = Field(default=None, alias='@classId')
    text: Literal['Rental and leasing of personal and household goods'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant643(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7721'] | None = Field(default=None, alias='@classId')
    text: Literal['Rental and leasing of recreational and sports goods'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant644(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7729'] | None = Field(default=None, alias='@classId')
    text: Literal['Rental and leasing of other personal and household goods'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant645(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['773'] | None = Field(default=None, alias='@classId')
    text: Literal['Rental and leasing of other machinery, equipment and tangible goods'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant646(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7730'] | None = Field(default=None, alias='@classId')
    text: Literal['Rental and leasing of other machinery, equipment and tangible goods'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant647(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['774'] | None = Field(default=None, alias='@classId')
    text: Literal['Leasing of intellectual property and similar products, except copyrighted works'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant648(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7740'] | None = Field(default=None, alias='@classId')
    text: Literal['Leasing of intellectual property and similar products, except copyrighted works'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant649(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['775'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for rental and leasing of tangible goods and non-financial intangible assets'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant650(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7751'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for rental and leasing of cars, motorhomes and trailers'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant651(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7752'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for rental and leasing of other tangible goods and non-financial intangible assets'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant652(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['78'] | None = Field(default=None, alias='@classId')
    text: Literal['Employment activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant653(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['781'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of employment placement agencies'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant654(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7810'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of employment placement agencies'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant655(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['782'] | None = Field(default=None, alias='@classId')
    text: Literal['Temporary employment agency activities and other human resource provisions'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant656(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7820'] | None = Field(default=None, alias='@classId')
    text: Literal['Temporary employment agency activities and other human resource provisions'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant657(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['79'] | None = Field(default=None, alias='@classId')
    text: Literal['Travel agency, tour operator, and other travel related activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant658(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['791'] | None = Field(default=None, alias='@classId')
    text: Literal['Travel agency and tour operator activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant659(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7911'] | None = Field(default=None, alias='@classId')
    text: Literal['Travel agency activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant660(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7912'] | None = Field(default=None, alias='@classId')
    text: Literal['Tour operator activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant661(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['799'] | None = Field(default=None, alias='@classId')
    text: Literal['Other travel related activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant662(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['7990'] | None = Field(default=None, alias='@classId')
    text: Literal['Other travel related activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant663(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['80'] | None = Field(default=None, alias='@classId')
    text: Literal['Investigation and security activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant664(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['801'] | None = Field(default=None, alias='@classId')
    text: Literal['Investigation and security activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant665(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8011'] | None = Field(default=None, alias='@classId')
    text: Literal['Investigation and private security activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant666(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8019'] | None = Field(default=None, alias='@classId')
    text: Literal['Security activities n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant667(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['81'] | None = Field(default=None, alias='@classId')
    text: Literal['Services to buildings and landscape activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant668(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['811'] | None = Field(default=None, alias='@classId')
    text: Literal['Combined facilities support activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant669(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8110'] | None = Field(default=None, alias='@classId')
    text: Literal['Combined facilities support activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant670(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['812'] | None = Field(default=None, alias='@classId')
    text: Literal['Cleaning activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant671(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8121'] | None = Field(default=None, alias='@classId')
    text: Literal['General cleaning of buildings'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant672(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8129'] | None = Field(default=None, alias='@classId')
    text: Literal['Other cleaning activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant673(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['813'] | None = Field(default=None, alias='@classId')
    text: Literal['Landscape service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant674(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8130'] | None = Field(default=None, alias='@classId')
    text: Literal['Landscape service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant675(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['82'] | None = Field(default=None, alias='@classId')
    text: Literal['Office administrative, office support and other business support activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant676(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['821'] | None = Field(default=None, alias='@classId')
    text: Literal['Office administrative and support activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant677(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8210'] | None = Field(default=None, alias='@classId')
    text: Literal['Office administrative and support activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant678(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['822'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of call centres'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant679(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8220'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of call centres'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant680(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['823'] | None = Field(default=None, alias='@classId')
    text: Literal['Organization of conventions and trade shows'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant681(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8230'] | None = Field(default=None, alias='@classId')
    text: Literal['Organization of conventions and trade shows'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant682(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['824'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for business support activities n.e.c., except financial intermediation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant683(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8240'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for business support activities n.e.c., except financial intermediation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant684(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['829'] | None = Field(default=None, alias='@classId')
    text: Literal['Business support service activities n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant685(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8291'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of collection agencies and credit bureaus'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant686(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8292'] | None = Field(default=None, alias='@classId')
    text: Literal['Packaging activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant687(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8299'] | None = Field(default=None, alias='@classId')
    text: Literal['Other business support service activities n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant688(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['P'] | None = Field(default=None, alias='@classId')
    text: Literal['Public administration and defence; compulsory social security'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant689(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['84'] | None = Field(default=None, alias='@classId')
    text: Literal['Public administration and defence; compulsory social security'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant690(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['841'] | None = Field(default=None, alias='@classId')
    text: Literal['Administration of the State and the economic, social and environmental policies of the community'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant691(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8411'] | None = Field(default=None, alias='@classId')
    text: Literal['General public administration activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant692(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8412'] | None = Field(default=None, alias='@classId')
    text: Literal['Regulation of the activities of providing health care, education, cultural services and other social services, excluding social security and environment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant693(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8413'] | None = Field(default=None, alias='@classId')
    text: Literal['Regulation of the activities of providing environmental services'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant694(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8414'] | None = Field(default=None, alias='@classId')
    text: Literal['Regulation of and contribution to more efficient operation of businesses'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant695(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['842'] | None = Field(default=None, alias='@classId')
    text: Literal['Provision of services to the community as a whole'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant696(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8421'] | None = Field(default=None, alias='@classId')
    text: Literal['Foreign affairs'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant697(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8422'] | None = Field(default=None, alias='@classId')
    text: Literal['Defence activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant698(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8423'] | None = Field(default=None, alias='@classId')
    text: Literal['Public order and safety activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant699(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['843'] | None = Field(default=None, alias='@classId')
    text: Literal['Compulsory social security activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant700(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8430'] | None = Field(default=None, alias='@classId')
    text: Literal['Compulsory social security activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant701(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['Q'] | None = Field(default=None, alias='@classId')
    text: Literal['Education'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant702(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['85'] | None = Field(default=None, alias='@classId')
    text: Literal['Education'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant703(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['851'] | None = Field(default=None, alias='@classId')
    text: Literal['Pre-primary education'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant704(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8510'] | None = Field(default=None, alias='@classId')
    text: Literal['Pre-primary education'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant705(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['852'] | None = Field(default=None, alias='@classId')
    text: Literal['Primary education'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant706(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8520'] | None = Field(default=None, alias='@classId')
    text: Literal['Primary education'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant707(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['853'] | None = Field(default=None, alias='@classId')
    text: Literal['Secondary and post-secondary non-tertiary education'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant708(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8531'] | None = Field(default=None, alias='@classId')
    text: Literal['General secondary education'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant709(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8532'] | None = Field(default=None, alias='@classId')
    text: Literal['Vocational secondary education'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant710(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8533'] | None = Field(default=None, alias='@classId')
    text: Literal['Post-secondary non-tertiary education'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant711(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['854'] | None = Field(default=None, alias='@classId')
    text: Literal['Tertiary education'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant712(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8540'] | None = Field(default=None, alias='@classId')
    text: Literal['Tertiary education'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant713(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['855'] | None = Field(default=None, alias='@classId')
    text: Literal['Other education'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant714(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8551'] | None = Field(default=None, alias='@classId')
    text: Literal['Sports and recreation education'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant715(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8552'] | None = Field(default=None, alias='@classId')
    text: Literal['Cultural education'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant716(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8553'] | None = Field(default=None, alias='@classId')
    text: Literal['Driving school activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant717(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8559'] | None = Field(default=None, alias='@classId')
    text: Literal['Other education n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant718(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['856'] | None = Field(default=None, alias='@classId')
    text: Literal['Educational support activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant719(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8561'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for courses and tutors'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant720(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8569'] | None = Field(default=None, alias='@classId')
    text: Literal['Other educational support activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant721(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['R'] | None = Field(default=None, alias='@classId')
    text: Literal['Human health and social work activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant722(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['86'] | None = Field(default=None, alias='@classId')
    text: Literal['Human health activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant723(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['861'] | None = Field(default=None, alias='@classId')
    text: Literal['Hospital activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant724(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8610'] | None = Field(default=None, alias='@classId')
    text: Literal['Hospital activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant725(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['862'] | None = Field(default=None, alias='@classId')
    text: Literal['Medical and dental practice activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant726(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8620'] | None = Field(default=None, alias='@classId')
    text: Literal['Medical and dental practice activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant727(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['869'] | None = Field(default=None, alias='@classId')
    text: Literal['Other human health activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant728(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8691'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for medical, dental, and other human health services'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant729(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8699'] | None = Field(default=None, alias='@classId')
    text: Literal['Other human health activities n.e.c'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant730(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['87'] | None = Field(default=None, alias='@classId')
    text: Literal['Residential care activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant731(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['871'] | None = Field(default=None, alias='@classId')
    text: Literal['Residential nursing care activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant732(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8710'] | None = Field(default=None, alias='@classId')
    text: Literal['Residential nursing care activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant733(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['872'] | None = Field(default=None, alias='@classId')
    text: Literal['Residential care activities for persons living with or having a diagnosis of a mental illness or substance abuse'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant734(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8720'] | None = Field(default=None, alias='@classId')
    text: Literal['Residential care activities for persons living with or having a diagnosis of a mental illness or substance abuse'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant735(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['873'] | None = Field(default=None, alias='@classId')
    text: Literal['Residential care activities for older persons or persons with physical disabilities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant736(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8730'] | None = Field(default=None, alias='@classId')
    text: Literal['Residential care activities for older persons or persons with physical disabilities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant737(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['879'] | None = Field(default=None, alias='@classId')
    text: Literal['Other residential care activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant738(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8791'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for residential care activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant739(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8799'] | None = Field(default=None, alias='@classId')
    text: Literal['Other residential care activities n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant740(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['88'] | None = Field(default=None, alias='@classId')
    text: Literal['Social work activities without accommodation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant741(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['881'] | None = Field(default=None, alias='@classId')
    text: Literal['Social work activities without accommodation for older persons or persons with disabilities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant742(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8810'] | None = Field(default=None, alias='@classId')
    text: Literal['Social work activities without accommodation for older persons or persons with disabilities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant743(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['889'] | None = Field(default=None, alias='@classId')
    text: Literal['Other social work activities without accommodation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant744(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['8890'] | None = Field(default=None, alias='@classId')
    text: Literal['Other social work activities without accommodation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant745(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['S'] | None = Field(default=None, alias='@classId')
    text: Literal['Arts, sports and recreation'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant746(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['90'] | None = Field(default=None, alias='@classId')
    text: Literal['Arts creation and performing arts activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant747(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['901'] | None = Field(default=None, alias='@classId')
    text: Literal['Arts creation activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant748(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9011'] | None = Field(default=None, alias='@classId')
    text: Literal['Literary creation and musical composition activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant749(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9012'] | None = Field(default=None, alias='@classId')
    text: Literal['Visual arts creation activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant750(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9013'] | None = Field(default=None, alias='@classId')
    text: Literal['Other arts creation activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant751(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['902'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of performing arts'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant752(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9020'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of performing arts'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant753(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['903'] | None = Field(default=None, alias='@classId')
    text: Literal['Support activities to arts creation and performing arts'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant754(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9031'] | None = Field(default=None, alias='@classId')
    text: Literal['Operation of arts facilities and sites'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant755(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9039'] | None = Field(default=None, alias='@classId')
    text: Literal['Other support activities to arts creation and performing arts'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant756(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['91'] | None = Field(default=None, alias='@classId')
    text: Literal['Library, archives, museum and other cultural activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant757(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['911'] | None = Field(default=None, alias='@classId')
    text: Literal['Library and archive activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant758(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9111'] | None = Field(default=None, alias='@classId')
    text: Literal['Library activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant759(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9112'] | None = Field(default=None, alias='@classId')
    text: Literal['Archive activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant760(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['912'] | None = Field(default=None, alias='@classId')
    text: Literal['Museum, collection, historical site and monument activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant761(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9121'] | None = Field(default=None, alias='@classId')
    text: Literal['Museum and collection activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant762(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9122'] | None = Field(default=None, alias='@classId')
    text: Literal['Historical site and monument activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant763(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['913'] | None = Field(default=None, alias='@classId')
    text: Literal['Conservation, restoration and other support activities for cultural heritage'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant764(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9130'] | None = Field(default=None, alias='@classId')
    text: Literal['Conservation, restoration and other support activities for cultural heritage'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant765(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['914'] | None = Field(default=None, alias='@classId')
    text: Literal['Botanical and zoological garden and nature reserve activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant766(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9141'] | None = Field(default=None, alias='@classId')
    text: Literal['Botanical and zoological garden activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant767(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9142'] | None = Field(default=None, alias='@classId')
    text: Literal['Nature reserve activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant768(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['92'] | None = Field(default=None, alias='@classId')
    text: Literal['Gambling and betting activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant769(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['920'] | None = Field(default=None, alias='@classId')
    text: Literal['Gambling and betting activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant770(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9200'] | None = Field(default=None, alias='@classId')
    text: Literal['Gambling and betting activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant771(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['93'] | None = Field(default=None, alias='@classId')
    text: Literal['Sports activities and amusement and recreation activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant772(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['931'] | None = Field(default=None, alias='@classId')
    text: Literal['Sports activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant773(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9311'] | None = Field(default=None, alias='@classId')
    text: Literal['Operation of sports facilities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant774(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9312'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of sports clubs'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant775(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9319'] | None = Field(default=None, alias='@classId')
    text: Literal['Other sports activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant776(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['932'] | None = Field(default=None, alias='@classId')
    text: Literal['Amusement and recreation activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant777(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9321'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of amusement parks and theme parks'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant778(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9329'] | None = Field(default=None, alias='@classId')
    text: Literal['Other amusement and recreation activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant779(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['T'] | None = Field(default=None, alias='@classId')
    text: Literal['Other service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant780(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['94'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of membership organizations'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant781(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['941'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of business, employers and professional membership organizations'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant782(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9411'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of business and employers membership organizations'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant783(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9412'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of professional membership organizations'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant784(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['942'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of trade unions'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant785(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9420'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of trade unions'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant786(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['949'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of other membership organizations'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant787(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9491'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of religious organizations'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant788(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9492'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of political organizations'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant789(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9499'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of other membership organizations n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant790(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['95'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of computers, personal and household goods, and motor vehicles and motorcycles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant791(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['951'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of computers and communication equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant792(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9510'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of computers and communication equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant793(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['952'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of personal and household goods'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant794(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9521'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of consumer electronics'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant795(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9522'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of household appliances and home and garden equipment'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant796(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9523'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of footwear and leather goods'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant797(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9524'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of furniture and home furnishings'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant798(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9529'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of other personal and household goods'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant799(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['953'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of motor vehicles and motorcycles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant800(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9531'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of motor vehicles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant801(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9532'] | None = Field(default=None, alias='@classId')
    text: Literal['Repair and maintenance of motorcycles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant802(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['954'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for repair and maintenance of computers, personal and household goods, and motor vehicles and motorcycles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant803(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9540'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for repair and maintenance of computers, personal and household goods, and motor vehicles and motorcycles'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant804(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['96'] | None = Field(default=None, alias='@classId')
    text: Literal['Personal service activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant805(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['961'] | None = Field(default=None, alias='@classId')
    text: Literal['Washing and cleaning of textile and fur products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant806(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9610'] | None = Field(default=None, alias='@classId')
    text: Literal['Washing and cleaning of textile and fur products'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant807(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['962'] | None = Field(default=None, alias='@classId')
    text: Literal['Hairdressing, beauty treatment, day spa and similar activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant808(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9621'] | None = Field(default=None, alias='@classId')
    text: Literal['Hairdressing and barber activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant809(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9622'] | None = Field(default=None, alias='@classId')
    text: Literal['Beauty care and other beauty treatment activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant810(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9623'] | None = Field(default=None, alias='@classId')
    text: Literal['Day spa, sauna and steam bath activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant811(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['963'] | None = Field(default=None, alias='@classId')
    text: Literal['Funeral and related activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant812(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9630'] | None = Field(default=None, alias='@classId')
    text: Literal['Funeral and related activities'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant813(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['964'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for personal services'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant814(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9640'] | None = Field(default=None, alias='@classId')
    text: Literal['Intermediation service activities for personal services'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant815(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['969'] | None = Field(default=None, alias='@classId')
    text: Literal['Other personal service activities n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant816(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9690'] | None = Field(default=None, alias='@classId')
    text: Literal['Other personal service activities n.e.c.'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant817(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['U'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of households as employers; undifferentiated goods- and services-producing activities of households for own use'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant818(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['97'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of households as employers of domestic personnel'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant819(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['970'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of households as employers of domestic personnel'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant820(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9700'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of households as employers of domestic personnel'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant821(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['98'] | None = Field(default=None, alias='@classId')
    text: Literal['Undifferentiated goods- and services-producing activities of private households for own use'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant822(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['981'] | None = Field(default=None, alias='@classId')
    text: Literal['Undifferentiated goods-producing activities of private households for own use'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant823(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9810'] | None = Field(default=None, alias='@classId')
    text: Literal['Undifferentiated goods-producing activities of private households for own use'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant824(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['982'] | None = Field(default=None, alias='@classId')
    text: Literal['Undifferentiated service-producing activities of private households for own use'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant825(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9820'] | None = Field(default=None, alias='@classId')
    text: Literal['Undifferentiated service-producing activities of private households for own use'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant826(TidasBaseModel):
    level: Literal['0'] | None = Field(default=None, alias='@level')
    class_id: Literal['V'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of extraterritorial organizations and bodies'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant827(TidasBaseModel):
    level: Literal['1'] | None = Field(default=None, alias='@level')
    class_id: Literal['99'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of extraterritorial organizations and bodies'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant828(TidasBaseModel):
    level: Literal['2'] | None = Field(default=None, alias='@level')
    class_id: Literal['990'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of extraterritorial organizations and bodies'] | None = Field(default=None, alias='#text')

class ProcessesCategoryVariant829(TidasBaseModel):
    level: Literal['3'] | None = Field(default=None, alias='@level')
    class_id: Literal['9900'] | None = Field(default=None, alias='@classId')
    text: Literal['Activities of extraterritorial organizations and bodies'] | None = Field(default=None, alias='#text')

ProcessesCategory = Union[
    ProcessesCategoryVariant0,
    ProcessesCategoryVariant1,
    ProcessesCategoryVariant2,
    ProcessesCategoryVariant3,
    ProcessesCategoryVariant4,
    ProcessesCategoryVariant5,
    ProcessesCategoryVariant6,
    ProcessesCategoryVariant7,
    ProcessesCategoryVariant8,
    ProcessesCategoryVariant9,
    ProcessesCategoryVariant10,
    ProcessesCategoryVariant11,
    ProcessesCategoryVariant12,
    ProcessesCategoryVariant13,
    ProcessesCategoryVariant14,
    ProcessesCategoryVariant15,
    ProcessesCategoryVariant16,
    ProcessesCategoryVariant17,
    ProcessesCategoryVariant18,
    ProcessesCategoryVariant19,
    ProcessesCategoryVariant20,
    ProcessesCategoryVariant21,
    ProcessesCategoryVariant22,
    ProcessesCategoryVariant23,
    ProcessesCategoryVariant24,
    ProcessesCategoryVariant25,
    ProcessesCategoryVariant26,
    ProcessesCategoryVariant27,
    ProcessesCategoryVariant28,
    ProcessesCategoryVariant29,
    ProcessesCategoryVariant30,
    ProcessesCategoryVariant31,
    ProcessesCategoryVariant32,
    ProcessesCategoryVariant33,
    ProcessesCategoryVariant34,
    ProcessesCategoryVariant35,
    ProcessesCategoryVariant36,
    ProcessesCategoryVariant37,
    ProcessesCategoryVariant38,
    ProcessesCategoryVariant39,
    ProcessesCategoryVariant40,
    ProcessesCategoryVariant41,
    ProcessesCategoryVariant42,
    ProcessesCategoryVariant43,
    ProcessesCategoryVariant44,
    ProcessesCategoryVariant45,
    ProcessesCategoryVariant46,
    ProcessesCategoryVariant47,
    ProcessesCategoryVariant48,
    ProcessesCategoryVariant49,
    ProcessesCategoryVariant50,
    ProcessesCategoryVariant51,
    ProcessesCategoryVariant52,
    ProcessesCategoryVariant53,
    ProcessesCategoryVariant54,
    ProcessesCategoryVariant55,
    ProcessesCategoryVariant56,
    ProcessesCategoryVariant57,
    ProcessesCategoryVariant58,
    ProcessesCategoryVariant59,
    ProcessesCategoryVariant60,
    ProcessesCategoryVariant61,
    ProcessesCategoryVariant62,
    ProcessesCategoryVariant63,
    ProcessesCategoryVariant64,
    ProcessesCategoryVariant65,
    ProcessesCategoryVariant66,
    ProcessesCategoryVariant67,
    ProcessesCategoryVariant68,
    ProcessesCategoryVariant69,
    ProcessesCategoryVariant70,
    ProcessesCategoryVariant71,
    ProcessesCategoryVariant72,
    ProcessesCategoryVariant73,
    ProcessesCategoryVariant74,
    ProcessesCategoryVariant75,
    ProcessesCategoryVariant76,
    ProcessesCategoryVariant77,
    ProcessesCategoryVariant78,
    ProcessesCategoryVariant79,
    ProcessesCategoryVariant80,
    ProcessesCategoryVariant81,
    ProcessesCategoryVariant82,
    ProcessesCategoryVariant83,
    ProcessesCategoryVariant84,
    ProcessesCategoryVariant85,
    ProcessesCategoryVariant86,
    ProcessesCategoryVariant87,
    ProcessesCategoryVariant88,
    ProcessesCategoryVariant89,
    ProcessesCategoryVariant90,
    ProcessesCategoryVariant91,
    ProcessesCategoryVariant92,
    ProcessesCategoryVariant93,
    ProcessesCategoryVariant94,
    ProcessesCategoryVariant95,
    ProcessesCategoryVariant96,
    ProcessesCategoryVariant97,
    ProcessesCategoryVariant98,
    ProcessesCategoryVariant99,
    ProcessesCategoryVariant100,
    ProcessesCategoryVariant101,
    ProcessesCategoryVariant102,
    ProcessesCategoryVariant103,
    ProcessesCategoryVariant104,
    ProcessesCategoryVariant105,
    ProcessesCategoryVariant106,
    ProcessesCategoryVariant107,
    ProcessesCategoryVariant108,
    ProcessesCategoryVariant109,
    ProcessesCategoryVariant110,
    ProcessesCategoryVariant111,
    ProcessesCategoryVariant112,
    ProcessesCategoryVariant113,
    ProcessesCategoryVariant114,
    ProcessesCategoryVariant115,
    ProcessesCategoryVariant116,
    ProcessesCategoryVariant117,
    ProcessesCategoryVariant118,
    ProcessesCategoryVariant119,
    ProcessesCategoryVariant120,
    ProcessesCategoryVariant121,
    ProcessesCategoryVariant122,
    ProcessesCategoryVariant123,
    ProcessesCategoryVariant124,
    ProcessesCategoryVariant125,
    ProcessesCategoryVariant126,
    ProcessesCategoryVariant127,
    ProcessesCategoryVariant128,
    ProcessesCategoryVariant129,
    ProcessesCategoryVariant130,
    ProcessesCategoryVariant131,
    ProcessesCategoryVariant132,
    ProcessesCategoryVariant133,
    ProcessesCategoryVariant134,
    ProcessesCategoryVariant135,
    ProcessesCategoryVariant136,
    ProcessesCategoryVariant137,
    ProcessesCategoryVariant138,
    ProcessesCategoryVariant139,
    ProcessesCategoryVariant140,
    ProcessesCategoryVariant141,
    ProcessesCategoryVariant142,
    ProcessesCategoryVariant143,
    ProcessesCategoryVariant144,
    ProcessesCategoryVariant145,
    ProcessesCategoryVariant146,
    ProcessesCategoryVariant147,
    ProcessesCategoryVariant148,
    ProcessesCategoryVariant149,
    ProcessesCategoryVariant150,
    ProcessesCategoryVariant151,
    ProcessesCategoryVariant152,
    ProcessesCategoryVariant153,
    ProcessesCategoryVariant154,
    ProcessesCategoryVariant155,
    ProcessesCategoryVariant156,
    ProcessesCategoryVariant157,
    ProcessesCategoryVariant158,
    ProcessesCategoryVariant159,
    ProcessesCategoryVariant160,
    ProcessesCategoryVariant161,
    ProcessesCategoryVariant162,
    ProcessesCategoryVariant163,
    ProcessesCategoryVariant164,
    ProcessesCategoryVariant165,
    ProcessesCategoryVariant166,
    ProcessesCategoryVariant167,
    ProcessesCategoryVariant168,
    ProcessesCategoryVariant169,
    ProcessesCategoryVariant170,
    ProcessesCategoryVariant171,
    ProcessesCategoryVariant172,
    ProcessesCategoryVariant173,
    ProcessesCategoryVariant174,
    ProcessesCategoryVariant175,
    ProcessesCategoryVariant176,
    ProcessesCategoryVariant177,
    ProcessesCategoryVariant178,
    ProcessesCategoryVariant179,
    ProcessesCategoryVariant180,
    ProcessesCategoryVariant181,
    ProcessesCategoryVariant182,
    ProcessesCategoryVariant183,
    ProcessesCategoryVariant184,
    ProcessesCategoryVariant185,
    ProcessesCategoryVariant186,
    ProcessesCategoryVariant187,
    ProcessesCategoryVariant188,
    ProcessesCategoryVariant189,
    ProcessesCategoryVariant190,
    ProcessesCategoryVariant191,
    ProcessesCategoryVariant192,
    ProcessesCategoryVariant193,
    ProcessesCategoryVariant194,
    ProcessesCategoryVariant195,
    ProcessesCategoryVariant196,
    ProcessesCategoryVariant197,
    ProcessesCategoryVariant198,
    ProcessesCategoryVariant199,
    ProcessesCategoryVariant200,
    ProcessesCategoryVariant201,
    ProcessesCategoryVariant202,
    ProcessesCategoryVariant203,
    ProcessesCategoryVariant204,
    ProcessesCategoryVariant205,
    ProcessesCategoryVariant206,
    ProcessesCategoryVariant207,
    ProcessesCategoryVariant208,
    ProcessesCategoryVariant209,
    ProcessesCategoryVariant210,
    ProcessesCategoryVariant211,
    ProcessesCategoryVariant212,
    ProcessesCategoryVariant213,
    ProcessesCategoryVariant214,
    ProcessesCategoryVariant215,
    ProcessesCategoryVariant216,
    ProcessesCategoryVariant217,
    ProcessesCategoryVariant218,
    ProcessesCategoryVariant219,
    ProcessesCategoryVariant220,
    ProcessesCategoryVariant221,
    ProcessesCategoryVariant222,
    ProcessesCategoryVariant223,
    ProcessesCategoryVariant224,
    ProcessesCategoryVariant225,
    ProcessesCategoryVariant226,
    ProcessesCategoryVariant227,
    ProcessesCategoryVariant228,
    ProcessesCategoryVariant229,
    ProcessesCategoryVariant230,
    ProcessesCategoryVariant231,
    ProcessesCategoryVariant232,
    ProcessesCategoryVariant233,
    ProcessesCategoryVariant234,
    ProcessesCategoryVariant235,
    ProcessesCategoryVariant236,
    ProcessesCategoryVariant237,
    ProcessesCategoryVariant238,
    ProcessesCategoryVariant239,
    ProcessesCategoryVariant240,
    ProcessesCategoryVariant241,
    ProcessesCategoryVariant242,
    ProcessesCategoryVariant243,
    ProcessesCategoryVariant244,
    ProcessesCategoryVariant245,
    ProcessesCategoryVariant246,
    ProcessesCategoryVariant247,
    ProcessesCategoryVariant248,
    ProcessesCategoryVariant249,
    ProcessesCategoryVariant250,
    ProcessesCategoryVariant251,
    ProcessesCategoryVariant252,
    ProcessesCategoryVariant253,
    ProcessesCategoryVariant254,
    ProcessesCategoryVariant255,
    ProcessesCategoryVariant256,
    ProcessesCategoryVariant257,
    ProcessesCategoryVariant258,
    ProcessesCategoryVariant259,
    ProcessesCategoryVariant260,
    ProcessesCategoryVariant261,
    ProcessesCategoryVariant262,
    ProcessesCategoryVariant263,
    ProcessesCategoryVariant264,
    ProcessesCategoryVariant265,
    ProcessesCategoryVariant266,
    ProcessesCategoryVariant267,
    ProcessesCategoryVariant268,
    ProcessesCategoryVariant269,
    ProcessesCategoryVariant270,
    ProcessesCategoryVariant271,
    ProcessesCategoryVariant272,
    ProcessesCategoryVariant273,
    ProcessesCategoryVariant274,
    ProcessesCategoryVariant275,
    ProcessesCategoryVariant276,
    ProcessesCategoryVariant277,
    ProcessesCategoryVariant278,
    ProcessesCategoryVariant279,
    ProcessesCategoryVariant280,
    ProcessesCategoryVariant281,
    ProcessesCategoryVariant282,
    ProcessesCategoryVariant283,
    ProcessesCategoryVariant284,
    ProcessesCategoryVariant285,
    ProcessesCategoryVariant286,
    ProcessesCategoryVariant287,
    ProcessesCategoryVariant288,
    ProcessesCategoryVariant289,
    ProcessesCategoryVariant290,
    ProcessesCategoryVariant291,
    ProcessesCategoryVariant292,
    ProcessesCategoryVariant293,
    ProcessesCategoryVariant294,
    ProcessesCategoryVariant295,
    ProcessesCategoryVariant296,
    ProcessesCategoryVariant297,
    ProcessesCategoryVariant298,
    ProcessesCategoryVariant299,
    ProcessesCategoryVariant300,
    ProcessesCategoryVariant301,
    ProcessesCategoryVariant302,
    ProcessesCategoryVariant303,
    ProcessesCategoryVariant304,
    ProcessesCategoryVariant305,
    ProcessesCategoryVariant306,
    ProcessesCategoryVariant307,
    ProcessesCategoryVariant308,
    ProcessesCategoryVariant309,
    ProcessesCategoryVariant310,
    ProcessesCategoryVariant311,
    ProcessesCategoryVariant312,
    ProcessesCategoryVariant313,
    ProcessesCategoryVariant314,
    ProcessesCategoryVariant315,
    ProcessesCategoryVariant316,
    ProcessesCategoryVariant317,
    ProcessesCategoryVariant318,
    ProcessesCategoryVariant319,
    ProcessesCategoryVariant320,
    ProcessesCategoryVariant321,
    ProcessesCategoryVariant322,
    ProcessesCategoryVariant323,
    ProcessesCategoryVariant324,
    ProcessesCategoryVariant325,
    ProcessesCategoryVariant326,
    ProcessesCategoryVariant327,
    ProcessesCategoryVariant328,
    ProcessesCategoryVariant329,
    ProcessesCategoryVariant330,
    ProcessesCategoryVariant331,
    ProcessesCategoryVariant332,
    ProcessesCategoryVariant333,
    ProcessesCategoryVariant334,
    ProcessesCategoryVariant335,
    ProcessesCategoryVariant336,
    ProcessesCategoryVariant337,
    ProcessesCategoryVariant338,
    ProcessesCategoryVariant339,
    ProcessesCategoryVariant340,
    ProcessesCategoryVariant341,
    ProcessesCategoryVariant342,
    ProcessesCategoryVariant343,
    ProcessesCategoryVariant344,
    ProcessesCategoryVariant345,
    ProcessesCategoryVariant346,
    ProcessesCategoryVariant347,
    ProcessesCategoryVariant348,
    ProcessesCategoryVariant349,
    ProcessesCategoryVariant350,
    ProcessesCategoryVariant351,
    ProcessesCategoryVariant352,
    ProcessesCategoryVariant353,
    ProcessesCategoryVariant354,
    ProcessesCategoryVariant355,
    ProcessesCategoryVariant356,
    ProcessesCategoryVariant357,
    ProcessesCategoryVariant358,
    ProcessesCategoryVariant359,
    ProcessesCategoryVariant360,
    ProcessesCategoryVariant361,
    ProcessesCategoryVariant362,
    ProcessesCategoryVariant363,
    ProcessesCategoryVariant364,
    ProcessesCategoryVariant365,
    ProcessesCategoryVariant366,
    ProcessesCategoryVariant367,
    ProcessesCategoryVariant368,
    ProcessesCategoryVariant369,
    ProcessesCategoryVariant370,
    ProcessesCategoryVariant371,
    ProcessesCategoryVariant372,
    ProcessesCategoryVariant373,
    ProcessesCategoryVariant374,
    ProcessesCategoryVariant375,
    ProcessesCategoryVariant376,
    ProcessesCategoryVariant377,
    ProcessesCategoryVariant378,
    ProcessesCategoryVariant379,
    ProcessesCategoryVariant380,
    ProcessesCategoryVariant381,
    ProcessesCategoryVariant382,
    ProcessesCategoryVariant383,
    ProcessesCategoryVariant384,
    ProcessesCategoryVariant385,
    ProcessesCategoryVariant386,
    ProcessesCategoryVariant387,
    ProcessesCategoryVariant388,
    ProcessesCategoryVariant389,
    ProcessesCategoryVariant390,
    ProcessesCategoryVariant391,
    ProcessesCategoryVariant392,
    ProcessesCategoryVariant393,
    ProcessesCategoryVariant394,
    ProcessesCategoryVariant395,
    ProcessesCategoryVariant396,
    ProcessesCategoryVariant397,
    ProcessesCategoryVariant398,
    ProcessesCategoryVariant399,
    ProcessesCategoryVariant400,
    ProcessesCategoryVariant401,
    ProcessesCategoryVariant402,
    ProcessesCategoryVariant403,
    ProcessesCategoryVariant404,
    ProcessesCategoryVariant405,
    ProcessesCategoryVariant406,
    ProcessesCategoryVariant407,
    ProcessesCategoryVariant408,
    ProcessesCategoryVariant409,
    ProcessesCategoryVariant410,
    ProcessesCategoryVariant411,
    ProcessesCategoryVariant412,
    ProcessesCategoryVariant413,
    ProcessesCategoryVariant414,
    ProcessesCategoryVariant415,
    ProcessesCategoryVariant416,
    ProcessesCategoryVariant417,
    ProcessesCategoryVariant418,
    ProcessesCategoryVariant419,
    ProcessesCategoryVariant420,
    ProcessesCategoryVariant421,
    ProcessesCategoryVariant422,
    ProcessesCategoryVariant423,
    ProcessesCategoryVariant424,
    ProcessesCategoryVariant425,
    ProcessesCategoryVariant426,
    ProcessesCategoryVariant427,
    ProcessesCategoryVariant428,
    ProcessesCategoryVariant429,
    ProcessesCategoryVariant430,
    ProcessesCategoryVariant431,
    ProcessesCategoryVariant432,
    ProcessesCategoryVariant433,
    ProcessesCategoryVariant434,
    ProcessesCategoryVariant435,
    ProcessesCategoryVariant436,
    ProcessesCategoryVariant437,
    ProcessesCategoryVariant438,
    ProcessesCategoryVariant439,
    ProcessesCategoryVariant440,
    ProcessesCategoryVariant441,
    ProcessesCategoryVariant442,
    ProcessesCategoryVariant443,
    ProcessesCategoryVariant444,
    ProcessesCategoryVariant445,
    ProcessesCategoryVariant446,
    ProcessesCategoryVariant447,
    ProcessesCategoryVariant448,
    ProcessesCategoryVariant449,
    ProcessesCategoryVariant450,
    ProcessesCategoryVariant451,
    ProcessesCategoryVariant452,
    ProcessesCategoryVariant453,
    ProcessesCategoryVariant454,
    ProcessesCategoryVariant455,
    ProcessesCategoryVariant456,
    ProcessesCategoryVariant457,
    ProcessesCategoryVariant458,
    ProcessesCategoryVariant459,
    ProcessesCategoryVariant460,
    ProcessesCategoryVariant461,
    ProcessesCategoryVariant462,
    ProcessesCategoryVariant463,
    ProcessesCategoryVariant464,
    ProcessesCategoryVariant465,
    ProcessesCategoryVariant466,
    ProcessesCategoryVariant467,
    ProcessesCategoryVariant468,
    ProcessesCategoryVariant469,
    ProcessesCategoryVariant470,
    ProcessesCategoryVariant471,
    ProcessesCategoryVariant472,
    ProcessesCategoryVariant473,
    ProcessesCategoryVariant474,
    ProcessesCategoryVariant475,
    ProcessesCategoryVariant476,
    ProcessesCategoryVariant477,
    ProcessesCategoryVariant478,
    ProcessesCategoryVariant479,
    ProcessesCategoryVariant480,
    ProcessesCategoryVariant481,
    ProcessesCategoryVariant482,
    ProcessesCategoryVariant483,
    ProcessesCategoryVariant484,
    ProcessesCategoryVariant485,
    ProcessesCategoryVariant486,
    ProcessesCategoryVariant487,
    ProcessesCategoryVariant488,
    ProcessesCategoryVariant489,
    ProcessesCategoryVariant490,
    ProcessesCategoryVariant491,
    ProcessesCategoryVariant492,
    ProcessesCategoryVariant493,
    ProcessesCategoryVariant494,
    ProcessesCategoryVariant495,
    ProcessesCategoryVariant496,
    ProcessesCategoryVariant497,
    ProcessesCategoryVariant498,
    ProcessesCategoryVariant499,
    ProcessesCategoryVariant500,
    ProcessesCategoryVariant501,
    ProcessesCategoryVariant502,
    ProcessesCategoryVariant503,
    ProcessesCategoryVariant504,
    ProcessesCategoryVariant505,
    ProcessesCategoryVariant506,
    ProcessesCategoryVariant507,
    ProcessesCategoryVariant508,
    ProcessesCategoryVariant509,
    ProcessesCategoryVariant510,
    ProcessesCategoryVariant511,
    ProcessesCategoryVariant512,
    ProcessesCategoryVariant513,
    ProcessesCategoryVariant514,
    ProcessesCategoryVariant515,
    ProcessesCategoryVariant516,
    ProcessesCategoryVariant517,
    ProcessesCategoryVariant518,
    ProcessesCategoryVariant519,
    ProcessesCategoryVariant520,
    ProcessesCategoryVariant521,
    ProcessesCategoryVariant522,
    ProcessesCategoryVariant523,
    ProcessesCategoryVariant524,
    ProcessesCategoryVariant525,
    ProcessesCategoryVariant526,
    ProcessesCategoryVariant527,
    ProcessesCategoryVariant528,
    ProcessesCategoryVariant529,
    ProcessesCategoryVariant530,
    ProcessesCategoryVariant531,
    ProcessesCategoryVariant532,
    ProcessesCategoryVariant533,
    ProcessesCategoryVariant534,
    ProcessesCategoryVariant535,
    ProcessesCategoryVariant536,
    ProcessesCategoryVariant537,
    ProcessesCategoryVariant538,
    ProcessesCategoryVariant539,
    ProcessesCategoryVariant540,
    ProcessesCategoryVariant541,
    ProcessesCategoryVariant542,
    ProcessesCategoryVariant543,
    ProcessesCategoryVariant544,
    ProcessesCategoryVariant545,
    ProcessesCategoryVariant546,
    ProcessesCategoryVariant547,
    ProcessesCategoryVariant548,
    ProcessesCategoryVariant549,
    ProcessesCategoryVariant550,
    ProcessesCategoryVariant551,
    ProcessesCategoryVariant552,
    ProcessesCategoryVariant553,
    ProcessesCategoryVariant554,
    ProcessesCategoryVariant555,
    ProcessesCategoryVariant556,
    ProcessesCategoryVariant557,
    ProcessesCategoryVariant558,
    ProcessesCategoryVariant559,
    ProcessesCategoryVariant560,
    ProcessesCategoryVariant561,
    ProcessesCategoryVariant562,
    ProcessesCategoryVariant563,
    ProcessesCategoryVariant564,
    ProcessesCategoryVariant565,
    ProcessesCategoryVariant566,
    ProcessesCategoryVariant567,
    ProcessesCategoryVariant568,
    ProcessesCategoryVariant569,
    ProcessesCategoryVariant570,
    ProcessesCategoryVariant571,
    ProcessesCategoryVariant572,
    ProcessesCategoryVariant573,
    ProcessesCategoryVariant574,
    ProcessesCategoryVariant575,
    ProcessesCategoryVariant576,
    ProcessesCategoryVariant577,
    ProcessesCategoryVariant578,
    ProcessesCategoryVariant579,
    ProcessesCategoryVariant580,
    ProcessesCategoryVariant581,
    ProcessesCategoryVariant582,
    ProcessesCategoryVariant583,
    ProcessesCategoryVariant584,
    ProcessesCategoryVariant585,
    ProcessesCategoryVariant586,
    ProcessesCategoryVariant587,
    ProcessesCategoryVariant588,
    ProcessesCategoryVariant589,
    ProcessesCategoryVariant590,
    ProcessesCategoryVariant591,
    ProcessesCategoryVariant592,
    ProcessesCategoryVariant593,
    ProcessesCategoryVariant594,
    ProcessesCategoryVariant595,
    ProcessesCategoryVariant596,
    ProcessesCategoryVariant597,
    ProcessesCategoryVariant598,
    ProcessesCategoryVariant599,
    ProcessesCategoryVariant600,
    ProcessesCategoryVariant601,
    ProcessesCategoryVariant602,
    ProcessesCategoryVariant603,
    ProcessesCategoryVariant604,
    ProcessesCategoryVariant605,
    ProcessesCategoryVariant606,
    ProcessesCategoryVariant607,
    ProcessesCategoryVariant608,
    ProcessesCategoryVariant609,
    ProcessesCategoryVariant610,
    ProcessesCategoryVariant611,
    ProcessesCategoryVariant612,
    ProcessesCategoryVariant613,
    ProcessesCategoryVariant614,
    ProcessesCategoryVariant615,
    ProcessesCategoryVariant616,
    ProcessesCategoryVariant617,
    ProcessesCategoryVariant618,
    ProcessesCategoryVariant619,
    ProcessesCategoryVariant620,
    ProcessesCategoryVariant621,
    ProcessesCategoryVariant622,
    ProcessesCategoryVariant623,
    ProcessesCategoryVariant624,
    ProcessesCategoryVariant625,
    ProcessesCategoryVariant626,
    ProcessesCategoryVariant627,
    ProcessesCategoryVariant628,
    ProcessesCategoryVariant629,
    ProcessesCategoryVariant630,
    ProcessesCategoryVariant631,
    ProcessesCategoryVariant632,
    ProcessesCategoryVariant633,
    ProcessesCategoryVariant634,
    ProcessesCategoryVariant635,
    ProcessesCategoryVariant636,
    ProcessesCategoryVariant637,
    ProcessesCategoryVariant638,
    ProcessesCategoryVariant639,
    ProcessesCategoryVariant640,
    ProcessesCategoryVariant641,
    ProcessesCategoryVariant642,
    ProcessesCategoryVariant643,
    ProcessesCategoryVariant644,
    ProcessesCategoryVariant645,
    ProcessesCategoryVariant646,
    ProcessesCategoryVariant647,
    ProcessesCategoryVariant648,
    ProcessesCategoryVariant649,
    ProcessesCategoryVariant650,
    ProcessesCategoryVariant651,
    ProcessesCategoryVariant652,
    ProcessesCategoryVariant653,
    ProcessesCategoryVariant654,
    ProcessesCategoryVariant655,
    ProcessesCategoryVariant656,
    ProcessesCategoryVariant657,
    ProcessesCategoryVariant658,
    ProcessesCategoryVariant659,
    ProcessesCategoryVariant660,
    ProcessesCategoryVariant661,
    ProcessesCategoryVariant662,
    ProcessesCategoryVariant663,
    ProcessesCategoryVariant664,
    ProcessesCategoryVariant665,
    ProcessesCategoryVariant666,
    ProcessesCategoryVariant667,
    ProcessesCategoryVariant668,
    ProcessesCategoryVariant669,
    ProcessesCategoryVariant670,
    ProcessesCategoryVariant671,
    ProcessesCategoryVariant672,
    ProcessesCategoryVariant673,
    ProcessesCategoryVariant674,
    ProcessesCategoryVariant675,
    ProcessesCategoryVariant676,
    ProcessesCategoryVariant677,
    ProcessesCategoryVariant678,
    ProcessesCategoryVariant679,
    ProcessesCategoryVariant680,
    ProcessesCategoryVariant681,
    ProcessesCategoryVariant682,
    ProcessesCategoryVariant683,
    ProcessesCategoryVariant684,
    ProcessesCategoryVariant685,
    ProcessesCategoryVariant686,
    ProcessesCategoryVariant687,
    ProcessesCategoryVariant688,
    ProcessesCategoryVariant689,
    ProcessesCategoryVariant690,
    ProcessesCategoryVariant691,
    ProcessesCategoryVariant692,
    ProcessesCategoryVariant693,
    ProcessesCategoryVariant694,
    ProcessesCategoryVariant695,
    ProcessesCategoryVariant696,
    ProcessesCategoryVariant697,
    ProcessesCategoryVariant698,
    ProcessesCategoryVariant699,
    ProcessesCategoryVariant700,
    ProcessesCategoryVariant701,
    ProcessesCategoryVariant702,
    ProcessesCategoryVariant703,
    ProcessesCategoryVariant704,
    ProcessesCategoryVariant705,
    ProcessesCategoryVariant706,
    ProcessesCategoryVariant707,
    ProcessesCategoryVariant708,
    ProcessesCategoryVariant709,
    ProcessesCategoryVariant710,
    ProcessesCategoryVariant711,
    ProcessesCategoryVariant712,
    ProcessesCategoryVariant713,
    ProcessesCategoryVariant714,
    ProcessesCategoryVariant715,
    ProcessesCategoryVariant716,
    ProcessesCategoryVariant717,
    ProcessesCategoryVariant718,
    ProcessesCategoryVariant719,
    ProcessesCategoryVariant720,
    ProcessesCategoryVariant721,
    ProcessesCategoryVariant722,
    ProcessesCategoryVariant723,
    ProcessesCategoryVariant724,
    ProcessesCategoryVariant725,
    ProcessesCategoryVariant726,
    ProcessesCategoryVariant727,
    ProcessesCategoryVariant728,
    ProcessesCategoryVariant729,
    ProcessesCategoryVariant730,
    ProcessesCategoryVariant731,
    ProcessesCategoryVariant732,
    ProcessesCategoryVariant733,
    ProcessesCategoryVariant734,
    ProcessesCategoryVariant735,
    ProcessesCategoryVariant736,
    ProcessesCategoryVariant737,
    ProcessesCategoryVariant738,
    ProcessesCategoryVariant739,
    ProcessesCategoryVariant740,
    ProcessesCategoryVariant741,
    ProcessesCategoryVariant742,
    ProcessesCategoryVariant743,
    ProcessesCategoryVariant744,
    ProcessesCategoryVariant745,
    ProcessesCategoryVariant746,
    ProcessesCategoryVariant747,
    ProcessesCategoryVariant748,
    ProcessesCategoryVariant749,
    ProcessesCategoryVariant750,
    ProcessesCategoryVariant751,
    ProcessesCategoryVariant752,
    ProcessesCategoryVariant753,
    ProcessesCategoryVariant754,
    ProcessesCategoryVariant755,
    ProcessesCategoryVariant756,
    ProcessesCategoryVariant757,
    ProcessesCategoryVariant758,
    ProcessesCategoryVariant759,
    ProcessesCategoryVariant760,
    ProcessesCategoryVariant761,
    ProcessesCategoryVariant762,
    ProcessesCategoryVariant763,
    ProcessesCategoryVariant764,
    ProcessesCategoryVariant765,
    ProcessesCategoryVariant766,
    ProcessesCategoryVariant767,
    ProcessesCategoryVariant768,
    ProcessesCategoryVariant769,
    ProcessesCategoryVariant770,
    ProcessesCategoryVariant771,
    ProcessesCategoryVariant772,
    ProcessesCategoryVariant773,
    ProcessesCategoryVariant774,
    ProcessesCategoryVariant775,
    ProcessesCategoryVariant776,
    ProcessesCategoryVariant777,
    ProcessesCategoryVariant778,
    ProcessesCategoryVariant779,
    ProcessesCategoryVariant780,
    ProcessesCategoryVariant781,
    ProcessesCategoryVariant782,
    ProcessesCategoryVariant783,
    ProcessesCategoryVariant784,
    ProcessesCategoryVariant785,
    ProcessesCategoryVariant786,
    ProcessesCategoryVariant787,
    ProcessesCategoryVariant788,
    ProcessesCategoryVariant789,
    ProcessesCategoryVariant790,
    ProcessesCategoryVariant791,
    ProcessesCategoryVariant792,
    ProcessesCategoryVariant793,
    ProcessesCategoryVariant794,
    ProcessesCategoryVariant795,
    ProcessesCategoryVariant796,
    ProcessesCategoryVariant797,
    ProcessesCategoryVariant798,
    ProcessesCategoryVariant799,
    ProcessesCategoryVariant800,
    ProcessesCategoryVariant801,
    ProcessesCategoryVariant802,
    ProcessesCategoryVariant803,
    ProcessesCategoryVariant804,
    ProcessesCategoryVariant805,
    ProcessesCategoryVariant806,
    ProcessesCategoryVariant807,
    ProcessesCategoryVariant808,
    ProcessesCategoryVariant809,
    ProcessesCategoryVariant810,
    ProcessesCategoryVariant811,
    ProcessesCategoryVariant812,
    ProcessesCategoryVariant813,
    ProcessesCategoryVariant814,
    ProcessesCategoryVariant815,
    ProcessesCategoryVariant816,
    ProcessesCategoryVariant817,
    ProcessesCategoryVariant818,
    ProcessesCategoryVariant819,
    ProcessesCategoryVariant820,
    ProcessesCategoryVariant821,
    ProcessesCategoryVariant822,
    ProcessesCategoryVariant823,
    ProcessesCategoryVariant824,
    ProcessesCategoryVariant825,
    ProcessesCategoryVariant826,
    ProcessesCategoryVariant827,
    ProcessesCategoryVariant828,
    ProcessesCategoryVariant829,
]
