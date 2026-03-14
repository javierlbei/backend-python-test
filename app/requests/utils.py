from .service import RequestService

# Instantiating the service on this module to avoid circular imports between dependencies and router
request_service = RequestService()
