from requests.exceptions import RequestServiceSaveException
from requests.models import NotificationRequest
from requests.schemas import CreateRequestBody
from repositories.exceptions import RequestRepositorySaveException
from repositories.requests import RequestRepository

class RequestService:

    def __init__(self):
        """Instantiate a RequestRepository object for database operations"""
        self._requests_repository = RequestRepository()

    async def save_request(self, request):
        """ Business logic for request saving.

        From the provided request body, creates a new object that will be sent
        to the repository method for saving.

        Args:
            request:
                The notification request to process. Class may vary:
                    - CreateRequestBody
                        Used by router module to create a new request
                    - NotificationRequest:
                        Used by client module (inside package notifications) to
                        update the request


        Returns:
            Returns a string containing the ID of the saved request

        Raises:
            RequestServiceSaveException: The repository could not generate a
            unique ID for the new request
        """
        if isinstance(request, CreateRequestBody):
            request_to_save = NotificationRequest(
                to=request.to,
                message=request.message,
                type=request.type
            )
        elif isinstance(request, NotificationRequest):
            request_to_save = request

        try:
            saved_request_id = await (self._requests_repository
                                        .save(request_to_save))
            return saved_request_id
        except RequestRepositorySaveException:
            raise RequestServiceSaveException

    async def get_request(self, request_id: str):
        """ Business logic for request retrieval.

        Args:
            request_id: ID of the request to retrieve

        Returns:
            Returns the retrieved request object
        """
        return await self._requests_repository.get_request_by_id(request_id)
