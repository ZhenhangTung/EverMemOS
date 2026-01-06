"""
Prometheus HTTP Metrics Middleware

Auto-instrumentation middleware for HTTP request metrics.
Inspired by Kratos, Hertz, and other microservice frameworks.

Usage:
    from fastapi import FastAPI
    from core.middleware.prometheus_middleware import PrometheusMiddleware
    
    app = FastAPI()
    app.add_middleware(PrometheusMiddleware)
"""
import re
import time
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from prometheus_client import Counter, Histogram
from core.metrics.registry import get_metrics_registry


# Pre-defined HTTP metrics (following Prometheus naming conventions)
_http_requests_total = Counter(
    name='http_requests_total',
    documentation='Total number of HTTP requests',
    labelnames=['method', 'path', 'status'],
    namespace='evermemos',
    registry=get_metrics_registry(),
)

_http_request_duration_seconds = Histogram(
    name='http_request_duration_seconds',
    documentation='HTTP request duration in seconds',
    labelnames=['method', 'path'],
    namespace='evermemos',
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=get_metrics_registry(),
)

_http_request_size_bytes = Histogram(
    name='http_request_size_bytes',
    documentation='HTTP request size in bytes',
    labelnames=['method', 'path'],
    namespace='evermemos',
    buckets=(100, 1000, 10000, 100000, 1000000, 10000000),
    registry=get_metrics_registry(),
)

_http_response_size_bytes = Histogram(
    name='http_response_size_bytes',
    documentation='HTTP response size in bytes',
    labelnames=['method', 'path'],
    namespace='evermemos',
    buckets=(100, 1000, 10000, 100000, 1000000, 10000000),
    registry=get_metrics_registry(),
)


def _normalize_path(path: str) -> str:
    """
    Normalize path to reduce cardinality.
    
    Examples:
        /api/v1/users/123 → /api/v1/users/{id}
        /api/v1/memory/abc-def-123 → /api/v1/memory/{id}
    """
    # Replace UUIDs
    path = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '{id}', path)
    # Replace numeric IDs
    path = re.sub(r'/\d+', '/{id}', path)
    return path


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Prometheus HTTP Metrics Middleware
    
    Automatically records:
    - http_requests_total (Counter): Total requests by method, path, status
    - http_request_duration_seconds (Histogram): Request latency
    - http_request_size_bytes (Histogram): Request body size
    - http_response_size_bytes (Histogram): Response body size
    
    Design inspired by:
    - Kratos (Bilibili): middleware.Middleware pattern
    - Hertz (ByteDance): promhttp.InstrumentHandler pattern
    - Go kit: endpoint.Middleware pattern
    
    Usage:
        app = FastAPI()
        app.add_middleware(PrometheusMiddleware)
    """
    
    # Paths to skip metrics collection
    SKIP_PATHS = {'/metrics', '/health', '/healthz', '/ready', '/favicon.ico'}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip metrics for certain paths
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)
        
        # Normalize path to reduce label cardinality
        path = _normalize_path(request.url.path)
        method = request.method
        
        # Record request size
        if request.headers.get('content-length'):
            request_size = int(request.headers.get('content-length', 0))
            _http_request_size_bytes.labels(method=method, path=path).observe(request_size)
        
        # Time the request
        start_time = time.perf_counter()
        status = '500'  # Default to 500 in case of unhandled exception
        
        try:
            response = await call_next(request)
            status = str(response.status_code)
        except Exception:
            raise
        finally:
            # Record metrics
            duration = time.perf_counter() - start_time
            
            _http_requests_total.labels(
                method=method,
                path=path,
                status=status,
            ).inc()
            
            _http_request_duration_seconds.labels(
                method=method,
                path=path,
            ).observe(duration)
        
        # Record response size
        if hasattr(response, 'headers') and response.headers.get('content-length'):
            response_size = int(response.headers.get('content-length', 0))
            _http_response_size_bytes.labels(method=method, path=path).observe(response_size)
        
        return response

