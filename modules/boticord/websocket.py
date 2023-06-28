import aiohttp

from discord.ext import commands
from discord import Webhook
from tools.models import MadBot
from config import settings

class BCWebSocket(commands.Cog):
    def __init__(self, bot: MadBot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.webhook = Webhook.from_url(
            settings["bc_webhook_url"], # type: ignore
            session=self.session
        )
        self.bot.boticordWebsocket.register_listener(
            "comment_removed",
            self.on_comment_removed
        )
    
    async def on_comment_removed(self, data):
        await self.webhook.send(
            content=f"Получены данные от Boticord:\n\n```\n"
            f"{data}\n```"
        )

async def setup(bot: MadBot):
    if bot.boticordWebsocket.not_closed:
        await bot.add_cog(BCWebSocket(bot))
