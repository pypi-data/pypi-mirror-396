"""
Auto generated file. DO NOT EDIT.
Source: tidas_processes.json
"""
from __future__ import annotations

from typing import Literal

from pydantic import Field
from tidas_sdk.core.base import TidasBaseModel
from tidas_sdk.core.multilang import MultiLangList

from .tidas_data_types import DateTime
from .tidas_data_types import GIS
from .tidas_data_types import GlobalReferenceType
from .tidas_data_types import Int6
from .tidas_data_types import LevelType
from .tidas_data_types import MatR
from .tidas_data_types import MatV
from .tidas_data_types import Perc
from .tidas_data_types import Real
from .tidas_data_types import String
from .tidas_data_types import UUID
from .tidas_data_types import Year
from .tidas_locations_category import LocationsCategory
from datetime import datetime

class ProcessInformationDataSetInformationName(TidasBaseModel):
    """General descriptive and specifying name of the process."""
    base_name: MultiLangList = Field(default_factory=MultiLangList, alias='baseName')
    treatment_standards_routes: MultiLangList = Field(default_factory=MultiLangList, alias='treatmentStandardsRoutes')
    mix_and_location_types: MultiLangList = Field(default_factory=MultiLangList, alias='mixAndLocationTypes')
    functional_unit_flow_properties: MultiLangList = Field(default_factory=MultiLangList, alias='functionalUnitFlowProperties')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessInformationDataSetInformationComplementingProcesses(TidasBaseModel):
    reference_to_complementing_process: GlobalReferenceType | None = Field(default=None, alias='referenceToComplementingProcess')

class CommonClassItemOption0(TidasBaseModel):
    level: LevelType = Field(default=..., alias='@level')
    class_id: str = Field(default=..., alias='@classId')
    text: str = Field(default=..., alias='#text')

class CommonClassItemOption1(TidasBaseModel):
    level: LevelType = Field(default=..., alias='@level')
    class_id: str = Field(default=..., alias='@classId')
    text: str = Field(default=..., alias='#text')

class CommonClassItemOption2(TidasBaseModel):
    level: LevelType = Field(default=..., alias='@level')
    class_id: str = Field(default=..., alias='@classId')
    text: str = Field(default=..., alias='#text')

class CommonClassItemOption3(TidasBaseModel):
    level: LevelType = Field(default=..., alias='@level')
    class_id: str = Field(default=..., alias='@classId')
    text: str = Field(default=..., alias='#text')

class DataSetInformationClassificationInformationCommonClassification(TidasBaseModel):
    """Optional statistical or other classification of the data set. Typically also used for structuring LCA databases."""
    common_class: list[CommonClassItemOption0 | CommonClassItemOption1 | CommonClassItemOption2 | CommonClassItemOption3] = Field(default_factory=list, alias='common:class')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessInformationDataSetInformationClassificationInformation(TidasBaseModel):
    """Hierarchical or flat classification of the good, service or function that is provided by this life cycle model; typically used to structure database contents in LCA software, among other purposes. (Note: This entry is NOT required for the identification of a Life cycle model, but it should nevertheless be avoided to use identical names for Life cycle model data sets in the same class. The ILCD classifications are defined in the ILCDClassifications.xml file, for common use.)"""
    common_classification: DataSetInformationClassificationInformationCommonClassification = Field(default=..., alias='common:classification', description='Optional statistical or other classification of the data set. Typically also used for structuring LCA databases.')

