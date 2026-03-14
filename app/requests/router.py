from fastapi import APIRouter, HTTPException, status, Depends, Response, Request

from concurrency.exceptions import QueueFullException
from concurrency.service import ConcurrencyService
from notifications.client import NotificationClient
from notifications.config import NotificationClientConfig
from notifications.service import NotificationService
from requests.constants import RequestStatus
from requests.dependencies import existant_request_id, get_concurrency_service, get_request_service
from requests.exceptions import RequestServiceSaveException
from requests.service import RequestService
from requests.schemas import CreateRequestBody, CreateRequestResponse, GetRequestResponse

router = APIRouter(prefix='/v1/requests')

@router.post('', status_code=status.HTTP_201_CREATED,
            response_model=CreateRequestResponse)
async def save_request(
    request: CreateRequestBody,
    request_service=Depends(get_request_service)
):
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=('The service could not save the request. '
                    'Please try again later.')
        )

@router.post('/{request_id}/process', status_code=status.HTTP_202_ACCEPTED)
async def process_request(
    request=Depends(existant_request_id),
    concurrency_service=Depends(get_concurrency_service)
):
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

    try:
        await concurrency_service.add_to_queue(request)
        return Response(status_code=status.HTTP_202_ACCEPTED)
    except QueueFullException:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=('You are being rate-limited. Please try again later.')
        )
    

@router.get('/{request_id}', status_code=status.HTTP_200_OK,
            response_model=GetRequestResponse)
async def get_request(request=Depends(existant_request_id)):
    """ Handler for request retrieval

    Calls the dependency existant_request_id to obtain a request given its ID.
    
    More information on dependencies.py
    """
    return request
