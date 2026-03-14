from fastapi import Depends, status
from httpx import AsyncClient

from notifications.config import NotificationClientConfig
from requests.constants import RequestStatus
from requests.models import NotificationRequest
from requests.service import RequestService

class NotificationClient:
    """Client to send notifications.

    Acts as a middleman between the program and the notification service

    Attributes:
        _client
            HTTP client for REST requests
        _MAX_RETIES
            Limit of retries before considering a notification processing has
            failed.
    """

    def __init__(
        self,
        client_settings: NotificationClientConfig,
        request_service: RequestService
    ):
        """Initializes the instance based on configuration

        Args:
            client_settings: Defines the URL, auth headers and retry threshold
        """
        self._client = AsyncClient(base_url=client_settings.BASE_URL,
                                    headers=client_settings.AUTH_HEADER)
        self._MAX_RETIES = client_settings.MAX_RETRIES
        self._request_service = request_service

    async def close(self):
        await self._client.aclose()

    async def send_notification(
        self,
        request: NotificationRequest
    ):
        """ Sends the notification request to the provider.

        Sends the notification request to the provider and updates the request
        status according to the execution state.

        Args:
            request: The notification request to process

        Returns:
            This method has no return

        Raises:
            This method raises no exceptions
        """
        request.status = RequestStatus.PROCESSING
        await self._request_service.save_request(request)
        
        for _ in range(self._MAX_RETIES):
            response = await self._client.post(
                "/v1/notify",
                json={
                    'to': request.to,
                    'message': request.message,
                    'type': request.type
                }
            )

            if (response.status_code == status.HTTP_200_OK):
                request.status = RequestStatus.SENT
                break
            else:
                request.status = RequestStatus.FAILED
        
        await self._request_service.save_request(request)
