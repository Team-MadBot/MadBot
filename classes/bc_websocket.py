import asyncio
import logging
import json
from contextlib import suppress
from typing import Callable

import aiohttp
from boticordpy import BotiCordWebsocket # type: ignore

class BoticordWS(BotiCordWebsocket):
    """Client for interacting with the Boticord API via websocket.

    Handles connecting, sending requests, and receiving responses 
    via the Boticord websocket API.
    """

    def __init__(self, token: str):
        super().__init__(token)
        self._on_connect: Callable | None = None
        self._on_close: Callable | None = None
        self.ws: aiohttp.ClientWebSocketResponse | None = None
        self._logger = logging.getLogger("boticord.websocket")

    async def _send_ping(self) -> None:
        """Sends a ping event to keep the websocket connection alive.
        Sends a ping event every 45 seconds if the connection is still open.
        """
        if self.not_closed:
            await asyncio.sleep(45)
            if not self.not_closed or not self.ws:
                return
            await self.ws.send_json({"event": "ping"})

    async def _handle_data(self, data):
        """Handles incoming data from the websocket.
        
        Parses the data and dispatches events based on the event type.
        Logs any errors received.

        Args:
            data (str): The raw JSON data received.
        """
        await super()._handle_data(data)
        data = json.loads(data)

        if data['event'] == "error":
            if data['data']['code'] == 6:
                # Это - жирный костыль из-за офигенной системы вебсокетов Boticord.
                # Когда система будет доработана, костыль я уберу.
                self._logger.error("Token is invalid. Closing Websocket...")
                await self.close()
            else:
                self._logger.error(f"An error occured! {data}")

    async def _handle_close(self, code: int):
        if self._on_close:
            await self._on_close(code)

        self._logger.debug(f"Connection closed with code {code}.")

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
