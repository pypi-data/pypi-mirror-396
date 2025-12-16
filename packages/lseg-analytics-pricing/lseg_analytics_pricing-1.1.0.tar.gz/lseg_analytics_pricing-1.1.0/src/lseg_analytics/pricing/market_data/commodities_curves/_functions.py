import copy
import datetime
from typing import Any, Dict, Iterator, List, Literal, Optional, Union

from lseg_analytics.core.common._resource_base import (
    AsyncPollingResponse,
    AsyncRequestResponse,
    ResourceBase,
)
from lseg_analytics.core.exceptions import (
    LibraryException,
    ResourceNotFound,
    check_async_polling_response,
    check_async_request_response,
    check_exception_and_raise,
    check_id,
)

from lseg_analytics.pricing._basic_client.models import (
    CalendarAdjustmentEnum,
    CalibrationMethodEnum,
    CommoditiesCalendarSpreadFields,
    CommoditiesCalendarSpreadFieldsDescription,
    CommoditiesCalendarSpreadFieldsFormulaDescription,
    CommoditiesCalendarSpreadFieldsOutput,
    CommoditiesCalendarSpreadFormulaFields,
    CommoditiesCalendarSpreadFormulaParameter,
    CommoditiesCalendarSpreadFormulaParameterDescription,
    CommoditiesCalendarSpreadFormulaParameterOutput,
    CommoditiesCalendarSpreadInstrument,
    CommoditiesCalendarSpreadInstrumentDefinition,
    CommoditiesCalendarSpreadInstrumentDescription,
    CommoditiesCalendarSpreadInstrumentOutput,
    CommoditiesChainSource,
    CommoditiesCurveConstituents,
    CommoditiesCurveConstituentsDescription,
    CommoditiesCurveConstituentsOutput,
    CommoditiesCurveCreateRequest,
    CommoditiesCurveDefinition,
    CommoditiesCurveDefinitionBase,
    CommoditiesCurveDefinitionDescription,
    CommoditiesCurveDefinitionOutput,
    CommoditiesCurveDefinitionRequest,
    CommoditiesCurveDefinitionRequestKeys,
    CommoditiesCurveDefinitionResponse,
    CommoditiesCurveDefinitionsResponse,
    CommoditiesCurveDefinitionsResponseItems,
    CommoditiesCurveParameters,
    CommoditiesCurveParametersDescription,
    CommoditiesCurvePoint,
    CommoditiesCurvePointsInstrument,
    CommoditiesCurveReferenceUpdateDefinition,
    CommoditiesCurveRequestItem,
    CommoditiesCurveResponse,
    CommoditiesCurveSegmentReferenceCurve,
    CommoditiesCurvesReferenceResponseItem,
    CommoditiesCurvesResponse,
    CommoditiesCurvesResponseItem,
    CommoditiesFieldsFormulaOutput,
    CommoditiesFuturesFields,
    CommoditiesFuturesFieldsDescription,
    CommoditiesFuturesFieldsFormulaDescription,
    CommoditiesFuturesFieldsOutput,
    CommoditiesFuturesFormulaFields,
    CommoditiesFuturesFormulaParameter,
    CommoditiesFuturesFormulaParameterDescription,
    CommoditiesFuturesFormulaParameterOutput,
    CommoditiesFuturesInstrument,
    CommoditiesFuturesInstrumentDefinition,
    CommoditiesFuturesInstrumentDescription,
    CommoditiesFuturesInstrumentOutput,
    CommoditiesInstrumentDefinitionDescription,
    CommoditiesInstrumentsOutput,
    CommoditiesInstrumentsRequest,
    CommoditiesInstrumentsSegment,
    CommoditiesInstrumentsSegmentCreate,
    CommoditiesInterestRateCurve,
    CommoditiesInterestRateCurveDefinition,
    CommoditiesInterProductSpreadFields,
    CommoditiesInterProductSpreadFieldsDescription,
    CommoditiesInterProductSpreadFieldsFormulaDescription,
    CommoditiesInterProductSpreadFieldsFormulaOutput,
    CommoditiesInterProductSpreadFieldsOutput,
    CommoditiesInterProductSpreadFormulaFields,
    CommoditiesInterProductSpreadFormulaParameter,
    CommoditiesInterProductSpreadFormulaParameterDescription,
    CommoditiesInterProductSpreadFormulaParameterOutput,
    CommoditiesInterProductSpreadInstrument,
    CommoditiesInterProductSpreadInstrumentDefinition,
    CommoditiesInterProductSpreadInstrumentDefinitionDescription,
    CommoditiesInterProductSpreadInstrumentDescription,
    CommoditiesInterProductSpreadInstrumentsOutput,
    CommoditiesReferenceCurve,
    CompoundingTypeEnum,
    ConstantForwardRateParameters,
    ConstituentOverrideModeEnum,
    ConstituentsFiltersDescription,
    CurveInfo,
    CurvesAndSurfacesConvexityAdjustment,
    CurvesAndSurfacesInterestCalculationMethodEnum,
    CurvesAndSurfacesPriceSideEnum,
    CurvesAndSurfacesUnitEnum,
    CurvesAndSurfacesValuationTime,
    CurveTenorsFrequencyEnum,
    ExtrapolationModeEnum,
    FieldDateOutput,
    FieldDateValue,
    FieldDescription,
    FieldDoubleOutput,
    FieldDoubleValue,
    FieldFormulaDescription,
    FieldFormulaDoubleOutput,
    FieldFormulaDoubleValue,
    FieldTimeOutput,
    FieldTimeValue,
    InstrumentTypeEnum,
    InterestRateCurveParameters,
    InterpolationModeEnum,
    MainConstituentAssetClassEnum,
    MarketDataAccessDeniedFallbackEnum,
    MarketDataLookBack,
    MarketDataTime,
    ProductEnum,
    RiskTypeEnum,
    Seasonality,
    SeasonalityCurvePoint,
    SeasonalityDescription,
    SectorEnum,
    Step,
    StepModeEnum,
    SubSectorEnum,
    Turn,
    ZcCurve,
    ZcCurveInstrument,
    ZcCurveParameters,
    ZcCurvePoint,
)
from lseg_analytics.pricing._client.client import Client

