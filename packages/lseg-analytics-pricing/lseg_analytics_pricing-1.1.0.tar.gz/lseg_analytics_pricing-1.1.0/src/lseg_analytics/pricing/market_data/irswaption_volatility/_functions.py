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
    CurvesAndSurfacesCalibrationTypeEnum,
    CurvesAndSurfacesPriceSideEnum,
    CurvesAndSurfacesStrikeTypeEnum,
    CurvesAndSurfacesTimeStampEnum,
    CurvesAndSurfacesUnderlyingTypeEnum,
    DiscountingTypeEnum,
    FormatEnum,
    InputVolatilityTypeEnum,
    OutputVolatilityTypeEnum,
    SurfaceOutput,
    VolatilityAdjustmentTypeEnum,
    VolatilityCubeDefinition,
    VolatilityCubeSurfaceParameters,
    VolatilityCubeSurfaceRequestItem,
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
    "CurvesAndSurfacesCalibrationTypeEnum",
    "CurvesAndSurfacesPriceSideEnum",
    "CurvesAndSurfacesStrikeTypeEnum",
    "CurvesAndSurfacesTimeStampEnum",
    "CurvesAndSurfacesUnderlyingTypeEnum",
    "DiscountingTypeEnum",
    "FormatEnum",
    "InputVolatilityTypeEnum",
    "OutputVolatilityTypeEnum",
    "SurfaceOutput",
    "VolatilityAdjustmentTypeEnum",
    "VolatilityCubeDefinition",
    "VolatilityCubeSurfaceParameters",
    "VolatilityCubeSurfaceRequestItem",
    "VolatilitySurfacePoint",
    "VolatilitySurfaceResponse",
    "VolatilitySurfaceResponseItem",
    "XAxisEnum",
    "YAxisEnum",
    "ZAxisEnum",
    "calculate",
]


def calculate(
    *, universe: Optional[List[VolatilityCubeSurfaceRequestItem]] = None, fields: Optional[str] = None
) -> VolatilitySurfaceResponse:
    """
    Generates the surfaces for the definitions provided

    Parameters
    ----------
    universe : List[VolatilityCubeSurfaceRequestItem], optional

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
    >>> print("Step 1: Creating Cube Definition...")
    >>> # Select currency and reference rate for caplets
    >>> currency = "USD"
    >>> index_name = "SOFR"
    >>>
    >>> # Create surface definition object
    >>> cube_definition = sv.VolatilityCubeDefinition(
    >>>         instrument_code = currency,
    >>>         index_name = index_name,
    >>>         index_tenor  = "ON",
    >>>         # discounting_type = sv.DiscountingTypeEnum.OisDiscounting  # Options: LiborDiscounting, OisDiscounting
    >>>         )
    >>> print(f"   Instrument: {cube_definition.instrument_code}")
    >>>
    >>> # Create the surface parameters - optional
    >>> print("Step 2: Configuring Cube Parameters...")
    >>> cube_parameters = sv.VolatilityCubeSurfaceParameters(
    >>>         calculation_date = dt.datetime.strptime("2025-01-18", "%Y-%m-%d"),
    >>>         x_axis = sv.XAxisEnum.STRIKE,                                     # Options: DATE, DELTA, EXPIRY, MONEYNESS, STRIKE, TENOR
    >>>         y_axis = sv.YAxisEnum.TENOR,                                      # Options: same as X-axis
    >>>         z_axis = sv.YAxisEnum.EXPIRY                                      # Options: same as X-axis
    >>>     )
    >>> print(f"   Surface Parameters: {cube_parameters}")
    >>>
    >>> # Create the main request object with basic configuration
    >>> print("Step 3: Create request item...")
    >>> request_item = sv.VolatilityCubeSurfaceRequestItem(
    >>>         surface_tag = f"{currency}_{index_name}_Swaption_volatility_cube",
    >>>         underlying_definition = cube_definition,
    >>>         surface_parameters = cube_parameters,
    >>>         underlying_type = sv.CurvesAndSurfacesUnderlyingTypeEnum.Swaption,
    >>>         surface_layout = sv.SurfaceOutput(
    >>>             format = sv.FormatEnum.LIST,  # Options: LIST (MATRIX and NDIMENSIONAL_ARRAY return an error)
    >>>         )
    >>>     )
    >>> print(f"   Request Item: {json.dumps(request_item.as_dict(), indent=4)}")
    Step 1: Creating Cube Definition...
       Instrument: USD
    Step 2: Configuring Cube Parameters...
       Surface Parameters: {'calculationDate': '2025-01-18T00:00:00Z', 'xAxis': 'Strike', 'yAxis': 'Tenor', 'zAxis': 'Expiry'}
    Step 3: Create request item...
       Request Item: {
        "surfaceTag": "USD_SOFR_Swaption_volatility_cube",
        "underlyingDefinition": {
            "instrumentCode": "USD",
            "indexName": "SOFR",
            "indexTenor": "ON"
        },
        "surfaceParameters": {
            "calculationDate": "2025-01-18T00:00:00Z",
            "xAxis": "Strike",
            "yAxis": "Tenor",
            "zAxis": "Expiry"
        },
        "underlyingType": "Swaption",
        "surfaceLayout": {
            "format": "List"
        }
    }


    >>> # Execute the calculation using the calculate function
    >>> # The 'universe' parameter accepts a list of request items for batch processing
    >>> try:
    >>>     response = sv.calculate(universe=[request_item])
    >>>
    >>>     # Display response structure information
    >>>     surface_data = response['data'][0]
    >>>     if 'surface' in surface_data:
    >>>         print(f"   Calculation successful!")
    >>>         print(f"   Cube data points available: {len(surface_data['surface'])}")
    >>>     else:
    >>>         print("   No cube data found in response")
    >>>
    >>> except Exception as e:
    >>>     print(f"   Calculation failed: {str(e)}")
    >>>     raise
       Calculation successful!
       Cube data points available: 9315

    """

    try:
        logger.info("Calling calculate")

        response = Client().irswaption_volatility.calculate(fields=fields, universe=universe)

        output = response
        logger.info("Called calculate")

        return output
    except Exception as err:
        logger.error("Error calculate.")
        check_exception_and_raise(err, logger)
