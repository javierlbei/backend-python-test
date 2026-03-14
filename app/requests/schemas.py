from pydantic import BaseModel
from .constants import RequestType, RequestStatus

class CreateRequestBody(BaseModel):
    """Represents the body of the create request endpoint.

    Attributes:
        to: The recipient's email address or phone number.
        message: The message content to be sent.
        type: The type of request being created.
    """

    to: str
    message: str
    type: RequestType

class CreateRequestResponse(BaseModel):
    """Represents the response of the create request endpoint.

    Attributes:
        id: A unique identifier for the created request.
    """

    id: str

class GetRequestResponse(BaseModel):
    """Represents the response of the get request endpoint.

    Attributes:
        id: A unique identifier for the request being queried.
        status: The current processing status of the request.
    """
    
    id: str
    status: RequestStatus
