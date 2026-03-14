# business logic
from requests.exceptions import RequestServiceSaveException
from requests.models import Request
from requests.schemas import CreateRequestBody
from repositories.exceptions import RequestRepositorySaveException
from repositories.requests import RequestRepository

class RequestService:

    def __init__(self):
        self._requests_repository = RequestRepository()

    async def save_request(self, request):
        if isinstance(request, CreateRequestBody):
            request_to_save = Request(
                to=request.to,
                message=request.message,
                type=request.type
            )
        elif isinstance(request, Request):
            request_to_save = request

        try:
            saved_request_id = await (self._requests_repository
                                        .save(request_to_save))
            return saved_request_id
        except RequestRepositorySaveException:
            raise RequestServiceSaveException

    async def get_request(self, request_id: str):
        return await self._requests_repository.get_request_by_id(request_id)
