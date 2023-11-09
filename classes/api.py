import aiohttp
import asyncio
import config

class Requests:
    get_sad_images = "get_sad_images"

async def api(request: Requests):
    async with aiohttp.ClientSession() as session:
        async def get_sad_image():
            headers = {
                "Authorization": config.settings['nc_token']
            }
            async with session.get("https://api.neppedcord.top/images/sad", headers=headers) as resp:
                response = await resp.json()
                return response['url']
        if request == Requests.get_sad_images: return await get_sad_image()