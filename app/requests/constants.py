from enum import Enum

class RequestType(str, Enum):
    EMAIL = 'email'
    SMS = 'sms'
    PUSH = 'push'

class RequestStatus(str, Enum):
    QUEUED = 'queued'
    PROCESSING = 'processing'
    SENT = 'sent'
    FAILED = 'failed'
