from contextlib import asynccontextmanager

from fastapi import FastAPI

from concurrency.service import ConcurrencyService
from notifications.config import NotificationClientConfig
from notifications.client import NotificationClient
from notifications.service import NotificationService
from requests import router as requests_router
from requests.service import RequestService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await notification_service.start()

    app.state.request_service = request_service
    app.state.concurrency_service = concurrency_service
    app.state.notification_client = notification_client
    app.state.notification_service = notification_service
    
    yield
    
    # Shutdown
    await notification_service.stop()
    await notification_client.close()


request_service = RequestService()
concurrency_service = ConcurrencyService()
notification_client_config = NotificationClientConfig(
    base_url='http://localhost:3001',
    auth_header={'X-API-Key': 'test-dev-2026'},
    max_retries=3
)
notification_client = NotificationClient(notification_client_config,
                                        request_service)
notification_service = NotificationService(concurrency_service,
                                            notification_client)

app = FastAPI(
    title='Notification Service (Technical Test)',
    lifespan=lifespan
)
app.include_router(requests_router.router)
