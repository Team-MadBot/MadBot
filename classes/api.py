import aiohttp
import config
from enum import Enum, auto

class Tag(Enum):
    baka = auto()
    cry = auto()
    cuddle = auto()
    happy = auto()
    hug = auto()
    kiss = auto()
    sad = auto()
    wag = auto()
    poke = auto()
    pat = auto()
    dance = auto()
    smug = auto()
    wave = auto()
    menhera_chan = auto()

async def api(tag: Tag):
    """Makes an API request based on the given request type.

    Args:
        request (Tag): The type of API request to make.

    Returns:
        Response data based on the request type. For example,
        a sad image URL for a 'get_sad_images' request.
    """
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": config.settings['nc_token']
        }
        async with session.get(f"https://api.neppedcord.top/images/{tag.name.replace('_', '-')}", headers=headers) as resp:
            response = await resp.json()
            return response['url']
