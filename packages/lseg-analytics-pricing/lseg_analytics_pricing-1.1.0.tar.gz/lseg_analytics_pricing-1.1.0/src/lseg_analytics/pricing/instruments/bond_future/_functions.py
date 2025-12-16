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
    AccruedCalculationMethodEnum,
    AccruedRoundingEnum,
    AccruedRoundingTypeEnum,
    AdjustInterestToPaymentDateEnum,
    AmortizationFrequencyEnum,
    AmortizationItemDefinition,
    AssignmentKey,
    BenchmarkYieldSelectionModeEnum,
    BondDefinition,
    BondFutureAnalyticsResponseData,
    BondFutureAnalyticsResponseWithError,
    BondFutureCalculationResponse,
    BondFutureDefinition,
    BondFutureDefinitionInstrument,
    BondFutureDescription,
    BondFutureNominalMeasures,
    BondFuturePricingAnalysis,
    BondFuturePricingParameters,
    BondFutureUnderlyingContract,
    BondFutureValuation,
    BondPricingParameters,
    BondRoundingParameters,
    CreditSpreadTypeEnum,
    DefaultBondQuote,
    DiscountMarketDataAssignmentKey,
    DiscountMarketDataAssignmentKeyAssignmentItem,
    FinancialContractResponse,
    FinancialContractStubRuleEnum,
    ForwardMarketDataAssignmentKey,
    ForwardMarketDataAssignmentKeyAssignmentItem,
    FxPriceSideEnum,
    Header,
    HullWhiteParameters,
    IndexAverageMethodEnum,
    IndexCompoundingMethodEnum,
    IndexResetFrequencyEnum,
    InflationModeEnum,
    InnerError,
    InterestCalculationMethodEnum,
    InterestPaymentFrequencyEnum,
    InterestRateAssignment,
    InterestTypeEnum,
    IPAAmortizationTypeEnum,
    IPADirectionEnum,
    IPADividendTypeEnum,
    IPAIndexObservationMethodEnum,
    IPAVolatilityTypeEnum,
    MarketDataAssignments,
    MarketDataQps,
    PaymentBusinessDayConventionEnum,
    PaymentRollConventionEnum,
    PriceRoundingEnum,
    PriceRoundingTypeEnum,
    PriceSideEnum,
    ProjectedIndexCalculationMethodEnum,
    QuotationModeEnum,
    QuoteFallbackLogicEnum,
    RedemptionDateTypeEnum,
    ServiceError,
    SpreadRoundingEnum,
    SpreadRoundingTypeEnum,
    TypeEnum,
    VolatilityTermStructureTypeEnum,
    YieldRoundingEnum,
    YieldRoundingTypeEnum,
    YieldTypeEnum,
)
from lseg_analytics.pricing._client.client import Client

from ._logger import logger

__all__ = [
    "AccruedCalculationMethodEnum",
    "AccruedRoundingEnum",
    "AccruedRoundingTypeEnum",
    "AdjustInterestToPaymentDateEnum",
    "AmortizationFrequencyEnum",
    "AmortizationItemDefinition",
    "AssignmentKey",
    "BenchmarkYieldSelectionModeEnum",
    "BondDefinition",
    "BondFutureAnalyticsResponseData",
    "BondFutureAnalyticsResponseWithError",
    "BondFutureCalculationResponse",
    "BondFutureDefinition",
    "BondFutureDefinitionInstrument",
    "BondFutureDescription",
    "BondFutureNominalMeasures",
    "BondFuturePricingAnalysis",
    "BondFuturePricingParameters",
    "BondFutureUnderlyingContract",
    "BondFutureValuation",
    "BondPricingParameters",
    "BondRoundingParameters",
    "CreditSpreadTypeEnum",
    "DefaultBondQuote",
    "DiscountMarketDataAssignmentKey",
    "DiscountMarketDataAssignmentKeyAssignmentItem",
    "FinancialContractResponse",
    "FinancialContractStubRuleEnum",
    "ForwardMarketDataAssignmentKey",
    "ForwardMarketDataAssignmentKeyAssignmentItem",
    "FxPriceSideEnum",
    "Header",
    "HullWhiteParameters",
    "IPAAmortizationTypeEnum",
    "IPADirectionEnum",
    "IPADividendTypeEnum",
    "IPAIndexObservationMethodEnum",
    "IPAVolatilityTypeEnum",
    "IndexAverageMethodEnum",
    "IndexCompoundingMethodEnum",
    "IndexResetFrequencyEnum",
    "InflationModeEnum",
    "InterestCalculationMethodEnum",
    "InterestPaymentFrequencyEnum",
    "InterestRateAssignment",
    "InterestTypeEnum",
    "MarketDataAssignments",
    "MarketDataQps",
    "PaymentBusinessDayConventionEnum",
    "PaymentRollConventionEnum",
    "PriceRoundingEnum",
    "PriceRoundingTypeEnum",
    "PriceSideEnum",
    "ProjectedIndexCalculationMethodEnum",
    "QuotationModeEnum",
    "QuoteFallbackLogicEnum",
    "RedemptionDateTypeEnum",
    "SpreadRoundingEnum",
    "SpreadRoundingTypeEnum",
    "TypeEnum",
    "VolatilityTermStructureTypeEnum",
    "YieldRoundingEnum",
    "YieldRoundingTypeEnum",
    "YieldTypeEnum",
    "price",
]


