import discord
import logging

from discord.ext import commands
from discord import app_commands
from discord import ui
from classes import db

from classes import checks
from config import *

logger = logging.getLogger('discord')

class Marries(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="marry", description="[Свадьбы] Пожениться")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(member="Участник, с которым Вы хотите пожениться.")
    async def marry(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        user_id = interaction.user.id
        member_id = member.id
        
        if member_id == user_id:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Нельзя жениться на самому себе!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Нельзя жениться на боте!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        marry = db.get_marries(interaction.guild.id, user_id)
        if marry is not None:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="У Вас есть активный брак! Разведитесь перед заведением нового брака."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        marry = db.get_marries(interaction.guild.id, member_id)
        if marry is not None:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Данный пользователь уже в браке!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        class Accept(ui.View):
            def __init__(self):
                super().__init__(timeout=180)
                self.value = None
                self.user_id = member_id
            
            @ui.button(label="Да", style=discord.ButtonStyle.green)
            async def yes(self, viewinteract: discord.Interaction, button: ui.Button):
                if viewinteract.user.id != member_id: 
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                self.value = True
                self.stop()
                
            @ui.button(label="Нет", style=discord.ButtonStyle.red)
            async def no(self, viewinteract: discord.Interaction, button: ui.Button):
                if viewinteract.user.id == user_id:
                    self.value = False
                    self.user_id = user_id
                    return self.stop()
                if viewinteract.user.id != member_id: 
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                self.value = False
                self.stop()
    
        embed = discord.Embed(
            title="Свадьба - Ожидание",
            color=discord.Color.yellow(),
            description=f"<@!{user_id}> хочет пожениться на Вас. Вы согласны?"
        )
        embed.set_footer(text="Время на ответ: 3 минуты.")
        view = Accept()
        await interaction.response.send_message(embed=embed, content=f"<@!{member_id}>", view=view)
        await view.wait()
        if view.value is None:
            embed = discord.Embed(
                title="Время вышло!",
                color=discord.Color.red()
            )
            return await interaction.edit_original_response(embed=embed, content=None, view=None)
        if not view.value and view.user_id == user_id:
            embed = discord.Embed(
                title="Свадьба - Отмена",
                color=discord.Color.red(),
                description="Инициатор отменил свадьбу."
            )
            return await interaction.edit_original_response(embed=embed, content=None, view=None)
        if not view.value and view.user_id == member_id:
            embed = discord.Embed(
                title="Свадьба - Отказ",
                color=discord.Color.red(),
                description="Вам отказали в свадьбе."
            )
            return await interaction.edit_original_response(embed=embed, content=None, view=None)
        db.marry(interaction.guild.id, user_id, member_id)
        embed = discord.Embed(
            title="Свадьба - Поздравляем!",
            color=discord.Color.green(),
            description=f"<@!{user_id}> и <@!{member_id}> теперь женаты. Горько!"
        )
        await interaction.edit_original_response(embed=embed, content=None, view=None)
    
    @app_commands.command(name="divorce", description="[Свадьбы] Развод")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    async def dibvorce(self, interaction: discord.Interaction):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        user_id = interaction.user.id
        
        marry = db.get_marries(interaction.guild.id, user_id)
        if marry is None:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="У Вас нет активного брака!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        class Accept(ui.View):
            def __init__(self):
                super().__init__(timeout=180)
                self.value = None
            
            @ui.button(label="Да", style=discord.ButtonStyle.green)
            async def yes(self, viewinteract: discord.Interaction, button: ui.Button):
                if viewinteract.user.id != user_id: 
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                self.value = True
                self.stop()
                
            @ui.button(label="Нет", style=discord.ButtonStyle.red)
            async def no(self, viewinteract: discord.Interaction, button: ui.Button):
                if viewinteract.user.id != user_id: 
                    return await viewinteract.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                self.value = False
                self.stop()
    
        embed = discord.Embed(
            title="Развод - Подтверждение",
            color=discord.Color.yellow(),
            description=f"Вы действительно хотите развестись с <@!{marry['married_id'] if marry['married_id'] != user_id else marry['user_id']}>?"
        )
        embed.set_footer(text="Время на ответ: 3 минуты.")
        view = Accept()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        await view.wait()
        if view.value is None:
            embed = discord.Embed(
                title="Время вышло!",
                color=discord.Color.red()
            )
            return await interaction.edit_original_response(embed=embed, content=None, view=None)
        if not view.value:
            embed = discord.Embed(
                title="Развод - Отмена",
                color=discord.Color.red(),
                description="Вы отменили развод."
            )
            return await interaction.edit_original_response(embed=embed, content=None, view=None)
        db.divorce(interaction.guild.id, user_id)
        embed = discord.Embed(
            title="Развод - Завершено!",
            color=discord.Color.green(),
            description="Вы успешно развелись. Надеемся, все будет хорошо..."
        )
        await interaction.edit_original_response(embed=embed, view=None)
    
    @app_commands.command(name="marry-info", description="[Свадьбы] Информация о Вашем браке")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(member="Участник, чей брак Вы хотите посмотреть.")
    async def marry_info(self, interaction: discord.Interaction, member: discord.User = None):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        user_id = interaction.user.id if member is None else member.id

        marry = db.get_marries(interaction.guild.id, user_id)
        if marry is None:
            if user_id == interaction.user.id:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Вы не имеете активного брака!"
                )
            else:
                embed = discord.Embed(
                    title="Ошибка!",
                    color=discord.Color.red(),
                    description="Пользователь не имеет активного брака!"
                )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        married_id = marry['married_id']
        user_id = marry['user_id']

        embed = discord.Embed(
            title="Информация о браке",
            color=discord.Color.orange(),
            description=f"<t:{marry['dt']}:R> <@!{user_id}> сделал предложение руки и сердца <@!{married_id}>. До сих пор они вместе."
        )
        embed.add_field(name="Дата заключения:", value=f"<t:{marry['dt']}>")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="marries", description="[Свадьбы] Список браков.")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    async def marries(self, interaction: discord.Interaction):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        marries = db.get_all_marries(interaction.guild.id)
        if marries is None:
            embed = discord.Embed(
                title="Браки сервера:",
                color=discord.Color.orange(),
                description="*Пусто...*"
            )
            embed.set_footer(text="Используйте команду /marry для предложения заключения брака.")
            return await interaction.response.send_message(embed=embed)
        description = "".join(
            f"`{count}.` <@!{marry['user_id']}> и <@!{marry['married_id']}>.\nДата заключения брака: <t:{marry['dt']}> (<t:{marry['dt']}:R>).\n\n"
            for count, marry in enumerate(marries, start=1)
        )
        embed = discord.Embed(
            title="Браки сервера:",
            color=discord.Color.orange(),
            description=description
        )
        embed.set_footer(text="Используйте команду /marry для предложения заключения брака.")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="marry-people", description="[Свадьбы] Поженить принудительно пару.")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(
        member="Участник, которого Вы хотите поженить.", 
        member2="Участник, с кем Вы хотите поженить первого участника."
    )
    async def marry_people(self, interaction: discord.Interaction, member: discord.User, member2: discord.User):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if not interaction.user.guild_permissions.manage_guild:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Для принудительной свадьбы необходимо право на `управление сервером`."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        user_id = member.id
        member_id = member2.id
        
        if member_id == user_id:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Нельзя женить человека самим с собой!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot or member2.bot:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Нельзя женить на боте!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        marry = db.get_marries(interaction.guild.id, user_id)
        if marry is not None:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description=f"У <@!{user_id}> есть активный брак! Разведите его перед заведением нового брака."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        marry = db.get_marries(interaction.guild.id, member_id)
        if marry is not None:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description=f"У <@!{member_id}> есть активный брак! Разведите его перед заведением нового брака."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        db.marry(interaction.guild.id, user_id, member_id)
        embed = discord.Embed(
            title="Свадьба - Поздравляем!",
            color=discord.Color.green(),
            description=f"Вы поженены купидоном {interaction.user.mention}. Горько!"
        )
        await interaction.response.send_message(embed=embed, content=f"<@!{user_id}> и <@!{member_id}>")
    
    @app_commands.command(name="divorce-people", description="[Свадьбы] Развести принудительно пару.")
    @app_commands.check(lambda i: not checks.is_in_blacklist(i.user.id))
    @app_commands.check(lambda i: not checks.is_shutted_down(i.command.name))
    @app_commands.describe(member="Участник, которого Вы хотите развести.")
    async def divorce_people(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed=discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Извините, но данная команда недоступна в личных сообщениях!")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if not interaction.user.guild_permissions.manage_guild:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Для принудительного развода необходимо право на `управление сервером`."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        user_id = member.id
        
        if interaction.user.id == user_id:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Нельзя развести принудительно себя! Используйте `/divorce`."
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description="Разве боты могут жениться?"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        marry = db.get_marries(interaction.guild.id, user_id)
        if marry is None:
            embed = discord.Embed(
                title="Ошибка!",
                color=discord.Color.red(),
                description=f"У <@!{user_id}> нет активного брака!"
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        db.divorce(interaction.guild.id, user_id)
        embed = discord.Embed(
            title="Развод - Успешно!",
            color=discord.Color.green(),
            description=f"Вы разведены антикупидоном {interaction.user.mention}."
        )
        await interaction.response.send_message(embed=embed, content=f"<@!{marry['user_id']}> и <@!{marry['married_id']}>")

async def setup(bot: commands.Bot):
    await bot.add_cog(Marries(bot))