"""
Auto generated file. DO NOT EDIT.
Source: tidas_lciamethods.json
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
from .tidas_data_types import Perc
from .tidas_data_types import Real
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

class CommonClassItemOption2(TidasBaseModel):
    level: LevelType = Field(default=..., alias='@level')
    class_id: str = Field(default=..., alias='@classId')
    text: str = Field(default=..., alias='#text')

class DataSetInformationClassificationInformationCommonClassification(TidasBaseModel):
    """Optional statistical or other classification of the data set. Typically also used for structuring LCA databases."""
    common_class: list[CommonClassItemOption0 | CommonClassItemOption1 | CommonClassItemOption2] = Field(default=..., alias='common:class')
    common_other: str | None = Field(default=None, alias='common:other')

class LCIAMethodInformationDataSetInformationClassificationInformation(TidasBaseModel):
    common_classification: DataSetInformationClassificationInformationCommonClassification = Field(default=..., alias='common:classification', description='Optional statistical or other classification of the data set. Typically also used for structuring LCA databases.')

class LCIAMethodDataSetLCIAMethodInformationDataSetInformation(TidasBaseModel):
    common_uuid: UUID = Field(default=..., alias='common:UUID', description='Unique identifier of the data set. The UUID is a 128-bit number represented as a hexadecimal string of the form: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx. The UUID is used to uniquely identify the data set in the ILCD database.')
    common_name: MultiLangList = Field(default_factory=MultiLangList, alias='common:name', description='Name of the data set. Composed as follows "LCIA methodology short name; Impact category/ies; midpoint/endpoint; Impact indicator; Source short name". Not applicable components are left out. Examples: "Impacts2007+; Climate change; midpoint; Global Warming Potential; IPCC 2001"; "ABC 2006; Acidification; endpoint; Species diversity loss; John Doe 2006"; "My-indicator2009; combined; endpoint; Ecopoints; various"')
    methodology: str | None = Field(default=None, alias='methodology', description='Name of the LCIA methodology/ies the data set belongs to, if any')
    classification_information: LCIAMethodInformationDataSetInformationClassificationInformation = Field(default=..., alias='classificationInformation')
    impact_category: Literal['Climate change', 'Ozone depletion', 'Terrestrial Eutrophication', 'Aquatic Eutrophication', 'Acidification', 'Photochemical ozone creation', 'Land use', 'Abiotic resource depletion', 'Biotic resource depletion', 'Ionizing radiation', 'Cancer human health effects', 'Non-cancer human health effects', 'Respiratory inorganics', 'Aquatic eco-toxicity', 'Terrestrial eco-toxicity', 'other'] | None = Field(default=None, alias='impactCategory', description='Impact category/ies covered by the LCIA method or methodology.')
    area_of_protection: Literal['Natural resources', 'Natural environment', 'Human health', 'Other'] | None = Field(default=None, alias='areaOfProtection', description='For damage (endpoint) and single-point indicators only: Area(s) of Protection the data set relates to.')
    impact_indicator: String | None = Field(default=None, alias='impactIndicator', description='Description of the meaning of the impact indicator of this data set (not applicable for LCIA methodologies data sets).')
    common_general_comment: MultiLangList = Field(default_factory=MultiLangList, alias='common:generalComment', description='General information about the data set, including e.g. general (internal, not reviewed) quality statements as well as information sources used. (Note: Please also check the more specific fields e.g. on "Intended application", "Advice on data set use" and the fields in the "Modelling and validation" section to avoid overlapping entries.)')
    reference_to_external_documentation: GlobalReferenceType | None = Field(default=None, alias='referenceToExternalDocumentation', description='"Source data set(s)" of external documents / files with further documentative information on the data set including on underlying data sources (e.g. time, geographical coverage, impact models, characterisation factors, substance property databases employed, etc.). (Note: can indirectly reference to digital file.)')
    common_other: str | None = Field(default=None, alias='common:other')

class LCIAMethodDataSetLCIAMethodInformationQuantitativeReference(TidasBaseModel):
    """This section allows to refer to the LCIA method(ology)'s quantitative reference, which is always the unit, in which the characterisation factors of the impact indicator are measured, e.g. \"kg CO2-Equivalents\"."""
    reference_quantity: GlobalReferenceType = Field(default=..., alias='referenceQuantity', description='"Flow property data set" of the reference quantity (flow property), in which the impact indicator values are measured.')
    common_other: str | None = Field(default=None, alias='common:other')

class LCIAMethodDataSetLCIAMethodInformationTime(TidasBaseModel):
    reference_year: MultiLangList = Field(default_factory=MultiLangList, alias='referenceYear', description='Reference year when the emission is assumed to take place, i.e. the start year of the time period for which the impact is modelled. For time-independent models "time independent" should be stated.')
    duration: MultiLangList = Field(default_factory=MultiLangList, alias='duration', description='Time period for which the impact is modelled.')
    time_representativeness_description: MultiLangList = Field(default_factory=MultiLangList, alias='timeRepresentativenessDescription', description='Description of the valid time span of the data set including information on limited usability within sub-time spans, if any.')
    common_other: str | None = Field(default=None, alias='common:other')

