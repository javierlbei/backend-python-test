from fastapi import HTTPException, status

from requests.utils import request_service

async def existant_request_id(request_id):
    """ Checks the existence of a request.

    Calls the service methods including the business logic for request
    retrieval.

    Args:
        request_id: The ID of the request to retrieve

    Returns:
        In case of existing the request, this will be returned

    Raises:
        HTTPException: Returns a 404 error as the request does not exist in
        database
    """
    request = await request_service.get_request(request_id)
    
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Request not found')

    return request
