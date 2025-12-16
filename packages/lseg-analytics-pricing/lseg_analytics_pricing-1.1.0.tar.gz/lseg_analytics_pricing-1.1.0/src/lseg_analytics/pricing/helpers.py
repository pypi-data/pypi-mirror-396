from typing import Any, Dict, List, Optional, Union

import pandas as pd

from lseg_analytics.pricing.market_data.fx_forward_curves import FxOutrightCurvePoint
from lseg_analytics.pricing.reference_data.calendars import Holiday

from ._basic_client._model_base import Model

__all__ = ["to_rows", "description_to_df", "valuation_to_df", "risk_to_df", "cashflows_to_df"]


def _plain_curve_point(point: FxOutrightCurvePoint):
    return {
        "tenor": point.tenor,
        "start_date": point.start_date,
        "end_date": point.end_date,
        "outright.bid": point.outright.bid,
        "outright.ask": point.outright.ask,
        "outright.mid": point.outright.mid,
    }


def _plain_holiday_output(output: Holiday):
    for oname in output.names:
        yield {
            "date": output.date,
            "name": oname.name,
            "calendars": oname.calendars,
            "countries": oname.countries,
        }


def to_rows(items: List[Union[FxOutrightCurvePoint, Holiday]]) -> List[dict]:
    """Convert list of FxForwardCurvePoint or HolidayOutput objects to list of dicts"""

    if isinstance(items, list):
        if not items:
            return []
        if isinstance(items[0], FxOutrightCurvePoint):
            return [_plain_curve_point(point) for point in items]
        elif isinstance(items[0], Holiday):
            result = []
            for item in items:
                result.extend(_plain_holiday_output(item))
            return result
    raise ValueError("Argument is not supported")


def description_to_df(description_response) -> pd.DataFrame:
    """
    Convert a description response object to a pandas DataFrame.

    This function takes a description response object and converts it into a single-row
    pandas DataFrame, with each key-value pair from the description becoming a column.

    Parameters
    ----------
    description_response : object
        A description object which is typically contained in the analytics object of the
        result from functions like value or solve. This object contains descriptive
        metadata about an instrument or analytics result.

    Returns
    -------
    DataFrame
        A pandas DataFrame with a single row containing all the description properties
        as columns.

    Examples
    --------
    >>> # Assuming valuation_response is from an analytics call
    >>> description_df = description_to_df(valuation_response.analytics[0]['description'])
    >>> display(description_df)
    | instrumentTag | instrumentDescription                                        | startDate  | endDate    | tenor |
    |---------------|--------------------------------------------------------------|------------|------------|-------|
    |               | Pay USD Annual 3.5% vs Receive USD Annual +10b...            | 2026-05-15 | 2028-05-15 | 2Y    |
    """
    if not description_response:
        return pd.DataFrame()

    return pd.DataFrame(description_response.as_dict(), index=[0])