class ProcessDataSetProcessInformationDataSetInformation(TidasBaseModel):
    """General data set information. Section covers all single fields in the ISO/TS 14048 \"Process description\", which are not part of the other sub-sections. In ISO/TS 14048 no own sub-section is foreseen for these entries."""
    common_uuid: UUID = Field(default=..., alias='common:UUID', description='Automatically generated Universally Unique Identifier of this data set. Together with the "Data set version", the UUID uniquely identifies each data set.')
    name: ProcessInformationDataSetInformationName = Field(default=..., alias='name', description='General descriptive and specifying name of the process.')
    identifier_of_sub_data_set: String | None = Field(default=None, alias='identifierOfSubDataSet', description='Identifier of a sub-set of a complete process data set. This can be the life cycle stage that a data set covers (such as used in EPDs for modular LCI reporting, with the inventory split up into "resource extraction stage", "production stage", "use stage" and "end-of-life stage"). Or it can be e.g. the type of emission source from which the elementary flows of the Inputs and Outputs stems (e.g. "incineration-related", "transport-related", etc.). Together with the field "Complementing processes" this allows to split up a process data set into a number of clearly identified data sets, each carrying only a part of the inventory and that together represent the complete inventory. Care has to be taken when naming the reference flow, to avoid misinterpretation.')
    common_synonyms: MultiLangList = Field(default_factory=MultiLangList, alias='common:synonyms', description='Synonyms / alternative names / brands of the good, service, or process. Separated by semicolon.')
    complementing_processes: ProcessInformationDataSetInformationComplementingProcesses | None = Field(default=None, alias='complementingProcesses')
    classification_information: ProcessInformationDataSetInformationClassificationInformation = Field(default=..., alias='classificationInformation', description='Hierarchical or flat classification of the good, service or function that is provided by this life cycle model; typically used to structure database contents in LCA software, among other purposes. (Note: This entry is NOT required for the identification of a Life cycle model, but it should nevertheless be avoided to use identical names for Life cycle model data sets in the same class. The ILCD classifications are defined in the ILCDClassifications.xml file, for common use.)')
    common_general_comment: MultiLangList = Field(default_factory=MultiLangList, alias='common:generalComment', description='Free text for general information about the Flow data set. It may contain information about e.g. the use of the substance, good, service or process in a specific technology or industry-context, information sources used, data selection principles etc.')
    reference_to_external_documentation: GlobalReferenceType | None = Field(default=None, alias='referenceToExternalDocumentation', description='"Source data set(s)" of detailed LCA study on the process or product represented by this data set, as well as documents / files with overarching documentative information on technology, geographical and / or time aspects etc. (e.g. basic engineering studies, process simulation results, patents, plant documentation, model behind the parameterisation of the "Mathematical model" section, etc.) (Note: can indirectly reference to digital file.)')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessDataSetProcessInformationQuantitativeReference(TidasBaseModel):
    """This section names the quantitative reference used for this data set, i.e. the reference to which the inputs and outputs quantiatively relate."""
    type: Literal['Reference flow(s)', 'Functional unit', 'Other parameter', 'Production period'] = Field(default=..., alias='@type')
    reference_to_reference_flow: Int6 = Field(default=..., alias='referenceToReferenceFlow')
    functional_unit_or_other: MultiLangList = Field(default_factory=MultiLangList, alias='functionalUnitOrOther')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessDataSetProcessInformationTime(TidasBaseModel):
    common_reference_year: Year = Field(default=..., alias='common:referenceYear', description='Reference year when the emission is assumed to take place, i.e. the start year of the time period for which the impact is modelled. For time-independent models "time independent" should be stated.')
    common_data_set_valid_until: Year | None = Field(default=None, alias='common:dataSetValidUntil', description='End year of the time period for which the data set is still valid / sufficiently representative. This date also determines when a data set revision / remodelling is required or recommended due to expected relevant changes in environmentally or technically relevant inventory values, including in the background system.')
    common_time_representativeness_description: MultiLangList = Field(default_factory=MultiLangList, alias='common:timeRepresentativenessDescription', description='Description of the valid time span of the data set including information on limited usability within sub-time spans, if any.')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessInformationGeographyLocationOfOperationSupplyOrProduction(TidasBaseModel):
    """Location, country or region the data set represents. [Note 1: This field does not refer to e.g. the country in which a specific site is located that is represented by this data set but to the actually represented country, region, or site. Note 2: Entry can be of type \"two-letter ISO 3166 country code\" for countries, \"seven-letter regional codes\" for regions or continents, or \"market areas and market organisations\", as predefined for the ILCD. Also a name for e.g. a specific plant etc. can be given here (e.g. \"FR, Lyon, XY Company, Z Site\"; user defined). Note 3: The fact whether the entry refers to production or to consumption / supply has to be stated in the name-field \"Mix and location types\" e.g. as \"Production mix\".]"""
    location: LocationsCategory = Field(default=..., alias='@location')
    latitude_and_longitude: GIS | None = Field(default=None, alias='@latitudeAndLongitude', description='Geographical latitude and longitude reference of "Location" / "Sub-location". For area-type locations (e.g. countries, continents) the field is empty.')
    description_of_restrictions: MultiLangList = Field(default_factory=MultiLangList, alias='descriptionOfRestrictions', description='Further explanations about additional aspects of the location: e.g. a company and/or site description and address, whether for certain sub-areas within the "Location" the data set is not valid, whether data is only valid for certain regions within the location indicated, or whether certain elementary flows or intermediate product flows are extrapolated from another geographical area.')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessInformationGeographySubLocationOfOperationSupplyOrProduction(TidasBaseModel):
    """One or more geographical sub-unit(s) of the stated \"Location\". Such sub-units can be e.g. the sampling sites of a company-average data set, the countries of a region-average data set, or specific sites in a country-average data set. [Note: For single site data sets this field is empty and the site is named in the \"Location\" field.]"""
    sub_location: LocationsCategory | None = Field(default=None, alias='@subLocation')
    latitude_and_longitude: GIS | None = Field(default=None, alias='@latitudeAndLongitude', description='Geographical latitude and longitude reference of "Location" / "Sub-location". For area-type locations (e.g. countries, continents) the field is empty.')
    description_of_restrictions: MultiLangList = Field(default_factory=MultiLangList, alias='descriptionOfRestrictions', description='Further explanations about additional aspects of the location: e.g. a company and/or site description and address, whether for certain sub-areas within the "Location" the data set is not valid, whether data is only valid for certain regions within the location indicated, or whether certain elementary flows or intermediate product flows are extrapolated from another geographical area.')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessDataSetProcessInformationGeography(TidasBaseModel):
    location_of_operation_supply_or_production: ProcessInformationGeographyLocationOfOperationSupplyOrProduction = Field(default=..., alias='locationOfOperationSupplyOrProduction', description='Location, country or region the data set represents. [Note 1: This field does not refer to e.g. the country in which a specific site is located that is represented by this data set but to the actually represented country, region, or site. Note 2: Entry can be of type "two-letter ISO 3166 country code" for countries, "seven-letter regional codes" for regions or continents, or "market areas and market organisations", as predefined for the ILCD. Also a name for e.g. a specific plant etc. can be given here (e.g. "FR, Lyon, XY Company, Z Site"; user defined). Note 3: The fact whether the entry refers to production or to consumption / supply has to be stated in the name-field "Mix and location types" e.g. as "Production mix".]')
    sub_location_of_operation_supply_or_production: ProcessInformationGeographySubLocationOfOperationSupplyOrProduction | None = Field(default=None, alias='subLocationOfOperationSupplyOrProduction', description='One or more geographical sub-unit(s) of the stated "Location". Such sub-units can be e.g. the sampling sites of a company-average data set, the countries of a region-average data set, or specific sites in a country-average data set. [Note: For single site data sets this field is empty and the site is named in the "Location" field.]')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessDataSetProcessInformationTechnology(TidasBaseModel):
    technology_description_and_included_processes: MultiLangList = Field(default_factory=MultiLangList, alias='technologyDescriptionAndIncludedProcesses', description='Description of the technological characteristics including operating conditions of the process or product system. For the latter this includes the relevant upstream and downstream processes included in the data set. Professional terminology should be used.')
    reference_to_included_processes: GlobalReferenceType | None = Field(default=None, alias='referenceToIncludedProcesses', description='"Process data set(s)" included in this data set, if any and available as separate data set(s).')
    technological_applicability: MultiLangList = Field(default_factory=MultiLangList, alias='technologicalApplicability', description='Description of the intended / possible applications of the good, service, or process. E.g. for which type of products the material, represented by this data set, is used. Examples: "This high purity chemical is used for analytical laboratories only." or "This technical quality bulk chemical is used for large scale synthesis in chemical industry.". Or: "This truck is used only for long-distance transport of liquid bulk chemicals".')
    reference_to_technology_pictogramme: GlobalReferenceType | None = Field(default=None, alias='referenceToTechnologyPictogramme', description='"Source data set" of the pictogramme of the good, service, technogy, plant etc. represented by this data set. For use in graphical user interfaces of LCA software.')
    reference_to_technology_flow_diagramm_or_picture: GlobalReferenceType | None = Field(default=None, alias='referenceToTechnologyFlowDiagrammOrPicture', description='"Source data set" of the flow diagramm(s) and/or photo(s) of the good, service, technology, plant etc represented by this data set. For clearer illustration and documentation of data set.')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessInformationMathematicalRelationsVariableParameter(TidasBaseModel):
    name: MatV | None = Field(default=None, alias='@name', description='Name of the variable parameter in the mathematical model.')
    formula: MatR | None = Field(default=None, alias='formula', description='Formula of the variable parameter in the mathematical model.')
    mean_value: Real | None = Field(default=None, alias='meanValue', description='Comment on the variable parameter in the mathematical model.')
    minimum_value: Real | None = Field(default=None, alias='minimumValue', description='Comment on the variable parameter in the mathematical model.')
    maximum_value: Real | None = Field(default=None, alias='maximumValue', description='Comment on the variable parameter in the mathematical model.')
    uncertainty_distribution_type: Literal['undefined', 'log-normal', 'normal', 'triangular', 'uniform'] | None = Field(default=None, alias='uncertaintyDistributionType', description='Defines the kind of uncertainty distribution that is valid for this particular object or parameter.')
    relative_standard_deviation95_in: Perc | None = Field(default=None, alias='relativeStandardDeviation95In')
    comment: MultiLangList = Field(default_factory=MultiLangList, alias='comment')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessDataSetProcessInformationMathematicalRelations(TidasBaseModel):
    model_description: MultiLangList = Field(default_factory=MultiLangList, alias='modelDescription', description='Description of the model(s) represented in this section of mathematical relations. Can cover information on restrictions, model strenghts and weaknesses, etc. (Note: Also see information provided on the level of the individual formula in field "Comment" and in the general process description in the fields in section "Technology".)')
    variable_parameter: ProcessInformationMathematicalRelationsVariableParameter | None = Field(default=None, alias='variableParameter')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessesProcessDataSetProcessInformation(TidasBaseModel):
    """Corresponds to the ISO/TS 14048 section \"Process description\". It comprises the following six sub-sections: 1) \"Data set information\" for data set identification and overarching information items, 2) \"Quantitative reference\", 3) \"Time\", 4) \"Geography\", 5) \"Technology\" and 6) \"Mathematical relations\"."""
    data_set_information: ProcessDataSetProcessInformationDataSetInformation = Field(default=..., alias='dataSetInformation', description='General data set information. Section covers all single fields in the ISO/TS 14048 "Process description", which are not part of the other sub-sections. In ISO/TS 14048 no own sub-section is foreseen for these entries.')
    quantitative_reference: ProcessDataSetProcessInformationQuantitativeReference = Field(default=..., alias='quantitativeReference', description='This section names the quantitative reference used for this data set, i.e. the reference to which the inputs and outputs quantiatively relate.')
    time: ProcessDataSetProcessInformationTime = Field(default=..., alias='time')
    geography: ProcessDataSetProcessInformationGeography = Field(default=..., alias='geography')
    technology: ProcessDataSetProcessInformationTechnology | None = Field(default=None, alias='technology')
    mathematical_relations: ProcessDataSetProcessInformationMathematicalRelations | None = Field(default=None, alias='mathematicalRelations')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessDataSetModellingAndValidationLCIMethodAndAllocation(TidasBaseModel):
    type_of_data_set: Literal['Unit process, single operation', 'Unit process, black box', 'LCI result', 'Partly terminated system', 'Avoided product system'] = Field(default=..., alias='typeOfDataSet', description='Type of the data set regarding systematic inclusion/exclusion of upstream or downstream processes, transparency and internal (hidden) multi-functionality, and the completeness of modelling.')
    lci_method_principle: Literal['Attributional', 'Consequential', 'Consequential with attributional components', 'Not applicable', 'Other'] | None = Field(default=None, alias='LCIMethodPrinciple', description='LCI method principle followed in the product system modelling, i.e. regarding using average data (= attributional = non-marginal) or modelling effects in a change-oriented way (= consequential = marginal).')
    deviations_from_lci_method_principle: MultiLangList = Field(default_factory=MultiLangList, alias='deviationsFromLCIMethodPrinciple', description='Short description of any deviations from the general "LCI method principles" and additional explanations. Refers especially to specific processes/cases where the stated "attributional" or "consequential" approach was not applied. Or where deviations were made from any specific rules for applying the "Consequential with attributional components" approach. A reference to the "Intended application" of the data collection can be made here, too. Allocated co-products may be reported here as well. In case of no (quantitatively relevant) deviations from the LCI method principle, "none" should be stated.')
    lci_method_approaches: Literal['Allocation - market value', 'Allocation - gross calorific value', 'Allocation - net calorific value', 'Allocation - exergetic content', 'Allocation - element content', 'Allocation - mass', 'Allocation - volume', 'Allocation - ability to bear', 'Allocation - marginal causality', 'Allocation - physical causality', 'Allocation - 100% to main function', 'Allocation - other explicit assignment', 'Allocation - equal distribution', 'Substitution - BAT', 'Substitution - average, market price correction', 'Substitution - average, technical properties correction', 'Allocation - recycled content', 'Substitution - recycling potential', 'Substitution - average, no correction', 'Substitution - specific', 'Consequential effects - other', 'Not applicable', 'Other'] | None = Field(default=None, alias='LCIMethodApproaches', description='Names briefly the specific approach(es) used in LCI modeling, e.g. allocation, substitution etc. In case of LCI results and Partly terminated system data sets this also covers those applied in the included background system.')
    deviations_from_lci_method_approaches: MultiLangList = Field(default_factory=MultiLangList, alias='deviationsFromLCIMethodApproaches', description='Description of relevant deviations from the applied approaches as well as of the relevant specific approaches that were applied, including in an possibly included background system. Further explanations and details of the allocation, substitution and other consequential approaches applied for relevant processes, e.g. how the marginal substitute was identified, year and region of which market prices were used in market allocation, i.e. method, procedure, data/information details. In case of no (result relevant) deviations from the before stated LCI method approaches, and in case of no need for further explanations, "none" is entered.')
    modelling_constants: MultiLangList = Field(default_factory=MultiLangList, alias='modellingConstants', description='Short identification and description of constants applied in LCI modelling other than allocation / substitution, e.g. systematic setting of recycling quota, use of gross or net calorific value, etc.')
    deviations_from_modelling_constants: MultiLangList = Field(default_factory=MultiLangList, alias='deviationsFromModellingConstants', description='Short description of data set specific deviations from the "Modelling constants" if any, including in the possibly included background system.')
    reference_to_lca_method_details: GlobalReferenceType | None = Field(default=None, alias='referenceToLCAMethodDetails', description='"Source data set"(s) where the generally used LCA methods including the LCI method principles and specific approaches, the modelling constants details, as well as any other applied methodological conventions are described.')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessDataSetModellingAndValidationDataSourcesTreatmentAndRepresentativeness(TidasBaseModel):
    data_cut_off_and_completeness_principles: MultiLangList = Field(default_factory=MultiLangList, alias='dataCutOffAndCompletenessPrinciples', description='Principles applied in data collection regarding completeness of (also intermediate) product and waste flows and of elementary flows. Examples are: cut-off rules, systematic exclusion of infrastructure, services or auxiliaries, etc. systematic exclusion of air in incineration processes, coling water, etc.')
    deviations_from_cut_off_and_completeness_principles: MultiLangList = Field(default_factory=MultiLangList, alias='deviationsFromCutOffAndCompletenessPrinciples', description='Short description of any deviations from the "Data completeness principles". In case of no (result relevant) deviations, "none" is entered.')
    data_selection_and_combination_principles: MultiLangList = Field(default_factory=MultiLangList, alias='dataSelectionAndCombinationPrinciples', description='Principles applied in data selection and in combination of data from different sources. Includes brief discussion of consistency of data sources regarding data itself, modelling, appropriateness. In case of averaging: Principles and data selection applied in horizontal and / or vertical averaging.')
    deviations_from_selection_and_combination_principles: MultiLangList = Field(default_factory=MultiLangList, alias='deviationsFromSelectionAndCombinationPrinciples', description='Short description of any deviations from the "Data selection and combination principles". In case of no (result relevant) deviations, "none" is entered.')
    data_treatment_and_extrapolations_principles: MultiLangList = Field(default_factory=MultiLangList, alias='dataTreatmentAndExtrapolationsPrinciples', description='Principles applied regarding methods, sources, and assumptions done in data adjustment including extrapolations of data from another time period, another geographical area, or another technology.')
    deviations_from_treatment_and_extrapolation_principles: MultiLangList = Field(default_factory=MultiLangList, alias='deviationsFromTreatmentAndExtrapolationPrinciples', description='Short description of any deviations from the " Data treatment and extrapolations principles". In case of no (result relevant) deviations, "none" is entered. (Note: If data representative for one "Location" is used for another "Location", its original representativity can be indicated here; see field "Percentage supply or production covered".)')
    reference_to_data_handling_principles: GlobalReferenceType | None = Field(default=None, alias='referenceToDataHandlingPrinciples', description='"Source data set"(s) of the source(s) in which the data completeness, selection, combination, treatment, and extrapolations principles\' details are described')
    reference_to_data_source: GlobalReferenceType = Field(default=..., alias='referenceToDataSource', description='"Source data set"(s) of the source(s) used for deriving/compiling the inventory of this data set e.g. questionnaires, monographies, plant operation protocols, etc. For LCI results and Partly terminated systems the sources for relevant background system data are to be given, too. For parameterised data sets the sources used for the parameterisation / mathematical relations in the section "Mathematical model" are referenced here as well. [Note: If the data set stems from another database or data set publication and is only re-published: identify the origin of a converted data set in "Converted original data set from:" field in section "Data entry by" and its unchanged re-publication in "Unchanged re-publication of:" in the section "Publication and ownership". The data sources used to model a converted or re-published data set are nevertheless to be given here in this field, for transparency reasons.]')
    percentage_supply_or_production_covered: Perc | None = Field(default=None, alias='percentageSupplyOrProductionCovered', description='Percentage of the overall supply, consumption, or production of the specific good, service, or technology represented by this data set, in the region/market of the stated "Location". For multi-functional processes the market share of the specific technology is stated. If data that is representative for a process operated in one "Location" is used for another "Location", the entry is \'0\'. The representativity for the original "Location" is documented in the field "Deviation from data treatment and extrapolation principles, explanations".')
    annual_supply_or_production_volume: MultiLangList = Field(default_factory=MultiLangList, alias='annualSupplyOrProductionVolume', description='Supply / consumption or production volume of the specific good, service, or technology in the region/market of the stated "Location". The market volume is given in absolute numbers per year, in common units, for the stated "Reference year". For multi-fucntional processes the data should be given for all co-functions (good and services).')
    sampling_procedure: MultiLangList = Field(default_factory=MultiLangList, alias='samplingProcedure', description='Sampling procedure used for quantifying the amounts of Inputs and Outputs. Possible problems in combining different sampling procedures should be mentioned.')
    data_collection_period: MultiLangList = Field(default_factory=MultiLangList, alias='dataCollectionPeriod', description='Date(s) or time period(s) when the data was collected. Note that this does NOT refer to e.g. the publication dates of papers or books from which the data may stem, but to the original data collection period.')
    uncertainty_adjustments: MultiLangList = Field(default_factory=MultiLangList, alias='uncertaintyAdjustments', description='Description of methods, sources, and assumptions made in uncertainty adjustment. [Note: For data sets where the additional uncertainty due to lacking representativeness has been included in the quantified uncertainty values, this field also reports the original representativeness, the additional uncertainty, and the procedure by which the overall uncertainty was assessed or calculated.]')
    use_advice_for_data_set: MultiLangList = Field(default_factory=MultiLangList, alias='useAdviceForDataSet', description='Specific methodological advice for data set users that requires attention. E.g. on inclusion/exclusion of recycling e.g. in material data sets, specific use phase behavior to be modelled, and other methodological advices. See also field "Technological applicability".')
    common_other: str | None = Field(default=None, alias='common:other')

