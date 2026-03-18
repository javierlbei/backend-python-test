"""API routes for creating, processing, and retrieving requests."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status

from concurrency.exceptions import QueueFullException
from requests.constants import RequestStatus
from requests.dependencies import get_concurrency_service, get_request_service
from requests.models import NotificationRequest
from requests.exceptions import InvalidPayloadException, RequestServiceSaveException
from requests.schemas import CreateRequestBody, CreateRequestResponse, GetRequestResponse


_logger = logging.getLogger('uvicorn.error')

router = APIRouter(prefix='/v1/requests')


@router.post(
    '',
    status_code=status.HTTP_201_CREATED,
    response_model=CreateRequestResponse,
)
async def save_request(
    request: CreateRequestBody,
    request_service=Depends(get_request_service),
) -> CreateRequestResponse:
    """Creates a new request and persists it.

    Args:
        request (CreateRequestBody): Payload containing user input.
        request_service (RequestService): Injected service used for
            persistence.

    Returns:
        CreateRequestResponse: Response containing the created request ID.

    Raises:
        HTTPException: Raised with status 500 when request persistence fails.
        HTTPException: Raised with status 400 when the request payload is
            invalid.
    """

    try:
        _logger.info('Creating request')
        created_request_id = await request_service.save_request(request)

        return CreateRequestResponse(id=created_request_id)
    except RequestServiceSaveException as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=('The service could not save the request. '
                    'Please try again later.')
        ) from exc
    except InvalidPayloadException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=('Invalid request payload. Please ensure the input is valid.')
        ) from exc

@router.post('/{request_id}/process', status_code=status.HTTP_202_ACCEPTED)
async def process_request(
    request_id: str,
    request_service=Depends(get_request_service),
    concurrency_service=Depends(get_concurrency_service),
) -> Response:
    """Enqueues an existing request for asynchronous processing.

    Args:
        request_id (str): ID of the request to process.
        request_service (RequestService): Injected service used to retrieve
            the request.
        concurrency_service (ConcurrencyService): Injected queue manager for
            background processing.

    Returns:
        Response: Empty response with status 200 if already sent, or 202 if
            accepted for processing.

    Raises:
        HTTPException: Raised with status 404 when the request is not found.
        HTTPException: Raised with status 429 when the processing queue is
            full.
    """

    request = await request_service.get_request(request_id)

    if request is None:
        _logger.warning('Request with ID %s was not found', request_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Request not found',
        )

    if request.status == RequestStatus.SENT:
        _logger.info('Request %s already sent', request.id)
        return Response()

    if request.status == RequestStatus.PROCESSING:
        _logger.info('Request %s already processing', request.id)
        return Response(status_code=status.HTTP_202_ACCEPTED)

    try:
        _logger.info('Queueing request %s for processing', request.id)
        await concurrency_service.add_to_queue(request)
        return Response(status_code=status.HTTP_202_ACCEPTED)
    except QueueFullException as exc:
        _logger.warning('Queue full while processing request %s', request.id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=('You are being rate-limited. Please try again later.')
        ) from exc


@router.get(
    '/{request_id}',
    status_code=status.HTTP_200_OK,
    response_model=GetRequestResponse,
)
async def get_request(
    request_id: str,
    request_service=Depends(get_request_service),
) -> NotificationRequest:
    """Retrieves a request by ID.

    Args:
        request_id (str): ID of the request to retrieve.
        request_service (RequestService): Injected service used to look up
            the request.

    Returns:
        NotificationRequest: Request entity serialized by the response model.

    Raises:
        HTTPException: Raised with status 404 when the request is not found.
    """

    request = await request_service.get_request(request_id)

    if request is None:
        _logger.warning('Request with ID %s was not found', request_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Request not found',
        )

    _logger.debug('Returning request %s', request.id)
    return request