def valuation_to_df(
    valuation_response, custom_extractors: Optional[Dict[str, Union[str, List[str], Dict[str, str]]]] = None
) -> pd.DataFrame:
    """
    Convert a valuation response object to a pandas DataFrame.

    This function takes a valuation response object and converts it into a single-row
    pandas DataFrame, where each column represents a valuation metric extracted from the response.

    Parameters
    ----------
    valuation_response : object
        A valuation object which is typically contained in the analytics object of the
        result from functions like value or solve. This object contains the valuation
        or solve result.
    custom_extractors : dict, optional
        Mapping to extract nested values. If not provided, attempts to extract 'value' or 'date' automatically.

        It supports multiple formats:

        1. Simple extraction (1 level). E.g. to extract 'value' from 'amount':
            {"amount": "value"}

        2. Complex extraction (multiple sub-keys at same level) with custom column name. E.g. to extract 'value'
            and 'unit' from 'annualRate' and display 'value' as 'annualRateValue' and 'unit' as 'annualRateUnit':
            {"annualRate": {"value": "annualRateValue", "unit": "annualRateUnit"}}

        3. Deep path extraction (infinite depth). E.g. to extract 'info.details.code' from 'metadata':
            {"metadata": "info.details.code"}  # dot notation
            {"metadata": ["info", "details", "code"]}  # list notation

        4. Deep path with multiple extractions and custom column names. E.g. to extract 'info.value' and 'info.status.code'
            from 'data' and displayed as 'data_value' and 'status_code':
            {"data": {
                "info.value": "data_value",
                "info.status.code": "status_code"
            }}

    Returns
    -------
    DataFrame
        A pandas DataFrame with a single row containing all the valuation properties
        as columns.

    Examples
    --------
    >>> # Assuming valuation_response is from an analytics call
    >>> # Extract default 'value' field
    >>> valuation_df = valuation_to_df(valuation_response.analytics[0]['valuation'])
    >>> display(valuation_df)
    | accrued | marketValue  | cleanMarketValue |
    |---------|--------------|------------------|
    | 0.0     | 1405.784351  | 1405.784351      |

    >>> # Extract nested fields in 'accrued' with custom column names
    >>> valuation_df = valuation_to_df(valuation_response.analytics[0]['valuation'],
    ...   custom_extractors={
    ...       "accrued": {
    ...           "value": "accrued_value",
    ...           "percent": "accrued_percent",
    ...           "dealCurrency.currency": "accrued_deal_currency",
    ...       }
    ...   },
    ... )
    >>> display(valuation_df)
    | accrued_value | accrued_percent | accrued_deal_currency | marketValue  | cleanMarketValue |
    |---------------|-----------------|-----------------------|--------------|------------------|
    | 0.0           | 0.0             | USD                   | 1405.784351  | 1405.784351      |
    """
    if not valuation_response:
        return pd.DataFrame()

    data = _extract_fields_with_rules(valuation_response, custom_extractors)
    return pd.DataFrame([data])


def risk_to_df(
    risk_response, custom_extractors: Optional[Dict[str, Union[str, List[str], Dict[str, str]]]] = None
) -> pd.DataFrame:
    """
    Convert a risk response object to a pandas DataFrame.

    This function takes a risk response object and converts it into a single-row
    pandas DataFrame, where each column represents a risk metric extracted from the response.

    Parameters
    ----------
    risk_response : object
        A risk object which is typically contained in the analytics object of the
        result from functions like value or solve. This object contains the risk
        or solve result.
    custom_extractors : dict, optional
        Mapping to extract nested values. If not provided, attempts to extract 'value' or 'date' automatically.

        It supports multiple formats:

        1. Simple extraction (1 level). E.g. to extract 'value' from 'amount':
            {"amount": "value"}

        2. Complex extraction (multiple sub-keys at same level) with custom column name. E.g. to extract 'value'
            and 'unit' from 'annualRate' and display 'value' as 'annualRateValue' and 'unit' as 'annualRateUnit':
            {"annualRate": {"value": "annualRateValue", "unit": "annualRateUnit"}}

        3. Deep path extraction (infinite depth). E.g. to extract 'info.details.code' from 'metadata':
            {"metadata": "info.details.code"}  # dot notation
            {"metadata": ["info", "details", "code"]}  # list notation

        4. Deep path with multiple extractions and custom column names. E.g. to extract 'info.value' and 'info.status.code'
            from 'data' and displayed as 'data_value' and 'status_code':
            {"data": {
                "info.value": "data_value",
                "info.status.code": "status_code"
            }}

    Returns
    -------
    DataFrame
        A pandas DataFrame with a single row containing all the risk properties
        as columns.

    Examples
    --------
    >>> # Assuming valuation_response is from an analytics call
    >>> # Extract default 'value' field
    >>> risk_df = risk_to_df(valuation_response.analytics[0]['risk'])
    >>> display(risk_df)
    | duration  | modifiedDuration | benchmarkHedgeNotional | annuity      | dv01         | pv01         | br01 |
    |-----------|------------------|------------------------|--------------|--------------|--------------|------|
    | -1.965995 | -1.896152        | -1.022009e+06          | -185.202632  | -182.044531  | -182.044531  | 0.0  |

    >>> # Extract 'bp' (basis points) field
    >>> risk_df = risk_to_df(valuation_response.analytics[0]['risk'],
    ...    custom_extractors={
    ...        "annuity": {
    ...            "value": "annuity_value",
    ...            "reportCurrency.currency": "annuity_deal_currency",
    ...        }
    ...    },
    ... )
    >>> display(risk_df)
    | duration  | modifiedDuration | benchmarkHedgeNotional | annuity_value | annuity_deal_currency | dv01         | pv01         | br01 |
    |-----------|------------------|------------------------|---------------|-----------------------|--------------|--------------|------|
    | -1.965995 | -1.896152        | -1.022009e+06          | -185.202632   | USD                   | -182.044531  | -182.044531  | 0.0  |
    """
    if not risk_response:
        return pd.DataFrame()

    data = _extract_fields_with_rules(risk_response, custom_extractors)
    return pd.DataFrame([data])


