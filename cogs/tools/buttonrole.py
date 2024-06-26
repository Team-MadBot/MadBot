import discord

from discord import app_commands
from discord.ext import commands

from . import hard_cooldown

from classes import checks


class ButtonRole(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(
        name="buttonrole",
        description="[Полезности] Настроить выдачу ролей по нажатию кнопки.",
    )
    @app_commands.checks.dynamic_cooldown(hard_cooldown)
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def buttonrole(self, interaction: discord.Interaction):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!",
            ).set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if not interaction.user.guild_permissions.manage_roles:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="У вас отсутствует право `управлять ролями` для использования команды!",
            )
            return interaction.response.send_message(embed=embed, ephemeral=True)

        bot_member = interaction.guild.get_member(self.bot.user.id)
        if not (bot_member.guild_permissions.manage_roles):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Бот не имеет права `управлять ролями`, что необходимо для работы команды!",
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        roles = []

        class SelectButton(discord.ui.RoleSelect):
            def __init__(self):
                super().__init__(
                    placeholder="Выберите роли для выдачи", min_values=1, max_values=25
                )

            async def callback(self, viewinteract: discord.Interaction):
                if not viewinteract.user.id == interaction.user.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя менюшка!", ephemeral=True
                    )

                for role in self.values:
                    if bot_member.top_role <= role:
                        embed = discord.Embed(
                            title="Ошибка!",
                            color=discord.Color.red(),
                            description=f"Роль {role.mention} выше роли бота, поэтому бот не сможет выдать её кому-либо.",
                        )
                        return await viewinteract.response.send_message(
                            embed=embed, ephemeral=True
                        )
                    if not role.is_assignable():
                        embed = discord.Embed(
                            title="Ошибка!",
                            color=discord.Color.red(),
                            description=f"Роль {role.mention} является ролью интеграции, поэтому выдать её кому-либо нельзя!",
                        )
                        return await viewinteract.response.send_message(
                            embed=embed, ephemeral=True
                        )

                self.view.roles = self.values
                self.view.interaction = viewinteract
                self.view.stop()

        class SelectButtonView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=180)
                self.add_item(SelectButton())
                self.roles: list[discord.Role] = []
                self.interaction = None

        embed = discord.Embed(
            title="Выдача ролей - Выбор",
            color=discord.Color.orange(),
            description="Пожалуйста, выберите до 25 ролей, которые бот будет выдавать пользователям",
        )
        view = SelectButtonView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        await view.wait()

        if view.roles == []:
            embed = discord.Embed(title="Время вышло!", color=discord.Color.red())
            return await interaction.edit_original_response(embed=embed, view=None)

        assert isinstance(view.interaction, discord.Interaction)
        assert isinstance(view.roles, list)

        selectinteract = view.interaction
        roles = sorted(view.roles, key=lambda x: x.name)

        title = ""
        description = ""
        color = discord.Color.orange()
        select_placeholder = None

        class Input(discord.ui.Modal, title="Кастомизация эмбеда"):
            main = discord.ui.TextInput(
                label="Заголовок эмбеда:",
                max_length=256,
                default="Выдача роли",
                placeholder="Получение роли",
                required=False,
            )
            description = discord.ui.TextInput(
                label="Описание:",
                max_length=4000,
                style=discord.TextStyle.long,
                default=f"Нажмите на {'кнопку' if len(roles) <= 1 else 'меню'} ниже, чтобы выбрать себе роль.",
                placeholder="Получите прекрасную роль, нажав снизу на компонент!",
                required=False,
            )
            color = discord.ui.TextInput(
                label="Цвет (по умолчанию - оранжевый):",
                min_length=7,
                max_length=7,
                required=False,
                placeholder="#FFFFFF",
            )
            select_placeholder = (
                discord.ui.TextInput(
                    label="Заполнитель меню выбора:",
                    max_length=150,
                    required=False,
                    placeholder="Выберите свою роль!",
                )
                if len(roles) > 1
                else None
            )

            async def on_submit(self, viewinteract: discord.Interaction) -> None:
                nonlocal title, description, color, select_placeholder

                await viewinteract.response.defer()

                title = str(self.main)
                description = str(self.description)

                if str(self.color) != "":
                    color = str(self.color)
                if (
                    self.select_placeholder is not None
                    and str(self.select_placeholder) != ""
                ):
                    select_placeholder = str(self.select_placeholder)

        class KostylView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=180)
                self.modal: discord.ui.Modal | None = None

            @discord.ui.button(label="Заполнить эмбед", style=discord.ButtonStyle.green)
            async def fill_embed(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                self.modal = Input()
                await viewinteract.response.send_modal(self.modal)
                await self.modal.wait()

                if self.modal.main is None or self.modal.description is None:
                    return

                self.stop()

        embed = discord.Embed(
            title="Выдача ролей - Заполнение эмбеда",
            color=discord.Color.orange(),
            description=f"Вы выбрали {'роли' if len(roles) > 1 else 'роль'}: {', '.join([i.mention for i in roles])}.\n\n"
            "Теперь нужно заполнить эмбед, который будут видеть пользователи перед выбором роли. Нажмите кнопку ниже, чтобы начать заполнение.",
        )
        kostyl_view = KostylView()
        await selectinteract.response.edit_message(embed=embed, view=kostyl_view)
        await kostyl_view.wait()
        modal = kostyl_view.modal

        if modal is None or modal.title is None:
            embed = discord.Embed(title="Время вышло!", color=discord.Color.red())
            return await interaction.edit_original_response(view=None, embed=embed)

        if isinstance(color, str):
            try:
                color = discord.Color.from_str(color)
            except ValueError:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Цвет введён неверно!",
                )
                return await interaction.followup.send(embed=embed, ephemeral=True)

        class View(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)

        view = View()
        options = []
        for role in roles:
            options.append(
                discord.SelectOption(
                    label=f"{role.name}",
                    value=str(role.id),
                    description="Выберите это пункт, чтобы взять/убрать роль.",
                )
            )
        if len(options) == 1:
            view.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.green,
                    label=roles[0].name,
                    custom_id=str(roles[0].id),
                )
            )
        else:
            view.add_item(
                discord.ui.Select(
                    custom_id=str(interaction.guild.id),
                    placeholder=select_placeholder or "Выберите роли",
                    max_values=len(options),
                    options=options,
                )
            )

        user_embed = discord.Embed(
            title=title, color=color, description=description
        ).set_footer(
            text=f"Создал: {interaction.user}",
            icon_url=interaction.user.display_avatar.url,
        )

        class AcceptRules(discord.ui.View):
            def __init__(self, bot: commands.Bot):
                super().__init__(timeout=60)
                self.value = None
                self.bot = bot

            @discord.ui.button(style=discord.ButtonStyle.green, emoji="✅")
            async def accept(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                nonlocal view
                self.value = True
                try:
                    await viewinteract.channel.send(embed=user_embed, view=view)
                except discord.Forbidden:
                    embed = discord.Embed(
                        title="Ошибка!",
                        color=discord.Color.red(),
                        description="Бот не имеет права на отправку сообщения в этом канале!",
                    )
                    return await viewinteract.response.edit_message(
                        embed=embed, view=None
                    )

                embed = discord.Embed(
                    title="Успешно!",
                    color=discord.Color.green(),
                    description="Выдача ролей успешно настроена!",
                )
                await viewinteract.response.edit_message(embed=embed, view=None)

            @discord.ui.button(
                style=discord.ButtonStyle.red, emoji="<:x_icon:975324570741526568>"
            )
            async def deny(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                self.value = False
                embed = discord.Embed(
                    title="Отмена!",
                    color=discord.Color.red(),
                    description="Выдача ролей по реакциям отменена!",
                )
                await viewinteract.response.edit_message(embed=embed, view=None)

        embed = discord.Embed(
            title="Обязательно к прочтению!",
            color=discord.Color.orange(),
            description=f"Мы, простые разработчики бота, просим не использовать в кастомизированном эмбеде что-либо, "
            "нарушающее правила Discord. В противном случае, Ваш сервер и Ваш аккаунт будут занесены в черный список бота.\n"
            "**Вы согласны с требованиями?**\n\n"
            "Кстати, выше Вы видите эмбед, который получается у Вас на данный момент. Он так и будет отправлен в канал без изменений "
            "(добавится только меню выбора ролей). "
            "Если он Вас не устраивает, Вы можете нажать на крест для отмены (либо просто убрать это сообщение).",
        )
        waiting = AcceptRules(bot=self.bot)
        msg_bot = await interaction.followup.send(
            embeds=[user_embed, embed], ephemeral=True, view=waiting
        )
        await waiting.wait()
        if waiting.value is None:
            embed = discord.Embed(title="Время истекло!", color=discord.Color.red())
            await msg_bot.edit(embed=embed, view=None)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(ButtonRole(bot))
