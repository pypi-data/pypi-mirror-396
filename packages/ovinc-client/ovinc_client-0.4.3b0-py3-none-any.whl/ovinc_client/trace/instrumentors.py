import traceback
from typing import Collection, Union

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest, HttpResponse
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.httpx import (
    HTTPXClientInstrumentor,
    RequestInfo,
    ResponseInfo,
)
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.pymysql import PyMySQLInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.trace import Span, StatusCode, format_trace_id
from redis import Redis
from requests import PreparedRequest, Response
from rest_framework import status

from ovinc_client.core.logger import logger
from ovinc_client.trace.constants import SPAN_REDIS_TYPE, SpanAttributes


def requests_hook(span: Span, request: PreparedRequest):
    """
    Http Request Hook
    """

    span.update_name(f"{request.method} {request.url}")
    span.set_attributes(
        attributes={
            SpanAttributes.HTTP_URL: request.url,
            SpanAttributes.HTTP_METHOD: request.method,
        }
    )


def response_hook(span: Span, request: Union[PreparedRequest, HttpRequest], response: Union[Response, HttpResponse]):
    """
    HTTP Response Hook
    """

    span.set_attributes(
        attributes={
            SpanAttributes.HTTP_STATUS_CODE: response.status_code,
        }
    )
    span.set_status(StatusCode.ERROR if response.status_code >= status.HTTP_400_BAD_REQUEST else StatusCode.OK)


def django_request_hook(span: Span, request: WSGIRequest):
    """
    Django Request Hook
    """

    # Set Trace ID for Request
    trace_id = span.get_span_context().trace_id
    request.otel_trace_id = format_trace_id(trace_id)


def django_response_hook(span: Span, request: HttpRequest, response: HttpResponse):
    """
    Django Response Hook
    """

    response_hook(span, request, response)


def redis_request_hook(span: Span, instance: Redis, args, kwargs):
    """
    Redis Request Hook
    """

    try:
        connection_kwargs: dict = instance.connection_pool.connection_kwargs
        host = connection_kwargs.get("host")
        port = connection_kwargs.get("port")
        db = connection_kwargs.get("db")
        span.set_attributes(
            {
                SpanAttributes.DB_INSTANCE: f"{host}/{db}",
                SpanAttributes.DB_NAME: f"{host}/{db}",
                SpanAttributes.DB_TYPE: SPAN_REDIS_TYPE,
                SpanAttributes.DB_PORT: port,
                SpanAttributes.DB_IP: host,
                SpanAttributes.DB_STATEMENT: " ".join([str(i) for i in args]),
                SpanAttributes.DB_OPERATION: str(args[0]),
            }
        )
    except Exception:  # pylint: disable=W0718
        logger.error(traceback.format_exc())


def httpx_request_hook(span: Span, request: RequestInfo):
    """
    HTTPX Request Hook
    """

    span.update_name(f"{request.method.decode()} {str(request.url)}")
    span.set_attributes(
        attributes={
            SpanAttributes.HTTP_URL: str(request.url),
            SpanAttributes.HTTP_METHOD: request.method.decode(),
        }
    )


def httpx_response_hook(span: Span, request: RequestInfo, response: ResponseInfo):
    """
    HTTPX Response Hook
    """

    span.set_attribute(SpanAttributes.HTTP_STATUS_CODE, response.status_code)
    span.set_status(StatusCode.ERROR if response.status_code >= status.HTTP_400_BAD_REQUEST else StatusCode.OK)


async def httpx_async_request_hook(span, request):
    """
    Async Request Hook
    """

    httpx_request_hook(span, request)


async def httpx_async_response_hook(span, request, response):
    """
    Async Response Hook
    """

    httpx_response_hook(span, request, response)


class Instrumentor(BaseInstrumentor):
    """
    Instrument OT
    """

    def instrumentation_dependencies(self) -> Collection[str]:
        return []

    def _instrument(self, **kwargs):
        LoggingInstrumentor().instrument()
        RequestsInstrumentor().instrument(request_hook=requests_hook, response_hook=response_hook)
        DjangoInstrumentor().instrument(request_hook=django_request_hook, response_hook=django_response_hook)
        CeleryInstrumentor().instrument()
        RedisInstrumentor().instrument(request_hook=redis_request_hook)
        HTTPXClientInstrumentor().instrument(
            request_hook=httpx_request_hook,
            response_hook=httpx_response_hook,
            async_request_hook=httpx_async_request_hook,
            async_response_hook=httpx_async_response_hook,
        )
        PyMySQLInstrumentor().instrument()

    def _uninstrument(self, **kwargs):
        if getattr(self, "instrumentors", None) is None:
            return
        for instrumentor in self.instrumentors:  # pylint: disable=E1101
            instrumentor.uninstrument()
