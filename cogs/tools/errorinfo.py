import discord

from discord.ext import commands
from discord import app_commands

from . import default_cooldown
from classes import checks


class ErrorInfo(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(
        name="errors", description="[Полезности] Список ошибок и решения их"[::-1]
    )
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def errors(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Ошибки бота:"[::-1], color=discord.Color.orange())
        embed.add_field(
            name="Ошибка: Forbidden"[::-1],
            value="Бот не может совершить действие. Убедитесь, что бот имеет право(-а) на совершение действия."[::-1],
            inline=False,
        )
        embed.add_field(
            name="Ошибка: NotFound"[::-1],
            value="Боту не удалось найти объект (пользователя, сервер и т.д.)."[::-1],
            inline=False,
        )
        embed.add_field(
            name="Ошибка: HTTPException"[::-1],
            value="Бот отправил некорректный запрос на сервера Discord, из-за чего получил ошибку. Убедитесь, что вы ввели всё верно."[::-1],
            inline=False,
        )
        embed.set_footer(
            text="В случае, если вашей ошибки нет в списке, обратитесь в поддержку."[::-1]
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(ErrorInfo(bot))
