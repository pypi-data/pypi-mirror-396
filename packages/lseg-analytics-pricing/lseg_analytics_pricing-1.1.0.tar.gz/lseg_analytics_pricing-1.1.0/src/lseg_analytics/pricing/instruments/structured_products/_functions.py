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
    AmericanMonteCarloMethodEnum,
    BasketItem,
    BasketUnderlying,
    Calibration,
    CalibrationTypeEnum,
    FinancialContractAssetClassEnum,
    FinancialContractResponse,
    GenericNumericalMethod,
    Header,
    InnerError,
    IPAModelParameters,
    MarketDataQps,
    MethodEnum,
    ModelDefinition,
    ModelNameEnum,
    NameTypeValue,
    ProductTypeEnum,
    ServiceError,
    StructuredProductsAnalyticsResponseData,
    StructuredProductsAnalyticsResponseWithError,
    StructuredProductsCalculationResponse,
    StructuredProductsCashflows,
    StructuredProductsDefinition,
    StructuredProductsDefinitionInstrument,
    StructuredProductsDescription,
    StructuredProductsGreeks,
    StructuredProductsPricingAnalysis,
    StructuredProductsPricingParameters,
    StructuredProductsValuation,
    TypeEnum,
)
from lseg_analytics.pricing._client.client import Client

from ._logger import logger

__all__ = [
    "AmericanMonteCarloMethodEnum",
    "BasketItem",
    "BasketUnderlying",
    "Calibration",
    "CalibrationTypeEnum",
    "FinancialContractAssetClassEnum",
    "FinancialContractResponse",
    "GenericNumericalMethod",
    "Header",
    "IPAModelParameters",
    "MarketDataQps",
    "MethodEnum",
    "ModelDefinition",
    "ModelNameEnum",
    "NameTypeValue",
    "ProductTypeEnum",
    "StructuredProductsAnalyticsResponseData",
    "StructuredProductsAnalyticsResponseWithError",
    "StructuredProductsCalculationResponse",
    "StructuredProductsCashflows",
    "StructuredProductsDefinition",
    "StructuredProductsDefinitionInstrument",
    "StructuredProductsDescription",
    "StructuredProductsGreeks",
    "StructuredProductsPricingAnalysis",
    "StructuredProductsPricingParameters",
    "StructuredProductsValuation",
    "TypeEnum",
    "price",
]