class ModellingAndValidationCompletenessCompletenessElementaryFlows(TidasBaseModel):
    """Completeness of the elementary flows in the Inputs and Outputs section of this data set from impact perspective, regarding addressing the individual mid-point problem field / impact category given. The completeness refers to the state-of-the-art of scientific knowledge whether or not an individual elementary flow contributes to the respective mid-point topic in a relevant way, which is e.g. the basis for the ILCD reference elementary flows. [Note: The \"Completeness\" statement does not automatically mean that related LCIA methods exist or reference the elementary flows of this data set. Hence for direct applicability of existing LCIA methods, check the field \"Supported LCIA method data sets\".]"""
    type: Literal['Climate change', 'Ozone depletion', 'Summer smog', 'Eutrophication', 'Acidification', 'Human toxicity', 'Freshwater ecotoxicity', 'Seawater eco-toxicity', 'Terrestric eco-toxicity', 'Radioactivity', 'Land use', 'Non-renewable material resource depletion', 'Renewable material resource consumption', 'Non-renewable primary energy depletion', 'Renewable primary energy consumption', 'Particulate matter/respiratory inorganics', 'Species depletion', 'Noise'] | None = Field(default=None, alias='@type')
    value: Literal['All relevant flows quantified', 'Relevant flows missing', 'Topic not relevant', 'No statement'] | None = Field(default=None, alias='@value')

