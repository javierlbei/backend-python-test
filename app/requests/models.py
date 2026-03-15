"""Domain models for notification request entities."""

from dataclasses import dataclass

from requests.constants import RequestType, RequestStatus

@dataclass
class NotificationRequest:
    """Represents a single notification request tracked by the system.

    Attributes:
        to (str): Recipient identifier. Expected format depends on ``type``
            (for example, email address for ``EMAIL``).
        message (str): Message body to deliver.
        type (RequestType): Delivery channel for the request.
        id (str | None): Unique request identifier. Assigned by the repository
            when a new request is saved.
        status (RequestStatus): Current processing status for the request.
    """

    to: str
    message: str
    type: RequestType
    id: str | None = None
    status: RequestStatus = RequestStatus.QUEUED
