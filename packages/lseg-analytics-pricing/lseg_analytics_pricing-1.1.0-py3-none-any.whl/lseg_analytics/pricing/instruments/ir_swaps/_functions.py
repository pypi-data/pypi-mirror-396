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
    AdjustableDate,
    AmortizationDefinition,
    AmortizationTypeEnum,
    Amount,
    BachelierParameters,
    BasePricingParameters,
    BlackScholesEquityParameters,
    BlackScholesFxParameters,
    BlackScholesInterestRateFuture,
    BusinessDayAdjustmentDefinition,
    CapFloorDefinition,
    CapFloorTypeEnum,
    Cashflow,
    CmdtyOptionVolSurfaceChoice,
    CmdtyVolSurfaceInput,
    CompoundingModeEnum,
    ConvexityAdjustment,
    CouponReferenceDateEnum,
    CreditCurveChoice,
    CreditCurveInput,
    CrossCurencySwapOverride,
    CurencyBasisSwapOverride,
    CurveDataPoint,
    Date,
    DatedRate,
    DatedValue,
    DateMovingConvention,
    DayCountBasis,
    Description,
    DirectionEnum,
    Dividend,
    DividendTypeEnum,
    EndOfMonthConvention,
    EqOptionVolSurfaceChoice,
    EqVolSurfaceInput,
    FixedRateDefinition,
    FloatingRateDefinition,
    FrequencyEnum,
    FutureDate,
    FutureDateCalculationMethodEnum,
    FxCurveInput,
    FxForwardCurveChoice,
    FxOptionVolSurfaceChoice,
    FxPricingParameters,
    FxRateTypeEnum,
    FxVolSurfaceInput,
    HestonEquityParameters,
    IncomeTaxCashflow,
    IndexCompoundingDefinition,
    IndexFixing,
    IndexFixingForwardSourceEnum,
    IndexObservationMethodEnum,
    InnerError,
    InterestCashflow,
    InterestRateDefinition,
    InterestRateLegDefinition,
    InterestRateTypeEnum,
    InterestType,
    IrCapVolSurfaceChoice,
    IrCurveChoice,
    IrLegDescriptionFields,
    IrLegResponseFields,
    IrLegValuationResponseFields,
    IrMeasure,
    IrPricingParameters,
    IrRiskFields,
    IrSwapAsCollectionItem,
    IrSwapDefinition,
    IrSwapDefinitionInstrument,
    IrSwapInstrumentDescriptionFields,
    IrSwapInstrumentRiskFields,
    IrSwapInstrumentSolveResponseFieldsOnResourceResponseData,
    IrSwapInstrumentSolveResponseFieldsResponseData,
    IrSwapInstrumentSolveResponseFieldsResponseWithError,
    IrSwapInstrumentValuationFields,
    IrSwapInstrumentValuationResponseFieldsOnResourceResponseData,
    IrSwapInstrumentValuationResponseFieldsResponseData,
    IrSwapInstrumentValuationResponseFieldsResponseWithError,
    IrSwapSolvingParameters,
    IrSwapSolvingTarget,
    IrSwapSolvingVariable,
    IrSwaptionVolCubeChoice,
    IrValuationFields,
    IrVolCubeInput,
    IrVolSurfaceInput,
    IrZcCurveInput,
    LoanDefinition,
    LoanInstrumentRiskFields,
    LoanInstrumentValuationFields,
    Location,
    MarketData,
    MarketVolatility,
    Measure,
    ModelParameters,
    MonthEnum,
    NumericalMethodEnum,
    OffsetDefinition,
    OptionPricingParameters,
    OptionSolvingParameters,
    OptionSolvingTarget,
    OptionSolvingVariable,
    OptionSolvingVariableEnum,
    PaidLegEnum,
    PartyEnum,
    PayerReceiverEnum,
    Payment,
    PaymentOccurrenceEnum,
    PaymentSettlementDefinition,
    PayoffCashflow,
    PremiumCashflow,
    PriceSideWithLastEnum,
    PrincipalCashflow,
    PrincipalDefinition,
    Rate,
    ReferenceDate,
    RelativeAdjustableDate,
    RequestPatternEnum,
    ResetDatesDefinition,
    ScheduleDefinition,
    ServiceError,
    SettlementCashflow,
    SolvingLegEnum,
    SolvingMethod,
    SolvingMethodEnum,
    SolvingResult,
    SortingOrderEnum,
    Spot,
    SpreadCompoundingModeEnum,
    StepRateDefinition,
    StrikeTypeEnum,
    StubIndexReferences,
    StubRuleEnum,
    SwapSolvingVariableEnum,
    TenorBasisSwapOverride,
    TimeStampEnum,
    UnitEnum,
    VanillaIrsOverride,
    VolatilityTypeEnum,
    VolCubePoint,
    VolModelTypeEnum,
    VolSurfacePoint,
    ZcTypeEnum,
)
from lseg_analytics.pricing._client.client import Client

from ._ir_swap import IrSwap
from ._logger import logger

__all__ = [
    "AmortizationDefinition",
    "AmortizationTypeEnum",
    "Amount",
    "BachelierParameters",
    "BasePricingParameters",
    "BlackScholesEquityParameters",
    "BlackScholesFxParameters",
    "BlackScholesInterestRateFuture",
    "BusinessDayAdjustmentDefinition",
    "CapFloorDefinition",
    "CapFloorTypeEnum",
    "Cashflow",
    "CmdtyOptionVolSurfaceChoice",
    "CmdtyVolSurfaceInput",
    "CompoundingModeEnum",
    "ConvexityAdjustment",
    "CouponReferenceDateEnum",
    "CreditCurveChoice",
    "CreditCurveInput",
    "CrossCurencySwapOverride",
    "CurencyBasisSwapOverride",
    "CurveDataPoint",
    "DatedRate",
    "DatedValue",
    "DirectionEnum",
    "Dividend",
    "DividendTypeEnum",
    "EqOptionVolSurfaceChoice",
    "EqVolSurfaceInput",
    "FixedRateDefinition",
    "FloatingRateDefinition",
    "FutureDate",
    "FutureDateCalculationMethodEnum",
    "FxCurveInput",
    "FxForwardCurveChoice",
    "FxOptionVolSurfaceChoice",
    "FxPricingParameters",
    "FxRateTypeEnum",
    "FxVolSurfaceInput",
    "HestonEquityParameters",
    "IncomeTaxCashflow",
    "IndexCompoundingDefinition",
    "IndexFixing",
    "IndexFixingForwardSourceEnum",
    "IndexObservationMethodEnum",
    "InterestCashflow",
    "InterestRateDefinition",
    "InterestRateLegDefinition",
    "InterestRateTypeEnum",
    "IrCapVolSurfaceChoice",
    "IrCurveChoice",
    "IrLegDescriptionFields",
    "IrLegResponseFields",
    "IrLegValuationResponseFields",
    "IrMeasure",
    "IrPricingParameters",
    "IrRiskFields",
    "IrSwap",
    "IrSwapAsCollectionItem",
    "IrSwapDefinition",
    "IrSwapDefinitionInstrument",
    "IrSwapInstrumentDescriptionFields",
    "IrSwapInstrumentRiskFields",
    "IrSwapInstrumentSolveResponseFieldsOnResourceResponseData",
    "IrSwapInstrumentSolveResponseFieldsResponseData",
    "IrSwapInstrumentSolveResponseFieldsResponseWithError",
    "IrSwapInstrumentValuationFields",
    "IrSwapInstrumentValuationResponseFieldsOnResourceResponseData",
    "IrSwapInstrumentValuationResponseFieldsResponseData",
    "IrSwapInstrumentValuationResponseFieldsResponseWithError",
    "IrSwapSolvingParameters",
    "IrSwapSolvingTarget",
    "IrSwapSolvingVariable",
    "IrSwaptionVolCubeChoice",
    "IrValuationFields",
    "IrVolCubeInput",
    "IrVolSurfaceInput",
    "IrZcCurveInput",
    "LoanDefinition",
    "LoanInstrumentRiskFields",
    "LoanInstrumentValuationFields",
    "MarketData",
    "MarketVolatility",
    "Measure",
    "ModelParameters",
    "MonthEnum",
    "NumericalMethodEnum",
    "OffsetDefinition",
    "OptionPricingParameters",
    "OptionSolvingParameters",
    "OptionSolvingTarget",
    "OptionSolvingVariable",
    "OptionSolvingVariableEnum",
    "PartyEnum",
    "Payment",
    "PaymentOccurrenceEnum",
    "PaymentSettlementDefinition",
    "PayoffCashflow",
    "PremiumCashflow",
    "PriceSideWithLastEnum",
    "PrincipalCashflow",
    "PrincipalDefinition",
    "Rate",
    "RequestPatternEnum",
    "ResetDatesDefinition",
    "ScheduleDefinition",
    "SettlementCashflow",
    "SolvingLegEnum",
    "SolvingMethod",
    "SolvingMethodEnum",
    "SolvingResult",
    "Spot",
    "SpreadCompoundingModeEnum",
    "StepRateDefinition",
    "StrikeTypeEnum",
    "StubIndexReferences",
    "SwapSolvingVariableEnum",
    "TenorBasisSwapOverride",
    "TimeStampEnum",
    "UnitEnum",
    "VanillaIrsOverride",
    "VolCubePoint",
    "VolModelTypeEnum",
    "VolSurfacePoint",
    "VolatilityTypeEnum",
    "ZcTypeEnum",
    "create_from_cbs_template",
    "create_from_ccs_template",
    "create_from_leg_template",
    "create_from_tbs_template",
    "create_from_vanilla_irs_template",
    "delete",
    "load",
    "search",
    "solve",
    "solve_polling",
    "value",
    "value_polling",
]