from ._logger import logger

__all__ = [
    "CalendarAdjustmentEnum",
    "CalibrationMethodEnum",
    "CommoditiesCalendarSpreadFields",
    "CommoditiesCalendarSpreadFieldsDescription",
    "CommoditiesCalendarSpreadFieldsFormulaDescription",
    "CommoditiesCalendarSpreadFieldsOutput",
    "CommoditiesCalendarSpreadFormulaFields",
    "CommoditiesCalendarSpreadFormulaParameter",
    "CommoditiesCalendarSpreadFormulaParameterDescription",
    "CommoditiesCalendarSpreadFormulaParameterOutput",
    "CommoditiesCalendarSpreadInstrument",
    "CommoditiesCalendarSpreadInstrumentDefinition",
    "CommoditiesCalendarSpreadInstrumentDescription",
    "CommoditiesCalendarSpreadInstrumentOutput",
    "CommoditiesChainSource",
    "CommoditiesCurveConstituents",
    "CommoditiesCurveConstituentsDescription",
    "CommoditiesCurveConstituentsOutput",
    "CommoditiesCurveDefinition",
    "CommoditiesCurveDefinitionBase",
    "CommoditiesCurveDefinitionDescription",
    "CommoditiesCurveDefinitionOutput",
    "CommoditiesCurveDefinitionRequest",
    "CommoditiesCurveDefinitionRequestKeys",
    "CommoditiesCurveDefinitionResponse",
    "CommoditiesCurveDefinitionsResponse",
    "CommoditiesCurveDefinitionsResponseItems",
    "CommoditiesCurveParameters",
    "CommoditiesCurveParametersDescription",
    "CommoditiesCurvePoint",
    "CommoditiesCurvePointsInstrument",
    "CommoditiesCurveReferenceUpdateDefinition",
    "CommoditiesCurveRequestItem",
    "CommoditiesCurveResponse",
    "CommoditiesCurveSegmentReferenceCurve",
    "CommoditiesCurvesReferenceResponseItem",
    "CommoditiesCurvesResponse",
    "CommoditiesCurvesResponseItem",
    "CommoditiesFieldsFormulaOutput",
    "CommoditiesFuturesFields",
    "CommoditiesFuturesFieldsDescription",
    "CommoditiesFuturesFieldsFormulaDescription",
    "CommoditiesFuturesFieldsOutput",
    "CommoditiesFuturesFormulaFields",
    "CommoditiesFuturesFormulaParameter",
    "CommoditiesFuturesFormulaParameterDescription",
    "CommoditiesFuturesFormulaParameterOutput",
    "CommoditiesFuturesInstrument",
    "CommoditiesFuturesInstrumentDefinition",
    "CommoditiesFuturesInstrumentDescription",
    "CommoditiesFuturesInstrumentOutput",
    "CommoditiesInstrumentDefinitionDescription",
    "CommoditiesInstrumentsOutput",
    "CommoditiesInstrumentsRequest",
    "CommoditiesInstrumentsSegment",
    "CommoditiesInstrumentsSegmentCreate",
    "CommoditiesInterProductSpreadFields",
    "CommoditiesInterProductSpreadFieldsDescription",
    "CommoditiesInterProductSpreadFieldsFormulaDescription",
    "CommoditiesInterProductSpreadFieldsFormulaOutput",
    "CommoditiesInterProductSpreadFieldsOutput",
    "CommoditiesInterProductSpreadFormulaFields",
    "CommoditiesInterProductSpreadFormulaParameter",
    "CommoditiesInterProductSpreadFormulaParameterDescription",
    "CommoditiesInterProductSpreadFormulaParameterOutput",
    "CommoditiesInterProductSpreadInstrument",
    "CommoditiesInterProductSpreadInstrumentDefinition",
    "CommoditiesInterProductSpreadInstrumentDefinitionDescription",
    "CommoditiesInterProductSpreadInstrumentDescription",
    "CommoditiesInterProductSpreadInstrumentsOutput",
    "CommoditiesInterestRateCurve",
    "CommoditiesInterestRateCurveDefinition",
    "CommoditiesReferenceCurve",
    "CompoundingTypeEnum",
    "ConstantForwardRateParameters",
    "ConstituentOverrideModeEnum",
    "ConstituentsFiltersDescription",
    "CurveInfo",
    "CurveTenorsFrequencyEnum",
    "CurvesAndSurfacesConvexityAdjustment",
    "CurvesAndSurfacesInterestCalculationMethodEnum",
    "CurvesAndSurfacesPriceSideEnum",
    "CurvesAndSurfacesUnitEnum",
    "CurvesAndSurfacesValuationTime",
    "ExtrapolationModeEnum",
    "FieldDateOutput",
    "FieldDateValue",
    "FieldDescription",
    "FieldDoubleOutput",
    "FieldDoubleValue",
    "FieldFormulaDescription",
    "FieldFormulaDoubleOutput",
    "FieldFormulaDoubleValue",
    "FieldTimeOutput",
    "FieldTimeValue",
    "InstrumentTypeEnum",
    "InterestRateCurveParameters",
    "InterpolationModeEnum",
    "MainConstituentAssetClassEnum",
    "MarketDataAccessDeniedFallbackEnum",
    "MarketDataLookBack",
    "MarketDataTime",
    "ProductEnum",
    "RiskTypeEnum",
    "Seasonality",
    "SeasonalityCurvePoint",
    "SeasonalityDescription",
    "SectorEnum",
    "Step",
    "StepModeEnum",
    "SubSectorEnum",
    "Turn",
    "ZcCurve",
    "ZcCurveInstrument",
    "ZcCurveParameters",
    "ZcCurvePoint",
    "calculate",
    "calculate_by_id",
    "create",
    "delete",
    "overwrite",
    "read",
    "search",
]


