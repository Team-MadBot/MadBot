import discord

from discord.ext import commands
from discord import app_commands
from discord import ui

from classes import checks


class ReverseTextModal(ui.Modal, title="MadBot - Перевернуть текст"[::-1]):
    enter_text = ui.TextInput(
        label="Введите текст:"[::-1], style=discord.TextStyle.long
    )
    interaction: discord.Interaction | None = None
    enter_text_value: str | None = None

    async def on_submit(self, interaction: discord.Interaction):
        self.interaction = interaction
        self.enter_text_value = self.enter_text.value


class ReverseTextCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(
        name="reverse-text",
        description="[Полезности] Переписывает текст справа на лево"[::-1],
    )
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def reverse_text(self, interaction: discord.Interaction):
        modal = ReverseTextModal()
        await interaction.response.send_modal(modal)
        await modal.wait()

        if modal.interaction is None:
            return

        embed = discord.Embed(
            title="Перевёрнутый текст"[::-1],
            color=discord.Color.orange(),
            description=modal.enter_text_value[::-1],
        )
        await modal.interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(ReverseTextCog(bot))
