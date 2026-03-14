import asyncio
from typing import Dict

from concurrency.exceptions import QueueFullException
from requests.models import NotificationRequest

class ConcurrencyService:
    """Queues all the pending request to process

    Attributes:
        _queue
            Asynchronous queue
        _lock
            Guarantee exclusive access to a shared resource
        _enqueued_requests
            Stores the requests currently enqueued
    """

    def __init__(self, queue_size: int = 0):
        """Initializes the instance based on arguments

        Args:
            queue_size
                Defines the maximum number of requests the queue can hold
        """
        self._queue = asyncio.Queue(queue_size)
        self._lock = asyncio.Lock()
        self._enqueued_requests = set()

    async def add_to_queue(self, request: NotificationRequest):
        """Adds a request to the queue

        Args:
            request
                The request to queue
        Raises:
            QueueFullException: The queue is full and does not admit more
            request
        """
        async with self._lock:
            # Protects the requests from being processed multiple times
            # in a short space of time

            if request.id in self._enqueued_requests:
                return

            try:
                self._queue.put_nowait(request)
            except QueueFull:
                raise QueueFullException

            self._enqueued_requests.add(request.id)

    async def get_next_request(self):
        """ Retrieves the next element of the queue

        If the queue is empty, it will wait for the next request to come

        Returns:
            The retrieved request
        """
        return await self._queue.get()

    async def complete_task(self, request_id):
        """Completes an already processed task"""
        async with self._lock:
            self._queue.task_done()
            self._enqueued_requests.delete(request_id)
