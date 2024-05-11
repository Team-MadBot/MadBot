import discord
import logging

from discord.ext import commands
from discord import app_commands

logger = logging.getLogger("discord")

class GetStickerCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.bot.tree.add_command(
            app_commands.ContextMenu(
                name="Получить стикер",
                callback=self.get_sticker
            )
        )
    
    async def get_sticker(self, interaction: discord.Interaction, message: discord.Message):
        if len(message.stickers) == 0:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="В данном сообщении нет стикеров!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        fetched_sticker = message.stickers[0]
        embed = discord.Embed(
            title="Получение стикера",
            color=discord.Color.orange(),
            description=f"[Скачать]({fetched_sticker.url})" + (
                "\n\nВнимание: данный стикер сделан в формате `lottie`. Вам загрузится JSON файл, который "
                "Вы можете позже конвертировать самостоятельно, используя сторонние сервисы."
                if fetched_sticker.format == discord.StickerFormatType.lottie else ""
            )
        )
        if fetched_sticker.format != discord.StickerFormatType.lottie:
            embed.set_image(
                url=fetched_sticker.url
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(GetStickerCog(bot))
