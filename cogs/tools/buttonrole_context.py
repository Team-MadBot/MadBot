import discord

from discord.ext import commands
from discord import app_commands
from discord import ui


class ButtonRoleEditRoles(ui.RoleSelect):
    def __init__(
        self,
        default_roles: (
            list[discord.abc.Snowflake] | None
        ) = None,  # TODO: use when d.py 2.4 final out
    ):
        super().__init__(placeholder="Выберите роли", max_values=25)

    async def callback(self, interaction: discord.Interaction):
        for i in self.values:
            if i >= interaction.guild.me.top_role:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description=f"Роль {i.mention} выше роли бота, поэтому бот не сможет выдать её кому-либо.",
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )
            if not i.is_assignable():
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description=f"Роль {i.mention} невозможно выдать. Возможно, это роль интеграции.",
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )

        self.view.interaction = interaction
        self.view.selected_roles = self.values
        self.view.stop()


class ButtonRoleEditRolesView(ui.View):
    def __init__(self, default_roles: list[discord.abc.Snowflake] | None = None):
        super().__init__(timeout=300)
        self.select = ButtonRoleEditRoles(default_roles=default_roles)
        self.add_item(self.select)
        self.selected_roles: list[discord.Role] | None = None
        self.interaction: discord.Interaction | None = None

    @ui.button(label="Пропустить", row=1)
    async def skip_button(self, interaction: discord.Interaction, _: ui.Button):
        self.interaction = interaction
        self.stop()


class ButtonRoleEditEmbedModal(ui.Modal, title="Выдача ролей - Изменение эмбеда"):
    embed_title = ui.TextInput(
        label="Заголовок:", max_length=256, placeholder="Получение роли", required=False
    )
    embed_description = ui.TextInput(
        label="Описание:",
        style=discord.TextStyle.long,
        placeholder="Получите прекрасную роль, нажав снизу на компонент!",
        required=False,
    )
    embed_color = ui.TextInput(
        label="Цвет (в #HEX):",
        placeholder="#FFFFFF",
        max_length=7,
        min_length=7,
        required=False,
    )
    select_placeholder = ui.TextInput(
        label="Заполнитель меню выбора:",
        placeholder="Выберите свою роль!",
        max_length=150,
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        self.interaction = interaction


class ButtonRoleEditEmbedView(ui.View):
    def __init__(
        self,
        embed_title: str,
        embed_description: str,
        embed_color: str,
        select_placeholder: str | None = discord.utils.MISSING,
    ):
        super().__init__(timeout=300)
        self.embed_title = embed_title
        self.embed_description = embed_description
        self.embed_color = embed_color
        self.select_placeholder = select_placeholder
        self.interaction: discord.Interaction | None = None

    @ui.button(label="Изменить эмбед", style=discord.ButtonStyle.green)
    async def edit_embed_button(self, interaction: discord.Interaction, _: ui.Button):
        modal = ButtonRoleEditEmbedModal()
        modal.embed_title.default = self.embed_title
        modal.embed_description.default = self.embed_description
        modal.embed_color.default = self.embed_color
        if self.select_placeholder is discord.utils.MISSING:
            modal.select_placeholder = None
        else:
            modal.select_placeholder.default = self.select_placeholder

        await interaction.response.send_modal(modal)
        await modal.wait()
        if modal.interaction is None:
            return

        if modal.embed_color.value is not None:
            try:
                discord.Color.from_str(modal.embed_color.value)
            except ValueError:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Введённое значение цвета некорректно!",
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )

        self.interaction = modal.interaction
        self.embed_title = modal.embed_title.value or self.embed_title
        self.embed_description = modal.embed_description.value or self.embed_description
        self.embed_color = modal.embed_color.value or self.embed_color
        self.stop()

    @ui.button(label="Пропустить", row=1)
    async def skip_button(self, interaction: discord.Interaction, _: ui.Button):
        self.interaction = interaction
        self.stop()


