"""Metrics utilities and middleware."""

import time
from collections import defaultdict, deque
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class MetricsCollector:
    """Simple in-memory metrics collector."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.request_count: defaultdict[str, int] = defaultdict(int)
        self.request_duration: defaultdict[str, deque[float]] = defaultdict(deque)
        self.error_count: defaultdict[str, int] = defaultdict(int)
        self.start_time = time.time()

    def record_request(
        self, method: str, path: str, status_code: int, duration: float
    ) -> None:
        """Record a request metric."""
        route_key = f"{method}:{path}"

        # Count requests
        self.request_count[route_key] += 1

        # Store duration (keep last 1000 requests)
        self.request_duration[route_key].append(duration)
        if len(self.request_duration[route_key]) > 1000:
            self.request_duration[route_key].popleft()

        # Count errors (4xx and 5xx)
        if status_code >= 400:
            self.error_count[route_key] += 1

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics summary."""
        total_requests = sum(self.request_count.values())
        total_errors = sum(self.error_count.values())
        uptime = time.time() - self.start_time

        # Calculate average response times
        avg_response_times = {}
        for route, durations in self.request_duration.items():
            if durations:
                avg_response_times[route] = sum(durations) / len(durations)

        return {
            "service": self.service_name,
            "uptime_seconds": uptime,
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": total_errors / total_requests if total_requests > 0 else 0,
            "requests_per_second": total_requests / uptime if uptime > 0 else 0,
            "routes": {
                "request_count": dict(self.request_count),
                "error_count": dict(self.error_count),
                "avg_response_time": avg_response_times,
            },
        }


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP request metrics."""

    def __init__(self, app: Any, collector: MetricsCollector) -> None:
        super().__init__(app)
        self.collector = collector

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Process request and collect metrics."""
        start_time = time.time()

        # Get route pattern if available
        route_path = request.url.path
        if hasattr(request, "scope") and "route" in request.scope:
            route = request.scope["route"]
            if hasattr(route, "path"):
                route_path = route.path

        # Process request
        response: Response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Record metrics
        self.collector.record_request(
            method=request.method,
            path=route_path,
            status_code=response.status_code,
            duration=duration,
        )

        # Add metrics headers
        response.headers["X-Response-Time"] = f"{duration:.4f}s"

        return response


# Global metrics collector
_metrics_collector: MetricsCollector | None = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        raise RuntimeError("Metrics collector not initialized.")
    return _metrics_collector


def create_metrics_middleware(service_name: str) -> type:
    """Create metrics middleware for the given service.

    Args:
        service_name: Name of the service

    Returns:
        Middleware class configured for the service
    """
    global _metrics_collector

    # Initialize metrics collector
    _metrics_collector = MetricsCollector(service_name)

    # Create middleware class
    class ServiceMetricsMiddleware(MetricsMiddleware):
        def __init__(self, app):
            if _metrics_collector is None:
                raise RuntimeError("Metrics collector not initialized")
            super().__init__(app, _metrics_collector)

    return ServiceMetricsMiddleware


def create_metrics_router():
    """Create router with metrics endpoints."""
    from fastapi import APIRouter, Depends

    router = APIRouter(prefix="/metrics", tags=["Metrics"])

    @router.get("/")
    async def get_metrics(
        collector: MetricsCollector = Depends(get_metrics_collector),  # noqa: B008
    ) -> dict:
        """Get service metrics."""
        return collector.get_metrics()

    @router.get("/prometheus")
    async def get_prometheus_metrics(
        collector: MetricsCollector = Depends(get_metrics_collector),  # noqa: B008
    ) -> Response:
        """Get metrics in Prometheus format."""
        metrics = collector.get_metrics()

        # Simple Prometheus format
        lines = [
            f'# HELP {metrics["service"]}_uptime_seconds Service uptime in seconds',
            f'# TYPE {metrics["service"]}_uptime_seconds gauge',
            f'{metrics["service"]}_uptime_seconds {metrics["uptime_seconds"]}',
            "",
            f'# HELP {metrics["service"]}_requests_total Total requests',
            f'# TYPE {metrics["service"]}_requests_total counter',
            f'{metrics["service"]}_requests_total {metrics["total_requests"]}',
            "",
            f'# HELP {metrics["service"]}_errors_total Total errors',
            f'# TYPE {metrics["service"]}_errors_total counter',
            f'{metrics["service"]}_errors_total {metrics["total_errors"]}',
            "",
        ]

        # Add per-route metrics
        for route, count in metrics["routes"]["request_count"].items():
            lines.extend(
                [
                    f'# HELP {metrics["service"]}_route_requests_total '
                    f"Total requests for route {route}",
                    f'# TYPE {metrics["service"]}_route_requests_total counter',
                    f'{metrics["service"]}_route_requests_total'
                    f'{{route="{route}"}} {count}',
                    "",
                ]
            )

        return Response(content="\n".join(lines), media_type="text/plain")

    return router
