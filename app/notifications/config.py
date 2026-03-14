class NotificationClientConfig:
    """Configuration values for instancing a client.

    Attributes:
        BASE_URL
            A string containing the base path of the webservice.
        AUTH_HEADER
            A dictionary containing the name and value of the authentication
            header.
        MAX_RETRIES
            Defines the maximum number of retries that the client can perfom
            when processing a request

    """

    def __init__(self,base_url: str, auth_header: dict, max_retries: int):
        self.BASE_URL = base_url
        self.AUTH_HEADER = auth_header
        self.MAX_RETRIES = max_retries
