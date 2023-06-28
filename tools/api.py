import aiohttp
import asyncio

from pynepcord.aio import ImageSession
from pynepcord.errors import NepuError
from tools import models, errors
from config import settings

class Requests:
    def __init__(self):
        self.__loop = asyncio.AbstractEventLoop()
        self.__nc_session = ImageSession(settings['nc_token'], self.__loop)

    async def nc_get_image(self, category: models.NC_CATEGORIES):
        image = await self.__nc_session.get_image(category)
        if image.code >= 400: raise NepuError(f"Code: {image.code}")
        return image.url

    async def send_sdc_stats(self, bot_id: int, servers: int, shards: int):
        async with aiohttp.ClientSession(loop=self.__loop) as session:
            headers = {
                "Authorization": settings["sdc_token"]
            }
            body = {
                'servers': servers,
                'shards': shards
            }
            async with session.post(
                url=models.SDC_URL.format(bot_id=bot_id),
                headers=headers,
                data=body
            ) as resp:
                if resp.ok:
                    await session.close()
                else:
                    raise errors.SDCError(resp, "An error occured when sending bot's statisticks")
