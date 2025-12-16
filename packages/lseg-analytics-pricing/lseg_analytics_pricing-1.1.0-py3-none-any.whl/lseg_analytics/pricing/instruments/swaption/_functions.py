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
    AdjustInterestToPaymentDateEnum,
    AmortizationFrequencyEnum,
    AmortizationItemDefinition,
    BermudanSwaptionDefinition,
    CancellableDefinition,
    ExerciseScheduleTypeEnum,
    FinancialContractResponse,
    FinancialContractStubRuleEnum,
    Header,
    IndexAverageMethodEnum,
    IndexCompoundingMethodEnum,
    IndexPriceSideEnum,
    IndexResetFrequencyEnum,
    IndexResetTypeEnum,
    IndexSpreadCompoundingMethodEnum,
    InnerError,
    InputFlow,
    InterestCalculationConventionEnum,
    InterestCalculationMethodEnum,
    InterestPaymentFrequencyEnum,
    InterestRateScheduleItem,
    InterestTypeEnum,
    IPAAmortizationTypeEnum,
    IPABuySellEnum,
    IPADirectionEnum,
    IPAExerciseStyleEnum,
    IPAIndexObservationMethodEnum,
    MarketDataQps,
    NotionalExchangeEnum,
    OptionOwnerEnum,
    PaymentBusinessDayConventionEnum,
    PaymentRollConventionEnum,
    PremiumSettlementTypeEnum,
    PriceSideEnum,
    ServiceError,
    SettlementTypeEnum,
    StubRateCalculationParameters,
    SwapDefinition,
    SwapLegDefinition,
    SwaptionAnalyticsResponseData,
    SwaptionAnalyticsResponseWithError,
    SwaptionCalculationResponse,
    SwaptionCashflows,
    SwaptionDefinition,
    SwaptionDefinitionInstrument,
    SwaptionDescription,
    SwaptionGreeks,
    SwaptionPricingAnalysis,
    SwaptionPricingParameters,
    SwaptionTypeEnum,
    SwaptionValuation,
    TypeEnum,
)
from lseg_analytics.pricing._client.client import Client

from ._logger import logger

__all__ = [
    "AccruedCalculationMethodEnum",
    "AdjustInterestToPaymentDateEnum",
    "AmortizationFrequencyEnum",
    "AmortizationItemDefinition",
    "BermudanSwaptionDefinition",
    "CancellableDefinition",
    "ExerciseScheduleTypeEnum",
    "FinancialContractResponse",
    "FinancialContractStubRuleEnum",
    "Header",
    "IPAAmortizationTypeEnum",
    "IPABuySellEnum",
    "IPADirectionEnum",
    "IPAExerciseStyleEnum",
    "IPAIndexObservationMethodEnum",
    "IndexAverageMethodEnum",
    "IndexCompoundingMethodEnum",
    "IndexPriceSideEnum",
    "IndexResetFrequencyEnum",
    "IndexResetTypeEnum",
    "IndexSpreadCompoundingMethodEnum",
    "InputFlow",
    "InterestCalculationConventionEnum",
    "InterestCalculationMethodEnum",
    "InterestPaymentFrequencyEnum",
    "InterestRateScheduleItem",
    "InterestTypeEnum",
    "MarketDataQps",
    "NotionalExchangeEnum",
    "OptionOwnerEnum",
    "PaymentBusinessDayConventionEnum",
    "PaymentRollConventionEnum",
    "PremiumSettlementTypeEnum",
    "PriceSideEnum",
    "SettlementTypeEnum",
    "StubRateCalculationParameters",
    "SwapDefinition",
    "SwapLegDefinition",
    "SwaptionAnalyticsResponseData",
    "SwaptionAnalyticsResponseWithError",
    "SwaptionCalculationResponse",
    "SwaptionCashflows",
    "SwaptionDefinition",
    "SwaptionDefinitionInstrument",
    "SwaptionDescription",
    "SwaptionGreeks",
    "SwaptionPricingAnalysis",
    "SwaptionPricingParameters",
    "SwaptionTypeEnum",
    "SwaptionValuation",
    "TypeEnum",
    "price",
]


