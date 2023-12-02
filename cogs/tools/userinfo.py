import discord

from discord.ext import commands
from discord import app_commands

from . import default_cooldown

from classes import checks
from classes.checks import isPremium

from config import settings
from config import coders
from config import supports
from config import bug_hunters
from config import bug_terminators
from config import verified

class UserInfo(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(name="userinfo", description="[Полезности] Показывает информацию о пользователе")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(member='Участник')
    async def userinfo(self, interaction: discord.Interaction, member: discord.User = None):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(member, discord.User):
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Пользователь должен находиться на сервере для использования команды на нём!")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
        badges = ''
        if member is None: member = interaction.user
        else:
            try:
                member = await interaction.guild.fetch_member(member.id)
            except:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Участник должен находиться на сервере для использования команды!")
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            member = await interaction.guild.fetch_member(member.id)
        except:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description=(
                    "Странно, но нам не удалось найти Вас как участника этого сервера. Так быть не должно. "
                    "Обратитесь в поддержку по ссылке в \"обо мне\" бота или по кнопке в `/help` или `/botinfo`."
                )
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        member_color = member.color
        if member_color.value == 0:
            member_color = discord.Color.orange()
        
        embed = discord.Embed(color=member_color, description=f"[Скачать]({member.display_avatar.replace(static_format='png', size=2048)})")
        embed.set_author(name=f"Аватар {member}")
        embed.set_image(url=member.display_avatar.replace(static_format="png", size=2048))
        embed.set_footer(text=f"Формат: png | Размер: 2048 | Тип аватара: Серверный.")

        if checks.is_in_blacklist(member.id):
            badges += '<:ban:946031802634612826> '
        if isPremium(self.bot, member.id) != 'None':
            badges += '<a:premium:988735181546475580> '
        if member.is_timed_out():
            badges += '<:timeout:950702768782458893> '
        if member.id == settings['owner_id']:
            badges += '<:botdev:977645046188871751> '
        if member.id in coders:
            badges += '<:code:946056751646638180> '
        if member.id in supports:
            badges += '<:support:946058006641143858> '
        if member.id in bug_hunters:
            badges += '<:bug_hunter:955497457020715038> '
        if member.id in bug_terminators:
            badges += '<:bug_terminator:955891723152801833> '
        if member.id in verified:
            badges += '<:verified:946057332389978152> '
        if member.bot:
            badges += '<:bot:946064625525465118> '
        emb: discord.Embed
        global_name = member.global_name or member.name
        username = str(member)
        if member.nick is None:
            emb = discord.Embed(
                title=f"`{global_name} "
                f"({username})` {badges}", 
                color=member_color
            )
        else:
            emb = discord.Embed(
                title=f"`{global_name} "
                f"({username})` | `{member.nick}` {badges}", 
                color=member_color
            )
        emb.add_field(name="Упоминание:", value=member.mention, inline=False)
        if self.bot.intents.presences:
            if member.status == discord.Status.online:
                emb.add_field(name="Статус:", value="🟢 В сети", inline=False)
            elif member.status == discord.Status.idle:
                emb.add_field(name="Статус:", value="🌙 Нет на месте", inline=False)
            elif member.status == discord.Status.dnd:
                emb.add_field(name="Статус:", value="🔴 Не беспокоить", inline=False)
            else:
                emb.add_field(name="Статус:", value="🔘 Не в сети", inline=False)
        emb.add_field(name="Ссылка на профиль:", value=f"[Тык](https://discord.com/users/{member.id})", inline=False)
        if member.bot:
            emb.add_field(name="Бот?:", value="Да", inline=False)
        else:
            emb.add_field(name="Бот?:", value="Нет", inline=False)
        if member.guild_permissions.administrator:
            emb.add_field(name="Администратор?:", value=f'Да', inline=False)
        else:
            emb.add_field(name="Администратор?:", value='Нет', inline=False)
        emb.add_field(name="Самая высокая роль на сервере:", value=f"{member.top_role.mention}", inline=False)
        emb.add_field(name="Акаунт был создан:", value=f"{discord.utils.format_dt(member.created_at, 'D')} ({discord.utils.format_dt(member.created_at, 'R')})", inline=False)
        emb.add_field(name="Присоединился:", value=f"{discord.utils.format_dt(member.joined_at, 'D')} ({discord.utils.format_dt(member.joined_at, 'R')})", inline=False)
        emb.set_thumbnail(url=member.display_avatar.replace(static_format="png", size=1024))
        member = await self.bot.fetch_user(member.id)
        if member.banner is not None:
            emb.set_image(url=member.banner.url)
        emb.set_footer(text=f'ID: {member.id}')

        if member.banner is not None:
            banner = discord.Embed(color=member_color, description=f"[Скачать]({member.banner.url})")
            banner.set_author(name=f"Баннер {member}")
            banner.set_image(url=member.banner.url)
        else:
            banner = discord.Embed(title="Ошибка", color=discord.Color.red(), description="У пользователя отсутствует баннер!")

        class SelectMenu(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="Аватар", value="avatar", description="Получить аватар пользователя.", emoji="🖼️"),
                    discord.SelectOption(label="Баннер", value="banner", description="Получить баннер пользователя (при наличии).", emoji="🏙️"),
                    discord.SelectOption(label="Информация", value="main", description="Информация об пользователе.", emoji="📙")
                ]
                super().__init__(placeholder="Информация...", min_values=1, max_values=1, options=options)
            
            async def callback(self, viewinteract: discord.Interaction):
                if self.values[0] == "main":
                    await viewinteract.response.send_message(embed=emb, ephemeral=True)
                elif self.values[0] == "avatar":
                    await viewinteract.response.send_message(embed=embed, ephemeral=True)
                else:
                    await viewinteract.response.send_message(embed=banner, ephemeral=True)

        class View(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(SelectMenu())

        await interaction.response.send_message(embed=emb, view=View())

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(UserInfo(bot))