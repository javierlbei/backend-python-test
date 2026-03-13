# Endpoints
from fastapi import APIRouter, HTTPException, status, Depends, Response
from .schemas import CreateRequestBody, CreateRequestResponse, GetRequestResponse
from .service import RequestService
from .utils import request_service
from .exceptions import RequestServiceSaveException
from .dependencies import existant_request_id
from .constants import RequestStatus
from notifications.config import NotificationClientConfig
from notifications.client import NotificationClient

router = APIRouter(
    prefix = '/v1/requests'
)
notification_client_config = NotificationClientConfig(
    base_url = "http://localhost:3001",
    auth_header = { 'X-API-Key': 'test-dev-2026' },
    max_retries = 3
)
notification_client = NotificationClient(notification_client_config)

@router.post(
    '/',
    status_code = status.HTTP_201_CREATED,
    response_model = CreateRequestResponse
)
async def save_request(request: CreateRequestBody):
    try:
        created_request_id = await request_service.save_request(request)

        return CreateRequestResponse(id = created_request_id)
    except RequestServiceSaveException:
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = 'The service could not save the request. Please try again later.'
        )

@router.post(
    '/{request_id}/process',
    status_code=status.HTTP_202_ACCEPTED
)
async def process_request(request = Depends(existant_request_id)):

    if (request.status == RequestStatus.SENT):
        return Response()

    if (request.status == RequestStatus.PROCESSING):
        return Response(status_code = status.HTTP_202_ACCEPTED)

    #try:
    await notification_client.send_notification(request)
    return Response(status_code = status.HTTP_202_ACCEPTED)
    """except:
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = 'The service could not save the request. Please try again later.'
        )"""
    

@router.get(
    '/{request_id}',
    status_code = status.HTTP_200_OK,
    response_model = GetRequestResponse
)
async def get_request(request = Depends(existant_request_id)):
    return request
