# db models
from .constants import RequestType, RequestStatus
from dataclasses import dataclass

@dataclass
class Request:
    to: str
    message: str
    type: RequestType
    id: str | None = None
    status: RequestStatus = RequestStatus.QUEUED
