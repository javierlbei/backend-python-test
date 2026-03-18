"""Application bootstrap and dependency wiring for the API service."""

from contextlib import asynccontextmanager
import logging

from circuitbreaker import CircuitBreaker
from fastapi import FastAPI
from fastapi_timeout import TimeoutMiddleware
from httpx import AsyncClient

from concurrency.service import ConcurrencyService
from notifications.client import NotificationClient
from requests import router as requests_router
from requests.service import RequestService


_logger = logging.getLogger('uvicorn.error')


PROVIDER_BASE_URL = 'http://localhost:3001'
PROVIDER_AUTH_HEADER = {'X-API-Key': 'test-dev-2026'}
MAX_RETRIES = 3
FAIL_THRESHOLD = 1
RESET_TIMEOUT = 60
NUM_WORKERS = 10

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Manages application startup and shutdown lifecycle.

    On startup, starts the request service and attaches shared services to
    the FastAPI application state. On shutdown, stops the request service
    and closes the notification client.

    Args:
        fastapi_app (FastAPI): The FastAPI application instance.

    Yields:
        None: Control is yielded to the application between startup and
            shutdown phases.
    """

    # Startup
    _logger.info('Starting application services')
    await request_service.start()

    fastapi_app.state.concurrency_service = concurrency_service
    fastapi_app.state.request_service = request_service

    yield

    # Shutdown
    _logger.info('Stopping application services')
    await request_service.stop()
    await notification_client.close()


# Instantiate concurrency service
concurrency_service = ConcurrencyService()


# Instantiate notification client
notification_client = NotificationClient(
    http_client=AsyncClient(
        base_url=PROVIDER_BASE_URL,
        headers=PROVIDER_AUTH_HEADER,
    ),
    circuit_breaker=CircuitBreaker(
        failure_threshold=FAIL_THRESHOLD,
        recovery_timeout=RESET_TIMEOUT,
    ),
    max_retries=MAX_RETRIES,
)


# Instantiate request service with dependencies
request_service = RequestService(
    concurrency_service,
    notification_client,
    NUM_WORKERS,
)


# Create FastAPI app and include routes
app = FastAPI(
    title='Notification Service (Technical Test)',
    lifespan=lifespan,
)
app.include_router(requests_router.router)


# Add timeout middleware to enforce a maximum processing time per request
app.add_middleware(TimeoutMiddleware, timeout_seconds=5.0)
