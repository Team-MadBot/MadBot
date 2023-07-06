import aiohttp
import asyncio
import traceback

from discord.ext import commands
from discord import Webhook
from tools.models import MadBot, BoticordWS
from config import settings

class BCWebSocket(commands.Cog):
    def __init__(self, bot: MadBot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.webhook = Webhook.from_url(
            settings["bc_webhook_url"], # type: ignore
            session=self.session
        )
        assert settings['bc_token']
        self.ws = BoticordWS(settings['bc_token'])
        self.ws._logger.setLevel(self.bot.log_level)
    
    async def cog_load(self):
        self.ws._logger.debug("Trying to launch Boticord Websocket")

        self.ws.register_listener(
            "comment_removed",
            self.comment_removed
        )
        self.ws.register_listener(
            "up_added",
            self.up_added
        )
        self.ws.register_listener(
            "comment_added",
            self.comment_added
        )
        self.ws.register_listener(
            "comment_edited",
            self.comment_edited
        )
        self.ws.register_connecter(
            self.on_connect
        )
        self.ws.register_closer(
            self.on_close
        )

        self.ws._logger.debug("cog_load: trying to connect")
        try:
            await self.ws.connect()
        except Exception:
            self.bot.logger.error(
                "An error occured while connecting to Boticord WebSocket:\n"
                "%s"
                "You'll not get information about bumps and comments.",
                traceback.format_exc()
            )
        else:
            self.ws._logger.debug("cog_load: done!")

    async def cog_unload(self):
        self.ws._logger.debug("Closing websocket...")
        await self.ws.close()
    
    async def comment_added(self, data):
        await self.webhook.send(
            content=f"Получены данные от Boticord:\n\n```\n"
            f"{data}\n```"
        )
    
    async def comment_edited(self, data):
        await self.webhook.send(
            content=f"Получены данные от Boticord:\n\n```\n"
            f"{data}\n```"
        )

    async def comment_removed(self, data):
        await self.webhook.send(
            content=f"Получены данные от Boticord:\n\n```\n"
            f"{data}\n```"
        )

    async def up_added(self, data):
        await self.webhook.send(
            content=f"Получены данные от Boticord:\n\n```\n"
            f"{data}\n```"
        )
    
    async def on_connect(self):
        await self.webhook.send(
            content=f"Websocket жив!"
        )
    
    async def on_close(self, code: int):
        await self.webhook.send(
            content=f"Websocket умер. Код выхода: {code}"
        )

async def setup(bot: MadBot):
    await bot.add_cog(BCWebSocket(bot))