class ProcessDataSetModellingAndValidationCompleteness(TidasBaseModel):
    completeness_product_model: Literal['All relevant flows quantified', 'Relevant flows missing', 'Topic not relevant', 'No statement'] | None = Field(default=None, alias='completenessProductModel', description='Completeness of coverage of relevant product, waste and elementary flows. [Notes: For LCI results and Partly terminated systems this means throughout the underlying product system model. "Relevant" refers to the overall environmental relevance, i.e. for unit processes including the upstream and downstream burdens of product and waste flows.]')
    reference_to_supported_impact_assessment_methods: GlobalReferenceType | None = Field(default=None, alias='referenceToSupportedImpactAssessmentMethods', description='"LCIA methods data sets" that can be applied to the elementary flows in the Inputs and Outputs section, i.e. ALL these flows are referenced by the respective LCIA method data set (if they are of environmental relevance and a characterisation factor is defined for the respective flow). [Note: Applicability is not given if the inventoty contains some elementary flows with the same meaning as referenced in the LCIA method data set but in a different nomenclature (and hence carry no characterisation factor), or if the flows are sum indicators or flow groups that are addressed differently in the LCIA method data set.]')
    completeness_elementary_flows: ModellingAndValidationCompletenessCompletenessElementaryFlows | None = Field(default=None, alias='completenessElementaryFlows', description='Completeness of the elementary flows in the Inputs and Outputs section of this data set from impact perspective, regarding addressing the individual mid-point problem field / impact category given. The completeness refers to the state-of-the-art of scientific knowledge whether or not an individual elementary flow contributes to the respective mid-point topic in a relevant way, which is e.g. the basis for the ILCD reference elementary flows. [Note: The "Completeness" statement does not automatically mean that related LCIA methods exist or reference the elementary flows of this data set. Hence for direct applicability of existing LCIA methods, check the field "Supported LCIA method data sets".]')
    completeness_other_problem_field: MultiLangList = Field(default_factory=MultiLangList, alias='completenessOtherProblemField', description='Completeness of coverage of elementary flows that contribute to other problem fields that are named here as free text, preferably using the same terminology as for the specified environmental problems.')
    common_other: str | None = Field(default=None, alias='common:other')

class Option0CommonMethodOption0(TidasBaseModel):
    name: Literal['Validation of data sources', 'Sample tests on calculations', 'Energy balance', 'Element balance', 'Cross-check with other source', 'Cross-check with other data set', 'Expert judgement', 'Mass balance', 'Compliance with legal limits', 'Compliance with ISO 14040 to 14044', 'Documentation', 'Evidence collection by means of plant visits and/or interviews'] = Field(default=..., alias='@name')

class Option0CommonMethodItem(TidasBaseModel):
    name: Literal['Validation of data sources', 'Sample tests on calculations', 'Energy balance', 'Element balance', 'Cross-check with other source', 'Cross-check with other data set', 'Expert judgement', 'Mass balance', 'Compliance with legal limits', 'Compliance with ISO 14040 to 14044', 'Documentation', 'Evidence collection by means of plant visits and/or interviews'] = Field(default=..., alias='@name')

class ReviewCommonScopeOption0(TidasBaseModel):
    name: Literal['Raw data', 'Unit process(es), single operation', 'Unit process(es), black box', 'LCI results or Partly terminated system', 'LCIA results', 'Documentation', 'Life cycle inventory methods', 'LCIA results calculation', 'Goal and scope definition'] = Field(default=..., alias='@name')
    common_method: Option0CommonMethodOption0 | list[Option0CommonMethodItem] = Field(default=..., alias='common:method', description='Validation method(s) used in the respective "Scope of review".')

