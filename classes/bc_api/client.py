import asyncio
import aiohttp

from .http import HttpClient
from .websocket import BoticordWebsocket

class BoticordClient:
    def __init__(self, token: str):
        self.session = aiohttp.ClientSession()
        self.token = token
        self.http = HttpClient(token, session=self.session)
        self.ws = BoticordWebsocket(token)
