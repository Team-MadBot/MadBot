# -*- coding: utf-8 -*-
import discord, time, datetime, os, sys
from urllib.parse import quote_plus
from boticordpy import BoticordClient
from discord import app_commands, Forbidden
from pypresence import Presence
from discord.ext import commands
from asyncio import sleep
from config import *

btns=[
    {
        "label": "Добавить бота",
        "url": f"https://discord.com/oauth2/authorize?client_id={settings['app_id']}&permissions={settings['perm_scope']}&scope=bot%20applications.commands"
    },
    {
        "label": "Поддержка бота",
        "url": settings['support_invite']
    }
]
try:
    RPC = Presence(f"{settings['app_id']}") # Discord Rich Presence. Будет видно при запуске бота.
except:
    pass
else:
    RPC.connect()
    RPC.update(
        state=f"Бот запущен.",
        details="Работа над ботом.",
        start=time.time(),
        large_image="mad_cat_default",
        large_text="MadBot - запущен",
        buttons=btns
    )

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('mad.'), intents=discord.Intents.all(), application_id=settings['app_id'])

    async def setup_hook(self):
        for ext in cogs:
            try:
                await self.load_extension(ext)
            except Exception as e:
                print(f"Не удалось подключить {ext}!\n{e}")
        
        await bot.tree.sync()
    
    async def on_connect(self):
        await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="Перезагрузка..."))
        print("Соединено! Авторизация...")

    async def on_ready(self):
        global started_at
        server = bot.get_guild(settings['server']) # Сервер логов.
        logs = server.get_channel(settings['log_channel']) # Канал логов.
        channel = bot.get_channel(967484036127813713) # Канал "общения" мониторинга. Закомментируйте, если хотите.
        for guild in bot.guilds: # Проверка на нахождение в чёрном списке.
            if guild.id in blacklist:
                await guild.leave()
                print(f"Бот вышел из {guild.name} ({guild.id})")
        print(f"Авторизация успешна! {bot.user} готов к работе!")
        if round(bot.latency, 3)*1000 < 90:
            started_at -= 10800
        async def get_stats():
            return {"servers": len(bot.guilds), "shards": 0, "users": len(bot.users)}

        async def on_success_posting():
            print("Статистика на boticord.top обновлена!")
        
        if bot.user.name == "MadBot":
            boticord_client = BoticordClient(settings['boticord_key'])
            autopost = (
                boticord_client.autopost()
                .init_stats(get_stats)
                .on_success(on_success_posting)
                .start()
            )
        embed = discord.Embed(title="Бот перезапущен!", color=discord.Color.red(), description=f"Пинг: `{int(round(bot.latency, 3)*1000)}ms`\nВерсия: `{settings['curr_version']}`")
        await logs.send(embed=embed)
        await channel.send("OK") # Канал "общения" мониторинга. Закомментируйте, если хотите.
        while True:
            await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} серверов | {int(round(bot.latency, 3)*1000)}ms"))
            await sleep(60)
            await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(bot.guilds)} серверов | v{settings['curr_version']}"))
            await sleep(60)
    
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            return
        try:
            await ctx.message.add_reaction("❌")
            message = await ctx.message.reply(content=f"```\n{error}```")
        except:
            pass
        print(error)
        await sleep(30)
        try:
            await message.delete()
            await ctx.message.delete()
        except:
            pass
    
    async def on_guild_join(self, guild: discord.Guild):
        if guild.id in blacklist or guild.owner.id in blacklist: # Проверка на чёрный список.
            embed=discord.Embed(title="Ваш сервер либо вы сами занесён(-ы) в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс ваш сервер либо вас в чёрный список! Бот покинет этот сервер. Если вы считаете, что это ошибка, обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
            embed.set_thumbnail(url=guild.icon_url)
            try:
                await guild.owner.send(embed=embed)
            except:
                pass
            await guild.leave()
            print(f"Бот вышел из {guild.name} ({guild.id})")
        else: 
            await sleep(1)
            embed = discord.Embed(title=f"Спасибо за добавление {bot.user.name} на сервер {guild.name}", color=discord.Color.orange(), description=f"Перед использованием убедитесь, что слеш-команды включены у вас на сервере. Ваш сервер: `{len(bot.guilds)}-ый`.")
            embed.add_field(name="Поддержка:", value=settings['support_invite'])
            embed.set_thumbnail(url=bot.user.avatar.url)
            adder = None
            try:
                async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.bot_add):
                    if entry.target.id == bot.user.id:
                        adder = entry.user
            except Forbidden:
                adder = guild.owner
                embed.set_footer(text="Бот написал вам, так как не смог уточнить, кто его добавил.")
            try:
                await adder.send(embed=embed)
            except:
                pass
            embed = discord.Embed(title="Новый сервер!", color=discord.Color.green())
            embed.add_field(name="Название:", value=f"`{guild.name}`")
            embed.add_field(name="Владелец:", value=f"{guild.owner.mention}")
            embed.add_field(name="ID сервера:", value=f"`{guild.id}`")
            embed.add_field(name="Кол-во участников:", value=f"`{guild.member_count}`")
            try:
                embed.set_thumbnail(url=guild.icon.url)
            except:
                pass
            log_channel = bot.get_channel(settings['log_channel'])
            await log_channel.send(embed=embed)
            await bot.tree.sync()
        
    async def on_member_join(self, member: discord.Member):
        if member.guild.id == 914181806285279232 and not(member.bot):
            channel = member.guild.get_channel(914191453738119240)
            embed = discord.Embed(title='Новый участник!', color=discord.Color.green(), description=f"Пользователь {member.mention} присоединился к серверу.", timestamp=member.joined_at)
            embed.add_field(name="Дата регистрации:", value=f"{discord.utils.format_dt(member.created_at, 'D')} ({discord.utils.format_dt(member.created_at, 'R')})", inline=False)
            embed.set_thumbnail(url=member.avatar.url)
            embed.set_footer(text=f"ID участника: {member.id}")
            try:
                embed.set_image(url=f"https://some-random-api.ml/welcome/img/5/gaming4?key={settings['key']}&type=join&username={quote_plus(member.name)}&discriminator={member.discriminator}&memberCount={member.guild.member_count}&guildName=MadBot%20Support&avatar={member.display_avatar.replace(format='png')}&textcolor=orange")
            except:
                pass
            await channel.send(embed=embed)
    

