from typing import Dict
from uuid import uuid4

from repositories.exceptions import RequestRepositorySaveException
from requests.models import NotificationRequest

class RequestRepository:
    """Performs operations in the database.

    Attributes:
        _data
            An in-memory database for demonstration purposes
    """

    def __init__(self):
        """Initializes the database"""

        self._data: Dict[str, NotificationRequest] = {}

    async def _generate_id(self):
        """ Generates a non-existant UUID

        Returns:
            A string containing the generated UUID

        Raises:
            RequestRepositorySaveException: The program could not generate
            a unique ID in the maximum attempts range.
        """
        max_retries = 0

        while max_retries < 10:
            generated_id = uuid4().hex

            if generated_id not in self._data: return generated_id
            
            max_retries += 1
        
        raise RequestRepositorySaveException
        

    async def save(self, request: NotificationRequest):
        """ Saves the request in database.

        If the provided request has no ID set, this will be saved as a new entry
        on the database. If provided, an update operation will be performed.

        Args:
            request: The notification request to save

        Returns:
            A string containing the ID of the saved request
        """
        if request.id is None:
            generated_id = await self._generate_id()
            request.id = generated_id

        self._data[request.id] = request

        return request.id
        


    async def get_request_by_id(self, request_id):
        """ Gets a request in database.

        Args:
            request_id: String containing the ID of the request to retrieve.

        Returns:
            If a request with the provided ID exists on database, a NotificationRequest
            object will be returned.

            If it does not exist, None will be returned.
        """
        return self._data.get(request_id)
