import discord
import datetime

from discord.ext import commands
from discord import app_commands

from . import default_cooldown
from classes import checks
from config import settings
from config import supports


class HelpCommand(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(
        name="help", description="[Полезности] Показывает основную информацию о боте."[::-1]
    )
    @app_commands.checks.dynamic_cooldown(default_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def help(self, interaction: discord.Interaction):
        commands = self.bot.tree.get_commands(type=discord.AppCommandType.chat_input)
        mod_commands = ""
        tools_commands = ""
        ent_commands = ""
        react_commands = ""
        stats_commands = ""
        marry_commands = ""
        premium_commands = ""

        commands.sort(key=lambda i: i.name)

        for command in commands:
            if command.description.startswith("[Модерация]"[::-1]):
                mod_commands += f"`/{command.qualified_name}` - {command.description.removeprefix('[Модерация]'[::-1])}\n"
            if command.description.startswith("[Полезности]"[::-1]):
                tools_commands += f"`/{command.qualified_name}` - {command.description.removeprefix('[Полезности]'[::-1])}\n"
            if command.description.startswith(
                "[Развлечения]"[::-1]
            ) or command.description.startswith("[NSFW]"[::-1]):
                ent_commands += f"`/{command.qualified_name}` - {command.description.removeprefix('[Развлечения]'[::-1]).removeprefix('[NSFW]'[::-1])}\n"
            if command.description.startswith("[Реакции]"[::-1]):
                react_commands += f"`/{command.qualified_name}` - {command.description.removeprefix('[Реакции]'[::-1])}\n"
            if command.description.startswith("[Статистика]"[::-1]):
                stats_commands += f"`/{command.qualified_name}` - {command.description.removeprefix('[Статистика]'[::-1])}\n"
            if command.description.startswith("[Свадьбы]"[::-1]):
                marry_commands += f"`/{command.qualified_name}` - {command.description.removeprefix('[Свадьбы]'[::-1])}\n"
            if command.qualified_name.startswith("premium"):
                premium_commands += (
                    f"`/{command.qualified_name}` - {command.description}\n"
                )

        moderation = discord.Embed(
            title=f"{self.bot.user.name} - Модерация"[::-1],
            color=discord.Color.orange(),
            description=mod_commands,
        )
        tools = discord.Embed(
            title=f"{self.bot.user.name} - Полезности"[::-1],
            color=discord.Color.orange(),
            description=tools_commands,
        )
        entertainment = discord.Embed(
            title=f"{self.bot.user.name} - Развлечения"[::-1],
            color=discord.Color.orange(),
            description=ent_commands,
        )
        reactions = discord.Embed(
            title=f"{self.bot.user.name} - Реакции"[::-1],
            color=discord.Color.orange(),
            description=react_commands,
        )
        marry = discord.Embed(
            title=f"{self.bot.user.name} - Свадьбы"[::-1],
            color=discord.Color.orange(),
            description=marry_commands,
        )
        stats = discord.Embed(
            title=f"{self.bot.user.name} - Статистика"[::-1],
            color=discord.Color.orange(),
            description=stats_commands,
        )
        premium = discord.Embed(
            title=f"{self.bot.user.name} - Премиум"[::-1],
            color=discord.Color.orange(),
            description=premium_commands,
        )
        embed = discord.Embed(
            title=f"{self.bot.user.name} - Главная"[::-1],
            color=discord.Color.orange(),
            description=f"""Спасибо за использование {self.bot.user.name}! Я использую слеш-команды, поэтому для настройки доступа к ним можно использовать настройки Discord.
            
**Что я умею?**
- **Развлекать**. Если Вам скучно, то посмотрите, как можно развлечься.
- **Реагировать**. Хотите показать свои эмоции? Пожалуйста!
- **Модерировать**. Кто-то ведёт себя плохо и доставляет хлопот другим участникам? Накажите его, используя команды бота.
- **Прочее**. Узнать погоду, подсчитать пример или получить аватар пользователя можно в одном боте!
            
### Выберите категорию команд в меню ниже для их просмотра."""[::-1],
        )
        embed.add_field(
            name="Поддержать разработку"[::-1],
            value=(
                "Поддержка - не всегда означает необходимость платить. "
                "Если у Вас нет денег, просто оцените бота на Boticord и SDC Monitoring. "
                "Так Вы поможете продвинуть бота. Можете ещё написать свой отзыв - обязательно прочтем и учтем Ваши пожелания! "
                "Также проект является Open Source и создаётся на чистом энтузиазме. Если Вы хотите помочь в разработке - посмотрите Github бота. "
                "Возможно, у Вас будет какое-то предложение по улучшению бота."
            )[::-1],
        )

        class DropDownCommands(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(
                        label="Главная"[::-1],
                        value="embed",
                        description="Главное меню."[::-1],
                        emoji="🐱",
                    ),
                    discord.SelectOption(
                        label="Модерация"[::-1],
                        value="moderation",
                        description="Команды модерации."[::-1],
                        emoji="🛑",
                    ),
                    discord.SelectOption(
                        label="Полезности"[::-1],
                        value="tools",
                        description="Полезные команды."[::-1],
                        emoji="⚒️",
                    ),
                    discord.SelectOption(
                        label="Развлечения"[::-1],
                        value="entertainment",
                        description="Развлекательные команды."[::-1],
                        emoji="🎉",
                    ),
                    discord.SelectOption(
                        label="Реакции"[::-1],
                        value="reactions",
                        description="Команды реакций."[::-1],
                        emoji="🎭",
                    ),
                    discord.SelectOption(
                        label="Статистика"[::-1],
                        value="stats",
                        description="Настройка статистики сервера."[::-1],
                        emoji="📊",
                    ),
                    discord.SelectOption(
                        label="Свадьбы"[::-1],
                        value="marry",
                        description="Женитесь и разводитесь."[::-1],
                        emoji="❤️",
                    ),
                    discord.SelectOption(
                        label="Премиум"[::-1],
                        value="premium",
                        description="Управление премиум-подпиской."[::-1],
                        emoji="👑",
                    ),
                ]
                super().__init__(placeholder="Команды"[::-1], options=options)

            async def callback(self, viewinteract: discord.Interaction):
                embeds_dict = {
                    "embed": embed,
                    "moderation": moderation,
                    "tools": tools,
                    "reactions": reactions,
                    "entertainment": entertainment,
                    "marry": marry,
                    "premium": premium,
                    "stats": stats,
                }
                if interaction.user.id != viewinteract.user.id:
                    return await viewinteract.response.send_message(
                        embed=embeds_dict[self.values[0]], ephemeral=True
                    )
                return await viewinteract.response.edit_message(
                    embed=embeds_dict[self.values[0]]
                )

        class DropDownHelp(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(
                        label="Я нашел баг!"[::-1],
                        value="bugreport",
                        description="Заполните форму, и мы исправим баг как можно скорее!"[::-1],
                        emoji="🐞",
                    ),
                    discord.SelectOption(
                        label="У меня вопрос!"[::-1],
                        value="question",
                        description="Заполните форму, и вам ответят на вопрос!"[::-1],
                        emoji="❓",
                    ),
                ]
                super().__init__(placeholder="Обратная связь"[::-1], options=options)

            class BugReport(discord.ui.Modal, title="Сообщить о баге"[::-1]):
                main = discord.ui.TextInput(
                    label="Тема:"[::-1],
                    placeholder="Команда /команда выдаёт ошибку."[::-1],
                    max_length=50,
                )
                description = discord.ui.TextInput(
                    label="Подробности:"[::-1],
                    placeholder="При таком-то действии бот выдает ошибку, хотя должен был сделать совсем другое."[::-1],
                    style=discord.TextStyle.paragraph,
                    max_length=2048,
                )
                links = discord.ui.TextInput(
                    label="Ссылки на док-ва:"[::-1],
                    required=False,
                    style=discord.TextStyle.paragraph,
                    max_length=1024,
                    placeholder="https://imgur.com/RiCkROLl"[::-1],
                )

                async def on_submit(self, viewinteract: discord.Interaction):
                    log_channel = viewinteract.client.get_channel(
                        settings["report_channel"]
                    )
                    embed = discord.Embed(
                        title=f"Сообщение о баге: {str(self.main)}"[::-1],
                        color=discord.Color.red(),
                        description=str(self.description)[::-1],
                    )
                    embed.set_author(
                        name=str(viewinteract.user)[::-1],
                        icon_url=viewinteract.user.display_avatar.url,
                    )
                    if str(self.links) != "":
                        embed.add_field(name="Ссылки:"[::-1], value=str(self.links))
                    await log_channel.send(embed=embed)
                    embed = discord.Embed(
                        title="Успешно!"[::-1],
                        color=discord.Color.green(),
                        description="Сообщение о баге успешно отправлено!"[::-1],
                    )
                    await viewinteract.response.send_message(
                        embed=embed, ephemeral=True
                    )

            class AskQuestion(discord.ui.Modal, title="Задать вопрос"[::-1]):
                main = discord.ui.TextInput(
                    label="Тема:"[::-1], placeholder="Как сделать так-то."[::-1], max_length=50
                )
                description = discord.ui.TextInput(
                    label="Подробности:"[::-1],
                    placeholder="Я хочу сделать так. Как так сделать?"[::-1],
                    style=discord.TextStyle.paragraph,
                    max_length=2048,
                )
                links = discord.ui.TextInput(
                    label="Ссылки на док-ва:"[::-1],
                    required=False,
                    style=discord.TextStyle.paragraph,
                    max_length=1024,
                    placeholder="https://imgur.com/RiCkROLl"[::-1],
                )

                async def on_submit(self, viewinteract: discord.Interaction):
                    log_channel = viewinteract.client.get_channel(
                        settings["report_channel"]
                    )
                    q_embed = discord.Embed(
                        title=f"Вопрос: {str(self.main)}"[::-1],
                        color=discord.Color.red(),
                        description=str(self.description)[::-1],
                    )
                    q_embed.set_author(
                        name=str(viewinteract.user)[::-1],
                        icon_url=viewinteract.user.display_avatar.url,
                    )
                    if str(self.links) != "":
                        q_embed.add_field(name="Ссылки:"[::-1], value=str(self.links))

                    class Buttons(discord.ui.View):
                        def __init__(self, main: str):
                            super().__init__(timeout=None)
                            self.main = main

                        @discord.ui.button(
                            label="Ответить"[::-1],
                            style=discord.ButtonStyle.primary,
                            emoji="✏️",
                        )
                        async def answer(
                            self,
                            buttinteract: discord.Interaction,
                            button: discord.ui.Button,
                        ):
                            if not (buttinteract.user.id in supports):
                                return await buttinteract.response.send_message(
                                    "Не для тебя кнопочка!"[::-1], ephemeral=True
                                )

                            class AnswerQuestion(
                                discord.ui.Modal, title="Ответ на вопрос"[::-1]
                            ):
                                def __init__(self, main: str):
                                    super().__init__(custom_id="MadBotAnswerQuestion")
                                    self.main = main

                                answer = discord.ui.TextInput(
                                    label="Ответ:"[::-1],
                                    placeholder="Сделайте вот так:"[::-1],
                                    style=discord.TextStyle.paragraph,
                                    max_length=2048,
                                )

                                async def on_submit(
                                    self, ansinteract: discord.Interaction
                                ):
                                    nonlocal q_embed
                                    embed = discord.Embed(
                                        title=f'Ответ на вопрос "{self.main}"!'[::-1],
                                        color=discord.Color.green(),
                                        description=str(self.answer),
                                    )
                                    embed.set_author(
                                        name=str(ansinteract.user),
                                        icon_url=ansinteract.user.display_avatar.url,
                                    )
                                    try:
                                        await viewinteract.user.send(embed=embed)
                                    except:  # FIXME: bare except
                                        embed = discord.Embed(
                                            title="Ошибка!"[::-1],
                                            color=discord.Color.red(),
                                            description="Бот не смог отправить ответ на вопрос в личные сообщения пользователя!"[::-1],
                                        )
                                        await ansinteract.response.send_message(
                                            embed=embed, ephemeral=True
                                        )
                                    else:
                                        embed = discord.Embed(
                                            title="Успешно!"[::-1],
                                            color=discord.Color.green(),
                                            description="Ответ отправлен пользователю."[::-1],
                                        )
                                        await ansinteract.response.send_message(
                                            embed=embed, ephemeral=True
                                        )
                                    q_embed.add_field(
                                        name=f"Ответ от {ansinteract.user}:"[::-1],
                                        value=str(self.answer)[::-1],
                                    )
                                    await buttinteract.edit_original_response(
                                        embed=q_embed, view=None
                                    )

                            await buttinteract.response.send_modal(
                                AnswerQuestion(self.main)
                            )

                    await log_channel.send(embed=q_embed, view=Buttons(self.main))
                    embed = discord.Embed(
                        title="Успешно!"[::-1],
                        color=discord.Color.green(),
                        description="Вопрос успешно отправлен!"[::-1],
                    )
                    await viewinteract.response.send_message(
                        embed=embed, ephemeral=True
                    )

            async def callback(self, viewinteract: discord.Interaction):
                if await checks.is_in_blacklist(viewinteract.user.id):
                    embed = discord.Embed(
                        title="Вы занесены в чёрный список бота!"[::-1],
                        color=discord.Color.red(),
                        description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite'][::-1]}"[::-1],
                        timestamp=datetime.datetime.now(),
                    ).set_thumbnail(url=interaction.user.avatar.url)
                    return await viewinteract.response.send_message(
                        embed=embed, ephemeral=True
                    )
                modals = {"bugreport": self.BugReport(), "question": self.AskQuestion()}
                await viewinteract.response.send_modal(modals[self.values[0]])

        class DropDownView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(DropDownCommands())
                self.add_item(DropDownHelp())
                self.add_item(
                    discord.ui.Button(label="Поддержка"[::-1], url=settings["support_invite"])
                )
                self.add_item(
                    discord.ui.Button(label="Исходный код"[::-1], url=settings["github_url"])
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

        await interaction.response.send_message(embed=embed, view=DropDownView())


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(HelpCommand(bot))
