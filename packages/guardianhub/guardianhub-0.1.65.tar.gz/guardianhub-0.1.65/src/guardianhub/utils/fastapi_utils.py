"""Common FastAPI utilities and middleware for Guardian Hub services."""
import uuid
from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .app_state import AppState
from .metrics import setup_metrics, get_metrics_registry
from guardianhub import get_logger

logger = get_logger(__name__)


def setup_middleware(app: FastAPI, settings: Any) -> None:
    """Set up common middleware for FastAPI applications.

    Args:
        app: The FastAPI application instance
        settings: Application settings containing CORS and other configurations
    """
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    
    # Set up metrics
    metrics = setup_metrics(settings.service.name)
    
    # Add request tracking middleware
    app.middleware('http')(create_request_tracking_middleware(metrics, app.state.app_state))


def create_request_tracking_middleware(metrics: Dict[str, Any], app_state: AppState):
    """Create request tracking middleware with metrics and logging.

    Args:
        metrics: Dictionary containing metric objects
        app_state: Application state for tracking

    Returns:
        Async middleware function
    """
    request_count = metrics['request_count']
    request_latency = metrics['request_latency']
    active_requests = metrics['active_requests']

    async def middleware(request: Request, call_next):
        # Skip tracking for health checks and metrics
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)

        # Track request start time
        start_time = datetime.now().timestamp()
        active_requests.inc()
        app_state.increment("active_requests")
        app_state.increment("total_requests")

        try:
            # Process the request
            response = await call_next(request)
            process_time = datetime.now().timestamp() - start_time

            # Record metrics
            request_latency.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(process_time)

            request_count.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code
            ).inc()

            # Log the request
            logger.info(
                f"Request: {request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Process Time: {process_time * 1000:.2f}ms"
            )

            # Add response headers
            response.headers["X-Process-Time"] = f"{process_time * 1000:.2f}ms"
            response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", str(uuid.uuid4()))

            return response

        except Exception as e:
            # Log unhandled exceptions
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            raise

        finally:
            # Ensure we always decrement active requests
            active_requests.dec()
            app_state.decrement("active_requests")

    return middleware


def setup_health_endpoint(app: FastAPI, service_name: str, app_state: AppState):
    """Set up a standard health check endpoint.

    Args:
        app: FastAPI application instance
        service_name: Name of the service
        app_state: Application state for health checks
    """
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": service_name,
            "version": "0.1",
            "uptime": (datetime.now() - app_state.get("startup_time")).total_seconds(),
            "active_requests": app_state.get("active_requests", 0),
            "total_requests": app_state.get("total_requests", 0)
        }


def setup_metrics_endpoint(app: FastAPI):
    """Set up a standard metrics endpoint for Prometheus."""
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint."""
        registry = get_metrics_registry()
        if registry is None:
            return Response("Metrics not initialized", status_code=500)
            
        return Response(
            content=generate_latest(registry),
            media_type=CONTENT_TYPE_LATEST
        )
