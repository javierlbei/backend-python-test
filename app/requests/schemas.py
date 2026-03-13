from pydantic import BaseModel
from .constants import RequestType, RequestStatus

class CreateRequestBody(BaseModel):
    to: str
    message: str
    type: RequestType

class CreateRequestResponse(BaseModel):
    id: str

class GetRequestResponse(BaseModel):
    id: str
    status: RequestStatus
