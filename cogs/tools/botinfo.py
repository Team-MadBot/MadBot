import discord
import sys
import distro
import datetime

from discord.ext import commands
from discord import app_commands

from . import default_cooldown

from classes import checks
from classes import db

from config import settings
from config import started_at


class BotInfo(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    async def cog_load(self):
        thanks_users = {  # я теперь знаю, что ещё переписать на базу данных.
            754719910256574646: "Бывший второй разработчик бота и лучший бета-тестер. Написал некоторые команды развлечений "
            "и помог выявить более 20-ти багов. Один из спонсоров бота.",
            777140702747426817: "Помимо его работы саппортом, он часто апает бота, чем помогает в распространении его. "
            "Один из первых спонсоров бота.",
            529302484901036043: "Бывший третий разработчик бота, который помогал в переписи текущего кода. "
            "Также он помог с выбором текущего хода развития бота.",
        }
        self.thanks_user = {}
        for tu in thanks_users:
            if not self.bot.intents.members:
                try:
                    u = await self.bot.fetch_user(tu)
                except discord.NotFound:
                    u = None
            else:
                u = self.bot.get_user(tu)

            self.thanks_user[str(u or f"Пользователь с ID {tu}")] = thanks_users[tu]

    @app_commands.command(name="botinfo", description="[Полезности] Информация о боте")
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"{self.bot.user.name} - v{settings['curr_version']}",
            color=discord.Color.orange(),
            description=f"Для выбора категории используйте меню снизу.\n\n**Основная информация:**",
        )
        embed.add_field(name="Разработчик", value=f"<@!{settings['owner_id']}>")
        embed.add_field(name="ID разработчика", value=f"`{settings['owner_id']}`")
        embed.add_field(name="ID бота", value=f"`{self.bot.user.id}`")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text=f"©️ 2021 - {datetime.datetime.now().year} MadBot. Все права защищены."
        )

        bot_stats = await db.get_bot_stats()
        stats = discord.Embed(
            title=f"{self.bot.user.name} - Статистика", color=discord.Color.orange()
        )
        stats.add_field(name="Пинг", value=f"{int(round(self.bot.latency, 3)*1000)}ms")
        stats.add_field(name="Запущен", value=f"<t:{started_at}:R>")
        stats.add_field(name="Кол-во серверов", value=f"{len(self.bot.guilds):,}")
        stats.add_field(name="Кол-во участников", value=f"{len(self.bot.users):,}")
        stats.add_field(
            name="Последняя использованная команда",
            value=bot_stats["last_command"] or "Ещё ни разу команды не использовались",
        )
        stats.add_field(
            name="Кол-во команд/контекстных меню",
            value=f"{len(self.bot.tree.get_commands(type=discord.AppCommandType.chat_input)):,}/{len(self.bot.tree.get_commands(type=discord.AppCommandType.user)) + len(self.bot.tree.get_commands(type=discord.AppCommandType.message)):,}",
        )
        stats.add_field(
            name="Обработано команд", value=f"{bot_stats['used_commands']:,}"
        )
        stats.set_thumbnail(url=self.bot.user.display_avatar.url)
        stats.set_footer(
            text=str(interaction.user), icon_url=interaction.user.display_avatar.url
        )

        versions = discord.Embed(
            title=f"{self.bot.user.name} - Версии", color=discord.Color.orange()
        )
        versions.add_field(name="Версия", value=settings["curr_version"])
        versions.add_field(
            name="Версия discord.py",
            value=f"{discord.version_info.major}.{discord.version_info.minor}.{discord.version_info.micro} `{discord.version_info.releaselevel.upper()}`",
        )
        versions.add_field(
            name="Версия Python",
            value=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        )
        ver_info = sys.platform
        if ver_info.startswith("win32"):
            ver_info = "Windows"
        if ver_info.startswith("linux"):
            ver_info = distro.name(pretty=True)
        if ver_info.startswith("aix"):
            ver_info = "AIX"
        if ver_info.startswith("darwin"):
            ver_info = "MacOS"
        versions.add_field(name="Операционная система", value=ver_info)
        versions.set_thumbnail(url=self.bot.user.display_avatar.url)
        versions.set_footer(
            text=str(interaction.user), icon_url=interaction.user.display_avatar.url
        )

        thanks = discord.Embed(
            title=f"{self.bot.user.name} - Благодарности",
            color=discord.Color.orange(),
            description="Этим людям я очень благодарен. Благодаря им, MadBot поднимается и улучшается.",
        )
        thanks.set_thumbnail(url=self.bot.user.display_avatar.url)
        thanks.set_footer(
            text=str(interaction.user), icon_url=interaction.user.display_avatar.url
        )

        for tu in self.thanks_user:
            thanks.add_field(name=tu, value=self.thanks_user[tu], inline=False)

        embeds = {
            "embed": embed,
            "stats": stats,
            "versions": versions,
            "thanks": thanks,
        }

        class DropDown(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(
                        label="Главная",
                        value="embed",
                        description="Главное меню.",
                        emoji="🐱",
                    ),
                    discord.SelectOption(
                        label="Статистика",
                        value="stats",
                        description="Статистика бота.",
                        emoji="📊",
                    ),
                    discord.SelectOption(
                        label="Версии",
                        value="versions",
                        description="Версии библиотек и Python.",
                        emoji="⚒️",
                    ),
                    discord.SelectOption(
                        label="Благодарности",
                        value="thanks",
                        description="Эти люди сделали многое для бота.",
                        emoji="❤️",
                    ),
                ]
                super().__init__(placeholder="Выбор...", options=options, row=1)

            async def callback(self, viewinteract: discord.Interaction):
                if interaction.user != viewinteract.user:
                    return await viewinteract.response.send_message(
                        embed=embeds[self.values[0]], ephemeral=True
                    )
                else:
                    await interaction.edit_original_response(
                        embed=embeds[self.values[0]]
                    )
                    await viewinteract.response.defer()

        class View(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(
                    discord.ui.Button(label="Поддержка", url=settings["support_invite"])
                )
                self.add_item(
                    discord.ui.Button(label="Исходный код", url=settings["github_url"])
                )
                self.add_item(
                    discord.ui.Button(
                        label="Добавить бота",
                        url=f"https://discord.com/oauth2/authorize?client_id={settings['app_id']}&permissions={settings['perm_scope']}&scope=bot%20applications.commands",
                    )
                )
                self.add_item(
                    discord.ui.Button(
                        label="Апнуть бота: BotiCord.top",
                        url=f"https://boticord.top/bot/{settings['app_id']}",
                        emoji="<:bc:947181639384051732>",
                    )
                )
                self.add_item(
                    discord.ui.Button(
                        label="Апнуть бота: SDC Monitoring",
                        url=f"https://bots.server-discord.com/{settings['app_id']}",
                        emoji="<:favicon:981586173204000808>",
                    )
                )
                self.add_item(DropDown())

        await interaction.response.send_message(embed=embed, view=View())


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(BotInfo(bot))