def _extract_nested_value(obj: Union[dict, Model], path: Union[str, List[str]]) -> Any:
    """
    Extract value from nested object using path.

    Parameters
    ----------
    obj : dict or Model
        Object to extract from
    path : str or list
        Path to the value. Can be:
        - String with dot notation: "field.subfield.value"
        - List of keys: ["field", "subfield", "value"]

    Returns
    -------
    Any or pd.NA
        Extracted value or pd.NA if path not found
    """
    if isinstance(path, str):
        path = path.split(".")

    current = obj
    for key in path:
        if isinstance(current, (dict, Model)):
            current = current.get(key)
            if current is None:
                return pd.NA
        else:
            return pd.NA

    return current if current is not None else pd.NA


def _extract_fields_with_rules(
    obj: Union[dict, Any], custom_extractors: Optional[Dict[str, Union[str, List[str], Dict[str, str]]]] = None
) -> dict:
    """
    Extract fields from a dictionary or object with custom extraction rules.

    This function processes each key-value pair in the input obj and extracts data
    based on custom extraction rules or default behavior (extracting 'value' or 'date' fields).

    Parameters
    ----------
    obj : dict or object
        Dictionary or object containing fields to extract
    custom_extractors : dict, optional
        Mapping to extract nested values. If not provided, attempts to extract 'value'
        or 'date' automatically.

        Supports multiple formats:
        1. Simple extraction (1 level): {"amount": "value"}
        2. Complex extraction (multiple sub-keys):
           {"annualRate": {"value": "rate", "unit": "rate_unit"}}
        3. Deep path extraction: {"metadata": "info.details.code"}
        4. Deep path with multiple extractions:
           {"data": {"info.value": "data_value", "info.status.code": "status_code"}}

    Returns
    -------
    dict
        Dictionary with extracted fields as key-value pairs

    Examples
    --------
    >>> data = _extract_fields_with_rules(
    ...     response_items,
    ...     custom_extractors={"accrued": {"value": "accrued_value", "percent": "accrued_percent"}}
    ... )
    """
    data = {}
    for key, value in obj.items():
        if isinstance(value, (dict, Model)):
            # Check if we have extraction rules for this field
            if custom_extractors and key in custom_extractors:
                extractor = custom_extractors[key]

                # Complex extraction: {path: column_name, ...}
                if isinstance(extractor, dict):
                    for path, col_name in extractor.items():
                        data[col_name] = _extract_nested_value(value, path)
                # Simple extraction: path string or list
                else:
                    data[key] = _extract_nested_value(value, extractor)
            # Auto-extract common fields
            elif "value" in value:
                data[key] = value["value"]
            elif "date" in value:
                data[key] = value["date"]
            else:
                # Keep the object if no extraction rule found
                data[key] = value
        else:
            data[key] = value
    return data


