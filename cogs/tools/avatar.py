import discord

from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice

from . import default_cooldown

from classes import checks

class UserAvatar(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(name="avatar", description="[Полезности] Присылает аватар пользователя")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(
        member='Участник, чью аватарку вы хотите получить', 
        format="Формат изображения", 
        size="Размер изображения", 
        type="Тип аватара"
    )
    @app_commands.choices(
        format=[
            Choice(name="PNG (прозрачный фон)", value="png"),
            Choice(name="JPEG (черный фон)", value="jpeg"),
            Choice(name="JPG (как JPEG)", value='jpg'),
            Choice(name="WEBP (веб-картинка)", value='webp')
        ],
        size=[
            Choice(name="16x16 пикселей", value=16),
            Choice(name="32x32 пикселей", value=32),
            Choice(name="64x64 пикселей", value=64),
            Choice(name="128x128 пикселей", value=128),
            Choice(name="256x256 пикселей", value=256),
            Choice(name="512x512 пикселей", value=512),
            Choice(name="1024x1024 пикселей", value=1024),
            Choice(name="2048x2048 пикселей", value=2048),
            Choice(name="4096x4096 пикселей", value=4096)
        ],
        type=[
            Choice(name="Стандартная", value='standart'),
            Choice(name="Серверная", value='server')
        ]
    )
    async def avatar(
        self, 
        interaction: discord.Interaction, 
        member: discord.User = None, 
        format: Choice[str] = "png", 
        size: Choice[int] = 2048, 
        type: Choice[str] = 'standart'
    ):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member is None: member = interaction.user
        try:
            member: discord.Member = await interaction.guild.fetch_member(member.id)
        except:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Данная команда работает только на участниках этого сервера"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if format != 'png': format = format.value
        if size != 2048: size = size.value
        if type != 'standart': type = type.value
        user_avatar = member.avatar or member.default_avatar
        if type == 'server': 
            if member.guild_avatar is None:
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Ошибка!",
                        color=discord.Color.red(),
                        description="Пользователь не имеет серверного аватара."
                    ),
                    ephemeral=True
                )
            user_avatar = member.guild_avatar
        embed = discord.Embed(
            color=discord.Color.orange() if member.color == discord.Color.default() else member.color,
            description=f"[Скачать]({user_avatar.replace(static_format=format, size=size)})"
        )
        embed.set_author(name=f"Аватар {member}")
        embed.set_image(url=user_avatar.replace(static_format=format, size=size))
        type = "Серверный" if type == "server" else "Стандартный"
        embed.set_footer(text=f"Запросил: {str(interaction.user)} | Формат: {format} | Размер: {size} | Тип аватара: {type}")
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(UserAvatar(bot))