class GeographyInterventionLocationOption0(TidasBaseModel):
    text: str | None = Field(default=None, alias='#text')
    latitude_and_longitude: GIS | None = Field(default=None, alias='@latitudeAndLongitude', description='Geographical latitude and longitude reference of "Location" / "Sub-location". For area-type locations (e.g. countries, continents) the field is empty.')

class GeographyIntervensionSubLocationOption0(TidasBaseModel):
    text: str | None = Field(default=None, alias='#text')
    latitude_and_longitude: GIS | None = Field(default=None, alias='@latitudeAndLongitude', description='Geographical latitude and longitude reference of "Location" / "Sub-location". For area-type locations (e.g. countries, continents) the field is empty.')

class GeographyImpactLocationOption0(TidasBaseModel):
    text: str | None = Field(default=None, alias='#text')
    latitude_and_longitude: GIS | None = Field(default=None, alias='@latitudeAndLongitude', description='Geographical latitude and longitude reference of "Location" / "Sub-location". For area-type locations (e.g. countries, continents) the field is empty.')

class LCIAMethodDataSetLCIAMethodInformationGeography(TidasBaseModel):
    intervention_location: GeographyInterventionLocationOption0 | str | None = Field(default=None, alias='interventionLocation', description='Specific, country, or region of the elementary flows\' / exchanges\' occurence for which the LCIA method(ology) is valid / modelled. [Note: Entry can be of type "two-letter ISO 3166 country code" for countries, "seven-letter regional codes" for regions or continents, or "market areas and market organisations", as predefined for the ILCD. Also a name for e.g. a specific plant etc. can be given here (e.g. "FR, Lyon, XY Company, Z Site"; user defined). ]')
    intervension_sub_location: GeographyIntervensionSubLocationOption0 | str | None = Field(default=None, alias='intervensionSubLocation', description='Geographical sub-unit(s) of "Intervention location(s)" that further specify the specifically modelled sub-locations. Such sub-locations can be e.g. sites of a company, specific catchments modleled, countries of a continent, or locations in a country. Information on limited representativeness should be provided if applicable.')
    impact_location: GeographyImpactLocationOption0 | str | None = Field(default=None, alias='impactLocation', description='Location or region where the impact is modelled to take place. [Note: Entry can be of type "two-letter ISO 3166 country code" for countries, "seven-letter regional codes" for regions or continents, or "market areas and market organisations", as predefined for the ILCD. Also a name for e.g. a specific catchment etc. can be given here, user defined).]')
    geographical_representativeness_description: MultiLangList = Field(default_factory=MultiLangList, alias='geographicalRepresentativenessDescription', description='Further explanation on additional aspects of the location, both regarding the intervention and the impact: whether certain areas are exempted from the location, whether data is only valid for certain sub-locations within the location indicated, or whether impact indicator values for certain elementary flows are extrapolated from another geographical area than indicated. Information on the use of generic intervention and/or impact locations, and other restrictions.')
    common_other: str | None = Field(default=None, alias='common:other')

class LCIAMethodDataSetLCIAMethodInformationImpactModel(TidasBaseModel):
    """Provides information about the general representativiness of the data set and about its composition of single LCIA-methods."""
    model_name: ST = Field(default=..., alias='modelName', description='Name(s) of the model(s) used for calculating the LCIA impact indicator values (if any)')
    model_description: MultiLangList = Field(default_factory=MultiLangList, alias='modelDescription', description='Description of the model used for calculating the LCIA impact indicator values, including underlying substance property data sources, background concentrations, etc. If an LCIA methodology comprises several LCIA methods, these are explicitly included in the description. Professional nomenclature is used for the description. Note that eventually included Normalisation and Weighting factors are described in the dedicated separate fields.')
    reference_to_model_source: GlobalReferenceType | None = Field(default=None, alias='referenceToModelSource', description='"Source data set(s)" of data sources concerning the characterisation model (guidelines, supporting documentation etc)')
    reference_to_included_methods: GlobalReferenceType | None = Field(default=None, alias='referenceToIncludedMethods', description='"LCIA method data set(s)" of LCIA characterisation methods included in this data set or used to derive this LCIA methodology')
    considered_mechanisms: MultiLangList = Field(default_factory=MultiLangList, alias='consideredMechanisms', description='Description of the environmental or other mechanisms included in the explicitly considered part of the impact chain. Can relate to (ilustrative): For emissions e.g.: transport, conversion / degradation, exposure, effect(s), damage(s) on humans and the natural environment. For material and energy resources: scarcity or other impact concept. For land use: soil, area, biocoenosis related meachanisms, effect(s), damage(s).')
    reference_to_methodology_flow_chart: GlobalReferenceType | None = Field(default=None, alias='referenceToMethodologyFlowChart', description='"Source data set(s)" of flowchart(s) and/or pictures depicting the LCIA method(ology).')
    common_other: str | None = Field(default=None, alias='common:other')

