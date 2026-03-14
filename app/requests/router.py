from fastapi import APIRouter, HTTPException, status, Depends, Response

from notifications.client import NotificationClient
from notifications.config import NotificationClientConfig
from requests.constants import RequestStatus
from requests.dependencies import existant_request_id
from requests.exceptions import RequestServiceSaveException
from requests.service import RequestService
from requests.schemas import CreateRequestBody, CreateRequestResponse, GetRequestResponse
from requests.utils import request_service

router = APIRouter(prefix='/v1/requests')
notification_client_config = NotificationClientConfig(
    base_url='http://localhost:3001',
    auth_header={'X-API-Key': 'test-dev-2026'},
    max_retries=3
)
notification_client = NotificationClient(notification_client_config)

@router.post('/', status_code=status.HTTP_201_CREATED,
            response_model=CreateRequestResponse)
async def save_request(request: CreateRequestBody):
    """ Handler for request creation endpoint

    Calls the service methods that include the business logic for 
    request saving.

    Args:
        request: The body containing the basic data of the request

    Returns:
        A JSON response containing the ID of the saved request

    Raises:
        HTTPException: Returns a 422 error if the request could not be saved
        on database
    """
    try:
        created_request_id = await request_service.save_request(request)

        return CreateRequestResponse(id = created_request_id)
    except RequestServiceSaveException:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=('The service could not save the request. '
                    'Please try again later.')
        )

@router.post('/{request_id}/process', status_code=status.HTTP_202_ACCEPTED)
async def process_request(request=Depends(existant_request_id)):
    """ Handler for request processing endpoint

    For queued requests, calls the notification client for their processing.
    
    This method depends on existant_request_id to check if there are request in
    database with the provided ID. Check dependencies.py for more information

    Args:
        request: The retrieved request from database

    Returns:
        Returns an empty response. Status code will vary:
            - If the request has already been processed successfully
                Status code 200 (OK)
            - If the request is already being processed
                Status code 202 (ACCEPTED)
            - Else
                The request will be processed asynchronously. A status code 202
                (ACCEPTED) is returned
    """
    if (request.status == RequestStatus.SENT): return Response()

    if (request.status == RequestStatus.PROCESSING):
        return Response(status_code=status.HTTP_202_ACCEPTED)

    await notification_client.send_notification(request)
    return Response(status_code=status.HTTP_202_ACCEPTED)
    

@router.get('/{request_id}', status_code=status.HTTP_200_OK,
            response_model=GetRequestResponse)
async def get_request(request=Depends(existant_request_id)):
    """ Handler for request retrieval

    Calls the dependency existant_request_id to obtain a request given its ID.
    
    More information on dependencies.py
    """
    return request