class ConfirmView(ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.value: bool | None = None
        self.interaction: discord.Interaction | None = None

    @ui.button(label="Да", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, _: ui.Button):
        self.value = True
        self.interaction = interaction
        self.stop()

    @ui.button(label="Нет", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, _: ui.Button):
        self.value = False
        self.interaction = interaction
        self.stop()


class ButtonRoleEditedView(ui.View):
    def __init__(
        self, guild_id: int, roles: list[discord.Role], select_placeholder: str | None
    ):
        super().__init__(timeout=None)
        if len(roles) == 1:
            self.add_item(
                ui.Button(
                    style=discord.ButtonStyle.green,
                    custom_id=str(roles[0].id),
                    label=roles[0].name,
                )
            )
        else:
            self.add_item(
                ui.Select(
                    custom_id=str(guild_id),
                    placeholder=select_placeholder or "Выберите роль",
                    max_values=len(roles),
                    options=[
                        discord.SelectOption(
                            label=r.name,
                            value=str(r.id),
                            description="Выберите этот пункт, чтобы взять/убрать роль.",
                        )
                        for r in roles
                    ],
                )
            )


class ButtonRoleContextCog(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.bot.tree.add_command(
            app_commands.ContextMenu(
                name="Изменить выдачу", callback=self.buttonrolecontext
            )
        )

    @app_commands.guild_only()
    async def buttonrolecontext(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        if not interaction.permissions.manage_roles:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Необходимо право на управление ролями для использования данной контекстной команды!",
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if not interaction.app_permissions.manage_roles:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Бот не имеет права на управление ролями, чтобы выдача работала корректно!",
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if message.author.id != self.bot.user.id or len(message.components) != 1:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Данное сообщение нельзя отредактировать!",
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        component = message.components[0].children[0]
        if component.custom_id not in [
            str(interaction.guild.id),
            *[str(r.id) for r in interaction.guild.roles],
        ]:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Данное сообщение нельзя отредактировать!",
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        roles = (
            [discord.Object(i.value) for i in component.options]
            if int(component.custom_id) == interaction.guild.id
            else [discord.Object(component.custom_id)]
        )
        role_edit_view = ButtonRoleEditRolesView(default_roles=roles)
        embed = discord.Embed(
            title="Изменение выдачи - Выбор ролей",
            color=discord.Color.orange(),
            description='Выберите роли, которые должны выдаваться в новой выдаче ролей. Нажмите кнопку "Пропустить", если Вам не нужно их изменять.',
        ).set_footer(text="Этап 1/3")
        await interaction.response.send_message(
            embed=embed, ephemeral=True, view=role_edit_view
        )
        await role_edit_view.wait()

        if role_edit_view.interaction is None:
            return await interaction.delete_original_response()

        selected_roles = sorted(
            role_edit_view.selected_roles
            or [
                interaction.guild.get_role(i.id)
                for i in roles
                if interaction.guild.get_role(i.id)
            ],
            key=lambda x: x.name,
        )

        embed_title = message.embeds[0].title
        embed_description = message.embeds[0].description
        embed_color = str(message.embeds[0].color).upper()
        select_placeholder = (
            discord.utils.MISSING
            if len(roles) < 2 or len(selected_roles) < 2
            else component.placeholder
        )
        embed_edit_view = ButtonRoleEditEmbedView(
            embed_title=embed_title,
            embed_description=embed_description,
            embed_color=embed_color,
            select_placeholder=select_placeholder,
        )
        embed = discord.Embed(
            title="Изменение выдачи - Изменение эмбеда",
            color=discord.Color.orange(),
            description="Теперь Вам предстоит изменить сообщение, которое видят пользователи. Если Вы не заполните какое-то поле - это поле изменено не будет. "
            'Если Вы хотите пропустить этот этап - нажмите кнопку "Пропустить".',
        ).set_footer(text="Этап 2/3")
        await role_edit_view.interaction.response.edit_message(
            embed=embed, view=embed_edit_view
        )
        await embed_edit_view.wait()

        if not embed_edit_view.interaction:
            return await role_edit_view.interaction.delete_original_response()

        buttonrole_embed = discord.Embed(
            title=embed_edit_view.embed_title,
            color=discord.Color.from_str(embed_edit_view.embed_color),
            description=embed_edit_view.embed_description,
        ).set_footer(
            text=f"Изменено: {str(interaction.user)}",
            icon_url=interaction.user.display_avatar.url,
        )
        embed = (
            discord.Embed(
                title="Изменение выдачи - Подтверждение",
                color=discord.Color.orange(),
                description="Финальный штрих! Подтвердите изменённые параметры. Предпросмотр находится выше.",
            )
            .set_footer(text="Этап 3/3")
            .add_field(
                name="Роли для выдачи",
                value=", ".join(i.mention for i in selected_roles),
            )
        )
        confirm_view = ConfirmView()
        await embed_edit_view.interaction.response.edit_message(
            embeds=[buttonrole_embed, embed], view=confirm_view
        )
        await confirm_view.wait()

        if not confirm_view.value:
            return await embed_edit_view.interaction.delete_original_response()

        await message.edit(
            embed=buttonrole_embed,
            view=ButtonRoleEditedView(interaction.guild.id, selected_roles),
        )
        embed = discord.Embed(
            title="Успешно!",
            color=discord.Color.green(),
            description="Вы успешно изменили выдачу ролей!",
        )
        await confirm_view.interaction.response.edit_message(embed=embed, view=None)


async def setup(bot: commands.AutoShardedBot):
    await bot.add_cog(ButtonRoleContextCog(bot))