def load(
    *,
    resource_id: Optional[str] = None,
    name: Optional[str] = None,
    space: Optional[str] = None,
):
    """
    Load a IrSwap using its name and space

    Parameters
    ----------
    resource_id : str, optional
        The IrSwap id. Or the combination of the space and name of the resource with a slash, e.g. 'HOME/my_resource'.
        Required if name is not provided.
    name : str, optional
        The IrSwap name.
        Required if resource_id is not provided. The name parameter must be specified when the object is first created. Thereafter it is optional.
    space : str, optional
        The space where the IrSwap is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    IrSwap
        The IrSwap instance.

    Examples
    --------
    >>> # fetch all available swaps
    >>> available_swaps = search()
    >>>
    >>> # execute the load of a swap using the first element of previously fetched data
    >>> loaded_swap = load(resource_id=available_swaps[0].id)
    >>>
    >>> print(loaded_swap)
    <IrSwap space='test' name='SwapResourceCreatdforTest' 186e9289‥>

    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _load_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Load IrSwap {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"IrSwap {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource IrSwap not found by identifier name={name} space={space}")
    elif not isinstance(result, list):
        raise LibraryException(f"Expected list of results, got {result}")
    elif len(result) > 1:
        logger.warn(f"Found more than one result for name={name!r} and space={space!r}, returning the first one")
    return _load_by_id(result[0].id)


def delete(
    *,
    resource_id: Optional[str] = None,
    name: Optional[str] = None,
    space: Optional[str] = None,
):
    """
    Delete IrSwap instance from the server.

    Parameters
    ----------
    resource_id : str, optional
        The IrSwap resource ID.
        Required if name is not provided.
    name : str, optional
        The IrSwap name.
        Required if resource_id is not provided.
    space : str, optional
        The space where the IrSwap is stored. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

    Returns
    -------
    ServiceErrorResponse, optional
        Error response, if applicable, otherwise None

    Examples
    --------
    >>> # Let's delete the instrument we created in HOME space
    >>> from lseg_analytics.pricing.instruments.ir_swaps import delete
    >>>
    >>> swap_id = "SOFR_OIS_1Y2Y"
    >>>
    >>> delete(name=swap_id, space="HOME")
    True

    """
    if not isinstance(resource_id, (str, type(None))):
        raise TypeError(f"Expected resource_id as a string, got {resource_id!r}")
    if resource_id:
        if name or space:
            logger.warn("resource_id argument received, name & space arguments are ignored")
        return _delete_by_id(resource_id)
    if not name:
        raise ValueError("Either resource_id or name argument should be provided")
    logger.info(f"Delete IrSwap {name} from space={space!r}")
    spaces = [space] if space else None
    result = search(names=[name], spaces=spaces)
    if not result:
        logger.error(f"IrSwap {name} not found in space={space!r}")
        raise ResourceNotFound(f"Resource IrSwap not found by identifier name={name} space={space}")
    elif not isinstance(result, list):
        raise LibraryException(f"Expected list of results, got {result}")
    return _delete_by_id(result[0].id)


def create_from_cbs_template(
    *,
    template_reference: str,
    overrides: Optional[CurencyBasisSwapOverride] = None,
    fields: Optional[str] = None,
) -> IrSwap:
    """
    Create an interest rate swap instance from a currency basis swap template.
    This user-defined instrument includes all trade-specific details (e.g., fixed rate, spread, start date, end date), and is typically based on a general template available via the Instrument Template API.

    Parameters
    ----------
    template_reference : str
        "The identifier of the currency basis swap template (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric character, and contain only alphanumeric characters, slashes and underscores.
    overrides : CurencyBasisSwapOverride, optional
        An object that contains the currency basis swap properties that can be overridden.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    IrSwap
        IrSwap

    Examples
    --------
    >>> swap_from_cbs = create_from_cbs_template(template_reference = "LSEG/GBUSSOSRBS")
    >>> print(swap_from_cbs.definition)
    {'firstLeg': {'rate': {'interestRateType': 'FloatingRate', 'index': 'LSEG/GBP_SONIA_ON_BOE', 'spreadSchedule': [{'rate': {'value': 0.0, 'unit': 'BasisPoint'}}], 'resetDates': {'offset': {'tenor': '0D', 'businessDayAdjustment': {'calendars': [], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Backward'}}, 'leverage': 1.0}, 'interestPeriods': {'startDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Quarterly', 'businessDayAdjustment': {'calendars': ['UKG', 'USA'], 'convention': 'ModifiedFollowing'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '2D', 'businessDayAdjustment': {'calendars': ['UKG', 'USA'], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Forward'}, 'couponDayCount': 'Dcb_Actual_365', 'accrualDayCount': 'Dcb_Actual_365', 'principal': {'currency': 'GBP', 'amount': 10000000.0, 'initialPrincipalExchange': True, 'finalPrincipalExchange': True, 'interimPrincipalExchange': False, 'repaymentCurrency': 'GBP'}, 'payer': 'Party1', 'receiver': 'Party2'}, 'secondLeg': {'rate': {'interestRateType': 'FloatingRate', 'index': 'LSEG/USD_SOFR_ON_FRBNY', 'spreadSchedule': [{'rate': {'value': 0.0, 'unit': 'BasisPoint'}}], 'resetDates': {'offset': {'tenor': '0D', 'businessDayAdjustment': {'calendars': [], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Backward'}}, 'leverage': 1.0}, 'interestPeriods': {'startDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Quarterly', 'businessDayAdjustment': {'calendars': ['UKG', 'USA'], 'convention': 'ModifiedFollowing'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '2D', 'businessDayAdjustment': {'calendars': ['UKG', 'USA'], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Forward'}, 'couponDayCount': 'Dcb_Actual_360', 'accrualDayCount': 'Dcb_Actual_360', 'principal': {'currency': 'USD', 'initialPrincipalExchange': True, 'finalPrincipalExchange': True, 'interimPrincipalExchange': False, 'repaymentCurrency': 'USD'}, 'payer': 'Party2', 'receiver': 'Party1'}}

    """

    try:
        logger.info("Calling create_from_cbs_template")

        response = Client().ir_swaps_resource.create_irs_from_cbs_template(
            fields=fields, template_reference=template_reference, overrides=overrides
        )

        output = response.data
        logger.info("Called create_from_cbs_template")

        return IrSwap(output)
    except Exception as err:
        logger.error("Error create_from_cbs_template")
        check_exception_and_raise(err, logger)


def create_from_ccs_template(
    *,
    template_reference: str,
    overrides: Optional[CrossCurencySwapOverride] = None,
    fields: Optional[str] = None,
) -> IrSwap:
    """
    Create an interest rate swap instance from a cross currency swap template.
    This user-defined instrument includes all trade-specific details (e.g., fixed rate, spread, start date, end date), and is typically based on a general template available via the Instrument Template API.

    Parameters
    ----------
    template_reference : str
        "The identifier of the cross currency swap template (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric character, and contain only alphanumeric characters, slashes and underscores.
    overrides : CrossCurencySwapOverride, optional
        An object that contains the cross currency swap properties that can be overridden.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    IrSwap
        IrSwap

    Examples
    --------
    >>> swap_from_ccs = create_from_ccs_template(template_reference = "LSEG/CNUSQMSRBS")
    >>> print(swap_from_ccs.definition)
    {'firstLeg': {'rate': {'interestRateType': 'FixedRate', 'rate': {'value': 0.0, 'unit': 'Percentage'}}, 'interestPeriods': {'startDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Quarterly', 'businessDayAdjustment': {'calendars': ['CHN', 'USA'], 'convention': 'ModifiedFollowing'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '2D', 'businessDayAdjustment': {'calendars': ['CHN', 'USA'], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Forward'}, 'couponDayCount': 'Dcb_Actual_360', 'accrualDayCount': 'Dcb_Actual_360', 'principal': {'currency': 'CNY', 'amount': 10000000.0, 'initialPrincipalExchange': False, 'finalPrincipalExchange': True, 'interimPrincipalExchange': False, 'repaymentCurrency': 'CNY'}, 'settlement': {'currency': 'USD'}, 'payer': 'Party1', 'receiver': 'Party2'}, 'secondLeg': {'rate': {'interestRateType': 'FloatingRate', 'index': 'LSEG/USD_SOFR_ON_FRBNY', 'spreadSchedule': [{'rate': {'value': 0.0, 'unit': 'BasisPoint'}}], 'resetDates': {'offset': {'tenor': '0D', 'businessDayAdjustment': {'calendars': [], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Backward'}}, 'leverage': 1.0}, 'interestPeriods': {'startDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Quarterly', 'businessDayAdjustment': {'calendars': ['CHN', 'USA'], 'convention': 'ModifiedFollowing'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '2D', 'businessDayAdjustment': {'calendars': ['CHN', 'USA'], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Forward'}, 'couponDayCount': 'Dcb_Actual_360', 'accrualDayCount': 'Dcb_Actual_360', 'principal': {'currency': 'USD', 'initialPrincipalExchange': False, 'finalPrincipalExchange': True, 'interimPrincipalExchange': False, 'repaymentCurrency': 'USD'}, 'settlement': {'currency': 'USD'}, 'payer': 'Party2', 'receiver': 'Party1'}}

    """

    try:
        logger.info("Calling create_from_ccs_template")

        response = Client().ir_swaps_resource.create_irs_from_ccs_template(
            fields=fields, template_reference=template_reference, overrides=overrides
        )

        output = response.data
        logger.info("Called create_from_ccs_template")

        return IrSwap(output)
    except Exception as err:
        logger.error("Error create_from_ccs_template")
        check_exception_and_raise(err, logger)


def create_from_leg_template(
    *, first_leg_reference: str, second_leg_reference: str, fields: Optional[str] = None
) -> IrSwap:
    """
    Create an interest rate swap instance from two interest rate leg templates.
    This user-defined instrument includes all trade-specific details (e.g., fixed rate, spread, start date, end date), and is typically based on a general template available via the Instrument Template API.

    Parameters
    ----------
    first_leg_reference : str
        The identifier of the template for the instrument's first leg (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric character, and contain only alphanumeric characters, slashes and underscores.
    second_leg_reference : str
        The identifier of the template for the instrument's second leg (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric character, and contain only alphanumeric characters, slashes and underscores.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    IrSwap
        IrSwap

    Examples
    --------
    >>> swap_from_leg = create_from_leg_template(first_leg_reference = "LSEG/EUR_AB3E_FLT", second_leg_reference = "LSEG/EUR_AB3E_FXD")
    >>> print(swap_from_leg.definition)
    {'firstLeg': {'rate': {'interestRateType': 'FloatingRate', 'index': 'LSEG/EUR_EURIBOR_3M_EMMI', 'spreadSchedule': [{'rate': {'value': 0.0, 'unit': 'BasisPoint'}}], 'resetDates': {'offset': {'tenor': '2D', 'businessDayAdjustment': {'calendars': [], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodStartDate', 'direction': 'Backward'}}, 'leverage': 1.0}, 'interestPeriods': {'startDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Quarterly', 'businessDayAdjustment': {'calendars': ['EMU'], 'convention': 'ModifiedFollowing'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '0D', 'businessDayAdjustment': {'calendars': ['EMU'], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Forward'}, 'couponDayCount': 'Dcb_Actual_360', 'accrualDayCount': 'Dcb_Actual_360', 'principal': {'currency': 'EUR', 'amount': 10000000.0, 'initialPrincipalExchange': False, 'finalPrincipalExchange': False, 'interimPrincipalExchange': False, 'repaymentCurrency': 'EUR'}, 'payer': 'Party2', 'receiver': 'Party1'}, 'secondLeg': {'rate': {'interestRateType': 'FixedRate', 'rate': {'value': 0.0, 'unit': 'Percentage'}}, 'interestPeriods': {'startDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Annual', 'businessDayAdjustment': {'calendars': ['EMU'], 'convention': 'ModifiedFollowing'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '0D', 'businessDayAdjustment': {'calendars': ['EMU'], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Forward'}, 'couponDayCount': 'Dcb_30_360', 'accrualDayCount': 'Dcb_30_360', 'principal': {'currency': 'EUR', 'amount': 10000000.0, 'initialPrincipalExchange': False, 'finalPrincipalExchange': False, 'interimPrincipalExchange': False, 'repaymentCurrency': 'EUR'}, 'payer': 'Party1', 'receiver': 'Party2'}}

    """

    try:
        logger.info("Calling create_from_leg_template")

        response = Client().ir_swaps_resource.create_irs_from_leg_template(
            fields=fields,
            first_leg_reference=first_leg_reference,
            second_leg_reference=second_leg_reference,
        )

        output = response.data
        logger.info("Called create_from_leg_template")

        return IrSwap(output)
    except Exception as err:
        logger.error("Error create_from_leg_template")
        check_exception_and_raise(err, logger)


def create_from_tbs_template(
    *,
    template_reference: str,
    overrides: Optional[TenorBasisSwapOverride] = None,
    fields: Optional[str] = None,
) -> IrSwap:
    """
    Create an interest rate swap instance from a tenor basis swap template.
    This user-defined instrument includes all trade-specific details (e.g., fixed rate, spread, start date, end date), and is typically based on a general template available via the Instrument Template API.

    Parameters
    ----------
    template_reference : str
        "The identifier of the tenor basis swap template (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric character, and contain only alphanumeric characters, slashes and underscores.
    overrides : TenorBasisSwapOverride, optional
        An object that contains the tenor basis swap properties that can be overridden.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    IrSwap
        IrSwap

    Examples
    --------
    >>> swap_from_tbs = create_from_tbs_template(template_reference = "LSEG/CBS_USDSR3LIMM")
    >>> print(swap_from_tbs.definition)
    {'firstLeg': {'rate': {'interestRateType': 'FloatingRate', 'index': 'LSEG/USD_SOFR_ON_FRBNY', 'spreadSchedule': [{'rate': {'value': 0.0, 'unit': 'BasisPoint'}}], 'resetDates': {'offset': {'tenor': '0D', 'businessDayAdjustment': {'calendars': [], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Backward'}}, 'leverage': 1.0}, 'interestPeriods': {'startDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Quarterly', 'businessDayAdjustment': {'calendars': ['USA'], 'convention': 'ModifiedFollowing'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '2D', 'businessDayAdjustment': {'calendars': ['USA'], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Forward'}, 'couponDayCount': 'Dcb_Actual_360', 'accrualDayCount': 'Dcb_Actual_360', 'principal': {'currency': 'USD', 'amount': 10000000.0, 'initialPrincipalExchange': False, 'finalPrincipalExchange': False, 'interimPrincipalExchange': False, 'repaymentCurrency': 'USD'}, 'payer': 'Party1', 'receiver': 'Party2'}, 'secondLeg': {'rate': {'interestRateType': 'FloatingRate', 'index': 'LSEG/USD_LIBOR_3M_IBA', 'spreadSchedule': [{'rate': {'value': 0.0, 'unit': 'BasisPoint'}}], 'resetDates': {'offset': {'tenor': '2D', 'businessDayAdjustment': {'calendars': [], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodStartDate', 'direction': 'Backward'}}, 'leverage': 1.0}, 'interestPeriods': {'startDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '0D', 'referenceDate': 'SpotDate'}, 'endDate': {'dateType': 'RelativeAdjustableDate', 'tenor': '10Y', 'referenceDate': 'StartDate'}, 'frequency': 'Quarterly', 'businessDayAdjustment': {'calendars': ['USA'], 'convention': 'ModifiedFollowing'}, 'rollConvention': 'Same'}, 'paymentOffset': {'tenor': '2D', 'businessDayAdjustment': {'calendars': ['USA'], 'convention': 'ModifiedFollowing'}, 'referenceDate': 'PeriodEndDate', 'direction': 'Forward'}, 'couponDayCount': 'Dcb_Actual_360', 'accrualDayCount': 'Dcb_Actual_360', 'principal': {'currency': 'USD', 'amount': 10000000.0, 'initialPrincipalExchange': False, 'finalPrincipalExchange': False, 'interimPrincipalExchange': False, 'repaymentCurrency': 'USD'}, 'payer': 'Party2', 'receiver': 'Party1'}}

    """

    try:
        logger.info("Calling create_from_tbs_template")

        response = Client().ir_swaps_resource.create_irs_from_tbs_template(
            fields=fields, template_reference=template_reference, overrides=overrides
        )

        output = response.data
        logger.info("Called create_from_tbs_template")

        return IrSwap(output)
    except Exception as err:
        logger.error("Error create_from_tbs_template")
        check_exception_and_raise(err, logger)


def create_from_vanilla_irs_template(
    *,
    template_reference: str,
    overrides: Optional[VanillaIrsOverride] = None,
    fields: Optional[str] = None,
) -> IrSwap:
    """
    Create an interest rate swap instance from a vanilla IRS template.
    This user-defined instrument includes all trade-specific details (e.g., fixed rate, spread, start date, end date), and is typically based on a general template available via the Instrument Template API.

    Parameters
    ----------
    template_reference : str
        "The identifier of the vanilla interest rate swap template (GUID or URI).
        Note that a URI must be at least 2 and at most 102 characters long, start with an alphanumeric character, and contain only alphanumeric characters, slashes and underscores.
    overrides : VanillaIrsOverride, optional
        An object that contains interest rate swap properties that can be overridden.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    IrSwap
        IrSwap

    Examples
    --------
    >>> # build the swap from 'LSEG/OIS_SOFR' template
    >>> fwd_start_sofr = create_from_vanilla_irs_template(template_reference = "LSEG/OIS_SOFR")
    >>>
    >>> fwd_start_sofr_def = IrSwapDefinitionInstrument(definition = fwd_start_sofr.definition)
    >>>
    >>> print(js.dumps(fwd_start_sofr_def.as_dict(), indent=4))
    {
        "definition": {
            "firstLeg": {
                "rate": {
                    "interestRateType": "FixedRate",
                    "rate": {
                        "value": 0.0,
                        "unit": "Percentage"
                    }
                },
                "interestPeriods": {
                    "startDate": {
                        "dateType": "RelativeAdjustableDate",
                        "tenor": "0D",
                        "referenceDate": "SpotDate"
                    },
                    "endDate": {
                        "dateType": "RelativeAdjustableDate",
                        "tenor": "10Y",
                        "referenceDate": "StartDate"
                    },
                    "frequency": "Annual",
                    "businessDayAdjustment": {
                        "calendars": [
                            "USA"
                        ],
                        "convention": "NextBusinessDay"
                    },
                    "rollConvention": "Same"
                },
                "paymentOffset": {
                    "tenor": "2D",
                    "businessDayAdjustment": {
                        "calendars": [
                            "USA"
                        ],
                        "convention": "NextBusinessDay"
                    },
                    "referenceDate": "PeriodEndDate",
                    "direction": "Forward"
                },
                "couponDayCount": "Dcb_Actual_360",
                "accrualDayCount": "Dcb_Actual_360",
                "principal": {
                    "currency": "USD",
                    "amount": 10000000.0,
                    "initialPrincipalExchange": false,
                    "finalPrincipalExchange": false,
                    "interimPrincipalExchange": false,
                    "repaymentCurrency": "USD"
                },
                "payer": "Party1",
                "receiver": "Party2"
            },
            "secondLeg": {
                "rate": {
                    "interestRateType": "FloatingRate",
                    "index": "LSEG/USD_SOFR_ON_FRBNY",
                    "spreadSchedule": [
                        {
                            "rate": {
                                "value": 0.0,
                                "unit": "BasisPoint"
                            }
                        }
                    ],
                    "resetDates": {
                        "offset": {
                            "tenor": "0D",
                            "businessDayAdjustment": {
                                "calendars": [],
                                "convention": "ModifiedFollowing"
                            },
                            "referenceDate": "PeriodEndDate",
                            "direction": "Backward"
                        }
                    },
                    "leverage": 1.0
                },
                "interestPeriods": {
                    "startDate": {
                        "dateType": "RelativeAdjustableDate",
                        "tenor": "0D",
                        "referenceDate": "SpotDate"
                    },
                    "endDate": {
                        "dateType": "RelativeAdjustableDate",
                        "tenor": "10Y",
                        "referenceDate": "StartDate"
                    },
                    "frequency": "Annual",
                    "businessDayAdjustment": {
                        "calendars": [
                            "USA"
                        ],
                        "convention": "NextBusinessDay"
                    },
                    "rollConvention": "Same"
                },
                "paymentOffset": {
                    "tenor": "2D",
                    "businessDayAdjustment": {
                        "calendars": [
                            "USA"
                        ],
                        "convention": "NextBusinessDay"
                    },
                    "referenceDate": "PeriodEndDate",
                    "direction": "Forward"
                },
                "couponDayCount": "Dcb_Actual_360",
                "accrualDayCount": "Dcb_Actual_360",
                "principal": {
                    "currency": "USD",
                    "amount": 10000000.0,
                    "initialPrincipalExchange": false,
                    "finalPrincipalExchange": false,
                    "interimPrincipalExchange": false,
                    "repaymentCurrency": "USD"
                },
                "payer": "Party2",
                "receiver": "Party1"
            }
        }
    }

    """

    try:
        logger.info("Calling create_from_vanilla_irs_template")

        response = Client().ir_swaps_resource.create_irs_from_vanilla_irs_template(
            fields=fields, template_reference=template_reference, overrides=overrides
        )

        output = response.data
        logger.info("Called create_from_vanilla_irs_template")

        return IrSwap(output)
    except Exception as err:
        logger.error("Error create_from_vanilla_irs_template")
        check_exception_and_raise(err, logger)


def _delete_by_id(instrument_id: str) -> bool:
    """
    Delete a IrSwap that exists in the platform. The IrSwap can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    instrument_id : str
        The instrument identifier.

    Returns
    --------
    bool


    Examples
    --------


    """

    try:
        logger.info(f"Deleting IrSwap with id: {instrument_id}")
        Client().ir_swap_resource.delete(instrument_id=instrument_id)
        logger.info(f"Deleted IrSwap with id: {instrument_id}")

        return True
    except Exception as err:
        logger.error(f"Error deleting IrSwap with id: {instrument_id}")
        check_exception_and_raise(err, logger)


def _load_by_id(instrument_id: str, fields: Optional[str] = None) -> IrSwap:
    """
    Access a IrSwap existing in the platform (read). The IrSwap can be identified either by its unique ID (GUID format) or by its location path (space/name).

    Parameters
    ----------
    instrument_id : str
        The instrument identifier.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    IrSwap


    Examples
    --------


    """

    try:
        logger.info(f"Opening IrSwap with id: {instrument_id}")

        response = Client().ir_swap_resource.read(instrument_id=instrument_id, fields=fields)

        output = IrSwap(response.data.definition, response.data.description)

        output._id = response.data.id

        output._location = response.data.location

        return output
    except Exception as err:
        logger.error("Error opening IrSwap:")
        check_exception_and_raise(err, logger)


def search(
    *,
    item_per_page: Optional[int] = None,
    page: Optional[int] = None,
    spaces: Optional[List[str]] = None,
    names: Optional[List[str]] = None,
    space_name_sort_order: Optional[Union[str, SortingOrderEnum]] = None,
    tags: Optional[List[str]] = None,
    fields: Optional[str] = None,
) -> List[IrSwapAsCollectionItem]:
    """
    List the IrSwaps existing in the platform (depending on permissions)

    Parameters
    ----------
    item_per_page : int, optional
        A parameter used to select the number of items allowed per page. The valid range is 1-500. If not provided, 50 will be used.
    page : int, optional
        A parameter used to define the page number to display.
    spaces : List[str], optional
        A parameter used to search for platform resources stored in a given space. Space is like a namespace where resources are stored. By default there are two spaces:
        LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space.
        If space is not specified, it will search within all spaces.
    names : List[str], optional
        A parameter used to search for platform resources with given names.
    space_name_sort_order : Union[str, SortingOrderEnum], optional
        A parameter used to sort platform resources by name based on a defined order.
    tags : List[str], optional
        A parameter used to search for platform resources with given tags.
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    List[IrSwapAsCollectionItem]
        A model template defining the partial description of the resource returned by the GET list service.

    Examples
    --------
    >>> # execute the search of IR swaps
    >>> available_swaps = search()
    >>>
    >>> print(available_swaps)
    [{'type': 'IrSwap', 'id': '186e9289-8b77-4e95-8451-534dd439f8bf', 'location': {'space': 'test', 'name': 'SwapResourceCreatdforTest'}, 'description': {'summary': '', 'tags': ['test']}}]

    """

    try:
        logger.info("Calling search")

        response = Client().ir_swaps_resource.list(
            item_per_page=item_per_page,
            page=page,
            spaces=spaces,
            names=names,
            space_name_sort_order=space_name_sort_order,
            tags=tags,
            fields=fields,
        )

        output = response.data
        logger.info("Called search")

        return output
    except Exception as err:
        logger.error("Error search.")
        check_exception_and_raise(err, logger)


def solve(
    *,
    definitions: List[IrSwapDefinitionInstrument],
    pricing_preferences: Optional[IrPricingParameters] = None,
    market_data: Optional[MarketData] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
    request_pattern: Optional[Union[str, RequestPatternEnum]] = RequestPatternEnum.SYNC,
) -> Union[IrSwapInstrumentSolveResponseFieldsResponseData, AsyncRequestResponse]:
    """
    Calculate analytics for one or more swaps not stored on the platform, by solving a variable parameter (e.g., fixed rate) provided in the request,
    so that a specified property (e.g., market value, duration) matches a target value.

    Parameters
    ----------
    definitions : List[IrSwapDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : IrPricingParameters, optional
        The parameters that control the computation of the analytics.
    market_data : MarketData, optional
        The market data used to compute the analytics.
    return_market_data : bool, optional
        Boolean property to determine if undelying market data used for calculation should be returned in the response
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'
    request_pattern : Union[str, RequestPatternEnum], optional
        Header indicating whether the request is synchronous or asynchronous polling.
        When asyncPolling is used, the operation should return a 202 Accepted response with a Location header to poll for the final result.

    Returns
    --------
    Union[IrSwapInstrumentSolveResponseFieldsResponseData, AsyncRequestResponse]


    Examples
    --------
    >>> # build the swap from 'LSEG/OIS_SOFR' template
    >>> fwd_start_sofr = create_from_vanilla_irs_template(template_reference = "LSEG/OIS_SOFR")
    >>>
    >>> # prepare the Definition Instrument
    >>> fwd_start_sofr_def = IrSwapDefinitionInstrument(definition = fwd_start_sofr.definition)
    >>>
    >>> # set a solving variable between first and second leg and Fixed Rate or Spread
    >>> solving_variable = IrSwapSolvingVariable(leg='FirstLeg', name='FixedRate')
    >>>
    >>> # Apply solving target(s)
    >>> solving_target=IrSwapSolvingTarget(market_value=IrMeasure(value=0.0))
    >>>
    >>> # Setup the solving parameter object
    >>> solving_parameters = IrSwapSolvingParameters(variable=solving_variable, target=solving_target)
    >>>
    >>> # instantiate pricing parameters
    >>> pricing_parameters = IrPricingParameters(solving_parameters=solving_parameters)
    >>>
    >>> # solve the swap par rate
    >>> solving_response_general = solve(
    >>>     definitions=[fwd_start_sofr_def],
    >>>     pricing_preferences=pricing_parameters
    >>>     )
    >>>
    >>> print(js.dumps(solving_response_general.as_dict(), indent=4))
    {
        "pricingPreferences": {
            "valuationDate": "2025-12-03",
            "reportCurrency": "USD"
        },
        "analytics": [
            {
                "solving": {
                    "result": 3.6484959229114566
                },
                "description": {
                    "instrumentTag": "",
                    "instrumentDescription": "Pay USD Annual 3.65% vs Receive USD Annual +0bp SOFR 2035-12-05",
                    "startDate": "2025-12-05",
                    "endDate": "2035-12-05",
                    "tenor": "10Y"
                },
                "valuation": {
                    "accrued": {
                        "value": 0.0,
                        "percent": 0.0,
                        "dealCurrency": {
                            "value": 0.0,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": 0.0,
                            "currency": "USD"
                        }
                    },
                    "marketValue": {
                        "value": -4.65661287307739e-10,
                        "dealCurrency": {
                            "value": -4.65661287307739e-10,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": -4.65661287307739e-10,
                            "currency": "USD"
                        }
                    },
                    "cleanMarketValue": {
                        "value": -4.65661287307739e-10,
                        "dealCurrency": {
                            "value": -4.65661287307739e-10,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": -4.65661287307739e-10,
                            "currency": "USD"
                        }
                    }
                },
                "risk": {
                    "duration": {
                        "value": -8.5292729764602
                    },
                    "modifiedDuration": {
                        "value": -8.21981997870496
                    },
                    "benchmarkHedgeNotional": {
                        "value": -9851555.83871575,
                        "currency": "USD"
                    },
                    "annuity": {
                        "value": -8420.58047395339,
                        "dealCurrency": {
                            "value": -8420.58047395339,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": -8420.58047395339,
                            "currency": "USD"
                        }
                    },
                    "dv01": {
                        "value": -8216.04252426699,
                        "bp": -8.21604252426699,
                        "dealCurrency": {
                            "value": -8216.04252426699,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": -8216.04252426699,
                            "currency": "USD"
                        }
                    },
                    "pv01": {
                        "value": -8216.04252426652,
                        "bp": -8.21604252426652,
                        "dealCurrency": {
                            "value": -8216.04252426652,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": -8216.04252426652,
                            "currency": "USD"
                        }
                    },
                    "br01": {
                        "value": 0.0,
                        "dealCurrency": {
                            "value": 0.0,
                            "currency": "USD"
                        },
                        "reportCurrency": {
                            "value": 0.0,
                            "currency": "USD"
                        }
                    }
                },
                "firstLeg": {
                    "description": {
                        "legTag": "PaidLeg",
                        "legDescription": "Pay USD Annual 3.65%",
                        "interestType": "Fixed",
                        "currency": "USD",
                        "startDate": "2025-12-05",
                        "endDate": "2035-12-05",
                        "index": ""
                    },
                    "valuation": {
                        "accrued": {
                            "value": 0.0,
                            "percent": 0.0,
                            "dealCurrency": {
                                "value": 0.0,
                                "currency": "USD"
                            },
                            "reportCurrency": {
                                "value": 0.0,
                                "currency": "USD"
                            }
                        },
                        "marketValue": {
                            "value": 3072245.3527767602,
                            "dealCurrency": {
                                "value": 3072245.3527767602,
                                "currency": "USD"
                            },
                            "reportCurrency": {
                                "value": 3072245.3527767602,
                                "currency": "USD"
                            }
                        },
                        "cleanMarketValue": {
                            "value": 3072245.3527767602,
                            "dealCurrency": {
                                "value": 3072245.3527767602,
                                "currency": "USD"
                            },
                            "reportCurrency": {
                                "value": 3072245.3527767602,
                                "currency": "USD"
                            }
                        }
                    },
                    "risk": {
                        "duration": {
                            "value": 8.529272976460197
                        },
                        "modifiedDuration": {
                            "value": 8.230105459282578
                        },
                        "benchmarkHedgeNotional": {
                            "value": 0.0,
                            "currency": "USD"
                        },
                        "annuity": {
                            "value": 8420.580473953392,
                            "dealCurrency": {
                                "value": 8420.580473953392,
                                "currency": "USD"
                            },
                            "reportCurrency": {
                                "value": 8420.580473953392,
                                "currency": "USD"
                            }
                        },
                        "dv01": {
                            "value": 8226.323278106749,
                            "bp": 8.226323278106749,
                            "dealCurrency": {
                                "value": 8226.323278106749,
                                "currency": "USD"
                            },
                            "reportCurrency": {
                                "value": 8226.323278106749,
                                "currency": "USD"
                            }
                        },
                        "pv01": {
                            "value": 1545.5316545399837,
                            "bp": 1.5455316545399838,
                            "dealCurrency": {
                                "value": 1545.5316545399837,
                                "currency": "USD"
                            },
                            "reportCurrency": {
                                "value": 1545.5316545399837,
                                "currency": "USD"
                            }
                        },
                        "br01": {
                            "value": 0.0,
                            "dealCurrency": {
                                "value": 0.0,
                                "currency": "USD"
                            },
                            "reportCurrency": {
                                "value": 0.0,
                                "currency": "USD"
                            }
                        }
                    },
                    "cashflows": [
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 3.6484959229114566,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.9653209001386095,
                            "startDate": "2025-12-05",
                            "endDate": "2026-12-07",
                            "remainingNotional": 10000000.0,
                            "interestRateType": "FixedRate",
                            "zeroRate": {
                                "value": 3.543097249667815,
                                "unit": "Percentage"
                            },
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2026-12-08"
                            },
                            "amount": {
                                "value": -371943.889919029,
                                "currency": "USD"
                            },
                            "payer": "Party1",
                            "receiver": "Party2",
                            "occurrence": "Future"
                        },
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 3.6484959229114566,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.936246039651183,
                            "startDate": "2026-12-07",
                            "endDate": "2027-12-06",
                            "remainingNotional": 10000000.0,
                            "interestRateType": "FixedRate",
                            "zeroRate": {
                                "value": 3.33014688945259,
                                "unit": "Percentage"
                            },
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2027-12-07"
                            },
                            "amount": {
                                "value": -368903.4766499361,
                                "currency": "USD"
                            },
                            "payer": "Party1",
                            "receiver": "Party2",
                            "occurrence": "Future"
                        },
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 3.6484959229114566,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.9067706628407697,
                            "startDate": "2027-12-06",
                            "endDate": "2028-12-05",
                            "remainingNotional": 10000000.0,
                            "interestRateType": "FixedRate",
                            "zeroRate": {
                                "value": 3.303716929113598,
                                "unit": "Percentage"
                            },
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2028-12-07"
                            },
                            "amount": {
                                "value": -369916.9477396338,
                                "currency": "USD"
                            },
                            "payer": "Party1",
                            "receiver": "Party2",
                            "occurrence": "Future"
                        },
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 3.6484959229114566,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.876889774085775,
                            "startDate": "2028-12-05",
                            "endDate": "2029-12-05",
                            "remainingNotional": 10000000.0,
                            "interestRateType": "FixedRate",
                            "zeroRate": {
                                "value": 3.329606764213433,
                                "unit": "Percentage"
                            },
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2029-12-07"
                            },
                            "amount": {
                                "value": -369916.9477396338,
                                "currency": "USD"
                            },
                            "payer": "Party1",
                            "receiver": "Party2",
                            "occurrence": "Future"
                        },
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 3.6484959229114566,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.8463864324567191,
                            "startDate": "2029-12-05",
                            "endDate": "2030-12-05",
                            "remainingNotional": 10000000.0,
                            "interestRateType": "FixedRate",
                            "zeroRate": {
                                "value": 3.3805388231770594,
                                "unit": "Percentage"
                            },
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2030-12-09"
                            },
                            "amount": {
                                "value": -369916.9477396338,
                                "currency": "USD"
                            },
                            "payer": "Party1",
                            "receiver": "Party2",
                            "occurrence": "Future"
                        },
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 3.6484959229114566,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.8155120608669456,
                            "startDate": "2030-12-05",
                            "endDate": "2031-12-05",
                            "remainingNotional": 10000000.0,
                            "interestRateType": "FixedRate",
                            "zeroRate": {
                                "value": 3.4478025333760876,
                                "unit": "Percentage"
                            },
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2031-12-09"
                            },
                            "amount": {
                                "value": -369916.9477396338,
                                "currency": "USD"
                            },
                            "payer": "Party1",
                            "receiver": "Party2",
                            "occurrence": "Future"
                        },
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 3.6484959229114566,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.7845302167684596,
                            "startDate": "2031-12-05",
                            "endDate": "2032-12-06",
                            "remainingNotional": 10000000.0,
                            "interestRateType": "FixedRate",
                            "zeroRate": {
                                "value": 3.521898228491094,
                                "unit": "Percentage"
                            },
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2032-12-07"
                            },
                            "amount": {
                                "value": -371943.889919029,
                                "currency": "USD"
                            },
                            "payer": "Party1",
                            "receiver": "Party2",
                            "occurrence": "Future"
                        },
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 3.6484959229114566,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.753544318950076,
                            "startDate": "2032-12-06",
                            "endDate": "2033-12-05",
                            "remainingNotional": 10000000.0,
                            "interestRateType": "FixedRate",
                            "zeroRate": {
                                "value": 3.595379518778663,
                                "unit": "Percentage"
                            },
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2033-12-07"
                            },
                            "amount": {
                                "value": -368903.4766499361,
                                "currency": "USD"
                            },
                            "payer": "Party1",
                            "receiver": "Party2",
                            "occurrence": "Future"
                        },
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 3.6484959229114566,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.7227550777494671,
                            "startDate": "2033-12-05",
                            "endDate": "2034-12-05",
                            "remainingNotional": 10000000.0,
                            "interestRateType": "FixedRate",
                            "zeroRate": {
                                "value": 3.668925025140979,
                                "unit": "Percentage"
                            },
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2034-12-07"
                            },
                            "amount": {
                                "value": -369916.9477396338,
                                "currency": "USD"
                            },
                            "payer": "Party1",
                            "receiver": "Party2",
                            "occurrence": "Future"
                        },
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 3.6484959229114566,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.6923159103223784,
                            "startDate": "2034-12-05",
                            "endDate": "2035-12-05",
                            "remainingNotional": 0.0,
                            "interestRateType": "FixedRate",
                            "zeroRate": {
                                "value": 3.7413958150893434,
                                "unit": "Percentage"
                            },
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2035-12-07"
                            },
                            "amount": {
                                "value": -369916.9477396338,
                                "currency": "USD"
                            },
                            "payer": "Party1",
                            "receiver": "Party2",
                            "occurrence": "Future"
                        }
                    ]
                },
                "secondLeg": {
                    "description": {
                        "legTag": "ReceivedLeg",
                        "legDescription": "Receive USD Annual +0bp SOFR",
                        "interestType": "Float",
                        "currency": "USD",
                        "startDate": "2025-12-05",
                        "endDate": "2035-12-05",
                        "index": "SOFR"
                    },
                    "valuation": {
                        "accrued": {
                            "value": 0.0,
                            "percent": 0.0,
                            "dealCurrency": {
                                "value": 0.0,
                                "currency": "USD"
                            },
                            "reportCurrency": {
                                "value": 0.0,
                                "currency": "USD"
                            }
                        },
                        "marketValue": {
                            "value": 3072245.35277676,
                            "dealCurrency": {
                                "value": 3072245.35277676,
                                "currency": "USD"
                            },
                            "reportCurrency": {
                                "value": 3072245.35277676,
                                "currency": "USD"
                            }
                        },
                        "cleanMarketValue": {
                            "value": 3072245.35277676,
                            "dealCurrency": {
                                "value": 3072245.35277676,
                                "currency": "USD"
                            },
                            "reportCurrency": {
                                "value": 3072245.35277676,
                                "currency": "USD"
                            }
                        }
                    },
                    "risk": {
                        "duration": {
                            "value": 0.0
                        },
                        "modifiedDuration": {
                            "value": 0.010285480577616019
                        },
                        "benchmarkHedgeNotional": {
                            "value": 0.0,
                            "currency": "USD"
                        },
                        "annuity": {
                            "value": 0.0,
                            "dealCurrency": {
                                "value": 0.0,
                                "currency": "USD"
                            },
                            "reportCurrency": {
                                "value": 0.0,
                                "currency": "USD"
                            }
                        },
                        "dv01": {
                            "value": 10.280753839761019,
                            "bp": 0.01028075383976102,
                            "dealCurrency": {
                                "value": 10.280753839761019,
                                "currency": "USD"
                            },
                            "reportCurrency": {
                                "value": 10.280753839761019,
                                "currency": "USD"
                            }
                        },
                        "pv01": {
                            "value": -6670.510869726539,
                            "bp": -6.670510869726539,
                            "dealCurrency": {
                                "value": -6670.510869726539,
                                "currency": "USD"
                            },
                            "reportCurrency": {
                                "value": -6670.510869726539,
                                "currency": "USD"
                            }
                        },
                        "br01": {
                            "value": 0.0,
                            "dealCurrency": {
                                "value": 0.0,
                                "currency": "USD"
                            },
                            "reportCurrency": {
                                "value": 0.0,
                                "currency": "USD"
                            }
                        }
                    },
                    "cashflows": [
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 3.4922020391170006,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.9653209001386095,
                            "startDate": "2025-12-05",
                            "endDate": "2026-12-07",
                            "remainingNotional": 10000000.0,
                            "interestRateType": "FloatingRate",
                            "zeroRate": {
                                "value": 3.543097249667815,
                                "unit": "Percentage"
                            },
                            "indexFixings": [
                                {
                                    "accrualEndDate": "2026-12-07",
                                    "accrualStartDate": "2025-12-05",
                                    "couponRate": {
                                        "value": 3.492202,
                                        "unit": "Percentage"
                                    },
                                    "fixingDate": "2025-12-05",
                                    "forwardSource": "ZcCurve",
                                    "referenceRate": {
                                        "value": 3.492202,
                                        "unit": "Percentage"
                                    },
                                    "spreadBp": 0.0
                                }
                            ],
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2026-12-08"
                            },
                            "amount": {
                                "value": 356010.5967655387,
                                "currency": "USD"
                            },
                            "payer": "Party2",
                            "receiver": "Party1",
                            "occurrence": "Projected"
                        },
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 3.0713328543915,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.936246039651183,
                            "startDate": "2026-12-07",
                            "endDate": "2027-12-06",
                            "remainingNotional": 10000000.0,
                            "interestRateType": "FloatingRate",
                            "zeroRate": {
                                "value": 3.33014688945259,
                                "unit": "Percentage"
                            },
                            "indexFixings": [
                                {
                                    "accrualEndDate": "2027-12-06",
                                    "accrualStartDate": "2026-12-07",
                                    "couponRate": {
                                        "value": 3.071333,
                                        "unit": "Percentage"
                                    },
                                    "fixingDate": "2026-12-07",
                                    "forwardSource": "ZcCurve",
                                    "referenceRate": {
                                        "value": 3.071333,
                                        "unit": "Percentage"
                                    },
                                    "spreadBp": 0.0
                                }
                            ],
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2027-12-07"
                            },
                            "amount": {
                                "value": 310545.877499585,
                                "currency": "USD"
                            },
                            "payer": "Party2",
                            "receiver": "Party1",
                            "occurrence": "Projected"
                        },
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 3.1964556349972,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.9067706628407697,
                            "startDate": "2027-12-06",
                            "endDate": "2028-12-05",
                            "remainingNotional": 10000000.0,
                            "interestRateType": "FloatingRate",
                            "zeroRate": {
                                "value": 3.303716929113598,
                                "unit": "Percentage"
                            },
                            "indexFixings": [
                                {
                                    "accrualEndDate": "2028-12-05",
                                    "accrualStartDate": "2027-12-06",
                                    "couponRate": {
                                        "value": 3.1964557,
                                        "unit": "Percentage"
                                    },
                                    "fixingDate": "2027-12-06",
                                    "forwardSource": "ZcCurve",
                                    "referenceRate": {
                                        "value": 3.1964557,
                                        "unit": "Percentage"
                                    },
                                    "spreadBp": 0.0
                                }
                            ],
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2028-12-07"
                            },
                            "amount": {
                                "value": 324085.08521499386,
                                "currency": "USD"
                            },
                            "payer": "Party2",
                            "receiver": "Party1",
                            "occurrence": "Projected"
                        },
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 3.3600334015592,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.876889774085775,
                            "startDate": "2028-12-05",
                            "endDate": "2029-12-05",
                            "remainingNotional": 10000000.0,
                            "interestRateType": "FloatingRate",
                            "zeroRate": {
                                "value": 3.329606764213433,
                                "unit": "Percentage"
                            },
                            "indexFixings": [
                                {
                                    "accrualEndDate": "2029-12-05",
                                    "accrualStartDate": "2028-12-05",
                                    "couponRate": {
                                        "value": 3.3600335,
                                        "unit": "Percentage"
                                    },
                                    "fixingDate": "2028-12-05",
                                    "forwardSource": "ZcCurve",
                                    "referenceRate": {
                                        "value": 3.3600335,
                                        "unit": "Percentage"
                                    },
                                    "spreadBp": 0.0
                                }
                            ],
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2029-12-07"
                            },
                            "amount": {
                                "value": 340670.0532136411,
                                "currency": "USD"
                            },
                            "payer": "Party2",
                            "receiver": "Party1",
                            "occurrence": "Projected"
                        },
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 3.5332793329013006,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.8463864324567191,
                            "startDate": "2029-12-05",
                            "endDate": "2030-12-05",
                            "remainingNotional": 10000000.0,
                            "interestRateType": "FloatingRate",
                            "zeroRate": {
                                "value": 3.3805388231770594,
                                "unit": "Percentage"
                            },
                            "indexFixings": [
                                {
                                    "accrualEndDate": "2030-12-05",
                                    "accrualStartDate": "2029-12-05",
                                    "couponRate": {
                                        "value": 3.5332794,
                                        "unit": "Percentage"
                                    },
                                    "fixingDate": "2029-12-05",
                                    "forwardSource": "ZcCurve",
                                    "referenceRate": {
                                        "value": 3.5332794,
                                        "unit": "Percentage"
                                    },
                                    "spreadBp": 0.0
                                }
                            ],
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2030-12-09"
                            },
                            "amount": {
                                "value": 358235.2656969374,
                                "currency": "USD"
                            },
                            "payer": "Party2",
                            "receiver": "Party1",
                            "occurrence": "Projected"
                        },
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 3.7319287676439004,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.8155120608669456,
                            "startDate": "2030-12-05",
                            "endDate": "2031-12-05",
                            "remainingNotional": 10000000.0,
                            "interestRateType": "FloatingRate",
                            "zeroRate": {
                                "value": 3.4478025333760876,
                                "unit": "Percentage"
                            },
                            "indexFixings": [
                                {
                                    "accrualEndDate": "2031-12-05",
                                    "accrualStartDate": "2030-12-05",
                                    "couponRate": {
                                        "value": 3.7319288,
                                        "unit": "Percentage"
                                    },
                                    "fixingDate": "2030-12-05",
                                    "forwardSource": "ZcCurve",
                                    "referenceRate": {
                                        "value": 3.7319288,
                                        "unit": "Percentage"
                                    },
                                    "spreadBp": 0.0
                                }
                            ],
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2031-12-09"
                            },
                            "amount": {
                                "value": 378376.11116389546,
                                "currency": "USD"
                            },
                            "payer": "Party2",
                            "receiver": "Party1",
                            "occurrence": "Projected"
                        },
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 3.905234767525,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.7845302167684596,
                            "startDate": "2031-12-05",
                            "endDate": "2032-12-06",
                            "remainingNotional": 10000000.0,
                            "interestRateType": "FloatingRate",
                            "zeroRate": {
                                "value": 3.521898228491094,
                                "unit": "Percentage"
                            },
                            "indexFixings": [
                                {
                                    "accrualEndDate": "2032-12-06",
                                    "accrualStartDate": "2031-12-05",
                                    "couponRate": {
                                        "value": 3.9052348,
                                        "unit": "Percentage"
                                    },
                                    "fixingDate": "2031-12-05",
                                    "forwardSource": "ZcCurve",
                                    "referenceRate": {
                                        "value": 3.9052348,
                                        "unit": "Percentage"
                                    },
                                    "spreadBp": 0.0
                                }
                            ],
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2032-12-07"
                            },
                            "amount": {
                                "value": 398116.9888004653,
                                "currency": "USD"
                            },
                            "payer": "Party2",
                            "receiver": "Party1",
                            "occurrence": "Projected"
                        },
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 4.054857952601,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.753544318950076,
                            "startDate": "2032-12-06",
                            "endDate": "2033-12-05",
                            "remainingNotional": 10000000.0,
                            "interestRateType": "FloatingRate",
                            "zeroRate": {
                                "value": 3.595379518778663,
                                "unit": "Percentage"
                            },
                            "indexFixings": [
                                {
                                    "accrualEndDate": "2033-12-05",
                                    "accrualStartDate": "2032-12-06",
                                    "couponRate": {
                                        "value": 4.0548577,
                                        "unit": "Percentage"
                                    },
                                    "fixingDate": "2032-12-06",
                                    "forwardSource": "ZcCurve",
                                    "referenceRate": {
                                        "value": 4.0548577,
                                        "unit": "Percentage"
                                    },
                                    "spreadBp": 0.0
                                }
                            ],
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2033-12-07"
                            },
                            "amount": {
                                "value": 409991.1929852122,
                                "currency": "USD"
                            },
                            "payer": "Party2",
                            "receiver": "Party1",
                            "occurrence": "Projected"
                        },
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 4.2008615397253,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.7227550777494671,
                            "startDate": "2033-12-05",
                            "endDate": "2034-12-05",
                            "remainingNotional": 10000000.0,
                            "interestRateType": "FloatingRate",
                            "zeroRate": {
                                "value": 3.668925025140979,
                                "unit": "Percentage"
                            },
                            "indexFixings": [
                                {
                                    "accrualEndDate": "2034-12-05",
                                    "accrualStartDate": "2033-12-05",
                                    "couponRate": {
                                        "value": 4.2008615,
                                        "unit": "Percentage"
                                    },
                                    "fixingDate": "2033-12-05",
                                    "forwardSource": "ZcCurve",
                                    "referenceRate": {
                                        "value": 4.2008615,
                                        "unit": "Percentage"
                                    },
                                    "spreadBp": 0.0
                                }
                            ],
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2034-12-07"
                            },
                            "amount": {
                                "value": 425920.68388881517,
                                "currency": "USD"
                            },
                            "payer": "Party2",
                            "receiver": "Party1",
                            "occurrence": "Projected"
                        },
                        {
                            "paymentType": "Interest",
                            "annualRate": {
                                "value": 4.3357394769504,
                                "unit": "Percentage"
                            },
                            "discountFactor": 0.6923159103223784,
                            "startDate": "2034-12-05",
                            "endDate": "2035-12-05",
                            "remainingNotional": 0.0,
                            "interestRateType": "FloatingRate",
                            "zeroRate": {
                                "value": 3.7413958150893434,
                                "unit": "Percentage"
                            },
                            "indexFixings": [
                                {
                                    "accrualEndDate": "2035-12-05",
                                    "accrualStartDate": "2034-12-05",
                                    "couponRate": {
                                        "value": 4.3357396,
                                        "unit": "Percentage"
                                    },
                                    "fixingDate": "2034-12-05",
                                    "forwardSource": "ZcCurve",
                                    "referenceRate": {
                                        "value": 4.3357396,
                                        "unit": "Percentage"
                                    },
                                    "spreadBp": 0.0
                                }
                            ],
                            "date": {
                                "dateType": "AdjustableDate",
                                "date": "2035-12-07"
                            },
                            "amount": {
                                "value": 439595.80807969335,
                                "currency": "USD"
                            },
                            "payer": "Party2",
                            "receiver": "Party1",
                            "occurrence": "Projected"
                        }
                    ]
                }
            }
        ]
    }

    """

    try:
        logger.info("Calling solve")

        response = check_async_request_response(
            Client().ir_swaps_resource.solve(
                fields=fields,
                request_pattern=request_pattern,
                definitions=definitions,
                pricing_preferences=pricing_preferences,
                market_data=market_data,
                return_market_data=return_market_data,
            )
        )

        output = response
        logger.info("Called solve")

        return output
    except Exception as err:
        logger.error("Error solve.")
        check_exception_and_raise(err, logger)


def solve_polling(*, operation_id: str) -> AsyncPollingResponse[IrSwapInstrumentSolveResponseFieldsResponseData]:
    """
    Polling for the response of the $solve async action

    Parameters
    ----------
    operation_id : str
        The operation identifier.

    Returns
    --------
    AsyncPollingResponse[IrSwapInstrumentSolveResponseFieldsResponseData]


    Examples
    --------


    """

    try:
        logger.info("Calling solve_polling")

        response = check_async_polling_response(Client().ir_swaps_resource.solve_polling(operation_id=operation_id))

        output = response
        logger.info("Called solve_polling")

        return output
    except Exception as err:
        logger.error("Error solve_polling.")
        check_exception_and_raise(err, logger)


def value(
    *,
    definitions: List[IrSwapDefinitionInstrument],
    pricing_preferences: Optional[IrPricingParameters] = None,
    market_data: Optional[MarketData] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
    request_pattern: Optional[Union[str, RequestPatternEnum]] = RequestPatternEnum.SYNC,
) -> Union[IrSwapInstrumentValuationResponseFieldsResponseData, AsyncRequestResponse]:
    """
    Calculate analytics for one or more swaps not stored on the platform, including valuation results, risk metrics, and other relevant measures.

    Parameters
    ----------
    definitions : List[IrSwapDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : IrPricingParameters, optional
        The parameters that control the computation of the analytics.
    market_data : MarketData, optional
        The market data used to compute the analytics.
    return_market_data : bool, optional
        Boolean property to determine if undelying market data used for calculation should be returned in the response
    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'
    request_pattern : Union[str, RequestPatternEnum], optional
        Header indicating whether the request is synchronous or asynchronous polling.
        When asyncPolling is used, the operation should return a 202 Accepted response with a Location header to poll for the final result.

    Returns
    --------
    Union[IrSwapInstrumentValuationResponseFieldsResponseData, AsyncRequestResponse]


    Examples
    --------
    >>> # build the swap from 'LSEG/OIS_SOFR' template
    >>> fwd_start_sofr = create_from_vanilla_irs_template(template_reference = "LSEG/OIS_SOFR")
    >>>
    >>> fwd_start_sofr_def = IrSwapDefinitionInstrument(definition = fwd_start_sofr.definition)
    >>>
    >>> # instantiate pricing parameters
    >>> pricing_parameters = IrPricingParameters()
    >>>
    >>> # value the swap
    >>> valuation_response = value(
    >>>     definitions=[fwd_start_sofr_def],
    >>>     pricing_preferences=pricing_parameters
    >>> )
    >>>
    >>> print(js.dumps(valuation_response.analytics[0].valuation.as_dict(), indent=4))
    {
        "accrued": {
            "value": 0.0,
            "percent": 0.0,
            "dealCurrency": {
                "value": 0.0,
                "currency": "USD"
            },
            "reportCurrency": {
                "value": 0.0,
                "currency": "USD"
            }
        },
        "marketValue": {
            "value": 3072227.3918728,
            "dealCurrency": {
                "value": 3072227.3918728,
                "currency": "USD"
            },
            "reportCurrency": {
                "value": 3072227.3918728,
                "currency": "USD"
            }
        },
        "cleanMarketValue": {
            "value": 3072227.3918728,
            "dealCurrency": {
                "value": 3072227.3918728,
                "currency": "USD"
            },
            "reportCurrency": {
                "value": 3072227.3918728,
                "currency": "USD"
            }
        }
    }

    """

    try:
        logger.info("Calling value")

        response = check_async_request_response(
            Client().ir_swaps_resource.value(
                fields=fields,
                request_pattern=request_pattern,
                definitions=definitions,
                pricing_preferences=pricing_preferences,
                market_data=market_data,
                return_market_data=return_market_data,
            )
        )

        output = response
        logger.info("Called value")

        return output
    except Exception as err:
        logger.error("Error value.")
        check_exception_and_raise(err, logger)


def value_polling(*, operation_id: str) -> AsyncPollingResponse[IrSwapInstrumentValuationResponseFieldsResponseData]:
    """
    Polling for the response of the $value async action

    Parameters
    ----------
    operation_id : str
        The operation identifier.

    Returns
    --------
    AsyncPollingResponse[IrSwapInstrumentValuationResponseFieldsResponseData]


    Examples
    --------


    """

    try:
        logger.info("Calling value_polling")

        response = check_async_polling_response(Client().ir_swaps_resource.value_polling(operation_id=operation_id))

        output = response
        logger.info("Called value_polling")

        return output
    except Exception as err:
        logger.error("Error value_polling.")
        check_exception_and_raise(err, logger)
