import asyncio
import aiohttp

from config import settings
from typing import List, Union
from . import exceptions


class HttpClient:
    def __init__(self, token: str = None, version: int = 3, **kwargs):
        self.token = token
        self.API_URL = f"https://api.boticord.top/v{version}"

        loop = kwargs.get("loop") or asyncio.get_event_loop()

        self.session = kwargs.get("session") or aiohttp.ClientSession(loop=loop)

    async def make_request(self, method: str, endpoint: str, **kwargs):
        kwargs["headers"] = {
            "Content-Type": "application/json",
            "User-Agent": f"MadBot v{settings['curr_version']}",
        }

        if self.token is not None:
            kwargs["headers"]["Authorization"] = self.token

        url = f"{self.API_URL}{endpoint}"

        async with self.session.request(method, url, **kwargs) as resp:
            data = await resp.json()

            if resp.ok:
                return data["result"]

            raise exceptions.HTTPException(
                {"status": resp.status, "error": data["errors"][0]["code"]}
            )

    async def get_bot_info(self, bot_id: str | int):
        return await self.make_request("GET", f"/bots/{bot_id}")

    async def get_guild_info(self, guild_id: str | int):
        return await self.make_request("GET", f"/servers/{guild_id}")

    async def post_bot_stats(self, bot_id: str | int, stats: dict):
        return await self.make_request("POST", f"/bots/{bot_id}/stats", json=stats)

    async def get_captcha(
        self, resource_id: int, user_id: int
    ) -> List[Union[aiohttp.ClientResponse, dict]]:
        async with self.make_request(
            "POST",
            "/resources/ups/service/prepare",
            json={
                "token": self.token,
                "resource": str(resource_id),
                "user": str(user_id),
            },
        ) as resp:
            if resp.content_type.lower() != "application/json":
                data = await resp.read()
                return [resp, {"error": data}]
            json = await resp.json()
            return [resp, json]

    async def submit_captcha(
        self, resource_id: int, captcha_id: str, user_id: int, answer: int
    ) -> List[Union[aiohttp.ClientResponse, dict]]:
        async with self.make_request(
            "/resources/ups/service/proceed",
            json={
                "token": self.token,
                "resource": str(resource_id),
                "user": str(user_id),
                "captchaId": captcha_id,
                "captchaAnswer": answer,
            },
        ) as resp:
            json = await resp.json()
            return [resp, json]