class ItemCommonMethodOption0(TidasBaseModel):
    name: Literal['Validation of data sources', 'Sample tests on calculations', 'Energy balance', 'Element balance', 'Cross-check with other source', 'Cross-check with other data set', 'Expert judgement', 'Mass balance', 'Compliance with legal limits', 'Compliance with ISO 14040 to 14044', 'Documentation', 'Evidence collection by means of plant visits and/or interviews'] = Field(default=..., alias='@name')

class ItemCommonMethodItem(TidasBaseModel):
    name: Literal['Validation of data sources', 'Sample tests on calculations', 'Energy balance', 'Element balance', 'Cross-check with other source', 'Cross-check with other data set', 'Expert judgement', 'Mass balance', 'Compliance with legal limits', 'Compliance with ISO 14040 to 14044', 'Documentation', 'Evidence collection by means of plant visits and/or interviews'] = Field(default=..., alias='@name')

class ReviewCommonScopeItem(TidasBaseModel):
    name: Literal['Raw data', 'Unit process(es), single operation', 'Unit process(es), black box', 'LCI results or Partly terminated system', 'LCIA results', 'Documentation', 'Life cycle inventory methods', 'LCIA results calculation', 'Goal and scope definition'] = Field(default=..., alias='@name')
    common_method: ItemCommonMethodOption0 | list[ItemCommonMethodItem] = Field(default=..., alias='common:method', description='Validation method(s) used in the respective "Scope of review".')

class CommonDataQualityIndicatorsCommonDataQualityIndicatorOption0(TidasBaseModel):
    name: Literal['Technological representativeness', 'Time representativeness', 'Geographical representativeness', 'Completeness', 'Precision', 'Methodological appropriateness and consistency', 'Overall quality'] = Field(default=..., alias='@name')
    value: Literal['Very good', 'Good', 'Fair', 'Poor', 'Very poor', 'Not evaluated / unknown', 'Not applicable'] = Field(default=..., alias='@value')

class CommonDataQualityIndicatorsCommonDataQualityIndicatorItem(TidasBaseModel):
    name: Literal['Technological representativeness', 'Time representativeness', 'Geographical representativeness', 'Completeness', 'Precision', 'Methodological appropriateness and consistency', 'Overall quality'] = Field(default=..., alias='@name')
    value: Literal['Very good', 'Good', 'Fair', 'Poor', 'Very poor', 'Not evaluated / unknown', 'Not applicable'] = Field(default=..., alias='@value')

class ValidationReviewCommonDataQualityIndicators(TidasBaseModel):
    """Data quality indicators serve to provide the reviewed key information on the data set in a defined, computer-readable (and hence searchable) form. This serves to support LCA practitioners to identify/select the highest quality and most appropriate data sets."""
    common_data_quality_indicator: CommonDataQualityIndicatorsCommonDataQualityIndicatorOption0 | list[CommonDataQualityIndicatorsCommonDataQualityIndicatorItem] = Field(default=..., alias='common:dataQualityIndicator', description='Data quality indicators serve to provide the reviewed key information on the data set in a defined, computer-readable (and hence searchable) form. This serves to support LCA practitioners to identify/select the highest quality and most appropriate data sets.')

class ModellingAndValidationValidationReview(TidasBaseModel):
    """Type of review that has been performed regarding independency and type of review process."""
    type: Literal['Dependent internal review', 'Independent internal review', 'Independent external review', 'Accredited third party review', 'Independent review panel', 'Not reviewed'] = Field(default=..., alias='@type')
    common_scope: ReviewCommonScopeOption0 | list[ReviewCommonScopeItem] | None = Field(default=None, alias='common:scope', description='Scope of review regarding which aspects and components of the data set was reviewed or verified. In case of aggregated e.g. LCI results also and on which level of detail (e.g. LCI results only, included unit processes, ...) the review / verification was performed.')
    common_data_quality_indicators: ValidationReviewCommonDataQualityIndicators | None = Field(default=None, alias='common:dataQualityIndicators', description='Data quality indicators serve to provide the reviewed key information on the data set in a defined, computer-readable (and hence searchable) form. This serves to support LCA practitioners to identify/select the highest quality and most appropriate data sets.')
    common_review_details: MultiLangList = Field(default_factory=MultiLangList, alias='common:reviewDetails', description='Summary of the review. All the following items should be explicitly addressed: Representativeness, completeness, and precision of Inputs and Outputs for the process in its documented location, technology and time i.e. both completeness of technical model (product, waste, and elementary flows) and completeness of coverage of the relevant problem fields (environmental, human health, resource use) for this specific good, service, or process. Plausibility of data. Correctness and appropriateness of the data set documentation. Appropriateness of system boundaries, cut-off rules, LCI modelling choices such as e.g. allocation, consistency of included processes and of LCI methodology. If the data set comprises pre-calculated LCIA results, the correspondence of the Input and Output elementary flows (including their geographical validity) with the applied LCIA method(s) should be addressed by the reviewer. An overall quality statement on the data set may be included here.')
    common_reference_to_name_of_reviewer_and_institution: GlobalReferenceType | None = Field(default=None, alias='common:referenceToNameOfReviewerAndInstitution', description='"Contact data set" of reviewer. The full name of reviewer(s) and institution(s) as well as a contact address and/or email should be provided in that contact data set.')
    common_other_review_details: MultiLangList = Field(default_factory=MultiLangList, alias='common:otherReviewDetails', description='Further information from the review process, especially comments received from third parties once the data set has been published or additional reviewer comments from an additional external review.')
    common_reference_to_complete_review_report: GlobalReferenceType | None = Field(default=None, alias='common:referenceToCompleteReviewReport', description='"Source data set" of the complete review report.')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessDataSetModellingAndValidationValidation(TidasBaseModel):
    """Review information on LCIA method."""
    review: ModellingAndValidationValidationReview = Field(default=..., alias='review', description='Type of review that has been performed regarding independency and type of review process.')
    common_other: str | None = Field(default=None, alias='common:other')

class ComplianceDeclarationsComplianceOption0(TidasBaseModel):
    common_reference_to_compliance_system: GlobalReferenceType = Field(default=..., alias='common:referenceToComplianceSystem', description='"Source data set" of the "Compliance system" that is declared to be met by the data set.')
    common_approval_of_overall_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:approvalOfOverallCompliance', description='Official approval whether or not and in how far the data set meets all the requirements of the "Compliance system" refered to. This approval should be issued/confirmed by the owner of that compliance system, who is identified via the respective "Contact data set".')
    common_nomenclature_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:nomenclatureCompliance', description='Nomenclature compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_methodological_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:methodologicalCompliance', description='Methodological compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_review_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:reviewCompliance', description='Review/Verification compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_documentation_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:documentationCompliance', description='Documentation/Reporting compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_quality_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:qualityCompliance', description='Quality compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_other: str | None = Field(default=None, alias='common:other')