def price(
    *,
    definitions: List[SwaptionDefinitionInstrument],
    pricing_preferences: Optional[SwaptionPricingParameters] = None,
    market_data: Optional[MarketDataQps] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> SwaptionCalculationResponse:
    """
    Calculate Swaption analytics

    Parameters
    ----------
    definitions : List[SwaptionDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : SwaptionPricingParameters, optional
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
    SwaptionCalculationResponse
        A model template describing the analytics response returned for an instrument provided as part of the request.

    Examples
    --------
    >>> print("Step 1: Creating Swaption Definition...")
    >>>
    >>> # Define a European payer swaption (protection against rising rates)
    >>> swaption_definition = sw.SwaptionDefinition(
    >>>     # Core Swaption Parameters
    >>>     buy_sell=sw.IPABuySellEnum.BUY,                            # Buy swaption protection. Options: BUY, SELL
    >>>     swaption_type=sw.SwaptionTypeEnum.PAYER,                   # Payer swaption (pay fixed, receive floating). Options: PAYER, RECEIVER
    >>>     exercise_style=sw.IPAExerciseStyleEnum.EURO,               # European exercise style. Options: EURO, AMER, BERM
    >>>
    >>>     # Option Timing
    >>>     start_date=dt.datetime(2025, 7, 18),                       # Option start date (defaults to valuation_date)
    >>>     end_date=dt.datetime(2026, 1, 15),                         # Option expiry date
    >>>     # Alternative: tenor="6M",                                 # Or use tenor instead of end_date
    >>>
    >>>     # Financial Terms
    >>>     notional_amount=10_000_000,                                # $10M notional (default: 1,000,000)
    >>>     strike_percent=3.50,                                       # 3.50% strike rate (fixed rate of underlying swap)
    >>>
    >>>     # Settlement Configuration
    >>>     settlement_type=sw.SettlementTypeEnum.PHYSICAL,           # Physical settlement. Options: PHYSICAL, CASH, CCP
    >>>     premium_settlement_type=sw.PremiumSettlementTypeEnum.SPOT, # Premium settlement timing. Options: SPOT, FORWARD, SCHEDULE
    >>>     delivery_date=dt.datetime(2026, 1, 17),                   # Settlement date (optional, defaults to end_date)
    >>>
    >>>     # Optional Parameters
    >>>     instrument_tag="USD_5Y_PAYER_SWAPTION",                   # User-defined identifier (max 40 chars)
    >>>     spread_vs_atm_in_bp=0.0,                                  # Spread vs ATM in basis points (for pre-trade scenarios)
    >>>
    >>>     # Underlying swap details (using SwapDefinition). Detailed swap definition setups are covered in IR Swap SDK
    >>>     underlying_definition=sw.SwapDefinition(
    >>>         template="OIS_SOFR",                                   # Standard USD SOFR swap template
    >>>         start_date=dt.datetime(2026, 1, 17),                   # Swap start (T+2 from option expiry)
    >>>         end_date=dt.datetime(2031, 1, 17),                     # 5Y swap tenor in date format
    >>>         instrument_tag="USD_5Y_SOFR_Underlying_Swap"           # Tag for underlying swap
    >>>     ),
    >>>
    >>> )
    >>>
    >>> # Display comprehensive information about the created swaption
    >>> print(f"   Swaption Type: {swaption_definition.swaption_type}")
    >>> print(f"   Exercise Style: {swaption_definition.exercise_style}")
    >>> print(f"   Buy/Sell: {swaption_definition.buy_sell}")
    >>> print(f"   Notional Amount: ${swaption_definition.notional_amount:,.0f}")
    >>> print(f"   Strike Rate: {swaption_definition.strike_percent}%")
    >>> print(f"   Option Start: {swaption_definition.start_date.strftime('%Y-%m-%d')}")
    >>> print(f"   Option Expiry: {swaption_definition.end_date.strftime('%Y-%m-%d')}")
    >>> print(f"   Settlement Type: {swaption_definition.settlement_type}")
    >>> print(f"   Premium Settlement: {swaption_definition.premium_settlement_type}")
    >>> print(f"   Underlying Template: {swaption_definition.underlying_definition.template}")
    >>> print(f"   Instrument Tag: {swaption_definition.instrument_tag}")
    >>> print()
    >>>
    >>> print("Step 2: Creating Instrument Object...")
    >>> swaption_instrument = sw.SwaptionDefinitionInstrument(definition=swaption_definition)
    >>> print("   Instrument container created for pricing")
    >>> print()
    >>>
    >>> print("Step 3: Configuring Pricing Parameters...")
    >>> pricing_params = sw.SwaptionPricingParameters(
    >>>     valuation_date=dt.datetime(2025, 7, 18),                   # Pricing date
    >>>     price_side=sw.PriceSideEnum.MID                            # Use mid-market prices. Options: BID, ASK, MID, LAST
    >>> )
    >>> print(f"   Valuation Date: {pricing_params.valuation_date.strftime('%Y-%m-%d')}")
    >>> print(f"   Price Side: {pricing_params.price_side}")
    Step 1: Creating Swaption Definition...
       Swaption Type: SwaptionTypeEnum.PAYER
       Exercise Style: IPAExerciseStyleEnum.EURO
       Buy/Sell: IPABuySellEnum.BUY
       Notional Amount: $10,000,000
       Strike Rate: 3.5%
       Option Start: 2025-07-18
       Option Expiry: 2026-01-15
       Settlement Type: SettlementTypeEnum.PHYSICAL
       Premium Settlement: PremiumSettlementTypeEnum.SPOT
       Underlying Template: OIS_SOFR
       Instrument Tag: USD_5Y_PAYER_SWAPTION

    Step 2: Creating Instrument Object...
       Instrument container created for pricing

    Step 3: Configuring Pricing Parameters...
       Valuation Date: 2025-07-18
       Price Side: PriceSideEnum.MID


    >>> # Execute the calculation using the price() function
    >>> # The 'definitions' parameter accepts a list of instrument definitions for batch processing
    >>>
    >>> try:
    >>>     response = sw.price(
    >>>         definitions=[swaption_instrument],
    >>>         pricing_preferences=pricing_params,
    >>>         fields="MarketValueInDealCcy, premiumPercent, premiumBp, deltaPercent, gammaPercent, vegaPercent, thetaPercent" # optional, used to build the tabular data explained below
    >>>     )
    >>>
    >>>     # Display response structure information
    >>>     analytics_data = response['data']['analytics'][0]
    >>>     if analytics_data['error'] == {}:
    >>>         print("   Calculation successful!")
    >>>         valuation_data = analytics_data.get('valuation', {})
    >>>     else:
    >>>         print(f"   Pricing error: {analytics_data['error']}")
    >>>
    >>> except Exception as e:
    >>>     print(f"   Calculation failed: {str(e)}")
    >>>     raise
       Calculation successful!

    """

    try:
        logger.info("Calling price")

        response = Client().swaption.price(
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
