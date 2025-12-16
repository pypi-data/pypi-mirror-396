import os
import logging
import functools
import time
import socket
from urllib.parse import urljoin
from contextlib import ContextDecorator
from typing import Optional, Dict

from opentelemetry import trace
from opentelemetry.baggage import get_baggage, set_baggage
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import AggregationTemporality
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SpanExporter,
    SpanExportResult,
)

from opentelemetry import metrics
from opentelemetry.metrics import Counter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    MetricExporter,
    MetricExportResult,
)

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor


class NoopSpanExporter(SpanExporter):
    """Noop span exporter that does nothing."""

    def export(self, spans):
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass


class NoopMetricExporter(MetricExporter):
    """Noop metric exporter that does nothing."""

    def export(self, metrics_data, timeout_millis=None):
        return MetricExportResult.SUCCESS

    def shutdown(self, timeout_millis=None):
        pass

    def force_flush(self, timeout_millis=None):
        return True


def _get_service_name() -> str:
    """
    Get the service name for telemetry.

    Priority:
    1. HMD_OTEL_SERVICE_NAME environment variable
    2. Combination of HMD_INSTANCE_NAME and HMD_REPO_NAME
    3. Hostname
    """
    service_name = os.environ.get("HMD_OTEL_SERVICE_NAME")
    if service_name:
        return service_name

    instance_name = os.environ.get("HMD_INSTANCE_NAME")
    repo_name = os.environ.get("HMD_REPO_NAME")

    if instance_name and repo_name:
        return f"{instance_name}-{repo_name}"

    return socket.gethostname()


def _create_resource(
    service_name: Optional[str] = None,
    resource_attributes: Optional[Dict[str, str]] = None,
) -> Resource:
    """
    Create an OpenTelemetry Resource with service attributes.

    Args:
        service_name: Optional service name override
        resource_attributes: Optional dictionary of additional resource attributes

    Returns:
        Resource with service attributes
    """
    if service_name is None:
        service_name = _get_service_name()

    attributes = {
        SERVICE_NAME: service_name,
        "instance_name": os.environ.get("HMD_INSTANCE_NAME"),
        "repo_name": os.environ.get("HMD_REPO_NAME"),
        "version": os.environ.get("HMD_REPO_VERSION"),
        "env": f"{os.environ.get('HMD_ENVIRONMENT')}_{os.environ.get('HMD_REGION')}_{os.environ.get('HMD_CUSTOMER_CODE')}",
        "environment": os.environ.get("HMD_ENVIRONMENT"),
        "deployment_id": os.environ.get("HMD_DID"),
        "customer_code": os.environ.get("HMD_CUSTOMER_CODE"),
        "hostname": socket.gethostname(),
    }

    # Merge in additional resource attributes if provided
    if resource_attributes:
        attributes.update(resource_attributes)

    return Resource(attributes=attributes)


# Global state for tracking providers (declared early for initial setup)
_current_metric_provider: Optional[MeterProvider] = None
_current_trace_provider: Optional[TracerProvider] = None
_current_logger_provider: Optional[LoggerProvider] = None


class HmdTracer:
    def __init__(self, name: str):
        self.tracer = trace.get_tracer(name)

    def start_span(self, name: str, context=None, attributes=None):
        kwargs = {}
        if context is not None:
            kwargs["context"] = context
        if attributes is not None:
            kwargs["attributes"] = attributes
        # Start a span with the given name, context, and attributes
        return self.tracer.start_as_current_span(name, **kwargs)

    def add_event(self, title: str, attributes=None):
        trace.get_current_span().add_event(title, attributes=attributes)

    def error(self, title, attributes=None):
        attrs = {"type": "error"}
        if attributes is not None:
            attrs = {**attrs, **attributes}

        self.add_event(title, attrs)

    def warning(self, title, attributes=None):
        attrs = {"type": "warning"}
        if attributes is not None:
            attrs = {**attrs, **attributes}

        self.add_event(title, attrs)

    def info(self, title, attributes=None):
        attrs = {"type": "info"}
        if attributes is not None:
            attrs = {**attrs, **attributes}

        self.add_event(title, attrs)

    def success(self, title, attributes=None):
        attrs = {"type": "success"}
        if attributes is not None:
            attrs = {**attrs, **attributes}

        self.add_event(title, attrs)

    def record_exception(self, ex: Exception, attributes=None):
        current_span = trace.get_current_span()
        current_span.set_status(Status(StatusCode.ERROR))
        current_span.record_exception(ex, attributes=attributes)

    def record_success(self, attributes=None):
        current_span = trace.get_current_span()
        current_span.set_status(Status(StatusCode.OK))
        if attributes is not None:
            current_span.set_attributes(attributes)

    def add_baggage(self, key: str, value: str):
        """
        Add baggage to the current span.
        """
        set_baggage(
            key,
            value,
        )

    def get_baggage(self, key: str):
        """
        Get baggage from the current span.
        """
        return get_baggage(key)