class LciamethodsLCIAMethodDataSetLCIAMethodInformation(TidasBaseModel):
    data_set_information: LCIAMethodDataSetLCIAMethodInformationDataSetInformation = Field(default=..., alias='dataSetInformation')
    quantitative_reference: LCIAMethodDataSetLCIAMethodInformationQuantitativeReference = Field(default=..., alias='quantitativeReference', description='This section allows to refer to the LCIA method(ology)\'s quantitative reference, which is always the unit, in which the characterisation factors of the impact indicator are measured, e.g. "kg CO2-Equivalents".')
    time: LCIAMethodDataSetLCIAMethodInformationTime = Field(default=..., alias='time')
    geography: LCIAMethodDataSetLCIAMethodInformationGeography | None = Field(default=None, alias='geography')
    impact_model: LCIAMethodDataSetLCIAMethodInformationImpactModel = Field(default=..., alias='impactModel', description='Provides information about the general representativiness of the data set and about its composition of single LCIA-methods.')
    common_other: str | None = Field(default=None, alias='common:other')

class LCIAMethodDataSetModellingAndValidationLCIAMethodNormalisationAndWeighting(TidasBaseModel):
    """LCIA methodological modelling aspects"""
    type_of_data_set: Literal['Inventory indicator', 'Mid-point indicator', 'Damage indicator', 'Area of Protection damage indicator', 'Combined single-point indicator', 'LCIA methodology documentation'] = Field(default=..., alias='typeOfDataSet', description='Type of data set regarding the extent of the impact chain that is covered.')
    lcia_method_principle: Literal['Distance-to-target', 'Critical surface-time', 'Effective volumes', 'AoP-Damage model', 'Carrying capacity', 'Resource dissipation', 'other'] = Field(default=..., alias='LCIAMethodPrinciple', description='LCIA method principle(s) followed to derive the impact factors.')
    deviations_from_lcia_method_principle: MultiLangList = Field(default_factory=MultiLangList, alias='deviationsFromLCIAMethodPrinciple', description='Short description of possible data set specific deviations from "LCIA method principle(s)". Refers especially to explanations on the combination of LCIA methods with different principles in a single LCIA methodology.')
    normalisation: Literal['true', 'false'] | None = Field(default=None, alias='normalisation', description='Indication whether or not a normalisation step was included in the resulting impact factors.')
    reference_to_usable_normalisation_data_sets: GlobalReferenceType | None = Field(default=None, alias='referenceToUsableNormalisationDataSets', description='"Normalisation data sets" that can be used together with the impact factors of this data set.')
    normalisation_description: MultiLangList = Field(default_factory=MultiLangList, alias='normalisationDescription', description='Short description of the included normalisation, if any.')
    reference_to_included_normalisation_data_sets: GlobalReferenceType | None = Field(default=None, alias='referenceToIncludedNormalisationDataSets', description='"Normalisation data set(s)" that was/were used to calculate the normalised impact factors of this data set, if any.')
    weighting: Literal['true', 'false'] | None = Field(default=None, alias='weighting', description='Indication whether or not a weighting-step was included in the resulting impact factors.')
    reference_to_usable_weighting_data_sets: GlobalReferenceType | None = Field(default=None, alias='referenceToUsableWeightingDataSets', description='"Weighting data set(s)", that can be used together with the impact factors of this data set.')
    weighting_description: MultiLangList = Field(default_factory=MultiLangList, alias='weightingDescription', description='Short description of the included weighting, if any.')
    reference_to_included_weighting_data_sets: GlobalReferenceType | None = Field(default=None, alias='referenceToIncludedWeightingDataSets', description='"Weighting data set" that was used to calculate the weighted impact factors of this data set, if any.')

class LCIAMethodDataSetModellingAndValidationDataSources(TidasBaseModel):
    """Data sources used for the model and the underlying substance and other data."""
    reference_to_data_source: GlobalReferenceType = Field(default=..., alias='referenceToDataSource', description='"Source data set(s)" of the data source(s) used for the data set e.g. paper, questionnaire, monography etc. The main data sources e.g. for underlying substance properties are named, too.')
    common_other: str | None = Field(default=None, alias='common:other')

class LCIAMethodDataSetModellingAndValidationCompleteness(TidasBaseModel):
    completeness_impact_coverage: Perc | None = Field(default=None, alias='completenessImpactCoverage', description='Estimate of the completeness of coverage of impact(s), as identified in the fields "Impact category/ies" or - only for LCIA methodologies with Damage indicator or Combined single-point indicators - "Area(s) of Protection". Expressed by the quantitative extent of coverage of the scientifically recognized, impact. Note that this information is typically highly uncertain.')
    inventory_items: Int6 | None = Field(default=None, alias='inventoryItems', description='Number of chemical substances/substance groups, chemical elements, or types covered, without considering variants by environmental emission or source compartment, geographical location, time, or other.')

class Option0CommonMethodOption0(TidasBaseModel):
    name: Literal['Validation of data sources', 'Sample tests on calculations', 'Energy balance', 'Element balance', 'Cross-check with other source', 'Cross-check with other data set', 'Expert judgement', 'Mass balance', 'Compliance with legal limitsRegulated Inputs and Outputs e.g. emission data are validated for compliance with legal limits, typically after relating and scaling the data to the regulated processes/sites etc.', 'Compliance with ISO 14040 to 14044', 'Documentation', 'Evidence collection by means of plant visits and/or interviews'] = Field(default=..., alias='@name')

