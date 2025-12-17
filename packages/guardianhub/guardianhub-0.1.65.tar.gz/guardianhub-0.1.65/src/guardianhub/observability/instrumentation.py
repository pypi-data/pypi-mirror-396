"""
Centralized OpenTelemetry instrumentation and observability configuration.

This module provides a consistent way to configure distributed tracing and metrics
across all services in the GuardianHub ecosystem. It sets up:

1. Distributed Tracing:
   - Automatic instrumentation for FastAPI (incoming requests)
   - HTTPX client instrumentation (outgoing requests)
   - OTLP export for centralized trace collection

2. Metrics:
   - System and application metrics
   - OTLP export for metrics collection

3. Context Propagation:
   - Ensures trace context is propagated across service boundaries (CRITICAL for Langfuse integration)
   - Integrates with Langfuse for LLM/agent tracing

The module follows OpenTelemetry best practices and provides sensible defaults
while remaining configurable for different deployment environments.
"""

import os
from typing import Optional

# Imports for resilient HTTP session configuration
import requests
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    ConsoleMetricExporter
)
from opentelemetry.sdk.resources import (
    SERVICE_NAME,
    Resource,
    SERVICE_VERSION,
    DEPLOYMENT_ENVIRONMENT
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from guardianhub import get_logger

logger = get_logger(__name__)

os.environ["LANGFUSE_HOST"] = "http://langfuse.guardianhub.com:3000"
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-f3b04336-2808-4dc1-a83d-aa7944aee2f7"
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-737015da-d020-4914-9813-ecb45bdb42f3"

def configure_instrumentation(
    app,
    service_name: str,
    environment: Optional[str] = None,
    service_version: Optional[str] = None,
    otlp_endpoint: Optional[str] = None,
    enable_console_export: bool = False,
    excluded_urls: str = "/health,/metrics",
    add_body_preview_middleware: bool = False,
    httpx_excluded_urls: str = "/health,/metrics",
) -> None:
    """Configure OpenTelemetry instrumentation for the application.

    Args:
        app: The FastAPI application instance to instrument
        service_name: Name of the service for resource identification
        environment: Deployment environment (defaults to ENV var or 'development')
        service_version: Service version string (defaults to ENV var or '0.1.0')
        otlp_endpoint: Base URL for OTLP collector (defaults to OTEL_EXPORTER_OTLP_ENDPOINT)
        enable_console_export: If True, export traces/metrics to console
        excluded_urls: Comma-separated URLs to exclude from tracing
    """
    # 1. Resolve configuration variables
    environment = environment or os.getenv('ENVIRONMENT', 'development')
    service_version = service_version or os.getenv('SERVICE_VERSION', '0.1.0')

    # Default to the known Kubernetes OTLP Collector service if the environment variable is missing.
    # We use the service-name.namespace:port format for cross-namespace communication.
    # default_otlp_endpoint = "http://otel-collector-service.monitoring.svc.cluster.local:4318"
    # otlp_endpoint = otlp_endpoint or os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
    #
    # # Ensure the endpoint doesn't have a trailing slash, as the exporter needs the clean base URL
    # if otlp_endpoint:
    #     otlp_endpoint = otlp_endpoint.rstrip('/')

    logger.info(
        "Configuring OpenTelemetry instrumentation",
        extra={
            "service_name": service_name,
            "environment": environment,
            "version": service_version,
            "otlp_endpoint": otlp_endpoint if otlp_endpoint else "Not configured"
        }
    )

    try:
        # 2. Create resource with service metadata
        resource = Resource.create(
            attributes={
                SERVICE_NAME: service_name,
                SERVICE_VERSION: service_version,
                DEPLOYMENT_ENVIRONMENT: environment,
                "service.namespace": "guardianhub",
            }
        )

        # # 2.5. Configure global context propagation using W3C Trace Context
        # set_global_textmap(TraceContextTextMapPropagator())
        # logger.info("Configured W3C Trace Context Propagator for context propagation")

        # 3. Configure tracing
        _setup_tracing(resource, otlp_endpoint, enable_console_export)

        # 4. Configure metrics
        _setup_metrics(resource, otlp_endpoint, enable_console_export)

        # 5. Instrument libraries
        # Preferred path: pass request/response hooks if supported
        FastAPIInstrumentor.instrument_app(
            app=app,
            tracer_provider=trace.get_tracer_provider(),
            excluded_urls=excluded_urls,
            # server_request_hook=server_request_hook,
            # server_response_hook=server_response_hook,
        )
        logger.info("Instrumented FastAPI application", extra={"excluded_urls": excluded_urls})

        HTTPXClientInstrumentor().instrument(
            excluded_urls=httpx_excluded_urls,
            # request_hook=client_request_hook,
            # response_hook=client_response_hook,
        )

        logger.info("Instrumented HTTPX clients for outbound requests")
        logger.info("OpenTelemetry instrumentation configured successfully")

    except Exception as e:
        logger.error(
            "Failed to configure OpenTelemetry instrumentation. Continuing without full tracing/metrics.",
            exc_info=True,
            extra={"error": str(e)}
        )
        # Note: We catch the error but don't re-raise, allowing the application to start
        # but with reduced observability. This is typically safer than failing startup.

def _setup_tracing(resource: Resource, otlp_endpoint: Optional[str], console_export: bool) -> None:
    """Configure and initialize OpenTelemetry tracing."""
    logger.debug("Configuring tracing subsystem")
    tracer_provider = TracerProvider(resource=resource)

    # 2. OTLP Exporter
    try:
        # The Python SDK must be trusted to append '/v1/traces' internally,
        # as demonstrated by the successful curl test to the collector.
        # Langfuse acts as an OTEL receiver via OTLP
        langfuse_base_url = "http://langfuse.guardianhub.com:4318"
        langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")

        otlp_exporter = OTLPSpanExporter(
            endpoint=f"{langfuse_base_url}/v1/traces",
            headers={
                "x-langfuse-public-key": langfuse_public_key,
                "x-langfuse-secret-key": langfuse_secret_key,
            }
        )

        otlp_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider.add_span_processor(otlp_processor)

        logger.info("Configured OTLP trace exporter", extra={"endpoint": f"{otlp_endpoint}/v1/traces (internal path)"})
        logger.info(f"{otlp_endpoint}/v1/traces (internal path)")

        trace.set_tracer_provider(tracer_provider)
    except Exception as e:
        # Only log the error, don't crash startup if the collector is unreachable
        logger.warning(
            "Failed to configure OTLP trace exporter. Check endpoint and network access.",
            extra={"endpoint": otlp_endpoint, "error": str(e)}
        )


def _setup_metrics(resource: Resource, otlp_endpoint: Optional[str], console_export: bool) -> None:
    """Configure and initialize OpenTelemetry metrics."""
    logger.debug("Configuring metrics subsystem")

    metric_readers = []

    # 1. Console Exporter
    if console_export:
        # Wrap the ConsoleMetricExporter in a PeriodicExportingMetricReader
        metric_readers.append(
            PeriodicExportingMetricReader(
                ConsoleMetricExporter()
            )
        )
        logger.debug("Enabled console metrics export")

    # 2. OTLP Exporter
    if otlp_endpoint:
        try:
            # Create a resilient HTTP session for the exporter
            otlp_session = _create_otlp_session()
            full_otlp_metrics_endpoint = f"{otlp_endpoint}/v1/metrics"

            # FIX for 404 error: Revert the explicit path addition.
            # The Python SDK must be trusted to append '/v1/metrics' internally.
            otlp_exporter = OTLPMetricExporter(
                endpoint=full_otlp_metrics_endpoint,
                session=otlp_session
            )
            # Wrap the OTLPMetricExporter in a PeriodicExportingMetricReader
            metric_readers.append(
                PeriodicExportingMetricReader(otlp_exporter)
            )
            logger.info("Configured OTLP metrics exporter", extra={"endpoint": f"{otlp_endpoint}/v1/metrics (internal path)"})
        except Exception as e:
            # Only log the error, don't crash startup if the collector is unreachable
            logger.warning(
                "Failed to configure OTLP metrics exporter. Check endpoint and network access.",
                extra={"endpoint": otlp_endpoint, "error": str(e)}
            )

    if metric_readers:
        # Set the MeterProvider only if at least one reader is successfully configured
        metrics.set_meter_provider(
            MeterProvider(
                resource=resource,
                metric_readers=metric_readers
            )
        )
    else:
        logger.info("No OTLP endpoint or console export enabled. Metrics will not be exported.")

def _create_otlp_session() -> requests.Session:
    """
    Creates a requests session configured for robust OTLP export retries.

    This helps handle transient network failures (like 'Connection refused'
    during service startup) in Kubernetes environments.
    """
    # Configure retry strategy: 5 total retries with 1 second backoff factor
    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
        # Includes connection errors and typical server errors
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(['POST']),
        # We allow the underlying connection errors to trigger retries
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    # Apply the resilient adapter to both HTTP and HTTPS protocols
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def get_meter(name: str) -> metrics.Meter:
    """Get a meter instance with the given name."""
    return metrics.get_meter(name)
