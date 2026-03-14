# db models
from typing import Dict
from uuid import uuid4

from repositories.exceptions import RequestRepositorySaveException
from requests.models import Request

class RequestRepository:

    def __init__(self):
        self._data: Dict[str, Request] = {}

    async def _generate_id(self):
        max_retries = 0

        while max_retries < 10:
            generated_id = uuid4().hex

            if self._data.get(generated_id) is None: return generated_id
            
            max_retries += 1
        
        raise RequestRepositorySaveException
        

    async def save(self, request: Request):
        if request.id is None:
            generated_id = await self._generate_id()
            request.id = generated_id

        self._data[request.id] = request

        return request.id
        


    async def get_request_by_id(self, request_id):
        return self._data.get(request_id)
