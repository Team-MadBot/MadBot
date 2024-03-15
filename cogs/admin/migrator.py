from discord.ext import commands
from classes import db
from config import *


class MigrateDB(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.command(name="migrate-db")
    @commands.is_owner()
    async def migrate_db(self, ctx: commands.Context):
        message = await ctx.send(
            "# Миграция\n[**В процессе...**] Мигрирование чёрного списка\n[В очереди] Мигрирование верифицированных"
        )
        for resource in blacklist:
            await db.add_blacklist(resource, ctx.author.id, None, None)
        await message.edit(
            content=f"# Миграция\n[*{len(blacklist)} перенесено*] Мигрирование чёрного списка\n"
            "[**В процессе...**] Мигрирование статистики бота\n"
            "[В очереди] Мигрирование верифицированных"
        )
        await db.create_bot_stats()
        await message.edit(
            content=f"# Миграция\n[*{len(blacklist)} перенесено*] Мигрирование чёрного списка\n"
            "[*Создано*] Мигрирование статистики бота\n"
            "[**Не реализовано!!!**] Мигрирование верифицированных"
        )


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(MigrateDB(bot))
