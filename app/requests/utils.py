"""Utility helpers for transforming request models into provider payloads."""

from requests.models import NotificationRequest


async def generate_payload(request: NotificationRequest) -> dict:
    """Builds the outbound notification payload for a stored request.

    Args:
        request (NotificationRequest): Request entity containing recipient,
            content, and channel information.

    Returns:
        dict: JSON-serialisable payload expected by the notification provider.
    """

    payload = {
        "to": request.to,
        "message": request.message,
        "type": request.type,
    }
    return payload