class Option0CommonMethodItem(TidasBaseModel):
    name: Literal['Validation of data sources', 'Sample tests on calculations', 'Energy balance', 'Element balance', 'Cross-check with other source', 'Cross-check with other data set', 'Expert judgement', 'Mass balance', 'Compliance with legal limitsRegulated Inputs and Outputs e.g. emission data are validated for compliance with legal limits, typically after relating and scaling the data to the regulated processes/sites etc.', 'Compliance with ISO 14040 to 14044', 'Documentation', 'Evidence collection by means of plant visits and/or interviews'] = Field(default=..., alias='@name')

class ReviewCommonScopeOption0(TidasBaseModel):
    name: Literal['Raw data', 'Unit process(es), single operation', 'Unit process(es), black box', 'LCI results or Partly terminated system', 'LCIA results', 'Documentation', 'Life cycle inventory methods', 'LCIA results calculation', 'Goal and scope definition'] = Field(default=..., alias='@name')
    common_method: Option0CommonMethodOption0 | list[Option0CommonMethodItem] = Field(default=..., alias='common:method', description='Validation method(s) used in the respective "Scope of review".')

class ItemCommonMethodOption0(TidasBaseModel):
    name: Literal['Validation of data sources', 'Sample tests on calculations', 'Energy balance', 'Element balance', 'Cross-check with other source', 'Cross-check with other data set', 'Expert judgement', 'Mass balance', 'Compliance with legal limitsRegulated Inputs and Outputs e.g. emission data are validated for compliance with legal limits, typically after relating and scaling the data to the regulated processes/sites etc.', 'Compliance with ISO 14040 to 14044', 'Documentation', 'Evidence collection by means of plant visits and/or interviews'] = Field(default=..., alias='@name')

class ItemCommonMethodItem(TidasBaseModel):
    name: Literal['Validation of data sources', 'Sample tests on calculations', 'Energy balance', 'Element balance', 'Cross-check with other source', 'Cross-check with other data set', 'Expert judgement', 'Mass balance', 'Compliance with legal limitsRegulated Inputs and Outputs e.g. emission data are validated for compliance with legal limits, typically after relating and scaling the data to the regulated processes/sites etc.', 'Compliance with ISO 14040 to 14044', 'Documentation', 'Evidence collection by means of plant visits and/or interviews'] = Field(default=..., alias='@name')

class ReviewCommonScopeItem(TidasBaseModel):
    name: Literal['Raw data', 'Unit process(es), single operation', 'Unit process(es), black box', 'LCI results or Partly terminated system', 'LCIA results', 'Documentation', 'Life cycle inventory methods', 'LCIA results calculation', 'Goal and scope definition'] = Field(default=..., alias='@name')
    common_method: ItemCommonMethodOption0 | list[ItemCommonMethodItem] = Field(default=..., alias='common:method', description='Validation method(s) used in the respective "Scope of review".')

class ModellingAndValidationValidationReview(TidasBaseModel):
    """Type of review that has been performed regarding independency and type of review process."""
    type: Literal['Dependent internal review', 'Independent internal review', 'Independent external review', 'Accredited third party review', 'Independent review panel', 'Not reviewed'] = Field(default=..., alias='@type')
    common_scope: ReviewCommonScopeOption0 | list[ReviewCommonScopeItem] | None = Field(default=None, alias='common:scope', description='Scope of review regarding which aspects and components of the data set was reviewed or verified. In case of aggregated e.g. LCI results also and on which level of detail (e.g. LCI results only, included unit processes, ...) the review / verification was performed.')
    common_review_details: MultiLangList = Field(default_factory=MultiLangList, alias='common:reviewDetails', description='Summary of the review. All the following items should be explicitly addressed: completeness and appropriateness of the model, geographical and temporal coverage and differentiation, correctness and precision of substance data or other underlying data; appropriateness and coherence of application of normalisation and/or weighting schemes, if included; correctness, appropriateness, comprehensibility, and completeness of the data set documentation; stakeholder aceptance of LCIA method. Optional: Comment of the reviewer on characterisation factors for single elementary flows or groups of elementary flows. Relevant restrictions to the review due to lack of transparency or documentation should be named. An overall quality statement may be included here.')
    common_reference_to_name_of_reviewer_and_institution: GlobalReferenceType | None = Field(default=None, alias='common:referenceToNameOfReviewerAndInstitution', description='"Contact data set" of reviewer. The full name of reviewer(s) and institution(s) as well as a contact address and/or email should be provided in that contact data set.')
    common_other_review_details: MultiLangList = Field(default_factory=MultiLangList, alias='common:otherReviewDetails', description='Further information from the review process, especially comments received from third parties once the data set has been published or additional reviewer comments from an additional external review.')
    common_reference_to_complete_review_report: GlobalReferenceType | None = Field(default=None, alias='common:referenceToCompleteReviewReport', description='"Source data set" of the complete review report.')
    common_other: str | None = Field(default=None, alias='common:other')

class LCIAMethodDataSetModellingAndValidationValidation(TidasBaseModel):
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

class LCIAMethodDataSetModellingAndValidationComplianceDeclarations(TidasBaseModel):
    """Statements on compliance of several data set aspects with compliance requirements as defined by the referenced compliance system (e.g. an EPD scheme, handbook of a national or international data network such as the ILCD, etc.)."""
    compliance: ComplianceDeclarationsComplianceOption0 | list[ComplianceDeclarationsComplianceItem] = Field(default=..., alias='compliance', description='One compliance declaration. Multiple declarations may be provided.')
    common_other: str | None = Field(default=None, alias='common:other')

