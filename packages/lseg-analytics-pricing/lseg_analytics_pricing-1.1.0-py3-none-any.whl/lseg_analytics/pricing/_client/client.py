from corehttp.rest import HttpRequest
from corehttp.rest._rest_py3 import _HttpResponseBase as SansIOHttpResponse
from corehttp.runtime.policies import SansIOHTTPPolicy
from lseg_analytics.core.sdk_session import SDKSession

from .. import __version__
from .._basic_client import AnalyticsAPIClient

__all__ = [
    "Client",
]

HTTPRequestType = HttpRequest
HTTPResponseType = SansIOHttpResponse


class CustomSDKPolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):
    """Custom Policy for decoding response of Rest Yield Book CSV related endpoints
    which don't have 'Content-Type' in the response."""

    def on_response(self, request, response):
        if "/results/bulk/csv" in response.http_response.url and response.http_response.status_code == 200:
            response.http_response._content_type = "text/csv"
        return super().on_response(request, response)


class Client:
    @classmethod
    def reload(cls):
        SDKSession.reload()
        cls._instance = None

    def __new__(cls):
        if not getattr(cls, "_instance", None):

            from corehttp.runtime.policies import (
                ContentDecodePolicy,
                NetworkTraceLoggingPolicy,
                ProxyPolicy,
                RetryPolicy,
                UserAgentPolicy,
            )

            logging_policy = NetworkTraceLoggingPolicy()
            logging_policy.enable_http_logger = True
            policies = [
                SDKSession()._headers_policy,
                UserAgentPolicy(user_agent=f"lseg-analytics-pricing/{__version__}"),
                ProxyPolicy(),
                ContentDecodePolicy(),
                RetryPolicy(),
                CustomSDKPolicy(),
                SDKSession()._authentication_policy,
                logging_policy,
            ]
            cls._instance = AnalyticsAPIClient(
                endpoint=SDKSession()._base_url,
                username=SDKSession()._username,
                policies=policies,
            )
            cls._instance._config.headers_policy = SDKSession()._headers_policy
            cls._instance._config.authentication_policy = SDKSession()._authentication_policy
            cls._instance._config.logging_policy = logging_policy
        return cls._instance