def cashflows_to_df(
    cashflows, custom_extractors: Optional[Dict[str, Union[str, List[str], Dict[str, str]]]] = None
) -> pd.DataFrame:
    """
    Convert list of cashflow objects to DataFrame with flexible nested extraction.

    Parameters
    ----------
    cashflows : list
        List of cashflow objects (typically dicts or Model objects)
    custom_extractors : dict, optional
        Mapping to extract nested values. If not provided, attempts to extract 'value' or 'date' automatically.

        It supports multiple formats:

        1. Simple extraction (1 level). E.g. to extract 'value' from 'amount':
           {"amount": "value"}

        2. Complex extraction (multiple sub-keys at same level) with custom column name. E.g. to extract 'value'
           and 'unit' from 'annualRate' and display 'value' as 'annualRateValue' and 'unit' as 'annualRateUnit':
           {"annualRate": {"value": "annualRateValue", "unit": "annualRateUnit"}}

        3. Deep path extraction (infinite depth). E.g. to extract 'info.details.code' from 'metadata':
           {"metadata": "info.details.code"}  # dot notation
           {"metadata": ["info", "details", "code"]}  # list notation

        4. Deep path with multiple extractions and custom column names. E.g. to extract 'info.value' and 'info.status.code'
           from 'data' and displayed as 'data_value' and 'status_code':
           {"data": {
               "info.value": "data_value",
               "info.status.code": "status_code"
           }}

    Returns
    -------
    pd.DataFrame
        DataFrame with one row per cashflow

    Examples
    --------
    >>> # Assuming valuation_response is from an analytics call
    >>> # Extract default fields (auto-extract 'value' and 'date')
    >>> cashflows_df = cashflows_to_df_new(
    ...    valuation_response.analytics[0]["firstLeg"]["cashflows"]
    ... )
    >>> display(cashflows_df)
    | paymentType | annualRate | discountFactor | startDate  | endDate    | remainingNotional | interestRateType | zeroRate | date       | amount         | payer  | receiver | occurrence |
    |-------------|------------|----------------|------------|------------|-------------------|------------------|----------|------------|----------------|--------|----------|------------|
    | Interest    | 3.496702   | 0.927995       | 2026-05-15 | 2027-05-17 | 1000000.0         | FixedRate        | 3.791282 | 2027-05-18 | -35646.930909  | Party1 | Party2   | Future     |
    | Interest    | 3.496702   | 0.896032       | 2027-05-17 | 2028-05-15 | 0.0               | FixedRate        | 3.720179 | 2028-05-17 | -35355.539103  | Party1 | Party2   | Future     |

    >>> # Extract value and unit from annualRate and display as annualRateValue and annualRateUnit
    >>> cashflows_df = cashflows_to_df(valuation_response.analytics[0]["firstLeg"]["cashflows"],
    ...     custom_extractors={
    ...         "annualRate": {"value": "annualRateValue", "unit": "annualRateUnit"}
    ...     }
    ... )
    >>> display(cashflows_df)
    | paymentType | annualRateValue | annualRateUnit | discountFactor | startDate  | endDate    | remainingNotional | interestRateType | zeroRate | date       | amount         | payer  | receiver | occurrence |
    |-------------|-----------------|----------------|----------------|------------|------------|-------------------|------------------|----------|------------|----------------|--------|----------|------------|
    | Interest    | 3.496702        | Percentage     | 0.927995       | 2026-05-15 | 2027-05-17 | 1000000.0         | FixedRate        | 3.791282 | 2027-05-18 | -35646.930909  | Party1 | Party2   | Future     |
    | Interest    | 3.496702        | Percentage     | 0.896032       | 2027-05-17 | 2028-05-15 | 0.0               | FixedRate        | 3.720179 | 2028-05-17 | -35355.539103  | Party1 | Party2   | Future     |
    """
    if not cashflows:
        return pd.DataFrame()

    rows = []
    for cashflow in cashflows:
        row = _extract_fields_with_rules(cashflow, custom_extractors)
        rows.append(row)

    return pd.DataFrame(rows)
