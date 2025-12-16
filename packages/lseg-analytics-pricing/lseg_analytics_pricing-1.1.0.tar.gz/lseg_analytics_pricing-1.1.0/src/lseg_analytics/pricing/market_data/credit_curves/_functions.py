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
    BasisSplineSmoothModelEnum,
    BidAskFieldsDescription,
    BidAskFieldsFormulaDescription,
    BidAskFieldsFormulaOutput,
    BidAskFieldsOutput,
    BidAskFormulaFields,
    BondInstrument,
    BondInstrumentDefinition,
    BondInstrumentDescription,
    BondInstrumentOutput,
    BusinessSectorEnum,
    CalendarAdjustmentEnum,
    CalibrationModelEnum,
    CalibrationParameters,
    CategoryEnum,
    CompoundingTypeEnum,
    CreditConstituents,
    CreditConstituentsDescription,
    CreditConstituentsOutput,
    CreditCurveCreateDefinition,
    CreditCurveCreateRequest,
    CreditCurveDefinition,
    CreditCurveDefinitionDescription,
    CreditCurveDefinitionOutput,
    CreditCurveDefinitionResponse,
    CreditCurveDefinitionResponseItem,
    CreditCurveDefinitionsResponse,
    CreditCurveDefinitionsResponseItems,
    CreditCurveInstrumentsSegment,
    CreditCurveParameters,
    CreditCurveParametersDescription,
    CreditCurvePoint,
    CreditCurveRequestItem,
    CreditCurveResponse,
    CreditCurveSearchDefinition,
    CreditCurvesResponse,
    CreditCurvesResponseItem,
    CreditCurveTypeEnum,
    CreditDefaultSwapInstrument,
    CreditDefaultSwapInstrumentDefinition,
    CreditDefaultSwapInstrumentOutput,
    CreditDefaultSwapsInstrumentDescription,
    CreditInstruments,
    CreditInstrumentsOutput,
    CrossCurrencyInstrument,
    CrossCurrencyInstrumentDefinition,
    CrossCurrencyInstrumentDefinitionOutput,
    CrossCurrencyInstrumentOutput,
    CrossCurrencyInstruments,
    CrossCurrencyInstrumentsOutput,
    CrossCurrencyInstrumentsSources,
    CurveInfo,
    CurvesAndSurfacesBidAskFields,
    CurvesAndSurfacesInstrument,
    CurvesAndSurfacesInterestCalculationMethodEnum,
    CurvesAndSurfacesPriceSideEnum,
    CurvesAndSurfacesQuotationModeEnum,
    CurvesAndSurfacesSeniorityEnum,
    CurveSubTypeEnum,
    DepositInstrumentOutput,
    EconomicSectorEnum,
    ErrorDetails,
    ErrorResponse,
    ExtrapolationModeEnum,
    ExtrapolationTypeEnum,
    FieldDescription,
    FieldDoubleOutput,
    FieldDoubleValue,
    FieldFormulaDescription,
    FieldFormulaDoubleOutput,
    FieldFormulaDoubleValue,
    FormulaParameter,
    FormulaParameterDescription,
    FormulaParameterOutput,
    FxForwardInstrument,
    FxForwardInstrumentDefinition,
    FxForwardInstrumentDefinitionOutput,
    FxForwardInstrumentOutput,
    FxForwardInstrumentsSource,
    FxSpotInstrument,
    FxSpotInstrumentDefinition,
    FxSpotInstrumentDefinitionOutput,
    FxSpotInstrumentOutput,
    FxSpotInstrumentsSource,
    IndustryEnum,
    IndustryGroupEnum,
    InstrumentDefinition,
    InstrumentDescription,
    InstrumentTypeEnum,
    InterpolationModeEnum,
    IssuerTypeEnum,
    MainConstituentAssetClassEnum,
    MarketDataLocationEnum,
    MarketDataTime,
    ProcessingInformation,
    RatingEnum,
    RatingScaleSourceEnum,
    ReferenceEntityTypeEnum,
    RiskTypeEnum,
)
from lseg_analytics.pricing._client.client import Client