class HmdTimer(ContextDecorator):
    def __init__(self, time_counter: Counter):
        self.time_counter = time_counter

    def __call__(self, fn):
        @functools.wraps(fn)
        def wrapper_timer(*args, **kwargs):
            with self:
                value = fn(*args, **kwargs)
                return value

        return wrapper_timer

    def __enter__(self):
        self.start = time.perf_counter()

    def __exit__(self, *exc):
        stop = time.perf_counter()
        elapsed = stop - self.start
        self.time_counter.record(elapsed)
        self.start = None


class HmdMetric:
    def __init__(self, name: str):
        self.meter = metrics.get_meter(name)

    def timer(self, name: str, unit="s", description=""):
        time_counter = self.meter.create_histogram(name, unit, description)

        wrapper = HmdTimer(time_counter)
        return wrapper

    def counter(self, name: str, unit="1", description=""):
        """
        Create a counter metric.
        """
        return self.meter.create_counter(name, unit, description)

    def histogram(self, name: str, unit="1", description=""):
        """
        Create a histogram metric.
        """
        return self.meter.create_histogram(name, unit, description)

    def gauge(self, name: str, unit="1", description=""):
        """
        Create a gauge metric.
        """
        return self.meter.create_gauge(name, unit, description)

    def up_down_counter(self, name: str, unit="1", description=""):
        """
        Create an up-down counter metric.
        """
        return self.meter.create_up_down_counter(name, unit, description)