def calculate(
    *,
    universe: Optional[List[CommoditiesCurveRequestItem]] = None,
    fields: Optional[str] = None,
) -> CommoditiesCurvesResponse:
    """
    Generates the curves for the definitions provided

    Parameters
    ----------
    universe : List[CommoditiesCurveRequestItem], optional

    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    CommoditiesCurvesResponse
        CommoditiesCurvesResponse

    Examples
    --------
    >>> print("Step 0: Discovering Available Curve Definitions...")
    >>> # Create a search filter to find specific commodity curves
    >>> # We can filter by sector, product, sub_sector, underlying_code, or source
    >>>
    >>> search_filter = cc.CommoditiesCurveDefinitionRequest(
    >>>     #sector=cc.SectorEnum.AGRICULTURE,              # Filter by commodity sector
    >>>     # sub_sector=cc.SubSectorEnum.SOFTS,            # Filter by sub-sector (soft commodities)
    >>>     # product=cc.ProductEnum.COCOA                     # Search specifically for cocoa curves
    >>>     underlying_code="NG"  #CC                        # Alternative: filter by underlying symbol
    >>> )
    >>>
    >>> # Execute the search to find matching curve definitions
    >>> search_results = cc.search(universe=[search_filter])
    >>>
    >>> # ========== Parse and display the search results ===========
    >>>
    >>> try:
    >>>     curve_definitions = search_results['data'][0]['curveDefinitions']
    >>>     num_curves = len(curve_definitions)
    >>>     print(f"   - Found {num_curves} curve definition(s) for the specified filter")
    >>>
    >>>     if num_curves > 0:
    >>>         # Convert to DataFrame for easier analysis
    >>>         curve_definitions_df = pd.DataFrame(curve_definitions)
    >>>
    >>> except (KeyError, IndexError) as e:
    >>>     print(f"   !!! Curves not found or unexpected response: {search_results}")
    >>>     curve_definitions_df = pd.DataFrame()
    >>>
    >>> print("Discovered Curve Definitions:")
    >>> print("=" * 50)
    >>>
    >>> if not curve_definitions_df.empty:
    >>>     display(curve_definitions_df)
    >>> else:
    >>>     print("   !!! No curve definitions available to display.")
    Step 0: Discovering Available Curve Definitions...
       - Found 1 curve definition(s) for the specified filter
    Discovered Curve Definitions:
    ==================================================


    >>> print("Step 1: Creating Curve Definition...")
    >>> # Define which commodity curve to calculate using proper curve definition selection from Step 0
    >>> # Specify tenor points or tenor frequency as needed
    >>>
    >>> selected_curve = curve_definitions_df.iloc[0]
    >>>
    >>> curve_definition = cc.CommoditiesCurveDefinitionRequestKeys(
    >>>     name=selected_curve['name'],                                    # Curve identifier name
    >>>     #curve_tenors=["1M", "3M", "6M", "1Y", "2Y"],                   # Curve tenor points
    >>>     curve_tenors_frequency=cc.CurveTenorsFrequencyEnum.MONTHLY      # Tenor frequency, output depends on curve constituents frequency
    >>> )
    >>>
    >>> print(f"   - Curve Name: {selected_curve['name']}")
    >>> print(f"   - Sector: {selected_curve['sector']}")
    >>> print(f"   - Product: {selected_curve['product']}")
    >>> print(f"   - Underlying Code: {selected_curve['underlyingCode']}")
    >>> print(f"   - Definition created successfully")
    Step 1: Creating Curve Definition...
       - Curve Name: NYM NG Natgas Future
       - Sector: Energy
       - Product: NaturalGasLiquids
       - Underlying Code: NG
       - Definition created successfully


    >>> print("Step 2.1: Basic Curve Parameters...")
    >>> # Configure the core parameters needed for commodity curve calculation
    >>> # These settings control how the curve is calculated and how missing data is handled
    >>>
    >>> curve_parameters = cc.CommoditiesCurveParameters(
    >>>     valuation_date=dt.date.today(),                     # Date for curve calculation
    >>>     #conversion_factor=1.0,                              # Price scaling factor, optional
    >>>     #year_basis=365,                                     # Day count convention, optional
    >>>     market_data_access_denied_fallback="ReturnError",    # How to handle missing data
    >>>     use_delayed_data_if_denied=True                       # Whether to use delayed data if access is denied
    >>>
    >>> )
    >>>
    >>> print(f"   - Valuation Date: {curve_parameters.valuation_date}")
    >>> print(f"   - Missing Data Policy: {curve_parameters.market_data_access_denied_fallback}")
    >>> print(f"   - Basic parameters configured successfully")
    Step 2.1: Basic Curve Parameters...
       - Valuation Date: 2025-12-03
       - Missing Data Policy: MarketDataAccessDeniedFallbackEnum.RETURN_ERROR
       - Basic parameters configured successfully


    >>> print("Step 2.2: Configure Constituents (Optional)...")
    >>> # Constituents define which market instruments contribute to the curve
    >>> # For most basic curves, this can be left as default (empty)
    >>>
    >>> # Configure user-defined constituents with specific Natural Gas futures (calendar spreads, inter-product spreads are optional)
    >>> ng_futures = []
    >>> ric_codes = ['NGF26', 'NGF27', 'NGF28']
    >>>
    >>> for ric in ric_codes:
    >>>     # Create futures instrument with RIC code
    >>>     futures_instrument = cc.CommoditiesFuturesInstrument()
    >>>     instrument_def = cc.CommoditiesFuturesInstrumentDefinition()
    >>>     instrument_def.instrument_code = ric
    >>>     futures_instrument.instrument_definition = instrument_def
    >>>     ng_futures.append(futures_instrument)
    >>>
    >>> # Create instruments request and constituents
    >>> instruments_request = cc.CommoditiesInstrumentsRequest(
    >>>     futures=ng_futures,
    >>>     calendar_spreads=[],
    >>>     inter_product_spreads=[]
    >>> )
    >>>
    >>> constituents = cc.CommoditiesCurveConstituents(
    >>>     commodities_instruments={"USD": instruments_request}
    >>> )
    >>>
    >>> print(f"   - Constituents configured with {len(ng_futures)} Natural Gas futures")
    >>> print(f"   - RIC codes: {ric_codes}")
    >>> print(f"   - Constituents created successfully")
    Step 2.2: Configure Constituents (Optional)...
       - Constituents configured with 3 Natural Gas futures
       - RIC codes: ['NGF26', 'NGF27', 'NGF28']
       - Constituents created successfully


    >>> print("Step 2.3: Seasonality (Optional)...")
    >>> # Seasonality can be customized for commodities with seasonal patterns. Examples: Natural gas (heating season), Agriculture (harvest cycles)
    >>>
    >>> # Define custom seasonal patterns
    >>> seasonal_points = [
    >>>     cc.SeasonalityCurvePoint(period=1, seasonality_factor=-0.0119),
    >>>     cc.SeasonalityCurvePoint(period=2, seasonality_factor=0.011),
    >>>     cc.SeasonalityCurvePoint(period=3, seasonality_factor=0.032),
    >>>     cc.SeasonalityCurvePoint(period=4, seasonality_factor=0.05),
    >>>     cc.SeasonalityCurvePoint(period=5, seasonality_factor=0.066),
    >>>     cc.SeasonalityCurvePoint(period=6, seasonality_factor=0.077),
    >>>     cc.SeasonalityCurvePoint(period=7, seasonality_factor=0.087),
    >>>     cc.SeasonalityCurvePoint(period=8, seasonality_factor=0.097),
    >>>     cc.SeasonalityCurvePoint(period=9, seasonality_factor=-0.166),
    >>>     cc.SeasonalityCurvePoint(period=10, seasonality_factor=-0.124),
    >>>     cc.SeasonalityCurvePoint(period=11, seasonality_factor=-0.079),
    >>>     cc.SeasonalityCurvePoint(period=12, seasonality_factor=-0.040)
    >>> ]
    >>>
    >>> seasonality_config = cc.Seasonality(
    >>>     apply_seasonality=True,                                         # Whether to apply seasonality adjustments
    >>>     #seasonality_name=selected_curve['underlyingCode'],              # Precomputed seasonality curve name (matching underlying code)
    >>>     seasonality_curve=seasonal_points                              # Custom seasonality curve points
    >>> )
    >>>
    >>> curve_parameters.seasonality = seasonality_config
    >>>
    >>> print(f"   - Seasonality: {seasonality_config.apply_seasonality}")
    Step 2.3: Seasonality (Optional)...
       - Seasonality: True


    >>> #print("Step 3: Create Curve Request Item...")
    >>> # Combine all configuration elements into the main request object
    >>> request_item = cc.CommoditiesCurveRequestItem(
    >>>     curve_definition=curve_definition,                                                 # Curve identification from Step 1
    >>>     curve_parameters=curve_parameters,                                                 # Calculation parameters from Step 2
    >>>     #constituents=constituents,                                                        # User defined constituents list
    >>>     curve_tag="Demo_Curve"                                                             # User-defined identifier
    >>>
    >>> )
    >>>
    >>> print(f"   - Request Item created successfully")
    >>> print(f"   - Curve Tag: {request_item.curve_tag}")
    >>> print(f"   - Configuration complete - ready for calculation")
       - Request Item created successfully
       - Curve Tag: Demo_Curve
       - Configuration complete - ready for calculation


    >>> print("Step 4: Execute Commodity Curve Calculation...")
    >>> # Calculate the curve using the configured request item
    >>>
    >>> try:
    >>>     response = cc.calculate(
    >>>         universe=[request_item],
    >>>         fields = "Constituents"
    >>>         )
    >>>     print(f"   - Calculation completed successfully!")
    >>>
    >>>     # Extract curve data from response
    >>>     curve_data = response['data'][0]
    >>>     curve_points = curve_data['curvePoints']
    >>>
    >>>     print(f"   - Curve Tag: {curve_data['curveTag']}")
    >>>     print(f"   - Number of curve points: {len(curve_points)}")
    >>>     print(f"   - Available data: {list(curve_data.keys())}")
    >>>
    >>> except Exception as e:
    >>>     print(f"   !!! Calculation failed: {str(e)}")
    >>>     print(f"   !!! Check your curve definition and parameters")
    >>>     raise
    Step 4: Execute Commodity Curve Calculation...
       - Calculation completed successfully!
       - Curve Tag: Demo_Curve
       - Number of curve points: 157
       - Available data: ['constituents', 'curveDefinition', 'curveParameters', 'curvePoints', 'curveTag', 'discountCurves']

    """

    try:
        logger.info("Calling calculate")

        response = Client().commodities_curves.calculate(fields=fields, universe=universe)

        output = response
        logger.info("Called calculate")

        return output
    except Exception as err:
        logger.error("Error calculate.")
        check_exception_and_raise(err, logger)