class ComplianceDeclarationsComplianceItem(TidasBaseModel):
    common_reference_to_compliance_system: GlobalReferenceType = Field(default=..., alias='common:referenceToComplianceSystem', description='"Source data set" of the "Compliance system" that is declared to be met by the data set.')
    common_approval_of_overall_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:approvalOfOverallCompliance', description='Official approval whether or not and in how far the data set meets all the requirements of the "Compliance system" refered to. This approval should be issued/confirmed by the owner of that compliance system, who is identified via the respective "Contact data set".')
    common_nomenclature_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:nomenclatureCompliance', description='Nomenclature compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_methodological_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:methodologicalCompliance', description='Methodological compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_review_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:reviewCompliance', description='Review/Verification compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_documentation_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:documentationCompliance', description='Documentation/Reporting compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_quality_compliance: Literal['Fully compliant', 'Not compliant', 'Not defined'] = Field(default=..., alias='common:qualityCompliance', description='Quality compliance of this data set with the respective requirements set by the "compliance system" refered to.')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessDataSetModellingAndValidationComplianceDeclarations(TidasBaseModel):
    """Statements on compliance of several data set aspects with compliance requirements as defined by the referenced compliance system (e.g. an EPD scheme, handbook of a national or international data network such as the ILCD, etc.)."""
    compliance: ComplianceDeclarationsComplianceOption0 | list[ComplianceDeclarationsComplianceItem] = Field(default=..., alias='compliance', description='One compliance declaration. Multiple declarations may be provided.')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessesProcessDataSetModellingAndValidation(TidasBaseModel):
    lci_method_and_allocation: ProcessDataSetModellingAndValidationLCIMethodAndAllocation = Field(default=..., alias='LCIMethodAndAllocation')
    data_sources_treatment_and_representativeness: ProcessDataSetModellingAndValidationDataSourcesTreatmentAndRepresentativeness | None = Field(default=None, alias='dataSourcesTreatmentAndRepresentativeness')
    completeness: ProcessDataSetModellingAndValidationCompleteness | None = Field(default=None, alias='completeness')
    validation: ProcessDataSetModellingAndValidationValidation = Field(default=..., alias='validation', description='Review information on LCIA method.')
    compliance_declarations: ProcessDataSetModellingAndValidationComplianceDeclarations = Field(default=..., alias='complianceDeclarations', description='Statements on compliance of several data set aspects with compliance requirements as defined by the referenced compliance system (e.g. an EPD scheme, handbook of a national or international data network such as the ILCD, etc.).')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessDataSetAdministrativeInformationCommonCommissionerAndGoal(TidasBaseModel):
    """Basic information about goal and scope of the data set."""
    common_reference_to_commissioner: GlobalReferenceType = Field(default=..., alias='common:referenceToCommissioner', description='"Contact data set" of the commissioner / financing party of the data collection / compilation and of the data set modelling. For groups of commissioners, each single organisation should be named. For data set updates and for direct use of data from formerly commissioned studies, also the original commissioner should be named.')
    common_project: MultiLangList = Field(default_factory=MultiLangList, alias='common:project', description='Extract of the information items linked to goal and scope of LCIA method modeling.')
    common_intended_applications: MultiLangList = Field(default_factory=MultiLangList, alias='common:intendedApplications', description='Documentation of the intended application(s) of data collection and data set modelling. This indicates / includes information on the level of detail, the specifidity, and the quality ambition in the effort.')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessDataSetAdministrativeInformationDataGenerator(TidasBaseModel):
    """Expert(s), that compiled and modelled the data set as well as internal administrative information linked to the data generation activity."""
    common_reference_to_person_or_entity_generating_the_data_set: GlobalReferenceType | None = Field(default=None, alias='common:referenceToPersonOrEntityGeneratingTheDataSet', description='"Contact data set" of the person(s), working group(s), organisation(s) or database network, that generated the data set, i.e. being responsible for its correctness regarding methods, inventory, and documentation.')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessDataSetAdministrativeInformationDataEntryBy(TidasBaseModel):
    """Staff or entity, that documented the generated data set, entering the information into the database; plus administrative information linked to the data entry activity."""
    common_time_stamp: DateTime = Field(default=..., alias='common:timeStamp')
    common_reference_to_data_set_format: GlobalReferenceType = Field(default=..., alias='common:referenceToDataSetFormat', description='"Source data set" of the used version of the ILCD format. If additional data format fields have been integrated into the data set file, using the "namespace" option, the used format namespace(s) are to be given. This is the case if the data sets carries additional information as specified by other, particular LCA formats, e.g. of other database networks or LCA softwares.')
    common_reference_to_converted_original_data_set_from: GlobalReferenceType | None = Field(default=None, alias='common:referenceToConvertedOriginalDataSetFrom', description='"Source data set" of the database or data set publication from which this data set has been obtained by conversion. This can cover e.g. conversion to a different format, applying a different nomenclature, mapping of flow names, conversion of units, etc. This may however not have changed or re-modeled the Inputs and Outputs, i.e. obtaining the same LCIA results. This entry is required for converted data sets stemming originally from other LCA databases (e.g. when re-publishing data from IISI, ILCD etc. databases). [Note: Identically re-published data sets are identied in the field "Unchanged re-publication of:" in the section "Publication and Ownership".]')
    common_reference_to_person_or_entity_entering_the_data: GlobalReferenceType = Field(default=..., alias='common:referenceToPersonOrEntityEnteringTheData', description='"Contact data set" of the responsible person or entity that has documented this data set, i.e. entered the data and the descriptive information.')
    common_reference_to_data_set_use_approval: GlobalReferenceType | None = Field(default=None, alias='common:referenceToDataSetUseApproval', description='"Source data set": Names exclusively the producer or operator of the good, service or technology represented by this data set, which officially has approved this data set in all its parts. In case of nationally or internationally averaged data sets, this will be the respective business association. If no official approval has been given, the entry "No official approval by producer or operator" is to be entered and the reference will point to an empty "Contact data set". [Notes: The producer or operator may only be named here, if a written approval of this data set was given. A recognition of this data set by any other organisation then the producer/operator of the good, service, or process is not to be stated here, but as a "review" in the validation section.]')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessDataSetAdministrativeInformationPublicationAndOwnership(TidasBaseModel):
    """Information related to publication and version management of the data set including copyright and access restrictions."""
    common_date_of_last_revision: datetime | None = Field(default=None, alias='common:dateOfLastRevision', description='Date when the data set was revised for the last time, typically manually set.')
    common_data_set_version: str = Field(default=..., alias='common:dataSetVersion', description='Version number of data set. First two digits refer to major updates, the second two digits to minor revisions and error corrections etc. The third three digits are intended for automatic and internal counting of versions during data set development. Together with the data set\'s UUID, the "Data set version" uniquely identifies each data set.')
    common_reference_to_preceding_data_set_version: GlobalReferenceType | None = Field(default=None, alias='common:referenceToPrecedingDataSetVersion', description='Last preceding data set, which was replaced by this version. Either a URI of that data set (i.e. an internet address) or its UUID plus version number is given (or both).')
    common_permanent_data_set_uri: str = Field(default=..., alias='common:permanentDataSetURI', description="URI (i.e. an internet address) of the original of this data set. [Note: This equally globally unique identifier supports users and software tools to identify and retrieve the original version of a data set via the internet or to check for available updates. The URI must not represent an existing WWW address, but it should be unique and point to the data access point, e.g. by combining the data owner's www path with the data set's UUID, e.g. http://www.mycompany.com/lca/processes/50f12420-8855-12db-b606-0900210c9a66.]")
    common_workflow_and_publication_status: Literal['Working draft', 'Final draft for internal review', 'Final draft for external review', 'Data set finalised; unpublished', 'Under revision', 'Withdrawn', 'Data set finalised; subsystems published', 'Data set finalised; entirely published'] | None = Field(default=None, alias='common:workflowAndPublicationStatus', description='Workflow or publication status of data set. Details e.g. of foreseen publication dates should be provided on request by the "Data set owner".')
    common_reference_to_unchanged_republication: GlobalReferenceType | None = Field(default=None, alias='common:referenceToUnchangedRepublication', description='"Source data set" of the publication, in which this data set was published for the first time. [Note: This refers to exactly this data set as it is, without any format conversion, adjustments, flow name mapping, etc. In case this data set was modified/converted, the original source is documented in "Converted original data set from:" in section "Data entry by".]')
    common_reference_to_registration_authority: GlobalReferenceType | None = Field(default=None, alias='common:referenceToRegistrationAuthority', description='"Contact data set" of the authority that has registered this data set.')
    common_registration_number: String | None = Field(default=None, alias='common:registrationNumber', description='A unique identifying number for this data set issued by the registration authority.')
    common_reference_to_ownership_of_data_set: GlobalReferenceType = Field(default=..., alias='common:referenceToOwnershipOfDataSet', description='"Contact data set" of the person or entity who owns this data set. (Note: this is not necessarily the publisher of the data set.)')
    common_copyright: Literal['true', 'false'] = Field(default=..., alias='common:copyright', description='Indicates whether or not a copyright on the data set exists. Decided upon by the "Owner of data set". [Note: See also field "Access and use restrictions".]')
    common_reference_to_entities_with_exclusive_access: GlobalReferenceType | None = Field(default=None, alias='common:referenceToEntitiesWithExclusiveAccess', description='"Contact data set" of those entities or persons (or groups of these), to which an exclusive access to this data set is granted. Mainly intended to be used in confidentiality management in projects. [Note: See also field "Access and use restrictions".]')
    common_license_type: Literal['Free of charge for all users and uses', 'Free of charge for some user types or use types', 'Free of charge for members only', 'License fee', 'Other'] = Field(default=..., alias='common:licenseType', description='Type of license that applies to the access and use of this data set.')
    common_access_restrictions: MultiLangList = Field(default_factory=MultiLangList, alias='common:accessRestrictions', description='Access restrictions / use conditions for this data set as free text or referring to e.g. license conditions. In case of no restrictions "None" is entered.')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessesProcessDataSetAdministrativeInformation(TidasBaseModel):
    """Information on data set management and administration."""
    common_commissioner_and_goal: ProcessDataSetAdministrativeInformationCommonCommissionerAndGoal = Field(default=..., alias='common:commissionerAndGoal', description='Basic information about goal and scope of the data set.')
    data_generator: ProcessDataSetAdministrativeInformationDataGenerator | None = Field(default=None, alias='dataGenerator', description='Expert(s), that compiled and modelled the data set as well as internal administrative information linked to the data generation activity.')
    data_entry_by: ProcessDataSetAdministrativeInformationDataEntryBy = Field(default=..., alias='dataEntryBy', description='Staff or entity, that documented the generated data set, entering the information into the database; plus administrative information linked to the data entry activity.')
    publication_and_ownership: ProcessDataSetAdministrativeInformationPublicationAndOwnership = Field(default=..., alias='publicationAndOwnership', description='Information related to publication and version management of the data set including copyright and access restrictions.')
    common_other: str | None = Field(default=None, alias='common:other')

