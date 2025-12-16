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

from lseg_analytics.pricing._basic_client._types import JobStoreInputData
from lseg_analytics.pricing._basic_client.models import (
    ActualVsProjectedGlobalSettings,
    ActualVsProjectedRequest,
    ActualVsProjectedRequestItem,
    ApimCurveShift,
    ApimError,
    Balloon,
    BondIndicRequest,
    BondSearchCriteria,
    BondSearchRequest,
    BulkCompact,
    BulkComposite,
    BulkDefaultSettings,
    BulkGlobalSettings,
    BulkJsonInputItem,
    BulkMeta,
    BulkResultItem,
    BulkResultRequest,
    BulkTemplateDataSource,
    CapVolatility,
    CapVolItem,
    CashflowFloaterSettings,
    CashFlowGlobalSettings,
    CashFlowInput,
    CashflowMbsSettings,
    CashflowPrepaySettings,
    CashFlowRequestData,
    CashflowVolatility,
    CloCallInfo,
    CloSettings,
    CmbsPrepayment,
    CmbsSettings,
    CMOModification,
    CollateralDetailsRequest,
    CollateralDetailsRequestInfo,
    ColumnDetail,
    ConvertiblePricing,
    CurveDetailsRequest,
    CurveMultiShift,
    CurvePoint,
    CurveSearch,
    CurveTypeAndCurrency,
    CustomScenario,
    DataItems,
    DataTable,
    DataTableColumnDetail,
    DefaultDials,
    Distribution,
    ExtraSettings,
    FloaterSettings,
    HecmSettings,
    HorizonInfo,
    IdentifierInfo,
    IdTypeEnum,
    IndexLinkerSettings,
    IndexProjection,
    InterpolationTypeAndVector,
    JobCreationRequest,
    JobResponse,
    JobResubmissionRequest,
    JobStatusResponse,
    JobTimelineEntry,
    JsonRef,
    JsonScenRef,
    LookbackSettings,
    LookupDetails,
    LossSettings,
    MappedResponseRefData,
    MarketSettingsRequest,
    MarketSettingsRequestInfo,
    MbsSettings,
    ModifyClass,
    ModifyCollateral,
    MonthRatePair,
    MuniSettings,
    OptionModel,
    OriginChannel,
    Partials,
    PrepayDialsInput,
    PrepayDialsSettings,
    PrepayModelSeller,
    PrepayModelServicer,
    PricingScenario,
    PyCalcGlobalSettings,
    PyCalcInput,
    PyCalcRequest,
    RefDataMeta,
    RequestId,
    RestPrepaySettings,
    ResultResponseBulkResultItem,
    Results,
    ReturnAttributionCurveTypeAndCurrency,
    ReturnAttributionGlobalSettings,
    ReturnAttributionInput,
    ReturnAttributionRequest,
    ScalarAndVector,
    ScalarAndVectorWithCollateral,
    ScenAbsoluteCurvePoint,
    Scenario,
    ScenarioCalcFloaterSettings,
    ScenarioCalcGlobalSettings,
    ScenarioCalcInput,
    ScenarioCalcRequest,
    ScenarioDefinition,
    ScenarioSettlement,
    ScenarioVolatility,
    ScenCalcExtraSettings,
    ScenPartials,
    ScheduleItem,
    SensitivityShocks,
    SettlementInfo,
    SqlSettings,
    StateHomePriceAppreciation,
    StoreType,
    StructureNote,
    Summary,
    SwaptionVolatility,
    SwaptionVolItem,
    SystemScenario,
    TermAndValue,
    TermRatePair,
    UDIExtension,
    UserCurve,
    UserLoan,
    UserLoanCollateral,
    UserLoanDeal,
    UserScenario,
    UserScenarioCurve,
    UserScenarioInput,
    UserScenCurveDefinition,
    UserVol,
    Vector,
    Volatility,
    VolItem,
    WalSensitivityInput,
    WalSensitivityPrepayType,
    WalSensitivityRequest,
    YBPortUserBond,
    YbRestCurveType,
    YbRestFrequency,
)
from lseg_analytics.pricing._client.client import Client

from ._logger import logger

__all__ = [
    "ActualVsProjectedGlobalSettings",
    "ActualVsProjectedRequestItem",
    "ApimCurveShift",
    "ApimError",
    "Balloon",
    "BondSearchCriteria",
    "BulkDefaultSettings",
    "BulkGlobalSettings",
    "BulkJsonInputItem",
    "BulkMeta",
    "BulkResultItem",
    "BulkTemplateDataSource",
    "CMOModification",
    "CapVolItem",
    "CapVolatility",
    "CashFlowGlobalSettings",
    "CashFlowInput",
    "CashflowFloaterSettings",
    "CashflowMbsSettings",
    "CashflowPrepaySettings",
    "CashflowVolatility",
    "CloCallInfo",
    "CloSettings",
    "CmbsPrepayment",
    "CmbsSettings",
    "CollateralDetailsRequestInfo",
    "ColumnDetail",
    "ConvertiblePricing",
    "CurveMultiShift",
    "CurvePoint",
    "CurveSearch",
    "CurveTypeAndCurrency",
    "CustomScenario",
    "DataItems",
    "DataTable",
    "DataTableColumnDetail",
    "DefaultDials",
    "Distribution",
    "ExtraSettings",
    "FloaterSettings",
    "HecmSettings",
    "HorizonInfo",
    "IdTypeEnum",
    "IdentifierInfo",
    "IndexLinkerSettings",
    "IndexProjection",
    "InterpolationTypeAndVector",
    "JobResponse",
    "JobStatusResponse",
    "JobStoreInputData",
    "JobTimelineEntry",
    "JsonRef",
    "JsonScenRef",
    "LookbackSettings",
    "LookupDetails",
    "LossSettings",
    "MappedResponseRefData",
    "MarketSettingsRequestInfo",
    "MbsSettings",
    "ModifyClass",
    "ModifyCollateral",
    "MonthRatePair",
    "MuniSettings",
    "OptionModel",
    "OriginChannel",
    "Partials",
    "PrepayDialsInput",
    "PrepayDialsSettings",
    "PrepayModelSeller",
    "PrepayModelServicer",
    "PricingScenario",
    "PyCalcGlobalSettings",
    "PyCalcInput",
    "RefDataMeta",
    "RequestId",
    "RestPrepaySettings",
    "ResultResponseBulkResultItem",
    "Results",
    "ReturnAttributionCurveTypeAndCurrency",
    "ReturnAttributionGlobalSettings",
    "ReturnAttributionInput",
    "ScalarAndVector",
    "ScalarAndVectorWithCollateral",
    "ScenAbsoluteCurvePoint",
    "ScenCalcExtraSettings",
    "ScenPartials",
    "Scenario",
    "ScenarioCalcFloaterSettings",
    "ScenarioCalcGlobalSettings",
    "ScenarioCalcInput",
    "ScenarioDefinition",
    "ScenarioSettlement",
    "ScenarioVolatility",
    "ScheduleItem",
    "SensitivityShocks",
    "SettlementInfo",
    "SqlSettings",
    "StateHomePriceAppreciation",
    "StoreType",
    "StructureNote",
    "Summary",
    "SwaptionVolItem",
    "SwaptionVolatility",
    "SystemScenario",
    "TermAndValue",
    "TermRatePair",
    "UDIExtension",
    "UserCurve",
    "UserLoan",
    "UserLoanCollateral",
    "UserLoanDeal",
    "UserScenCurveDefinition",
    "UserScenario",
    "UserScenarioCurve",
    "UserScenarioInput",
    "UserVol",
    "Vector",
    "VolItem",
    "Volatility",
    "WalSensitivityInput",
    "WalSensitivityPrepayType",
    "YBPortUserBond",
    "YbRestCurveType",
    "YbRestFrequency",
    "abort_job",
    "bulk_compact_request",
    "bulk_composite_request",
    "bulk_yb_port_udi_request",
    "bulk_zip_request",
    "close_job",
    "create_job",
    "get_cash_flow_async",
    "get_cash_flow_sync",
    "get_csv_bulk_result",
    "get_formatted_result",
    "get_job",
    "get_job_data",
    "get_job_object_meta",
    "get_job_status",
    "get_json_result",
    "get_result",
    "get_tba_pricing_sync",
    "post_cash_flow_async",
    "post_cash_flow_sync",
    "post_csv_bulk_results_sync",
    "post_json_bulk_request_sync",
    "post_market_setting_sync",
    "request_actual_vs_projected_async",
    "request_actual_vs_projected_async_get",
    "request_actual_vs_projected_sync",
    "request_actual_vs_projected_sync_get",
    "request_bond_indic_async",
    "request_bond_indic_async_get",
    "request_bond_indic_sync",
    "request_bond_indic_sync_get",
    "request_bond_search_async_get",
    "request_bond_search_async_post",
    "request_bond_search_sync_get",
    "request_bond_search_sync_post",
    "request_collateral_details_async",
    "request_collateral_details_async_get",
    "request_collateral_details_sync",
    "request_collateral_details_sync_get",
    "request_curve_async",
    "request_curve_sync",
    "request_curves_async",
    "request_curves_sync",
    "request_get_scen_calc_sys_scen_async",
    "request_get_scen_calc_sys_scen_sync",
    "request_historical_data_async",
    "request_historical_data_sync",
    "request_index_catalogue_info_async",
    "request_index_catalogue_info_sync",
    "request_index_data_by_ticker_async",
    "request_index_data_by_ticker_sync",
    "request_index_providers_async",
    "request_index_providers_sync",
    "request_mbs_history_async",
    "request_mbs_history_sync",
    "request_mortgage_model_async",
    "request_mortgage_model_sync",
    "request_py_calculation_async",
    "request_py_calculation_async_by_id",
    "request_py_calculation_sync",
    "request_py_calculation_sync_by_id",
    "request_return_attribution_async",
    "request_return_attribution_sync",
    "request_scenario_calculation_async",
    "request_scenario_calculation_sync",
    "request_volatility_async",
    "request_volatility_sync",
    "request_wal_sensitivity_asyn_get",
    "request_wal_sensitivity_async",
    "request_wal_sensitivity_sync",
    "request_wal_sensitivity_sync_get",
    "resubmit_job",
    "upload_csv_job_data_async",
    "upload_csv_job_data_sync",
    "upload_csv_job_data_with_name_async",
    "upload_csv_job_data_with_name_sync",
    "upload_json_job_data_async",
    "upload_json_job_data_sync",
    "upload_json_job_data_with_name_async",
    "upload_json_job_data_with_name_sync",
    "upload_text_job_data_async",
    "upload_text_job_data_sync",
    "upload_text_job_data_with_name_async",
    "upload_text_job_data_with_name_sync",
]


def abort_job(*, job_ref: str) -> JobResponse:
    """
    Abort a job

    Parameters
    ----------
    job_ref : str
        Job reference. This can be of the form J-number or job name.

    Returns
    --------
    JobResponse


    Examples
    --------
    >>> # create temp job
    >>> job_response = create_job(
    >>>     name="close_Job"
    >>> )
    >>>
    >>> # abort job
    >>> response = abort_job(job_ref="close_Job")
    >>>
    >>> print(js.dumps(response.as_dict(), indent=4))
    {
        "id": "J-3638",
        "sequence": 0,
        "asOf": "2025-08-19",
        "closed": true,
        "onHold": false,
        "aborted": true,
        "exitStatus": "NEVER_STARTED",
        "actualHold": false,
        "name": "close_Job",
        "priority": 0,
        "order": "FAST",
        "requestCount": 0,
        "pendingCount": 0,
        "runningCount": 0,
        "okCount": 0,
        "errorCount": 0,
        "abortedCount": 0,
        "skipCount": 0,
        "startAfter": "2025-08-19T02:31:22.850Z",
        "stopAfter": "2025-08-20T02:31:22.850Z",
        "createdAt": "2025-08-19T02:31:22.852Z",
        "updatedAt": "2025-08-19T02:31:22.852Z"
    }

    """

    try:
        logger.info("Calling abort_job")

        response = Client().yield_book_rest.abort_job(job_ref=job_ref)

        output = response
        logger.info("Called abort_job")

        return output
    except Exception as err:
        logger.error("Error abort_job.")
        check_exception_and_raise(err, logger)


def bulk_compact_request(
    *,
    path: Optional[str] = None,
    name_expr: Optional[str] = None,
    body: Optional[str] = None,
    requests: Optional[List[Dict[str, Any]]] = None,
    data_source: Optional[BulkTemplateDataSource] = None,
    params: Optional[Dict[str, Any]] = None,
    create_job: Optional[bool] = None,
    chain_job: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> ResultResponseBulkResultItem:
    """
    Bulk compact request.

    Parameters
    ----------
    path : str, optional
        URL to which each individual request should be posted.i.e "/bond/py" for PY calculation.
    name_expr : str, optional
        Name of each request. This can be a valid JSON path expression, i.e "concat($.CUSIP,"_PY")" will give each request the name CUSIP_PY. Name should be unique within a single job.
    body : str, optional
        POST body associated with the calculation. This is specific to each request type. Refer to individual calculation section for more details.
    requests : List[Dict[str, Any]], optional
        List of key value pairs. This values provided will be used to update corresponding variables in the body of the request.
    data_source : BulkTemplateDataSource, optional

    params : Dict[str, Any], optional

    create_job : bool, optional
        Boolean with `true` and `false` values.
    chain_job : str, optional
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    ResultResponseBulkResultItem


    Examples
    --------


    """

    try:
        logger.info("Calling bulk_compact_request")

        response = Client().yield_book_rest.bulk_compact_request(
            body=BulkCompact(
                path=path,
                name_expr=name_expr,
                body=body,
                requests=requests,
                data_source=data_source,
                params=params,
            ),
            create_job=create_job,
            chain_job=chain_job,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
            content_type="application/json",
        )

        output = response
        logger.info("Called bulk_compact_request")

        return output
    except Exception as err:
        logger.error("Error bulk_compact_request.")
        check_exception_and_raise(err, logger)


def bulk_composite_request(
    *,
    requests: List[BulkJsonInputItem],
    create_job: Optional[bool] = None,
    chain_job: Optional[str] = None,
    partial: Optional[bool] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> ResultResponseBulkResultItem:
    """
    Bulk composite request.

    Parameters
    ----------
    requests : List[BulkJsonInputItem]

    create_job : bool, optional
        Boolean with `true` and `false` values.
    chain_job : str, optional
        A sequence of textual characters.
    partial : bool, optional
        Boolean with `true` and `false` values.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    ResultResponseBulkResultItem


    Examples
    --------


    """

    try:
        logger.info("Calling bulk_composite_request")

        response = Client().yield_book_rest.bulk_composite_request(
            body=BulkComposite(requests=requests),
            create_job=create_job,
            chain_job=chain_job,
            partial=partial,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
            content_type="application/json",
        )

        output = response
        logger.info("Called bulk_composite_request")

        return output
    except Exception as err:
        logger.error("Error bulk_composite_request.")
        check_exception_and_raise(err, logger)


def bulk_yb_port_udi_request(
    *,
    data: str,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    create_job: Optional[bool] = None,
    chain_job: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> ResultResponseBulkResultItem:
    """
    Bulk YB Port UDI request.

    Parameters
    ----------
    data : str
        A sequence of textual characters.
    prefix : str, optional
        A sequence of textual characters.
    suffix : str, optional
        A sequence of textual characters.
    create_job : bool, optional
        Boolean with `true` and `false` values.
    chain_job : str, optional
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    ResultResponseBulkResultItem


    Examples
    --------


    """

    try:
        logger.info("Calling bulk_yb_port_udi_request")

        response = Client().yield_book_rest.bulk_yb_port_udi_request(
            prefix=prefix,
            suffix=suffix,
            create_job=create_job,
            chain_job=chain_job,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
            content_type="text/plain",
            data=data,
        )

        output = response
        logger.info("Called bulk_yb_port_udi_request")

        return output
    except Exception as err:
        logger.error("Error bulk_yb_port_udi_request.")
        check_exception_and_raise(err, logger)


def bulk_zip_request(
    *,
    data: bytes,
    default_target: Optional[str] = None,
    create_job: Optional[bool] = None,
    chain_job: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> ResultResponseBulkResultItem:
    """
    Bulk zip request.

    Parameters
    ----------
    data : bytes
        Represent a byte array
    default_target : str, optional
        A sequence of textual characters.
    create_job : bool, optional
        Boolean with `true` and `false` values.
    chain_job : str, optional
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    ResultResponseBulkResultItem


    Examples
    --------


    """

    try:
        logger.info("Calling bulk_zip_request")

        response = Client().yield_book_rest.bulk_zip_request(
            default_target=default_target,
            create_job=create_job,
            chain_job=chain_job,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
            content_type="application/zip",
            data=data,
        )

        output = response
        logger.info("Called bulk_zip_request")

        return output
    except Exception as err:
        logger.error("Error bulk_zip_request.")
        check_exception_and_raise(err, logger)


def close_job(*, job_ref: str) -> JobResponse:
    """
    Close a job

    Parameters
    ----------
    job_ref : str
        Job reference. This can be of the form J-number or job name.

    Returns
    --------
    JobResponse


    Examples
    --------
    >>> # create temp job
    >>> job_response = create_job(
    >>>     name="close_Job"
    >>> )
    >>>
    >>> # close job
    >>> response = close_job(job_ref="close_Job")
    >>>
    >>> print(js.dumps(response.as_dict(), indent=4))
    {
        "id": "J-3637",
        "sequence": 0,
        "asOf": "2025-08-19",
        "closed": true,
        "onHold": false,
        "aborted": false,
        "exitStatus": "NEVER_STARTED",
        "actualHold": false,
        "name": "close_Job",
        "priority": 0,
        "order": "FAST",
        "requestCount": 0,
        "pendingCount": 0,
        "runningCount": 0,
        "okCount": 0,
        "errorCount": 0,
        "abortedCount": 0,
        "skipCount": 0,
        "startAfter": "2025-08-19T02:31:17.445Z",
        "stopAfter": "2025-08-20T02:31:17.445Z",
        "createdAt": "2025-08-19T02:31:17.448Z",
        "updatedAt": "2025-08-19T02:31:17.766Z"
    }

    """

    try:
        logger.info("Calling close_job")

        response = Client().yield_book_rest.close_job(job_ref=job_ref)

        output = response
        logger.info("Called close_job")

        return output
    except Exception as err:
        logger.error("Error close_job.")
        check_exception_and_raise(err, logger)


def create_job(
    *,
    priority: Optional[int] = None,
    hold: Optional[bool] = None,
    start_after: Optional[datetime.datetime] = None,
    stop_after: Optional[datetime.datetime] = None,
    name: Optional[str] = None,
    asof: Optional[Union[str, datetime.date]] = None,
    order: Optional[Literal["FAST", "FIFO", "NONE"]] = None,
    chain: Optional[str] = None,
    desc: Optional[str] = None,
) -> JobResponse:
    """
    Create a new job

    Parameters
    ----------
    priority : int, optional
        Control priority of job. Requests within jobs of higher priority are processed prior to jobs with lower priority.
    hold : bool, optional
        When set to true, suspends the excution of all requests in the job, processing resumes only after the job is updated and the value is set to false.
    start_after : datetime.datetime, optional
        An instant in coordinated universal time (UTC)"
    stop_after : datetime.datetime, optional
        An instant in coordinated universal time (UTC)"
    name : str, optional
        Optional. Unique name associated with a job. There can only be one active job with this name. Job name can be used for all future job references. If a previously open job exists with the same name, the older job is closed before a new job is created.
    asof : Union[str, datetime.date], optional
        A date on a calendar without a time zone, e.g. "April 10th"
    order : Literal["FAST","FIFO","NONE"], optional

    chain : str, optional
        A sequence of textual characters.
    desc : str, optional
        User defined description of the job.

    Returns
    --------
    JobResponse


    Examples
    --------
    >>> # create job
    >>> job_response = create_job(
    >>>     priority=0,
    >>>     hold=True,
    >>>     start_after=datetime(2025, 3, 3, 10, 10, 15, 263),
    >>>     stop_after=datetime(2025, 3, 10, 20, 10, 15, 263),
    >>>     name="myJob",
    >>>     asof="2025-03-10",
    >>>     order="FAST",
    >>>     chain="string",
    >>>     desc="string",
    >>> )
    >>>
    >>> print(js.dumps(job_response.as_dict(), indent=4))
    {
        "id": "J-16433",
        "sequence": 0,
        "asOf": "2025-03-10",
        "closed": true,
        "onHold": true,
        "aborted": true,
        "exitStatus": "NEVER_STARTED",
        "actualHold": true,
        "name": "myJob",
        "chain": "string",
        "description": "string",
        "priority": 0,
        "order": "FAST",
        "requestCount": 0,
        "pendingCount": 0,
        "runningCount": 0,
        "okCount": 0,
        "errorCount": 0,
        "abortedCount": 0,
        "skipCount": 0,
        "startAfter": "2025-03-03T10:10:15Z",
        "stopAfter": "2025-03-10T20:10:15Z",
        "createdAt": "2025-12-03T12:43:00.855Z",
        "updatedAt": "2025-12-03T12:43:00.855Z"
    }

    """

    try:
        logger.info("Calling create_job")

        response = Client().yield_book_rest.create_job(
            body=JobCreationRequest(
                priority=priority,
                hold=hold,
                start_after=start_after,
                stop_after=stop_after,
                name=name,
                asof=asof,
                order=order,
                chain=chain,
                desc=desc,
            )
        )

        output = response
        logger.info("Called create_job")

        return output
    except Exception as err:
        logger.error("Error create_job.")
        check_exception_and_raise(err, logger)


def get_cash_flow_async(
    *,
    id: str,
    id_type: Optional[str] = None,
    pricing_date: Optional[str] = None,
    par_amount: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Get cash flow request async.

    Parameters
    ----------
    id : str
        Security reference ID.
    id_type : str, optional
        A sequence of textual characters.
    pricing_date : str, optional
        A sequence of textual characters.
    par_amount : str, optional
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------
    >>> # Formulate and execute the get request by using instrument ID, Par_amount and job in which the calculation will be done
    >>> cf_async_get_response = get_cash_flow_async(
    >>>             id="999818LH",
    >>>             par_amount="10000"
    >>>         )
    >>>
    >>> cf_async_get_result = {}
    >>>
    >>> attempt = 1
    >>>
    >>> while attempt < 10:
    >>>
    >>>     try:
    >>>         time.sleep(10)
    >>>
    >>>         cf_async_get_result = get_result(request_id_parameter=cf_async_get_response.request_id)
    >>>
    >>>         break
    >>>
    >>>     except Exception as error:
    >>>         print(f"Attempt " + str(attempt) + " resulted in error retrieving results from:" + cf_async_get_response.request_id)
    >>>
    >>>         attempt+=1
    >>>
    >>> # Print output to a file, as CF output is too long for terminal printout
    >>> # print(js.dumps(cf_async_get_result, indent=4), file=open('.\\CF_async_get_output.json', 'w+'))
    >>>
    >>>
    >>> # Print onyl payment information
    >>> for paymentInfo in cf_async_get_result["data"]["cashFlow"]["dataPaymentList"]:
    >>>     print(js.dumps(paymentInfo, indent=4))
    {
        "date": "2025-10-20",
        "totalCashFlow": 143643.11083,
        "interestPayment": 41666.666667,
        "principalBalance": 9898023.555837,
        "principalPayment": 101976.444163,
        "endPrincipalBalance": 9898023.555837,
        "beginPrincipalBalance": 10000000.0,
        "prepayPrincipalPayment": 57528.797683,
        "scheduledPrincipalPayment": 44447.64648
    }
    {
        "date": "2025-11-20",
        "totalCashFlow": 142775.491344,
        "interestPayment": 41241.764816,
        "principalBalance": 9796489.829309,
        "principalPayment": 101533.726528,
        "endPrincipalBalance": 9796489.829309,
        "beginPrincipalBalance": 9898023.555837,
        "prepayPrincipalPayment": 57145.169785,
        "scheduledPrincipalPayment": 44388.556743
    }
    {
        "date": "2025-12-20",
        "totalCashFlow": 134860.061834,
        "interestPayment": 40818.707622,
        "principalBalance": 9702448.475097,
        "principalPayment": 94041.354212,
        "endPrincipalBalance": 9702448.475097,
        "beginPrincipalBalance": 9796489.829309,
        "prepayPrincipalPayment": 49712.737659,
        "scheduledPrincipalPayment": 44328.616553
    }
    {
        "date": "2026-01-20",
        "totalCashFlow": 139412.98894,
        "interestPayment": 40426.868646,
        "principalBalance": 9603462.354803,
        "principalPayment": 98986.120294,
        "endPrincipalBalance": 9603462.354803,
        "beginPrincipalBalance": 9702448.475097,
        "prepayPrincipalPayment": 54686.114506,
        "scheduledPrincipalPayment": 44300.005788
    }
    {
        "date": "2026-02-20",
        "totalCashFlow": 129907.051581,
        "interestPayment": 40014.426478,
        "principalBalance": 9513569.7297,
        "principalPayment": 89892.625103,
        "endPrincipalBalance": 9513569.7297,
        "beginPrincipalBalance": 9603462.354803,
        "prepayPrincipalPayment": 45646.333606,
        "scheduledPrincipalPayment": 44246.291497
    }
    {
        "date": "2026-03-20",
        "totalCashFlow": 129554.906715,
        "interestPayment": 39639.873874,
        "principalBalance": 9423654.696859,
        "principalPayment": 89915.032841,
        "endPrincipalBalance": 9423654.696859,
        "beginPrincipalBalance": 9513569.7297,
        "prepayPrincipalPayment": 45682.965703,
        "scheduledPrincipalPayment": 44232.067138
    }
    {
        "date": "2026-04-20",
        "totalCashFlow": 136313.476005,
        "interestPayment": 39265.227904,
        "principalBalance": 9326606.448758,
        "principalPayment": 97048.248101,
        "endPrincipalBalance": 9326606.448758,
        "beginPrincipalBalance": 9423654.696859,
        "prepayPrincipalPayment": 52832.586331,
        "scheduledPrincipalPayment": 44215.66177
    }
    {
        "date": "2026-05-20",
        "totalCashFlow": 139322.71775,
        "interestPayment": 38860.860203,
        "principalBalance": 9226144.591211,
        "principalPayment": 100461.857547,
        "endPrincipalBalance": 9226144.591211,
        "beginPrincipalBalance": 9326606.448758,
        "prepayPrincipalPayment": 56298.503597,
        "scheduledPrincipalPayment": 44163.35395
    }
    {
        "date": "2026-06-20",
        "totalCashFlow": 138392.384431,
        "interestPayment": 38442.26913,
        "principalBalance": 9126194.475909,
        "principalPayment": 99950.115301,
        "endPrincipalBalance": 9126194.475909,
        "beginPrincipalBalance": 9226144.591211,
        "prepayPrincipalPayment": 55858.182044,
        "scheduledPrincipalPayment": 44091.933257
    }
    {
        "date": "2026-07-20",
        "totalCashFlow": 142662.258004,
        "interestPayment": 38025.810316,
        "principalBalance": 9021558.028222,
        "principalPayment": 104636.447687,
        "endPrincipalBalance": 9021558.028222,
        "beginPrincipalBalance": 9126194.475909,
        "prepayPrincipalPayment": 60616.632624,
        "scheduledPrincipalPayment": 44019.815063
    }
    {
        "date": "2026-08-20",
        "totalCashFlow": 140971.010132,
        "interestPayment": 37589.825118,
        "principalBalance": 8918176.843208,
        "principalPayment": 103381.185014,
        "endPrincipalBalance": 8918176.843208,
        "beginPrincipalBalance": 9021558.028222,
        "prepayPrincipalPayment": 59459.494936,
        "scheduledPrincipalPayment": 43921.690078
    }
    {
        "date": "2026-09-20",
        "totalCashFlow": 136866.207597,
        "interestPayment": 37159.07018,
        "principalBalance": 8818469.705791,
        "principalPayment": 99707.137417,
        "endPrincipalBalance": 8818469.705791,
        "beginPrincipalBalance": 8918176.843208,
        "prepayPrincipalPayment": 55881.095876,
        "scheduledPrincipalPayment": 43826.04154
    }
    {
        "date": "2026-10-20",
        "totalCashFlow": 134542.82725,
        "interestPayment": 36743.623774,
        "principalBalance": 8720670.502316,
        "principalPayment": 97799.203476,
        "endPrincipalBalance": 8720670.502316,
        "beginPrincipalBalance": 8818469.705791,
        "prepayPrincipalPayment": 54054.244536,
        "scheduledPrincipalPayment": 43744.95894
    }
    {
        "date": "2026-11-20",
        "totalCashFlow": 131928.871146,
        "interestPayment": 36336.127093,
        "principalBalance": 8625077.758263,
        "principalPayment": 95592.744053,
        "endPrincipalBalance": 8625077.758263,
        "beginPrincipalBalance": 8720670.502316,
        "prepayPrincipalPayment": 51922.710962,
        "scheduledPrincipalPayment": 43670.033091
    }
    {
        "date": "2026-12-20",
        "totalCashFlow": 127543.986637,
        "interestPayment": 35937.823993,
        "principalBalance": 8533471.595619,
        "principalPayment": 91606.162644,
        "endPrincipalBalance": 8533471.595619,
        "beginPrincipalBalance": 8625077.758263,
        "prepayPrincipalPayment": 48003.194726,
        "scheduledPrincipalPayment": 43602.967918
    }
    {
        "date": "2027-01-20",
        "totalCashFlow": 130113.494613,
        "interestPayment": 35556.131648,
        "principalBalance": 8438914.232655,
        "principalPayment": 94557.362964,
        "endPrincipalBalance": 8438914.232655,
        "beginPrincipalBalance": 8533471.595619,
        "prepayPrincipalPayment": 51004.270252,
        "scheduledPrincipalPayment": 43553.092713
    }
    {
        "date": "2027-02-20",
        "totalCashFlow": 119829.637295,
        "interestPayment": 35162.142636,
        "principalBalance": 8354246.737995,
        "principalPayment": 84667.494659,
        "endPrincipalBalance": 8354246.737995,
        "beginPrincipalBalance": 8438914.232655,
        "prepayPrincipalPayment": 41182.323517,
        "scheduledPrincipalPayment": 43485.171142
    }
    {
        "date": "2027-03-20",
        "totalCashFlow": 120605.050635,
        "interestPayment": 34809.361408,
        "principalBalance": 8268451.048769,
        "principalPayment": 85795.689226,
        "endPrincipalBalance": 8268451.048769,
        "beginPrincipalBalance": 8354246.737995,
        "prepayPrincipalPayment": 42330.185483,
        "scheduledPrincipalPayment": 43465.503744
    }
    {
        "date": "2027-04-20",
        "totalCashFlow": 127458.449304,
        "interestPayment": 34451.87937,
        "principalBalance": 8175444.478835,
        "principalPayment": 93006.569934,
        "endPrincipalBalance": 8175444.478835,
        "beginPrincipalBalance": 8268451.048769,
        "prepayPrincipalPayment": 49568.936245,
        "scheduledPrincipalPayment": 43437.633689
    }
    {
        "date": "2027-05-20",
        "totalCashFlow": 129416.800315,
        "interestPayment": 34064.351995,
        "principalBalance": 8080092.030516,
        "principalPayment": 95352.448319,
        "endPrincipalBalance": 8080092.030516,
        "beginPrincipalBalance": 8175444.478835,
        "prepayPrincipalPayment": 51983.384311,
        "scheduledPrincipalPayment": 43369.064008
    }
    {
        "date": "2027-06-20",
        "totalCashFlow": 128431.220868,
        "interestPayment": 33667.050127,
        "principalBalance": 7985327.859775,
        "principalPayment": 94764.170741,
        "endPrincipalBalance": 7985327.859775,
        "beginPrincipalBalance": 8080092.030516,
        "prepayPrincipalPayment": 51479.502688,
        "scheduledPrincipalPayment": 43284.668052
    }
    {
        "date": "2027-07-20",
        "totalCashFlow": 132194.532629,
        "interestPayment": 33272.199416,
        "principalBalance": 7886405.526562,
        "principalPayment": 98922.333213,
        "endPrincipalBalance": 7886405.526562,
        "beginPrincipalBalance": 7985327.859775,
        "prepayPrincipalPayment": 55722.465511,
        "scheduledPrincipalPayment": 43199.867702
    }
    {
        "date": "2027-08-20",
        "totalCashFlow": 128714.546851,
        "interestPayment": 32860.023027,
        "principalBalance": 7790551.002739,
        "principalPayment": 95854.523823,
        "endPrincipalBalance": 7790551.002739,
        "beginPrincipalBalance": 7886405.526562,
        "prepayPrincipalPayment": 52765.786026,
        "scheduledPrincipalPayment": 43088.737798
    }
    {
        "date": "2027-09-20",
        "totalCashFlow": 127971.327413,
        "interestPayment": 32460.629178,
        "principalBalance": 7695040.304503,
        "principalPayment": 95510.698235,
        "endPrincipalBalance": 7695040.304503,
        "beginPrincipalBalance": 7790551.002739,
        "prepayPrincipalPayment": 52520.31433,
        "scheduledPrincipalPayment": 42990.383906
    }
    {
        "date": "2027-10-20",
        "totalCashFlow": 124043.250752,
        "interestPayment": 32062.667935,
        "principalBalance": 7603059.721687,
        "principalPayment": 91980.582816,
        "endPrincipalBalance": 7603059.721687,
        "beginPrincipalBalance": 7695040.304503,
        "prepayPrincipalPayment": 49090.550692,
        "scheduledPrincipalPayment": 42890.032124
    }
    {
        "date": "2027-11-20",
        "totalCashFlow": 120139.358706,
        "interestPayment": 31679.415507,
        "principalBalance": 7514599.778489,
        "principalPayment": 88459.943199,
        "endPrincipalBalance": 7514599.778489,
        "beginPrincipalBalance": 7603059.721687,
        "prepayPrincipalPayment": 45654.360288,
        "scheduledPrincipalPayment": 42805.582911
    }
    {
        "date": "2027-12-20",
        "totalCashFlow": 118785.58524,
        "interestPayment": 31310.83241,
        "principalBalance": 7427125.025659,
        "principalPayment": 87474.752829,
        "endPrincipalBalance": 7427125.025659,
        "beginPrincipalBalance": 7514599.778489,
        "prepayPrincipalPayment": 44737.263198,
        "scheduledPrincipalPayment": 42737.489631
    }
    {
        "date": "2028-01-20",
        "totalCashFlow": 118271.964361,
        "interestPayment": 30946.354274,
        "principalBalance": 7339799.415572,
        "principalPayment": 87325.610087,
        "endPrincipalBalance": 7339799.415572,
        "beginPrincipalBalance": 7427125.025659,
        "prepayPrincipalPayment": 44653.903081,
        "scheduledPrincipalPayment": 42671.707006
    }
    {
        "date": "2028-02-20",
        "totalCashFlow": 111263.692309,
        "interestPayment": 30582.497565,
        "principalBalance": 7259118.220828,
        "principalPayment": 80681.194744,
        "endPrincipalBalance": 7259118.220828,
        "beginPrincipalBalance": 7339799.415572,
        "prepayPrincipalPayment": 38077.723036,
        "scheduledPrincipalPayment": 42603.471707
    }
    {
        "date": "2028-03-20",
        "totalCashFlow": 111876.56821,
        "interestPayment": 30246.32592,
        "principalBalance": 7177487.978538,
        "principalPayment": 81630.24229,
        "endPrincipalBalance": 7177487.978538,
        "beginPrincipalBalance": 7259118.220828,
        "prepayPrincipalPayment": 39059.425379,
        "scheduledPrincipalPayment": 42570.816911
    }
    {
        "date": "2028-04-20",
        "totalCashFlow": 117312.831305,
        "interestPayment": 29906.199911,
        "principalBalance": 7090081.347143,
        "principalPayment": 87406.631395,
        "endPrincipalBalance": 7090081.347143,
        "beginPrincipalBalance": 7177487.978538,
        "prepayPrincipalPayment": 44876.754919,
        "scheduledPrincipalPayment": 42529.876476
    }
    {
        "date": "2028-05-20",
        "totalCashFlow": 114992.681511,
        "interestPayment": 29542.005613,
        "principalBalance": 7004630.671245,
        "principalPayment": 85450.675898,
        "endPrincipalBalance": 7004630.671245,
        "beginPrincipalBalance": 7090081.347143,
        "prepayPrincipalPayment": 42999.17551,
        "scheduledPrincipalPayment": 42451.500388
    }
    {
        "date": "2028-06-20",
        "totalCashFlow": 120297.03831,
        "interestPayment": 29185.96113,
        "principalBalance": 6913519.594066,
        "principalPayment": 91111.07718,
        "endPrincipalBalance": 6913519.594066,
        "beginPrincipalBalance": 7004630.671245,
        "prepayPrincipalPayment": 48729.77154,
        "scheduledPrincipalPayment": 42381.30564
    }
    {
        "date": "2028-07-20",
        "totalCashFlow": 120517.77979,
        "interestPayment": 28806.331642,
        "principalBalance": 6821808.145918,
        "principalPayment": 91711.448148,
        "endPrincipalBalance": 6821808.145918,
        "beginPrincipalBalance": 6913519.594066,
        "prepayPrincipalPayment": 49438.446375,
        "scheduledPrincipalPayment": 42273.001773
    }
    {
        "date": "2028-08-20",
        "totalCashFlow": 115897.669089,
        "interestPayment": 28424.200608,
        "principalBalance": 6734334.677437,
        "principalPayment": 87473.468481,
        "endPrincipalBalance": 6734334.677437,
        "beginPrincipalBalance": 6821808.145918,
        "prepayPrincipalPayment": 45316.809299,
        "scheduledPrincipalPayment": 42156.659182
    }
    {
        "date": "2028-09-20",
        "totalCashFlow": 117957.545179,
        "interestPayment": 28059.727823,
        "principalBalance": 6644436.860081,
        "principalPayment": 89897.817356,
        "endPrincipalBalance": 6644436.860081,
        "beginPrincipalBalance": 6734334.677437,
        "prepayPrincipalPayment": 47835.553293,
        "scheduledPrincipalPayment": 42062.264063
    }
    {
        "date": "2028-10-20",
        "totalCashFlow": 111734.515729,
        "interestPayment": 27685.153584,
        "principalBalance": 6560387.497936,
        "principalPayment": 84049.362145,
        "endPrincipalBalance": 6560387.497936,
        "beginPrincipalBalance": 6644436.860081,
        "prepayPrincipalPayment": 42100.870862,
        "scheduledPrincipalPayment": 41948.491283
    }
    {
        "date": "2028-11-20",
        "totalCashFlow": 110704.416081,
        "interestPayment": 27334.947908,
        "principalBalance": 6477018.029763,
        "principalPayment": 83369.468173,
        "endPrincipalBalance": 6477018.029763,
        "beginPrincipalBalance": 6560387.497936,
        "prepayPrincipalPayment": 41501.939606,
        "scheduledPrincipalPayment": 41867.528567
    }
    {
        "date": "2028-12-20",
        "totalCashFlow": 108224.886164,
        "interestPayment": 26987.575124,
        "principalBalance": 6395780.718723,
        "principalPayment": 81237.31104,
        "endPrincipalBalance": 6395780.718723,
        "beginPrincipalBalance": 6477018.029763,
        "prepayPrincipalPayment": 39450.179215,
        "scheduledPrincipalPayment": 41787.131825
    }
    {
        "date": "2029-01-20",
        "totalCashFlow": 106558.334344,
        "interestPayment": 26649.086328,
        "principalBalance": 6315871.470708,
        "principalPayment": 79909.248016,
        "endPrincipalBalance": 6315871.470708,
        "beginPrincipalBalance": 6395780.718723,
        "prepayPrincipalPayment": 38192.434632,
        "scheduledPrincipalPayment": 41716.813384
    }
    {
        "date": "2029-02-20",
        "totalCashFlow": 102419.550007,
        "interestPayment": 26316.131128,
        "principalBalance": 6239768.051828,
        "principalPayment": 76103.41888,
        "endPrincipalBalance": 6239768.051828,
        "beginPrincipalBalance": 6315871.470708,
        "prepayPrincipalPayment": 34451.792517,
        "scheduledPrincipalPayment": 41651.626362
    }
    {
        "date": "2029-03-20",
        "totalCashFlow": 101060.0852,
        "interestPayment": 25999.033549,
        "principalBalance": 6164707.000177,
        "principalPayment": 75061.051651,
        "endPrincipalBalance": 6164707.000177,
        "beginPrincipalBalance": 6239768.051828,
        "prepayPrincipalPayment": 33452.767161,
        "scheduledPrincipalPayment": 41608.28449
    }
    {
        "date": "2029-04-20",
        "totalCashFlow": 105055.455272,
        "interestPayment": 25686.279167,
        "principalBalance": 6085337.824073,
        "principalPayment": 79369.176104,
        "endPrincipalBalance": 6085337.824073,
        "beginPrincipalBalance": 6164707.000177,
        "prepayPrincipalPayment": 37800.26812,
        "scheduledPrincipalPayment": 41568.907984
    }
    {
        "date": "2029-05-20",
        "totalCashFlow": 106265.784886,
        "interestPayment": 25355.574267,
        "principalBalance": 6004427.613454,
        "principalPayment": 80910.210619,
        "endPrincipalBalance": 6004427.613454,
        "beginPrincipalBalance": 6085337.824073,
        "prepayPrincipalPayment": 39413.049522,
        "scheduledPrincipalPayment": 41497.161097
    }
    {
        "date": "2029-06-20",
        "totalCashFlow": 108985.472115,
        "interestPayment": 25018.448389,
        "principalBalance": 5920460.589728,
        "principalPayment": 83967.023726,
        "endPrincipalBalance": 5920460.589728,
        "beginPrincipalBalance": 6004427.613454,
        "prepayPrincipalPayment": 42555.984804,
        "scheduledPrincipalPayment": 41411.038921
    }
    {
        "date": "2029-07-20",
        "totalCashFlow": 107766.829588,
        "interestPayment": 24668.585791,
        "principalBalance": 5837362.345931,
        "principalPayment": 83098.243797,
        "endPrincipalBalance": 5837362.345931,
        "beginPrincipalBalance": 5920460.589728,
        "prepayPrincipalPayment": 41798.749253,
        "scheduledPrincipalPayment": 41299.494544
    }
    {
        "date": "2029-08-20",
        "totalCashFlow": 106291.831009,
        "interestPayment": 24322.343108,
        "principalBalance": 5755392.85803,
        "principalPayment": 81969.487901,
        "endPrincipalBalance": 5755392.85803,
        "beginPrincipalBalance": 5837362.345931,
        "prepayPrincipalPayment": 40780.116845,
        "scheduledPrincipalPayment": 41189.371056
    }
    {
        "date": "2029-09-20",
        "totalCashFlow": 106706.737869,
        "interestPayment": 23980.803575,
        "principalBalance": 5672666.923735,
        "principalPayment": 82725.934294,
        "endPrincipalBalance": 5672666.923735,
        "beginPrincipalBalance": 5755392.85803,
        "prepayPrincipalPayment": 41643.333578,
        "scheduledPrincipalPayment": 41082.600716
    }
    {
        "date": "2029-10-20",
        "totalCashFlow": 100223.59303,
        "interestPayment": 23636.112182,
        "principalBalance": 5596079.442887,
        "principalPayment": 76587.480848,
        "endPrincipalBalance": 5596079.442887,
        "beginPrincipalBalance": 5672666.923735,
        "prepayPrincipalPayment": 35621.766867,
        "scheduledPrincipalPayment": 40965.713981
    }
    {
        "date": "2029-11-20",
        "totalCashFlow": 101386.318502,
        "interestPayment": 23316.997679,
        "principalBalance": 5518010.122064,
        "principalPayment": 78069.320823,
        "endPrincipalBalance": 5518010.122064,
        "beginPrincipalBalance": 5596079.442887,
        "prepayPrincipalPayment": 37180.562109,
        "scheduledPrincipalPayment": 40888.758715
    }
    {
        "date": "2029-12-20",
        "totalCashFlow": 98190.897838,
        "interestPayment": 22991.708842,
        "principalBalance": 5442810.933068,
        "principalPayment": 75199.188996,
        "endPrincipalBalance": 5442810.933068,
        "beginPrincipalBalance": 5518010.122064,
        "prepayPrincipalPayment": 34402.343785,
        "scheduledPrincipalPayment": 40796.845211
    }
    {
        "date": "2030-01-20",
        "totalCashFlow": 96717.162794,
        "interestPayment": 22678.378888,
        "principalBalance": 5368772.149161,
        "principalPayment": 74038.783906,
        "endPrincipalBalance": 5368772.149161,
        "beginPrincipalBalance": 5442810.933068,
        "prepayPrincipalPayment": 33316.764252,
        "scheduledPrincipalPayment": 40722.019654
    }
    {
        "date": "2030-02-20",
        "totalCashFlow": 93141.66824,
        "interestPayment": 22369.883955,
        "principalBalance": 5298000.364876,
        "principalPayment": 70771.784285,
        "endPrincipalBalance": 5298000.364876,
        "beginPrincipalBalance": 5368772.149161,
        "prepayPrincipalPayment": 30119.805875,
        "scheduledPrincipalPayment": 40651.97841
    }
    {
        "date": "2030-03-20",
        "totalCashFlow": 91930.898095,
        "interestPayment": 22075.00152,
        "principalBalance": 5228144.468302,
        "principalPayment": 69855.896575,
        "endPrincipalBalance": 5228144.468302,
        "beginPrincipalBalance": 5298000.364876,
        "prepayPrincipalPayment": 29252.834139,
        "scheduledPrincipalPayment": 40603.062436
    }
    {
        "date": "2030-04-20",
        "totalCashFlow": 94783.377283,
        "interestPayment": 21783.935285,
        "principalBalance": 5155145.026303,
        "principalPayment": 72999.441998,
        "endPrincipalBalance": 5155145.026303,
        "beginPrincipalBalance": 5228144.468302,
        "prepayPrincipalPayment": 32441.612514,
        "scheduledPrincipalPayment": 40557.829484
    }
    {
        "date": "2030-05-20",
        "totalCashFlow": 96634.588759,
        "interestPayment": 21479.770943,
        "principalBalance": 5079990.208487,
        "principalPayment": 75154.817816,
        "endPrincipalBalance": 5079990.208487,
        "beginPrincipalBalance": 5155145.026303,
        "prepayPrincipalPayment": 34670.263585,
        "scheduledPrincipalPayment": 40484.554231
    }
    {
        "date": "2030-06-20",
        "totalCashFlow": 98329.245993,
        "interestPayment": 21166.625869,
        "principalBalance": 5002827.588363,
        "principalPayment": 77162.620124,
        "endPrincipalBalance": 5002827.588363,
        "beginPrincipalBalance": 5079990.208487,
        "prepayPrincipalPayment": 36772.554392,
        "scheduledPrincipalPayment": 40390.065732
    }
    {
        "date": "2030-07-20",
        "totalCashFlow": 96125.359657,
        "interestPayment": 20845.114952,
        "principalBalance": 4927547.343658,
        "principalPayment": 75280.244705,
        "endPrincipalBalance": 4927547.343658,
        "beginPrincipalBalance": 5002827.588363,
        "prepayPrincipalPayment": 35005.467309,
        "scheduledPrincipalPayment": 40274.777396
    }
    {
        "date": "2030-08-20",
        "totalCashFlow": 96916.719418,
        "interestPayment": 20531.447265,
        "principalBalance": 4851162.071505,
        "principalPayment": 76385.272153,
        "endPrincipalBalance": 4851162.071505,
        "beginPrincipalBalance": 4927547.343658,
        "prepayPrincipalPayment": 36215.631651,
        "scheduledPrincipalPayment": 40169.640501
    }
    {
        "date": "2030-09-20",
        "totalCashFlow": 95139.016155,
        "interestPayment": 20213.175298,
        "principalBalance": 4776236.230647,
        "principalPayment": 74925.840857,
        "endPrincipalBalance": 4776236.230647,
        "beginPrincipalBalance": 4851162.071505,
        "prepayPrincipalPayment": 34875.431615,
        "scheduledPrincipalPayment": 40050.409243
    }
    {
        "date": "2030-10-20",
        "totalCashFlow": 91552.428074,
        "interestPayment": 19900.984294,
        "principalBalance": 4704584.786867,
        "principalPayment": 71651.44378,
        "endPrincipalBalance": 4704584.786867,
        "beginPrincipalBalance": 4776236.230647,
        "prepayPrincipalPayment": 31713.430933,
        "scheduledPrincipalPayment": 39938.012847
    }
    {
        "date": "2030-11-20",
        "totalCashFlow": 91486.524033,
        "interestPayment": 19602.436612,
        "principalBalance": 4632700.699447,
        "principalPayment": 71884.087421,
        "endPrincipalBalance": 4632700.699447,
        "beginPrincipalBalance": 4704584.786867,
        "prepayPrincipalPayment": 32035.966669,
        "scheduledPrincipalPayment": 39848.120752
    }
    {
        "date": "2030-12-20",
        "totalCashFlow": 87935.036582,
        "interestPayment": 19302.919581,
        "principalBalance": 4564068.582446,
        "principalPayment": 68632.117001,
        "endPrincipalBalance": 4564068.582446,
        "beginPrincipalBalance": 4632700.699447,
        "prepayPrincipalPayment": 28880.565113,
        "scheduledPrincipalPayment": 39751.551888
    }
    {
        "date": "2031-01-20",
        "totalCashFlow": 88217.232246,
        "interestPayment": 19016.952427,
        "principalBalance": 4494868.302627,
        "principalPayment": 69200.279819,
        "endPrincipalBalance": 4494868.302627,
        "beginPrincipalBalance": 4564068.582446,
        "prepayPrincipalPayment": 29521.916936,
        "scheduledPrincipalPayment": 39678.362883
    }
    {
        "date": "2031-02-20",
        "totalCashFlow": 84378.157293,
        "interestPayment": 18728.617928,
        "principalBalance": 4429218.763261,
        "principalPayment": 65649.539366,
        "endPrincipalBalance": 4429218.763261,
        "beginPrincipalBalance": 4494868.302627,
        "prepayPrincipalPayment": 26053.678099,
        "scheduledPrincipalPayment": 39595.861266
    }
    {
        "date": "2031-03-20",
        "totalCashFlow": 83292.546975,
        "interestPayment": 18455.07818,
        "principalBalance": 4364381.294467,
        "principalPayment": 64837.468795,
        "endPrincipalBalance": 4364381.294467,
        "beginPrincipalBalance": 4429218.763261,
        "prepayPrincipalPayment": 25297.002124,
        "scheduledPrincipalPayment": 39540.466671
    }
    {
        "date": "2031-04-20",
        "totalCashFlow": 85536.197841,
        "interestPayment": 18184.92206,
        "principalBalance": 4297030.018686,
        "principalPayment": 67351.275781,
        "endPrincipalBalance": 4297030.018686,
        "beginPrincipalBalance": 4364381.294467,
        "prepayPrincipalPayment": 27862.750502,
        "scheduledPrincipalPayment": 39488.525279
    }
    {
        "date": "2031-05-20",
        "totalCashFlow": 86946.951693,
        "interestPayment": 17904.291745,
        "principalBalance": 4227987.358738,
        "principalPayment": 69042.659948,
        "endPrincipalBalance": 4227987.358738,
        "beginPrincipalBalance": 4297030.018686,
        "prepayPrincipalPayment": 29632.963404,
        "scheduledPrincipalPayment": 39409.696544
    }
    {
        "date": "2031-06-20",
        "totalCashFlow": 87371.126866,
        "interestPayment": 17616.613995,
        "principalBalance": 4158232.845867,
        "principalPayment": 69754.512871,
        "endPrincipalBalance": 4158232.845867,
        "beginPrincipalBalance": 4227987.358738,
        "prepayPrincipalPayment": 30443.976192,
        "scheduledPrincipalPayment": 39310.536679
    }
    {
        "date": "2031-07-20",
        "totalCashFlow": 87203.05642,
        "interestPayment": 17325.970191,
        "principalBalance": 4088355.759638,
        "principalPayment": 69877.086229,
        "endPrincipalBalance": 4088355.759638,
        "beginPrincipalBalance": 4158232.845867,
        "prepayPrincipalPayment": 30677.628775,
        "scheduledPrincipalPayment": 39199.457454
    }
    {
        "date": "2031-08-20",
        "totalCashFlow": 86817.175778,
        "interestPayment": 17034.815665,
        "principalBalance": 4018573.399526,
        "principalPayment": 69782.360112,
        "endPrincipalBalance": 4018573.399526,
        "beginPrincipalBalance": 4088355.759638,
        "prepayPrincipalPayment": 30700.740251,
        "scheduledPrincipalPayment": 39081.619861
    }
    {
        "date": "2031-09-20",
        "totalCashFlow": 84457.799707,
        "interestPayment": 16744.055831,
        "principalBalance": 3950859.65565,
        "principalPayment": 67713.743876,
        "endPrincipalBalance": 3950859.65565,
        "beginPrincipalBalance": 4018573.399526,
        "prepayPrincipalPayment": 28754.868328,
        "scheduledPrincipalPayment": 38958.875548
    }
    {
        "date": "2031-10-20",
        "totalCashFlow": 82957.942528,
        "interestPayment": 16461.915232,
        "principalBalance": 3884363.628353,
        "principalPayment": 66496.027296,
        "endPrincipalBalance": 3884363.628353,
        "beginPrincipalBalance": 3950859.65565,
        "prepayPrincipalPayment": 27645.569448,
        "scheduledPrincipalPayment": 38850.457848
    }
    {
        "date": "2031-11-20",
        "totalCashFlow": 82030.707809,
        "interestPayment": 16184.848451,
        "principalBalance": 3818517.768996,
        "principalPayment": 65845.859357,
        "endPrincipalBalance": 3818517.768996,
        "beginPrincipalBalance": 3884363.628353,
        "prepayPrincipalPayment": 27097.324558,
        "scheduledPrincipalPayment": 38748.534799
    }
    {
        "date": "2031-12-20",
        "totalCashFlow": 78391.102623,
        "interestPayment": 15910.490704,
        "principalBalance": 3756037.157077,
        "principalPayment": 62480.611919,
        "endPrincipalBalance": 3756037.157077,
        "beginPrincipalBalance": 3818517.768996,
        "prepayPrincipalPayment": 23832.932722,
        "scheduledPrincipalPayment": 38647.679197
    }
    {
        "date": "2032-01-20",
        "totalCashFlow": 79793.650718,
        "interestPayment": 15650.154821,
        "principalBalance": 3691893.66118,
        "principalPayment": 64143.495897,
        "endPrincipalBalance": 3691893.66118,
        "beginPrincipalBalance": 3756037.157077,
        "prepayPrincipalPayment": 25567.641145,
        "scheduledPrincipalPayment": 38575.854752
    }
    {
        "date": "2032-02-20",
        "totalCashFlow": 75463.202131,
        "interestPayment": 15382.890255,
        "principalBalance": 3631813.349304,
        "principalPayment": 60080.311876,
        "endPrincipalBalance": 3631813.349304,
        "beginPrincipalBalance": 3691893.66118,
        "prepayPrincipalPayment": 21598.33121,
        "scheduledPrincipalPayment": 38481.980666
    }
    {
        "date": "2032-03-20",
        "totalCashFlow": 74990.530157,
        "interestPayment": 15132.555622,
        "principalBalance": 3571955.374769,
        "principalPayment": 59857.974535,
        "endPrincipalBalance": 3571955.374769,
        "beginPrincipalBalance": 3631813.349304,
        "prepayPrincipalPayment": 21432.303809,
        "scheduledPrincipalPayment": 38425.670726
    }
    {
        "date": "2032-04-20",
        "totalCashFlow": 77535.854092,
        "interestPayment": 14883.147395,
        "principalBalance": 3509302.668072,
        "principalPayment": 62652.706697,
        "endPrincipalBalance": 3509302.668072,
        "beginPrincipalBalance": 3571955.374769,
        "prepayPrincipalPayment": 24285.291727,
        "scheduledPrincipalPayment": 38367.41497
    }
    {
        "date": "2032-05-20",
        "totalCashFlow": 77996.497322,
        "interestPayment": 14622.09445,
        "principalBalance": 3445928.2652,
        "principalPayment": 63374.402872,
        "endPrincipalBalance": 3445928.2652,
        "beginPrincipalBalance": 3509302.668072,
        "prepayPrincipalPayment": 25100.161478,
        "scheduledPrincipalPayment": 38274.241394
    }
    {
        "date": "2032-06-20",
        "totalCashFlow": 77225.080123,
        "interestPayment": 14358.034438,
        "principalBalance": 3383061.219516,
        "principalPayment": 62867.045684,
        "endPrincipalBalance": 3383061.219516,
        "beginPrincipalBalance": 3445928.2652,
        "prepayPrincipalPayment": 24699.539401,
        "scheduledPrincipalPayment": 38167.506283
    }
    {
        "date": "2032-07-20",
        "totalCashFlow": 78361.356148,
        "interestPayment": 14096.088415,
        "principalBalance": 3318795.951783,
        "principalPayment": 64265.267733,
        "endPrincipalBalance": 3318795.951783,
        "beginPrincipalBalance": 3383061.219516,
        "prepayPrincipalPayment": 26204.83891,
        "scheduledPrincipalPayment": 38060.428823
    }
    {
        "date": "2032-08-20",
        "totalCashFlow": 76542.97884,
        "interestPayment": 13828.316466,
        "principalBalance": 3256081.289409,
        "principalPayment": 62714.662374,
        "endPrincipalBalance": 3256081.289409,
        "beginPrincipalBalance": 3318795.951783,
        "prepayPrincipalPayment": 24783.413999,
        "scheduledPrincipalPayment": 37931.248375
    }
    {
        "date": "2032-09-20",
        "totalCashFlow": 75837.987278,
        "interestPayment": 13567.005373,
        "principalBalance": 3193810.307503,
        "principalPayment": 62270.981906,
        "endPrincipalBalance": 3193810.307503,
        "beginPrincipalBalance": 3256081.289409,
        "prepayPrincipalPayment": 24457.803318,
        "scheduledPrincipalPayment": 37813.178588
    }
    {
        "date": "2032-10-20",
        "totalCashFlow": 73889.728862,
        "interestPayment": 13307.542948,
        "principalBalance": 3133228.121589,
        "principalPayment": 60582.185914,
        "endPrincipalBalance": 3133228.121589,
        "beginPrincipalBalance": 3193810.307503,
        "prepayPrincipalPayment": 22888.447332,
        "scheduledPrincipalPayment": 37693.738582
    }
    {
        "date": "2032-11-20",
        "totalCashFlow": 71982.842493,
        "interestPayment": 13055.117173,
        "principalBalance": 3074300.396269,
        "principalPayment": 58927.72532,
        "endPrincipalBalance": 3074300.396269,
        "beginPrincipalBalance": 3133228.121589,
        "prepayPrincipalPayment": 21339.888996,
        "scheduledPrincipalPayment": 37587.836324
    }
    {
        "date": "2032-12-20",
        "totalCashFlow": 71100.391235,
        "interestPayment": 12809.584984,
        "principalBalance": 3016009.590019,
        "principalPayment": 58290.806251,
        "endPrincipalBalance": 3016009.590019,
        "beginPrincipalBalance": 3074300.396269,
        "prepayPrincipalPayment": 20795.036768,
        "scheduledPrincipalPayment": 37495.769483
    }
    {
        "date": "2033-01-20",
        "totalCashFlow": 70541.347015,
        "interestPayment": 12566.706625,
        "principalBalance": 2958034.949629,
        "principalPayment": 57974.64039,
        "endPrincipalBalance": 2958034.949629,
        "beginPrincipalBalance": 3016009.590019,
        "prepayPrincipalPayment": 20568.985003,
        "scheduledPrincipalPayment": 37405.655387
    }
    {
        "date": "2033-02-20",
        "totalCashFlow": 67523.582244,
        "interestPayment": 12325.145623,
        "principalBalance": 2902836.513009,
        "principalPayment": 55198.43662,
        "endPrincipalBalance": 2902836.513009,
        "beginPrincipalBalance": 2958034.949629,
        "prepayPrincipalPayment": 17884.854567,
        "scheduledPrincipalPayment": 37313.582053
    }
    {
        "date": "2033-03-20",
        "totalCashFlow": 67043.633495,
        "interestPayment": 12095.152138,
        "principalBalance": 2847888.031651,
        "principalPayment": 54948.481358,
        "endPrincipalBalance": 2847888.031651,
        "beginPrincipalBalance": 2902836.513009,
        "prepayPrincipalPayment": 17697.430895,
        "scheduledPrincipalPayment": 37251.050463
    }
    {
        "date": "2033-04-20",
        "totalCashFlow": 69134.863254,
        "interestPayment": 11866.200132,
        "principalBalance": 2790619.368529,
        "principalPayment": 57268.663122,
        "endPrincipalBalance": 2790619.368529,
        "beginPrincipalBalance": 2847888.031651,
        "prepayPrincipalPayment": 20082.000681,
        "scheduledPrincipalPayment": 37186.662441
    }
    {
        "date": "2033-05-20",
        "totalCashFlow": 68416.587212,
        "interestPayment": 11627.580702,
        "principalBalance": 2733830.362019,
        "principalPayment": 56789.006509,
        "endPrincipalBalance": 2733830.362019,
        "beginPrincipalBalance": 2790619.368529,
        "prepayPrincipalPayment": 19702.815341,
        "scheduledPrincipalPayment": 37086.191168
    }
    {
        "date": "2033-06-20",
        "totalCashFlow": 68956.413497,
        "interestPayment": 11390.959842,
        "principalBalance": 2676264.908364,
        "principalPayment": 57565.453656,
        "endPrincipalBalance": 2676264.908364,
        "beginPrincipalBalance": 2733830.362019,
        "prepayPrincipalPayment": 20579.858323,
        "scheduledPrincipalPayment": 36985.595333
    }
    {
        "date": "2033-07-20",
        "totalCashFlow": 69168.399027,
        "interestPayment": 11151.103785,
        "principalBalance": 2618247.613122,
        "principalPayment": 58017.295242,
        "endPrincipalBalance": 2618247.613122,
        "beginPrincipalBalance": 2676264.908364,
        "prepayPrincipalPayment": 21149.692712,
        "scheduledPrincipalPayment": 36867.60253
    }
    {
        "date": "2033-08-20",
        "totalCashFlow": 67115.782482,
        "interestPayment": 10909.365055,
        "principalBalance": 2562041.195694,
        "principalPayment": 56206.417428,
        "endPrincipalBalance": 2562041.195694,
        "beginPrincipalBalance": 2618247.613122,
        "prepayPrincipalPayment": 19470.57732,
        "scheduledPrincipalPayment": 36735.840108
    }
    {
        "date": "2033-09-20",
        "totalCashFlow": 67437.066686,
        "interestPayment": 10675.171649,
        "principalBalance": 2505279.300657,
        "principalPayment": 56761.895037,
        "endPrincipalBalance": 2505279.300657,
        "beginPrincipalBalance": 2562041.195694,
        "prepayPrincipalPayment": 20139.975262,
        "scheduledPrincipalPayment": 36621.919775
    }
    {
        "date": "2033-10-20",
        "totalCashFlow": 65312.13937,
        "interestPayment": 10438.663753,
        "principalBalance": 2450405.82504,
        "principalPayment": 54873.475617,
        "endPrincipalBalance": 2450405.82504,
        "beginPrincipalBalance": 2505279.300657,
        "prepayPrincipalPayment": 18381.035987,
        "scheduledPrincipalPayment": 36492.439631
    }
    {
        "date": "2033-11-20",
        "totalCashFlow": 63719.671675,
        "interestPayment": 10210.024271,
        "principalBalance": 2396896.177636,
        "principalPayment": 53509.647404,
        "endPrincipalBalance": 2396896.177636,
        "beginPrincipalBalance": 2450405.82504,
        "prepayPrincipalPayment": 17126.819745,
        "scheduledPrincipalPayment": 36382.827658
    }
    {
        "date": "2033-12-20",
        "totalCashFlow": 62916.843889,
        "interestPayment": 9987.067407,
        "principalBalance": 2343966.401154,
        "principalPayment": 52929.776483,
        "endPrincipalBalance": 2343966.401154,
        "beginPrincipalBalance": 2396896.177636,
        "prepayPrincipalPayment": 16643.4168,
        "scheduledPrincipalPayment": 36286.359682
    }
    {
        "date": "2034-01-20",
        "totalCashFlow": 62363.597316,
        "interestPayment": 9766.526671,
        "principalBalance": 2291369.330509,
        "principalPayment": 52597.070644,
        "endPrincipalBalance": 2291369.330509,
        "beginPrincipalBalance": 2343966.401154,
        "prepayPrincipalPayment": 16405.310387,
        "scheduledPrincipalPayment": 36191.760257
    }
    {
        "date": "2034-02-20",
        "totalCashFlow": 59944.527889,
        "interestPayment": 9547.37221,
        "principalBalance": 2240972.174831,
        "principalPayment": 50397.155679,
        "endPrincipalBalance": 2240972.174831,
        "beginPrincipalBalance": 2291369.330509,
        "prepayPrincipalPayment": 14301.865492,
        "scheduledPrincipalPayment": 36095.290186
    }
    {
        "date": "2034-03-20",
        "totalCashFlow": 59464.058425,
        "interestPayment": 9337.384062,
        "principalBalance": 2190845.500467,
        "principalPayment": 50126.674364,
        "endPrincipalBalance": 2190845.500467,
        "beginPrincipalBalance": 2240972.174831,
        "prepayPrincipalPayment": 14099.781086,
        "scheduledPrincipalPayment": 36026.893278
    }
    {
        "date": "2034-04-20",
        "totalCashFlow": 60921.204541,
        "interestPayment": 9128.522919,
        "principalBalance": 2139052.818844,
        "principalPayment": 51792.681623,
        "endPrincipalBalance": 2139052.818844,
        "beginPrincipalBalance": 2190845.500467,
        "prepayPrincipalPayment": 15835.977136,
        "scheduledPrincipalPayment": 35956.704487
    }
    {
        "date": "2034-05-20",
        "totalCashFlow": 60067.722657,
        "interestPayment": 8912.720079,
        "principalBalance": 2087897.816266,
        "principalPayment": 51155.002579,
        "endPrincipalBalance": 2087897.816266,
        "beginPrincipalBalance": 2139052.818844,
        "prepayPrincipalPayment": 15302.815125,
        "scheduledPrincipalPayment": 35852.187454
    }
    {
        "date": "2034-06-20",
        "totalCashFlow": 60925.598495,
        "interestPayment": 8699.574234,
        "principalBalance": 2035671.792005,
        "principalPayment": 52226.024261,
        "endPrincipalBalance": 2035671.792005,
        "beginPrincipalBalance": 2087897.816266,
        "prepayPrincipalPayment": 16475.424894,
        "scheduledPrincipalPayment": 35750.599367
    }
    {
        "date": "2034-07-20",
        "totalCashFlow": 60547.156175,
        "interestPayment": 8481.9658,
        "principalBalance": 1983606.60163,
        "principalPayment": 52065.190375,
        "endPrincipalBalance": 1983606.60163,
        "beginPrincipalBalance": 2035671.792005,
        "prepayPrincipalPayment": 16442.911014,
        "scheduledPrincipalPayment": 35622.27936
    }
    {
        "date": "2034-08-20",
        "totalCashFlow": 58914.685674,
        "interestPayment": 8265.027507,
        "principalBalance": 1932956.943463,
        "principalPayment": 50649.658167,
        "endPrincipalBalance": 1932956.943463,
        "beginPrincipalBalance": 1983606.60163,
        "prepayPrincipalPayment": 15162.139392,
        "scheduledPrincipalPayment": 35487.518775
    }
    {
        "date": "2034-09-20",
        "totalCashFlow": 59046.888015,
        "interestPayment": 8053.987264,
        "principalBalance": 1881964.042713,
        "principalPayment": 50992.90075,
        "endPrincipalBalance": 1881964.042713,
        "beginPrincipalBalance": 1932956.943463,
        "prepayPrincipalPayment": 15624.009376,
        "scheduledPrincipalPayment": 35368.891375
    }
    {
        "date": "2034-10-20",
        "totalCashFlow": 57038.156912,
        "interestPayment": 7841.516845,
        "principalBalance": 1832767.402646,
        "principalPayment": 49196.640067,
        "endPrincipalBalance": 1832767.402646,
        "beginPrincipalBalance": 1881964.042713,
        "prepayPrincipalPayment": 13961.989922,
        "scheduledPrincipalPayment": 35234.650145
    }
    {
        "date": "2034-11-20",
        "totalCashFlow": 56416.303626,
        "interestPayment": 7636.530844,
        "principalBalance": 1783987.629865,
        "principalPayment": 48779.772782,
        "endPrincipalBalance": 1783987.629865,
        "beginPrincipalBalance": 1832767.402646,
        "prepayPrincipalPayment": 13655.027276,
        "scheduledPrincipalPayment": 35124.745506
    }
    {
        "date": "2034-12-20",
        "totalCashFlow": 55437.596378,
        "interestPayment": 7433.281791,
        "principalBalance": 1735983.315277,
        "principalPayment": 48004.314587,
        "endPrincipalBalance": 1735983.315277,
        "beginPrincipalBalance": 1783987.629865,
        "prepayPrincipalPayment": 12990.390002,
        "scheduledPrincipalPayment": 35013.924585
    }
    {
        "date": "2035-01-20",
        "totalCashFlow": 54699.374373,
        "interestPayment": 7233.263814,
        "principalBalance": 1688517.204718,
        "principalPayment": 47466.11056,
        "endPrincipalBalance": 1688517.204718,
        "beginPrincipalBalance": 1735983.315277,
        "prepayPrincipalPayment": 12556.726129,
        "scheduledPrincipalPayment": 34909.38443
    }
    {
        "date": "2035-02-20",
        "totalCashFlow": 53365.369483,
        "interestPayment": 7035.488353,
        "principalBalance": 1642187.323588,
        "principalPayment": 46329.88113,
        "endPrincipalBalance": 1642187.323588,
        "beginPrincipalBalance": 1688517.204718,
        "prepayPrincipalPayment": 11523.119094,
        "scheduledPrincipalPayment": 34806.762036
    }
    {
        "date": "2035-03-20",
        "totalCashFlow": 52730.388774,
        "interestPayment": 6842.447182,
        "principalBalance": 1596299.381996,
        "principalPayment": 45887.941592,
        "endPrincipalBalance": 1596299.381996,
        "beginPrincipalBalance": 1642187.323588,
        "prepayPrincipalPayment": 11169.039523,
        "scheduledPrincipalPayment": 34718.902069
    }
    {
        "date": "2035-04-20",
        "totalCashFlow": 53328.476004,
        "interestPayment": 6651.247425,
        "principalBalance": 1549622.153417,
        "principalPayment": 46677.228579,
        "endPrincipalBalance": 1549622.153417,
        "beginPrincipalBalance": 1596299.381996,
        "prepayPrincipalPayment": 12045.273419,
        "scheduledPrincipalPayment": 34631.95516
    }
    {
        "date": "2035-05-20",
        "totalCashFlow": 53230.032693,
        "interestPayment": 6456.758973,
        "principalBalance": 1502848.879696,
        "principalPayment": 46773.27372,
        "endPrincipalBalance": 1502848.879696,
        "beginPrincipalBalance": 1549622.153417,
        "prepayPrincipalPayment": 12254.655132,
        "scheduledPrincipalPayment": 34518.618588
    }
    {
        "date": "2035-06-20",
        "totalCashFlow": 53441.588709,
        "interestPayment": 6261.870332,
        "principalBalance": 1455669.161319,
        "principalPayment": 47179.718377,
        "endPrincipalBalance": 1455669.161319,
        "beginPrincipalBalance": 1502848.879696,
        "prepayPrincipalPayment": 12787.076312,
        "scheduledPrincipalPayment": 34392.642065
    }
    {
        "date": "2035-07-20",
        "totalCashFlow": 52751.096574,
        "interestPayment": 6065.288172,
        "principalBalance": 1408983.352917,
        "principalPayment": 46685.808402,
        "endPrincipalBalance": 1408983.352917,
        "beginPrincipalBalance": 1455669.161319,
        "prepayPrincipalPayment": 12440.084956,
        "scheduledPrincipalPayment": 34245.723446
    }
    {
        "date": "2035-08-20",
        "totalCashFlow": 52000.581102,
        "interestPayment": 5870.76397,
        "principalBalance": 1362853.535786,
        "principalPayment": 46129.817132,
        "endPrincipalBalance": 1362853.535786,
        "beginPrincipalBalance": 1408983.352917,
        "prepayPrincipalPayment": 12031.898735,
        "scheduledPrincipalPayment": 34097.918397
    }
    {
        "date": "2035-09-20",
        "totalCashFlow": 51647.749001,
        "interestPayment": 5678.556399,
        "principalBalance": 1316884.343184,
        "principalPayment": 45969.192602,
        "endPrincipalBalance": 1316884.343184,
        "beginPrincipalBalance": 1362853.535786,
        "prepayPrincipalPayment": 12018.41909,
        "scheduledPrincipalPayment": 33950.773512
    }
    {
        "date": "2035-10-20",
        "totalCashFlow": 49863.356467,
        "interestPayment": 5487.018097,
        "principalBalance": 1272508.004814,
        "principalPayment": 44376.33837,
        "endPrincipalBalance": 1272508.004814,
        "beginPrincipalBalance": 1316884.343184,
        "prepayPrincipalPayment": 10582.055443,
        "scheduledPrincipalPayment": 33794.282927
    }
    {
        "date": "2035-11-20",
        "totalCashFlow": 49677.616501,
        "interestPayment": 5302.116687,
        "principalBalance": 1228132.504999,
        "principalPayment": 44375.499814,
        "endPrincipalBalance": 1228132.504999,
        "beginPrincipalBalance": 1272508.004814,
        "prepayPrincipalPayment": 10709.947007,
        "scheduledPrincipalPayment": 33665.552808
    }
    {
        "date": "2035-12-20",
        "totalCashFlow": 48608.767567,
        "interestPayment": 5117.218771,
        "principalBalance": 1184640.956203,
        "principalPayment": 43491.548796,
        "endPrincipalBalance": 1184640.956203,
        "beginPrincipalBalance": 1228132.504999,
        "prepayPrincipalPayment": 9967.687949,
        "scheduledPrincipalPayment": 33523.860847
    }
    {
        "date": "2036-01-20",
        "totalCashFlow": 47895.417395,
        "interestPayment": 4936.003984,
        "principalBalance": 1141681.542792,
        "principalPayment": 42959.413411,
        "endPrincipalBalance": 1141681.542792,
        "beginPrincipalBalance": 1184640.956203,
        "prepayPrincipalPayment": 9566.504578,
        "scheduledPrincipalPayment": 33392.908833
    }
    {
        "date": "2036-02-20",
        "totalCashFlow": 46794.371141,
        "interestPayment": 4757.006428,
        "principalBalance": 1099644.17808,
        "principalPayment": 42037.364712,
        "endPrincipalBalance": 1099644.17808,
        "beginPrincipalBalance": 1141681.542792,
        "prepayPrincipalPayment": 8773.748794,
        "scheduledPrincipalPayment": 33263.615918
    }
    {
        "date": "2036-03-20",
        "totalCashFlow": 46303.072097,
        "interestPayment": 4581.850742,
        "principalBalance": 1057922.956724,
        "principalPayment": 41721.221355,
        "endPrincipalBalance": 1057922.956724,
        "beginPrincipalBalance": 1099644.17808,
        "prepayPrincipalPayment": 8573.22918,
        "scheduledPrincipalPayment": 33147.992175
    }
    {
        "date": "2036-04-20",
        "totalCashFlow": 46243.062364,
        "interestPayment": 4408.01232,
        "principalBalance": 1016087.90668,
        "principalPayment": 41835.050045,
        "endPrincipalBalance": 1016087.90668,
        "beginPrincipalBalance": 1057922.956724,
        "prepayPrincipalPayment": 8806.379383,
        "scheduledPrincipalPayment": 33028.670661
    }
    {
        "date": "2036-05-20",
        "totalCashFlow": 46100.522185,
        "interestPayment": 4233.699611,
        "principalBalance": 974221.084106,
        "principalPayment": 41866.822574,
        "endPrincipalBalance": 974221.084106,
        "beginPrincipalBalance": 1016087.90668,
        "prepayPrincipalPayment": 8975.416666,
        "scheduledPrincipalPayment": 32891.405909
    }
    {
        "date": "2036-06-20",
        "totalCashFlow": 45716.738785,
        "interestPayment": 4059.254517,
        "principalBalance": 932563.599838,
        "principalPayment": 41657.484268,
        "endPrincipalBalance": 932563.599838,
        "beginPrincipalBalance": 974221.084106,
        "prepayPrincipalPayment": 8920.492465,
        "scheduledPrincipalPayment": 32736.991803
    }
    {
        "date": "2036-07-20",
        "totalCashFlow": 45191.411673,
        "interestPayment": 3885.681666,
        "principalBalance": 891257.869831,
        "principalPayment": 41305.730007,
        "endPrincipalBalance": 891257.869831,
        "beginPrincipalBalance": 932563.599838,
        "prepayPrincipalPayment": 8733.808814,
        "scheduledPrincipalPayment": 32571.921193
    }
    {
        "date": "2036-08-20",
        "totalCashFlow": 44611.006034,
        "interestPayment": 3713.574458,
        "principalBalance": 850360.438255,
        "principalPayment": 40897.431576,
        "endPrincipalBalance": 850360.438255,
        "beginPrincipalBalance": 891257.869831,
        "prepayPrincipalPayment": 8497.253938,
        "scheduledPrincipalPayment": 32400.177639
    }
    {
        "date": "2036-09-20",
        "totalCashFlow": 43651.191264,
        "interestPayment": 3543.168493,
        "principalBalance": 810252.415483,
        "principalPayment": 40108.022771,
        "endPrincipalBalance": 810252.415483,
        "beginPrincipalBalance": 850360.438255,
        "prepayPrincipalPayment": 7884.845473,
        "scheduledPrincipalPayment": 32223.177298
    }
    {
        "date": "2036-10-20",
        "totalCashFlow": 42871.457082,
        "interestPayment": 3376.051731,
        "principalBalance": 770757.010132,
        "principalPayment": 39495.405351,
        "endPrincipalBalance": 770757.010132,
        "beginPrincipalBalance": 810252.415483,
        "prepayPrincipalPayment": 7439.971808,
        "scheduledPrincipalPayment": 32055.433543
    }
    {
        "date": "2036-11-20",
        "totalCashFlow": 42211.073456,
        "interestPayment": 3211.487542,
        "principalBalance": 731757.424218,
        "principalPayment": 38999.585913,
        "endPrincipalBalance": 731757.424218,
        "beginPrincipalBalance": 770757.010132,
        "prepayPrincipalPayment": 7108.542525,
        "scheduledPrincipalPayment": 31891.043389
    }
    {
        "date": "2036-12-20",
        "totalCashFlow": 41093.608155,
        "interestPayment": 3048.989268,
        "principalBalance": 693712.805331,
        "principalPayment": 38044.618888,
        "endPrincipalBalance": 693712.805331,
        "beginPrincipalBalance": 731757.424218,
        "prepayPrincipalPayment": 6319.056078,
        "scheduledPrincipalPayment": 31725.562809
    }
    {
        "date": "2037-01-20",
        "totalCashFlow": 40851.668197,
        "interestPayment": 2890.470022,
        "principalBalance": 655751.607156,
        "principalPayment": 37961.198175,
        "endPrincipalBalance": 655751.607156,
        "beginPrincipalBalance": 693712.805331,
        "prepayPrincipalPayment": 6381.325723,
        "scheduledPrincipalPayment": 31579.872452
    }
    {
        "date": "2037-02-20",
        "totalCashFlow": 39690.614787,
        "interestPayment": 2732.298363,
        "principalBalance": 618793.290732,
        "principalPayment": 36958.316424,
        "endPrincipalBalance": 618793.290732,
        "beginPrincipalBalance": 655751.607156,
        "prepayPrincipalPayment": 5542.837976,
        "scheduledPrincipalPayment": 31415.478449
    }
    {
        "date": "2037-03-20",
        "totalCashFlow": 39168.190421,
        "interestPayment": 2578.305378,
        "principalBalance": 582203.405689,
        "principalPayment": 36589.885043,
        "endPrincipalBalance": 582203.405689,
        "beginPrincipalBalance": 618793.290732,
        "prepayPrincipalPayment": 5313.976137,
        "scheduledPrincipalPayment": 31275.908906
    }
    {
        "date": "2037-04-20",
        "totalCashFlow": 39024.809076,
        "interestPayment": 2425.847524,
        "principalBalance": 545604.444137,
        "principalPayment": 36598.961552,
        "endPrincipalBalance": 545604.444137,
        "beginPrincipalBalance": 582203.405689,
        "prepayPrincipalPayment": 5467.243148,
        "scheduledPrincipalPayment": 31131.718404
    }
    {
        "date": "2037-05-20",
        "totalCashFlow": 38623.219048,
        "interestPayment": 2273.351851,
        "principalBalance": 509254.576939,
        "principalPayment": 36349.867198,
        "endPrincipalBalance": 509254.576939,
        "beginPrincipalBalance": 545604.444137,
        "prepayPrincipalPayment": 5389.077731,
        "scheduledPrincipalPayment": 30960.789466
    }
    {
        "date": "2037-06-20",
        "totalCashFlow": 37985.186879,
        "interestPayment": 2121.894071,
        "principalBalance": 473391.284131,
        "principalPayment": 35863.292808,
        "endPrincipalBalance": 473391.284131,
        "beginPrincipalBalance": 509254.576939,
        "prepayPrincipalPayment": 5089.609737,
        "scheduledPrincipalPayment": 30773.683072
    }
    {
        "date": "2037-07-20",
        "totalCashFlow": 37585.68091,
        "interestPayment": 1972.463684,
        "principalBalance": 437778.066905,
        "principalPayment": 35613.217226,
        "endPrincipalBalance": 437778.066905,
        "beginPrincipalBalance": 473391.284131,
        "prepayPrincipalPayment": 5030.626984,
        "scheduledPrincipalPayment": 30582.590242
    }
    {
        "date": "2037-08-20",
        "totalCashFlow": 36871.390778,
        "interestPayment": 1824.075279,
        "principalBalance": 402730.751405,
        "principalPayment": 35047.3155,
        "endPrincipalBalance": 402730.751405,
        "beginPrincipalBalance": 437778.066905,
        "prepayPrincipalPayment": 4676.863306,
        "scheduledPrincipalPayment": 30370.452193
    }
    {
        "date": "2037-09-20",
        "totalCashFlow": 36064.651027,
        "interestPayment": 1678.044798,
        "principalBalance": 368344.145176,
        "principalPayment": 34386.60623,
        "endPrincipalBalance": 368344.145176,
        "beginPrincipalBalance": 402730.751405,
        "prepayPrincipalPayment": 4230.446091,
        "scheduledPrincipalPayment": 30156.160138
    }
    {
        "date": "2037-10-20",
        "totalCashFlow": 35341.623503,
        "interestPayment": 1534.767272,
        "principalBalance": 334537.288944,
        "principalPayment": 33806.856232,
        "endPrincipalBalance": 334537.288944,
        "beginPrincipalBalance": 368344.145176,
        "prepayPrincipalPayment": 3859.69157,
        "scheduledPrincipalPayment": 29947.164662
    }
    {
        "date": "2037-11-20",
        "totalCashFlow": 34615.519934,
        "interestPayment": 1393.905371,
        "principalBalance": 301315.674381,
        "principalPayment": 33221.614563,
        "endPrincipalBalance": 301315.674381,
        "beginPrincipalBalance": 334537.288944,
        "prepayPrincipalPayment": 3483.536538,
        "scheduledPrincipalPayment": 29738.078026
    }
    {
        "date": "2037-12-20",
        "totalCashFlow": 33849.813851,
        "interestPayment": 1255.481977,
        "principalBalance": 268721.342507,
        "principalPayment": 32594.331874,
        "endPrincipalBalance": 268721.342507,
        "beginPrincipalBalance": 301315.674381,
        "prepayPrincipalPayment": 3064.572056,
        "scheduledPrincipalPayment": 29529.759818
    }
    {
        "date": "2038-01-20",
        "totalCashFlow": 33283.757989,
        "interestPayment": 1119.67226,
        "principalBalance": 236557.256779,
        "principalPayment": 32164.085728,
        "endPrincipalBalance": 236557.256779,
        "beginPrincipalBalance": 268721.342507,
        "prepayPrincipalPayment": 2836.638507,
        "scheduledPrincipalPayment": 29327.447221
    }
    {
        "date": "2038-02-20",
        "totalCashFlow": 32393.56878,
        "interestPayment": 985.655237,
        "principalBalance": 205149.343235,
        "principalPayment": 31407.913544,
        "endPrincipalBalance": 205149.343235,
        "beginPrincipalBalance": 236557.256779,
        "prepayPrincipalPayment": 2298.289401,
        "scheduledPrincipalPayment": 29109.624143
    }
    {
        "date": "2038-03-20",
        "totalCashFlow": 31790.112143,
        "interestPayment": 854.78893,
        "principalBalance": 174214.020022,
        "principalPayment": 30935.323213,
        "endPrincipalBalance": 174214.020022,
        "beginPrincipalBalance": 205149.343235,
        "prepayPrincipalPayment": 2019.379013,
        "scheduledPrincipalPayment": 28915.944201
    }
    {
        "date": "2038-04-20",
        "totalCashFlow": 31265.863285,
        "interestPayment": 725.89175,
        "principalBalance": 143674.048487,
        "principalPayment": 30539.971535,
        "endPrincipalBalance": 143674.048487,
        "beginPrincipalBalance": 174214.020022,
        "prepayPrincipalPayment": 1827.445969,
        "scheduledPrincipalPayment": 28712.525566
    }
    {
        "date": "2038-05-20",
        "totalCashFlow": 30567.483992,
        "interestPayment": 598.641869,
        "principalBalance": 113705.206364,
        "principalPayment": 29968.842123,
        "endPrincipalBalance": 113705.206364,
        "beginPrincipalBalance": 143674.048487,
        "prepayPrincipalPayment": 1490.060679,
        "scheduledPrincipalPayment": 28478.781444
    }
    {
        "date": "2038-06-20",
        "totalCashFlow": 29841.556843,
        "interestPayment": 473.771693,
        "principalBalance": 84337.421214,
        "principalPayment": 29367.78515,
        "endPrincipalBalance": 84337.421214,
        "beginPrincipalBalance": 113705.206364,
        "prepayPrincipalPayment": 1131.585127,
        "scheduledPrincipalPayment": 28236.200022
    }
    {
        "date": "2038-07-20",
        "totalCashFlow": 29126.135077,
        "interestPayment": 351.405922,
        "principalBalance": 55562.692059,
        "principalPayment": 28774.729155,
        "endPrincipalBalance": 55562.692059,
        "beginPrincipalBalance": 84337.421214,
        "prepayPrincipalPayment": 787.684259,
        "scheduledPrincipalPayment": 27987.044896
    }
    {
        "date": "2038-08-20",
        "totalCashFlow": 28339.059168,
        "interestPayment": 231.511217,
        "principalBalance": 27455.144108,
        "principalPayment": 28107.547951,
        "endPrincipalBalance": 27455.144108,
        "beginPrincipalBalance": 55562.692059,
        "prepayPrincipalPayment": 388.223908,
        "scheduledPrincipalPayment": 27719.324044
    }
    {
        "date": "2038-09-20",
        "totalCashFlow": 27569.540542,
        "interestPayment": 114.396434,
        "principalBalance": 0.0,
        "principalPayment": 27455.144108,
        "endPrincipalBalance": 0.0,
        "beginPrincipalBalance": 27455.144108,
        "prepayPrincipalPayment": 0.0,
        "scheduledPrincipalPayment": 27455.144108
    }

    """

    try:
        logger.info("Calling get_cash_flow_async")

        response = Client().yield_book_rest.get_cash_flow_async(
            id=id,
            id_type=id_type,
            pricing_date=pricing_date,
            par_amount=par_amount,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called get_cash_flow_async")

        return output
    except Exception as err:
        logger.error("Error get_cash_flow_async.")
        check_exception_and_raise(err, logger)


def get_cash_flow_sync(
    *,
    id: str,
    id_type: Optional[str] = None,
    pricing_date: Optional[str] = None,
    par_amount: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Get cash flow sync.

    Parameters
    ----------
    id : str
        Security reference ID.
    id_type : str, optional
        A sequence of textual characters.
    pricing_date : str, optional
        A sequence of textual characters.
    par_amount : str, optional
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------
    >>> # Formulate and execute the get request by using instrument ID and Par_amount
    >>> cf_sync_get_response = get_cash_flow_sync(
    >>>             id='01F002628', #01F002628
    >>>             par_amount="10000"
    >>>         )
    >>>
    >>> # Print full output to a file, as CF output is too long for terminal printout
    >>> # print(js.dumps(cf_sync_get_response, indent=4), file=open('.\\CF_sync_get_output.json', 'w+'))
    >>>
    >>> # Print onyl payment information
    >>> for paymentInfo in cf_sync_get_response["data"]["cashFlow"]["dataPaymentList"]:
    >>>     print(js.dumps(paymentInfo, indent=4))
    {
        "date": "2026-03-25",
        "totalCashFlow": 44388.458814,
        "interestPayment": 4166.666667,
        "principalBalance": 9959778.207853,
        "principalPayment": 40221.792147,
        "endPrincipalBalance": 9959778.207853,
        "beginPrincipalBalance": 10000000.0,
        "prepayPrincipalPayment": 15261.689129,
        "scheduledPrincipalPayment": 24960.103018
    }
    {
        "date": "2026-04-25",
        "totalCashFlow": 47982.609901,
        "interestPayment": 4149.907587,
        "principalBalance": 9915945.505539,
        "principalPayment": 43832.702314,
        "endPrincipalBalance": 9915945.505539,
        "beginPrincipalBalance": 9959778.207853,
        "prepayPrincipalPayment": 18884.827621,
        "scheduledPrincipalPayment": 24947.874693
    }
    {
        "date": "2026-05-25",
        "totalCashFlow": 50190.816923,
        "interestPayment": 4131.643961,
        "principalBalance": 9869886.332577,
        "principalPayment": 46059.172962,
        "endPrincipalBalance": 9869886.332577,
        "beginPrincipalBalance": 9915945.505539,
        "prepayPrincipalPayment": 21132.782982,
        "scheduledPrincipalPayment": 24926.38998
    }
    {
        "date": "2026-06-25",
        "totalCashFlow": 50465.372076,
        "interestPayment": 4112.452639,
        "principalBalance": 9823533.413139,
        "principalPayment": 46352.919438,
        "endPrincipalBalance": 9823533.413139,
        "beginPrincipalBalance": 9869886.332577,
        "prepayPrincipalPayment": 21453.87674,
        "scheduledPrincipalPayment": 24899.042698
    }
    {
        "date": "2026-07-25",
        "totalCashFlow": 53012.385342,
        "interestPayment": 4093.138922,
        "principalBalance": 9774614.166719,
        "principalPayment": 48919.24642,
        "endPrincipalBalance": 9774614.166719,
        "beginPrincipalBalance": 9823533.413139,
        "prepayPrincipalPayment": 24048.582925,
        "scheduledPrincipalPayment": 24870.663495
    }
    {
        "date": "2026-08-25",
        "totalCashFlow": 52874.355106,
        "interestPayment": 4072.755903,
        "principalBalance": 9725812.567517,
        "principalPayment": 48801.599203,
        "endPrincipalBalance": 9725812.567517,
        "beginPrincipalBalance": 9774614.166719,
        "prepayPrincipalPayment": 23966.131721,
        "scheduledPrincipalPayment": 24835.467482
    }
    {
        "date": "2026-09-25",
        "totalCashFlow": 51621.072654,
        "interestPayment": 4052.421903,
        "principalBalance": 9678243.916766,
        "principalPayment": 47568.650751,
        "endPrincipalBalance": 9678243.916766,
        "beginPrincipalBalance": 9725812.567517,
        "prepayPrincipalPayment": 22768.425156,
        "scheduledPrincipalPayment": 24800.225595
    }
    {
        "date": "2026-10-25",
        "totalCashFlow": 51171.25269,
        "interestPayment": 4032.601632,
        "principalBalance": 9631105.265708,
        "principalPayment": 47138.651058,
        "endPrincipalBalance": 9631105.265708,
        "beginPrincipalBalance": 9678243.916766,
        "prepayPrincipalPayment": 22370.859037,
        "scheduledPrincipalPayment": 24767.79202
    }
    {
        "date": "2026-11-25",
        "totalCashFlow": 50444.331088,
        "interestPayment": 4012.960527,
        "principalBalance": 9584673.895147,
        "principalPayment": 46431.370561,
        "endPrincipalBalance": 9584673.895147,
        "beginPrincipalBalance": 9631105.265708,
        "prepayPrincipalPayment": 21695.235153,
        "scheduledPrincipalPayment": 24736.135408
    }
    {
        "date": "2026-12-25",
        "totalCashFlow": 48825.848159,
        "interestPayment": 3993.614123,
        "principalBalance": 9539841.661111,
        "principalPayment": 44832.234036,
        "endPrincipalBalance": 9539841.661111,
        "beginPrincipalBalance": 9584673.895147,
        "prepayPrincipalPayment": 20126.254644,
        "scheduledPrincipalPayment": 24705.979391
    }
    {
        "date": "2027-01-25",
        "totalCashFlow": 50453.50088,
        "interestPayment": 3974.934025,
        "principalBalance": 9493363.094257,
        "principalPayment": 46478.566854,
        "endPrincipalBalance": 9493363.094257,
        "beginPrincipalBalance": 9539841.661111,
        "prepayPrincipalPayment": 21798.918852,
        "scheduledPrincipalPayment": 24679.648002
    }
    {
        "date": "2027-02-25",
        "totalCashFlow": 45469.973242,
        "interestPayment": 3955.567956,
        "principalBalance": 9451848.68897,
        "principalPayment": 41514.405286,
        "endPrincipalBalance": 9451848.68897,
        "beginPrincipalBalance": 9493363.094257,
        "prepayPrincipalPayment": 16865.648464,
        "scheduledPrincipalPayment": 24648.756822
    }
    {
        "date": "2027-03-25",
        "totalCashFlow": 46301.151236,
        "interestPayment": 3938.270287,
        "principalBalance": 9409485.808021,
        "principalPayment": 42362.880949,
        "endPrincipalBalance": 9409485.808021,
        "beginPrincipalBalance": 9451848.68897,
        "prepayPrincipalPayment": 17732.398372,
        "scheduledPrincipalPayment": 24630.482578
    }
    {
        "date": "2027-04-25",
        "totalCashFlow": 50312.157811,
        "interestPayment": 3920.619087,
        "principalBalance": 9363094.269296,
        "principalPayment": 46391.538725,
        "endPrincipalBalance": 9363094.269296,
        "beginPrincipalBalance": 9409485.808021,
        "prepayPrincipalPayment": 21781.777072,
        "scheduledPrincipalPayment": 24609.761653
    }
    {
        "date": "2027-05-25",
        "totalCashFlow": 51933.332953,
        "interestPayment": 3901.289279,
        "principalBalance": 9315062.225622,
        "principalPayment": 48032.043674,
        "endPrincipalBalance": 9315062.225622,
        "beginPrincipalBalance": 9363094.269296,
        "prepayPrincipalPayment": 23453.824244,
        "scheduledPrincipalPayment": 24578.219431
    }
    {
        "date": "2027-06-25",
        "totalCashFlow": 52050.96994,
        "interestPayment": 3881.275927,
        "principalBalance": 9266892.531609,
        "principalPayment": 48169.694012,
        "endPrincipalBalance": 9266892.531609,
        "beginPrincipalBalance": 9315062.225622,
        "prepayPrincipalPayment": 23627.66514,
        "scheduledPrincipalPayment": 24542.028872
    }
    {
        "date": "2027-07-25",
        "totalCashFlow": 54682.664688,
        "interestPayment": 3861.205222,
        "principalBalance": 9216071.072143,
        "principalPayment": 50821.459466,
        "endPrincipalBalance": 9216071.072143,
        "beginPrincipalBalance": 9266892.531609,
        "prepayPrincipalPayment": 26316.346322,
        "scheduledPrincipalPayment": 24505.113145
    }
    {
        "date": "2027-08-25",
        "totalCashFlow": 53324.385968,
        "interestPayment": 3840.029613,
        "principalBalance": 9166586.715788,
        "principalPayment": 49484.356355,
        "endPrincipalBalance": 9166586.715788,
        "beginPrincipalBalance": 9216071.072143,
        "prepayPrincipalPayment": 25023.564458,
        "scheduledPrincipalPayment": 24460.791897
    }
    {
        "date": "2027-09-25",
        "totalCashFlow": 53503.738292,
        "interestPayment": 3819.411132,
        "principalBalance": 9116902.388628,
        "principalPayment": 49684.32716,
        "endPrincipalBalance": 9116902.388628,
        "beginPrincipalBalance": 9166586.715788,
        "prepayPrincipalPayment": 25264.717563,
        "scheduledPrincipalPayment": 24419.609597
    }
    {
        "date": "2027-10-25",
        "totalCashFlow": 51886.461223,
        "interestPayment": 3798.709329,
        "principalBalance": 9068814.636734,
        "principalPayment": 48087.751895,
        "endPrincipalBalance": 9068814.636734,
        "beginPrincipalBalance": 9116902.388628,
        "prepayPrincipalPayment": 23710.259997,
        "scheduledPrincipalPayment": 24377.491898
    }
    {
        "date": "2027-11-25",
        "totalCashFlow": 50193.39363,
        "interestPayment": 3778.672765,
        "principalBalance": 9022399.915869,
        "principalPayment": 46414.720865,
        "endPrincipalBalance": 9022399.915869,
        "beginPrincipalBalance": 9068814.636734,
        "prepayPrincipalPayment": 22075.470299,
        "scheduledPrincipalPayment": 24339.250566
    }
    {
        "date": "2027-12-25",
        "totalCashFlow": 49998.876976,
        "interestPayment": 3759.333298,
        "principalBalance": 8976160.372191,
        "principalPayment": 46239.543678,
        "endPrincipalBalance": 8976160.372191,
        "beginPrincipalBalance": 9022399.915869,
        "prepayPrincipalPayment": 21934.408082,
        "scheduledPrincipalPayment": 24305.135595
    }
    {
        "date": "2028-01-25",
        "totalCashFlow": 50278.022827,
        "interestPayment": 3740.066822,
        "principalBalance": 8929622.416186,
        "principalPayment": 46537.956005,
        "endPrincipalBalance": 8929622.416186,
        "beginPrincipalBalance": 8976160.372191,
        "prepayPrincipalPayment": 22266.812237,
        "scheduledPrincipalPayment": 24271.143768
    }
    {
        "date": "2028-02-25",
        "totalCashFlow": 46259.973026,
        "interestPayment": 3720.676007,
        "principalBalance": 8887083.119167,
        "principalPayment": 42539.297019,
        "endPrincipalBalance": 8887083.119167,
        "beginPrincipalBalance": 8929622.416186,
        "prepayPrincipalPayment": 18303.305423,
        "scheduledPrincipalPayment": 24235.991596
    }
    {
        "date": "2028-03-25",
        "totalCashFlow": 47276.005827,
        "interestPayment": 3702.9513,
        "principalBalance": 8843510.06464,
        "principalPayment": 43573.054528,
        "endPrincipalBalance": 8843510.06464,
        "beginPrincipalBalance": 8887083.119167,
        "prepayPrincipalPayment": 19361.681404,
        "scheduledPrincipalPayment": 24211.373123
    }
    {
        "date": "2028-04-25",
        "totalCashFlow": 51520.936796,
        "interestPayment": 3684.79586,
        "principalBalance": 8795673.923704,
        "principalPayment": 47836.140935,
        "endPrincipalBalance": 8795673.923704,
        "beginPrincipalBalance": 8843510.06464,
        "prepayPrincipalPayment": 23652.494488,
        "scheduledPrincipalPayment": 24183.646447
    }
    {
        "date": "2028-05-25",
        "totalCashFlow": 50835.671472,
        "interestPayment": 3664.864135,
        "principalBalance": 8748503.116367,
        "principalPayment": 47170.807337,
        "endPrincipalBalance": 8748503.116367,
        "beginPrincipalBalance": 8795673.923704,
        "prepayPrincipalPayment": 23026.895117,
        "scheduledPrincipalPayment": 24143.91222
    }
    {
        "date": "2028-06-25",
        "totalCashFlow": 55323.044772,
        "interestPayment": 3645.209632,
        "principalBalance": 8696825.281227,
        "principalPayment": 51677.83514,
        "endPrincipalBalance": 8696825.281227,
        "beginPrincipalBalance": 8748503.116367,
        "prepayPrincipalPayment": 27572.221287,
        "scheduledPrincipalPayment": 24105.613853
    }
    {
        "date": "2028-07-25",
        "totalCashFlow": 56413.342255,
        "interestPayment": 3623.677201,
        "principalBalance": 8644035.616172,
        "principalPayment": 52789.665054,
        "endPrincipalBalance": 8644035.616172,
        "beginPrincipalBalance": 8696825.281227,
        "prepayPrincipalPayment": 28735.202918,
        "scheduledPrincipalPayment": 24054.462136
    }
    {
        "date": "2028-08-25",
        "totalCashFlow": 53958.59513,
        "interestPayment": 3601.681507,
        "principalBalance": 8593678.702549,
        "principalPayment": 50356.913624,
        "endPrincipalBalance": 8593678.702549,
        "beginPrincipalBalance": 8644035.616172,
        "prepayPrincipalPayment": 26357.176625,
        "scheduledPrincipalPayment": 23999.736999
    }
    {
        "date": "2028-09-25",
        "totalCashFlow": 56290.502702,
        "interestPayment": 3580.699459,
        "principalBalance": 8540968.899306,
        "principalPayment": 52709.803242,
        "endPrincipalBalance": 8540968.899306,
        "beginPrincipalBalance": 8593678.702549,
        "prepayPrincipalPayment": 28758.526099,
        "scheduledPrincipalPayment": 23951.277143
    }
    {
        "date": "2028-10-25",
        "totalCashFlow": 52458.075434,
        "interestPayment": 3558.737041,
        "principalBalance": 8492069.560914,
        "principalPayment": 48899.338393,
        "endPrincipalBalance": 8492069.560914,
        "beginPrincipalBalance": 8540968.899306,
        "prepayPrincipalPayment": 25003.57208,
        "scheduledPrincipalPayment": 23895.766313
    }
    {
        "date": "2028-11-25",
        "totalCashFlow": 52395.265386,
        "interestPayment": 3538.362317,
        "principalBalance": 8443212.657844,
        "principalPayment": 48856.903069,
        "endPrincipalBalance": 8443212.657844,
        "beginPrincipalBalance": 8492069.560914,
        "prepayPrincipalPayment": 25006.469209,
        "scheduledPrincipalPayment": 23850.43386
    }
    {
        "date": "2028-12-25",
        "totalCashFlow": 51261.365907,
        "interestPayment": 3518.005274,
        "principalBalance": 8395469.297212,
        "principalPayment": 47743.360633,
        "endPrincipalBalance": 8395469.297212,
        "beginPrincipalBalance": 8443212.657844,
        "prepayPrincipalPayment": 23938.585755,
        "scheduledPrincipalPayment": 23804.774878
    }
    {
        "date": "2029-01-25",
        "totalCashFlow": 50668.611909,
        "interestPayment": 3498.112207,
        "principalBalance": 8348298.79751,
        "principalPayment": 47170.499702,
        "endPrincipalBalance": 8348298.79751,
        "beginPrincipalBalance": 8395469.297212,
        "prepayPrincipalPayment": 23408.681907,
        "scheduledPrincipalPayment": 23761.817794
    }
    {
        "date": "2029-02-25",
        "totalCashFlow": 47704.901782,
        "interestPayment": 3478.457832,
        "principalBalance": 8304072.353561,
        "principalPayment": 44226.443949,
        "endPrincipalBalance": 8304072.353561,
        "beginPrincipalBalance": 8348298.79751,
        "prepayPrincipalPayment": 20506.385453,
        "scheduledPrincipalPayment": 23720.058496
    }
    {
        "date": "2029-03-25",
        "totalCashFlow": 47386.823123,
        "interestPayment": 3460.030147,
        "principalBalance": 8260145.560585,
        "principalPayment": 43926.792976,
        "endPrincipalBalance": 8260145.560585,
        "beginPrincipalBalance": 8304072.353561,
        "prepayPrincipalPayment": 20240.517855,
        "scheduledPrincipalPayment": 23686.275121
    }
    {
        "date": "2029-04-25",
        "totalCashFlow": 51714.882098,
        "interestPayment": 3441.727317,
        "principalBalance": 8211872.405803,
        "principalPayment": 48273.154782,
        "endPrincipalBalance": 8211872.405803,
        "beginPrincipalBalance": 8260145.560585,
        "prepayPrincipalPayment": 24620.165334,
        "scheduledPrincipalPayment": 23652.989447
    }
    {
        "date": "2029-05-25",
        "totalCashFlow": 53818.444952,
        "interestPayment": 3421.613502,
        "principalBalance": 8161475.574354,
        "principalPayment": 50396.831449,
        "endPrincipalBalance": 8161475.574354,
        "beginPrincipalBalance": 8211872.405803,
        "prepayPrincipalPayment": 26789.979607,
        "scheduledPrincipalPayment": 23606.851842
    }
    {
        "date": "2029-06-25",
        "totalCashFlow": 57424.247186,
        "interestPayment": 3400.614823,
        "principalBalance": 8107451.941991,
        "principalPayment": 54023.632364,
        "endPrincipalBalance": 8107451.941991,
        "beginPrincipalBalance": 8161475.574354,
        "prepayPrincipalPayment": 30469.506285,
        "scheduledPrincipalPayment": 23554.126079
    }
    {
        "date": "2029-07-25",
        "totalCashFlow": 57260.219057,
        "interestPayment": 3378.104976,
        "principalBalance": 8053569.827909,
        "principalPayment": 53882.114081,
        "endPrincipalBalance": 8053569.827909,
        "beginPrincipalBalance": 8107451.941991,
        "prepayPrincipalPayment": 30391.734233,
        "scheduledPrincipalPayment": 23490.379848
    }
    {
        "date": "2029-08-25",
        "totalCashFlow": 56714.159057,
        "interestPayment": 3355.654095,
        "principalBalance": 8000211.322947,
        "principalPayment": 53358.504962,
        "endPrincipalBalance": 8000211.322947,
        "beginPrincipalBalance": 8053569.827909,
        "prepayPrincipalPayment": 29932.060278,
        "scheduledPrincipalPayment": 23426.444684
    }
    {
        "date": "2029-09-25",
        "totalCashFlow": 57965.642689,
        "interestPayment": 3333.421385,
        "principalBalance": 7945579.101642,
        "principalPayment": 54632.221305,
        "endPrincipalBalance": 7945579.101642,
        "beginPrincipalBalance": 8000211.322947,
        "prepayPrincipalPayment": 31268.786233,
        "scheduledPrincipalPayment": 23363.435072
    }
    {
        "date": "2029-10-25",
        "totalCashFlow": 52388.065775,
        "interestPayment": 3310.657959,
        "principalBalance": 7896501.693826,
        "principalPayment": 49077.407816,
        "endPrincipalBalance": 7896501.693826,
        "beginPrincipalBalance": 7945579.101642,
        "prepayPrincipalPayment": 25781.314558,
        "scheduledPrincipalPayment": 23296.093258
    }
    {
        "date": "2029-11-25",
        "totalCashFlow": 54268.961942,
        "interestPayment": 3290.209039,
        "principalBalance": 7845522.940923,
        "principalPayment": 50978.752903,
        "endPrincipalBalance": 7845522.940923,
        "beginPrincipalBalance": 7896501.693826,
        "prepayPrincipalPayment": 27734.283825,
        "scheduledPrincipalPayment": 23244.469078
    }
    {
        "date": "2029-12-25",
        "totalCashFlow": 51853.914591,
        "interestPayment": 3268.967892,
        "principalBalance": 7796937.994223,
        "principalPayment": 48584.946699,
        "endPrincipalBalance": 7796937.994223,
        "beginPrincipalBalance": 7845522.940923,
        "prepayPrincipalPayment": 25398.230738,
        "scheduledPrincipalPayment": 23186.715961
    }
    {
        "date": "2030-01-25",
        "totalCashFlow": 51055.421479,
        "interestPayment": 3248.724164,
        "principalBalance": 7749131.296908,
        "principalPayment": 47806.697315,
        "endPrincipalBalance": 7749131.296908,
        "beginPrincipalBalance": 7796937.994223,
        "prepayPrincipalPayment": 24671.19156,
        "scheduledPrincipalPayment": 23135.505755
    }
    {
        "date": "2030-02-25",
        "totalCashFlow": 47693.262332,
        "interestPayment": 3228.804707,
        "principalBalance": 7704666.839284,
        "principalPayment": 44464.457625,
        "endPrincipalBalance": 7704666.839284,
        "beginPrincipalBalance": 7749131.296908,
        "prepayPrincipalPayment": 21378.352458,
        "scheduledPrincipalPayment": 23086.105166
    }
    {
        "date": "2030-03-25",
        "totalCashFlow": 47181.950732,
        "interestPayment": 3210.27785,
        "principalBalance": 7660695.166401,
        "principalPayment": 43971.672883,
        "endPrincipalBalance": 7660695.166401,
        "beginPrincipalBalance": 7704666.839284,
        "prepayPrincipalPayment": 20925.466637,
        "scheduledPrincipalPayment": 23046.206246
    }
    {
        "date": "2030-04-25",
        "totalCashFlow": 51173.76293,
        "interestPayment": 3191.956319,
        "principalBalance": 7612713.359791,
        "principalPayment": 47981.806611,
        "endPrincipalBalance": 7612713.359791,
        "beginPrincipalBalance": 7660695.166401,
        "prepayPrincipalPayment": 24974.439358,
        "scheduledPrincipalPayment": 23007.367253
    }
    {
        "date": "2030-05-25",
        "totalCashFlow": 54256.264604,
        "interestPayment": 3171.9639,
        "principalBalance": 7561629.059087,
        "principalPayment": 51084.300704,
        "endPrincipalBalance": 7561629.059087,
        "beginPrincipalBalance": 7612713.359791,
        "prepayPrincipalPayment": 28128.277492,
        "scheduledPrincipalPayment": 22956.023212
    }
    {
        "date": "2030-06-25",
        "totalCashFlow": 57289.417875,
        "interestPayment": 3150.678775,
        "principalBalance": 7507490.319987,
        "principalPayment": 54138.7391,
        "endPrincipalBalance": 7507490.319987,
        "beginPrincipalBalance": 7561629.059087,
        "prepayPrincipalPayment": 31243.968934,
        "scheduledPrincipalPayment": 22894.770166
    }
    {
        "date": "2030-07-25",
        "totalCashFlow": 55743.611242,
        "interestPayment": 3128.120967,
        "principalBalance": 7454874.829711,
        "principalPayment": 52615.490276,
        "endPrincipalBalance": 7454874.829711,
        "beginPrincipalBalance": 7507490.319987,
        "prepayPrincipalPayment": 29791.856648,
        "scheduledPrincipalPayment": 22823.633628
    }
    {
        "date": "2030-08-25",
        "totalCashFlow": 57649.89698,
        "interestPayment": 3106.197846,
        "principalBalance": 7400331.130576,
        "principalPayment": 54543.699135,
        "endPrincipalBalance": 7400331.130576,
        "beginPrincipalBalance": 7454874.829711,
        "prepayPrincipalPayment": 31787.232375,
        "scheduledPrincipalPayment": 22756.46676
    }
    {
        "date": "2030-09-25",
        "totalCashFlow": 56431.526975,
        "interestPayment": 3083.471304,
        "principalBalance": 7346983.074905,
        "principalPayment": 53348.055671,
        "endPrincipalBalance": 7346983.074905,
        "beginPrincipalBalance": 7400331.130576,
        "prepayPrincipalPayment": 30665.315242,
        "scheduledPrincipalPayment": 22682.740429
    }
    {
        "date": "2030-10-25",
        "totalCashFlow": 52898.299536,
        "interestPayment": 3061.242948,
        "principalBalance": 7297146.018317,
        "principalPayment": 49837.056588,
        "endPrincipalBalance": 7297146.018317,
        "beginPrincipalBalance": 7346983.074905,
        "prepayPrincipalPayment": 27225.067693,
        "scheduledPrincipalPayment": 22611.988896
    }
    {
        "date": "2030-11-25",
        "totalCashFlow": 53632.879501,
        "interestPayment": 3040.477508,
        "principalBalance": 7246553.616324,
        "principalPayment": 50592.401993,
        "endPrincipalBalance": 7246553.616324,
        "beginPrincipalBalance": 7297146.018317,
        "prepayPrincipalPayment": 28040.996431,
        "scheduledPrincipalPayment": 22551.405562
    }
    {
        "date": "2030-12-25",
        "totalCashFlow": 50022.635212,
        "interestPayment": 3019.39734,
        "principalBalance": 7199550.378452,
        "principalPayment": 47003.237872,
        "endPrincipalBalance": 7199550.378452,
        "beginPrincipalBalance": 7246553.616324,
        "prepayPrincipalPayment": 24515.359527,
        "scheduledPrincipalPayment": 22487.878345
    }
    {
        "date": "2031-01-25",
        "totalCashFlow": 51224.24979,
        "interestPayment": 2999.812658,
        "principalBalance": 7151325.94132,
        "principalPayment": 48224.437132,
        "endPrincipalBalance": 7151325.94132,
        "beginPrincipalBalance": 7199550.378452,
        "prepayPrincipalPayment": 25789.527556,
        "scheduledPrincipalPayment": 22434.909576
    }
    {
        "date": "2031-02-25",
        "totalCashFlow": 46694.063742,
        "interestPayment": 2979.719142,
        "principalBalance": 7107611.59672,
        "principalPayment": 43714.3446,
        "endPrincipalBalance": 7107611.59672,
        "beginPrincipalBalance": 7151325.94132,
        "prepayPrincipalPayment": 21336.764656,
        "scheduledPrincipalPayment": 22377.579944
    }
    {
        "date": "2031-03-25",
        "totalCashFlow": 46131.448046,
        "interestPayment": 2961.504832,
        "principalBalance": 7064441.653506,
        "principalPayment": 43169.943214,
        "endPrincipalBalance": 7064441.653506,
        "beginPrincipalBalance": 7107611.59672,
        "prepayPrincipalPayment": 20836.098596,
        "scheduledPrincipalPayment": 22333.844618
    }
    {
        "date": "2031-04-25",
        "totalCashFlow": 50194.655989,
        "interestPayment": 2943.517356,
        "principalBalance": 7017190.514873,
        "principalPayment": 47251.138634,
        "endPrincipalBalance": 7017190.514873,
        "beginPrincipalBalance": 7064441.653506,
        "prepayPrincipalPayment": 24959.776477,
        "scheduledPrincipalPayment": 22291.362156
    }
    {
        "date": "2031-05-25",
        "totalCashFlow": 53329.17828,
        "interestPayment": 2923.829381,
        "principalBalance": 6966785.165974,
        "principalPayment": 50405.348899,
        "endPrincipalBalance": 6966785.165974,
        "beginPrincipalBalance": 7017190.514873,
        "prepayPrincipalPayment": 28169.857045,
        "scheduledPrincipalPayment": 22235.491854
    }
    {
        "date": "2031-06-25",
        "totalCashFlow": 55153.433529,
        "interestPayment": 2902.827152,
        "principalBalance": 6914534.559597,
        "principalPayment": 52250.606377,
        "endPrincipalBalance": 6914534.559597,
        "beginPrincipalBalance": 6966785.165974,
        "prepayPrincipalPayment": 30081.591885,
        "scheduledPrincipalPayment": 22169.014492
    }
    {
        "date": "2031-07-25",
        "totalCashFlow": 56103.07118,
        "interestPayment": 2881.056066,
        "principalBalance": 6861312.544483,
        "principalPayment": 53222.015114,
        "endPrincipalBalance": 6861312.544483,
        "beginPrincipalBalance": 6914534.559597,
        "prepayPrincipalPayment": 31126.036165,
        "scheduledPrincipalPayment": 22095.978949
    }
    {
        "date": "2031-08-25",
        "totalCashFlow": 56662.721083,
        "interestPayment": 2858.880227,
        "principalBalance": 6807508.703628,
        "principalPayment": 53803.840856,
        "endPrincipalBalance": 6807508.703628,
        "beginPrincipalBalance": 6861312.544483,
        "prepayPrincipalPayment": 31784.733951,
        "scheduledPrincipalPayment": 22019.106904
    }
    {
        "date": "2031-09-25",
        "totalCashFlow": 54144.523091,
        "interestPayment": 2836.46196,
        "principalBalance": 6756200.642496,
        "principalPayment": 51308.061131,
        "endPrincipalBalance": 6756200.642496,
        "beginPrincipalBalance": 6807508.703628,
        "prepayPrincipalPayment": 29368.455211,
        "scheduledPrincipalPayment": 21939.605921
    }
    {
        "date": "2031-10-25",
        "totalCashFlow": 52881.0798,
        "interestPayment": 2815.083601,
        "principalBalance": 6706134.646297,
        "principalPayment": 50065.996199,
        "endPrincipalBalance": 6706134.646297,
        "beginPrincipalBalance": 6756200.642496,
        "prepayPrincipalPayment": 28198.591706,
        "scheduledPrincipalPayment": 21867.404494
    }
    {
        "date": "2031-11-25",
        "totalCashFlow": 52406.608698,
        "interestPayment": 2794.222769,
        "principalBalance": 6656522.260369,
        "principalPayment": 49612.385928,
        "endPrincipalBalance": 6656522.260369,
        "beginPrincipalBalance": 6706134.646297,
        "prepayPrincipalPayment": 27813.863386,
        "scheduledPrincipalPayment": 21798.522543
    }
    {
        "date": "2031-12-25",
        "totalCashFlow": 47638.108444,
        "interestPayment": 2773.550942,
        "principalBalance": 6611657.702867,
        "principalPayment": 44864.557502,
        "endPrincipalBalance": 6611657.702867,
        "beginPrincipalBalance": 6656522.260369,
        "prepayPrincipalPayment": 23134.127413,
        "scheduledPrincipalPayment": 21730.430089
    }
    {
        "date": "2032-01-25",
        "totalCashFlow": 50910.364665,
        "interestPayment": 2754.857376,
        "principalBalance": 6563502.195577,
        "principalPayment": 48155.507289,
        "endPrincipalBalance": 6563502.195577,
        "beginPrincipalBalance": 6611657.702867,
        "prepayPrincipalPayment": 26478.289713,
        "scheduledPrincipalPayment": 21677.217576
    }
    {
        "date": "2032-02-25",
        "totalCashFlow": 44442.304719,
        "interestPayment": 2734.792581,
        "principalBalance": 6521794.68344,
        "principalPayment": 41707.512138,
        "endPrincipalBalance": 6521794.68344,
        "beginPrincipalBalance": 6563502.195577,
        "prepayPrincipalPayment": 20094.903086,
        "scheduledPrincipalPayment": 21612.609052
    }
    {
        "date": "2032-03-25",
        "totalCashFlow": 44656.504626,
        "interestPayment": 2717.414451,
        "principalBalance": 6479855.593266,
        "principalPayment": 41939.090174,
        "endPrincipalBalance": 6479855.593266,
        "beginPrincipalBalance": 6521794.68344,
        "prepayPrincipalPayment": 20370.425191,
        "scheduledPrincipalPayment": 21568.664983
    }
    {
        "date": "2032-04-25",
        "totalCashFlow": 50204.208159,
        "interestPayment": 2699.939831,
        "principalBalance": 6432351.324937,
        "principalPayment": 47504.268328,
        "endPrincipalBalance": 6432351.324937,
        "beginPrincipalBalance": 6479855.593266,
        "prepayPrincipalPayment": 25980.798332,
        "scheduledPrincipalPayment": 21523.469996
    }
    {
        "date": "2032-05-25",
        "totalCashFlow": 52393.67496,
        "interestPayment": 2680.146385,
        "principalBalance": 6382637.796363,
        "principalPayment": 49713.528575,
        "endPrincipalBalance": 6382637.796363,
        "beginPrincipalBalance": 6432351.324937,
        "prepayPrincipalPayment": 28254.313839,
        "scheduledPrincipalPayment": 21459.214736
    }
    {
        "date": "2032-06-25",
        "totalCashFlow": 52371.812087,
        "interestPayment": 2659.432415,
        "principalBalance": 6332925.416691,
        "principalPayment": 49712.379672,
        "endPrincipalBalance": 6332925.416691,
        "beginPrincipalBalance": 6382637.796363,
        "prepayPrincipalPayment": 28325.485925,
        "scheduledPrincipalPayment": 21386.893747
    }
    {
        "date": "2032-07-25",
        "totalCashFlow": 55851.892061,
        "interestPayment": 2638.718924,
        "principalBalance": 6279712.243554,
        "principalPayment": 53213.173137,
        "endPrincipalBalance": 6279712.243554,
        "beginPrincipalBalance": 6332925.416691,
        "prepayPrincipalPayment": 31899.332499,
        "scheduledPrincipalPayment": 21313.840638
    }
    {
        "date": "2032-08-25",
        "totalCashFlow": 53729.717513,
        "interestPayment": 2616.546768,
        "principalBalance": 6228599.072809,
        "principalPayment": 51113.170745,
        "endPrincipalBalance": 6228599.072809,
        "beginPrincipalBalance": 6279712.243554,
        "prepayPrincipalPayment": 29884.962061,
        "scheduledPrincipalPayment": 21228.208683
    }
    {
        "date": "2032-09-25",
        "totalCashFlow": 53626.633065,
        "interestPayment": 2595.249614,
        "principalBalance": 6177567.689358,
        "principalPayment": 51031.383451,
        "endPrincipalBalance": 6177567.689358,
        "beginPrincipalBalance": 6228599.072809,
        "prepayPrincipalPayment": 29882.534715,
        "scheduledPrincipalPayment": 21148.848736
    }
    {
        "date": "2032-10-25",
        "totalCashFlow": 51082.780828,
        "interestPayment": 2573.986537,
        "principalBalance": 6129058.895067,
        "principalPayment": 48508.794291,
        "endPrincipalBalance": 6129058.895067,
        "beginPrincipalBalance": 6177567.689358,
        "prepayPrincipalPayment": 27439.831668,
        "scheduledPrincipalPayment": 21068.962622
    }
    {
        "date": "2032-11-25",
        "totalCashFlow": 48423.262519,
        "interestPayment": 2553.77454,
        "principalBalance": 6083189.407088,
        "principalPayment": 45869.48798,
        "endPrincipalBalance": 6083189.407088,
        "beginPrincipalBalance": 6129058.895067,
        "prepayPrincipalPayment": 24872.58179,
        "scheduledPrincipalPayment": 20996.90619
    }
    {
        "date": "2032-12-25",
        "totalCashFlow": 47879.451907,
        "interestPayment": 2534.662253,
        "principalBalance": 6037844.617434,
        "principalPayment": 45344.789654,
        "endPrincipalBalance": 6037844.617434,
        "beginPrincipalBalance": 6083189.407088,
        "prepayPrincipalPayment": 24411.602055,
        "scheduledPrincipalPayment": 20933.187599
    }
    {
        "date": "2033-01-25",
        "totalCashFlow": 47893.179777,
        "interestPayment": 2515.768591,
        "principalBalance": 5992467.206248,
        "principalPayment": 45377.411186,
        "endPrincipalBalance": 5992467.206248,
        "beginPrincipalBalance": 6037844.617434,
        "prepayPrincipalPayment": 24506.800125,
        "scheduledPrincipalPayment": 20870.611061
    }
    {
        "date": "2033-02-25",
        "totalCashFlow": 42482.849654,
        "interestPayment": 2496.861336,
        "principalBalance": 5952481.21793,
        "principalPayment": 39985.988318,
        "endPrincipalBalance": 5952481.21793,
        "beginPrincipalBalance": 5992467.206248,
        "prepayPrincipalPayment": 19178.730421,
        "scheduledPrincipalPayment": 20807.257897
    }
    {
        "date": "2033-03-25",
        "totalCashFlow": 42644.328131,
        "interestPayment": 2480.200507,
        "principalBalance": 5912317.090306,
        "principalPayment": 40164.127624,
        "endPrincipalBalance": 5912317.090306,
        "beginPrincipalBalance": 5952481.21793,
        "prepayPrincipalPayment": 19402.090212,
        "scheduledPrincipalPayment": 20762.037412
    }
    {
        "date": "2033-04-25",
        "totalCashFlow": 48515.452113,
        "interestPayment": 2463.465454,
        "principalBalance": 5866265.103647,
        "principalPayment": 46051.986659,
        "endPrincipalBalance": 5866265.103647,
        "beginPrincipalBalance": 5912317.090306,
        "prepayPrincipalPayment": 25336.303518,
        "scheduledPrincipalPayment": 20715.683141
    }
    {
        "date": "2033-05-25",
        "totalCashFlow": 48473.682364,
        "interestPayment": 2444.277127,
        "principalBalance": 5820235.698409,
        "principalPayment": 46029.405237,
        "endPrincipalBalance": 5820235.698409,
        "beginPrincipalBalance": 5866265.103647,
        "prepayPrincipalPayment": 25381.321995,
        "scheduledPrincipalPayment": 20648.083242
    }
    {
        "date": "2033-06-25",
        "totalCashFlow": 51274.994487,
        "interestPayment": 2425.098208,
        "principalBalance": 5771385.80213,
        "principalPayment": 48849.896279,
        "endPrincipalBalance": 5771385.80213,
        "beginPrincipalBalance": 5820235.698409,
        "prepayPrincipalPayment": 28270.050757,
        "scheduledPrincipalPayment": 20579.845522
    }
    {
        "date": "2033-07-25",
        "totalCashFlow": 53393.807386,
        "interestPayment": 2404.744084,
        "principalBalance": 5720396.738828,
        "principalPayment": 50989.063302,
        "endPrincipalBalance": 5720396.738828,
        "beginPrincipalBalance": 5771385.80213,
        "prepayPrincipalPayment": 30488.200074,
        "scheduledPrincipalPayment": 20500.863228
    }
    {
        "date": "2033-08-25",
        "totalCashFlow": 50044.947179,
        "interestPayment": 2383.498641,
        "principalBalance": 5672735.29029,
        "principalPayment": 47661.448537,
        "endPrincipalBalance": 5672735.29029,
        "beginPrincipalBalance": 5720396.738828,
        "prepayPrincipalPayment": 27248.028368,
        "scheduledPrincipalPayment": 20413.42017
    }
    {
        "date": "2033-09-25",
        "totalCashFlow": 52322.771495,
        "interestPayment": 2363.639704,
        "principalBalance": 5622776.1585,
        "principalPayment": 49959.13179,
        "endPrincipalBalance": 5622776.1585,
        "beginPrincipalBalance": 5672735.29029,
        "prepayPrincipalPayment": 29622.132989,
        "scheduledPrincipalPayment": 20336.998801
    }
    {
        "date": "2033-10-25",
        "totalCashFlow": 48624.882646,
        "interestPayment": 2342.823399,
        "principalBalance": 5576494.099253,
        "principalPayment": 46282.059247,
        "endPrincipalBalance": 5576494.099253,
        "beginPrincipalBalance": 5622776.1585,
        "prepayPrincipalPayment": 26030.565795,
        "scheduledPrincipalPayment": 20251.493452
    }
    {
        "date": "2033-11-25",
        "totalCashFlow": 46004.917503,
        "interestPayment": 2323.539208,
        "principalBalance": 5532812.720958,
        "principalPayment": 43681.378295,
        "endPrincipalBalance": 5532812.720958,
        "beginPrincipalBalance": 5576494.099253,
        "prepayPrincipalPayment": 23502.980459,
        "scheduledPrincipalPayment": 20178.397837
    }
    {
        "date": "2033-12-25",
        "totalCashFlow": 45448.295067,
        "interestPayment": 2305.338634,
        "principalBalance": 5489669.764525,
        "principalPayment": 43142.956434,
        "endPrincipalBalance": 5489669.764525,
        "beginPrincipalBalance": 5532812.720958,
        "prepayPrincipalPayment": 23028.982112,
        "scheduledPrincipalPayment": 20113.974321
    }
    {
        "date": "2034-01-25",
        "totalCashFlow": 45423.261299,
        "interestPayment": 2287.362402,
        "principalBalance": 5446533.865628,
        "principalPayment": 43135.898897,
        "endPrincipalBalance": 5446533.865628,
        "beginPrincipalBalance": 5489669.764525,
        "prepayPrincipalPayment": 23085.085016,
        "scheduledPrincipalPayment": 20050.81388
    }
    {
        "date": "2034-02-25",
        "totalCashFlow": 40169.498993,
        "interestPayment": 2269.389111,
        "principalBalance": 5408633.755745,
        "principalPayment": 37900.109882,
        "endPrincipalBalance": 5408633.755745,
        "beginPrincipalBalance": 5446533.865628,
        "prepayPrincipalPayment": 17913.124397,
        "scheduledPrincipalPayment": 19986.985486
    }
    {
        "date": "2034-03-25",
        "totalCashFlow": 40421.923998,
        "interestPayment": 2253.597398,
        "principalBalance": 5370465.429146,
        "principalPayment": 38168.3266,
        "endPrincipalBalance": 5370465.429146,
        "beginPrincipalBalance": 5408633.755745,
        "prepayPrincipalPayment": 18226.567446,
        "scheduledPrincipalPayment": 19941.759154
    }
    {
        "date": "2034-04-25",
        "totalCashFlow": 46206.719664,
        "interestPayment": 2237.693929,
        "principalBalance": 5326496.40341,
        "principalPayment": 43969.025735,
        "endPrincipalBalance": 5326496.40341,
        "beginPrincipalBalance": 5370465.429146,
        "prepayPrincipalPayment": 24074.014648,
        "scheduledPrincipalPayment": 19895.011087
    }
    {
        "date": "2034-05-25",
        "totalCashFlow": 45760.252187,
        "interestPayment": 2219.373501,
        "principalBalance": 5282955.524725,
        "principalPayment": 43540.878686,
        "endPrincipalBalance": 5282955.524725,
        "beginPrincipalBalance": 5326496.40341,
        "prepayPrincipalPayment": 23714.751215,
        "scheduledPrincipalPayment": 19826.127471
    }
    {
        "date": "2034-06-25",
        "totalCashFlow": 50332.994723,
        "interestPayment": 2201.231469,
        "principalBalance": 5234823.76147,
        "principalPayment": 48131.763254,
        "endPrincipalBalance": 5234823.76147,
        "beginPrincipalBalance": 5282955.524725,
        "prepayPrincipalPayment": 28373.67599,
        "scheduledPrincipalPayment": 19758.087264
    }
    {
        "date": "2034-07-25",
        "totalCashFlow": 51332.846587,
        "interestPayment": 2181.176567,
        "principalBalance": 5185672.091451,
        "principalPayment": 49151.670019,
        "endPrincipalBalance": 5185672.091451,
        "beginPrincipalBalance": 5234823.76147,
        "prepayPrincipalPayment": 29479.627384,
        "scheduledPrincipalPayment": 19672.042635
    }
    {
        "date": "2034-08-25",
        "totalCashFlow": 48172.995533,
        "interestPayment": 2160.696705,
        "principalBalance": 5139659.792623,
        "principalPayment": 46012.298828,
        "endPrincipalBalance": 5139659.792623,
        "beginPrincipalBalance": 5185672.091451,
        "prepayPrincipalPayment": 26431.080241,
        "scheduledPrincipalPayment": 19581.218586
    }
    {
        "date": "2034-09-25",
        "totalCashFlow": 50512.378913,
        "interestPayment": 2141.524914,
        "principalBalance": 5091288.938624,
        "principalPayment": 48370.853999,
        "endPrincipalBalance": 5091288.938624,
        "beginPrincipalBalance": 5139659.792623,
        "prepayPrincipalPayment": 28869.525333,
        "scheduledPrincipalPayment": 19501.328666
    }
    {
        "date": "2034-10-25",
        "totalCashFlow": 45886.661302,
        "interestPayment": 2121.370391,
        "principalBalance": 5047523.647713,
        "principalPayment": 43765.290911,
        "endPrincipalBalance": 5047523.647713,
        "beginPrincipalBalance": 5091288.938624,
        "prepayPrincipalPayment": 24353.719282,
        "scheduledPrincipalPayment": 19411.571629
    }
    {
        "date": "2034-11-25",
        "totalCashFlow": 45508.063297,
        "interestPayment": 2103.134853,
        "principalBalance": 5004118.71927,
        "principalPayment": 43404.928443,
        "endPrincipalBalance": 5004118.71927,
        "beginPrincipalBalance": 5047523.647713,
        "prepayPrincipalPayment": 24066.442391,
        "scheduledPrincipalPayment": 19338.486052
    }
    {
        "date": "2034-12-25",
        "totalCashFlow": 44044.429762,
        "interestPayment": 2085.049466,
        "principalBalance": 4962159.338974,
        "principalPayment": 41959.380296,
        "endPrincipalBalance": 4962159.338974,
        "beginPrincipalBalance": 5004118.71927,
        "prepayPrincipalPayment": 22693.406352,
        "scheduledPrincipalPayment": 19265.973943
    }
    {
        "date": "2035-01-25",
        "totalCashFlow": 43139.396973,
        "interestPayment": 2067.566391,
        "principalBalance": 4921087.508393,
        "principalPayment": 41071.830582,
        "endPrincipalBalance": 4921087.508393,
        "beginPrincipalBalance": 4962159.338974,
        "prepayPrincipalPayment": 21873.5871,
        "scheduledPrincipalPayment": 19198.243482
    }
    {
        "date": "2035-02-25",
        "totalCashFlow": 39745.068456,
        "interestPayment": 2050.453128,
        "principalBalance": 4883392.893065,
        "principalPayment": 37694.615328,
        "endPrincipalBalance": 4883392.893065,
        "beginPrincipalBalance": 4921087.508393,
        "prepayPrincipalPayment": 18561.418221,
        "scheduledPrincipalPayment": 19133.197106
    }
    {
        "date": "2035-03-25",
        "totalCashFlow": 39201.092786,
        "interestPayment": 2034.747039,
        "principalBalance": 4846226.547318,
        "principalPayment": 37166.345747,
        "endPrincipalBalance": 4846226.547318,
        "beginPrincipalBalance": 4883392.893065,
        "prepayPrincipalPayment": 18085.742202,
        "scheduledPrincipalPayment": 19080.603545
    }
    {
        "date": "2035-04-25",
        "totalCashFlow": 43504.756315,
        "interestPayment": 2019.261061,
        "principalBalance": 4804741.052064,
        "principalPayment": 41485.495254,
        "endPrincipalBalance": 4804741.052064,
        "beginPrincipalBalance": 4846226.547318,
        "prepayPrincipalPayment": 22456.032561,
        "scheduledPrincipalPayment": 19029.462693
    }
    {
        "date": "2035-05-25",
        "totalCashFlow": 45494.171031,
        "interestPayment": 2001.975438,
        "principalBalance": 4761248.856471,
        "principalPayment": 43492.195593,
        "endPrincipalBalance": 4761248.856471,
        "beginPrincipalBalance": 4804741.052064,
        "prepayPrincipalPayment": 24531.527469,
        "scheduledPrincipalPayment": 18960.668124
    }
    {
        "date": "2035-06-25",
        "totalCashFlow": 48908.546608,
        "interestPayment": 1983.85369,
        "principalBalance": 4714324.163553,
        "principalPayment": 46924.692918,
        "endPrincipalBalance": 4714324.163553,
        "beginPrincipalBalance": 4761248.856471,
        "prepayPrincipalPayment": 28041.566207,
        "scheduledPrincipalPayment": 18883.126711
    }
    {
        "date": "2035-07-25",
        "totalCashFlow": 48589.151469,
        "interestPayment": 1964.301735,
        "principalBalance": 4667699.313818,
        "principalPayment": 46624.849734,
        "endPrincipalBalance": 4667699.313818,
        "beginPrincipalBalance": 4714324.163553,
        "prepayPrincipalPayment": 27833.825167,
        "scheduledPrincipalPayment": 18791.024567
    }
    {
        "date": "2035-08-25",
        "totalCashFlow": 47871.346311,
        "interestPayment": 1944.874714,
        "principalBalance": 4621772.842221,
        "principalPayment": 45926.471597,
        "endPrincipalBalance": 4621772.842221,
        "beginPrincipalBalance": 4667699.313818,
        "prepayPrincipalPayment": 27227.377085,
        "scheduledPrincipalPayment": 18699.094512
    }
    {
        "date": "2035-09-25",
        "totalCashFlow": 48909.933618,
        "interestPayment": 1925.738684,
        "principalBalance": 4574788.647288,
        "principalPayment": 46984.194934,
        "endPrincipalBalance": 4574788.647288,
        "beginPrincipalBalance": 4621772.842221,
        "prepayPrincipalPayment": 28375.249562,
        "scheduledPrincipalPayment": 18608.945372
    }
    {
        "date": "2035-10-25",
        "totalCashFlow": 43238.673487,
        "interestPayment": 1906.161936,
        "principalBalance": 4533456.135738,
        "principalPayment": 41332.51155,
        "endPrincipalBalance": 4533456.135738,
        "beginPrincipalBalance": 4574788.647288,
        "prepayPrincipalPayment": 22819.012337,
        "scheduledPrincipalPayment": 18513.499213
    }
    {
        "date": "2035-11-25",
        "totalCashFlow": 44887.881143,
        "interestPayment": 1888.940057,
        "principalBalance": 4490457.194651,
        "principalPayment": 42998.941086,
        "endPrincipalBalance": 4490457.194651,
        "beginPrincipalBalance": 4533456.135738,
        "prepayPrincipalPayment": 24558.973987,
        "scheduledPrincipalPayment": 18439.9671
    }
    {
        "date": "2035-12-25",
        "totalCashFlow": 42422.032168,
        "interestPayment": 1871.023831,
        "principalBalance": 4449906.186315,
        "principalPayment": 40551.008336,
        "endPrincipalBalance": 4449906.186315,
        "beginPrincipalBalance": 4490457.194651,
        "prepayPrincipalPayment": 22192.239756,
        "scheduledPrincipalPayment": 18358.76858
    }
    {
        "date": "2036-01-25",
        "totalCashFlow": 41494.087045,
        "interestPayment": 1854.127578,
        "principalBalance": 4410266.226848,
        "principalPayment": 39639.959467,
        "endPrincipalBalance": 4410266.226848,
        "beginPrincipalBalance": 4449906.186315,
        "prepayPrincipalPayment": 21353.265205,
        "scheduledPrincipalPayment": 18286.694262
    }
    {
        "date": "2036-02-25",
        "totalCashFlow": 38149.395772,
        "interestPayment": 1837.610928,
        "principalBalance": 4373954.442003,
        "principalPayment": 36311.784845,
        "endPrincipalBalance": 4373954.442003,
        "beginPrincipalBalance": 4410266.226848,
        "prepayPrincipalPayment": 18094.246127,
        "scheduledPrincipalPayment": 18217.538717
    }
    {
        "date": "2036-03-25",
        "totalCashFlow": 38384.683659,
        "interestPayment": 1822.481018,
        "principalBalance": 4337392.239361,
        "principalPayment": 36562.202642,
        "endPrincipalBalance": 4337392.239361,
        "beginPrincipalBalance": 4373954.442003,
        "prepayPrincipalPayment": 18400.817636,
        "scheduledPrincipalPayment": 18161.385006
    }
    {
        "date": "2036-04-25",
        "totalCashFlow": 41292.061016,
        "interestPayment": 1807.246766,
        "principalBalance": 4297907.425111,
        "principalPayment": 39484.81425,
        "endPrincipalBalance": 4297907.425111,
        "beginPrincipalBalance": 4337392.239361,
        "prepayPrincipalPayment": 21381.312864,
        "scheduledPrincipalPayment": 18103.501386
    }
    {
        "date": "2036-05-25",
        "totalCashFlow": 44176.578091,
        "interestPayment": 1790.79476,
        "principalBalance": 4255521.641781,
        "principalPayment": 42385.783331,
        "endPrincipalBalance": 4255521.641781,
        "beginPrincipalBalance": 4297907.425111,
        "prepayPrincipalPayment": 24353.133307,
        "scheduledPrincipalPayment": 18032.650024
    }
    {
        "date": "2036-06-25",
        "totalCashFlow": 45813.436006,
        "interestPayment": 1773.134017,
        "principalBalance": 4211481.339792,
        "principalPayment": 44040.301988,
        "endPrincipalBalance": 4211481.339792,
        "beginPrincipalBalance": 4255521.641781,
        "prepayPrincipalPayment": 26091.583338,
        "scheduledPrincipalPayment": 17948.718651
    }
    {
        "date": "2036-07-25",
        "totalCashFlow": 46623.125747,
        "interestPayment": 1754.783892,
        "principalBalance": 4166612.997937,
        "principalPayment": 44868.341856,
        "endPrincipalBalance": 4166612.997937,
        "beginPrincipalBalance": 4211481.339792,
        "prepayPrincipalPayment": 27011.555589,
        "scheduledPrincipalPayment": 17856.786266
    }
    {
        "date": "2036-08-25",
        "totalCashFlow": 47046.438468,
        "interestPayment": 1736.088749,
        "principalBalance": 4121302.648218,
        "principalPayment": 45310.349719,
        "endPrincipalBalance": 4121302.648218,
        "beginPrincipalBalance": 4166612.997937,
        "prepayPrincipalPayment": 27550.099791,
        "scheduledPrincipalPayment": 17760.249928
    }
    {
        "date": "2036-09-25",
        "totalCashFlow": 44638.634461,
        "interestPayment": 1717.209437,
        "principalBalance": 4078381.223194,
        "principalPayment": 42921.425024,
        "endPrincipalBalance": 4078381.223194,
        "beginPrincipalBalance": 4121302.648218,
        "prepayPrincipalPayment": 25260.733097,
        "scheduledPrincipalPayment": 17660.691927
    }
    {
        "date": "2036-10-25",
        "totalCashFlow": 43416.473038,
        "interestPayment": 1699.32551,
        "principalBalance": 4036664.075666,
        "principalPayment": 41717.147528,
        "endPrincipalBalance": 4036664.075666,
        "beginPrincipalBalance": 4078381.223194,
        "prepayPrincipalPayment": 24146.885972,
        "scheduledPrincipalPayment": 17570.261556
    }
    {
        "date": "2036-11-25",
        "totalCashFlow": 42862.209214,
        "interestPayment": 1681.943365,
        "principalBalance": 3995483.809818,
        "principalPayment": 41180.265849,
        "endPrincipalBalance": 3995483.809818,
        "beginPrincipalBalance": 4036664.075666,
        "prepayPrincipalPayment": 23696.289186,
        "scheduledPrincipalPayment": 17483.976663
    }
    {
        "date": "2036-12-25",
        "totalCashFlow": 38562.926322,
        "interestPayment": 1664.784921,
        "principalBalance": 3958585.668416,
        "principalPayment": 36898.141401,
        "endPrincipalBalance": 3958585.668416,
        "beginPrincipalBalance": 3995483.809818,
        "prepayPrincipalPayment": 19499.141701,
        "scheduledPrincipalPayment": 17398.9997
    }
    {
        "date": "2037-01-25",
        "totalCashFlow": 41359.310644,
        "interestPayment": 1649.410695,
        "principalBalance": 3918875.768467,
        "principalPayment": 39709.899949,
        "endPrincipalBalance": 3918875.768467,
        "beginPrincipalBalance": 3958585.668416,
        "prepayPrincipalPayment": 22378.14877,
        "scheduledPrincipalPayment": 17331.751179
    }
    {
        "date": "2037-02-25",
        "totalCashFlow": 35575.964481,
        "interestPayment": 1632.864904,
        "principalBalance": 3884932.66889,
        "principalPayment": 33943.099577,
        "endPrincipalBalance": 3884932.66889,
        "beginPrincipalBalance": 3918875.768467,
        "prepayPrincipalPayment": 16691.805403,
        "scheduledPrincipalPayment": 17251.294174
    }
    {
        "date": "2037-03-25",
        "totalCashFlow": 35720.495005,
        "interestPayment": 1618.721945,
        "principalBalance": 3850830.89583,
        "principalPayment": 34101.77306,
        "endPrincipalBalance": 3850830.89583,
        "beginPrincipalBalance": 3884932.66889,
        "prepayPrincipalPayment": 16906.389603,
        "scheduledPrincipalPayment": 17195.383457
    }
    {
        "date": "2037-04-25",
        "totalCashFlow": 40078.356698,
        "interestPayment": 1604.512873,
        "principalBalance": 3812357.052006,
        "principalPayment": 38473.843825,
        "endPrincipalBalance": 3812357.052006,
        "beginPrincipalBalance": 3850830.89583,
        "prepayPrincipalPayment": 21335.790093,
        "scheduledPrincipalPayment": 17138.053731
    }
    {
        "date": "2037-05-25",
        "totalCashFlow": 42403.800039,
        "interestPayment": 1588.482105,
        "principalBalance": 3771541.734071,
        "principalPayment": 40815.317934,
        "endPrincipalBalance": 3771541.734071,
        "beginPrincipalBalance": 3812357.052006,
        "prepayPrincipalPayment": 23754.89045,
        "scheduledPrincipalPayment": 17060.427484
    }
    {
        "date": "2037-06-25",
        "totalCashFlow": 42338.453276,
        "interestPayment": 1571.475723,
        "principalBalance": 3730774.756518,
        "principalPayment": 40766.977554,
        "endPrincipalBalance": 3730774.756518,
        "beginPrincipalBalance": 3771541.734071,
        "prepayPrincipalPayment": 23795.671817,
        "scheduledPrincipalPayment": 16971.305737
    }
    {
        "date": "2037-07-25",
        "totalCashFlow": 45283.703686,
        "interestPayment": 1554.489482,
        "principalBalance": 3687045.542313,
        "principalPayment": 43729.214205,
        "endPrincipalBalance": 3687045.542313,
        "beginPrincipalBalance": 3730774.756518,
        "prepayPrincipalPayment": 26847.902606,
        "scheduledPrincipalPayment": 16881.311598
    }
    {
        "date": "2037-08-25",
        "totalCashFlow": 44447.858152,
        "interestPayment": 1536.268976,
        "principalBalance": 3644133.953137,
        "principalPayment": 42911.589176,
        "endPrincipalBalance": 3644133.953137,
        "beginPrincipalBalance": 3687045.542313,
        "prepayPrincipalPayment": 26134.855759,
        "scheduledPrincipalPayment": 16776.733417
    }
    {
        "date": "2037-09-25",
        "totalCashFlow": 42111.423508,
        "interestPayment": 1518.389147,
        "principalBalance": 3603540.918776,
        "principalPayment": 40593.034361,
        "endPrincipalBalance": 3603540.918776,
        "beginPrincipalBalance": 3644133.953137,
        "prepayPrincipalPayment": 23918.41158,
        "scheduledPrincipalPayment": 16674.622781
    }
    {
        "date": "2037-10-25",
        "totalCashFlow": 40906.377352,
        "interestPayment": 1501.475383,
        "principalBalance": 3564136.016807,
        "principalPayment": 39404.90197,
        "endPrincipalBalance": 3564136.016807,
        "beginPrincipalBalance": 3603540.918776,
        "prepayPrincipalPayment": 22822.97193,
        "scheduledPrincipalPayment": 16581.930039
    }
    {
        "date": "2037-11-25",
        "totalCashFlow": 39438.093966,
        "interestPayment": 1485.056674,
        "principalBalance": 3526182.979514,
        "principalPayment": 37953.037292,
        "endPrincipalBalance": 3526182.979514,
        "beginPrincipalBalance": 3564136.016807,
        "prepayPrincipalPayment": 21459.451212,
        "scheduledPrincipalPayment": 16493.58608
    }
    {
        "date": "2037-12-25",
        "totalCashFlow": 37147.180886,
        "interestPayment": 1469.242908,
        "principalBalance": 3490505.041537,
        "principalPayment": 35677.937977,
        "endPrincipalBalance": 3490505.041537,
        "beginPrincipalBalance": 3526182.979514,
        "prepayPrincipalPayment": 19267.043601,
        "scheduledPrincipalPayment": 16410.894377
    }
    {
        "date": "2038-01-25",
        "totalCashFlow": 38822.62776,
        "interestPayment": 1454.377101,
        "principalBalance": 3453136.790878,
        "principalPayment": 37368.250659,
        "endPrincipalBalance": 3453136.790878,
        "beginPrincipalBalance": 3490505.041537,
        "prepayPrincipalPayment": 21030.443748,
        "scheduledPrincipalPayment": 16337.806911
    }
    {
        "date": "2038-02-25",
        "totalCashFlow": 32717.32514,
        "interestPayment": 1438.806996,
        "principalBalance": 3421858.272734,
        "principalPayment": 31278.518144,
        "endPrincipalBalance": 3421858.272734,
        "beginPrincipalBalance": 3453136.790878,
        "prepayPrincipalPayment": 15022.694606,
        "scheduledPrincipalPayment": 16255.823537
    }
    {
        "date": "2038-03-25",
        "totalCashFlow": 33477.490054,
        "interestPayment": 1425.77428,
        "principalBalance": 3389806.55696,
        "principalPayment": 32051.715774,
        "endPrincipalBalance": 3389806.55696,
        "beginPrincipalBalance": 3421858.272734,
        "prepayPrincipalPayment": 15850.087722,
        "scheduledPrincipalPayment": 16201.628051
    }
    {
        "date": "2038-04-25",
        "totalCashFlow": 38290.254203,
        "interestPayment": 1412.419399,
        "principalBalance": 3352928.722157,
        "principalPayment": 36877.834804,
        "endPrincipalBalance": 3352928.722157,
        "beginPrincipalBalance": 3389806.55696,
        "prepayPrincipalPayment": 20734.811748,
        "scheduledPrincipalPayment": 16143.023056
    }
    {
        "date": "2038-05-25",
        "totalCashFlow": 39148.214228,
        "interestPayment": 1397.053634,
        "principalBalance": 3315177.561562,
        "principalPayment": 37751.160594,
        "endPrincipalBalance": 3315177.561562,
        "beginPrincipalBalance": 3352928.722157,
        "prepayPrincipalPayment": 21690.641578,
        "scheduledPrincipalPayment": 16060.519016
    }
    {
        "date": "2038-06-25",
        "totalCashFlow": 39498.250421,
        "interestPayment": 1381.323984,
        "principalBalance": 3277060.635126,
        "principalPayment": 38116.926437,
        "endPrincipalBalance": 3277060.635126,
        "beginPrincipalBalance": 3315177.561562,
        "prepayPrincipalPayment": 22144.18464,
        "scheduledPrincipalPayment": 15972.741797
    }
    {
        "date": "2038-07-25",
        "totalCashFlow": 42177.990018,
        "interestPayment": 1365.441931,
        "principalBalance": 3236248.087039,
        "principalPayment": 40812.548087,
        "endPrincipalBalance": 3236248.087039,
        "beginPrincipalBalance": 3277060.635126,
        "prepayPrincipalPayment": 24930.488358,
        "scheduledPrincipalPayment": 15882.059729
    }
    {
        "date": "2038-08-25",
        "totalCashFlow": 40347.094552,
        "interestPayment": 1348.436703,
        "principalBalance": 3197249.429189,
        "principalPayment": 38998.65785,
        "endPrincipalBalance": 3197249.429189,
        "beginPrincipalBalance": 3236248.087039,
        "prepayPrincipalPayment": 23221.593176,
        "scheduledPrincipalPayment": 15777.064674
    }
    {
        "date": "2038-09-25",
        "totalCashFlow": 40120.079604,
        "interestPayment": 1332.187262,
        "principalBalance": 3158461.536847,
        "principalPayment": 38787.892342,
        "endPrincipalBalance": 3158461.536847,
        "beginPrincipalBalance": 3197249.429189,
        "prepayPrincipalPayment": 23108.274148,
        "scheduledPrincipalPayment": 15679.618194
    }
    {
        "date": "2038-10-25",
        "totalCashFlow": 38007.218907,
        "interestPayment": 1316.02564,
        "principalBalance": 3121770.34358,
        "principalPayment": 36691.193267,
        "endPrincipalBalance": 3121770.34358,
        "beginPrincipalBalance": 3158461.536847,
        "prepayPrincipalPayment": 21109.244458,
        "scheduledPrincipalPayment": 15581.948809
    }
    {
        "date": "2038-11-25",
        "totalCashFlow": 35806.784569,
        "interestPayment": 1300.737643,
        "principalBalance": 3087264.296654,
        "principalPayment": 34506.046926,
        "endPrincipalBalance": 3087264.296654,
        "beginPrincipalBalance": 3121770.34358,
        "prepayPrincipalPayment": 19012.632562,
        "scheduledPrincipalPayment": 15493.414364
    }
    {
        "date": "2038-12-25",
        "totalCashFlow": 35322.998238,
        "interestPayment": 1286.360124,
        "principalBalance": 3053227.65854,
        "principalPayment": 34036.638114,
        "endPrincipalBalance": 3053227.65854,
        "beginPrincipalBalance": 3087264.296654,
        "prepayPrincipalPayment": 18622.014316,
        "scheduledPrincipalPayment": 15414.623798
    }
    {
        "date": "2039-01-25",
        "totalCashFlow": 35234.244405,
        "interestPayment": 1272.178191,
        "principalBalance": 3019265.592326,
        "principalPayment": 33962.066214,
        "endPrincipalBalance": 3019265.592326,
        "beginPrincipalBalance": 3053227.65854,
        "prepayPrincipalPayment": 18624.928621,
        "scheduledPrincipalPayment": 15337.137593
    }
    {
        "date": "2039-02-25",
        "totalCashFlow": 30995.909484,
        "interestPayment": 1258.02733,
        "principalBalance": 2989527.710172,
        "principalPayment": 29737.882154,
        "endPrincipalBalance": 2989527.710172,
        "beginPrincipalBalance": 3019265.592326,
        "prepayPrincipalPayment": 14478.896406,
        "scheduledPrincipalPayment": 15258.985748
    }
    {
        "date": "2039-03-25",
        "totalCashFlow": 31086.305586,
        "interestPayment": 1245.636546,
        "principalBalance": 2959687.041132,
        "principalPayment": 29840.66904,
        "endPrincipalBalance": 2959687.041132,
        "beginPrincipalBalance": 2989527.710172,
        "prepayPrincipalPayment": 14639.411326,
        "scheduledPrincipalPayment": 15201.257713
    }
    {
        "date": "2039-04-25",
        "totalCashFlow": 35494.72212,
        "interestPayment": 1233.202934,
        "principalBalance": 2925425.521946,
        "principalPayment": 34261.519186,
        "endPrincipalBalance": 2925425.521946,
        "beginPrincipalBalance": 2959687.041132,
        "prepayPrincipalPayment": 19119.324215,
        "scheduledPrincipalPayment": 15142.194971
    }
    {
        "date": "2039-05-25",
        "totalCashFlow": 35455.350917,
        "interestPayment": 1218.927301,
        "principalBalance": 2891189.09833,
        "principalPayment": 34236.423616,
        "endPrincipalBalance": 2891189.09833,
        "beginPrincipalBalance": 2925425.521946,
        "prepayPrincipalPayment": 19176.878243,
        "scheduledPrincipalPayment": 15059.545373
    }
    {
        "date": "2039-06-25",
        "totalCashFlow": 37522.588371,
        "interestPayment": 1204.662124,
        "principalBalance": 2854871.172083,
        "principalPayment": 36317.926247,
        "endPrincipalBalance": 2854871.172083,
        "beginPrincipalBalance": 2891189.09833,
        "prepayPrincipalPayment": 21342.027023,
        "scheduledPrincipalPayment": 14975.899224
    }
    {
        "date": "2039-07-25",
        "totalCashFlow": 39041.755323,
        "interestPayment": 1189.529655,
        "principalBalance": 2817018.946416,
        "principalPayment": 37852.225668,
        "endPrincipalBalance": 2817018.946416,
        "beginPrincipalBalance": 2854871.172083,
        "prepayPrincipalPayment": 22971.966209,
        "scheduledPrincipalPayment": 14880.259458
    }
    {
        "date": "2039-08-25",
        "totalCashFlow": 36428.737886,
        "interestPayment": 1173.757894,
        "principalBalance": 2781763.966424,
        "principalPayment": 35254.979992,
        "endPrincipalBalance": 2781763.966424,
        "beginPrincipalBalance": 2817018.946416,
        "prepayPrincipalPayment": 20479.708286,
        "scheduledPrincipalPayment": 14775.271706
    }
    {
        "date": "2039-09-25",
        "totalCashFlow": 37999.621104,
        "interestPayment": 1159.068319,
        "principalBalance": 2744923.41364,
        "principalPayment": 36840.552784,
        "endPrincipalBalance": 2744923.41364,
        "beginPrincipalBalance": 2781763.966424,
        "prepayPrincipalPayment": 22157.985143,
        "scheduledPrincipalPayment": 14682.567641
    }
    {
        "date": "2039-10-25",
        "totalCashFlow": 35158.153429,
        "interestPayment": 1143.718089,
        "principalBalance": 2710908.9783,
        "principalPayment": 34014.43534,
        "endPrincipalBalance": 2710908.9783,
        "beginPrincipalBalance": 2744923.41364,
        "prepayPrincipalPayment": 19434.269573,
        "scheduledPrincipalPayment": 14580.165767
    }
    {
        "date": "2039-11-25",
        "totalCashFlow": 33120.324203,
        "interestPayment": 1129.545408,
        "principalBalance": 2678918.199504,
        "principalPayment": 31990.778796,
        "endPrincipalBalance": 2678918.199504,
        "beginPrincipalBalance": 2710908.9783,
        "prepayPrincipalPayment": 17499.313405,
        "scheduledPrincipalPayment": 14491.465391
    }
    {
        "date": "2039-12-25",
        "totalCashFlow": 32651.980194,
        "interestPayment": 1116.215916,
        "principalBalance": 2647382.435227,
        "principalPayment": 31535.764277,
        "endPrincipalBalance": 2647382.435227,
        "beginPrincipalBalance": 2678918.199504,
        "prepayPrincipalPayment": 17123.348842,
        "scheduledPrincipalPayment": 14412.415435
    }
    {
        "date": "2040-01-25",
        "totalCashFlow": 32540.011347,
        "interestPayment": 1103.076015,
        "principalBalance": 2615945.499895,
        "principalPayment": 31436.935332,
        "endPrincipalBalance": 2615945.499895,
        "beginPrincipalBalance": 2647382.435227,
        "prepayPrincipalPayment": 17102.224304,
        "scheduledPrincipalPayment": 14334.711028
    }
    {
        "date": "2040-02-25",
        "totalCashFlow": 28669.223791,
        "interestPayment": 1089.977292,
        "principalBalance": 2588366.253395,
        "principalPayment": 27579.246499,
        "endPrincipalBalance": 2588366.253395,
        "beginPrincipalBalance": 2615945.499895,
        "prepayPrincipalPayment": 13322.807569,
        "scheduledPrincipalPayment": 14256.43893
    }
    {
        "date": "2040-03-25",
        "totalCashFlow": 29300.751601,
        "interestPayment": 1078.485939,
        "principalBalance": 2560143.987733,
        "principalPayment": 28222.265662,
        "endPrincipalBalance": 2560143.987733,
        "beginPrincipalBalance": 2588366.253395,
        "prepayPrincipalPayment": 14024.057123,
        "scheduledPrincipalPayment": 14198.208539
    }
    {
        "date": "2040-04-25",
        "totalCashFlow": 31673.377644,
        "interestPayment": 1066.726662,
        "principalBalance": 2529537.33675,
        "principalPayment": 30606.650983,
        "endPrincipalBalance": 2529537.33675,
        "beginPrincipalBalance": 2560143.987733,
        "prepayPrincipalPayment": 16471.085001,
        "scheduledPrincipalPayment": 14135.565982
    }
    {
        "date": "2040-05-25",
        "totalCashFlow": 32976.775631,
        "interestPayment": 1053.97389,
        "principalBalance": 2497614.535009,
        "principalPayment": 31922.801741,
        "endPrincipalBalance": 2497614.535009,
        "beginPrincipalBalance": 2529537.33675,
        "prepayPrincipalPayment": 17864.054757,
        "scheduledPrincipalPayment": 14058.746985
    }
    {
        "date": "2040-06-25",
        "totalCashFlow": 35245.215293,
        "interestPayment": 1040.672723,
        "principalBalance": 2463409.992438,
        "principalPayment": 34204.542571,
        "endPrincipalBalance": 2463409.992438,
        "beginPrincipalBalance": 2497614.535009,
        "prepayPrincipalPayment": 20231.095394,
        "scheduledPrincipalPayment": 13973.447177
    }
    {
        "date": "2040-07-25",
        "totalCashFlow": 34853.279737,
        "interestPayment": 1026.42083,
        "principalBalance": 2429583.133532,
        "principalPayment": 33826.858906,
        "endPrincipalBalance": 2429583.133532,
        "beginPrincipalBalance": 2463409.992438,
        "prepayPrincipalPayment": 19952.798694,
        "scheduledPrincipalPayment": 13874.060212
    }
    {
        "date": "2040-08-25",
        "totalCashFlow": 34173.735193,
        "interestPayment": 1012.326306,
        "principalBalance": 2396421.724645,
        "principalPayment": 33161.408887,
        "endPrincipalBalance": 2396421.724645,
        "beginPrincipalBalance": 2429583.133532,
        "prepayPrincipalPayment": 19386.025995,
        "scheduledPrincipalPayment": 13775.382892
    }
    {
        "date": "2040-09-25",
        "totalCashFlow": 34696.540724,
        "interestPayment": 998.509052,
        "principalBalance": 2362723.692973,
        "principalPayment": 33698.031672,
        "endPrincipalBalance": 2362723.692973,
        "beginPrincipalBalance": 2396421.724645,
        "prepayPrincipalPayment": 20018.957279,
        "scheduledPrincipalPayment": 13679.074393
    }
    {
        "date": "2040-10-25",
        "totalCashFlow": 30652.865458,
        "interestPayment": 984.468205,
        "principalBalance": 2333055.29572,
        "principalPayment": 29668.397253,
        "endPrincipalBalance": 2333055.29572,
        "beginPrincipalBalance": 2362723.692973,
        "prepayPrincipalPayment": 16090.120263,
        "scheduledPrincipalPayment": 13578.27699
    }
    {
        "date": "2040-11-25",
        "totalCashFlow": 31599.983925,
        "interestPayment": 972.106373,
        "principalBalance": 2302427.418169,
        "principalPayment": 30627.877552,
        "endPrincipalBalance": 2302427.418169,
        "beginPrincipalBalance": 2333055.29572,
        "prepayPrincipalPayment": 17128.555779,
        "scheduledPrincipalPayment": 13499.321773
    }
    {
        "date": "2040-12-25",
        "totalCashFlow": 29807.356776,
        "interestPayment": 959.344758,
        "principalBalance": 2273579.40615,
        "principalPayment": 28848.012018,
        "endPrincipalBalance": 2273579.40615,
        "beginPrincipalBalance": 2302427.418169,
        "prepayPrincipalPayment": 15434.416837,
        "scheduledPrincipalPayment": 13413.595182
    }
    {
        "date": "2041-01-25",
        "totalCashFlow": 29047.110879,
        "interestPayment": 947.324753,
        "principalBalance": 2245479.620024,
        "principalPayment": 28099.786126,
        "endPrincipalBalance": 2245479.620024,
        "beginPrincipalBalance": 2273579.40615,
        "prepayPrincipalPayment": 14762.758172,
        "scheduledPrincipalPayment": 13337.027954
    }
    {
        "date": "2041-02-25",
        "totalCashFlow": 26694.115306,
        "interestPayment": 935.616508,
        "principalBalance": 2219721.121227,
        "principalPayment": 25758.498797,
        "endPrincipalBalance": 2219721.121227,
        "beginPrincipalBalance": 2245479.620024,
        "prepayPrincipalPayment": 12494.779556,
        "scheduledPrincipalPayment": 13263.719241
    }
    {
        "date": "2041-03-25",
        "totalCashFlow": 26230.426942,
        "interestPayment": 924.883801,
        "principalBalance": 2194415.578085,
        "principalPayment": 25305.543142,
        "endPrincipalBalance": 2194415.578085,
        "beginPrincipalBalance": 2219721.121227,
        "prepayPrincipalPayment": 12102.328241,
        "scheduledPrincipalPayment": 13203.214901
    }
    {
        "date": "2041-04-25",
        "totalCashFlow": 28522.25707,
        "interestPayment": 914.339824,
        "principalBalance": 2166807.660839,
        "principalPayment": 27607.917246,
        "endPrincipalBalance": 2166807.660839,
        "beginPrincipalBalance": 2194415.578085,
        "prepayPrincipalPayment": 14463.441536,
        "scheduledPrincipalPayment": 13144.475709
    }
    {
        "date": "2041-05-25",
        "totalCashFlow": 30262.986846,
        "interestPayment": 902.836525,
        "principalBalance": 2137447.510518,
        "principalPayment": 29360.150321,
        "endPrincipalBalance": 2137447.510518,
        "beginPrincipalBalance": 2166807.660839,
        "prepayPrincipalPayment": 16289.230839,
        "scheduledPrincipalPayment": 13070.919482
    }
    {
        "date": "2041-06-25",
        "totalCashFlow": 31890.059799,
        "interestPayment": 890.603129,
        "principalBalance": 2106448.053849,
        "principalPayment": 30999.456669,
        "endPrincipalBalance": 2106448.053849,
        "beginPrincipalBalance": 2137447.510518,
        "prepayPrincipalPayment": 18013.883143,
        "scheduledPrincipalPayment": 12985.573526
    }
    {
        "date": "2041-07-25",
        "totalCashFlow": 30739.232909,
        "interestPayment": 877.686689,
        "principalBalance": 2076586.507629,
        "principalPayment": 29861.54622,
        "endPrincipalBalance": 2076586.507629,
        "beginPrincipalBalance": 2106448.053849,
        "prepayPrincipalPayment": 16972.668915,
        "scheduledPrincipalPayment": 12888.877305
    }
    {
        "date": "2041-08-25",
        "totalCashFlow": 31601.630989,
        "interestPayment": 865.244378,
        "principalBalance": 2045850.121019,
        "principalPayment": 30736.38661,
        "endPrincipalBalance": 2045850.121019,
        "beginPrincipalBalance": 2076586.507629,
        "prepayPrincipalPayment": 17938.683502,
        "scheduledPrincipalPayment": 12797.703109
    }
    {
        "date": "2041-09-25",
        "totalCashFlow": 30600.343416,
        "interestPayment": 852.43755,
        "principalBalance": 2016102.215153,
        "principalPayment": 29747.905866,
        "endPrincipalBalance": 2016102.215153,
        "beginPrincipalBalance": 2045850.121019,
        "prepayPrincipalPayment": 17048.22676,
        "scheduledPrincipalPayment": 12699.679106
    }
    {
        "date": "2041-10-25",
        "totalCashFlow": 28358.960629,
        "interestPayment": 840.04259,
        "principalBalance": 1988583.297113,
        "principalPayment": 27518.918039,
        "endPrincipalBalance": 1988583.297113,
        "beginPrincipalBalance": 2016102.215153,
        "prepayPrincipalPayment": 14912.609462,
        "scheduledPrincipalPayment": 12606.308578
    }
    {
        "date": "2041-11-25",
        "totalCashFlow": 28500.193183,
        "interestPayment": 828.576374,
        "principalBalance": 1960911.680304,
        "principalPayment": 27671.616809,
        "endPrincipalBalance": 1960911.680304,
        "beginPrincipalBalance": 1988583.297113,
        "prepayPrincipalPayment": 15146.106866,
        "scheduledPrincipalPayment": 12525.509943
    }
    {
        "date": "2041-12-25",
        "totalCashFlow": 26328.717555,
        "interestPayment": 817.046533,
        "principalBalance": 1935400.009283,
        "principalPayment": 25511.671022,
        "endPrincipalBalance": 1935400.009283,
        "beginPrincipalBalance": 1960911.680304,
        "prepayPrincipalPayment": 13069.219328,
        "scheduledPrincipalPayment": 12442.451694
    }
    {
        "date": "2042-01-25",
        "totalCashFlow": 26749.67803,
        "interestPayment": 806.416671,
        "principalBalance": 1909456.747923,
        "principalPayment": 25943.26136,
        "endPrincipalBalance": 1909456.747923,
        "beginPrincipalBalance": 1935400.009283,
        "prepayPrincipalPayment": 13571.392576,
        "scheduledPrincipalPayment": 12371.868783
    }
    {
        "date": "2042-02-25",
        "totalCashFlow": 24128.589665,
        "interestPayment": 795.606978,
        "principalBalance": 1886123.765237,
        "principalPayment": 23332.982687,
        "endPrincipalBalance": 1886123.765237,
        "beginPrincipalBalance": 1909456.747923,
        "prepayPrincipalPayment": 11035.629519,
        "scheduledPrincipalPayment": 12297.353168
    }
    {
        "date": "2042-03-25",
        "totalCashFlow": 23698.694394,
        "interestPayment": 785.884902,
        "principalBalance": 1863210.955745,
        "principalPayment": 22912.809492,
        "endPrincipalBalance": 1863210.955745,
        "beginPrincipalBalance": 1886123.765237,
        "prepayPrincipalPayment": 10674.253847,
        "scheduledPrincipalPayment": 12238.555645
    }
    {
        "date": "2042-04-25",
        "totalCashFlow": 25641.939086,
        "interestPayment": 776.337898,
        "principalBalance": 1838345.354557,
        "principalPayment": 24865.601188,
        "endPrincipalBalance": 1838345.354557,
        "beginPrincipalBalance": 1863210.955745,
        "prepayPrincipalPayment": 12684.084423,
        "scheduledPrincipalPayment": 12181.516765
    }
    {
        "date": "2042-05-25",
        "totalCashFlow": 27384.60479,
        "interestPayment": 765.977231,
        "principalBalance": 1811726.726997,
        "principalPayment": 26618.627559,
        "endPrincipalBalance": 1811726.726997,
        "beginPrincipalBalance": 1838345.354557,
        "prepayPrincipalPayment": 14507.981885,
        "scheduledPrincipalPayment": 12110.645674
    }
    {
        "date": "2042-06-25",
        "totalCashFlow": 27831.947209,
        "interestPayment": 754.886136,
        "principalBalance": 1784649.665924,
        "principalPayment": 27077.061073,
        "endPrincipalBalance": 1784649.665924,
        "beginPrincipalBalance": 1811726.726997,
        "prepayPrincipalPayment": 15050.109806,
        "scheduledPrincipalPayment": 12026.951267
    }
    {
        "date": "2042-07-25",
        "totalCashFlow": 28089.176216,
        "interestPayment": 743.604027,
        "principalBalance": 1757304.093736,
        "principalPayment": 27345.572188,
        "endPrincipalBalance": 1757304.093736,
        "beginPrincipalBalance": 1784649.665924,
        "prepayPrincipalPayment": 15406.773799,
        "scheduledPrincipalPayment": 11938.798389
    }
    {
        "date": "2042-08-25",
        "totalCashFlow": 28118.072886,
        "interestPayment": 732.210039,
        "principalBalance": 1729918.230889,
        "principalPayment": 27385.862847,
        "endPrincipalBalance": 1729918.230889,
        "beginPrincipalBalance": 1757304.093736,
        "prepayPrincipalPayment": 15538.497358,
        "scheduledPrincipalPayment": 11847.365489
    }
    {
        "date": "2042-09-25",
        "totalCashFlow": 26642.384021,
        "interestPayment": 720.799263,
        "principalBalance": 1703996.64613,
        "principalPayment": 25921.584759,
        "endPrincipalBalance": 1703996.64613,
        "beginPrincipalBalance": 1729918.230889,
        "prepayPrincipalPayment": 14167.456371,
        "scheduledPrincipalPayment": 11754.128387
    }
    {
        "date": "2042-10-25",
        "totalCashFlow": 25828.118412,
        "interestPayment": 709.998603,
        "principalBalance": 1678878.526321,
        "principalPayment": 25118.119809,
        "endPrincipalBalance": 1678878.526321,
        "beginPrincipalBalance": 1703996.64613,
        "prepayPrincipalPayment": 13448.76945,
        "scheduledPrincipalPayment": 11669.350359
    }
    {
        "date": "2042-11-25",
        "totalCashFlow": 25364.218768,
        "interestPayment": 699.532719,
        "principalBalance": 1654213.840272,
        "principalPayment": 24664.686049,
        "endPrincipalBalance": 1654213.840272,
        "beginPrincipalBalance": 1678878.526321,
        "prepayPrincipalPayment": 13076.01197,
        "scheduledPrincipalPayment": 11588.674079
    }
    {
        "date": "2042-12-25",
        "totalCashFlow": 23016.771369,
        "interestPayment": 689.255767,
        "principalBalance": 1631886.32467,
        "principalPayment": 22327.515602,
        "endPrincipalBalance": 1631886.32467,
        "beginPrincipalBalance": 1654213.840272,
        "prepayPrincipalPayment": 10817.750862,
        "scheduledPrincipalPayment": 11509.76474
    }
    {
        "date": "2043-01-25",
        "totalCashFlow": 24294.593816,
        "interestPayment": 679.952635,
        "principalBalance": 1608271.683489,
        "principalPayment": 23614.641181,
        "endPrincipalBalance": 1608271.683489,
        "beginPrincipalBalance": 1631886.32467,
        "prepayPrincipalPayment": 12168.761672,
        "scheduledPrincipalPayment": 11445.879508
    }
    {
        "date": "2043-02-25",
        "totalCashFlow": 21243.058587,
        "interestPayment": 670.113201,
        "principalBalance": 1587698.738104,
        "principalPayment": 20572.945385,
        "endPrincipalBalance": 1587698.738104,
        "beginPrincipalBalance": 1608271.683489,
        "prepayPrincipalPayment": 9201.185905,
        "scheduledPrincipalPayment": 11371.75948
    }
    {
        "date": "2043-03-25",
        "totalCashFlow": 21213.235941,
        "interestPayment": 661.541141,
        "principalBalance": 1567147.043304,
        "principalPayment": 20551.6948,
        "endPrincipalBalance": 1567147.043304,
        "beginPrincipalBalance": 1587698.738104,
        "prepayPrincipalPayment": 9233.680991,
        "scheduledPrincipalPayment": 11318.01381
    }
    {
        "date": "2043-04-25",
        "totalCashFlow": 23037.704831,
        "interestPayment": 652.977935,
        "principalBalance": 1544762.316408,
        "principalPayment": 22384.726896,
        "endPrincipalBalance": 1544762.316408,
        "beginPrincipalBalance": 1567147.043304,
        "prepayPrincipalPayment": 11121.288034,
        "scheduledPrincipalPayment": 11263.438862
    }
    {
        "date": "2043-05-25",
        "totalCashFlow": 24262.216297,
        "interestPayment": 643.650965,
        "principalBalance": 1521143.751075,
        "principalPayment": 23618.565332,
        "endPrincipalBalance": 1521143.751075,
        "beginPrincipalBalance": 1544762.316408,
        "prepayPrincipalPayment": 12423.987431,
        "scheduledPrincipalPayment": 11194.577901
    }
    {
        "date": "2043-06-25",
        "totalCashFlow": 24092.466587,
        "interestPayment": 633.809896,
        "principalBalance": 1497685.094385,
        "principalPayment": 23458.656691,
        "endPrincipalBalance": 1497685.094385,
        "beginPrincipalBalance": 1521143.751075,
        "prepayPrincipalPayment": 12343.203569,
        "scheduledPrincipalPayment": 11115.453122
    }
    {
        "date": "2043-07-25",
        "totalCashFlow": 25362.612024,
        "interestPayment": 624.035456,
        "principalBalance": 1472946.517816,
        "principalPayment": 24738.576568,
        "endPrincipalBalance": 1472946.517816,
        "beginPrincipalBalance": 1497685.094385,
        "prepayPrincipalPayment": 13702.498919,
        "scheduledPrincipalPayment": 11036.07765
    }
    {
        "date": "2043-08-25",
        "totalCashFlow": 24800.934493,
        "interestPayment": 613.727716,
        "principalBalance": 1448759.311039,
        "principalPayment": 24187.206778,
        "endPrincipalBalance": 1448759.311039,
        "beginPrincipalBalance": 1472946.517816,
        "prepayPrincipalPayment": 13241.459107,
        "scheduledPrincipalPayment": 10945.74767
    }
    {
        "date": "2043-09-25",
        "totalCashFlow": 23539.936393,
        "interestPayment": 603.649713,
        "principalBalance": 1425823.024359,
        "principalPayment": 22936.28668,
        "endPrincipalBalance": 1425823.024359,
        "beginPrincipalBalance": 1448759.311039,
        "prepayPrincipalPayment": 12078.376977,
        "scheduledPrincipalPayment": 10857.909703
    }
    {
        "date": "2043-10-25",
        "totalCashFlow": 22834.751052,
        "interestPayment": 594.092927,
        "principalBalance": 1403582.366233,
        "principalPayment": 22240.658125,
        "endPrincipalBalance": 1403582.366233,
        "beginPrincipalBalance": 1425823.024359,
        "prepayPrincipalPayment": 11462.739588,
        "scheduledPrincipalPayment": 10777.918538
    }
    {
        "date": "2043-11-25",
        "totalCashFlow": 22014.674447,
        "interestPayment": 584.825986,
        "principalBalance": 1382152.517772,
        "principalPayment": 21429.848461,
        "endPrincipalBalance": 1382152.517772,
        "beginPrincipalBalance": 1403582.366233,
        "prepayPrincipalPayment": 10728.101669,
        "scheduledPrincipalPayment": 10701.746792
    }
    {
        "date": "2043-12-25",
        "totalCashFlow": 20849.106797,
        "interestPayment": 575.896882,
        "principalBalance": 1361879.307858,
        "principalPayment": 20273.209915,
        "endPrincipalBalance": 1361879.307858,
        "beginPrincipalBalance": 1382152.517772,
        "prepayPrincipalPayment": 9642.827222,
        "scheduledPrincipalPayment": 10630.382692
    }
    {
        "date": "2044-01-25",
        "totalCashFlow": 21485.270557,
        "interestPayment": 567.449712,
        "principalBalance": 1340961.487012,
        "principalPayment": 20917.820846,
        "endPrincipalBalance": 1340961.487012,
        "beginPrincipalBalance": 1361879.307858,
        "prepayPrincipalPayment": 10351.18224,
        "scheduledPrincipalPayment": 10566.638606
    }
    {
        "date": "2044-02-25",
        "totalCashFlow": 18631.462605,
        "interestPayment": 558.733953,
        "principalBalance": 1322888.75836,
        "principalPayment": 18072.728652,
        "endPrincipalBalance": 1322888.75836,
        "beginPrincipalBalance": 1340961.487012,
        "prepayPrincipalPayment": 7576.108891,
        "scheduledPrincipalPayment": 10496.619761
    }
    {
        "date": "2044-03-25",
        "totalCashFlow": 19195.17038,
        "interestPayment": 551.203649,
        "principalBalance": 1304244.791629,
        "principalPayment": 18643.966731,
        "endPrincipalBalance": 1304244.791629,
        "beginPrincipalBalance": 1322888.75836,
        "prepayPrincipalPayment": 8196.246492,
        "scheduledPrincipalPayment": 10447.720239
    }
    {
        "date": "2044-04-25",
        "totalCashFlow": 20891.915378,
        "interestPayment": 543.43533,
        "principalBalance": 1283896.311581,
        "principalPayment": 20348.480048,
        "endPrincipalBalance": 1283896.311581,
        "beginPrincipalBalance": 1304244.791629,
        "prepayPrincipalPayment": 9955.191161,
        "scheduledPrincipalPayment": 10393.288887
    }
    {
        "date": "2044-05-25",
        "totalCashFlow": 20761.679367,
        "interestPayment": 534.956796,
        "principalBalance": 1263669.58901,
        "principalPayment": 20226.722571,
        "endPrincipalBalance": 1263669.58901,
        "beginPrincipalBalance": 1283896.311581,
        "prepayPrincipalPayment": 9902.658997,
        "scheduledPrincipalPayment": 10324.063573
    }
    {
        "date": "2044-06-25",
        "totalCashFlow": 21603.247267,
        "interestPayment": 526.528995,
        "principalBalance": 1242592.870738,
        "principalPayment": 21076.718272,
        "endPrincipalBalance": 1242592.870738,
        "beginPrincipalBalance": 1263669.58901,
        "prepayPrincipalPayment": 10822.258825,
        "scheduledPrincipalPayment": 10254.459447
    }
    {
        "date": "2044-07-25",
        "totalCashFlow": 22164.271843,
        "interestPayment": 517.747029,
        "principalBalance": 1220946.345924,
        "principalPayment": 21646.524813,
        "endPrincipalBalance": 1220946.345924,
        "beginPrincipalBalance": 1242592.870738,
        "prepayPrincipalPayment": 11470.015099,
        "scheduledPrincipalPayment": 10176.509714
    }
    {
        "date": "2044-08-25",
        "totalCashFlow": 20836.297577,
        "interestPayment": 508.727644,
        "principalBalance": 1200618.775991,
        "principalPayment": 20327.569933,
        "endPrincipalBalance": 1200618.775991,
        "beginPrincipalBalance": 1220946.345924,
        "prepayPrincipalPayment": 10235.270429,
        "scheduledPrincipalPayment": 10092.299504
    }
    {
        "date": "2044-09-25",
        "totalCashFlow": 21406.665695,
        "interestPayment": 500.257823,
        "principalBalance": 1179712.36812,
        "principalPayment": 20906.407872,
        "endPrincipalBalance": 1179712.36812,
        "beginPrincipalBalance": 1200618.775991,
        "prepayPrincipalPayment": 10888.99397,
        "scheduledPrincipalPayment": 10017.413901
    }
    {
        "date": "2044-10-25",
        "totalCashFlow": 20015.87817,
        "interestPayment": 491.54682,
        "principalBalance": 1160188.03677,
        "principalPayment": 19524.33135,
        "endPrincipalBalance": 1160188.03677,
        "beginPrincipalBalance": 1179712.36812,
        "prepayPrincipalPayment": 9588.195275,
        "scheduledPrincipalPayment": 9936.136076
    }
    {
        "date": "2044-11-25",
        "totalCashFlow": 19008.014853,
        "interestPayment": 483.411682,
        "principalBalance": 1141663.433598,
        "principalPayment": 18524.603172,
        "endPrincipalBalance": 1141663.433598,
        "beginPrincipalBalance": 1160188.03677,
        "prepayPrincipalPayment": 8659.644386,
        "scheduledPrincipalPayment": 9864.958785
    }
    {
        "date": "2044-12-25",
        "totalCashFlow": 18699.211652,
        "interestPayment": 475.693097,
        "principalBalance": 1123439.915043,
        "principalPayment": 18223.518555,
        "endPrincipalBalance": 1123439.915043,
        "beginPrincipalBalance": 1141663.433598,
        "prepayPrincipalPayment": 8422.624643,
        "scheduledPrincipalPayment": 9800.893912
    }
    {
        "date": "2045-01-25",
        "totalCashFlow": 18545.876452,
        "interestPayment": 468.099965,
        "principalBalance": 1105362.138556,
        "principalPayment": 18077.776487,
        "endPrincipalBalance": 1105362.138556,
        "beginPrincipalBalance": 1123439.915043,
        "prepayPrincipalPayment": 8339.681505,
        "scheduledPrincipalPayment": 9738.094982
    }
    {
        "date": "2045-02-25",
        "totalCashFlow": 16821.160917,
        "interestPayment": 460.567558,
        "principalBalance": 1089001.545197,
        "principalPayment": 16360.593359,
        "endPrincipalBalance": 1089001.545197,
        "beginPrincipalBalance": 1105362.138556,
        "prepayPrincipalPayment": 6685.351811,
        "scheduledPrincipalPayment": 9675.241548
    }
    {
        "date": "2045-03-25",
        "totalCashFlow": 16767.408374,
        "interestPayment": 453.750644,
        "principalBalance": 1072687.887467,
        "principalPayment": 16313.65773,
        "endPrincipalBalance": 1072687.887467,
        "beginPrincipalBalance": 1089001.545197,
        "prepayPrincipalPayment": 6687.432945,
        "scheduledPrincipalPayment": 9626.224784
    }
    {
        "date": "2045-04-25",
        "totalCashFlow": 18298.457014,
        "interestPayment": 446.953286,
        "principalBalance": 1054836.38374,
        "principalPayment": 17851.503728,
        "endPrincipalBalance": 1054836.38374,
        "beginPrincipalBalance": 1072687.887467,
        "prepayPrincipalPayment": 8274.954482,
        "scheduledPrincipalPayment": 9576.549245
    }
    {
        "date": "2045-05-25",
        "totalCashFlow": 18016.637642,
        "interestPayment": 439.51516,
        "principalBalance": 1037259.261257,
        "principalPayment": 17577.122482,
        "endPrincipalBalance": 1037259.261257,
        "beginPrincipalBalance": 1054836.38374,
        "prepayPrincipalPayment": 8065.216431,
        "scheduledPrincipalPayment": 9511.906051
    }
    {
        "date": "2045-06-25",
        "totalCashFlow": 19113.353486,
        "interestPayment": 432.191359,
        "principalBalance": 1018578.099131,
        "principalPayment": 18681.162127,
        "endPrincipalBalance": 1018578.099131,
        "beginPrincipalBalance": 1037259.261257,
        "prepayPrincipalPayment": 9232.813539,
        "scheduledPrincipalPayment": 9448.348588
    }
    {
        "date": "2045-07-25",
        "totalCashFlow": 19177.955611,
        "interestPayment": 424.407541,
        "principalBalance": 999824.551061,
        "principalPayment": 18753.54807,
        "endPrincipalBalance": 999824.551061,
        "beginPrincipalBalance": 1018578.099131,
        "prepayPrincipalPayment": 9380.320269,
        "scheduledPrincipalPayment": 9373.227801
    }
    {
        "date": "2045-08-25",
        "totalCashFlow": 18123.697815,
        "interestPayment": 416.593563,
        "principalBalance": 982117.446809,
        "principalPayment": 17707.104252,
        "endPrincipalBalance": 982117.446809,
        "beginPrincipalBalance": 999824.551061,
        "prepayPrincipalPayment": 8411.325357,
        "scheduledPrincipalPayment": 9295.778895
    }
    {
        "date": "2045-09-25",
        "totalCashFlow": 18529.828873,
        "interestPayment": 409.215603,
        "principalBalance": 963996.833538,
        "principalPayment": 18120.61327,
        "endPrincipalBalance": 963996.833538,
        "beginPrincipalBalance": 982117.446809,
        "prepayPrincipalPayment": 8894.170954,
        "scheduledPrincipalPayment": 9226.442317
    }
    {
        "date": "2045-10-25",
        "totalCashFlow": 17155.701943,
        "interestPayment": 401.665347,
        "principalBalance": 947242.796943,
        "principalPayment": 16754.036595,
        "endPrincipalBalance": 947242.796943,
        "beginPrincipalBalance": 963996.833538,
        "prepayPrincipalPayment": 7602.419413,
        "scheduledPrincipalPayment": 9151.617182
    }
    {
        "date": "2045-11-25",
        "totalCashFlow": 16884.418079,
        "interestPayment": 394.684499,
        "principalBalance": 930753.063363,
        "principalPayment": 16489.73358,
        "endPrincipalBalance": 930753.063363,
        "beginPrincipalBalance": 947242.796943,
        "prepayPrincipalPayment": 7401.523982,
        "scheduledPrincipalPayment": 9088.209598
    }
    {
        "date": "2045-12-25",
        "totalCashFlow": 16370.861387,
        "interestPayment": 387.813776,
        "principalBalance": 914770.015752,
        "principalPayment": 15983.047611,
        "endPrincipalBalance": 914770.015752,
        "beginPrincipalBalance": 930753.063363,
        "prepayPrincipalPayment": 6957.146794,
        "scheduledPrincipalPayment": 9025.900817
    }
    {
        "date": "2046-01-25",
        "totalCashFlow": 16001.698453,
        "interestPayment": 381.154173,
        "principalBalance": 899149.471472,
        "principalPayment": 15620.54428,
        "endPrincipalBalance": 899149.471472,
        "beginPrincipalBalance": 914770.015752,
        "prepayPrincipalPayment": 6653.43946,
        "scheduledPrincipalPayment": 8967.10482
    }
    {
        "date": "2046-02-25",
        "totalCashFlow": 15067.747578,
        "interestPayment": 374.645613,
        "principalBalance": 884456.369507,
        "principalPayment": 14693.101965,
        "endPrincipalBalance": 884456.369507,
        "beginPrincipalBalance": 899149.471472,
        "prepayPrincipalPayment": 5782.591546,
        "scheduledPrincipalPayment": 8910.510419
    }
    {
        "date": "2046-03-25",
        "totalCashFlow": 14828.012695,
        "interestPayment": 368.523487,
        "principalBalance": 869996.880299,
        "principalPayment": 14459.489207,
        "endPrincipalBalance": 869996.880299,
        "beginPrincipalBalance": 884456.369507,
        "prepayPrincipalPayment": 5597.635961,
        "scheduledPrincipalPayment": 8861.853246
    }
    {
        "date": "2046-04-25",
        "totalCashFlow": 15660.641531,
        "interestPayment": 362.4987,
        "principalBalance": 854698.737468,
        "principalPayment": 15298.142831,
        "endPrincipalBalance": 854698.737468,
        "beginPrincipalBalance": 869996.880299,
        "prepayPrincipalPayment": 6483.770927,
        "scheduledPrincipalPayment": 8814.371904
    }
    {
        "date": "2046-05-25",
        "totalCashFlow": 15953.773943,
        "interestPayment": 356.124474,
        "principalBalance": 839101.087999,
        "principalPayment": 15597.649469,
        "endPrincipalBalance": 839101.087999,
        "beginPrincipalBalance": 854698.737468,
        "prepayPrincipalPayment": 6840.527723,
        "scheduledPrincipalPayment": 8757.121746
    }
    {
        "date": "2046-06-25",
        "totalCashFlow": 16522.470479,
        "interestPayment": 349.625453,
        "principalBalance": 822928.242973,
        "principalPayment": 16172.845026,
        "endPrincipalBalance": 822928.242973,
        "beginPrincipalBalance": 839101.087999,
        "prepayPrincipalPayment": 7477.487651,
        "scheduledPrincipalPayment": 8695.357375
    }
    {
        "date": "2046-07-25",
        "totalCashFlow": 16280.456863,
        "interestPayment": 342.886768,
        "principalBalance": 806990.672878,
        "principalPayment": 15937.570095,
        "endPrincipalBalance": 806990.672878,
        "beginPrincipalBalance": 822928.242973,
        "prepayPrincipalPayment": 7311.535002,
        "scheduledPrincipalPayment": 8626.035093
    }
    {
        "date": "2046-08-25",
        "totalCashFlow": 15959.211649,
        "interestPayment": 336.246114,
        "principalBalance": 791367.707343,
        "principalPayment": 15622.965535,
        "endPrincipalBalance": 791367.707343,
        "beginPrincipalBalance": 806990.672878,
        "prepayPrincipalPayment": 7065.477942,
        "scheduledPrincipalPayment": 8557.487593
    }
    {
        "date": "2046-09-25",
        "totalCashFlow": 15991.408499,
        "interestPayment": 329.736545,
        "principalBalance": 775706.03539,
        "principalPayment": 15661.671954,
        "endPrincipalBalance": 775706.03539,
        "beginPrincipalBalance": 791367.707343,
        "prepayPrincipalPayment": 7171.07593,
        "scheduledPrincipalPayment": 8490.596023
    }
    {
        "date": "2046-10-25",
        "totalCashFlow": 14721.816392,
        "interestPayment": 323.210848,
        "principalBalance": 761307.429846,
        "principalPayment": 14398.605543,
        "endPrincipalBalance": 761307.429846,
        "beginPrincipalBalance": 775706.03539,
        "prepayPrincipalPayment": 5977.019172,
        "scheduledPrincipalPayment": 8421.586372
    }
    {
        "date": "2046-11-25",
        "totalCashFlow": 14889.680614,
        "interestPayment": 317.211429,
        "principalBalance": 746734.960661,
        "principalPayment": 14572.469185,
        "endPrincipalBalance": 746734.960661,
        "beginPrincipalBalance": 761307.429846,
        "prepayPrincipalPayment": 6207.781431,
        "scheduledPrincipalPayment": 8364.687754
    }
    {
        "date": "2046-12-25",
        "totalCashFlow": 14287.999165,
        "interestPayment": 311.139567,
        "principalBalance": 732758.101063,
        "principalPayment": 13976.859598,
        "endPrincipalBalance": 732758.101063,
        "beginPrincipalBalance": 746734.960661,
        "prepayPrincipalPayment": 5672.494745,
        "scheduledPrincipalPayment": 8304.364853
    }
    {
        "date": "2047-01-25",
        "totalCashFlow": 13986.274264,
        "interestPayment": 305.315875,
        "principalBalance": 719077.142674,
        "principalPayment": 13680.958389,
        "endPrincipalBalance": 719077.142674,
        "beginPrincipalBalance": 732758.101063,
        "prepayPrincipalPayment": 5431.802285,
        "scheduledPrincipalPayment": 8249.156104
    }
    {
        "date": "2047-02-25",
        "totalCashFlow": 13265.549462,
        "interestPayment": 299.615476,
        "principalBalance": 706111.208689,
        "principalPayment": 12965.933985,
        "endPrincipalBalance": 706111.208689,
        "beginPrincipalBalance": 719077.142674,
        "prepayPrincipalPayment": 4770.095164,
        "scheduledPrincipalPayment": 8195.838822
    }
    {
        "date": "2047-03-25",
        "totalCashFlow": 13061.897349,
        "interestPayment": 294.213004,
        "principalBalance": 693343.524344,
        "principalPayment": 12767.684345,
        "endPrincipalBalance": 693343.524344,
        "beginPrincipalBalance": 706111.208689,
        "prepayPrincipalPayment": 4618.360498,
        "scheduledPrincipalPayment": 8149.323848
    }
    {
        "date": "2047-04-25",
        "totalCashFlow": 13580.261658,
        "interestPayment": 288.893135,
        "principalBalance": 680052.155821,
        "principalPayment": 13291.368523,
        "endPrincipalBalance": 680052.155821,
        "beginPrincipalBalance": 693343.524344,
        "prepayPrincipalPayment": 5187.53542,
        "scheduledPrincipalPayment": 8103.833103
    }
    {
        "date": "2047-05-25",
        "totalCashFlow": 13930.006926,
        "interestPayment": 283.355065,
        "principalBalance": 666405.503959,
        "principalPayment": 13646.651862,
        "endPrincipalBalance": 666405.503959,
        "beginPrincipalBalance": 680052.155821,
        "prepayPrincipalPayment": 5595.790392,
        "scheduledPrincipalPayment": 8050.861469
    }
    {
        "date": "2047-06-25",
        "totalCashFlow": 14234.757656,
        "interestPayment": 277.66896,
        "principalBalance": 652448.415263,
        "principalPayment": 13957.088696,
        "endPrincipalBalance": 652448.415263,
        "beginPrincipalBalance": 666405.503959,
        "prepayPrincipalPayment": 5964.950696,
        "scheduledPrincipalPayment": 7992.138
    }
    {
        "date": "2047-07-25",
        "totalCashFlow": 13834.144428,
        "interestPayment": 271.853506,
        "principalBalance": 638886.124341,
        "principalPayment": 13562.290922,
        "endPrincipalBalance": 638886.124341,
        "beginPrincipalBalance": 652448.415263,
        "prepayPrincipalPayment": 5634.30864,
        "scheduledPrincipalPayment": 7927.982282
    }
    {
        "date": "2047-08-25",
        "totalCashFlow": 13938.701532,
        "interestPayment": 266.202552,
        "principalBalance": 625213.625361,
        "principalPayment": 13672.49898,
        "endPrincipalBalance": 625213.625361,
        "beginPrincipalBalance": 638886.124341,
        "prepayPrincipalPayment": 5805.635903,
        "scheduledPrincipalPayment": 7866.863077
    }
    {
        "date": "2047-09-25",
        "totalCashFlow": 13587.014725,
        "interestPayment": 260.505677,
        "principalBalance": 611887.116314,
        "principalPayment": 13326.509047,
        "endPrincipalBalance": 611887.116314,
        "beginPrincipalBalance": 625213.625361,
        "prepayPrincipalPayment": 5523.905081,
        "scheduledPrincipalPayment": 7802.603966
    }
    {
        "date": "2047-10-25",
        "totalCashFlow": 12945.202713,
        "interestPayment": 254.952965,
        "principalBalance": 599196.866566,
        "principalPayment": 12690.249747,
        "endPrincipalBalance": 599196.866566,
        "beginPrincipalBalance": 611887.116314,
        "prepayPrincipalPayment": 4949.399782,
        "scheduledPrincipalPayment": 7740.849965
    }
    {
        "date": "2047-11-25",
        "totalCashFlow": 12886.48445,
        "interestPayment": 249.665361,
        "principalBalance": 586560.047478,
        "principalPayment": 12636.819089,
        "endPrincipalBalance": 586560.047478,
        "beginPrincipalBalance": 599196.866566,
        "prepayPrincipalPayment": 4951.387832,
        "scheduledPrincipalPayment": 7685.431256
    }
    {
        "date": "2047-12-25",
        "totalCashFlow": 12284.212075,
        "interestPayment": 244.40002,
        "principalBalance": 574520.235423,
        "principalPayment": 12039.812055,
        "endPrincipalBalance": 574520.235423,
        "beginPrincipalBalance": 586560.047478,
        "prepayPrincipalPayment": 4410.774893,
        "scheduledPrincipalPayment": 7629.037162
    }
    {
        "date": "2048-01-25",
        "totalCashFlow": 12297.081322,
        "interestPayment": 239.383431,
        "principalBalance": 562462.537533,
        "principalPayment": 12057.69789,
        "endPrincipalBalance": 562462.537533,
        "beginPrincipalBalance": 574520.235423,
        "prepayPrincipalPayment": 4478.898671,
        "scheduledPrincipalPayment": 7578.799219
    }
    {
        "date": "2048-02-25",
        "totalCashFlow": 11620.187837,
        "interestPayment": 234.359391,
        "principalBalance": 551076.709086,
        "principalPayment": 11385.828447,
        "endPrincipalBalance": 551076.709086,
        "beginPrincipalBalance": 562462.537533,
        "prepayPrincipalPayment": 3859.070347,
        "scheduledPrincipalPayment": 7526.7581
    }
    {
        "date": "2048-03-25",
        "totalCashFlow": 11445.644324,
        "interestPayment": 229.615295,
        "principalBalance": 539860.680057,
        "principalPayment": 11216.029028,
        "endPrincipalBalance": 539860.680057,
        "beginPrincipalBalance": 551076.709086,
        "prepayPrincipalPayment": 3733.826791,
        "scheduledPrincipalPayment": 7482.202238
    }
    {
        "date": "2048-04-25",
        "totalCashFlow": 11903.932825,
        "interestPayment": 224.94195,
        "principalBalance": 528181.689182,
        "principalPayment": 11678.990875,
        "endPrincipalBalance": 528181.689182,
        "beginPrincipalBalance": 539860.680057,
        "prepayPrincipalPayment": 4240.441754,
        "scheduledPrincipalPayment": 7438.549122
    }
    {
        "date": "2048-05-25",
        "totalCashFlow": 12073.691443,
        "interestPayment": 220.075704,
        "principalBalance": 516328.073444,
        "principalPayment": 11853.615739,
        "endPrincipalBalance": 516328.073444,
        "beginPrincipalBalance": 528181.689182,
        "prepayPrincipalPayment": 4466.623686,
        "scheduledPrincipalPayment": 7386.992053
    }
    {
        "date": "2048-06-25",
        "totalCashFlow": 11935.406733,
        "interestPayment": 215.136697,
        "principalBalance": 504607.803408,
        "principalPayment": 11720.270036,
        "endPrincipalBalance": 504607.803408,
        "beginPrincipalBalance": 516328.073444,
        "prepayPrincipalPayment": 4389.004129,
        "scheduledPrincipalPayment": 7331.265907
    }
    {
        "date": "2048-07-25",
        "totalCashFlow": 12156.913928,
        "interestPayment": 210.253251,
        "principalBalance": 492661.142731,
        "principalPayment": 11946.660677,
        "endPrincipalBalance": 492661.142731,
        "beginPrincipalBalance": 504607.803408,
        "prepayPrincipalPayment": 4671.040305,
        "scheduledPrincipalPayment": 7275.620372
    }
    {
        "date": "2048-08-25",
        "totalCashFlow": 11919.68659,
        "interestPayment": 205.275476,
        "principalBalance": 480946.731617,
        "principalPayment": 11714.411114,
        "endPrincipalBalance": 480946.731617,
        "beginPrincipalBalance": 492661.142731,
        "prepayPrincipalPayment": 4499.61719,
        "scheduledPrincipalPayment": 7214.793924
    }
    {
        "date": "2048-09-25",
        "totalCashFlow": 11519.395973,
        "interestPayment": 200.394472,
        "principalBalance": 469627.730115,
        "principalPayment": 11319.001502,
        "endPrincipalBalance": 469627.730115,
        "beginPrincipalBalance": 480946.731617,
        "prepayPrincipalPayment": 4163.635976,
        "scheduledPrincipalPayment": 7155.365526
    }
    {
        "date": "2048-10-25",
        "totalCashFlow": 11259.693829,
        "interestPayment": 195.678221,
        "principalBalance": 458563.714508,
        "principalPayment": 11064.015608,
        "endPrincipalBalance": 458563.714508,
        "beginPrincipalBalance": 469627.730115,
        "prepayPrincipalPayment": 3964.142786,
        "scheduledPrincipalPayment": 7099.872822
    }
    {
        "date": "2048-11-25",
        "totalCashFlow": 10981.412751,
        "interestPayment": 191.068214,
        "principalBalance": 447773.369971,
        "principalPayment": 10790.344536,
        "endPrincipalBalance": 447773.369971,
        "beginPrincipalBalance": 458563.714508,
        "prepayPrincipalPayment": 3743.989593,
        "scheduledPrincipalPayment": 7046.354943
    }
    {
        "date": "2048-12-25",
        "totalCashFlow": 10623.3386,
        "interestPayment": 186.572237,
        "principalBalance": 437336.603609,
        "principalPayment": 10436.766363,
        "endPrincipalBalance": 437336.603609,
        "beginPrincipalBalance": 447773.369971,
        "prepayPrincipalPayment": 3441.560824,
        "scheduledPrincipalPayment": 6995.205539
    }
    {
        "date": "2049-01-25",
        "totalCashFlow": 10691.971208,
        "interestPayment": 182.223585,
        "principalBalance": 426826.855986,
        "principalPayment": 10509.747623,
        "endPrincipalBalance": 426826.855986,
        "beginPrincipalBalance": 437336.603609,
        "prepayPrincipalPayment": 3561.930314,
        "scheduledPrincipalPayment": 6947.817309
    }
    {
        "date": "2049-02-25",
        "totalCashFlow": 9965.941668,
        "interestPayment": 177.844523,
        "principalBalance": 417038.758841,
        "principalPayment": 9788.097145,
        "endPrincipalBalance": 417038.758841,
        "beginPrincipalBalance": 426826.855986,
        "prepayPrincipalPayment": 2890.603086,
        "scheduledPrincipalPayment": 6897.494058
    }
    {
        "date": "2049-03-25",
        "totalCashFlow": 9992.56066,
        "interestPayment": 173.76615,
        "principalBalance": 407219.964331,
        "principalPayment": 9818.79451,
        "endPrincipalBalance": 407219.964331,
        "beginPrincipalBalance": 417038.758841,
        "prepayPrincipalPayment": 2961.644237,
        "scheduledPrincipalPayment": 6857.150273
    }
    {
        "date": "2049-04-25",
        "totalCashFlow": 10399.66706,
        "interestPayment": 169.674985,
        "principalBalance": 396989.972256,
        "principalPayment": 10229.992075,
        "endPrincipalBalance": 396989.972256,
        "beginPrincipalBalance": 407219.964331,
        "prepayPrincipalPayment": 3415.26136,
        "scheduledPrincipalPayment": 6814.730715
    }
    {
        "date": "2049-05-25",
        "totalCashFlow": 10400.116912,
        "interestPayment": 165.412488,
        "principalBalance": 386755.267832,
        "principalPayment": 10234.704423,
        "endPrincipalBalance": 386755.267832,
        "beginPrincipalBalance": 396989.972256,
        "prepayPrincipalPayment": 3471.061908,
        "scheduledPrincipalPayment": 6763.642515
    }
    {
        "date": "2049-06-25",
        "totalCashFlow": 10347.594303,
        "interestPayment": 161.148028,
        "principalBalance": 376568.821558,
        "principalPayment": 10186.446275,
        "endPrincipalBalance": 376568.821558,
        "beginPrincipalBalance": 386755.267832,
        "prepayPrincipalPayment": 3475.983546,
        "scheduledPrincipalPayment": 6710.462729
    }
    {
        "date": "2049-07-25",
        "totalCashFlow": 10497.26152,
        "interestPayment": 156.903676,
        "principalBalance": 366228.463713,
        "principalPayment": 10340.357844,
        "endPrincipalBalance": 366228.463713,
        "beginPrincipalBalance": 376568.821558,
        "prepayPrincipalPayment": 3684.34453,
        "scheduledPrincipalPayment": 6656.013314
    }
    {
        "date": "2049-08-25",
        "totalCashFlow": 10240.831754,
        "interestPayment": 152.595193,
        "principalBalance": 356140.227153,
        "principalPayment": 10088.236561,
        "endPrincipalBalance": 356140.227153,
        "beginPrincipalBalance": 366228.463713,
        "prepayPrincipalPayment": 3491.653082,
        "scheduledPrincipalPayment": 6596.583479
    }
    {
        "date": "2049-09-25",
        "totalCashFlow": 10127.883387,
        "interestPayment": 148.391761,
        "principalBalance": 346160.735528,
        "principalPayment": 9979.491625,
        "endPrincipalBalance": 346160.735528,
        "beginPrincipalBalance": 356140.227153,
        "prepayPrincipalPayment": 3440.149413,
        "scheduledPrincipalPayment": 6539.342212
    }
    {
        "date": "2049-10-25",
        "totalCashFlow": 9858.05354,
        "interestPayment": 144.23364,
        "principalBalance": 336446.915627,
        "principalPayment": 9713.8199,
        "endPrincipalBalance": 336446.915627,
        "beginPrincipalBalance": 346160.735528,
        "prepayPrincipalPayment": 3232.081465,
        "scheduledPrincipalPayment": 6481.738435
    }
    {
        "date": "2049-11-25",
        "totalCashFlow": 9592.434902,
        "interestPayment": 140.186215,
        "principalBalance": 326994.66694,
        "principalPayment": 9452.248687,
        "endPrincipalBalance": 326994.66694,
        "beginPrincipalBalance": 336446.915627,
        "prepayPrincipalPayment": 3025.49711,
        "scheduledPrincipalPayment": 6426.751577
    }
    {
        "date": "2049-12-25",
        "totalCashFlow": 9466.694509,
        "interestPayment": 136.247778,
        "principalBalance": 317664.220209,
        "principalPayment": 9330.446731,
        "endPrincipalBalance": 317664.220209,
        "beginPrincipalBalance": 326994.66694,
        "prepayPrincipalPayment": 2955.979964,
        "scheduledPrincipalPayment": 6374.466767
    }
    {
        "date": "2050-01-25",
        "totalCashFlow": 9373.392436,
        "interestPayment": 132.360092,
        "principalBalance": 308423.187865,
        "principalPayment": 9241.032344,
        "endPrincipalBalance": 308423.187865,
        "beginPrincipalBalance": 317664.220209,
        "prepayPrincipalPayment": 2918.756561,
        "scheduledPrincipalPayment": 6322.275783
    }
    {
        "date": "2050-02-25",
        "totalCashFlow": 8975.826765,
        "interestPayment": 128.509662,
        "principalBalance": 299575.870762,
        "principalPayment": 8847.317104,
        "endPrincipalBalance": 299575.870762,
        "beginPrincipalBalance": 308423.187865,
        "prepayPrincipalPayment": 2577.787185,
        "scheduledPrincipalPayment": 6269.529918
    }
    {
        "date": "2050-03-25",
        "totalCashFlow": 8903.352274,
        "interestPayment": 124.823279,
        "principalBalance": 290797.341767,
        "principalPayment": 8778.528995,
        "endPrincipalBalance": 290797.341767,
        "beginPrincipalBalance": 299575.870762,
        "prepayPrincipalPayment": 2556.011764,
        "scheduledPrincipalPayment": 6222.51723
    }
    {
        "date": "2050-04-25",
        "totalCashFlow": 9125.356904,
        "interestPayment": 121.165559,
        "principalBalance": 281793.150422,
        "principalPayment": 9004.191345,
        "endPrincipalBalance": 281793.150422,
        "beginPrincipalBalance": 290797.341767,
        "prepayPrincipalPayment": 2829.466104,
        "scheduledPrincipalPayment": 6174.725241
    }
    {
        "date": "2050-05-25",
        "totalCashFlow": 9019.035493,
        "interestPayment": 117.413813,
        "principalBalance": 272891.528742,
        "principalPayment": 8901.62168,
        "endPrincipalBalance": 272891.528742,
        "beginPrincipalBalance": 281793.150422,
        "prepayPrincipalPayment": 2781.912027,
        "scheduledPrincipalPayment": 6119.709653
    }
    {
        "date": "2050-06-25",
        "totalCashFlow": 9048.643734,
        "interestPayment": 113.704804,
        "principalBalance": 263956.589812,
        "principalPayment": 8934.93893,
        "endPrincipalBalance": 263956.589812,
        "beginPrincipalBalance": 272891.528742,
        "prepayPrincipalPayment": 2870.674927,
        "scheduledPrincipalPayment": 6064.264004
    }
    {
        "date": "2050-07-25",
        "totalCashFlow": 9031.436385,
        "interestPayment": 109.981912,
        "principalBalance": 255035.135339,
        "principalPayment": 8921.454473,
        "endPrincipalBalance": 255035.135339,
        "beginPrincipalBalance": 263956.589812,
        "prepayPrincipalPayment": 2916.184186,
        "scheduledPrincipalPayment": 6005.270286
    }
    {
        "date": "2050-08-25",
        "totalCashFlow": 8757.002068,
        "interestPayment": 106.26464,
        "principalBalance": 246384.397911,
        "principalPayment": 8650.737428,
        "endPrincipalBalance": 246384.397911,
        "beginPrincipalBalance": 255035.135339,
        "prepayPrincipalPayment": 2707.172988,
        "scheduledPrincipalPayment": 5943.56444
    }
    {
        "date": "2050-09-25",
        "totalCashFlow": 8739.883941,
        "interestPayment": 102.660166,
        "principalBalance": 237747.174136,
        "principalPayment": 8637.223775,
        "endPrincipalBalance": 237747.174136,
        "beginPrincipalBalance": 246384.397911,
        "prepayPrincipalPayment": 2752.13116,
        "scheduledPrincipalPayment": 5885.092614
    }
    {
        "date": "2050-10-25",
        "totalCashFlow": 8462.178098,
        "interestPayment": 99.061323,
        "principalBalance": 229384.057361,
        "principalPayment": 8363.116775,
        "endPrincipalBalance": 229384.057361,
        "beginPrincipalBalance": 237747.174136,
        "prepayPrincipalPayment": 2539.309511,
        "scheduledPrincipalPayment": 5823.807264
    }
    {
        "date": "2050-11-25",
        "totalCashFlow": 8242.740458,
        "interestPayment": 95.576691,
        "principalBalance": 221236.893594,
        "principalPayment": 8147.163767,
        "endPrincipalBalance": 221236.893594,
        "beginPrincipalBalance": 229384.057361,
        "prepayPrincipalPayment": 2381.120836,
        "scheduledPrincipalPayment": 5766.042931
    }
    {
        "date": "2050-12-25",
        "totalCashFlow": 8111.768492,
        "interestPayment": 92.182039,
        "principalBalance": 213217.307141,
        "principalPayment": 8019.586453,
        "endPrincipalBalance": 213217.307141,
        "beginPrincipalBalance": 221236.893594,
        "prepayPrincipalPayment": 2308.998942,
        "scheduledPrincipalPayment": 5710.587511
    }
    {
        "date": "2051-01-25",
        "totalCashFlow": 8001.616146,
        "interestPayment": 88.840545,
        "principalBalance": 205304.531539,
        "principalPayment": 7912.775601,
        "endPrincipalBalance": 205304.531539,
        "beginPrincipalBalance": 213217.307141,
        "prepayPrincipalPayment": 2257.482553,
        "scheduledPrincipalPayment": 5655.293048
    }
    {
        "date": "2051-02-25",
        "totalCashFlow": 7705.948004,
        "interestPayment": 85.543555,
        "principalBalance": 197684.12709,
        "principalPayment": 7620.404449,
        "endPrincipalBalance": 197684.12709,
        "beginPrincipalBalance": 205304.531539,
        "prepayPrincipalPayment": 2020.792546,
        "scheduledPrincipalPayment": 5599.611903
    }
    {
        "date": "2051-03-25",
        "totalCashFlow": 7610.910405,
        "interestPayment": 82.368386,
        "principalBalance": 190155.585072,
        "principalPayment": 7528.542018,
        "endPrincipalBalance": 190155.585072,
        "beginPrincipalBalance": 197684.12709,
        "prepayPrincipalPayment": 1979.818078,
        "scheduledPrincipalPayment": 5548.72394
    }
    {
        "date": "2051-04-25",
        "totalCashFlow": 7676.696209,
        "interestPayment": 79.231494,
        "principalBalance": 182558.120357,
        "principalPayment": 7597.464716,
        "endPrincipalBalance": 182558.120357,
        "beginPrincipalBalance": 190155.585072,
        "prepayPrincipalPayment": 2100.196049,
        "scheduledPrincipalPayment": 5497.268666
    }
    {
        "date": "2051-05-25",
        "totalCashFlow": 7556.033163,
        "interestPayment": 76.065883,
        "principalBalance": 175078.153077,
        "principalPayment": 7479.967279,
        "endPrincipalBalance": 175078.153077,
        "beginPrincipalBalance": 182558.120357,
        "prepayPrincipalPayment": 2039.560148,
        "scheduledPrincipalPayment": 5440.407131
    }
    {
        "date": "2051-06-25",
        "totalCashFlow": 7567.658055,
        "interestPayment": 72.94923,
        "principalBalance": 167583.444253,
        "principalPayment": 7494.708825,
        "endPrincipalBalance": 167583.444253,
        "beginPrincipalBalance": 175078.153077,
        "prepayPrincipalPayment": 2111.347675,
        "scheduledPrincipalPayment": 5383.361149
    }
    {
        "date": "2051-07-25",
        "totalCashFlow": 7461.953249,
        "interestPayment": 69.826435,
        "principalBalance": 160191.317439,
        "principalPayment": 7392.126814,
        "endPrincipalBalance": 160191.317439,
        "beginPrincipalBalance": 167583.444253,
        "prepayPrincipalPayment": 2070.207708,
        "scheduledPrincipalPayment": 5321.919106
    }
    {
        "date": "2051-08-25",
        "totalCashFlow": 7243.463543,
        "interestPayment": 66.746382,
        "principalBalance": 153014.600279,
        "principalPayment": 7176.717161,
        "endPrincipalBalance": 153014.600279,
        "beginPrincipalBalance": 160191.317439,
        "prepayPrincipalPayment": 1917.224627,
        "scheduledPrincipalPayment": 5259.492534
    }
    {
        "date": "2051-09-25",
        "totalCashFlow": 7191.649624,
        "interestPayment": 63.756083,
        "principalBalance": 145886.706738,
        "principalPayment": 7127.89354,
        "endPrincipalBalance": 145886.706738,
        "beginPrincipalBalance": 153014.600279,
        "prepayPrincipalPayment": 1928.07446,
        "scheduledPrincipalPayment": 5199.819081
    }
    {
        "date": "2051-10-25",
        "totalCashFlow": 6963.513563,
        "interestPayment": 60.786128,
        "principalBalance": 138983.979304,
        "principalPayment": 6902.727435,
        "endPrincipalBalance": 138983.979304,
        "beginPrincipalBalance": 145886.706738,
        "prepayPrincipalPayment": 1765.38821,
        "scheduledPrincipalPayment": 5137.339225
    }
    {
        "date": "2051-11-25",
        "totalCashFlow": 6844.932485,
        "interestPayment": 57.909991,
        "principalBalance": 132196.95681,
        "principalPayment": 6787.022494,
        "endPrincipalBalance": 132196.95681,
        "beginPrincipalBalance": 138983.979304,
        "prepayPrincipalPayment": 1708.835506,
        "scheduledPrincipalPayment": 5078.186988
    }
    {
        "date": "2051-12-25",
        "totalCashFlow": 6700.687225,
        "interestPayment": 55.082065,
        "principalBalance": 125551.351651,
        "principalPayment": 6645.605159,
        "endPrincipalBalance": 125551.351651,
        "beginPrincipalBalance": 132196.95681,
        "prepayPrincipalPayment": 1627.001058,
        "scheduledPrincipalPayment": 5018.604101
    }
    {
        "date": "2052-01-25",
        "totalCashFlow": 6570.609639,
        "interestPayment": 52.313063,
        "principalBalance": 119033.055074,
        "principalPayment": 6518.296576,
        "endPrincipalBalance": 119033.055074,
        "beginPrincipalBalance": 125551.351651,
        "prepayPrincipalPayment": 1558.734974,
        "scheduledPrincipalPayment": 4959.561602
    }
    {
        "date": "2052-02-25",
        "totalCashFlow": 6395.296329,
        "interestPayment": 49.597106,
        "principalBalance": 112687.355851,
        "principalPayment": 6345.699223,
        "endPrincipalBalance": 112687.355851,
        "beginPrincipalBalance": 119033.055074,
        "prepayPrincipalPayment": 1445.144062,
        "scheduledPrincipalPayment": 4900.555161
    }
    {
        "date": "2052-03-25",
        "totalCashFlow": 6290.82994,
        "interestPayment": 46.953065,
        "principalBalance": 106443.478977,
        "principalPayment": 6243.876875,
        "endPrincipalBalance": 106443.478977,
        "beginPrincipalBalance": 112687.355851,
        "prepayPrincipalPayment": 1400.332364,
        "scheduledPrincipalPayment": 4843.544511
    }
    {
        "date": "2052-04-25",
        "totalCashFlow": 6227.916178,
        "interestPayment": 44.35145,
        "principalBalance": 100259.914248,
        "principalPayment": 6183.564728,
        "endPrincipalBalance": 100259.914248,
        "beginPrincipalBalance": 106443.478977,
        "prepayPrincipalPayment": 1397.93292,
        "scheduledPrincipalPayment": 4785.631808
    }
    {
        "date": "2052-05-25",
        "totalCashFlow": 6152.332044,
        "interestPayment": 41.774964,
        "principalBalance": 94149.357168,
        "principalPayment": 6110.55708,
        "endPrincipalBalance": 94149.357168,
        "beginPrincipalBalance": 100259.914248,
        "prepayPrincipalPayment": 1385.817701,
        "scheduledPrincipalPayment": 4724.739379
    }
    {
        "date": "2052-06-25",
        "totalCashFlow": 6064.71896,
        "interestPayment": 39.228899,
        "principalBalance": 88123.867107,
        "principalPayment": 6025.490061,
        "endPrincipalBalance": 88123.867107,
        "beginPrincipalBalance": 94149.357168,
        "prepayPrincipalPayment": 1364.436771,
        "scheduledPrincipalPayment": 4661.05329
    }
    {
        "date": "2052-07-25",
        "totalCashFlow": 5908.390274,
        "interestPayment": 36.718278,
        "principalBalance": 82252.195111,
        "principalPayment": 5871.671996,
        "endPrincipalBalance": 82252.195111,
        "beginPrincipalBalance": 88123.867107,
        "prepayPrincipalPayment": 1276.904999,
        "scheduledPrincipalPayment": 4594.766998
    }
    {
        "date": "2052-08-25",
        "totalCashFlow": 5796.101126,
        "interestPayment": 34.271748,
        "principalBalance": 76490.365733,
        "principalPayment": 5761.829378,
        "endPrincipalBalance": 76490.365733,
        "beginPrincipalBalance": 82252.195111,
        "prepayPrincipalPayment": 1232.589295,
        "scheduledPrincipalPayment": 4529.240083
    }
    {
        "date": "2052-09-25",
        "totalCashFlow": 5643.547386,
        "interestPayment": 31.870986,
        "principalBalance": 70878.689333,
        "principalPayment": 5611.676401,
        "endPrincipalBalance": 70878.689333,
        "beginPrincipalBalance": 76490.365733,
        "prepayPrincipalPayment": 1149.621288,
        "scheduledPrincipalPayment": 4462.055112
    }
    {
        "date": "2052-10-25",
        "totalCashFlow": 5470.227145,
        "interestPayment": 29.532787,
        "principalBalance": 65437.994975,
        "principalPayment": 5440.694358,
        "endPrincipalBalance": 65437.994975,
        "beginPrincipalBalance": 70878.689333,
        "prepayPrincipalPayment": 1045.282919,
        "scheduledPrincipalPayment": 4395.411438
    }
    {
        "date": "2052-11-25",
        "totalCashFlow": 5343.375557,
        "interestPayment": 27.265831,
        "principalBalance": 60121.885249,
        "principalPayment": 5316.109726,
        "endPrincipalBalance": 60121.885249,
        "beginPrincipalBalance": 65437.994975,
        "prepayPrincipalPayment": 985.298549,
        "scheduledPrincipalPayment": 4330.811177
    }
    {
        "date": "2052-12-25",
        "totalCashFlow": 5177.728664,
        "interestPayment": 25.050786,
        "principalBalance": 54969.20737,
        "principalPayment": 5152.677879,
        "endPrincipalBalance": 54969.20737,
        "beginPrincipalBalance": 60121.885249,
        "prepayPrincipalPayment": 887.258627,
        "scheduledPrincipalPayment": 4265.419251
    }
    {
        "date": "2053-01-25",
        "totalCashFlow": 5055.190237,
        "interestPayment": 22.903836,
        "principalBalance": 49936.92097,
        "principalPayment": 5032.286401,
        "endPrincipalBalance": 49936.92097,
        "beginPrincipalBalance": 54969.20737,
        "prepayPrincipalPayment": 830.249137,
        "scheduledPrincipalPayment": 4202.037263
    }
    {
        "date": "2053-02-25",
        "totalCashFlow": 4891.750769,
        "interestPayment": 20.80705,
        "principalBalance": 45065.977251,
        "principalPayment": 4870.943719,
        "endPrincipalBalance": 45065.977251,
        "beginPrincipalBalance": 49936.92097,
        "prepayPrincipalPayment": 733.321269,
        "scheduledPrincipalPayment": 4137.622449
    }
    {
        "date": "2053-03-25",
        "totalCashFlow": 4759.545389,
        "interestPayment": 18.777491,
        "principalBalance": 40325.209353,
        "principalPayment": 4740.767898,
        "endPrincipalBalance": 40325.209353,
        "beginPrincipalBalance": 45065.977251,
        "prepayPrincipalPayment": 665.154502,
        "scheduledPrincipalPayment": 4075.613396
    }
    {
        "date": "2053-04-25",
        "totalCashFlow": 4651.281334,
        "interestPayment": 16.802171,
        "principalBalance": 35690.730189,
        "principalPayment": 4634.479164,
        "endPrincipalBalance": 35690.730189,
        "beginPrincipalBalance": 40325.209353,
        "prepayPrincipalPayment": 620.824591,
        "scheduledPrincipalPayment": 4013.654573
    }
    {
        "date": "2053-05-25",
        "totalCashFlow": 4532.435582,
        "interestPayment": 14.871138,
        "principalBalance": 31173.165744,
        "principalPayment": 4517.564445,
        "endPrincipalBalance": 31173.165744,
        "beginPrincipalBalance": 35690.730189,
        "prepayPrincipalPayment": 568.422572,
        "scheduledPrincipalPayment": 3949.141873
    }
    {
        "date": "2053-06-25",
        "totalCashFlow": 4397.029228,
        "interestPayment": 12.988819,
        "principalBalance": 26789.125335,
        "principalPayment": 4384.040409,
        "endPrincipalBalance": 26789.125335,
        "beginPrincipalBalance": 31173.165744,
        "prepayPrincipalPayment": 501.579026,
        "scheduledPrincipalPayment": 3882.461383
    }
    {
        "date": "2053-07-25",
        "totalCashFlow": 4258.428515,
        "interestPayment": 11.162136,
        "principalBalance": 22541.858956,
        "principalPayment": 4247.266379,
        "endPrincipalBalance": 22541.858956,
        "beginPrincipalBalance": 26789.125335,
        "prepayPrincipalPayment": 432.191303,
        "scheduledPrincipalPayment": 3815.075076
    }
    {
        "date": "2053-08-25",
        "totalCashFlow": 4117.440881,
        "interestPayment": 9.392441,
        "principalBalance": 18433.810516,
        "principalPayment": 4108.04844,
        "endPrincipalBalance": 18433.810516,
        "beginPrincipalBalance": 22541.858956,
        "prepayPrincipalPayment": 360.843856,
        "scheduledPrincipalPayment": 3747.204584
    }
    {
        "date": "2053-09-25",
        "totalCashFlow": 3969.701659,
        "interestPayment": 7.680754,
        "principalBalance": 14471.789611,
        "principalPayment": 3962.020905,
        "endPrincipalBalance": 14471.789611,
        "beginPrincipalBalance": 18433.810516,
        "prepayPrincipalPayment": 282.93156,
        "scheduledPrincipalPayment": 3679.089345
    }
    {
        "date": "2053-10-25",
        "totalCashFlow": 3828.175546,
        "interestPayment": 6.029912,
        "principalBalance": 10649.643977,
        "principalPayment": 3822.145634,
        "endPrincipalBalance": 10649.643977,
        "beginPrincipalBalance": 14471.789611,
        "prepayPrincipalPayment": 209.84637,
        "scheduledPrincipalPayment": 3612.299264
    }
    {
        "date": "2053-11-25",
        "totalCashFlow": 3689.969408,
        "interestPayment": 4.437352,
        "principalBalance": 6964.111921,
        "principalPayment": 3685.532056,
        "endPrincipalBalance": 6964.111921,
        "beginPrincipalBalance": 10649.643977,
        "prepayPrincipalPayment": 139.345957,
        "scheduledPrincipalPayment": 3546.186099
    }
    {
        "date": "2053-12-25",
        "totalCashFlow": 3550.388377,
        "interestPayment": 2.901713,
        "principalBalance": 3416.625257,
        "principalPayment": 3547.486664,
        "endPrincipalBalance": 3416.625257,
        "beginPrincipalBalance": 6964.111921,
        "prepayPrincipalPayment": 67.24333,
        "scheduledPrincipalPayment": 3480.243334
    }
    {
        "date": "2054-01-25",
        "totalCashFlow": 3418.048851,
        "interestPayment": 1.423594,
        "principalBalance": 0.0,
        "principalPayment": 3416.625257,
        "endPrincipalBalance": 0.0,
        "beginPrincipalBalance": 3416.625257,
        "prepayPrincipalPayment": 0.0,
        "scheduledPrincipalPayment": 3416.625257
    }

    """

    try:
        logger.info("Calling get_cash_flow_sync")

        response = Client().yield_book_rest.get_cash_flow_sync(
            id=id,
            id_type=id_type,
            pricing_date=pricing_date,
            par_amount=par_amount,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called get_cash_flow_sync")

        return output
    except Exception as err:
        logger.error("Error get_cash_flow_sync.")
        check_exception_and_raise(err, logger)


def get_csv_bulk_result(*, ids: List[str], fields: List[str], job: Optional[str] = None) -> str:
    """
    Retrieve bulk results with multiple request id or request name.

    Parameters
    ----------
    ids : List[str]
          Ids can be provided comma separated. Different formats for id are:
          1) RequestId R-number
          2) Request name R:name. In this case also provide jobid (J-number) or jobname (J:name)
          3) Jobid J-number
          4) Job name J:name - only 1 active job with the jobname
          5) Tag name T:name. In this case also provide jobid (J-number) or jobname (J:name)
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    fields : List[str]


    Returns
    --------
    str
        A sequence of textual characters.

    Examples
    --------


    """

    try:
        logger.info("Calling get_csv_bulk_result")

        response = Client().yield_book_rest.get_csv_bulk_result(ids=ids, job=job, fields=fields)

        output = response
        logger.info("Called get_csv_bulk_result")

        return output
    except Exception as err:
        logger.error("Error get_csv_bulk_result.")
        check_exception_and_raise(err, logger)


def get_formatted_result(*, request_id_parameter: str, format: str, job: Optional[str] = None) -> Any:
    """
    Retrieve single formatted result using request id or request name.

    Parameters
    ----------
    request_id_parameter : str
        Unique request id. This can be of the format R-number or request name. If request name is used, corresponding job information should be passed in the query parameter.
    format : str
        Only "html" format supported for now.
    job : str, optional
        Job reference. This can be of the form J-number or job name.

    Returns
    --------
    Any


    Examples
    --------
    >>> # link a request to the job
    >>> indic_response = request_bond_indic_async_get(id="999818YT",
    >>>                                               id_type=IdTypeEnum.CUSIP
    >>>         )
    >>>
    >>> # provide a window of time for job to finish
    >>> time.sleep(10)
    >>>
    >>> # get result
    >>> response = get_formatted_result(request_id_parameter=indic_response['requestId'], format="html")
    >>>
    >>> print(response)


    <!DOCTYPE HTML>
    <html>
       <head>
          <style>
             html,
    body {
        font-family: Arial, sans-serif;
        font-size: 11px;
    }

    html,
    body,
    div,
    span {
        box-sizing: content-box;
    }
    * {
        box-sizing: border-box;
    }
    *:before {
        box-sizing: border-box;
    }
    *:after {
        box-sizing: border-box;
    }

    button,
    input[type="button"] {
        font-size: 11px;
        cursor: pointer;
        outline: 0;
        border: none;
        border-radius: 3px;
        padding: 0 10px;
    }

    textarea {
        font-family: Arial, sans-serif;
        font-size: 11px;
        color: #5b6974;
        padding-left: 5px;
        padding-right: 5px;
    }
             .main-container {
        padding: 5px;
        margin: 0 auto;
    }
    .main-container .root-container {
        display: flex;
    }
    .main-container .section-container {
        display: flex;
        flex-direction: row;
        width: 1375px;
        flex-wrap: wrap;
        margin: 0 auto;
    }

    .section-container .json-group {
        margin: 5px 10px 15px 5px;
        padding: 15px 20px 15px 15px;
        border: solid #e9ebec;
        overflow: auto;
        width: 1315px;
    }

    .main-container .section-column-container {
        display: flex;
        flex-direction: column;
    }

    .main-container .top-info {
        padding-left: 10px;
        width: 1375px;
        margin: 0 auto;
    }
    .main-container .top-info label {
        font-size: 12px;
        font-weight: bold;
        margin-right: 5px;
    }
    .section-container .section-group {
        margin: 5px 10px 15px 5px;
        padding: 15px 20px 15px 15px;
        border: solid #e9ebec;
        overflow: auto;
        min-width: 400px;
    }
    .section-container .section-group .header {
        padding: 5px;
        padding-top: 1px;
        font-weight: bold;
        /* text-transform: uppercase; */
    }
    .section-container .section-group table {
        width: 100%;
        font-size: 11px;
    }
    .section-container .section-group table td {
        padding: 3px;
        border-bottom: 1px solid rgba(0, 0, 0, 0.08);
    }
    .section-container .key-value-table td:nth-child(1) {
        width: 60%;
    }
    .section-container .key-value-table td:nth-child(1) span:nth-child(2) {
        background-color: #f3df9d;
    }
    .section-container .key-value-table td:nth-child(2) {
        width: 40%;
        text-align: right;
    }

    .section-container .partial-table td:nth-child(1),
    .section-container .partial-table th:nth-child(1) {
        width: 20%;
        text-align: center;
    }
    .section-container .partial-table th span:nth-child(3) {
        background-color: #f3df9d;
    }
    .section-container .partial-table td:nth-child(2),
    .section-container .partial-table td:nth-child(3),
    .section-container .partial-table th:nth-child(2),
    .section-container .partial-table th:nth-child(3) {
        width: 40%;
        text-align: right;
    }

    .section-container .regular-table th {
        text-align: right;
    }
    .section-container .regular-table th:nth-child(1) {
        text-align: left;
    }
    .section-container .regular-table td {
        padding: 3px;
        border-bottom: 1px solid rgba(0, 0, 0, 0.08);
        text-align: right;
    }
    .section-container .regular-table th span:nth-child(3) {
        background-color: #f3df9d;
    }
    .section-container .regular-table td:nth-child(1) {
        text-align: left;
    }
    .section-container .prepayment-model-projection-table {
        width: calc(66.66% - 55px);
    }
    .section-container .prepayment-model-projection-table td {
        width: 16%;
    }
    .section-container .prepayment-model-projection-table td:nth-child(1) {
        width: 20%;
    }

    .section-container .flat-table table,
    .section-container .flat-table table th,
    .section-container .flat-table table td {
        padding: 10px;
        border: 1px solid rgba(0, 0, 0, 0.25);
        border-collapse: collapse;
        text-align: center;
    }

    /* Indic Layoyut*/
    .section-container .indic-bond-description {
        min-height: 436px;
    }
    .section-container .indic-bond-row {
        min-height: 190px;
    }

    .section-container .indic-mort-collatral {
        min-height: 532px;
    }
    .section-container .indic-mort-row {
        min-height: 140px;
    }

          </style>
       </head>
       <body>
          <div class="main-container">

    <div class="root-container">
      <div class="section-container section-column-container">
        <div class="section-group key-value-table indic-mort-collatral">
          <div class="header">COLLATERAL</div>
          <table>
            <tbody>
              <tr>
                <td>Ticker</td>
                <td>GNMA</td>
              </tr>
              <tr>
                <td>Original Term</td>
                <td>360</td>
              </tr>
              <tr>
                <td>Issue Date</td>
                <td>2013-05-01</td>
              </tr>
              <tr>
                <td>Gross WAC</td>
                <td>4.0000</td>
              </tr>
              <tr>
                <td>Coupon</td>
                <td>3.500000</td>
              </tr>
              <tr>
                <td>Credit Score</td>
                <td>692</td>
              </tr>
              <tr>
                <td>Original LTV</td>
                <td>90.0000</td>
              </tr>
              <tr>
                <td>Current LTV</td>
                <td>27.5000</td>
              </tr>
              <tr>
                <td>Original TPO</td>
                <td></td>
              </tr>
              <tr>
                <td>Current TPO</td>
                <td></td>
              </tr>
              <tr>
                <td>SATO</td>
                <td>22.3000</td>
              </tr>
              <tr>
                <td>Security Type</td>
                <td>MORT</td>
              </tr>
              <tr>
                <td>Security Sub Type</td>
                <td>MPGNMA</td>
              </tr>
              <tr>
                <td>Maturity</td>
                <td>2041-12-01</td>
              </tr>
              <tr>
                <td>WAM</td>
                <td>196</td>
              </tr>
              <tr>
                <td>WALA</td>
                <td>147</td>
              </tr>
              <tr>
                <td>Weighted Avg Loan Size</td>
                <td>101863.0000</td>
              </tr>
              <tr>
                <td>Weighted Average Original Loan Size</td>
                <td></td>
              </tr>
              <tr>
                <td>Current Loan Size</td>
                <td></td>
              </tr>
              <tr>
                <td>Original Loan Size</td>
                <td>182051.000000</td>
              </tr>
              <tr>
                <td>Servicer</td>
                <td></td>
              </tr>
              <tr>
                <td>Delay</td>
                <td>44</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="section-container section-column-container">
        <div class="section-group key-value-table indic-mort-row">
          <div class="header">DISCLOSURE INFORMATION</div>
          <table>
            <tbody>
              <tr>
                <td>Credit Score</td>
                <td>MORT</td>
              </tr>
              <tr>
                <td>LTV</td>
                <td>692</td>
              </tr>
              <tr>
                <td>Load Size</td>
                <td></td>
              </tr>
              <tr>
                <td>% Refinance</td>
                <td></td>
              </tr>
              <tr>
                <td>% Refinance</td>
                <td>0.0000</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="section-group key-value-table indic-mort-row">
          <div class="header">Ratings</div>
          <table>
            <tbody>

              <tr>
                <td>Moody's</td>
                <td>Aaa</td>
              </tr>


            </tbody>
          </table>
        </div>
        <div class="section-group key-value-table indic-mort-row">
          <div class="header">Sector</div>
          <table>
            <tbody>
              <tr>
                <td>GLIC Code</td>
                <td>MBS</td>
              </tr>
              <tr>
                <td>COBS Code</td>
                <td>MTGE</td>
              </tr>
              <tr>
                <td>Market Type</td>
                <td>DOMC</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="section-container section-column-container">
        <div class="section-group partial-table indic-mort-collatral">
          <div class="header">PREPAY HISTORY</div>

          <h4>PSA</h4>
          <table>
            <tbody>
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Value</th>
                </tr>
              </thead>

              <tr>
                <td>1</td>
                <td>104.2558</td>
              </tr>

              <tr>
                <td>3</td>
                <td>101.9675</td>
              </tr>

              <tr>
                <td>6</td>
                <td>101.3512</td>
              </tr>

              <tr>
                <td>12</td>
                <td>101.4048</td>
              </tr>

              <tr>
                <td>24</td>
                <td>0.0000</td>
              </tr>

            </tbody>
          </table>

          <h4>CPR</h4>
          <table>
            <tbody>
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Value</th>
                </tr>
              </thead>

              <tr>
                <td>1</td>
                <td>6.2554</td>
              </tr>

              <tr>
                <td>3</td>
                <td>6.1180</td>
              </tr>

              <tr>
                <td>6</td>
                <td>6.0811</td>
              </tr>

              <tr>
                <td>12</td>
                <td>6.0843</td>
              </tr>

              <tr>
                <td>24</td>
                <td>0.0000</td>
              </tr>

            </tbody>
          </table>

        </div>
      </div>
    </div>

          </div>
          <div style="page-break-before: always;">
             <div class="main-container">
                <div class="section-container">
                   <details>
                      <summary>Show json</summary>
                      <div class="json-group">
                         <pre>{
      &quot;data&quot; : {
        &quot;cusip&quot; : &quot;999818YT8&quot;,
        &quot;indic&quot; : {
          &quot;ltv&quot; : 90.0000,
          &quot;wam&quot; : 196,
          &quot;figi&quot; : &quot;BBG0033WXBV4&quot;,
          &quot;cusip&quot; : &quot;999818YT8&quot;,
          &quot;moody&quot; : [ {
            &quot;value&quot; : &quot;Aaa&quot;
          } ],
          &quot;source&quot; : &quot;CITI&quot;,
          &quot;ticker&quot; : &quot;GNMA&quot;,
          &quot;country&quot; : &quot;US&quot;,
          &quot;loanAge&quot; : 147,
          &quot;lockout&quot; : 0,
          &quot;putFlag&quot; : false,
          &quot;callFlag&quot; : false,
          &quot;cobsCode&quot; : &quot;MTGE&quot;,
          &quot;country2&quot; : &quot;US&quot;,
          &quot;country3&quot; : &quot;USA&quot;,
          &quot;currency&quot; : &quot;USD&quot;,
          &quot;dayCount&quot; : &quot;30/360 eom&quot;,
          &quot;glicCode&quot; : &quot;MBS&quot;,
          &quot;grossWAC&quot; : 4.0000,
          &quot;ioPeriod&quot; : 0,
          &quot;poolCode&quot; : &quot;NA&quot;,
          &quot;sinkFlag&quot; : false,
          &quot;cmaTicker&quot; : &quot;N/A&quot;,
          &quot;datedDate&quot; : &quot;2013-05-01&quot;,
          &quot;gnma2Flag&quot; : false,
          &quot;percentVA&quot; : 11.040,
          &quot;currentLTV&quot; : 27.5000,
          &quot;extendFlag&quot; : &quot;N&quot;,
          &quot;isoCountry&quot; : &quot;US&quot;,
          &quot;marketType&quot; : &quot;DOMC&quot;,
          &quot;percentDTI&quot; : 34.000000,
          &quot;percentFHA&quot; : 80.910,
          &quot;percentInv&quot; : 0.0000,
          &quot;percentPIH&quot; : 0.140,
          &quot;percentRHS&quot; : 7.900,
          &quot;securityID&quot; : &quot;999818YT&quot;,
          &quot;serviceFee&quot; : 0.5000,
          &quot;vPointType&quot; : &quot;MPGNMA&quot;,
          &quot;adjustedLTV&quot; : 27.5000,
          &quot;combinedLTV&quot; : 90.700000,
          &quot;creditScore&quot; : 692,
          &quot;description&quot; : &quot;30-YR GNMA-2013 PROD&quot;,
          &quot;esgBondFlag&quot; : false,
          &quot;indexRating&quot; : &quot;AA+&quot;,
          &quot;issueAmount&quot; : 8597.24000000,
          &quot;lowerRating&quot; : &quot;AA+&quot;,
          &quot;paymentFreq&quot; : 12,
          &quot;percentHARP&quot; : 0.000,
          &quot;percentRefi&quot; : 63.7000,
          &quot;tierCapital&quot; : &quot;NA&quot;,
          &quot;balloonMonth&quot; : 0,
          &quot;deliveryFlag&quot; : &quot;N&quot;,
          &quot;indexCountry&quot; : &quot;US&quot;,
          &quot;industryCode&quot; : &quot;MT&quot;,
          &quot;issuerTicker&quot; : &quot;GNMA&quot;,
          &quot;lowestRating&quot; : &quot;AA+&quot;,
          &quot;maturityDate&quot; : &quot;2041-12-01&quot;,
          &quot;middleRating&quot; : &quot;AA+&quot;,
          &quot;modifiedDate&quot; : &quot;2025-08-13&quot;,
          &quot;originalTerm&quot; : 360,
          &quot;parentTicker&quot; : &quot;GNMA&quot;,
          &quot;percentHARP2&quot; : 0.000,
          &quot;percentJumbo&quot; : 0.000,
          &quot;securityType&quot; : &quot;MORT&quot;,
          &quot;currentCoupon&quot; : 3.500000,
          &quot;dataStateList&quot; : [ {
            &quot;state&quot; : &quot;PR&quot;,
            &quot;percent&quot; : 17.1300
          }, {
            &quot;state&quot; : &quot;TX&quot;,
            &quot;percent&quot; : 10.0300
          }, {
            &quot;state&quot; : &quot;FL&quot;,
            &quot;percent&quot; : 5.6600
          }, {
            &quot;state&quot; : &quot;CA&quot;,
            &quot;percent&quot; : 4.9500
          }, {
            &quot;state&quot; : &quot;OH&quot;,
            &quot;percent&quot; : 4.7700
          }, {
            &quot;state&quot; : &quot;NY&quot;,
            &quot;percent&quot; : 4.7600
          }, {
            &quot;state&quot; : &quot;GA&quot;,
            &quot;percent&quot; : 4.4100
          }, {
            &quot;state&quot; : &quot;PA&quot;,
            &quot;percent&quot; : 3.3800
          }, {
            &quot;state&quot; : &quot;MI&quot;,
            &quot;percent&quot; : 3.0800
          }, {
            &quot;state&quot; : &quot;NC&quot;,
            &quot;percent&quot; : 2.7300
          }, {
            &quot;state&quot; : &quot;IL&quot;,
            &quot;percent&quot; : 2.6800
          }, {
            &quot;state&quot; : &quot;VA&quot;,
            &quot;percent&quot; : 2.6800
          }, {
            &quot;state&quot; : &quot;NJ&quot;,
            &quot;percent&quot; : 2.4000
          }, {
            &quot;state&quot; : &quot;IN&quot;,
            &quot;percent&quot; : 2.3700
          }, {
            &quot;state&quot; : &quot;MD&quot;,
            &quot;percent&quot; : 2.2300
          }, {
            &quot;state&quot; : &quot;MO&quot;,
            &quot;percent&quot; : 2.1100
          }, {
            &quot;state&quot; : &quot;AZ&quot;,
            &quot;percent&quot; : 1.7200
          }, {
            &quot;state&quot; : &quot;TN&quot;,
            &quot;percent&quot; : 1.6600
          }, {
            &quot;state&quot; : &quot;WA&quot;,
            &quot;percent&quot; : 1.4900
          }, {
            &quot;state&quot; : &quot;AL&quot;,
            &quot;percent&quot; : 1.4800
          }, {
            &quot;state&quot; : &quot;OK&quot;,
            &quot;percent&quot; : 1.2300
          }, {
            &quot;state&quot; : &quot;LA&quot;,
            &quot;percent&quot; : 1.2200
          }, {
            &quot;state&quot; : &quot;MN&quot;,
            &quot;percent&quot; : 1.1800
          }, {
            &quot;state&quot; : &quot;SC&quot;,
            &quot;percent&quot; : 1.1100
          }, {
            &quot;state&quot; : &quot;CT&quot;,
            &quot;percent&quot; : 1.0800
          }, {
            &quot;state&quot; : &quot;CO&quot;,
            &quot;percent&quot; : 1.0400
          }, {
            &quot;state&quot; : &quot;KY&quot;,
            &quot;percent&quot; : 1.0400
          }, {
            &quot;state&quot; : &quot;WI&quot;,
            &quot;percent&quot; : 1.0000
          }, {
            &quot;state&quot; : &quot;MS&quot;,
            &quot;percent&quot; : 0.9600
          }, {
            &quot;state&quot; : &quot;NM&quot;,
            &quot;percent&quot; : 0.9500
          }, {
            &quot;state&quot; : &quot;OR&quot;,
            &quot;percent&quot; : 0.8900
          }, {
            &quot;state&quot; : &quot;AR&quot;,
            &quot;percent&quot; : 0.7500
          }, {
            &quot;state&quot; : &quot;NV&quot;,
            &quot;percent&quot; : 0.7000
          }, {
            &quot;state&quot; : &quot;MA&quot;,
            &quot;percent&quot; : 0.6700
          }, {
            &quot;state&quot; : &quot;IA&quot;,
            &quot;percent&quot; : 0.6100
          }, {
            &quot;state&quot; : &quot;UT&quot;,
            &quot;percent&quot; : 0.5900
          }, {
            &quot;state&quot; : &quot;KS&quot;,
            &quot;percent&quot; : 0.5800
          }, {
            &quot;state&quot; : &quot;DE&quot;,
            &quot;percent&quot; : 0.4500
          }, {
            &quot;state&quot; : &quot;ID&quot;,
            &quot;percent&quot; : 0.4000
          }, {
            &quot;state&quot; : &quot;NE&quot;,
            &quot;percent&quot; : 0.3800
          }, {
            &quot;state&quot; : &quot;WV&quot;,
            &quot;percent&quot; : 0.2700
          }, {
            &quot;state&quot; : &quot;ME&quot;,
            &quot;percent&quot; : 0.1900
          }, {
            &quot;state&quot; : &quot;NH&quot;,
            &quot;percent&quot; : 0.1600
          }, {
            &quot;state&quot; : &quot;HI&quot;,
            &quot;percent&quot; : 0.1500
          }, {
            &quot;state&quot; : &quot;MT&quot;,
            &quot;percent&quot; : 0.1300
          }, {
            &quot;state&quot; : &quot;AK&quot;,
            &quot;percent&quot; : 0.1200
          }, {
            &quot;state&quot; : &quot;RI&quot;,
            &quot;percent&quot; : 0.1200
          }, {
            &quot;state&quot; : &quot;WY&quot;,
            &quot;percent&quot; : 0.0800
          }, {
            &quot;state&quot; : &quot;SD&quot;,
            &quot;percent&quot; : 0.0700
          }, {
            &quot;state&quot; : &quot;VT&quot;,
            &quot;percent&quot; : 0.0600
          }, {
            &quot;state&quot; : &quot;DC&quot;,
            &quot;percent&quot; : 0.0400
          }, {
            &quot;state&quot; : &quot;ND&quot;,
            &quot;percent&quot; : 0.0400
          } ],
          &quot;delinquencies&quot; : {
            &quot;del30Days&quot; : {
              &quot;percent&quot; : 3.1400
            },
            &quot;del60Days&quot; : {
              &quot;percent&quot; : 0.5700
            },
            &quot;del90Days&quot; : {
              &quot;percent&quot; : 0.2100
            },
            &quot;del90PlusDays&quot; : {
              &quot;percent&quot; : 0.5900
            },
            &quot;del120PlusDays&quot; : {
              &quot;percent&quot; : 0.3800
            }
          },
          &quot;greenBondFlag&quot; : false,
          &quot;highestRating&quot; : &quot;AAA&quot;,
          &quot;incomeCountry&quot; : &quot;US&quot;,
          &quot;issuerCountry&quot; : &quot;US&quot;,
          &quot;percentSecond&quot; : 0.000,
          &quot;poolAgeMethod&quot; : &quot;Calculated&quot;,
          &quot;prepayEffDate&quot; : &quot;2025-05-01&quot;,
          &quot;seniorityType&quot; : &quot;NA&quot;,
          &quot;assetClassCode&quot; : &quot;CO&quot;,
          &quot;cgmiSectorCode&quot; : &quot;MTGE&quot;,
          &quot;cleanPayMonths&quot; : 0,
          &quot;collateralType&quot; : &quot;GNMA&quot;,
          &quot;fullPledgeFlag&quot; : false,
          &quot;gpmPercentStep&quot; : 0.0000,
          &quot;incomeCountry3&quot; : &quot;USA&quot;,
          &quot;instrumentType&quot; : &quot;NA&quot;,
          &quot;issuerCountry2&quot; : &quot;US&quot;,
          &quot;issuerCountry3&quot; : &quot;USA&quot;,
          &quot;lowestRatingNF&quot; : &quot;AA+&quot;,
          &quot;poolIssuerName&quot; : &quot;NA&quot;,
          &quot;vPointCategory&quot; : &quot;RP&quot;,
          &quot;amortizedFHALTV&quot; : 63.0000,
          &quot;bloombergTicker&quot; : &quot;GNSF 3.5 2013&quot;,
          &quot;industrySubCode&quot; : &quot;MT&quot;,
          &quot;originationDate&quot; : &quot;2013-05-01&quot;,
          &quot;originationYear&quot; : 2013,
          &quot;percent2To4Unit&quot; : 2.7000,
          &quot;percentHAMPMods&quot; : 0.900000,
          &quot;percentPurchase&quot; : 31.8000,
          &quot;percentStateHFA&quot; : 0.400000,
          &quot;poolOriginalWAM&quot; : 0,
          &quot;preliminaryFlag&quot; : false,
          &quot;redemptionValue&quot; : 100.0000,
          &quot;securitySubType&quot; : &quot;MPGNMA&quot;,
          &quot;dataQuartileList&quot; : [ {
            &quot;ltvlow&quot; : 17.000,
            &quot;ltvhigh&quot; : 87.000,
            &quot;loanSizeLow&quot; : 22000.000,
            &quot;loanSizeHigh&quot; : 101000.000,
            &quot;percentDTILow&quot; : 10.000,
            &quot;creditScoreLow&quot; : 300.000,
            &quot;percentDTIHigh&quot; : 24.500,
            &quot;creditScoreHigh&quot; : 655.000,
            &quot;originalLoanAgeLow&quot; : 0,
            &quot;originationYearLow&quot; : 20101101,
            &quot;originalLoanAgeHigh&quot; : 0,
            &quot;originationYearHigh&quot; : 20130401
          }, {
            &quot;ltvlow&quot; : 87.000,
            &quot;ltvhigh&quot; : 93.000,
            &quot;loanSizeLow&quot; : 101000.000,
            &quot;loanSizeHigh&quot; : 132000.000,
            &quot;percentDTILow&quot; : 24.500,
            &quot;creditScoreLow&quot; : 655.000,
            &quot;percentDTIHigh&quot; : 34.700,
            &quot;creditScoreHigh&quot; : 691.000,
            &quot;originalLoanAgeLow&quot; : 0,
            &quot;originationYearLow&quot; : 20130401,
            &quot;originalLoanAgeHigh&quot; : 0,
            &quot;originationYearHigh&quot; : 20130501
          }, {
            &quot;ltvlow&quot; : 93.000,
            &quot;ltvhigh&quot; : 97.000,
            &quot;loanSizeLow&quot; : 132000.000,
            &quot;loanSizeHigh&quot; : 183000.000,
            &quot;percentDTILow&quot; : 34.700,
            &quot;creditScoreLow&quot; : 691.000,
            &quot;percentDTIHigh&quot; : 43.600,
            &quot;creditScoreHigh&quot; : 739.000,
            &quot;originalLoanAgeLow&quot; : 0,
            &quot;originationYearLow&quot; : 20130501,
            &quot;originalLoanAgeHigh&quot; : 1,
            &quot;originationYearHigh&quot; : 20130701
          }, {
            &quot;ltvlow&quot; : 97.000,
            &quot;ltvhigh&quot; : 118.000,
            &quot;loanSizeLow&quot; : 183000.000,
            &quot;loanSizeHigh&quot; : 743000.000,
            &quot;percentDTILow&quot; : 43.600,
            &quot;creditScoreLow&quot; : 739.000,
            &quot;percentDTIHigh&quot; : 65.000,
            &quot;creditScoreHigh&quot; : 832.000,
            &quot;originalLoanAgeLow&quot; : 1,
            &quot;originationYearLow&quot; : 20130701,
            &quot;originalLoanAgeHigh&quot; : 43,
            &quot;originationYearHigh&quot; : 20141101
          } ],
          &quot;gpmNumberOfSteps&quot; : 0,
          &quot;percentHARPOwner&quot; : 0.000,
          &quot;percentPrincipal&quot; : 100.0000,
          &quot;securityCalcType&quot; : &quot;GNMA&quot;,
          &quot;assetClassSubCode&quot; : &quot;MBS&quot;,
          &quot;forbearanceAmount&quot; : 0.000000,
          &quot;modifiedTimeStamp&quot; : &quot;2025-08-13T19:37:00Z&quot;,
          &quot;outstandingAmount&quot; : 1079.93000000,
          &quot;parentDescription&quot; : &quot;NA&quot;,
          &quot;poolIsBalloonFlag&quot; : false,
          &quot;prepaymentOptions&quot; : {
            &quot;prepayType&quot; : [ &quot;CPR&quot;, &quot;PSA&quot;, &quot;VEC&quot; ]
          },
          &quot;reperformerMonths&quot; : 1,
          &quot;dataPPMHistoryList&quot; : [ {
            &quot;prepayType&quot; : &quot;PSA&quot;,
            &quot;dataPPMHistoryDetailList&quot; : [ {
              &quot;month&quot; : &quot;1&quot;,
              &quot;prepayRate&quot; : 104.2558
            }, {
              &quot;month&quot; : &quot;3&quot;,
              &quot;prepayRate&quot; : 101.9675
            }, {
              &quot;month&quot; : &quot;6&quot;,
              &quot;prepayRate&quot; : 101.3512
            }, {
              &quot;month&quot; : &quot;12&quot;,
              &quot;prepayRate&quot; : 101.4048
            }, {
              &quot;month&quot; : &quot;24&quot;,
              &quot;prepayRate&quot; : 0.0000
            } ]
          }, {
            &quot;prepayType&quot; : &quot;CPR&quot;,
            &quot;dataPPMHistoryDetailList&quot; : [ {
              &quot;month&quot; : &quot;1&quot;,
              &quot;prepayRate&quot; : 6.2554
            }, {
              &quot;month&quot; : &quot;3&quot;,
              &quot;prepayRate&quot; : 6.1180
            }, {
              &quot;month&quot; : &quot;6&quot;,
              &quot;prepayRate&quot; : 6.0811
            }, {
              &quot;month&quot; : &quot;12&quot;,
              &quot;prepayRate&quot; : 6.0843
            }, {
              &quot;month&quot; : &quot;24&quot;,
              &quot;prepayRate&quot; : 0.0000
            } ]
          } ],
          &quot;daysToFirstPayment&quot; : 44,
          &quot;issuerLowestRating&quot; : &quot;NA&quot;,
          &quot;issuerMiddleRating&quot; : &quot;NA&quot;,
          &quot;newCurrentLoanSize&quot; : 101863.000,
          &quot;originationChannel&quot; : {
            &quot;broker&quot; : 4.650,
            &quot;retail&quot; : 61.970,
            &quot;unknown&quot; : 0.000,
            &quot;unspecified&quot; : 0.000,
            &quot;correspondence&quot; : 33.370
          },
          &quot;percentMultiFamily&quot; : 2.700000,
          &quot;percentRefiCashout&quot; : 5.8000,
          &quot;percentRegularMods&quot; : 3.600000,
          &quot;percentReperformer&quot; : 0.500000,
          &quot;relocationLoanFlag&quot; : false,
          &quot;socialDensityScore&quot; : 0.000,
          &quot;umbsfhlgPercentage&quot; : 0.00,
          &quot;umbsfnmaPercentage&quot; : 0.00,
          &quot;industryDescription&quot; : &quot;Mortgage&quot;,
          &quot;issuerHighestRating&quot; : &quot;NA&quot;,
          &quot;newOriginalLoanSize&quot; : 182051.000,
          &quot;socialCriteriaShare&quot; : 0.000,
          &quot;spreadAtOrigination&quot; : 22.3000,
          &quot;weightedAvgLoanSize&quot; : 101863.0000,
          &quot;poolOriginalLoanSize&quot; : 182051.000000,
          &quot;cgmiSectorDescription&quot; : &quot;Mortgage&quot;,
          &quot;cleanPayAverageMonths&quot; : 0,
          &quot;expModelAvailableFlag&quot; : true,
          &quot;fhfaImpliedCurrentLTV&quot; : 27.5000,
          &quot;percentRefiNonCashout&quot; : 57.9000,
          &quot;prepayPenaltySchedule&quot; : &quot;0.000&quot;,
          &quot;defaultHorizonPYMethod&quot; : &quot;OAS Change&quot;,
          &quot;industrySubDescription&quot; : &quot;Mortgage Asset Backed&quot;,
          &quot;actualPrepayHistoryList&quot; : {
            &quot;date&quot; : &quot;2025-10-01&quot;,
            &quot;genericValue&quot; : 0.957500
          },
          &quot;adjustedCurrentLoanSize&quot; : 101863.00,
          &quot;forbearanceModification&quot; : 0.000000,
          &quot;percentTwoPlusBorrowers&quot; : 44.000,
          &quot;poolAvgOriginalLoanTerm&quot; : 0,
          &quot;adjustedOriginalLoanSize&quot; : 182040.00,
          &quot;assetClassSubDescription&quot; : &quot;Collateralized Asset Backed - Mortgage&quot;,
          &quot;mortgageInsurancePremium&quot; : {
            &quot;annual&quot; : {
              &quot;va&quot; : 0.000,
              &quot;fha&quot; : 0.797,
              &quot;pih&quot; : 0.000,
              &quot;rhs&quot; : 0.399
            },
            &quot;upfront&quot; : {
              &quot;va&quot; : 0.500,
              &quot;fha&quot; : 0.693,
              &quot;pih&quot; : 1.000,
              &quot;rhs&quot; : 1.996
            }
          },
          &quot;percentReperformerAndMod&quot; : 0.100,
          &quot;reperformerMonthsForMods&quot; : 2,
          &quot;originalLoanSizeRemaining&quot; : 150891.000,
          &quot;percentFirstTimeHomeBuyer&quot; : 20.800000,
          &quot;current3rdPartyOrigination&quot; : 38.020,
          &quot;adjustedSpreadAtOrigination&quot; : 22.3000,
          &quot;dataPrepayModelServicerList&quot; : [ {
            &quot;percent&quot; : 23.8400,
            &quot;servicer&quot; : &quot;FREE&quot;
          }, {
            &quot;percent&quot; : 11.4000,
            &quot;servicer&quot; : &quot;NSTAR&quot;
          }, {
            &quot;percent&quot; : 11.3900,
            &quot;servicer&quot; : &quot;WELLS&quot;
          }, {
            &quot;percent&quot; : 11.1500,
            &quot;servicer&quot; : &quot;BCPOP&quot;
          }, {
            &quot;percent&quot; : 7.2300,
            &quot;servicer&quot; : &quot;QUICK&quot;
          }, {
            &quot;percent&quot; : 7.1300,
            &quot;servicer&quot; : &quot;PENNY&quot;
          }, {
            &quot;percent&quot; : 6.5100,
            &quot;servicer&quot; : &quot;LAKEV&quot;
          }, {
            &quot;percent&quot; : 6.3400,
            &quot;servicer&quot; : &quot;CARRG&quot;
          }, {
            &quot;percent&quot; : 5.5000,
            &quot;servicer&quot; : &quot;USB&quot;
          }, {
            &quot;percent&quot; : 2.4100,
            &quot;servicer&quot; : &quot;PNC&quot;
          }, {
            &quot;percent&quot; : 1.3400,
            &quot;servicer&quot; : &quot;MNTBK&quot;
          }, {
            &quot;percent&quot; : 1.1700,
            &quot;servicer&quot; : &quot;NWRES&quot;
          }, {
            &quot;percent&quot; : 0.9500,
            &quot;servicer&quot; : &quot;FIFTH&quot;
          }, {
            &quot;percent&quot; : 0.7500,
            &quot;servicer&quot; : &quot;DEPOT&quot;
          }, {
            &quot;percent&quot; : 0.6000,
            &quot;servicer&quot; : &quot;BOKF&quot;
          }, {
            &quot;percent&quot; : 0.5100,
            &quot;servicer&quot; : &quot;JPM&quot;
          }, {
            &quot;percent&quot; : 0.4800,
            &quot;servicer&quot; : &quot;TRUIS&quot;
          }, {
            &quot;percent&quot; : 0.4200,
            &quot;servicer&quot; : &quot;CITI&quot;
          }, {
            &quot;percent&quot; : 0.3800,
            &quot;servicer&quot; : &quot;GUILD&quot;
          }, {
            &quot;percent&quot; : 0.2100,
            &quot;servicer&quot; : &quot;REGNS&quot;
          }, {
            &quot;percent&quot; : 0.2000,
            &quot;servicer&quot; : &quot;CNTRL&quot;
          }, {
            &quot;percent&quot; : 0.0900,
            &quot;servicer&quot; : &quot;COLNL&quot;
          }, {
            &quot;percent&quot; : 0.0600,
            &quot;servicer&quot; : &quot;HFAGY&quot;
          }, {
            &quot;percent&quot; : 0.0600,
            &quot;servicer&quot; : &quot;MNSRC&quot;
          }, {
            &quot;percent&quot; : 0.0300,
            &quot;servicer&quot; : &quot;HOMBR&quot;
          } ],
          &quot;nonWeightedOriginalLoanSize&quot; : 0.000,
          &quot;original3rdPartyOrigination&quot; : 0.000,
          &quot;percentHARPDec2010Extension&quot; : 0.000,
          &quot;percentHARPOneYearExtension&quot; : 0.000,
          &quot;percentDownPaymentAssistance&quot; : 5.600,
          &quot;percentAmortizedFHALTVUnder78&quot; : 95.40,
          &quot;loanPerformanceImpliedCurrentLTV&quot; : 44.8000,
          &quot;reperformerMonthsForReperformers&quot; : 28
        },
        &quot;ticker&quot; : &quot;GNMA&quot;,
        &quot;country&quot; : &quot;US&quot;,
        &quot;currency&quot; : &quot;USD&quot;,
        &quot;identifier&quot; : &quot;999818YT&quot;,
        &quot;description&quot; : &quot;30-YR GNMA-2013 PROD&quot;,
        &quot;issuerTicker&quot; : &quot;GNMA&quot;,
        &quot;maturityDate&quot; : &quot;2041-12-01&quot;,
        &quot;securityType&quot; : &quot;MORT&quot;,
        &quot;currentCoupon&quot; : 3.500000,
        &quot;securitySubType&quot; : &quot;MPGNMA&quot;
      },
      &quot;meta&quot; : {
        &quot;status&quot; : &quot;DONE&quot;,
        &quot;requestId&quot; : &quot;R-20901&quot;,
        &quot;timeStamp&quot; : &quot;2025-08-18T22:33:24Z&quot;,
        &quot;responseType&quot; : &quot;BOND_INDIC&quot;
      }
    }</pre>
                      </div>
                   </details>
                </div>
             </div>
          </div>
       </body>
    </html>

    """

    try:
        logger.info("Calling get_formatted_result")

        response = Client().yield_book_rest.get_formatted_result(
            request_id_parameter=request_id_parameter, format=format, job=job
        )

        output = response
        logger.info("Called get_formatted_result")

        return output
    except Exception as err:
        logger.error("Error get_formatted_result.")
        check_exception_and_raise(err, logger)


def get_job(*, job_ref: str) -> JobResponse:
    """
    Get job details

    Parameters
    ----------
    job_ref : str
        Job reference. This can be of the form J-number or job name.

    Returns
    --------
    JobResponse


    Examples
    --------
    >>> # get job
    >>> response = get_job(job_ref='myJob')
    >>>
    >>> print(js.dumps(response.as_dict(), indent=4))
    {
        "id": "J-16433",
        "sequence": 0,
        "asOf": "2025-03-10",
        "closed": true,
        "onHold": true,
        "aborted": true,
        "exitStatus": "NEVER_STARTED",
        "actualHold": true,
        "name": "myJob",
        "chain": "string",
        "description": "string",
        "priority": 0,
        "order": "FAST",
        "requestCount": 0,
        "pendingCount": 0,
        "runningCount": 0,
        "okCount": 0,
        "errorCount": 0,
        "abortedCount": 0,
        "skipCount": 0,
        "startAfter": "2025-03-03T10:10:15Z",
        "stopAfter": "2025-03-10T20:10:15Z",
        "createdAt": "2025-12-03T12:43:00.855Z",
        "updatedAt": "2025-12-03T12:43:00.881Z"
    }

    """

    try:
        logger.info("Calling get_job")

        response = Client().yield_book_rest.get_job(job_ref=job_ref)

        output = response
        logger.info("Called get_job")

        return output
    except Exception as err:
        logger.error("Error get_job.")
        check_exception_and_raise(err, logger)


def get_job_data(*, job: str, store_type: Union[str, StoreType], request_name: str) -> Any:
    """
    Retrieve job data body using request id or request name.

    Parameters
    ----------
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    request_name : str
        Unique request id. This can be of the format R-number or request name. If request name is used, corresponding job information should be passed in the query parameter.

    Returns
    --------
    Any


    Examples
    --------


    """

    try:
        logger.info("Calling get_job_data")

        response = Client().yield_book_rest.get_job_data(job=job, store_type=store_type, request_name=request_name)

        output = response
        logger.info("Called get_job_data")

        return output
    except Exception as err:
        logger.error("Error get_job_data.")
        check_exception_and_raise(err, logger)


def get_job_object_meta(*, job: str, store_type: Union[str, StoreType], request_id_parameter: str) -> Dict[str, Any]:
    """
    Retrieve job object metadata using request id or request name.

    Parameters
    ----------
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    request_id_parameter : str
        Unique request id. This can be of the format R-number or request name. If request name is used, corresponding job information should be passed in the query parameter.

    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling get_job_object_meta")

        response = Client().yield_book_rest.get_job_object_meta(
            job=job, store_type=store_type, request_id_parameter=request_id_parameter
        )

        output = response
        logger.info("Called get_job_object_meta")

        return output
    except Exception as err:
        logger.error("Error get_job_object_meta.")
        check_exception_and_raise(err, logger)


def get_job_status(*, job_ref: str) -> JobStatusResponse:
    """
    Get job status

    Parameters
    ----------
    job_ref : str
        Job reference. This can be of the form J-number or job name.

    Returns
    --------
    JobStatusResponse


    Examples
    --------
    >>> # create temp job
    >>> job_response = create_job(
    >>>     name="status_Job"
    >>> )
    >>>
    >>> # get job status
    >>> response = get_job_status(job_ref="status_Job")
    >>>
    >>> print(js.dumps(response.as_dict(), indent=4))
    {
        "id": "J-16434",
        "name": "status_Job",
        "jobStatus": "EMPTY",
        "requestCount": 0,
        "pendingCount": 0,
        "runningCount": 0,
        "okCount": 0,
        "errorCount": 0,
        "abortedCount": 0,
        "skippedCount": 0
    }

    """

    try:
        logger.info("Calling get_job_status")

        response = Client().yield_book_rest.get_job_status(job_ref=job_ref)

        output = response
        logger.info("Called get_job_status")

        return output
    except Exception as err:
        logger.error("Error get_job_status.")
        check_exception_and_raise(err, logger)


def get_json_result(
    *, ids: List[str], job: Optional[str] = None, fields: Optional[List[str]] = None, format: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve json result using request id or request name.

    Parameters
    ----------
    ids : List[str]
          Ids can be provided comma separated. Different formats for id are:
          1) RequestId R-number
          2) Request name R:name. In this case also provide jobid (J-number) or jobname (J:name)
          3) Jobid J-number
          4) Job name J:name - only 1 active job with the jobname
          5) Tag name T:name. In this case also provide jobid (J-number) or jobname (J:name)
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    fields : List[str], optional

    format : str, optional
        A sequence of textual characters.

    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling get_json_result")

        response = Client().yield_book_rest.get_json_result(ids=ids, job=job, fields=fields, format=format)

        output = response
        logger.info("Called get_json_result")

        return output
    except Exception as err:
        logger.error("Error get_json_result.")
        check_exception_and_raise(err, logger)


def get_result(*, request_id_parameter: str, job: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve single result using request id or request name.

    Parameters
    ----------
    request_id_parameter : str
        Unique request id. This can be of the format R-number or request name. If request name is used, corresponding job information should be passed in the query parameter.
    job : str, optional
        Job reference. This can be of the form J-number or job name.

    Returns
    --------
    Dict[str, Any]


    Examples
    --------
    >>> # link a request to the job
    >>> indic_response = request_bond_indic_async_get(id="999818YT",
    >>>                                               id_type=IdTypeEnum.CUSIP
    >>>         )
    >>>
    >>> # provide a window of time for job to finish
    >>> time.sleep(10)
    >>>
    >>> # get result
    >>> response = get_result(request_id_parameter=indic_response['requestId'])
    >>>
    >>> print(js.dumps(response, indent=4))
    {
        "data": {
            "cusip": "999818YT8",
            "indic": {
                "ltv": 90.0,
                "wam": 196,
                "figi": "BBG0033WXBV4",
                "cusip": "999818YT8",
                "moody": [
                    {
                        "value": "Aaa"
                    }
                ],
                "source": "CITI",
                "ticker": "GNMA",
                "country": "US",
                "loanAge": 147,
                "lockout": 0,
                "putFlag": false,
                "callFlag": false,
                "cobsCode": "MTGE",
                "country2": "US",
                "country3": "USA",
                "currency": "USD",
                "dayCount": "30/360 eom",
                "glicCode": "MBS",
                "grossWAC": 4.0,
                "ioPeriod": 0,
                "poolCode": "NA",
                "sinkFlag": false,
                "cmaTicker": "N/A",
                "datedDate": "2013-05-01",
                "gnma2Flag": false,
                "percentVA": 11.04,
                "currentLTV": 27.5,
                "extendFlag": "N",
                "isoCountry": "US",
                "marketType": "DOMC",
                "percentDTI": 34.0,
                "percentFHA": 80.91,
                "percentInv": 0.0,
                "percentPIH": 0.14,
                "percentRHS": 7.9,
                "securityID": "999818YT",
                "serviceFee": 0.5,
                "vPointType": "MPGNMA",
                "adjustedLTV": 27.5,
                "combinedLTV": 90.7,
                "creditScore": 692,
                "description": "30-YR GNMA-2013 PROD",
                "esgBondFlag": false,
                "indexRating": "AA+",
                "issueAmount": 8597.24,
                "lowerRating": "AA+",
                "paymentFreq": 12,
                "percentHARP": 0.0,
                "percentRefi": 63.7,
                "tierCapital": "NA",
                "balloonMonth": 0,
                "deliveryFlag": "N",
                "indexCountry": "US",
                "industryCode": "MT",
                "issuerTicker": "GNMA",
                "lowestRating": "AA+",
                "maturityDate": "2041-12-01",
                "middleRating": "AA+",
                "modifiedDate": "2025-08-13",
                "originalTerm": 360,
                "parentTicker": "GNMA",
                "percentHARP2": 0.0,
                "percentJumbo": 0.0,
                "securityType": "MORT",
                "currentCoupon": 3.5,
                "dataStateList": [
                    {
                        "state": "PR",
                        "percent": 17.13
                    },
                    {
                        "state": "TX",
                        "percent": 10.03
                    },
                    {
                        "state": "FL",
                        "percent": 5.66
                    },
                    {
                        "state": "CA",
                        "percent": 4.95
                    },
                    {
                        "state": "OH",
                        "percent": 4.77
                    },
                    {
                        "state": "NY",
                        "percent": 4.76
                    },
                    {
                        "state": "GA",
                        "percent": 4.41
                    },
                    {
                        "state": "PA",
                        "percent": 3.38
                    },
                    {
                        "state": "MI",
                        "percent": 3.08
                    },
                    {
                        "state": "NC",
                        "percent": 2.73
                    },
                    {
                        "state": "IL",
                        "percent": 2.68
                    },
                    {
                        "state": "VA",
                        "percent": 2.68
                    },
                    {
                        "state": "NJ",
                        "percent": 2.4
                    },
                    {
                        "state": "IN",
                        "percent": 2.37
                    },
                    {
                        "state": "MD",
                        "percent": 2.23
                    },
                    {
                        "state": "MO",
                        "percent": 2.11
                    },
                    {
                        "state": "AZ",
                        "percent": 1.72
                    },
                    {
                        "state": "TN",
                        "percent": 1.66
                    },
                    {
                        "state": "WA",
                        "percent": 1.49
                    },
                    {
                        "state": "AL",
                        "percent": 1.48
                    },
                    {
                        "state": "OK",
                        "percent": 1.23
                    },
                    {
                        "state": "LA",
                        "percent": 1.22
                    },
                    {
                        "state": "MN",
                        "percent": 1.18
                    },
                    {
                        "state": "SC",
                        "percent": 1.11
                    },
                    {
                        "state": "CT",
                        "percent": 1.08
                    },
                    {
                        "state": "CO",
                        "percent": 1.04
                    },
                    {
                        "state": "KY",
                        "percent": 1.04
                    },
                    {
                        "state": "WI",
                        "percent": 1.0
                    },
                    {
                        "state": "MS",
                        "percent": 0.96
                    },
                    {
                        "state": "NM",
                        "percent": 0.95
                    },
                    {
                        "state": "OR",
                        "percent": 0.89
                    },
                    {
                        "state": "AR",
                        "percent": 0.75
                    },
                    {
                        "state": "NV",
                        "percent": 0.7
                    },
                    {
                        "state": "MA",
                        "percent": 0.67
                    },
                    {
                        "state": "IA",
                        "percent": 0.61
                    },
                    {
                        "state": "UT",
                        "percent": 0.59
                    },
                    {
                        "state": "KS",
                        "percent": 0.58
                    },
                    {
                        "state": "DE",
                        "percent": 0.45
                    },
                    {
                        "state": "ID",
                        "percent": 0.4
                    },
                    {
                        "state": "NE",
                        "percent": 0.38
                    },
                    {
                        "state": "WV",
                        "percent": 0.27
                    },
                    {
                        "state": "ME",
                        "percent": 0.19
                    },
                    {
                        "state": "NH",
                        "percent": 0.16
                    },
                    {
                        "state": "HI",
                        "percent": 0.15
                    },
                    {
                        "state": "MT",
                        "percent": 0.13
                    },
                    {
                        "state": "AK",
                        "percent": 0.12
                    },
                    {
                        "state": "RI",
                        "percent": 0.12
                    },
                    {
                        "state": "WY",
                        "percent": 0.08
                    },
                    {
                        "state": "SD",
                        "percent": 0.07
                    },
                    {
                        "state": "VT",
                        "percent": 0.06
                    },
                    {
                        "state": "DC",
                        "percent": 0.04
                    },
                    {
                        "state": "ND",
                        "percent": 0.04
                    }
                ],
                "delinquencies": {
                    "del30Days": {
                        "percent": 3.14
                    },
                    "del60Days": {
                        "percent": 0.57
                    },
                    "del90Days": {
                        "percent": 0.21
                    },
                    "del90PlusDays": {
                        "percent": 0.59
                    },
                    "del120PlusDays": {
                        "percent": 0.38
                    }
                },
                "greenBondFlag": false,
                "highestRating": "AAA",
                "incomeCountry": "US",
                "issuerCountry": "US",
                "percentSecond": 0.0,
                "poolAgeMethod": "Calculated",
                "prepayEffDate": "2025-05-01",
                "seniorityType": "NA",
                "assetClassCode": "CO",
                "cgmiSectorCode": "MTGE",
                "cleanPayMonths": 0,
                "collateralType": "GNMA",
                "fullPledgeFlag": false,
                "gpmPercentStep": 0.0,
                "incomeCountry3": "USA",
                "instrumentType": "NA",
                "issuerCountry2": "US",
                "issuerCountry3": "USA",
                "lowestRatingNF": "AA+",
                "poolIssuerName": "NA",
                "vPointCategory": "RP",
                "amortizedFHALTV": 63.0,
                "bloombergTicker": "GNSF 3.5 2013",
                "industrySubCode": "MT",
                "originationDate": "2013-05-01",
                "originationYear": 2013,
                "percent2To4Unit": 2.7,
                "percentHAMPMods": 0.9,
                "percentPurchase": 31.8,
                "percentStateHFA": 0.4,
                "poolOriginalWAM": 0,
                "preliminaryFlag": false,
                "redemptionValue": 100.0,
                "securitySubType": "MPGNMA",
                "dataQuartileList": [
                    {
                        "ltvlow": 17.0,
                        "ltvhigh": 87.0,
                        "loanSizeLow": 22000.0,
                        "loanSizeHigh": 101000.0,
                        "percentDTILow": 10.0,
                        "creditScoreLow": 300.0,
                        "percentDTIHigh": 24.5,
                        "creditScoreHigh": 655.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20101101,
                        "originalLoanAgeHigh": 0,
                        "originationYearHigh": 20130401
                    },
                    {
                        "ltvlow": 87.0,
                        "ltvhigh": 93.0,
                        "loanSizeLow": 101000.0,
                        "loanSizeHigh": 132000.0,
                        "percentDTILow": 24.5,
                        "creditScoreLow": 655.0,
                        "percentDTIHigh": 34.7,
                        "creditScoreHigh": 691.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20130401,
                        "originalLoanAgeHigh": 0,
                        "originationYearHigh": 20130501
                    },
                    {
                        "ltvlow": 93.0,
                        "ltvhigh": 97.0,
                        "loanSizeLow": 132000.0,
                        "loanSizeHigh": 183000.0,
                        "percentDTILow": 34.7,
                        "creditScoreLow": 691.0,
                        "percentDTIHigh": 43.6,
                        "creditScoreHigh": 739.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20130501,
                        "originalLoanAgeHigh": 1,
                        "originationYearHigh": 20130701
                    },
                    {
                        "ltvlow": 97.0,
                        "ltvhigh": 118.0,
                        "loanSizeLow": 183000.0,
                        "loanSizeHigh": 743000.0,
                        "percentDTILow": 43.6,
                        "creditScoreLow": 739.0,
                        "percentDTIHigh": 65.0,
                        "creditScoreHigh": 832.0,
                        "originalLoanAgeLow": 1,
                        "originationYearLow": 20130701,
                        "originalLoanAgeHigh": 43,
                        "originationYearHigh": 20141101
                    }
                ],
                "gpmNumberOfSteps": 0,
                "percentHARPOwner": 0.0,
                "percentPrincipal": 100.0,
                "securityCalcType": "GNMA",
                "assetClassSubCode": "MBS",
                "forbearanceAmount": 0.0,
                "modifiedTimeStamp": "2025-08-13T19:37:00Z",
                "outstandingAmount": 1079.93,
                "parentDescription": "NA",
                "poolIsBalloonFlag": false,
                "prepaymentOptions": {
                    "prepayType": [
                        "CPR",
                        "PSA",
                        "VEC"
                    ]
                },
                "reperformerMonths": 1,
                "dataPPMHistoryList": [
                    {
                        "prepayType": "PSA",
                        "dataPPMHistoryDetailList": [
                            {
                                "month": "1",
                                "prepayRate": 104.2558
                            },
                            {
                                "month": "3",
                                "prepayRate": 101.9675
                            },
                            {
                                "month": "6",
                                "prepayRate": 101.3512
                            },
                            {
                                "month": "12",
                                "prepayRate": 101.4048
                            },
                            {
                                "month": "24",
                                "prepayRate": 0.0
                            }
                        ]
                    },
                    {
                        "prepayType": "CPR",
                        "dataPPMHistoryDetailList": [
                            {
                                "month": "1",
                                "prepayRate": 6.2554
                            },
                            {
                                "month": "3",
                                "prepayRate": 6.118
                            },
                            {
                                "month": "6",
                                "prepayRate": 6.0811
                            },
                            {
                                "month": "12",
                                "prepayRate": 6.0843
                            },
                            {
                                "month": "24",
                                "prepayRate": 0.0
                            }
                        ]
                    }
                ],
                "daysToFirstPayment": 44,
                "issuerLowestRating": "NA",
                "issuerMiddleRating": "NA",
                "newCurrentLoanSize": 101863.0,
                "originationChannel": {
                    "broker": 4.65,
                    "retail": 61.97,
                    "unknown": 0.0,
                    "unspecified": 0.0,
                    "correspondence": 33.37
                },
                "percentMultiFamily": 2.7,
                "percentRefiCashout": 5.8,
                "percentRegularMods": 3.6,
                "percentReperformer": 0.5,
                "relocationLoanFlag": false,
                "socialDensityScore": 0.0,
                "umbsfhlgPercentage": 0.0,
                "umbsfnmaPercentage": 0.0,
                "industryDescription": "Mortgage",
                "issuerHighestRating": "NA",
                "newOriginalLoanSize": 182051.0,
                "socialCriteriaShare": 0.0,
                "spreadAtOrigination": 22.3,
                "weightedAvgLoanSize": 101863.0,
                "poolOriginalLoanSize": 182051.0,
                "cgmiSectorDescription": "Mortgage",
                "cleanPayAverageMonths": 0,
                "expModelAvailableFlag": true,
                "fhfaImpliedCurrentLTV": 27.5,
                "percentRefiNonCashout": 57.9,
                "prepayPenaltySchedule": "0.000",
                "defaultHorizonPYMethod": "OAS Change",
                "industrySubDescription": "Mortgage Asset Backed",
                "actualPrepayHistoryList": {
                    "date": "2025-10-01",
                    "genericValue": 0.9575
                },
                "adjustedCurrentLoanSize": 101863.0,
                "forbearanceModification": 0.0,
                "percentTwoPlusBorrowers": 44.0,
                "poolAvgOriginalLoanTerm": 0,
                "adjustedOriginalLoanSize": 182040.0,
                "assetClassSubDescription": "Collateralized Asset Backed - Mortgage",
                "mortgageInsurancePremium": {
                    "annual": {
                        "va": 0.0,
                        "fha": 0.797,
                        "pih": 0.0,
                        "rhs": 0.399
                    },
                    "upfront": {
                        "va": 0.5,
                        "fha": 0.693,
                        "pih": 1.0,
                        "rhs": 1.996
                    }
                },
                "percentReperformerAndMod": 0.1,
                "reperformerMonthsForMods": 2,
                "originalLoanSizeRemaining": 150891.0,
                "percentFirstTimeHomeBuyer": 20.8,
                "current3rdPartyOrigination": 38.02,
                "adjustedSpreadAtOrigination": 22.3,
                "dataPrepayModelServicerList": [
                    {
                        "percent": 23.84,
                        "servicer": "FREE"
                    },
                    {
                        "percent": 11.4,
                        "servicer": "NSTAR"
                    },
                    {
                        "percent": 11.39,
                        "servicer": "WELLS"
                    },
                    {
                        "percent": 11.15,
                        "servicer": "BCPOP"
                    },
                    {
                        "percent": 7.23,
                        "servicer": "QUICK"
                    },
                    {
                        "percent": 7.13,
                        "servicer": "PENNY"
                    },
                    {
                        "percent": 6.51,
                        "servicer": "LAKEV"
                    },
                    {
                        "percent": 6.34,
                        "servicer": "CARRG"
                    },
                    {
                        "percent": 5.5,
                        "servicer": "USB"
                    },
                    {
                        "percent": 2.41,
                        "servicer": "PNC"
                    },
                    {
                        "percent": 1.34,
                        "servicer": "MNTBK"
                    },
                    {
                        "percent": 1.17,
                        "servicer": "NWRES"
                    },
                    {
                        "percent": 0.95,
                        "servicer": "FIFTH"
                    },
                    {
                        "percent": 0.75,
                        "servicer": "DEPOT"
                    },
                    {
                        "percent": 0.6,
                        "servicer": "BOKF"
                    },
                    {
                        "percent": 0.51,
                        "servicer": "JPM"
                    },
                    {
                        "percent": 0.48,
                        "servicer": "TRUIS"
                    },
                    {
                        "percent": 0.42,
                        "servicer": "CITI"
                    },
                    {
                        "percent": 0.38,
                        "servicer": "GUILD"
                    },
                    {
                        "percent": 0.21,
                        "servicer": "REGNS"
                    },
                    {
                        "percent": 0.2,
                        "servicer": "CNTRL"
                    },
                    {
                        "percent": 0.09,
                        "servicer": "COLNL"
                    },
                    {
                        "percent": 0.06,
                        "servicer": "HFAGY"
                    },
                    {
                        "percent": 0.06,
                        "servicer": "MNSRC"
                    },
                    {
                        "percent": 0.03,
                        "servicer": "HOMBR"
                    }
                ],
                "nonWeightedOriginalLoanSize": 0.0,
                "original3rdPartyOrigination": 0.0,
                "percentHARPDec2010Extension": 0.0,
                "percentHARPOneYearExtension": 0.0,
                "percentDownPaymentAssistance": 5.6,
                "percentAmortizedFHALTVUnder78": 95.4,
                "loanPerformanceImpliedCurrentLTV": 44.8,
                "reperformerMonthsForReperformers": 28
            },
            "ticker": "GNMA",
            "country": "US",
            "currency": "USD",
            "identifier": "999818YT",
            "description": "30-YR GNMA-2013 PROD",
            "issuerTicker": "GNMA",
            "maturityDate": "2041-12-01",
            "securityType": "MORT",
            "currentCoupon": 3.5,
            "securitySubType": "MPGNMA"
        },
        "meta": {
            "status": "DONE",
            "requestId": "R-20900",
            "timeStamp": "2025-08-18T22:33:09Z",
            "responseType": "BOND_INDIC"
        }
    }

    """

    try:
        logger.info("Calling get_result")

        response = Client().yield_book_rest.get_result(request_id_parameter=request_id_parameter, job=job)

        output = response
        logger.info("Called get_result")

        return output
    except Exception as err:
        logger.error("Error get_result.")
        check_exception_and_raise(err, logger)


def get_tba_pricing_sync(
    *,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Get tba-pricing sync.

    Parameters
    ----------
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling get_tba_pricing_sync")

        response = Client().yield_book_rest.get_tba_pricing_sync(job=job, name=name, pri=pri, tags=tags)

        output = response
        logger.info("Called get_tba_pricing_sync")

        return output
    except Exception as err:
        logger.error("Error get_tba_pricing_sync.")
        check_exception_and_raise(err, logger)


def post_cash_flow_async(
    *,
    global_settings: Optional[CashFlowGlobalSettings] = None,
    input: Optional[List[CashFlowInput]] = None,
    keywords: Optional[List[str]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Post cash flow request async.

    Parameters
    ----------
    global_settings : CashFlowGlobalSettings, optional

    input : List[CashFlowInput], optional

    keywords : List[str], optional
        Optional. Used to specify the keywords a user will retrieve in the response. All keywords are returned by default.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------
    >>> # post_cash_flow_async
    >>> global_settings = CashFlowGlobalSettings(
    >>>         )
    >>>
    >>> input = CashFlowInput(
    >>>             identifier="01F002628",
    >>>             par_amount="10000"
    >>>         )
    >>>
    >>> cf_async_post_response = post_cash_flow_async(
    >>>             global_settings=global_settings,
    >>>             input=[input]
    >>>         )
    >>>
    >>> cf_async_post_result = {}
    >>>
    >>> attempt = 1
    >>>
    >>> while attempt < 10:
    >>>
    >>>     try:
    >>>         time.sleep(10)
    >>>
    >>>         cf_async_post_result = get_result(request_id_parameter=cf_async_post_response.request_id)
    >>>
    >>>         break
    >>>
    >>>     except Exception as error:
    >>>         print(f"Attempt " + str(attempt) + " resulted in error retrieving results from:" + cf_async_post_response.request_id)
    >>>
    >>>         attempt+=1
    >>>
    >>> # Print output to a file, as CF output is too long for terminal printout
    >>> # print(js.dumps(cf_async_post_result, indent=4), file=open('.\\CF_async_post_output.json', 'w+'))
    >>>
    >>> # Print onyl payment information
    >>> for paymentInfo in cf_async_post_result["results"][0]["cashFlow"]["dataPaymentList"]:
    >>>     print(js.dumps(paymentInfo, indent=4))
    {
        "date": "2026-03-25",
        "totalCashFlow": 43240.102925,
        "interestPayment": 4166.666667,
        "principalBalance": 9960926.563741,
        "principalPayment": 39073.436259,
        "endPrincipalBalance": 9960926.563741,
        "beginPrincipalBalance": 10000000.0,
        "prepayPrincipalPayment": 14113.333241,
        "scheduledPrincipalPayment": 24960.103018
    }
    {
        "date": "2026-04-25",
        "totalCashFlow": 46525.285989,
        "interestPayment": 4150.386068,
        "principalBalance": 9918551.66382,
        "principalPayment": 42374.899921,
        "endPrincipalBalance": 9918551.66382,
        "beginPrincipalBalance": 9960926.563741,
        "prepayPrincipalPayment": 17424.148754,
        "scheduledPrincipalPayment": 24950.751166
    }
    {
        "date": "2026-05-25",
        "totalCashFlow": 48712.807936,
        "interestPayment": 4132.72986,
        "principalBalance": 9873971.585744,
        "principalPayment": 44580.078076,
        "endPrincipalBalance": 9873971.585744,
        "beginPrincipalBalance": 9918551.66382,
        "prepayPrincipalPayment": 19647.136818,
        "scheduledPrincipalPayment": 24932.941259
    }
    {
        "date": "2026-06-25",
        "totalCashFlow": 49212.075446,
        "interestPayment": 4114.154827,
        "principalBalance": 9828873.665125,
        "principalPayment": 45097.920619,
        "endPrincipalBalance": 9828873.665125,
        "beginPrincipalBalance": 9873971.585744,
        "prepayPrincipalPayment": 20188.571937,
        "scheduledPrincipalPayment": 24909.348682
    }
    {
        "date": "2026-07-25",
        "totalCashFlow": 51737.961794,
        "interestPayment": 4095.364027,
        "principalBalance": 9781231.067359,
        "principalPayment": 47642.597767,
        "endPrincipalBalance": 9781231.067359,
        "beginPrincipalBalance": 9828873.665125,
        "prepayPrincipalPayment": 22758.414125,
        "scheduledPrincipalPayment": 24884.183641
    }
    {
        "date": "2026-08-25",
        "totalCashFlow": 51667.218557,
        "interestPayment": 4075.512945,
        "principalBalance": 9733639.361746,
        "principalPayment": 47591.705612,
        "endPrincipalBalance": 9733639.361746,
        "beginPrincipalBalance": 9781231.067359,
        "prepayPrincipalPayment": 22739.425823,
        "scheduledPrincipalPayment": 24852.27979
    }
    {
        "date": "2026-09-25",
        "totalCashFlow": 50398.345822,
        "interestPayment": 4055.683067,
        "principalBalance": 9687296.698992,
        "principalPayment": 46342.662754,
        "endPrincipalBalance": 9687296.698992,
        "beginPrincipalBalance": 9733639.361746,
        "prepayPrincipalPayment": 21522.479314,
        "scheduledPrincipalPayment": 24820.18344
    }
    {
        "date": "2026-10-25",
        "totalCashFlow": 49757.462556,
        "interestPayment": 4036.373625,
        "principalBalance": 9641575.61006,
        "principalPayment": 45721.088932,
        "endPrincipalBalance": 9641575.61006,
        "beginPrincipalBalance": 9687296.698992,
        "prepayPrincipalPayment": 20930.129751,
        "scheduledPrincipalPayment": 24790.959181
    }
    {
        "date": "2026-11-25",
        "totalCashFlow": 48882.03192,
        "interestPayment": 4017.323171,
        "principalBalance": 9596710.901311,
        "principalPayment": 44864.708749,
        "endPrincipalBalance": 9596710.901311,
        "beginPrincipalBalance": 9641575.61006,
        "prepayPrincipalPayment": 20101.681738,
        "scheduledPrincipalPayment": 24763.02701
    }
    {
        "date": "2026-12-25",
        "totalCashFlow": 47270.138842,
        "interestPayment": 3998.629542,
        "principalBalance": 9553439.392012,
        "principalPayment": 43271.509299,
        "endPrincipalBalance": 9553439.392012,
        "beginPrincipalBalance": 9596710.901311,
        "prepayPrincipalPayment": 18534.502663,
        "scheduledPrincipalPayment": 24737.006636
    }
    {
        "date": "2027-01-25",
        "totalCashFlow": 48743.633434,
        "interestPayment": 3980.599747,
        "principalBalance": 9508676.358324,
        "principalPayment": 44763.033688,
        "endPrincipalBalance": 9508676.358324,
        "beginPrincipalBalance": 9553439.392012,
        "prepayPrincipalPayment": 20048.208245,
        "scheduledPrincipalPayment": 24714.825442
    }
    {
        "date": "2027-02-25",
        "totalCashFlow": 44132.795776,
        "interestPayment": 3961.948483,
        "principalBalance": 9468505.511031,
        "principalPayment": 40170.847293,
        "endPrincipalBalance": 9468505.511031,
        "beginPrincipalBalance": 9508676.358324,
        "prepayPrincipalPayment": 15482.330807,
        "scheduledPrincipalPayment": 24688.516486
    }
    {
        "date": "2027-03-25",
        "totalCashFlow": 44952.113459,
        "interestPayment": 3945.21063,
        "principalBalance": 9427498.608202,
        "principalPayment": 41006.902829,
        "endPrincipalBalance": 9427498.608202,
        "beginPrincipalBalance": 9468505.511031,
        "prepayPrincipalPayment": 16333.014398,
        "scheduledPrincipalPayment": 24673.888432
    }
    {
        "date": "2027-04-25",
        "totalCashFlow": 48717.535794,
        "interestPayment": 3928.12442,
        "principalBalance": 9382709.196828,
        "principalPayment": 44789.411374,
        "endPrincipalBalance": 9382709.196828,
        "beginPrincipalBalance": 9427498.608202,
        "prepayPrincipalPayment": 20132.538675,
        "scheduledPrincipalPayment": 24656.872699
    }
    {
        "date": "2027-05-25",
        "totalCashFlow": 50259.380717,
        "interestPayment": 3909.462165,
        "principalBalance": 9336359.278276,
        "principalPayment": 46349.918552,
        "endPrincipalBalance": 9336359.278276,
        "beginPrincipalBalance": 9382709.196828,
        "prepayPrincipalPayment": 21720.209733,
        "scheduledPrincipalPayment": 24629.708819
    }
    {
        "date": "2027-06-25",
        "totalCashFlow": 50404.111406,
        "interestPayment": 3890.149699,
        "principalBalance": 9289845.316569,
        "principalPayment": 46513.961707,
        "endPrincipalBalance": 9289845.316569,
        "beginPrincipalBalance": 9336359.278276,
        "prepayPrincipalPayment": 21915.822326,
        "scheduledPrincipalPayment": 24598.139381
    }
    {
        "date": "2027-07-25",
        "totalCashFlow": 52864.921712,
        "interestPayment": 3870.768882,
        "principalBalance": 9240851.163739,
        "principalPayment": 48994.15283,
        "endPrincipalBalance": 9240851.163739,
        "beginPrincipalBalance": 9289845.316569,
        "prepayPrincipalPayment": 24428.343979,
        "scheduledPrincipalPayment": 24565.808851
    }
    {
        "date": "2027-08-25",
        "totalCashFlow": 51614.130553,
        "interestPayment": 3850.354652,
        "principalBalance": 9193087.387838,
        "principalPayment": 47763.775901,
        "endPrincipalBalance": 9193087.387838,
        "beginPrincipalBalance": 9240851.163739,
        "prepayPrincipalPayment": 23237.21404,
        "scheduledPrincipalPayment": 24526.561861
    }
    {
        "date": "2027-09-25",
        "totalCashFlow": 51834.039123,
        "interestPayment": 3830.453078,
        "principalBalance": 9145083.801794,
        "principalPayment": 48003.586044,
        "endPrincipalBalance": 9145083.801794,
        "beginPrincipalBalance": 9193087.387838,
        "prepayPrincipalPayment": 23513.37917,
        "scheduledPrincipalPayment": 24490.206874
    }
    {
        "date": "2027-10-25",
        "totalCashFlow": 50332.989459,
        "interestPayment": 3810.451584,
        "principalBalance": 9098561.263919,
        "principalPayment": 46522.537875,
        "endPrincipalBalance": 9098561.263919,
        "beginPrincipalBalance": 9145083.801794,
        "prepayPrincipalPayment": 22069.692294,
        "scheduledPrincipalPayment": 24452.845581
    }
    {
        "date": "2027-11-25",
        "totalCashFlow": 48763.226545,
        "interestPayment": 3791.067193,
        "principalBalance": 9053589.104568,
        "principalPayment": 44972.159351,
        "endPrincipalBalance": 9053589.104568,
        "beginPrincipalBalance": 9098561.263919,
        "prepayPrincipalPayment": 20553.073587,
        "scheduledPrincipalPayment": 24419.085764
    }
    {
        "date": "2027-12-25",
        "totalCashFlow": 48590.414778,
        "interestPayment": 3772.328794,
        "principalBalance": 9008771.018584,
        "principalPayment": 44818.085984,
        "endPrincipalBalance": 9008771.018584,
        "beginPrincipalBalance": 9053589.104568,
        "prepayPrincipalPayment": 20428.930897,
        "scheduledPrincipalPayment": 24389.155088
    }
    {
        "date": "2028-01-25",
        "totalCashFlow": 48860.144183,
        "interestPayment": 3753.654591,
        "principalBalance": 8963664.528992,
        "principalPayment": 45106.489591,
        "endPrincipalBalance": 8963664.528992,
        "beginPrincipalBalance": 9008771.018584,
        "prepayPrincipalPayment": 20747.168067,
        "scheduledPrincipalPayment": 24359.321525
    }
    {
        "date": "2028-02-25",
        "totalCashFlow": 45091.584517,
        "interestPayment": 3734.86022,
        "principalBalance": 8922307.804696,
        "principalPayment": 41356.724296,
        "endPrincipalBalance": 8922307.804696,
        "beginPrincipalBalance": 8963664.528992,
        "prepayPrincipalPayment": 17028.338607,
        "scheduledPrincipalPayment": 24328.385689
    }
    {
        "date": "2028-03-25",
        "totalCashFlow": 46059.668455,
        "interestPayment": 3717.628252,
        "principalBalance": 8879965.764493,
        "principalPayment": 42342.040203,
        "endPrincipalBalance": 8879965.764493,
        "beginPrincipalBalance": 8922307.804696,
        "prepayPrincipalPayment": 18034.703309,
        "scheduledPrincipalPayment": 24307.336894
    }
    {
        "date": "2028-04-25",
        "totalCashFlow": 50023.616913,
        "interestPayment": 3699.985735,
        "principalBalance": 8833642.133316,
        "principalPayment": 46323.631178,
        "endPrincipalBalance": 8833642.133316,
        "beginPrincipalBalance": 8879965.764493,
        "prepayPrincipalPayment": 22040.292216,
        "scheduledPrincipalPayment": 24283.338962
    }
    {
        "date": "2028-05-25",
        "totalCashFlow": 49358.349604,
        "interestPayment": 3680.684222,
        "principalBalance": 8787964.467934,
        "principalPayment": 45677.665382,
        "endPrincipalBalance": 8787964.467934,
        "beginPrincipalBalance": 8833642.133316,
        "prepayPrincipalPayment": 21429.531344,
        "scheduledPrincipalPayment": 24248.134038
    }
    {
        "date": "2028-06-25",
        "totalCashFlow": 53490.274903,
        "interestPayment": 3661.651862,
        "principalBalance": 8738135.844892,
        "principalPayment": 49828.623042,
        "endPrincipalBalance": 8738135.844892,
        "beginPrincipalBalance": 8787964.467934,
        "prepayPrincipalPayment": 25614.277433,
        "scheduledPrincipalPayment": 24214.345608
    }
    {
        "date": "2028-07-25",
        "totalCashFlow": 54451.047812,
        "interestPayment": 3640.889935,
        "principalBalance": 8687325.687015,
        "principalPayment": 50810.157877,
        "endPrincipalBalance": 8687325.687015,
        "beginPrincipalBalance": 8738135.844892,
        "prepayPrincipalPayment": 26641.435266,
        "scheduledPrincipalPayment": 24168.722611
    }
    {
        "date": "2028-08-25",
        "totalCashFlow": 52122.889362,
        "interestPayment": 3619.719036,
        "principalBalance": 8638822.516689,
        "principalPayment": 48503.170326,
        "endPrincipalBalance": 8638822.516689,
        "beginPrincipalBalance": 8687325.687015,
        "prepayPrincipalPayment": 24383.240589,
        "scheduledPrincipalPayment": 24119.929738
    }
    {
        "date": "2028-09-25",
        "totalCashFlow": 54212.911945,
        "interestPayment": 3599.509382,
        "principalBalance": 8588209.114126,
        "principalPayment": 50613.402563,
        "endPrincipalBalance": 8588209.114126,
        "beginPrincipalBalance": 8638822.516689,
        "prepayPrincipalPayment": 26536.305961,
        "scheduledPrincipalPayment": 24077.096602
    }
    {
        "date": "2028-10-25",
        "totalCashFlow": 50634.241212,
        "interestPayment": 3578.420464,
        "principalBalance": 8541153.293378,
        "principalPayment": 47055.820748,
        "endPrincipalBalance": 8541153.293378,
        "beginPrincipalBalance": 8588209.114126,
        "prepayPrincipalPayment": 23027.886628,
        "scheduledPrincipalPayment": 24027.93412
    }
    {
        "date": "2028-11-25",
        "totalCashFlow": 50526.503693,
        "interestPayment": 3558.813872,
        "principalBalance": 8494185.603558,
        "principalPayment": 46967.68982,
        "endPrincipalBalance": 8494185.603558,
        "beginPrincipalBalance": 8541153.293378,
        "prepayPrincipalPayment": 22979.40166,
        "scheduledPrincipalPayment": 23988.288161
    }
    {
        "date": "2028-12-25",
        "totalCashFlow": 49443.760337,
        "interestPayment": 3539.244001,
        "principalBalance": 8448281.087222,
        "principalPayment": 45904.516336,
        "endPrincipalBalance": 8448281.087222,
        "beginPrincipalBalance": 8494185.603558,
        "prepayPrincipalPayment": 21956.028448,
        "scheduledPrincipalPayment": 23948.487887
    }
    {
        "date": "2029-01-25",
        "totalCashFlow": 48864.189905,
        "interestPayment": 3520.11712,
        "principalBalance": 8402937.014437,
        "principalPayment": 45344.072785,
        "endPrincipalBalance": 8402937.014437,
        "beginPrincipalBalance": 8448281.087222,
        "prepayPrincipalPayment": 21432.78102,
        "scheduledPrincipalPayment": 23911.291765
    }
    {
        "date": "2029-02-25",
        "totalCashFlow": 46103.869307,
        "interestPayment": 3501.223756,
        "principalBalance": 8360334.368886,
        "principalPayment": 42602.645551,
        "endPrincipalBalance": 8360334.368886,
        "beginPrincipalBalance": 8402937.014437,
        "prepayPrincipalPayment": 18727.343246,
        "scheduledPrincipalPayment": 23875.302305
    }
    {
        "date": "2029-03-25",
        "totalCashFlow": 45798.432977,
        "interestPayment": 3483.472654,
        "principalBalance": 8318019.408563,
        "principalPayment": 42314.960323,
        "endPrincipalBalance": 8318019.408563,
        "beginPrincipalBalance": 8360334.368886,
        "prepayPrincipalPayment": 18468.205198,
        "scheduledPrincipalPayment": 23846.755126
    }
    {
        "date": "2029-04-25",
        "totalCashFlow": 49682.462983,
        "interestPayment": 3465.84142,
        "principalBalance": 8271802.787,
        "principalPayment": 46216.621563,
        "endPrincipalBalance": 8271802.787,
        "beginPrincipalBalance": 8318019.408563,
        "prepayPrincipalPayment": 22397.909913,
        "scheduledPrincipalPayment": 23818.71165
    }
    {
        "date": "2029-05-25",
        "totalCashFlow": 51530.569551,
        "interestPayment": 3446.584495,
        "principalBalance": 8223718.801943,
        "principalPayment": 48083.985057,
        "endPrincipalBalance": 8223718.801943,
        "beginPrincipalBalance": 8271802.787,
        "prepayPrincipalPayment": 24304.850017,
        "scheduledPrincipalPayment": 23779.135039
    }
    {
        "date": "2029-06-25",
        "totalCashFlow": 54720.498394,
        "interestPayment": 3426.549501,
        "principalBalance": 8172424.85305,
        "principalPayment": 51293.948893,
        "endPrincipalBalance": 8172424.85305,
        "beginPrincipalBalance": 8223718.801943,
        "prepayPrincipalPayment": 27560.188039,
        "scheduledPrincipalPayment": 23733.760854
    }
    {
        "date": "2029-07-25",
        "totalCashFlow": 54516.415883,
        "interestPayment": 3405.177022,
        "principalBalance": 8121313.614189,
        "principalPayment": 51111.238861,
        "endPrincipalBalance": 8121313.614189,
        "beginPrincipalBalance": 8172424.85305,
        "prepayPrincipalPayment": 27432.607713,
        "scheduledPrincipalPayment": 23678.631147
    }
    {
        "date": "2029-08-25",
        "totalCashFlow": 53965.10817,
        "interestPayment": 3383.880673,
        "principalBalance": 8070732.386692,
        "principalPayment": 50581.227497,
        "endPrincipalBalance": 8070732.386692,
        "beginPrincipalBalance": 8121313.614189,
        "prepayPrincipalPayment": 26957.72783,
        "scheduledPrincipalPayment": 23623.499667
    }
    {
        "date": "2029-09-25",
        "totalCashFlow": 55024.239624,
        "interestPayment": 3362.805161,
        "principalBalance": 8019070.952228,
        "principalPayment": 51661.434463,
        "endPrincipalBalance": 8019070.952228,
        "beginPrincipalBalance": 8070732.386692,
        "prepayPrincipalPayment": 28092.053045,
        "scheduledPrincipalPayment": 23569.381418
    }
    {
        "date": "2029-10-25",
        "totalCashFlow": 50013.075696,
        "interestPayment": 3341.279563,
        "principalBalance": 7972399.156095,
        "principalPayment": 46671.796133,
        "endPrincipalBalance": 7972399.156095,
        "beginPrincipalBalance": 8019070.952228,
        "prepayPrincipalPayment": 23160.227957,
        "scheduledPrincipalPayment": 23511.568176
    }
    {
        "date": "2029-11-25",
        "totalCashFlow": 51638.915542,
        "interestPayment": 3321.832982,
        "principalBalance": 7924082.073535,
        "principalPayment": 48317.082561,
        "endPrincipalBalance": 7924082.073535,
        "beginPrincipalBalance": 7972399.156095,
        "prepayPrincipalPayment": 24849.198573,
        "scheduledPrincipalPayment": 23467.883988
    }
    {
        "date": "2029-12-25",
        "totalCashFlow": 49457.453825,
        "interestPayment": 3301.700864,
        "principalBalance": 7877926.320574,
        "principalPayment": 46155.752961,
        "endPrincipalBalance": 7877926.320574,
        "beginPrincipalBalance": 7924082.073535,
        "prepayPrincipalPayment": 22736.862764,
        "scheduledPrincipalPayment": 23418.890197
    }
    {
        "date": "2030-01-25",
        "totalCashFlow": 48730.207454,
        "interestPayment": 3282.4693,
        "principalBalance": 7832478.582419,
        "principalPayment": 45447.738154,
        "endPrincipalBalance": 7832478.582419,
        "beginPrincipalBalance": 7877926.320574,
        "prepayPrincipalPayment": 22071.919357,
        "scheduledPrincipalPayment": 23375.818797
    }
    {
        "date": "2030-02-25",
        "totalCashFlow": 45761.832171,
        "interestPayment": 3263.532743,
        "principalBalance": 7789980.282991,
        "principalPayment": 42498.299428,
        "endPrincipalBalance": 7789980.282991,
        "beginPrincipalBalance": 7832478.582419,
        "prepayPrincipalPayment": 19163.887178,
        "scheduledPrincipalPayment": 23334.41225
    }
    {
        "date": "2030-03-25",
        "totalCashFlow": 45343.540324,
        "interestPayment": 3245.825118,
        "principalBalance": 7747882.567786,
        "principalPayment": 42097.715206,
        "endPrincipalBalance": 7747882.567786,
        "beginPrincipalBalance": 7789980.282991,
        "prepayPrincipalPayment": 18796.319312,
        "scheduledPrincipalPayment": 23301.395894
    }
    {
        "date": "2030-04-25",
        "totalCashFlow": 48905.852954,
        "interestPayment": 3228.284403,
        "principalBalance": 7702204.999235,
        "principalPayment": 45677.56855,
        "endPrincipalBalance": 7702204.999235,
        "beginPrincipalBalance": 7747882.567786,
        "prepayPrincipalPayment": 22408.351359,
        "scheduledPrincipalPayment": 23269.217192
    }
    {
        "date": "2030-05-25",
        "totalCashFlow": 51651.372428,
        "interestPayment": 3209.252083,
        "principalBalance": 7653762.87889,
        "principalPayment": 48442.120345,
        "endPrincipalBalance": 7653762.87889,
        "beginPrincipalBalance": 7702204.999235,
        "prepayPrincipalPayment": 25216.236434,
        "scheduledPrincipalPayment": 23225.883911
    }
    {
        "date": "2030-06-25",
        "totalCashFlow": 54367.252657,
        "interestPayment": 3189.067866,
        "principalBalance": 7602584.694099,
        "principalPayment": 51178.184791,
        "endPrincipalBalance": 7602584.694099,
        "beginPrincipalBalance": 7653762.87889,
        "prepayPrincipalPayment": 28004.455869,
        "scheduledPrincipalPayment": 23173.728921
    }
    {
        "date": "2030-07-25",
        "totalCashFlow": 53022.4596,
        "interestPayment": 3167.743623,
        "principalBalance": 7552729.978122,
        "principalPayment": 49854.715977,
        "endPrincipalBalance": 7552729.978122,
        "beginPrincipalBalance": 7602584.694099,
        "prepayPrincipalPayment": 26741.98452,
        "scheduledPrincipalPayment": 23112.731457
    }
    {
        "date": "2030-08-25",
        "totalCashFlow": 54735.527373,
        "interestPayment": 3146.970824,
        "principalBalance": 7501141.421573,
        "principalPayment": 51588.556549,
        "endPrincipalBalance": 7501141.421573,
        "beginPrincipalBalance": 7552729.978122,
        "prepayPrincipalPayment": 28533.380893,
        "scheduledPrincipalPayment": 23055.175656
    }
    {
        "date": "2030-09-25",
        "totalCashFlow": 53683.341855,
        "interestPayment": 3125.475592,
        "principalBalance": 7450583.555311,
        "principalPayment": 50557.866262,
        "endPrincipalBalance": 7450583.555311,
        "beginPrincipalBalance": 7501141.421573,
        "prepayPrincipalPayment": 27566.132408,
        "scheduledPrincipalPayment": 22991.733854
    }
    {
        "date": "2030-10-25",
        "totalCashFlow": 50556.776602,
        "interestPayment": 3104.409815,
        "principalBalance": 7403131.188524,
        "principalPayment": 47452.366787,
        "endPrincipalBalance": 7403131.188524,
        "beginPrincipalBalance": 7450583.555311,
        "prepayPrincipalPayment": 24521.524168,
        "scheduledPrincipalPayment": 22930.84262
    }
    {
        "date": "2030-11-25",
        "totalCashFlow": 51238.256481,
        "interestPayment": 3084.637995,
        "principalBalance": 7354977.570038,
        "principalPayment": 48153.618486,
        "endPrincipalBalance": 7354977.570038,
        "beginPrincipalBalance": 7403131.188524,
        "prepayPrincipalPayment": 25274.671917,
        "scheduledPrincipalPayment": 22878.946569
    }
    {
        "date": "2030-12-25",
        "totalCashFlow": 48030.303667,
        "interestPayment": 3064.573988,
        "principalBalance": 7310011.840358,
        "principalPayment": 44965.72968,
        "endPrincipalBalance": 7310011.840358,
        "beginPrincipalBalance": 7354977.570038,
        "prepayPrincipalPayment": 22141.384538,
        "scheduledPrincipalPayment": 22824.345142
    }
    {
        "date": "2031-01-25",
        "totalCashFlow": 49119.137794,
        "interestPayment": 3045.838267,
        "principalBalance": 7263938.540831,
        "principalPayment": 46073.299527,
        "endPrincipalBalance": 7263938.540831,
        "beginPrincipalBalance": 7310011.840358,
        "prepayPrincipalPayment": 23294.174995,
        "scheduledPrincipalPayment": 22779.124531
    }
    {
        "date": "2031-02-25",
        "totalCashFlow": 45056.369989,
        "interestPayment": 3026.641059,
        "principalBalance": 7221908.811901,
        "principalPayment": 42029.728931,
        "endPrincipalBalance": 7221908.811901,
        "beginPrincipalBalance": 7263938.540831,
        "prepayPrincipalPayment": 19299.767139,
        "scheduledPrincipalPayment": 22729.961791
    }
    {
        "date": "2031-03-25",
        "totalCashFlow": 44575.81083,
        "interestPayment": 3009.128672,
        "principalBalance": 7180342.129742,
        "principalPayment": 41566.682158,
        "endPrincipalBalance": 7180342.129742,
        "beginPrincipalBalance": 7221908.811901,
        "prepayPrincipalPayment": 18873.687887,
        "scheduledPrincipalPayment": 22692.994272
    }
    {
        "date": "2031-04-25",
        "totalCashFlow": 48230.977805,
        "interestPayment": 2991.809221,
        "principalBalance": 7135102.961158,
        "principalPayment": 45239.168584,
        "endPrincipalBalance": 7135102.961158,
        "beginPrincipalBalance": 7180342.129742,
        "prepayPrincipalPayment": 22582.090408,
        "scheduledPrincipalPayment": 22657.078177
    }
    {
        "date": "2031-05-25",
        "totalCashFlow": 51044.970602,
        "interestPayment": 2972.959567,
        "principalBalance": 7087030.950123,
        "principalPayment": 48072.011035,
        "endPrincipalBalance": 7087030.950123,
        "beginPrincipalBalance": 7135102.961158,
        "prepayPrincipalPayment": 25462.887992,
        "scheduledPrincipalPayment": 22609.123043
    }
    {
        "date": "2031-06-25",
        "totalCashFlow": 52698.165462,
        "interestPayment": 2952.929563,
        "principalBalance": 7037285.714223,
        "principalPayment": 49745.2359,
        "endPrincipalBalance": 7037285.714223,
        "beginPrincipalBalance": 7087030.950123,
        "prepayPrincipalPayment": 27193.58717,
        "scheduledPrincipalPayment": 22551.64873
    }
    {
        "date": "2031-07-25",
        "totalCashFlow": 53566.042314,
        "interestPayment": 2932.202381,
        "principalBalance": 6986651.87429,
        "principalPayment": 50633.839933,
        "endPrincipalBalance": 6986651.87429,
        "beginPrincipalBalance": 7037285.714223,
        "prepayPrincipalPayment": 28145.599306,
        "scheduledPrincipalPayment": 22488.240627
    }
    {
        "date": "2031-08-25",
        "totalCashFlow": 54079.589714,
        "interestPayment": 2911.104948,
        "principalBalance": 6935483.389524,
        "principalPayment": 51168.484767,
        "endPrincipalBalance": 6935483.389524,
        "beginPrincipalBalance": 6986651.87429,
        "prepayPrincipalPayment": 28747.142855,
        "scheduledPrincipalPayment": 22421.341912
    }
    {
        "date": "2031-09-25",
        "totalCashFlow": 51839.685154,
        "interestPayment": 2889.784746,
        "principalBalance": 6886533.489116,
        "principalPayment": 48949.900408,
        "endPrincipalBalance": 6886533.489116,
        "beginPrincipalBalance": 6935483.389524,
        "prepayPrincipalPayment": 26597.850773,
        "scheduledPrincipalPayment": 22352.049635
    }
    {
        "date": "2031-10-25",
        "totalCashFlow": 50713.051089,
        "interestPayment": 2869.388954,
        "principalBalance": 6838689.82698,
        "principalPayment": 47843.662135,
        "endPrincipalBalance": 6838689.82698,
        "beginPrincipalBalance": 6886533.489116,
        "prepayPrincipalPayment": 25554.416843,
        "scheduledPrincipalPayment": 22289.245292
    }
    {
        "date": "2031-11-25",
        "totalCashFlow": 50296.938159,
        "interestPayment": 2849.454095,
        "principalBalance": 6791242.342916,
        "principalPayment": 47447.484064,
        "endPrincipalBalance": 6791242.342916,
        "beginPrincipalBalance": 6838689.82698,
        "prepayPrincipalPayment": 25218.086323,
        "scheduledPrincipalPayment": 22229.397741
    }
    {
        "date": "2031-12-25",
        "totalCashFlow": 46013.709933,
        "interestPayment": 2829.68431,
        "principalBalance": 6748058.317293,
        "principalPayment": 43184.025623,
        "endPrincipalBalance": 6748058.317293,
        "beginPrincipalBalance": 6791242.342916,
        "prepayPrincipalPayment": 21013.797511,
        "scheduledPrincipalPayment": 22170.228113
    }
    {
        "date": "2032-01-25",
        "totalCashFlow": 48960.734385,
        "interestPayment": 2811.690966,
        "principalBalance": 6701909.273873,
        "principalPayment": 46149.04342,
        "endPrincipalBalance": 6701909.273873,
        "beginPrincipalBalance": 6748058.317293,
        "prepayPrincipalPayment": 24024.617908,
        "scheduledPrincipalPayment": 22124.425512
    }
    {
        "date": "2032-02-25",
        "totalCashFlow": 43117.465396,
        "interestPayment": 2792.462197,
        "principalBalance": 6661584.270674,
        "principalPayment": 40325.003199,
        "endPrincipalBalance": 6661584.270674,
        "beginPrincipalBalance": 6701909.273873,
        "prepayPrincipalPayment": 18256.640803,
        "scheduledPrincipalPayment": 22068.362396
    }
    {
        "date": "2032-03-25",
        "totalCashFlow": 43328.440831,
        "interestPayment": 2775.660113,
        "principalBalance": 6621031.489956,
        "principalPayment": 40552.780718,
        "endPrincipalBalance": 6621031.489956,
        "beginPrincipalBalance": 6661584.270674,
        "prepayPrincipalPayment": 18521.808207,
        "scheduledPrincipalPayment": 22030.972511
    }
    {
        "date": "2032-04-25",
        "totalCashFlow": 48343.702661,
        "interestPayment": 2758.763121,
        "principalBalance": 6575446.550415,
        "principalPayment": 45584.93954,
        "endPrincipalBalance": 6575446.550415,
        "beginPrincipalBalance": 6621031.489956,
        "prepayPrincipalPayment": 23592.540086,
        "scheduledPrincipalPayment": 21992.399455
    }
    {
        "date": "2032-05-25",
        "totalCashFlow": 50329.941026,
        "interestPayment": 2739.769396,
        "principalBalance": 6527856.378786,
        "principalPayment": 47590.17163,
        "endPrincipalBalance": 6527856.378786,
        "beginPrincipalBalance": 6575446.550415,
        "prepayPrincipalPayment": 25653.571406,
        "scheduledPrincipalPayment": 21936.600223
    }
    {
        "date": "2032-06-25",
        "totalCashFlow": 50337.994489,
        "interestPayment": 2719.940158,
        "principalBalance": 6480238.324454,
        "principalPayment": 47618.054332,
        "endPrincipalBalance": 6480238.324454,
        "beginPrincipalBalance": 6527856.378786,
        "prepayPrincipalPayment": 25744.563273,
        "scheduledPrincipalPayment": 21873.491058
    }
    {
        "date": "2032-07-25",
        "totalCashFlow": 53506.618977,
        "interestPayment": 2700.099302,
        "principalBalance": 6429431.804779,
        "principalPayment": 50806.519675,
        "endPrincipalBalance": 6429431.804779,
        "beginPrincipalBalance": 6480238.324454,
        "prepayPrincipalPayment": 28996.888603,
        "scheduledPrincipalPayment": 21809.631072
    }
    {
        "date": "2032-08-25",
        "totalCashFlow": 51619.849886,
        "interestPayment": 2678.929919,
        "principalBalance": 6380490.884812,
        "principalPayment": 48940.919967,
        "endPrincipalBalance": 6380490.884812,
        "beginPrincipalBalance": 6429431.804779,
        "prepayPrincipalPayment": 27206.592856,
        "scheduledPrincipalPayment": 21734.327111
    }
    {
        "date": "2032-09-25",
        "totalCashFlow": 51558.956426,
        "interestPayment": 2658.537869,
        "principalBalance": 6331590.466255,
        "principalPayment": 48900.418557,
        "endPrincipalBalance": 6331590.466255,
        "beginPrincipalBalance": 6380490.884812,
        "prepayPrincipalPayment": 27235.829938,
        "scheduledPrincipalPayment": 21664.588619
    }
    {
        "date": "2032-10-25",
        "totalCashFlow": 49279.257658,
        "interestPayment": 2638.162694,
        "principalBalance": 6284949.371291,
        "principalPayment": 46641.094963,
        "endPrincipalBalance": 6284949.371291,
        "beginPrincipalBalance": 6331590.466255,
        "prepayPrincipalPayment": 25046.828485,
        "scheduledPrincipalPayment": 21594.266479
    }
    {
        "date": "2032-11-25",
        "totalCashFlow": 46896.42984,
        "interestPayment": 2618.728905,
        "principalBalance": 6240671.670356,
        "principalPayment": 44277.700935,
        "endPrincipalBalance": 6240671.670356,
        "beginPrincipalBalance": 6284949.371291,
        "prepayPrincipalPayment": 22746.745757,
        "scheduledPrincipalPayment": 21530.955178
    }
    {
        "date": "2032-12-25",
        "totalCashFlow": 46428.656327,
        "interestPayment": 2600.279863,
        "principalBalance": 6196843.293892,
        "principalPayment": 43828.376464,
        "endPrincipalBalance": 6196843.293892,
        "beginPrincipalBalance": 6240671.670356,
        "prepayPrincipalPayment": 22353.268248,
        "scheduledPrincipalPayment": 21475.108216
    }
    {
        "date": "2033-01-25",
        "totalCashFlow": 46471.346264,
        "interestPayment": 2582.018039,
        "principalBalance": 6152953.965667,
        "principalPayment": 43889.328225,
        "endPrincipalBalance": 6152953.965667,
        "beginPrincipalBalance": 6196843.293892,
        "prepayPrincipalPayment": 22469.117142,
        "scheduledPrincipalPayment": 21420.211083
    }
    {
        "date": "2033-02-25",
        "totalCashFlow": 41532.531414,
        "interestPayment": 2563.730819,
        "principalBalance": 6113985.165072,
        "principalPayment": 38968.800595,
        "endPrincipalBalance": 6113985.165072,
        "beginPrincipalBalance": 6152953.965667,
        "prepayPrincipalPayment": 17604.294861,
        "scheduledPrincipalPayment": 21364.505735
    }
    {
        "date": "2033-03-25",
        "totalCashFlow": 41716.758299,
        "interestPayment": 2547.493819,
        "principalBalance": 6074815.900591,
        "principalPayment": 39169.264481,
        "endPrincipalBalance": 6074815.900591,
        "beginPrincipalBalance": 6113985.165072,
        "prepayPrincipalPayment": 17843.907191,
        "scheduledPrincipalPayment": 21325.35729
    }
    {
        "date": "2033-04-25",
        "totalCashFlow": 47123.92888,
        "interestPayment": 2531.173292,
        "principalBalance": 6030223.145003,
        "principalPayment": 44592.755588,
        "endPrincipalBalance": 6030223.145003,
        "beginPrincipalBalance": 6074815.900591,
        "prepayPrincipalPayment": 23307.706188,
        "scheduledPrincipalPayment": 21285.0494
    }
    {
        "date": "2033-05-25",
        "totalCashFlow": 47126.584901,
        "interestPayment": 2512.592977,
        "principalBalance": 5985609.153079,
        "principalPayment": 44613.991924,
        "endPrincipalBalance": 5985609.153079,
        "beginPrincipalBalance": 6030223.145003,
        "prepayPrincipalPayment": 23388.809075,
        "scheduledPrincipalPayment": 21225.182849
    }
    {
        "date": "2033-06-25",
        "totalCashFlow": 49739.130562,
        "interestPayment": 2494.003814,
        "principalBalance": 5938364.02633,
        "principalPayment": 47245.126749,
        "endPrincipalBalance": 5938364.02633,
        "beginPrincipalBalance": 5985609.153079,
        "prepayPrincipalPayment": 26080.535122,
        "scheduledPrincipalPayment": 21164.591627
    }
    {
        "date": "2033-07-25",
        "totalCashFlow": 51726.070624,
        "interestPayment": 2474.318344,
        "principalBalance": 5889112.27405,
        "principalPayment": 49251.75228,
        "endPrincipalBalance": 5889112.27405,
        "beginPrincipalBalance": 5938364.02633,
        "prepayPrincipalPayment": 28157.756335,
        "scheduledPrincipalPayment": 21093.995945
    }
    {
        "date": "2033-08-25",
        "totalCashFlow": 48679.523222,
        "interestPayment": 2453.796781,
        "principalBalance": 5842886.547609,
        "principalPayment": 46225.726441,
        "endPrincipalBalance": 5842886.547609,
        "beginPrincipalBalance": 5889112.27405,
        "prepayPrincipalPayment": 25210.239445,
        "scheduledPrincipalPayment": 21015.486996
    }
    {
        "date": "2033-09-25",
        "totalCashFlow": 50799.38027,
        "interestPayment": 2434.536062,
        "principalBalance": 5794521.703401,
        "principalPayment": 48364.844208,
        "endPrincipalBalance": 5794521.703401,
        "beginPrincipalBalance": 5842886.547609,
        "prepayPrincipalPayment": 27417.845867,
        "scheduledPrincipalPayment": 20946.998341
    }
    {
        "date": "2033-10-25",
        "totalCashFlow": 47413.541394,
        "interestPayment": 2414.384043,
        "principalBalance": 5749522.54605,
        "principalPayment": 44999.157351,
        "endPrincipalBalance": 5749522.54605,
        "beginPrincipalBalance": 5794521.703401,
        "prepayPrincipalPayment": 24129.089786,
        "scheduledPrincipalPayment": 20870.067565
    }
    {
        "date": "2033-11-25",
        "totalCashFlow": 45035.554016,
        "interestPayment": 2395.634394,
        "principalBalance": 5706882.626428,
        "principalPayment": 42639.919622,
        "endPrincipalBalance": 5706882.626428,
        "beginPrincipalBalance": 5749522.54605,
        "prepayPrincipalPayment": 21835.422883,
        "scheduledPrincipalPayment": 20804.496739
    }
    {
        "date": "2033-12-25",
        "totalCashFlow": 44560.694913,
        "interestPayment": 2377.867761,
        "principalBalance": 5664699.799276,
        "principalPayment": 42182.827152,
        "endPrincipalBalance": 5664699.799276,
        "beginPrincipalBalance": 5706882.626428,
        "prepayPrincipalPayment": 21436.039507,
        "scheduledPrincipalPayment": 20746.787645
    }
    {
        "date": "2034-01-25",
        "totalCashFlow": 44579.282921,
        "interestPayment": 2360.291583,
        "principalBalance": 5622480.807939,
        "principalPayment": 42218.991337,
        "endPrincipalBalance": 5622480.807939,
        "beginPrincipalBalance": 5664699.799276,
        "prepayPrincipalPayment": 21528.886789,
        "scheduledPrincipalPayment": 20690.104548
    }
    {
        "date": "2034-02-25",
        "totalCashFlow": 39696.216446,
        "interestPayment": 2342.700337,
        "principalBalance": 5585127.291829,
        "principalPayment": 37353.51611,
        "endPrincipalBalance": 5585127.291829,
        "beginPrincipalBalance": 5622480.807939,
        "prepayPrincipalPayment": 16720.863293,
        "scheduledPrincipalPayment": 20632.652817
    }
    {
        "date": "2034-03-25",
        "totalCashFlow": 39982.107978,
        "interestPayment": 2327.136372,
        "principalBalance": 5547472.320223,
        "principalPayment": 37654.971607,
        "endPrincipalBalance": 5547472.320223,
        "beginPrincipalBalance": 5585127.291829,
        "prepayPrincipalPayment": 17062.476657,
        "scheduledPrincipalPayment": 20592.494949
    }
    {
        "date": "2034-04-25",
        "totalCashFlow": 45444.51209,
        "interestPayment": 2311.4468,
        "principalBalance": 5504339.254932,
        "principalPayment": 43133.06529,
        "endPrincipalBalance": 5504339.254932,
        "beginPrincipalBalance": 5547472.320223,
        "prepayPrincipalPayment": 22582.328157,
        "scheduledPrincipalPayment": 20550.737133
    }
    {
        "date": "2034-05-25",
        "totalCashFlow": 45091.013024,
        "interestPayment": 2293.47469,
        "principalBalance": 5461541.716598,
        "principalPayment": 42797.538335,
        "endPrincipalBalance": 5461541.716598,
        "beginPrincipalBalance": 5504339.254932,
        "prepayPrincipalPayment": 22309.449459,
        "scheduledPrincipalPayment": 20488.088876
    }
    {
        "date": "2034-06-25",
        "totalCashFlow": 49451.227253,
        "interestPayment": 2275.642382,
        "principalBalance": 5414366.131727,
        "principalPayment": 47175.584871,
        "endPrincipalBalance": 5414366.131727,
        "beginPrincipalBalance": 5461541.716598,
        "prepayPrincipalPayment": 26749.590874,
        "scheduledPrincipalPayment": 20425.993997
    }
    {
        "date": "2034-07-25",
        "totalCashFlow": 50460.734362,
        "interestPayment": 2255.985888,
        "principalBalance": 5366161.383253,
        "principalPayment": 48204.748474,
        "endPrincipalBalance": 5366161.383253,
        "beginPrincipalBalance": 5414366.131727,
        "prepayPrincipalPayment": 27858.00019,
        "scheduledPrincipalPayment": 20346.748284
    }
    {
        "date": "2034-08-25",
        "totalCashFlow": 47535.237805,
        "interestPayment": 2235.900576,
        "principalBalance": 5320862.046024,
        "principalPayment": 45299.337229,
        "endPrincipalBalance": 5320862.046024,
        "beginPrincipalBalance": 5366161.383253,
        "prepayPrincipalPayment": 25036.586873,
        "scheduledPrincipalPayment": 20262.750356
    }
    {
        "date": "2034-09-25",
        "totalCashFlow": 49798.374966,
        "interestPayment": 2217.025853,
        "principalBalance": 5273280.69691,
        "principalPayment": 47581.349114,
        "endPrincipalBalance": 5273280.69691,
        "beginPrincipalBalance": 5320862.046024,
        "prepayPrincipalPayment": 27392.487646,
        "scheduledPrincipalPayment": 20188.861468
    }
    {
        "date": "2034-10-25",
        "totalCashFlow": 45462.428272,
        "interestPayment": 2197.20029,
        "principalBalance": 5230015.468929,
        "principalPayment": 43265.227982,
        "endPrincipalBalance": 5230015.468929,
        "beginPrincipalBalance": 5273280.69691,
        "prepayPrincipalPayment": 23159.775865,
        "scheduledPrincipalPayment": 20105.452117
    }
    {
        "date": "2034-11-25",
        "totalCashFlow": 45142.142227,
        "interestPayment": 2179.173112,
        "principalBalance": 5187052.499814,
        "principalPayment": 42962.969115,
        "endPrincipalBalance": 5187052.499814,
        "beginPrincipalBalance": 5230015.468929,
        "prepayPrincipalPayment": 22925.305449,
        "scheduledPrincipalPayment": 20037.663666
    }
    {
        "date": "2034-12-25",
        "totalCashFlow": 43795.139435,
        "interestPayment": 2161.271875,
        "principalBalance": 5145418.632253,
        "principalPayment": 41633.86756,
        "endPrincipalBalance": 5145418.632253,
        "beginPrincipalBalance": 5187052.499814,
        "prepayPrincipalPayment": 21663.594289,
        "scheduledPrincipalPayment": 19970.273271
    }
    {
        "date": "2035-01-25",
        "totalCashFlow": 42973.543419,
        "interestPayment": 2143.92443,
        "principalBalance": 5104589.013264,
        "principalPayment": 40829.618989,
        "endPrincipalBalance": 5104589.013264,
        "beginPrincipalBalance": 5145418.632253,
        "prepayPrincipalPayment": 20922.358264,
        "scheduledPrincipalPayment": 19907.260725
    }
    {
        "date": "2035-02-25",
        "totalCashFlow": 39724.252466,
        "interestPayment": 2126.912089,
        "principalBalance": 5066991.672887,
        "principalPayment": 37597.340377,
        "endPrincipalBalance": 5066991.672887,
        "beginPrincipalBalance": 5104589.013264,
        "prepayPrincipalPayment": 17750.689089,
        "scheduledPrincipalPayment": 19846.651288
    }
    {
        "date": "2035-03-25",
        "totalCashFlow": 39254.199039,
        "interestPayment": 2111.24653,
        "principalBalance": 5029848.720379,
        "principalPayment": 37142.952508,
        "endPrincipalBalance": 5029848.720379,
        "beginPrincipalBalance": 5066991.672887,
        "prepayPrincipalPayment": 17344.983884,
        "scheduledPrincipalPayment": 19797.968625
    }
    {
        "date": "2035-04-25",
        "totalCashFlow": 43444.953704,
        "interestPayment": 2095.7703,
        "principalBalance": 4988499.536975,
        "principalPayment": 41349.183404,
        "endPrincipalBalance": 4988499.536975,
        "beginPrincipalBalance": 5029848.720379,
        "prepayPrincipalPayment": 21598.699674,
        "scheduledPrincipalPayment": 19750.48373
    }
    {
        "date": "2035-05-25",
        "totalCashFlow": 45408.239694,
        "interestPayment": 2078.541474,
        "principalBalance": 4945169.838755,
        "principalPayment": 43329.69822,
        "endPrincipalBalance": 4945169.838755,
        "beginPrincipalBalance": 4988499.536975,
        "prepayPrincipalPayment": 23643.874752,
        "scheduledPrincipalPayment": 19685.823467
    }
    {
        "date": "2035-06-25",
        "totalCashFlow": 48749.315864,
        "interestPayment": 2060.487433,
        "principalBalance": 4898481.010324,
        "principalPayment": 46688.828431,
        "endPrincipalBalance": 4898481.010324,
        "beginPrincipalBalance": 4945169.838755,
        "prepayPrincipalPayment": 27076.270573,
        "scheduledPrincipalPayment": 19612.557858
    }
    {
        "date": "2035-07-25",
        "totalCashFlow": 48483.379891,
        "interestPayment": 2041.033754,
        "principalBalance": 4852038.664187,
        "principalPayment": 46442.346137,
        "endPrincipalBalance": 4852038.664187,
        "beginPrincipalBalance": 4898481.010324,
        "prepayPrincipalPayment": 26917.282986,
        "scheduledPrincipalPayment": 19525.063151
    }
    {
        "date": "2035-08-25",
        "totalCashFlow": 47817.051327,
        "interestPayment": 2021.682777,
        "principalBalance": 4806243.295637,
        "principalPayment": 45795.36855,
        "endPrincipalBalance": 4806243.295637,
        "beginPrincipalBalance": 4852038.664187,
        "prepayPrincipalPayment": 26357.799106,
        "scheduledPrincipalPayment": 19437.569444
    }
    {
        "date": "2035-09-25",
        "totalCashFlow": 48847.447408,
        "interestPayment": 2002.601373,
        "principalBalance": 4759398.449601,
        "principalPayment": 46844.846035,
        "endPrincipalBalance": 4759398.449601,
        "beginPrincipalBalance": 4806243.295637,
        "prepayPrincipalPayment": 27493.155248,
        "scheduledPrincipalPayment": 19351.690787
    }
    {
        "date": "2035-10-25",
        "totalCashFlow": 43375.42713,
        "interestPayment": 1983.082687,
        "principalBalance": 4718006.105159,
        "principalPayment": 41392.344442,
        "endPrincipalBalance": 4718006.105159,
        "beginPrincipalBalance": 4759398.449601,
        "prepayPrincipalPayment": 22131.756414,
        "scheduledPrincipalPayment": 19260.588028
    }
    {
        "date": "2035-11-25",
        "totalCashFlow": 44988.733907,
        "interestPayment": 1965.835877,
        "principalBalance": 4674983.207129,
        "principalPayment": 43022.89803,
        "endPrincipalBalance": 4674983.207129,
        "beginPrincipalBalance": 4718006.105159,
        "prepayPrincipalPayment": 23832.268464,
        "scheduledPrincipalPayment": 19190.629566
    }
    {
        "date": "2035-12-25",
        "totalCashFlow": 42622.154548,
        "interestPayment": 1947.90967,
        "principalBalance": 4634308.962251,
        "principalPayment": 40674.244878,
        "endPrincipalBalance": 4634308.962251,
        "beginPrincipalBalance": 4674983.207129,
        "prepayPrincipalPayment": 21561.060831,
        "scheduledPrincipalPayment": 19113.184047
    }
    {
        "date": "2036-01-25",
        "totalCashFlow": 41741.136678,
        "interestPayment": 1930.962068,
        "principalBalance": 4594498.78764,
        "principalPayment": 39810.174611,
        "endPrincipalBalance": 4594498.78764,
        "beginPrincipalBalance": 4634308.962251,
        "prepayPrincipalPayment": 20765.68523,
        "scheduledPrincipalPayment": 19044.48938
    }
    {
        "date": "2036-02-25",
        "totalCashFlow": 38460.524851,
        "interestPayment": 1914.374495,
        "principalBalance": 4557952.637285,
        "principalPayment": 36546.150356,
        "endPrincipalBalance": 4557952.637285,
        "beginPrincipalBalance": 4594498.78764,
        "prepayPrincipalPayment": 17567.600027,
        "scheduledPrincipalPayment": 18978.550329
    }
    {
        "date": "2036-03-25",
        "totalCashFlow": 38716.150694,
        "interestPayment": 1899.146932,
        "principalBalance": 4521135.633523,
        "principalPayment": 36817.003762,
        "endPrincipalBalance": 4521135.633523,
        "beginPrincipalBalance": 4557952.637285,
        "prepayPrincipalPayment": 17891.627701,
        "scheduledPrincipalPayment": 18925.37606
    }
    {
        "date": "2036-04-25",
        "totalCashFlow": 41580.832562,
        "interestPayment": 1883.806514,
        "principalBalance": 4481438.607475,
        "principalPayment": 39697.026048,
        "endPrincipalBalance": 4481438.607475,
        "beginPrincipalBalance": 4521135.633523,
        "prepayPrincipalPayment": 20826.612516,
        "scheduledPrincipalPayment": 18870.413532
    }
    {
        "date": "2036-05-25",
        "totalCashFlow": 44422.485524,
        "interestPayment": 1867.266086,
        "principalBalance": 4438883.388038,
        "principalPayment": 42555.219437,
        "endPrincipalBalance": 4438883.388038,
        "beginPrincipalBalance": 4481438.607475,
        "prepayPrincipalPayment": 23752.531055,
        "scheduledPrincipalPayment": 18802.688383
    }
    {
        "date": "2036-06-25",
        "totalCashFlow": 46050.883204,
        "interestPayment": 1849.534745,
        "principalBalance": 4394682.039579,
        "principalPayment": 44201.348459,
        "endPrincipalBalance": 4394682.039579,
        "beginPrincipalBalance": 4438883.388038,
        "prepayPrincipalPayment": 25479.256137,
        "scheduledPrincipalPayment": 18722.092322
    }
    {
        "date": "2036-07-25",
        "totalCashFlow": 46864.0773,
        "interestPayment": 1831.117516,
        "principalBalance": 4349649.079795,
        "principalPayment": 45032.959784,
        "endPrincipalBalance": 4349649.079795,
        "beginPrincipalBalance": 4394682.039579,
        "prepayPrincipalPayment": 26399.397966,
        "scheduledPrincipalPayment": 18633.561818
    }
    {
        "date": "2036-08-25",
        "totalCashFlow": 47287.297728,
        "interestPayment": 1812.353783,
        "principalBalance": 4304174.13585,
        "principalPayment": 45474.943945,
        "endPrincipalBalance": 4304174.13585,
        "beginPrincipalBalance": 4349649.079795,
        "prepayPrincipalPayment": 26934.499993,
        "scheduledPrincipalPayment": 18540.443951
    }
    {
        "date": "2036-09-25",
        "totalCashFlow": 44940.360976,
        "interestPayment": 1793.40589,
        "principalBalance": 4261027.180764,
        "principalPayment": 43146.955086,
        "endPrincipalBalance": 4261027.180764,
        "beginPrincipalBalance": 4304174.13585,
        "prepayPrincipalPayment": 24702.618453,
        "scheduledPrincipalPayment": 18444.336634
    }
    {
        "date": "2036-10-25",
        "totalCashFlow": 43748.395585,
        "interestPayment": 1775.427992,
        "principalBalance": 4219054.21317,
        "principalPayment": 41972.967593,
        "endPrincipalBalance": 4219054.21317,
        "beginPrincipalBalance": 4261027.180764,
        "prepayPrincipalPayment": 23615.840595,
        "scheduledPrincipalPayment": 18357.126999
    }
    {
        "date": "2036-11-25",
        "totalCashFlow": 43206.70855,
        "interestPayment": 1757.939255,
        "principalBalance": 4177605.443876,
        "principalPayment": 41448.769294,
        "endPrincipalBalance": 4177605.443876,
        "beginPrincipalBalance": 4219054.21317,
        "prepayPrincipalPayment": 23174.807424,
        "scheduledPrincipalPayment": 18273.96187
    }
    {
        "date": "2036-12-25",
        "totalCashFlow": 39006.126143,
        "interestPayment": 1740.668935,
        "principalBalance": 4140339.986668,
        "principalPayment": 37265.457208,
        "endPrincipalBalance": 4140339.986668,
        "beginPrincipalBalance": 4177605.443876,
        "prepayPrincipalPayment": 19073.37852,
        "scheduledPrincipalPayment": 18192.078688
    }
    {
        "date": "2037-01-25",
        "totalCashFlow": 41754.749319,
        "interestPayment": 1725.141661,
        "principalBalance": 4100310.379011,
        "principalPayment": 40029.607658,
        "endPrincipalBalance": 4100310.379011,
        "beginPrincipalBalance": 4140339.986668,
        "prepayPrincipalPayment": 21902.087261,
        "scheduledPrincipalPayment": 18127.520397
    }
    {
        "date": "2037-02-25",
        "totalCashFlow": 36050.686313,
        "interestPayment": 1708.462658,
        "principalBalance": 4065968.155355,
        "principalPayment": 34342.223655,
        "endPrincipalBalance": 4065968.155355,
        "beginPrincipalBalance": 4100310.379011,
        "prepayPrincipalPayment": 16292.235665,
        "scheduledPrincipalPayment": 18049.98799
    }
    {
        "date": "2037-03-25",
        "totalCashFlow": 36214.400713,
        "interestPayment": 1694.153398,
        "principalBalance": 4031447.908041,
        "principalPayment": 34520.247315,
        "endPrincipalBalance": 4031447.908041,
        "beginPrincipalBalance": 4065968.155355,
        "prepayPrincipalPayment": 16523.569505,
        "scheduledPrincipalPayment": 17996.67781
    }
    {
        "date": "2037-04-25",
        "totalCashFlow": 40527.71527,
        "interestPayment": 1679.769962,
        "principalBalance": 3992599.962732,
        "principalPayment": 38847.945308,
        "endPrincipalBalance": 3992599.962732,
        "beginPrincipalBalance": 4031447.908041,
        "prepayPrincipalPayment": 20906.058809,
        "scheduledPrincipalPayment": 17941.8865
    }
    {
        "date": "2037-05-25",
        "totalCashFlow": 42850.180168,
        "interestPayment": 1663.583318,
        "principalBalance": 3951413.365881,
        "principalPayment": 41186.596851,
        "endPrincipalBalance": 3951413.365881,
        "beginPrincipalBalance": 3992599.962732,
        "prepayPrincipalPayment": 23319.57621,
        "scheduledPrincipalPayment": 17867.020641
    }
    {
        "date": "2037-06-25",
        "totalCashFlow": 42819.868823,
        "interestPayment": 1646.422236,
        "principalBalance": 3910239.919294,
        "principalPayment": 41173.446587,
        "endPrincipalBalance": 3910239.919294,
        "beginPrincipalBalance": 3951413.365881,
        "prepayPrincipalPayment": 23392.748652,
        "scheduledPrincipalPayment": 17780.697936
    }
    {
        "date": "2037-07-25",
        "totalCashFlow": 45750.271249,
        "interestPayment": 1629.266633,
        "principalBalance": 3866118.914678,
        "principalPayment": 44121.004616,
        "endPrincipalBalance": 3866118.914678,
        "beginPrincipalBalance": 3910239.919294,
        "prepayPrincipalPayment": 26427.634523,
        "scheduledPrincipalPayment": 17693.370093
    }
    {
        "date": "2037-08-25",
        "totalCashFlow": 44939.863185,
        "interestPayment": 1610.882881,
        "principalBalance": 3822789.934374,
        "principalPayment": 43328.980304,
        "endPrincipalBalance": 3822789.934374,
        "beginPrincipalBalance": 3866118.914678,
        "prepayPrincipalPayment": 25737.430201,
        "scheduledPrincipalPayment": 17591.550103
    }
    {
        "date": "2037-09-25",
        "totalCashFlow": 42643.126396,
        "interestPayment": 1592.829139,
        "principalBalance": 3781739.637117,
        "principalPayment": 41050.297257,
        "endPrincipalBalance": 3781739.637117,
        "beginPrincipalBalance": 3822789.934374,
        "prepayPrincipalPayment": 23558.190505,
        "scheduledPrincipalPayment": 17492.106752
    }
    {
        "date": "2037-10-25",
        "totalCashFlow": 41464.889299,
        "interestPayment": 1575.724849,
        "principalBalance": 3741850.472667,
        "principalPayment": 39889.16445,
        "endPrincipalBalance": 3741850.472667,
        "beginPrincipalBalance": 3781739.637117,
        "prepayPrincipalPayment": 22487.241313,
        "scheduledPrincipalPayment": 17401.923137
    }
    {
        "date": "2037-11-25",
        "totalCashFlow": 40022.923218,
        "interestPayment": 1559.104364,
        "principalBalance": 3703386.653812,
        "principalPayment": 38463.818855,
        "endPrincipalBalance": 3703386.653812,
        "beginPrincipalBalance": 3741850.472667,
        "prepayPrincipalPayment": 21147.831873,
        "scheduledPrincipalPayment": 17315.986982
    }
    {
        "date": "2037-12-25",
        "totalCashFlow": 37773.533213,
        "interestPayment": 1543.077772,
        "principalBalance": 3667156.198372,
        "principalPayment": 36230.45544,
        "endPrincipalBalance": 3667156.198372,
        "beginPrincipalBalance": 3703386.653812,
        "prepayPrincipalPayment": 18994.853214,
        "scheduledPrincipalPayment": 17235.602226
    }
    {
        "date": "2038-01-25",
        "totalCashFlow": 39450.92825,
        "interestPayment": 1527.981749,
        "principalBalance": 3629233.251871,
        "principalPayment": 37922.946501,
        "endPrincipalBalance": 3629233.251871,
        "beginPrincipalBalance": 3667156.198372,
        "prepayPrincipalPayment": 20758.298643,
        "scheduledPrincipalPayment": 17164.647858
    }
    {
        "date": "2038-02-25",
        "totalCashFlow": 33368.78178,
        "interestPayment": 1512.180522,
        "principalBalance": 3597376.650613,
        "principalPayment": 31856.601258,
        "endPrincipalBalance": 3597376.650613,
        "beginPrincipalBalance": 3629233.251871,
        "prepayPrincipalPayment": 14771.794345,
        "scheduledPrincipalPayment": 17084.806914
    }
    {
        "date": "2038-03-25",
        "totalCashFlow": 34149.173318,
        "interestPayment": 1498.906938,
        "principalBalance": 3564726.384233,
        "principalPayment": 32650.26638,
        "endPrincipalBalance": 3564726.384233,
        "beginPrincipalBalance": 3597376.650613,
        "prepayPrincipalPayment": 15617.60348,
        "scheduledPrincipalPayment": 17032.662901
    }
    {
        "date": "2038-04-25",
        "totalCashFlow": 38977.169449,
        "interestPayment": 1485.30266,
        "principalBalance": 3527234.517444,
        "principalPayment": 37491.866789,
        "endPrincipalBalance": 3527234.517444,
        "beginPrincipalBalance": 3564726.384233,
        "prepayPrincipalPayment": 20515.83608,
        "scheduledPrincipalPayment": 16976.030709
    }
    {
        "date": "2038-05-25",
        "totalCashFlow": 39876.104124,
        "interestPayment": 1469.681049,
        "principalBalance": 3488828.094369,
        "principalPayment": 38406.423075,
        "endPrincipalBalance": 3488828.094369,
        "beginPrincipalBalance": 3527234.517444,
        "prepayPrincipalPayment": 21510.979796,
        "scheduledPrincipalPayment": 16895.443278
    }
    {
        "date": "2038-06-25",
        "totalCashFlow": 40266.167431,
        "interestPayment": 1453.678373,
        "principalBalance": 3450015.605311,
        "principalPayment": 38812.489058,
        "endPrincipalBalance": 3450015.605311,
        "beginPrincipalBalance": 3488828.094369,
        "prepayPrincipalPayment": 22003.087664,
        "scheduledPrincipalPayment": 16809.401394
    }
    {
        "date": "2038-07-25",
        "totalCashFlow": 42980.979507,
        "interestPayment": 1437.506502,
        "principalBalance": 3408472.132307,
        "principalPayment": 41543.473004,
        "endPrincipalBalance": 3408472.132307,
        "beginPrincipalBalance": 3450015.605311,
        "prepayPrincipalPayment": 24823.19834,
        "scheduledPrincipalPayment": 16720.274664
    }
    {
        "date": "2038-08-25",
        "totalCashFlow": 41168.586846,
        "interestPayment": 1420.196722,
        "principalBalance": 3368723.742182,
        "principalPayment": 39748.390124,
        "endPrincipalBalance": 3368723.742182,
        "beginPrincipalBalance": 3408472.132307,
        "prepayPrincipalPayment": 23131.714324,
        "scheduledPrincipalPayment": 16616.6758
    }
    {
        "date": "2038-09-25",
        "totalCashFlow": 40949.848397,
        "interestPayment": 1403.634893,
        "principalBalance": 3329177.528678,
        "principalPayment": 39546.213504,
        "endPrincipalBalance": 3329177.528678,
        "beginPrincipalBalance": 3368723.742182,
        "prepayPrincipalPayment": 23025.668815,
        "scheduledPrincipalPayment": 16520.544689
    }
    {
        "date": "2038-10-25",
        "totalCashFlow": 38836.244437,
        "interestPayment": 1387.157304,
        "principalBalance": 3291728.441544,
        "principalPayment": 37449.087134,
        "endPrincipalBalance": 3291728.441544,
        "beginPrincipalBalance": 3329177.528678,
        "prepayPrincipalPayment": 21024.92834,
        "scheduledPrincipalPayment": 16424.158794
    }
    {
        "date": "2038-11-25",
        "totalCashFlow": 36631.289714,
        "interestPayment": 1371.553517,
        "principalBalance": 3256468.705348,
        "principalPayment": 35259.736197,
        "endPrincipalBalance": 3256468.705348,
        "beginPrincipalBalance": 3291728.441544,
        "prepayPrincipalPayment": 18922.816082,
        "scheduledPrincipalPayment": 16336.920115
    }
    {
        "date": "2038-12-25",
        "totalCashFlow": 36154.194884,
        "interestPayment": 1356.861961,
        "principalBalance": 3221671.372424,
        "principalPayment": 34797.332924,
        "endPrincipalBalance": 3221671.372424,
        "beginPrincipalBalance": 3256468.705348,
        "prepayPrincipalPayment": 18537.876272,
        "scheduledPrincipalPayment": 16259.456651
    }
    {
        "date": "2039-01-25",
        "totalCashFlow": 36069.971954,
        "interestPayment": 1342.363072,
        "principalBalance": 3186943.763542,
        "principalPayment": 34727.608882,
        "endPrincipalBalance": 3186943.763542,
        "beginPrincipalBalance": 3221671.372424,
        "prepayPrincipalPayment": 18544.335755,
        "scheduledPrincipalPayment": 16183.273127
    }
    {
        "date": "2039-02-25",
        "totalCashFlow": 31781.406695,
        "interestPayment": 1327.893235,
        "principalBalance": 3156490.250082,
        "principalPayment": 30453.51346,
        "endPrincipalBalance": 3156490.250082,
        "beginPrincipalBalance": 3186943.763542,
        "prepayPrincipalPayment": 14347.10348,
        "scheduledPrincipalPayment": 16106.40998
    }
    {
        "date": "2039-03-25",
        "totalCashFlow": 31892.820585,
        "interestPayment": 1315.204271,
        "principalBalance": 3125912.633768,
        "principalPayment": 30577.616314,
        "endPrincipalBalance": 3125912.633768,
        "beginPrincipalBalance": 3156490.250082,
        "prepayPrincipalPayment": 14527.38149,
        "scheduledPrincipalPayment": 16050.234824
    }
    {
        "date": "2039-04-25",
        "totalCashFlow": 36359.880339,
        "interestPayment": 1302.463597,
        "principalBalance": 3090855.217027,
        "principalPayment": 35057.416741,
        "endPrincipalBalance": 3090855.217027,
        "beginPrincipalBalance": 3125912.633768,
        "prepayPrincipalPayment": 19064.787147,
        "scheduledPrincipalPayment": 15992.629594
    }
    {
        "date": "2039-05-25",
        "totalCashFlow": 36357.868051,
        "interestPayment": 1287.85634,
        "principalBalance": 3055785.205317,
        "principalPayment": 35070.011711,
        "endPrincipalBalance": 3055785.205317,
        "beginPrincipalBalance": 3090855.217027,
        "prepayPrincipalPayment": 19158.865098,
        "scheduledPrincipalPayment": 15911.146612
    }
    {
        "date": "2039-06-25",
        "totalCashFlow": 38478.956215,
        "interestPayment": 1273.243836,
        "principalBalance": 3018579.492937,
        "principalPayment": 37205.712379,
        "endPrincipalBalance": 3018579.492937,
        "beginPrincipalBalance": 3055785.205317,
        "prepayPrincipalPayment": 21377.231527,
        "scheduledPrincipalPayment": 15828.480853
    }
    {
        "date": "2039-07-25",
        "totalCashFlow": 40042.901245,
        "interestPayment": 1257.741455,
        "principalBalance": 2979794.333148,
        "principalPayment": 38785.15979,
        "endPrincipalBalance": 2979794.333148,
        "beginPrincipalBalance": 3018579.492937,
        "prepayPrincipalPayment": 23051.614091,
        "scheduledPrincipalPayment": 15733.545699
    }
    {
        "date": "2039-08-25",
        "totalCashFlow": 37418.147193,
        "interestPayment": 1241.580972,
        "principalBalance": 2943617.766926,
        "principalPayment": 36176.566221,
        "endPrincipalBalance": 2943617.766926,
        "beginPrincipalBalance": 2979794.333148,
        "prepayPrincipalPayment": 20547.537188,
        "scheduledPrincipalPayment": 15629.029033
    }
    {
        "date": "2039-09-25",
        "totalCashFlow": 39022.136406,
        "interestPayment": 1226.507403,
        "principalBalance": 2905822.137923,
        "principalPayment": 37795.629004,
        "endPrincipalBalance": 2905822.137923,
        "beginPrincipalBalance": 2943617.766926,
        "prepayPrincipalPayment": 22258.772716,
        "scheduledPrincipalPayment": 15536.856287
    }
    {
        "date": "2039-10-25",
        "totalCashFlow": 36159.709427,
        "interestPayment": 1210.759224,
        "principalBalance": 2870873.18772,
        "principalPayment": 34948.950203,
        "endPrincipalBalance": 2870873.18772,
        "beginPrincipalBalance": 2905822.137923,
        "prepayPrincipalPayment": 19514.141257,
        "scheduledPrincipalPayment": 15434.808946
    }
    {
        "date": "2039-11-25",
        "totalCashFlow": 34103.673156,
        "interestPayment": 1196.197162,
        "principalBalance": 2837965.711726,
        "principalPayment": 32907.475994,
        "endPrincipalBalance": 2837965.711726,
        "beginPrincipalBalance": 2870873.18772,
        "prepayPrincipalPayment": 17560.904134,
        "scheduledPrincipalPayment": 15346.57186
    }
    {
        "date": "2039-12-25",
        "totalCashFlow": 33646.840683,
        "interestPayment": 1182.485713,
        "principalBalance": 2805501.356756,
        "principalPayment": 32464.35497,
        "endPrincipalBalance": 2805501.356756,
        "beginPrincipalBalance": 2837965.711726,
        "prepayPrincipalPayment": 17196.273684,
        "scheduledPrincipalPayment": 15268.081286
    }
    {
        "date": "2040-01-25",
        "totalCashFlow": 33547.017347,
        "interestPayment": 1168.958899,
        "principalBalance": 2773123.298308,
        "principalPayment": 32378.058448,
        "endPrincipalBalance": 2773123.298308,
        "beginPrincipalBalance": 2805501.356756,
        "prepayPrincipalPayment": 17187.185115,
        "scheduledPrincipalPayment": 15190.873333
    }
    {
        "date": "2040-02-25",
        "totalCashFlow": 29601.916925,
        "interestPayment": 1155.468041,
        "principalBalance": 2744676.849424,
        "principalPayment": 28446.448884,
        "endPrincipalBalance": 2744676.849424,
        "beginPrincipalBalance": 2773123.298308,
        "prepayPrincipalPayment": 13333.418835,
        "scheduledPrincipalPayment": 15113.030049
    }
    {
        "date": "2040-03-25",
        "totalCashFlow": 30267.269444,
        "interestPayment": 1143.615354,
        "principalBalance": 2715553.195334,
        "principalPayment": 29123.65409,
        "endPrincipalBalance": 2715553.195334,
        "beginPrincipalBalance": 2744676.849424,
        "prepayPrincipalPayment": 14068.020355,
        "scheduledPrincipalPayment": 15055.633734
    }
    {
        "date": "2040-04-25",
        "totalCashFlow": 32713.670347,
        "interestPayment": 1131.480498,
        "principalBalance": 2683971.005485,
        "principalPayment": 31582.189849,
        "endPrincipalBalance": 2683971.005485,
        "beginPrincipalBalance": 2715553.195334,
        "prepayPrincipalPayment": 16588.548259,
        "scheduledPrincipalPayment": 14993.64159
    }
    {
        "date": "2040-05-25",
        "totalCashFlow": 34077.116898,
        "interestPayment": 1118.321252,
        "principalBalance": 2651012.209839,
        "principalPayment": 32958.795645,
        "endPrincipalBalance": 2651012.209839,
        "beginPrincipalBalance": 2683971.005485,
        "prepayPrincipalPayment": 18041.732065,
        "scheduledPrincipalPayment": 14917.06358
    }
    {
        "date": "2040-06-25",
        "totalCashFlow": 36429.695317,
        "interestPayment": 1104.588421,
        "principalBalance": 2615687.102943,
        "principalPayment": 35325.106896,
        "endPrincipalBalance": 2615687.102943,
        "beginPrincipalBalance": 2651012.209839,
        "prepayPrincipalPayment": 20493.443099,
        "scheduledPrincipalPayment": 14831.663798
    }
    {
        "date": "2040-07-25",
        "totalCashFlow": 36067.227276,
        "interestPayment": 1089.869626,
        "principalBalance": 2580709.745293,
        "principalPayment": 34977.35765,
        "endPrincipalBalance": 2580709.745293,
        "beginPrincipalBalance": 2615687.102943,
        "prepayPrincipalPayment": 20245.664398,
        "scheduledPrincipalPayment": 14731.693252
    }
    {
        "date": "2040-08-25",
        "totalCashFlow": 35398.172053,
        "interestPayment": 1075.295727,
        "principalBalance": 2546386.868968,
        "principalPayment": 34322.876326,
        "endPrincipalBalance": 2546386.868968,
        "beginPrincipalBalance": 2580709.745293,
        "prepayPrincipalPayment": 19690.627531,
        "scheduledPrincipalPayment": 14632.248794
    }
    {
        "date": "2040-09-25",
        "totalCashFlow": 35956.807875,
        "interestPayment": 1060.994529,
        "principalBalance": 2511491.055622,
        "principalPayment": 34895.813346,
        "endPrincipalBalance": 2511491.055622,
        "beginPrincipalBalance": 2546386.868968,
        "prepayPrincipalPayment": 20360.719186,
        "scheduledPrincipalPayment": 14535.09416
    }
    {
        "date": "2040-10-25",
        "totalCashFlow": 31830.123939,
        "interestPayment": 1046.454607,
        "principalBalance": 2480707.386289,
        "principalPayment": 30783.669333,
        "endPrincipalBalance": 2480707.386289,
        "beginPrincipalBalance": 2511491.055622,
        "prepayPrincipalPayment": 16350.444952,
        "scheduledPrincipalPayment": 14433.224381
    }
    {
        "date": "2040-11-25",
        "totalCashFlow": 32815.802359,
        "interestPayment": 1033.628078,
        "principalBalance": 2448925.212008,
        "principalPayment": 31782.174281,
        "endPrincipalBalance": 2448925.212008,
        "beginPrincipalBalance": 2480707.386289,
        "prepayPrincipalPayment": 17428.520815,
        "scheduledPrincipalPayment": 14353.653466
    }
    {
        "date": "2040-12-25",
        "totalCashFlow": 30997.524237,
        "interestPayment": 1020.385505,
        "principalBalance": 2418948.073276,
        "principalPayment": 29977.138732,
        "endPrincipalBalance": 2418948.073276,
        "beginPrincipalBalance": 2448925.212008,
        "prepayPrincipalPayment": 15710.069479,
        "scheduledPrincipalPayment": 14267.069253
    }
    {
        "date": "2041-01-25",
        "totalCashFlow": 30232.634645,
        "interestPayment": 1007.895031,
        "principalBalance": 2389723.333662,
        "principalPayment": 29224.739615,
        "endPrincipalBalance": 2389723.333662,
        "beginPrincipalBalance": 2418948.073276,
        "prepayPrincipalPayment": 15034.965558,
        "scheduledPrincipalPayment": 14189.774056
    }
    {
        "date": "2041-02-25",
        "totalCashFlow": 27797.515588,
        "interestPayment": 995.718056,
        "principalBalance": 2362921.536129,
        "principalPayment": 26801.797533,
        "endPrincipalBalance": 2362921.536129,
        "beginPrincipalBalance": 2389723.333662,
        "prepayPrincipalPayment": 12686.051801,
        "scheduledPrincipalPayment": 14115.745732
    }
    {
        "date": "2041-03-25",
        "totalCashFlow": 27347.155821,
        "interestPayment": 984.55064,
        "principalBalance": 2336558.930948,
        "principalPayment": 26362.605181,
        "endPrincipalBalance": 2336558.930948,
        "beginPrincipalBalance": 2362921.536129,
        "prepayPrincipalPayment": 12307.613976,
        "scheduledPrincipalPayment": 14054.991205
    }
    {
        "date": "2041-04-25",
        "totalCashFlow": 29746.940035,
        "interestPayment": 973.566221,
        "principalBalance": 2307785.557134,
        "principalPayment": 28773.373814,
        "endPrincipalBalance": 2307785.557134,
        "beginPrincipalBalance": 2336558.930948,
        "prepayPrincipalPayment": 14777.464189,
        "scheduledPrincipalPayment": 13995.909625
    }
    {
        "date": "2041-05-25",
        "totalCashFlow": 31585.391852,
        "interestPayment": 961.577315,
        "principalBalance": 2277161.742598,
        "principalPayment": 30623.814536,
        "endPrincipalBalance": 2277161.742598,
        "beginPrincipalBalance": 2307785.557134,
        "prepayPrincipalPayment": 16702.46852,
        "scheduledPrincipalPayment": 13921.346017
    }
    {
        "date": "2041-06-25",
        "totalCashFlow": 33309.672079,
        "interestPayment": 948.817393,
        "principalBalance": 2244800.887912,
        "principalPayment": 32360.854686,
        "endPrincipalBalance": 2244800.887912,
        "beginPrincipalBalance": 2277161.742598,
        "prepayPrincipalPayment": 18526.479295,
        "scheduledPrincipalPayment": 13834.375391
    }
    {
        "date": "2041-07-25",
        "totalCashFlow": 32145.593043,
        "interestPayment": 935.333703,
        "principalBalance": 2213590.628572,
        "principalPayment": 31210.259339,
        "endPrincipalBalance": 2213590.628572,
        "beginPrincipalBalance": 2244800.887912,
        "prepayPrincipalPayment": 17474.83246,
        "scheduledPrincipalPayment": 13735.426879
    }
    {
        "date": "2041-08-25",
        "totalCashFlow": 33062.86634,
        "interestPayment": 922.329429,
        "principalBalance": 2181450.091661,
        "principalPayment": 32140.536911,
        "endPrincipalBalance": 2181450.091661,
        "beginPrincipalBalance": 2213590.628572,
        "prepayPrincipalPayment": 18498.497168,
        "scheduledPrincipalPayment": 13642.039744
    }
    {
        "date": "2041-09-25",
        "totalCashFlow": 32038.59487,
        "interestPayment": 908.937538,
        "principalBalance": 2150320.434329,
        "principalPayment": 31129.657332,
        "endPrincipalBalance": 2150320.434329,
        "beginPrincipalBalance": 2181450.091661,
        "prepayPrincipalPayment": 17588.237134,
        "scheduledPrincipalPayment": 13541.420198
    }
    {
        "date": "2041-10-25",
        "totalCashFlow": 29719.56796,
        "interestPayment": 895.966848,
        "principalBalance": 2121496.833217,
        "principalPayment": 28823.601112,
        "endPrincipalBalance": 2121496.833217,
        "beginPrincipalBalance": 2150320.434329,
        "prepayPrincipalPayment": 15378.051213,
        "scheduledPrincipalPayment": 13445.549899
    }
    {
        "date": "2041-11-25",
        "totalCashFlow": 29879.438934,
        "interestPayment": 883.957014,
        "principalBalance": 2092501.351297,
        "principalPayment": 28995.48192,
        "endPrincipalBalance": 2092501.351297,
        "beginPrincipalBalance": 2121496.833217,
        "prepayPrincipalPayment": 15632.788128,
        "scheduledPrincipalPayment": 13362.693792
    }
    {
        "date": "2041-12-25",
        "totalCashFlow": 27640.078237,
        "interestPayment": 871.875563,
        "principalBalance": 2065733.148623,
        "principalPayment": 26768.202674,
        "endPrincipalBalance": 2065733.148623,
        "beginPrincipalBalance": 2092501.351297,
        "prepayPrincipalPayment": 13490.783174,
        "scheduledPrincipalPayment": 13277.419501
    }
    {
        "date": "2042-01-25",
        "totalCashFlow": 28100.736751,
        "interestPayment": 860.722145,
        "principalBalance": 2038493.134017,
        "principalPayment": 27240.014606,
        "endPrincipalBalance": 2038493.134017,
        "beginPrincipalBalance": 2065733.148623,
        "prepayPrincipalPayment": 14035.003066,
        "scheduledPrincipalPayment": 13205.01154
    }
    {
        "date": "2042-02-25",
        "totalCashFlow": 25351.089324,
        "interestPayment": 849.372139,
        "principalBalance": 2013991.416832,
        "principalPayment": 24501.717185,
        "endPrincipalBalance": 2013991.416832,
        "beginPrincipalBalance": 2038493.134017,
        "prepayPrincipalPayment": 11373.339165,
        "scheduledPrincipalPayment": 13128.37802
    }
    {
        "date": "2042-03-25",
        "totalCashFlow": 24928.628397,
        "interestPayment": 839.16309,
        "principalBalance": 1989901.951525,
        "principalPayment": 24089.465307,
        "endPrincipalBalance": 1989901.951525,
        "beginPrincipalBalance": 2013991.416832,
        "prepayPrincipalPayment": 11021.210467,
        "scheduledPrincipalPayment": 13068.25484
    }
    {
        "date": "2042-04-25",
        "totalCashFlow": 27004.194757,
        "interestPayment": 829.125813,
        "principalBalance": 1963726.882581,
        "principalPayment": 26175.068944,
        "endPrincipalBalance": 1963726.882581,
        "beginPrincipalBalance": 1989901.951525,
        "prepayPrincipalPayment": 13165.257087,
        "scheduledPrincipalPayment": 13009.811857
    }
    {
        "date": "2042-05-25",
        "totalCashFlow": 28878.794295,
        "interestPayment": 818.219534,
        "principalBalance": 1935666.307821,
        "principalPayment": 28060.574761,
        "endPrincipalBalance": 1935666.307821,
        "beginPrincipalBalance": 1963726.882581,
        "prepayPrincipalPayment": 15123.941055,
        "scheduledPrincipalPayment": 12936.633705
    }
    {
        "date": "2042-06-25",
        "totalCashFlow": 29389.496558,
        "interestPayment": 806.527628,
        "principalBalance": 1907083.338891,
        "principalPayment": 28582.96893,
        "endPrincipalBalance": 1907083.338891,
        "beginPrincipalBalance": 1935666.307821,
        "prepayPrincipalPayment": 15733.258206,
        "scheduledPrincipalPayment": 12849.710724
    }
    {
        "date": "2042-07-25",
        "totalCashFlow": 29693.792698,
        "interestPayment": 794.618058,
        "principalBalance": 1878184.164251,
        "principalPayment": 28899.174641,
        "endPrincipalBalance": 1878184.164251,
        "beginPrincipalBalance": 1907083.338891,
        "prepayPrincipalPayment": 16141.329821,
        "scheduledPrincipalPayment": 12757.844819
    }
    {
        "date": "2042-08-25",
        "totalCashFlow": 29747.748473,
        "interestPayment": 782.576735,
        "principalBalance": 1849218.992512,
        "principalPayment": 28965.171738,
        "endPrincipalBalance": 1849218.992512,
        "beginPrincipalBalance": 1878184.164251,
        "prepayPrincipalPayment": 16302.858864,
        "scheduledPrincipalPayment": 12662.312874
    }
    {
        "date": "2042-09-25",
        "totalCashFlow": 28200.53265,
        "interestPayment": 770.507914,
        "principalBalance": 1821788.967776,
        "principalPayment": 27430.024737,
        "endPrincipalBalance": 1821788.967776,
        "beginPrincipalBalance": 1849218.992512,
        "prepayPrincipalPayment": 14865.293603,
        "scheduledPrincipalPayment": 12564.731134
    }
    {
        "date": "2042-10-25",
        "totalCashFlow": 27352.694639,
        "interestPayment": 759.078737,
        "principalBalance": 1795195.351873,
        "principalPayment": 26593.615903,
        "endPrincipalBalance": 1795195.351873,
        "beginPrincipalBalance": 1821788.967776,
        "prepayPrincipalPayment": 14117.597365,
        "scheduledPrincipalPayment": 12476.018538
    }
    {
        "date": "2042-11-25",
        "totalCashFlow": 26870.54728,
        "interestPayment": 747.998063,
        "principalBalance": 1769072.802656,
        "principalPayment": 26122.549217,
        "endPrincipalBalance": 1769072.802656,
        "beginPrincipalBalance": 1795195.351873,
        "prepayPrincipalPayment": 13730.983351,
        "scheduledPrincipalPayment": 12391.565866
    }
    {
        "date": "2042-12-25",
        "totalCashFlow": 24390.87582,
        "interestPayment": 737.113668,
        "principalBalance": 1745419.040504,
        "principalPayment": 23653.762152,
        "endPrincipalBalance": 1745419.040504,
        "beginPrincipalBalance": 1769072.802656,
        "prepayPrincipalPayment": 11344.826468,
        "scheduledPrincipalPayment": 12308.935683
    }
    {
        "date": "2043-01-25",
        "totalCashFlow": 25765.893417,
        "interestPayment": 727.257934,
        "principalBalance": 1720380.405021,
        "principalPayment": 25038.635483,
        "endPrincipalBalance": 1720380.405021,
        "beginPrincipalBalance": 1745419.040504,
        "prepayPrincipalPayment": 12796.449414,
        "scheduledPrincipalPayment": 12242.186069
    }
    {
        "date": "2043-02-25",
        "totalCashFlow": 22503.312682,
        "interestPayment": 716.825169,
        "principalBalance": 1698593.917508,
        "principalPayment": 21786.487514,
        "endPrincipalBalance": 1698593.917508,
        "beginPrincipalBalance": 1720380.405021,
        "prepayPrincipalPayment": 9622.030239,
        "scheduledPrincipalPayment": 12164.457274
    }
    {
        "date": "2043-03-25",
        "totalCashFlow": 22491.948413,
        "interestPayment": 707.747466,
        "principalBalance": 1676809.71656,
        "principalPayment": 21784.200948,
        "endPrincipalBalance": 1676809.71656,
        "beginPrincipalBalance": 1698593.917508,
        "prepayPrincipalPayment": 9675.663633,
        "scheduledPrincipalPayment": 12108.537315
    }
    {
        "date": "2043-04-25",
        "totalCashFlow": 24469.84531,
        "interestPayment": 698.670715,
        "principalBalance": 1653038.541965,
        "principalPayment": 23771.174595,
        "endPrincipalBalance": 1653038.541965,
        "beginPrincipalBalance": 1676809.71656,
        "prepayPrincipalPayment": 11719.565394,
        "scheduledPrincipalPayment": 12051.6092
    }
    {
        "date": "2043-05-25",
        "totalCashFlow": 25814.123919,
        "interestPayment": 688.766059,
        "principalBalance": 1627913.184105,
        "principalPayment": 25125.35786,
        "endPrincipalBalance": 1627913.184105,
        "beginPrincipalBalance": 1653038.541965,
        "prepayPrincipalPayment": 13146.124204,
        "scheduledPrincipalPayment": 11979.233656
    }
    {
        "date": "2043-06-25",
        "totalCashFlow": 25653.933773,
        "interestPayment": 678.29716,
        "principalBalance": 1602937.547492,
        "principalPayment": 24975.636613,
        "endPrincipalBalance": 1602937.547492,
        "beginPrincipalBalance": 1627913.184105,
        "prepayPrincipalPayment": 13079.987257,
        "scheduledPrincipalPayment": 11895.649357
    }
    {
        "date": "2043-07-25",
        "totalCashFlow": 27028.211923,
        "interestPayment": 667.890645,
        "principalBalance": 1576577.226214,
        "principalPayment": 26360.321278,
        "endPrincipalBalance": 1576577.226214,
        "beginPrincipalBalance": 1602937.547492,
        "prepayPrincipalPayment": 14548.663869,
        "scheduledPrincipalPayment": 11811.657409
    }
    {
        "date": "2043-08-25",
        "totalCashFlow": 26431.063104,
        "interestPayment": 656.907178,
        "principalBalance": 1550803.070287,
        "principalPayment": 25774.155927,
        "endPrincipalBalance": 1550803.070287,
        "beginPrincipalBalance": 1576577.226214,
        "prepayPrincipalPayment": 14058.308615,
        "scheduledPrincipalPayment": 11715.847312
    }
    {
        "date": "2043-09-25",
        "totalCashFlow": 25081.186524,
        "interestPayment": 646.167946,
        "principalBalance": 1526368.051709,
        "principalPayment": 24435.018578,
        "endPrincipalBalance": 1526368.051709,
        "beginPrincipalBalance": 1550803.070287,
        "prepayPrincipalPayment": 12812.329029,
        "scheduledPrincipalPayment": 11622.689549
    }
    {
        "date": "2043-10-25",
        "totalCashFlow": 24328.886761,
        "interestPayment": 635.986688,
        "principalBalance": 1502675.151636,
        "principalPayment": 23692.900073,
        "endPrincipalBalance": 1502675.151636,
        "beginPrincipalBalance": 1526368.051709,
        "prepayPrincipalPayment": 12154.95305,
        "scheduledPrincipalPayment": 11537.947023
    }
    {
        "date": "2043-11-25",
        "totalCashFlow": 23448.659548,
        "interestPayment": 626.114647,
        "principalBalance": 1479852.606734,
        "principalPayment": 22822.544902,
        "endPrincipalBalance": 1479852.606734,
        "beginPrincipalBalance": 1502675.151636,
        "prepayPrincipalPayment": 11365.255775,
        "scheduledPrincipalPayment": 11457.289126
    }
    {
        "date": "2043-12-25",
        "totalCashFlow": 22204.836817,
        "interestPayment": 616.605253,
        "principalBalance": 1458264.37517,
        "principalPayment": 21588.231564,
        "endPrincipalBalance": 1458264.37517,
        "beginPrincipalBalance": 1479852.606734,
        "prepayPrincipalPayment": 10206.41998,
        "scheduledPrincipalPayment": 11381.811584
    }
    {
        "date": "2044-01-25",
        "totalCashFlow": 22894.646676,
        "interestPayment": 607.610156,
        "principalBalance": 1435977.338651,
        "principalPayment": 22287.036519,
        "endPrincipalBalance": 1435977.338651,
        "beginPrincipalBalance": 1458264.37517,
        "prepayPrincipalPayment": 10972.559123,
        "scheduledPrincipalPayment": 11314.477396
    }
    {
        "date": "2044-02-25",
        "totalCashFlow": 19813.534953,
        "interestPayment": 598.323891,
        "principalBalance": 1416762.127589,
        "principalPayment": 19215.211062,
        "endPrincipalBalance": 1416762.127589,
        "beginPrincipalBalance": 1435977.338651,
        "prepayPrincipalPayment": 7974.837452,
        "scheduledPrincipalPayment": 11240.373609
    }
    {
        "date": "2044-03-25",
        "totalCashFlow": 20428.102309,
        "interestPayment": 590.317553,
        "principalBalance": 1396924.342834,
        "principalPayment": 19837.784756,
        "endPrincipalBalance": 1396924.342834,
        "beginPrincipalBalance": 1416762.127589,
        "prepayPrincipalPayment": 8648.684946,
        "scheduledPrincipalPayment": 11189.099809
    }
    {
        "date": "2044-04-25",
        "totalCashFlow": 22269.580479,
        "interestPayment": 582.05181,
        "principalBalance": 1375236.814164,
        "principalPayment": 21687.52867,
        "endPrincipalBalance": 1375236.814164,
        "beginPrincipalBalance": 1396924.342834,
        "prepayPrincipalPayment": 10555.693341,
        "scheduledPrincipalPayment": 11131.835329
    }
    {
        "date": "2044-05-25",
        "totalCashFlow": 22146.471175,
        "interestPayment": 573.015339,
        "principalBalance": 1353663.358329,
        "principalPayment": 21573.455835,
        "endPrincipalBalance": 1353663.358329,
        "beginPrincipalBalance": 1375236.814164,
        "prepayPrincipalPayment": 10514.905258,
        "scheduledPrincipalPayment": 11058.550577
    }
    {
        "date": "2044-06-25",
        "totalCashFlow": 23068.541019,
        "interestPayment": 564.026399,
        "principalBalance": 1331158.843709,
        "principalPayment": 22504.51462,
        "endPrincipalBalance": 1331158.843709,
        "beginPrincipalBalance": 1353663.358329,
        "prepayPrincipalPayment": 11519.771351,
        "scheduledPrincipalPayment": 10984.743269
    }
    {
        "date": "2044-07-25",
        "totalCashFlow": 23684.193336,
        "interestPayment": 554.649518,
        "principalBalance": 1308029.299891,
        "principalPayment": 23129.543818,
        "endPrincipalBalance": 1308029.299891,
        "beginPrincipalBalance": 1331158.843709,
        "prepayPrincipalPayment": 12227.702014,
        "scheduledPrincipalPayment": 10901.841804
    }
    {
        "date": "2044-08-25",
        "totalCashFlow": 22252.063102,
        "interestPayment": 545.012208,
        "principalBalance": 1286322.248997,
        "principalPayment": 21707.050894,
        "endPrincipalBalance": 1286322.248997,
        "beginPrincipalBalance": 1308029.299891,
        "prepayPrincipalPayment": 10894.926759,
        "scheduledPrincipalPayment": 10812.124135
    }
    {
        "date": "2044-09-25",
        "totalCashFlow": 22869.015094,
        "interestPayment": 535.967604,
        "principalBalance": 1263989.201506,
        "principalPayment": 22333.04749,
        "endPrincipalBalance": 1263989.201506,
        "beginPrincipalBalance": 1286322.248997,
        "prepayPrincipalPayment": 11600.563012,
        "scheduledPrincipalPayment": 10732.484479
    }
    {
        "date": "2044-10-25",
        "totalCashFlow": 21367.787698,
        "interestPayment": 526.662167,
        "principalBalance": 1243148.075975,
        "principalPayment": 20841.125531,
        "endPrincipalBalance": 1243148.075975,
        "beginPrincipalBalance": 1263989.201506,
        "prepayPrincipalPayment": 10195.167208,
        "scheduledPrincipalPayment": 10645.958323
    }
    {
        "date": "2044-11-25",
        "totalCashFlow": 20279.691057,
        "interestPayment": 517.978365,
        "principalBalance": 1223386.363283,
        "principalPayment": 19761.712692,
        "endPrincipalBalance": 1223386.363283,
        "beginPrincipalBalance": 1243148.075975,
        "prepayPrincipalPayment": 9191.353281,
        "scheduledPrincipalPayment": 10570.359412
    }
    {
        "date": "2044-12-25",
        "totalCashFlow": 19955.604039,
        "interestPayment": 509.744318,
        "principalBalance": 1203940.503562,
        "principalPayment": 19445.859721,
        "endPrincipalBalance": 1203940.503562,
        "beginPrincipalBalance": 1223386.363283,
        "prepayPrincipalPayment": 8943.394979,
        "scheduledPrincipalPayment": 10502.464743
    }
    {
        "date": "2045-01-25",
        "totalCashFlow": 19795.822771,
        "interestPayment": 501.641876,
        "principalBalance": 1184646.322667,
        "principalPayment": 19294.180894,
        "endPrincipalBalance": 1184646.322667,
        "beginPrincipalBalance": 1203940.503562,
        "prepayPrincipalPayment": 8858.29837,
        "scheduledPrincipalPayment": 10435.882525
    }
    {
        "date": "2045-02-25",
        "totalCashFlow": 17923.54704,
        "interestPayment": 493.602634,
        "principalBalance": 1167216.378262,
        "principalPayment": 17429.944405,
        "endPrincipalBalance": 1167216.378262,
        "beginPrincipalBalance": 1184646.322667,
        "prepayPrincipalPayment": 7060.727909,
        "scheduledPrincipalPayment": 10369.216496
    }
    {
        "date": "2045-03-25",
        "totalCashFlow": 17876.974969,
        "interestPayment": 486.340158,
        "principalBalance": 1149825.74345,
        "principalPayment": 17390.634812,
        "endPrincipalBalance": 1149825.74345,
        "beginPrincipalBalance": 1167216.378262,
        "prepayPrincipalPayment": 7073.030325,
        "scheduledPrincipalPayment": 10317.604487
    }
    {
        "date": "2045-04-25",
        "totalCashFlow": 19549.14613,
        "interestPayment": 479.09406,
        "principalBalance": 1130755.69138,
        "principalPayment": 19070.05207,
        "endPrincipalBalance": 1130755.69138,
        "beginPrincipalBalance": 1149825.74345,
        "prepayPrincipalPayment": 8804.845402,
        "scheduledPrincipalPayment": 10265.206669
    }
    {
        "date": "2045-05-25",
        "totalCashFlow": 19262.31343,
        "interestPayment": 471.148205,
        "principalBalance": 1111964.526155,
        "principalPayment": 18791.165226,
        "endPrincipalBalance": 1111964.526155,
        "beginPrincipalBalance": 1130755.69138,
        "prepayPrincipalPayment": 8594.66265,
        "scheduledPrincipalPayment": 10196.502575
    }
    {
        "date": "2045-06-25",
        "totalCashFlow": 20470.10121,
        "interestPayment": 463.318553,
        "principalBalance": 1091957.743497,
        "principalPayment": 20006.782657,
        "endPrincipalBalance": 1091957.743497,
        "beginPrincipalBalance": 1111964.526155,
        "prepayPrincipalPayment": 9877.947126,
        "scheduledPrincipalPayment": 10128.835531
    }
    {
        "date": "2045-07-25",
        "totalCashFlow": 20553.464291,
        "interestPayment": 454.982393,
        "principalBalance": 1071859.261599,
        "principalPayment": 20098.481898,
        "endPrincipalBalance": 1071859.261599,
        "beginPrincipalBalance": 1091957.743497,
        "prepayPrincipalPayment": 10049.995005,
        "scheduledPrincipalPayment": 10048.486893
    }
    {
        "date": "2045-08-25",
        "totalCashFlow": 19412.240776,
        "interestPayment": 446.608026,
        "principalBalance": 1052893.628849,
        "principalPayment": 18965.63275,
        "endPrincipalBalance": 1052893.628849,
        "beginPrincipalBalance": 1071859.261599,
        "prepayPrincipalPayment": 9000.117608,
        "scheduledPrincipalPayment": 9965.515142
    }
    {
        "date": "2045-09-25",
        "totalCashFlow": 19859.413809,
        "interestPayment": 438.705679,
        "principalBalance": 1033472.920718,
        "principalPayment": 19420.70813,
        "endPrincipalBalance": 1033472.920718,
        "beginPrincipalBalance": 1052893.628849,
        "prepayPrincipalPayment": 9529.363298,
        "scheduledPrincipalPayment": 9891.344832
    }
    {
        "date": "2045-10-25",
        "totalCashFlow": 18367.182342,
        "interestPayment": 430.613717,
        "principalBalance": 1015536.352093,
        "principalPayment": 17936.568625,
        "endPrincipalBalance": 1015536.352093,
        "beginPrincipalBalance": 1033472.920718,
        "prepayPrincipalPayment": 8125.386462,
        "scheduledPrincipalPayment": 9811.182163
    }
    {
        "date": "2045-11-25",
        "totalCashFlow": 18074.068613,
        "interestPayment": 423.140147,
        "principalBalance": 997885.423627,
        "principalPayment": 17650.928466,
        "endPrincipalBalance": 997885.423627,
        "beginPrincipalBalance": 1015536.352093,
        "prepayPrincipalPayment": 7907.484386,
        "scheduledPrincipalPayment": 9743.44408
    }
    {
        "date": "2045-12-25",
        "totalCashFlow": 17521.726637,
        "interestPayment": 415.785593,
        "principalBalance": 980779.482583,
        "principalPayment": 17105.941043,
        "endPrincipalBalance": 980779.482583,
        "beginPrincipalBalance": 997885.423627,
        "prepayPrincipalPayment": 7429.029718,
        "scheduledPrincipalPayment": 9676.911326
    }
    {
        "date": "2046-01-25",
        "totalCashFlow": 17122.460023,
        "interestPayment": 408.658118,
        "principalBalance": 964065.680678,
        "principalPayment": 16713.801905,
        "endPrincipalBalance": 964065.680678,
        "beginPrincipalBalance": 980779.482583,
        "prepayPrincipalPayment": 7099.63411,
        "scheduledPrincipalPayment": 9614.167795
    }
    {
        "date": "2046-02-25",
        "totalCashFlow": 16095.707746,
        "interestPayment": 401.694034,
        "principalBalance": 948371.666966,
        "principalPayment": 15694.013712,
        "endPrincipalBalance": 948371.666966,
        "beginPrincipalBalance": 964065.680678,
        "prepayPrincipalPayment": 6140.188052,
        "scheduledPrincipalPayment": 9553.82566
    }
    {
        "date": "2046-03-25",
        "totalCashFlow": 15842.52566,
        "interestPayment": 395.154861,
        "principalBalance": 932924.296167,
        "principalPayment": 15447.370799,
        "endPrincipalBalance": 932924.296167,
        "beginPrincipalBalance": 948371.666966,
        "prepayPrincipalPayment": 5945.115148,
        "scheduledPrincipalPayment": 9502.255651
    }
    {
        "date": "2046-04-25",
        "totalCashFlow": 16759.557413,
        "interestPayment": 388.718457,
        "principalBalance": 916553.457211,
        "principalPayment": 16370.838956,
        "endPrincipalBalance": 916553.457211,
        "beginPrincipalBalance": 932924.296167,
        "prepayPrincipalPayment": 6918.918046,
        "scheduledPrincipalPayment": 9451.92091
    }
    {
        "date": "2046-05-25",
        "totalCashFlow": 17090.740912,
        "interestPayment": 381.897274,
        "principalBalance": 899844.613573,
        "principalPayment": 16708.843638,
        "endPrincipalBalance": 899844.613573,
        "beginPrincipalBalance": 916553.457211,
        "prepayPrincipalPayment": 7317.967227,
        "scheduledPrincipalPayment": 9390.87641
    }
    {
        "date": "2046-06-25",
        "totalCashFlow": 17721.277861,
        "interestPayment": 374.935256,
        "principalBalance": 882498.270968,
        "principalPayment": 17346.342605,
        "endPrincipalBalance": 882498.270968,
        "beginPrincipalBalance": 899844.613573,
        "prepayPrincipalPayment": 8021.51797,
        "scheduledPrincipalPayment": 9324.824635
    }
    {
        "date": "2046-07-25",
        "totalCashFlow": 17462.819157,
        "interestPayment": 367.707613,
        "principalBalance": 865403.159424,
        "principalPayment": 17095.111544,
        "endPrincipalBalance": 865403.159424,
        "beginPrincipalBalance": 882498.270968,
        "prepayPrincipalPayment": 7844.656088,
        "scheduledPrincipalPayment": 9250.455456
    }
    {
        "date": "2046-08-25",
        "totalCashFlow": 17113.287736,
        "interestPayment": 360.58465,
        "principalBalance": 848650.456338,
        "principalPayment": 16752.703086,
        "endPrincipalBalance": 848650.456338,
        "beginPrincipalBalance": 865403.159424,
        "prepayPrincipalPayment": 7575.798013,
        "scheduledPrincipalPayment": 9176.905073
    }
    {
        "date": "2046-09-25",
        "totalCashFlow": 17148.362216,
        "interestPayment": 353.604357,
        "principalBalance": 831855.698479,
        "principalPayment": 16794.757859,
        "endPrincipalBalance": 831855.698479,
        "beginPrincipalBalance": 848650.456338,
        "prepayPrincipalPayment": 7689.574361,
        "scheduledPrincipalPayment": 9105.183498
    }
    {
        "date": "2046-10-25",
        "totalCashFlow": 15763.410586,
        "interestPayment": 346.606541,
        "principalBalance": 816438.894434,
        "principalPayment": 15416.804045,
        "endPrincipalBalance": 816438.894434,
        "beginPrincipalBalance": 831855.698479,
        "prepayPrincipalPayment": 6385.619171,
        "scheduledPrincipalPayment": 9031.184874
    }
    {
        "date": "2046-11-25",
        "totalCashFlow": 15944.739935,
        "interestPayment": 340.182873,
        "principalBalance": 800834.337372,
        "principalPayment": 15604.557062,
        "endPrincipalBalance": 800834.337372,
        "beginPrincipalBalance": 816438.894434,
        "prepayPrincipalPayment": 6634.125205,
        "scheduledPrincipalPayment": 8970.431857
    }
    {
        "date": "2046-12-25",
        "totalCashFlow": 15292.626009,
        "interestPayment": 333.680974,
        "principalBalance": 785875.392337,
        "principalPayment": 14958.945035,
        "endPrincipalBalance": 785875.392337,
        "beginPrincipalBalance": 800834.337372,
        "prepayPrincipalPayment": 6052.946421,
        "scheduledPrincipalPayment": 8905.998614
    }
    {
        "date": "2047-01-25",
        "totalCashFlow": 14965.158025,
        "interestPayment": 327.44808,
        "principalBalance": 771237.682392,
        "principalPayment": 14637.709944,
        "endPrincipalBalance": 771237.682392,
        "beginPrincipalBalance": 785875.392337,
        "prepayPrincipalPayment": 5790.576381,
        "scheduledPrincipalPayment": 8847.133563
    }
    {
        "date": "2047-02-25",
        "totalCashFlow": 14172.724877,
        "interestPayment": 321.349034,
        "principalBalance": 757386.30655,
        "principalPayment": 13851.375842,
        "endPrincipalBalance": 757386.30655,
        "beginPrincipalBalance": 771237.682392,
        "prepayPrincipalPayment": 5061.025874,
        "scheduledPrincipalPayment": 8790.349968
    }
    {
        "date": "2047-03-25",
        "totalCashFlow": 13958.021755,
        "interestPayment": 315.577628,
        "principalBalance": 743743.862423,
        "principalPayment": 13642.444127,
        "endPrincipalBalance": 743743.862423,
        "beginPrincipalBalance": 757386.30655,
        "prepayPrincipalPayment": 4901.347521,
        "scheduledPrincipalPayment": 8741.096606
    }
    {
        "date": "2047-04-25",
        "totalCashFlow": 14530.329715,
        "interestPayment": 309.893276,
        "principalBalance": 729523.425983,
        "principalPayment": 14220.436439,
        "endPrincipalBalance": 729523.425983,
        "beginPrincipalBalance": 743743.862423,
        "prepayPrincipalPayment": 5527.521714,
        "scheduledPrincipalPayment": 8692.914725
    }
    {
        "date": "2047-05-25",
        "totalCashFlow": 14920.817459,
        "interestPayment": 303.968094,
        "principalBalance": 714906.576619,
        "principalPayment": 14616.849364,
        "endPrincipalBalance": 714906.576619,
        "beginPrincipalBalance": 729523.425983,
        "prepayPrincipalPayment": 5980.317606,
        "scheduledPrincipalPayment": 8636.531758
    }
    {
        "date": "2047-06-25",
        "totalCashFlow": 15261.361701,
        "interestPayment": 297.87774,
        "principalBalance": 699943.092658,
        "principalPayment": 14963.483961,
        "endPrincipalBalance": 699943.092658,
        "beginPrincipalBalance": 714906.576619,
        "prepayPrincipalPayment": 6389.677197,
        "scheduledPrincipalPayment": 8573.806764
    }
    {
        "date": "2047-07-25",
        "totalCashFlow": 14829.787835,
        "interestPayment": 291.642955,
        "principalBalance": 685404.947778,
        "principalPayment": 14538.14488,
        "endPrincipalBalance": 685404.947778,
        "beginPrincipalBalance": 699943.092658,
        "prepayPrincipalPayment": 6033.048834,
        "scheduledPrincipalPayment": 8505.096046
    }
    {
        "date": "2047-08-25",
        "totalCashFlow": 14945.867692,
        "interestPayment": 285.585395,
        "principalBalance": 670744.66548,
        "principalPayment": 14660.282297,
        "endPrincipalBalance": 670744.66548,
        "beginPrincipalBalance": 685404.947778,
        "prepayPrincipalPayment": 6220.614145,
        "scheduledPrincipalPayment": 8439.668152
    }
    {
        "date": "2047-09-25",
        "totalCashFlow": 14562.998375,
        "interestPayment": 279.476944,
        "principalBalance": 656461.144049,
        "principalPayment": 14283.521431,
        "endPrincipalBalance": 656461.144049,
        "beginPrincipalBalance": 670744.66548,
        "prepayPrincipalPayment": 5912.694605,
        "scheduledPrincipalPayment": 8370.826826
    }
    {
        "date": "2047-10-25",
        "totalCashFlow": 13864.867191,
        "interestPayment": 273.525477,
        "principalBalance": 642869.802334,
        "principalPayment": 13591.341715,
        "endPrincipalBalance": 642869.802334,
        "beginPrincipalBalance": 656461.144049,
        "prepayPrincipalPayment": 5286.595482,
        "scheduledPrincipalPayment": 8304.746232
    }
    {
        "date": "2047-11-25",
        "totalCashFlow": 13800.222155,
        "interestPayment": 267.862418,
        "principalBalance": 629337.442597,
        "principalPayment": 13532.359738,
        "endPrincipalBalance": 629337.442597,
        "beginPrincipalBalance": 642869.802334,
        "prepayPrincipalPayment": 5286.769768,
        "scheduledPrincipalPayment": 8245.589969
    }
    {
        "date": "2047-12-25",
        "totalCashFlow": 13148.497926,
        "interestPayment": 262.223934,
        "principalBalance": 616451.168605,
        "principalPayment": 12886.273992,
        "endPrincipalBalance": 616451.168605,
        "beginPrincipalBalance": 629337.442597,
        "prepayPrincipalPayment": 4700.856732,
        "scheduledPrincipalPayment": 8185.41726
    }
    {
        "date": "2048-01-25",
        "totalCashFlow": 13163.849683,
        "interestPayment": 256.854654,
        "principalBalance": 603544.173575,
        "principalPayment": 12906.99503,
        "endPrincipalBalance": 603544.173575,
        "beginPrincipalBalance": 616451.168605,
        "prepayPrincipalPayment": 4775.062772,
        "scheduledPrincipalPayment": 8131.932258
    }
    {
        "date": "2048-02-25",
        "totalCashFlow": 12422.788069,
        "interestPayment": 251.476739,
        "principalBalance": 591372.862245,
        "principalPayment": 12171.31133,
        "endPrincipalBalance": 591372.862245,
        "beginPrincipalBalance": 603544.173575,
        "prepayPrincipalPayment": 4094.807218,
        "scheduledPrincipalPayment": 8076.504112
    }
    {
        "date": "2048-03-25",
        "totalCashFlow": 12239.743902,
        "interestPayment": 246.405359,
        "principalBalance": 579379.523702,
        "principalPayment": 11993.338542,
        "endPrincipalBalance": 579379.523702,
        "beginPrincipalBalance": 591372.862245,
        "prepayPrincipalPayment": 3964.01834,
        "scheduledPrincipalPayment": 8029.320202
    }
    {
        "date": "2048-04-25",
        "totalCashFlow": 12745.83395,
        "interestPayment": 241.408135,
        "principalBalance": 566875.097887,
        "principalPayment": 12504.425815,
        "endPrincipalBalance": 566875.097887,
        "beginPrincipalBalance": 579379.523702,
        "prepayPrincipalPayment": 4521.360543,
        "scheduledPrincipalPayment": 7983.065273
    }
    {
        "date": "2048-05-25",
        "totalCashFlow": 12938.293931,
        "interestPayment": 236.197957,
        "principalBalance": 554173.001913,
        "principalPayment": 12702.095974,
        "endPrincipalBalance": 554173.001913,
        "beginPrincipalBalance": 566875.097887,
        "prepayPrincipalPayment": 4773.949412,
        "scheduledPrincipalPayment": 7928.146562
    }
    {
        "date": "2048-06-25",
        "totalCashFlow": 12794.245399,
        "interestPayment": 230.905417,
        "principalBalance": 541609.661931,
        "principalPayment": 12563.339982,
        "endPrincipalBalance": 541609.661931,
        "beginPrincipalBalance": 554173.001913,
        "prepayPrincipalPayment": 4694.719536,
        "scheduledPrincipalPayment": 7868.620446
    }
    {
        "date": "2048-07-25",
        "totalCashFlow": 13039.998244,
        "interestPayment": 225.670692,
        "principalBalance": 528795.33438,
        "principalPayment": 12814.327551,
        "endPrincipalBalance": 528795.33438,
        "beginPrincipalBalance": 541609.661931,
        "prepayPrincipalPayment": 5005.200813,
        "scheduledPrincipalPayment": 7809.126738
    }
    {
        "date": "2048-08-25",
        "totalCashFlow": 12783.231483,
        "interestPayment": 220.331389,
        "principalBalance": 516232.434286,
        "principalPayment": 12562.900094,
        "endPrincipalBalance": 516232.434286,
        "beginPrincipalBalance": 528795.33438,
        "prepayPrincipalPayment": 4818.937693,
        "scheduledPrincipalPayment": 7743.962401
    }
    {
        "date": "2048-09-25",
        "totalCashFlow": 12348.20514,
        "interestPayment": 215.096848,
        "principalBalance": 504099.325994,
        "principalPayment": 12133.108292,
        "endPrincipalBalance": 504099.325994,
        "beginPrincipalBalance": 516232.434286,
        "prepayPrincipalPayment": 4452.773816,
        "scheduledPrincipalPayment": 7680.334476
    }
    {
        "date": "2048-10-25",
        "totalCashFlow": 12066.782383,
        "interestPayment": 210.041386,
        "principalBalance": 492242.584997,
        "principalPayment": 11856.740997,
        "endPrincipalBalance": 492242.584997,
        "beginPrincipalBalance": 504099.325994,
        "prepayPrincipalPayment": 4235.723595,
        "scheduledPrincipalPayment": 7621.017403
    }
    {
        "date": "2048-11-25",
        "totalCashFlow": 11764.140539,
        "interestPayment": 205.101077,
        "principalBalance": 480683.545535,
        "principalPayment": 11559.039462,
        "endPrincipalBalance": 480683.545535,
        "beginPrincipalBalance": 492242.584997,
        "prepayPrincipalPayment": 3995.170228,
        "scheduledPrincipalPayment": 7563.869234
    }
    {
        "date": "2048-12-25",
        "totalCashFlow": 11378.109399,
        "interestPayment": 200.284811,
        "principalBalance": 469505.720946,
        "principalPayment": 11177.824589,
        "endPrincipalBalance": 469505.720946,
        "beginPrincipalBalance": 480683.545535,
        "prepayPrincipalPayment": 3668.489676,
        "scheduledPrincipalPayment": 7509.334913
    }
    {
        "date": "2049-01-25",
        "totalCashFlow": 11453.754432,
        "interestPayment": 195.627384,
        "principalBalance": 458247.593898,
        "principalPayment": 11258.127048,
        "endPrincipalBalance": 458247.593898,
        "beginPrincipalBalance": 469505.720946,
        "prepayPrincipalPayment": 3799.249955,
        "scheduledPrincipalPayment": 7458.877094
    }
    {
        "date": "2049-02-25",
        "totalCashFlow": 10663.256962,
        "interestPayment": 190.936497,
        "principalBalance": 447775.273433,
        "principalPayment": 10472.320464,
        "endPrincipalBalance": 447775.273433,
        "beginPrincipalBalance": 458247.593898,
        "prepayPrincipalPayment": 3067.069338,
        "scheduledPrincipalPayment": 7405.251127
    }
    {
        "date": "2049-03-25",
        "totalCashFlow": 10694.369376,
        "interestPayment": 186.573031,
        "principalBalance": 437267.477088,
        "principalPayment": 10507.796345,
        "endPrincipalBalance": 437267.477088,
        "beginPrincipalBalance": 447775.273433,
        "prepayPrincipalPayment": 3145.261633,
        "scheduledPrincipalPayment": 7362.534712
    }
    {
        "date": "2049-04-25",
        "totalCashFlow": 11139.25986,
        "interestPayment": 182.194782,
        "principalBalance": 426310.41201,
        "principalPayment": 10957.065078,
        "endPrincipalBalance": 426310.41201,
        "beginPrincipalBalance": 437267.477088,
        "prepayPrincipalPayment": 3639.496275,
        "scheduledPrincipalPayment": 7317.568803
    }
    {
        "date": "2049-05-25",
        "totalCashFlow": 11144.657541,
        "interestPayment": 177.629338,
        "principalBalance": 415343.383807,
        "principalPayment": 10967.028203,
        "endPrincipalBalance": 415343.383807,
        "beginPrincipalBalance": 426310.41201,
        "prepayPrincipalPayment": 3703.844171,
        "scheduledPrincipalPayment": 7263.184032
    }
    {
        "date": "2049-06-25",
        "totalCashFlow": 11091.46839,
        "interestPayment": 173.059743,
        "principalBalance": 404424.97516,
        "principalPayment": 10918.408647,
        "endPrincipalBalance": 404424.97516,
        "beginPrincipalBalance": 415343.383807,
        "prepayPrincipalPayment": 3711.922973,
        "scheduledPrincipalPayment": 7206.485674
    }
    {
        "date": "2049-07-25",
        "totalCashFlow": 11256.591087,
        "interestPayment": 168.510406,
        "principalBalance": 393336.89448,
        "principalPayment": 11088.080681,
        "endPrincipalBalance": 393336.89448,
        "beginPrincipalBalance": 404424.97516,
        "prepayPrincipalPayment": 3939.698061,
        "scheduledPrincipalPayment": 7148.38262
    }
    {
        "date": "2049-08-25",
        "totalCashFlow": 10978.529285,
        "interestPayment": 163.890373,
        "principalBalance": 382522.255567,
        "principalPayment": 10814.638913,
        "endPrincipalBalance": 382522.255567,
        "beginPrincipalBalance": 393336.89448,
        "prepayPrincipalPayment": 3729.772724,
        "scheduledPrincipalPayment": 7084.866188
    }
    {
        "date": "2049-09-25",
        "totalCashFlow": 10855.913254,
        "interestPayment": 159.384273,
        "principalBalance": 371825.726586,
        "principalPayment": 10696.528981,
        "endPrincipalBalance": 371825.726586,
        "beginPrincipalBalance": 382522.255567,
        "prepayPrincipalPayment": 3672.767714,
        "scheduledPrincipalPayment": 7023.761267
    }
    {
        "date": "2049-10-25",
        "totalCashFlow": 10563.481652,
        "interestPayment": 154.927386,
        "principalBalance": 361417.17232,
        "principalPayment": 10408.554266,
        "endPrincipalBalance": 361417.17232,
        "beginPrincipalBalance": 371825.726586,
        "prepayPrincipalPayment": 3446.247869,
        "scheduledPrincipalPayment": 6962.306396
    }
    {
        "date": "2049-11-25",
        "totalCashFlow": 10275.200179,
        "interestPayment": 150.590488,
        "principalBalance": 351292.56263,
        "principalPayment": 10124.60969,
        "endPrincipalBalance": 351292.56263,
        "beginPrincipalBalance": 361417.17232,
        "prepayPrincipalPayment": 3220.88053,
        "scheduledPrincipalPayment": 6903.72916
    }
    {
        "date": "2049-12-25",
        "totalCashFlow": 10140.731031,
        "interestPayment": 146.371901,
        "principalBalance": 341298.2035,
        "principalPayment": 9994.359129,
        "endPrincipalBalance": 341298.2035,
        "beginPrincipalBalance": 351292.56263,
        "prepayPrincipalPayment": 3146.226752,
        "scheduledPrincipalPayment": 6848.132377
    }
    {
        "date": "2050-01-25",
        "totalCashFlow": 10040.562754,
        "interestPayment": 142.207585,
        "principalBalance": 331399.848331,
        "principalPayment": 9898.355169,
        "endPrincipalBalance": 331399.848331,
        "beginPrincipalBalance": 341298.2035,
        "prepayPrincipalPayment": 3105.706739,
        "scheduledPrincipalPayment": 6792.648431
    }
    {
        "date": "2050-02-25",
        "totalCashFlow": 9607.956675,
        "interestPayment": 138.08327,
        "principalBalance": 321929.974926,
        "principalPayment": 9469.873405,
        "endPrincipalBalance": 321929.974926,
        "beginPrincipalBalance": 331399.848331,
        "prepayPrincipalPayment": 2733.281132,
        "scheduledPrincipalPayment": 6736.592273
    }
    {
        "date": "2050-03-25",
        "totalCashFlow": 9532.773741,
        "interestPayment": 134.13749,
        "principalBalance": 312531.338675,
        "principalPayment": 9398.636251,
        "endPrincipalBalance": 312531.338675,
        "beginPrincipalBalance": 321929.974926,
        "prepayPrincipalPayment": 2711.799922,
        "scheduledPrincipalPayment": 6686.836329
    }
    {
        "date": "2050-04-25",
        "totalCashFlow": 9776.696332,
        "interestPayment": 130.221391,
        "principalBalance": 302884.863734,
        "principalPayment": 9646.47494,
        "endPrincipalBalance": 302884.863734,
        "beginPrincipalBalance": 312531.338675,
        "prepayPrincipalPayment": 3010.254905,
        "scheduledPrincipalPayment": 6636.220035
    }
    {
        "date": "2050-05-25",
        "totalCashFlow": 9666.339678,
        "interestPayment": 126.202027,
        "principalBalance": 293344.726083,
        "principalPayment": 9540.137651,
        "endPrincipalBalance": 293344.726083,
        "beginPrincipalBalance": 302884.863734,
        "prepayPrincipalPayment": 2962.378676,
        "scheduledPrincipalPayment": 6577.758975
    }
    {
        "date": "2050-06-25",
        "totalCashFlow": 9702.375823,
        "interestPayment": 122.226969,
        "principalBalance": 283764.577229,
        "principalPayment": 9580.148854,
        "endPrincipalBalance": 283764.577229,
        "beginPrincipalBalance": 293344.726083,
        "prepayPrincipalPayment": 3061.368769,
        "scheduledPrincipalPayment": 6518.780085
    }
    {
        "date": "2050-07-25",
        "totalCashFlow": 9686.77533,
        "interestPayment": 118.235241,
        "principalBalance": 274196.037139,
        "principalPayment": 9568.54009,
        "endPrincipalBalance": 274196.037139,
        "beginPrincipalBalance": 283764.577229,
        "prepayPrincipalPayment": 3112.618739,
        "scheduledPrincipalPayment": 6455.921351
    }
    {
        "date": "2050-08-25",
        "totalCashFlow": 9390.907533,
        "interestPayment": 114.248349,
        "principalBalance": 264919.377955,
        "principalPayment": 9276.659184,
        "endPrincipalBalance": 264919.377955,
        "beginPrincipalBalance": 274196.037139,
        "prepayPrincipalPayment": 2886.552136,
        "scheduledPrincipalPayment": 6390.107048
    }
    {
        "date": "2050-09-25",
        "totalCashFlow": 9373.635912,
        "interestPayment": 110.383074,
        "principalBalance": 255656.125117,
        "principalPayment": 9263.252838,
        "endPrincipalBalance": 255656.125117,
        "beginPrincipalBalance": 264919.377955,
        "prepayPrincipalPayment": 2935.437084,
        "scheduledPrincipalPayment": 6327.815754
    }
    {
        "date": "2050-10-25",
        "totalCashFlow": 9074.339851,
        "interestPayment": 106.523385,
        "principalBalance": 246688.308652,
        "principalPayment": 8967.816465,
        "endPrincipalBalance": 246688.308652,
        "beginPrincipalBalance": 255656.125117,
        "prepayPrincipalPayment": 2705.315117,
        "scheduledPrincipalPayment": 6262.501348
    }
    {
        "date": "2050-11-25",
        "totalCashFlow": 8837.856805,
        "interestPayment": 102.786795,
        "principalBalance": 237953.238642,
        "principalPayment": 8735.070009,
        "endPrincipalBalance": 237953.238642,
        "beginPrincipalBalance": 246688.308652,
        "prepayPrincipalPayment": 2534.048916,
        "scheduledPrincipalPayment": 6201.021094
    }
    {
        "date": "2050-12-25",
        "totalCashFlow": 8698.495155,
        "interestPayment": 99.147183,
        "principalBalance": 229353.89067,
        "principalPayment": 8599.347973,
        "endPrincipalBalance": 229353.89067,
        "beginPrincipalBalance": 237953.238642,
        "prepayPrincipalPayment": 2457.276591,
        "scheduledPrincipalPayment": 6142.071382
    }
    {
        "date": "2051-01-25",
        "totalCashFlow": 8581.065973,
        "interestPayment": 95.564121,
        "principalBalance": 220868.388817,
        "principalPayment": 8485.501852,
        "endPrincipalBalance": 220868.388817,
        "beginPrincipalBalance": 229353.89067,
        "prepayPrincipalPayment": 2402.208329,
        "scheduledPrincipalPayment": 6083.293523
    }
    {
        "date": "2051-02-25",
        "totalCashFlow": 8261.18641,
        "interestPayment": 92.028495,
        "principalBalance": 212699.230902,
        "principalPayment": 8169.157915,
        "endPrincipalBalance": 212699.230902,
        "beginPrincipalBalance": 220868.388817,
        "prepayPrincipalPayment": 2145.04705,
        "scheduledPrincipalPayment": 6024.110865
    }
    {
        "date": "2051-03-25",
        "totalCashFlow": 8161.650481,
        "interestPayment": 88.62468,
        "principalBalance": 204626.205101,
        "principalPayment": 8073.025801,
        "endPrincipalBalance": 204626.205101,
        "beginPrincipalBalance": 212699.230902,
        "prepayPrincipalPayment": 2102.848368,
        "scheduledPrincipalPayment": 5970.177434
    }
    {
        "date": "2051-04-25",
        "totalCashFlow": 8236.058159,
        "interestPayment": 85.260919,
        "principalBalance": 196475.407861,
        "principalPayment": 8150.79724,
        "endPrincipalBalance": 196475.407861,
        "beginPrincipalBalance": 204626.205101,
        "prepayPrincipalPayment": 2235.192788,
        "scheduledPrincipalPayment": 5915.604452
    }
    {
        "date": "2051-05-25",
        "totalCashFlow": 8109.596827,
        "interestPayment": 81.864753,
        "principalBalance": 188447.675786,
        "principalPayment": 8027.732074,
        "endPrincipalBalance": 188447.675786,
        "beginPrincipalBalance": 196475.407861,
        "prepayPrincipalPayment": 2172.576424,
        "scheduledPrincipalPayment": 5855.155651
    }
    {
        "date": "2051-06-25",
        "totalCashFlow": 8125.604164,
        "interestPayment": 78.519865,
        "principalBalance": 180400.591487,
        "principalPayment": 8047.084299,
        "endPrincipalBalance": 180400.591487,
        "beginPrincipalBalance": 188447.675786,
        "prepayPrincipalPayment": 2252.632629,
        "scheduledPrincipalPayment": 5794.45167
    }
    {
        "date": "2051-07-25",
        "totalCashFlow": 8014.069043,
        "interestPayment": 75.166913,
        "principalBalance": 172461.689357,
        "principalPayment": 7938.90213,
        "endPrincipalBalance": 172461.689357,
        "beginPrincipalBalance": 180400.591487,
        "prepayPrincipalPayment": 2209.951047,
        "scheduledPrincipalPayment": 5728.951084
    }
    {
        "date": "2051-08-25",
        "totalCashFlow": 7779.570463,
        "interestPayment": 71.859037,
        "principalBalance": 164753.977932,
        "principalPayment": 7707.711426,
        "endPrincipalBalance": 164753.977932,
        "beginPrincipalBalance": 172461.689357,
        "prepayPrincipalPayment": 2045.351055,
        "scheduledPrincipalPayment": 5662.36037
    }
    {
        "date": "2051-09-25",
        "totalCashFlow": 7724.810603,
        "interestPayment": 68.647491,
        "principalBalance": 157097.814819,
        "principalPayment": 7656.163112,
        "endPrincipalBalance": 157097.814819,
        "beginPrincipalBalance": 164753.977932,
        "prepayPrincipalPayment": 2057.410598,
        "scheduledPrincipalPayment": 5598.752514
    }
    {
        "date": "2051-10-25",
        "totalCashFlow": 7479.627963,
        "interestPayment": 65.457423,
        "principalBalance": 149683.644279,
        "principalPayment": 7414.17054,
        "endPrincipalBalance": 149683.644279,
        "beginPrincipalBalance": 157097.814819,
        "prepayPrincipalPayment": 1882.036844,
        "scheduledPrincipalPayment": 5532.133696
    }
    {
        "date": "2051-11-25",
        "totalCashFlow": 7352.634099,
        "interestPayment": 62.368185,
        "principalBalance": 142393.378365,
        "principalPayment": 7290.265914,
        "endPrincipalBalance": 142393.378365,
        "beginPrincipalBalance": 149683.644279,
        "prepayPrincipalPayment": 1821.13531,
        "scheduledPrincipalPayment": 5469.130604
    }
    {
        "date": "2051-12-25",
        "totalCashFlow": 7198.859824,
        "interestPayment": 59.330574,
        "principalBalance": 135253.849115,
        "principalPayment": 7139.529249,
        "endPrincipalBalance": 135253.849115,
        "beginPrincipalBalance": 142393.378365,
        "prepayPrincipalPayment": 1733.837546,
        "scheduledPrincipalPayment": 5405.691703
    }
    {
        "date": "2052-01-25",
        "totalCashFlow": 7060.07628,
        "interestPayment": 56.35577,
        "principalBalance": 128250.128606,
        "principalPayment": 7003.720509,
        "endPrincipalBalance": 128250.128606,
        "beginPrincipalBalance": 135253.849115,
        "prepayPrincipalPayment": 1660.888371,
        "scheduledPrincipalPayment": 5342.832138
    }
    {
        "date": "2052-02-25",
        "totalCashFlow": 6871.231669,
        "interestPayment": 53.437554,
        "principalBalance": 121432.33449,
        "principalPayment": 6817.794116,
        "endPrincipalBalance": 121432.33449,
        "beginPrincipalBalance": 128250.128606,
        "prepayPrincipalPayment": 1537.774803,
        "scheduledPrincipalPayment": 5280.019312
    }
    {
        "date": "2052-03-25",
        "totalCashFlow": 6761.016926,
        "interestPayment": 50.596806,
        "principalBalance": 114721.91437,
        "principalPayment": 6710.42012,
        "endPrincipalBalance": 114721.91437,
        "beginPrincipalBalance": 121432.33449,
        "prepayPrincipalPayment": 1490.99765,
        "scheduledPrincipalPayment": 5219.42247
    }
    {
        "date": "2052-04-25",
        "totalCashFlow": 6695.816595,
        "interestPayment": 47.800798,
        "principalBalance": 108073.898572,
        "principalPayment": 6648.015798,
        "endPrincipalBalance": 108073.898572,
        "beginPrincipalBalance": 114721.91437,
        "prepayPrincipalPayment": 1490.190746,
        "scheduledPrincipalPayment": 5157.825052
    }
    {
        "date": "2052-05-25",
        "totalCashFlow": 6616.98244,
        "interestPayment": 45.030791,
        "principalBalance": 101501.946923,
        "principalPayment": 6571.951649,
        "endPrincipalBalance": 101501.946923,
        "beginPrincipalBalance": 108073.898572,
        "prepayPrincipalPayment": 1478.978966,
        "scheduledPrincipalPayment": 5092.972683
    }
    {
        "date": "2052-06-25",
        "totalCashFlow": 6524.953569,
        "interestPayment": 42.292478,
        "principalBalance": 95019.285833,
        "principalPayment": 6482.661091,
        "endPrincipalBalance": 95019.285833,
        "beginPrincipalBalance": 101501.946923,
        "prepayPrincipalPayment": 1457.603057,
        "scheduledPrincipalPayment": 5025.058034
    }
    {
        "date": "2052-07-25",
        "totalCashFlow": 6358.253959,
        "interestPayment": 39.591369,
        "principalBalance": 88700.623243,
        "principalPayment": 6318.66259,
        "endPrincipalBalance": 88700.623243,
        "beginPrincipalBalance": 95019.285833,
        "prepayPrincipalPayment": 1364.369354,
        "scheduledPrincipalPayment": 4954.293235
    }
    {
        "date": "2052-08-25",
        "totalCashFlow": 6238.709137,
        "interestPayment": 36.958593,
        "principalBalance": 82498.872699,
        "principalPayment": 6201.750544,
        "endPrincipalBalance": 82498.872699,
        "beginPrincipalBalance": 88700.623243,
        "prepayPrincipalPayment": 1317.425966,
        "scheduledPrincipalPayment": 4884.324578
    }
    {
        "date": "2052-09-25",
        "totalCashFlow": 6075.539459,
        "interestPayment": 34.37453,
        "principalBalance": 76457.70777,
        "principalPayment": 6041.164929,
        "endPrincipalBalance": 76457.70777,
        "beginPrincipalBalance": 82498.872699,
        "prepayPrincipalPayment": 1228.604377,
        "scheduledPrincipalPayment": 4812.560551
    }
    {
        "date": "2052-10-25",
        "totalCashFlow": 5890.045364,
        "interestPayment": 31.857378,
        "principalBalance": 70599.519785,
        "principalPayment": 5858.187985,
        "endPrincipalBalance": 70599.519785,
        "beginPrincipalBalance": 76457.70777,
        "prepayPrincipalPayment": 1116.803989,
        "scheduledPrincipalPayment": 4741.383996
    }
    {
        "date": "2052-11-25",
        "totalCashFlow": 5754.532991,
        "interestPayment": 29.416467,
        "principalBalance": 64874.403261,
        "principalPayment": 5725.116524,
        "endPrincipalBalance": 64874.403261,
        "beginPrincipalBalance": 70599.519785,
        "prepayPrincipalPayment": 1052.705802,
        "scheduledPrincipalPayment": 4672.410722
    }
    {
        "date": "2052-12-25",
        "totalCashFlow": 5577.624124,
        "interestPayment": 27.031001,
        "principalBalance": 59323.810138,
        "principalPayment": 5550.593123,
        "endPrincipalBalance": 59323.810138,
        "beginPrincipalBalance": 64874.403261,
        "prepayPrincipalPayment": 948.000781,
        "scheduledPrincipalPayment": 4602.592341
    }
    {
        "date": "2053-01-25",
        "totalCashFlow": 5446.930399,
        "interestPayment": 24.718254,
        "principalBalance": 53901.597993,
        "principalPayment": 5422.212145,
        "endPrincipalBalance": 53901.597993,
        "beginPrincipalBalance": 59323.810138,
        "prepayPrincipalPayment": 887.293911,
        "scheduledPrincipalPayment": 4534.918234
    }
    {
        "date": "2053-02-25",
        "totalCashFlow": 5271.675988,
        "interestPayment": 22.458999,
        "principalBalance": 48652.381004,
        "principalPayment": 5249.216988,
        "endPrincipalBalance": 48652.381004,
        "beginPrincipalBalance": 53901.597993,
        "prepayPrincipalPayment": 783.093375,
        "scheduledPrincipalPayment": 4466.123613
    }
    {
        "date": "2053-03-25",
        "totalCashFlow": 5130.944302,
        "interestPayment": 20.271825,
        "principalBalance": 43541.708528,
        "principalPayment": 5110.672477,
        "endPrincipalBalance": 43541.708528,
        "beginPrincipalBalance": 48652.381004,
        "prepayPrincipalPayment": 710.716947,
        "scheduledPrincipalPayment": 4399.955529
    }
    {
        "date": "2053-04-25",
        "totalCashFlow": 5015.900748,
        "interestPayment": 18.142379,
        "principalBalance": 38543.950158,
        "principalPayment": 4997.758369,
        "endPrincipalBalance": 38543.950158,
        "beginPrincipalBalance": 43541.708528,
        "prepayPrincipalPayment": 663.958735,
        "scheduledPrincipalPayment": 4333.799634
    }
    {
        "date": "2053-05-25",
        "totalCashFlow": 4889.391645,
        "interestPayment": 16.059979,
        "principalBalance": 33670.618493,
        "principalPayment": 4873.331666,
        "endPrincipalBalance": 33670.618493,
        "beginPrincipalBalance": 38543.950158,
        "prepayPrincipalPayment": 608.483995,
        "scheduledPrincipalPayment": 4264.847671
    }
    {
        "date": "2053-06-25",
        "totalCashFlow": 4744.849254,
        "interestPayment": 14.029424,
        "principalBalance": 28939.798663,
        "principalPayment": 4730.819829,
        "endPrincipalBalance": 28939.798663,
        "beginPrincipalBalance": 33670.618493,
        "prepayPrincipalPayment": 537.313237,
        "scheduledPrincipalPayment": 4193.506592
    }
    {
        "date": "2053-07-25",
        "totalCashFlow": 4596.626896,
        "interestPayment": 12.058249,
        "principalBalance": 24355.230017,
        "principalPayment": 4584.568646,
        "endPrincipalBalance": 24355.230017,
        "beginPrincipalBalance": 28939.798663,
        "prepayPrincipalPayment": 463.213313,
        "scheduledPrincipalPayment": 4121.355333
    }
    {
        "date": "2053-08-25",
        "totalCashFlow": 4445.629553,
        "interestPayment": 10.148013,
        "principalBalance": 19919.748477,
        "principalPayment": 4435.48154,
        "endPrincipalBalance": 19919.748477,
        "beginPrincipalBalance": 24355.230017,
        "prepayPrincipalPayment": 386.834544,
        "scheduledPrincipalPayment": 4048.646996
    }
    {
        "date": "2053-09-25",
        "totalCashFlow": 4287.278501,
        "interestPayment": 8.299895,
        "principalBalance": 15640.769871,
        "principalPayment": 4278.978605,
        "endPrincipalBalance": 15640.769871,
        "beginPrincipalBalance": 19919.748477,
        "prepayPrincipalPayment": 303.320164,
        "scheduledPrincipalPayment": 3975.658441
    }
    {
        "date": "2053-10-25",
        "totalCashFlow": 4135.601416,
        "interestPayment": 6.516987,
        "principalBalance": 11511.685443,
        "principalPayment": 4129.084429,
        "endPrincipalBalance": 11511.685443,
        "beginPrincipalBalance": 15640.769871,
        "prepayPrincipalPayment": 224.996336,
        "scheduledPrincipalPayment": 3904.088093
    }
    {
        "date": "2053-11-25",
        "totalCashFlow": 3987.444772,
        "interestPayment": 4.796536,
        "principalBalance": 7529.037206,
        "principalPayment": 3982.648237,
        "endPrincipalBalance": 7529.037206,
        "beginPrincipalBalance": 11511.685443,
        "prepayPrincipalPayment": 149.414094,
        "scheduledPrincipalPayment": 3833.234142
    }
    {
        "date": "2053-12-25",
        "totalCashFlow": 3837.818275,
        "interestPayment": 3.137099,
        "principalBalance": 3694.35603,
        "principalPayment": 3834.681176,
        "endPrincipalBalance": 3694.35603,
        "beginPrincipalBalance": 7529.037206,
        "prepayPrincipalPayment": 72.122239,
        "scheduledPrincipalPayment": 3762.558937
    }
    {
        "date": "2054-01-25",
        "totalCashFlow": 3695.895345,
        "interestPayment": 1.539315,
        "principalBalance": 0.0,
        "principalPayment": 3694.35603,
        "endPrincipalBalance": 0.0,
        "beginPrincipalBalance": 3694.35603,
        "prepayPrincipalPayment": 0.0,
        "scheduledPrincipalPayment": 3694.35603
    }

    """

    try:
        logger.info("Calling post_cash_flow_async")

        response = Client().yield_book_rest.post_cash_flow_async(
            body=CashFlowRequestData(global_settings=global_settings, input=input, keywords=keywords),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
            content_type="application/json",
        )

        output = response
        logger.info("Called post_cash_flow_async")

        return output
    except Exception as err:
        logger.error("Error post_cash_flow_async.")
        check_exception_and_raise(err, logger)


def post_cash_flow_sync(
    *,
    global_settings: Optional[CashFlowGlobalSettings] = None,
    input: Optional[List[CashFlowInput]] = None,
    keywords: Optional[List[str]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Post cash flow sync.

    Parameters
    ----------
    global_settings : CashFlowGlobalSettings, optional

    input : List[CashFlowInput], optional

    keywords : List[str], optional
        Optional. Used to specify the keywords a user will retrieve in the response. All keywords are returned by default.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------
    >>> # Formulate API Request body parameters - Global Settings
    >>> global_settings = CashFlowGlobalSettings(
    >>>         )
    >>>
    >>> # Formulate API Request body parameters - Input
    >>> input = CashFlowInput(
    >>>             identifier="01F002628",
    >>>             par_amount="10000"
    >>>         )
    >>>
    >>> # Execute API Post sync request with prepared inputs
    >>> cf_async_get_response = post_cash_flow_sync(
    >>>                             global_settings=global_settings,
    >>>                             input=[input]
    >>>                         )
    >>>
    >>> # Print output to a file, as CF output is too long for terminal printout
    >>> # print(js.dumps(cf_async_get_response, indent=4), file=open('.CF_sync_post_output.json', 'w+'))
    >>>
    >>> # Print onyl payment information
    >>> for paymentInfo in cf_async_get_response["results"][0]["cashFlow"]["dataPaymentList"]:
    >>>     print(js.dumps(paymentInfo, indent=4))
    {
        "date": "2026-03-25",
        "totalCashFlow": 44388.458814,
        "interestPayment": 4166.666667,
        "principalBalance": 9959778.207853,
        "principalPayment": 40221.792147,
        "endPrincipalBalance": 9959778.207853,
        "beginPrincipalBalance": 10000000.0,
        "prepayPrincipalPayment": 15261.689129,
        "scheduledPrincipalPayment": 24960.103018
    }
    {
        "date": "2026-04-25",
        "totalCashFlow": 47982.609901,
        "interestPayment": 4149.907587,
        "principalBalance": 9915945.505539,
        "principalPayment": 43832.702314,
        "endPrincipalBalance": 9915945.505539,
        "beginPrincipalBalance": 9959778.207853,
        "prepayPrincipalPayment": 18884.827621,
        "scheduledPrincipalPayment": 24947.874693
    }
    {
        "date": "2026-05-25",
        "totalCashFlow": 50190.816923,
        "interestPayment": 4131.643961,
        "principalBalance": 9869886.332577,
        "principalPayment": 46059.172962,
        "endPrincipalBalance": 9869886.332577,
        "beginPrincipalBalance": 9915945.505539,
        "prepayPrincipalPayment": 21132.782982,
        "scheduledPrincipalPayment": 24926.38998
    }
    {
        "date": "2026-06-25",
        "totalCashFlow": 50465.372076,
        "interestPayment": 4112.452639,
        "principalBalance": 9823533.413139,
        "principalPayment": 46352.919438,
        "endPrincipalBalance": 9823533.413139,
        "beginPrincipalBalance": 9869886.332577,
        "prepayPrincipalPayment": 21453.87674,
        "scheduledPrincipalPayment": 24899.042698
    }
    {
        "date": "2026-07-25",
        "totalCashFlow": 53012.385342,
        "interestPayment": 4093.138922,
        "principalBalance": 9774614.166719,
        "principalPayment": 48919.24642,
        "endPrincipalBalance": 9774614.166719,
        "beginPrincipalBalance": 9823533.413139,
        "prepayPrincipalPayment": 24048.582925,
        "scheduledPrincipalPayment": 24870.663495
    }
    {
        "date": "2026-08-25",
        "totalCashFlow": 52874.355106,
        "interestPayment": 4072.755903,
        "principalBalance": 9725812.567517,
        "principalPayment": 48801.599203,
        "endPrincipalBalance": 9725812.567517,
        "beginPrincipalBalance": 9774614.166719,
        "prepayPrincipalPayment": 23966.131721,
        "scheduledPrincipalPayment": 24835.467482
    }
    {
        "date": "2026-09-25",
        "totalCashFlow": 51621.072654,
        "interestPayment": 4052.421903,
        "principalBalance": 9678243.916766,
        "principalPayment": 47568.650751,
        "endPrincipalBalance": 9678243.916766,
        "beginPrincipalBalance": 9725812.567517,
        "prepayPrincipalPayment": 22768.425156,
        "scheduledPrincipalPayment": 24800.225595
    }
    {
        "date": "2026-10-25",
        "totalCashFlow": 51171.25269,
        "interestPayment": 4032.601632,
        "principalBalance": 9631105.265708,
        "principalPayment": 47138.651058,
        "endPrincipalBalance": 9631105.265708,
        "beginPrincipalBalance": 9678243.916766,
        "prepayPrincipalPayment": 22370.859037,
        "scheduledPrincipalPayment": 24767.79202
    }
    {
        "date": "2026-11-25",
        "totalCashFlow": 50444.331088,
        "interestPayment": 4012.960527,
        "principalBalance": 9584673.895147,
        "principalPayment": 46431.370561,
        "endPrincipalBalance": 9584673.895147,
        "beginPrincipalBalance": 9631105.265708,
        "prepayPrincipalPayment": 21695.235153,
        "scheduledPrincipalPayment": 24736.135408
    }
    {
        "date": "2026-12-25",
        "totalCashFlow": 48825.848159,
        "interestPayment": 3993.614123,
        "principalBalance": 9539841.661111,
        "principalPayment": 44832.234036,
        "endPrincipalBalance": 9539841.661111,
        "beginPrincipalBalance": 9584673.895147,
        "prepayPrincipalPayment": 20126.254644,
        "scheduledPrincipalPayment": 24705.979391
    }
    {
        "date": "2027-01-25",
        "totalCashFlow": 50453.50088,
        "interestPayment": 3974.934025,
        "principalBalance": 9493363.094257,
        "principalPayment": 46478.566854,
        "endPrincipalBalance": 9493363.094257,
        "beginPrincipalBalance": 9539841.661111,
        "prepayPrincipalPayment": 21798.918852,
        "scheduledPrincipalPayment": 24679.648002
    }
    {
        "date": "2027-02-25",
        "totalCashFlow": 45469.973242,
        "interestPayment": 3955.567956,
        "principalBalance": 9451848.68897,
        "principalPayment": 41514.405286,
        "endPrincipalBalance": 9451848.68897,
        "beginPrincipalBalance": 9493363.094257,
        "prepayPrincipalPayment": 16865.648464,
        "scheduledPrincipalPayment": 24648.756822
    }
    {
        "date": "2027-03-25",
        "totalCashFlow": 46301.151236,
        "interestPayment": 3938.270287,
        "principalBalance": 9409485.808021,
        "principalPayment": 42362.880949,
        "endPrincipalBalance": 9409485.808021,
        "beginPrincipalBalance": 9451848.68897,
        "prepayPrincipalPayment": 17732.398372,
        "scheduledPrincipalPayment": 24630.482578
    }
    {
        "date": "2027-04-25",
        "totalCashFlow": 50312.157811,
        "interestPayment": 3920.619087,
        "principalBalance": 9363094.269296,
        "principalPayment": 46391.538725,
        "endPrincipalBalance": 9363094.269296,
        "beginPrincipalBalance": 9409485.808021,
        "prepayPrincipalPayment": 21781.777072,
        "scheduledPrincipalPayment": 24609.761653
    }
    {
        "date": "2027-05-25",
        "totalCashFlow": 51933.332953,
        "interestPayment": 3901.289279,
        "principalBalance": 9315062.225622,
        "principalPayment": 48032.043674,
        "endPrincipalBalance": 9315062.225622,
        "beginPrincipalBalance": 9363094.269296,
        "prepayPrincipalPayment": 23453.824244,
        "scheduledPrincipalPayment": 24578.219431
    }
    {
        "date": "2027-06-25",
        "totalCashFlow": 52050.96994,
        "interestPayment": 3881.275927,
        "principalBalance": 9266892.531609,
        "principalPayment": 48169.694012,
        "endPrincipalBalance": 9266892.531609,
        "beginPrincipalBalance": 9315062.225622,
        "prepayPrincipalPayment": 23627.66514,
        "scheduledPrincipalPayment": 24542.028872
    }
    {
        "date": "2027-07-25",
        "totalCashFlow": 54682.664688,
        "interestPayment": 3861.205222,
        "principalBalance": 9216071.072143,
        "principalPayment": 50821.459466,
        "endPrincipalBalance": 9216071.072143,
        "beginPrincipalBalance": 9266892.531609,
        "prepayPrincipalPayment": 26316.346322,
        "scheduledPrincipalPayment": 24505.113145
    }
    {
        "date": "2027-08-25",
        "totalCashFlow": 53324.385968,
        "interestPayment": 3840.029613,
        "principalBalance": 9166586.715788,
        "principalPayment": 49484.356355,
        "endPrincipalBalance": 9166586.715788,
        "beginPrincipalBalance": 9216071.072143,
        "prepayPrincipalPayment": 25023.564458,
        "scheduledPrincipalPayment": 24460.791897
    }
    {
        "date": "2027-09-25",
        "totalCashFlow": 53503.738292,
        "interestPayment": 3819.411132,
        "principalBalance": 9116902.388628,
        "principalPayment": 49684.32716,
        "endPrincipalBalance": 9116902.388628,
        "beginPrincipalBalance": 9166586.715788,
        "prepayPrincipalPayment": 25264.717563,
        "scheduledPrincipalPayment": 24419.609597
    }
    {
        "date": "2027-10-25",
        "totalCashFlow": 51886.461223,
        "interestPayment": 3798.709329,
        "principalBalance": 9068814.636734,
        "principalPayment": 48087.751895,
        "endPrincipalBalance": 9068814.636734,
        "beginPrincipalBalance": 9116902.388628,
        "prepayPrincipalPayment": 23710.259997,
        "scheduledPrincipalPayment": 24377.491898
    }
    {
        "date": "2027-11-25",
        "totalCashFlow": 50193.39363,
        "interestPayment": 3778.672765,
        "principalBalance": 9022399.915869,
        "principalPayment": 46414.720865,
        "endPrincipalBalance": 9022399.915869,
        "beginPrincipalBalance": 9068814.636734,
        "prepayPrincipalPayment": 22075.470299,
        "scheduledPrincipalPayment": 24339.250566
    }
    {
        "date": "2027-12-25",
        "totalCashFlow": 49998.876976,
        "interestPayment": 3759.333298,
        "principalBalance": 8976160.372191,
        "principalPayment": 46239.543678,
        "endPrincipalBalance": 8976160.372191,
        "beginPrincipalBalance": 9022399.915869,
        "prepayPrincipalPayment": 21934.408082,
        "scheduledPrincipalPayment": 24305.135595
    }
    {
        "date": "2028-01-25",
        "totalCashFlow": 50278.022827,
        "interestPayment": 3740.066822,
        "principalBalance": 8929622.416186,
        "principalPayment": 46537.956005,
        "endPrincipalBalance": 8929622.416186,
        "beginPrincipalBalance": 8976160.372191,
        "prepayPrincipalPayment": 22266.812237,
        "scheduledPrincipalPayment": 24271.143768
    }
    {
        "date": "2028-02-25",
        "totalCashFlow": 46259.973026,
        "interestPayment": 3720.676007,
        "principalBalance": 8887083.119167,
        "principalPayment": 42539.297019,
        "endPrincipalBalance": 8887083.119167,
        "beginPrincipalBalance": 8929622.416186,
        "prepayPrincipalPayment": 18303.305423,
        "scheduledPrincipalPayment": 24235.991596
    }
    {
        "date": "2028-03-25",
        "totalCashFlow": 47276.005827,
        "interestPayment": 3702.9513,
        "principalBalance": 8843510.06464,
        "principalPayment": 43573.054528,
        "endPrincipalBalance": 8843510.06464,
        "beginPrincipalBalance": 8887083.119167,
        "prepayPrincipalPayment": 19361.681404,
        "scheduledPrincipalPayment": 24211.373123
    }
    {
        "date": "2028-04-25",
        "totalCashFlow": 51520.936796,
        "interestPayment": 3684.79586,
        "principalBalance": 8795673.923704,
        "principalPayment": 47836.140935,
        "endPrincipalBalance": 8795673.923704,
        "beginPrincipalBalance": 8843510.06464,
        "prepayPrincipalPayment": 23652.494488,
        "scheduledPrincipalPayment": 24183.646447
    }
    {
        "date": "2028-05-25",
        "totalCashFlow": 50835.671472,
        "interestPayment": 3664.864135,
        "principalBalance": 8748503.116367,
        "principalPayment": 47170.807337,
        "endPrincipalBalance": 8748503.116367,
        "beginPrincipalBalance": 8795673.923704,
        "prepayPrincipalPayment": 23026.895117,
        "scheduledPrincipalPayment": 24143.91222
    }
    {
        "date": "2028-06-25",
        "totalCashFlow": 55323.044772,
        "interestPayment": 3645.209632,
        "principalBalance": 8696825.281227,
        "principalPayment": 51677.83514,
        "endPrincipalBalance": 8696825.281227,
        "beginPrincipalBalance": 8748503.116367,
        "prepayPrincipalPayment": 27572.221287,
        "scheduledPrincipalPayment": 24105.613853
    }
    {
        "date": "2028-07-25",
        "totalCashFlow": 56413.342255,
        "interestPayment": 3623.677201,
        "principalBalance": 8644035.616172,
        "principalPayment": 52789.665054,
        "endPrincipalBalance": 8644035.616172,
        "beginPrincipalBalance": 8696825.281227,
        "prepayPrincipalPayment": 28735.202918,
        "scheduledPrincipalPayment": 24054.462136
    }
    {
        "date": "2028-08-25",
        "totalCashFlow": 53958.59513,
        "interestPayment": 3601.681507,
        "principalBalance": 8593678.702549,
        "principalPayment": 50356.913624,
        "endPrincipalBalance": 8593678.702549,
        "beginPrincipalBalance": 8644035.616172,
        "prepayPrincipalPayment": 26357.176625,
        "scheduledPrincipalPayment": 23999.736999
    }
    {
        "date": "2028-09-25",
        "totalCashFlow": 56290.502702,
        "interestPayment": 3580.699459,
        "principalBalance": 8540968.899306,
        "principalPayment": 52709.803242,
        "endPrincipalBalance": 8540968.899306,
        "beginPrincipalBalance": 8593678.702549,
        "prepayPrincipalPayment": 28758.526099,
        "scheduledPrincipalPayment": 23951.277143
    }
    {
        "date": "2028-10-25",
        "totalCashFlow": 52458.075434,
        "interestPayment": 3558.737041,
        "principalBalance": 8492069.560914,
        "principalPayment": 48899.338393,
        "endPrincipalBalance": 8492069.560914,
        "beginPrincipalBalance": 8540968.899306,
        "prepayPrincipalPayment": 25003.57208,
        "scheduledPrincipalPayment": 23895.766313
    }
    {
        "date": "2028-11-25",
        "totalCashFlow": 52395.265386,
        "interestPayment": 3538.362317,
        "principalBalance": 8443212.657844,
        "principalPayment": 48856.903069,
        "endPrincipalBalance": 8443212.657844,
        "beginPrincipalBalance": 8492069.560914,
        "prepayPrincipalPayment": 25006.469209,
        "scheduledPrincipalPayment": 23850.43386
    }
    {
        "date": "2028-12-25",
        "totalCashFlow": 51261.365907,
        "interestPayment": 3518.005274,
        "principalBalance": 8395469.297212,
        "principalPayment": 47743.360633,
        "endPrincipalBalance": 8395469.297212,
        "beginPrincipalBalance": 8443212.657844,
        "prepayPrincipalPayment": 23938.585755,
        "scheduledPrincipalPayment": 23804.774878
    }
    {
        "date": "2029-01-25",
        "totalCashFlow": 50668.611909,
        "interestPayment": 3498.112207,
        "principalBalance": 8348298.79751,
        "principalPayment": 47170.499702,
        "endPrincipalBalance": 8348298.79751,
        "beginPrincipalBalance": 8395469.297212,
        "prepayPrincipalPayment": 23408.681907,
        "scheduledPrincipalPayment": 23761.817794
    }
    {
        "date": "2029-02-25",
        "totalCashFlow": 47704.901782,
        "interestPayment": 3478.457832,
        "principalBalance": 8304072.353561,
        "principalPayment": 44226.443949,
        "endPrincipalBalance": 8304072.353561,
        "beginPrincipalBalance": 8348298.79751,
        "prepayPrincipalPayment": 20506.385453,
        "scheduledPrincipalPayment": 23720.058496
    }
    {
        "date": "2029-03-25",
        "totalCashFlow": 47386.823123,
        "interestPayment": 3460.030147,
        "principalBalance": 8260145.560585,
        "principalPayment": 43926.792976,
        "endPrincipalBalance": 8260145.560585,
        "beginPrincipalBalance": 8304072.353561,
        "prepayPrincipalPayment": 20240.517855,
        "scheduledPrincipalPayment": 23686.275121
    }
    {
        "date": "2029-04-25",
        "totalCashFlow": 51714.882098,
        "interestPayment": 3441.727317,
        "principalBalance": 8211872.405803,
        "principalPayment": 48273.154782,
        "endPrincipalBalance": 8211872.405803,
        "beginPrincipalBalance": 8260145.560585,
        "prepayPrincipalPayment": 24620.165334,
        "scheduledPrincipalPayment": 23652.989447
    }
    {
        "date": "2029-05-25",
        "totalCashFlow": 53818.444952,
        "interestPayment": 3421.613502,
        "principalBalance": 8161475.574354,
        "principalPayment": 50396.831449,
        "endPrincipalBalance": 8161475.574354,
        "beginPrincipalBalance": 8211872.405803,
        "prepayPrincipalPayment": 26789.979607,
        "scheduledPrincipalPayment": 23606.851842
    }
    {
        "date": "2029-06-25",
        "totalCashFlow": 57424.247186,
        "interestPayment": 3400.614823,
        "principalBalance": 8107451.941991,
        "principalPayment": 54023.632364,
        "endPrincipalBalance": 8107451.941991,
        "beginPrincipalBalance": 8161475.574354,
        "prepayPrincipalPayment": 30469.506285,
        "scheduledPrincipalPayment": 23554.126079
    }
    {
        "date": "2029-07-25",
        "totalCashFlow": 57260.219057,
        "interestPayment": 3378.104976,
        "principalBalance": 8053569.827909,
        "principalPayment": 53882.114081,
        "endPrincipalBalance": 8053569.827909,
        "beginPrincipalBalance": 8107451.941991,
        "prepayPrincipalPayment": 30391.734233,
        "scheduledPrincipalPayment": 23490.379848
    }
    {
        "date": "2029-08-25",
        "totalCashFlow": 56714.159057,
        "interestPayment": 3355.654095,
        "principalBalance": 8000211.322947,
        "principalPayment": 53358.504962,
        "endPrincipalBalance": 8000211.322947,
        "beginPrincipalBalance": 8053569.827909,
        "prepayPrincipalPayment": 29932.060278,
        "scheduledPrincipalPayment": 23426.444684
    }
    {
        "date": "2029-09-25",
        "totalCashFlow": 57965.642689,
        "interestPayment": 3333.421385,
        "principalBalance": 7945579.101642,
        "principalPayment": 54632.221305,
        "endPrincipalBalance": 7945579.101642,
        "beginPrincipalBalance": 8000211.322947,
        "prepayPrincipalPayment": 31268.786233,
        "scheduledPrincipalPayment": 23363.435072
    }
    {
        "date": "2029-10-25",
        "totalCashFlow": 52388.065775,
        "interestPayment": 3310.657959,
        "principalBalance": 7896501.693826,
        "principalPayment": 49077.407816,
        "endPrincipalBalance": 7896501.693826,
        "beginPrincipalBalance": 7945579.101642,
        "prepayPrincipalPayment": 25781.314558,
        "scheduledPrincipalPayment": 23296.093258
    }
    {
        "date": "2029-11-25",
        "totalCashFlow": 54268.961942,
        "interestPayment": 3290.209039,
        "principalBalance": 7845522.940923,
        "principalPayment": 50978.752903,
        "endPrincipalBalance": 7845522.940923,
        "beginPrincipalBalance": 7896501.693826,
        "prepayPrincipalPayment": 27734.283825,
        "scheduledPrincipalPayment": 23244.469078
    }
    {
        "date": "2029-12-25",
        "totalCashFlow": 51853.914591,
        "interestPayment": 3268.967892,
        "principalBalance": 7796937.994223,
        "principalPayment": 48584.946699,
        "endPrincipalBalance": 7796937.994223,
        "beginPrincipalBalance": 7845522.940923,
        "prepayPrincipalPayment": 25398.230738,
        "scheduledPrincipalPayment": 23186.715961
    }
    {
        "date": "2030-01-25",
        "totalCashFlow": 51055.421479,
        "interestPayment": 3248.724164,
        "principalBalance": 7749131.296908,
        "principalPayment": 47806.697315,
        "endPrincipalBalance": 7749131.296908,
        "beginPrincipalBalance": 7796937.994223,
        "prepayPrincipalPayment": 24671.19156,
        "scheduledPrincipalPayment": 23135.505755
    }
    {
        "date": "2030-02-25",
        "totalCashFlow": 47693.262332,
        "interestPayment": 3228.804707,
        "principalBalance": 7704666.839284,
        "principalPayment": 44464.457625,
        "endPrincipalBalance": 7704666.839284,
        "beginPrincipalBalance": 7749131.296908,
        "prepayPrincipalPayment": 21378.352458,
        "scheduledPrincipalPayment": 23086.105166
    }
    {
        "date": "2030-03-25",
        "totalCashFlow": 47181.950732,
        "interestPayment": 3210.27785,
        "principalBalance": 7660695.166401,
        "principalPayment": 43971.672883,
        "endPrincipalBalance": 7660695.166401,
        "beginPrincipalBalance": 7704666.839284,
        "prepayPrincipalPayment": 20925.466637,
        "scheduledPrincipalPayment": 23046.206246
    }
    {
        "date": "2030-04-25",
        "totalCashFlow": 51173.76293,
        "interestPayment": 3191.956319,
        "principalBalance": 7612713.359791,
        "principalPayment": 47981.806611,
        "endPrincipalBalance": 7612713.359791,
        "beginPrincipalBalance": 7660695.166401,
        "prepayPrincipalPayment": 24974.439358,
        "scheduledPrincipalPayment": 23007.367253
    }
    {
        "date": "2030-05-25",
        "totalCashFlow": 54256.264604,
        "interestPayment": 3171.9639,
        "principalBalance": 7561629.059087,
        "principalPayment": 51084.300704,
        "endPrincipalBalance": 7561629.059087,
        "beginPrincipalBalance": 7612713.359791,
        "prepayPrincipalPayment": 28128.277492,
        "scheduledPrincipalPayment": 22956.023212
    }
    {
        "date": "2030-06-25",
        "totalCashFlow": 57289.417875,
        "interestPayment": 3150.678775,
        "principalBalance": 7507490.319987,
        "principalPayment": 54138.7391,
        "endPrincipalBalance": 7507490.319987,
        "beginPrincipalBalance": 7561629.059087,
        "prepayPrincipalPayment": 31243.968934,
        "scheduledPrincipalPayment": 22894.770166
    }
    {
        "date": "2030-07-25",
        "totalCashFlow": 55743.611242,
        "interestPayment": 3128.120967,
        "principalBalance": 7454874.829711,
        "principalPayment": 52615.490276,
        "endPrincipalBalance": 7454874.829711,
        "beginPrincipalBalance": 7507490.319987,
        "prepayPrincipalPayment": 29791.856648,
        "scheduledPrincipalPayment": 22823.633628
    }
    {
        "date": "2030-08-25",
        "totalCashFlow": 57649.89698,
        "interestPayment": 3106.197846,
        "principalBalance": 7400331.130576,
        "principalPayment": 54543.699135,
        "endPrincipalBalance": 7400331.130576,
        "beginPrincipalBalance": 7454874.829711,
        "prepayPrincipalPayment": 31787.232375,
        "scheduledPrincipalPayment": 22756.46676
    }
    {
        "date": "2030-09-25",
        "totalCashFlow": 56431.526975,
        "interestPayment": 3083.471304,
        "principalBalance": 7346983.074905,
        "principalPayment": 53348.055671,
        "endPrincipalBalance": 7346983.074905,
        "beginPrincipalBalance": 7400331.130576,
        "prepayPrincipalPayment": 30665.315242,
        "scheduledPrincipalPayment": 22682.740429
    }
    {
        "date": "2030-10-25",
        "totalCashFlow": 52898.299536,
        "interestPayment": 3061.242948,
        "principalBalance": 7297146.018317,
        "principalPayment": 49837.056588,
        "endPrincipalBalance": 7297146.018317,
        "beginPrincipalBalance": 7346983.074905,
        "prepayPrincipalPayment": 27225.067693,
        "scheduledPrincipalPayment": 22611.988896
    }
    {
        "date": "2030-11-25",
        "totalCashFlow": 53632.879501,
        "interestPayment": 3040.477508,
        "principalBalance": 7246553.616324,
        "principalPayment": 50592.401993,
        "endPrincipalBalance": 7246553.616324,
        "beginPrincipalBalance": 7297146.018317,
        "prepayPrincipalPayment": 28040.996431,
        "scheduledPrincipalPayment": 22551.405562
    }
    {
        "date": "2030-12-25",
        "totalCashFlow": 50022.635212,
        "interestPayment": 3019.39734,
        "principalBalance": 7199550.378452,
        "principalPayment": 47003.237872,
        "endPrincipalBalance": 7199550.378452,
        "beginPrincipalBalance": 7246553.616324,
        "prepayPrincipalPayment": 24515.359527,
        "scheduledPrincipalPayment": 22487.878345
    }
    {
        "date": "2031-01-25",
        "totalCashFlow": 51224.24979,
        "interestPayment": 2999.812658,
        "principalBalance": 7151325.94132,
        "principalPayment": 48224.437132,
        "endPrincipalBalance": 7151325.94132,
        "beginPrincipalBalance": 7199550.378452,
        "prepayPrincipalPayment": 25789.527556,
        "scheduledPrincipalPayment": 22434.909576
    }
    {
        "date": "2031-02-25",
        "totalCashFlow": 46694.063742,
        "interestPayment": 2979.719142,
        "principalBalance": 7107611.59672,
        "principalPayment": 43714.3446,
        "endPrincipalBalance": 7107611.59672,
        "beginPrincipalBalance": 7151325.94132,
        "prepayPrincipalPayment": 21336.764656,
        "scheduledPrincipalPayment": 22377.579944
    }
    {
        "date": "2031-03-25",
        "totalCashFlow": 46131.448046,
        "interestPayment": 2961.504832,
        "principalBalance": 7064441.653506,
        "principalPayment": 43169.943214,
        "endPrincipalBalance": 7064441.653506,
        "beginPrincipalBalance": 7107611.59672,
        "prepayPrincipalPayment": 20836.098596,
        "scheduledPrincipalPayment": 22333.844618
    }
    {
        "date": "2031-04-25",
        "totalCashFlow": 50194.655989,
        "interestPayment": 2943.517356,
        "principalBalance": 7017190.514873,
        "principalPayment": 47251.138634,
        "endPrincipalBalance": 7017190.514873,
        "beginPrincipalBalance": 7064441.653506,
        "prepayPrincipalPayment": 24959.776477,
        "scheduledPrincipalPayment": 22291.362156
    }
    {
        "date": "2031-05-25",
        "totalCashFlow": 53329.17828,
        "interestPayment": 2923.829381,
        "principalBalance": 6966785.165974,
        "principalPayment": 50405.348899,
        "endPrincipalBalance": 6966785.165974,
        "beginPrincipalBalance": 7017190.514873,
        "prepayPrincipalPayment": 28169.857045,
        "scheduledPrincipalPayment": 22235.491854
    }
    {
        "date": "2031-06-25",
        "totalCashFlow": 55153.433529,
        "interestPayment": 2902.827152,
        "principalBalance": 6914534.559597,
        "principalPayment": 52250.606377,
        "endPrincipalBalance": 6914534.559597,
        "beginPrincipalBalance": 6966785.165974,
        "prepayPrincipalPayment": 30081.591885,
        "scheduledPrincipalPayment": 22169.014492
    }
    {
        "date": "2031-07-25",
        "totalCashFlow": 56103.07118,
        "interestPayment": 2881.056066,
        "principalBalance": 6861312.544483,
        "principalPayment": 53222.015114,
        "endPrincipalBalance": 6861312.544483,
        "beginPrincipalBalance": 6914534.559597,
        "prepayPrincipalPayment": 31126.036165,
        "scheduledPrincipalPayment": 22095.978949
    }
    {
        "date": "2031-08-25",
        "totalCashFlow": 56662.721083,
        "interestPayment": 2858.880227,
        "principalBalance": 6807508.703628,
        "principalPayment": 53803.840856,
        "endPrincipalBalance": 6807508.703628,
        "beginPrincipalBalance": 6861312.544483,
        "prepayPrincipalPayment": 31784.733951,
        "scheduledPrincipalPayment": 22019.106904
    }
    {
        "date": "2031-09-25",
        "totalCashFlow": 54144.523091,
        "interestPayment": 2836.46196,
        "principalBalance": 6756200.642496,
        "principalPayment": 51308.061131,
        "endPrincipalBalance": 6756200.642496,
        "beginPrincipalBalance": 6807508.703628,
        "prepayPrincipalPayment": 29368.455211,
        "scheduledPrincipalPayment": 21939.605921
    }
    {
        "date": "2031-10-25",
        "totalCashFlow": 52881.0798,
        "interestPayment": 2815.083601,
        "principalBalance": 6706134.646297,
        "principalPayment": 50065.996199,
        "endPrincipalBalance": 6706134.646297,
        "beginPrincipalBalance": 6756200.642496,
        "prepayPrincipalPayment": 28198.591706,
        "scheduledPrincipalPayment": 21867.404494
    }
    {
        "date": "2031-11-25",
        "totalCashFlow": 52406.608698,
        "interestPayment": 2794.222769,
        "principalBalance": 6656522.260369,
        "principalPayment": 49612.385928,
        "endPrincipalBalance": 6656522.260369,
        "beginPrincipalBalance": 6706134.646297,
        "prepayPrincipalPayment": 27813.863386,
        "scheduledPrincipalPayment": 21798.522543
    }
    {
        "date": "2031-12-25",
        "totalCashFlow": 47638.108444,
        "interestPayment": 2773.550942,
        "principalBalance": 6611657.702867,
        "principalPayment": 44864.557502,
        "endPrincipalBalance": 6611657.702867,
        "beginPrincipalBalance": 6656522.260369,
        "prepayPrincipalPayment": 23134.127413,
        "scheduledPrincipalPayment": 21730.430089
    }
    {
        "date": "2032-01-25",
        "totalCashFlow": 50910.364665,
        "interestPayment": 2754.857376,
        "principalBalance": 6563502.195577,
        "principalPayment": 48155.507289,
        "endPrincipalBalance": 6563502.195577,
        "beginPrincipalBalance": 6611657.702867,
        "prepayPrincipalPayment": 26478.289713,
        "scheduledPrincipalPayment": 21677.217576
    }
    {
        "date": "2032-02-25",
        "totalCashFlow": 44442.304719,
        "interestPayment": 2734.792581,
        "principalBalance": 6521794.68344,
        "principalPayment": 41707.512138,
        "endPrincipalBalance": 6521794.68344,
        "beginPrincipalBalance": 6563502.195577,
        "prepayPrincipalPayment": 20094.903086,
        "scheduledPrincipalPayment": 21612.609052
    }
    {
        "date": "2032-03-25",
        "totalCashFlow": 44656.504626,
        "interestPayment": 2717.414451,
        "principalBalance": 6479855.593266,
        "principalPayment": 41939.090174,
        "endPrincipalBalance": 6479855.593266,
        "beginPrincipalBalance": 6521794.68344,
        "prepayPrincipalPayment": 20370.425191,
        "scheduledPrincipalPayment": 21568.664983
    }
    {
        "date": "2032-04-25",
        "totalCashFlow": 50204.208159,
        "interestPayment": 2699.939831,
        "principalBalance": 6432351.324937,
        "principalPayment": 47504.268328,
        "endPrincipalBalance": 6432351.324937,
        "beginPrincipalBalance": 6479855.593266,
        "prepayPrincipalPayment": 25980.798332,
        "scheduledPrincipalPayment": 21523.469996
    }
    {
        "date": "2032-05-25",
        "totalCashFlow": 52393.67496,
        "interestPayment": 2680.146385,
        "principalBalance": 6382637.796363,
        "principalPayment": 49713.528575,
        "endPrincipalBalance": 6382637.796363,
        "beginPrincipalBalance": 6432351.324937,
        "prepayPrincipalPayment": 28254.313839,
        "scheduledPrincipalPayment": 21459.214736
    }
    {
        "date": "2032-06-25",
        "totalCashFlow": 52371.812087,
        "interestPayment": 2659.432415,
        "principalBalance": 6332925.416691,
        "principalPayment": 49712.379672,
        "endPrincipalBalance": 6332925.416691,
        "beginPrincipalBalance": 6382637.796363,
        "prepayPrincipalPayment": 28325.485925,
        "scheduledPrincipalPayment": 21386.893747
    }
    {
        "date": "2032-07-25",
        "totalCashFlow": 55851.892061,
        "interestPayment": 2638.718924,
        "principalBalance": 6279712.243554,
        "principalPayment": 53213.173137,
        "endPrincipalBalance": 6279712.243554,
        "beginPrincipalBalance": 6332925.416691,
        "prepayPrincipalPayment": 31899.332499,
        "scheduledPrincipalPayment": 21313.840638
    }
    {
        "date": "2032-08-25",
        "totalCashFlow": 53729.717513,
        "interestPayment": 2616.546768,
        "principalBalance": 6228599.072809,
        "principalPayment": 51113.170745,
        "endPrincipalBalance": 6228599.072809,
        "beginPrincipalBalance": 6279712.243554,
        "prepayPrincipalPayment": 29884.962061,
        "scheduledPrincipalPayment": 21228.208683
    }
    {
        "date": "2032-09-25",
        "totalCashFlow": 53626.633065,
        "interestPayment": 2595.249614,
        "principalBalance": 6177567.689358,
        "principalPayment": 51031.383451,
        "endPrincipalBalance": 6177567.689358,
        "beginPrincipalBalance": 6228599.072809,
        "prepayPrincipalPayment": 29882.534715,
        "scheduledPrincipalPayment": 21148.848736
    }
    {
        "date": "2032-10-25",
        "totalCashFlow": 51082.780828,
        "interestPayment": 2573.986537,
        "principalBalance": 6129058.895067,
        "principalPayment": 48508.794291,
        "endPrincipalBalance": 6129058.895067,
        "beginPrincipalBalance": 6177567.689358,
        "prepayPrincipalPayment": 27439.831668,
        "scheduledPrincipalPayment": 21068.962622
    }
    {
        "date": "2032-11-25",
        "totalCashFlow": 48423.262519,
        "interestPayment": 2553.77454,
        "principalBalance": 6083189.407088,
        "principalPayment": 45869.48798,
        "endPrincipalBalance": 6083189.407088,
        "beginPrincipalBalance": 6129058.895067,
        "prepayPrincipalPayment": 24872.58179,
        "scheduledPrincipalPayment": 20996.90619
    }
    {
        "date": "2032-12-25",
        "totalCashFlow": 47879.451907,
        "interestPayment": 2534.662253,
        "principalBalance": 6037844.617434,
        "principalPayment": 45344.789654,
        "endPrincipalBalance": 6037844.617434,
        "beginPrincipalBalance": 6083189.407088,
        "prepayPrincipalPayment": 24411.602055,
        "scheduledPrincipalPayment": 20933.187599
    }
    {
        "date": "2033-01-25",
        "totalCashFlow": 47893.179777,
        "interestPayment": 2515.768591,
        "principalBalance": 5992467.206248,
        "principalPayment": 45377.411186,
        "endPrincipalBalance": 5992467.206248,
        "beginPrincipalBalance": 6037844.617434,
        "prepayPrincipalPayment": 24506.800125,
        "scheduledPrincipalPayment": 20870.611061
    }
    {
        "date": "2033-02-25",
        "totalCashFlow": 42482.849654,
        "interestPayment": 2496.861336,
        "principalBalance": 5952481.21793,
        "principalPayment": 39985.988318,
        "endPrincipalBalance": 5952481.21793,
        "beginPrincipalBalance": 5992467.206248,
        "prepayPrincipalPayment": 19178.730421,
        "scheduledPrincipalPayment": 20807.257897
    }
    {
        "date": "2033-03-25",
        "totalCashFlow": 42644.328131,
        "interestPayment": 2480.200507,
        "principalBalance": 5912317.090306,
        "principalPayment": 40164.127624,
        "endPrincipalBalance": 5912317.090306,
        "beginPrincipalBalance": 5952481.21793,
        "prepayPrincipalPayment": 19402.090212,
        "scheduledPrincipalPayment": 20762.037412
    }
    {
        "date": "2033-04-25",
        "totalCashFlow": 48515.452113,
        "interestPayment": 2463.465454,
        "principalBalance": 5866265.103647,
        "principalPayment": 46051.986659,
        "endPrincipalBalance": 5866265.103647,
        "beginPrincipalBalance": 5912317.090306,
        "prepayPrincipalPayment": 25336.303518,
        "scheduledPrincipalPayment": 20715.683141
    }
    {
        "date": "2033-05-25",
        "totalCashFlow": 48473.682364,
        "interestPayment": 2444.277127,
        "principalBalance": 5820235.698409,
        "principalPayment": 46029.405237,
        "endPrincipalBalance": 5820235.698409,
        "beginPrincipalBalance": 5866265.103647,
        "prepayPrincipalPayment": 25381.321995,
        "scheduledPrincipalPayment": 20648.083242
    }
    {
        "date": "2033-06-25",
        "totalCashFlow": 51274.994487,
        "interestPayment": 2425.098208,
        "principalBalance": 5771385.80213,
        "principalPayment": 48849.896279,
        "endPrincipalBalance": 5771385.80213,
        "beginPrincipalBalance": 5820235.698409,
        "prepayPrincipalPayment": 28270.050757,
        "scheduledPrincipalPayment": 20579.845522
    }
    {
        "date": "2033-07-25",
        "totalCashFlow": 53393.807386,
        "interestPayment": 2404.744084,
        "principalBalance": 5720396.738828,
        "principalPayment": 50989.063302,
        "endPrincipalBalance": 5720396.738828,
        "beginPrincipalBalance": 5771385.80213,
        "prepayPrincipalPayment": 30488.200074,
        "scheduledPrincipalPayment": 20500.863228
    }
    {
        "date": "2033-08-25",
        "totalCashFlow": 50044.947179,
        "interestPayment": 2383.498641,
        "principalBalance": 5672735.29029,
        "principalPayment": 47661.448537,
        "endPrincipalBalance": 5672735.29029,
        "beginPrincipalBalance": 5720396.738828,
        "prepayPrincipalPayment": 27248.028368,
        "scheduledPrincipalPayment": 20413.42017
    }
    {
        "date": "2033-09-25",
        "totalCashFlow": 52322.771495,
        "interestPayment": 2363.639704,
        "principalBalance": 5622776.1585,
        "principalPayment": 49959.13179,
        "endPrincipalBalance": 5622776.1585,
        "beginPrincipalBalance": 5672735.29029,
        "prepayPrincipalPayment": 29622.132989,
        "scheduledPrincipalPayment": 20336.998801
    }
    {
        "date": "2033-10-25",
        "totalCashFlow": 48624.882646,
        "interestPayment": 2342.823399,
        "principalBalance": 5576494.099253,
        "principalPayment": 46282.059247,
        "endPrincipalBalance": 5576494.099253,
        "beginPrincipalBalance": 5622776.1585,
        "prepayPrincipalPayment": 26030.565795,
        "scheduledPrincipalPayment": 20251.493452
    }
    {
        "date": "2033-11-25",
        "totalCashFlow": 46004.917503,
        "interestPayment": 2323.539208,
        "principalBalance": 5532812.720958,
        "principalPayment": 43681.378295,
        "endPrincipalBalance": 5532812.720958,
        "beginPrincipalBalance": 5576494.099253,
        "prepayPrincipalPayment": 23502.980459,
        "scheduledPrincipalPayment": 20178.397837
    }
    {
        "date": "2033-12-25",
        "totalCashFlow": 45448.295067,
        "interestPayment": 2305.338634,
        "principalBalance": 5489669.764525,
        "principalPayment": 43142.956434,
        "endPrincipalBalance": 5489669.764525,
        "beginPrincipalBalance": 5532812.720958,
        "prepayPrincipalPayment": 23028.982112,
        "scheduledPrincipalPayment": 20113.974321
    }
    {
        "date": "2034-01-25",
        "totalCashFlow": 45423.261299,
        "interestPayment": 2287.362402,
        "principalBalance": 5446533.865628,
        "principalPayment": 43135.898897,
        "endPrincipalBalance": 5446533.865628,
        "beginPrincipalBalance": 5489669.764525,
        "prepayPrincipalPayment": 23085.085016,
        "scheduledPrincipalPayment": 20050.81388
    }
    {
        "date": "2034-02-25",
        "totalCashFlow": 40169.498993,
        "interestPayment": 2269.389111,
        "principalBalance": 5408633.755745,
        "principalPayment": 37900.109882,
        "endPrincipalBalance": 5408633.755745,
        "beginPrincipalBalance": 5446533.865628,
        "prepayPrincipalPayment": 17913.124397,
        "scheduledPrincipalPayment": 19986.985486
    }
    {
        "date": "2034-03-25",
        "totalCashFlow": 40421.923998,
        "interestPayment": 2253.597398,
        "principalBalance": 5370465.429146,
        "principalPayment": 38168.3266,
        "endPrincipalBalance": 5370465.429146,
        "beginPrincipalBalance": 5408633.755745,
        "prepayPrincipalPayment": 18226.567446,
        "scheduledPrincipalPayment": 19941.759154
    }
    {
        "date": "2034-04-25",
        "totalCashFlow": 46206.719664,
        "interestPayment": 2237.693929,
        "principalBalance": 5326496.40341,
        "principalPayment": 43969.025735,
        "endPrincipalBalance": 5326496.40341,
        "beginPrincipalBalance": 5370465.429146,
        "prepayPrincipalPayment": 24074.014648,
        "scheduledPrincipalPayment": 19895.011087
    }
    {
        "date": "2034-05-25",
        "totalCashFlow": 45760.252187,
        "interestPayment": 2219.373501,
        "principalBalance": 5282955.524725,
        "principalPayment": 43540.878686,
        "endPrincipalBalance": 5282955.524725,
        "beginPrincipalBalance": 5326496.40341,
        "prepayPrincipalPayment": 23714.751215,
        "scheduledPrincipalPayment": 19826.127471
    }
    {
        "date": "2034-06-25",
        "totalCashFlow": 50332.994723,
        "interestPayment": 2201.231469,
        "principalBalance": 5234823.76147,
        "principalPayment": 48131.763254,
        "endPrincipalBalance": 5234823.76147,
        "beginPrincipalBalance": 5282955.524725,
        "prepayPrincipalPayment": 28373.67599,
        "scheduledPrincipalPayment": 19758.087264
    }
    {
        "date": "2034-07-25",
        "totalCashFlow": 51332.846587,
        "interestPayment": 2181.176567,
        "principalBalance": 5185672.091451,
        "principalPayment": 49151.670019,
        "endPrincipalBalance": 5185672.091451,
        "beginPrincipalBalance": 5234823.76147,
        "prepayPrincipalPayment": 29479.627384,
        "scheduledPrincipalPayment": 19672.042635
    }
    {
        "date": "2034-08-25",
        "totalCashFlow": 48172.995533,
        "interestPayment": 2160.696705,
        "principalBalance": 5139659.792623,
        "principalPayment": 46012.298828,
        "endPrincipalBalance": 5139659.792623,
        "beginPrincipalBalance": 5185672.091451,
        "prepayPrincipalPayment": 26431.080241,
        "scheduledPrincipalPayment": 19581.218586
    }
    {
        "date": "2034-09-25",
        "totalCashFlow": 50512.378913,
        "interestPayment": 2141.524914,
        "principalBalance": 5091288.938624,
        "principalPayment": 48370.853999,
        "endPrincipalBalance": 5091288.938624,
        "beginPrincipalBalance": 5139659.792623,
        "prepayPrincipalPayment": 28869.525333,
        "scheduledPrincipalPayment": 19501.328666
    }
    {
        "date": "2034-10-25",
        "totalCashFlow": 45886.661302,
        "interestPayment": 2121.370391,
        "principalBalance": 5047523.647713,
        "principalPayment": 43765.290911,
        "endPrincipalBalance": 5047523.647713,
        "beginPrincipalBalance": 5091288.938624,
        "prepayPrincipalPayment": 24353.719282,
        "scheduledPrincipalPayment": 19411.571629
    }
    {
        "date": "2034-11-25",
        "totalCashFlow": 45508.063297,
        "interestPayment": 2103.134853,
        "principalBalance": 5004118.71927,
        "principalPayment": 43404.928443,
        "endPrincipalBalance": 5004118.71927,
        "beginPrincipalBalance": 5047523.647713,
        "prepayPrincipalPayment": 24066.442391,
        "scheduledPrincipalPayment": 19338.486052
    }
    {
        "date": "2034-12-25",
        "totalCashFlow": 44044.429762,
        "interestPayment": 2085.049466,
        "principalBalance": 4962159.338974,
        "principalPayment": 41959.380296,
        "endPrincipalBalance": 4962159.338974,
        "beginPrincipalBalance": 5004118.71927,
        "prepayPrincipalPayment": 22693.406352,
        "scheduledPrincipalPayment": 19265.973943
    }
    {
        "date": "2035-01-25",
        "totalCashFlow": 43139.396973,
        "interestPayment": 2067.566391,
        "principalBalance": 4921087.508393,
        "principalPayment": 41071.830582,
        "endPrincipalBalance": 4921087.508393,
        "beginPrincipalBalance": 4962159.338974,
        "prepayPrincipalPayment": 21873.5871,
        "scheduledPrincipalPayment": 19198.243482
    }
    {
        "date": "2035-02-25",
        "totalCashFlow": 39745.068456,
        "interestPayment": 2050.453128,
        "principalBalance": 4883392.893065,
        "principalPayment": 37694.615328,
        "endPrincipalBalance": 4883392.893065,
        "beginPrincipalBalance": 4921087.508393,
        "prepayPrincipalPayment": 18561.418221,
        "scheduledPrincipalPayment": 19133.197106
    }
    {
        "date": "2035-03-25",
        "totalCashFlow": 39201.092786,
        "interestPayment": 2034.747039,
        "principalBalance": 4846226.547318,
        "principalPayment": 37166.345747,
        "endPrincipalBalance": 4846226.547318,
        "beginPrincipalBalance": 4883392.893065,
        "prepayPrincipalPayment": 18085.742202,
        "scheduledPrincipalPayment": 19080.603545
    }
    {
        "date": "2035-04-25",
        "totalCashFlow": 43504.756315,
        "interestPayment": 2019.261061,
        "principalBalance": 4804741.052064,
        "principalPayment": 41485.495254,
        "endPrincipalBalance": 4804741.052064,
        "beginPrincipalBalance": 4846226.547318,
        "prepayPrincipalPayment": 22456.032561,
        "scheduledPrincipalPayment": 19029.462693
    }
    {
        "date": "2035-05-25",
        "totalCashFlow": 45494.171031,
        "interestPayment": 2001.975438,
        "principalBalance": 4761248.856471,
        "principalPayment": 43492.195593,
        "endPrincipalBalance": 4761248.856471,
        "beginPrincipalBalance": 4804741.052064,
        "prepayPrincipalPayment": 24531.527469,
        "scheduledPrincipalPayment": 18960.668124
    }
    {
        "date": "2035-06-25",
        "totalCashFlow": 48908.546608,
        "interestPayment": 1983.85369,
        "principalBalance": 4714324.163553,
        "principalPayment": 46924.692918,
        "endPrincipalBalance": 4714324.163553,
        "beginPrincipalBalance": 4761248.856471,
        "prepayPrincipalPayment": 28041.566207,
        "scheduledPrincipalPayment": 18883.126711
    }
    {
        "date": "2035-07-25",
        "totalCashFlow": 48589.151469,
        "interestPayment": 1964.301735,
        "principalBalance": 4667699.313818,
        "principalPayment": 46624.849734,
        "endPrincipalBalance": 4667699.313818,
        "beginPrincipalBalance": 4714324.163553,
        "prepayPrincipalPayment": 27833.825167,
        "scheduledPrincipalPayment": 18791.024567
    }
    {
        "date": "2035-08-25",
        "totalCashFlow": 47871.346311,
        "interestPayment": 1944.874714,
        "principalBalance": 4621772.842221,
        "principalPayment": 45926.471597,
        "endPrincipalBalance": 4621772.842221,
        "beginPrincipalBalance": 4667699.313818,
        "prepayPrincipalPayment": 27227.377085,
        "scheduledPrincipalPayment": 18699.094512
    }
    {
        "date": "2035-09-25",
        "totalCashFlow": 48909.933618,
        "interestPayment": 1925.738684,
        "principalBalance": 4574788.647288,
        "principalPayment": 46984.194934,
        "endPrincipalBalance": 4574788.647288,
        "beginPrincipalBalance": 4621772.842221,
        "prepayPrincipalPayment": 28375.249562,
        "scheduledPrincipalPayment": 18608.945372
    }
    {
        "date": "2035-10-25",
        "totalCashFlow": 43238.673487,
        "interestPayment": 1906.161936,
        "principalBalance": 4533456.135738,
        "principalPayment": 41332.51155,
        "endPrincipalBalance": 4533456.135738,
        "beginPrincipalBalance": 4574788.647288,
        "prepayPrincipalPayment": 22819.012337,
        "scheduledPrincipalPayment": 18513.499213
    }
    {
        "date": "2035-11-25",
        "totalCashFlow": 44887.881143,
        "interestPayment": 1888.940057,
        "principalBalance": 4490457.194651,
        "principalPayment": 42998.941086,
        "endPrincipalBalance": 4490457.194651,
        "beginPrincipalBalance": 4533456.135738,
        "prepayPrincipalPayment": 24558.973987,
        "scheduledPrincipalPayment": 18439.9671
    }
    {
        "date": "2035-12-25",
        "totalCashFlow": 42422.032168,
        "interestPayment": 1871.023831,
        "principalBalance": 4449906.186315,
        "principalPayment": 40551.008336,
        "endPrincipalBalance": 4449906.186315,
        "beginPrincipalBalance": 4490457.194651,
        "prepayPrincipalPayment": 22192.239756,
        "scheduledPrincipalPayment": 18358.76858
    }
    {
        "date": "2036-01-25",
        "totalCashFlow": 41494.087045,
        "interestPayment": 1854.127578,
        "principalBalance": 4410266.226848,
        "principalPayment": 39639.959467,
        "endPrincipalBalance": 4410266.226848,
        "beginPrincipalBalance": 4449906.186315,
        "prepayPrincipalPayment": 21353.265205,
        "scheduledPrincipalPayment": 18286.694262
    }
    {
        "date": "2036-02-25",
        "totalCashFlow": 38149.395772,
        "interestPayment": 1837.610928,
        "principalBalance": 4373954.442003,
        "principalPayment": 36311.784845,
        "endPrincipalBalance": 4373954.442003,
        "beginPrincipalBalance": 4410266.226848,
        "prepayPrincipalPayment": 18094.246127,
        "scheduledPrincipalPayment": 18217.538717
    }
    {
        "date": "2036-03-25",
        "totalCashFlow": 38384.683659,
        "interestPayment": 1822.481018,
        "principalBalance": 4337392.239361,
        "principalPayment": 36562.202642,
        "endPrincipalBalance": 4337392.239361,
        "beginPrincipalBalance": 4373954.442003,
        "prepayPrincipalPayment": 18400.817636,
        "scheduledPrincipalPayment": 18161.385006
    }
    {
        "date": "2036-04-25",
        "totalCashFlow": 41292.061016,
        "interestPayment": 1807.246766,
        "principalBalance": 4297907.425111,
        "principalPayment": 39484.81425,
        "endPrincipalBalance": 4297907.425111,
        "beginPrincipalBalance": 4337392.239361,
        "prepayPrincipalPayment": 21381.312864,
        "scheduledPrincipalPayment": 18103.501386
    }
    {
        "date": "2036-05-25",
        "totalCashFlow": 44176.578091,
        "interestPayment": 1790.79476,
        "principalBalance": 4255521.641781,
        "principalPayment": 42385.783331,
        "endPrincipalBalance": 4255521.641781,
        "beginPrincipalBalance": 4297907.425111,
        "prepayPrincipalPayment": 24353.133307,
        "scheduledPrincipalPayment": 18032.650024
    }
    {
        "date": "2036-06-25",
        "totalCashFlow": 45813.436006,
        "interestPayment": 1773.134017,
        "principalBalance": 4211481.339792,
        "principalPayment": 44040.301988,
        "endPrincipalBalance": 4211481.339792,
        "beginPrincipalBalance": 4255521.641781,
        "prepayPrincipalPayment": 26091.583338,
        "scheduledPrincipalPayment": 17948.718651
    }
    {
        "date": "2036-07-25",
        "totalCashFlow": 46623.125747,
        "interestPayment": 1754.783892,
        "principalBalance": 4166612.997937,
        "principalPayment": 44868.341856,
        "endPrincipalBalance": 4166612.997937,
        "beginPrincipalBalance": 4211481.339792,
        "prepayPrincipalPayment": 27011.555589,
        "scheduledPrincipalPayment": 17856.786266
    }
    {
        "date": "2036-08-25",
        "totalCashFlow": 47046.438468,
        "interestPayment": 1736.088749,
        "principalBalance": 4121302.648218,
        "principalPayment": 45310.349719,
        "endPrincipalBalance": 4121302.648218,
        "beginPrincipalBalance": 4166612.997937,
        "prepayPrincipalPayment": 27550.099791,
        "scheduledPrincipalPayment": 17760.249928
    }
    {
        "date": "2036-09-25",
        "totalCashFlow": 44638.634461,
        "interestPayment": 1717.209437,
        "principalBalance": 4078381.223194,
        "principalPayment": 42921.425024,
        "endPrincipalBalance": 4078381.223194,
        "beginPrincipalBalance": 4121302.648218,
        "prepayPrincipalPayment": 25260.733097,
        "scheduledPrincipalPayment": 17660.691927
    }
    {
        "date": "2036-10-25",
        "totalCashFlow": 43416.473038,
        "interestPayment": 1699.32551,
        "principalBalance": 4036664.075666,
        "principalPayment": 41717.147528,
        "endPrincipalBalance": 4036664.075666,
        "beginPrincipalBalance": 4078381.223194,
        "prepayPrincipalPayment": 24146.885972,
        "scheduledPrincipalPayment": 17570.261556
    }
    {
        "date": "2036-11-25",
        "totalCashFlow": 42862.209214,
        "interestPayment": 1681.943365,
        "principalBalance": 3995483.809818,
        "principalPayment": 41180.265849,
        "endPrincipalBalance": 3995483.809818,
        "beginPrincipalBalance": 4036664.075666,
        "prepayPrincipalPayment": 23696.289186,
        "scheduledPrincipalPayment": 17483.976663
    }
    {
        "date": "2036-12-25",
        "totalCashFlow": 38562.926322,
        "interestPayment": 1664.784921,
        "principalBalance": 3958585.668416,
        "principalPayment": 36898.141401,
        "endPrincipalBalance": 3958585.668416,
        "beginPrincipalBalance": 3995483.809818,
        "prepayPrincipalPayment": 19499.141701,
        "scheduledPrincipalPayment": 17398.9997
    }
    {
        "date": "2037-01-25",
        "totalCashFlow": 41359.310644,
        "interestPayment": 1649.410695,
        "principalBalance": 3918875.768467,
        "principalPayment": 39709.899949,
        "endPrincipalBalance": 3918875.768467,
        "beginPrincipalBalance": 3958585.668416,
        "prepayPrincipalPayment": 22378.14877,
        "scheduledPrincipalPayment": 17331.751179
    }
    {
        "date": "2037-02-25",
        "totalCashFlow": 35575.964481,
        "interestPayment": 1632.864904,
        "principalBalance": 3884932.66889,
        "principalPayment": 33943.099577,
        "endPrincipalBalance": 3884932.66889,
        "beginPrincipalBalance": 3918875.768467,
        "prepayPrincipalPayment": 16691.805403,
        "scheduledPrincipalPayment": 17251.294174
    }
    {
        "date": "2037-03-25",
        "totalCashFlow": 35720.495005,
        "interestPayment": 1618.721945,
        "principalBalance": 3850830.89583,
        "principalPayment": 34101.77306,
        "endPrincipalBalance": 3850830.89583,
        "beginPrincipalBalance": 3884932.66889,
        "prepayPrincipalPayment": 16906.389603,
        "scheduledPrincipalPayment": 17195.383457
    }
    {
        "date": "2037-04-25",
        "totalCashFlow": 40078.356698,
        "interestPayment": 1604.512873,
        "principalBalance": 3812357.052006,
        "principalPayment": 38473.843825,
        "endPrincipalBalance": 3812357.052006,
        "beginPrincipalBalance": 3850830.89583,
        "prepayPrincipalPayment": 21335.790093,
        "scheduledPrincipalPayment": 17138.053731
    }
    {
        "date": "2037-05-25",
        "totalCashFlow": 42403.800039,
        "interestPayment": 1588.482105,
        "principalBalance": 3771541.734071,
        "principalPayment": 40815.317934,
        "endPrincipalBalance": 3771541.734071,
        "beginPrincipalBalance": 3812357.052006,
        "prepayPrincipalPayment": 23754.89045,
        "scheduledPrincipalPayment": 17060.427484
    }
    {
        "date": "2037-06-25",
        "totalCashFlow": 42338.453276,
        "interestPayment": 1571.475723,
        "principalBalance": 3730774.756518,
        "principalPayment": 40766.977554,
        "endPrincipalBalance": 3730774.756518,
        "beginPrincipalBalance": 3771541.734071,
        "prepayPrincipalPayment": 23795.671817,
        "scheduledPrincipalPayment": 16971.305737
    }
    {
        "date": "2037-07-25",
        "totalCashFlow": 45283.703686,
        "interestPayment": 1554.489482,
        "principalBalance": 3687045.542313,
        "principalPayment": 43729.214205,
        "endPrincipalBalance": 3687045.542313,
        "beginPrincipalBalance": 3730774.756518,
        "prepayPrincipalPayment": 26847.902606,
        "scheduledPrincipalPayment": 16881.311598
    }
    {
        "date": "2037-08-25",
        "totalCashFlow": 44447.858152,
        "interestPayment": 1536.268976,
        "principalBalance": 3644133.953137,
        "principalPayment": 42911.589176,
        "endPrincipalBalance": 3644133.953137,
        "beginPrincipalBalance": 3687045.542313,
        "prepayPrincipalPayment": 26134.855759,
        "scheduledPrincipalPayment": 16776.733417
    }
    {
        "date": "2037-09-25",
        "totalCashFlow": 42111.423508,
        "interestPayment": 1518.389147,
        "principalBalance": 3603540.918776,
        "principalPayment": 40593.034361,
        "endPrincipalBalance": 3603540.918776,
        "beginPrincipalBalance": 3644133.953137,
        "prepayPrincipalPayment": 23918.41158,
        "scheduledPrincipalPayment": 16674.622781
    }
    {
        "date": "2037-10-25",
        "totalCashFlow": 40906.377352,
        "interestPayment": 1501.475383,
        "principalBalance": 3564136.016807,
        "principalPayment": 39404.90197,
        "endPrincipalBalance": 3564136.016807,
        "beginPrincipalBalance": 3603540.918776,
        "prepayPrincipalPayment": 22822.97193,
        "scheduledPrincipalPayment": 16581.930039
    }
    {
        "date": "2037-11-25",
        "totalCashFlow": 39438.093966,
        "interestPayment": 1485.056674,
        "principalBalance": 3526182.979514,
        "principalPayment": 37953.037292,
        "endPrincipalBalance": 3526182.979514,
        "beginPrincipalBalance": 3564136.016807,
        "prepayPrincipalPayment": 21459.451212,
        "scheduledPrincipalPayment": 16493.58608
    }
    {
        "date": "2037-12-25",
        "totalCashFlow": 37147.180886,
        "interestPayment": 1469.242908,
        "principalBalance": 3490505.041537,
        "principalPayment": 35677.937977,
        "endPrincipalBalance": 3490505.041537,
        "beginPrincipalBalance": 3526182.979514,
        "prepayPrincipalPayment": 19267.043601,
        "scheduledPrincipalPayment": 16410.894377
    }
    {
        "date": "2038-01-25",
        "totalCashFlow": 38822.62776,
        "interestPayment": 1454.377101,
        "principalBalance": 3453136.790878,
        "principalPayment": 37368.250659,
        "endPrincipalBalance": 3453136.790878,
        "beginPrincipalBalance": 3490505.041537,
        "prepayPrincipalPayment": 21030.443748,
        "scheduledPrincipalPayment": 16337.806911
    }
    {
        "date": "2038-02-25",
        "totalCashFlow": 32717.32514,
        "interestPayment": 1438.806996,
        "principalBalance": 3421858.272734,
        "principalPayment": 31278.518144,
        "endPrincipalBalance": 3421858.272734,
        "beginPrincipalBalance": 3453136.790878,
        "prepayPrincipalPayment": 15022.694606,
        "scheduledPrincipalPayment": 16255.823537
    }
    {
        "date": "2038-03-25",
        "totalCashFlow": 33477.490054,
        "interestPayment": 1425.77428,
        "principalBalance": 3389806.55696,
        "principalPayment": 32051.715774,
        "endPrincipalBalance": 3389806.55696,
        "beginPrincipalBalance": 3421858.272734,
        "prepayPrincipalPayment": 15850.087722,
        "scheduledPrincipalPayment": 16201.628051
    }
    {
        "date": "2038-04-25",
        "totalCashFlow": 38290.254203,
        "interestPayment": 1412.419399,
        "principalBalance": 3352928.722157,
        "principalPayment": 36877.834804,
        "endPrincipalBalance": 3352928.722157,
        "beginPrincipalBalance": 3389806.55696,
        "prepayPrincipalPayment": 20734.811748,
        "scheduledPrincipalPayment": 16143.023056
    }
    {
        "date": "2038-05-25",
        "totalCashFlow": 39148.214228,
        "interestPayment": 1397.053634,
        "principalBalance": 3315177.561562,
        "principalPayment": 37751.160594,
        "endPrincipalBalance": 3315177.561562,
        "beginPrincipalBalance": 3352928.722157,
        "prepayPrincipalPayment": 21690.641578,
        "scheduledPrincipalPayment": 16060.519016
    }
    {
        "date": "2038-06-25",
        "totalCashFlow": 39498.250421,
        "interestPayment": 1381.323984,
        "principalBalance": 3277060.635126,
        "principalPayment": 38116.926437,
        "endPrincipalBalance": 3277060.635126,
        "beginPrincipalBalance": 3315177.561562,
        "prepayPrincipalPayment": 22144.18464,
        "scheduledPrincipalPayment": 15972.741797
    }
    {
        "date": "2038-07-25",
        "totalCashFlow": 42177.990018,
        "interestPayment": 1365.441931,
        "principalBalance": 3236248.087039,
        "principalPayment": 40812.548087,
        "endPrincipalBalance": 3236248.087039,
        "beginPrincipalBalance": 3277060.635126,
        "prepayPrincipalPayment": 24930.488358,
        "scheduledPrincipalPayment": 15882.059729
    }
    {
        "date": "2038-08-25",
        "totalCashFlow": 40347.094552,
        "interestPayment": 1348.436703,
        "principalBalance": 3197249.429189,
        "principalPayment": 38998.65785,
        "endPrincipalBalance": 3197249.429189,
        "beginPrincipalBalance": 3236248.087039,
        "prepayPrincipalPayment": 23221.593176,
        "scheduledPrincipalPayment": 15777.064674
    }
    {
        "date": "2038-09-25",
        "totalCashFlow": 40120.079604,
        "interestPayment": 1332.187262,
        "principalBalance": 3158461.536847,
        "principalPayment": 38787.892342,
        "endPrincipalBalance": 3158461.536847,
        "beginPrincipalBalance": 3197249.429189,
        "prepayPrincipalPayment": 23108.274148,
        "scheduledPrincipalPayment": 15679.618194
    }
    {
        "date": "2038-10-25",
        "totalCashFlow": 38007.218907,
        "interestPayment": 1316.02564,
        "principalBalance": 3121770.34358,
        "principalPayment": 36691.193267,
        "endPrincipalBalance": 3121770.34358,
        "beginPrincipalBalance": 3158461.536847,
        "prepayPrincipalPayment": 21109.244458,
        "scheduledPrincipalPayment": 15581.948809
    }
    {
        "date": "2038-11-25",
        "totalCashFlow": 35806.784569,
        "interestPayment": 1300.737643,
        "principalBalance": 3087264.296654,
        "principalPayment": 34506.046926,
        "endPrincipalBalance": 3087264.296654,
        "beginPrincipalBalance": 3121770.34358,
        "prepayPrincipalPayment": 19012.632562,
        "scheduledPrincipalPayment": 15493.414364
    }
    {
        "date": "2038-12-25",
        "totalCashFlow": 35322.998238,
        "interestPayment": 1286.360124,
        "principalBalance": 3053227.65854,
        "principalPayment": 34036.638114,
        "endPrincipalBalance": 3053227.65854,
        "beginPrincipalBalance": 3087264.296654,
        "prepayPrincipalPayment": 18622.014316,
        "scheduledPrincipalPayment": 15414.623798
    }
    {
        "date": "2039-01-25",
        "totalCashFlow": 35234.244405,
        "interestPayment": 1272.178191,
        "principalBalance": 3019265.592326,
        "principalPayment": 33962.066214,
        "endPrincipalBalance": 3019265.592326,
        "beginPrincipalBalance": 3053227.65854,
        "prepayPrincipalPayment": 18624.928621,
        "scheduledPrincipalPayment": 15337.137593
    }
    {
        "date": "2039-02-25",
        "totalCashFlow": 30995.909484,
        "interestPayment": 1258.02733,
        "principalBalance": 2989527.710172,
        "principalPayment": 29737.882154,
        "endPrincipalBalance": 2989527.710172,
        "beginPrincipalBalance": 3019265.592326,
        "prepayPrincipalPayment": 14478.896406,
        "scheduledPrincipalPayment": 15258.985748
    }
    {
        "date": "2039-03-25",
        "totalCashFlow": 31086.305586,
        "interestPayment": 1245.636546,
        "principalBalance": 2959687.041132,
        "principalPayment": 29840.66904,
        "endPrincipalBalance": 2959687.041132,
        "beginPrincipalBalance": 2989527.710172,
        "prepayPrincipalPayment": 14639.411326,
        "scheduledPrincipalPayment": 15201.257713
    }
    {
        "date": "2039-04-25",
        "totalCashFlow": 35494.72212,
        "interestPayment": 1233.202934,
        "principalBalance": 2925425.521946,
        "principalPayment": 34261.519186,
        "endPrincipalBalance": 2925425.521946,
        "beginPrincipalBalance": 2959687.041132,
        "prepayPrincipalPayment": 19119.324215,
        "scheduledPrincipalPayment": 15142.194971
    }
    {
        "date": "2039-05-25",
        "totalCashFlow": 35455.350917,
        "interestPayment": 1218.927301,
        "principalBalance": 2891189.09833,
        "principalPayment": 34236.423616,
        "endPrincipalBalance": 2891189.09833,
        "beginPrincipalBalance": 2925425.521946,
        "prepayPrincipalPayment": 19176.878243,
        "scheduledPrincipalPayment": 15059.545373
    }
    {
        "date": "2039-06-25",
        "totalCashFlow": 37522.588371,
        "interestPayment": 1204.662124,
        "principalBalance": 2854871.172083,
        "principalPayment": 36317.926247,
        "endPrincipalBalance": 2854871.172083,
        "beginPrincipalBalance": 2891189.09833,
        "prepayPrincipalPayment": 21342.027023,
        "scheduledPrincipalPayment": 14975.899224
    }
    {
        "date": "2039-07-25",
        "totalCashFlow": 39041.755323,
        "interestPayment": 1189.529655,
        "principalBalance": 2817018.946416,
        "principalPayment": 37852.225668,
        "endPrincipalBalance": 2817018.946416,
        "beginPrincipalBalance": 2854871.172083,
        "prepayPrincipalPayment": 22971.966209,
        "scheduledPrincipalPayment": 14880.259458
    }
    {
        "date": "2039-08-25",
        "totalCashFlow": 36428.737886,
        "interestPayment": 1173.757894,
        "principalBalance": 2781763.966424,
        "principalPayment": 35254.979992,
        "endPrincipalBalance": 2781763.966424,
        "beginPrincipalBalance": 2817018.946416,
        "prepayPrincipalPayment": 20479.708286,
        "scheduledPrincipalPayment": 14775.271706
    }
    {
        "date": "2039-09-25",
        "totalCashFlow": 37999.621104,
        "interestPayment": 1159.068319,
        "principalBalance": 2744923.41364,
        "principalPayment": 36840.552784,
        "endPrincipalBalance": 2744923.41364,
        "beginPrincipalBalance": 2781763.966424,
        "prepayPrincipalPayment": 22157.985143,
        "scheduledPrincipalPayment": 14682.567641
    }
    {
        "date": "2039-10-25",
        "totalCashFlow": 35158.153429,
        "interestPayment": 1143.718089,
        "principalBalance": 2710908.9783,
        "principalPayment": 34014.43534,
        "endPrincipalBalance": 2710908.9783,
        "beginPrincipalBalance": 2744923.41364,
        "prepayPrincipalPayment": 19434.269573,
        "scheduledPrincipalPayment": 14580.165767
    }
    {
        "date": "2039-11-25",
        "totalCashFlow": 33120.324203,
        "interestPayment": 1129.545408,
        "principalBalance": 2678918.199504,
        "principalPayment": 31990.778796,
        "endPrincipalBalance": 2678918.199504,
        "beginPrincipalBalance": 2710908.9783,
        "prepayPrincipalPayment": 17499.313405,
        "scheduledPrincipalPayment": 14491.465391
    }
    {
        "date": "2039-12-25",
        "totalCashFlow": 32651.980194,
        "interestPayment": 1116.215916,
        "principalBalance": 2647382.435227,
        "principalPayment": 31535.764277,
        "endPrincipalBalance": 2647382.435227,
        "beginPrincipalBalance": 2678918.199504,
        "prepayPrincipalPayment": 17123.348842,
        "scheduledPrincipalPayment": 14412.415435
    }
    {
        "date": "2040-01-25",
        "totalCashFlow": 32540.011347,
        "interestPayment": 1103.076015,
        "principalBalance": 2615945.499895,
        "principalPayment": 31436.935332,
        "endPrincipalBalance": 2615945.499895,
        "beginPrincipalBalance": 2647382.435227,
        "prepayPrincipalPayment": 17102.224304,
        "scheduledPrincipalPayment": 14334.711028
    }
    {
        "date": "2040-02-25",
        "totalCashFlow": 28669.223791,
        "interestPayment": 1089.977292,
        "principalBalance": 2588366.253395,
        "principalPayment": 27579.246499,
        "endPrincipalBalance": 2588366.253395,
        "beginPrincipalBalance": 2615945.499895,
        "prepayPrincipalPayment": 13322.807569,
        "scheduledPrincipalPayment": 14256.43893
    }
    {
        "date": "2040-03-25",
        "totalCashFlow": 29300.751601,
        "interestPayment": 1078.485939,
        "principalBalance": 2560143.987733,
        "principalPayment": 28222.265662,
        "endPrincipalBalance": 2560143.987733,
        "beginPrincipalBalance": 2588366.253395,
        "prepayPrincipalPayment": 14024.057123,
        "scheduledPrincipalPayment": 14198.208539
    }
    {
        "date": "2040-04-25",
        "totalCashFlow": 31673.377644,
        "interestPayment": 1066.726662,
        "principalBalance": 2529537.33675,
        "principalPayment": 30606.650983,
        "endPrincipalBalance": 2529537.33675,
        "beginPrincipalBalance": 2560143.987733,
        "prepayPrincipalPayment": 16471.085001,
        "scheduledPrincipalPayment": 14135.565982
    }
    {
        "date": "2040-05-25",
        "totalCashFlow": 32976.775631,
        "interestPayment": 1053.97389,
        "principalBalance": 2497614.535009,
        "principalPayment": 31922.801741,
        "endPrincipalBalance": 2497614.535009,
        "beginPrincipalBalance": 2529537.33675,
        "prepayPrincipalPayment": 17864.054757,
        "scheduledPrincipalPayment": 14058.746985
    }
    {
        "date": "2040-06-25",
        "totalCashFlow": 35245.215293,
        "interestPayment": 1040.672723,
        "principalBalance": 2463409.992438,
        "principalPayment": 34204.542571,
        "endPrincipalBalance": 2463409.992438,
        "beginPrincipalBalance": 2497614.535009,
        "prepayPrincipalPayment": 20231.095394,
        "scheduledPrincipalPayment": 13973.447177
    }
    {
        "date": "2040-07-25",
        "totalCashFlow": 34853.279737,
        "interestPayment": 1026.42083,
        "principalBalance": 2429583.133532,
        "principalPayment": 33826.858906,
        "endPrincipalBalance": 2429583.133532,
        "beginPrincipalBalance": 2463409.992438,
        "prepayPrincipalPayment": 19952.798694,
        "scheduledPrincipalPayment": 13874.060212
    }
    {
        "date": "2040-08-25",
        "totalCashFlow": 34173.735193,
        "interestPayment": 1012.326306,
        "principalBalance": 2396421.724645,
        "principalPayment": 33161.408887,
        "endPrincipalBalance": 2396421.724645,
        "beginPrincipalBalance": 2429583.133532,
        "prepayPrincipalPayment": 19386.025995,
        "scheduledPrincipalPayment": 13775.382892
    }
    {
        "date": "2040-09-25",
        "totalCashFlow": 34696.540724,
        "interestPayment": 998.509052,
        "principalBalance": 2362723.692973,
        "principalPayment": 33698.031672,
        "endPrincipalBalance": 2362723.692973,
        "beginPrincipalBalance": 2396421.724645,
        "prepayPrincipalPayment": 20018.957279,
        "scheduledPrincipalPayment": 13679.074393
    }
    {
        "date": "2040-10-25",
        "totalCashFlow": 30652.865458,
        "interestPayment": 984.468205,
        "principalBalance": 2333055.29572,
        "principalPayment": 29668.397253,
        "endPrincipalBalance": 2333055.29572,
        "beginPrincipalBalance": 2362723.692973,
        "prepayPrincipalPayment": 16090.120263,
        "scheduledPrincipalPayment": 13578.27699
    }
    {
        "date": "2040-11-25",
        "totalCashFlow": 31599.983925,
        "interestPayment": 972.106373,
        "principalBalance": 2302427.418169,
        "principalPayment": 30627.877552,
        "endPrincipalBalance": 2302427.418169,
        "beginPrincipalBalance": 2333055.29572,
        "prepayPrincipalPayment": 17128.555779,
        "scheduledPrincipalPayment": 13499.321773
    }
    {
        "date": "2040-12-25",
        "totalCashFlow": 29807.356776,
        "interestPayment": 959.344758,
        "principalBalance": 2273579.40615,
        "principalPayment": 28848.012018,
        "endPrincipalBalance": 2273579.40615,
        "beginPrincipalBalance": 2302427.418169,
        "prepayPrincipalPayment": 15434.416837,
        "scheduledPrincipalPayment": 13413.595182
    }
    {
        "date": "2041-01-25",
        "totalCashFlow": 29047.110879,
        "interestPayment": 947.324753,
        "principalBalance": 2245479.620024,
        "principalPayment": 28099.786126,
        "endPrincipalBalance": 2245479.620024,
        "beginPrincipalBalance": 2273579.40615,
        "prepayPrincipalPayment": 14762.758172,
        "scheduledPrincipalPayment": 13337.027954
    }
    {
        "date": "2041-02-25",
        "totalCashFlow": 26694.115306,
        "interestPayment": 935.616508,
        "principalBalance": 2219721.121227,
        "principalPayment": 25758.498797,
        "endPrincipalBalance": 2219721.121227,
        "beginPrincipalBalance": 2245479.620024,
        "prepayPrincipalPayment": 12494.779556,
        "scheduledPrincipalPayment": 13263.719241
    }
    {
        "date": "2041-03-25",
        "totalCashFlow": 26230.426942,
        "interestPayment": 924.883801,
        "principalBalance": 2194415.578085,
        "principalPayment": 25305.543142,
        "endPrincipalBalance": 2194415.578085,
        "beginPrincipalBalance": 2219721.121227,
        "prepayPrincipalPayment": 12102.328241,
        "scheduledPrincipalPayment": 13203.214901
    }
    {
        "date": "2041-04-25",
        "totalCashFlow": 28522.25707,
        "interestPayment": 914.339824,
        "principalBalance": 2166807.660839,
        "principalPayment": 27607.917246,
        "endPrincipalBalance": 2166807.660839,
        "beginPrincipalBalance": 2194415.578085,
        "prepayPrincipalPayment": 14463.441536,
        "scheduledPrincipalPayment": 13144.475709
    }
    {
        "date": "2041-05-25",
        "totalCashFlow": 30262.986846,
        "interestPayment": 902.836525,
        "principalBalance": 2137447.510518,
        "principalPayment": 29360.150321,
        "endPrincipalBalance": 2137447.510518,
        "beginPrincipalBalance": 2166807.660839,
        "prepayPrincipalPayment": 16289.230839,
        "scheduledPrincipalPayment": 13070.919482
    }
    {
        "date": "2041-06-25",
        "totalCashFlow": 31890.059799,
        "interestPayment": 890.603129,
        "principalBalance": 2106448.053849,
        "principalPayment": 30999.456669,
        "endPrincipalBalance": 2106448.053849,
        "beginPrincipalBalance": 2137447.510518,
        "prepayPrincipalPayment": 18013.883143,
        "scheduledPrincipalPayment": 12985.573526
    }
    {
        "date": "2041-07-25",
        "totalCashFlow": 30739.232909,
        "interestPayment": 877.686689,
        "principalBalance": 2076586.507629,
        "principalPayment": 29861.54622,
        "endPrincipalBalance": 2076586.507629,
        "beginPrincipalBalance": 2106448.053849,
        "prepayPrincipalPayment": 16972.668915,
        "scheduledPrincipalPayment": 12888.877305
    }
    {
        "date": "2041-08-25",
        "totalCashFlow": 31601.630989,
        "interestPayment": 865.244378,
        "principalBalance": 2045850.121019,
        "principalPayment": 30736.38661,
        "endPrincipalBalance": 2045850.121019,
        "beginPrincipalBalance": 2076586.507629,
        "prepayPrincipalPayment": 17938.683502,
        "scheduledPrincipalPayment": 12797.703109
    }
    {
        "date": "2041-09-25",
        "totalCashFlow": 30600.343416,
        "interestPayment": 852.43755,
        "principalBalance": 2016102.215153,
        "principalPayment": 29747.905866,
        "endPrincipalBalance": 2016102.215153,
        "beginPrincipalBalance": 2045850.121019,
        "prepayPrincipalPayment": 17048.22676,
        "scheduledPrincipalPayment": 12699.679106
    }
    {
        "date": "2041-10-25",
        "totalCashFlow": 28358.960629,
        "interestPayment": 840.04259,
        "principalBalance": 1988583.297113,
        "principalPayment": 27518.918039,
        "endPrincipalBalance": 1988583.297113,
        "beginPrincipalBalance": 2016102.215153,
        "prepayPrincipalPayment": 14912.609462,
        "scheduledPrincipalPayment": 12606.308578
    }
    {
        "date": "2041-11-25",
        "totalCashFlow": 28500.193183,
        "interestPayment": 828.576374,
        "principalBalance": 1960911.680304,
        "principalPayment": 27671.616809,
        "endPrincipalBalance": 1960911.680304,
        "beginPrincipalBalance": 1988583.297113,
        "prepayPrincipalPayment": 15146.106866,
        "scheduledPrincipalPayment": 12525.509943
    }
    {
        "date": "2041-12-25",
        "totalCashFlow": 26328.717555,
        "interestPayment": 817.046533,
        "principalBalance": 1935400.009283,
        "principalPayment": 25511.671022,
        "endPrincipalBalance": 1935400.009283,
        "beginPrincipalBalance": 1960911.680304,
        "prepayPrincipalPayment": 13069.219328,
        "scheduledPrincipalPayment": 12442.451694
    }
    {
        "date": "2042-01-25",
        "totalCashFlow": 26749.67803,
        "interestPayment": 806.416671,
        "principalBalance": 1909456.747923,
        "principalPayment": 25943.26136,
        "endPrincipalBalance": 1909456.747923,
        "beginPrincipalBalance": 1935400.009283,
        "prepayPrincipalPayment": 13571.392576,
        "scheduledPrincipalPayment": 12371.868783
    }
    {
        "date": "2042-02-25",
        "totalCashFlow": 24128.589665,
        "interestPayment": 795.606978,
        "principalBalance": 1886123.765237,
        "principalPayment": 23332.982687,
        "endPrincipalBalance": 1886123.765237,
        "beginPrincipalBalance": 1909456.747923,
        "prepayPrincipalPayment": 11035.629519,
        "scheduledPrincipalPayment": 12297.353168
    }
    {
        "date": "2042-03-25",
        "totalCashFlow": 23698.694394,
        "interestPayment": 785.884902,
        "principalBalance": 1863210.955745,
        "principalPayment": 22912.809492,
        "endPrincipalBalance": 1863210.955745,
        "beginPrincipalBalance": 1886123.765237,
        "prepayPrincipalPayment": 10674.253847,
        "scheduledPrincipalPayment": 12238.555645
    }
    {
        "date": "2042-04-25",
        "totalCashFlow": 25641.939086,
        "interestPayment": 776.337898,
        "principalBalance": 1838345.354557,
        "principalPayment": 24865.601188,
        "endPrincipalBalance": 1838345.354557,
        "beginPrincipalBalance": 1863210.955745,
        "prepayPrincipalPayment": 12684.084423,
        "scheduledPrincipalPayment": 12181.516765
    }
    {
        "date": "2042-05-25",
        "totalCashFlow": 27384.60479,
        "interestPayment": 765.977231,
        "principalBalance": 1811726.726997,
        "principalPayment": 26618.627559,
        "endPrincipalBalance": 1811726.726997,
        "beginPrincipalBalance": 1838345.354557,
        "prepayPrincipalPayment": 14507.981885,
        "scheduledPrincipalPayment": 12110.645674
    }
    {
        "date": "2042-06-25",
        "totalCashFlow": 27831.947209,
        "interestPayment": 754.886136,
        "principalBalance": 1784649.665924,
        "principalPayment": 27077.061073,
        "endPrincipalBalance": 1784649.665924,
        "beginPrincipalBalance": 1811726.726997,
        "prepayPrincipalPayment": 15050.109806,
        "scheduledPrincipalPayment": 12026.951267
    }
    {
        "date": "2042-07-25",
        "totalCashFlow": 28089.176216,
        "interestPayment": 743.604027,
        "principalBalance": 1757304.093736,
        "principalPayment": 27345.572188,
        "endPrincipalBalance": 1757304.093736,
        "beginPrincipalBalance": 1784649.665924,
        "prepayPrincipalPayment": 15406.773799,
        "scheduledPrincipalPayment": 11938.798389
    }
    {
        "date": "2042-08-25",
        "totalCashFlow": 28118.072886,
        "interestPayment": 732.210039,
        "principalBalance": 1729918.230889,
        "principalPayment": 27385.862847,
        "endPrincipalBalance": 1729918.230889,
        "beginPrincipalBalance": 1757304.093736,
        "prepayPrincipalPayment": 15538.497358,
        "scheduledPrincipalPayment": 11847.365489
    }
    {
        "date": "2042-09-25",
        "totalCashFlow": 26642.384021,
        "interestPayment": 720.799263,
        "principalBalance": 1703996.64613,
        "principalPayment": 25921.584759,
        "endPrincipalBalance": 1703996.64613,
        "beginPrincipalBalance": 1729918.230889,
        "prepayPrincipalPayment": 14167.456371,
        "scheduledPrincipalPayment": 11754.128387
    }
    {
        "date": "2042-10-25",
        "totalCashFlow": 25828.118412,
        "interestPayment": 709.998603,
        "principalBalance": 1678878.526321,
        "principalPayment": 25118.119809,
        "endPrincipalBalance": 1678878.526321,
        "beginPrincipalBalance": 1703996.64613,
        "prepayPrincipalPayment": 13448.76945,
        "scheduledPrincipalPayment": 11669.350359
    }
    {
        "date": "2042-11-25",
        "totalCashFlow": 25364.218768,
        "interestPayment": 699.532719,
        "principalBalance": 1654213.840272,
        "principalPayment": 24664.686049,
        "endPrincipalBalance": 1654213.840272,
        "beginPrincipalBalance": 1678878.526321,
        "prepayPrincipalPayment": 13076.01197,
        "scheduledPrincipalPayment": 11588.674079
    }
    {
        "date": "2042-12-25",
        "totalCashFlow": 23016.771369,
        "interestPayment": 689.255767,
        "principalBalance": 1631886.32467,
        "principalPayment": 22327.515602,
        "endPrincipalBalance": 1631886.32467,
        "beginPrincipalBalance": 1654213.840272,
        "prepayPrincipalPayment": 10817.750862,
        "scheduledPrincipalPayment": 11509.76474
    }
    {
        "date": "2043-01-25",
        "totalCashFlow": 24294.593816,
        "interestPayment": 679.952635,
        "principalBalance": 1608271.683489,
        "principalPayment": 23614.641181,
        "endPrincipalBalance": 1608271.683489,
        "beginPrincipalBalance": 1631886.32467,
        "prepayPrincipalPayment": 12168.761672,
        "scheduledPrincipalPayment": 11445.879508
    }
    {
        "date": "2043-02-25",
        "totalCashFlow": 21243.058587,
        "interestPayment": 670.113201,
        "principalBalance": 1587698.738104,
        "principalPayment": 20572.945385,
        "endPrincipalBalance": 1587698.738104,
        "beginPrincipalBalance": 1608271.683489,
        "prepayPrincipalPayment": 9201.185905,
        "scheduledPrincipalPayment": 11371.75948
    }
    {
        "date": "2043-03-25",
        "totalCashFlow": 21213.235941,
        "interestPayment": 661.541141,
        "principalBalance": 1567147.043304,
        "principalPayment": 20551.6948,
        "endPrincipalBalance": 1567147.043304,
        "beginPrincipalBalance": 1587698.738104,
        "prepayPrincipalPayment": 9233.680991,
        "scheduledPrincipalPayment": 11318.01381
    }
    {
        "date": "2043-04-25",
        "totalCashFlow": 23037.704831,
        "interestPayment": 652.977935,
        "principalBalance": 1544762.316408,
        "principalPayment": 22384.726896,
        "endPrincipalBalance": 1544762.316408,
        "beginPrincipalBalance": 1567147.043304,
        "prepayPrincipalPayment": 11121.288034,
        "scheduledPrincipalPayment": 11263.438862
    }
    {
        "date": "2043-05-25",
        "totalCashFlow": 24262.216297,
        "interestPayment": 643.650965,
        "principalBalance": 1521143.751075,
        "principalPayment": 23618.565332,
        "endPrincipalBalance": 1521143.751075,
        "beginPrincipalBalance": 1544762.316408,
        "prepayPrincipalPayment": 12423.987431,
        "scheduledPrincipalPayment": 11194.577901
    }
    {
        "date": "2043-06-25",
        "totalCashFlow": 24092.466587,
        "interestPayment": 633.809896,
        "principalBalance": 1497685.094385,
        "principalPayment": 23458.656691,
        "endPrincipalBalance": 1497685.094385,
        "beginPrincipalBalance": 1521143.751075,
        "prepayPrincipalPayment": 12343.203569,
        "scheduledPrincipalPayment": 11115.453122
    }
    {
        "date": "2043-07-25",
        "totalCashFlow": 25362.612024,
        "interestPayment": 624.035456,
        "principalBalance": 1472946.517816,
        "principalPayment": 24738.576568,
        "endPrincipalBalance": 1472946.517816,
        "beginPrincipalBalance": 1497685.094385,
        "prepayPrincipalPayment": 13702.498919,
        "scheduledPrincipalPayment": 11036.07765
    }
    {
        "date": "2043-08-25",
        "totalCashFlow": 24800.934493,
        "interestPayment": 613.727716,
        "principalBalance": 1448759.311039,
        "principalPayment": 24187.206778,
        "endPrincipalBalance": 1448759.311039,
        "beginPrincipalBalance": 1472946.517816,
        "prepayPrincipalPayment": 13241.459107,
        "scheduledPrincipalPayment": 10945.74767
    }
    {
        "date": "2043-09-25",
        "totalCashFlow": 23539.936393,
        "interestPayment": 603.649713,
        "principalBalance": 1425823.024359,
        "principalPayment": 22936.28668,
        "endPrincipalBalance": 1425823.024359,
        "beginPrincipalBalance": 1448759.311039,
        "prepayPrincipalPayment": 12078.376977,
        "scheduledPrincipalPayment": 10857.909703
    }
    {
        "date": "2043-10-25",
        "totalCashFlow": 22834.751052,
        "interestPayment": 594.092927,
        "principalBalance": 1403582.366233,
        "principalPayment": 22240.658125,
        "endPrincipalBalance": 1403582.366233,
        "beginPrincipalBalance": 1425823.024359,
        "prepayPrincipalPayment": 11462.739588,
        "scheduledPrincipalPayment": 10777.918538
    }
    {
        "date": "2043-11-25",
        "totalCashFlow": 22014.674447,
        "interestPayment": 584.825986,
        "principalBalance": 1382152.517772,
        "principalPayment": 21429.848461,
        "endPrincipalBalance": 1382152.517772,
        "beginPrincipalBalance": 1403582.366233,
        "prepayPrincipalPayment": 10728.101669,
        "scheduledPrincipalPayment": 10701.746792
    }
    {
        "date": "2043-12-25",
        "totalCashFlow": 20849.106797,
        "interestPayment": 575.896882,
        "principalBalance": 1361879.307858,
        "principalPayment": 20273.209915,
        "endPrincipalBalance": 1361879.307858,
        "beginPrincipalBalance": 1382152.517772,
        "prepayPrincipalPayment": 9642.827222,
        "scheduledPrincipalPayment": 10630.382692
    }
    {
        "date": "2044-01-25",
        "totalCashFlow": 21485.270557,
        "interestPayment": 567.449712,
        "principalBalance": 1340961.487012,
        "principalPayment": 20917.820846,
        "endPrincipalBalance": 1340961.487012,
        "beginPrincipalBalance": 1361879.307858,
        "prepayPrincipalPayment": 10351.18224,
        "scheduledPrincipalPayment": 10566.638606
    }
    {
        "date": "2044-02-25",
        "totalCashFlow": 18631.462605,
        "interestPayment": 558.733953,
        "principalBalance": 1322888.75836,
        "principalPayment": 18072.728652,
        "endPrincipalBalance": 1322888.75836,
        "beginPrincipalBalance": 1340961.487012,
        "prepayPrincipalPayment": 7576.108891,
        "scheduledPrincipalPayment": 10496.619761
    }
    {
        "date": "2044-03-25",
        "totalCashFlow": 19195.17038,
        "interestPayment": 551.203649,
        "principalBalance": 1304244.791629,
        "principalPayment": 18643.966731,
        "endPrincipalBalance": 1304244.791629,
        "beginPrincipalBalance": 1322888.75836,
        "prepayPrincipalPayment": 8196.246492,
        "scheduledPrincipalPayment": 10447.720239
    }
    {
        "date": "2044-04-25",
        "totalCashFlow": 20891.915378,
        "interestPayment": 543.43533,
        "principalBalance": 1283896.311581,
        "principalPayment": 20348.480048,
        "endPrincipalBalance": 1283896.311581,
        "beginPrincipalBalance": 1304244.791629,
        "prepayPrincipalPayment": 9955.191161,
        "scheduledPrincipalPayment": 10393.288887
    }
    {
        "date": "2044-05-25",
        "totalCashFlow": 20761.679367,
        "interestPayment": 534.956796,
        "principalBalance": 1263669.58901,
        "principalPayment": 20226.722571,
        "endPrincipalBalance": 1263669.58901,
        "beginPrincipalBalance": 1283896.311581,
        "prepayPrincipalPayment": 9902.658997,
        "scheduledPrincipalPayment": 10324.063573
    }
    {
        "date": "2044-06-25",
        "totalCashFlow": 21603.247267,
        "interestPayment": 526.528995,
        "principalBalance": 1242592.870738,
        "principalPayment": 21076.718272,
        "endPrincipalBalance": 1242592.870738,
        "beginPrincipalBalance": 1263669.58901,
        "prepayPrincipalPayment": 10822.258825,
        "scheduledPrincipalPayment": 10254.459447
    }
    {
        "date": "2044-07-25",
        "totalCashFlow": 22164.271843,
        "interestPayment": 517.747029,
        "principalBalance": 1220946.345924,
        "principalPayment": 21646.524813,
        "endPrincipalBalance": 1220946.345924,
        "beginPrincipalBalance": 1242592.870738,
        "prepayPrincipalPayment": 11470.015099,
        "scheduledPrincipalPayment": 10176.509714
    }
    {
        "date": "2044-08-25",
        "totalCashFlow": 20836.297577,
        "interestPayment": 508.727644,
        "principalBalance": 1200618.775991,
        "principalPayment": 20327.569933,
        "endPrincipalBalance": 1200618.775991,
        "beginPrincipalBalance": 1220946.345924,
        "prepayPrincipalPayment": 10235.270429,
        "scheduledPrincipalPayment": 10092.299504
    }
    {
        "date": "2044-09-25",
        "totalCashFlow": 21406.665695,
        "interestPayment": 500.257823,
        "principalBalance": 1179712.36812,
        "principalPayment": 20906.407872,
        "endPrincipalBalance": 1179712.36812,
        "beginPrincipalBalance": 1200618.775991,
        "prepayPrincipalPayment": 10888.99397,
        "scheduledPrincipalPayment": 10017.413901
    }
    {
        "date": "2044-10-25",
        "totalCashFlow": 20015.87817,
        "interestPayment": 491.54682,
        "principalBalance": 1160188.03677,
        "principalPayment": 19524.33135,
        "endPrincipalBalance": 1160188.03677,
        "beginPrincipalBalance": 1179712.36812,
        "prepayPrincipalPayment": 9588.195275,
        "scheduledPrincipalPayment": 9936.136076
    }
    {
        "date": "2044-11-25",
        "totalCashFlow": 19008.014853,
        "interestPayment": 483.411682,
        "principalBalance": 1141663.433598,
        "principalPayment": 18524.603172,
        "endPrincipalBalance": 1141663.433598,
        "beginPrincipalBalance": 1160188.03677,
        "prepayPrincipalPayment": 8659.644386,
        "scheduledPrincipalPayment": 9864.958785
    }
    {
        "date": "2044-12-25",
        "totalCashFlow": 18699.211652,
        "interestPayment": 475.693097,
        "principalBalance": 1123439.915043,
        "principalPayment": 18223.518555,
        "endPrincipalBalance": 1123439.915043,
        "beginPrincipalBalance": 1141663.433598,
        "prepayPrincipalPayment": 8422.624643,
        "scheduledPrincipalPayment": 9800.893912
    }
    {
        "date": "2045-01-25",
        "totalCashFlow": 18545.876452,
        "interestPayment": 468.099965,
        "principalBalance": 1105362.138556,
        "principalPayment": 18077.776487,
        "endPrincipalBalance": 1105362.138556,
        "beginPrincipalBalance": 1123439.915043,
        "prepayPrincipalPayment": 8339.681505,
        "scheduledPrincipalPayment": 9738.094982
    }
    {
        "date": "2045-02-25",
        "totalCashFlow": 16821.160917,
        "interestPayment": 460.567558,
        "principalBalance": 1089001.545197,
        "principalPayment": 16360.593359,
        "endPrincipalBalance": 1089001.545197,
        "beginPrincipalBalance": 1105362.138556,
        "prepayPrincipalPayment": 6685.351811,
        "scheduledPrincipalPayment": 9675.241548
    }
    {
        "date": "2045-03-25",
        "totalCashFlow": 16767.408374,
        "interestPayment": 453.750644,
        "principalBalance": 1072687.887467,
        "principalPayment": 16313.65773,
        "endPrincipalBalance": 1072687.887467,
        "beginPrincipalBalance": 1089001.545197,
        "prepayPrincipalPayment": 6687.432945,
        "scheduledPrincipalPayment": 9626.224784
    }
    {
        "date": "2045-04-25",
        "totalCashFlow": 18298.457014,
        "interestPayment": 446.953286,
        "principalBalance": 1054836.38374,
        "principalPayment": 17851.503728,
        "endPrincipalBalance": 1054836.38374,
        "beginPrincipalBalance": 1072687.887467,
        "prepayPrincipalPayment": 8274.954482,
        "scheduledPrincipalPayment": 9576.549245
    }
    {
        "date": "2045-05-25",
        "totalCashFlow": 18016.637642,
        "interestPayment": 439.51516,
        "principalBalance": 1037259.261257,
        "principalPayment": 17577.122482,
        "endPrincipalBalance": 1037259.261257,
        "beginPrincipalBalance": 1054836.38374,
        "prepayPrincipalPayment": 8065.216431,
        "scheduledPrincipalPayment": 9511.906051
    }
    {
        "date": "2045-06-25",
        "totalCashFlow": 19113.353486,
        "interestPayment": 432.191359,
        "principalBalance": 1018578.099131,
        "principalPayment": 18681.162127,
        "endPrincipalBalance": 1018578.099131,
        "beginPrincipalBalance": 1037259.261257,
        "prepayPrincipalPayment": 9232.813539,
        "scheduledPrincipalPayment": 9448.348588
    }
    {
        "date": "2045-07-25",
        "totalCashFlow": 19177.955611,
        "interestPayment": 424.407541,
        "principalBalance": 999824.551061,
        "principalPayment": 18753.54807,
        "endPrincipalBalance": 999824.551061,
        "beginPrincipalBalance": 1018578.099131,
        "prepayPrincipalPayment": 9380.320269,
        "scheduledPrincipalPayment": 9373.227801
    }
    {
        "date": "2045-08-25",
        "totalCashFlow": 18123.697815,
        "interestPayment": 416.593563,
        "principalBalance": 982117.446809,
        "principalPayment": 17707.104252,
        "endPrincipalBalance": 982117.446809,
        "beginPrincipalBalance": 999824.551061,
        "prepayPrincipalPayment": 8411.325357,
        "scheduledPrincipalPayment": 9295.778895
    }
    {
        "date": "2045-09-25",
        "totalCashFlow": 18529.828873,
        "interestPayment": 409.215603,
        "principalBalance": 963996.833538,
        "principalPayment": 18120.61327,
        "endPrincipalBalance": 963996.833538,
        "beginPrincipalBalance": 982117.446809,
        "prepayPrincipalPayment": 8894.170954,
        "scheduledPrincipalPayment": 9226.442317
    }
    {
        "date": "2045-10-25",
        "totalCashFlow": 17155.701943,
        "interestPayment": 401.665347,
        "principalBalance": 947242.796943,
        "principalPayment": 16754.036595,
        "endPrincipalBalance": 947242.796943,
        "beginPrincipalBalance": 963996.833538,
        "prepayPrincipalPayment": 7602.419413,
        "scheduledPrincipalPayment": 9151.617182
    }
    {
        "date": "2045-11-25",
        "totalCashFlow": 16884.418079,
        "interestPayment": 394.684499,
        "principalBalance": 930753.063363,
        "principalPayment": 16489.73358,
        "endPrincipalBalance": 930753.063363,
        "beginPrincipalBalance": 947242.796943,
        "prepayPrincipalPayment": 7401.523982,
        "scheduledPrincipalPayment": 9088.209598
    }
    {
        "date": "2045-12-25",
        "totalCashFlow": 16370.861387,
        "interestPayment": 387.813776,
        "principalBalance": 914770.015752,
        "principalPayment": 15983.047611,
        "endPrincipalBalance": 914770.015752,
        "beginPrincipalBalance": 930753.063363,
        "prepayPrincipalPayment": 6957.146794,
        "scheduledPrincipalPayment": 9025.900817
    }
    {
        "date": "2046-01-25",
        "totalCashFlow": 16001.698453,
        "interestPayment": 381.154173,
        "principalBalance": 899149.471472,
        "principalPayment": 15620.54428,
        "endPrincipalBalance": 899149.471472,
        "beginPrincipalBalance": 914770.015752,
        "prepayPrincipalPayment": 6653.43946,
        "scheduledPrincipalPayment": 8967.10482
    }
    {
        "date": "2046-02-25",
        "totalCashFlow": 15067.747578,
        "interestPayment": 374.645613,
        "principalBalance": 884456.369507,
        "principalPayment": 14693.101965,
        "endPrincipalBalance": 884456.369507,
        "beginPrincipalBalance": 899149.471472,
        "prepayPrincipalPayment": 5782.591546,
        "scheduledPrincipalPayment": 8910.510419
    }
    {
        "date": "2046-03-25",
        "totalCashFlow": 14828.012695,
        "interestPayment": 368.523487,
        "principalBalance": 869996.880299,
        "principalPayment": 14459.489207,
        "endPrincipalBalance": 869996.880299,
        "beginPrincipalBalance": 884456.369507,
        "prepayPrincipalPayment": 5597.635961,
        "scheduledPrincipalPayment": 8861.853246
    }
    {
        "date": "2046-04-25",
        "totalCashFlow": 15660.641531,
        "interestPayment": 362.4987,
        "principalBalance": 854698.737468,
        "principalPayment": 15298.142831,
        "endPrincipalBalance": 854698.737468,
        "beginPrincipalBalance": 869996.880299,
        "prepayPrincipalPayment": 6483.770927,
        "scheduledPrincipalPayment": 8814.371904
    }
    {
        "date": "2046-05-25",
        "totalCashFlow": 15953.773943,
        "interestPayment": 356.124474,
        "principalBalance": 839101.087999,
        "principalPayment": 15597.649469,
        "endPrincipalBalance": 839101.087999,
        "beginPrincipalBalance": 854698.737468,
        "prepayPrincipalPayment": 6840.527723,
        "scheduledPrincipalPayment": 8757.121746
    }
    {
        "date": "2046-06-25",
        "totalCashFlow": 16522.470479,
        "interestPayment": 349.625453,
        "principalBalance": 822928.242973,
        "principalPayment": 16172.845026,
        "endPrincipalBalance": 822928.242973,
        "beginPrincipalBalance": 839101.087999,
        "prepayPrincipalPayment": 7477.487651,
        "scheduledPrincipalPayment": 8695.357375
    }
    {
        "date": "2046-07-25",
        "totalCashFlow": 16280.456863,
        "interestPayment": 342.886768,
        "principalBalance": 806990.672878,
        "principalPayment": 15937.570095,
        "endPrincipalBalance": 806990.672878,
        "beginPrincipalBalance": 822928.242973,
        "prepayPrincipalPayment": 7311.535002,
        "scheduledPrincipalPayment": 8626.035093
    }
    {
        "date": "2046-08-25",
        "totalCashFlow": 15959.211649,
        "interestPayment": 336.246114,
        "principalBalance": 791367.707343,
        "principalPayment": 15622.965535,
        "endPrincipalBalance": 791367.707343,
        "beginPrincipalBalance": 806990.672878,
        "prepayPrincipalPayment": 7065.477942,
        "scheduledPrincipalPayment": 8557.487593
    }
    {
        "date": "2046-09-25",
        "totalCashFlow": 15991.408499,
        "interestPayment": 329.736545,
        "principalBalance": 775706.03539,
        "principalPayment": 15661.671954,
        "endPrincipalBalance": 775706.03539,
        "beginPrincipalBalance": 791367.707343,
        "prepayPrincipalPayment": 7171.07593,
        "scheduledPrincipalPayment": 8490.596023
    }
    {
        "date": "2046-10-25",
        "totalCashFlow": 14721.816392,
        "interestPayment": 323.210848,
        "principalBalance": 761307.429846,
        "principalPayment": 14398.605543,
        "endPrincipalBalance": 761307.429846,
        "beginPrincipalBalance": 775706.03539,
        "prepayPrincipalPayment": 5977.019172,
        "scheduledPrincipalPayment": 8421.586372
    }
    {
        "date": "2046-11-25",
        "totalCashFlow": 14889.680614,
        "interestPayment": 317.211429,
        "principalBalance": 746734.960661,
        "principalPayment": 14572.469185,
        "endPrincipalBalance": 746734.960661,
        "beginPrincipalBalance": 761307.429846,
        "prepayPrincipalPayment": 6207.781431,
        "scheduledPrincipalPayment": 8364.687754
    }
    {
        "date": "2046-12-25",
        "totalCashFlow": 14287.999165,
        "interestPayment": 311.139567,
        "principalBalance": 732758.101063,
        "principalPayment": 13976.859598,
        "endPrincipalBalance": 732758.101063,
        "beginPrincipalBalance": 746734.960661,
        "prepayPrincipalPayment": 5672.494745,
        "scheduledPrincipalPayment": 8304.364853
    }
    {
        "date": "2047-01-25",
        "totalCashFlow": 13986.274264,
        "interestPayment": 305.315875,
        "principalBalance": 719077.142674,
        "principalPayment": 13680.958389,
        "endPrincipalBalance": 719077.142674,
        "beginPrincipalBalance": 732758.101063,
        "prepayPrincipalPayment": 5431.802285,
        "scheduledPrincipalPayment": 8249.156104
    }
    {
        "date": "2047-02-25",
        "totalCashFlow": 13265.549462,
        "interestPayment": 299.615476,
        "principalBalance": 706111.208689,
        "principalPayment": 12965.933985,
        "endPrincipalBalance": 706111.208689,
        "beginPrincipalBalance": 719077.142674,
        "prepayPrincipalPayment": 4770.095164,
        "scheduledPrincipalPayment": 8195.838822
    }
    {
        "date": "2047-03-25",
        "totalCashFlow": 13061.897349,
        "interestPayment": 294.213004,
        "principalBalance": 693343.524344,
        "principalPayment": 12767.684345,
        "endPrincipalBalance": 693343.524344,
        "beginPrincipalBalance": 706111.208689,
        "prepayPrincipalPayment": 4618.360498,
        "scheduledPrincipalPayment": 8149.323848
    }
    {
        "date": "2047-04-25",
        "totalCashFlow": 13580.261658,
        "interestPayment": 288.893135,
        "principalBalance": 680052.155821,
        "principalPayment": 13291.368523,
        "endPrincipalBalance": 680052.155821,
        "beginPrincipalBalance": 693343.524344,
        "prepayPrincipalPayment": 5187.53542,
        "scheduledPrincipalPayment": 8103.833103
    }
    {
        "date": "2047-05-25",
        "totalCashFlow": 13930.006926,
        "interestPayment": 283.355065,
        "principalBalance": 666405.503959,
        "principalPayment": 13646.651862,
        "endPrincipalBalance": 666405.503959,
        "beginPrincipalBalance": 680052.155821,
        "prepayPrincipalPayment": 5595.790392,
        "scheduledPrincipalPayment": 8050.861469
    }
    {
        "date": "2047-06-25",
        "totalCashFlow": 14234.757656,
        "interestPayment": 277.66896,
        "principalBalance": 652448.415263,
        "principalPayment": 13957.088696,
        "endPrincipalBalance": 652448.415263,
        "beginPrincipalBalance": 666405.503959,
        "prepayPrincipalPayment": 5964.950696,
        "scheduledPrincipalPayment": 7992.138
    }
    {
        "date": "2047-07-25",
        "totalCashFlow": 13834.144428,
        "interestPayment": 271.853506,
        "principalBalance": 638886.124341,
        "principalPayment": 13562.290922,
        "endPrincipalBalance": 638886.124341,
        "beginPrincipalBalance": 652448.415263,
        "prepayPrincipalPayment": 5634.30864,
        "scheduledPrincipalPayment": 7927.982282
    }
    {
        "date": "2047-08-25",
        "totalCashFlow": 13938.701532,
        "interestPayment": 266.202552,
        "principalBalance": 625213.625361,
        "principalPayment": 13672.49898,
        "endPrincipalBalance": 625213.625361,
        "beginPrincipalBalance": 638886.124341,
        "prepayPrincipalPayment": 5805.635903,
        "scheduledPrincipalPayment": 7866.863077
    }
    {
        "date": "2047-09-25",
        "totalCashFlow": 13587.014725,
        "interestPayment": 260.505677,
        "principalBalance": 611887.116314,
        "principalPayment": 13326.509047,
        "endPrincipalBalance": 611887.116314,
        "beginPrincipalBalance": 625213.625361,
        "prepayPrincipalPayment": 5523.905081,
        "scheduledPrincipalPayment": 7802.603966
    }
    {
        "date": "2047-10-25",
        "totalCashFlow": 12945.202713,
        "interestPayment": 254.952965,
        "principalBalance": 599196.866566,
        "principalPayment": 12690.249747,
        "endPrincipalBalance": 599196.866566,
        "beginPrincipalBalance": 611887.116314,
        "prepayPrincipalPayment": 4949.399782,
        "scheduledPrincipalPayment": 7740.849965
    }
    {
        "date": "2047-11-25",
        "totalCashFlow": 12886.48445,
        "interestPayment": 249.665361,
        "principalBalance": 586560.047478,
        "principalPayment": 12636.819089,
        "endPrincipalBalance": 586560.047478,
        "beginPrincipalBalance": 599196.866566,
        "prepayPrincipalPayment": 4951.387832,
        "scheduledPrincipalPayment": 7685.431256
    }
    {
        "date": "2047-12-25",
        "totalCashFlow": 12284.212075,
        "interestPayment": 244.40002,
        "principalBalance": 574520.235423,
        "principalPayment": 12039.812055,
        "endPrincipalBalance": 574520.235423,
        "beginPrincipalBalance": 586560.047478,
        "prepayPrincipalPayment": 4410.774893,
        "scheduledPrincipalPayment": 7629.037162
    }
    {
        "date": "2048-01-25",
        "totalCashFlow": 12297.081322,
        "interestPayment": 239.383431,
        "principalBalance": 562462.537533,
        "principalPayment": 12057.69789,
        "endPrincipalBalance": 562462.537533,
        "beginPrincipalBalance": 574520.235423,
        "prepayPrincipalPayment": 4478.898671,
        "scheduledPrincipalPayment": 7578.799219
    }
    {
        "date": "2048-02-25",
        "totalCashFlow": 11620.187837,
        "interestPayment": 234.359391,
        "principalBalance": 551076.709086,
        "principalPayment": 11385.828447,
        "endPrincipalBalance": 551076.709086,
        "beginPrincipalBalance": 562462.537533,
        "prepayPrincipalPayment": 3859.070347,
        "scheduledPrincipalPayment": 7526.7581
    }
    {
        "date": "2048-03-25",
        "totalCashFlow": 11445.644324,
        "interestPayment": 229.615295,
        "principalBalance": 539860.680057,
        "principalPayment": 11216.029028,
        "endPrincipalBalance": 539860.680057,
        "beginPrincipalBalance": 551076.709086,
        "prepayPrincipalPayment": 3733.826791,
        "scheduledPrincipalPayment": 7482.202238
    }
    {
        "date": "2048-04-25",
        "totalCashFlow": 11903.932825,
        "interestPayment": 224.94195,
        "principalBalance": 528181.689182,
        "principalPayment": 11678.990875,
        "endPrincipalBalance": 528181.689182,
        "beginPrincipalBalance": 539860.680057,
        "prepayPrincipalPayment": 4240.441754,
        "scheduledPrincipalPayment": 7438.549122
    }
    {
        "date": "2048-05-25",
        "totalCashFlow": 12073.691443,
        "interestPayment": 220.075704,
        "principalBalance": 516328.073444,
        "principalPayment": 11853.615739,
        "endPrincipalBalance": 516328.073444,
        "beginPrincipalBalance": 528181.689182,
        "prepayPrincipalPayment": 4466.623686,
        "scheduledPrincipalPayment": 7386.992053
    }
    {
        "date": "2048-06-25",
        "totalCashFlow": 11935.406733,
        "interestPayment": 215.136697,
        "principalBalance": 504607.803408,
        "principalPayment": 11720.270036,
        "endPrincipalBalance": 504607.803408,
        "beginPrincipalBalance": 516328.073444,
        "prepayPrincipalPayment": 4389.004129,
        "scheduledPrincipalPayment": 7331.265907
    }
    {
        "date": "2048-07-25",
        "totalCashFlow": 12156.913928,
        "interestPayment": 210.253251,
        "principalBalance": 492661.142731,
        "principalPayment": 11946.660677,
        "endPrincipalBalance": 492661.142731,
        "beginPrincipalBalance": 504607.803408,
        "prepayPrincipalPayment": 4671.040305,
        "scheduledPrincipalPayment": 7275.620372
    }
    {
        "date": "2048-08-25",
        "totalCashFlow": 11919.68659,
        "interestPayment": 205.275476,
        "principalBalance": 480946.731617,
        "principalPayment": 11714.411114,
        "endPrincipalBalance": 480946.731617,
        "beginPrincipalBalance": 492661.142731,
        "prepayPrincipalPayment": 4499.61719,
        "scheduledPrincipalPayment": 7214.793924
    }
    {
        "date": "2048-09-25",
        "totalCashFlow": 11519.395973,
        "interestPayment": 200.394472,
        "principalBalance": 469627.730115,
        "principalPayment": 11319.001502,
        "endPrincipalBalance": 469627.730115,
        "beginPrincipalBalance": 480946.731617,
        "prepayPrincipalPayment": 4163.635976,
        "scheduledPrincipalPayment": 7155.365526
    }
    {
        "date": "2048-10-25",
        "totalCashFlow": 11259.693829,
        "interestPayment": 195.678221,
        "principalBalance": 458563.714508,
        "principalPayment": 11064.015608,
        "endPrincipalBalance": 458563.714508,
        "beginPrincipalBalance": 469627.730115,
        "prepayPrincipalPayment": 3964.142786,
        "scheduledPrincipalPayment": 7099.872822
    }
    {
        "date": "2048-11-25",
        "totalCashFlow": 10981.412751,
        "interestPayment": 191.068214,
        "principalBalance": 447773.369971,
        "principalPayment": 10790.344536,
        "endPrincipalBalance": 447773.369971,
        "beginPrincipalBalance": 458563.714508,
        "prepayPrincipalPayment": 3743.989593,
        "scheduledPrincipalPayment": 7046.354943
    }
    {
        "date": "2048-12-25",
        "totalCashFlow": 10623.3386,
        "interestPayment": 186.572237,
        "principalBalance": 437336.603609,
        "principalPayment": 10436.766363,
        "endPrincipalBalance": 437336.603609,
        "beginPrincipalBalance": 447773.369971,
        "prepayPrincipalPayment": 3441.560824,
        "scheduledPrincipalPayment": 6995.205539
    }
    {
        "date": "2049-01-25",
        "totalCashFlow": 10691.971208,
        "interestPayment": 182.223585,
        "principalBalance": 426826.855986,
        "principalPayment": 10509.747623,
        "endPrincipalBalance": 426826.855986,
        "beginPrincipalBalance": 437336.603609,
        "prepayPrincipalPayment": 3561.930314,
        "scheduledPrincipalPayment": 6947.817309
    }
    {
        "date": "2049-02-25",
        "totalCashFlow": 9965.941668,
        "interestPayment": 177.844523,
        "principalBalance": 417038.758841,
        "principalPayment": 9788.097145,
        "endPrincipalBalance": 417038.758841,
        "beginPrincipalBalance": 426826.855986,
        "prepayPrincipalPayment": 2890.603086,
        "scheduledPrincipalPayment": 6897.494058
    }
    {
        "date": "2049-03-25",
        "totalCashFlow": 9992.56066,
        "interestPayment": 173.76615,
        "principalBalance": 407219.964331,
        "principalPayment": 9818.79451,
        "endPrincipalBalance": 407219.964331,
        "beginPrincipalBalance": 417038.758841,
        "prepayPrincipalPayment": 2961.644237,
        "scheduledPrincipalPayment": 6857.150273
    }
    {
        "date": "2049-04-25",
        "totalCashFlow": 10399.66706,
        "interestPayment": 169.674985,
        "principalBalance": 396989.972256,
        "principalPayment": 10229.992075,
        "endPrincipalBalance": 396989.972256,
        "beginPrincipalBalance": 407219.964331,
        "prepayPrincipalPayment": 3415.26136,
        "scheduledPrincipalPayment": 6814.730715
    }
    {
        "date": "2049-05-25",
        "totalCashFlow": 10400.116912,
        "interestPayment": 165.412488,
        "principalBalance": 386755.267832,
        "principalPayment": 10234.704423,
        "endPrincipalBalance": 386755.267832,
        "beginPrincipalBalance": 396989.972256,
        "prepayPrincipalPayment": 3471.061908,
        "scheduledPrincipalPayment": 6763.642515
    }
    {
        "date": "2049-06-25",
        "totalCashFlow": 10347.594303,
        "interestPayment": 161.148028,
        "principalBalance": 376568.821558,
        "principalPayment": 10186.446275,
        "endPrincipalBalance": 376568.821558,
        "beginPrincipalBalance": 386755.267832,
        "prepayPrincipalPayment": 3475.983546,
        "scheduledPrincipalPayment": 6710.462729
    }
    {
        "date": "2049-07-25",
        "totalCashFlow": 10497.26152,
        "interestPayment": 156.903676,
        "principalBalance": 366228.463713,
        "principalPayment": 10340.357844,
        "endPrincipalBalance": 366228.463713,
        "beginPrincipalBalance": 376568.821558,
        "prepayPrincipalPayment": 3684.34453,
        "scheduledPrincipalPayment": 6656.013314
    }
    {
        "date": "2049-08-25",
        "totalCashFlow": 10240.831754,
        "interestPayment": 152.595193,
        "principalBalance": 356140.227153,
        "principalPayment": 10088.236561,
        "endPrincipalBalance": 356140.227153,
        "beginPrincipalBalance": 366228.463713,
        "prepayPrincipalPayment": 3491.653082,
        "scheduledPrincipalPayment": 6596.583479
    }
    {
        "date": "2049-09-25",
        "totalCashFlow": 10127.883387,
        "interestPayment": 148.391761,
        "principalBalance": 346160.735528,
        "principalPayment": 9979.491625,
        "endPrincipalBalance": 346160.735528,
        "beginPrincipalBalance": 356140.227153,
        "prepayPrincipalPayment": 3440.149413,
        "scheduledPrincipalPayment": 6539.342212
    }
    {
        "date": "2049-10-25",
        "totalCashFlow": 9858.05354,
        "interestPayment": 144.23364,
        "principalBalance": 336446.915627,
        "principalPayment": 9713.8199,
        "endPrincipalBalance": 336446.915627,
        "beginPrincipalBalance": 346160.735528,
        "prepayPrincipalPayment": 3232.081465,
        "scheduledPrincipalPayment": 6481.738435
    }
    {
        "date": "2049-11-25",
        "totalCashFlow": 9592.434902,
        "interestPayment": 140.186215,
        "principalBalance": 326994.66694,
        "principalPayment": 9452.248687,
        "endPrincipalBalance": 326994.66694,
        "beginPrincipalBalance": 336446.915627,
        "prepayPrincipalPayment": 3025.49711,
        "scheduledPrincipalPayment": 6426.751577
    }
    {
        "date": "2049-12-25",
        "totalCashFlow": 9466.694509,
        "interestPayment": 136.247778,
        "principalBalance": 317664.220209,
        "principalPayment": 9330.446731,
        "endPrincipalBalance": 317664.220209,
        "beginPrincipalBalance": 326994.66694,
        "prepayPrincipalPayment": 2955.979964,
        "scheduledPrincipalPayment": 6374.466767
    }
    {
        "date": "2050-01-25",
        "totalCashFlow": 9373.392436,
        "interestPayment": 132.360092,
        "principalBalance": 308423.187865,
        "principalPayment": 9241.032344,
        "endPrincipalBalance": 308423.187865,
        "beginPrincipalBalance": 317664.220209,
        "prepayPrincipalPayment": 2918.756561,
        "scheduledPrincipalPayment": 6322.275783
    }
    {
        "date": "2050-02-25",
        "totalCashFlow": 8975.826765,
        "interestPayment": 128.509662,
        "principalBalance": 299575.870762,
        "principalPayment": 8847.317104,
        "endPrincipalBalance": 299575.870762,
        "beginPrincipalBalance": 308423.187865,
        "prepayPrincipalPayment": 2577.787185,
        "scheduledPrincipalPayment": 6269.529918
    }
    {
        "date": "2050-03-25",
        "totalCashFlow": 8903.352274,
        "interestPayment": 124.823279,
        "principalBalance": 290797.341767,
        "principalPayment": 8778.528995,
        "endPrincipalBalance": 290797.341767,
        "beginPrincipalBalance": 299575.870762,
        "prepayPrincipalPayment": 2556.011764,
        "scheduledPrincipalPayment": 6222.51723
    }
    {
        "date": "2050-04-25",
        "totalCashFlow": 9125.356904,
        "interestPayment": 121.165559,
        "principalBalance": 281793.150422,
        "principalPayment": 9004.191345,
        "endPrincipalBalance": 281793.150422,
        "beginPrincipalBalance": 290797.341767,
        "prepayPrincipalPayment": 2829.466104,
        "scheduledPrincipalPayment": 6174.725241
    }
    {
        "date": "2050-05-25",
        "totalCashFlow": 9019.035493,
        "interestPayment": 117.413813,
        "principalBalance": 272891.528742,
        "principalPayment": 8901.62168,
        "endPrincipalBalance": 272891.528742,
        "beginPrincipalBalance": 281793.150422,
        "prepayPrincipalPayment": 2781.912027,
        "scheduledPrincipalPayment": 6119.709653
    }
    {
        "date": "2050-06-25",
        "totalCashFlow": 9048.643734,
        "interestPayment": 113.704804,
        "principalBalance": 263956.589812,
        "principalPayment": 8934.93893,
        "endPrincipalBalance": 263956.589812,
        "beginPrincipalBalance": 272891.528742,
        "prepayPrincipalPayment": 2870.674927,
        "scheduledPrincipalPayment": 6064.264004
    }
    {
        "date": "2050-07-25",
        "totalCashFlow": 9031.436385,
        "interestPayment": 109.981912,
        "principalBalance": 255035.135339,
        "principalPayment": 8921.454473,
        "endPrincipalBalance": 255035.135339,
        "beginPrincipalBalance": 263956.589812,
        "prepayPrincipalPayment": 2916.184186,
        "scheduledPrincipalPayment": 6005.270286
    }
    {
        "date": "2050-08-25",
        "totalCashFlow": 8757.002068,
        "interestPayment": 106.26464,
        "principalBalance": 246384.397911,
        "principalPayment": 8650.737428,
        "endPrincipalBalance": 246384.397911,
        "beginPrincipalBalance": 255035.135339,
        "prepayPrincipalPayment": 2707.172988,
        "scheduledPrincipalPayment": 5943.56444
    }
    {
        "date": "2050-09-25",
        "totalCashFlow": 8739.883941,
        "interestPayment": 102.660166,
        "principalBalance": 237747.174136,
        "principalPayment": 8637.223775,
        "endPrincipalBalance": 237747.174136,
        "beginPrincipalBalance": 246384.397911,
        "prepayPrincipalPayment": 2752.13116,
        "scheduledPrincipalPayment": 5885.092614
    }
    {
        "date": "2050-10-25",
        "totalCashFlow": 8462.178098,
        "interestPayment": 99.061323,
        "principalBalance": 229384.057361,
        "principalPayment": 8363.116775,
        "endPrincipalBalance": 229384.057361,
        "beginPrincipalBalance": 237747.174136,
        "prepayPrincipalPayment": 2539.309511,
        "scheduledPrincipalPayment": 5823.807264
    }
    {
        "date": "2050-11-25",
        "totalCashFlow": 8242.740458,
        "interestPayment": 95.576691,
        "principalBalance": 221236.893594,
        "principalPayment": 8147.163767,
        "endPrincipalBalance": 221236.893594,
        "beginPrincipalBalance": 229384.057361,
        "prepayPrincipalPayment": 2381.120836,
        "scheduledPrincipalPayment": 5766.042931
    }
    {
        "date": "2050-12-25",
        "totalCashFlow": 8111.768492,
        "interestPayment": 92.182039,
        "principalBalance": 213217.307141,
        "principalPayment": 8019.586453,
        "endPrincipalBalance": 213217.307141,
        "beginPrincipalBalance": 221236.893594,
        "prepayPrincipalPayment": 2308.998942,
        "scheduledPrincipalPayment": 5710.587511
    }
    {
        "date": "2051-01-25",
        "totalCashFlow": 8001.616146,
        "interestPayment": 88.840545,
        "principalBalance": 205304.531539,
        "principalPayment": 7912.775601,
        "endPrincipalBalance": 205304.531539,
        "beginPrincipalBalance": 213217.307141,
        "prepayPrincipalPayment": 2257.482553,
        "scheduledPrincipalPayment": 5655.293048
    }
    {
        "date": "2051-02-25",
        "totalCashFlow": 7705.948004,
        "interestPayment": 85.543555,
        "principalBalance": 197684.12709,
        "principalPayment": 7620.404449,
        "endPrincipalBalance": 197684.12709,
        "beginPrincipalBalance": 205304.531539,
        "prepayPrincipalPayment": 2020.792546,
        "scheduledPrincipalPayment": 5599.611903
    }
    {
        "date": "2051-03-25",
        "totalCashFlow": 7610.910405,
        "interestPayment": 82.368386,
        "principalBalance": 190155.585072,
        "principalPayment": 7528.542018,
        "endPrincipalBalance": 190155.585072,
        "beginPrincipalBalance": 197684.12709,
        "prepayPrincipalPayment": 1979.818078,
        "scheduledPrincipalPayment": 5548.72394
    }
    {
        "date": "2051-04-25",
        "totalCashFlow": 7676.696209,
        "interestPayment": 79.231494,
        "principalBalance": 182558.120357,
        "principalPayment": 7597.464716,
        "endPrincipalBalance": 182558.120357,
        "beginPrincipalBalance": 190155.585072,
        "prepayPrincipalPayment": 2100.196049,
        "scheduledPrincipalPayment": 5497.268666
    }
    {
        "date": "2051-05-25",
        "totalCashFlow": 7556.033163,
        "interestPayment": 76.065883,
        "principalBalance": 175078.153077,
        "principalPayment": 7479.967279,
        "endPrincipalBalance": 175078.153077,
        "beginPrincipalBalance": 182558.120357,
        "prepayPrincipalPayment": 2039.560148,
        "scheduledPrincipalPayment": 5440.407131
    }
    {
        "date": "2051-06-25",
        "totalCashFlow": 7567.658055,
        "interestPayment": 72.94923,
        "principalBalance": 167583.444253,
        "principalPayment": 7494.708825,
        "endPrincipalBalance": 167583.444253,
        "beginPrincipalBalance": 175078.153077,
        "prepayPrincipalPayment": 2111.347675,
        "scheduledPrincipalPayment": 5383.361149
    }
    {
        "date": "2051-07-25",
        "totalCashFlow": 7461.953249,
        "interestPayment": 69.826435,
        "principalBalance": 160191.317439,
        "principalPayment": 7392.126814,
        "endPrincipalBalance": 160191.317439,
        "beginPrincipalBalance": 167583.444253,
        "prepayPrincipalPayment": 2070.207708,
        "scheduledPrincipalPayment": 5321.919106
    }
    {
        "date": "2051-08-25",
        "totalCashFlow": 7243.463543,
        "interestPayment": 66.746382,
        "principalBalance": 153014.600279,
        "principalPayment": 7176.717161,
        "endPrincipalBalance": 153014.600279,
        "beginPrincipalBalance": 160191.317439,
        "prepayPrincipalPayment": 1917.224627,
        "scheduledPrincipalPayment": 5259.492534
    }
    {
        "date": "2051-09-25",
        "totalCashFlow": 7191.649624,
        "interestPayment": 63.756083,
        "principalBalance": 145886.706738,
        "principalPayment": 7127.89354,
        "endPrincipalBalance": 145886.706738,
        "beginPrincipalBalance": 153014.600279,
        "prepayPrincipalPayment": 1928.07446,
        "scheduledPrincipalPayment": 5199.819081
    }
    {
        "date": "2051-10-25",
        "totalCashFlow": 6963.513563,
        "interestPayment": 60.786128,
        "principalBalance": 138983.979304,
        "principalPayment": 6902.727435,
        "endPrincipalBalance": 138983.979304,
        "beginPrincipalBalance": 145886.706738,
        "prepayPrincipalPayment": 1765.38821,
        "scheduledPrincipalPayment": 5137.339225
    }
    {
        "date": "2051-11-25",
        "totalCashFlow": 6844.932485,
        "interestPayment": 57.909991,
        "principalBalance": 132196.95681,
        "principalPayment": 6787.022494,
        "endPrincipalBalance": 132196.95681,
        "beginPrincipalBalance": 138983.979304,
        "prepayPrincipalPayment": 1708.835506,
        "scheduledPrincipalPayment": 5078.186988
    }
    {
        "date": "2051-12-25",
        "totalCashFlow": 6700.687225,
        "interestPayment": 55.082065,
        "principalBalance": 125551.351651,
        "principalPayment": 6645.605159,
        "endPrincipalBalance": 125551.351651,
        "beginPrincipalBalance": 132196.95681,
        "prepayPrincipalPayment": 1627.001058,
        "scheduledPrincipalPayment": 5018.604101
    }
    {
        "date": "2052-01-25",
        "totalCashFlow": 6570.609639,
        "interestPayment": 52.313063,
        "principalBalance": 119033.055074,
        "principalPayment": 6518.296576,
        "endPrincipalBalance": 119033.055074,
        "beginPrincipalBalance": 125551.351651,
        "prepayPrincipalPayment": 1558.734974,
        "scheduledPrincipalPayment": 4959.561602
    }
    {
        "date": "2052-02-25",
        "totalCashFlow": 6395.296329,
        "interestPayment": 49.597106,
        "principalBalance": 112687.355851,
        "principalPayment": 6345.699223,
        "endPrincipalBalance": 112687.355851,
        "beginPrincipalBalance": 119033.055074,
        "prepayPrincipalPayment": 1445.144062,
        "scheduledPrincipalPayment": 4900.555161
    }
    {
        "date": "2052-03-25",
        "totalCashFlow": 6290.82994,
        "interestPayment": 46.953065,
        "principalBalance": 106443.478977,
        "principalPayment": 6243.876875,
        "endPrincipalBalance": 106443.478977,
        "beginPrincipalBalance": 112687.355851,
        "prepayPrincipalPayment": 1400.332364,
        "scheduledPrincipalPayment": 4843.544511
    }
    {
        "date": "2052-04-25",
        "totalCashFlow": 6227.916178,
        "interestPayment": 44.35145,
        "principalBalance": 100259.914248,
        "principalPayment": 6183.564728,
        "endPrincipalBalance": 100259.914248,
        "beginPrincipalBalance": 106443.478977,
        "prepayPrincipalPayment": 1397.93292,
        "scheduledPrincipalPayment": 4785.631808
    }
    {
        "date": "2052-05-25",
        "totalCashFlow": 6152.332044,
        "interestPayment": 41.774964,
        "principalBalance": 94149.357168,
        "principalPayment": 6110.55708,
        "endPrincipalBalance": 94149.357168,
        "beginPrincipalBalance": 100259.914248,
        "prepayPrincipalPayment": 1385.817701,
        "scheduledPrincipalPayment": 4724.739379
    }
    {
        "date": "2052-06-25",
        "totalCashFlow": 6064.71896,
        "interestPayment": 39.228899,
        "principalBalance": 88123.867107,
        "principalPayment": 6025.490061,
        "endPrincipalBalance": 88123.867107,
        "beginPrincipalBalance": 94149.357168,
        "prepayPrincipalPayment": 1364.436771,
        "scheduledPrincipalPayment": 4661.05329
    }
    {
        "date": "2052-07-25",
        "totalCashFlow": 5908.390274,
        "interestPayment": 36.718278,
        "principalBalance": 82252.195111,
        "principalPayment": 5871.671996,
        "endPrincipalBalance": 82252.195111,
        "beginPrincipalBalance": 88123.867107,
        "prepayPrincipalPayment": 1276.904999,
        "scheduledPrincipalPayment": 4594.766998
    }
    {
        "date": "2052-08-25",
        "totalCashFlow": 5796.101126,
        "interestPayment": 34.271748,
        "principalBalance": 76490.365733,
        "principalPayment": 5761.829378,
        "endPrincipalBalance": 76490.365733,
        "beginPrincipalBalance": 82252.195111,
        "prepayPrincipalPayment": 1232.589295,
        "scheduledPrincipalPayment": 4529.240083
    }
    {
        "date": "2052-09-25",
        "totalCashFlow": 5643.547386,
        "interestPayment": 31.870986,
        "principalBalance": 70878.689333,
        "principalPayment": 5611.676401,
        "endPrincipalBalance": 70878.689333,
        "beginPrincipalBalance": 76490.365733,
        "prepayPrincipalPayment": 1149.621288,
        "scheduledPrincipalPayment": 4462.055112
    }
    {
        "date": "2052-10-25",
        "totalCashFlow": 5470.227145,
        "interestPayment": 29.532787,
        "principalBalance": 65437.994975,
        "principalPayment": 5440.694358,
        "endPrincipalBalance": 65437.994975,
        "beginPrincipalBalance": 70878.689333,
        "prepayPrincipalPayment": 1045.282919,
        "scheduledPrincipalPayment": 4395.411438
    }
    {
        "date": "2052-11-25",
        "totalCashFlow": 5343.375557,
        "interestPayment": 27.265831,
        "principalBalance": 60121.885249,
        "principalPayment": 5316.109726,
        "endPrincipalBalance": 60121.885249,
        "beginPrincipalBalance": 65437.994975,
        "prepayPrincipalPayment": 985.298549,
        "scheduledPrincipalPayment": 4330.811177
    }
    {
        "date": "2052-12-25",
        "totalCashFlow": 5177.728664,
        "interestPayment": 25.050786,
        "principalBalance": 54969.20737,
        "principalPayment": 5152.677879,
        "endPrincipalBalance": 54969.20737,
        "beginPrincipalBalance": 60121.885249,
        "prepayPrincipalPayment": 887.258627,
        "scheduledPrincipalPayment": 4265.419251
    }
    {
        "date": "2053-01-25",
        "totalCashFlow": 5055.190237,
        "interestPayment": 22.903836,
        "principalBalance": 49936.92097,
        "principalPayment": 5032.286401,
        "endPrincipalBalance": 49936.92097,
        "beginPrincipalBalance": 54969.20737,
        "prepayPrincipalPayment": 830.249137,
        "scheduledPrincipalPayment": 4202.037263
    }
    {
        "date": "2053-02-25",
        "totalCashFlow": 4891.750769,
        "interestPayment": 20.80705,
        "principalBalance": 45065.977251,
        "principalPayment": 4870.943719,
        "endPrincipalBalance": 45065.977251,
        "beginPrincipalBalance": 49936.92097,
        "prepayPrincipalPayment": 733.321269,
        "scheduledPrincipalPayment": 4137.622449
    }
    {
        "date": "2053-03-25",
        "totalCashFlow": 4759.545389,
        "interestPayment": 18.777491,
        "principalBalance": 40325.209353,
        "principalPayment": 4740.767898,
        "endPrincipalBalance": 40325.209353,
        "beginPrincipalBalance": 45065.977251,
        "prepayPrincipalPayment": 665.154502,
        "scheduledPrincipalPayment": 4075.613396
    }
    {
        "date": "2053-04-25",
        "totalCashFlow": 4651.281334,
        "interestPayment": 16.802171,
        "principalBalance": 35690.730189,
        "principalPayment": 4634.479164,
        "endPrincipalBalance": 35690.730189,
        "beginPrincipalBalance": 40325.209353,
        "prepayPrincipalPayment": 620.824591,
        "scheduledPrincipalPayment": 4013.654573
    }
    {
        "date": "2053-05-25",
        "totalCashFlow": 4532.435582,
        "interestPayment": 14.871138,
        "principalBalance": 31173.165744,
        "principalPayment": 4517.564445,
        "endPrincipalBalance": 31173.165744,
        "beginPrincipalBalance": 35690.730189,
        "prepayPrincipalPayment": 568.422572,
        "scheduledPrincipalPayment": 3949.141873
    }
    {
        "date": "2053-06-25",
        "totalCashFlow": 4397.029228,
        "interestPayment": 12.988819,
        "principalBalance": 26789.125335,
        "principalPayment": 4384.040409,
        "endPrincipalBalance": 26789.125335,
        "beginPrincipalBalance": 31173.165744,
        "prepayPrincipalPayment": 501.579026,
        "scheduledPrincipalPayment": 3882.461383
    }
    {
        "date": "2053-07-25",
        "totalCashFlow": 4258.428515,
        "interestPayment": 11.162136,
        "principalBalance": 22541.858956,
        "principalPayment": 4247.266379,
        "endPrincipalBalance": 22541.858956,
        "beginPrincipalBalance": 26789.125335,
        "prepayPrincipalPayment": 432.191303,
        "scheduledPrincipalPayment": 3815.075076
    }
    {
        "date": "2053-08-25",
        "totalCashFlow": 4117.440881,
        "interestPayment": 9.392441,
        "principalBalance": 18433.810516,
        "principalPayment": 4108.04844,
        "endPrincipalBalance": 18433.810516,
        "beginPrincipalBalance": 22541.858956,
        "prepayPrincipalPayment": 360.843856,
        "scheduledPrincipalPayment": 3747.204584
    }
    {
        "date": "2053-09-25",
        "totalCashFlow": 3969.701659,
        "interestPayment": 7.680754,
        "principalBalance": 14471.789611,
        "principalPayment": 3962.020905,
        "endPrincipalBalance": 14471.789611,
        "beginPrincipalBalance": 18433.810516,
        "prepayPrincipalPayment": 282.93156,
        "scheduledPrincipalPayment": 3679.089345
    }
    {
        "date": "2053-10-25",
        "totalCashFlow": 3828.175546,
        "interestPayment": 6.029912,
        "principalBalance": 10649.643977,
        "principalPayment": 3822.145634,
        "endPrincipalBalance": 10649.643977,
        "beginPrincipalBalance": 14471.789611,
        "prepayPrincipalPayment": 209.84637,
        "scheduledPrincipalPayment": 3612.299264
    }
    {
        "date": "2053-11-25",
        "totalCashFlow": 3689.969408,
        "interestPayment": 4.437352,
        "principalBalance": 6964.111921,
        "principalPayment": 3685.532056,
        "endPrincipalBalance": 6964.111921,
        "beginPrincipalBalance": 10649.643977,
        "prepayPrincipalPayment": 139.345957,
        "scheduledPrincipalPayment": 3546.186099
    }
    {
        "date": "2053-12-25",
        "totalCashFlow": 3550.388377,
        "interestPayment": 2.901713,
        "principalBalance": 3416.625257,
        "principalPayment": 3547.486664,
        "endPrincipalBalance": 3416.625257,
        "beginPrincipalBalance": 6964.111921,
        "prepayPrincipalPayment": 67.24333,
        "scheduledPrincipalPayment": 3480.243334
    }
    {
        "date": "2054-01-25",
        "totalCashFlow": 3418.048851,
        "interestPayment": 1.423594,
        "principalBalance": 0.0,
        "principalPayment": 3416.625257,
        "endPrincipalBalance": 0.0,
        "beginPrincipalBalance": 3416.625257,
        "prepayPrincipalPayment": 0.0,
        "scheduledPrincipalPayment": 3416.625257
    }

    """

    try:
        logger.info("Calling post_cash_flow_sync")

        response = Client().yield_book_rest.post_cash_flow_sync(
            body=CashFlowRequestData(global_settings=global_settings, input=input, keywords=keywords),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
            content_type="application/json",
        )

        output = response
        logger.info("Called post_cash_flow_sync")

        return output
    except Exception as err:
        logger.error("Error post_cash_flow_sync.")
        check_exception_and_raise(err, logger)


def post_csv_bulk_results_sync(
    *,
    ids: List[str],
    default_settings: Optional[BulkDefaultSettings] = None,
    global_settings: Optional[BulkGlobalSettings] = None,
    fields: Optional[List[ColumnDetail]] = None,
    job: Optional[str] = None,
) -> str:
    """
    Retrieve bulk result using request id or request name in csv format.

    Parameters
    ----------
    default_settings : BulkDefaultSettings, optional

    global_settings : BulkGlobalSettings, optional

    fields : List[ColumnDetail], optional

    ids : List[str]
          Ids can be provided comma separated. Different formats for id are:
          1) RequestId R-number
          2) Request name R:name. In this case also provide jobid (J-number) or jobname (J:name)
          3) Jobid J-number
          4) Job name J:name - only 1 active job with the jobname
          5) Tag name T:name. In this case also provide jobid (J-number) or jobname (J:name)
    job : str, optional
        Job reference. This can be of the form J-number or job name.

    Returns
    --------
    str
        A sequence of textual characters.

    Examples
    --------


    """

    try:
        logger.info("Calling post_csv_bulk_results_sync")

        response = Client().yield_book_rest.post_csv_bulk_results_sync(
            body=BulkResultRequest(
                default_settings=default_settings,
                global_settings=global_settings,
                fields=fields,
            ),
            ids=ids,
            job=job,
            content_type="application/json",
        )

        output = response
        logger.info("Called post_csv_bulk_results_sync")

        return output
    except Exception as err:
        logger.error("Error post_csv_bulk_results_sync.")
        check_exception_and_raise(err, logger)


def post_json_bulk_request_sync(
    *,
    ids: List[str],
    default_settings: Optional[BulkDefaultSettings] = None,
    global_settings: Optional[BulkGlobalSettings] = None,
    fields: Optional[List[ColumnDetail]] = None,
    job: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve bulk json result using request id or request name.

    Parameters
    ----------
    default_settings : BulkDefaultSettings, optional

    global_settings : BulkGlobalSettings, optional

    fields : List[ColumnDetail], optional

    ids : List[str]
          Ids can be provided comma separated. Different formats for id are:
          1) RequestId R-number
          2) Request name R:name. In this case also provide jobid (J-number) or jobname (J:name)
          3) Jobid J-number
          4) Job name J:name - only 1 active job with the jobname
          5) Tag name T:name. In this case also provide jobid (J-number) or jobname (J:name)
    job : str, optional
        Job reference. This can be of the form J-number or job name.

    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling post_json_bulk_request_sync")

        response = Client().yield_book_rest.post_json_bulk_request_sync(
            body=BulkResultRequest(
                default_settings=default_settings,
                global_settings=global_settings,
                fields=fields,
            ),
            ids=ids,
            job=job,
            content_type="application/json",
        )

        output = response
        logger.info("Called post_json_bulk_request_sync")

        return output
    except Exception as err:
        logger.error("Error post_json_bulk_request_sync.")
        check_exception_and_raise(err, logger)


def post_market_setting_sync(
    *,
    input: Optional[List[MarketSettingsRequestInfo]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Post Bond market setting.

    Parameters
    ----------
    input : List[MarketSettingsRequestInfo], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling post_market_setting_sync")

        response = Client().yield_book_rest.post_market_setting_sync(
            body=MarketSettingsRequest(input=input),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called post_market_setting_sync")

        return output
    except Exception as err:
        logger.error("Error post_market_setting_sync.")
        check_exception_and_raise(err, logger)


def request_actual_vs_projected_async(
    *,
    global_settings: Optional[ActualVsProjectedGlobalSettings] = None,
    input: Optional[List[ActualVsProjectedRequestItem]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """


    Parameters
    ----------
    global_settings : ActualVsProjectedGlobalSettings, optional

    input : List[ActualVsProjectedRequestItem], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_actual_vs_projected_async")

        response = Client().yield_book_rest.request_actual_vs_projected_async(
            body=ActualVsProjectedRequest(global_settings=global_settings, input=input),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_actual_vs_projected_async")

        return output
    except Exception as err:
        logger.error("Error request_actual_vs_projected_async.")
        check_exception_and_raise(err, logger)


def request_actual_vs_projected_async_get(
    *,
    id: str,
    id_type: Optional[str] = None,
    prepay_type: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """


    Parameters
    ----------
    id : str
        Security reference ID.
    id_type : str, optional
        A sequence of textual characters.
    prepay_type : str, optional
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_actual_vs_projected_async_get")

        response = Client().yield_book_rest.request_actual_vs_projected_async_get(
            id=id,
            id_type=id_type,
            prepay_type=prepay_type,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_actual_vs_projected_async_get")

        return output
    except Exception as err:
        logger.error("Error request_actual_vs_projected_async_get.")
        check_exception_and_raise(err, logger)


def request_actual_vs_projected_sync(
    *,
    global_settings: Optional[ActualVsProjectedGlobalSettings] = None,
    input: Optional[List[ActualVsProjectedRequestItem]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """


    Parameters
    ----------
    global_settings : ActualVsProjectedGlobalSettings, optional

    input : List[ActualVsProjectedRequestItem], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_actual_vs_projected_sync")

        response = Client().yield_book_rest.request_actual_vs_projected_sync(
            body=ActualVsProjectedRequest(global_settings=global_settings, input=input),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_actual_vs_projected_sync")

        return output
    except Exception as err:
        logger.error("Error request_actual_vs_projected_sync.")
        check_exception_and_raise(err, logger)


def request_actual_vs_projected_sync_get(
    *,
    id: str,
    id_type: Optional[str] = None,
    prepay_type: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """


    Parameters
    ----------
    id : str
        Security reference ID.
    id_type : str, optional
        A sequence of textual characters.
    prepay_type : str, optional
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_actual_vs_projected_sync_get")

        response = Client().yield_book_rest.request_actual_vs_projected_sync_get(
            id=id,
            id_type=id_type,
            prepay_type=prepay_type,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_actual_vs_projected_sync_get")

        return output
    except Exception as err:
        logger.error("Error request_actual_vs_projected_sync_get.")
        check_exception_and_raise(err, logger)


def request_bond_indic_async(
    *,
    input: Optional[List[IdentifierInfo]] = None,
    keywords: Optional[List[str]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Asynchronous Post method to retrieve the contractual information about the reference data of instruments, which will typically not need any further calculations. Retrieve a request ID by which, using subsequent API 'getResult' endpoint, instrument reference data can be obtained given a BondIndicRequest - 'Input' - parameter that includes the information of which security or list of securities to be queried by CUSIP, ISIN, or other identifier type to obtain basic contractual information such as security type, sector,  maturity, credit ratings, coupon, and specific information based on security type like current pool factor if the requested identifier is a mortgage. Recommended and preferred method for high-volume instrument queries (single requsts broken to recommended 100 items, up to 250 max).

    Parameters
    ----------
    input : List[IdentifierInfo], optional
        Single identifier or a list of identifiers to search instruments by.
    keywords : List[str], optional
        List of keywords from the MappedResponseRefData to be exposed in the result data set.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------
    >>> # Request bond indic with async post
    >>> response = request_bond_indic_async(input=[IdentifierInfo(identifier="999818YT")])
    >>>
    >>> # Get results by request_id
    >>> results_response = get_result(request_id_parameter=response.request_id)
    >>>
    >>> # Print results in json format
    >>> print(js.dumps(results_response, indent=4))
    {
        "meta": {
            "status": "DONE",
            "requestId": "R-20896",
            "timeStamp": "2025-08-18T22:30:54Z",
            "responseType": "BOND_INDIC",
            "resultsStatus": "ALL"
        },
        "results": [
            {
                "cusip": "999818YT8",
                "indic": {
                    "ltv": 90.0,
                    "wam": 196,
                    "figi": "BBG0033WXBV4",
                    "cusip": "999818YT8",
                    "moody": [
                        {
                            "value": "Aaa"
                        }
                    ],
                    "source": "CITI",
                    "ticker": "GNMA",
                    "country": "US",
                    "loanAge": 147,
                    "lockout": 0,
                    "putFlag": false,
                    "callFlag": false,
                    "cobsCode": "MTGE",
                    "country2": "US",
                    "country3": "USA",
                    "currency": "USD",
                    "dayCount": "30/360 eom",
                    "glicCode": "MBS",
                    "grossWAC": 4.0,
                    "ioPeriod": 0,
                    "poolCode": "NA",
                    "sinkFlag": false,
                    "cmaTicker": "N/A",
                    "datedDate": "2013-05-01",
                    "gnma2Flag": false,
                    "percentVA": 11.04,
                    "currentLTV": 27.5,
                    "extendFlag": "N",
                    "isoCountry": "US",
                    "marketType": "DOMC",
                    "percentDTI": 34.0,
                    "percentFHA": 80.91,
                    "percentInv": 0.0,
                    "percentPIH": 0.14,
                    "percentRHS": 7.9,
                    "securityID": "999818YT",
                    "serviceFee": 0.5,
                    "vPointType": "MPGNMA",
                    "adjustedLTV": 27.5,
                    "combinedLTV": 90.7,
                    "creditScore": 692,
                    "description": "30-YR GNMA-2013 PROD",
                    "esgBondFlag": false,
                    "indexRating": "AA+",
                    "issueAmount": 8597.24,
                    "lowerRating": "AA+",
                    "paymentFreq": 12,
                    "percentHARP": 0.0,
                    "percentRefi": 63.7,
                    "tierCapital": "NA",
                    "balloonMonth": 0,
                    "deliveryFlag": "N",
                    "indexCountry": "US",
                    "industryCode": "MT",
                    "issuerTicker": "GNMA",
                    "lowestRating": "AA+",
                    "maturityDate": "2041-12-01",
                    "middleRating": "AA+",
                    "modifiedDate": "2025-08-13",
                    "originalTerm": 360,
                    "parentTicker": "GNMA",
                    "percentHARP2": 0.0,
                    "percentJumbo": 0.0,
                    "securityType": "MORT",
                    "currentCoupon": 3.5,
                    "dataStateList": [
                        {
                            "state": "PR",
                            "percent": 17.13
                        },
                        {
                            "state": "TX",
                            "percent": 10.03
                        },
                        {
                            "state": "FL",
                            "percent": 5.66
                        },
                        {
                            "state": "CA",
                            "percent": 4.95
                        },
                        {
                            "state": "OH",
                            "percent": 4.77
                        },
                        {
                            "state": "NY",
                            "percent": 4.76
                        },
                        {
                            "state": "GA",
                            "percent": 4.41
                        },
                        {
                            "state": "PA",
                            "percent": 3.38
                        },
                        {
                            "state": "MI",
                            "percent": 3.08
                        },
                        {
                            "state": "NC",
                            "percent": 2.73
                        },
                        {
                            "state": "IL",
                            "percent": 2.68
                        },
                        {
                            "state": "VA",
                            "percent": 2.68
                        },
                        {
                            "state": "NJ",
                            "percent": 2.4
                        },
                        {
                            "state": "IN",
                            "percent": 2.37
                        },
                        {
                            "state": "MD",
                            "percent": 2.23
                        },
                        {
                            "state": "MO",
                            "percent": 2.11
                        },
                        {
                            "state": "AZ",
                            "percent": 1.72
                        },
                        {
                            "state": "TN",
                            "percent": 1.66
                        },
                        {
                            "state": "WA",
                            "percent": 1.49
                        },
                        {
                            "state": "AL",
                            "percent": 1.48
                        },
                        {
                            "state": "OK",
                            "percent": 1.23
                        },
                        {
                            "state": "LA",
                            "percent": 1.22
                        },
                        {
                            "state": "MN",
                            "percent": 1.18
                        },
                        {
                            "state": "SC",
                            "percent": 1.11
                        },
                        {
                            "state": "CT",
                            "percent": 1.08
                        },
                        {
                            "state": "CO",
                            "percent": 1.04
                        },
                        {
                            "state": "KY",
                            "percent": 1.04
                        },
                        {
                            "state": "WI",
                            "percent": 1.0
                        },
                        {
                            "state": "MS",
                            "percent": 0.96
                        },
                        {
                            "state": "NM",
                            "percent": 0.95
                        },
                        {
                            "state": "OR",
                            "percent": 0.89
                        },
                        {
                            "state": "AR",
                            "percent": 0.75
                        },
                        {
                            "state": "NV",
                            "percent": 0.7
                        },
                        {
                            "state": "MA",
                            "percent": 0.67
                        },
                        {
                            "state": "IA",
                            "percent": 0.61
                        },
                        {
                            "state": "UT",
                            "percent": 0.59
                        },
                        {
                            "state": "KS",
                            "percent": 0.58
                        },
                        {
                            "state": "DE",
                            "percent": 0.45
                        },
                        {
                            "state": "ID",
                            "percent": 0.4
                        },
                        {
                            "state": "NE",
                            "percent": 0.38
                        },
                        {
                            "state": "WV",
                            "percent": 0.27
                        },
                        {
                            "state": "ME",
                            "percent": 0.19
                        },
                        {
                            "state": "NH",
                            "percent": 0.16
                        },
                        {
                            "state": "HI",
                            "percent": 0.15
                        },
                        {
                            "state": "MT",
                            "percent": 0.13
                        },
                        {
                            "state": "AK",
                            "percent": 0.12
                        },
                        {
                            "state": "RI",
                            "percent": 0.12
                        },
                        {
                            "state": "WY",
                            "percent": 0.08
                        },
                        {
                            "state": "SD",
                            "percent": 0.07
                        },
                        {
                            "state": "VT",
                            "percent": 0.06
                        },
                        {
                            "state": "DC",
                            "percent": 0.04
                        },
                        {
                            "state": "ND",
                            "percent": 0.04
                        }
                    ],
                    "delinquencies": {
                        "del30Days": {
                            "percent": 3.14
                        },
                        "del60Days": {
                            "percent": 0.57
                        },
                        "del90Days": {
                            "percent": 0.21
                        },
                        "del90PlusDays": {
                            "percent": 0.59
                        },
                        "del120PlusDays": {
                            "percent": 0.38
                        }
                    },
                    "greenBondFlag": false,
                    "highestRating": "AAA",
                    "incomeCountry": "US",
                    "issuerCountry": "US",
                    "percentSecond": 0.0,
                    "poolAgeMethod": "Calculated",
                    "prepayEffDate": "2025-05-01",
                    "seniorityType": "NA",
                    "assetClassCode": "CO",
                    "cgmiSectorCode": "MTGE",
                    "cleanPayMonths": 0,
                    "collateralType": "GNMA",
                    "fullPledgeFlag": false,
                    "gpmPercentStep": 0.0,
                    "incomeCountry3": "USA",
                    "instrumentType": "NA",
                    "issuerCountry2": "US",
                    "issuerCountry3": "USA",
                    "lowestRatingNF": "AA+",
                    "poolIssuerName": "NA",
                    "vPointCategory": "RP",
                    "amortizedFHALTV": 63.0,
                    "bloombergTicker": "GNSF 3.5 2013",
                    "industrySubCode": "MT",
                    "originationDate": "2013-05-01",
                    "originationYear": 2013,
                    "percent2To4Unit": 2.7,
                    "percentHAMPMods": 0.9,
                    "percentPurchase": 31.8,
                    "percentStateHFA": 0.4,
                    "poolOriginalWAM": 0,
                    "preliminaryFlag": false,
                    "redemptionValue": 100.0,
                    "securitySubType": "MPGNMA",
                    "dataQuartileList": [
                        {
                            "ltvlow": 17.0,
                            "ltvhigh": 87.0,
                            "loanSizeLow": 22000.0,
                            "loanSizeHigh": 101000.0,
                            "percentDTILow": 10.0,
                            "creditScoreLow": 300.0,
                            "percentDTIHigh": 24.5,
                            "creditScoreHigh": 655.0,
                            "originalLoanAgeLow": 0,
                            "originationYearLow": 20101101,
                            "originalLoanAgeHigh": 0,
                            "originationYearHigh": 20130401
                        },
                        {
                            "ltvlow": 87.0,
                            "ltvhigh": 93.0,
                            "loanSizeLow": 101000.0,
                            "loanSizeHigh": 132000.0,
                            "percentDTILow": 24.5,
                            "creditScoreLow": 655.0,
                            "percentDTIHigh": 34.7,
                            "creditScoreHigh": 691.0,
                            "originalLoanAgeLow": 0,
                            "originationYearLow": 20130401,
                            "originalLoanAgeHigh": 0,
                            "originationYearHigh": 20130501
                        },
                        {
                            "ltvlow": 93.0,
                            "ltvhigh": 97.0,
                            "loanSizeLow": 132000.0,
                            "loanSizeHigh": 183000.0,
                            "percentDTILow": 34.7,
                            "creditScoreLow": 691.0,
                            "percentDTIHigh": 43.6,
                            "creditScoreHigh": 739.0,
                            "originalLoanAgeLow": 0,
                            "originationYearLow": 20130501,
                            "originalLoanAgeHigh": 1,
                            "originationYearHigh": 20130701
                        },
                        {
                            "ltvlow": 97.0,
                            "ltvhigh": 118.0,
                            "loanSizeLow": 183000.0,
                            "loanSizeHigh": 743000.0,
                            "percentDTILow": 43.6,
                            "creditScoreLow": 739.0,
                            "percentDTIHigh": 65.0,
                            "creditScoreHigh": 832.0,
                            "originalLoanAgeLow": 1,
                            "originationYearLow": 20130701,
                            "originalLoanAgeHigh": 43,
                            "originationYearHigh": 20141101
                        }
                    ],
                    "gpmNumberOfSteps": 0,
                    "percentHARPOwner": 0.0,
                    "percentPrincipal": 100.0,
                    "securityCalcType": "GNMA",
                    "assetClassSubCode": "MBS",
                    "forbearanceAmount": 0.0,
                    "modifiedTimeStamp": "2025-08-13T19:37:00Z",
                    "outstandingAmount": 1079.93,
                    "parentDescription": "NA",
                    "poolIsBalloonFlag": false,
                    "prepaymentOptions": {
                        "prepayType": [
                            "CPR",
                            "PSA",
                            "VEC"
                        ]
                    },
                    "reperformerMonths": 1,
                    "dataPPMHistoryList": [
                        {
                            "prepayType": "PSA",
                            "dataPPMHistoryDetailList": [
                                {
                                    "month": "1",
                                    "prepayRate": 104.2558
                                },
                                {
                                    "month": "3",
                                    "prepayRate": 101.9675
                                },
                                {
                                    "month": "6",
                                    "prepayRate": 101.3512
                                },
                                {
                                    "month": "12",
                                    "prepayRate": 101.4048
                                },
                                {
                                    "month": "24",
                                    "prepayRate": 0.0
                                }
                            ]
                        },
                        {
                            "prepayType": "CPR",
                            "dataPPMHistoryDetailList": [
                                {
                                    "month": "1",
                                    "prepayRate": 6.2554
                                },
                                {
                                    "month": "3",
                                    "prepayRate": 6.118
                                },
                                {
                                    "month": "6",
                                    "prepayRate": 6.0811
                                },
                                {
                                    "month": "12",
                                    "prepayRate": 6.0843
                                },
                                {
                                    "month": "24",
                                    "prepayRate": 0.0
                                }
                            ]
                        }
                    ],
                    "daysToFirstPayment": 44,
                    "issuerLowestRating": "NA",
                    "issuerMiddleRating": "NA",
                    "newCurrentLoanSize": 101863.0,
                    "originationChannel": {
                        "broker": 4.65,
                        "retail": 61.97,
                        "unknown": 0.0,
                        "unspecified": 0.0,
                        "correspondence": 33.37
                    },
                    "percentMultiFamily": 2.7,
                    "percentRefiCashout": 5.8,
                    "percentRegularMods": 3.6,
                    "percentReperformer": 0.5,
                    "relocationLoanFlag": false,
                    "socialDensityScore": 0.0,
                    "umbsfhlgPercentage": 0.0,
                    "umbsfnmaPercentage": 0.0,
                    "industryDescription": "Mortgage",
                    "issuerHighestRating": "NA",
                    "newOriginalLoanSize": 182051.0,
                    "socialCriteriaShare": 0.0,
                    "spreadAtOrigination": 22.3,
                    "weightedAvgLoanSize": 101863.0,
                    "poolOriginalLoanSize": 182051.0,
                    "cgmiSectorDescription": "Mortgage",
                    "cleanPayAverageMonths": 0,
                    "expModelAvailableFlag": true,
                    "fhfaImpliedCurrentLTV": 27.5,
                    "percentRefiNonCashout": 57.9,
                    "prepayPenaltySchedule": "0.000",
                    "defaultHorizonPYMethod": "OAS Change",
                    "industrySubDescription": "Mortgage Asset Backed",
                    "actualPrepayHistoryList": {
                        "date": "2025-10-01",
                        "genericValue": 0.9575
                    },
                    "adjustedCurrentLoanSize": 101863.0,
                    "forbearanceModification": 0.0,
                    "percentTwoPlusBorrowers": 44.0,
                    "poolAvgOriginalLoanTerm": 0,
                    "adjustedOriginalLoanSize": 182040.0,
                    "assetClassSubDescription": "Collateralized Asset Backed - Mortgage",
                    "mortgageInsurancePremium": {
                        "annual": {
                            "va": 0.0,
                            "fha": 0.797,
                            "pih": 0.0,
                            "rhs": 0.399
                        },
                        "upfront": {
                            "va": 0.5,
                            "fha": 0.693,
                            "pih": 1.0,
                            "rhs": 1.996
                        }
                    },
                    "percentReperformerAndMod": 0.1,
                    "reperformerMonthsForMods": 2,
                    "originalLoanSizeRemaining": 150891.0,
                    "percentFirstTimeHomeBuyer": 20.8,
                    "current3rdPartyOrigination": 38.02,
                    "adjustedSpreadAtOrigination": 22.3,
                    "dataPrepayModelServicerList": [
                        {
                            "percent": 23.84,
                            "servicer": "FREE"
                        },
                        {
                            "percent": 11.4,
                            "servicer": "NSTAR"
                        },
                        {
                            "percent": 11.39,
                            "servicer": "WELLS"
                        },
                        {
                            "percent": 11.15,
                            "servicer": "BCPOP"
                        },
                        {
                            "percent": 7.23,
                            "servicer": "QUICK"
                        },
                        {
                            "percent": 7.13,
                            "servicer": "PENNY"
                        },
                        {
                            "percent": 6.51,
                            "servicer": "LAKEV"
                        },
                        {
                            "percent": 6.34,
                            "servicer": "CARRG"
                        },
                        {
                            "percent": 5.5,
                            "servicer": "USB"
                        },
                        {
                            "percent": 2.41,
                            "servicer": "PNC"
                        },
                        {
                            "percent": 1.34,
                            "servicer": "MNTBK"
                        },
                        {
                            "percent": 1.17,
                            "servicer": "NWRES"
                        },
                        {
                            "percent": 0.95,
                            "servicer": "FIFTH"
                        },
                        {
                            "percent": 0.75,
                            "servicer": "DEPOT"
                        },
                        {
                            "percent": 0.6,
                            "servicer": "BOKF"
                        },
                        {
                            "percent": 0.51,
                            "servicer": "JPM"
                        },
                        {
                            "percent": 0.48,
                            "servicer": "TRUIS"
                        },
                        {
                            "percent": 0.42,
                            "servicer": "CITI"
                        },
                        {
                            "percent": 0.38,
                            "servicer": "GUILD"
                        },
                        {
                            "percent": 0.21,
                            "servicer": "REGNS"
                        },
                        {
                            "percent": 0.2,
                            "servicer": "CNTRL"
                        },
                        {
                            "percent": 0.09,
                            "servicer": "COLNL"
                        },
                        {
                            "percent": 0.06,
                            "servicer": "HFAGY"
                        },
                        {
                            "percent": 0.06,
                            "servicer": "MNSRC"
                        },
                        {
                            "percent": 0.03,
                            "servicer": "HOMBR"
                        }
                    ],
                    "nonWeightedOriginalLoanSize": 0.0,
                    "original3rdPartyOrigination": 0.0,
                    "percentHARPDec2010Extension": 0.0,
                    "percentHARPOneYearExtension": 0.0,
                    "percentDownPaymentAssistance": 5.6,
                    "percentAmortizedFHALTVUnder78": 95.4,
                    "loanPerformanceImpliedCurrentLTV": 44.8,
                    "reperformerMonthsForReperformers": 28
                },
                "ticker": "GNMA",
                "country": "US",
                "currency": "USD",
                "identifier": "999818YT",
                "description": "30-YR GNMA-2013 PROD",
                "issuerTicker": "GNMA",
                "maturityDate": "2041-12-01",
                "securityType": "MORT",
                "currentCoupon": 3.5,
                "securitySubType": "MPGNMA"
            }
        ]
    }


    >>> # Request bond indic with async post
    >>> response = request_bond_indic_async(input=[IdentifierInfo(identifier="999818YT",
    >>>                                                          id_type="CUSIP",
    >>>                                                          )])
    >>>
    >>> # Get results by request_id
    >>> results_response = get_result(request_id_parameter=response.request_id)
    >>>
    >>> # Print results in json format
    >>> print(js.dumps(results_response, indent=4))
    {
        "meta": {
            "status": "DONE",
            "requestId": "R-20897",
            "timeStamp": "2025-08-18T22:30:58Z",
            "responseType": "BOND_INDIC",
            "resultsStatus": "ALL"
        },
        "results": [
            {
                "cusip": "999818YT8",
                "indic": {
                    "ltv": 90.0,
                    "wam": 196,
                    "figi": "BBG0033WXBV4",
                    "cusip": "999818YT8",
                    "moody": [
                        {
                            "value": "Aaa"
                        }
                    ],
                    "source": "CITI",
                    "ticker": "GNMA",
                    "country": "US",
                    "loanAge": 147,
                    "lockout": 0,
                    "putFlag": false,
                    "callFlag": false,
                    "cobsCode": "MTGE",
                    "country2": "US",
                    "country3": "USA",
                    "currency": "USD",
                    "dayCount": "30/360 eom",
                    "glicCode": "MBS",
                    "grossWAC": 4.0,
                    "ioPeriod": 0,
                    "poolCode": "NA",
                    "sinkFlag": false,
                    "cmaTicker": "N/A",
                    "datedDate": "2013-05-01",
                    "gnma2Flag": false,
                    "percentVA": 11.04,
                    "currentLTV": 27.5,
                    "extendFlag": "N",
                    "isoCountry": "US",
                    "marketType": "DOMC",
                    "percentDTI": 34.0,
                    "percentFHA": 80.91,
                    "percentInv": 0.0,
                    "percentPIH": 0.14,
                    "percentRHS": 7.9,
                    "securityID": "999818YT",
                    "serviceFee": 0.5,
                    "vPointType": "MPGNMA",
                    "adjustedLTV": 27.5,
                    "combinedLTV": 90.7,
                    "creditScore": 692,
                    "description": "30-YR GNMA-2013 PROD",
                    "esgBondFlag": false,
                    "indexRating": "AA+",
                    "issueAmount": 8597.24,
                    "lowerRating": "AA+",
                    "paymentFreq": 12,
                    "percentHARP": 0.0,
                    "percentRefi": 63.7,
                    "tierCapital": "NA",
                    "balloonMonth": 0,
                    "deliveryFlag": "N",
                    "indexCountry": "US",
                    "industryCode": "MT",
                    "issuerTicker": "GNMA",
                    "lowestRating": "AA+",
                    "maturityDate": "2041-12-01",
                    "middleRating": "AA+",
                    "modifiedDate": "2025-08-13",
                    "originalTerm": 360,
                    "parentTicker": "GNMA",
                    "percentHARP2": 0.0,
                    "percentJumbo": 0.0,
                    "securityType": "MORT",
                    "currentCoupon": 3.5,
                    "dataStateList": [
                        {
                            "state": "PR",
                            "percent": 17.13
                        },
                        {
                            "state": "TX",
                            "percent": 10.03
                        },
                        {
                            "state": "FL",
                            "percent": 5.66
                        },
                        {
                            "state": "CA",
                            "percent": 4.95
                        },
                        {
                            "state": "OH",
                            "percent": 4.77
                        },
                        {
                            "state": "NY",
                            "percent": 4.76
                        },
                        {
                            "state": "GA",
                            "percent": 4.41
                        },
                        {
                            "state": "PA",
                            "percent": 3.38
                        },
                        {
                            "state": "MI",
                            "percent": 3.08
                        },
                        {
                            "state": "NC",
                            "percent": 2.73
                        },
                        {
                            "state": "IL",
                            "percent": 2.68
                        },
                        {
                            "state": "VA",
                            "percent": 2.68
                        },
                        {
                            "state": "NJ",
                            "percent": 2.4
                        },
                        {
                            "state": "IN",
                            "percent": 2.37
                        },
                        {
                            "state": "MD",
                            "percent": 2.23
                        },
                        {
                            "state": "MO",
                            "percent": 2.11
                        },
                        {
                            "state": "AZ",
                            "percent": 1.72
                        },
                        {
                            "state": "TN",
                            "percent": 1.66
                        },
                        {
                            "state": "WA",
                            "percent": 1.49
                        },
                        {
                            "state": "AL",
                            "percent": 1.48
                        },
                        {
                            "state": "OK",
                            "percent": 1.23
                        },
                        {
                            "state": "LA",
                            "percent": 1.22
                        },
                        {
                            "state": "MN",
                            "percent": 1.18
                        },
                        {
                            "state": "SC",
                            "percent": 1.11
                        },
                        {
                            "state": "CT",
                            "percent": 1.08
                        },
                        {
                            "state": "CO",
                            "percent": 1.04
                        },
                        {
                            "state": "KY",
                            "percent": 1.04
                        },
                        {
                            "state": "WI",
                            "percent": 1.0
                        },
                        {
                            "state": "MS",
                            "percent": 0.96
                        },
                        {
                            "state": "NM",
                            "percent": 0.95
                        },
                        {
                            "state": "OR",
                            "percent": 0.89
                        },
                        {
                            "state": "AR",
                            "percent": 0.75
                        },
                        {
                            "state": "NV",
                            "percent": 0.7
                        },
                        {
                            "state": "MA",
                            "percent": 0.67
                        },
                        {
                            "state": "IA",
                            "percent": 0.61
                        },
                        {
                            "state": "UT",
                            "percent": 0.59
                        },
                        {
                            "state": "KS",
                            "percent": 0.58
                        },
                        {
                            "state": "DE",
                            "percent": 0.45
                        },
                        {
                            "state": "ID",
                            "percent": 0.4
                        },
                        {
                            "state": "NE",
                            "percent": 0.38
                        },
                        {
                            "state": "WV",
                            "percent": 0.27
                        },
                        {
                            "state": "ME",
                            "percent": 0.19
                        },
                        {
                            "state": "NH",
                            "percent": 0.16
                        },
                        {
                            "state": "HI",
                            "percent": 0.15
                        },
                        {
                            "state": "MT",
                            "percent": 0.13
                        },
                        {
                            "state": "AK",
                            "percent": 0.12
                        },
                        {
                            "state": "RI",
                            "percent": 0.12
                        },
                        {
                            "state": "WY",
                            "percent": 0.08
                        },
                        {
                            "state": "SD",
                            "percent": 0.07
                        },
                        {
                            "state": "VT",
                            "percent": 0.06
                        },
                        {
                            "state": "DC",
                            "percent": 0.04
                        },
                        {
                            "state": "ND",
                            "percent": 0.04
                        }
                    ],
                    "delinquencies": {
                        "del30Days": {
                            "percent": 3.14
                        },
                        "del60Days": {
                            "percent": 0.57
                        },
                        "del90Days": {
                            "percent": 0.21
                        },
                        "del90PlusDays": {
                            "percent": 0.59
                        },
                        "del120PlusDays": {
                            "percent": 0.38
                        }
                    },
                    "greenBondFlag": false,
                    "highestRating": "AAA",
                    "incomeCountry": "US",
                    "issuerCountry": "US",
                    "percentSecond": 0.0,
                    "poolAgeMethod": "Calculated",
                    "prepayEffDate": "2025-05-01",
                    "seniorityType": "NA",
                    "assetClassCode": "CO",
                    "cgmiSectorCode": "MTGE",
                    "cleanPayMonths": 0,
                    "collateralType": "GNMA",
                    "fullPledgeFlag": false,
                    "gpmPercentStep": 0.0,
                    "incomeCountry3": "USA",
                    "instrumentType": "NA",
                    "issuerCountry2": "US",
                    "issuerCountry3": "USA",
                    "lowestRatingNF": "AA+",
                    "poolIssuerName": "NA",
                    "vPointCategory": "RP",
                    "amortizedFHALTV": 63.0,
                    "bloombergTicker": "GNSF 3.5 2013",
                    "industrySubCode": "MT",
                    "originationDate": "2013-05-01",
                    "originationYear": 2013,
                    "percent2To4Unit": 2.7,
                    "percentHAMPMods": 0.9,
                    "percentPurchase": 31.8,
                    "percentStateHFA": 0.4,
                    "poolOriginalWAM": 0,
                    "preliminaryFlag": false,
                    "redemptionValue": 100.0,
                    "securitySubType": "MPGNMA",
                    "dataQuartileList": [
                        {
                            "ltvlow": 17.0,
                            "ltvhigh": 87.0,
                            "loanSizeLow": 22000.0,
                            "loanSizeHigh": 101000.0,
                            "percentDTILow": 10.0,
                            "creditScoreLow": 300.0,
                            "percentDTIHigh": 24.5,
                            "creditScoreHigh": 655.0,
                            "originalLoanAgeLow": 0,
                            "originationYearLow": 20101101,
                            "originalLoanAgeHigh": 0,
                            "originationYearHigh": 20130401
                        },
                        {
                            "ltvlow": 87.0,
                            "ltvhigh": 93.0,
                            "loanSizeLow": 101000.0,
                            "loanSizeHigh": 132000.0,
                            "percentDTILow": 24.5,
                            "creditScoreLow": 655.0,
                            "percentDTIHigh": 34.7,
                            "creditScoreHigh": 691.0,
                            "originalLoanAgeLow": 0,
                            "originationYearLow": 20130401,
                            "originalLoanAgeHigh": 0,
                            "originationYearHigh": 20130501
                        },
                        {
                            "ltvlow": 93.0,
                            "ltvhigh": 97.0,
                            "loanSizeLow": 132000.0,
                            "loanSizeHigh": 183000.0,
                            "percentDTILow": 34.7,
                            "creditScoreLow": 691.0,
                            "percentDTIHigh": 43.6,
                            "creditScoreHigh": 739.0,
                            "originalLoanAgeLow": 0,
                            "originationYearLow": 20130501,
                            "originalLoanAgeHigh": 1,
                            "originationYearHigh": 20130701
                        },
                        {
                            "ltvlow": 97.0,
                            "ltvhigh": 118.0,
                            "loanSizeLow": 183000.0,
                            "loanSizeHigh": 743000.0,
                            "percentDTILow": 43.6,
                            "creditScoreLow": 739.0,
                            "percentDTIHigh": 65.0,
                            "creditScoreHigh": 832.0,
                            "originalLoanAgeLow": 1,
                            "originationYearLow": 20130701,
                            "originalLoanAgeHigh": 43,
                            "originationYearHigh": 20141101
                        }
                    ],
                    "gpmNumberOfSteps": 0,
                    "percentHARPOwner": 0.0,
                    "percentPrincipal": 100.0,
                    "securityCalcType": "GNMA",
                    "assetClassSubCode": "MBS",
                    "forbearanceAmount": 0.0,
                    "modifiedTimeStamp": "2025-08-13T19:37:00Z",
                    "outstandingAmount": 1079.93,
                    "parentDescription": "NA",
                    "poolIsBalloonFlag": false,
                    "prepaymentOptions": {
                        "prepayType": [
                            "CPR",
                            "PSA",
                            "VEC"
                        ]
                    },
                    "reperformerMonths": 1,
                    "dataPPMHistoryList": [
                        {
                            "prepayType": "PSA",
                            "dataPPMHistoryDetailList": [
                                {
                                    "month": "1",
                                    "prepayRate": 104.2558
                                },
                                {
                                    "month": "3",
                                    "prepayRate": 101.9675
                                },
                                {
                                    "month": "6",
                                    "prepayRate": 101.3512
                                },
                                {
                                    "month": "12",
                                    "prepayRate": 101.4048
                                },
                                {
                                    "month": "24",
                                    "prepayRate": 0.0
                                }
                            ]
                        },
                        {
                            "prepayType": "CPR",
                            "dataPPMHistoryDetailList": [
                                {
                                    "month": "1",
                                    "prepayRate": 6.2554
                                },
                                {
                                    "month": "3",
                                    "prepayRate": 6.118
                                },
                                {
                                    "month": "6",
                                    "prepayRate": 6.0811
                                },
                                {
                                    "month": "12",
                                    "prepayRate": 6.0843
                                },
                                {
                                    "month": "24",
                                    "prepayRate": 0.0
                                }
                            ]
                        }
                    ],
                    "daysToFirstPayment": 44,
                    "issuerLowestRating": "NA",
                    "issuerMiddleRating": "NA",
                    "newCurrentLoanSize": 101863.0,
                    "originationChannel": {
                        "broker": 4.65,
                        "retail": 61.97,
                        "unknown": 0.0,
                        "unspecified": 0.0,
                        "correspondence": 33.37
                    },
                    "percentMultiFamily": 2.7,
                    "percentRefiCashout": 5.8,
                    "percentRegularMods": 3.6,
                    "percentReperformer": 0.5,
                    "relocationLoanFlag": false,
                    "socialDensityScore": 0.0,
                    "umbsfhlgPercentage": 0.0,
                    "umbsfnmaPercentage": 0.0,
                    "industryDescription": "Mortgage",
                    "issuerHighestRating": "NA",
                    "newOriginalLoanSize": 182051.0,
                    "socialCriteriaShare": 0.0,
                    "spreadAtOrigination": 22.3,
                    "weightedAvgLoanSize": 101863.0,
                    "poolOriginalLoanSize": 182051.0,
                    "cgmiSectorDescription": "Mortgage",
                    "cleanPayAverageMonths": 0,
                    "expModelAvailableFlag": true,
                    "fhfaImpliedCurrentLTV": 27.5,
                    "percentRefiNonCashout": 57.9,
                    "prepayPenaltySchedule": "0.000",
                    "defaultHorizonPYMethod": "OAS Change",
                    "industrySubDescription": "Mortgage Asset Backed",
                    "actualPrepayHistoryList": {
                        "date": "2025-10-01",
                        "genericValue": 0.9575
                    },
                    "adjustedCurrentLoanSize": 101863.0,
                    "forbearanceModification": 0.0,
                    "percentTwoPlusBorrowers": 44.0,
                    "poolAvgOriginalLoanTerm": 0,
                    "adjustedOriginalLoanSize": 182040.0,
                    "assetClassSubDescription": "Collateralized Asset Backed - Mortgage",
                    "mortgageInsurancePremium": {
                        "annual": {
                            "va": 0.0,
                            "fha": 0.797,
                            "pih": 0.0,
                            "rhs": 0.399
                        },
                        "upfront": {
                            "va": 0.5,
                            "fha": 0.693,
                            "pih": 1.0,
                            "rhs": 1.996
                        }
                    },
                    "percentReperformerAndMod": 0.1,
                    "reperformerMonthsForMods": 2,
                    "originalLoanSizeRemaining": 150891.0,
                    "percentFirstTimeHomeBuyer": 20.8,
                    "current3rdPartyOrigination": 38.02,
                    "adjustedSpreadAtOrigination": 22.3,
                    "dataPrepayModelServicerList": [
                        {
                            "percent": 23.84,
                            "servicer": "FREE"
                        },
                        {
                            "percent": 11.4,
                            "servicer": "NSTAR"
                        },
                        {
                            "percent": 11.39,
                            "servicer": "WELLS"
                        },
                        {
                            "percent": 11.15,
                            "servicer": "BCPOP"
                        },
                        {
                            "percent": 7.23,
                            "servicer": "QUICK"
                        },
                        {
                            "percent": 7.13,
                            "servicer": "PENNY"
                        },
                        {
                            "percent": 6.51,
                            "servicer": "LAKEV"
                        },
                        {
                            "percent": 6.34,
                            "servicer": "CARRG"
                        },
                        {
                            "percent": 5.5,
                            "servicer": "USB"
                        },
                        {
                            "percent": 2.41,
                            "servicer": "PNC"
                        },
                        {
                            "percent": 1.34,
                            "servicer": "MNTBK"
                        },
                        {
                            "percent": 1.17,
                            "servicer": "NWRES"
                        },
                        {
                            "percent": 0.95,
                            "servicer": "FIFTH"
                        },
                        {
                            "percent": 0.75,
                            "servicer": "DEPOT"
                        },
                        {
                            "percent": 0.6,
                            "servicer": "BOKF"
                        },
                        {
                            "percent": 0.51,
                            "servicer": "JPM"
                        },
                        {
                            "percent": 0.48,
                            "servicer": "TRUIS"
                        },
                        {
                            "percent": 0.42,
                            "servicer": "CITI"
                        },
                        {
                            "percent": 0.38,
                            "servicer": "GUILD"
                        },
                        {
                            "percent": 0.21,
                            "servicer": "REGNS"
                        },
                        {
                            "percent": 0.2,
                            "servicer": "CNTRL"
                        },
                        {
                            "percent": 0.09,
                            "servicer": "COLNL"
                        },
                        {
                            "percent": 0.06,
                            "servicer": "HFAGY"
                        },
                        {
                            "percent": 0.06,
                            "servicer": "MNSRC"
                        },
                        {
                            "percent": 0.03,
                            "servicer": "HOMBR"
                        }
                    ],
                    "nonWeightedOriginalLoanSize": 0.0,
                    "original3rdPartyOrigination": 0.0,
                    "percentHARPDec2010Extension": 0.0,
                    "percentHARPOneYearExtension": 0.0,
                    "percentDownPaymentAssistance": 5.6,
                    "percentAmortizedFHALTVUnder78": 95.4,
                    "loanPerformanceImpliedCurrentLTV": 44.8,
                    "reperformerMonthsForReperformers": 28
                },
                "ticker": "GNMA",
                "country": "US",
                "currency": "USD",
                "identifier": "999818YT",
                "description": "30-YR GNMA-2013 PROD",
                "issuerTicker": "GNMA",
                "maturityDate": "2041-12-01",
                "securityType": "MORT",
                "currentCoupon": 3.5,
                "securitySubType": "MPGNMA"
            }
        ]
    }

    """

    try:
        logger.info("Calling request_bond_indic_async")

        response = Client().yield_book_rest.request_bond_indic_async(
            body=BondIndicRequest(input=input, keywords=keywords),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_bond_indic_async")

        return output
    except Exception as err:
        logger.error("Error request_bond_indic_async.")
        check_exception_and_raise(err, logger)


def request_bond_indic_async_get(
    *,
    id: str,
    id_type: Optional[Union[str, IdTypeEnum]] = None,
    keywords: Optional[List[str]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Asynchronous Get method to retrieve the contractual information about the reference data of instruments, which will typically not need any further calculations. Retrieve a request ID by which, using subsequent API 'getResult' endpoint, instrument reference data can be obtained given a BondIndicRequest - 'Input' - parameter that includes the information of which security or list of securities to be queried by CUSIP, ISIN, or other identifier type to obtain basic contractual information such as security type, sector,  maturity, credit ratings, coupon, and specific information based on security type like current pool factor if the requested identifier is a mortgage.

    Parameters
    ----------
    id : str
        A sequence of textual characters.
    id_type : Union[str, IdTypeEnum], optional

    keywords : List[str], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------
    >>> # Request bond indic with async get
    >>> response = request_bond_indic_async_get(id="999818YT", id_type=IdTypeEnum.CUSIP)
    >>>
    >>> # Get results by request_id
    >>> results_response = get_result(request_id_parameter=response.request_id)
    >>>
    >>> # Due to async nature, code Will perform the fetch 10 times, as result is not always ready instantly, with 3 second lapse between attempts
    >>> attempt = 1
    >>>
    >>> if not results_response:
    >>>     while attempt < 10:
    >>>         print(f"Attempt " + str(attempt) + " resulted in error retrieving results from:" + response.request_id)
    >>>
    >>>         time.sleep(10)
    >>>
    >>>         results_response = get_result(request_id_parameter=response.request_id)
    >>>
    >>>         if not results_response:
    >>>             attempt += 1
    >>>         else:
    >>>             break
    >>>
    >>> # Print results in json format
    >>> print(js.dumps(results_response, indent=4))
    {
        "data": {
            "cusip": "999818YT8",
            "indic": {
                "ltv": 90.0,
                "wam": 196,
                "figi": "BBG0033WXBV4",
                "cusip": "999818YT8",
                "moody": [
                    {
                        "value": "Aaa"
                    }
                ],
                "source": "CITI",
                "ticker": "GNMA",
                "country": "US",
                "loanAge": 147,
                "lockout": 0,
                "putFlag": false,
                "callFlag": false,
                "cobsCode": "MTGE",
                "country2": "US",
                "country3": "USA",
                "currency": "USD",
                "dayCount": "30/360 eom",
                "glicCode": "MBS",
                "grossWAC": 4.0,
                "ioPeriod": 0,
                "poolCode": "NA",
                "sinkFlag": false,
                "cmaTicker": "N/A",
                "datedDate": "2013-05-01",
                "gnma2Flag": false,
                "percentVA": 11.04,
                "currentLTV": 27.5,
                "extendFlag": "N",
                "isoCountry": "US",
                "marketType": "DOMC",
                "percentDTI": 34.0,
                "percentFHA": 80.91,
                "percentInv": 0.0,
                "percentPIH": 0.14,
                "percentRHS": 7.9,
                "securityID": "999818YT",
                "serviceFee": 0.5,
                "vPointType": "MPGNMA",
                "adjustedLTV": 27.5,
                "combinedLTV": 90.7,
                "creditScore": 692,
                "description": "30-YR GNMA-2013 PROD",
                "esgBondFlag": false,
                "indexRating": "AA+",
                "issueAmount": 8597.24,
                "lowerRating": "AA+",
                "paymentFreq": 12,
                "percentHARP": 0.0,
                "percentRefi": 63.7,
                "tierCapital": "NA",
                "balloonMonth": 0,
                "deliveryFlag": "N",
                "indexCountry": "US",
                "industryCode": "MT",
                "issuerTicker": "GNMA",
                "lowestRating": "AA+",
                "maturityDate": "2041-12-01",
                "middleRating": "AA+",
                "modifiedDate": "2025-08-13",
                "originalTerm": 360,
                "parentTicker": "GNMA",
                "percentHARP2": 0.0,
                "percentJumbo": 0.0,
                "securityType": "MORT",
                "currentCoupon": 3.5,
                "dataStateList": [
                    {
                        "state": "PR",
                        "percent": 17.13
                    },
                    {
                        "state": "TX",
                        "percent": 10.03
                    },
                    {
                        "state": "FL",
                        "percent": 5.66
                    },
                    {
                        "state": "CA",
                        "percent": 4.95
                    },
                    {
                        "state": "OH",
                        "percent": 4.77
                    },
                    {
                        "state": "NY",
                        "percent": 4.76
                    },
                    {
                        "state": "GA",
                        "percent": 4.41
                    },
                    {
                        "state": "PA",
                        "percent": 3.38
                    },
                    {
                        "state": "MI",
                        "percent": 3.08
                    },
                    {
                        "state": "NC",
                        "percent": 2.73
                    },
                    {
                        "state": "IL",
                        "percent": 2.68
                    },
                    {
                        "state": "VA",
                        "percent": 2.68
                    },
                    {
                        "state": "NJ",
                        "percent": 2.4
                    },
                    {
                        "state": "IN",
                        "percent": 2.37
                    },
                    {
                        "state": "MD",
                        "percent": 2.23
                    },
                    {
                        "state": "MO",
                        "percent": 2.11
                    },
                    {
                        "state": "AZ",
                        "percent": 1.72
                    },
                    {
                        "state": "TN",
                        "percent": 1.66
                    },
                    {
                        "state": "WA",
                        "percent": 1.49
                    },
                    {
                        "state": "AL",
                        "percent": 1.48
                    },
                    {
                        "state": "OK",
                        "percent": 1.23
                    },
                    {
                        "state": "LA",
                        "percent": 1.22
                    },
                    {
                        "state": "MN",
                        "percent": 1.18
                    },
                    {
                        "state": "SC",
                        "percent": 1.11
                    },
                    {
                        "state": "CT",
                        "percent": 1.08
                    },
                    {
                        "state": "CO",
                        "percent": 1.04
                    },
                    {
                        "state": "KY",
                        "percent": 1.04
                    },
                    {
                        "state": "WI",
                        "percent": 1.0
                    },
                    {
                        "state": "MS",
                        "percent": 0.96
                    },
                    {
                        "state": "NM",
                        "percent": 0.95
                    },
                    {
                        "state": "OR",
                        "percent": 0.89
                    },
                    {
                        "state": "AR",
                        "percent": 0.75
                    },
                    {
                        "state": "NV",
                        "percent": 0.7
                    },
                    {
                        "state": "MA",
                        "percent": 0.67
                    },
                    {
                        "state": "IA",
                        "percent": 0.61
                    },
                    {
                        "state": "UT",
                        "percent": 0.59
                    },
                    {
                        "state": "KS",
                        "percent": 0.58
                    },
                    {
                        "state": "DE",
                        "percent": 0.45
                    },
                    {
                        "state": "ID",
                        "percent": 0.4
                    },
                    {
                        "state": "NE",
                        "percent": 0.38
                    },
                    {
                        "state": "WV",
                        "percent": 0.27
                    },
                    {
                        "state": "ME",
                        "percent": 0.19
                    },
                    {
                        "state": "NH",
                        "percent": 0.16
                    },
                    {
                        "state": "HI",
                        "percent": 0.15
                    },
                    {
                        "state": "MT",
                        "percent": 0.13
                    },
                    {
                        "state": "AK",
                        "percent": 0.12
                    },
                    {
                        "state": "RI",
                        "percent": 0.12
                    },
                    {
                        "state": "WY",
                        "percent": 0.08
                    },
                    {
                        "state": "SD",
                        "percent": 0.07
                    },
                    {
                        "state": "VT",
                        "percent": 0.06
                    },
                    {
                        "state": "DC",
                        "percent": 0.04
                    },
                    {
                        "state": "ND",
                        "percent": 0.04
                    }
                ],
                "delinquencies": {
                    "del30Days": {
                        "percent": 3.14
                    },
                    "del60Days": {
                        "percent": 0.57
                    },
                    "del90Days": {
                        "percent": 0.21
                    },
                    "del90PlusDays": {
                        "percent": 0.59
                    },
                    "del120PlusDays": {
                        "percent": 0.38
                    }
                },
                "greenBondFlag": false,
                "highestRating": "AAA",
                "incomeCountry": "US",
                "issuerCountry": "US",
                "percentSecond": 0.0,
                "poolAgeMethod": "Calculated",
                "prepayEffDate": "2025-05-01",
                "seniorityType": "NA",
                "assetClassCode": "CO",
                "cgmiSectorCode": "MTGE",
                "cleanPayMonths": 0,
                "collateralType": "GNMA",
                "fullPledgeFlag": false,
                "gpmPercentStep": 0.0,
                "incomeCountry3": "USA",
                "instrumentType": "NA",
                "issuerCountry2": "US",
                "issuerCountry3": "USA",
                "lowestRatingNF": "AA+",
                "poolIssuerName": "NA",
                "vPointCategory": "RP",
                "amortizedFHALTV": 63.0,
                "bloombergTicker": "GNSF 3.5 2013",
                "industrySubCode": "MT",
                "originationDate": "2013-05-01",
                "originationYear": 2013,
                "percent2To4Unit": 2.7,
                "percentHAMPMods": 0.9,
                "percentPurchase": 31.8,
                "percentStateHFA": 0.4,
                "poolOriginalWAM": 0,
                "preliminaryFlag": false,
                "redemptionValue": 100.0,
                "securitySubType": "MPGNMA",
                "dataQuartileList": [
                    {
                        "ltvlow": 17.0,
                        "ltvhigh": 87.0,
                        "loanSizeLow": 22000.0,
                        "loanSizeHigh": 101000.0,
                        "percentDTILow": 10.0,
                        "creditScoreLow": 300.0,
                        "percentDTIHigh": 24.5,
                        "creditScoreHigh": 655.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20101101,
                        "originalLoanAgeHigh": 0,
                        "originationYearHigh": 20130401
                    },
                    {
                        "ltvlow": 87.0,
                        "ltvhigh": 93.0,
                        "loanSizeLow": 101000.0,
                        "loanSizeHigh": 132000.0,
                        "percentDTILow": 24.5,
                        "creditScoreLow": 655.0,
                        "percentDTIHigh": 34.7,
                        "creditScoreHigh": 691.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20130401,
                        "originalLoanAgeHigh": 0,
                        "originationYearHigh": 20130501
                    },
                    {
                        "ltvlow": 93.0,
                        "ltvhigh": 97.0,
                        "loanSizeLow": 132000.0,
                        "loanSizeHigh": 183000.0,
                        "percentDTILow": 34.7,
                        "creditScoreLow": 691.0,
                        "percentDTIHigh": 43.6,
                        "creditScoreHigh": 739.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20130501,
                        "originalLoanAgeHigh": 1,
                        "originationYearHigh": 20130701
                    },
                    {
                        "ltvlow": 97.0,
                        "ltvhigh": 118.0,
                        "loanSizeLow": 183000.0,
                        "loanSizeHigh": 743000.0,
                        "percentDTILow": 43.6,
                        "creditScoreLow": 739.0,
                        "percentDTIHigh": 65.0,
                        "creditScoreHigh": 832.0,
                        "originalLoanAgeLow": 1,
                        "originationYearLow": 20130701,
                        "originalLoanAgeHigh": 43,
                        "originationYearHigh": 20141101
                    }
                ],
                "gpmNumberOfSteps": 0,
                "percentHARPOwner": 0.0,
                "percentPrincipal": 100.0,
                "securityCalcType": "GNMA",
                "assetClassSubCode": "MBS",
                "forbearanceAmount": 0.0,
                "modifiedTimeStamp": "2025-08-13T19:37:00Z",
                "outstandingAmount": 1079.93,
                "parentDescription": "NA",
                "poolIsBalloonFlag": false,
                "prepaymentOptions": {
                    "prepayType": [
                        "CPR",
                        "PSA",
                        "VEC"
                    ]
                },
                "reperformerMonths": 1,
                "dataPPMHistoryList": [
                    {
                        "prepayType": "PSA",
                        "dataPPMHistoryDetailList": [
                            {
                                "month": "1",
                                "prepayRate": 104.2558
                            },
                            {
                                "month": "3",
                                "prepayRate": 101.9675
                            },
                            {
                                "month": "6",
                                "prepayRate": 101.3512
                            },
                            {
                                "month": "12",
                                "prepayRate": 101.4048
                            },
                            {
                                "month": "24",
                                "prepayRate": 0.0
                            }
                        ]
                    },
                    {
                        "prepayType": "CPR",
                        "dataPPMHistoryDetailList": [
                            {
                                "month": "1",
                                "prepayRate": 6.2554
                            },
                            {
                                "month": "3",
                                "prepayRate": 6.118
                            },
                            {
                                "month": "6",
                                "prepayRate": 6.0811
                            },
                            {
                                "month": "12",
                                "prepayRate": 6.0843
                            },
                            {
                                "month": "24",
                                "prepayRate": 0.0
                            }
                        ]
                    }
                ],
                "daysToFirstPayment": 44,
                "issuerLowestRating": "NA",
                "issuerMiddleRating": "NA",
                "newCurrentLoanSize": 101863.0,
                "originationChannel": {
                    "broker": 4.65,
                    "retail": 61.97,
                    "unknown": 0.0,
                    "unspecified": 0.0,
                    "correspondence": 33.37
                },
                "percentMultiFamily": 2.7,
                "percentRefiCashout": 5.8,
                "percentRegularMods": 3.6,
                "percentReperformer": 0.5,
                "relocationLoanFlag": false,
                "socialDensityScore": 0.0,
                "umbsfhlgPercentage": 0.0,
                "umbsfnmaPercentage": 0.0,
                "industryDescription": "Mortgage",
                "issuerHighestRating": "NA",
                "newOriginalLoanSize": 182051.0,
                "socialCriteriaShare": 0.0,
                "spreadAtOrigination": 22.3,
                "weightedAvgLoanSize": 101863.0,
                "poolOriginalLoanSize": 182051.0,
                "cgmiSectorDescription": "Mortgage",
                "cleanPayAverageMonths": 0,
                "expModelAvailableFlag": true,
                "fhfaImpliedCurrentLTV": 27.5,
                "percentRefiNonCashout": 57.9,
                "prepayPenaltySchedule": "0.000",
                "defaultHorizonPYMethod": "OAS Change",
                "industrySubDescription": "Mortgage Asset Backed",
                "actualPrepayHistoryList": {
                    "date": "2025-10-01",
                    "genericValue": 0.9575
                },
                "adjustedCurrentLoanSize": 101863.0,
                "forbearanceModification": 0.0,
                "percentTwoPlusBorrowers": 44.0,
                "poolAvgOriginalLoanTerm": 0,
                "adjustedOriginalLoanSize": 182040.0,
                "assetClassSubDescription": "Collateralized Asset Backed - Mortgage",
                "mortgageInsurancePremium": {
                    "annual": {
                        "va": 0.0,
                        "fha": 0.797,
                        "pih": 0.0,
                        "rhs": 0.399
                    },
                    "upfront": {
                        "va": 0.5,
                        "fha": 0.693,
                        "pih": 1.0,
                        "rhs": 1.996
                    }
                },
                "percentReperformerAndMod": 0.1,
                "reperformerMonthsForMods": 2,
                "originalLoanSizeRemaining": 150891.0,
                "percentFirstTimeHomeBuyer": 20.8,
                "current3rdPartyOrigination": 38.02,
                "adjustedSpreadAtOrigination": 22.3,
                "dataPrepayModelServicerList": [
                    {
                        "percent": 23.84,
                        "servicer": "FREE"
                    },
                    {
                        "percent": 11.4,
                        "servicer": "NSTAR"
                    },
                    {
                        "percent": 11.39,
                        "servicer": "WELLS"
                    },
                    {
                        "percent": 11.15,
                        "servicer": "BCPOP"
                    },
                    {
                        "percent": 7.23,
                        "servicer": "QUICK"
                    },
                    {
                        "percent": 7.13,
                        "servicer": "PENNY"
                    },
                    {
                        "percent": 6.51,
                        "servicer": "LAKEV"
                    },
                    {
                        "percent": 6.34,
                        "servicer": "CARRG"
                    },
                    {
                        "percent": 5.5,
                        "servicer": "USB"
                    },
                    {
                        "percent": 2.41,
                        "servicer": "PNC"
                    },
                    {
                        "percent": 1.34,
                        "servicer": "MNTBK"
                    },
                    {
                        "percent": 1.17,
                        "servicer": "NWRES"
                    },
                    {
                        "percent": 0.95,
                        "servicer": "FIFTH"
                    },
                    {
                        "percent": 0.75,
                        "servicer": "DEPOT"
                    },
                    {
                        "percent": 0.6,
                        "servicer": "BOKF"
                    },
                    {
                        "percent": 0.51,
                        "servicer": "JPM"
                    },
                    {
                        "percent": 0.48,
                        "servicer": "TRUIS"
                    },
                    {
                        "percent": 0.42,
                        "servicer": "CITI"
                    },
                    {
                        "percent": 0.38,
                        "servicer": "GUILD"
                    },
                    {
                        "percent": 0.21,
                        "servicer": "REGNS"
                    },
                    {
                        "percent": 0.2,
                        "servicer": "CNTRL"
                    },
                    {
                        "percent": 0.09,
                        "servicer": "COLNL"
                    },
                    {
                        "percent": 0.06,
                        "servicer": "HFAGY"
                    },
                    {
                        "percent": 0.06,
                        "servicer": "MNSRC"
                    },
                    {
                        "percent": 0.03,
                        "servicer": "HOMBR"
                    }
                ],
                "nonWeightedOriginalLoanSize": 0.0,
                "original3rdPartyOrigination": 0.0,
                "percentHARPDec2010Extension": 0.0,
                "percentHARPOneYearExtension": 0.0,
                "percentDownPaymentAssistance": 5.6,
                "percentAmortizedFHALTVUnder78": 95.4,
                "loanPerformanceImpliedCurrentLTV": 44.8,
                "reperformerMonthsForReperformers": 28
            },
            "ticker": "GNMA",
            "country": "US",
            "currency": "USD",
            "identifier": "999818YT",
            "description": "30-YR GNMA-2013 PROD",
            "issuerTicker": "GNMA",
            "maturityDate": "2041-12-01",
            "securityType": "MORT",
            "currentCoupon": 3.5,
            "securitySubType": "MPGNMA"
        },
        "meta": {
            "status": "DONE",
            "requestId": "R-20894",
            "timeStamp": "2025-08-18T22:30:44Z",
            "responseType": "BOND_INDIC"
        }
    }


    >>> # Request bond indic with async get
    >>> response = request_bond_indic_async_get(
    >>>                                     id="999818YT",
    >>>                                     id_type=IdTypeEnum.CUSIP
    >>>                                     )
    >>>
    >>> # Get results by request_id
    >>> results_response = get_result(request_id_parameter=response.request_id)
    >>>
    >>> # Due to async nature, code Will perform the fetch 10 times, as result is not always ready instantly, with 3 second lapse between attempts
    >>> attempt = 1
    >>>
    >>> if not results_response:
    >>>     while attempt < 10:
    >>>         print(f"Attempt " + str(attempt) + " resulted in error retrieving results from:" + response.request_id)
    >>>
    >>>         time.sleep(10)
    >>>
    >>>         results_response = get_result(request_id_parameter=response.request_id)
    >>>
    >>>         if not results_response:
    >>>             attempt += 1
    >>>         else:
    >>>             break
    >>>
    >>> # Print results in json format
    >>> print(js.dumps(results_response, indent=4))
    {
        "data": {
            "cusip": "999818YT8",
            "indic": {
                "ltv": 90.0,
                "wam": 196,
                "figi": "BBG0033WXBV4",
                "cusip": "999818YT8",
                "moody": [
                    {
                        "value": "Aaa"
                    }
                ],
                "source": "CITI",
                "ticker": "GNMA",
                "country": "US",
                "loanAge": 147,
                "lockout": 0,
                "putFlag": false,
                "callFlag": false,
                "cobsCode": "MTGE",
                "country2": "US",
                "country3": "USA",
                "currency": "USD",
                "dayCount": "30/360 eom",
                "glicCode": "MBS",
                "grossWAC": 4.0,
                "ioPeriod": 0,
                "poolCode": "NA",
                "sinkFlag": false,
                "cmaTicker": "N/A",
                "datedDate": "2013-05-01",
                "gnma2Flag": false,
                "percentVA": 11.04,
                "currentLTV": 27.5,
                "extendFlag": "N",
                "isoCountry": "US",
                "marketType": "DOMC",
                "percentDTI": 34.0,
                "percentFHA": 80.91,
                "percentInv": 0.0,
                "percentPIH": 0.14,
                "percentRHS": 7.9,
                "securityID": "999818YT",
                "serviceFee": 0.5,
                "vPointType": "MPGNMA",
                "adjustedLTV": 27.5,
                "combinedLTV": 90.7,
                "creditScore": 692,
                "description": "30-YR GNMA-2013 PROD",
                "esgBondFlag": false,
                "indexRating": "AA+",
                "issueAmount": 8597.24,
                "lowerRating": "AA+",
                "paymentFreq": 12,
                "percentHARP": 0.0,
                "percentRefi": 63.7,
                "tierCapital": "NA",
                "balloonMonth": 0,
                "deliveryFlag": "N",
                "indexCountry": "US",
                "industryCode": "MT",
                "issuerTicker": "GNMA",
                "lowestRating": "AA+",
                "maturityDate": "2041-12-01",
                "middleRating": "AA+",
                "modifiedDate": "2025-08-13",
                "originalTerm": 360,
                "parentTicker": "GNMA",
                "percentHARP2": 0.0,
                "percentJumbo": 0.0,
                "securityType": "MORT",
                "currentCoupon": 3.5,
                "dataStateList": [
                    {
                        "state": "PR",
                        "percent": 17.13
                    },
                    {
                        "state": "TX",
                        "percent": 10.03
                    },
                    {
                        "state": "FL",
                        "percent": 5.66
                    },
                    {
                        "state": "CA",
                        "percent": 4.95
                    },
                    {
                        "state": "OH",
                        "percent": 4.77
                    },
                    {
                        "state": "NY",
                        "percent": 4.76
                    },
                    {
                        "state": "GA",
                        "percent": 4.41
                    },
                    {
                        "state": "PA",
                        "percent": 3.38
                    },
                    {
                        "state": "MI",
                        "percent": 3.08
                    },
                    {
                        "state": "NC",
                        "percent": 2.73
                    },
                    {
                        "state": "IL",
                        "percent": 2.68
                    },
                    {
                        "state": "VA",
                        "percent": 2.68
                    },
                    {
                        "state": "NJ",
                        "percent": 2.4
                    },
                    {
                        "state": "IN",
                        "percent": 2.37
                    },
                    {
                        "state": "MD",
                        "percent": 2.23
                    },
                    {
                        "state": "MO",
                        "percent": 2.11
                    },
                    {
                        "state": "AZ",
                        "percent": 1.72
                    },
                    {
                        "state": "TN",
                        "percent": 1.66
                    },
                    {
                        "state": "WA",
                        "percent": 1.49
                    },
                    {
                        "state": "AL",
                        "percent": 1.48
                    },
                    {
                        "state": "OK",
                        "percent": 1.23
                    },
                    {
                        "state": "LA",
                        "percent": 1.22
                    },
                    {
                        "state": "MN",
                        "percent": 1.18
                    },
                    {
                        "state": "SC",
                        "percent": 1.11
                    },
                    {
                        "state": "CT",
                        "percent": 1.08
                    },
                    {
                        "state": "CO",
                        "percent": 1.04
                    },
                    {
                        "state": "KY",
                        "percent": 1.04
                    },
                    {
                        "state": "WI",
                        "percent": 1.0
                    },
                    {
                        "state": "MS",
                        "percent": 0.96
                    },
                    {
                        "state": "NM",
                        "percent": 0.95
                    },
                    {
                        "state": "OR",
                        "percent": 0.89
                    },
                    {
                        "state": "AR",
                        "percent": 0.75
                    },
                    {
                        "state": "NV",
                        "percent": 0.7
                    },
                    {
                        "state": "MA",
                        "percent": 0.67
                    },
                    {
                        "state": "IA",
                        "percent": 0.61
                    },
                    {
                        "state": "UT",
                        "percent": 0.59
                    },
                    {
                        "state": "KS",
                        "percent": 0.58
                    },
                    {
                        "state": "DE",
                        "percent": 0.45
                    },
                    {
                        "state": "ID",
                        "percent": 0.4
                    },
                    {
                        "state": "NE",
                        "percent": 0.38
                    },
                    {
                        "state": "WV",
                        "percent": 0.27
                    },
                    {
                        "state": "ME",
                        "percent": 0.19
                    },
                    {
                        "state": "NH",
                        "percent": 0.16
                    },
                    {
                        "state": "HI",
                        "percent": 0.15
                    },
                    {
                        "state": "MT",
                        "percent": 0.13
                    },
                    {
                        "state": "AK",
                        "percent": 0.12
                    },
                    {
                        "state": "RI",
                        "percent": 0.12
                    },
                    {
                        "state": "WY",
                        "percent": 0.08
                    },
                    {
                        "state": "SD",
                        "percent": 0.07
                    },
                    {
                        "state": "VT",
                        "percent": 0.06
                    },
                    {
                        "state": "DC",
                        "percent": 0.04
                    },
                    {
                        "state": "ND",
                        "percent": 0.04
                    }
                ],
                "delinquencies": {
                    "del30Days": {
                        "percent": 3.14
                    },
                    "del60Days": {
                        "percent": 0.57
                    },
                    "del90Days": {
                        "percent": 0.21
                    },
                    "del90PlusDays": {
                        "percent": 0.59
                    },
                    "del120PlusDays": {
                        "percent": 0.38
                    }
                },
                "greenBondFlag": false,
                "highestRating": "AAA",
                "incomeCountry": "US",
                "issuerCountry": "US",
                "percentSecond": 0.0,
                "poolAgeMethod": "Calculated",
                "prepayEffDate": "2025-05-01",
                "seniorityType": "NA",
                "assetClassCode": "CO",
                "cgmiSectorCode": "MTGE",
                "cleanPayMonths": 0,
                "collateralType": "GNMA",
                "fullPledgeFlag": false,
                "gpmPercentStep": 0.0,
                "incomeCountry3": "USA",
                "instrumentType": "NA",
                "issuerCountry2": "US",
                "issuerCountry3": "USA",
                "lowestRatingNF": "AA+",
                "poolIssuerName": "NA",
                "vPointCategory": "RP",
                "amortizedFHALTV": 63.0,
                "bloombergTicker": "GNSF 3.5 2013",
                "industrySubCode": "MT",
                "originationDate": "2013-05-01",
                "originationYear": 2013,
                "percent2To4Unit": 2.7,
                "percentHAMPMods": 0.9,
                "percentPurchase": 31.8,
                "percentStateHFA": 0.4,
                "poolOriginalWAM": 0,
                "preliminaryFlag": false,
                "redemptionValue": 100.0,
                "securitySubType": "MPGNMA",
                "dataQuartileList": [
                    {
                        "ltvlow": 17.0,
                        "ltvhigh": 87.0,
                        "loanSizeLow": 22000.0,
                        "loanSizeHigh": 101000.0,
                        "percentDTILow": 10.0,
                        "creditScoreLow": 300.0,
                        "percentDTIHigh": 24.5,
                        "creditScoreHigh": 655.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20101101,
                        "originalLoanAgeHigh": 0,
                        "originationYearHigh": 20130401
                    },
                    {
                        "ltvlow": 87.0,
                        "ltvhigh": 93.0,
                        "loanSizeLow": 101000.0,
                        "loanSizeHigh": 132000.0,
                        "percentDTILow": 24.5,
                        "creditScoreLow": 655.0,
                        "percentDTIHigh": 34.7,
                        "creditScoreHigh": 691.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20130401,
                        "originalLoanAgeHigh": 0,
                        "originationYearHigh": 20130501
                    },
                    {
                        "ltvlow": 93.0,
                        "ltvhigh": 97.0,
                        "loanSizeLow": 132000.0,
                        "loanSizeHigh": 183000.0,
                        "percentDTILow": 34.7,
                        "creditScoreLow": 691.0,
                        "percentDTIHigh": 43.6,
                        "creditScoreHigh": 739.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20130501,
                        "originalLoanAgeHigh": 1,
                        "originationYearHigh": 20130701
                    },
                    {
                        "ltvlow": 97.0,
                        "ltvhigh": 118.0,
                        "loanSizeLow": 183000.0,
                        "loanSizeHigh": 743000.0,
                        "percentDTILow": 43.6,
                        "creditScoreLow": 739.0,
                        "percentDTIHigh": 65.0,
                        "creditScoreHigh": 832.0,
                        "originalLoanAgeLow": 1,
                        "originationYearLow": 20130701,
                        "originalLoanAgeHigh": 43,
                        "originationYearHigh": 20141101
                    }
                ],
                "gpmNumberOfSteps": 0,
                "percentHARPOwner": 0.0,
                "percentPrincipal": 100.0,
                "securityCalcType": "GNMA",
                "assetClassSubCode": "MBS",
                "forbearanceAmount": 0.0,
                "modifiedTimeStamp": "2025-08-13T19:37:00Z",
                "outstandingAmount": 1079.93,
                "parentDescription": "NA",
                "poolIsBalloonFlag": false,
                "prepaymentOptions": {
                    "prepayType": [
                        "CPR",
                        "PSA",
                        "VEC"
                    ]
                },
                "reperformerMonths": 1,
                "dataPPMHistoryList": [
                    {
                        "prepayType": "PSA",
                        "dataPPMHistoryDetailList": [
                            {
                                "month": "1",
                                "prepayRate": 104.2558
                            },
                            {
                                "month": "3",
                                "prepayRate": 101.9675
                            },
                            {
                                "month": "6",
                                "prepayRate": 101.3512
                            },
                            {
                                "month": "12",
                                "prepayRate": 101.4048
                            },
                            {
                                "month": "24",
                                "prepayRate": 0.0
                            }
                        ]
                    },
                    {
                        "prepayType": "CPR",
                        "dataPPMHistoryDetailList": [
                            {
                                "month": "1",
                                "prepayRate": 6.2554
                            },
                            {
                                "month": "3",
                                "prepayRate": 6.118
                            },
                            {
                                "month": "6",
                                "prepayRate": 6.0811
                            },
                            {
                                "month": "12",
                                "prepayRate": 6.0843
                            },
                            {
                                "month": "24",
                                "prepayRate": 0.0
                            }
                        ]
                    }
                ],
                "daysToFirstPayment": 44,
                "issuerLowestRating": "NA",
                "issuerMiddleRating": "NA",
                "newCurrentLoanSize": 101863.0,
                "originationChannel": {
                    "broker": 4.65,
                    "retail": 61.97,
                    "unknown": 0.0,
                    "unspecified": 0.0,
                    "correspondence": 33.37
                },
                "percentMultiFamily": 2.7,
                "percentRefiCashout": 5.8,
                "percentRegularMods": 3.6,
                "percentReperformer": 0.5,
                "relocationLoanFlag": false,
                "socialDensityScore": 0.0,
                "umbsfhlgPercentage": 0.0,
                "umbsfnmaPercentage": 0.0,
                "industryDescription": "Mortgage",
                "issuerHighestRating": "NA",
                "newOriginalLoanSize": 182051.0,
                "socialCriteriaShare": 0.0,
                "spreadAtOrigination": 22.3,
                "weightedAvgLoanSize": 101863.0,
                "poolOriginalLoanSize": 182051.0,
                "cgmiSectorDescription": "Mortgage",
                "cleanPayAverageMonths": 0,
                "expModelAvailableFlag": true,
                "fhfaImpliedCurrentLTV": 27.5,
                "percentRefiNonCashout": 57.9,
                "prepayPenaltySchedule": "0.000",
                "defaultHorizonPYMethod": "OAS Change",
                "industrySubDescription": "Mortgage Asset Backed",
                "actualPrepayHistoryList": {
                    "date": "2025-10-01",
                    "genericValue": 0.9575
                },
                "adjustedCurrentLoanSize": 101863.0,
                "forbearanceModification": 0.0,
                "percentTwoPlusBorrowers": 44.0,
                "poolAvgOriginalLoanTerm": 0,
                "adjustedOriginalLoanSize": 182040.0,
                "assetClassSubDescription": "Collateralized Asset Backed - Mortgage",
                "mortgageInsurancePremium": {
                    "annual": {
                        "va": 0.0,
                        "fha": 0.797,
                        "pih": 0.0,
                        "rhs": 0.399
                    },
                    "upfront": {
                        "va": 0.5,
                        "fha": 0.693,
                        "pih": 1.0,
                        "rhs": 1.996
                    }
                },
                "percentReperformerAndMod": 0.1,
                "reperformerMonthsForMods": 2,
                "originalLoanSizeRemaining": 150891.0,
                "percentFirstTimeHomeBuyer": 20.8,
                "current3rdPartyOrigination": 38.02,
                "adjustedSpreadAtOrigination": 22.3,
                "dataPrepayModelServicerList": [
                    {
                        "percent": 23.84,
                        "servicer": "FREE"
                    },
                    {
                        "percent": 11.4,
                        "servicer": "NSTAR"
                    },
                    {
                        "percent": 11.39,
                        "servicer": "WELLS"
                    },
                    {
                        "percent": 11.15,
                        "servicer": "BCPOP"
                    },
                    {
                        "percent": 7.23,
                        "servicer": "QUICK"
                    },
                    {
                        "percent": 7.13,
                        "servicer": "PENNY"
                    },
                    {
                        "percent": 6.51,
                        "servicer": "LAKEV"
                    },
                    {
                        "percent": 6.34,
                        "servicer": "CARRG"
                    },
                    {
                        "percent": 5.5,
                        "servicer": "USB"
                    },
                    {
                        "percent": 2.41,
                        "servicer": "PNC"
                    },
                    {
                        "percent": 1.34,
                        "servicer": "MNTBK"
                    },
                    {
                        "percent": 1.17,
                        "servicer": "NWRES"
                    },
                    {
                        "percent": 0.95,
                        "servicer": "FIFTH"
                    },
                    {
                        "percent": 0.75,
                        "servicer": "DEPOT"
                    },
                    {
                        "percent": 0.6,
                        "servicer": "BOKF"
                    },
                    {
                        "percent": 0.51,
                        "servicer": "JPM"
                    },
                    {
                        "percent": 0.48,
                        "servicer": "TRUIS"
                    },
                    {
                        "percent": 0.42,
                        "servicer": "CITI"
                    },
                    {
                        "percent": 0.38,
                        "servicer": "GUILD"
                    },
                    {
                        "percent": 0.21,
                        "servicer": "REGNS"
                    },
                    {
                        "percent": 0.2,
                        "servicer": "CNTRL"
                    },
                    {
                        "percent": 0.09,
                        "servicer": "COLNL"
                    },
                    {
                        "percent": 0.06,
                        "servicer": "HFAGY"
                    },
                    {
                        "percent": 0.06,
                        "servicer": "MNSRC"
                    },
                    {
                        "percent": 0.03,
                        "servicer": "HOMBR"
                    }
                ],
                "nonWeightedOriginalLoanSize": 0.0,
                "original3rdPartyOrigination": 0.0,
                "percentHARPDec2010Extension": 0.0,
                "percentHARPOneYearExtension": 0.0,
                "percentDownPaymentAssistance": 5.6,
                "percentAmortizedFHALTVUnder78": 95.4,
                "loanPerformanceImpliedCurrentLTV": 44.8,
                "reperformerMonthsForReperformers": 28
            },
            "ticker": "GNMA",
            "country": "US",
            "currency": "USD",
            "identifier": "999818YT",
            "description": "30-YR GNMA-2013 PROD",
            "issuerTicker": "GNMA",
            "maturityDate": "2041-12-01",
            "securityType": "MORT",
            "currentCoupon": 3.5,
            "securitySubType": "MPGNMA"
        },
        "meta": {
            "status": "DONE",
            "requestId": "R-20895",
            "timeStamp": "2025-08-18T22:30:49Z",
            "responseType": "BOND_INDIC"
        }
    }

    """

    try:
        logger.info("Calling request_bond_indic_async_get")

        response = Client().yield_book_rest.request_bond_indic_async_get(
            id=id,
            id_type=id_type,
            keywords=keywords,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_bond_indic_async_get")

        return output
    except Exception as err:
        logger.error("Error request_bond_indic_async_get.")
        check_exception_and_raise(err, logger)


def request_bond_indic_sync(
    *,
    input: Optional[List[IdentifierInfo]] = None,
    keywords: Optional[List[str]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> MappedResponseRefData:
    """
    Synchronous Post method to retrieve the contractual information about the reference data of instruments, which will typically not need any further calculations. Retrieve instrument reference data given a BondIndicRequest - 'Input' - parameter that includes the information of which security or list of securities to be queried by CUSIP, ISIN, or other identifier type to obtain basic contractual information in the MappedResponseRefData such as security type, sector,  maturity, credit ratings, coupon, and specific information based on security type like current pool factor if the requested identifier is a mortgage. Recommended and preferred method for single or low-volume instrument queries (up to 50-70 per request, 250 max).

    Parameters
    ----------
    input : List[IdentifierInfo], optional
        Single identifier or a list of identifiers to search instruments by.
    keywords : List[str], optional
        List of keywords from the MappedResponseRefData to be exposed in the result data set.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    MappedResponseRefData
        Bond indicative response data from the server. It returns a generic container of data contaning a combined dataset of all available instrument types, with only dedicated data filled out. For more information check 'Results' model documentation.

    Examples
    --------
    >>> # Request bond indic with sync post
    >>> response = request_bond_indic_sync(input=[IdentifierInfo(identifier="999818YT")])
    >>>
    >>> # Print results
    >>> print(js.dumps(response.as_dict(), indent=4))
    {
        "meta": {
            "status": "DONE",
            "requestId": "R-150602",
            "timeStamp": "2025-12-03T07:42:59Z",
            "responseType": "BOND_INDIC",
            "resultsStatus": "ALL"
        },
        "results": [
            {
                "cusip": "999818YT8",
                "indic": {
                    "ltv": 91.0,
                    "wam": 192,
                    "figi": "BBG0033WXBV4",
                    "cusip": "999818YT8",
                    "moody": [
                        {
                            "value": "Aaa"
                        }
                    ],
                    "source": "CITI",
                    "ticker": "GNMA",
                    "country": "US",
                    "loanAge": 151,
                    "lockout": 0,
                    "putFlag": false,
                    "callFlag": false,
                    "cobsCode": "MTGE",
                    "country2": "US",
                    "country3": "USA",
                    "currency": "USD",
                    "dayCount": "30/360 eom",
                    "glicCode": "MBS",
                    "grossWAC": 4.0,
                    "ioPeriod": 0,
                    "poolCode": "NA",
                    "sinkFlag": false,
                    "cmaTicker": "N/A",
                    "datedDate": "2013-05-01",
                    "gnma2Flag": false,
                    "percentVA": 11.01,
                    "currentLTV": 27.6,
                    "extendFlag": "N",
                    "isoCountry": "US",
                    "marketType": "DOMC",
                    "percentDTI": 34.0,
                    "percentFHA": 80.9,
                    "percentInv": 0.0,
                    "percentPIH": 0.15,
                    "percentRHS": 7.94,
                    "securityID": "999818YT",
                    "serviceFee": 0.5,
                    "vPointType": "MPGNMA",
                    "adjustedLTV": 27.6,
                    "combinedLTV": 90.7,
                    "creditScore": 692,
                    "description": "30-YR GNMA-2013 PROD",
                    "esgBondFlag": false,
                    "indexRating": "AA+",
                    "issueAmount": 8597.24,
                    "lowerRating": "AA+",
                    "paymentFreq": 12,
                    "percentHARP": 0.0,
                    "percentRefi": 63.6,
                    "tierCapital": "NA",
                    "balloonMonth": 0,
                    "deliveryFlag": "N",
                    "indexCountry": "US",
                    "industryCode": "MT",
                    "issuerTicker": "GNMA",
                    "lowestRating": "AA+",
                    "maturityDate": "2041-12-01",
                    "middleRating": "AA+",
                    "modifiedDate": "2025-11-14",
                    "originalTerm": 360,
                    "parentTicker": "GNMA",
                    "percentHARP2": 0.0,
                    "percentJumbo": 0.0,
                    "securityType": "MORT",
                    "currentCoupon": 3.5,
                    "dataStateList": [
                        {
                            "state": "PR",
                            "percent": 17.28
                        },
                        {
                            "state": "TX",
                            "percent": 10.02
                        },
                        {
                            "state": "FL",
                            "percent": 5.65
                        },
                        {
                            "state": "CA",
                            "percent": 4.98
                        },
                        {
                            "state": "NY",
                            "percent": 4.79
                        },
                        {
                            "state": "OH",
                            "percent": 4.77
                        },
                        {
                            "state": "GA",
                            "percent": 4.43
                        },
                        {
                            "state": "PA",
                            "percent": 3.39
                        },
                        {
                            "state": "MI",
                            "percent": 3.02
                        },
                        {
                            "state": "NC",
                            "percent": 2.73
                        },
                        {
                            "state": "VA",
                            "percent": 2.68
                        },
                        {
                            "state": "IL",
                            "percent": 2.62
                        },
                        {
                            "state": "NJ",
                            "percent": 2.42
                        },
                        {
                            "state": "IN",
                            "percent": 2.35
                        },
                        {
                            "state": "MD",
                            "percent": 2.18
                        },
                        {
                            "state": "MO",
                            "percent": 2.11
                        },
                        {
                            "state": "AZ",
                            "percent": 1.73
                        },
                        {
                            "state": "TN",
                            "percent": 1.66
                        },
                        {
                            "state": "WA",
                            "percent": 1.48
                        },
                        {
                            "state": "AL",
                            "percent": 1.46
                        },
                        {
                            "state": "LA",
                            "percent": 1.23
                        },
                        {
                            "state": "OK",
                            "percent": 1.22
                        },
                        {
                            "state": "MN",
                            "percent": 1.18
                        },
                        {
                            "state": "SC",
                            "percent": 1.11
                        },
                        {
                            "state": "CT",
                            "percent": 1.1
                        },
                        {
                            "state": "KY",
                            "percent": 1.05
                        },
                        {
                            "state": "CO",
                            "percent": 1.01
                        },
                        {
                            "state": "WI",
                            "percent": 1.01
                        },
                        {
                            "state": "NM",
                            "percent": 0.96
                        },
                        {
                            "state": "MS",
                            "percent": 0.95
                        },
                        {
                            "state": "OR",
                            "percent": 0.91
                        },
                        {
                            "state": "AR",
                            "percent": 0.76
                        },
                        {
                            "state": "NV",
                            "percent": 0.7
                        },
                        {
                            "state": "MA",
                            "percent": 0.65
                        },
                        {
                            "state": "IA",
                            "percent": 0.61
                        },
                        {
                            "state": "UT",
                            "percent": 0.58
                        },
                        {
                            "state": "KS",
                            "percent": 0.57
                        },
                        {
                            "state": "DE",
                            "percent": 0.44
                        },
                        {
                            "state": "ID",
                            "percent": 0.4
                        },
                        {
                            "state": "NE",
                            "percent": 0.38
                        },
                        {
                            "state": "WV",
                            "percent": 0.27
                        },
                        {
                            "state": "ME",
                            "percent": 0.19
                        },
                        {
                            "state": "HI",
                            "percent": 0.16
                        },
                        {
                            "state": "NH",
                            "percent": 0.16
                        },
                        {
                            "state": "MT",
                            "percent": 0.13
                        },
                        {
                            "state": "AK",
                            "percent": 0.12
                        },
                        {
                            "state": "RI",
                            "percent": 0.12
                        },
                        {
                            "state": "WY",
                            "percent": 0.08
                        },
                        {
                            "state": "SD",
                            "percent": 0.07
                        },
                        {
                            "state": "VT",
                            "percent": 0.06
                        },
                        {
                            "state": "DC",
                            "percent": 0.04
                        },
                        {
                            "state": "ND",
                            "percent": 0.04
                        }
                    ],
                    "delinquencies": {
                        "del30Days": {
                            "percent": 2.26
                        },
                        "del60Days": {
                            "percent": 0.61
                        },
                        "del90Days": {
                            "percent": 0.22
                        },
                        "del90PlusDays": {
                            "percent": 0.69
                        },
                        "del120PlusDays": {
                            "percent": 0.47
                        }
                    },
                    "greenBondFlag": false,
                    "highestRating": "AAA",
                    "incomeCountry": "US",
                    "issuerCountry": "US",
                    "percentSecond": 0.0,
                    "poolAgeMethod": "Calculated",
                    "prepayEffDate": "2025-10-01",
                    "seniorityType": "NA",
                    "assetClassCode": "CO",
                    "cgmiSectorCode": "MTGE",
                    "cleanPayMonths": 0,
                    "collateralType": "GNMA",
                    "fullPledgeFlag": false,
                    "gpmPercentStep": 0.0,
                    "incomeCountry3": "USA",
                    "instrumentType": "NA",
                    "issuerCountry2": "US",
                    "issuerCountry3": "USA",
                    "lowestRatingNF": "AA+",
                    "poolIssuerName": "NA",
                    "vPointCategory": "RP",
                    "amortizedFHALTV": 62.1,
                    "bloombergTicker": "GNSF 3.5 2013",
                    "industrySubCode": "MT",
                    "originationDate": "2013-05-01",
                    "originationYear": 2013,
                    "percent2To4Unit": 2.7,
                    "percentHAMPMods": 0.9,
                    "percentPurchase": 32.0,
                    "percentStateHFA": 0.4,
                    "poolOriginalWAM": 0,
                    "preliminaryFlag": false,
                    "redemptionValue": 100.0,
                    "securitySubType": "MPGNMA",
                    "dataQuartileList": [
                        {
                            "ltvlow": 17.0,
                            "ltvhigh": 87.0,
                            "loanSizeLow": 22000.0,
                            "loanSizeHigh": 101000.0,
                            "percentDTILow": 10.0,
                            "creditScoreLow": 300.0,
                            "percentDTIHigh": 24.4,
                            "creditScoreHigh": 655.0,
                            "originalLoanAgeLow": 0,
                            "originationYearLow": 20101101,
                            "originalLoanAgeHigh": 0,
                            "originationYearHigh": 20130401
                        },
                        {
                            "ltvlow": 87.0,
                            "ltvhigh": 93.0,
                            "loanSizeLow": 101000.0,
                            "loanSizeHigh": 132000.0,
                            "percentDTILow": 24.4,
                            "creditScoreLow": 655.0,
                            "percentDTIHigh": 34.9,
                            "creditScoreHigh": 691.0,
                            "originalLoanAgeLow": 0,
                            "originationYearLow": 20130401,
                            "originalLoanAgeHigh": 0,
                            "originationYearHigh": 20130501
                        },
                        {
                            "ltvlow": 93.0,
                            "ltvhigh": 97.0,
                            "loanSizeLow": 132000.0,
                            "loanSizeHigh": 183000.0,
                            "percentDTILow": 34.9,
                            "creditScoreLow": 691.0,
                            "percentDTIHigh": 43.6,
                            "creditScoreHigh": 738.0,
                            "originalLoanAgeLow": 0,
                            "originationYearLow": 20130501,
                            "originalLoanAgeHigh": 1,
                            "originationYearHigh": 20130701
                        },
                        {
                            "ltvlow": 97.0,
                            "ltvhigh": 118.0,
                            "loanSizeLow": 183000.0,
                            "loanSizeHigh": 743000.0,
                            "percentDTILow": 43.6,
                            "creditScoreLow": 738.0,
                            "percentDTIHigh": 65.0,
                            "creditScoreHigh": 832.0,
                            "originalLoanAgeLow": 1,
                            "originationYearLow": 20130701,
                            "originalLoanAgeHigh": 43,
                            "originationYearHigh": 20141101
                        }
                    ],
                    "gpmNumberOfSteps": 0,
                    "percentHARPOwner": 0.0,
                    "percentPrincipal": 100.0,
                    "securityCalcType": "GNMA",
                    "assetClassSubCode": "MBS",
                    "forbearanceAmount": 0.0,
                    "modifiedTimeStamp": "2025-11-14T17:21:00Z",
                    "outstandingAmount": 1049.36,
                    "parentDescription": "NA",
                    "poolIsBalloonFlag": false,
                    "prepaymentOptions": {
                        "prepayType": [
                            "CPR",
                            "PSA",
                            "VEC"
                        ]
                    },
                    "reperformerMonths": 1,
                    "dataPPMHistoryList": [
                        {
                            "prepayType": "PSA",
                            "dataPPMHistoryDetailList": [
                                {
                                    "month": "1",
                                    "prepayRate": 114.1334
                                },
                                {
                                    "month": "3",
                                    "prepayRate": 108.6911
                                },
                                {
                                    "month": "6",
                                    "prepayRate": 105.6514
                                },
                                {
                                    "month": "12",
                                    "prepayRate": 103.3021
                                },
                                {
                                    "month": "24",
                                    "prepayRate": 0.0
                                }
                            ]
                        },
                        {
                            "prepayType": "CPR",
                            "dataPPMHistoryDetailList": [
                                {
                                    "month": "1",
                                    "prepayRate": 6.848
                                },
                                {
                                    "month": "3",
                                    "prepayRate": 6.5215
                                },
                                {
                                    "month": "6",
                                    "prepayRate": 6.3391
                                },
                                {
                                    "month": "12",
                                    "prepayRate": 6.1981
                                },
                                {
                                    "month": "24",
                                    "prepayRate": 0.0
                                }
                            ]
                        }
                    ],
                    "daysToFirstPayment": 44,
                    "issuerLowestRating": "NA",
                    "issuerMiddleRating": "NA",
                    "newCurrentLoanSize": 100633.0,
                    "originationChannel": {
                        "broker": 4.68,
                        "retail": 61.86,
                        "unknown": 0.0,
                        "unspecified": 0.0,
                        "correspondence": 33.46
                    },
                    "percentMultiFamily": 2.7,
                    "percentRefiCashout": 5.8,
                    "percentRegularMods": 3.6,
                    "percentReperformer": 0.5,
                    "relocationLoanFlag": false,
                    "socialDensityScore": 0.0,
                    "umbsfhlgPercentage": 0.0,
                    "umbsfnmaPercentage": 0.0,
                    "industryDescription": "Mortgage",
                    "issuerHighestRating": "NA",
                    "newOriginalLoanSize": 182005.0,
                    "socialCriteriaShare": 0.0,
                    "spreadAtOrigination": 22.2,
                    "weightedAvgLoanSize": 100633.0,
                    "poolOriginalLoanSize": 182005.0,
                    "cgmiSectorDescription": "Mortgage",
                    "cleanPayAverageMonths": 0,
                    "expModelAvailableFlag": true,
                    "fhfaImpliedCurrentLTV": 27.6,
                    "percentRefiNonCashout": 57.8,
                    "prepayPenaltySchedule": "0.000",
                    "defaultHorizonPYMethod": "OAS Change",
                    "industrySubDescription": "Mortgage Asset Backed",
                    "actualPrepayHistoryList": {
                        "date": "2026-01-01",
                        "genericValue": 1.0104
                    },
                    "adjustedCurrentLoanSize": 100633.0,
                    "forbearanceModification": 0.0,
                    "percentTwoPlusBorrowers": 43.9,
                    "poolAvgOriginalLoanTerm": 0,
                    "adjustedOriginalLoanSize": 181994.0,
                    "assetClassSubDescription": "Collateralized Asset Backed - Mortgage",
                    "mortgageInsurancePremium": {
                        "annual": {
                            "va": 0.0,
                            "fha": 0.797,
                            "pih": 0.0,
                            "rhs": 0.399
                        },
                        "upfront": {
                            "va": 0.5,
                            "fha": 0.694,
                            "pih": 1.0,
                            "rhs": 1.996
                        }
                    },
                    "percentReperformerAndMod": 0.1,
                    "reperformerMonthsForMods": 2,
                    "originalLoanSizeRemaining": 150963.0,
                    "percentFirstTimeHomeBuyer": 20.9,
                    "current3rdPartyOrigination": 38.14,
                    "adjustedSpreadAtOrigination": 22.2,
                    "dataPrepayModelServicerList": [
                        {
                            "percent": 23.73,
                            "servicer": "FREE"
                        },
                        {
                            "percent": 11.9,
                            "servicer": "NSTAR"
                        },
                        {
                            "percent": 11.23,
                            "servicer": "BCPOP"
                        },
                        {
                            "percent": 7.2,
                            "servicer": "QUICK"
                        },
                        {
                            "percent": 7.16,
                            "servicer": "PENNY"
                        },
                        {
                            "percent": 6.47,
                            "servicer": "LAKEV"
                        },
                        {
                            "percent": 6.38,
                            "servicer": "CARRG"
                        },
                        {
                            "percent": 5.5,
                            "servicer": "USB"
                        },
                        {
                            "percent": 3.61,
                            "servicer": "WELLS"
                        },
                        {
                            "percent": 2.4,
                            "servicer": "PNC"
                        },
                        {
                            "percent": 1.35,
                            "servicer": "MNTBK"
                        },
                        {
                            "percent": 1.16,
                            "servicer": "NWRES"
                        },
                        {
                            "percent": 0.95,
                            "servicer": "FIFTH"
                        },
                        {
                            "percent": 0.75,
                            "servicer": "DEPOT"
                        },
                        {
                            "percent": 0.61,
                            "servicer": "BOKF"
                        },
                        {
                            "percent": 0.49,
                            "servicer": "JPM"
                        },
                        {
                            "percent": 0.48,
                            "servicer": "TRUIS"
                        },
                        {
                            "percent": 0.43,
                            "servicer": "CITI"
                        },
                        {
                            "percent": 0.39,
                            "servicer": "GUILD"
                        },
                        {
                            "percent": 0.21,
                            "servicer": "CNTRL"
                        },
                        {
                            "percent": 0.21,
                            "servicer": "REGNS"
                        },
                        {
                            "percent": 0.09,
                            "servicer": "COLNL"
                        },
                        {
                            "percent": 0.06,
                            "servicer": "HFAGY"
                        },
                        {
                            "percent": 0.06,
                            "servicer": "MNSRC"
                        }
                    ],
                    "nonWeightedOriginalLoanSize": 0.0,
                    "original3rdPartyOrigination": 0.0,
                    "percentHARPDec2010Extension": 0.0,
                    "percentHARPOneYearExtension": 0.0,
                    "percentDownPaymentAssistance": 5.6,
                    "percentAmortizedFHALTVUnder78": 95.4,
                    "loanPerformanceImpliedCurrentLTV": 43.6,
                    "reperformerMonthsForReperformers": 28
                },
                "ticker": "GNMA",
                "country": "US",
                "currency": "USD",
                "identifier": "999818YT",
                "description": "30-YR GNMA-2013 PROD",
                "issuerTicker": "GNMA",
                "maturityDate": "2041-12-01",
                "securityType": "MORT",
                "currentCoupon": 3.5,
                "securitySubType": "MPGNMA"
            }
        ]
    }


    >>> # Request bond indic with sync post
    >>> response = request_bond_indic_sync(input=[IdentifierInfo(identifier="999818YT",
    >>>                                                          id_type="CUSIP",
    >>>                                                          )])
    >>>
    >>> # Print results
    >>> print(js.dumps(response.as_dict(), indent=4))
    {
        "meta": {
            "status": "DONE",
            "requestId": "R-150603",
            "timeStamp": "2025-12-03T07:43:00Z",
            "responseType": "BOND_INDIC",
            "resultsStatus": "ALL"
        },
        "results": [
            {
                "cusip": "999818YT8",
                "indic": {
                    "ltv": 91.0,
                    "wam": 192,
                    "figi": "BBG0033WXBV4",
                    "cusip": "999818YT8",
                    "moody": [
                        {
                            "value": "Aaa"
                        }
                    ],
                    "source": "CITI",
                    "ticker": "GNMA",
                    "country": "US",
                    "loanAge": 151,
                    "lockout": 0,
                    "putFlag": false,
                    "callFlag": false,
                    "cobsCode": "MTGE",
                    "country2": "US",
                    "country3": "USA",
                    "currency": "USD",
                    "dayCount": "30/360 eom",
                    "glicCode": "MBS",
                    "grossWAC": 4.0,
                    "ioPeriod": 0,
                    "poolCode": "NA",
                    "sinkFlag": false,
                    "cmaTicker": "N/A",
                    "datedDate": "2013-05-01",
                    "gnma2Flag": false,
                    "percentVA": 11.01,
                    "currentLTV": 27.6,
                    "extendFlag": "N",
                    "isoCountry": "US",
                    "marketType": "DOMC",
                    "percentDTI": 34.0,
                    "percentFHA": 80.9,
                    "percentInv": 0.0,
                    "percentPIH": 0.15,
                    "percentRHS": 7.94,
                    "securityID": "999818YT",
                    "serviceFee": 0.5,
                    "vPointType": "MPGNMA",
                    "adjustedLTV": 27.6,
                    "combinedLTV": 90.7,
                    "creditScore": 692,
                    "description": "30-YR GNMA-2013 PROD",
                    "esgBondFlag": false,
                    "indexRating": "AA+",
                    "issueAmount": 8597.24,
                    "lowerRating": "AA+",
                    "paymentFreq": 12,
                    "percentHARP": 0.0,
                    "percentRefi": 63.6,
                    "tierCapital": "NA",
                    "balloonMonth": 0,
                    "deliveryFlag": "N",
                    "indexCountry": "US",
                    "industryCode": "MT",
                    "issuerTicker": "GNMA",
                    "lowestRating": "AA+",
                    "maturityDate": "2041-12-01",
                    "middleRating": "AA+",
                    "modifiedDate": "2025-11-14",
                    "originalTerm": 360,
                    "parentTicker": "GNMA",
                    "percentHARP2": 0.0,
                    "percentJumbo": 0.0,
                    "securityType": "MORT",
                    "currentCoupon": 3.5,
                    "dataStateList": [
                        {
                            "state": "PR",
                            "percent": 17.28
                        },
                        {
                            "state": "TX",
                            "percent": 10.02
                        },
                        {
                            "state": "FL",
                            "percent": 5.65
                        },
                        {
                            "state": "CA",
                            "percent": 4.98
                        },
                        {
                            "state": "NY",
                            "percent": 4.79
                        },
                        {
                            "state": "OH",
                            "percent": 4.77
                        },
                        {
                            "state": "GA",
                            "percent": 4.43
                        },
                        {
                            "state": "PA",
                            "percent": 3.39
                        },
                        {
                            "state": "MI",
                            "percent": 3.02
                        },
                        {
                            "state": "NC",
                            "percent": 2.73
                        },
                        {
                            "state": "VA",
                            "percent": 2.68
                        },
                        {
                            "state": "IL",
                            "percent": 2.62
                        },
                        {
                            "state": "NJ",
                            "percent": 2.42
                        },
                        {
                            "state": "IN",
                            "percent": 2.35
                        },
                        {
                            "state": "MD",
                            "percent": 2.18
                        },
                        {
                            "state": "MO",
                            "percent": 2.11
                        },
                        {
                            "state": "AZ",
                            "percent": 1.73
                        },
                        {
                            "state": "TN",
                            "percent": 1.66
                        },
                        {
                            "state": "WA",
                            "percent": 1.48
                        },
                        {
                            "state": "AL",
                            "percent": 1.46
                        },
                        {
                            "state": "LA",
                            "percent": 1.23
                        },
                        {
                            "state": "OK",
                            "percent": 1.22
                        },
                        {
                            "state": "MN",
                            "percent": 1.18
                        },
                        {
                            "state": "SC",
                            "percent": 1.11
                        },
                        {
                            "state": "CT",
                            "percent": 1.1
                        },
                        {
                            "state": "KY",
                            "percent": 1.05
                        },
                        {
                            "state": "CO",
                            "percent": 1.01
                        },
                        {
                            "state": "WI",
                            "percent": 1.01
                        },
                        {
                            "state": "NM",
                            "percent": 0.96
                        },
                        {
                            "state": "MS",
                            "percent": 0.95
                        },
                        {
                            "state": "OR",
                            "percent": 0.91
                        },
                        {
                            "state": "AR",
                            "percent": 0.76
                        },
                        {
                            "state": "NV",
                            "percent": 0.7
                        },
                        {
                            "state": "MA",
                            "percent": 0.65
                        },
                        {
                            "state": "IA",
                            "percent": 0.61
                        },
                        {
                            "state": "UT",
                            "percent": 0.58
                        },
                        {
                            "state": "KS",
                            "percent": 0.57
                        },
                        {
                            "state": "DE",
                            "percent": 0.44
                        },
                        {
                            "state": "ID",
                            "percent": 0.4
                        },
                        {
                            "state": "NE",
                            "percent": 0.38
                        },
                        {
                            "state": "WV",
                            "percent": 0.27
                        },
                        {
                            "state": "ME",
                            "percent": 0.19
                        },
                        {
                            "state": "HI",
                            "percent": 0.16
                        },
                        {
                            "state": "NH",
                            "percent": 0.16
                        },
                        {
                            "state": "MT",
                            "percent": 0.13
                        },
                        {
                            "state": "AK",
                            "percent": 0.12
                        },
                        {
                            "state": "RI",
                            "percent": 0.12
                        },
                        {
                            "state": "WY",
                            "percent": 0.08
                        },
                        {
                            "state": "SD",
                            "percent": 0.07
                        },
                        {
                            "state": "VT",
                            "percent": 0.06
                        },
                        {
                            "state": "DC",
                            "percent": 0.04
                        },
                        {
                            "state": "ND",
                            "percent": 0.04
                        }
                    ],
                    "delinquencies": {
                        "del30Days": {
                            "percent": 2.26
                        },
                        "del60Days": {
                            "percent": 0.61
                        },
                        "del90Days": {
                            "percent": 0.22
                        },
                        "del90PlusDays": {
                            "percent": 0.69
                        },
                        "del120PlusDays": {
                            "percent": 0.47
                        }
                    },
                    "greenBondFlag": false,
                    "highestRating": "AAA",
                    "incomeCountry": "US",
                    "issuerCountry": "US",
                    "percentSecond": 0.0,
                    "poolAgeMethod": "Calculated",
                    "prepayEffDate": "2025-10-01",
                    "seniorityType": "NA",
                    "assetClassCode": "CO",
                    "cgmiSectorCode": "MTGE",
                    "cleanPayMonths": 0,
                    "collateralType": "GNMA",
                    "fullPledgeFlag": false,
                    "gpmPercentStep": 0.0,
                    "incomeCountry3": "USA",
                    "instrumentType": "NA",
                    "issuerCountry2": "US",
                    "issuerCountry3": "USA",
                    "lowestRatingNF": "AA+",
                    "poolIssuerName": "NA",
                    "vPointCategory": "RP",
                    "amortizedFHALTV": 62.1,
                    "bloombergTicker": "GNSF 3.5 2013",
                    "industrySubCode": "MT",
                    "originationDate": "2013-05-01",
                    "originationYear": 2013,
                    "percent2To4Unit": 2.7,
                    "percentHAMPMods": 0.9,
                    "percentPurchase": 32.0,
                    "percentStateHFA": 0.4,
                    "poolOriginalWAM": 0,
                    "preliminaryFlag": false,
                    "redemptionValue": 100.0,
                    "securitySubType": "MPGNMA",
                    "dataQuartileList": [
                        {
                            "ltvlow": 17.0,
                            "ltvhigh": 87.0,
                            "loanSizeLow": 22000.0,
                            "loanSizeHigh": 101000.0,
                            "percentDTILow": 10.0,
                            "creditScoreLow": 300.0,
                            "percentDTIHigh": 24.4,
                            "creditScoreHigh": 655.0,
                            "originalLoanAgeLow": 0,
                            "originationYearLow": 20101101,
                            "originalLoanAgeHigh": 0,
                            "originationYearHigh": 20130401
                        },
                        {
                            "ltvlow": 87.0,
                            "ltvhigh": 93.0,
                            "loanSizeLow": 101000.0,
                            "loanSizeHigh": 132000.0,
                            "percentDTILow": 24.4,
                            "creditScoreLow": 655.0,
                            "percentDTIHigh": 34.9,
                            "creditScoreHigh": 691.0,
                            "originalLoanAgeLow": 0,
                            "originationYearLow": 20130401,
                            "originalLoanAgeHigh": 0,
                            "originationYearHigh": 20130501
                        },
                        {
                            "ltvlow": 93.0,
                            "ltvhigh": 97.0,
                            "loanSizeLow": 132000.0,
                            "loanSizeHigh": 183000.0,
                            "percentDTILow": 34.9,
                            "creditScoreLow": 691.0,
                            "percentDTIHigh": 43.6,
                            "creditScoreHigh": 738.0,
                            "originalLoanAgeLow": 0,
                            "originationYearLow": 20130501,
                            "originalLoanAgeHigh": 1,
                            "originationYearHigh": 20130701
                        },
                        {
                            "ltvlow": 97.0,
                            "ltvhigh": 118.0,
                            "loanSizeLow": 183000.0,
                            "loanSizeHigh": 743000.0,
                            "percentDTILow": 43.6,
                            "creditScoreLow": 738.0,
                            "percentDTIHigh": 65.0,
                            "creditScoreHigh": 832.0,
                            "originalLoanAgeLow": 1,
                            "originationYearLow": 20130701,
                            "originalLoanAgeHigh": 43,
                            "originationYearHigh": 20141101
                        }
                    ],
                    "gpmNumberOfSteps": 0,
                    "percentHARPOwner": 0.0,
                    "percentPrincipal": 100.0,
                    "securityCalcType": "GNMA",
                    "assetClassSubCode": "MBS",
                    "forbearanceAmount": 0.0,
                    "modifiedTimeStamp": "2025-11-14T17:21:00Z",
                    "outstandingAmount": 1049.36,
                    "parentDescription": "NA",
                    "poolIsBalloonFlag": false,
                    "prepaymentOptions": {
                        "prepayType": [
                            "CPR",
                            "PSA",
                            "VEC"
                        ]
                    },
                    "reperformerMonths": 1,
                    "dataPPMHistoryList": [
                        {
                            "prepayType": "PSA",
                            "dataPPMHistoryDetailList": [
                                {
                                    "month": "1",
                                    "prepayRate": 114.1334
                                },
                                {
                                    "month": "3",
                                    "prepayRate": 108.6911
                                },
                                {
                                    "month": "6",
                                    "prepayRate": 105.6514
                                },
                                {
                                    "month": "12",
                                    "prepayRate": 103.3021
                                },
                                {
                                    "month": "24",
                                    "prepayRate": 0.0
                                }
                            ]
                        },
                        {
                            "prepayType": "CPR",
                            "dataPPMHistoryDetailList": [
                                {
                                    "month": "1",
                                    "prepayRate": 6.848
                                },
                                {
                                    "month": "3",
                                    "prepayRate": 6.5215
                                },
                                {
                                    "month": "6",
                                    "prepayRate": 6.3391
                                },
                                {
                                    "month": "12",
                                    "prepayRate": 6.1981
                                },
                                {
                                    "month": "24",
                                    "prepayRate": 0.0
                                }
                            ]
                        }
                    ],
                    "daysToFirstPayment": 44,
                    "issuerLowestRating": "NA",
                    "issuerMiddleRating": "NA",
                    "newCurrentLoanSize": 100633.0,
                    "originationChannel": {
                        "broker": 4.68,
                        "retail": 61.86,
                        "unknown": 0.0,
                        "unspecified": 0.0,
                        "correspondence": 33.46
                    },
                    "percentMultiFamily": 2.7,
                    "percentRefiCashout": 5.8,
                    "percentRegularMods": 3.6,
                    "percentReperformer": 0.5,
                    "relocationLoanFlag": false,
                    "socialDensityScore": 0.0,
                    "umbsfhlgPercentage": 0.0,
                    "umbsfnmaPercentage": 0.0,
                    "industryDescription": "Mortgage",
                    "issuerHighestRating": "NA",
                    "newOriginalLoanSize": 182005.0,
                    "socialCriteriaShare": 0.0,
                    "spreadAtOrigination": 22.2,
                    "weightedAvgLoanSize": 100633.0,
                    "poolOriginalLoanSize": 182005.0,
                    "cgmiSectorDescription": "Mortgage",
                    "cleanPayAverageMonths": 0,
                    "expModelAvailableFlag": true,
                    "fhfaImpliedCurrentLTV": 27.6,
                    "percentRefiNonCashout": 57.8,
                    "prepayPenaltySchedule": "0.000",
                    "defaultHorizonPYMethod": "OAS Change",
                    "industrySubDescription": "Mortgage Asset Backed",
                    "actualPrepayHistoryList": {
                        "date": "2026-01-01",
                        "genericValue": 1.0104
                    },
                    "adjustedCurrentLoanSize": 100633.0,
                    "forbearanceModification": 0.0,
                    "percentTwoPlusBorrowers": 43.9,
                    "poolAvgOriginalLoanTerm": 0,
                    "adjustedOriginalLoanSize": 181994.0,
                    "assetClassSubDescription": "Collateralized Asset Backed - Mortgage",
                    "mortgageInsurancePremium": {
                        "annual": {
                            "va": 0.0,
                            "fha": 0.797,
                            "pih": 0.0,
                            "rhs": 0.399
                        },
                        "upfront": {
                            "va": 0.5,
                            "fha": 0.694,
                            "pih": 1.0,
                            "rhs": 1.996
                        }
                    },
                    "percentReperformerAndMod": 0.1,
                    "reperformerMonthsForMods": 2,
                    "originalLoanSizeRemaining": 150963.0,
                    "percentFirstTimeHomeBuyer": 20.9,
                    "current3rdPartyOrigination": 38.14,
                    "adjustedSpreadAtOrigination": 22.2,
                    "dataPrepayModelServicerList": [
                        {
                            "percent": 23.73,
                            "servicer": "FREE"
                        },
                        {
                            "percent": 11.9,
                            "servicer": "NSTAR"
                        },
                        {
                            "percent": 11.23,
                            "servicer": "BCPOP"
                        },
                        {
                            "percent": 7.2,
                            "servicer": "QUICK"
                        },
                        {
                            "percent": 7.16,
                            "servicer": "PENNY"
                        },
                        {
                            "percent": 6.47,
                            "servicer": "LAKEV"
                        },
                        {
                            "percent": 6.38,
                            "servicer": "CARRG"
                        },
                        {
                            "percent": 5.5,
                            "servicer": "USB"
                        },
                        {
                            "percent": 3.61,
                            "servicer": "WELLS"
                        },
                        {
                            "percent": 2.4,
                            "servicer": "PNC"
                        },
                        {
                            "percent": 1.35,
                            "servicer": "MNTBK"
                        },
                        {
                            "percent": 1.16,
                            "servicer": "NWRES"
                        },
                        {
                            "percent": 0.95,
                            "servicer": "FIFTH"
                        },
                        {
                            "percent": 0.75,
                            "servicer": "DEPOT"
                        },
                        {
                            "percent": 0.61,
                            "servicer": "BOKF"
                        },
                        {
                            "percent": 0.49,
                            "servicer": "JPM"
                        },
                        {
                            "percent": 0.48,
                            "servicer": "TRUIS"
                        },
                        {
                            "percent": 0.43,
                            "servicer": "CITI"
                        },
                        {
                            "percent": 0.39,
                            "servicer": "GUILD"
                        },
                        {
                            "percent": 0.21,
                            "servicer": "CNTRL"
                        },
                        {
                            "percent": 0.21,
                            "servicer": "REGNS"
                        },
                        {
                            "percent": 0.09,
                            "servicer": "COLNL"
                        },
                        {
                            "percent": 0.06,
                            "servicer": "HFAGY"
                        },
                        {
                            "percent": 0.06,
                            "servicer": "MNSRC"
                        }
                    ],
                    "nonWeightedOriginalLoanSize": 0.0,
                    "original3rdPartyOrigination": 0.0,
                    "percentHARPDec2010Extension": 0.0,
                    "percentHARPOneYearExtension": 0.0,
                    "percentDownPaymentAssistance": 5.6,
                    "percentAmortizedFHALTVUnder78": 95.4,
                    "loanPerformanceImpliedCurrentLTV": 43.6,
                    "reperformerMonthsForReperformers": 28
                },
                "ticker": "GNMA",
                "country": "US",
                "currency": "USD",
                "identifier": "999818YT",
                "description": "30-YR GNMA-2013 PROD",
                "issuerTicker": "GNMA",
                "maturityDate": "2041-12-01",
                "securityType": "MORT",
                "currentCoupon": 3.5,
                "securitySubType": "MPGNMA"
            }
        ]
    }

    """

    try:
        logger.info("Calling request_bond_indic_sync")

        response = Client().yield_book_rest.request_bond_indic_sync(
            body=BondIndicRequest(input=input, keywords=keywords),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_bond_indic_sync")

        return output
    except Exception as err:
        logger.error("Error request_bond_indic_sync.")
        check_exception_and_raise(err, logger)


def request_bond_indic_sync_get(
    *,
    id: str,
    id_type: Optional[Union[str, IdTypeEnum]] = None,
    keywords: Optional[List[str]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Synchronous Get method to retrieve the contractual information about the reference data of an instrument, which will typically not need any further calculations. Retrieve instrument reference data given an instrument ID and optionaly an ID type as input parameters to obtain basic contractual information in the Record structure with information such as security type, sector,  maturity, credit ratings, coupon, and specific information based on security type like current pool factor if the requested identifier is a mortgage.

    Parameters
    ----------
    id : str
        A sequence of textual characters.
    id_type : Union[str, IdTypeEnum], optional

    keywords : List[str], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------
    >>> # Request bond indic with sync get
    >>> response = request_bond_indic_sync_get(id="999818YT")
    >>>
    >>> # Print results in json format
    >>> print(js.dumps(response, indent=4))
    {
        "data": {
            "cusip": "999818YT8",
            "indic": {
                "ltv": 91.0,
                "wam": 192,
                "figi": "BBG0033WXBV4",
                "cusip": "999818YT8",
                "moody": [
                    {
                        "value": "Aaa"
                    }
                ],
                "source": "CITI",
                "ticker": "GNMA",
                "country": "US",
                "loanAge": 151,
                "lockout": 0,
                "putFlag": false,
                "callFlag": false,
                "cobsCode": "MTGE",
                "country2": "US",
                "country3": "USA",
                "currency": "USD",
                "dayCount": "30/360 eom",
                "glicCode": "MBS",
                "grossWAC": 4.0,
                "ioPeriod": 0,
                "poolCode": "NA",
                "sinkFlag": false,
                "cmaTicker": "N/A",
                "datedDate": "2013-05-01",
                "gnma2Flag": false,
                "percentVA": 11.01,
                "currentLTV": 27.6,
                "extendFlag": "N",
                "isoCountry": "US",
                "marketType": "DOMC",
                "percentDTI": 34.0,
                "percentFHA": 80.9,
                "percentInv": 0.0,
                "percentPIH": 0.15,
                "percentRHS": 7.94,
                "securityID": "999818YT",
                "serviceFee": 0.5,
                "vPointType": "MPGNMA",
                "adjustedLTV": 27.6,
                "combinedLTV": 90.7,
                "creditScore": 692,
                "description": "30-YR GNMA-2013 PROD",
                "esgBondFlag": false,
                "indexRating": "AA+",
                "issueAmount": 8597.24,
                "lowerRating": "AA+",
                "paymentFreq": 12,
                "percentHARP": 0.0,
                "percentRefi": 63.6,
                "tierCapital": "NA",
                "balloonMonth": 0,
                "deliveryFlag": "N",
                "indexCountry": "US",
                "industryCode": "MT",
                "issuerTicker": "GNMA",
                "lowestRating": "AA+",
                "maturityDate": "2041-12-01",
                "middleRating": "AA+",
                "modifiedDate": "2025-11-14",
                "originalTerm": 360,
                "parentTicker": "GNMA",
                "percentHARP2": 0.0,
                "percentJumbo": 0.0,
                "securityType": "MORT",
                "currentCoupon": 3.5,
                "dataStateList": [
                    {
                        "state": "PR",
                        "percent": 17.28
                    },
                    {
                        "state": "TX",
                        "percent": 10.02
                    },
                    {
                        "state": "FL",
                        "percent": 5.65
                    },
                    {
                        "state": "CA",
                        "percent": 4.98
                    },
                    {
                        "state": "NY",
                        "percent": 4.79
                    },
                    {
                        "state": "OH",
                        "percent": 4.77
                    },
                    {
                        "state": "GA",
                        "percent": 4.43
                    },
                    {
                        "state": "PA",
                        "percent": 3.39
                    },
                    {
                        "state": "MI",
                        "percent": 3.02
                    },
                    {
                        "state": "NC",
                        "percent": 2.73
                    },
                    {
                        "state": "VA",
                        "percent": 2.68
                    },
                    {
                        "state": "IL",
                        "percent": 2.62
                    },
                    {
                        "state": "NJ",
                        "percent": 2.42
                    },
                    {
                        "state": "IN",
                        "percent": 2.35
                    },
                    {
                        "state": "MD",
                        "percent": 2.18
                    },
                    {
                        "state": "MO",
                        "percent": 2.11
                    },
                    {
                        "state": "AZ",
                        "percent": 1.73
                    },
                    {
                        "state": "TN",
                        "percent": 1.66
                    },
                    {
                        "state": "WA",
                        "percent": 1.48
                    },
                    {
                        "state": "AL",
                        "percent": 1.46
                    },
                    {
                        "state": "LA",
                        "percent": 1.23
                    },
                    {
                        "state": "OK",
                        "percent": 1.22
                    },
                    {
                        "state": "MN",
                        "percent": 1.18
                    },
                    {
                        "state": "SC",
                        "percent": 1.11
                    },
                    {
                        "state": "CT",
                        "percent": 1.1
                    },
                    {
                        "state": "KY",
                        "percent": 1.05
                    },
                    {
                        "state": "CO",
                        "percent": 1.01
                    },
                    {
                        "state": "WI",
                        "percent": 1.01
                    },
                    {
                        "state": "NM",
                        "percent": 0.96
                    },
                    {
                        "state": "MS",
                        "percent": 0.95
                    },
                    {
                        "state": "OR",
                        "percent": 0.91
                    },
                    {
                        "state": "AR",
                        "percent": 0.76
                    },
                    {
                        "state": "NV",
                        "percent": 0.7
                    },
                    {
                        "state": "MA",
                        "percent": 0.65
                    },
                    {
                        "state": "IA",
                        "percent": 0.61
                    },
                    {
                        "state": "UT",
                        "percent": 0.58
                    },
                    {
                        "state": "KS",
                        "percent": 0.57
                    },
                    {
                        "state": "DE",
                        "percent": 0.44
                    },
                    {
                        "state": "ID",
                        "percent": 0.4
                    },
                    {
                        "state": "NE",
                        "percent": 0.38
                    },
                    {
                        "state": "WV",
                        "percent": 0.27
                    },
                    {
                        "state": "ME",
                        "percent": 0.19
                    },
                    {
                        "state": "HI",
                        "percent": 0.16
                    },
                    {
                        "state": "NH",
                        "percent": 0.16
                    },
                    {
                        "state": "MT",
                        "percent": 0.13
                    },
                    {
                        "state": "AK",
                        "percent": 0.12
                    },
                    {
                        "state": "RI",
                        "percent": 0.12
                    },
                    {
                        "state": "WY",
                        "percent": 0.08
                    },
                    {
                        "state": "SD",
                        "percent": 0.07
                    },
                    {
                        "state": "VT",
                        "percent": 0.06
                    },
                    {
                        "state": "DC",
                        "percent": 0.04
                    },
                    {
                        "state": "ND",
                        "percent": 0.04
                    }
                ],
                "delinquencies": {
                    "del30Days": {
                        "percent": 2.26
                    },
                    "del60Days": {
                        "percent": 0.61
                    },
                    "del90Days": {
                        "percent": 0.22
                    },
                    "del90PlusDays": {
                        "percent": 0.69
                    },
                    "del120PlusDays": {
                        "percent": 0.47
                    }
                },
                "greenBondFlag": false,
                "highestRating": "AAA",
                "incomeCountry": "US",
                "issuerCountry": "US",
                "percentSecond": 0.0,
                "poolAgeMethod": "Calculated",
                "prepayEffDate": "2025-10-01",
                "seniorityType": "NA",
                "assetClassCode": "CO",
                "cgmiSectorCode": "MTGE",
                "cleanPayMonths": 0,
                "collateralType": "GNMA",
                "fullPledgeFlag": false,
                "gpmPercentStep": 0.0,
                "incomeCountry3": "USA",
                "instrumentType": "NA",
                "issuerCountry2": "US",
                "issuerCountry3": "USA",
                "lowestRatingNF": "AA+",
                "poolIssuerName": "NA",
                "vPointCategory": "RP",
                "amortizedFHALTV": 62.1,
                "bloombergTicker": "GNSF 3.5 2013",
                "industrySubCode": "MT",
                "originationDate": "2013-05-01",
                "originationYear": 2013,
                "percent2To4Unit": 2.7,
                "percentHAMPMods": 0.9,
                "percentPurchase": 32.0,
                "percentStateHFA": 0.4,
                "poolOriginalWAM": 0,
                "preliminaryFlag": false,
                "redemptionValue": 100.0,
                "securitySubType": "MPGNMA",
                "dataQuartileList": [
                    {
                        "ltvlow": 17.0,
                        "ltvhigh": 87.0,
                        "loanSizeLow": 22000.0,
                        "loanSizeHigh": 101000.0,
                        "percentDTILow": 10.0,
                        "creditScoreLow": 300.0,
                        "percentDTIHigh": 24.4,
                        "creditScoreHigh": 655.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20101101,
                        "originalLoanAgeHigh": 0,
                        "originationYearHigh": 20130401
                    },
                    {
                        "ltvlow": 87.0,
                        "ltvhigh": 93.0,
                        "loanSizeLow": 101000.0,
                        "loanSizeHigh": 132000.0,
                        "percentDTILow": 24.4,
                        "creditScoreLow": 655.0,
                        "percentDTIHigh": 34.9,
                        "creditScoreHigh": 691.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20130401,
                        "originalLoanAgeHigh": 0,
                        "originationYearHigh": 20130501
                    },
                    {
                        "ltvlow": 93.0,
                        "ltvhigh": 97.0,
                        "loanSizeLow": 132000.0,
                        "loanSizeHigh": 183000.0,
                        "percentDTILow": 34.9,
                        "creditScoreLow": 691.0,
                        "percentDTIHigh": 43.6,
                        "creditScoreHigh": 738.0,
                        "originalLoanAgeLow": 0,
                        "originationYearLow": 20130501,
                        "originalLoanAgeHigh": 1,
                        "originationYearHigh": 20130701
                    },
                    {
                        "ltvlow": 97.0,
                        "ltvhigh": 118.0,
                        "loanSizeLow": 183000.0,
                        "loanSizeHigh": 743000.0,
                        "percentDTILow": 43.6,
                        "creditScoreLow": 738.0,
                        "percentDTIHigh": 65.0,
                        "creditScoreHigh": 832.0,
                        "originalLoanAgeLow": 1,
                        "originationYearLow": 20130701,
                        "originalLoanAgeHigh": 43,
                        "originationYearHigh": 20141101
                    }
                ],
                "gpmNumberOfSteps": 0,
                "percentHARPOwner": 0.0,
                "percentPrincipal": 100.0,
                "securityCalcType": "GNMA",
                "assetClassSubCode": "MBS",
                "forbearanceAmount": 0.0,
                "modifiedTimeStamp": "2025-11-14T17:21:00Z",
                "outstandingAmount": 1049.36,
                "parentDescription": "NA",
                "poolIsBalloonFlag": false,
                "prepaymentOptions": {
                    "prepayType": [
                        "CPR",
                        "PSA",
                        "VEC"
                    ]
                },
                "reperformerMonths": 1,
                "dataPPMHistoryList": [
                    {
                        "prepayType": "PSA",
                        "dataPPMHistoryDetailList": [
                            {
                                "month": "1",
                                "prepayRate": 114.1334
                            },
                            {
                                "month": "3",
                                "prepayRate": 108.6911
                            },
                            {
                                "month": "6",
                                "prepayRate": 105.6514
                            },
                            {
                                "month": "12",
                                "prepayRate": 103.3021
                            },
                            {
                                "month": "24",
                                "prepayRate": 0.0
                            }
                        ]
                    },
                    {
                        "prepayType": "CPR",
                        "dataPPMHistoryDetailList": [
                            {
                                "month": "1",
                                "prepayRate": 6.848
                            },
                            {
                                "month": "3",
                                "prepayRate": 6.5215
                            },
                            {
                                "month": "6",
                                "prepayRate": 6.3391
                            },
                            {
                                "month": "12",
                                "prepayRate": 6.1981
                            },
                            {
                                "month": "24",
                                "prepayRate": 0.0
                            }
                        ]
                    }
                ],
                "daysToFirstPayment": 44,
                "issuerLowestRating": "NA",
                "issuerMiddleRating": "NA",
                "newCurrentLoanSize": 100633.0,
                "originationChannel": {
                    "broker": 4.68,
                    "retail": 61.86,
                    "unknown": 0.0,
                    "unspecified": 0.0,
                    "correspondence": 33.46
                },
                "percentMultiFamily": 2.7,
                "percentRefiCashout": 5.8,
                "percentRegularMods": 3.6,
                "percentReperformer": 0.5,
                "relocationLoanFlag": false,
                "socialDensityScore": 0.0,
                "umbsfhlgPercentage": 0.0,
                "umbsfnmaPercentage": 0.0,
                "industryDescription": "Mortgage",
                "issuerHighestRating": "NA",
                "newOriginalLoanSize": 182005.0,
                "socialCriteriaShare": 0.0,
                "spreadAtOrigination": 22.2,
                "weightedAvgLoanSize": 100633.0,
                "poolOriginalLoanSize": 182005.0,
                "cgmiSectorDescription": "Mortgage",
                "cleanPayAverageMonths": 0,
                "expModelAvailableFlag": true,
                "fhfaImpliedCurrentLTV": 27.6,
                "percentRefiNonCashout": 57.8,
                "prepayPenaltySchedule": "0.000",
                "defaultHorizonPYMethod": "OAS Change",
                "industrySubDescription": "Mortgage Asset Backed",
                "actualPrepayHistoryList": {
                    "date": "2026-01-01",
                    "genericValue": 1.0104
                },
                "adjustedCurrentLoanSize": 100633.0,
                "forbearanceModification": 0.0,
                "percentTwoPlusBorrowers": 43.9,
                "poolAvgOriginalLoanTerm": 0,
                "adjustedOriginalLoanSize": 181994.0,
                "assetClassSubDescription": "Collateralized Asset Backed - Mortgage",
                "mortgageInsurancePremium": {
                    "annual": {
                        "va": 0.0,
                        "fha": 0.797,
                        "pih": 0.0,
                        "rhs": 0.399
                    },
                    "upfront": {
                        "va": 0.5,
                        "fha": 0.694,
                        "pih": 1.0,
                        "rhs": 1.996
                    }
                },
                "percentReperformerAndMod": 0.1,
                "reperformerMonthsForMods": 2,
                "originalLoanSizeRemaining": 150963.0,
                "percentFirstTimeHomeBuyer": 20.9,
                "current3rdPartyOrigination": 38.14,
                "adjustedSpreadAtOrigination": 22.2,
                "dataPrepayModelServicerList": [
                    {
                        "percent": 23.73,
                        "servicer": "FREE"
                    },
                    {
                        "percent": 11.9,
                        "servicer": "NSTAR"
                    },
                    {
                        "percent": 11.23,
                        "servicer": "BCPOP"
                    },
                    {
                        "percent": 7.2,
                        "servicer": "QUICK"
                    },
                    {
                        "percent": 7.16,
                        "servicer": "PENNY"
                    },
                    {
                        "percent": 6.47,
                        "servicer": "LAKEV"
                    },
                    {
                        "percent": 6.38,
                        "servicer": "CARRG"
                    },
                    {
                        "percent": 5.5,
                        "servicer": "USB"
                    },
                    {
                        "percent": 3.61,
                        "servicer": "WELLS"
                    },
                    {
                        "percent": 2.4,
                        "servicer": "PNC"
                    },
                    {
                        "percent": 1.35,
                        "servicer": "MNTBK"
                    },
                    {
                        "percent": 1.16,
                        "servicer": "NWRES"
                    },
                    {
                        "percent": 0.95,
                        "servicer": "FIFTH"
                    },
                    {
                        "percent": 0.75,
                        "servicer": "DEPOT"
                    },
                    {
                        "percent": 0.61,
                        "servicer": "BOKF"
                    },
                    {
                        "percent": 0.49,
                        "servicer": "JPM"
                    },
                    {
                        "percent": 0.48,
                        "servicer": "TRUIS"
                    },
                    {
                        "percent": 0.43,
                        "servicer": "CITI"
                    },
                    {
                        "percent": 0.39,
                        "servicer": "GUILD"
                    },
                    {
                        "percent": 0.21,
                        "servicer": "CNTRL"
                    },
                    {
                        "percent": 0.21,
                        "servicer": "REGNS"
                    },
                    {
                        "percent": 0.09,
                        "servicer": "COLNL"
                    },
                    {
                        "percent": 0.06,
                        "servicer": "HFAGY"
                    },
                    {
                        "percent": 0.06,
                        "servicer": "MNSRC"
                    }
                ],
                "nonWeightedOriginalLoanSize": 0.0,
                "original3rdPartyOrigination": 0.0,
                "percentHARPDec2010Extension": 0.0,
                "percentHARPOneYearExtension": 0.0,
                "percentDownPaymentAssistance": 5.6,
                "percentAmortizedFHALTVUnder78": 95.4,
                "loanPerformanceImpliedCurrentLTV": 43.6,
                "reperformerMonthsForReperformers": 28
            },
            "ticker": "GNMA",
            "country": "US",
            "currency": "USD",
            "identifier": "999818YT",
            "description": "30-YR GNMA-2013 PROD",
            "issuerTicker": "GNMA",
            "maturityDate": "2041-12-01",
            "securityType": "MORT",
            "currentCoupon": 3.5,
            "securitySubType": "MPGNMA"
        },
        "meta": {
            "status": "DONE",
            "requestId": "R-150600",
            "timeStamp": "2025-12-03T07:42:57Z",
            "responseType": "BOND_INDIC"
        }
    }


    >>> # Request bond indic with sync get
    >>> response = request_bond_indic_sync_get(
    >>>                                     id="01F002628",
    >>>                                     id_type=IdTypeEnum.CUSIP,
    >>>                                     keywords=["keyword1", "keyword2"],
    >>>                                     job="JobName",
    >>>                                     name="Name",
    >>>                                     pri=0,
    >>>                                     tags=["tag1", "tag2"]
    >>>                                     )
    >>>
    >>> # Print results in json format
    >>> print(js.dumps(response, indent=4))
    {
        "data": {
            "cusip": "01F002628",
            "indic": {},
            "ticker": "FNMA",
            "country": "US",
            "currency": "USD",
            "identifier": "01F00262",
            "description": "30-YR UMBS-TBA PROD FEB",
            "issuerTicker": "UMBS",
            "maturityDate": "2054-01-01",
            "securityType": "MORT",
            "currentCoupon": 0.5,
            "securitySubType": "FNTBA"
        },
        "meta": {
            "status": "DONE",
            "requestId": "R-150601",
            "timeStamp": "2025-12-03T07:42:58Z",
            "responseType": "BOND_INDIC"
        }
    }

    """

    try:
        logger.info("Calling request_bond_indic_sync_get")

        response = Client().yield_book_rest.request_bond_indic_sync_get(
            id=id,
            id_type=id_type,
            keywords=keywords,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_bond_indic_sync_get")

        return output
    except Exception as err:
        logger.error("Error request_bond_indic_sync_get.")
        check_exception_and_raise(err, logger)


def request_bond_search_async_get(
    *,
    id: str,
    include_matured_bonds: Optional[bool] = None,
    include_muni: Optional[bool] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """


    Parameters
    ----------
    id : str
        Security reference ID.
    include_matured_bonds : bool, optional
        Boolean with `true` and `false` values.
    include_muni : bool, optional
        Boolean with `true` and `false` values.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_bond_search_async_get")

        response = Client().yield_book_rest.request_bond_search_async_get(
            id=id,
            include_matured_bonds=include_matured_bonds,
            include_muni=include_muni,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_bond_search_async_get")

        return output
    except Exception as err:
        logger.error("Error request_bond_search_async_get.")
        check_exception_and_raise(err, logger)


def request_bond_search_async_post(
    *,
    identifier: Optional[str] = None,
    include_matured_bonds: Optional[bool] = None,
    include_muni: Optional[bool] = None,
    search_criteria: Optional[List[BondSearchCriteria]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """


    Parameters
    ----------
    identifier : str, optional
        Security reference ID.
    include_matured_bonds : bool, optional
        Optional, if true, the search will also include called and matured securities. This can increase search times.
    include_muni : bool, optional
        Optional, if true, the search will also include municipal bonds. This can increase search times.
    search_criteria : List[BondSearchCriteria], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_bond_search_async_post")

        response = Client().yield_book_rest.request_bond_search_async_post(
            body=BondSearchRequest(
                identifier=identifier,
                include_matured_bonds=include_matured_bonds,
                include_muni=include_muni,
                search_criteria=search_criteria,
            ),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_bond_search_async_post")

        return output
    except Exception as err:
        logger.error("Error request_bond_search_async_post.")
        check_exception_and_raise(err, logger)


def request_bond_search_sync_get(
    *,
    id: str,
    include_matured_bonds: Optional[bool] = None,
    include_muni: Optional[bool] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """


    Parameters
    ----------
    id : str
        Security reference ID.
    include_matured_bonds : bool, optional
        Boolean with `true` and `false` values.
    include_muni : bool, optional
        Boolean with `true` and `false` values.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_bond_search_sync_get")

        response = Client().yield_book_rest.request_bond_search_sync_get(
            id=id,
            include_matured_bonds=include_matured_bonds,
            include_muni=include_muni,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_bond_search_sync_get")

        return output
    except Exception as err:
        logger.error("Error request_bond_search_sync_get.")
        check_exception_and_raise(err, logger)


def request_bond_search_sync_post(
    *,
    identifier: Optional[str] = None,
    include_matured_bonds: Optional[bool] = None,
    include_muni: Optional[bool] = None,
    search_criteria: Optional[List[BondSearchCriteria]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """


    Parameters
    ----------
    identifier : str, optional
        Security reference ID.
    include_matured_bonds : bool, optional
        Optional, if true, the search will also include called and matured securities. This can increase search times.
    include_muni : bool, optional
        Optional, if true, the search will also include municipal bonds. This can increase search times.
    search_criteria : List[BondSearchCriteria], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_bond_search_sync_post")

        response = Client().yield_book_rest.request_bond_search_sync_post(
            body=BondSearchRequest(
                identifier=identifier,
                include_matured_bonds=include_matured_bonds,
                include_muni=include_muni,
                search_criteria=search_criteria,
            ),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_bond_search_sync_post")

        return output
    except Exception as err:
        logger.error("Error request_bond_search_sync_post.")
        check_exception_and_raise(err, logger)


def request_collateral_details_async(
    *,
    input: Optional[List[CollateralDetailsRequestInfo]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """


    Parameters
    ----------
    input : List[CollateralDetailsRequestInfo], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_collateral_details_async")

        response = Client().yield_book_rest.request_collateral_details_async(
            body=CollateralDetailsRequest(input=input),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_collateral_details_async")

        return output
    except Exception as err:
        logger.error("Error request_collateral_details_async.")
        check_exception_and_raise(err, logger)


def request_collateral_details_async_get(
    *,
    id: str,
    id_type: Optional[str] = None,
    user_tag: Optional[str] = None,
    data_items: Optional[List[Union[str, DataItems]]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """


    Parameters
    ----------
    id : str
        Security reference ID.
    id_type : str, optional
        A sequence of textual characters.
    user_tag : str, optional
        A sequence of textual characters.
    data_items : List[Union[str, DataItems]], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_collateral_details_async_get")

        response = Client().yield_book_rest.request_collateral_details_async_get(
            id=id,
            id_type=id_type,
            user_tag=user_tag,
            data_items=data_items,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_collateral_details_async_get")

        return output
    except Exception as err:
        logger.error("Error request_collateral_details_async_get.")
        check_exception_and_raise(err, logger)


def request_collateral_details_sync(
    *,
    input: Optional[List[CollateralDetailsRequestInfo]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """


    Parameters
    ----------
    input : List[CollateralDetailsRequestInfo], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_collateral_details_sync")

        response = Client().yield_book_rest.request_collateral_details_sync(
            body=CollateralDetailsRequest(input=input),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_collateral_details_sync")

        return output
    except Exception as err:
        logger.error("Error request_collateral_details_sync.")
        check_exception_and_raise(err, logger)


def request_collateral_details_sync_get(
    *,
    id: str,
    id_type: Optional[str] = None,
    user_tag: Optional[str] = None,
    data_items: Optional[List[Union[str, DataItems]]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """


    Parameters
    ----------
    id : str
        Security reference ID.
    id_type : str, optional
        A sequence of textual characters.
    user_tag : str, optional
        A sequence of textual characters.
    data_items : List[Union[str, DataItems]], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_collateral_details_sync_get")

        response = Client().yield_book_rest.request_collateral_details_sync_get(
            id=id,
            id_type=id_type,
            user_tag=user_tag,
            data_items=data_items,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_collateral_details_sync_get")

        return output
    except Exception as err:
        logger.error("Error request_collateral_details_sync_get.")
        check_exception_and_raise(err, logger)


def request_curve_async(
    *,
    date: Union[str, datetime.date],
    currency: str,
    curve_type: Union[str, YbRestCurveType],
    cds_ticker: Optional[str] = None,
    expand_curve: Optional[bool] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Request curve async.

    Parameters
    ----------
    date : Union[str, datetime.date]
        A date on a calendar without a time zone, e.g. "April 10th"
    currency : str
        A sequence of textual characters.
    curve_type : Union[str, YbRestCurveType]

    cds_ticker : str, optional
        A sequence of textual characters.
    expand_curve : bool, optional
        Boolean with `true` and `false` values.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_curve_async")

        response = Client().yield_book_rest.request_curve_async(
            date=date,
            currency=currency,
            curve_type=curve_type,
            cds_ticker=cds_ticker,
            expand_curve=expand_curve,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_curve_async")

        return output
    except Exception as err:
        logger.error("Error request_curve_async.")
        check_exception_and_raise(err, logger)


def request_curve_sync(
    *,
    date: Union[str, datetime.date],
    currency: str,
    curve_type: Union[str, YbRestCurveType],
    cds_ticker: Optional[str] = None,
    expand_curve: Optional[bool] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Request curve sync.

    Parameters
    ----------
    date : Union[str, datetime.date]
        A date on a calendar without a time zone, e.g. "April 10th"
    currency : str
        A sequence of textual characters.
    curve_type : Union[str, YbRestCurveType]

    cds_ticker : str, optional
        A sequence of textual characters.
    expand_curve : bool, optional
        Boolean with `true` and `false` values.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_curve_sync")

        response = Client().yield_book_rest.request_curve_sync(
            date=date,
            currency=currency,
            curve_type=curve_type,
            cds_ticker=cds_ticker,
            expand_curve=expand_curve,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_curve_sync")

        return output
    except Exception as err:
        logger.error("Error request_curve_sync.")
        check_exception_and_raise(err, logger)


def request_curves_async(
    *,
    curves: Optional[List[CurveSearch]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Request curves async.

    Parameters
    ----------
    curves : List[CurveSearch], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_curves_async")

        response = Client().yield_book_rest.request_curves_async(
            body=CurveDetailsRequest(curves=curves),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
            content_type="application/json",
        )

        output = response
        logger.info("Called request_curves_async")

        return output
    except Exception as err:
        logger.error("Error request_curves_async.")
        check_exception_and_raise(err, logger)


def request_curves_sync(
    *,
    curves: Optional[List[CurveSearch]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Request curves sync.

    Parameters
    ----------
    curves : List[CurveSearch], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_curves_sync")

        response = Client().yield_book_rest.request_curves_sync(
            body=CurveDetailsRequest(curves=curves),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
            content_type="application/json",
        )

        output = response
        logger.info("Called request_curves_sync")

        return output
    except Exception as err:
        logger.error("Error request_curves_sync.")
        check_exception_and_raise(err, logger)


def request_get_scen_calc_sys_scen_async(
    *,
    id: str,
    level: str,
    pricing_date: str,
    curve_type: Union[str, YbRestCurveType],
    h_py_method: str,
    scenario: str,
    id_type: Optional[str] = None,
    h_days: Optional[int] = None,
    h_months: Optional[int] = None,
    currency: Optional[str] = None,
    volatility: Optional[str] = None,
    prepay_type: Optional[str] = None,
    prepay_rate: Optional[float] = None,
    h_level: Optional[str] = None,
    h_prepay_rate: Optional[float] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Request get scenario calculation system scenario async.

    Parameters
    ----------
    id : str
        Security reference ID.
    id_type : str, optional
        A sequence of textual characters.
    level : str
        A sequence of textual characters.
    pricing_date : str
        A sequence of textual characters.
    h_days : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    h_months : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    curve_type : Union[str, YbRestCurveType]

    currency : str, optional
        A sequence of textual characters.
    volatility : str, optional
        A sequence of textual characters.
    prepay_type : str, optional
        A sequence of textual characters.
    prepay_rate : float, optional
        A 64 bit floating point number. (`±5.0 × 10^−324` to `±1.7 × 10^308`)
    h_level : str, optional
        A sequence of textual characters.
    h_py_method : str
        A sequence of textual characters.
    h_prepay_rate : float, optional
        A 64 bit floating point number. (`±5.0 × 10^−324` to `±1.7 × 10^308`)
    scenario : str
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------
    >>> # Formulate and execute the get request by using instrument ID, Par_amount and job in which the calculation will be done
    >>> sa_async_get_response = request_get_scen_calc_sys_scen_async(
    >>>             id='US742718AV11',
    >>>             scenario="/sys/scenario/Par/50",
    >>>             pricing_date="2025-01-01",
    >>>             curve_type="GVT",
    >>>             h_py_method="OAS",
    >>>             level="100"
    >>>         )
    >>>
    >>> async_get_results_response = {}
    >>>
    >>> attempt = 1
    >>>
    >>> while attempt < 10:
    >>>
    >>>     from lseg_analytics.core.exceptions import ServerError
    >>>     try:
    >>>         time.sleep(10)
    >>>         # Request bond indic with async post
    >>>         async_get_results_response = get_result(request_id_parameter=sa_async_get_response.request_id)
    >>>         break
    >>>     except Exception as err:
    >>>         print(f"Attempt " + str(
    >>>             attempt) + " resulted in error retrieving results from:" + sa_async_get_response.request_id)
    >>>         if (isinstance(err, ServerError)
    >>>                 and f"The result is not ready yet for requestID:{sa_async_get_response.request_id}" in str(err)):
    >>>
    >>>             attempt += 1
    >>>         else:
    >>>             raise err
    >>>
    >>> print(js.dumps(async_get_results_response, indent=4))
    {
        "data": {
            "isin": "US742718AV11",
            "cusip": "742718AV1",
            "ticker": "PG",
            "scenario": {
                "horizon": [
                    {
                        "oas": 361.951,
                        "wal": 4.8139,
                        "price": 98.053324,
                        "yield": 8.4961,
                        "balance": 1.0,
                        "duration": 3.8584,
                        "fullPrice": 99.542213,
                        "returnCode": 0,
                        "scenarioID": "/sys/scenario/Par/50",
                        "spreadDV01": 0.0,
                        "volatility": 16.0,
                        "actualPrice": 98.053,
                        "grossSpread": 361.3423,
                        "horizonDays": 0,
                        "marketValue": 99.542213,
                        "optionValue": 0.0,
                        "totalReturn": -1.91811763,
                        "dollarReturn": -1.94667627,
                        "convexityCost": 0.0,
                        "nominalSpread": 361.3423,
                        "effectiveYield": 0.0,
                        "interestReturn": 0.0,
                        "settlementDate": "2025-01-03",
                        "spreadDuration": 0.0,
                        "accruedInterest": 1.488889,
                        "actualFullPrice": 99.542,
                        "horizonPYMethod": "OAS",
                        "interestPayment": 0.0,
                        "principalReturn": -1.91811763,
                        "underlyingPrice": 0.0,
                        "principalPayment": 0.0,
                        "reinvestmentRate": 4.829956,
                        "yieldCurveMargin": 361.951,
                        "effectiveCallDate": "0",
                        "reinvestmentAmount": 0.0,
                        "actualAccruedInterest": 1.489
                    }
                ],
                "settlement": {
                    "oas": 361.951,
                    "psa": 0.0,
                    "wal": 4.8139,
                    "price": 100.0,
                    "yield": 7.9953,
                    "fullPrice": 101.488889,
                    "volatility": 13.0,
                    "grossSpread": 361.2649,
                    "optionValue": 0.0,
                    "pricingDate": "2024-12-31",
                    "forwardYield": 0.0,
                    "staticSpread": 0.0,
                    "effectiveDV01": 0.039405887,
                    "nominalSpread": 0.0,
                    "settlementDate": "2025-01-03",
                    "accruedInterest": 1.488889,
                    "reinvestmentRate": 4.329956,
                    "yieldCurveMargin": 0.0,
                    "effectiveDuration": 3.8828,
                    "effectiveConvexity": 0.1873
                }
            },
            "returnCode": 0,
            "securityID": "742718AV",
            "description": "PROCTER & GAMBLE CO",
            "maturityDate": "2029-10-26",
            "securityType": "BOND",
            "currentCoupon": 8.0
        },
        "meta": {
            "status": "DONE",
            "requestId": "R-21319",
            "timeStamp": "2025-08-19T02:16:32Z",
            "responseType": "SCENARIO_CALC"
        }
    }

    """

    try:
        logger.info("Calling request_get_scen_calc_sys_scen_async")

        response = Client().yield_book_rest.request_get_scen_calc_sys_scen_async(
            id=id,
            id_type=id_type,
            level=level,
            pricing_date=pricing_date,
            h_days=h_days,
            h_months=h_months,
            curve_type=curve_type,
            currency=currency,
            volatility=volatility,
            prepay_type=prepay_type,
            prepay_rate=prepay_rate,
            h_level=h_level,
            h_py_method=h_py_method,
            h_prepay_rate=h_prepay_rate,
            scenario=scenario,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_get_scen_calc_sys_scen_async")

        return output
    except Exception as err:
        logger.error("Error request_get_scen_calc_sys_scen_async.")
        check_exception_and_raise(err, logger)


def request_get_scen_calc_sys_scen_sync(
    *,
    id: str,
    level: str,
    pricing_date: str,
    curve_type: Union[str, YbRestCurveType],
    h_py_method: str,
    scenario: str,
    id_type: Optional[str] = None,
    h_days: Optional[int] = None,
    h_months: Optional[int] = None,
    currency: Optional[str] = None,
    volatility: Optional[str] = None,
    prepay_type: Optional[str] = None,
    prepay_rate: Optional[float] = None,
    h_level: Optional[str] = None,
    h_prepay_rate: Optional[float] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Request get scenario calculation system scenario sync.

    Parameters
    ----------
    id : str
        Security reference ID.
    id_type : str, optional
        A sequence of textual characters.
    level : str
        A sequence of textual characters.
    pricing_date : str
        A sequence of textual characters.
    h_days : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    h_months : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    curve_type : Union[str, YbRestCurveType]

    currency : str, optional
        A sequence of textual characters.
    volatility : str, optional
        A sequence of textual characters.
    prepay_type : str, optional
        A sequence of textual characters.
    prepay_rate : float, optional
        A 64 bit floating point number. (`±5.0 × 10^−324` to `±1.7 × 10^308`)
    h_level : str, optional
        A sequence of textual characters.
    h_py_method : str
        A sequence of textual characters.
    h_prepay_rate : float, optional
        A 64 bit floating point number. (`±5.0 × 10^−324` to `±1.7 × 10^308`)
    scenario : str
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------
    >>> sa_sync_get_response = request_get_scen_calc_sys_scen_sync(
    >>>             id='US742718AV11',
    >>>             level="100",
    >>>             scenario="/sys/scenario/Par/50",
    >>>             curve_type="GVT",
    >>>             pricing_date="2025-01-01",
    >>>             h_py_method="OAS",
    >>>         )
    >>>
    >>> print(js.dumps(sa_sync_get_response, indent=4))
    {
        "data": {
            "isin": "US742718AV11",
            "cusip": "742718AV1",
            "ticker": "PG",
            "scenario": {
                "horizon": [
                    {
                        "oas": 361.951,
                        "wal": 4.8139,
                        "price": 98.053324,
                        "yield": 8.4961,
                        "balance": 1.0,
                        "duration": 3.8584,
                        "fullPrice": 99.542213,
                        "returnCode": 0,
                        "scenarioID": "/sys/scenario/Par/50",
                        "spreadDV01": 0.0,
                        "volatility": 16.0,
                        "actualPrice": 98.053,
                        "grossSpread": 361.3423,
                        "horizonDays": 0,
                        "marketValue": 99.542213,
                        "optionValue": 0.0,
                        "totalReturn": -1.91811763,
                        "dollarReturn": -1.94667627,
                        "convexityCost": 0.0,
                        "nominalSpread": 361.3423,
                        "effectiveYield": 0.0,
                        "interestReturn": 0.0,
                        "settlementDate": "2025-01-03",
                        "spreadDuration": 0.0,
                        "accruedInterest": 1.488889,
                        "actualFullPrice": 99.542,
                        "horizonPYMethod": "OAS",
                        "interestPayment": 0.0,
                        "principalReturn": -1.91811763,
                        "underlyingPrice": 0.0,
                        "principalPayment": 0.0,
                        "reinvestmentRate": 4.829956,
                        "yieldCurveMargin": 361.951,
                        "effectiveCallDate": "0",
                        "reinvestmentAmount": 0.0,
                        "actualAccruedInterest": 1.489
                    }
                ],
                "settlement": {
                    "oas": 361.951,
                    "psa": 0.0,
                    "wal": 4.8139,
                    "price": 100.0,
                    "yield": 7.9953,
                    "fullPrice": 101.488889,
                    "volatility": 13.0,
                    "grossSpread": 361.2649,
                    "optionValue": 0.0,
                    "pricingDate": "2024-12-31",
                    "forwardYield": 0.0,
                    "staticSpread": 0.0,
                    "effectiveDV01": 0.039405887,
                    "nominalSpread": 0.0,
                    "settlementDate": "2025-01-03",
                    "accruedInterest": 1.488889,
                    "reinvestmentRate": 4.329956,
                    "yieldCurveMargin": 0.0,
                    "effectiveDuration": 3.8828,
                    "effectiveConvexity": 0.1873
                }
            },
            "returnCode": 0,
            "securityID": "742718AV",
            "description": "PROCTER & GAMBLE CO",
            "maturityDate": "2029-10-26",
            "securityType": "BOND",
            "currentCoupon": 8.0
        },
        "meta": {
            "status": "DONE",
            "requestId": "R-150608",
            "timeStamp": "2025-12-03T07:43:05Z",
            "responseType": "SCENARIO_CALC"
        }
    }

    """

    try:
        logger.info("Calling request_get_scen_calc_sys_scen_sync")

        response = Client().yield_book_rest.request_get_scen_calc_sys_scen_sync(
            id=id,
            id_type=id_type,
            level=level,
            pricing_date=pricing_date,
            h_days=h_days,
            h_months=h_months,
            curve_type=curve_type,
            currency=currency,
            volatility=volatility,
            prepay_type=prepay_type,
            prepay_rate=prepay_rate,
            h_level=h_level,
            h_py_method=h_py_method,
            h_prepay_rate=h_prepay_rate,
            scenario=scenario,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_get_scen_calc_sys_scen_sync")

        return output
    except Exception as err:
        logger.error("Error request_get_scen_calc_sys_scen_sync.")
        check_exception_and_raise(err, logger)


def request_historical_data_async(
    *,
    id: str,
    id_type: Optional[str] = None,
    keyword: Optional[List[str]] = None,
    start_date: Optional[Union[str, datetime.date]] = None,
    end_date: Optional[Union[str, datetime.date]] = None,
    frequency: Optional[Union[str, YbRestFrequency]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Request Historical Data async by Security reference ID.

    Parameters
    ----------
    id : str
        Security reference ID.
    id_type : str, optional
        A sequence of textual characters.
    keyword : List[str], optional

    start_date : Union[str, datetime.date], optional
        A date on a calendar without a time zone, e.g. "April 10th"
    end_date : Union[str, datetime.date], optional
        A date on a calendar without a time zone, e.g. "April 10th"
    frequency : Union[str, YbRestFrequency], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_historical_data_async")

        response = Client().yield_book_rest.request_historical_data_async(
            id=id,
            id_type=id_type,
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_historical_data_async")

        return output
    except Exception as err:
        logger.error("Error request_historical_data_async.")
        check_exception_and_raise(err, logger)


def request_historical_data_sync(
    *,
    id: str,
    id_type: Optional[str] = None,
    keyword: Optional[List[str]] = None,
    start_date: Optional[Union[str, datetime.date]] = None,
    end_date: Optional[Union[str, datetime.date]] = None,
    frequency: Optional[Union[str, YbRestFrequency]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Request Historical Data sync by Security reference ID.

    Parameters
    ----------
    id : str
        Security reference ID.
    id_type : str, optional
        A sequence of textual characters.
    keyword : List[str], optional

    start_date : Union[str, datetime.date], optional
        A date on a calendar without a time zone, e.g. "April 10th"
    end_date : Union[str, datetime.date], optional
        A date on a calendar without a time zone, e.g. "April 10th"
    frequency : Union[str, YbRestFrequency], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_historical_data_sync")

        response = Client().yield_book_rest.request_historical_data_sync(
            id=id,
            id_type=id_type,
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_historical_data_sync")

        return output
    except Exception as err:
        logger.error("Error request_historical_data_sync.")
        check_exception_and_raise(err, logger)


def request_index_catalogue_info_async(
    *,
    provider: str,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """


    Parameters
    ----------
    provider : str
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_index_catalogue_info_async")

        response = Client().yield_book_rest.request_index_catalogue_info_async(
            provider=provider, job=job, name=name, pri=pri, tags=tags
        )

        output = response
        logger.info("Called request_index_catalogue_info_async")

        return output
    except Exception as err:
        logger.error("Error request_index_catalogue_info_async.")
        check_exception_and_raise(err, logger)


def request_index_catalogue_info_sync(
    *,
    provider: str,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """


    Parameters
    ----------
    provider : str
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_index_catalogue_info_sync")

        response = Client().yield_book_rest.request_index_catalogue_info_sync(
            provider=provider, job=job, name=name, pri=pri, tags=tags
        )

        output = response
        logger.info("Called request_index_catalogue_info_sync")

        return output
    except Exception as err:
        logger.error("Error request_index_catalogue_info_sync.")
        check_exception_and_raise(err, logger)


def request_index_data_by_ticker_async(
    *,
    ticker: str,
    asof_date: Union[str, datetime.date],
    pricing_date: Optional[Union[str, datetime.date]] = None,
    base_currency: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """


    Parameters
    ----------
    ticker : str
        A sequence of textual characters.
    asof_date : Union[str, datetime.date]
        A date on a calendar without a time zone, e.g. "April 10th"
    pricing_date : Union[str, datetime.date], optional
        A date on a calendar without a time zone, e.g. "April 10th"
    base_currency : str, optional
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_index_data_by_ticker_async")

        response = Client().yield_book_rest.request_index_data_by_ticker_async(
            ticker=ticker,
            asof_date=asof_date,
            pricing_date=pricing_date,
            base_currency=base_currency,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_index_data_by_ticker_async")

        return output
    except Exception as err:
        logger.error("Error request_index_data_by_ticker_async.")
        check_exception_and_raise(err, logger)


def request_index_data_by_ticker_sync(
    *,
    ticker: str,
    asof_date: Union[str, datetime.date],
    pricing_date: Optional[Union[str, datetime.date]] = None,
    base_currency: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """


    Parameters
    ----------
    ticker : str
        A sequence of textual characters.
    asof_date : Union[str, datetime.date]
        A date on a calendar without a time zone, e.g. "April 10th"
    pricing_date : Union[str, datetime.date], optional
        A date on a calendar without a time zone, e.g. "April 10th"
    base_currency : str, optional
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_index_data_by_ticker_sync")

        response = Client().yield_book_rest.request_index_data_by_ticker_sync(
            ticker=ticker,
            asof_date=asof_date,
            pricing_date=pricing_date,
            base_currency=base_currency,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_index_data_by_ticker_sync")

        return output
    except Exception as err:
        logger.error("Error request_index_data_by_ticker_sync.")
        check_exception_and_raise(err, logger)


def request_index_providers_async(
    *,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """


    Parameters
    ----------
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_index_providers_async")

        response = Client().yield_book_rest.request_index_providers_async(job=job, name=name, pri=pri, tags=tags)

        output = response
        logger.info("Called request_index_providers_async")

        return output
    except Exception as err:
        logger.error("Error request_index_providers_async.")
        check_exception_and_raise(err, logger)


def request_index_providers_sync(
    *,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """


    Parameters
    ----------
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_index_providers_sync")

        response = Client().yield_book_rest.request_index_providers_sync(job=job, name=name, pri=pri, tags=tags)

        output = response
        logger.info("Called request_index_providers_sync")

        return output
    except Exception as err:
        logger.error("Error request_index_providers_sync.")
        check_exception_and_raise(err, logger)


def request_mbs_history_async(
    *,
    id: str,
    id_type: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """


    Parameters
    ----------
    id : str
        Security reference ID.
    id_type : str, optional
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_mbs_history_async")

        response = Client().yield_book_rest.request_mbs_history_async(
            id=id, id_type=id_type, job=job, name=name, pri=pri, tags=tags
        )

        output = response
        logger.info("Called request_mbs_history_async")

        return output
    except Exception as err:
        logger.error("Error request_mbs_history_async.")
        check_exception_and_raise(err, logger)


def request_mbs_history_sync(
    *,
    id: str,
    id_type: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """


    Parameters
    ----------
    id : str
        Security reference ID.
    id_type : str, optional
        A sequence of textual characters.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_mbs_history_sync")

        response = Client().yield_book_rest.request_mbs_history_sync(
            id=id, id_type=id_type, job=job, name=name, pri=pri, tags=tags
        )

        output = response
        logger.info("Called request_mbs_history_sync")

        return output
    except Exception as err:
        logger.error("Error request_mbs_history_sync.")
        check_exception_and_raise(err, logger)


def request_mortgage_model_async(
    *,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """


    Parameters
    ----------
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_mortgage_model_async")

        response = Client().yield_book_rest.request_mortgage_model_async(job=job, name=name, pri=pri, tags=tags)

        output = response
        logger.info("Called request_mortgage_model_async")

        return output
    except Exception as err:
        logger.error("Error request_mortgage_model_async.")
        check_exception_and_raise(err, logger)


def request_mortgage_model_sync(
    *,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """


    Parameters
    ----------
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_mortgage_model_sync")

        response = Client().yield_book_rest.request_mortgage_model_sync(job=job, name=name, pri=pri, tags=tags)

        output = response
        logger.info("Called request_mortgage_model_sync")

        return output
    except Exception as err:
        logger.error("Error request_mortgage_model_sync.")
        check_exception_and_raise(err, logger)


def request_py_calculation_async(
    *,
    global_settings: Optional[PyCalcGlobalSettings] = None,
    input: Optional[List[PyCalcInput]] = None,
    keywords: Optional[List[str]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Request PY calculation async.

    Parameters
    ----------
    global_settings : PyCalcGlobalSettings, optional

    input : List[PyCalcInput], optional

    keywords : List[str], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------
    >>> # request_py_calculation_sync
    >>> global_settings = PyCalcGlobalSettings(
    >>>             pricing_date=date(2025, 1, 17),
    >>>         )
    >>>
    >>> input = [
    >>>             PyCalcInput(
    >>>                 identifier="29874QEL",
    >>>                 level="100",
    >>>                 curve=CurveTypeAndCurrency(
    >>>                     curve_type="GVT",
    >>>                     currency="USD"
    >>>                 )
    >>>             )
    >>>         ]
    >>>
    >>> py_async_post_response = request_py_calculation_async(
    >>>             global_settings=global_settings,
    >>>             input=input,
    >>>         )
    >>>
    >>> # provide a window of time for job to finish
    >>> time.sleep(10)
    >>>
    >>> py_async_post_result = get_result(request_id_parameter=py_async_post_response.request_id)
    >>>
    >>> print(js.dumps(py_async_post_result, indent=4))
    {
        "meta": {
            "status": "DONE",
            "requestId": "R-20906",
            "timeStamp": "2025-08-18T22:36:37Z",
            "responseType": "PY_CALC",
            "resultsStatus": "ALL"
        },
        "results": [
            {
                "py": {
                    "oas": -373.0749,
                    "wal": 0.841096,
                    "dv01": 0.00838988,
                    "isin": "US29874QEL41",
                    "cusip": "29874QEL4",
                    "price": 100.0,
                    "yield": 0.499919,
                    "ticker": "EBRD",
                    "cSpread": 7.672,
                    "cdYield": 0.493835,
                    "pyLevel": "100",
                    "zSpread": -373.074889,
                    "duration": 0.838324,
                    "recovery": 37.4,
                    "ziSpread": -374.496164,
                    "znSpread": -378.43626,
                    "assetSwap": -395.112,
                    "benchmark": "US 3.875 07/27",
                    "convexity": 0.0112,
                    "curveDate": "2025-01-17",
                    "curveType": "Govt",
                    "fullPrice": 100.07916667,
                    "securityID": "29874QEL",
                    "spreadDV01": 0.008389905,
                    "tsyCurveID": "USDp0117",
                    "volatility": 13.0,
                    "accruedDays": 57,
                    "description": "EUROPEAN BANK FOR RECON AND DEV",
                    "grossSpread": -374.4927,
                    "optionValue": 0.0,
                    "pricingDate": "2025-01-17",
                    "swapCurveID": "SUSp117Q2",
                    "currentYield": 0.5,
                    "effectiveWAL": 0.8417,
                    "maturityDate": "2025-11-25",
                    "securityType": "BOND",
                    "volModelType": "Single",
                    "yieldToWorst": 0.499919,
                    "convexityCost": 0.0,
                    "currentCoupon": 0.5,
                    "discountYield": 0.0,
                    "effectiveCV01": 0.000112198,
                    "effectiveDV01": 0.008388666,
                    "worstCallDate": "2025-11-25",
                    "cdsAdjustedOAS": -380.657,
                    "effectiveYield": 0.496,
                    "marketSettings": {
                        "settlementDate": "2025-01-22"
                    },
                    "settlementDate": "2025-01-22",
                    "spreadDuration": 0.838327,
                    "walToWorstCall": 0.841096,
                    "zSpreadToWorst": -378.436,
                    "accruedInterest": 0.07916667,
                    "annualizedYield": 0.501,
                    "assetSwapSpread": -371.247,
                    "cdsImpliedPrice": 96.879,
                    "compoundingFreq": 2,
                    "convexityEffect": 0.0,
                    "dv01ToWorstCall": 0.00839,
                    "spreadConvexity": 0.011,
                    "yearsToMaturity": 0.8411,
                    "ziWorstCallDate": "2025-11-25",
                    "znWorstCallDate": "2025-11-25",
                    "assetSwapToLibor": {
                        "type": "PAR",
                        "value": -395.1121
                    },
                    "cdsAdjustedYield": 0.424,
                    "economicExposure": 100.079167,
                    "macaulayDuration": 0.8404,
                    "spreadToActCurve": -373.3523,
                    "spreadToNextCall": -374.4927,
                    "spreadToTsyCurve": -374.5047,
                    "yearsToWorstCall": 0.842,
                    "yieldCurveMargin": -373.0749,
                    "yieldToWorstCall": 0.499919,
                    "effectiveDuration": 0.838203073,
                    "macaulayConvexity": 0.7069,
                    "spreadToBenchmark": -377.2128,
                    "spreadToSwapCurve": -400.5193,
                    "spreadToWorstCall": -374,
                    "effectiveConvexity": 0.011210883,
                    "ffndSpreadDuration": 0.0,
                    "optionModelCurveID": "USDp0117",
                    "yieldCurveDuration": 0.8382,
                    "durationToWorstCall": 0.8383,
                    "durationToWorstCase": 0.838324,
                    "indexSpreadDuration": 0.0,
                    "semiAnnualizedYield": 0.499919,
                    "ziSpreadToWorstCall": -374.496,
                    "znSpreadToWorstCall": -378.436,
                    "benchmarkToWorstCall": "US 3.875 07/27",
                    "spreadToRFRSwapCurve": -371.6566,
                    "yearsToFinalMaturity": 0.842,
                    "gnmafnmaSpreadDuration": 0.0,
                    "spreadDurationTreasury": 0.838327,
                    "fundedEffectiveDuration": 0.838203,
                    "effectiveDurationPriceUp": 99.8698,
                    "fundedEffectiveConvexity": 0.011211,
                    "effectiveDurationPriceDown": 100.289234,
                    "spreadToActCurveToWorstCall": -373.3523,
                    "currentCouponSpreadConvexity": 0.0,
                    "spreadToBenchmarkToWorstCall": -377.2128,
                    "currentCouponSpreadSensitivity": 0.0,
                    "spreadToTsyCurveAtBenchmarkTenor": -371.1762
                },
                "securityID": "29874QEL"
            }
        ]
    }

    """

    try:
        logger.info("Calling request_py_calculation_async")

        response = Client().yield_book_rest.request_py_calculation_async(
            body=PyCalcRequest(global_settings=global_settings, input=input, keywords=keywords),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
            content_type="application/json",
        )

        output = response
        logger.info("Called request_py_calculation_async")

        return output
    except Exception as err:
        logger.error("Error request_py_calculation_async.")
        check_exception_and_raise(err, logger)


def request_py_calculation_async_by_id(
    *,
    id: str,
    level: str,
    curve_type: Union[str, YbRestCurveType],
    id_type: Optional[str] = None,
    pricing_date: Optional[Union[str, datetime.date]] = None,
    currency: Optional[str] = None,
    prepay_type: Optional[str] = None,
    prepay_rate: Optional[float] = None,
    option_model: Optional[Union[str, OptionModel]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Request PY calculation async by ID.

    Parameters
    ----------
    id : str
        A sequence of textual characters.
    id_type : str, optional
        A sequence of textual characters.
    level : str
        A sequence of textual characters.
    pricing_date : Union[str, datetime.date], optional
        A date on a calendar without a time zone, e.g. "April 10th"
    curve_type : Union[str, YbRestCurveType]

    currency : str, optional
        A sequence of textual characters.
    prepay_type : str, optional
        A sequence of textual characters.
    prepay_rate : float, optional
        A 64 bit floating point number. (`±5.0 × 10^−324` to `±1.7 × 10^308`)
    option_model : Union[str, OptionModel], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------
    >>> # request_py_calculation_sync_by_id
    >>> py_async_get_response = request_py_calculation_async_by_id(
    >>>             id="01F002628",
    >>>             level="100",
    >>>             curve_type="GVT"
    >>>         )
    >>>
    >>> # provide a window of time for job to finish
    >>> time.sleep(10)
    >>>
    >>> py_async_get_result = get_result(request_id_parameter=py_async_get_response.request_id)
    >>>
    >>> print(js.dumps(py_async_get_result, indent=4))
    {
        "data": {
            "py": {
                "ltv": 67.0,
                "oas": -435.6297,
                "wal": 10.098174,
                "dv01": 0.097250231,
                "cusip": "01F002628",
                "price": 100.0,
                "yield": 0.497093,
                "ticker": "FNMA",
                "cmmType": 100,
                "pyLevel": "100",
                "zSpread": -416.336945,
                "duration": 9.723537,
                "loanSize": 290000.0,
                "modelLTV": 51.6,
                "ziSpread": -416.336945,
                "znSpread": -353.877594,
                "benchmark": "10 yr",
                "convexity": 1.4255,
                "curveDate": "2025-08-15",
                "curveType": "Govt",
                "fullPrice": 100.01527778,
                "modelCode": 2501,
                "prepayRate": 100.0,
                "prepayType": "VEC",
                "securityID": "01F00262",
                "spreadDV01": 0.100176565,
                "tsyCurveID": "USDp0815",
                "accruedDays": 11,
                "creditScore": 760,
                "description": "30-YR UMBS-TBA PROD FEB",
                "grossSpread": -383.4278,
                "pricingDate": "2025-08-15",
                "swapCurveID": "SUSp815Q2",
                "currentYield": 0.5,
                "effectiveWAL": 10.7124,
                "maturityDate": "2054-01-01",
                "securityType": "MORT",
                "volModelType": "LMMSOFRFLAT",
                "yieldToWorst": 0.497093,
                "convexityCost": 27.4846,
                "currentCoupon": 0.5,
                "effectiveCV01": 0.001154157,
                "effectiveDV01": 0.094492547,
                "modelLoanSize": 361200.0,
                "mortgageYield": 0.4966,
                "remainingTerm": 335,
                "effectiveYield": 0.0105,
                "marketSettings": {
                    "settlementDate": "2026-02-12"
                },
                "settlementDate": "2026-02-12",
                "spreadDuration": 10.016126,
                "accruedInterest": 0.01527778,
                "annualizedYield": 0.498,
                "compoundingFreq": 2,
                "convexityEffect": -27.4846,
                "dataPpmProjList": [
                    {
                        "oneYear": 40.879,
                        "longTerm": 73.5063,
                        "oneMonth": 32.433,
                        "sixMonth": 41.584,
                        "prepayType": "PSA",
                        "threeMonth": 38.005
                    },
                    {
                        "oneYear": 2.3847,
                        "longTerm": 4.3945,
                        "oneMonth": 1.693,
                        "sixMonth": 2.357,
                        "prepayType": "CPR",
                        "threeMonth": 2.052
                    },
                    {
                        "oneYear": 2.3217,
                        "longTerm": 3.7992,
                        "oneMonth": 1.665,
                        "sixMonth": 2.311,
                        "prepayType": "FwdCPR",
                        "threeMonth": 2.016
                    },
                    {
                        "oneYear": 0.0,
                        "longTerm": 0.0,
                        "oneMonth": 0.0,
                        "sixMonth": 0.0,
                        "prepayType": "FwdCDR",
                        "threeMonth": 0.0
                    },
                    {
                        "oneYear": 0.0,
                        "longTerm": 0.0,
                        "oneMonth": 0.0,
                        "sixMonth": 0.0,
                        "prepayType": "FwdVPR",
                        "threeMonth": 0.0
                    },
                    {
                        "oneYear": 0.0,
                        "longTerm": 0.0,
                        "oneMonth": 0.0,
                        "sixMonth": 0.0,
                        "prepayType": "FwdVPRTurnover",
                        "threeMonth": 0.0
                    },
                    {
                        "oneYear": 0.0,
                        "longTerm": 0.0,
                        "oneMonth": 0.0,
                        "sixMonth": 0.0,
                        "prepayType": "FwdVPRCurtail",
                        "threeMonth": 0.0
                    },
                    {
                        "oneYear": 0.0,
                        "longTerm": 0.0,
                        "oneMonth": 0.0,
                        "sixMonth": 0.0,
                        "prepayType": "FwdVPRRefi",
                        "threeMonth": 0.0
                    },
                    {
                        "oneYear": 0.0,
                        "longTerm": 0.0,
                        "oneMonth": 0.0,
                        "sixMonth": 0.0,
                        "prepayType": "FwdVPRRefiRateterm",
                        "threeMonth": 0.0
                    },
                    {
                        "oneYear": 0.0,
                        "longTerm": 0.0,
                        "oneMonth": 0.0,
                        "sixMonth": 0.0,
                        "prepayType": "FwdVPRRefiCashout",
                        "threeMonth": 0.0
                    }
                ],
                "forwardMeasures": {
                    "wal": 10.57462,
                    "yield": 0.497224,
                    "margin": -408.145
                },
                "spreadConvexity": 1.522,
                "yearsToMaturity": 27.8861,
                "economicExposure": 100.015278,
                "macaulayDuration": 9.7477,
                "modelCreditScore": 763.4,
                "spreadToActCurve": -383.4915,
                "spreadToNextCall": -442.2918,
                "spreadToTsyCurve": -383.4278,
                "yieldCurveMargin": -408.1451,
                "yieldToWorstCall": 0.497093,
                "effectiveDuration": 9.447811127,
                "spreadToBenchmark": -382.8623,
                "spreadToSwapCurve": -359.0922,
                "spreadToWorstCall": -383,
                "effectiveConvexity": 0.115398034,
                "moatsCurrentCoupon": 5.406,
                "optionModelCurveID": "USDp0815",
                "yieldCurveDuration": 9.4478,
                "durationToWorstCase": 9.723537,
                "semiAnnualizedYield": 0.497093,
                "spreadToRFRSwapCurve": -330.6714,
                "yearsToFinalMaturity": 27.886,
                "spreadDurationTreasury": 10.016126,
                "fundedEffectiveDuration": 9.447811,
                "effectiveDurationPriceUp": 97.641293,
                "fundedEffectiveConvexity": 0.115398,
                "lastPrincipalPaymentDate": "2054-01-25",
                "effectiveDurationPriceDown": 102.36592,
                "spreadToTsyCurveAtBenchmarkTenor": -382.8623
            },
            "securityID": "01F00262"
        },
        "meta": {
            "status": "DONE",
            "requestId": "R-20905",
            "timeStamp": "2025-08-18T22:35:49Z",
            "responseType": "PY_CALC"
        }
    }

    """

    try:
        logger.info("Calling request_py_calculation_async_by_id")

        response = Client().yield_book_rest.request_py_calculation_async_by_id(
            id=id,
            id_type=id_type,
            level=level,
            pricing_date=pricing_date,
            curve_type=curve_type,
            currency=currency,
            prepay_type=prepay_type,
            prepay_rate=prepay_rate,
            option_model=option_model,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_py_calculation_async_by_id")

        return output
    except Exception as err:
        logger.error("Error request_py_calculation_async_by_id.")
        check_exception_and_raise(err, logger)


def request_py_calculation_sync(
    *,
    global_settings: Optional[PyCalcGlobalSettings] = None,
    input: Optional[List[PyCalcInput]] = None,
    keywords: Optional[List[str]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Request PY calculation sync.

    Parameters
    ----------
    global_settings : PyCalcGlobalSettings, optional

    input : List[PyCalcInput], optional

    keywords : List[str], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------
    >>> # request_py_calculation_sync
    >>> global_settings = PyCalcGlobalSettings(
    >>>             pricing_date=date(2025, 1, 17),
    >>>         )
    >>>
    >>> input = [
    >>>             PyCalcInput(
    >>>                 identifier="29874QEL",
    >>>                 level="100",
    >>>                 curve=CurveTypeAndCurrency(
    >>>                     curve_type="GVT",
    >>>                     currency="USD",
    >>>                     retrieve_curve=True,
    >>>                     snapshot="EOD",
    >>>                 ),
    >>>             )
    >>>         ]
    >>>
    >>> # request_py_calculation_sync
    >>> py_sync_post_response = request_py_calculation_sync(
    >>>             global_settings=global_settings,
    >>>             input=input
    >>>         )
    >>>
    >>> print(js.dumps(py_sync_post_response, indent=4))
    {
        "meta": {
            "status": "DONE",
            "requestId": "R-150605",
            "timeStamp": "2025-12-03T07:43:03Z",
            "responseType": "PY_CALC",
            "resultsStatus": "ALL"
        },
        "extra": {
            "curves": [
                {
                    "points": [
                        {
                            "rate": 4.3116,
                            "term": 0.25
                        },
                        {
                            "rate": 4.3164,
                            "term": 0.5
                        },
                        {
                            "rate": 4.264,
                            "term": 0.75
                        },
                        {
                            "rate": 4.2117,
                            "term": 1.0
                        },
                        {
                            "rate": 4.2268,
                            "term": 1.25
                        },
                        {
                            "rate": 4.2419,
                            "term": 1.5
                        },
                        {
                            "rate": 4.257,
                            "term": 1.75
                        },
                        {
                            "rate": 4.272,
                            "term": 2.0
                        },
                        {
                            "rate": 4.2873,
                            "term": 2.25
                        },
                        {
                            "rate": 4.3025,
                            "term": 2.5
                        },
                        {
                            "rate": 4.3177,
                            "term": 2.75
                        },
                        {
                            "rate": 4.3329,
                            "term": 3.0
                        },
                        {
                            "rate": 4.3431,
                            "term": 3.25
                        },
                        {
                            "rate": 4.3533,
                            "term": 3.5
                        },
                        {
                            "rate": 4.3635,
                            "term": 3.75
                        },
                        {
                            "rate": 4.3737,
                            "term": 4.0
                        },
                        {
                            "rate": 4.3839,
                            "term": 4.25
                        },
                        {
                            "rate": 4.394,
                            "term": 4.5
                        },
                        {
                            "rate": 4.4042,
                            "term": 4.75
                        },
                        {
                            "rate": 4.4144,
                            "term": 5.0
                        },
                        {
                            "rate": 4.427,
                            "term": 5.25
                        },
                        {
                            "rate": 4.4395,
                            "term": 5.5
                        },
                        {
                            "rate": 4.4521,
                            "term": 5.75
                        },
                        {
                            "rate": 4.4646,
                            "term": 6.0
                        },
                        {
                            "rate": 4.4771,
                            "term": 6.25
                        },
                        {
                            "rate": 4.4897,
                            "term": 6.5
                        },
                        {
                            "rate": 4.5022,
                            "term": 6.75
                        },
                        {
                            "rate": 4.5148,
                            "term": 7.0
                        },
                        {
                            "rate": 4.5226,
                            "term": 7.25
                        },
                        {
                            "rate": 4.5304,
                            "term": 7.5
                        },
                        {
                            "rate": 4.5383,
                            "term": 7.75
                        },
                        {
                            "rate": 4.5461,
                            "term": 8.0
                        },
                        {
                            "rate": 4.5539,
                            "term": 8.25
                        },
                        {
                            "rate": 4.5618,
                            "term": 8.5
                        },
                        {
                            "rate": 4.5696,
                            "term": 8.75
                        },
                        {
                            "rate": 4.5774,
                            "term": 9.0
                        },
                        {
                            "rate": 4.5853,
                            "term": 9.25
                        },
                        {
                            "rate": 4.5931,
                            "term": 9.5
                        },
                        {
                            "rate": 4.6009,
                            "term": 9.75
                        },
                        {
                            "rate": 4.6087,
                            "term": 10.0
                        },
                        {
                            "rate": 4.6164,
                            "term": 10.25
                        },
                        {
                            "rate": 4.6241,
                            "term": 10.5
                        },
                        {
                            "rate": 4.6318,
                            "term": 10.75
                        },
                        {
                            "rate": 4.6395,
                            "term": 11.0
                        },
                        {
                            "rate": 4.6472,
                            "term": 11.25
                        },
                        {
                            "rate": 4.6549,
                            "term": 11.5
                        },
                        {
                            "rate": 4.6626,
                            "term": 11.75
                        },
                        {
                            "rate": 4.6703,
                            "term": 12.0
                        },
                        {
                            "rate": 4.678,
                            "term": 12.25
                        },
                        {
                            "rate": 4.6857,
                            "term": 12.5
                        },
                        {
                            "rate": 4.6934,
                            "term": 12.75
                        },
                        {
                            "rate": 4.7011,
                            "term": 13.0
                        },
                        {
                            "rate": 4.7088,
                            "term": 13.25
                        },
                        {
                            "rate": 4.7165,
                            "term": 13.5
                        },
                        {
                            "rate": 4.7242,
                            "term": 13.75
                        },
                        {
                            "rate": 4.7319,
                            "term": 14.0
                        },
                        {
                            "rate": 4.7396,
                            "term": 14.25
                        },
                        {
                            "rate": 4.7473,
                            "term": 14.5
                        },
                        {
                            "rate": 4.755,
                            "term": 14.75
                        },
                        {
                            "rate": 4.7627,
                            "term": 15.0
                        },
                        {
                            "rate": 4.7704,
                            "term": 15.25
                        },
                        {
                            "rate": 4.7781,
                            "term": 15.5
                        },
                        {
                            "rate": 4.7858,
                            "term": 15.75
                        },
                        {
                            "rate": 4.7934,
                            "term": 16.0
                        },
                        {
                            "rate": 4.8011,
                            "term": 16.25
                        },
                        {
                            "rate": 4.8088,
                            "term": 16.5
                        },
                        {
                            "rate": 4.8165,
                            "term": 16.75
                        },
                        {
                            "rate": 4.8242,
                            "term": 17.0
                        },
                        {
                            "rate": 4.8319,
                            "term": 17.25
                        },
                        {
                            "rate": 4.8396,
                            "term": 17.5
                        },
                        {
                            "rate": 4.8473,
                            "term": 17.75
                        },
                        {
                            "rate": 4.855,
                            "term": 18.0
                        },
                        {
                            "rate": 4.8627,
                            "term": 18.25
                        },
                        {
                            "rate": 4.8704,
                            "term": 18.5
                        },
                        {
                            "rate": 4.8781,
                            "term": 18.75
                        },
                        {
                            "rate": 4.8858,
                            "term": 19.0
                        },
                        {
                            "rate": 4.8935,
                            "term": 19.25
                        },
                        {
                            "rate": 4.9012,
                            "term": 19.5
                        },
                        {
                            "rate": 4.9089,
                            "term": 19.75
                        },
                        {
                            "rate": 4.9166,
                            "term": 20.0
                        },
                        {
                            "rate": 4.9148,
                            "term": 20.25
                        },
                        {
                            "rate": 4.913,
                            "term": 20.5
                        },
                        {
                            "rate": 4.9112,
                            "term": 20.75
                        },
                        {
                            "rate": 4.9094,
                            "term": 21.0
                        },
                        {
                            "rate": 4.9077,
                            "term": 21.25
                        },
                        {
                            "rate": 4.9059,
                            "term": 21.5
                        },
                        {
                            "rate": 4.9041,
                            "term": 21.75
                        },
                        {
                            "rate": 4.9023,
                            "term": 22.0
                        },
                        {
                            "rate": 4.9005,
                            "term": 22.25
                        },
                        {
                            "rate": 4.8987,
                            "term": 22.5
                        },
                        {
                            "rate": 4.897,
                            "term": 22.75
                        },
                        {
                            "rate": 4.8952,
                            "term": 23.0
                        },
                        {
                            "rate": 4.8934,
                            "term": 23.25
                        },
                        {
                            "rate": 4.8916,
                            "term": 23.5
                        },
                        {
                            "rate": 4.8898,
                            "term": 23.75
                        },
                        {
                            "rate": 4.888,
                            "term": 24.0
                        },
                        {
                            "rate": 4.8863,
                            "term": 24.25
                        },
                        {
                            "rate": 4.8845,
                            "term": 24.5
                        },
                        {
                            "rate": 4.8827,
                            "term": 24.75
                        },
                        {
                            "rate": 4.8809,
                            "term": 25.0
                        },
                        {
                            "rate": 4.8791,
                            "term": 25.25
                        },
                        {
                            "rate": 4.8773,
                            "term": 25.5
                        },
                        {
                            "rate": 4.8756,
                            "term": 25.75
                        },
                        {
                            "rate": 4.8738,
                            "term": 26.0
                        },
                        {
                            "rate": 4.872,
                            "term": 26.25
                        },
                        {
                            "rate": 4.8702,
                            "term": 26.5
                        },
                        {
                            "rate": 4.8684,
                            "term": 26.75
                        },
                        {
                            "rate": 4.8666,
                            "term": 27.0
                        },
                        {
                            "rate": 4.8649,
                            "term": 27.25
                        },
                        {
                            "rate": 4.8631,
                            "term": 27.5
                        },
                        {
                            "rate": 4.8613,
                            "term": 27.75
                        },
                        {
                            "rate": 4.8595,
                            "term": 28.0
                        },
                        {
                            "rate": 4.8577,
                            "term": 28.25
                        },
                        {
                            "rate": 4.8559,
                            "term": 28.5
                        },
                        {
                            "rate": 4.8542,
                            "term": 28.75
                        },
                        {
                            "rate": 4.8524,
                            "term": 29.0
                        },
                        {
                            "rate": 4.8506,
                            "term": 29.25
                        },
                        {
                            "rate": 4.8488,
                            "term": 29.5
                        },
                        {
                            "rate": 4.847,
                            "term": 29.75
                        },
                        {
                            "rate": 4.8452,
                            "term": 30.0
                        }
                    ],
                    "source": "SSB",
                    "curveId": "USDp0117",
                    "currency": "USD",
                    "pricingDate": "2025-01-17",
                    "curveEffDate": "2025-01-17",
                    "curveYieldFreq": 2
                }
            ]
        },
        "results": [
            {
                "py": {
                    "oas": -373.0749,
                    "wal": 0.841096,
                    "dv01": 0.00838988,
                    "isin": "US29874QEL41",
                    "cusip": "29874QEL4",
                    "price": 100.0,
                    "yield": 0.499919,
                    "ticker": "EBRD",
                    "cSpread": 7.672,
                    "cdYield": 0.493835,
                    "pyLevel": "100",
                    "zSpread": -373.074889,
                    "duration": 0.838324,
                    "recovery": 37.4,
                    "ziSpread": -374.496164,
                    "znSpread": -378.43626,
                    "assetSwap": -395.112,
                    "benchmark": "US 3.375 11/27",
                    "convexity": 0.0112,
                    "curveDate": "2025-01-17",
                    "curveType": "Govt",
                    "fullPrice": 100.07916667,
                    "securityID": "29874QEL",
                    "spreadDV01": 0.008389905,
                    "tsyCurveID": "USDp0117",
                    "volatility": 13.0,
                    "accruedDays": 57,
                    "description": "EUROPEAN BANK FOR RECON AND DEV",
                    "grossSpread": -374.4927,
                    "optionValue": 0.0,
                    "pricingDate": "2025-01-17",
                    "swapCurveID": "SUSp117Q2",
                    "currentYield": 0.5,
                    "effectiveWAL": 0.8417,
                    "maturityDate": "2025-11-25",
                    "securityType": "BOND",
                    "volModelType": "Single",
                    "yieldToWorst": 0.499919,
                    "convexityCost": 0.0,
                    "currentCoupon": 0.5,
                    "discountYield": 0.0,
                    "effectiveCV01": 0.000112198,
                    "effectiveDV01": 0.008388666,
                    "worstCallDate": "2025-11-25",
                    "cdsAdjustedOAS": -380.657,
                    "effectiveYield": 0.496,
                    "marketSettings": {
                        "settlementDate": "2025-01-22"
                    },
                    "settlementDate": "2025-01-22",
                    "spreadDuration": 0.838327,
                    "walToWorstCall": 0.841096,
                    "zSpreadToWorst": -378.436,
                    "accruedInterest": 0.07916667,
                    "annualizedYield": 0.501,
                    "assetSwapSpread": -371.247,
                    "cdsImpliedPrice": 96.879,
                    "compoundingFreq": 2,
                    "convexityEffect": 0.0,
                    "dv01ToWorstCall": 0.00839,
                    "spreadConvexity": 0.011,
                    "yearsToMaturity": 0.8411,
                    "ziWorstCallDate": "2025-11-25",
                    "znWorstCallDate": "2025-11-25",
                    "assetSwapToLibor": {
                        "type": "PAR",
                        "value": -395.1121
                    },
                    "cdsAdjustedYield": 0.424,
                    "economicExposure": 100.079167,
                    "macaulayDuration": 0.8404,
                    "spreadToActCurve": -373.3523,
                    "spreadToNextCall": -374.4927,
                    "spreadToTsyCurve": -374.5047,
                    "yearsToWorstCall": 0.842,
                    "yieldCurveMargin": -373.0749,
                    "yieldToWorstCall": 0.499919,
                    "effectiveDuration": 0.838203073,
                    "macaulayConvexity": 0.7069,
                    "spreadToBenchmark": -377.2128,
                    "spreadToSwapCurve": -400.5193,
                    "spreadToWorstCall": -374,
                    "effectiveConvexity": 0.011210883,
                    "ffndSpreadDuration": 0.0,
                    "optionModelCurveID": "USDp0117",
                    "yieldCurveDuration": 0.8382,
                    "durationToWorstCall": 0.8383,
                    "durationToWorstCase": 0.838324,
                    "indexSpreadDuration": 0.0,
                    "semiAnnualizedYield": 0.499919,
                    "ziSpreadToWorstCall": -374.496,
                    "znSpreadToWorstCall": -378.436,
                    "benchmarkToWorstCall": "US 3.375 11/27",
                    "spreadToRFRSwapCurve": -371.6566,
                    "yearsToFinalMaturity": 0.842,
                    "gnmafnmaSpreadDuration": 0.0,
                    "spreadDurationTreasury": 0.838327,
                    "fundedEffectiveDuration": 0.838203,
                    "effectiveDurationPriceUp": 99.8698,
                    "fundedEffectiveConvexity": 0.011211,
                    "effectiveDurationPriceDown": 100.289234,
                    "spreadToActCurveToWorstCall": -373.3523,
                    "currentCouponSpreadConvexity": 0.0,
                    "spreadToBenchmarkToWorstCall": -377.2128,
                    "currentCouponSpreadSensitivity": 0.0,
                    "spreadToTsyCurveAtBenchmarkTenor": -371.1762
                },
                "securityID": "29874QEL"
            }
        ]
    }

    """

    try:
        logger.info("Calling request_py_calculation_sync")

        response = Client().yield_book_rest.request_py_calculation_sync(
            body=PyCalcRequest(global_settings=global_settings, input=input, keywords=keywords),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
            content_type="application/json",
        )

        output = response
        logger.info("Called request_py_calculation_sync")

        return output
    except Exception as err:
        logger.error("Error request_py_calculation_sync.")
        check_exception_and_raise(err, logger)


def request_py_calculation_sync_by_id(
    *,
    id: str,
    level: str,
    curve_type: Union[str, YbRestCurveType],
    id_type: Optional[str] = None,
    pricing_date: Optional[Union[str, datetime.date]] = None,
    currency: Optional[str] = None,
    prepay_type: Optional[str] = None,
    prepay_rate: Optional[float] = None,
    option_model: Optional[Union[str, OptionModel]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Request PY calculation sync by ID.

    Parameters
    ----------
    id : str
        A sequence of textual characters.
    id_type : str, optional
        A sequence of textual characters.
    level : str
        A sequence of textual characters.
    pricing_date : Union[str, datetime.date], optional
        A date on a calendar without a time zone, e.g. "April 10th"
    curve_type : Union[str, YbRestCurveType]

    currency : str, optional
        A sequence of textual characters.
    prepay_type : str, optional
        A sequence of textual characters.
    prepay_rate : float, optional
        A 64 bit floating point number. (`±5.0 × 10^−324` to `±1.7 × 10^308`)
    option_model : Union[str, OptionModel], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------
    >>> # request_py_calculation_sync_by_id
    >>> py_sync_get_response = request_py_calculation_sync_by_id(
    >>>             id="912810FP",
    >>>             level="100",
    >>>             curve_type="GVT",
    >>>         )
    >>>
    >>> print(js.dumps(py_sync_get_response, indent=4))
    {
        "data": {
            "py": {
                "oas": 170.1825,
                "wal": 5.2,
                "dv01": 0.044853229,
                "isin": "US912810FP85",
                "cusip": "912810FP8",
                "price": 100.0,
                "yield": 5.373097,
                "ticker": "US",
                "cSpread": 26.165,
                "cdYield": 5.293433,
                "pyLevel": "100",
                "zSpread": 170.182457,
                "cdsShift": 159.32,
                "duration": 4.413764,
                "recovery": 37.4,
                "ziSpread": 170.506169,
                "znSpread": 195.899518,
                "assetSwap": 168.309,
                "benchmark": "US  3.5 11/30",
                "convexity": 0.2347,
                "curveDate": "2025-12-02",
                "curveType": "Govt",
                "fullPrice": 101.62126359,
                "securityID": "912810FP",
                "spreadDV01": 0.0,
                "tsyCurveID": "USDp1202",
                "accruedDays": 111,
                "description": "US TREASURY",
                "grossSpread": 169.6741,
                "optionValue": 0.0,
                "pricingDate": "2025-12-02",
                "swapCurveID": "SUSp1202Q2",
                "currentYield": 5.375,
                "effectiveWAL": 5.1972,
                "maturityDate": "2031-02-15",
                "securityType": "BOND",
                "volModelType": "MarketWSkew",
                "yieldToWorst": 5.373097,
                "convexityCost": 0.0,
                "currentCoupon": 5.375,
                "effectiveCV01": 0.002391646,
                "effectiveDV01": 0.044933353,
                "worstCallDate": "2031-02-15",
                "cdsAdjustedOAS": 143.27,
                "effectiveYield": 5.3505,
                "marketSettings": {
                    "settlementDate": "2025-12-04"
                },
                "settlementDate": "2025-12-04",
                "spreadDuration": 0.0,
                "walToWorstCall": 5.2,
                "zSpreadToWorst": 195.9,
                "accruedInterest": 1.62126359,
                "annualizedYield": 5.445,
                "assetSwapSpread": 197.414,
                "cdsImpliedPrice": 108.104,
                "compoundingFreq": 2,
                "convexityEffect": 0.0,
                "dv01ToWorstCall": 0.044853,
                "spreadConvexity": 0.235,
                "yearsToMaturity": 5.2,
                "ziWorstCallDate": "2031-02-15",
                "znWorstCallDate": "2031-02-15",
                "assetSwapToLibor": {
                    "type": "PAR",
                    "value": 168.3094
                },
                "cdsAdjustedYield": 5.109,
                "economicExposure": 101.621264,
                "macaulayDuration": 4.5323,
                "spreadToActCurve": 169.5654,
                "spreadToNextCall": 169.6741,
                "spreadToTsyCurve": 169.647,
                "yearsToWorstCall": 5.197,
                "yieldCurveMargin": 170.1825,
                "yieldToWorstCall": 5.373096,
                "effectiveDuration": 4.421648502,
                "macaulayConvexity": 22.4816,
                "spreadToBenchmark": 171.6042,
                "spreadToSwapCurve": 171.9941,
                "spreadToWorstCall": 170,
                "effectiveConvexity": 0.23534897,
                "ffndSpreadDuration": 0.0,
                "optionModelCurveID": "USDp1202",
                "yieldCurveDuration": 4.4216,
                "durationToWorstCall": 4.4138,
                "durationToWorstCase": 4.413764,
                "indexSpreadDuration": 0.0,
                "semiAnnualizedYield": 5.373097,
                "ziSpreadToWorstCall": 170.506,
                "znSpreadToWorstCall": 195.9,
                "benchmarkToWorstCall": "US  3.5 11/30",
                "spreadToRFRSwapCurve": 200.549,
                "yearsToFinalMaturity": 5.197,
                "gnmafnmaSpreadDuration": 0.0,
                "spreadDurationTreasury": 4.412092,
                "fundedEffectiveDuration": 4.421649,
                "effectiveDurationPriceUp": 100.505404,
                "fundedEffectiveConvexity": 0.235349,
                "effectiveDurationPriceDown": 102.752071,
                "spreadToActCurveToWorstCall": 169.5654,
                "currentCouponSpreadConvexity": 0.0,
                "spreadToBenchmarkToWorstCall": 171.6041,
                "currentCouponSpreadSensitivity": 0.0,
                "spreadToTsyCurveAtBenchmarkTenor": 171.6042
            },
            "securityID": "912810FP"
        },
        "meta": {
            "status": "DONE",
            "requestId": "R-150604",
            "timeStamp": "2025-12-03T07:43:02Z",
            "responseType": "PY_CALC"
        }
    }

    """

    try:
        logger.info("Calling request_py_calculation_sync_by_id")

        response = Client().yield_book_rest.request_py_calculation_sync_by_id(
            id=id,
            id_type=id_type,
            level=level,
            pricing_date=pricing_date,
            curve_type=curve_type,
            currency=currency,
            prepay_type=prepay_type,
            prepay_rate=prepay_rate,
            option_model=option_model,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_py_calculation_sync_by_id")

        return output
    except Exception as err:
        logger.error("Error request_py_calculation_sync_by_id.")
        check_exception_and_raise(err, logger)


def request_return_attribution_async(
    *,
    global_settings: Optional[ReturnAttributionGlobalSettings] = None,
    input: Optional[List[ReturnAttributionInput]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Request return attribution async.

    Parameters
    ----------
    global_settings : ReturnAttributionGlobalSettings, optional

    input : List[ReturnAttributionInput], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_return_attribution_async")

        response = Client().yield_book_rest.request_return_attribution_async(
            body=ReturnAttributionRequest(global_settings=global_settings, input=input),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_return_attribution_async")

        return output
    except Exception as err:
        logger.error("Error request_return_attribution_async.")
        check_exception_and_raise(err, logger)


def request_return_attribution_sync(
    *,
    global_settings: Optional[ReturnAttributionGlobalSettings] = None,
    input: Optional[List[ReturnAttributionInput]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Request return attribution sync.

    Parameters
    ----------
    global_settings : ReturnAttributionGlobalSettings, optional

    input : List[ReturnAttributionInput], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_return_attribution_sync")

        response = Client().yield_book_rest.request_return_attribution_sync(
            body=ReturnAttributionRequest(global_settings=global_settings, input=input),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_return_attribution_sync")

        return output
    except Exception as err:
        logger.error("Error request_return_attribution_sync.")
        check_exception_and_raise(err, logger)


def request_scenario_calculation_async(
    *,
    global_settings: Optional[ScenarioCalcGlobalSettings] = None,
    keywords: Optional[List[str]] = None,
    scenarios: Optional[List[Scenario]] = None,
    input: Optional[List[ScenarioCalcInput]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Request scenario calculation async.

    Parameters
    ----------
    global_settings : ScenarioCalcGlobalSettings, optional

    keywords : List[str], optional

    scenarios : List[Scenario], optional

    input : List[ScenarioCalcInput], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------
    >>> # request_scenario_calculation_async
    >>> global_settings = ScenarioCalcGlobalSettings(
    >>>             pricing_date="2025-01-01",
    >>>         )
    >>>
    >>> scenario = Scenario(
    >>>             scenario_id="ScenID1",
    >>>             definition=ScenarioDefinition(
    >>>                 system_scenario=SystemScenario(name="BEARFLAT100")
    >>>             ),
    >>>         )
    >>>
    >>> input = ScenarioCalcInput(
    >>>             identifier="US742718AV11",
    >>>             id_type="ISIN",
    >>>             curve=CurveTypeAndCurrency(
    >>>                 curve_type="GVT",
    >>>                 currency="USD",
    >>>             ),
    >>>             settlement_info=SettlementInfo(
    >>>                 level="100",
    >>>             ),
    >>>             horizon_info=[
    >>>                 HorizonInfo(
    >>>                     scenario_id="ScenID1",
    >>>                     level="100",
    >>>                 )
    >>>             ],
    >>>             horizon_py_method="OAS",
    >>>         )
    >>>
    >>> # Request bond CF with async post
    >>> sa_async_post_response = request_scenario_calculation_async(
    >>>                             global_settings=global_settings,
    >>>                             scenarios=[scenario],
    >>>                             input=[input],
    >>>                         )
    >>>
    >>> async_post_results_response = {}
    >>>
    >>> attempt = 1
    >>>
    >>> while attempt < 10:
    >>>
    >>>     from lseg_analytics.core.exceptions import ServerError
    >>>     try:
    >>>         time.sleep(10)
    >>>         # Request bond indic with async post
    >>>         async_post_results_response = get_result(request_id_parameter=sa_async_post_response.request_id)
    >>>         break
    >>>     except Exception as err:
    >>>         print(f"Attempt " + str(
    >>>             attempt) + " resulted in error retrieving results from:" + sa_async_post_response.request_id)
    >>>         if (isinstance(err, ServerError)
    >>>                 and f"The result is not ready yet for requestID:{sa_async_post_response.request_id}" in str(err)):
    >>>
    >>>             attempt += 1
    >>>         else:
    >>>             raise err
    >>>
    >>> print(js.dumps(async_post_results_response, indent=4))
    {
        "meta": {
            "status": "DONE",
            "requestId": "R-21320",
            "timeStamp": "2025-08-19T02:17:06Z",
            "responseType": "SCENARIO_CALC",
            "resultsStatus": "ALL"
        },
        "results": [
            {
                "isin": "US742718AV11",
                "cusip": "742718AV1",
                "ticker": "PG",
                "scenario": {
                    "horizon": [
                        {
                            "oas": 100.0,
                            "wal": 4.8139,
                            "price": 104.89765,
                            "yield": 6.7865,
                            "balance": 1.0,
                            "pylevel": "100.000000",
                            "duration": 3.9209,
                            "fullPrice": 106.386538,
                            "returnCode": 0,
                            "scenarioID": "ScenID1",
                            "spreadDV01": 0.0,
                            "volatility": 16.0,
                            "actualPrice": 104.898,
                            "grossSpread": 99.9335,
                            "horizonDays": 0,
                            "marketValue": 106.386538,
                            "optionValue": 0.0,
                            "totalReturn": 4.8257988,
                            "dollarReturn": 4.89764958,
                            "convexityCost": 0.0,
                            "nominalSpread": 99.9335,
                            "effectiveYield": 0.0,
                            "interestReturn": 0.0,
                            "settlementDate": "2025-01-03",
                            "spreadDuration": 0.0,
                            "accruedInterest": 1.488889,
                            "actualFullPrice": 106.387,
                            "horizonPYMethod": "OAS",
                            "interestPayment": 0.0,
                            "principalReturn": 4.8257988,
                            "underlyingPrice": 0.0,
                            "principalPayment": 0.0,
                            "reinvestmentRate": 5.145556,
                            "yieldCurveMargin": 100.0,
                            "effectiveCallDate": "0",
                            "reinvestmentAmount": 0.0,
                            "actualAccruedInterest": 1.489
                        }
                    ],
                    "settlement": {
                        "oas": 361.951,
                        "psa": 0.0,
                        "wal": 4.8139,
                        "price": 100.0,
                        "yield": 7.9953,
                        "fullPrice": 101.488889,
                        "volatility": 13.0,
                        "grossSpread": 361.2649,
                        "optionValue": 0.0,
                        "pricingDate": "2024-12-31",
                        "forwardYield": 0.0,
                        "staticSpread": 0.0,
                        "effectiveDV01": 0.039405887,
                        "nominalSpread": 0.0,
                        "settlementDate": "2025-01-03",
                        "accruedInterest": 1.488889,
                        "reinvestmentRate": 4.329956,
                        "yieldCurveMargin": 0.0,
                        "effectiveDuration": 3.8828,
                        "effectiveConvexity": 0.1873
                    }
                },
                "returnCode": 0,
                "securityID": "742718AV",
                "description": "PROCTER & GAMBLE CO",
                "maturityDate": "2029-10-26",
                "securityType": "BOND",
                "currentCoupon": 8.0
            }
        ]
    }

    """

    try:
        logger.info("Calling request_scenario_calculation_async")

        response = Client().yield_book_rest.request_scenario_calculation_async(
            body=ScenarioCalcRequest(
                global_settings=global_settings,
                keywords=keywords,
                scenarios=scenarios,
                input=input,
            ),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
            content_type="application/json",
        )

        output = response
        logger.info("Called request_scenario_calculation_async")

        return output
    except Exception as err:
        logger.error("Error request_scenario_calculation_async.")
        check_exception_and_raise(err, logger)


def request_scenario_calculation_sync(
    *,
    global_settings: Optional[ScenarioCalcGlobalSettings] = None,
    keywords: Optional[List[str]] = None,
    scenarios: Optional[List[Scenario]] = None,
    input: Optional[List[ScenarioCalcInput]] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Request scenario calculation sync.

    Parameters
    ----------
    global_settings : ScenarioCalcGlobalSettings, optional

    keywords : List[str], optional

    scenarios : List[Scenario], optional

    input : List[ScenarioCalcInput], optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------
    >>> # request_scenario_calculation_async
    >>> global_settings = ScenarioCalcGlobalSettings(
    >>>             pricing_date="2025-01-01",
    >>>         )
    >>>
    >>> scenario = Scenario(
    >>>             scenario_id="ScenID1",
    >>>             definition=ScenarioDefinition(
    >>>                 system_scenario=SystemScenario(name="BEARFLAT100")
    >>>             ),
    >>>         )
    >>>
    >>> input = ScenarioCalcInput(
    >>>             identifier="US742718AV11",
    >>>             id_type="ISIN",
    >>>             curve=CurveTypeAndCurrency(
    >>>                 curve_type="GVT",
    >>>                 currency="USD",
    >>>             ),
    >>>             settlement_info=SettlementInfo(
    >>>                 level="100",
    >>>             ),
    >>>             horizon_info=[
    >>>                 HorizonInfo(
    >>>                     scenario_id="ScenID1",
    >>>                     level="100",
    >>>                 )
    >>>             ],
    >>>             horizon_py_method="OAS",
    >>>         )
    >>>
    >>> # Execute Post sync request with prepared inputs
    >>> sa_sync_post_response = request_scenario_calculation_sync(
    >>>                             global_settings=global_settings,
    >>>                             scenarios=[scenario],
    >>>                             input=[input],
    >>>                         )
    >>>
    >>> print(js.dumps(sa_sync_post_response, indent=4))
    {
        "meta": {
            "status": "DONE",
            "requestId": "R-150609",
            "timeStamp": "2025-12-03T07:43:10Z",
            "responseType": "SCENARIO_CALC",
            "resultsStatus": "ALL"
        },
        "results": [
            {
                "isin": "US742718AV11",
                "cusip": "742718AV1",
                "ticker": "PG",
                "scenario": {
                    "horizon": [
                        {
                            "oas": 100.0,
                            "wal": 4.8139,
                            "price": 104.89765,
                            "yield": 6.7865,
                            "balance": 1.0,
                            "pylevel": "100.000000",
                            "duration": 3.9209,
                            "fullPrice": 106.386538,
                            "returnCode": 0,
                            "scenarioID": "ScenID1",
                            "spreadDV01": 0.0,
                            "volatility": 16.0,
                            "actualPrice": 104.898,
                            "grossSpread": 99.9335,
                            "horizonDays": 0,
                            "marketValue": 106.386538,
                            "optionValue": 0.0,
                            "totalReturn": 4.8257988,
                            "dollarReturn": 4.89764958,
                            "convexityCost": 0.0,
                            "nominalSpread": 99.9335,
                            "effectiveYield": 0.0,
                            "interestReturn": 0.0,
                            "settlementDate": "2025-01-03",
                            "spreadDuration": 0.0,
                            "accruedInterest": 1.488889,
                            "actualFullPrice": 106.387,
                            "horizonPYMethod": "OAS",
                            "interestPayment": 0.0,
                            "principalReturn": 4.8257988,
                            "underlyingPrice": 0.0,
                            "principalPayment": 0.0,
                            "reinvestmentRate": 5.145556,
                            "yieldCurveMargin": 100.0,
                            "effectiveCallDate": "0",
                            "reinvestmentAmount": 0.0,
                            "actualAccruedInterest": 1.489
                        }
                    ],
                    "settlement": {
                        "oas": 361.951,
                        "psa": 0.0,
                        "wal": 4.8139,
                        "price": 100.0,
                        "yield": 7.9953,
                        "fullPrice": 101.488889,
                        "volatility": 13.0,
                        "grossSpread": 361.2649,
                        "optionValue": 0.0,
                        "pricingDate": "2024-12-31",
                        "forwardYield": 0.0,
                        "staticSpread": 0.0,
                        "effectiveDV01": 0.039405887,
                        "nominalSpread": 0.0,
                        "settlementDate": "2025-01-03",
                        "accruedInterest": 1.488889,
                        "reinvestmentRate": 4.329956,
                        "yieldCurveMargin": 0.0,
                        "effectiveDuration": 3.8828,
                        "effectiveConvexity": 0.1873
                    }
                },
                "returnCode": 0,
                "securityID": "742718AV",
                "description": "PROCTER & GAMBLE CO",
                "maturityDate": "2029-10-26",
                "securityType": "BOND",
                "currentCoupon": 8.0
            }
        ]
    }

    """

    try:
        logger.info("Calling request_scenario_calculation_sync")

        response = Client().yield_book_rest.request_scenario_calculation_sync(
            body=ScenarioCalcRequest(
                global_settings=global_settings,
                keywords=keywords,
                scenarios=scenarios,
                input=input,
            ),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
            content_type="application/json",
        )

        output = response
        logger.info("Called request_scenario_calculation_sync")

        return output
    except Exception as err:
        logger.error("Error request_scenario_calculation_sync.")
        check_exception_and_raise(err, logger)


def request_volatility_async(
    *,
    currency: str,
    date: str,
    quote_type: str,
    vol_model: Optional[str] = None,
    vol_type: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Request volatility async.

    Parameters
    ----------
    currency : str
        Currency should be a 3 letter upper case string
    date : str
        A sequence of textual characters.
    quote_type : str
        Should be one of the following - Calibrated, SOFRMarket, LIBORMarket.
    vol_model : str, optional
        Should be one of the following - Default, LMMSOFR, LMMSOFRNEW, LMMSOFRFLAT, LMMDL, LMMDDNEW, LMMDD. To be provided when quoteType is Calibrated
    vol_type : str, optional
        Should be one of the following - NORM, BLACK, To be provided when quoteType is SOFRMarket or LIBORMarket.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_volatility_async")

        response = Client().yield_book_rest.request_volatility_async(
            currency=currency,
            date=date,
            quote_type=quote_type,
            vol_model=vol_model,
            vol_type=vol_type,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_volatility_async")

        return output
    except Exception as err:
        logger.error("Error request_volatility_async.")
        check_exception_and_raise(err, logger)


def request_volatility_sync(
    *,
    currency: str,
    date: str,
    quote_type: str,
    vol_model: Optional[str] = None,
    vol_type: Optional[str] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Request volatility sync.

    Parameters
    ----------
    currency : str
        Currency should be a 3 letter upper case string
    date : str
        A sequence of textual characters.
    quote_type : str
        Should be one of the following - Calibrated, SOFRMarket, LIBORMarket.
    vol_model : str, optional
        Should be one of the following - Default, LMMSOFR, LMMSOFRNEW, LMMSOFRFLAT, LMMDL, LMMDDNEW, LMMDD. To be provided when quoteType is Calibrated
    vol_type : str, optional
        Should be one of the following - NORM, BLACK, To be provided when quoteType is SOFRMarket or LIBORMarket.
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_volatility_sync")

        response = Client().yield_book_rest.request_volatility_sync(
            currency=currency,
            date=date,
            quote_type=quote_type,
            vol_model=vol_model,
            vol_type=vol_type,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_volatility_sync")

        return output
    except Exception as err:
        logger.error("Error request_volatility_sync.")
        check_exception_and_raise(err, logger)


def request_wal_sensitivity_asyn_get(
    *,
    id: str,
    prepay_type: Union[str, WalSensitivityPrepayType],
    prepay_rate_start: int,
    prepay_rate_end: int,
    prepay_rate_step: int,
    tolerance: float,
    id_type: Optional[str] = None,
    horizon_date: Optional[Union[str, datetime.date]] = None,
    prepay_rate: Optional[int] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """


    Parameters
    ----------
    id : str
        Security reference ID.
    id_type : str, optional
        A sequence of textual characters.
    prepay_type : Union[str, WalSensitivityPrepayType]

    prepay_rate_start : int
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    prepay_rate_end : int
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    prepay_rate_step : int
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tolerance : float
        A 64 bit floating point number. (`±5.0 × 10^−324` to `±1.7 × 10^308`)
    horizon_date : Union[str, datetime.date], optional
        A date on a calendar without a time zone, e.g. "April 10th"
    prepay_rate : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_wal_sensitivity_asyn_get")

        response = Client().yield_book_rest.request_wal_sensitivity_asyn_get(
            id=id,
            id_type=id_type,
            prepay_type=prepay_type,
            prepay_rate_start=prepay_rate_start,
            prepay_rate_end=prepay_rate_end,
            prepay_rate_step=prepay_rate_step,
            tolerance=tolerance,
            horizon_date=horizon_date,
            prepay_rate=prepay_rate,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_wal_sensitivity_asyn_get")

        return output
    except Exception as err:
        logger.error("Error request_wal_sensitivity_asyn_get.")
        check_exception_and_raise(err, logger)


def request_wal_sensitivity_async(
    *,
    input: Optional[WalSensitivityInput] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """


    Parameters
    ----------
    input : WalSensitivityInput, optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling request_wal_sensitivity_async")

        response = Client().yield_book_rest.request_wal_sensitivity_async(
            body=WalSensitivityRequest(input=input),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_wal_sensitivity_async")

        return output
    except Exception as err:
        logger.error("Error request_wal_sensitivity_async.")
        check_exception_and_raise(err, logger)


def request_wal_sensitivity_sync(
    *,
    input: Optional[WalSensitivityInput] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """


    Parameters
    ----------
    input : WalSensitivityInput, optional

    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_wal_sensitivity_sync")

        response = Client().yield_book_rest.request_wal_sensitivity_sync(
            body=WalSensitivityRequest(input=input),
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_wal_sensitivity_sync")

        return output
    except Exception as err:
        logger.error("Error request_wal_sensitivity_sync.")
        check_exception_and_raise(err, logger)


def request_wal_sensitivity_sync_get(
    *,
    id: str,
    prepay_type: Union[str, WalSensitivityPrepayType],
    prepay_rate_start: int,
    prepay_rate_end: int,
    prepay_rate_step: int,
    tolerance: float,
    id_type: Optional[str] = None,
    horizon_date: Optional[Union[str, datetime.date]] = None,
    prepay_rate: Optional[int] = None,
    job: Optional[str] = None,
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """


    Parameters
    ----------
    id : str
        Security reference ID.
    id_type : str, optional
        A sequence of textual characters.
    prepay_type : Union[str, WalSensitivityPrepayType]

    prepay_rate_start : int
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    prepay_rate_end : int
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    prepay_rate_step : int
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tolerance : float
        A 64 bit floating point number. (`±5.0 × 10^−324` to `±1.7 × 10^308`)
    horizon_date : Union[str, datetime.date], optional
        A date on a calendar without a time zone, e.g. "April 10th"
    prepay_rate : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    job : str, optional
        Job reference. This can be of the form J-number or job name.
    name : str, optional
        User provided name.
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling request_wal_sensitivity_sync_get")

        response = Client().yield_book_rest.request_wal_sensitivity_sync_get(
            id=id,
            id_type=id_type,
            prepay_type=prepay_type,
            prepay_rate_start=prepay_rate_start,
            prepay_rate_end=prepay_rate_end,
            prepay_rate_step=prepay_rate_step,
            tolerance=tolerance,
            horizon_date=horizon_date,
            prepay_rate=prepay_rate,
            job=job,
            name=name,
            pri=pri,
            tags=tags,
        )

        output = response
        logger.info("Called request_wal_sensitivity_sync_get")

        return output
    except Exception as err:
        logger.error("Error request_wal_sensitivity_sync_get.")
        check_exception_and_raise(err, logger)


def resubmit_job(
    *,
    job_ref: str,
    scope: Optional[Literal["OK", "ERROR", "ABORTED", "FAILED", "ALL"]] = None,
    ids: Optional[List[str]] = None,
) -> JobResponse:
    """
    Resubmit a job

    Parameters
    ----------
    scope : Literal["OK","ERROR","ABORTED","FAILED","ALL"], optional

    ids : List[str], optional

    job_ref : str
        Job reference. This can be of the form J-number or job name.

    Returns
    --------
    JobResponse


    Examples
    --------
    >>> # create temp job
    >>> job_response = create_job(
    >>>     name="close_Job"
    >>> )
    >>>
    >>> # link a request to the job
    >>> indic_response = request_bond_indic_async_get(id="999818YT",
    >>>                                               id_type=IdTypeEnum.CUSIP,
    >>>                                               job=job_response.id
    >>>         )
    >>>
    >>> # close job
    >>> close_job_response = close_job(job_ref="close_Job")
    >>>
    >>> # provide a window of time for job to finish
    >>> time.sleep(10)
    >>>
    >>> # resubmit job
    >>> response = resubmit_job(job_ref=job_response.name, ids=[job_response.id], scope='OK')
    >>>
    >>> print(js.dumps(response.as_dict(), indent=4))
    {
        "id": "J-3640",
        "sequence": 0,
        "asOf": "2025-08-19",
        "closed": true,
        "onHold": false,
        "aborted": false,
        "actualHold": false,
        "name": "close_Job",
        "priority": 0,
        "order": "FAST",
        "requestCount": 1,
        "pendingCount": 1,
        "runningCount": 0,
        "okCount": 0,
        "errorCount": 0,
        "abortedCount": 0,
        "skipCount": 0,
        "startAfter": "2025-08-19T02:32:47.696Z",
        "stopAfter": "2025-08-20T02:32:47.696Z",
        "createdAt": "2025-08-19T02:32:47.698Z",
        "updatedAt": "2025-08-19T02:32:58.769Z"
    }

    """

    try:
        logger.info("Calling resubmit_job")

        response = Client().yield_book_rest.resubmit_job(
            body=JobResubmissionRequest(scope=scope, ids=ids), job_ref=job_ref
        )

        output = response
        logger.info("Called resubmit_job")

        return output
    except Exception as err:
        logger.error("Error resubmit_job.")
        check_exception_and_raise(err, logger)


def upload_csv_job_data_async(
    *,
    data: str,
    job: str,
    store_type: Union[str, StoreType],
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Async upload csv job data.

    Parameters
    ----------
    data : str
        A sequence of textual characters.
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    name : str, optional
        A sequence of textual characters.
    pri : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling upload_csv_job_data_async")

        response = Client().yield_book_rest.upload_csv_job_data_async(
            job=job,
            store_type=store_type,
            name=name,
            pri=pri,
            tags=tags,
            content_type="text/csv",
            data=data,
        )

        output = response
        logger.info("Called upload_csv_job_data_async")

        return output
    except Exception as err:
        logger.error("Error upload_csv_job_data_async.")
        check_exception_and_raise(err, logger)


def upload_csv_job_data_sync(
    *,
    data: str,
    job: str,
    store_type: Union[str, StoreType],
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Sync upload csv job data.

    Parameters
    ----------
    data : str
        A sequence of textual characters.
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    name : str, optional
        A sequence of textual characters.
    pri : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling upload_csv_job_data_sync")

        response = Client().yield_book_rest.upload_csv_job_data_sync(
            job=job,
            store_type=store_type,
            name=name,
            pri=pri,
            tags=tags,
            content_type="text/csv",
            data=data,
        )

        output = response
        logger.info("Called upload_csv_job_data_sync")

        return output
    except Exception as err:
        logger.error("Error upload_csv_job_data_sync.")
        check_exception_and_raise(err, logger)


def upload_csv_job_data_with_name_async(
    *,
    data: str,
    job: str,
    store_type: Union[str, StoreType],
    request_name: str,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Async upload csv job data with a user-provided name.

    Parameters
    ----------
    data : str
        A sequence of textual characters.
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    request_name : str
        User provided name for the request
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling upload_csv_job_data_with_name_async")

        response = Client().yield_book_rest.upload_csv_job_data_with_name_async(
            job=job,
            store_type=store_type,
            request_name=request_name,
            pri=pri,
            tags=tags,
            content_type="text/csv",
            data=data,
        )

        output = response
        logger.info("Called upload_csv_job_data_with_name_async")

        return output
    except Exception as err:
        logger.error("Error upload_csv_job_data_with_name_async.")
        check_exception_and_raise(err, logger)


def upload_csv_job_data_with_name_sync(
    *,
    data: str,
    job: str,
    store_type: Union[str, StoreType],
    request_name: str,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Sync upload csv job with a user-provided name.

    Parameters
    ----------
    data : str
        A sequence of textual characters.
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    request_name : str
        User provided name for the request
    pri : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling upload_csv_job_data_with_name_sync")

        response = Client().yield_book_rest.upload_csv_job_data_with_name_sync(
            job=job,
            store_type=store_type,
            request_name=request_name,
            pri=pri,
            tags=tags,
            content_type="text/csv",
            data=data,
        )

        output = response
        logger.info("Called upload_csv_job_data_with_name_sync")

        return output
    except Exception as err:
        logger.error("Error upload_csv_job_data_with_name_sync.")
        check_exception_and_raise(err, logger)


def upload_json_job_data_async(
    *,
    data: JobStoreInputData,
    job: str,
    store_type: Union[str, StoreType],
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Async upload json job data.

    Parameters
    ----------
    data : JobStoreInputData

    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    name : str, optional
        A sequence of textual characters.
    pri : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling upload_json_job_data_async")

        response = Client().yield_book_rest.upload_json_job_data_async(
            job=job,
            store_type=store_type,
            name=name,
            pri=pri,
            tags=tags,
            content_type="application/json",
            data=data,
        )

        output = response
        logger.info("Called upload_json_job_data_async")

        return output
    except Exception as err:
        logger.error("Error upload_json_job_data_async.")
        check_exception_and_raise(err, logger)


def upload_json_job_data_sync(
    *,
    data: JobStoreInputData,
    job: str,
    store_type: Union[str, StoreType],
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Sync upload json job data.

    Parameters
    ----------
    data : JobStoreInputData

    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    name : str, optional
        A sequence of textual characters.
    pri : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling upload_json_job_data_sync")

        response = Client().yield_book_rest.upload_json_job_data_sync(
            job=job,
            store_type=store_type,
            name=name,
            pri=pri,
            tags=tags,
            content_type="application/json",
            data=data,
        )

        output = response
        logger.info("Called upload_json_job_data_sync")

        return output
    except Exception as err:
        logger.error("Error upload_json_job_data_sync.")
        check_exception_and_raise(err, logger)


def upload_json_job_data_with_name_async(
    *,
    data: JobStoreInputData,
    job: str,
    store_type: Union[str, StoreType],
    request_name: str,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Async upload json job data with a user-provided name.

    Parameters
    ----------
    data : JobStoreInputData

    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    request_name : str
        User provided name for the request
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling upload_json_job_data_with_name_async")

        response = Client().yield_book_rest.upload_json_job_data_with_name_async(
            job=job,
            store_type=store_type,
            request_name=request_name,
            pri=pri,
            tags=tags,
            content_type="application/json",
            data=data,
        )

        output = response
        logger.info("Called upload_json_job_data_with_name_async")

        return output
    except Exception as err:
        logger.error("Error upload_json_job_data_with_name_async.")
        check_exception_and_raise(err, logger)


def upload_json_job_data_with_name_sync(
    *,
    data: JobStoreInputData,
    job: str,
    store_type: Union[str, StoreType],
    request_name: str,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Sync upload json job data with a user-provided name.

    Parameters
    ----------
    data : JobStoreInputData

    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    request_name : str
        User provided name for the request
    pri : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling upload_json_job_data_with_name_sync")

        response = Client().yield_book_rest.upload_json_job_data_with_name_sync(
            job=job,
            store_type=store_type,
            request_name=request_name,
            pri=pri,
            tags=tags,
            content_type="application/json",
            data=data,
        )

        output = response
        logger.info("Called upload_json_job_data_with_name_sync")

        return output
    except Exception as err:
        logger.error("Error upload_json_job_data_with_name_sync.")
        check_exception_and_raise(err, logger)


def upload_text_job_data_async(
    *,
    data: str,
    job: str,
    store_type: Union[str, StoreType],
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Async upload text job data.

    Parameters
    ----------
    data : str
        A sequence of textual characters.
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    name : str, optional
        A sequence of textual characters.
    pri : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling upload_text_job_data_async")

        response = Client().yield_book_rest.upload_text_job_data_async(
            job=job,
            store_type=store_type,
            name=name,
            pri=pri,
            tags=tags,
            content_type="text/plain",
            data=data,
        )

        output = response
        logger.info("Called upload_text_job_data_async")

        return output
    except Exception as err:
        logger.error("Error upload_text_job_data_async.")
        check_exception_and_raise(err, logger)


def upload_text_job_data_sync(
    *,
    data: str,
    job: str,
    store_type: Union[str, StoreType],
    name: Optional[str] = None,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Sync upload text job data.

    Parameters
    ----------
    data : str
        A sequence of textual characters.
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    name : str, optional
        A sequence of textual characters.
    pri : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling upload_text_job_data_sync")

        response = Client().yield_book_rest.upload_text_job_data_sync(
            job=job,
            store_type=store_type,
            name=name,
            pri=pri,
            tags=tags,
            content_type="text/plain",
            data=data,
        )

        output = response
        logger.info("Called upload_text_job_data_sync")

        return output
    except Exception as err:
        logger.error("Error upload_text_job_data_sync.")
        check_exception_and_raise(err, logger)


def upload_text_job_data_with_name_async(
    *,
    data: str,
    job: str,
    store_type: Union[str, StoreType],
    request_name: str,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> RequestId:
    """
    Async upload text job data with a user-provided name.

    Parameters
    ----------
    data : str
        A sequence of textual characters.
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    request_name : str
        User provided name for the request
    pri : int, optional
        Priority for this request in the queue.
    tags : List[str], optional


    Returns
    --------
    RequestId


    Examples
    --------


    """

    try:
        logger.info("Calling upload_text_job_data_with_name_async")

        response = Client().yield_book_rest.upload_text_job_data_with_name_async(
            job=job,
            store_type=store_type,
            request_name=request_name,
            pri=pri,
            tags=tags,
            content_type="text/plain",
            data=data,
        )

        output = response
        logger.info("Called upload_text_job_data_with_name_async")

        return output
    except Exception as err:
        logger.error("Error upload_text_job_data_with_name_async.")
        check_exception_and_raise(err, logger)


def upload_text_job_data_with_name_sync(
    *,
    data: str,
    job: str,
    store_type: Union[str, StoreType],
    request_name: str,
    pri: Optional[int] = None,
    tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Sync upload text job data with a user-provided name.

    Parameters
    ----------
    data : str
        A sequence of textual characters.
    job : str
        Job reference. This can be of the form J-number or job name.
    store_type : Union[str, StoreType]
        Job store object type. Should be one of the enumerated types.
    request_name : str
        User provided name for the request
    pri : int, optional
        A 32-bit integer. (`-2,147,483,648` to `2,147,483,647`)
    tags : List[str], optional


    Returns
    --------
    Dict[str, Any]


    Examples
    --------


    """

    try:
        logger.info("Calling upload_text_job_data_with_name_sync")

        response = Client().yield_book_rest.upload_text_job_data_with_name_sync(
            job=job,
            store_type=store_type,
            request_name=request_name,
            pri=pri,
            tags=tags,
            content_type="text/plain",
            data=data,
        )

        output = response
        logger.info("Called upload_text_job_data_with_name_sync")

        return output
    except Exception as err:
        logger.error("Error upload_text_job_data_with_name_sync.")
        check_exception_and_raise(err, logger)
