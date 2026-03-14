import asyncio

from concurrency.service import ConcurrencyService
from notifications.client import NotificationClient

class NotificationService:
    """Worker class to process the enqueued requests.

    Attributes:
        _concurrency_service
            Instance of ConcurrencyService
        _notification_client
            Instance of NotificationClient
        _processing_tasks
            Stores the async tasks
        _num_tasks
            Defines the number of async tasks that the service will create
    """

    def __init__(
        self,
        concurrency_service: ConcurrencyService,
        notification_client: NotificationClient,
        num_tasks: int = 1
    ):
        """Initializes the instance based on arguments

        Args:
            concurrency_service
                Instance of ConcurrencyService
            notification_client
                Instance of NotificationClient
            num_tasks
                Defines the number of async tasks that the service will create
        """
        self._concurrency_service = concurrency_service
        self._notification_client = notification_client
        self._processing_tasks = []
        self._num_tasks = num_tasks

    async def start(self):
        """Starts the notification service.

        Creates tasks based on the defined configuration
        """
        for _ in range(self._num_tasks):
            task = asyncio.create_task(self._notification_processor())
            self._processing_tasks.append(task)
        
    async def stop(self):
        """Cancels all the active tasks for service shutdown"""
        for task in self._processing_tasks:
            task.cancel()

        await asyncio.gather(*self._processing_tasks, return_exceptions=True)

    async def _notification_processor(self):
        """Process all the requests coming from the queue"""
        while True:
            request = await self._concurrency_service.get_next_request()
            await self._notification_client.send_notification(request)
        
