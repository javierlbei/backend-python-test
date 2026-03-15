"""Custom exceptions raised by request service helpers."""


class RequestServiceSaveException(Exception):
    """Raised when a request cannot be persisted by the service."""


class InvalidPayloadException(Exception):
    """Raised when a notification payload is missing required fields or has invalid values."""
