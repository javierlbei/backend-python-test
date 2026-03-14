# db models
from dataclasses import dataclass

from requests.constants import RequestType, RequestStatus

@dataclass
class Request:
    to: str
    message: str
    type: RequestType
    id: str | None = None
    status: RequestStatus = RequestStatus.QUEUED
