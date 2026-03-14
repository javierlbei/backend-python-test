import re
from typing_extensions import Self

from pydantic import BaseModel, model_validator

from requests.constants import RequestType, RequestStatus

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

    @model_validator(mode='after')
    def check_valid_recipient(self) -> Self:        
        recipient = self.to
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        phone_pattern = r'^\+[1-9]\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'

        match self.type:
            case RequestType.EMAIL | RequestType.PUSH:
                if re.match(email_pattern, recipient) is not None: 
                    return self
                else:
                    raise ValueError('Email format is incorrect')
            case RequestType.SMS:
                if re.match(phone_pattern, recipient) is not None: 
                    return self
                else:
                    raise ValueError('Phone number format is incorrect')

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
