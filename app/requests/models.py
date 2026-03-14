from dataclasses import dataclass

from requests.constants import RequestType, RequestStatus

@dataclass
class NotificationRequest:
    """A notification request

    Attributes:
        to
            A string containing the 
        message
            A string containing the message to send
        type
            The type of the request. Defined by the Enum RequestType.
            Check constants.py for more information
        id
            A string containing the UUID of the request.
            This may be null. Check module requests (inside package 
            repositories) for more details.
        status
            The status of the request, defined byt the enum RequestStatus.
            Check constants.py for more information.
    """
    
    to: str
    message: str
    type: RequestType
    id: str | None = None
    status: RequestStatus = RequestStatus.QUEUED