class LciamethodsLCIAMethodDataSetModellingAndValidation(TidasBaseModel):
    """Covers the five sub-sections 1) LCIA method, normalisation, weighting 2) Data sources 3) Completeness, 4) Validation, and 5) Compliance declarations."""
    use_advice_for_data_set: MultiLangList = Field(default_factory=MultiLangList, alias='useAdviceForDataSet', description='Methodological advice for the use and application of this data set, such as limits in applicability or representativeness as well as recommendations to use it together with others from the same LCIA methodology to ensure consistency.')
    lcia_method_normalisation_and_weighting: LCIAMethodDataSetModellingAndValidationLCIAMethodNormalisationAndWeighting = Field(default=..., alias='LCIAMethodNormalisationAndWeighting', description='LCIA methodological modelling aspects')
    data_sources: LCIAMethodDataSetModellingAndValidationDataSources = Field(default=..., alias='dataSources', description='Data sources used for the model and the underlying substance and other data.')
    completeness: LCIAMethodDataSetModellingAndValidationCompleteness | None = Field(default=None, alias='completeness')
    validation: LCIAMethodDataSetModellingAndValidationValidation = Field(default=..., alias='validation', description='Review information on LCIA method.')
    compliance_declarations: LCIAMethodDataSetModellingAndValidationComplianceDeclarations = Field(default=..., alias='complianceDeclarations', description='Statements on compliance of several data set aspects with compliance requirements as defined by the referenced compliance system (e.g. an EPD scheme, handbook of a national or international data network such as the ILCD, etc.).')
    common_other: str | None = Field(default=None, alias='common:other')

class LCIAMethodDataSetAdministrativeInformationCommonCommissionerAndGoal(TidasBaseModel):
    """Extract of the information items linked to goal and scope of LCIA method modeling."""
    common_reference_to_commissioner: GlobalReferenceType | None = Field(default=None, alias='common:referenceToCommissioner', description='"Contact data set" of the commissioner / financing party of the data collection / compilation and of the data set modelling. For groups of commissioners, each single organisation should be named. For data set updates and for direct use of data from formerly commissioned studies, also the original commissioner should be named.')
    common_project: MultiLangList = Field(default_factory=MultiLangList, alias='common:project', description='Extract of the information items linked to goal and scope of LCIA method modeling.')
    common_intended_applications: MultiLangList = Field(default_factory=MultiLangList, alias='common:intendedApplications', description='Documentation of the intended application(s) of data collection and data set modelling. This indicates / includes information on the level of detail, the specifidity, and the quality ambition in the effort.')
    common_other: str | None = Field(default=None, alias='common:other')

class LCIAMethodDataSetAdministrativeInformationDataGenerator(TidasBaseModel):
    """Expert(s), that compiled and modelled the data set as well as internal administrative information linked to the data generation activity."""
    common_reference_to_person_or_entity_generating_the_data_set: GlobalReferenceType = Field(default=..., alias='common:referenceToPersonOrEntityGeneratingTheDataSet', description='"Contact data set" of the person(s), working group(s), organisation(s) or database network, that generated the data set, i.e. being responsible for its correctness regarding methods, inventory, and documentation.')
    common_other: str | None = Field(default=None, alias='common:other')

class AdministrativeInformationDataEntryByRecommendationBy(TidasBaseModel):
    reference_to_entity: GlobalReferenceType = Field(default=..., alias='referenceToEntity', description='"Contact data set(s)" of the governmental body/ies that has/ve officially recommended this LCIA method data set and its impact factors for use within the documented scope. Eventually deviating (downgraded) recommendations for individual exchanges are documented in the "Inputs and Outputs" section of the data set.')
    level: Literal['Level I', 'Level II', 'Level III', 'Interim', 'Not recommended'] = Field(default=..., alias='level', description='Level of recommendation given to this data set by the recommending governmental body. Note that the recommendation level of individual elementary flows can be different (lower) from the general level; this is documented as "Deviating recommendation" in the section "Characterisation factors" directly for each affected elementary flow.')
    meaning: MultiLangList = Field(default_factory=MultiLangList, alias='meaning', description='Specific meaning of the declared recommendation level of this LCIA method / methodology and the characterisation factors, as defined in the guidance document referenced in in the field "Compliance system"')

