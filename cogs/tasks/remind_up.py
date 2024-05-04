import discord
import time

from discord.ext import commands
from discord.ext import tasks

from cogs.boticord.websocket import LinktoBoticord
from classes import db

from contextlib import suppress


class RemindUpCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    async def cog_load(self):
        self.remind_up.start()

    async def cog_unload(self) -> None:
        self.remind_up.cancel()

    @tasks.loop(seconds=1)
    async def remind_up(self):
        async for user in db.get_users():
            if user["next_bump"] > time.time():
                continue
            if user["reminded"] or not user["enabled"]:
                continue
            assert self.bot.user is not None
            view = LinktoBoticord(self.bot.user.id)
            embed = discord.Embed(
                title="Напоминание о повышении!",
                color=discord.Color.orange(),
                description="Нажмите на кнопку ниже для перехода на страницу бота "
                "либо используйте команду `/up` в <@1000051258679373914> (может не работать, "
                "если уровень буста на Boticord ниже третьего).",
            ).set_thumbnail(
                url="https://cdn.discordapp.com/attachments/1058728870540476506/1125117851578142822/favicon.png"
            )
            await db.update_user(user_id=user["user_id"], reminded=True)
            user = await self.bot.fetch_user(user["user_id"])
            await user.send(
                f"<@{user['user_id']}>, время апнуть MadBot на Boticord!",
                embed=embed,
                view=view,
            )

    @remind_up.before_loop
    async def remind_up_before(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(RemindUpCog(bot))
