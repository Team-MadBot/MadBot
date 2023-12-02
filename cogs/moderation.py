import discord
import datetime
import config
import logging

from discord import app_commands, Forbidden, NotFound
from asyncio import sleep
from discord.ext import commands
from discord import utils as dutils

from config import *
from classes import checks

logger = logging.getLogger('discord')

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="kick", description="[Модерация] Выгнать участника с сервера")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(member='Участник, который будет исключен', reason="Причина кика")
    async def kick(
        self, 
        interaction: discord.Interaction, 
        member: discord.User, 
        reason: app_commands.Range[str, None, 512]
    ):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        try:
            member = await interaction.guild.fetch_member(member.id)
        except:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(), 
                description="Участник должен находиться на сервере для использования команды!"
            ).set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        member_bot = interaction.guild.me # пашет без интентов, так что живём.
        
        if not interaction.user.guild_permissions.kick_members:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="У вас нет прав на исключение участников!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if (member.top_role.position >= member_bot.top_role.position or 
                interaction.guild.owner_id == member.id or
                not member_bot.guild_permissions.kick_members):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Бот не может исключить данного пользователя!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if ((member.top_role.position >= interaction.user.top_role.position 
                or interaction.guild.owner_id == member.id)
                and interaction.user.id != interaction.guild.owner_id):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Вы не можете исключать участников, чья роль выше либо равна Вашей!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        await interaction.response.defer(thinking=True)

        embed = discord.Embed(
            title=f"Участник исключён с сервера {interaction.guild}!",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now()
        ).add_field(
            name="Участник",
            value=f"{member.mention}\n({member.id})"
        ).add_field(
            name="Модератор",
            value=f"{interaction.user.mention}\n({interaction.user.id})"
        ).add_field(
            name="Причина",
            value=dutils.escape_markdown(reason)
        )

        try:
            message = await member.send(embed=embed)
        except:
            embed.set_footer(text="Участник не получил сообщение о исключении!")
        
        try:
            await interaction.guild.kick(
                member, 
                reason=f"{reason} // {interaction.user}"
            )
        except:
            await message.delete()
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Бот не смог исключить данного пользователя! Убедитесь, что у бота есть все необходимые права!"
            )
            return await interaction.followup.send(embed=embed)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="ban", description="[Модерация] Забанить участника на сервере")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(member='Участник, который будет забанен', reason="Причина бана", delete_message_days="За какой период дней удалить сообщения.")
    async def ban(
        self, 
        interaction: discord.Interaction, 
        member: discord.User, 
        reason: app_commands.Range[str, None, 512], 
        delete_message_days: app_commands.Range[int, 0, 7] = 0
    ):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        member_bot = interaction.guild.me # пашет без интентов, так что живём.
        
        if not interaction.user.guild_permissions.ban_members:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="У вас нет прав на блокировку участников!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if (member.top_role.position >= member_bot.top_role.position or 
                interaction.guild.owner_id == member.id or
                not member_bot.guild_permissions.ban_members):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Бот не может забанить данного пользователя!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if ((member.top_role.position >= interaction.user.top_role.position 
                or interaction.guild.owner_id == member.id)
                and interaction.user.id != interaction.guild.owner_id):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Вы не можете банить участников, чья роль выше либо равна Вашей!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        await interaction.response.defer(thinking=True)

        embed = discord.Embed(
            title=f"Участник заблокирован на сервере {interaction.guild}!",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now()
        ).add_field(
            name="Участник",
            value=f"{member.mention}\n({member.id})"
        ).add_field(
            name="Модератор",
            value=f"{interaction.user.mention}\n({interaction.user.id})"
        ).add_field(
            name="Причина",
            value=dutils.escape_markdown(reason)
        )

        try:
            message = await member.send(embed=embed)
        except:
            embed.set_footer(text="Участник не получил сообщение о блокировке!")
        
        try:
            await interaction.guild.ban(
                member, 
                reason=f"{reason} // {interaction.user}",
                delete_message_days=delete_message_days
            )
        except:
            await message.delete()
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Бот не смог забанить данного пользователя! Убедитесь, что у бота есть все необходимые права!"
            )
            return await interaction.followup.send(embed=embed)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="unban", description="[Модерация] Разбанить участника на сервере")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(member="Участник, который должен быть разбанен", reason="Причина разбана")
    async def unban(
        self, 
        interaction: discord.Interaction, 
        member: app_commands.Range[str, 18, 19], 
        reason: app_commands.Range[str, None, 512]
    ):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if not interaction.user.guild_permissions.ban_members:
            embed = discord.Embed(
                title='Ошибка!',
                color=discord.Color.red(),
                description="У вас нет прав на разблокировку участников!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        try:
            await interaction.guild.unban(
                member, 
                reason=f"{reason} // {interaction.user}"
            )
        except Forbidden:
            embed = discord.Embed(
                title='Ошибка!', 
                color=discord.Color.red(), 
                description=f"Не удалось разбанить участника. Проверьте наличия права `банить участников` у бота.\n"
                "Тип ошибки: `Forbidden`"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        except NotFound:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(), 
                description=f"Данный участник не обнаружен в списке забаненных!\n"
                "Тип ошибки: `NotFound`"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception:
            embed = discord.Embed(
                title="Неизвестная ошибка!",
                color=discord.Color.red(),
                description="По какой-то неизвестной причине, разбан участника не был завершён. "
                "Убедитесь в наличии прав у бота и корректности указанного участника и повторите попытку"
            )
        else:
            embed = discord.Embed(
                title="Участник разбанен!", 
                color=discord.Color.red(), 
                timestamp=datetime.datetime.now()
            ).add_field(
                name="Участник:", 
                value=f"{member.mention}\n({member.id})"
            ).add_field(
                name="Модератор:", 
                value=f"{interaction.user.mention}\n({interaction.user.id})"
            ).add_field(
                name="Причина:", 
                value=dutils.escape_markdown(reason)
            )
            return await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clear", description="[Модерация] Очистка сообщений")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(
        radius='Радиус, в котором будут очищаться сообщения.', 
        member="Участник, чьи сообщения будут очищены."
    )
    async def clear(
        self, 
        interaction: discord.Interaction, 
        radius: app_commands.Range[int, 1, 1000], 
        member: discord.User = None
    ):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if not interaction.channel.permissions_for(interaction.user).manage_messages:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(), 
                description="Вы не имеете права `управление сообщениями` на использование команды!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await interaction.response.defer(thinking=True, ephemeral=True)
        try:
            deleted = await interaction.channel.purge(
                limit=radius, 
                check=lambda m: m.author == member or member is None
            )
        except Forbidden:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(), 
                description=f"Не удалось очистить `{radius} сообщений`. Возможно, я не имею право на управление сообщениями.\n"
                "Тип ошибки: `Forbidden`", 
                timestamp=datetime.datetime.now()
            )
            return await interaction.followup.send(embed=embed)
        else:
            from_member = '.' if member is None else f" от участника {member.mention}."
            embed = discord.Embed(
                title="Успешно!", 
                color=discord.Color.green(), 
                description=f"Мною очищено `{len(deleted)}` сообщений в этом канале{from_member}", 
                timestamp=datetime.datetime.now()
            )
            return await interaction.followup.send(embed=embed)

    @app_commands.command(name="slowmode", description="[Модерация] Установить медленный режим в данном канале. Введите 0 для отключения.")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(seconds="Кол-во секунд. Укажите 0 для снятия.", reason='Причина установки медленного режима')
    async def slowmode(
        self, 
        interaction: discord.Interaction, 
        seconds: app_commands.Range[int, 0, 21600], 
        reason: app_commands.Range[str, None, 512] = "Отсутствует"
    ):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(), 
                description="Извините, но данная команда недоступна в личных сообщениях!"
            ).set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if not interaction.channel.permissions_for(interaction.user).manage_channels:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(), 
                description="Вы не имеете права `управление каналом` для использования этой команды!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        delay = seconds
        try:
            await interaction.channel.edit(
                reason=f"{reason} // {interaction.user}", 
                slowmode_delay=delay
            )
        except Forbidden:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(), 
                description=f"У бота отсутствует право на управление данным каналом!\n"
                "Тип ошибки: `Forbidden`"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = None
            if seconds > 0:
                embed = discord.Embed(
                    title="Успешно!", 
                    color=discord.Color.green(), 
                    description=f"Медленный режим успешно установлен на `{seconds}` секунд.", 
                    timestamp=datetime.datetime.now()
                )
            else:
                embed = discord.Embed(
                    title="Успешно!", 
                    color=discord.Color.green(), 
                    description="Медленный режим успешно снят.", 
                    timestamp=datetime.datetime.now()
                )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="timeout", description="[Модерация] Отправляет участника подумать о своем поведении")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(
        member="Участник, которому нужно выдать тайм-аут", 
        minutes="Кол-во минут, на которые будет выдан тайм-аут.", 
        reason="Причина выдачи наказания."
    )
    async def timeout(
        self, 
        interaction: discord.Interaction, 
        member: discord.User, 
        minutes: app_commands.Range[int, 0, 40320], 
        reason: app_commands.Range[str, None, 512]
    ):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        try:
            member: discord.Member = await interaction.guild.fetch_member(member.id)
        except NotFound:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Указанный пользователь не найден в этом сервере!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        member_bot = interaction.guild.me

        if not interaction.user.guild_permissions.moderate_members:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(), 
                description="У вас отсутствует право `управление участниками` для использования команды!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if (member.top_role.position >= member_bot.top_role.position or 
                member.guild_permissions.administrator or
                not member_bot.guild_permissions.moderate_members):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Бот не может замутить данного пользователя!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if ((member.top_role.position >= interaction.user.top_role.position or 
                interaction.guild.owner_id == member.id) and 
                interaction.guild.owner_id != interaction.user.id):
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(), 
                description="Вы не можете выдавать наказание участникам, чья роль выше либо равна вашей!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        until = datetime.datetime.now().astimezone() + datetime.timedelta(minutes=minutes) if minutes > 0 else None
        try:
            await member.edit(
                timed_out_until=until, 
                reason=f"{reason} // {interaction.user}"
            )
        except Forbidden:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(), 
                description=f"Не удалось выдать участнику тайм-аут. Убедитесь в наличии прав на управление участниками "
                "у бота и попробуйте снова!\nТип ошибки: `Forbidden`"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if minutes > 0:    
            embed = discord.Embed(
                title=f'Участник отправлен в тайм-аут на сервере {interaction.guild.name}!', 
                color=discord.Color.red(), 
                timestamp=datetime.datetime.now()
            ).add_field(
                name="Участник:", 
                value=f"{member.mention}\n({member.id})",
            ).add_field(
                name="Модератор:", 
                value=f"{interaction.user.mention}\n({interaction.user.id})"
            ).add_field(
                name="Срок:", 
                value=f"{minutes:,} минут"
            ).add_field(
                name="Причина:", 
                value=dutils.escape_markdown(reason)
            )
            try:
                await member.send(embed=embed)
            except:
                embed.set_footer(
                    text="Личные сообщения участника закрыты, поэтому бот не смог оповестить участника о выдаче наказания!"
                )
            return await interaction.response.send_message(embed=embed)

        embed = discord.Embed(
            title=f'С участника снят тайм-аут на сервере {interaction.guild.name}!', 
            color=discord.Color.red(), 
            timestamp=datetime.datetime.now()
        ).add_field(
            name="Участник:", 
            value=f"{member.mention}\n({member.id})"
        ).add_field(
            name="Модератор:", 
            value=f"{interaction.user.mention}\n({interaction.user.id})"
        ).add_field(
            name="Причина:", 
            value=dutils.escape_markdown(reason)
        )
        try:
            await member.send(embed=embed)
        except:
            embed.set_footer(
                text="Личные сообщения участника закрыты, поэтому бот не смог оповестить участника о выдаче наказания!"
            )
        return await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name='clone', description="[Модерация] Клонирует чат.")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(delete_original="Удалять ли клонируемый канал?", reason="Причина клонирования")
    async def clone(
        self, 
        interaction: discord.Interaction, 
        reason: app_commands.Range[str, None, 512], 
        delete_original: bool = False
    ):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(), 
                description="Извините, но данная команда недоступна в личных сообщениях!"
            ).set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if isinstance(interaction.channel, discord.Thread):
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Данная команда недоступна в ветках!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if not interaction.user.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(), 
                description="У вас отсутствует право `управление каналами` для использования команды."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        try:
            cloned = await interaction.channel.clone(reason=f"{reason} // {interaction.user}")
        except Forbidden:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(), 
                description=f"Бот не имеет право `управление каналами` для совершения действия!\n"
                "Тип ошибки: `Forbidden`"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await cloned.move(
                after=discord.Object(id=interaction.channel.id), 
                reason=f"Клонирование // {interaction.user}"
            )
            embed = discord.Embed(
                title="Успешно!", 
                color=discord.Color.green(), 
                description="Канал успешно клонирован!"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            if delete_original:
                await sleep(10)
                await interaction.channel.delete(
                    reason=f"Использование команды // {interaction.user}"
                )

    @app_commands.command(name="resetnick", description="[Модерация] Просит участника поменять ник")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(member="Участник, которого надо попросить сменить ник", reason="Причина сброса ника")
    async def resetnick(
        self, 
        interaction: discord.Interaction, 
        member: discord.User, 
        reason: app_commands.Range[str, None, 512]
    ):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            member = await interaction.guild.fetch_member(member.id)
        except NotFound:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(), 
                description="Участник должен находиться на сервере для использования команды!"
            ).set_thumbnail(url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if not interaction.user.guild_permissions.manage_nicknames:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(), 
                description="У вас отсутствует право `управлять никнеймами` для использования команды."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if member.top_role.position >= interaction.user.top_role.position and interaction.guild.owner_id != interaction.user.id:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(), 
                description="Вы не можете управлять никнеймами участников, чья роль выше либо равна вашей!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(
                title="Не понял", 
                color=discord.Color.red(), 
                description="Нельзя сбросить ник боту."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            await member.edit(
                nick="Смените ник", 
                reason=f"{reason} // {interaction.user}"
            )
        except Forbidden:
            embed = discord.Embed(
                title="Ошибка!", 
                color=discord.Color.red(), 
                description=f"У бота отсутствует право `управлять никнеймами` для совершения действия!"
                "\nТип ошибки: `Forbidden`"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        embed = discord.Embed(
            title=f"Никнейм сброшен на сервере {interaction.guild.name}!", 
            color=discord.Color.red()
        ).add_field(
            name="Участник:", 
            value=f"{member.mention}\n({member.id})"
        ).add_field(
            name="Модератор:", 
            value=f"{interaction.user.mention}\n({interaction.user.id})"
        ).add_field(
            name="Причина:", 
            value=dutils.escape_markdown(reason)
        )
        try:
            await member.send(embed=embed)
        except:
            embed.set_footer(text="Участник закрыл доступ к личным сообщениям, поэтому не был оповещён.")
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
    logger.info('Cog "Moderation" запущен!')
