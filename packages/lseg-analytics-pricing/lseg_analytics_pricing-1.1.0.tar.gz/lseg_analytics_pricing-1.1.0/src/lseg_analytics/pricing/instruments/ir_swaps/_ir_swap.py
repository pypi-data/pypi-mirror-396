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
    CrossCurencySwapOverride,
    CurencyBasisSwapOverride,
    Description,
    IrPricingParameters,
    IrSwapAsCollectionItem,
    IrSwapDefinition,
    IrSwapDefinitionInstrument,
    IrSwapInstrumentSolveResponseFieldsOnResourceResponseData,
    IrSwapInstrumentSolveResponseFieldsResponseData,
    IrSwapInstrumentValuationResponseFieldsOnResourceResponseData,
    IrSwapInstrumentValuationResponseFieldsResponseData,
    Location,
    MarketData,
    RequestPatternEnum,
    ResourceType,
    SortingOrderEnum,
    TenorBasisSwapOverride,
    VanillaIrsOverride,
)
from lseg_analytics.pricing._client.client import Client

from ._logger import logger


class IrSwap(ResourceBase):
    """
    IrSwap object.

    Contains all the necessary information to identify and define a IrSwap instance.

    Attributes
    ----------
    type : Union[str, ResourceType], optional
        Property defining the type of the resource.
    id : str, optional
        Unique identifier of the IrSwap.
    location : Location
        Object defining the location of the IrSwap in the platform.
    description : Description, optional
        Object defining metadata for the IrSwap.
    definition : IrSwapDefinition
        Object defining the IrSwap.

    See Also
    --------
    IrSwap.solve : Calculate analytics for an interest rate swap stored on the platform, by solving a variable parameter (e.g., fixed rate) provided in the request,
        so that a specified property (e.g., market value, duration) matches a target value.
        Provide an instrument ID in the request to perform the solving.
    IrSwap.solvePolling : Polling for the response of the $solve async action
    IrSwap.value : Calculate analytics for an interest rate swap stored on the platform, including valuation results, risk metrics, and other relevant measures.
        Provide an instrument ID in the request to perform the valuation.
    IrSwap.valuePolling : Polling for the response of the $value async action

    Examples
    --------


    """

    _definition_class = IrSwapDefinition

    def __init__(self, definition: IrSwapDefinition, description: Optional[Description] = None):
        """
        IrSwap constructor

        Parameters
        ----------
        definition : IrSwapDefinition
            Object defining the IrSwap.
        description : Description, optional
            Object defining metadata for the IrSwap.

        Examples
        --------


        """
        self.definition: IrSwapDefinition = definition
        self.type: Optional[Union[str, ResourceType]] = "IrSwap"
        if description is None:
            self.description: Optional[Description] = Description(tags=[])
        else:
            self.description: Optional[Description] = description
        self._location: Location = Location(name="")
        self._id: Optional[str] = None

    @property
    def id(self):
        """
        Returns the IrSwap id

        Parameters
        ----------


        Returns
        --------
        str
            Unique identifier of the IrSwap.

        Examples
        --------


        """
        return self._id

    @id.setter
    def id(self, value):
        raise AttributeError("id is read only")

    @property
    def location(self):
        """
        Returns the IrSwap location

        Parameters
        ----------


        Returns
        --------
        Location
            Object defining the location of the IrSwap in the platform.

        Examples
        --------


        """
        return self._location

    @location.setter
    def location(self, value):
        raise AttributeError("location is read only")

    def _create(self, location: Location) -> None:
        """
        Save a new IrSwap in the platform

        Parameters
        ----------
        location : Location
            Object defining the location of the IrSwap in the platform.

        Returns
        --------
        None


        Examples
        --------


        """

        try:
            logger.info("Creating IrSwap")

            response = Client().ir_swaps_resource.create(
                location=location,
                description=self.description,
                definition=self.definition,
            )

            self._id = response.data.id

            self._location = response.data.location
            logger.info(f"IrSwap created with id: {self._id}")
        except Exception as err:
            logger.error("Error creating IrSwap:")
            raise err

    def _overwrite(self) -> None:
        """
        Overwrite a IrSwap that exists in the platform. The IrSwap can be identified either by its unique ID (GUID format) or by its location path (space/name).

        Parameters
        ----------


        Returns
        --------
        None


        Examples
        --------


        """
        logger.info(f"Overwriting IrSwap with id: {self._id}")
        Client().ir_swap_resource.overwrite(
            instrument_id=self._id,
            location=self._location,
            description=self.description,
            definition=self.definition,
        )

    def solve(
        self,
        *,
        pricing_preferences: Optional[IrPricingParameters] = None,
        market_data: Optional[MarketData] = None,
        return_market_data: Optional[bool] = None,
        fields: Optional[str] = None,
        request_pattern: Optional[Union[str, RequestPatternEnum]] = RequestPatternEnum.SYNC,
    ) -> Union[IrSwapInstrumentSolveResponseFieldsOnResourceResponseData, AsyncRequestResponse]:
        """
        Calculate analytics for an interest rate swap stored on the platform, by solving a variable parameter (e.g., fixed rate) provided in the request,
        so that a specified property (e.g., market value, duration) matches a target value.
        Provide an instrument ID in the request to perform the solving.

        Parameters
        ----------
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
        Union[IrSwapInstrumentSolveResponseFieldsOnResourceResponseData, AsyncRequestResponse]


        Examples
        --------
        >>> # build the swap from 'LSEG/OIS_SOFR' template
        >>> fwd_start_sofr = create_from_vanilla_irs_template(template_reference = "LSEG/OIS_SOFR")
        >>>
        >>> # Swap needs to be saved in order for the solve class method to be executable
        >>> fwd_start_sofr.save(name="sofr_fwd_start_swap_exm")
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
        >>> solving_response_object = fwd_start_sofr.solve(pricing_preferences=pricing_parameters)
        >>>
        >>> delete(name="sofr_fwd_start_swap_exm")
        >>>
        >>> print(js.dumps(solving_response_object.analytics.as_dict(), indent=4))
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

        """

        try:
            logger.info("Calling solve for irSwap with id")
            check_id(self._id)

            response = check_async_request_response(
                Client().ir_swap_resource.solve(
                    instrument_id=self._id,
                    fields=fields,
                    request_pattern=request_pattern,
                    pricing_preferences=pricing_preferences,
                    market_data=market_data,
                    return_market_data=return_market_data,
                )
            )

            output = response
            logger.info("Called solve for irSwap with id")

            return output
        except Exception as err:
            logger.error("Error solve for irSwap with id.")
            check_exception_and_raise(err, logger)

    def solve_polling(
        self, *, operation_id: str
    ) -> AsyncPollingResponse[IrSwapInstrumentSolveResponseFieldsOnResourceResponseData]:
        """
        Polling for the response of the $solve async action

        Parameters
        ----------
        operation_id : str
            The operation identifier.

        Returns
        --------
        AsyncPollingResponse[IrSwapInstrumentSolveResponseFieldsOnResourceResponseData]


        Examples
        --------


        """

        try:
            logger.info("Calling solve_polling for irSwap with id")

            response = check_async_polling_response(Client().ir_swap_resource.solve_polling(operation_id=operation_id))

            output = response
            logger.info("Called solve_polling for irSwap with id")

            return output
        except Exception as err:
            logger.error("Error solve_polling for irSwap with id.")
            check_exception_and_raise(err, logger)

    def value(
        self,
        *,
        pricing_preferences: Optional[IrPricingParameters] = None,
        market_data: Optional[MarketData] = None,
        return_market_data: Optional[bool] = None,
        fields: Optional[str] = None,
        request_pattern: Optional[Union[str, RequestPatternEnum]] = RequestPatternEnum.SYNC,
    ) -> Union[
        IrSwapInstrumentValuationResponseFieldsOnResourceResponseData,
        AsyncRequestResponse,
    ]:
        """
        Calculate analytics for an interest rate swap stored on the platform, including valuation results, risk metrics, and other relevant measures.
        Provide an instrument ID in the request to perform the valuation.

        Parameters
        ----------
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
        Union[IrSwapInstrumentValuationResponseFieldsOnResourceResponseData, AsyncRequestResponse]


        Examples
        --------
        >>> # build the swap from 'LSEG/OIS_SOFR' template
        >>> fwd_start_sofr = create_from_vanilla_irs_template(template_reference = "LSEG/OIS_SOFR")
        >>>
        >>> # Swap needs to be saved in order for the value class method to be executable
        >>> fwd_start_sofr.save(name="sofr_fwd_start_swap_exm")
        >>>
        >>> # instantiate pricing parameters
        >>> pricing_parameters = IrPricingParameters()
        >>>
        >>> # solve the swap par rate
        >>> valuing_response_object = fwd_start_sofr.value(pricing_preferences=pricing_parameters)
        >>>
        >>> delete(name="sofr_fwd_start_swap_exm")
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
            logger.info("Calling value for irSwap with id")
            check_id(self._id)

            response = check_async_request_response(
                Client().ir_swap_resource.value(
                    instrument_id=self._id,
                    fields=fields,
                    request_pattern=request_pattern,
                    pricing_preferences=pricing_preferences,
                    market_data=market_data,
                    return_market_data=return_market_data,
                )
            )

            output = response
            logger.info("Called value for irSwap with id")

            return output
        except Exception as err:
            logger.error("Error value for irSwap with id.")
            check_exception_and_raise(err, logger)

    def value_polling(
        self, *, operation_id: str
    ) -> AsyncPollingResponse[IrSwapInstrumentValuationResponseFieldsOnResourceResponseData]:
        """
        Polling for the response of the $value async action

        Parameters
        ----------
        operation_id : str
            The operation identifier.

        Returns
        --------
        AsyncPollingResponse[IrSwapInstrumentValuationResponseFieldsOnResourceResponseData]


        Examples
        --------


        """

        try:
            logger.info("Calling value_polling for irSwap with id")

            response = check_async_polling_response(Client().ir_swap_resource.value_polling(operation_id=operation_id))

            output = response
            logger.info("Called value_polling for irSwap with id")

            return output
        except Exception as err:
            logger.error("Error value_polling for irSwap with id.")
            check_exception_and_raise(err, logger)

    def save(self, *, name: Optional[str] = None, space: Optional[str] = None) -> bool:
        """
        Save IrSwap instance in the platform store.

        Parameters
        ----------
        name : str, optional
            The IrSwap name. The name parameter must be specified when the object is first created. Thereafter it is optional. For first creation, name must follow the pattern '^[A-Za-z0-9_]{1,50}$'.
        space : str, optional
            The space where the IrSwap is stored. Space is like a namespace where resources are stored. By default there are two spaces:
            LSEG is reserved for LSEG maintained resources, HOME is reserved for user's default space. If space is not specified, HOME will be used.

        Returns
        --------
        bool, optional
            True, if saved successfully, otherwise None


        Examples
        --------
        >>> # build the swap from 'LSEG/OIS_SOFR' template
        >>> fwd_start_sofr = create_from_vanilla_irs_template(template_reference = "LSEG/OIS_SOFR")
        >>>
        >>> swap_id = "SOFR_OIS_1Y2Y"
        >>>
        >>> swap_space = "HOME"
        >>>
        >>> try:
        >>>     # If the instrument does not exist in HOME space, we can save it
        >>>     fwd_start_sofr.save(name=swap_id, space=swap_space)
        >>>     print(f"Instrument {swap_id} saved in {swap_space} space.")
        >>> except:
        >>>     # Check if the instrument already exists in HOME space
        >>>     fwd_start_sofr = load(name=swap_id, space=swap_space)
        >>>     print(f"Instrument {swap_id} already exists in {swap_space} space.")
        Instrument SOFR_OIS_1Y2Y saved in HOME space.

        """
        try:
            logger.info("Saving IrSwap")
            if self._id:
                if name and name != self._location.name or (space and space != self._location.space):
                    raise LibraryException("When saving an existing resource, you may not change the name or space")
                self._overwrite()
                logger.info("IrSwap saved")
            elif name:
                location = Location(name=name, space=space)
                self._create(location=location)
                logger.info(f"IrSwap saved to space: {self._location.space} name: {self._location.name}")
            else:
                raise LibraryException("When saving for the first time, name must be defined.")
            return True
        except Exception as err:
            logger.info("IrSwap save failed")
            check_exception_and_raise(err, logger)

    def clone(self) -> "IrSwap":
        """
        Return the same object, without id, name and space

        Parameters
        ----------


        Returns
        --------
        IrSwap
            The cloned IrSwap object


        Examples
        --------


        """
        definition = self._definition_class()
        definition._data = copy.deepcopy(self.definition._data)
        description = None
        if self.description:
            description = Description()
            description._data = copy.deepcopy(self.description._data)
        return self.__class__(definition=definition, description=description)
