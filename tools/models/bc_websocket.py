import logging
import aiohttp
import asyncio
import json

from boticordpy import BotiCordWebsocket
from contextlib import suppress
from typing import Callable

class BoticordWS(BotiCordWebsocket):
    """Custom Boticord Websocket based on boticordpy's Websocket."""

    def __init__(self, token: str):
        super().__init__(token)
        self.__session: aiohttp.ClientSession | None = None
        self._on_connect: Callable | None = None
        self._on_close: Callable | None = None
        self.ws: aiohttp.ClientWebSocketResponse | None = None
        self._logger = logging.getLogger("boticord.websocket")
    
    async def _send_ping(self) -> None:
        if self.not_closed:
            await asyncio.sleep(45)
            assert self.ws
            await self.ws.send_json({"event": "ping"})
    
    async def _handle_data(self, data):
        await super()._handle_data(data)
        data = json.loads(data)

        if data['event'] == "error":
            if data['data']['code'] == 6:
                self._logger.error("Token is invalid. Closing websocket...")
                await self.close()
            else:
                self._logger.error(f"An error occured! {data}")
    
    async def _handle_close(self, code: int):
        if self._on_close:
            self.loop.create_task(self._on_close(code))

        self._logger.debug(f"Connection closed with code {code}.")

        if code == 1006:
            self.not_closed = False
            if self.__session and not self.__session.closed:
                await self.__session.close()
            
            self._logger.debug("WebSocket was closed. Retrying...")
            await self.connect()
            return
        
        return await super()._handle_close(code)
    
    async def connect(self):
        self._logger.debug("Start connecting...")

        while not self.ws:
            with suppress(Exception):
                await super().connect()

        self._logger.debug("Done!")
                
        if self._on_connect:
            self._logger.debug("Creating task for on_connect")
            self.loop.create_task(self._on_connect())
        else:
            self._logger.debug("No on_connect handler. Skip.")
        
    def remove_listener(self, notification_type: str):
        """Method to remove the listener
        
        Args:
            notification_type (:obj:`str`)
                Type of notification
        """
        self._listeners[notification_type] = None
        return self

    def clear_listeners(self):
        """Method to clear ALL listeners (including `on_connect` and `on_close`"""
        self._listeners = {}
        self._on_connect = None
        self._on_close = None
        return self
        
    def register_closer(self, callback: Callable):
        """Method to set the closer.

        Args:
            callback (:obj:`function`)
                Coroutine Callback Function
        """
        if not asyncio.iscoroutinefunction(callback):
            raise TypeError(f"<{callback.__qualname__}> must be a coroutine function")

        self._on_close = callback
        self._logger.debug(f"Closer {callback.__qualname__} added successfully!")
        return self

    def register_connecter(self, callback: Callable):
        """Method to set the connecter.

        Args:
            callback (:obj:`function`)
                Coroutine Callback Function
        """
        if not asyncio.iscoroutinefunction(callback):
            raise TypeError(f"<{callback.__qualname__}> must be a coroutine function")

        self._on_connect = callback
        self._logger.debug(f"Connecter {callback.__qualname__} added successfully!")
        return self
