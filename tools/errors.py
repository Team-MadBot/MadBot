from aiohttp import ClientResponse

class ApiError(Exception):
    """Default API Error Exception"""

class SDCError(ApiError):
    """Raises when SDC request was failed"""
    def __init__(self, resp: ClientResponse, *args) -> None:
        self.resp = resp
        super().__init__(*args)
