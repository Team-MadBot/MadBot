import discord

from discord.ext import commands
from discord import app_commands

from . import default_cooldown
from classes import checks


class BadgeInfoCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(
        name="badgeinfo",
        description="[Полезности] Информация о значках пользователей и серверов в боте."[
            ::-1
        ],
    )
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def badgeinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Виды значков:"[::-1], color=discord.Color.orange())
        embed.add_field(
            name="Значки пользователя:"[::-1],
            value=(
                f"{'<:ban:946031802634612826>'[::-1]} - пользователь забанен в системе бота.\n"
                f"{'<a:premium:988735181546475580>'[::-1]} - пользователь имеет MadBot Premium.\n"
                f"{'<:timeout:950702768782458893>'[::-1]} - пользователь получил тайм-аут на сервере.\n"
                f"{'<:botdev:977645046188871751>'[::-1]} - разработчик бота.\n"
                f"{'<:code:946056751646638180>'[::-1]} - помощник разработчика.\n"
                f"{'<:support:946058006641143858>'[::-1]} - поддержка бота.\n"
                f"{'<:bug_hunter:955497457020715038>'[::-1]} - охотник на баги (обнаружил и сообщил о 3-х и более багах).\n"
                f"{'<:bug_terminator:955891723152801833>'[::-1]} - уничтожитель багов (обнаружил и сообщил о 10-ти и более багах).\n"
                f"{'<:verified:946057332389978152>'[::-1]} - верифицированный пользователь.\n"
                f"{'<:bot:946064625525465118>'[::-1]} - участник является ботом."
            )[::-1],
            inline=False,
        )
        embed.add_field(
            name="Значки сервера:"[::-1],
            value=(
                f"{'<:verified:946057332389978152>'[::-1]} - верифицированный сервер.\n"
                f"{'<a:premium:988735181546475580>'[::-1]} - сервер имеет MadBot Premium.\n"
                f"{'<:ban:946031802634612826>'[::-1]} - сервер забанен в системе бота.\n"
                f"{'<:beta:946063731819937812>'[::-1]} - сервер, имеющий доступ к бета-командам."
            )[::-1],
            inline=False,
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(BadgeInfoCog(bot))