def configure_telemetry(
    otel_endpoint: Optional[str] = None,
    service_name: Optional[str] = None,
    metrics_enabled: Optional[bool] = None,
    traces_enabled: Optional[bool] = None,
    dd_enabled: Optional[bool] = None,
    dd_api_key: Optional[str] = None,
    auth_token: Optional[str] = None,
    client_certs: Optional[tuple] = None,
    resource_attributes: Optional[Dict[str, str]] = None,
) -> None:
    """
    Configure or reconfigure OpenTelemetry with new endpoints and settings.

    This function allows dynamic configuration of telemetry after the initial
    module import. It will create new providers and exporters with the specified
    configuration.

    Args:
        otel_endpoint: OTEL endpoint URL (e.g., "https://otel-collector.example.com")
        service_name: Service name override (defaults to hostname or HMD_OTEL_SERVICE_NAME)
        metrics_enabled: Whether to enable metrics collection (default: True)
        traces_enabled: Whether to enable traces collection (default: True)
        dd_enabled: Whether to enable Datadog-specific configuration (default: False)
        dd_api_key: Datadog API key (required if dd_enabled=True)
        auth_token: JWT authentication token (for OAuth2/Bearer authentication)
        client_certs: Tuple of (cert_file, key_file) paths for mTLS authentication
        resource_attributes: Optional dictionary of additional resource attributes to add

    Example:
        >>> from hmd_lib_telemetry.hmd_lib_telemetry import configure_telemetry
        >>> # Configure telemetry to send to a specific librarian
        >>> configure_telemetry(
        ...     otel_endpoint="https://librarian.example.com",
        ...     service_name="my-sync-manager",
        ...     auth_token="Bearer eyJhbGc...",
        ...     resource_attributes={"app_version": "1.2.3", "cluster": "prod"}
        ... )
    """
    global _current_metric_provider, _current_trace_provider, _current_logger_provider

    # Use defaults if not specified
    if otel_endpoint is None:
        otel_endpoint = os.environ.get("HMD_OTEL_ENDPOINT")

    if metrics_enabled is None:
        metrics_enabled = (
            os.environ.get("HMD_OTEL_METRICS_ENABLED", "true").lower() == "true"
        )

    if traces_enabled is None:
        traces_enabled = (
            os.environ.get("HMD_OTEL_TRACES_ENABLED", "true").lower() == "true"
        )

    if dd_enabled is None:
        dd_enabled = (
            os.environ.get("HMD_OTEL_DD_METRICS_ENABLED", "false").lower() == "true"
        )

    if dd_api_key is None:
        dd_api_key = os.environ.get("DD_API_KEY")

    # Create new resource
    new_resource = _create_resource(service_name, resource_attributes)

    # Configure metrics
    if metrics_enabled:
        metrics_exporter = NoopMetricExporter()
        headers = {}

        if dd_enabled:
            if not dd_api_key:
                raise ValueError("dd_api_key is required when dd_enabled=True")
            headers["dd-api-key"] = dd_api_key
            headers["dd-otel-metric-config"] = '{"resource_attributes_as_tags": true}'

        # Add authentication header if auth_token is provided
        if auth_token:
            headers["Authorization"] = (
                f"Bearer {auth_token}"
                if not auth_token.startswith("Bearer ")
                else auth_token
            )

        metrics_endpoint_url = os.environ.get(
            "HMD_OTEL_METRICS_ENDPOINT", otel_endpoint
        )
        if metrics_endpoint_url is not None:
            exporter_kwargs = {
                "endpoint": urljoin(metrics_endpoint_url, "v1/metrics"),
                "preferred_temporality": (
                    AggregationTemporality.DELTA if dd_enabled else None
                ),
            }
            if headers:
                exporter_kwargs["headers"] = headers
            if client_certs:
                exporter_kwargs["certificate_file"] = client_certs[0]
                exporter_kwargs["private_key_file"] = client_certs[1]

            metrics_exporter = OTLPMetricExporter(**exporter_kwargs)

        metric_reader = PeriodicExportingMetricReader(metrics_exporter)
        _current_metric_provider = MeterProvider(
            resource=new_resource, metric_readers=[metric_reader]
        )
        metrics.set_meter_provider(_current_metric_provider)

    # Configure traces
    _current_trace_provider = TracerProvider(resource=new_resource)

    traces_exporter = NoopSpanExporter()
    traces_endpoint_url = os.environ.get("HMD_OTEL_TRACES_ENDPOINT", otel_endpoint)

    if traces_endpoint_url is not None:
        exporter_kwargs = {"endpoint": urljoin(traces_endpoint_url, "v1/traces")}

        # Add authentication
        if auth_token:
            trace_headers = {}
            trace_headers["Authorization"] = (
                f"Bearer {auth_token}"
                if not auth_token.startswith("Bearer ")
                else auth_token
            )
            exporter_kwargs["headers"] = trace_headers

        if client_certs:
            exporter_kwargs["certificate_file"] = client_certs[0]
            exporter_kwargs["private_key_file"] = client_certs[1]

        traces_exporter = OTLPSpanExporter(**exporter_kwargs)

    processor = BatchSpanProcessor(traces_exporter)
    if traces_enabled:
        _current_trace_provider.add_span_processor(processor)

    trace.set_tracer_provider(_current_trace_provider)

    # Configure logs
    logger_endpoint_url = os.environ.get("HMD_OTEL_LOGS_ENDPOINT", otel_endpoint)
    if logger_endpoint_url is not None:
        log_headers = {}
        if dd_enabled and dd_api_key:
            log_headers["dd-api-key"] = dd_api_key
            log_headers[
                "dd-otel-metric-config"
            ] = '{"resource_attributes_as_tags": true}'

        # Add authentication header if auth_token is provided
        if auth_token:
            log_headers["Authorization"] = (
                f"Bearer {auth_token}"
                if not auth_token.startswith("Bearer ")
                else auth_token
            )

        _current_logger_provider = LoggerProvider(resource=new_resource)
        set_logger_provider(_current_logger_provider)

        exporter_kwargs = {"endpoint": urljoin(logger_endpoint_url, "v1/logs")}
        if log_headers:
            exporter_kwargs["headers"] = log_headers
        if client_certs:
            exporter_kwargs["certificate_file"] = client_certs[0]
            exporter_kwargs["private_key_file"] = client_certs[1]

        exporter = OTLPLogExporter(**exporter_kwargs)
        _current_logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(exporter)
        )
        handler = LoggingHandler(
            level=logging.NOTSET, logger_provider=_current_logger_provider
        )

        # Attach OTLP handler to root logger
        logging.getLogger().addHandler(handler)


def update_otel_endpoint(endpoint: str, service_name: Optional[str] = None) -> None:
    """
    Update the OTEL endpoint dynamically after initial configuration.

    This is a convenience function that calls configure_telemetry with the
    current settings but updates the endpoint.

    Args:
        endpoint: New OTEL endpoint URL
        service_name: Optional service name override

    Example:
        >>> from hmd_lib_telemetry.hmd_lib_telemetry import update_otel_endpoint
        >>> # Switch to a different librarian endpoint
        >>> update_otel_endpoint("https://librarian2.example.com")
    """
    configure_telemetry(otel_endpoint=endpoint, service_name=service_name)


def update_service_name(service_name: str) -> None:
    """
    Update the service name dynamically after initial configuration.

    This is a convenience function that calls configure_telemetry with the
    current settings but updates the service name.

    Args:
        service_name: New service name

    Example:
        >>> from hmd_lib_telemetry.hmd_lib_telemetry import update_service_name
        >>> # Change service name to hostname
        >>> import socket
        >>> update_service_name(socket.gethostname())
    """
    configure_telemetry(service_name=service_name)


# Initialize telemetry with default configuration from environment variables
# This is called automatically on module import
configure_telemetry()
