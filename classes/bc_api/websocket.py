import logging
import json
import asyncio
import typing

import aiohttp

logger = logging.getLogger("discord")


class BoticordWebsocket:
    """Represents a websocket client for receiving notifications from Boticord."""

    def __init__(self, token: str):
        self.__session = None
        self.loop = asyncio.get_event_loop()
        self.ws = None
        self._listeners = {}
        self.not_closed = False
        self._token = token

    def __set_listener(self, notification_type: str, func: typing.Any):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f"<{func.__qualname__}> must be a coroutine function")
        self._listeners[notification_type] = func
        logger.debug(f"Listener {notification_type} added successfully!")

    def listener(self):
        """Decorator to set the listener.

        If you set default listener, you will get `response['data']`. If you set `global_listener`, it'll
        return all `response` from Boticord WebSocket,

        .. warning::

            Callback functions must be a **coroutine**. If they aren't, then you might get unexpected
            errors. In order to turn a function into a coroutine they must be ``async def``
            functions.

        For example:

        .. code-block:: python

            @websocket.listener()
            async def new_bot_bump(data):
                pass
        """

        def inner(func):
            self.__set_listener(func.__qualname__, func)
            return func

        return inner

    def register_listener(self, notification_type: str, callback: typing.Any):
        """Method to set the listener.

        If you set default listener, you will get `response['data']`. If you set `global_listener`, it'll
        return all `response` from Boticord WebSocket,

        Args:
            notification_type (:obj:`str`)
                Type of notification
            callback (:obj:`function`)
                Coroutine Callback Function

        .. warning::

            Callback functions must be a **coroutine**. If they aren't, then you might get unexpected
            errors. In order to turn a function into a coroutine they must be ``async def``
            functions.

        For example:

        .. code-block:: python

            async def new_bot_bump(data):
                pass

            websocket.register_listener("new_bot_bump", new_bot_bump)
        """
        self.__set_listener(notification_type, callback)
        return self

    async def connect(self) -> None:
        """Connect to BotiCord."""
        try:
            self.__session = aiohttp.ClientSession()
            self.ws = await self.__session.ws_connect(
                "wss://gateway.boticord.top/websocket/",
                timeout=30.0,
            )

            logger.info("Connected to BotiCord.")

            self.not_closed = True

            self.loop.create_task(self._receive())
            await self._send_identify()
        except Exception as exc:
            logger.error("Connecting failed!")

            raise exc

    async def _send_identify(self) -> None:
        await self.ws.send_json({"event": "auth", "data": {"token": self._token}})

    async def _receive(self) -> None:
        while self.not_closed:
            async for msg in self.ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self._handle_data(msg.data)
                else:
                    raise RuntimeError

            close_code = self.ws.close_code

            if close_code is not None:
                await self._handle_close(close_code)

    async def _handle_data(self, data):
        data = json.loads(data)

        if data["event"] == "hello":
            logger.info("BCWS: Authorized successfully.")
            self.loop.create_task(self._send_ping())
        elif data["event"] == "notify":
            listener = self._listeners.get(data["data"]["type"])
            if global_listener := self._listeners.get("global_listener", None):
                self.loop.create_task(global_listener(data))
            if listener:
                self.loop.create_task(listener(data["data"]))
        elif data["event"] == "pong":
            logger.info("BCWS: Received pong-response.")
            self.loop.create_task(self._send_ping())
        else:
            logger.error("BCWS: An error has occurred.")

    async def _handle_close(self, code: int) -> None:
        self.not_closed = False
        await self.__session.close()

        if code == 4000:
            logger.info("Closed connection successfully.")
            return
        elif (
            code == 1006
        ):  # FIXME: BC WS can raise this close code not only when token is invalid.
            logger.error(
                "Token is invalid. Maybe, BC API just a piece of shit, so trying to reconnect."
            )
            # return

        logger.info("Disconnected from BotiCord. Reconnecting in 5 seconds...")
        await asyncio.sleep(5)

        await self.connect()

    async def _send_ping(self) -> None:
        if not self.ws.closed:
            await asyncio.sleep(45)
            await self.ws.send_json({"event": "ping"})

    async def close(self) -> None:
        """Close websocket connection with BotiCord API"""
        if self.ws:
            self.not_closed = False
            await self.ws.close(code=4000)