bot=MyBot()

@bot.tree.error
async def on_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CommandOnCooldown):
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"У вас кулдаун! Попробуйте через `{str(error).removeprefix('You are on cooldown. Try again in ')}`!")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    if isinstance(error, app_commands.CheckFailure):
        embed = discord.Embed(title="Команда отключена!", color=discord.Color.red(), description="Владелец бота временно отключил эту команду! Попробуйте позже!")
        return await interaction.response.send_message(embed=embed, ephemeral=True) 
    if str(error).startswith("Failed to convert"):
        embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description="Данная команда недоступна в личных сообщениях!")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    embed = discord.Embed(title="Ошибка!", color=discord.Color.red(), description=f"Произошла неизвестная ошибка! Обратитесь в поддержку со скриншотом ошибки!\n```\n{error}```", timestamp=discord.utils.utcnow())
    channel = bot.get_channel(settings['log_channel'])
    await channel.send(f"```\nOn command '{interaction.command.name}'\n{error}```")
    try:
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except discord.errors.InteractionResponded:
        await interaction.edit_original_message(embeds=[embed], view=None)
    print(error)

@bot.command()
async def debug(ctx: commands.Context):
    if ctx.author.id in coders or ctx.author.id == settings['owner_id']:
        class Button(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=30)
                self.value = None
            
            @discord.ui.button(label="Показать панель", emoji="⚒️", style=discord.ButtonStyle.danger)
            async def show_panel(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != ctx.author.id:
                    return await interaction.response.send_message("Не для тебя кнопочка!", ephemeral=True)
                class Page1(discord.ui.View):
                    def __init__(self):
                        super().__init__(timeout=300)

                    class Page2(discord.ui.View):
                        def __init__(self):
                            super().__init__(timeout=300)
                        
                        @discord.ui.button(label="Список подключенных когов", style=discord.ButtonStyle.blurple)
                        async def cogs(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                            embed = discord.Embed(title="Список подключенных когов", color=discord.Color.orange())
                            for name in bot.cogs:
                                embed.add_field(name=name, value="Запущен")
                            await viewinteract.response.send_message(embed=embed, ephemeral=True)
                        
                        @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.primary, row=1)
                        async def prevpage(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                            await viewinteract.response.edit_message(view=Page1())
                    
                    @discord.ui.button(label="Сервера", style=discord.ButtonStyle.primary)
                    async def servers(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        servernames = []
                        gnames = " "
                        for guild in bot.guilds:
                            servernames.append(guild.name)
                        for name in servernames:
                            gnames += f"`{name}`, "
                        await viewinteract.response.send_message(f"Сервера: {gnames}", ephemeral=True)
                    
                    @discord.ui.button(label="Получить сервер", style=discord.ButtonStyle.primary)
                    async def getserver(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - получение сервера"):
                            ans = discord.ui.TextInput(label="Название/ID сервера:", max_length=100, min_length=2)
                            async def on_submit(self, modalinteract: discord.Interaction):
                                for guild in bot.guilds:
                                    if str(self.ans) == guild.name:
                                        return await modalinteract.response.send_message(f"Name: {guild.name}, owner: {guild.owner.mention}, ID: {guild.id}", ephemeral=True)
                                    try:
                                        if int(str(self.ans)) == guild.id:
                                            return await modalinteract.response.send_message(f"Name: {guild.name}, owner: {guild.owner.mention}, ID: {guild.id}", ephemeral=True)
                                    except:
                                        pass
                        await viewinteract.response.send_modal(Input())
                    
                    @discord.ui.button(label="Выгрузка кога", style=discord.ButtonStyle.blurple)
                    async def unloadcog(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - выгрузка кога"):
                            ans = discord.ui.TextInput(label="Название кога:", max_length=64, placeholder="tools")
                            async def on_submit(self, modalinteract: discord.Interaction):
                                try:
                                    await bot.unload_extension(f'cogs.{str(self.ans)}')
                                except Exception as e:
                                    return await modalinteract.response.send_message(f"```\n{e}```", ephemeral=True)
                                await bot.tree.sync()
                                await modalinteract.response.send_message(f"Ког {str(self.ans)} выгружен!", ephemeral=True)
                        await viewinteract.response.send_modal(Input())
                    
                    @discord.ui.button(label="В черный список", style=discord.ButtonStyle.primary)
                    async def addblacklist(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - в чёрный список"):
                            ans = discord.ui.TextInput(label="ID участника/сервера:", min_length=18, max_length=18)
                            async def on_submit(self, modalinteract: discord.Interaction):
                                blacklist.append(int(str(self.ans)))
                                guild = bot.get_guild(int(str(self.ans)))
                                if guild != None:
                                    embed=discord.Embed(title="Ваш сервер занесён в чёрный список бота!", color=discord.Color.red(), description=f"Владелец бота занёс ваш сервер в чёрный список! Бот покинет этот сервер. Если вы считаете, что это ошибка: обратитесь в поддержку: {settings['support_invite']}", timestamp=datetime.datetime.utcnow())
                                    embed.set_thumbnail(url=guild.icon_url)
                                    blacklist.append(guild.owner.id)
                                    try:
                                        await guild.owner.send(embed=embed)
                                    except:
                                        pass
                                    await guild.leave()
                                await modalinteract.response.send_message(f"`{str(self.ans)}` занесен в черный список!", ephemeral=True)
                                await sleep(30)
                                if int(str(self.ans)) == settings['owner_id']:
                                    blacklist.remove(settings['owner_id'])
                        await viewinteract.response.send_modal(Input())
                    
                    @discord.ui.button(label="Верифицировать", style=discord.ButtonStyle.primary)
                    async def verify(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - верификация"):
                            ans = discord.ui.TextInput(label="ID участника/сервера:", min_length=18, max_length=18)
                            async def on_submit(self, modalinteract: discord.Interaction):
                                verified.append(int(str(self.ans)))
                                await modalinteract.response.send_message(f"`{str(self.ans)}` верифицирован(-а)", ephemeral=True)
                        await viewinteract.response.send_modal(Input())
                    
                    @discord.ui.button(label="Выдать значок саппорта", disabled=not(ctx.author.id == settings['owner_id']))
                    async def support(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - в саппорты"):
                            ans = discord.ui.TextInput(label="ID участника:", min_length=18, max_length=18)
                            async def on_submit(self, modalinteract: discord.Interaction):
                                supports.append(int(str(self.ans)))
                                await modalinteract.response.send_message(f"`{str(self.ans)}` теперь - саппорт", ephemeral=True)
                        await viewinteract.response.send_modal(Input())
                    
                    @discord.ui.button(label="Добавить кодера", disabled=not(ctx.author.id == settings['owner_id']))
                    async def coder(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - в кодеры"):
                            ans = discord.ui.TextInput(label="ID участника:", min_length=18, max_length=18)
                            async def on_submit(self, modalinteract: discord.Interaction):
                                coders.append(int(str(self.ans)))
                                await modalinteract.response.send_message(f"`{str(self.ans)}` теперь - кодер", ephemeral=True)
                        await viewinteract.response.send_modal(Input())
                    
                    @discord.ui.button(label="Черный список")
                    async def blacklist(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        await viewinteract.response.send_message(f"Забаненные: {blacklist}", ephemeral=True)

                    @discord.ui.button(label="Убрать из ЧС")
                    async def removeblacklist(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - убрать из ЧС"):
                            ans = discord.ui.TextInput(label="ID участника/сервера:", min_length=18, max_length=18)
                            async def on_submit(self, modalinteract: discord.Interaction):
                                try:
                                    blacklist.remove(int(str(self.ans)))
                                except:
                                    await modalinteract.response.send_message("Участник/сервер в ЧСе не обнаружен!", ephemeral=True)
                                else:
                                    await modalinteract.response.send_message(f"`{str(self.ans)}` вынесен(-а) из ЧС!", ephemeral=True)
                        await viewinteract.response.send_modal(Input())
                    
                    @discord.ui.button(label="Покинуть сервер", disabled=not(ctx.author.id == settings['owner_id']))
                    async def leaveserver(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - выход из сервера"):
                            ans = discord.ui.TextInput(label="ID сервера:", max_length=18, min_length=18)
                            async def on_submit(self, modalinteract: discord.Interaction):
                                guild = await bot.fetch_guild(int(str(self.ans)))
                                if guild == None:
                                    return await modalinteract.response.send_message("Сервер не обнаружен!", ephemeral=True)
                                await guild.leave()
                                await modalinteract.response.send_message(f"Бот вышел с {guild.name}!", ephemeral=True)
                        await viewinteract.response.send_modal(Input())
                    
                    @discord.ui.button(label="Синхронизация команд", style=discord.ButtonStyle.green)
                    async def sync(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        await viewinteract.response.send_message("Синхронизация...", ephemeral=True)
                        await bot.tree.sync()
                        await viewinteract.edit_original_message(content="Команды синхронизированы!")
                    
                    @discord.ui.button(label='Смена ника', style=discord.ButtonStyle.green, disabled=not(ctx.author.id == settings['owner_id']))
                    async def changename(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - смена ника"):
                            ans = discord.ui.TextInput(label="Новый ник:", min_length=2, max_length=32)
                            async def on_submit(self, modalinteract: discord.Interaction):
                                try:
                                    await bot.user.edit(username=str(self.ans))
                                except Exception as e:
                                    await modalinteract.response.send_message(f"```\n{e}```", ephemeral=True)
                                else:
                                    await modalinteract.response.send_message("Ник бота изменен!", ephemeral=True)
                        await viewinteract.response.send_modal(Input())
                    
                    @discord.ui.button(label="Начать печатать", style=discord.ButtonStyle.green)
                    async def starttyping(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - печатание"):
                            ans = discord.ui.TextInput(label="Кол-во секунд", max_length=4)
                            async def on_submit(self, modalinteract: discord.Interaction):
                                await modalinteract.response.send_message(f"Начинаем печатать {str(self.ans)} секунд...", ephemeral=True)
                                async with modalinteract.channel.typing():
                                    await sleep(int(str(self.ans)))
                        await viewinteract.response.send_modal(Input())

                    @discord.ui.button(label="Выполнить команду", style=discord.ButtonStyle.green, disabled=not(ctx.author.id == settings['owner_id']))
                    async def sudo(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - выполнение команды"):
                            ans = discord.ui.TextInput(label="Команда:", style=discord.TextStyle.long)
                            async def on_submit(self, modalinteract: discord.Interaction):
                                try:
                                    exec(str(self.ans))
                                except Exception as e:
                                    return await modalinteract.response.send_message(f"```\n{e}```", ephemeral=True)
                                await modalinteract.response.send_message("Команда выполнена!", ephemeral=True)
                        await viewinteract.response.send_modal(Input())
                    
                    @discord.ui.button(label="Перезапустить", style=discord.ButtonStyle.green)
                    async def restart(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        await viewinteract.response.send_message("Перезапускаемся...", ephemeral=True)
                        print(f"{viewinteract.user} инициировал перезагрузку!")
                        await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="Перезагрузка..."))
                        await sleep(2)
                        os.execv(sys.executable, ['python'] + sys.argv)
                    
                    @discord.ui.button(label="Выключить", style=discord.ButtonStyle.danger, disabled=not(ctx.author.id == settings['owner_id']))
                    async def stop(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        await viewinteract.response.send_message("Выключение...", ephemeral=True)
                        await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="Выключение..."))
                        await sleep(2)
                        quit()
                    
                    @discord.ui.button(label="Отключить команду", style=discord.ButtonStyle.red)
                    async def offcmd(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - отключение команды"):
                            ans = discord.ui.TextInput(label="Команда:", max_length=32)
                            async def on_submit(self, modalinteract: discord.Interaction):
                                shutted_down.append(str(self.ans))
                                await modalinteract.response.send_message(f"Команда `{str(self.ans)}` отключена!", ephemeral=True)
                        await viewinteract.response.send_modal(Input())

                    @discord.ui.button(label="Включить команду", style=discord.ButtonStyle.red)
                    async def oncmd(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - включение команды"):
                            ans = discord.ui.TextInput(label="Команда:", max_length=32)
                            async def on_submit(self, modalinteract: discord.Interaction):
                                try:
                                    shutted_down.remove(str(self.ans))
                                except:
                                    return await modalinteract.response.send_message(f"Команда `{str(self.ans)}` не была отключена!", ephemeral=True)
                                await modalinteract.response.send_message(f"Команда `{str(self.ans)}` включена!", ephemeral=True)
                        await viewinteract.response.send_modal(Input())
                    
                    @discord.ui.button(label="Перезагрузка когов", style=discord.ButtonStyle.red)
                    async def reloadcogs(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        for ext in cogs:
                            try:
                                await bot.reload_extension(ext)
                            except Exception as e:
                                print(f"Не удалось перезагрузить {ext}!\n{e}")
                        await bot.tree.sync()
                        await viewinteract.response.send_message("Коги перезапущены!", ephemeral=True)
                    
                    @discord.ui.button(label="Загрузка кога", style=discord.ButtonStyle.red)
                    async def loadcog(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        class Input(discord.ui.Modal, title="Debug - загрузка кога"):
                            ans = discord.ui.TextInput(label="Название кога:", max_length=64, placeholder="tools")
                            async def on_submit(self, modalinteract: discord.Interaction):
                                try:
                                    await bot.load_extension(f'cogs.{str(self.ans)}')
                                except Exception as e:
                                    return await modalinteract.response.send_message(f"```\n{e}```", ephemeral=True)
                                await bot.tree.sync()
                                await modalinteract.response.send_message(f"Ког {str(self.ans)} загружен!", ephemeral=True)
                        await viewinteract.response.send_modal(Input())
                    
                    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.blurple)
                    async def nextpage(self, viewinteract: discord.Interaction, button: discord.ui.Button):
                        await viewinteract.response.edit_message(view=self.Page2())

                embed = discord.Embed(
                    title="Панель:", 
                    color=discord.Color.orange(),
                    description="Отключенные кнопки вам недоступны, однако доступны для владельца. Наслаждайтесь!"
                )
                await interaction.response.send_message(embed=embed, view=Page1(), ephemeral=True)
                await ctx.message.delete()
                view.stop()
            
            @discord.ui.button(label="Отмена", style=discord.ButtonStyle.red, emoji="<:x_icon:975324570741526568>")
            async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                await ctx.message.delete()
                view.stop()

        view = Button()
        message = await ctx.reply("Для показа панели нажмите на кнопку.", view=view)
        await view.wait()
        await message.delete()
    elif not (ctx.author.id in blacklist):
        embed = discord.Embed(title="Попытка использования debug-команды!", color=discord.Color.red())
        embed.add_field(name="Пользователь:", value=f'{ctx.author.mention} (`{ctx.author}`)')
        channel = bot.get_channel(settings['log_channel'])
        await channel.send(embed=embed)


print("Подключение к Discord...")
bot.run(settings['token'])
