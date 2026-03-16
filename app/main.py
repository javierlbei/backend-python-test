"""Application bootstrap and dependency wiring for the API service."""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi_timeout import TimeoutMiddleware

from concurrency.service import ConcurrencyService
from notifications.client import NotificationClient
from notifications.config import NotificationClientConfig
from requests import router as requests_router
from requests.service import RequestService


_logger = logging.getLogger('uvicorn.error')


PROVIDER_BASE_URL = "http://localhost:3001"
PROVIDER_AUTH_HEADER = {"X-API-Key": "test-dev-2026"}
MAX_RETRIES = 3
NUM_WORKERS = 10

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    _logger.info('Starting application services')
    await request_service.start()

    app.state.concurrency_service = concurrency_service
    app.state.request_service = request_service

    yield

    # Shutdown
    _logger.info('Stopping application services')
    await request_service.stop()
    await notification_client.close()


concurrency_service = ConcurrencyService()
notification_client_config = NotificationClientConfig(
    base_url=PROVIDER_BASE_URL,
    auth_header=PROVIDER_AUTH_HEADER,
    max_retries=MAX_RETRIES,
)
notification_client = NotificationClient(notification_client_config)
request_service = RequestService(
    concurrency_service,
    notification_client,
    NUM_WORKERS,
)

app = FastAPI(
    title="Notification Service (Technical Test)",
    lifespan=lifespan,
)
app.include_router(requests_router.router)
app.add_middleware(TimeoutMiddleware, timeout_seconds=5.0)