class LCIAMethodDataSetAdministrativeInformationDataEntryBy(TidasBaseModel):
    """Staff or entity, that documented the generated data set, entering the information into the database; plus administrative information linked to the data entry activity."""
    common_time_stamp: DateTime = Field(default=..., alias='common:timeStamp', description='Date and time stamp of data set generation, typically an automated entry ("last saved").')
    common_reference_to_data_set_format: GlobalReferenceType = Field(default=..., alias='common:referenceToDataSetFormat', description='"Source data set" of the used version of the ILCD format. If additional data format fields have been integrated into the data set file, using the "namespace" option, the used format namespace(s) are to be given. This is the case if the data sets carries additional information as specified by other, particular LCA formats, e.g. of other database networks or LCA softwares.')
    common_reference_to_converted_original_data_set_from: GlobalReferenceType | None = Field(default=None, alias='common:referenceToConvertedOriginalDataSetFrom', description='"Source data set" of the database or data set publication from which this data set has been obtained by conversion. This can cover e.g. conversion to a different format, applying a different nomenclature, mapping of flow names, conversion of units, etc. This may however not have changed or re-modeled the Inputs and Outputs, i.e. obtaining the same LCIA results. This entry is required for converted data sets stemming originally from other LCA databases (e.g. when re-publishing data from IISI, ILCD etc. databases). [Note: Identically re-published data sets are identied in the field "Unchanged re-publication of:" in the section "Publication and Ownership".]')
    common_reference_to_person_or_entity_entering_the_data: GlobalReferenceType | None = Field(default=None, alias='common:referenceToPersonOrEntityEnteringTheData', description='"Contact data set" of the responsible person or entity that has documented this data set, i.e. entered the data and the descriptive information.')
    recommendation_by: AdministrativeInformationDataEntryByRecommendationBy = Field(default=..., alias='recommendationBy')
    common_other: str | None = Field(default=None, alias='common:other')

class LCIAMethodDataSetAdministrativeInformationPublicationAndOwnership(TidasBaseModel):
    """Information related to publication and version management of the data set including copyright and access restrictions."""
    common_date_of_last_revision: DateTime = Field(default=..., alias='common:dateOfLastRevision', description='Date when the data set was revised for the last time, typically manually set.')
    common_data_set_version: str = Field(default=..., alias='common:dataSetVersion', description='Version number of data set. First two digits refer to major updates, the second two digits to minor revisions and error corrections etc. The third three digits are intended for automatic and internal counting of versions during data set development. Together with the data set\'s UUID, the "Data set version" uniquely identifies each data set.')
    common_reference_to_preceding_data_set_version: GlobalReferenceType | None = Field(default=None, alias='common:referenceToPrecedingDataSetVersion', description='Last preceding data set, which was replaced by this version. Either a URI of that data set (i.e. an internet address) or its UUID plus version number is given (or both).')
    common_permanent_data_set_uri: str | None = Field(default=None, alias='common:permanentDataSetURI', description="URI (i.e. an internet address) of the original of this data set. [Note: This equally globally unique identifier supports users and software tools to identify and retrieve the original version of a data set via the internet or to check for available updates. The URI must not represent an existing WWW address, but it should be unique and point to the data access point, e.g. by combining the data owner's www path with the data set's UUID, e.g. http://www.mycompany.com/lca/processes/50f12420-8855-12db-b606-0900210c9a66.]")
    common_workflow_and_publication_status: Literal['Working draft', 'Final draft for internal review', 'Final draft for external review', 'Data set finalised; unpublished', 'Under revision', 'Withdrawn', 'Data set finalised; subsystems published', 'Data set finalised; entirely published'] | None = Field(default=None, alias='common:workflowAndPublicationStatus', description='Workflow or publication status of data set. Details e.g. of foreseen publication dates should be provided on request by the "Data set owner".')
    common_reference_to_unchanged_republication: GlobalReferenceType | None = Field(default=None, alias='common:referenceToUnchangedRepublication', description='"Source data set" of the publication, in which this data set was published for the first time. [Note: This refers to exactly this data set as it is, without any format conversion, adjustments, flow name mapping, etc. In case this data set was modified/converted, the original source is documented in "Converted original data set from:" in section "Data entry by".]')
    common_reference_to_ownership_of_data_set: GlobalReferenceType = Field(default=..., alias='common:referenceToOwnershipOfDataSet', description='"Contact data set" of the person or entity who owns this data set. (Note: this is not necessarily the publisher of the data set.)')
    common_copyright: Literal['true', 'false'] | None = Field(default=None, alias='common:copyright', description='Indicates whether or not a copyright on the data set exists. Decided upon by the "Owner of data set". [Note: See also field "Access and use restrictions".]')
    common_access_restrictions: MultiLangList = Field(default_factory=MultiLangList, alias='common:accessRestrictions', description='Access restrictions / use conditions for this data set as free text or referring to e.g. license conditions. In case of no restrictions "None" is entered.')
    common_other: str | None = Field(default=None, alias='common:other')

class LciamethodsLCIAMethodDataSetAdministrativeInformation(TidasBaseModel):
    """Information required for data set management and administration."""
    common_commissioner_and_goal: LCIAMethodDataSetAdministrativeInformationCommonCommissionerAndGoal | None = Field(default=None, alias='common:commissionerAndGoal', description='Extract of the information items linked to goal and scope of LCIA method modeling.')
    data_generator: LCIAMethodDataSetAdministrativeInformationDataGenerator = Field(default=..., alias='dataGenerator', description='Expert(s), that compiled and modelled the data set as well as internal administrative information linked to the data generation activity.')
    data_entry_by: LCIAMethodDataSetAdministrativeInformationDataEntryBy = Field(default=..., alias='dataEntryBy', description='Staff or entity, that documented the generated data set, entering the information into the database; plus administrative information linked to the data entry activity.')
    publication_and_ownership: LCIAMethodDataSetAdministrativeInformationPublicationAndOwnership = Field(default=..., alias='publicationAndOwnership', description='Information related to publication and version management of the data set including copyright and access restrictions.')
    common_other: str | None = Field(default=None, alias='common:other')