class ItemAllocationsAllocation(TidasBaseModel):
    """specifies one allocation of this exchange (see the attributes of this tag below)"""
    internal_reference_to_co_product: Int6 | None = Field(default=None, alias='@internalReferenceToCoProduct', description='Reference to one of the co-products. The applied allocation approach(es), details and and explanations are documented in the fields "LCI method approaches" and "Deviations from LCI method approaches / explanations". [Notes: Applicable only to multifunctional processes. The documented allocated fractions are only applicable when using the data set for attributional modelling and are to be ignored for consequential modeling.]')
    allocated_fraction: Perc | None = Field(default=None, alias='@allocatedFraction', description='Fraction (expressed in %) of this Input or Output flow that is foreseen to be allocated to this co-product (recommended allocation). The numbers across the co-products should sum up to 100%.')

class ExchangeItemAllocations(TidasBaseModel):
    """container tag for the specification of allocations if process has more than one reference product. Use only for multifunctional processes."""
    allocation: ItemAllocationsAllocation | None = Field(default=None, alias='allocation', description='specifies one allocation of this exchange (see the attributes of this tag below)')

class ExchangeItemReferencesToDataSource(TidasBaseModel):
    """\"Source data set\" of data source(s) used for the value of this specific Input or Output, especially if differing from the general data source used for this data set."""
    reference_to_data_source: GlobalReferenceType | None = Field(default=None, alias='referenceToDataSource', description='"Source data set" of data source(s) used for the value of this specific Input or Output, especially if differing from the general data source used for this data set.')
    common_other: str | None = Field(default=None, alias='common:other')

class ExchangesExchangeItem(TidasBaseModel):
    data_set_internal_id: Int6 = Field(default=..., alias='@dataSetInternalID')
    reference_to_flow_data_set: GlobalReferenceType = Field(default=..., alias='referenceToFlowDataSet', description='"Flow data set" of this Input or Output.')
    location: String | None = Field(default=None, alias='location', description='Location where exchange of elementary flow occurs. Used only for those LCIA methods, that make use of this information. This information refers to the entry within the same field in the "Inputs and Outpts" section of the "Process or LCI result data set".')
    function_type: Literal['General reminder flow', 'Allocation reminder flow', 'System expansion reminder flow'] | None = Field(default=None, alias='functionType')
    exchange_direction: Literal['Input', 'Output'] = Field(default=..., alias='exchangeDirection')
    reference_to_variable: String | None = Field(default=None, alias='referenceToVariable', description='Data set internal reference to a variable or parameter name as defined in the section "Mathematical model". The value of this variable or parameter acts as linear multiplier to the value given in the field "Mean amount" to yield the "Resulting amount", which is the final value in the inventory.')
    mean_amount: Real = Field(default=..., alias='meanAmount', description='Mean amount of the Input or Output. Only significant digits of the amount should be stated.')
    resulting_amount: Real = Field(default=..., alias='resultingAmount', description='Final value to be used for calculation of the LCI results and in the product system: It is calculated as the product of the "Mean amount" value times the value of the "Variable". In case that no "Variable" entry is given, the "Resulting amount" is identical to the "Mean amount", i.e. a factor "1" is applied.')
    minimum_amount: Real | None = Field(default=None, alias='minimumAmount', description='Minimum amount of the Input or Output in case the uncertainty distribution is uniform or triangular. In case of calculated LCI results and for the aggregated flows in Partly terminated system data sets, the lower end of the 95% likelihood range, i.e. the "2.5% value" can be reported in this field.')
    maximum_amount: Real | None = Field(default=None, alias='maximumAmount', description='Maximum amount of the Input or Output in case the uncertainty distribution is uniform or triangular. In case of calculated LCI results and for the aggregated flows in Partly terminated system data sets, the upper end of the 95% likelihood range, i.e. the "97.5% value" can be reported in this field.')
    uncertainty_distribution_type: Literal['undefined', 'log-normal', 'normal', 'triangular', 'uniform'] | None = Field(default=None, alias='uncertaintyDistributionType')
    relative_standard_deviation95_in: Perc | None = Field(default=None, alias='relativeStandardDeviation95In', description='The resulting overall uncertainty of the calculated variable value considering uncertainty of measurements, modelling, appropriateness etc. [Notes: For log-normal distribution the square of the geometric standard deviation (SDg^2) is stated. Mean value times SDg^2 equals the 97.5% value (= Maximum value), Mean value divided by SDg^2 equals the 2.5% value (= Minimum value). For normal distribution the doubled standard deviation value (2*SD) is entered. Mean value plus 2*SD equals 97.5% value (= Maximum value), Mean value minus 2*SD equals 2.5% value (= Minimum value). This data field remains empty when uniform or triangular uncertainty distribution is applied.]')
    allocations: ExchangeItemAllocations | None = Field(default=None, alias='allocations', description='container tag for the specification of allocations if process has more than one reference product. Use only for multifunctional processes.')
    data_source_type: Literal['Primary', '> 90% primary', 'Mixed primary / secondary', 'Secondary'] | None = Field(default=None, alias='dataSourceType')
    data_derivation_type_status: Literal['Measured', 'Calculated', 'Estimated', 'Unknown derivation', 'Missing important', 'Missing unimportant'] = Field(default=..., alias='dataDerivationTypeStatus')
    references_to_data_source: ExchangeItemReferencesToDataSource | None = Field(default=None, alias='referencesToDataSource', description='"Source data set" of data source(s) used for the value of this specific Input or Output, especially if differing from the general data source used for this data set.')
    general_comment: MultiLangList = Field(default_factory=MultiLangList, alias='generalComment', description='General comment on this specific Input or Output, e.g. commenting on the data sources used and their specific representatuveness etc., on the status of "finalisation" of an entry as workflow information, etc.')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessesProcessDataSetExchanges(TidasBaseModel):
    exchange: list[ExchangesExchangeItem] = Field(default_factory=list, alias='exchange')
    common_other: str | None = Field(default=None, alias='common:other')

