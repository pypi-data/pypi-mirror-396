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
    CapletsStrippingDefinition,
    CapletsStrippingSurfaceParameters,
    CapletsStrippingSurfaceRequestItem,
    CurvesAndSurfacesPriceSideEnum,
    CurvesAndSurfacesTimeStampEnum,
    CurvesAndSurfacesUnderlyingTypeEnum,
    DiscountingTypeEnum,
    FormatEnum,
    InputVolatilityTypeEnum,
    MaturityFilter,
    StrikeFilter,
    StrikeFilterRange,
    SurfaceFilters,
    SurfaceOutput,
    VolatilityAdjustmentTypeEnum,
    VolatilitySurfacePoint,
    VolatilitySurfaceResponse,
    VolatilitySurfaceResponseItem,
    XAxisEnum,
    YAxisEnum,
    ZAxisEnum,
)
from lseg_analytics.pricing._client.client import Client

from ._logger import logger

__all__ = [
    "CapletsStrippingDefinition",
    "CapletsStrippingSurfaceParameters",
    "CapletsStrippingSurfaceRequestItem",
    "CurvesAndSurfacesPriceSideEnum",
    "CurvesAndSurfacesTimeStampEnum",
    "CurvesAndSurfacesUnderlyingTypeEnum",
    "DiscountingTypeEnum",
    "FormatEnum",
    "InputVolatilityTypeEnum",
    "MaturityFilter",
    "StrikeFilter",
    "StrikeFilterRange",
    "SurfaceFilters",
    "SurfaceOutput",
    "VolatilityAdjustmentTypeEnum",
    "VolatilitySurfacePoint",
    "VolatilitySurfaceResponse",
    "VolatilitySurfaceResponseItem",
    "XAxisEnum",
    "YAxisEnum",
    "ZAxisEnum",
    "calculate",
]


def calculate(
    *, universe: Optional[List[CapletsStrippingSurfaceRequestItem]] = None, fields: Optional[str] = None
) -> VolatilitySurfaceResponse:
    """
    Generates the surfaces for the definitions provided

    Parameters
    ----------
    universe : List[CapletsStrippingSurfaceRequestItem], optional

    fields : str, optional
        A parameter used to select the fields to return in response. If not provided, all fields will be returned.
        Some usage examples:
        1. Simply enumerating the fields, separating them by ',', e.g. 'fields=//please insert the selected fields here, e.g., field1, field2 //'
        2. Using parentheses to indicate nesting, e.g. 'fields= //please insert the selected field and subfields here, e.g., field1(subfield1, subfield2), field2(subfield3)//’
        3. Using forward slash '/' to indicate nesting, e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1/subfield1, field1/subfield2, field2/subfield3//’ (same result as example above)
        4. Operators can even be combined (forward slashes in brackets, not the way around), e.g. 'fields=//please insert the selected field and subfields here, e.g.,  field1(subfield1/subsubfield1), field2/subfield2//'

    Returns
    --------
    VolatilitySurfaceResponse


    Examples
    --------
    >>> print("Step 1: Creating Surface Definition...")
    >>> # Select currency and reference rate for caplets
    >>> currency = "USD"
    >>> index_name = "SOFR"
    >>>
    >>> # Create surface definition object
    >>> surface_definition = cv.CapletsStrippingDefinition(
    >>>         instrument_code = currency,
    >>>         index_name = index_name,
    >>>         reference_caplet_tenor = "ON"
    >>>         # discounting_type = cv.DiscountingTypeEnum.OisDiscounting  # Options: LiborDiscounting, OisDiscounting
    >>>         )
    >>> print(f"   Instrument: {surface_definition.instrument_code}")
    >>>
    >>>
    >>> print("Step 2: Configuring Surface Parameters...")
    >>> surface_parameters = cv.CapletsStrippingSurfaceParameters(
    >>>         calculation_date = dt.datetime.strptime("2025-01-18", "%Y-%m-%d"),
    >>>         x_axis = cv.XAxisEnum.STRIKE,                                    # Options: DATE, DELTA, EXPIRY, MONEYNESS, STRIKE, TENOR
    >>>         y_axis = cv.YAxisEnum.TENOR                                      # Options: same as X-axis
    >>>     )
    >>> print(f"   Surface Parameters: {surface_parameters}")
    >>>
    >>>
    >>> print("Step 3: Create request item...")
    >>> # Create the main request object with basic configuration
    >>> request_item = cv.CapletsStrippingSurfaceRequestItem(
    >>>         surface_tag = f"{currency}_CAPLET_VOLSURFACE",
    >>>         underlying_definition = surface_definition,
    >>>         surface_parameters = surface_parameters,
    >>>         underlying_type = cv.CurvesAndSurfacesUnderlyingTypeEnum.Cap,
    >>>         surface_layout = cv.SurfaceOutput(
    >>>             format = cv.FormatEnum.Matrix,  # Options: List, Matrix
    >>>         )
    >>>     )
    >>> print(f"   Request Item: {json.dumps(request_item.as_dict(), indent=4)}")
    Step 1: Creating Surface Definition...
       Instrument: USD
    Step 2: Configuring Surface Parameters...
       Surface Parameters: {'calculationDate': '2025-01-18T00:00:00Z', 'xAxis': 'Strike', 'yAxis': 'Tenor'}
    Step 3: Create request item...
       Request Item: {
        "surfaceTag": "USD_CAPLET_VOLSURFACE",
        "underlyingDefinition": {
            "instrumentCode": "USD",
            "indexName": "SOFR",
            "referenceCapletTenor": "ON"
        },
        "surfaceParameters": {
            "calculationDate": "2025-01-18T00:00:00Z",
            "xAxis": "Strike",
            "yAxis": "Tenor"
        },
        "underlyingType": "Cap",
        "surfaceLayout": {
            "format": "Matrix"
        }
    }


    >>> # Execute the calculation using the calculate function
    >>> # The 'universe' parameter accepts a list of request items for batch processing
    >>> try:
    >>>     response = cv.calculate(universe=[request_item])
    >>>
    >>>     # Display response structure information
    >>>     surface_data = response['data'][0]
    >>>     if 'surface' in surface_data:
    >>>         print(f"   Surface Calculation successful!")
    >>>         print(f"   Surface data points available: {len(surface_data['surface']) - 1} x {len(surface_data['surface'][0]) - 1}")
    >>>     else:
    >>>         print("   No surface data found in response")
    >>>
    >>> except Exception as e:
    >>>     print(f"   Surface Calculation failed: {str(e)}")
    >>>     raise
       Surface Calculation successful!
       Surface data points available: 14 x 25

    """

    try:
        logger.info("Calling calculate")

        response = Client().ircaplet_volatility.calculate(fields=fields, universe=universe)

        output = response
        logger.info("Called calculate")

        return output
    except Exception as err:
        logger.error("Error calculate.")
        check_exception_and_raise(err, logger)