def calculate_by_id(
    *,
    curve_id: str,
    valuation_date: Optional[Union[str, datetime.date]] = None,
    fields: Optional[str] = None,
) -> CommoditiesCurvesResponseItem:
    """
    Generates the curve for the given curve id

    Parameters
    ----------
    valuation_date : Union[str, datetime.date], optional
        The date on which the curve is constructed. The value is expressed in ISO 8601 format: YYYY-MM-DD (e.g., '2023-01-01').
        The valuation date should not be in the future.
    curve_id : str
        The curve identifier.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    CommoditiesCurvesResponseItem
        CommoditiesCurvesResponseItem

    Examples
    --------


    """

    try:
        logger.info("Calling calculate_by_id")

        response = Client().commodities_curves.calculate_by_id(
            curve_id=curve_id, fields=fields, valuation_date=valuation_date
        )

        output = response
        logger.info("Called calculate_by_id")

        return output
    except Exception as err:
        logger.error("Error calculate_by_id.")
        check_exception_and_raise(err, logger)


def create(
    *,
    curve_definition: Optional[CommoditiesCurveDefinitionDescription] = None,
    segments: Optional[List[CommoditiesInstrumentsSegmentCreate]] = None,
) -> CommoditiesCurveResponse:
    """
    Creates a curve definition

    Parameters
    ----------
    curve_definition : CommoditiesCurveDefinitionDescription, optional
        CommoditiesCurveDefinitionDescription
    segments : List[CommoditiesInstrumentsSegmentCreate], optional
        Get segments

    Returns
    --------
    CommoditiesCurveResponse


    Examples
    --------


    """

    try:
        logger.info("Calling create")

        response = Client().commodities_curves.create(
            body=CommoditiesCurveCreateRequest(curve_definition=curve_definition, segments=segments)
        )

        output = response
        logger.info("Called create")

        return output
    except Exception as err:
        logger.error("Error create.")
        check_exception_and_raise(err, logger)


