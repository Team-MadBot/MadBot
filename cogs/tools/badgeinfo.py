import discord

from discord.ext import commands
from discord import app_commands

from . import default_cooldown
from classes import checks

class BadgeInfoCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(name="badgeinfo", description="[Полезности] Информация о значках пользователей и серверов в боте.")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def badgeinfo(self, interaction: discord.Interaction):
        embed=discord.Embed(title="Виды значков:", color=discord.Color.orange())
        embed.add_field(name="Значки пользователя:", value=f"<:ban:946031802634612826> - пользователь забанен в системе бота.\n<a:premium:988735181546475580> - пользователь имеет MadBot Premium.\n<:timeout:950702768782458893> - пользователь получил тайм-аут на сервере.\n<:botdev:977645046188871751> - разработчик бота.\n<:code:946056751646638180> - помощник разработчика.\n<:support:946058006641143858> - поддержка бота.\n<:bug_hunter:955497457020715038> - охотник на баги (обнаружил и сообщил о 3-х и более багах).\n<:bug_terminator:955891723152801833> - уничтожитель багов (обнаружил и сообщил о 10-ти и более багах).\n<:verified:946057332389978152> - верифицированный пользователь.\n<:bot:946064625525465118> - участник является ботом.", inline=False)
        embed.add_field(name="Значки сервера:", value=f"<:verified:946057332389978152> - верифицированный сервер.\n<a:premium:988735181546475580> - сервер имеет MadBot Premium.\n<:ban:946031802634612826> - сервер забанен в системе бота.\n<:beta:946063731819937812> - сервер, имеющий доступ к бета-командам.", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(BadgeInfoCog(bot))
