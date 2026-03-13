# router dependencies
from .utils import request_service
from fastapi import HTTPException, status

async def existant_request_id(request_id):
    request = await request_service.get_request(request_id)
    
    if request is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'Request not found'
        )

    return request
