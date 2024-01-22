import discord

from discord.ext import commands
from discord import app_commands

from . import default_cooldown

from classes import checks
from classes.checks import isPremiumServer

from config import verified
from config import beta_testers

class ServerInfo(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(name="serverinfo", description="[Полезности] Информация о сервере")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def serverinfo(self, interaction: discord.Interaction):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        badges = ''
        if await checks.is_in_blacklist(interaction.guild.id):
            badges += '<:ban:946031802634612826> '
        if interaction.guild.id in verified:
            badges += '<:verified:946057332389978152> '
        if await isPremiumServer(interaction.guild):
            badges += '<a:premium:988735181546475580> '
        if interaction.guild.id in beta_testers:
            badges += '<:beta:946063731819937812> '
        embed = discord.Embed(
            title=f"{interaction.guild.name} {badges}", 
            color=discord.Color.orange()
        )
        embed.add_field(name="Владелец:", value=f"<@!{interaction.guild.owner_id}>", inline=True)
        if interaction.guild.default_notifications == "all_messages":
            embed.add_field(name="Стандартный режим получения уведомлений:", value="Все сообщения", inline=True)
        else:
            embed.add_field(name="Стандартный режим получения уведомлений:", value="Только @упоминания", inline=True)
        embed.add_field(name="Кол-во каналов:", value=len(interaction.guild.channels) - len(interaction.guild.categories), inline=True)
        embed.add_field(name="Кол-во категорий:", value=len(interaction.guild.categories), inline=True)
        embed.add_field(name="Текстовых каналов:", value=len(interaction.guild.text_channels), inline=True)
        embed.add_field(name="Голосовых каналов:", value=len(interaction.guild.voice_channels), inline=True)
        embed.add_field(name="Трибун:", value=len(interaction.guild.stage_channels), inline=True)
        embed.add_field(name="Кол-во эмодзи:", value=f"{len(interaction.guild.emojis)}/{interaction.guild.emoji_limit * 2}", inline=True)
        temp = interaction.guild.verification_level
        if temp == discord.VerificationLevel.none:
            embed.add_field(name="Уровень проверки:", value="Отсутствует", inline=True)
        elif temp == discord.VerificationLevel.low:
            embed.add_field(name="Уровень проверки:", value="Низкий", inline=True)
        elif temp == discord.VerificationLevel.medium:
            embed.add_field(name="Уровень проверки:", value="Средний", inline=True)
        elif temp == discord.VerificationLevel.high:
            embed.add_field(name="Уровень проверки:", value="Высокий", inline=True)
        elif temp == discord.VerificationLevel.highest:
            embed.add_field(name="Уровень проверки:", value="Очень высокий", inline=True)
        embed.add_field(name="Дата создания:", value=f"{discord.utils.format_dt(interaction.guild.created_at, 'D')} ({discord.utils.format_dt(interaction.guild.created_at, 'R')})", inline=True)
        if interaction.guild.rules_channel is not None:
            embed.add_field(name="Канал с правилами:", value=interaction.guild.rules_channel.mention)
        else:
            embed.add_field(name="Канал с правилами:", value="Недоступно (сервер не является сервером сообщества)")
        embed.add_field(name="Веток:", value=f"{len(interaction.guild.threads)}")
        roles = ""
        counter = 0
        guild_roles = await interaction.guild.fetch_roles()
        guild_roles = list(guild_roles)
        guild_roles.sort(key=lambda x: x.position, reverse=True)
        for role in guild_roles:
            if counter <= 15: roles += f"{role.mention}, "
            else:
                roles += f"и ещё {len(guild_roles) - 16}..."
                break
            counter += 1
        embed.add_field(name=f"Роли ({len(interaction.guild.roles) - 1}):", value=roles)
        if interaction.guild.icon is not None: embed.set_thumbnail(url=interaction.guild.icon.replace(static_format="png", size=1024))
        if interaction.guild.banner is not None: embed.set_image(url=interaction.guild.banner.replace(static_format="png"))
        embed.set_footer(text=f"ID: {interaction.guild.id}")

        if interaction.guild.banner is not None:
            banner = discord.Embed(color=discord.Color.orange(), description=f"[Скачать]({interaction.guild.banner.url})")
            banner.set_author(name=f"Баннер {interaction.guild.name}")
            banner.set_image(url=interaction.guild.banner.url)
        else:
            banner = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У сервера отсутствует баннер!")

        if interaction.guild.icon is not None:
            icon = discord.Embed(color=discord.Color.orange(), description=f"[Скачать]({interaction.guild.icon.url})")
            icon.set_author(name=f"Аватар {interaction.guild.name}")
            icon.set_image(url=interaction.guild.icon.url)
        else:
            icon = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У сервера отсутствует аватар!")

        class SelectMenu(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="Аватар", value="avatar", description="Получить аватар сервера.", emoji="🖼️"),
                    discord.SelectOption(label="Баннер", value="banner", description="Получить баннер сервера (при наличии).", emoji="🏙️"),
                    discord.SelectOption(label="Информация", value="main", description="Информация об сервере.", emoji="📙")
                ]
                super().__init__(placeholder="Информация...", min_values=1, max_values=1, options=options)
            
            async def callback(self, viewinteract: discord.Interaction):
                if self.values[0] == "main":
                    await viewinteract.response.send_message(embed=embed, ephemeral=True)
                elif self.values[0] == "avatar":
                    await viewinteract.response.send_message(embed=icon, ephemeral=True)
                else:
                    await viewinteract.response.send_message(embed=banner, ephemeral=True)

        class View(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(SelectMenu())

        await interaction.response.send_message(embed=embed, view=View())

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(ServerInfo(bot))
