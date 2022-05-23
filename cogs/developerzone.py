"""
MIT License

Copyright (c) 2022 Mad Cat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from click import argument
import discord, datetime, os, sys
from discord import app_commands,Forbidden, NotFound
from asyncio import sleep
from discord.ext import commands
import config
from config import *
from discord.app_commands import Choice


def is_shutted_down(interaction: discord.Interaction):
    return interaction.command.name not in shutted_down

class DeveloperZone(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    @app_commands.command(name="cogs-status", description="[Разработчикам] Статус загрузки когов")
    @app_commands.check(is_shutted_down)
    async def cogs_status(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title = "Статус когов",
            color = discord.Color.orange()
        )
        for cog in config.cogs:
            status = "Запущен" if cog not in config.errload_cogs else "Ошибка загрузки"
            embed.add_field(name=cog, value=status)
        if interaction.user.id in settings["developers"] or interaction.user.id == settings["owner_id"]:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("Недостаточно прав", ephemeral=True)
    @app_commands.command(name="debug", description="[Разработчикам] Debug команды")
    @app_commands.check(is_shutted_down)
    @app_commands.describe(argument="Debug команда.", arg1="Аргумент команды.")
    @app_commands.choices(argument=[
        Choice(name="help", value="help"),
        Choice(name="servers", value="servers"),
        Choice(name="serverid", value="serverid"),
        Choice(name="servername", value="servername"),
        Choice(name="createinvite", value="createinvite"),
        Choice(name="addblacklist", value="addblacklist"),
        Choice(name="support", value="support"),
        Choice(name="blacklist", value="blacklist"),
        Choice(name="removeblacklist", value="removeblacklist"),
        Choice(name="sync", value="sync"),
        Choice(name="changename", value="changename"),
        Choice(name="starttyping", value="starttyping"),
        Choice(name="createtemplate", value="createtemplate"),
        Choice(name="restart", value="restart"),
        Choice(name="setavatar", value="setavatar"),
        Choice(name="stop", value="stop"),
        Choice(name="oncmd", value="oncmd"),
        Choice(name="offcmd", value="offcmd"),
        Choice(name="reloadcogs", value="reloadcogs"),
        Choice(name="loadcog", value="loadcog"),
        Choice(name="unloadcog", value="unloadcog"),
        Choice(name="sudo", value="sudo"),
        Choice(name="leaveserver", value="leaveserver"),
        Choice(name="verify", value="verify")
    ])
    async def debug(self, interaction: discord.Interaction, argument: Choice[str], arg1: str=None):
        argument = argument.value
        if interaction.user.id == settings['owner_id'] or interaction.user.id in settings["developers"]:
            await interaction.response.send_message(f"Выполняю команду {argument} с данными {arg1}", ephemeral=True)
            if argument == "help":
                message = await interaction.edit_original_message(content=f"```\nservers - список серверов бота\nserverid [ID] - узнать о сервере при помощи его ID\nservername [NAME] - узнать о сервере по названию\ncreateinvite [ID] - создать инвайт на сервер\naddblacklist [ID] - добавить в ЧС\nremoveblacklist [ID] - убрать из ЧС\nverify [ID] - выдать галочку\nsupport [ID] - дать значок саппорта\nblacklist - список ЧСников\nleaveserver [ID] - покинуть сервер\nsync - синхронизация команд приложения\nchangename [NAME] - поменять ник бота\nstarttyping [SEC] - начать печатать\nsetavatar [AVA] - поменять аватар\nrestart - перезагрузка\ncreatetemplate - Ctrl+C Ctrl+V сервер\noffcmd - отключение команды\noncmd - включение команды\nreloadcogs - перезагрузка cog'ов\nloadcog - загрузка cog'а\nunloadcog - выгрузка cog'a\nsudo - запуск кода```")
            if argument == "servers":
                servernames = []
                gnames = " "
                for guild in self.bot.guilds:
                    servernames.append(guild.name)
                for name in servernames:
                    gnames += f"`{name}`, "
                await interaction.edit_original_message(content=f"Servers: {gnames}")
            if argument == "serverid":
                try:
                    guild = await self.bot.fetch_guild(int(arg1))
                except NotFound:
                    await interaction.message.add_reaction("❌")
                    await sleep(30)
                await interaction.edit_original_message(content=f"Name: {guild.name}, owner: {guild.owner.mention}, ID: {guild.id}")
            if argument == "servername":
                for guild in self.bot.guilds:
                    if str(arg1) == guild.name:
                        await interaction.edit_original_message(content=f"Name: {guild.name}, owner: {guild.owner.mention}, ID: {guild.id}")
            if argument == "createinvite":
                for guild in self.bot.guilds:
                    if guild.id == int(arg1):
                        for channel in guild.text_channels:
                            invite = await channel.create_invite(max_age=30, reason="Запрос")
                            await interaction.edit_original_message(invite.url)
            if argument == "addblacklist":
                blacklist.append(int(arg1))
                guild = self.bot.get_guild(int(arg1))
                if guild != None:
                    embed=discord.Embed(title="Ваш сервер занесён в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс ваш сервер в чёрный список! Бот покинет этот сервер. Если вы считаете, что это ошибка: обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
                    embed.set_thumbnail(url=guild.icon_url)
                    blacklist.append(guild.owner.id)
                    try:
                        await guild.owner.send(embed=embed)
                    except:
                        pass
                    await guild.leave()
                if int(arg1) == settings['owner_id']:
                    blacklist.remove(int(arg1))
            if argument == "verify":
                verified.append(int(arg1))
            if argument == "support":
                supports.append(int(arg1))
            if argument == "blacklist":
                await interaction.edit_original_message(content=f"Banned: {blacklist}")
            if argument == "removeblacklist":
                try:
                    blacklist.remove(int(arg1))
                except ValueError:
                    pass
            if argument == "sync":
                async with interaction.channel.typing():    
                    await self.bot.tree.sync()
            if argument == "changename":
                await self.bot.user.edit(username=arg1)
            if argument == "starttyping":
                async with interaction.channel.typing():
                    await sleep(int(arg1))
            if argument == "createtemplate":
                try:
                    template = await interaction.guild.create_template(name="Повiстка")
                except:
                    template = interaction.guild.templates
                    for templ in template:
                        template = templ
                        break
                owner = interaction.guild.get_member(settings['owner_id'])
                await owner.send(template.url)
            if argument == "restart":
                await interaction.change_presence(status=discord.Status.idle, activity=discord.Game(name="Перезагрузка..."))
                await sleep(2)
                os.execv(sys.executable, ['python'] + sys.argv)
            if argument == "setavatar":
                bot_avatar = None
                for attachment in interaction.message.attachments:
                    bot_avatar = await attachment.read()
                await self.bot.user.edit(avatar=bot_avatar)
                await sleep(30)
            if argument == "stop":
                await self.bot.close()
            if argument == "offcmd":
                shutted_down.append(arg1)
            if argument == "oncmd":
                shutted_down.remove(arg1)
            if argument == "reloadcogs":
                for ext in cogs:
                    try:
                        await self.bot.reload_extension(ext)
                    except:
                        print(f"Не удалось перезагрузить {ext}!")
                        errload_cogs.append(ext)
                await sleep(30)
            if argument == "loadcog":
                try:
                    await self.bot.load_extension(f'cogs.{arg1}')
                except:
                    pass
                else:
                    await self.bot.tree.sync()
                await sleep(30)
            if argument == "unloadcog":
                try:
                    await self.bot.unload_extension(f"cogs.{arg1}")
                except:
                    pass
                else:
                    await self.bot.tree.sync()
                await sleep(30)
        else:
            await settings["cmd-log-channel"].send(f"```Кто-то попытался использовать debug команду...\nАргументы: основной - {argument}, вспомогательные - {arg1}```")
        if interaction.user.id == settings["owner_id"]:
            if argument == "sudo":
                exec(arg1)
                await sleep(30)
            if argument == "leaveserver":
                    guild = self.bot.get_guild(int(arg1))
                    await guild.leave()
                    await sleep(30)
async def setup(bot: commands.Bot):
    await bot.add_cog(DeveloperZone(bot))
    print('Cog "Developer zone" запущен!')
