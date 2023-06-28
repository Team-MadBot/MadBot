import discord

from discord import ui

class BotUseTry(ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @ui.button(label="Не понял")
    async def button_click(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(
            title="А что непонятного?",
            color=discord.Color.orange(),
            description="На данный момент, MadBot v2 доступна только владельцам бота. Ожидайте "
            "релиза v2."
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)