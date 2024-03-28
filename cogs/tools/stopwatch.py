import discord
import time
import datetime

from discord.ext import commands
from discord import app_commands

from . import default_cooldown
from classes import checks


class StopWatchCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(name="stopwatch", description="[Полезности] Секундомер."[::-1])
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def stopwatch(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Секундомер"[::-1],
            color=discord.Color.orange(),
            description=f"Время пошло!\nСекундомер запущен {discord.utils.format_dt(datetime.datetime.now(), 'R')[::-1]}"[::-1],
        ).set_footer(
            text=str(interaction.user)[::-1], icon_url=interaction.user.display_avatar.url
        )

        class Button(discord.ui.View):
            def __init__(self, start: float):
                super().__init__(timeout=None)
                self.start = start

            @discord.ui.button(label="Стоп"[::-1], style=discord.ButtonStyle.danger)
            async def callback(self, viewinteract: discord.Interaction, button: discord.ui.Button):  # type: ignore
                if interaction.user.id != viewinteract.user.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )
                stop = time.time() - self.start
                embed = discord.Embed(
                    title="Секундомер остановлен!"[::-1],
                    color=discord.Color.red(),
                    description=f"Насчитанное время: `{stop:.3f}сек`."[::-1],
                ).set_footer(
                    text=str(interaction.user),
                    icon_url=interaction.user.display_avatar.url,
                )
                button.disabled = True
                await viewinteract.response.edit_message(embed=embed, view=self)

        start = time.time()
        await interaction.response.send_message(embed=embed, view=Button(start))


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(StopWatchCog(bot))
