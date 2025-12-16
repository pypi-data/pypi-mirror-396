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
    CdsAnalyticsResponseData,
    CdsAnalyticsResponseWithError,
    CdsCalculationResponse,
    CdsCashflows,
    CdsConventionEnum,
    CdsDefinition,
    CdsDefinitionInstrument,
    CdsDescription,
    CdsNominalMeasures,
    CdsPricingAnalysis,
    CdsPricingParameters,
    CdsSpreadMeasures,
    CdsValuation,
    DocClauseEnum,
    EndDateMovingConventionEnum,
    FinancialContractResponse,
    FinancialContractStubRuleEnum,
    Header,
    InnerError,
    InterestCalculationMethodEnum,
    InterestPaymentFrequencyEnum,
    IPADirectionEnum,
    MarketDataQps,
    PaymentBusinessDayConventionEnum,
    PremiumLegDefinition,
    ProtectionLegDefinition,
    SeniorityEnum,
    ServiceError,
    StartDateMovingConventionEnum,
    TypeEnum,
)
from lseg_analytics.pricing._client.client import Client

from ._logger import logger

__all__ = [
    "AccruedCalculationMethodEnum",
    "CdsAnalyticsResponseData",
    "CdsAnalyticsResponseWithError",
    "CdsCalculationResponse",
    "CdsCashflows",
    "CdsConventionEnum",
    "CdsDefinition",
    "CdsDefinitionInstrument",
    "CdsDescription",
    "CdsNominalMeasures",
    "CdsPricingAnalysis",
    "CdsPricingParameters",
    "CdsSpreadMeasures",
    "CdsValuation",
    "DocClauseEnum",
    "EndDateMovingConventionEnum",
    "FinancialContractResponse",
    "FinancialContractStubRuleEnum",
    "Header",
    "IPADirectionEnum",
    "InterestCalculationMethodEnum",
    "InterestPaymentFrequencyEnum",
    "MarketDataQps",
    "PaymentBusinessDayConventionEnum",
    "PremiumLegDefinition",
    "ProtectionLegDefinition",
    "SeniorityEnum",
    "StartDateMovingConventionEnum",
    "TypeEnum",
    "price",
]


def price(
    *,
    definitions: List[CdsDefinitionInstrument],
    pricing_preferences: Optional[CdsPricingParameters] = None,
    market_data: Optional[MarketDataQps] = None,
    return_market_data: Optional[bool] = None,
    fields: Optional[str] = None,
) -> CdsCalculationResponse:
    """
    Calculate Cds analytics

    Parameters
    ----------
    definitions : List[CdsDefinitionInstrument]
        An array of objects describing a curve or an instrument.
        Please provide either a full definition (for a user-defined curve/instrument), or reference to a curve/instrument definition saved in the platform, or the code identifying the existing curve/instrument.
    pricing_preferences : CdsPricingParameters, optional
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
    CdsCalculationResponse
        A model template describing the analytics response returned for an instrument provided as part of the request.

    Examples
    --------
    >>> # Create CDS definition with instrument code (RIC)
    >>> cds_definition = cds.CdsDefinition(
    >>>     instrument_code="BNPP5YEUAM=R"                                          # BNP Paribas 5Y EUR CDS RIC
    >>> )
    >>>
    >>> # Create CDS instrument from definition
    >>> cds_instrument = cds.CdsDefinitionInstrument(
    >>>     definition=cds_definition
    >>> )
    >>>
    >>> print("CDS instrument created from RIC")
    >>>
    >>> # Configure pricing parameters, optional
    >>> pricing_params = cds.CdsPricingParameters(
    >>>     valuation_date = dt.datetime.strptime("2023-03-01", "%Y-%m-%d"),          # Valuation date
    >>> )
    >>> print("Pricing parameters configured")
    CDS instrument created from RIC
    Pricing parameters configured


    >>> # Execute the calculation using the price() function with error handling
    >>> try:
    >>>     # The 'definitions' parameter accepts a list of request items for batch processing
    >>>     response = cds.price(
    >>>         definitions=[cds_instrument],
    >>>         pricing_preferences=pricing_params,
    >>>         fields="accruedAmountInDealCcy, upfrontAmountInDealCcy, MarketValueInDealCcy, cleanMarketValueInDealCcy"  # optional
    >>>     )
    >>>     errors = [a.error for a in response.data.analytics if a.error]
    >>>     if errors:
    >>>         raise Exception(errors[0].message)
    >>>     print("CDS pricing execution completed")
    >>> except Exception as e:
    >>>     print(f"Price Calculation failed: {str(e)}")
    >>>     raise
    CDS pricing execution completed

    """

    try:
        logger.info("Calling price")

        response = Client().cds.price(
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