def delete(*, curve_id: str) -> bool:
    """
    Delete a CommoditiesCurveDefinition that exists in the platform. The CommoditiesCurveDefinition can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    curve_id : str
        The curve identifier.

    Returns
    --------
    bool
        A ResultAsync object specifying a status message or error response

    Examples
    --------


    """

    try:
        logger.info(f"Deleting CommoditiesCurvesResource with id: {curve_id}")
        Client().commodities_curves.delete(curve_id=curve_id)
        logger.info(f"Deleted CommoditiesCurvesResource with id: {curve_id}")

        return True
    except Exception as err:
        logger.error("Error delete.")
        check_exception_and_raise(err, logger)


def overwrite(
    *,
    curve_id: str,
    curve_definition: Optional[CommoditiesCurveDefinitionDescription] = None,
    segments: Optional[List[CommoditiesInstrumentsSegmentCreate]] = None,
) -> CommoditiesCurveResponse:
    """
    Overwrite a CommoditiesCurveDefinition that exists in the platform. The CommoditiesCurveDefinition can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    curve_definition : CommoditiesCurveDefinitionDescription, optional
        CommoditiesCurveDefinitionDescription
    segments : List[CommoditiesInstrumentsSegmentCreate], optional
        Get segments
    curve_id : str
        The curve identifier.

    Returns
    --------
    CommoditiesCurveResponse


    Examples
    --------


    """

    try:
        logger.info("Calling overwrite")

        response = Client().commodities_curves.overwrite(
            body=CommoditiesCurveCreateRequest(curve_definition=curve_definition, segments=segments),
            curve_id=curve_id,
        )

        output = response
        logger.info("Called overwrite")

        return output
    except Exception as err:
        logger.error("Error overwrite.")
        check_exception_and_raise(err, logger)