def price(
    *,
    definitions: List[StructuredProductsDefinitionInstrument],
    pricing_preferences: Optional[StructuredProductsPricingParameters] = None,
    market_data: Optional[MarketDataQps] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> StructuredProductsCalculationResponse:
    """
    Calculate StructuredProducts analytics

    Parameters
    ----------
    definitions : List[StructuredProductsDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : StructuredProductsPricingParameters, optional
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
    StructuredProductsCalculationResponse
        A model template describing the analytics response returned for an instrument provided as part of the request.

    Examples
    --------
    >>> # 1. Create SP definition object
    >>>
    >>> tarf_definition = sp.StructuredProductsDefinition(
    >>>     deal_ccy = "EUR",
    >>>     instrument_tag = "TARF_Target_KO",
    >>>     inputs = [
    >>>         sp.NameTypeValue(name="Underlying", type = "string", value="USDEUR"),
    >>>         sp.NameTypeValue(name="StartDate", type = "date", value= dt.date(2022, 1, 25)),
    >>>         sp.NameTypeValue(name="EndDate", type = "string", value="StartDate + 1Y"),
    >>>         sp.NameTypeValue(name="Frequency", type = "string", value="3M"),
    >>>         sp.NameTypeValue(name="Notional", type = "string", value="100000"),
    >>>         sp.NameTypeValue(name="Strike", type = "string", value="0.8"),
    >>>         sp.NameTypeValue(name="KnockOutRate", type = "string", value="1.02"),
    >>>         sp.NameTypeValue(name="IsKnockOutEvent", type = "string", value="FX[t] >= KnockOutRate"),
    >>>         sp.NameTypeValue(name="IsRedemptionEvent", type = "string", value="Sum[t] >= ProfitTarget"),
    >>>         sp.NameTypeValue(name="ProfitTarget", type = "string", value="4%"),
    >>>         sp.NameTypeValue(name="ResidualProfitTarget", type = "string", value="Max(ProfitTarget - Sum[t-1], 0)"),
    >>>         sp.NameTypeValue(name="KO_Payment", type = "string", value="Settlement[t]"),
    >>>     ],
    >>>     payoff_description = [
    >>> 					[
    >>>                         "Schedule Type",
    >>>                         "Schedule description",
    >>>                         "FX",
    >>>                         "Coupon",
    >>>                         "Settlement",
    >>>                         "Sum",
    >>>                         "Alive",
    >>>                         "KO_Amount",
    >>>                         "Price"
    >>>                     ],
    >>>                     [
    >>>                         "AtDate",
    >>>                         "StartDate",
    >>>                         "",
    >>>                         "",
    >>>                         "0",
    >>>                         "",
    >>>                         "IF(ProfitTarget >= 0, 1, 0)",
    >>>                         "",
    >>>                         ""
    >>>                     ],
    >>>                     [
    >>>                         "OnSchedule",
    >>>                         "DateTable(StartDate + Frequency, EndDate, Frequency, ResetGap := 0b)",
    >>>                         "FxSpot(Underlying)",
    >>>                         "IF(IsKnockOutEvent, ResidualProfitTarget, FX[t] - Strike)",
    >>>                         "Coupon[t] * Notional",
    >>>                         "Sum[LastDate] + max(Coupon[t],0)",
    >>>                         "If(IsRedemptionEvent or IsKnockOutEvent, 0, Alive[LastDate-1])",
    >>>                         "Alive[LastDate-1] * (1-Alive[LastDate]) * KO_Payment",
    >>>                         "Receive (Alive[t] * Settlement[t] + KO_Amount[t])"
    >>>                     ],
    >>>                     [
    >>>                         "AtDate",
    >>>                         "EndDate",
    >>>                         "FxSpot(Underlying)",
    >>>                         "IF(IsKnockOutEvent, ResidualProfitTarget, FX[t] - Strike)",
    >>>                         "Coupon[LastDate] * Notional",
    >>>                         "Sum[LastDate] + max(Coupon[t],0)",
    >>>                         "If(IsRedemptionEvent or IsKnockOutEvent, 0, Alive[LastDate-1])",
    >>>                         "Alive[LastDate-1] * (1-Alive[LastDate]) * KO_Payment",
    >>>                         "Receive (Alive[LastDate] * Settlement[t] + KO_Amount[t])"
    >>>                     ]
    >>> 				]
    >>> )
    >>>
    >>>
    >>> # 2. Create SP instrument definition object
    >>>
    >>> tarf_target_ko = sp.StructuredProductsDefinitionInstrument(definition = tarf_definition)
    >>> print("Instrument definition created")
    >>>
    >>>
    >>> # 3. Create SP parameters object - optional
    >>>
    >>> tarf_pricing_params = sp.StructuredProductsPricingParameters(
    >>>     valuation_date= dt.date(2022, 3, 16),  # Set your desired valuation date
    >>>     numerical_method = sp.GenericNumericalMethod(method="MonteCarlo"),
    >>>     models=[sp.ModelDefinition(
    >>>             underlying_code = "USDEUR",
    >>>             underlying_tag = "USDEUR",
    >>>             underlying_currency = "EUR",
    >>>             asset_class = "ForeignExchange",
    >>>             model_name= "Heston")]
    >>> )
    >>> print("Pricing parameters configured")
    Instrument definition created
    Pricing parameters configured


    >>> # Execute the calculation using the price() function
    >>> # The 'definitions' parameter accepts a list of instruments definitions for batch processing
    >>>
    >>> response = sp.price(
    >>>     definitions=[tarf_target_ko],
    >>>     pricing_preferences=tarf_pricing_params,
    >>>     market_data=None,
    >>>     return_market_data=True,  # or False
    >>>     fields=None  # or specify fields as a string
    >>> )
    >>>
    >>> print("Pricing execution completed")
    Pricing execution completed

    """

    try:
        logger.info("Calling price")

        response = Client().structured_products.price(
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
