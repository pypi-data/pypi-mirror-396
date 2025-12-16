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
    BenchmarkYieldSelectionModeEnum,
    BondAnalyticsResponseData,
    BondAnalyticsResponseWithError,
    BondCalculationResponse,
    BondCashflows,
    BondDefinition,
    BondDefinitionInstrument,
    BondDescription,
    BondEffectiveMeasures,
    BondNominalMeasures,
    BondPricingAnalysis,
    BondPricingParameters,
    BondRoundingParameters,
    BondSpreadMeasures,
    BondValuation,
    CreditSpreadTypeEnum,
    DefaultBondQuote,
    FinancialContractResponse,
    FinancialContractStubRuleEnum,
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
    InterestTypeEnum,
    IPAAmortizationTypeEnum,
    IPADirectionEnum,
    IPADividendTypeEnum,
    IPAIndexObservationMethodEnum,
    IPAVolatilityTypeEnum,
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
    "BenchmarkYieldSelectionModeEnum",
    "BondAnalyticsResponseData",
    "BondAnalyticsResponseWithError",
    "BondCalculationResponse",
    "BondCashflows",
    "BondDefinition",
    "BondDefinitionInstrument",
    "BondDescription",
    "BondEffectiveMeasures",
    "BondNominalMeasures",
    "BondPricingAnalysis",
    "BondPricingParameters",
    "BondRoundingParameters",
    "BondSpreadMeasures",
    "BondValuation",
    "CreditSpreadTypeEnum",
    "DefaultBondQuote",
    "FinancialContractResponse",
    "FinancialContractStubRuleEnum",
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
    "InterestTypeEnum",
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
    definitions: List[BondDefinitionInstrument],
    pricing_preferences: Optional[BondPricingParameters] = None,
    market_data: Optional[MarketDataQps] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> BondCalculationResponse:
    """
    Calculate Bond analytics

    Parameters
    ----------
    definitions : List[BondDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : BondPricingParameters, optional
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
    BondCalculationResponse
        A model template describing the analytics response returned for an instrument provided as part of the request.

    Examples
    --------
    >>> # Example 1: Fixed rate bond definition
    >>>
    >>> bond_definition_fixed_rate_user_defined = bd.BondDefinition(
    >>>     # Core Bond Parameters
    >>>         # Face value/Par value
    >>>     notional_amount=1_000_000,                                 # $1M face value (default: 1,000,000)
    >>>     notional_ccy="USD",                                        # USD currency
    >>>
    >>>         # Coupon Rate and Type
    >>>     fixed_rate_percent=4.25,                                   # 4.25% annual coupon rate
    >>>     interest_type=bd.InterestTypeEnum.FIXED,                   # Fixed rate bond. Options: FIXED, FLOAT
    >>>
    >>>         # Bond Timing
    >>>     issue_date=dt.datetime(2020, 3, 15),                       # Bond issue date
    >>>     end_date=dt.datetime(2025, 3, 15),                         # 5-year maturity in date format (Or use tenor directly instead of end_date: )
    >>>
    >>>         # Payment Structure
    >>>     interest_payment_frequency=bd.InterestPaymentFrequencyEnum.SEMI_ANNUAL,  # Semi-annual coupons. Options: ANNUAL, SEMI_ANNUAL, QUARTERLY, MONTHLY, etc.
    >>>     first_regular_payment_date=dt.datetime(2020, 9, 15),      # First coupon payment date
    >>>
    >>>     # Market Conventions
    >>>     interest_calculation_method=bd.InterestCalculationMethodEnum.DCB_30_360,  # 30/360 day count. Options: DCB_30_360, DCB_ACTUAL_360, DCB_ACTUAL_365, etc.
    >>>     payment_business_day_convention=bd.PaymentBusinessDayConventionEnum.MODIFIED_FOLLOWING,  # Business day adjustment. Options: MODIFIED_FOLLOWING, NEXT_BUSINESS_DAY, PREVIOUS_BUSINESS_DAY
    >>>     payment_business_days="USA",                               # US holiday calendar
    >>>
    >>>     # Optional Parameters
    >>>     instrument_tag="USD_5Y_BOND_4.25",                         # User-defined identifier (max 40 chars)
    >>>     stub_rule=bd.FinancialContractStubRuleEnum.MATURITY,       # Stub period alignment. Options: ISSUE, MATURITY
    >>>     is_perpetual=False,                                        # Non-perpetual bond
    >>> )
    >>>
    >>>
    >>> # Display comprehensive information about the created bond
    >>> print(f"✓ Fixed rate Bond:")
    >>> print(f"   Bond Type: {bond_definition_fixed_rate_user_defined.interest_type}")
    >>> print(f"   Notional Amount: {bond_definition_fixed_rate_user_defined.notional_ccy} {bond_definition_fixed_rate_user_defined.notional_amount:,.0f}")
    >>> print(f"   Coupon Rate: {bond_definition_fixed_rate_user_defined.fixed_rate_percent}%")
    >>> print(f"   Payment Frequency: {bond_definition_fixed_rate_user_defined.interest_payment_frequency}")
    >>> print(f"   Issue Date: {bond_definition_fixed_rate_user_defined.issue_date.strftime('%Y-%m-%d')}")
    >>> print(f"   Maturity Date: {bond_definition_fixed_rate_user_defined.end_date.strftime('%Y-%m-%d')}")
    >>> print(f"   Day Count: {bond_definition_fixed_rate_user_defined.interest_calculation_method}")
    >>> print(f"   Business Day Convention: {bond_definition_fixed_rate_user_defined.payment_business_day_convention}")
    >>> print(f"   Calendar: {bond_definition_fixed_rate_user_defined.payment_business_days}")
    >>> print(f"   Instrument Tag: {bond_definition_fixed_rate_user_defined.instrument_tag}")
    >>> print()
    ✓ Fixed rate Bond:
       Bond Type: InterestTypeEnum.FIXED
       Notional Amount: USD 1,000,000
       Coupon Rate: 4.25%
       Payment Frequency: InterestPaymentFrequencyEnum.SEMI_ANNUAL
       Issue Date: 2020-03-15
       Maturity Date: 2025-03-15
       Day Count: InterestCalculationMethodEnum.DCB_30_360
       Business Day Convention: PaymentBusinessDayConventionEnum.MODIFIED_FOLLOWING
       Calendar: USA
       Instrument Tag: USD_5Y_BOND_4.25



    >>> # Example 2: Floating rate bond definition
    >>>
    >>> floating_bond = bd.BondDefinition(
    >>>     notional_amount=1_000_000,
    >>>     notional_ccy="USD",
    >>>     interest_type=bd.InterestTypeEnum.FLOAT,                    # FLOAT instead of FIXED
    >>>
    >>>     # Floating Rate Parameters
    >>>     index_fixing_ric="USDSOFR=",                                # Reference rate RIC
    >>>     spread_bp=150,                                              # 150bp spread over SOFR
    >>>     index_reset_frequency=bd.IndexResetFrequencyEnum.MONTHLY,   # Monthly resets
    >>>
    >>>     issue_date=dt.datetime(2023, 3, 15),
    >>>     end_date=dt.datetime(2033, 3, 15),
    >>>     interest_payment_frequency=bd.InterestPaymentFrequencyEnum.QUARTERLY,
    >>>     interest_calculation_method=bd.InterestCalculationMethodEnum.DCB_30_360,
    >>>
    >>>     instrument_tag="USD_10Y_BOND_SOFR_150",
    >>> )
    >>>
    >>> # Display comprehensive information about the created bond
    >>> print(f"✓ Floating rate Bond:")
    >>> print(f"   Bond Type: {floating_bond.interest_type}")
    >>> print(f"   Notional Amount: {floating_bond.notional_ccy} {floating_bond.notional_amount:,.0f}")
    >>> print(f"   Floating interest rate index: {floating_bond.index_fixing_ric}")
    >>> print(f"   Spread in addition to floating rate: {floating_bond.spread_bp}bps")
    >>> print(f"   Payment Frequency: {floating_bond.interest_payment_frequency}")
    >>> print(f"   Issue Date: {floating_bond.issue_date.strftime('%Y-%m-%d')}")
    >>> print(f"   Maturity Date: {floating_bond.end_date.strftime('%Y-%m-%d')}")
    >>> print(f"   Day Count: {floating_bond.interest_calculation_method}")
    >>> print(f"   Instrument Tag: {floating_bond.instrument_tag}")
    ✓ Floating rate Bond:
       Bond Type: InterestTypeEnum.FLOAT
       Notional Amount: USD 1,000,000
       Floating interest rate index: USDSOFR=
       Spread in addition to floating rate: 150.0bps
       Payment Frequency: InterestPaymentFrequencyEnum.QUARTERLY
       Issue Date: 2023-03-15
       Maturity Date: 2033-03-15
       Day Count: InterestCalculationMethodEnum.DCB_30_360
       Instrument Tag: USD_10Y_BOND_SOFR_150


    >>> # Example 3: Zero coupon bond definition
    >>>
    >>> zero_coupon_bond = bd.BondDefinition(
    >>>     notional_amount=1_000_000,
    >>>     notional_ccy="USD",
    >>>     fixed_rate_percent=0.0,                                     # No coupon payments
    >>>     interest_payment_frequency=bd.InterestPaymentFrequencyEnum.ZERO,  # Zero frequency
    >>>     interest_calculation_method=bd.InterestCalculationMethodEnum.DCB_30_360,
    >>>
    >>>     issue_date=dt.datetime(2020, 3, 15),
    >>>     end_date=dt.datetime(2025, 3, 15),
    >>>
    >>>     instrument_tag="USD_5Y_BOND_ZC"
    >>> )
    >>>
    >>> # Display comprehensive information about the created bond
    >>> print(f"✓ Zero Coupon Bond:")
    >>> print(f"   Notional Amount: {zero_coupon_bond.notional_ccy} {zero_coupon_bond.notional_amount:,.0f}")
    >>> print(f"   Coupon Rate: {zero_coupon_bond.fixed_rate_percent}%")
    >>> print(f"   Payment Frequency: {zero_coupon_bond.interest_payment_frequency}")
    >>> print(f"   Issue Date: {zero_coupon_bond.issue_date.strftime('%Y-%m-%d')}")
    >>> print(f"   Maturity Date: {zero_coupon_bond.end_date.strftime('%Y-%m-%d')}")
    >>> print(f"   Day Count: {zero_coupon_bond.interest_calculation_method}")
    >>> print(f"   Business Day Convention: {zero_coupon_bond.payment_business_day_convention}")
    >>> print(f"   Calendar: {zero_coupon_bond.payment_business_days}")
    >>> print(f"   Instrument Tag: {zero_coupon_bond.instrument_tag}")
    ✓ Zero Coupon Bond:
       Notional Amount: USD 1,000,000
       Coupon Rate: 0.0%
       Payment Frequency: InterestPaymentFrequencyEnum.ZERO
       Issue Date: 2020-03-15
       Maturity Date: 2025-03-15
       Day Count: InterestCalculationMethodEnum.DCB_30_360
       Business Day Convention: None
       Calendar: None
       Instrument Tag: USD_5Y_BOND_ZC


    >>> # Method 2: Definition Using existing market instruments
    >>>
    >>> bond_definition_isin = bd.BondDefinition(
    >>>     instrument_code="US912810RQ31",   # ISIN, RIC, CUSIP
    >>>     instrument_tag="BOND_ISIN=US912810RQ31")


    >>> bond_instrument1 = bd.BondDefinitionInstrument(definition=bond_definition_fixed_rate_user_defined)
    >>> bond_instrument2 = bd.BondDefinitionInstrument(definition=floating_bond)
    >>> bond_instrument3 = bd.BondDefinitionInstrument(definition=zero_coupon_bond)
    >>> bond_instrument4 = bd.BondDefinitionInstrument(definition=bond_definition_isin)
    >>>
    >>> print("   Bond instrument containers created for pricing")
       Bond instrument containers created for pricing


    >>> pricing_params = bd.BondPricingParameters(
    >>>     valuation_date=dt.datetime(2023, 7, 18),                   # Pricing date
    >>>     price_side=bd.PriceSideEnum.MID,                           # Use mid-market prices. Options: BID, ASK, MID, LAST
    >>>     report_ccy="USD",                                          # Reporting currency for analytics
    >>>     settlement_convention="2WD",                               # T+2 settlement convention
    >>>
    >>>     # Optional pricing inputs (comment out to use market data)
    >>>     # yield_percent=4.50,                                      # Input yield to calculate price
    >>>     # clean_price=98.50,                                       # Input price to calculate yield
    >>> )
    >>>
    >>> print(f"   Valuation Date: {pricing_params.valuation_date.strftime('%Y-%m-%d')}")
    >>> print(f"   Price Side: {pricing_params.price_side}")
    >>> print(f"   Report Currency: {pricing_params.report_ccy}")
    >>> print(f"   Settlement Convention: {pricing_params.settlement_convention}")
       Valuation Date: 2023-07-18
       Price Side: PriceSideEnum.MID
       Report Currency: USD
       Settlement Convention: 2WD


    >>> # setup response fields
    >>>
    >>> basic_fields = "InstrumentTag, NotionalCcy, MarketValueInDealCcy, ReportCcy, MarketValueInReportCcy"
    >>> additional_fields = "cleanPricePercent, dirtyPricePercent, yieldPercent, ModifiedDuration, convexity, DV01Bp"
    >>> fields = basic_fields + "," + additional_fields


    >>> # Execute the calculation using the price() function
    >>> # The 'definitions' parameter accepts a list of instrument definitions for batch processing
    >>>
    >>> try:
    >>>     response = bd.price(
    >>>         definitions=[bond_instrument1, bond_instrument2, bond_instrument3, bond_instrument4],
    >>>         pricing_preferences=pricing_params,
    >>>         fields=fields
    >>>     )
    >>>
    >>>     # Display response structure information
    >>>     analytics_data = response['data']['analytics'][0]
    >>>     if analytics_data['error'] == {}:
    >>>         print("   Calculation successful!")
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

        response = Client().bond.price(
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