def price(
    *,
    definitions: List[BondFutureDefinitionInstrument],
    pricing_preferences: Optional[BondFuturePricingParameters] = None,
    market_data: Optional[MarketDataQps] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> BondFutureCalculationResponse:
    """
    Calculate BondFuture analytics

    Parameters
    ----------
    definitions : List[BondFutureDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : BondFuturePricingParameters, optional
        The parameters that control the computation of the analytics.
    market_data : MarketDataQps, optional
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

    Returns
    --------
    BondFutureCalculationResponse
        A model template describing the analytics response returned for an instrument provided as part of the request.

    Examples
    --------
    >>> # 1.Define an underlying Bond instrument
    >>> fixed_bond_definition = bf.BondDefinition(
    >>>     notional_ccy = "EUR",
    >>>     issue_date = dt.datetime.strptime("2025-01-01", "%Y-%m-%d"),
    >>>     end_date = dt.datetime.strptime("2030-01-01", "%Y-%m-%d"),
    >>>     fixed_rate_percent = 2,
    >>>     interest_payment_frequency = bf.InterestPaymentFrequencyEnum.QUARTERLY,
    >>>     interest_calculation_method = bf.InterestCalculationMethodEnum.DCB_ACTUAL_ACTUAL
    >>>
    >>> )
    >>>
    >>> underlying_bond = bf.BondFutureUnderlyingContract(
    >>>         instrument_definition = fixed_bond_definition,
    >>>         instrument_type = "Bond"
    >>> )
    >>> print("1 - Underlying Bond definition created")
    >>>
    >>> # 2.Define Future instrument
    >>> future_definition = bf.BondFutureDefinition(
    >>>     instrument_code = "FOATc1",  # Mandatory field
    >>>     underlying_instruments = [underlying_bond]
    >>> )
    >>> print("2 - Future instrument defined")
    >>>
    >>> # 3.Create the Future Instrument from the defintion
    >>> future_instrument = bf.BondFutureDefinitionInstrument(definition = future_definition)
    >>> print("3 - Future Instrument created")
    >>>
    >>> # 4. Configure pricing parameters
    >>> pricing_params = bf.BondFuturePricingParameters(
    >>>     valuation_date = dt.datetime.strptime("2025-07-18", "%Y-%m-%d"),
    >>> )
    >>> print("4 - Pricing parameters configured")
    1 - Underlying Bond definition created
    2 - Future instrument defined
    3 - Future Instrument created
    4 - Pricing parameters configured


    >>> #  Execute the calculation using the price() function
    >>> # The 'definitions' parameter accepts a list of instruments definitions for batch processing
    >>>
    >>> # Execute the calculation using the price() function with error handling
    >>> try:
    >>>     # The 'definitions' parameter accepts a list of request items for batch processing
    >>>     response = bf.price(
    >>>         definitions=[future_instrument],
    >>>         pricing_preferences=pricing_params
    >>>     )
    >>>     errors = [a.error for a in response.data.analytics if a.error]
    >>>     if errors:
    >>>         raise Exception(errors[0].message)
    >>>     print("Bond Future pricing execution completed")
    >>> except Exception as e:
    >>>     print(f"Price Calculation failed: {str(e)}")
    >>>     raise
    Bond Future pricing execution completed

    """

    try:
        logger.info("Calling price")

        response = Client().bond_future.price(
            fields=fields,
            definitions=definitions,
            pricing_preferences=pricing_preferences,
            market_data=market_data,
            return_market_data=return_market_data,
        )

        output = response
        logger.info("Called price")

        return output
    except Exception as err:
        logger.error("Error price.")
        check_exception_and_raise(err, logger)
