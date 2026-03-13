# env vars
class NotificationClientConfig:
    BASE_URL: str
    AUTH_HEADER: dict
    MAX_RETRIES: int

    def __init__(self,base_url: str, auth_header: dict, max_retries: int):
        self.BASE_URL = base_url
        self.AUTH_HEADER = auth_header
        self.MAX_RETRIES = max_retries