class CharacterisationFactorsFactorOption0(TidasBaseModel):
    reference_to_flow_data_set: GlobalReferenceType = Field(default=..., alias='referenceToFlowDataSet', description='Reference to "UUID of flow" of "Flow data set" to link the particular impact factor in the "LCIA data set" to the respective "Flow data set". Please be aware, that for location-specific LCIA methods, there may be multiple references to the same Flow data set.')
    location: str | None = Field(default=None, alias='location', description='Location where exchange of elementary flow occurs. Used only for those LCIA methods, that make use of such information. This information refers to the entry within the same field in the "Process data set".')
    exchange_direction: Literal['Input', 'Output'] = Field(default=..., alias='exchangeDirection', description='Direction of exchange; this information refers to the entry within the same field in the "Process data set".')
    mean_value: Real = Field(default=..., alias='meanValue', description='Mean value of the impact characterisation factor for the exchange identified by the fields "Reference to flow data set", "Exchange direction" and "Location of direction". It is recommended to report only significant digits of the amount. ! If for an elementary flow its relevant contribution to this LCIA theme is known by state-of-the-art scientific knowledge, but no impact factor is provided in the LCIA method, the flow should nevertheless be referrenced and the mean value to be entered is "0"!')
    minimum_value: Real | None = Field(default=None, alias='minimumValue', description='Minimum value of the characterisation factor for the exchange in case uncertainty distribution is uniform or triangular.')
    maximum_value: Real | None = Field(default=None, alias='maximumValue', description='Maximum value of the characterisation factor for the exchange in case uncertainty distribution is uniform or triangular.')
    uncertainty_distribution_type: Literal['undefined', 'log-normal', 'normalisation', 'triangular', 'uniform'] | None = Field(default=None, alias='uncertaintyDistributionType', description='Defines the kind of uncertainty distribution that is valid for this particular object or parameter.')
    relative_standard_deviation95_in: Perc | None = Field(default=None, alias='relativeStandardDeviation95In', description='The resulting overall uncertainty of the calculated variable value considering uncertainty of measurements, modelling, appropriateness etc. [Notes: For log-normal distribution the square of the geometric standard deviation (SDg^2) is stated. Mean value times SDg^2 equals the 97.5% value (= Maximum value), Mean value divided by SDg^2 equals the 2.5% value (= Minimum value). For normal distribution the doubled standard deviation value (2*SD) is entered. Mean value plus 2*SD equals 97.5% value (= Maximum value), Mean value minus 2*SD equals 2.5% value (= Minimum value). This data field remains empty when uniform or triangular uncertainty distribution is applied.]')
    data_derivation_type_status: Literal['Measured', 'Calculated', 'Estimated', 'Unknown derivation', 'Missing important', 'Missing unimportant'] | None = Field(default=None, alias='dataDerivationTypeStatus', description='Identifies the way by which the individual Input / Output amount was derived (e.g. measured, estimated etc.), respectively the status and relevancy of missing data.')
    deviating_recommendation: Literal['Level I', 'Level II', 'Level III', 'Interim', 'Not recommended'] = Field(default=..., alias='deviatingRecommendation', description='Deviating (downgraded) recommendation level for this exchange, in reference to the recommendation level of the LCIA method data set as a whole (see field "Official recommendation of data set by governmental body:").')
    reference_to_data_source: GlobalReferenceType | None = Field(default=None, alias='referenceToDataSource', description='Reference to "UUID of source"(s) in the "Source data set" of data source(s) used for modelling the value of this single LCIA factor e.g. a specific paper, questionnaire, monography etc. If, as typical, more than one data source was used, more than one source can be referenced.')
    general_comment: MultiLangList = Field(default_factory=MultiLangList, alias='generalComment', description='General information about the data set, including e.g. general (internal, not reviewed) quality statements as well as information sources used. (Note: Please also check the more specific fields e.g. on "Intended application", "Advice on data set use" and the fields in the "Modelling and validation" section to avoid overlapping entries.)')
    common_other: str | None = Field(default=None, alias='common:other')

class FactorItemReferenceToDataSource(TidasBaseModel):
    reference_to_data_source: GlobalReferenceType | None = Field(default=None, alias='referenceToDataSource', description='Reference to "UUID of source"(s) in the "Source data set" of data source(s) used for modelling the value of this single LCIA factor e.g. a specific paper, questionnaire, monography etc. If, as typical, more than one data source was used, more than one source can be referenced.')

