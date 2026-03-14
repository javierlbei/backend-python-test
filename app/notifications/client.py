from fastapi import status
from httpx import AsyncClient

from notifications.config import NotificationClientConfig
from requests.constants import RequestStatus
from requests.models import Request
from requests.utils import request_service

class NotificationClient:

    def __init__(self, client_settings: NotificationClientConfig):
        self._client = AsyncClient(base_url=client_settings.BASE_URL,
                                    headers=client_settings.AUTH_HEADER)
        self._MAX_RETIES = client_settings.MAX_RETRIES

    async def send_notification(self, request: Request):
        request.status = RequestStatus.PROCESSING
        request_service.save_request(request)
        
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
        else:
            request.status = RequestStatus.FAILED

        request_service.save_request(request)
