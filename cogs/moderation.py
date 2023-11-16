import discord
import datetime
import config

from discord import app_commands, Forbidden, NotFound
from asyncio import sleep
from discord.ext import commands

from config import *
from classes import checks

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ctx_kick = app_commands.ContextMenu(
            name = "Кикнуть участника",
            callback = self.context_kick
        )
        self.ctx_ban = app_commands.ContextMenu(
            name = "Забанить участника",
            callback = self.context_ban
        )
        self.ctx_timeout = app_commands.ContextMenu(
            name = "Выдать тайм-аут",
            callback = self.context_timeout
        )
        self.bot.tree.add_command(self.ctx_kick)
        self.bot.tree.add_command(self.ctx_ban)
        self.bot.tree.add_command(self.ctx_timeout)
    
    @app_commands.command(name="kick", description="[Модерация] Выгнать участника с сервера")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(member='Участник, который будет исключен', reason="Причина кика")
    async def kick(self, interaction: discord.Interaction, member: discord.User, reason: str):
        config.used_commands += 1
        if checks.is_in_blacklist(interaction.user.id):
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        try:
            member = await interaction.guild.fetch_member(member.id)
        except:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Участник должен находиться на сервере для использования команды!")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = "`/kick`"
        if interaction.user.guild_permissions.kick_members:
            member_bot = await interaction.guild.fetch_member(self.bot.user.id)
            if (member.top_role.position >= interaction.user.top_role.position or interaction.guild.owner.id == member.id) and interaction.guild.owner.id != interaction.user.id:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не можете выдавать наказание участникам, чья роль выше либо равна вашей!")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            if member.top_role.position >= member_bot.top_role.position or interaction.guild.owner.id == member.id or member_bot.guild_permissions.kick_members == False:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет права на исключение данного участника!\nТип ошибки: `Forbidden`.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            reason = reason[:460] + (reason[460:] and '..')
            embed = discord.Embed(title=f'Участник выгнан с сервера {interaction.guild.name}!', color=discord.Color.red(), timestamp=discord.utils.utcnow())
            embed.add_field(name="Участник:", value=f"{member.mention}", inline=True)
            embed.add_field(name="Модератор:", value=f"{interaction.user.mention}", inline=True)
            embed.add_field(name="Причина:", value=f"{reason}", inline=True)
            try:
                await member.send(embed=embed)
            except:
                embed.set_footer(text="Личные сообщения участника закрыты, поэтому бот не смог оповестить участника о выдаче наказания!")
            await member.kick(reason=f"{reason} // {interaction.user.name}")
            return await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description='У вас недостаточно прав для использования команды')
            return await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ban", description="[Модерация] Забанить участника на сервере")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(member='Участник, который будет забанен', reason="Причина бана", delete_message_days="За какой период дней удалить сообщения.")
    async def ban(self, interaction: discord.Interaction, member: discord.User, reason: str, delete_message_days: app_commands.Range[int, 0, 7] = 0):
        config.used_commands += 1
        if checks.is_in_blacklist(interaction.user.id):
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        try:
            member = await interaction.guild.fetch_member(member.id)
        except:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Участник должен находиться на сервере для использования команды!")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = "`/ban`"
        if interaction.user.guild_permissions.ban_members:
            member_bot = await interaction.guild.fetch_member(self.bot.user.id)
            if (member.top_role.position >= interaction.user.top_role.position or interaction.guild.owner.id == member.id) and interaction.guild.owner.id != interaction.user.id:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не можете выдавать наказание участникам, чья роль выше либо равна вашей!")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            if member.top_role.position >= member_bot.top_role.position or interaction.guild.owner.id == member.id or member_bot.guild_permissions.ban_members == False:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет права на бан данного участника!\nТип ошибки: `Forbidden`.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            reason = reason[:460] + (reason[460:] and '..')
            embed = discord.Embed(title=f'Участник забанен на сервере {interaction.guild.name}!', color=discord.Color.red(), timestamp=discord.utils.utcnow())
            embed.add_field(name="Участник:", value=f"{member.mention}", inline=True)
            embed.add_field(name="Модератор:", value=f"{interaction.user.mention}", inline=True)
            embed.add_field(name="Причина:", value=f"{reason}", inline=True)
            try:
                await member.send(embed=embed)
            except:
                embed.set_footer(text="Личные сообщения участника закрыты, поэтому бот не смог оповестить участника о выдаче наказания!")
            await member.ban(reason=f"{reason} // {interaction.user.name}", delete_message_days=delete_message_days)
            return await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description='У вас недостаточно прав для использования команды')
            return await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    async def context_kick(self, interaction: discord.Interaction, message: discord.Message):
        config.used_commands += 1
        if checks.is_in_blacklist(interaction.user.id):
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = "`/kick`"
        if interaction.user.guild_permissions.kick_members:
            if isinstance(message.author, discord.User):
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Пользователь должен находиться на сервере, чтобы использовать команду!"
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            member_bot = interaction.guild.get_member(self.bot.user.id)
            if (message.author.top_role.position >= interaction.user.top_role.position or interaction.guild.owner.id == message.author.id) and interaction.guild.owner.id != interaction.user.id:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не можете выдавать наказание участникам, чья роль выше либо равна вашей!")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            if message.author.top_role.position >= member_bot.top_role.position or interaction.guild.owner.id == message.author.id or member_bot.guild_permissions.kick_members == False:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет права на исключение данного участника!\nТип ошибки: `Forbidden`.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)

            class ReasonInput(discord.ui.Modal, title="Выдача наказания"):
                answer = discord.ui.TextInput(label="Укажите причину выдачи наказания", style=discord.TextStyle.paragraph, placeholder="Бунтует", required=True, max_length=450)
                async def on_submit(self, viewinteract: discord.Interaction):
                    reason = self.answer
                    proofs = message.content
                    if message.embeds != None:
                        for emb in message.embeds:
                            if bool(emb):
                                proofs += "embed:\n"
                                proofs += f"title={emb.title}\n" if emb.title != None else ''
                                proofs += f"description={emb.description[:896] + (emb.description[896:] and '..')}" if emb.description != None else ''
                    if message.attachments != None:
                        for attach in message.attachments:
                            proofs += f'\n{attach.url}'
                    embed = discord.Embed(title=f'Участник выгнан с сервера {interaction.guild.name}!', color=discord.Color.red(), timestamp=discord.utils.utcnow())
                    embed.add_field(name="Участник:", value=f"{message.author.mention}", inline=True)
                    embed.add_field(name="Модератор:", value=f"{interaction.user.mention}", inline=True)
                    embed.add_field(name="Причина:", value=f"{reason}", inline=True)
                    embed.add_field(name="Доказательства:", value=f"||{message.content}||")
                    try:
                        await message.author.send(embed=embed)
                    except:
                        embed.set_footer(text="Личные сообщения участника закрыты, поэтому бот не смог оповестить участника о выдаче наказания!")
                    await message.author.kick(reason=f"{reason} // {interaction.user.name}")
                    return await viewinteract.response.send_message(embed=embed)

            await interaction.response.send_modal(ReasonInput())
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У вас отсутствует право `исключение участников` для использования команды!")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    async def context_ban(self, interaction: discord.Interaction, message: discord.Message):
        config.used_commands += 1
        if checks.is_in_blacklist(interaction.user.id):
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = "`/ban`"
        if interaction.user.guild_permissions.ban_members:
            if isinstance(message.author, discord.User):
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Пользователь должен находиться на сервере, чтобы использовать команду!"
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            member_bot = interaction.guild.get_member(self.bot.user.id)
            if (message.author.top_role.position >= interaction.user.top_role.position or interaction.guild.owner.id == message.author.id) and interaction.guild.owner.id != interaction.user.id:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не можете выдавать наказание участникам, чья роль выше либо равна вашей!")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            if message.author.top_role.position >= member_bot.top_role.position or interaction.guild.owner.id == message.author.id or member_bot.guild_permissions.ban_members == False:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет права на бан данного участника!\nТип ошибки: `Forbidden`.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)



            class InputText(discord.ui.Modal, title="Выдача наказания"):
                reason = discord.ui.TextInput(label="Укажите причину", style=discord.TextStyle.paragraph, placeholder="Бунтует", required=True, max_length=430)
                delete_message_days = discord.ui.TextInput(label="Удалить историю сообщений", style=discord.TextStyle.short, placeholder="0-7", max_length=1, required=False)
                async def on_submit(self, viewinteract: discord.Interaction):
                    delete_message_days = (
                        0
                        if str(self.delete_message_days) is None
                        or not (str(self.delete_message_days).isdigit())
                        else int(str(self.delete_message_days))
                    )
                    if str(self.delete_message_days) != None and str(self.delete_message_days).isdigit() and int(str(self.delete_message_days)) > 7:
                        delete_message_days = 7
                    proofs = message.content
                    if message.embeds != None:
                        for emb in message.embeds:
                            if bool(emb):
                                proofs += "embed:\n"
                                proofs += f"title={emb.title}\n" if emb.title != None else ''
                                proofs += f"description={emb.description[:896] + (emb.description[896:] and '..')}" if emb.description != None else ''
                    if message.attachments != None:
                        for attach in message.attachments:
                            proofs += f'\n{attach.url}'
                    embed = discord.Embed(title=f'Участник забанен на сервере {interaction.guild.name}!', color=discord.Color.red(), timestamp=discord.utils.utcnow())
                    embed.add_field(name="Участник:", value=f"{message.author.mention}", inline=True)
                    embed.add_field(name="Модератор:", value=f"{interaction.user.mention}", inline=True)
                    embed.add_field(name="Причина:", value=f"{self.reason}", inline=True)
                    embed.add_field(name="Доказательства:", value=f"||{proofs}||")
                    try:
                        await message.author.send(embed=embed)
                    except:
                        embed.set_footer(text="Личные сообщения участника закрыты, поэтому бот не смог оповестить участника о выдаче наказания!")
                    await message.author.ban(delete_message_days=delete_message_days, reason=f"{self.reason} // {interaction.user.name}")
                    return await viewinteract.response.send_message(embed=embed)


            await interaction.response.send_modal(InputText())
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У вас отсутствует право `банить участников` для использования команды!")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="banoff", description="[Модерация] Банит участника, используя его ID")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(member="ID участника, который должен быть забанен", delete_message_days="За какой период удалять сообщения", reason="Причина бана")
    async def banoff(self, interaction: discord.Interaction, member: app_commands.Range[str, 18, 19], reason: str, delete_message_days: app_commands.Range[int, 0, 7] = 0):
        config.used_commands += 1
        if checks.is_in_blacklist(interaction.user.id):
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/banoff`'
        if interaction.user.guild_permissions.ban_members:
            if member.isdigit():
                if interaction.guild.fetch_member(int(member)) is None:
                    embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Нельзя использовать `/banoff`, если участник находится на сервере! Используйте `/ban`!")
                    return await interaction.response.send_message(embed=embed, ephemeral=True)
                member = discord.Object(int(member))
            else:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Указанное значение не является чьим-то ID.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            reason = reason[:460] + (reason[460:] and '..')
            try:
                await interaction.guild.ban(member, delete_message_days=delete_message_days, reason=f"{reason} // {interaction.user.name}#{interaction.user.discriminator}")
            except Forbidden:
                embed = discord.Embed(title='Ошибка!', color=discord.Color.red(), description=f"Не удалось забанить участника. Проверьте наличия права `банить участников` у бота.\nТип ошибки: `Forbidden`")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            except NotFound:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Участник не был обнаружен! Удостоверьтесь в правильности ID!\nТип ошибки: `NotFound`")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(title='Участник забанен на сервере!', color=discord.Color.red(), timestamp=discord.utils.utcnow())
                embed.add_field(name="Участник:", value=f"<@!{member.id}>", inline=True)
                embed.add_field(name="Модератор:", value=f"{interaction.user.mention}", inline=True)
                embed.add_field(name="Причина:", value=f"{reason}", inline=True)
                return await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description='У вас недостаточно прав для использования команды')
            return await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="unban", description="[Модерация] Разбанить участника на сервере")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(member="ID участника, который должен быть разбанен", reason="Причина разбана")
    async def unban(self, interaction: discord.Interaction, member: app_commands.Range[str, 18, 19], reason: str):
        config.used_commands += 1
        if checks.is_in_blacklist(interaction.user.id):
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = '`/unban`'
        if interaction.user.guild_permissions.ban_members:
            if member.isdigit():
                member = discord.Object(id=int(member))
            else:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Указанное значение не является чьим-то ID.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            reason = reason[:460] + (reason[460:] and '..')
            try:
                await interaction.guild.unban(member, reason=f"{reason} // {interaction.user.name}#{interaction.user.discriminator}")
            except Forbidden:
                embed = discord.Embed(title='Ошибка!', color=discord.Color.red(), description=f"Не удалось разбанить участника. Проверьте наличия права `банить участников` у бота.\nТип ошибки: `Forbidden`")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            except NotFound:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Данный участник не обнаружен в списке забаненных!\nТип ошибки: `NotFound`")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(title="Участник разбанен!", color=discord.Color.red(), timestamp=discord.utils.utcnow())
                embed.add_field(name="Участник:", value=f"<@!{member.id}>")
                embed.add_field(name="Модератор:", value=interaction.user.mention)
                embed.add_field(name="Причина:", value=reason)
                return await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У вас недостаточно прав для использования команды")
            return await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clear", description="[Модерация] Очистка сообщений")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(radius='Радиус, в котором будут очищаться сообщения.', member="Участник, чьи сообщения будут очищены.")
    async def clear(self, interaction: discord.Interaction, radius: app_commands.Range[int, 1, 1000], member: discord.User = None):
        config.used_commands += 1
        if checks.is_in_blacklist(interaction.user.id):
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = "`/clear`"
        if interaction.channel.permissions_for(interaction.user).manage_messages:
            deleted = None
            def check(m):
                return True
            if member != None:
                def check(m):
                    return m.author.id == member.id
            trying = discord.Embed(title="В процессе...", color=discord.Color.gold(), description="Сообщения очищаются, ожидайте...", timestamp=discord.utils.utcnow())
            trying.set_footer(text=f"{interaction.user.name}#{interaction.user.discriminator}")
            await interaction.response.send_message(embed=trying, ephemeral=True) 
            try:
                deleted = await interaction.channel.purge(limit=radius, check=check)
            except Forbidden:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f'Не удалось очистить `{radius} сообщений`. Возможно, я не имею право на управление сообщениями.\nТип ошибки: `Forbidden`', timestamp=discord.utils.utcnow())
                return await interaction.edit_original_response(embeds=[embed])
            else:
                from_member = '.'
                if member != None:
                    from_member = f" от участника {member.mention}."
                embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description=f"Мною очищено `{len(deleted)}` сообщений в этом канале{from_member}", timestamp=discord.utils.utcnow())
                return await interaction.edit_original_response(embeds=[embed])
        else:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не имеете права `управление сообщениями` на использование команды!")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="slowmode", description="[Модерация] Установить медленный режим в данном канале. Введите 0 для отключения.")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(seconds="Кол-во секунд. Укажите 0 для снятия.", reason='Причина установки медленного режима')
    async def slowmode(self, interaction: discord.Interaction, seconds: app_commands.Range[int, 0, 21600], reason: str = "Отсутствует"):
        config.used_commands += 1
        if checks.is_in_blacklist(interaction.user.id):
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = "`/slowmode`"
        delay = seconds
        if interaction.channel.permissions_for(interaction.user).manage_channels:
            reason = reason[:460] + (reason[460:] and '..')
            try:
                await interaction.channel.edit(reason=f"{reason} // {interaction.user.name}#{interaction.user.discriminator}", slowmode_delay=delay)
            except:
                embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"У бота отсутствует право на управление данным каналом!\nТип ошибки: `Forbidden`")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = None
                if seconds>0:
                    embed=discord.Embed(title="Успешно!", color=discord.Color.green(), description=f"Медленный режим успешно установлен на `{seconds}` секунд.", timestamp=discord.utils.utcnow())
                else:
                    embed=discord.Embed(title="Успешно!", color=discord.Color.green(), description="Медленный режим успешно снят.", timestamp=discord.utils.utcnow())
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не имеете права `управление каналом` для использования этой команды!")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="timeout", description="[Модерация] Отправляет участника подумать о своем поведении")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(member="Участник, которому нужно выдать тайм-аут", minutes="Кол-во минут, на которые будет выдан тайм-аут.", reason="Причина выдачи наказания.")
    async def timeout(self, interaction: discord.Interaction, member: discord.User, minutes: app_commands.Range[int, 0, 40320], reason: str):
        config.used_commands += 1
        if checks.is_in_blacklist(interaction.user.id):
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.guild.get_member(member.id) is None:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Участник должен находиться на сервере для использования команды!")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = "`/timeout`"
        if interaction.user.guild_permissions.moderate_members:
            if (member.top_role.position >= interaction.user.top_role.position or interaction.guild.owner.id == member.id) and interaction.guild.owner.id != interaction.user.id:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не можете выдавать наказание участникам, чья роль выше либо равна вашей!")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            until = discord.utils.utcnow() + datetime.timedelta(minutes=minutes)
            reason = reason[:460] + (reason[460:] and '..')
            if minutes == 0:
                until = None
            try:
                await member.edit(timed_out_until=until, reason=f"{reason} // {interaction.user.name}#{interaction.user.discriminator}")
            except:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось выдать участнику тайм-аут. Убедитесь в наличии прав на управление участниками у бота и попробуйте снова!\nТип ошибки: `Forbidden`")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                if minutes > 0:    
                    embed = discord.Embed(title=f'Участник отправлен в тайм-аут на сервере {interaction.guild.name}!', color=discord.Color.red(), timestamp=discord.utils.utcnow())
                    embed.add_field(name="Участник:", value=f"{member.mention}",)
                    embed.add_field(name="Модератор:", value=f"{interaction.user.mention}")
                    embed.add_field(name="Срок:", value=f"{minutes} минут")
                    embed.add_field(name="Причина:", value=reason)
                    try:
                        await member.send(embed=embed)
                    except:
                        embed.set_footer(text="Личные сообщения участника закрыты, поэтому бот не смог оповестить участника о выдаче наказания!")
                    return await interaction.response.send_message(embed=embed)
                if minutes == 0:
                    embed = discord.Embed(title=f'С участника снят тайм-аут на сервере {interaction.guild.name}!', color=discord.Color.red(), timestamp=discord.utils.utcnow())
                    embed.add_field(name="Участник:", value=f"{member.mention}")
                    embed.add_field(name="Модератор:", value=f"{interaction.user.mention}")
                    embed.add_field(name="Причина:", value=reason)
                    try:
                        await member.send(embed=embed)
                    except:
                        embed.set_footer(text="Личные сообщения участника закрыты, поэтому бот не смог оповестить участника о выдаче наказания!")
                    return await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У вас отсутствует право `управление участниками` для использования команды!")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    async def context_timeout(self, interaction: discord.Interaction, message: discord.Message):
        config.used_commands += 1
        if checks.is_in_blacklist(interaction.user.id):
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = "`/timeout`"
        if interaction.user.guild_permissions.moderate_members:
            if isinstance(message.author, discord.User):
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Участник должен находиться на сервере для выдачи наказания!"
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            if (message.author.top_role.position >= interaction.user.top_role.position or interaction.guild.owner.id == message.author.id) and interaction.guild.owner.id != interaction.user.id:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не можете выдавать наказание участникам, чья роль выше либо равна вашей!")
                return await interaction.response.send_message(embed=embed, ephemeral=True)



            class InputText(discord.ui.Modal, title="Выдача наказания"):
                until = discord.ui.TextInput(label="Срок выдачи наказания (в минутах)", style=discord.TextStyle.short, required=True, placeholder="0 - 40320", max_length=5)
                reason = discord.ui.TextInput(label="Причина", style=discord.TextStyle.paragraph, placeholder="Бунтует", required=True, max_length=430)
                async def on_submit(self, viewinteract: discord.Interaction):
                    if not(str(self.until).isdigit()):
                        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Причина должна быть численная!")
                        return await viewinteract.response.send_message(embed=embed, ephemeral=True)
                    if int(str(self.until)) > 40320:
                        self.until = 40320
                    if int(str(self.until)) == 0:
                        self.until = None
                    self.minutes = discord.utils.utcnow() + datetime.timedelta(minutes=int(str(self.until)))
                    try:
                        await message.author.edit(timed_out_until=self.minutes, reason=f"{self.reason} // {interaction.user.name}#{interaction.user.discriminator}")
                    except:
                        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Не удалось выдать участнику тайм-аут. Убедитесь в наличии прав на управление участниками у бота и попробуйте снова!\nТип ошибки: `Forbidden`")
                        return await viewinteract.response.send_message(embed=embed, ephemeral=True)
                    else:
                        if self.until is not None:
                            proofs = message.content
                            if message.embeds != None:
                                for emb in message.embeds:
                                    if bool(emb):
                                        proofs += "embed:\n"
                                        proofs += f"title={emb.title}\n" if emb.title != None else ''
                                        proofs += f"description={emb.description[:896] + (emb.description[896:] and '..')}" if emb.description != None else ''
                            if message.attachments != None:
                                for attach in message.attachments:
                                    proofs += f'\n{attach.url}'
                            embed = discord.Embed(title=f'Участник отправлен в тайм-аут на сервере {interaction.guild.name}!', color=discord.Color.red(), timestamp=discord.utils.utcnow())
                            embed.add_field(name="Участник:", value=f"{message.author.mention}")
                            embed.add_field(name="Модератор:", value=f"{interaction.user.mention}")
                            embed.add_field(name="Срок:", value=f"{self.until} минут")
                            embed.add_field(name="Причина:", value=self.reason)
                            embed.add_field(name="Доказательства:", value=f"||{proofs}||")
                            try:
                                await message.author.send(embed=embed)
                            except:
                                embed.set_footer(text="Личные сообщения участника закрыты, поэтому бот не смог оповестить участника о выдаче наказания!")
                            return await viewinteract.response.send_message(embed=embed)
                        embed = discord.Embed(title=f'С участника снят тайм-аут на сервере {interaction.guild.name}!', color=discord.Color.red(), timestamp=discord.utils.utcnow())
                        embed.add_field(name="Участник:", value=f"{message.author.mention}")
                        embed.add_field(name="Модератор:", value=f"{interaction.user.mention}")
                        embed.add_field(name="Причина:", value=self.reason)
                        try:
                            await message.author.send(embed=embed)
                        except:
                            embed.set_footer(text="Личные сообщения участника закрыты, поэтому бот не смог оповестить участника о выдаче наказания!")
                        return await viewinteract.response.send_message(embed=embed)


            await interaction.response.send_modal(InputText())
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У вас отсутствует право `управление участниками` для использования команды!")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name='clone', description="[Модерация] Клонирует чат.")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(delete_original="Удалять ли клонируемый канал?", reason="Причина клонирования")
    async def clone(self, interaction: discord.Interaction, reason: str, delete_original: bool = False):
        config.used_commands += 1
        if checks.is_in_blacklist(interaction.user.id):
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.Thread):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Данная команда недоступна в ветках!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = "`/clone`"
        if interaction.user.guild_permissions.manage_channels:
            cloned = None
            reason = reason[:460] + (reason[460:] and '..')
            try:
                cloned = await interaction.channel.clone(reason=f"{reason} // {interaction.user.name}#{interaction.user.discriminator}")
            except Forbidden:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Бот не имеет право `управление каналами` для совершения действия!\nТип ошибки: `Forbidden`")
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await cloned.move(after=discord.Object(id=interaction.channel.id), reason=f"Клонирование // {interaction.user.name}#{interaction.user.discriminator}")
                embed = discord.Embed(title="Успешно!", color=discord.Color.green(), description="Канал успешно клонирован!")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                if delete_original:
                    await sleep(10)
                    await interaction.channel.delete(reason=f"Использование команды // {interaction.user.name}#{interaction.user.discriminator}")
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У вас отсутствует право `управление каналами` для использования команды.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="resetnick", description="[Модерация] Просит участника поменять ник")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(member="Участник, которого надо попросить сменить ник", reason="Причина сброса ника")
    async def resetnick(self, interaction: discord.Interaction, member: discord.User, reason: str):
        config.used_commands += 1
        if checks.is_in_blacklist(interaction.user.id):
            embed=discord.Embed(title="Вы занесены в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс вас в чёрный список бота! Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.guild.get_member(member.id) is None:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Участник должен находиться на сервере для использования команды!")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        config.lastcommand = "`/resetnick`"
        if interaction.user.guild_permissions.manage_nicknames:
            reason = reason[:460] + (reason[460:] and '..')
            if member.top_role.position >= interaction.user.top_role.position and interaction.guild.owner.id != interaction.user.id:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Вы не можете управлять никнеймами участников, чья роль выше либо равна вашей!")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            if member.bot:
                embed = discord.Embed(title="Не понял", color=discord.Color.red(), description="Нельзя сбросить ник боту.")
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            try:
                await member.edit(nick="Смените ник", reason=f"{reason} // {interaction.user.name}#{interaction.user.discriminator}")
            except Forbidden:
                embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"У бота отсутствует право `управлять никнеймами` для совершения действия!\nТип ошибки: `Forbidden`")
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(title=f"Никнейм сброшен на сервере {interaction.guild.name}!", color=discord.Color.red())
                embed.add_field(name="Участник:", value=member.mention)
                embed.add_field(name="Модератор:", value=interaction.user.mention)
                embed.add_field(name="Причина:", value=reason)
                try:
                    await member.send(embed=embed)
                except:
                    embed.set_footer(text="Участник закрыл доступ к личным сообщениям, поэтому не был оповещён.")
                await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="У вас отсутствует право `управлять никнеймами` для использования команды.")
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
    print('Cog "Moderation" запущен!')
