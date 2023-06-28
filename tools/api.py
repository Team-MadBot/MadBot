import aiohttp
import asyncio

from pynepcord.aio import ImageSession
from pynepcord.errors import NepuError
from tools import models, errors
from config import settings

class Requests:
    def __init__(self):
        self.__nc_session = ImageSession(settings['nc_token'])

    async def nc_get_image(self, category: models.NC_CATEGORIES) -> str:
        try:
            image = await self.__nc_session.get_image(category)
        except Exception as e:
            await self.__nc_session.session.close()
            raise NepuError().with_traceback(e.__traceback__)
        await self.__nc_session.session.close()
        if image.code >= 400: 
            raise NepuError(f"Code: {image.code}")
        return image.url

    async def send_sdc_stats(self, bot_id: int, servers: int, shards: int):
        async with aiohttp.ClientSession() as session:
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