from ._logger import logger

__all__ = [
    "BasisSplineSmoothModelEnum",
    "BidAskFieldsDescription",
    "BidAskFieldsFormulaDescription",
    "BidAskFieldsFormulaOutput",
    "BidAskFieldsOutput",
    "BidAskFormulaFields",
    "BondInstrument",
    "BondInstrumentDefinition",
    "BondInstrumentDescription",
    "BondInstrumentOutput",
    "BusinessSectorEnum",
    "CalendarAdjustmentEnum",
    "CalibrationModelEnum",
    "CalibrationParameters",
    "CategoryEnum",
    "CompoundingTypeEnum",
    "CreditConstituents",
    "CreditConstituentsDescription",
    "CreditConstituentsOutput",
    "CreditCurveCreateDefinition",
    "CreditCurveDefinition",
    "CreditCurveDefinitionDescription",
    "CreditCurveDefinitionOutput",
    "CreditCurveDefinitionResponse",
    "CreditCurveDefinitionResponseItem",
    "CreditCurveDefinitionsResponse",
    "CreditCurveDefinitionsResponseItems",
    "CreditCurveInstrumentsSegment",
    "CreditCurveParameters",
    "CreditCurveParametersDescription",
    "CreditCurvePoint",
    "CreditCurveRequestItem",
    "CreditCurveResponse",
    "CreditCurveSearchDefinition",
    "CreditCurveTypeEnum",
    "CreditCurvesResponse",
    "CreditCurvesResponseItem",
    "CreditDefaultSwapInstrument",
    "CreditDefaultSwapInstrumentDefinition",
    "CreditDefaultSwapInstrumentOutput",
    "CreditDefaultSwapsInstrumentDescription",
    "CreditInstruments",
    "CreditInstrumentsOutput",
    "CrossCurrencyInstrument",
    "CrossCurrencyInstrumentDefinition",
    "CrossCurrencyInstrumentDefinitionOutput",
    "CrossCurrencyInstrumentOutput",
    "CrossCurrencyInstruments",
    "CrossCurrencyInstrumentsOutput",
    "CrossCurrencyInstrumentsSources",
    "CurveInfo",
    "CurveSubTypeEnum",
    "CurvesAndSurfacesBidAskFields",
    "CurvesAndSurfacesInstrument",
    "CurvesAndSurfacesInterestCalculationMethodEnum",
    "CurvesAndSurfacesPriceSideEnum",
    "CurvesAndSurfacesQuotationModeEnum",
    "CurvesAndSurfacesSeniorityEnum",
    "DepositInstrumentOutput",
    "EconomicSectorEnum",
    "ErrorDetails",
    "ErrorResponse",
    "ExtrapolationModeEnum",
    "ExtrapolationTypeEnum",
    "FieldDescription",
    "FieldDoubleOutput",
    "FieldDoubleValue",
    "FieldFormulaDescription",
    "FieldFormulaDoubleOutput",
    "FieldFormulaDoubleValue",
    "FormulaParameter",
    "FormulaParameterDescription",
    "FormulaParameterOutput",
    "FxForwardInstrument",
    "FxForwardInstrumentDefinition",
    "FxForwardInstrumentDefinitionOutput",
    "FxForwardInstrumentOutput",
    "FxForwardInstrumentsSource",
    "FxSpotInstrument",
    "FxSpotInstrumentDefinition",
    "FxSpotInstrumentDefinitionOutput",
    "FxSpotInstrumentOutput",
    "FxSpotInstrumentsSource",
    "IndustryEnum",
    "IndustryGroupEnum",
    "InstrumentDefinition",
    "InstrumentDescription",
    "InstrumentTypeEnum",
    "InterpolationModeEnum",
    "IssuerTypeEnum",
    "MainConstituentAssetClassEnum",
    "MarketDataLocationEnum",
    "MarketDataTime",
    "ProcessingInformation",
    "RatingEnum",
    "RatingScaleSourceEnum",
    "ReferenceEntityTypeEnum",
    "RiskTypeEnum",
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
    universe: Optional[List[CreditCurveRequestItem]] = None,
    fields: Optional[str] = None,
) -> CreditCurvesResponse:
    """
    Generates the curves for the definitions provided

    Parameters
    ----------
    universe : List[CreditCurveRequestItem], optional

    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    CreditCurvesResponse
        CreditCurvesResponse

    Examples
    --------
    >>> print("Step 1: Configuring Curve Definition...")
    >>>
    >>> curve_definition = CreditCurveDefinition(
    >>>     name = "Belgium GOV Par Benchmark Curve", # combination of Name | Country | Currency | isCurrencyCountryOriginator, see Appendix 2 below
    >>>     issuer_type = IssuerTypeEnum.SOVEREIGN,
    >>>     country = "BE",
    >>>     source = RatingScaleSourceEnum.REFINITIV,
    >>>     currency = "EUR",
    >>>     curve_sub_type=CurveSubTypeEnum.GOVERNMENT_BENCHMARK,
    >>>     is_currency_country_originator=True
    >>> )
    >>>
    >>> print(f"   Curve Name: {curve_definition.name}")
    >>>
    >>>
    >>> print("Step 2: Configuring Curve Parameters...")
    >>>
    >>>
    >>> curve_parameters = CreditCurveParameters(
    >>>     valuation_date = dt.date(2025, 9, 19), # remove valuation_date to get a real-time
    >>>     calibration_model = CalibrationModelEnum.BASIS_SPLINE,
    >>>     calibration_parameters = CalibrationParameters(
    >>>         is_monotonic = True,
    >>>         extrapolation_points_number = 4,
    >>>         extrapolation_type = ExtrapolationTypeEnum.EXTRAPOLATION_RIGHT_FLAT
    >>>     ),
    >>>     use_duration_weighted_minimization = True,
    >>>     use_multi_dimensional_solver = True,
    >>>     calendar_adjustment = CalendarAdjustmentEnum.CALENDAR,
    >>>     use_delayed_data_if_denied = False
    >>> )
    >>>
    >>> print(f"   Curve Parameters: {curve_parameters}")
    >>>
    >>>
    >>> print("Step 3: Create request item...")
    >>>
    >>> credit_curve_request = CreditCurveRequestItem(
    >>>     curve_parameters = curve_parameters,
    >>>     curve_definition = curve_definition,
    >>>     constituents = None # default set of constituents is used, i.e. no bonds are filtered by maturity/notional/etc
    >>> )
    >>>
    >>> print(f"   Request: {json.dumps(credit_curve_request.as_dict(), indent=4)}")
    Step 1: Configuring Curve Definition...
       Curve Name: Belgium GOV Par Benchmark Curve
    Step 2: Configuring Curve Parameters...
       Curve Parameters: {'valuationDate': '2025-09-19', 'calibrationModel': 'BasisSpline', 'calibrationParameters': {'isMonotonic': True, 'extrapolationPointsNumber': 4, 'extrapolationType': 'ExtrapolationRightFlat'}, 'useDurationWeightedMinimization': True, 'useMultiDimensionalSolver': True, 'calendarAdjustment': 'Calendar', 'useDelayedDataIfDenied': False}
    Step 3: Create request item...
       Request: {
        "curveParameters": {
            "valuationDate": "2025-09-19",
            "calibrationModel": "BasisSpline",
            "calibrationParameters": {
                "isMonotonic": true,
                "extrapolationPointsNumber": 4,
                "extrapolationType": "ExtrapolationRightFlat"
            },
            "useDurationWeightedMinimization": true,
            "useMultiDimensionalSolver": true,
            "calendarAdjustment": "Calendar",
            "useDelayedDataIfDenied": false
        },
        "curveDefinition": {
            "name": "Belgium GOV Par Benchmark Curve",
            "issuerType": "Sovereign",
            "country": "BE",
            "source": "Refinitiv",
            "currency": "EUR",
            "curveSubType": "GovernmentBenchmark",
            "isCurrencyCountryOriginator": true
        }
    }


    >>> # Get the constituents
    >>> try:
    >>>     response_constituents = cc.calculate(universe=[credit_curve_request], fields="Constituents")
    >>>     print("Credit curve calculation completed")
    >>> except Exception as e:
    >>>     print("Error during credit curve calculation:", str(e))
    >>>
    >>> # Get the curve
    >>> try:
    >>>     response = cc.calculate(universe=[credit_curve_request])
    >>>     print("Credit curve calculation completed")
    >>> except Exception as e:
    >>>     print("Error during credit curve calculation:", str(e))
    Credit curve calculation completed
    Credit curve calculation completed

    """

    try:
        logger.info("Calling calculate")

        response = Client().credit_curves.calculate(fields=fields, universe=universe)

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
) -> CreditCurvesResponseItem:
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
    CreditCurvesResponseItem


    Examples
    --------


    """

    try:
        logger.info("Calling calculate_by_id")

        response = Client().credit_curves.calculate_by_id(
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
    curve_definition: Optional[CreditCurveCreateDefinition] = None,
    segments: Optional[List[CreditCurveInstrumentsSegment]] = None,
) -> CreditCurveResponse:
    """
    Creates a curve definition

    Parameters
    ----------
    curve_definition : CreditCurveCreateDefinition, optional
        CreditCurveCreateDefinition
    segments : List[CreditCurveInstrumentsSegment], optional
        Get segments

    Returns
    --------
    CreditCurveResponse


    Examples
    --------
    >>> unique_id_create_name = "SDKTest-55241" # Unique ID of Create, it can be created only once via Create function
    >>> # In case of duplicate, you will got an error:
    >>> # "Exception: Bad request: code=FinancialContract-API.InvalidInputError The service failed to create the curve definition: Such a curve definition already exists"
    >>>
    >>> curve_definition_create = cc.CreditCurveDefinition(
    >>>     name=unique_id_create_name,
    >>>     issuer_type=cc.IssuerTypeEnum.SOVEREIGN,
    >>>     country="DE",
    >>>     source="LFA",
    >>>     currency="EUR",
    >>>     curve_sub_type=cc.CurveSubTypeEnum.GOVERNMENT_BENCHMARK,
    >>>     main_constituent_asset_class="Bond",
    >>> )
    >>>
    >>> segments_create = [
    >>>     cc.CreditCurveInstrumentsSegment(
    >>>         constituents=cc.CreditConstituentsDescription(
    >>>             bonds=[
    >>>                 cc.BondInstrumentDescription(
    >>>                     instrument_definition=cc.BondInstrumentDefinition(
    >>>                         instrument_code="DE114181=",
    >>>                         fixed_rate_percent=0.0,
    >>>                         template="ACC:AA CCM:BBAA CFADJ:NO CLDR:EMU_FI DATED:31JAN2020 DMC:F EMC:S FRCD:11APR2021 FRQ:1 ISSUE:31JAN2020 NOTIONAL:1 PX:C PXRND:1E-5:NEAR REFDATE:MATURITY RP:1 SETTLE:2WD XD:NO",
    >>>                         quotation_mode="PercentCleanPrice",
    >>>                     )
    >>>                 )
    >>>             ]
    >>>         ),
    >>>         start_date=dt.date(2025, 1, 1),
    >>>     )
    >>> ]
    >>>
    >>> print("Creating Curve Definition...")
    >>> response_create = create(curve_definition=curve_definition_create, segments=segments_create)
    >>>
    >>> print(f"   Response: {json.dumps(response_create.as_dict(), indent=4)}")
    >>>
    >>> print(response_create.data.curve_definition.id)
    Creating Curve Definition...
       Response: {
        "data": {
            "curveDefinition": {
                "country": "DE",
                "currency": "EUR",
                "curveSubType": "GovernmentBenchmark",
                "firstHistoricalAvailabilityDate": "2025-01-01",
                "id": "a8609860-2eec-4660-93c2-473ac8bc7ea1",
                "issuerType": "Sovereign",
                "mainConstituentAssetClass": "Bond",
                "name": "SDKTest-55241",
                "owner": "GE-SP3A4U7WBPXE",
                "riskType": "Credit",
                "source": "LFA"
            },
            "curveInfo": {
                "creationDateTime": "2025-12-03T12:45:44.891Z",
                "creationUserId": "GE-SP3A4U7WBPXE",
                "updateDateTime": "2025-12-03T12:45:44.891Z",
                "updateUserId": "GE-SP3A4U7WBPXE"
            },
            "segments": [
                {
                    "constituents": {
                        "bonds": [
                            {
                                "instrumentDefinition": {
                                    "fixedRatePercent": 0.0,
                                    "instrumentCode": "DE114181=",
                                    "quotationMode": "PercentCleanPrice",
                                    "template": "ACC:AA CCM:BBAA CFADJ:NO CLDR:EMU_FI DATED:31JAN2020 DMC:F EMC:S FRCD:11APR2021 FRQ:1 ISSUE:31JAN2020 NOTIONAL:1 PX:C PXRND:1E-5:NEAR REFDATE:MATURITY RP:1 SETTLE:2WD XD:NO"
                                }
                            }
                        ]
                    },
                    "startDate": "2025-01-01"
                }
            ]
        }
    }
    a8609860-2eec-4660-93c2-473ac8bc7ea1

    """

    try:
        logger.info("Calling create")

        response = Client().credit_curves.create(
            body=CreditCurveCreateRequest(curve_definition=curve_definition, segments=segments)
        )

        output = response
        logger.info("Called create")

        return output
    except Exception as err:
        logger.error("Error create.")
        check_exception_and_raise(err, logger)


def delete(*, curve_id: str) -> bool:
    """
    Delete a CreditCurveDefinition that exists in the platform. The CreditCurveDefinition can be identified either by its unique ID (GUID format) or by its location path (space/name).

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
    >>> delete(curve_id=response_create.data.curve_definition.id)
    True

    """

    try:
        logger.info(f"Deleting CreditCurvesResource with id: {curve_id}")
        Client().credit_curves.delete(curve_id=curve_id)
        logger.info(f"Deleted CreditCurvesResource with id: {curve_id}")

        return True
    except Exception as err:
        logger.error("Error delete.")
        check_exception_and_raise(err, logger)


def overwrite(
    *,
    curve_id: str,
    curve_definition: Optional[CreditCurveCreateDefinition] = None,
    segments: Optional[List[CreditCurveInstrumentsSegment]] = None,
) -> CreditCurveResponse:
    """
    Overwrite a CreditCurveDefinition that exists in the platform. The CreditCurveDefinition can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    curve_definition : CreditCurveCreateDefinition, optional
        CreditCurveCreateDefinition
    segments : List[CreditCurveInstrumentsSegment], optional
        Get segments
    curve_id : str
        The curve identifier.

    Returns
    --------
    CreditCurveResponse


    Examples
    --------
    >>> curve_definition_overwrite = curve_definition_create
    >>> curve_definition_overwrite.country = "US"
    >>> curve_definition_overwrite.currency = "USD"
    >>>
    >>> response_overwrite = overwrite(curve_id=response_create.data.curve_definition.id,
    >>>                                   curve_definition=curve_definition_overwrite,
    >>>                                   segments=segments_create)
    >>> print(json.dumps(response_overwrite.as_dict(), indent=4))
    >>>
    >>> response_read = read(curve_id=response_create.data.curve_definition.id)
    >>> print(f"   Response: {json.dumps(response_read.as_dict(), indent=4)}") # Now it has USD and US
    {
        "data": {
            "curveDefinition": {
                "country": "US",
                "currency": "USD",
                "curveSubType": "GovernmentBenchmark",
                "firstHistoricalAvailabilityDate": "2025-01-01",
                "id": "a8609860-2eec-4660-93c2-473ac8bc7ea1",
                "issuerType": "Sovereign",
                "mainConstituentAssetClass": "Bond",
                "name": "SDKTest-55241",
                "owner": "GE-SP3A4U7WBPXE",
                "riskType": "Credit",
                "source": "LFA"
            },
            "curveInfo": {
                "creationDateTime": "2025-12-03T12:45:44.891Z",
                "creationUserId": "GE-SP3A4U7WBPXE",
                "updateDateTime": "2025-12-03T12:45:48.620Z",
                "updateUserId": "GE-SP3A4U7WBPXE"
            },
            "segments": [
                {
                    "constituents": {
                        "bonds": [
                            {
                                "instrumentDefinition": {
                                    "fixedRatePercent": 0.0,
                                    "instrumentCode": "DE114181=",
                                    "quotationMode": "PercentCleanPrice",
                                    "template": "ACC:AA CCM:BBAA CFADJ:NO CLDR:EMU_FI DATED:31JAN2020 DMC:F EMC:S FRCD:11APR2021 FRQ:1 ISSUE:31JAN2020 NOTIONAL:1 PX:C PXRND:1E-5:NEAR REFDATE:MATURITY RP:1 SETTLE:2WD XD:NO"
                                }
                            }
                        ]
                    },
                    "startDate": "2025-01-01"
                }
            ]
        }
    }
       Response: {
        "data": {
            "curveDefinition": {
                "country": "US",
                "currency": "USD",
                "curveSubType": "GovernmentBenchmark",
                "firstHistoricalAvailabilityDate": "2025-01-01",
                "id": "a8609860-2eec-4660-93c2-473ac8bc7ea1",
                "issuerType": "Sovereign",
                "mainConstituentAssetClass": "Bond",
                "name": "SDKTest-55241",
                "owner": "GE-SP3A4U7WBPXE",
                "riskType": "Credit",
                "source": "LFA"
            },
            "curveInfo": {
                "creationDateTime": "2025-12-03T12:45:44.891Z",
                "creationUserId": "GE-SP3A4U7WBPXE",
                "updateDateTime": "2025-12-03T12:45:48.620Z",
                "updateUserId": "GE-SP3A4U7WBPXE"
            },
            "segments": [
                {
                    "constituents": {
                        "bonds": [
                            {
                                "instrumentDefinition": {
                                    "fixedRatePercent": 0.0,
                                    "instrumentCode": "DE114181=",
                                    "quotationMode": "PercentCleanPrice",
                                    "template": "ACC:AA CCM:BBAA CFADJ:NO CLDR:EMU_FI DATED:31JAN2020 DMC:F EMC:S FRCD:11APR2021 FRQ:1 ISSUE:31JAN2020 NOTIONAL:1 PX:C PXRND:1E-5:NEAR REFDATE:MATURITY RP:1 SETTLE:2WD XD:NO"
                                }
                            }
                        ]
                    },
                    "startDate": "2025-01-01"
                }
            ]
        }
    }

    """

    try:
        logger.info("Calling overwrite")

        response = Client().credit_curves.overwrite(
            body=CreditCurveCreateRequest(curve_definition=curve_definition, segments=segments),
            curve_id=curve_id,
        )

        output = response
        logger.info("Called overwrite")

        return output
    except Exception as err:
        logger.error("Error overwrite.")
        check_exception_and_raise(err, logger)


def read(*, curve_id: str, fields: Optional[str] = None) -> CreditCurveResponse:
    """
    Access a CreditCurveDefinition existing in the platform (read). The CreditCurveDefinition can be identified either by its unique ID (GUID format) or by its location path (space/name).

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
    CreditCurveResponse


    Examples
    --------
    >>> response_read = read(curve_id=response_create.data.curve_definition.id)
    >>>
    >>> print(f"   Response: {json.dumps(response_read.as_dict(), indent=4)}")
       Response: {
        "data": {
            "curveDefinition": {
                "country": "DE",
                "currency": "EUR",
                "curveSubType": "GovernmentBenchmark",
                "firstHistoricalAvailabilityDate": "2025-01-01",
                "id": "a8609860-2eec-4660-93c2-473ac8bc7ea1",
                "issuerType": "Sovereign",
                "mainConstituentAssetClass": "Bond",
                "name": "SDKTest-55241",
                "owner": "GE-SP3A4U7WBPXE",
                "riskType": "Credit",
                "source": "LFA"
            },
            "curveInfo": {
                "creationDateTime": "2025-12-03T12:45:44.891Z",
                "creationUserId": "GE-SP3A4U7WBPXE",
                "updateDateTime": "2025-12-03T12:45:44.891Z",
                "updateUserId": "GE-SP3A4U7WBPXE"
            },
            "segments": [
                {
                    "constituents": {
                        "bonds": [
                            {
                                "instrumentDefinition": {
                                    "fixedRatePercent": 0.0,
                                    "instrumentCode": "DE114181=",
                                    "quotationMode": "PercentCleanPrice",
                                    "template": "ACC:AA CCM:BBAA CFADJ:NO CLDR:EMU_FI DATED:31JAN2020 DMC:F EMC:S FRCD:11APR2021 FRQ:1 ISSUE:31JAN2020 NOTIONAL:1 PX:C PXRND:1E-5:NEAR REFDATE:MATURITY RP:1 SETTLE:2WD XD:NO"
                                }
                            }
                        ]
                    },
                    "startDate": "2025-01-01"
                }
            ]
        }
    }

    """

    try:
        logger.info("Calling read")

        response = Client().credit_curves.read(curve_id=curve_id, fields=fields)

        output = response
        logger.info("Called read")

        return output
    except Exception as err:
        logger.error("Error read.")
        check_exception_and_raise(err, logger)


def search(
    *,
    universe: Optional[List[CreditCurveSearchDefinition]] = None,
    fields: Optional[str] = None,
) -> CreditCurveDefinitionsResponse:
    """
    Returns the definitions of the available curves for the filters selected

    Parameters
    ----------
    universe : List[CreditCurveSearchDefinition], optional
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
    CreditCurveDefinitionsResponse
        CreditCurveDefinitionsResponse

    Examples
    --------
    >>> curve_definition_search = CreditCurveDefinition(
    >>>     issuer_type = IssuerTypeEnum.SOVEREIGN,
    >>>     source = RatingScaleSourceEnum.REFINITIV,
    >>>     currency = "EUR",
    >>>     curve_sub_type=CurveSubTypeEnum.GOVERNMENT_BENCHMARK,
    >>> )
    >>>
    >>> response_search = search(universe=[curve_definition_search])
    >>>
    >>>
    >>> curve_defs = response_search['data'][0]['curveDefinitions']
    >>> df_curves = pd.DataFrame(curve_defs)
    >>> display(df_curves) # it is a subset of Appendix 2 for specific currency provided below
    >>>
    >>> curve_definition_selected = [curve for curve in curve_defs if curve['country'] == "BE"][0]
    >>> curve_definition_selected_id = curve_definition_selected['id']
    >>>
    >>> print(json.dumps(curve_definition_selected.as_dict(), indent=4))
    {
        "country": "BE",
        "currency": "EUR",
        "curveSubType": "GovernmentBenchmark",
        "firstHistoricalAvailabilityDate": "2022-03-29",
        "id": "21c8ba29-7ed6-4907-bd56-d5663f972703",
        "isCurrencyCountryOriginator": true,
        "issuerType": "Sovereign",
        "mainConstituentAssetClass": "Bond",
        "name": "Belgium GOV Par Benchmark Curve",
        "source": "Refinitiv"
    }

    """

    try:
        logger.info("Calling search")

        response = Client().credit_curves.search(fields=fields, universe=universe)

        output = response
        logger.info("Called search")

        return output
    except Exception as err:
        logger.error("Error search.")
        check_exception_and_raise(err, logger)
