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

    @app_commands.command(name="help", description="[Полезности] Показывает основную информацию о боте.")
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
        for command in commands:
            if command.description.startswith("[Модерация]"):
                mod_commands += f"`/{command.qualified_name}` - {command.description.removeprefix('[Модерация]')}\n"
            if command.description.startswith("[Полезности]"):
                tools_commands += f"`/{command.qualified_name}` - {command.description.removeprefix('[Полезности]')}\n"
            if command.description.startswith("[Развлечения]") or command.description.startswith("[NSFW]"):
                ent_commands += f"`/{command.qualified_name}` - {command.description.removeprefix('[Развлечения]').removeprefix('[NSFW]')}\n"
            if command.description.startswith("[Реакции]"):
                react_commands += f"`/{command.qualified_name}` - {command.description.removeprefix('[Реакции]')}\n"
            if command.description.startswith("[Статистика]"):
                stats_commands += f"`/{command.qualified_name}` - {command.description.removeprefix('[Статистика]')}\n"
            if command.description.startswith("[Свадьбы]"):
                marry_commands += f"`/{command.qualified_name}` - {command.description.removeprefix('[Свадьбы]')}\n"
            if command.qualified_name.startswith("premium"):
                premium_commands += f"`/{command.qualified_name}` - {command.description}\n"

        moderation = discord.Embed(
           title=f"{self.bot.user.name} - Модерация", 
           color=discord.Color.orange(), 
           description=mod_commands
        )
        tools = discord.Embed(
            title=f"{self.bot.user.name} - Полезности",
            color=discord.Color.orange(), 
            description=tools_commands
        )
        entartaiment = discord.Embed(
            title=f"{self.bot.user.name} - Развлечения",
            color=discord.Color.orange(), 
            description=ent_commands
        )
        reactions = discord.Embed(
            title=f"{self.bot.user.name} - Реакции",
            color=discord.Color.orange(),
            description=react_commands
        )
        stats = discord.Embed(
            title=f"{self.bot.user.name} - Свадьбы",
            color=discord.Color.orange(),
            description=stats_commands
        )
        marry = discord.Embed(
            title=f"{self.bot.user.name} - Статистика",
            color=discord.Color.orange(),
            description=marry_commands
        )
        premium = discord.Embed(
            title=f"{self.bot.user.name} - Премиум",
            color=discord.Color.orange(),
            description=premium_commands
        )
        embed = discord.Embed(
            title=f"{self.bot.user.name} - Главная", 
            color=discord.Color.orange(), 
            description=f"""Спасибо за использование {self.bot.user.name}! Я использую слеш-команды, поэтому для настройки доступа к ним можно использовать настройки Discord.
            
**Что я умею?**
- **Развлекать**. Если Вам скучно, то посмотрите, как можно развлечься.
- **Реагировать**. Хотите показать свои эмоции? Пожалуйста!
- **Модерировать**. Кто-то ведёт себя плохо и доставляет хлопот другим участникам? Накажите его, используя команды бота.
- **Прочее**. Узнать погоду, подсчитать пример или получить аватар пользователя можно в одном боте!
            
Выберите категорию команд для их просмотра.""")
        embed.add_field(
            name="Поддержать разработку",
            value=f"""Поддержка - не всегда означает необходимость платить. Если у Вас нету денег, просто оцените бота на Boticord и SDC Monitoring. Так Вы поможете продвинуть бота. Можете ещё написать свой отзыв - обязательно прочтем и учтем.
            
**СКОРО:** Если у Вас есть деньги, Вы можете связаться с разработчиком для покупки MadBot Premium. Так мы сможет продолжать разработку, а Вы получите уникальные функции."""
        )

        class DropDownCommands(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="Главная", value="embed", description="Главное меню.", emoji="🐱"),
                    discord.SelectOption(label="Модерация", value="moderation", description="Команды модерации.", emoji="🛑"),
                    discord.SelectOption(label="Полезности", value="tools", description="Полезные команды.", emoji="⚒️"),
                    discord.SelectOption(label="Развлечения", value="entartaiment", description="Развлекательные команды.", emoji="🎉"),
                    discord.SelectOption(label="Реакции", value="reactions", description="Команды реакций.", emoji="🎭"),
                    discord.SelectOption(label="Статистика", value="stats", description="Настройка статистики сервера.", emoji="📊"),
                    discord.SelectOption(label="Свадьбы", value="marry", description="Женитесь и разводитесь.", emoji="❤️"),
                    discord.SelectOption(label="Премиум", value="premium", description="Управление премиум-подпиской.", emoji="👑")
                ]
                super().__init__(placeholder="Команды", options=options)
            
            async def callback(self, viewinteract: discord.Interaction):
                if interaction.user.id != viewinteract.user.id:
                    if self.values[0] == "embed":
                        return await viewinteract.response.send_message(embed=embed, ephemeral=True)
                    elif self.values[0] == "moderation":
                       return await viewinteract.response.send_message(embed=moderation, ephemeral=True)
                    elif self.values[0] == "tools":
                        return await viewinteract.response.send_message(embed=tools, ephemeral=True)
                    elif self.values[0] == "reactions":
                        return await viewinteract.response.send_message(embed=reactions, ephemeral=True)
                    elif self.values[0] == "entartaiment":
                        return await viewinteract.response.send_message(embed=entartaiment, ephemeral=True)
                    elif self.values[0] == "marry":
                        return await viewinteract.response.send_message(embed=marry, ephemeral=True)
                    elif self.values[0] == "premium":
                        return await viewinteract.response.send_message(embed=premium, ephemeral=True)
                    else:
                        return await viewinteract.response.send_message(embed=stats, ephemeral=True)
                if self.values[0] == "embed":
                    await viewinteract.response.edit_message(embed=embed)
                elif self.values[0] == "moderation":
                   await viewinteract.response.edit_message(embed=moderation)
                elif self.values[0] == "tools":
                    await viewinteract.response.edit_message(embed=tools)
                elif self.values[0] == "reactions":
                    return await viewinteract.response.edit_message(embed=reactions)
                elif self.values[0] == "entartaiment":
                    return await viewinteract.response.edit_message(embed=entartaiment)
                elif self.values[0] == "marry":
                    return await viewinteract.response.edit_message(embed=marry)
                elif self.values[0] == "premium":
                    return await viewinteract.response.edit_message(embed=premium)
                else:
                    return await viewinteract.response.edit_message(embed=stats)

        class DropDownHelp(discord.ui.Select):
            def __init__(self):
                options = [
                    discord.SelectOption(label="Я нашел баг!", value="bugreport", description="Заполните форму, и мы исправим баг как можно скорее!", emoji='🐞'),
                    discord.SelectOption(label="У меня вопрос!", value="question", description="Заполните форму, и вам ответят на вопрос!", emoji='❓')
                ]
                super().__init__(placeholder='Обратная связь', options=options)

            class BugReport(discord.ui.Modal, title="Сообщить о баге"):
                main = discord.ui.TextInput(label="Тема:", placeholder="Команда /команда выдаёт ошибку.", max_length=50)
                description = discord.ui.TextInput(label="Подробности:", placeholder="При таком-то действии бот выдает ошибку, хотя должен был сделать совсем другое.", style=discord.TextStyle.paragraph, max_length=2048)
                links = discord.ui.TextInput(label="Ссылки на док-ва:", required=False, style=discord.TextStyle.paragraph, max_length=1024, placeholder="https://imgur.com/RiCkROLl")

                async def on_submit(self, viewinteract: discord.Interaction):
                    log_channel = viewinteract.client.get_channel(settings['report_channel'])
                    embed = discord.Embed(title=f"Сообщение о баге: {str(self.main)}", color=discord.Color.red(), description=str(self.description))
                    embed.set_author(name=str(viewinteract.user), icon_url=viewinteract.user.display_avatar.url)
                    if str(self.links) != "":
                        embed.add_field(name="Ссылки:", value=str(self.links))
                    await log_channel.send(embed=embed)
                    embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Сообщение о баге успешно отправлено!")
                    await viewinteract.response.send_message(embed=embed, ephemeral=True)
                
            class AskQuestion(discord.ui.Modal, title="Задать вопрос"):
                main = discord.ui.TextInput(label="Тема:", placeholder="Как сделать так-то.", max_length=50)
                description = discord.ui.TextInput(label="Подробности:", placeholder="Я хочу сделать так. Как так сделать?", style=discord.TextStyle.paragraph, max_length=2048)
                links = discord.ui.TextInput(label="Ссылки на док-ва:", required=False, style=discord.TextStyle.paragraph, max_length=1024, placeholder="https://imgur.com/RiCkROLl")

                async def on_submit(self, viewinteract: discord.Interaction):
                    log_channel = viewinteract.client.get_channel(settings['report_channel'])
                    q_embed = discord.Embed(title=f"Вопрос: {str(self.main)}", color=discord.Color.red(), description=str(self.description))
                    q_embed.set_author(name=str(viewinteract.user), icon_url=viewinteract.user.display_avatar.url)
                    if str(self.links) != "":
                        q_embed.add_field(name="Ссылки:", value=str(self.links))

                    class Buttons(discord.ui.View):
                        def __init__(self, main: str):
                            super().__init__(timeout=None)
                            self.main = main
                        
                        @discord.ui.button(label="Ответить", style=discord.ButtonStyle.primary, emoji="✏️")
                        async def answer(self, buttinteract: discord.Interaction, button: discord.ui.Button):
                            if not (buttinteract.user.id in supports):
                                return await buttinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True) 
                            class AnswerQuestion(discord.ui.Modal, title="Ответ на вопрос"):
                                def __init__(self, main: str):
                                    super().__init__(custom_id="MadBotAnswerQuestion")
                                    self.main = main
                                answer = discord.ui.TextInput(label="Ответ:", placeholder="Сделайте вот так:", style=discord.TextStyle.paragraph, max_length=2048)

                                async def on_submit(self, ansinteract: discord.Interaction):
                                    nonlocal q_embed
                                    embed = discord.Embed(title=f'Ответ на вопрос "{self.main}"!', color=discord.Color.green(), description=str(self.answer))
                                    embed.set_author(name=str(ansinteract.user), icon_url=ansinteract.user.display_avatar.url)
                                    try:
                                        await viewinteract.user.send(embed=embed)
                                    except:  # FIXME: bare except
                                        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Бот не смог отправить ответ на вопрос в личные сообщения пользователя!")
                                        await ansinteract.response.send_message(embed=embed, ephemeral=True)
                                    else:
                                        embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Ответ отправлен пользователю.")
                                        await ansinteract.response.send_message(embed=embed, ephemeral=True)
                                    q_embed.add_field(name=f"Ответ от {ansinteract.user}:", value=str(self.answer))
                                    await buttinteract.edit_original_response(embed=q_embed, view=None)
                                
                            await buttinteract.response.send_modal(AnswerQuestion(self.main))

                    await log_channel.send(embed=q_embed, view=Buttons(self.main))
                    embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Вопрос успешно отправлен!")
                    await viewinteract.response.send_message(embed=embed, ephemeral=True)

            async def callback(self, viewinteract: discord.Interaction):
                if await checks.is_in_blacklist(viewinteract.user.id):
                    embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.now())
                    embed.set_thumbnail(url=interaction.user.avatar.url)
                    return await viewinteract.response.send_message(embed=embed, ephemeral=True)
                modals = {
                    'bugreport': self.BugReport(),
                    'question': self.AskQuestion()
                }
                await viewinteract.response.send_modal(modals[self.values[0]])
           
        class DropDownView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)
                self.add_item(DropDownCommands())
                self.add_item(DropDownHelp())
                self.add_item(discord.ui.Button(label="Поддержка", url=settings['support_invite']))
                self.add_item(discord.ui.Button(label="Добавить бота", url=f"https://discord.com/oauth2/authorize?client_id={settings['app_id']}&permissions={settings['perm_scope']}&scope=bot%20applications.commands"))
                self.add_item(discord.ui.Button(label="Апнуть бота: BotiCord.top", url=f"https://boticord.top/bot/{settings['app_id']}", emoji="<:bc:947181639384051732>"))
                self.add_item(discord.ui.Button(label="Апнуть бота: SDC Monitoring", url=f"https://bots.server-discord.com/{settings['app_id']}", emoji="<:favicon:981586173204000808>"))

        await interaction.response.send_message(embed=embed, view=DropDownView())

async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(HelpCommand(bot))