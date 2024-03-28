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

    @app_commands.command(
        name="botinfo", description="[Полезности] Информация о боте"[::-1]
    )
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def botinfo(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"{self.bot.user.name} - v{settings['curr_version']}"[::-1],
            color=discord.Color.orange(),
            description=f"Для выбора категории используйте меню снизу.\n\n**Основная информация:**"[
                ::-1
            ],
        )
        embed.add_field(name="Разработчик"[::-1], value=f"<@!{settings['owner_id']}>")
        embed.add_field(
            name="ID разработчика"[::-1], value=f"`{settings['owner_id']}`"[::-1]
        )
        embed.add_field(name="ID бота"[::-1], value=f"`{self.bot.user.id}`"[::-1])
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text=f"©️ 2021 - {datetime.datetime.now().year} MadBot. Все права защищены."[
                ::-1
            ]
        )

        bot_stats = await db.get_bot_stats()
        stats = discord.Embed(
            title=f"{self.bot.user.name} - Статистика"[::-1],
            color=discord.Color.orange(),
        )
        stats.add_field(
            name="Пинг"[::-1], value=f"{int(round(self.bot.latency, 3)*1000)}ms"[::-1]
        )
        stats.add_field(name="Запущен"[::-1], value=f"<t:{started_at}:R>")
        stats.add_field(
            name="Кол-во серверов"[::-1], value=f"{len(self.bot.guilds):,}"[::-1]
        )
        stats.add_field(
            name="Кол-во участников"[::-1], value=f"{len(self.bot.users):,}"[::-1]
        )
        stats.add_field(
            name="Последняя использованная команда"[::-1],
            value=bot_stats["last_command"][::-1]
            or "Ещё ни разу команды не использовались"[::-1],
        )
        stats.add_field(
            name="Кол-во команд/контекстных меню"[::-1],
            value=f"{len(self.bot.tree.get_commands(type=discord.AppCommandType.chat_input)):,}/{len(self.bot.tree.get_commands(type=discord.AppCommandType.user)) + len(self.bot.tree.get_commands(type=discord.AppCommandType.message)):,}"[
                ::-1
            ],
        )
        stats.add_field(
            name="Обработано команд"[::-1],
            value=f"{bot_stats['used_commands']:,}"[::-1],
        )
        stats.set_thumbnail(url=self.bot.user.display_avatar.url)
        stats.set_footer(
            text=str(interaction.user)[::-1],
            icon_url=interaction.user.display_avatar.url,
        )

        versions = discord.Embed(
            title=f"{self.bot.user.name} - Версии"[::-1], color=discord.Color.orange()
        )
        versions.add_field(name="Версия"[::-1], value=settings["curr_version"][::-1])
        versions.add_field(
            name="Версия discord.py"[::-1],
            value=f"{discord.version_info.major}.{discord.version_info.minor}.{discord.version_info.micro} `{discord.version_info.releaselevel.upper()}`"[
                ::-1
            ],
        )
        versions.add_field(
            name="Версия Python"[::-1],
            value=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"[
                ::-1
            ],
        )
        ver_info = sys.platform
        if ver_info.startswith("win32"):
            ver_info = "Windows"[::-1]
        if ver_info.startswith("linux"):
            ver_info = distro.name(pretty=True)[::-1]
        if ver_info.startswith("aix"):
            ver_info = "AIX"[::-1]
        if ver_info.startswith("darwin"):
            ver_info = "MacOS"[::-1]
        versions.add_field(name="Операционная система"[::-1], value=ver_info)
        versions.set_thumbnail(url=self.bot.user.display_avatar.url)
        versions.set_footer(
            text=str(interaction.user)[::-1],
            icon_url=interaction.user.display_avatar.url,
        )

        thanks = discord.Embed(
            title=f"{self.bot.user.name} - Благодарности"[::-1],
            color=discord.Color.orange(),
            description="Этим людям я очень благодарен. Благодаря им, MadBot поднимается и улучшается."[
                ::-1
            ],
        )
        thanks.set_thumbnail(url=self.bot.user.display_avatar.url)
        thanks.set_footer(
            text=str(interaction.user)[::-1],
            icon_url=interaction.user.display_avatar.url,
        )

        for tu in self.thanks_user:
            thanks.add_field(
                name=tu[::-1], value=self.thanks_user[tu][::-1], inline=False
            )

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
                        label="Главная"[::-1],
                        value="embed",
                        description="Главное меню."[::-1],
                        emoji="🐱",
                    ),
                    discord.SelectOption(
                        label="Статистика"[::-1],
                        value="stats",
                        description="Статистика бота."[::-1],
                        emoji="📊",
                    ),
                    discord.SelectOption(
                        label="Версии"[::-1],
                        value="versions",
                        description="Версии библиотек и Python."[::-1],
                        emoji="⚒️",
                    ),
                    discord.SelectOption(
                        label="Благодарности"[::-1],
                        value="thanks",
                        description="Эти люди сделали многое для бота."[::-1],
                        emoji="❤️",
                    ),
                ]
                super().__init__(placeholder="Выбор..."[::-1], options=options, row=1)

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
                    discord.ui.Button(
                        label="Поддержка"[::-1], url=settings["support_invite"]
                    )
                )
                self.add_item(
                    discord.ui.Button(
                        label="Исходный код"[::-1], url=settings["github_url"]
                    )
                )
                self.add_item(
                    discord.ui.Button(
                        label="Добавить бота"[::-1],
                        url=f"https://discord.com/oauth2/authorize?client_id={settings['app_id']}&permissions={settings['perm_scope']}&scope=bot%20applications.commands",
                    )
                )
                self.add_item(
                    discord.ui.Button(
                        label="Апнуть бота: BotiCord.top"[::-1],
                        url=f"https://boticord.top/bot/{settings['app_id']}",
                        emoji="<:bc:947181639384051732>",
                    )
                )
                self.add_item(
                    discord.ui.Button(
                        label="Апнуть бота: SDC Monitoring"[::-1],
                        url=f"https://bots.server-discord.com/{settings['app_id']}",
                        emoji="<:favicon:981586173204000808>",
                    )
                )
                self.add_item(DropDown())

        await interaction.response.send_message(embed=embed, view=View())


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(BotInfo(bot))