class LCIAResultsLCIAResultOption0(TidasBaseModel):
    reference_to_lcia_method_data_set: GlobalReferenceType | None = Field(default=None, alias='referenceToLCIAMethodDataSet', description='"LCIA method data set" applied to calculate the LCIA results.')
    mean_amount: Real = Field(default=..., alias='meanAmount', description='Mean amount of the Input or Output. Only significant digits of the amount should be stated.')
    uncertainty_distribution_type: Literal['undefined', 'log-normal', 'normal', 'triangular', 'uniform'] | None = Field(default=None, alias='uncertaintyDistributionType')
    relative_standard_deviation95_in: Perc | None = Field(default=None, alias='relativeStandardDeviation95In', description='The resulting overall uncertainty of the calculated variable value considering uncertainty of measurements, modelling, appropriateness etc. [Notes: For log-normal distribution the square of the geometric standard deviation (SDg^2) is stated. Mean value times SDg^2 equals the 97.5% value (= Maximum value), Mean value divided by SDg^2 equals the 2.5% value (= Minimum value). For normal distribution the doubled standard deviation value (2*SD) is entered. Mean value plus 2*SD equals 97.5% value (= Maximum value), Mean value minus 2*SD equals 2.5% value (= Minimum value). This data field remains empty when uniform or triangular uncertainty distribution is applied.]')
    general_comment: MultiLangList = Field(default_factory=MultiLangList, alias='generalComment', description='General comment on this specific Input or Output, e.g. commenting on the data sources used and their specific representatuveness etc., on the status of "finalisation" of an entry as workflow information, etc.')
    common_other: str | None = Field(default=None, alias='common:other')

class LCIAResultsLCIAResultItem(TidasBaseModel):
    reference_to_lcia_method_data_set: GlobalReferenceType | None = Field(default=None, alias='referenceToLCIAMethodDataSet', description='"LCIA method data set" applied to calculate the LCIA results.')
    mean_amount: Real = Field(default=..., alias='meanAmount', description='Mean amount of the Input or Output. Only significant digits of the amount should be stated.')
    uncertainty_distribution_type: Literal['undefined', 'log-normal', 'normal', 'triangular', 'uniform'] | None = Field(default=None, alias='uncertaintyDistributionType')
    relative_standard_deviation95_in: Perc | None = Field(default=None, alias='relativeStandardDeviation95In', description='The resulting overall uncertainty of the calculated variable value considering uncertainty of measurements, modelling, appropriateness etc. [Notes: For log-normal distribution the square of the geometric standard deviation (SDg^2) is stated. Mean value times SDg^2 equals the 97.5% value (= Maximum value), Mean value divided by SDg^2 equals the 2.5% value (= Minimum value). For normal distribution the doubled standard deviation value (2*SD) is entered. Mean value plus 2*SD equals 97.5% value (= Maximum value), Mean value minus 2*SD equals 2.5% value (= Minimum value). This data field remains empty when uniform or triangular uncertainty distribution is applied.]')
    general_comment: MultiLangList = Field(default_factory=MultiLangList, alias='generalComment', description='General comment on this specific Input or Output, e.g. commenting on the data sources used and their specific representatuveness etc., on the status of "finalisation" of an entry as workflow information, etc.')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessesProcessDataSetLCIAResults(TidasBaseModel):
    lcia_result: LCIAResultsLCIAResultOption0 | list[LCIAResultsLCIAResultItem] | None = Field(default=None, alias='LCIAResult')
    common_other: str | None = Field(default=None, alias='common:other')

class ProcessesProcessDataSet(TidasBaseModel):
    xmlns_common: Literal['http://lca.jrc.it/ILCD/Common'] = Field(default=..., alias='@xmlns:common')
    xmlns: Literal['http://lca.jrc.it/ILCD/Process'] = Field(default=..., alias='@xmlns')
    xmlns_xsi: Literal['http://www.w3.org/2001/XMLSchema-instance'] = Field(default=..., alias='@xmlns:xsi')
    version: Literal['1.1'] = Field(default=..., alias='@version')
    locations: Literal['../ILCDLocations.xml'] = Field(default=..., alias='@locations')
    xsi_schema_location: str = Field(default=..., alias='@xsi:schemaLocation', description='http://lca.jrc.it/ILCD/Process ../../schemas/ILCD_ProcessDataSet.xsd')
    process_information: ProcessesProcessDataSetProcessInformation = Field(default=..., alias='processInformation', description='Corresponds to the ISO/TS 14048 section "Process description". It comprises the following six sub-sections: 1) "Data set information" for data set identification and overarching information items, 2) "Quantitative reference", 3) "Time", 4) "Geography", 5) "Technology" and 6) "Mathematical relations".')
    modelling_and_validation: ProcessesProcessDataSetModellingAndValidation = Field(default=..., alias='modellingAndValidation')
    administrative_information: ProcessesProcessDataSetAdministrativeInformation = Field(default=..., alias='administrativeInformation', description='Information on data set management and administration.')
    exchanges: ProcessesProcessDataSetExchanges = Field(default=..., alias='exchanges')
    lcia_results: ProcessesProcessDataSetLCIAResults | None = Field(default=None, alias='LCIAResults')
    common_other: str | None = Field(default=None, alias='common:other')

class Processes(TidasBaseModel):
    process_data_set: ProcessesProcessDataSet = Field(default=..., alias='processDataSet')