def read(*, curve_id: str, fields: Optional[str] = None) -> CommoditiesCurveResponse:
    """
    Access a CommoditiesCurveDefinition existing in the platform (read). The CommoditiesCurveDefinition can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    curve_id : str
        The curve identifier.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    CommoditiesCurveResponse


    Examples
    --------


    """

    try:
        logger.info("Calling read")

        response = Client().commodities_curves.read(curve_id=curve_id, fields=fields)

        output = response
        logger.info("Called read")

        return output
    except Exception as err:
        logger.error("Error read.")
        check_exception_and_raise(err, logger)


def search(
    *,
    universe: Optional[List[CommoditiesCurveDefinitionRequest]] = None,
    fields: Optional[str] = None,
) -> CommoditiesCurveDefinitionsResponse:
    """
    Returns the definitions of the available curves for the filters selected

    Parameters
    ----------
    universe : List[CommoditiesCurveDefinitionRequest], optional
        Get universe
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    CommoditiesCurveDefinitionsResponse
        CommoditiesCurveDefinitionsResponse

    Examples
    --------


    """

    try:
        logger.info("Calling search")

        response = Client().commodities_curves.search(fields=fields, universe=universe)

        output = response
        logger.info("Called search")

        return output
    except Exception as err:
        logger.error("Error search.")
        check_exception_and_raise(err, logger)
