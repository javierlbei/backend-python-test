"""Business logic for request lifecycle and asynchronous processing."""

import asyncio
import logging

from cache import AsyncTTL

from concurrency.service import ConcurrencyService
from notifications.client import NotificationClient
from notifications.exceptions import NotificationClientException
from requests.constants import RequestStatus
from requests.exceptions import (
    RequestServiceSaveException,
    InvalidPayloadException,
)
from requests.models import NotificationRequest
from requests.schemas import CreateRequestBody
from requests.utils import generate_payload
from repositories.exceptions import RequestRepositorySaveException
from repositories.requests import RequestRepository


class RequestService:
    """Coordinates persistence, prompt generation, and notification delivery.

    Attributes:
        _concurrency_service (ConcurrencyService): Queue and task tracker.
        _notification_client (NotificationClient): Notification transport.
        _num_tasks (int): Number of background worker tasks.
        _processing_tasks (list[asyncio.Task]): Running processor tasks.
        _requests_repository (RequestRepository): Persistence abstraction.
        _logger (logging.Logger): Service logger.
    """

    def __init__(
        self,
        concurrency_service: ConcurrencyService,
        notification_client: NotificationClient,
        num_tasks: int = 1
    ):
        """Initializes the request service dependencies.

        Args:
            concurrency_service (ConcurrencyService): Queue and synchronization
                service for background processing.
            notification_client (NotificationClient): Client responsible for
                sending notifications.
            num_tasks (int): Number of background processor tasks to spawn.
        """

        self._concurrency_service = concurrency_service
        self._notification_client = notification_client
        self._num_tasks = num_tasks
        self._processing_tasks = []
        self._requests_repository = RequestRepository()
        self._logger = logging.getLogger('uvicorn.error')

    # ---------- CRUD OPERATIONS ----------


    async def save_request(self, request: CreateRequestBody | NotificationRequest) -> str:
        """Persists a new or existing request.

        Accepts either API payload schema objects or already-built domain
        objects and writes them through the repository.

        Args:
            request (CreateRequestBody | NotificationRequest): Request content to
                persist.

        Returns:
            str: ID of the saved request.

        Raises:
            RequestServiceSaveException: If the repository cannot save the
                request.
        """

        if isinstance(request, CreateRequestBody):
            request_to_save = NotificationRequest(
                request.to,
                request.message,
                request.type,
            )
        elif isinstance(request, NotificationRequest):
            request_to_save = request
        else:
            raise InvalidPayloadException()

        try:
            saved_request_id = await self._requests_repository.save(request_to_save)
            return saved_request_id
        except RequestRepositorySaveException:
            raise RequestServiceSaveException()

    @AsyncTTL(time_to_live=600)
    async def get_request(self, request_id: str) -> NotificationRequest | None:
        """Retrieves a request by ID.

        Args:
            request_id (str): Request identifier.

        Returns:
            NotificationRequest | None: Stored request when found, otherwise ``None``.
        """

        return await self._requests_repository.get_request_by_id(request_id)

    # ---------- REQUEST PROCESSING ----------


    async def start(self):
        """Starts background request processor tasks."""

        for _ in range(self._num_tasks):
            task = asyncio.create_task(self._request_processor())
            self._processing_tasks.append(task)

    async def stop(self):
        """Stops all active processor tasks and waits for cancellation."""

        for task in self._processing_tasks:
            task.cancel()

        await asyncio.gather(*self._processing_tasks, return_exceptions=True)

    async def _request_processor(self):
        """Consumes queued requests and executes the processing pipeline.

        The pipeline updates request status, sends notifications, and stores the
        final state.

        Raises:
            asyncio.CancelledError: Raised when processor task is cancelled.
        """

        while True:
            try:
                request = await self._concurrency_service.get_next_request()

                self._logger.info('Processing request with ID: %s', request.id)

                request.status = RequestStatus.PROCESSING
                await self._requests_repository.save(request)

                try:
                    payload = await generate_payload(request)

                    await self._notification_client.send_notification(payload)

                    self._logger.info('Notification sent for request with '
                                      'ID: %s', request.id)
                    request.status = RequestStatus.SENT
                except NotificationClientException:
                    self._logger.info('Notification sending failed for request with '
                                      'ID: %s', request.id)
                    request.status = RequestStatus.FAILED
                except Exception:
                    self._logger.error(
                        'Unhandled exception while processing request with ID: %s',
                        request.id,
                        exc_info=True,
                    )
                    request.status = RequestStatus.FAILED
                finally:
                    try:
                        await self._requests_repository.save(request)
                    except RequestRepositorySaveException:
                        self._logger.error(
                            'Could not persist final status for request with ID: %s',
                            request.id,
                            exc_info=True,
                        )

                    await self._concurrency_service.complete_task(request.id)
            except asyncio.CancelledError:
                self._logger.info('Request processor cancelled')
                raise
            except Exception:
                self._logger.error(
                    'CRITICAL: Unhandled exception in processor loop',
                    exc_info=True,
                )