class CharacterisationFactorsFactorItem(TidasBaseModel):
    reference_to_flow_data_set: GlobalReferenceType = Field(default=..., alias='referenceToFlowDataSet', description='Reference to "UUID of flow" of "Flow data set" to link the particular impact factor in the "LCIA data set" to the respective "Flow data set". Please be aware, that for location-specific LCIA methods, there may be multiple references to the same Flow data set.')
    location: str | None = Field(default=None, alias='location', description='Location where exchange of elementary flow occurs. Used only for those LCIA methods, that make use of such information. This information refers to the entry within the same field in the "Process data set".')
    exchange_direction: Literal['Input', 'Output'] = Field(default=..., alias='exchangeDirection', description='Direction of exchange; this information refers to the entry within the same field in the "Process data set".')
    mean_value: Real = Field(default=..., alias='meanValue', description='Mean value of the impact characterisation factor for the exchange identified by the fields "Reference to flow data set", "Exchange direction" and "Location of direction". It is recommended to report only significant digits of the amount. ! If for an elementary flow its relevant contribution to this LCIA theme is known by state-of-the-art scientific knowledge, but no impact factor is provided in the LCIA method, the flow should nevertheless be referrenced and the mean value to be entered is "0"!')
    minimum_value: Real | None = Field(default=None, alias='minimumValue', description='Minimum value of the characterisation factor for the exchange in case uncertainty distribution is uniform or triangular.')
    maximum_value: Real | None = Field(default=None, alias='maximumValue', description='Maximum value of the characterisation factor for the exchange in case uncertainty distribution is uniform or triangular.')
    uncertainty_type: Literal['undefined', 'log-normal', 'normalisation', 'triangular', 'uniform'] | None = Field(default=None, alias='uncertaintyType', description='Defines the kind of uncertainty distribution that is valid for this particular object or parameter.')
    relative_standard_deviation95_in: Perc | None = Field(default=None, alias='relativeStandardDeviation95In', description='The resulting overall uncertainty of the calculated variable value considering uncertainty of measurements, modelling, appropriateness etc. [Notes: For log-normal distribution the square of the geometric standard deviation (SDg^2) is stated. Mean value times SDg^2 equals the 97.5% value (= Maximum value), Mean value divided by SDg^2 equals the 2.5% value (= Minimum value). For normal distribution the doubled standard deviation value (2*SD) is entered. Mean value plus 2*SD equals 97.5% value (= Maximum value), Mean value minus 2*SD equals 2.5% value (= Minimum value). This data field remains empty when uniform or triangular uncertainty distribution is applied.]')
    data_derivation_type_status: Literal['Measured', 'Calculated', 'Estimated', 'Unknown derivation', 'Missing important', 'Missing unimportant'] | None = Field(default=None, alias='dataDerivationTypeStatus', description='Identifies the way by which the individual Input / Output amount was derived (e.g. measured, estimated etc.), respectively the status and relevancy of missing data.')
    deviating_recommendation: Literal['Level I', 'Level II', 'Level III', 'Interim', 'Not recommended'] = Field(default=..., alias='deviatingRecommendation', description='Deviating (downgraded) recommendation level for this exchange, in reference to the recommendation level of the LCIA method data set as a whole (see field "Official recommendation of data set by governmental body:").')
    reference_to_data_source: FactorItemReferenceToDataSource | None = Field(default=None, alias='referenceToDataSource')
    general_comment: MultiLangList = Field(default_factory=MultiLangList, alias='generalComment', description='General information about the data set, including e.g. general (internal, not reviewed) quality statements as well as information sources used. (Note: Please also check the more specific fields e.g. on "Intended application", "Advice on data set use" and the fields in the "Modelling and validation" section to avoid overlapping entries.)')

class LciamethodsLCIAMethodDataSetCharacterisationFactors(TidasBaseModel):
    """Flow / Exchanges list with corresponding impact factors according to the respective LCIA method."""
    factor: CharacterisationFactorsFactorOption0 | list[CharacterisationFactorsFactorItem] = Field(default=..., alias='factor')
    common_other: str | None = Field(default=None, alias='common:other')

class LciamethodsLCIAMethodDataSet(TidasBaseModel):
    xmlns: Literal['http://lca.jrc.it/ILCD/LCIAMethod'] | None = Field(default=None, alias='@xmlns')
    xmlns_common: Literal['http://lca.jrc.it/ILCD/Common'] | None = Field(default=None, alias='@xmlns:common')
    xmlns_xsi: Literal['http://www.w3.org/2001/XMLSchema-instance'] | None = Field(default=None, alias='@xmlns:xsi')
    version: Literal['1.1'] | None = Field(default=None, alias='@version')
    xsi_schema_location: Literal['http://lca.jrc.it/ILCD/LCIAMethod ../../schemas/ILCD_LCIAMethodDataSet.xsd'] | None = Field(default=None, alias='@xsi:schemaLocation')
    lcia_method_information: LciamethodsLCIAMethodDataSetLCIAMethodInformation = Field(default=..., alias='LCIAMethodInformation')
    modelling_and_validation: LciamethodsLCIAMethodDataSetModellingAndValidation = Field(default=..., alias='modellingAndValidation', description='Covers the five sub-sections 1) LCIA method, normalisation, weighting 2) Data sources 3) Completeness, 4) Validation, and 5) Compliance declarations.')
    administrative_information: LciamethodsLCIAMethodDataSetAdministrativeInformation = Field(default=..., alias='administrativeInformation', description='Information required for data set management and administration.')
    characterisation_factors: LciamethodsLCIAMethodDataSetCharacterisationFactors = Field(default=..., alias='characterisationFactors', description='Flow / Exchanges list with corresponding impact factors according to the respective LCIA method.')
    common_other: str | None = Field(default=None, alias='common:other')

class Lciamethods(TidasBaseModel):
    lcia_method_data_set: LciamethodsLCIAMethodDataSet = Field(default=..., alias='LCIAMethodDataSet')
