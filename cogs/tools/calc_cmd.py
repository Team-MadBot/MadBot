import discord
import numexpr  # type: ignore

from discord.ext import commands
from discord import app_commands

from . import default_cooldown
from classes import checks


class CalcCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(
        name="calc", description="[Полезности] Калькулятор в Discord."
    )
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(problem="Пример для решения")
    async def calc(
        self,
        interaction: discord.Interaction,
        problem: app_commands.Range[str, None, 30],
    ):
        if "**" in problem:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Использование степени запрещено!",
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        try:
            answer = numexpr.evaluate(problem)  # type: ignore
        except ZeroDivisionError:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Расскажу-ка тебе секрет. На ноль делить нельзя. У нас тут не высшая математика.",
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        except:  # FIXME: bare except
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Пример введён некорректно!",
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="Калькулятор",
                color=discord.Color.orange(),
                description=f"Ваш пример: `{problem}`\nОтвет: `{answer}`",
            )
            embed.set_footer(
                text=str(interaction.user), icon_url=interaction.user.display_avatar.url
            )
            await interaction.response.send_message(embed=embed)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(CalcCog(bot))
