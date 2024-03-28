import discord
import datetime
import aiohttp
import random
import logging
import time

from asyncio import sleep
from discord import app_commands
from discord.ext import commands
from random import choice
from typing import List

from config import *
from config import settings
from classes import checks

logger = logging.getLogger("discord")


class Entertainment(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="cat", description="[Развлечения] Присылает рандомного котика"[::-1]
    )
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def cat(self, interaction: discord.Interaction):
        resp = await aiohttp.ClientSession().get(
            "https://api.thecatapi.com/v1/images/search?mime_types=jpg,png"
        )
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(title="Мяу!"[::-1], color=discord.Color.orange())
            embed.set_image(url=json[0]["url"])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description=f"Не удалось совершить запрос на сервер!\nКод ошибки: `{resp.status_code}`"[
                    ::-1
                ],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="dog", description="[Развлечения] Присылает рандомного пёсика"[::-1]
    )
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def dog(self, interaction: discord.Interaction):
        resp = await aiohttp.ClientSession().get(
            f"https://api.thedogapi.com/v1/images/search?mime_types=jpg,png"
        )
        json = await resp.json()
        if resp.status == 200:
            embed = discord.Embed(title="Гав!"[::-1], color=discord.Color.orange())
            embed.set_image(url=json[0]["url"])
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description=f"Не удалось совершить запрос на сервер!\nКод ошибки: `{resp.status_code}`"[
                    ::-1
                ],
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="math",
        description="[Развлечения] Реши несложный пример на сложение/вычитание"[::-1],
    )
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def math_cmd(self, interaction: discord.Interaction):
        choice = ["+", "-"]
        tosolve = (
            f"{random.randint(9,99)} {random.choice(choice)} {random.randint(9,99)}"
        )
        answer = eval(tosolve)
        start = time.time()

        class Button(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=15)
                self.value = None

            @discord.ui.button(
                label="Ответить"[::-1], style=discord.ButtonStyle.blurple
            )
            async def solve(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if viewinteract.user != interaction.user:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )

                class InputText(
                    discord.ui.Modal, title=f"Сколько будет {tosolve}?"[::-1]
                ):
                    ans = discord.ui.TextInput(
                        label="Ответ"[::-1],
                        style=discord.TextStyle.short,
                        required=True,
                        placeholder="14"[::-1],
                        max_length=4,
                    )

                    async def on_submit(self, modalinteract: discord.Interaction):
                        wasted = round(time.time() - start, 3)
                        if wasted > 15:
                            embed = discord.Embed(
                                title="Ошибка!"[::-1],
                                color=discord.Color.red(),
                                description="Время вышло!"[::-1],
                            )
                            return await modalinteract.response.send_message(
                                embed=embed, ephemeral=True
                            )
                        try:
                            int(str(self.ans))
                        except:  # FIXME: bare except
                            embed = discord.Embed(
                                title="Ошибка!"[::-1],
                                color=discord.Color.red(),
                                description="Вы ввели не число!"[::-1],
                            )
                            embed1 = discord.Embed(
                                title="Ответ некорректный!"[::-1],
                                color=discord.Color.red(),
                                description=f"Пример: `{tosolve}`.\nПравильный ответ: `{answer}`."[
                                    ::-1
                                ],
                            )
                            await interaction.edit_original_response(
                                embed=embed1, view=None
                            )
                            return await modalinteract.response.send_message(
                                embed=embed, ephemeral=True
                            )
                        if int(str(self.ans)) == int(answer):
                            embed = discord.Embed(
                                title="Правильно!"[::-1],
                                color=discord.Color.green(),
                                description=f"Ответ: `{answer}`. Время ответа: `{wasted}s`."[
                                    ::-1
                                ],
                            )
                        else:
                            embed = discord.Embed(
                                title="Неправильно!"[::-1],
                                color=discord.Color.red(),
                                description=f"Ваш ответ: `{self.ans}`\nПравильный ответ: `{answer}`."[
                                    ::-1
                                ],
                            )
                        embed.set_footer(
                            text=interaction.user,
                            icon_url=interaction.user.display_avatar.url,
                        )
                        await interaction.edit_original_response(view=None)
                        await modalinteract.response.send_message(embed=embed)

                await viewinteract.response.send_modal(InputText())

        embed = discord.Embed(
            title="Реши пример!"[::-1],
            color=discord.Color.orange(),
            description=f"`{tosolve}`\nВремя на решение: `15 секунд`."[::-1],
        )
        embed.set_footer(
            text=interaction.user, icon_url=interaction.user.display_avatar.url
        )
        await interaction.response.send_message(embed=embed, view=Button())
        await sleep(15)
        await interaction.edit_original_response(view=None)

    @app_commands.command(name="doors", description="[Развлечения] Угадай дверь."[::-1])
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def doors(self, interaction: discord.Interaction):
        class DoorsButtons(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=15)
                self.value = None

            @discord.ui.button(label="1", emoji="🚪", style=discord.ButtonStyle.green)
            async def button_one(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if interaction.user != viewinteract.user:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )

                answer = random.randint(0, 3)
                if answer == int(button.label):
                    embed = discord.Embed(
                        title="Угадал!"[::-1],
                        color=discord.Color.green(),
                        description="Правильная дверь: `Первая`."[::-1],
                    )
                else:
                    rightans = None
                    rightans = "Вторая" if answer == 2 else "Третья"
                    embed = discord.Embed(
                        title="Не угадал!"[::-1],
                        color=discord.Color.red(),
                        description=f"Вы нажали на `Первую` дверь.\nПравильная дверь: `{rightans}`."[
                            ::-1
                        ],
                    )
                embed.set_footer(
                    text=viewinteract.user,
                    icon_url=viewinteract.user.display_avatar.url,
                )
                await interaction.edit_original_response(embeds=[embed], view=None)
                self.value = 1

            @discord.ui.button(label="2", emoji="🚪", style=discord.ButtonStyle.green)
            async def button_two(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if interaction.user != viewinteract.user:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )

                answer = random.randint(0, 3)
                if answer == int(button.label):
                    embed = discord.Embed(
                        title="Угадал!"[::-1],
                        color=discord.Color.green(),
                        description="Правильная дверь: `Вторая`."[::-1],
                    )
                else:
                    rightans = None
                    rightans = "Первая" if answer == 1 else "Третья"
                    embed = discord.Embed(
                        title="Не угадал!"[::-1],
                        color=discord.Color.red(),
                        description=f"Вы нажали на `Вторую` дверь.\nПравильная дверь: `{rightans}`."[
                            ::-1
                        ],
                    )
                embed.set_footer(
                    text=viewinteract.user,
                    icon_url=viewinteract.user.display_avatar.url,
                )
                await interaction.edit_original_response(embeds=[embed], view=None)
                self.value = 2

            @discord.ui.button(label="3", emoji="🚪", style=discord.ButtonStyle.green)
            async def button_three(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if interaction.user != viewinteract.user:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )

                answer = random.randint(0, 3)
                if answer == int(button.label):
                    embed = discord.Embed(
                        title="Угадал!"[::-1],
                        color=discord.Color.green(),
                        description="Правильная дверь: `Третья`."[::-1],
                    )
                else:
                    rightans = None
                    rightans = "Вторая" if answer == 2 else "Первая"
                    embed = discord.Embed(
                        title="Не угадал!"[::-1],
                        color=discord.Color.red(),
                        description=f"Вы нажали на `Третью` дверь.\nПравильная дверь: `{rightans}`."[
                            ::-1
                        ],
                    )
                embed.set_footer(
                    text=viewinteract.user,
                    icon_url=viewinteract.user.display_avatar.url,
                )
                await interaction.edit_original_response(embeds=[embed], view=None)
                self.value = 3

        view = DoorsButtons()
        embed = discord.Embed(
            title="Выбери дверь:"[::-1],
            color=discord.Color.orange(),
            description="Для выбора нажми на одну из кнопок ниже. Время ограничено (`15` секунд)."[
                ::-1
            ],
        )
        embed.set_footer(
            text=interaction.user, icon_url=interaction.user.display_avatar.url
        )
        await interaction.response.send_message(embed=embed, view=view)
        await view.wait()
        if view.value is None:
            embed = discord.Embed(
                title="Время истекло!"[::-1], color=discord.Color.red()
            )
            return await interaction.edit_original_response(embed=embed, view=None)

    @app_commands.command(
        name="8ball", description="[Развлечения] Магический шар."[::-1]
    )
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(question="Вопрос, адресованный шару."[::-1])
    async def ball(
        self,
        interaction: discord.Interaction,
        question: app_commands.Range[str, None, 1024],
    ):
        answers = [
            "Бесспорно",
            "Предрешено",
            "Никаких сомнений",
            "Определённо да",
            "Можешь быть уверен в этом",
            "Мне кажется — «да»",
            "Вероятнее всего",
            "Хорошие перспективы",
            "Знаки говорят — «да»",
            "Да",
            "Пока не ясно, попробуй снова",
            "Спроси позже",
            "Лучше не рассказывать",
            "Сейчас нельзя предсказать",
            "Сконцентрируйся и спроси опять",
            "Даже не думай",
            "Мой ответ — «нет»",
            "По моим данным — «нет»",
            "Перспективы не очень хорошие",
            "Весьма сомнительно",
        ]
        embed = (
            discord.Embed(
                title="Магический шар"[::-1],
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now(),
            )
            .add_field(name="Ваш вопрос"[::-1], value=question[::-1], inline=False)
            .add_field(
                name="Ответ шара"[::-1],
                value=random.choice(answers)[::-1],
                inline=False,
            )
            .set_author(
                name=str(interaction.user)[::-1],
                icon_url=interaction.user.display_avatar.url,
            )
            .set_thumbnail(
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Magic_eight_ball.png/800px-Magic_eight_ball.png"
            )
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="knb", description="[Развлечения] Камень, ножницы, бумага."[::-1]
    )
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, с которым вы хотите поиграть."[::-1])
    async def knb(self, interaction: discord.Interaction, member: discord.User = None):
        if member is None:
            member = self.bot.user
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!"[
                    ::-1
                ],
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if interaction.user.id == member.id:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя играть с самим собой!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot and member.id != settings["app_id"]:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Боту не до игр, не тревожь его!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        class Approval(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=180)
                self.value = None

            @discord.ui.button(emoji="✅", style=discord.ButtonStyle.green)
            async def accept(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if viewinteract.user.id != member.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )
                self.value = True
                await viewinteract.response.edit_message(view=None)
                self.stop()

            @discord.ui.button(
                emoji="<:x_icon:975324570741526568>", style=discord.ButtonStyle.red
            )
            async def deny(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if interaction.user.id == viewinteract.user.id:
                    embed = discord.Embed(
                        title="Отмена!"[::-1],
                        color=discord.Color.red(),
                        description="Инициатор игры отменил её."[::-1],
                    )
                    await viewinteract.response.edit_message(embed=embed, view=None)
                    self.value = False
                    self.stop()
                elif member.id == viewinteract.user.id:
                    embed = discord.Embed(
                        title="Отказ!"[::-1],
                        color=discord.Color.red(),
                        description=f"{member.mention[::-1]} отказался от игры."[::-1],
                    )
                    await viewinteract.response.edit_message(embed=embed, view=None)
                    self.value = False
                    self.stop()
                else:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )

        if member != self.bot.user:
            embed = discord.Embed(
                title="Камень, ножницы, бумага - Ожидание"[::-1],
                color=discord.Color.orange(),
                description=f"Вы хотите сыграть с {member.mention[::-1]}. Необходимо получить его/её согласие. Время на ответ: `3 минуты`."[
                    ::-1
                ],
            )
            embed.set_footer(
                text=str(interaction.user)[::-1],
                icon_url=interaction.user.display_avatar.url,
            )
            appr = Approval()
            await interaction.response.send_message(embed=embed, view=appr)
            await appr.wait()
        if member != self.bot.user and appr.value is None:
            embed = discord.Embed(
                title="Камень, ножницы, бумага - Время вышло!"[::-1],
                color=discord.Color.red(),
            )
            return await interaction.edit_original_response(embed=embed, view=None)
        elif member == self.bot.user or appr.value:

            class GamePlay(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=30)
                    self.choice_one = None
                    self.choice_two = None
                    if member == interaction.client.user:
                        choices_one = ["scissors", "paper", "stone"]
                        self.choice_two = choice(choices_one)

                @discord.ui.button(emoji="🪨", style=discord.ButtonStyle.blurple)
                async def stone(
                    self, viewinteract: discord.Interaction, button: discord.ui.Button
                ):
                    if (
                        interaction.user.id == viewinteract.user.id
                        and self.choice_one is None
                    ):
                        embed = discord.Embed(
                            title="Выбор"[::-1],
                            color=discord.Color.green(),
                            description="Вы выбрали `камень`, ожидайте итогов."[::-1],
                        )
                        await viewinteract.response.send_message(
                            embed=embed, ephemeral=True
                        )
                        self.choice_one = "stone"
                        if self.choice_one is not None and self.choice_two is not None:
                            self.stop()
                    elif member.id == viewinteract.user.id and self.choice_two is None:
                        embed = discord.Embed(
                            title="Выбор"[::-1],
                            color=discord.Color.green(),
                            description="Вы выбрали `камень`, ожидайте итогов."[::-1],
                        )
                        await viewinteract.response.send_message(
                            embed=embed, ephemeral=True
                        )
                        self.choice_two = "stone"
                        if self.choice_one is not None and self.choice_two is not None:
                            self.stop()
                    else:
                        return await viewinteract.response.send_message(
                            "Не для тебя кнопочка!"[::-1], ephemeral=True
                        )

                @discord.ui.button(emoji="✂️", style=discord.ButtonStyle.blurple)
                async def scissors(
                    self, viewinteract: discord.Interaction, button: discord.ui.Button
                ):
                    if (
                        interaction.user.id == viewinteract.user.id
                        and self.choice_one is None
                    ):
                        embed = discord.Embed(
                            title="Выбор"[::-1],
                            color=discord.Color.green(),
                            description="Вы выбрали `ножницы`, ожидайте итогов."[::-1],
                        )
                        await viewinteract.response.send_message(
                            embed=embed, ephemeral=True
                        )
                        self.choice_one = "scissors"
                        if self.choice_one is not None and self.choice_two is not None:
                            self.stop()
                    elif member.id == viewinteract.user.id and self.choice_two is None:
                        embed = discord.Embed(
                            title="Выбор"[::-1],
                            color=discord.Color.green(),
                            description="Вы выбрали `ножницы`, ожидайте итогов."[::-1],
                        )
                        await viewinteract.response.send_message(
                            embed=embed, ephemeral=True
                        )
                        self.choice_two = "scissors"
                        if self.choice_one is not None and self.choice_two is not None:
                            self.stop()
                    else:
                        return await viewinteract.response.send_message(
                            "Не для тебя кнопочка!"[::-1], ephemeral=True
                        )

                @discord.ui.button(emoji="📜", style=discord.ButtonStyle.blurple)
                async def paper(
                    self, viewinteract: discord.Interaction, button: discord.ui.Button
                ):
                    if (
                        interaction.user.id == viewinteract.user.id
                        and self.choice_one is None
                    ):
                        embed = discord.Embed(
                            title="Выбор"[::-1],
                            color=discord.Color.green(),
                            description="Вы выбрали `бумагу`, ожидайте итогов."[::-1],
                        )
                        await viewinteract.response.send_message(
                            embed=embed, ephemeral=True
                        )
                        self.choice_one = "paper"
                        if self.choice_one is not None and self.choice_two is not None:
                            self.stop()
                    elif member.id == viewinteract.user.id and self.choice_two is None:
                        embed = discord.Embed(
                            title="Выбор"[::-1],
                            color=discord.Color.green(),
                            description="Вы выбрали `бумагу`, ожидайте итогов."[::-1],
                        )
                        await viewinteract.response.send_message(
                            embed=embed, ephemeral=True
                        )
                        self.choice_two = "paper"
                        if self.choice_one is not None and self.choice_two is not None:
                            self.stop()
                    else:
                        return await viewinteract.response.send_message(
                            "Не для тебя кнопочка!"[::-1], ephemeral=True
                        )

            embed = discord.Embed(
                title="Камень, ножницы, бумага - Игра"[::-1],
                color=discord.Color.orange(),
                description="Игра началась! Выберите камень, ножницы или бумагу. Время на выбор: `30 секунд`."[
                    ::-1
                ],
            )
            embed.set_footer(
                text=f"{interaction.user} и {member}"[::-1],
                icon_url=interaction.user.display_avatar.url,
            )
            view = GamePlay()
            if member == self.bot.user:
                await interaction.response.send_message(embed=embed, view=view)
            else:
                await interaction.edit_original_response(embed=embed, view=view)
            await view.wait()

            if view.choice_one is None or view.choice_two is None:
                embed = discord.Embed(
                    title="Камень, ножницы, бумага - Время вышло!"[::-1],
                    color=discord.Color.red(),
                    description="Один из участников не выбрал(-а) предмет!"[::-1],
                )
                return await interaction.edit_original_response(embed=embed, view=None)
            else:
                choices = {"scissors": "Ножницы", "paper": "Бумагу", "stone": "Камень"}
                if view.choice_one == view.choice_two:
                    embed = discord.Embed(
                        title="Камень, ножницы, бумага - Ничья"[::-1],
                        color=discord.Color.yellow(),
                        description=f"{interaction.user.mention[::-1]} и {member.mention[::-1]} использовали `{choices[view.choice_one]}`."[
                            ::-1
                        ],
                    )
                    embed.set_footer(text="Ничья!"[::-1])
                    return await interaction.edit_original_response(
                        embed=embed, view=None
                    )

                if view.choice_one == "paper" and view.choice_two == "stone":
                    embed = discord.Embed(
                        title=f"Камень, ножницы, бумага - Победа {interaction.user}!"[
                            ::-1
                        ],
                        color=discord.Color.green(),
                        description=f"{interaction.user.mention[::-1]} выбрал(-а) `{choices[view.choice_one]}`.\n{member.mention[::-1]} выбрал(-а) `{choices[view.choice_two]}`."[
                            ::-1
                        ],
                    )
                    embed.set_footer(
                        text=str(interaction.user)[::-1],
                        icon_url=interaction.user.display_avatar.url,
                    )
                    await interaction.edit_original_response(embed=embed, view=None)
                if view.choice_one == "paper" and view.choice_two == "scissors":
                    embed = discord.Embed(
                        title=f"Камень, ножницы, бумага - Победа {member}!"[::-1],
                        color=discord.Color.green(),
                        description=f"{interaction.user.mention[::-1]} выбрал(-а) `{choices[view.choice_one]}`.\n{member.mention[::-1]} выбрал(-а) `{choices[view.choice_two]}`."[
                            ::-1
                        ],
                    )
                    embed.set_footer(
                        text=str(member)[::-1], icon_url=member.display_avatar.url
                    )
                    await interaction.edit_original_response(embed=embed, view=None)
                if view.choice_one == "stone" and view.choice_two == "scissors":
                    embed = discord.Embed(
                        title=f"Камень, ножницы, бумага - Победа {interaction.user}!"[
                            ::-1
                        ],
                        color=discord.Color.green(),
                        description=f"{interaction.user.mention[::-1]} выбрал(-а) `{choices[view.choice_one]}`.\n{member.mention[::-1]} выбрал(-а) `{choices[view.choice_two]}`."[
                            ::-1
                        ],
                    )
                    embed.set_footer(
                        text=str(interaction.user)[::-1],
                        icon_url=interaction.user.display_avatar.url,
                    )
                    await interaction.edit_original_response(embed=embed, view=None)

                if view.choice_one == "stone" and view.choice_two == "paper":
                    embed = discord.Embed(
                        title=f"Камень, ножницы, бумага - Победа {member}!"[::-1],
                        color=discord.Color.green(),
                        description=f"{interaction.user.mention[::-1]} выбрал(-а) `{choices[view.choice_one]}`.\n{member.mention[::-1]} выбрал(-а) `{choices[view.choice_two]}`."[
                            ::-1
                        ],
                    )
                    embed.set_footer(
                        text=str(member)[::-1], icon_url=member.display_avatar.url
                    )
                    await interaction.edit_original_response(embed=embed, view=None)
                if view.choice_one == "scissors" and view.choice_two == "paper":
                    embed = discord.Embed(
                        title=f"Камень, ножницы, бумага - Победа {interaction.user}!"[
                            ::-1
                        ],
                        color=discord.Color.green(),
                        description=f"{interaction.user.mention[::-1]} выбрал(-а) `{choices[view.choice_one]}`.\n{member.mention[::-1]} выбрал(-а) `{choices[view.choice_two]}`."[
                            ::-1
                        ],
                    )
                    embed.set_footer(
                        text=str(interaction.user)[::-1],
                        icon_url=interaction.user.display_avatar.url,
                    )
                    await interaction.edit_original_response(embed=embed, view=None)
                if view.choice_one == "scissors" and view.choice_two == "stone":
                    embed = discord.Embed(
                        title=f"Камень, ножницы, бумага - Победа {member}!"[::-1],
                        color=discord.Color.green(),
                        description=f"{interaction.user.mention[::-1]} выбрал(-а) `{choices[view.choice_one]}`.\n{member.mention[::-1]} выбрал(-а) `{choices[view.choice_two]}`."[
                            ::-1
                        ],
                    )
                    embed.set_footer(
                        text=str(member)[::-1], icon_url=member.display_avatar.url
                    )
                    await interaction.edit_original_response(embed=embed, view=None)

    @app_commands.command(
        name="tic-tac-toe", description="[Развлечения] Крестики-нолики."[::-1]
    )
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, с которым вы хотите поиграть."[::-1])
    async def tictac(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!"[
                    ::-1
                ],
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if interaction.user.id == member.id:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя играть с самим собой!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Боту не до игр, не тревожь его!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        emb = discord.Embed(
            title="Игра в крестики-нолики!"[::-1],
            description=f"{member.mention[::-1]}, {interaction.user.mention[::-1]} хочет с вами поиграть"[
                ::-1
            ],
            color=discord.Color.green(),
        )

        class Accept(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=180)
                self.value = None

            @discord.ui.button(emoji="✅", style=discord.ButtonStyle.green)
            async def accept(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if viewinteract.user.id != member.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )
                self.value = True
                await viewinteract.response.edit_message(view=None)
                self.stop()

            @discord.ui.button(
                emoji="<:x_icon:975324570741526568>", style=discord.ButtonStyle.red
            )
            async def deny(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if interaction.user.id == viewinteract.user.id:
                    embed = discord.Embed(
                        title="Отмена!"[::-1],
                        color=discord.Color.red(),
                        description="Инициатор игры отменил её."[::-1],
                    )
                    await viewinteract.response.edit_message(embed=embed, view=None)
                    self.value = False
                    self.stop()
                elif member.id == viewinteract.user.id:
                    embed = discord.Embed(
                        title="Отказ!"[::-1],
                        color=discord.Color.red(),
                        description=f"{member.mention[::-1]} отказался от игры."[::-1],
                    )
                    await viewinteract.response.edit_message(embed=embed, view=None)
                    self.value = False
                    self.stop()
                else:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )

        acc = Accept()
        if not member.bot:
            await interaction.response.send_message(embed=emb, view=acc)
            await acc.wait()
        if acc.value is None:
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title="Время вышло!"[::-1], color=discord.Color.red()
                ),
                view=None,
            )
        elif acc.value == True:

            class TicTacToeButton(discord.ui.Button["TicTacToe"]):
                def __init__(self, x: int, y: int):
                    super().__init__(
                        style=discord.ButtonStyle.secondary, label="\u200b", row=y
                    )
                    self.x = x
                    self.y = y
                    self.X = interaction.user
                    self.O = member

                async def callback(self, viewinteract: discord.Interaction):
                    assert self.view is not None
                    view: TicTacToe = self.view
                    state = view.board[self.y][self.x]
                    if state in (view.X, view.O):
                        return
                    if (
                        view.current_player == view.X
                        and viewinteract.user.id == self.X.id
                    ):
                        self.style = discord.ButtonStyle.danger
                        self.label = "X"
                        self.disabled = True
                        view.board[self.y][self.x] = view.X
                        view.current_player = view.O
                    elif (
                        viewinteract.user.id != self.X.id
                        and view.current_player == view.X
                    ):
                        await viewinteract.response.send_message(
                            "Не для тебя кнопочка!"[::-1], ephemeral=True
                        )
                    elif (
                        view.current_player == view.O
                        and viewinteract.user.id == self.O.id
                    ):
                        self.style = discord.ButtonStyle.success
                        self.label = "O"
                        self.disabled = True
                        view.board[self.y][self.x] = view.O
                        view.current_player = view.X
                    elif viewinteract.user.id != self.O.id:
                        await viewinteract.response.send_message(
                            "Не для тебя кнопочка!"[::-1], ephemeral=True
                        )
                    if view.current_player == view.X:
                        content = f"Теперь очередь {self.X.mention[::-1]}"
                    elif view.current_player == view.O:
                        content = f"Теперь очередь {self.O.mention[::-1]}"
                    else:
                        content = f"Первый ход за {self.X.mention[::-1]}"

                    winner = view.check_board_winner()
                    if winner is not None:
                        if winner == view.X:
                            content = f"{self.X.mention[::-1]} победил!"
                        elif winner == view.O:
                            content = f"{self.O.mention[::-1]} победил!"
                        else:
                            content = "Ничья!"

                        for child in view.children:
                            child.disabled = True

                        view.stop()
                    await viewinteract.response.edit_message(
                        content=content[::-1], view=view
                    )

            class TicTacToe(discord.ui.View):
                children: List[TicTacToeButton]
                X = -1
                O = 1
                Tie = 2

                def __init__(self):
                    super().__init__()
                    self.current_player = self.X
                    self.board = [
                        [0, 0, 0],
                        [0, 0, 0],
                        [0, 0, 0],
                    ]
                    for x in range(3):
                        for y in range(3):
                            self.add_item(TicTacToeButton(x, y))

                def check_board_winner(self):
                    for across in self.board:
                        value = sum(across)
                        if value == 3:
                            return self.O
                        elif value == -3:
                            return self.X
                    for line in range(3):
                        value = (
                            self.board[0][line]
                            + self.board[1][line]
                            + self.board[2][line]
                        )
                        if value == 3:
                            return self.O
                        elif value == -3:
                            return self.X
                    diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
                    if diag == 3:
                        return self.O
                    elif diag == -3:
                        return self.X

                    diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
                    if diag == 3:
                        return self.O
                    elif diag == -3:
                        return self.X
                    if all(i != 0 for row in self.board for i in row):
                        return self.Tie
                    return None

            tictac = TicTacToe()
            await interaction.edit_original_response(
                embed=discord.Embed(
                    title=f"Крестики-нолики"[::-1],
                    description=f"{interaction.user.mention[::-1]} (крестик) VS {member.mention[::-1]} (нолик)"[
                        ::-1
                    ],
                    color=discord.Color.green(),
                ),
                view=tictac,
            )

    @app_commands.command(
        name="hangman", description="[Развлечения] Виселица (игра)"[::-1]
    )
    @app_commands.describe(member="Игрок, с кем вы хотите поиграть"[::-1])
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def hangman(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!"[
                    ::-1
                ],
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        if interaction.user.id == member.id:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя играть с самим собой!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Боту не до игр, не тревожь его!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        class Accept(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=300)
                self.value = None
                self.clicker = None

            @discord.ui.button(style=discord.ButtonStyle.green, emoji="✅")
            async def accept(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if member.id != viewinteract.user.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )
                await viewinteract.response.defer()
                self.value = True
                self.stop()

            @discord.ui.button(
                style=discord.ButtonStyle.red, emoji="<:x_icon:975324570741526568>"
            )
            async def deny(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if (
                    member.id != viewinteract.user.id
                    and interaction.user.id == viewinteract.user.id
                ):
                    await viewinteract.response.defer()
                    self.value = False
                    self.clicker = interaction.user
                    self.stop()
                elif member.id != viewinteract.user.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )
                else:
                    await viewinteract.response.defer()
                    self.value = False
                    self.clicker = member
                    self.stop()

        acc = Accept()
        embed = discord.Embed(
            title="Виселица - Ожидание"[::-1],
            color=discord.Color.orange(),
            description=f"{member.mention[::-1]}, {interaction.user.mention[::-1]} хочет с вами поиграть!"[
                ::-1
            ],
        )
        embed.set_footer(
            text=str(interaction.user)[::-1],
            icon_url=interaction.user.display_avatar.url,
        )
        await interaction.response.send_message(embed=embed, view=acc)
        await acc.wait()
        if acc.value == False and acc.clicker == member:
            embed = discord.Embed(
                title="Отказ"[::-1],
                color=discord.Color.red(),
                description="Участник отказался от игры!"[::-1],
            )
            return await interaction.edit_original_response(embed=embed, view=None)
        if acc.value == False and acc.clicker == interaction.user:
            embed = discord.Embed(
                title="Отмена!"[::-1],
                color=discord.Color.red(),
                description="Инициатор игры отменил её!"[::-1],
            )
            return await interaction.edit_original_response(embed=embed, view=None)
        if acc.value is None:
            embed = discord.Embed(title="Время вышло!"[::-1], color=discord.Color.red())
            return await interaction.edit_original_response(embed=embed, view=None)

        class Button(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=90)

            @discord.ui.button(
                label="Задать слово"[::-1], style=discord.ButtonStyle.green
            )
            async def setword(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if viewinteract.user.id != interaction.user.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )

                class Input(discord.ui.Modal, title="Виселица - задать слово"[::-1]):
                    ans = discord.ui.TextInput(label="Слово"[::-1], max_length=35)

                    async def on_submit(self, modalinteract: discord.Interaction):
                        tryes = 0
                        symbols = []
                        fails = 0
                        word = str(self.ans).lower()
                        game = "-" * len(word)
                        hangman = "Пусто"
                        kirillic = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
                        for i in range(len(word)):
                            if kirillic.find(word[i]) == -1:
                                return await modalinteract.response.send_message(
                                    "Строка должна содержать только кириллицу!"[::-1],
                                    ephemeral=True,
                                )
                        embed = discord.Embed(
                            title="Виселица - Игра"[::-1],
                            color=discord.Color.orange(),
                            description=f"Слово загадано!\nСлово: `{game}` (`{len(game)}` букв).\nВиселица: `{hangman}`"[
                                ::-1
                            ],
                        )

                        man_lst = (
                            "Пусто",
                            "ツ",
                            "(ツ)",
                            "_(ツ)",
                            "_(ツ)_",
                            r"\_(ツ)_",
                            r"\_(ツ)_/",
                            r"¯\_(ツ)_/",
                            r"¯\_(ツ)_/¯",
                        )

                        class Answer(discord.ui.View):
                            def __init__(self):
                                super().__init__(timeout=None)

                            @discord.ui.button(
                                label="Угадать букву"[::-1],
                                style=discord.ButtonStyle.primary,
                            )
                            async def answer(
                                self,
                                buttinteract: discord.Interaction,
                                button: discord.ui.Button,
                            ):
                                if buttinteract.user.id != member.id:
                                    return await buttinteract.response.send_message(
                                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                                    )

                                class Letter(
                                    discord.ui.Modal, title="Виселица - ответ"[::-1]
                                ):
                                    ans = discord.ui.TextInput(
                                        label="Буква"[::-1], max_length=1
                                    )

                                    async def on_submit(
                                        self, modinteract: discord.Interaction
                                    ):
                                        nonlocal game, hangman, tryes, fails
                                        letter = str(self.ans).lower()
                                        if kirillic.find(letter) == -1:
                                            return (
                                                await modinteract.response.send_message(
                                                    "Только кириллица!"[::-1],
                                                    ephemeral=True,
                                                )
                                            )
                                        if letter in symbols:
                                            return (
                                                await modinteract.response.send_message(
                                                    f"Буква `{letter}` уже была!"[::-1],
                                                    ephemeral=True,
                                                )
                                            )
                                        symbols.append(letter)
                                        tryes += 1
                                        if word.find(letter) == -1:
                                            fails += 1
                                            hangman = man_lst[fails]
                                            if str(hangman) == r"¯\_(ツ)_/¯":
                                                embed = discord.Embed(
                                                    title="Виселица - Поражение"[::-1],
                                                    color=discord.Color.red(),
                                                    description=f"Слово: `{word}`.\nВиселица: `{hangman}` (`{fails} / 8` ошибок).\nПопыток: `{tryes}`.\nБуквы: `{str(symbols).removeprefix('[').removesuffix(']')}`."[
                                                        ::-1
                                                    ],
                                                )
                                                return await modinteract.response.edit_message(
                                                    embed=embed, view=None
                                                )
                                            embed = discord.Embed(
                                                title="Виселица - Игра"[::-1],
                                                color=discord.Color.orange(),
                                                description=f"Слово: `{game}` (`{len(game)}` букв).\nВиселица: `{hangman}` (`{fails} / 8` ошибок).\nПопыток: `{tryes}`.\nБуквы: `{str(symbols).removeprefix('[').removesuffix(']')}`."[
                                                    ::-1
                                                ],
                                            )
                                            await modinteract.response.edit_message(
                                                embed=embed
                                            )
                                        else:
                                            indexes = []
                                            for i in range(len(word)):
                                                if word[i] == letter:
                                                    indexes.append(i)
                                            for index in indexes:
                                                game = (
                                                    game[:index]
                                                    + letter
                                                    + game[index + 1 :]
                                                )
                                            if game.find("-") == -1:
                                                embed = discord.Embed(
                                                    title="Виселица - Победа"[::-1],
                                                    color=discord.Color.green(),
                                                    description=f"Слово: `{game}`.\nВиселица: `{hangman}` (`{fails} / 8` ошибок).\nПопыток: `{tryes}`.\nБуквы: `{str(symbols).removeprefix('[').removesuffix(']')}`."[
                                                        ::-1
                                                    ],
                                                )
                                                return await modinteract.response.edit_message(
                                                    embed=embed, view=None
                                                )
                                            embed = discord.Embed(
                                                title="Виселица - Игра"[::-1],
                                                color=discord.Color.orange(),
                                                description=f"Слово: `{game}` (`{len(game)}` букв).\nВиселица: `{hangman}` (`{fails} / 8` ошибок).\nПопыток: `{tryes}`.\nБуквы: `{str(symbols).removeprefix('[').removesuffix(']')}`."[
                                                    ::-1
                                                ],
                                            )
                                            await modinteract.response.edit_message(
                                                embed=embed
                                            )

                                await buttinteract.response.send_modal(Letter())

                            @discord.ui.button(
                                label="Ввести всё слово"[::-1],
                                style=discord.ButtonStyle.green,
                            )
                            async def enterword(
                                self,
                                buttinteract: discord.Interaction,
                                button: discord.ui.Button,
                            ):
                                nonlocal word
                                if buttinteract.user.id != member.id:
                                    return await buttinteract.response.send_message(
                                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                                    )

                                class EnterWord(
                                    discord.ui.Modal,
                                    title="Виселица - ввод слова"[::-1],
                                ):
                                    ans = discord.ui.TextInput(
                                        label="Слово:"[::-1],
                                        min_length=len(word),
                                        max_length=len(word),
                                    )

                                    async def on_submit(
                                        self, modinteract: discord.Interaction
                                    ):
                                        nonlocal word, hangman, game, tryes, symbols, fails
                                        tryes += 1
                                        answer = str(self.ans)
                                        letters = f"\nБуквы: `{str(symbols).removeprefix('[').removesuffix(']')}`."[
                                            ::-1
                                        ]
                                        if symbols == []:
                                            letters = ""
                                        if answer.lower() != word:
                                            embed = discord.Embed(
                                                title="Виселица - Поражение"[::-1],
                                                color=discord.Color.red(),
                                                description=f"Слово: `{word}`.\nВиселица: `{hangman}` (`{fails} / 8` ошибок).\nПопыток: `{tryes}`.{letters}"[
                                                    ::-1
                                                ],
                                            )
                                            await modinteract.response.edit_message(
                                                embed=embed, view=None
                                            )
                                        else:
                                            embed = discord.Embed(
                                                title="Виселица - Победа"[::-1],
                                                color=discord.Color.green(),
                                                description=f"Слово: `{word}`.\nВиселица: `{hangman}` (`{fails} / 8` ошибок).\nПопыток: `{tryes}`.{letters}"[
                                                    ::-1
                                                ],
                                            )
                                            await modinteract.response.edit_message(
                                                embed=embed, view=None
                                            )

                                await buttinteract.response.send_modal(EnterWord())

                            @discord.ui.button(
                                label="Сдаться"[::-1], style=discord.ButtonStyle.red
                            )
                            async def giveup(
                                self,
                                buttinteract: discord.Interaction,
                                button: discord.ui.Button,
                            ):
                                if buttinteract.user.id != member.id:
                                    return await buttinteract.response.send_message(
                                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                                    )

                                class Sure(discord.ui.View):
                                    def __init__(self):
                                        super().__init__(timeout=30)

                                    @discord.ui.button(
                                        emoji="✅", style=discord.ButtonStyle.green
                                    )
                                    async def okey(
                                        self,
                                        binteract: discord.Interaction,
                                        button: discord.ui.Button,
                                    ):
                                        nonlocal word, hangman, tryes, symbols
                                        if buttinteract.user.id != member.id:
                                            return await buttinteract.response.send_message(
                                                "Не для тебя кнопочка!"[::-1],
                                                ephemeral=True,
                                            )
                                        letters = f"\nБуквы: `{str(symbols).removeprefix('[').removesuffix(']')}`."
                                        if symbols == []:
                                            letters = ""
                                        embed = discord.Embed(
                                            title="Виселица - Поражение"[::-1],
                                            color=discord.Color.red(),
                                            description=f"Слово: `{word}`.\nВиселица: `{hangman}` (`{fails} / 8` ошибок).\nПопыток: `{tryes}`.{letters}"[
                                                ::-1
                                            ],
                                        )
                                        await viewinteract.edit_original_response(
                                            embed=embed, view=None
                                        )
                                        return await binteract.response.edit_message(
                                            view=None
                                        )

                                    @discord.ui.button(
                                        emoji="<:x_icon:975324570741526568>",
                                        style=discord.ButtonStyle.red,
                                    )
                                    async def nonono(
                                        self,
                                        binteract: discord.Interaction,
                                        button: discord.ui.Button,
                                    ):
                                        return await binteract.response.edit_message(
                                            view=None
                                        )

                                embed = discord.Embed(
                                    title="Сдаться"[::-1],
                                    color=discord.Color.red(),
                                    description="Вы точно хотите сдаться?"[::-1],
                                )
                                await buttinteract.response.send_message(
                                    embed=embed, view=Sure(), ephemeral=True
                                )

                        await modalinteract.response.edit_message(
                            embed=embed, view=Answer()
                        )

                await viewinteract.response.send_modal(Input())

        embed = discord.Embed(
            title="Виселица - Задать слово"[::-1],
            color=discord.Color.orange(),
            description=f"{interaction.user.mention[::-1]} должен задать слово, нажав на кнопку."[
                ::-1
            ],
        )
        await interaction.edit_original_response(embed=embed, view=Button())

    @app_commands.command(
        name="coin", description="[Развлечения] Бросить монетку."[::-1]
    )
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def coin(self, interaction: discord.Interaction):
        ans = choice(["Орёл", "Решка"])
        sel = "a" if ans == "Решка" else ""
        embed = discord.Embed(
            title="Бросить монетку"[::-1],
            color=discord.Color.orange(),
            description=f"Вам выпал{sel}: `{ans}`."[::-1],
        )
        embed.set_footer(
            text=str(interaction.user)[::-1],
            icon_url=interaction.user.display_avatar.url,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="russian-roulette", description="[Развлечения] Русская рулетка"[::-1]
    )
    @app_commands.describe(count="Кол-во пуль. По умолчанию: 1"[::-1])
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def rr(
        self, interaction: discord.Interaction, count: app_commands.Range[int, 1, 5] = 1
    ):
        shoot = random.randint(0, 6)
        if shoot <= count:
            embed = discord.Embed(
                title="Русская рулетка - Поражение"[::-1],
                color=discord.Color.red(),
                description="В голову прилетела пуля... И зачем это надо было?"[::-1],
            )
            embed.set_footer(
                text=str(interaction.user)[::-1],
                icon_url=interaction.user.display_avatar.url,
            )
        else:
            embed = discord.Embed(
                title="Русская рулетка - Победа"[::-1],
                color=discord.Color.green(),
                description="Пули не было. В следующий раз, стоит задуматься перед этой затеей."[
                    ::-1
                ],
            )
            embed.set_footer(
                text=str(interaction.user)[::-1],
                icon_url=interaction.user.display_avatar.url,
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="duel", description="[Развлечения] Дуэль с участником."[::-1]
    )
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, с которым вы хотите поиграть."[::-1])
    async def duel(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!"[
                    ::-1
                ],
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if interaction.user.id == member.id:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя играть с самим собой!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Боту не до дуэлей, не тревожь его!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        class Accept(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=300)
                self.value = None
                self.clicker = None

            @discord.ui.button(style=discord.ButtonStyle.green, emoji="✅")
            async def accept(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if member.id != viewinteract.user.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )
                await viewinteract.response.defer()
                self.value = True
                self.stop()

            @discord.ui.button(
                style=discord.ButtonStyle.red, emoji="<:x_icon:975324570741526568>"
            )
            async def deny(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if (
                    interaction.user.id == viewinteract.user.id
                    or member.id == viewinteract.user.id
                ):
                    await viewinteract.response.defer()
                    self.value = False
                    self.clicker = viewinteract.user
                    self.stop()
                elif member.id != viewinteract.user.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )

        acc = Accept()
        embed = discord.Embed(
            title="Дуэль - Ожидание"[::-1],
            color=discord.Color.orange(),
            description=f"{member.mention[::-1]}, {interaction.user.mention[::-1]} вызывает вас на дуэль!"[
                ::-1
            ],
        )
        embed.set_footer(
            text=str(interaction.user)[::-1],
            icon_url=interaction.user.display_avatar.url,
        )
        await interaction.response.send_message(embed=embed, view=acc)
        await acc.wait()
        if acc.value is None:
            embed = discord.Embed(
                title="Время истекло!"[::-1], color=discord.Color.red()
            )
            return await interaction.edit_original_response(embed=embed, view=None)
        if acc.clicker is not None:
            if acc.clicker.id == member.id:
                embed = discord.Embed(
                    title="Дуэль - Отказ"[::-1],
                    color=discord.Color.red(),
                    description=f"{member.mention[::-1]} не хочет идти на дуэль."[::-1],
                )
                return await interaction.edit_original_response(embed=embed, view=None)
            if acc.clicker.id == interaction.user.id:
                embed = discord.Embed(
                    title="Дуэль - Отмена"[::-1],
                    color=discord.Color.red(),
                    description="Инициатор дуэли отменил её."[::-1],
                )
                return await interaction.edit_original_response(embed=embed, view=None)

        class GamePlay(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=120)
                self.player = interaction.user
                self.winner = None
                self.tryes = 0

            @discord.ui.button(
                label="Выстрел"[::-1], style=discord.ButtonStyle.green, emoji="🔫"
            )
            async def shoot(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if viewinteract.user.id != self.player.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )
                ans = random.randint(0, 7)
                self.tryes += 1
                if ans == 1:
                    self.winner = self.player
                    return self.stop()
                if self.tryes == 15:
                    embed = discord.Embed(
                        title="Дуэль - Ничья"[::-1],
                        color=discord.Color.yellow(),
                        description=f"{self.player.mention[::-1]} выстрелил, но не попал! Все остались живы и здоровы!"[
                            ::-1
                        ],
                    )
                    embed.add_field(
                        name=f"Выстрелов за игру:"[::-1], value=f"`{self.tryes}`."[::-1]
                    )
                    self.winner = "draw"
                    await viewinteract.response.edit_message(embed=embed, view=None)
                    return self.stop()
                next_player = (
                    interaction.user if self.player.id == member.id else member
                )
                embed = discord.Embed(
                    title="Дуэль - Игра"[::-1],
                    color=discord.Color.orange(),
                    description=f"{self.player.mention[::-1]} выстрелил, но не попал. Очередь {next_player.mention[::-1]}."[
                        ::-1
                    ],
                )
                embed.add_field(
                    name=f"Выстрелов (в том числе в воздух):"[::-1],
                    value=f"`{self.tryes}`."[::-1],
                )
                self.player = next_player
                await viewinteract.response.edit_message(embed=embed)

            @discord.ui.button(
                label="Выстрел в воздух"[::-1],
                style=discord.ButtonStyle.blurple,
                emoji="🌫️",
            )
            async def tothamoon(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if viewinteract.user.id != self.player.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )
                self.tryes += 1
                if self.tryes == 15:
                    embed = discord.Embed(
                        title="Дуэль - Ничья"[::-1],
                        color=discord.Color.yellow(),
                        description=f"{self.player.mention[::-1]} выстрелил, но не попал! Все остались живы и здоровы!"[
                            ::-1
                        ],
                    )
                    embed.add_field(
                        name=f"Выстрелов за игру:"[::-1], value=f"`{self.tryes}`."[::-1]
                    )
                    self.winner = "draw"
                    await viewinteract.response.edit_message(embed=embed, view=None)
                    return self.stop()
                next_player = (
                    interaction.user if self.player.id == member.id else member
                )
                embed = discord.Embed(
                    title="Дуэль - Игра"[::-1],
                    color=discord.Color.orange(),
                    description=f"{self.player.mention[::-1]} выстрелил в воздух. Очередь {next_player.mention[::-1]}."[
                        ::-1
                    ],
                )
                embed.add_field(
                    name=f"Выстрелов (в том числе в воздух):"[::-1],
                    value=f"`{self.tryes}`."[::-1],
                )
                self.player = next_player
                await viewinteract.response.edit_message(embed=embed)

            @discord.ui.button(
                label="Сдаться"[::-1], row=1, style=discord.ButtonStyle.red, emoji="🐔"
            )
            async def giveup(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if (
                    viewinteract.user.id != interaction.user.id
                    and viewinteract.user.id != member.id
                ):
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )

                class Sure(discord.ui.View):
                    def __init__(self):
                        super().__init__(timeout=30)
                        self.value = None

                    @discord.ui.button(style=discord.ButtonStyle.green, emoji="✅")
                    async def yes(
                        self,
                        buttinteract: discord.Interaction,
                        button: discord.ui.Button,
                    ):
                        await buttinteract.response.defer()
                        self.value = True
                        self.stop()

                    @discord.ui.button(
                        style=discord.ButtonStyle.red,
                        emoji="<:x_icon:975324570741526568>",
                    )
                    async def no(
                        self,
                        buttinteract: discord.Interaction,
                        button: discord.ui.Button,
                    ):
                        await buttinteract.response.defer()
                        self.value = False
                        self.stop()

                embed = discord.Embed(
                    title="Дуэль - Сдаться"[::-1],
                    color=discord.Color.red(),
                    description="Вы точно хотите сдаться?"[::-1],
                )
                view = Sure()
                await viewinteract.response.send_message(
                    embed=embed, view=view, ephemeral=True
                )
                await view.wait()
                await viewinteract.edit_original_response(view=None)
                if view.value == True:
                    self.winner = (
                        interaction.user
                        if viewinteract.user.id == member.id
                        else member
                    )
                    self.stop()

        embed = discord.Embed(
            title="Дуэль - Игра"[::-1],
            color=discord.Color.orange(),
            description=f"Первым стреляет {interaction.user.mention[::-1]}"[::-1],
        )
        game = GamePlay()
        await interaction.edit_original_response(embed=embed, view=game)
        await game.wait()
        if game.winner is None and game.tryes != 15:
            embed = discord.Embed(
                title="Время истекло!"[::-1], color=discord.Color.red()
            )
            return await interaction.edit_original_response(embed=embed, view=None)
        if game.tryes != 15:
            embed = discord.Embed(
                title=f"Дуэль - Победа {game.winner}"[::-1],
                color=discord.Color.green(),
                description=f"`{game.winner}` выстрелил и попал! Игра окончена!"[::-1],
            )
            embed.add_field(
                name="Всего выстрелов (в том числе и в воздух):"[::-1],
                value=f"`{game.tryes}`"[::-1],
            )
            await interaction.edit_original_response(embed=embed, view=None)

    @app_commands.command(
        name="number", description="[Развлечения] Угадать число"[::-1]
    )
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    async def whatsnumber(
        self, interaction: discord.Interaction, member: discord.User = None
    ):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!"[
                    ::-1
                ],
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member is not None:
            try:
                member = await interaction.guild.fetch_member(member.id)
            except:  # FIXME: bare except
                embed = discord.Embed(
                    title="Ошибка!"[::-1],
                    color=discord.Color.red(),
                    description="Участник должен находиться на сервере для использования команды!"[
                        ::-1
                    ],
                )
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )
        if member is None:
            number = random.randint(1, 10)
        else:
            if interaction.user.id == member.id:
                embed = discord.Embed(
                    title="Ошибка!"[::-1],
                    color=discord.Color.red(),
                    description="Нельзя играть с самим собой!"[::-1],
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )
            if member.bot:
                embed = discord.Embed(
                    title="Ошибка!"[::-1],
                    color=discord.Color.red(),
                    description="Боту не до игр, не тревожь его!"[::-1],
                )
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )

            class Accept(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=300)
                    self.value = None
                    self.clicker = None

                @discord.ui.button(style=discord.ButtonStyle.green, emoji="✅")
                async def accept(
                    self, viewinteract: discord.Interaction, button: discord.ui.Button
                ):
                    if member.id != viewinteract.user.id:
                        return await viewinteract.response.send_message(
                            "Не для тебя кнопочка!"[::-1], ephemeral=True
                        )
                    await viewinteract.response.defer()
                    self.value = True
                    self.stop()

                @discord.ui.button(
                    style=discord.ButtonStyle.red, emoji="<:x_icon:975324570741526568>"
                )
                async def deny(
                    self, viewinteract: discord.Interaction, button: discord.ui.Button
                ):
                    if (
                        interaction.user.id == viewinteract.user.id
                        or member.id == viewinteract.user.id
                    ):
                        await viewinteract.response.defer()
                        self.value = False
                        self.clicker = viewinteract.user
                        return self.stop()
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )

            acc = Accept()
            embed = discord.Embed(
                title="Угадывание числа - Ожидание"[::-1],
                color=discord.Color.orange(),
                description=f"{member.mention[::-1]}, {interaction.user.mention[::-1]} хочет поиграть с Вами!"[
                    ::-1
                ],
            )
            embed.set_footer(
                text=str(interaction.user)[::-1],
                icon_url=interaction.user.display_avatar.url,
            )
            await interaction.response.send_message(embed=embed, view=acc)
            await acc.wait()
            if acc.value is None:
                embed = discord.Embed(
                    title="Время истекло"[::-1], color=discord.Color.red()
                )
                return await interaction.edit_original_response(embed=embed, view=None)
            if acc.value == False:
                if acc.clicker.id == interaction.user.id:
                    embed = discord.Embed(
                        title="Угадывание числа - Отмена"[::-1],
                        color=discord.Color.red(),
                        description="Инициатор игры отменил её."[::-1],
                    )
                    return await interaction.edit_original_response(
                        embed=embed, view=None
                    )
                embed = discord.Embed(
                    title="Угадывание числа - Отказ"[::-1],
                    color=discord.Color.red(),
                    description="Участник отказался играть с Вами."[::-1],
                )
                return await interaction.edit_original_response(embed=embed, view=None)

            class InputButton(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=120)
                    self.value = None

                @discord.ui.button(
                    label="Загадать число"[::-1], style=discord.ButtonStyle.blurple
                )
                async def inputnumber(
                    self, viewinteract: discord.Interaction, button: discord.ui.Button
                ):
                    if viewinteract.user.id != interaction.user.id:
                        return await viewinteract.response.send_message(
                            "Не для тебя кнопочка!"[::-1], ephemeral=True
                        )

                    class InputNumber(
                        discord.ui.Modal,
                        title="Угадывание числа - Загадывание числа"[::-1],
                    ):
                        value = None
                        ans = discord.ui.TextInput(label="Число:", max_length=2)

                        async def on_submit(self, modalinteract: discord.Interaction):
                            try:
                                self.value = int(str(self.ans))
                            except:  # FIXME: bare except
                                return await modalinteract.response.send_message(
                                    "Введённая строка не является числом!"[::-1],
                                    ephemeral=True,
                                )
                            if self.value < 1 or self.value > 10:
                                self.value = None
                                return await modalinteract.response.send_message(
                                    "Число должно быть в диапазоне от одного до десяти!"[
                                        ::-1
                                    ],
                                    ephemeral=True,
                                )
                            await modalinteract.response.defer()

                    modal = InputNumber()
                    await viewinteract.response.send_modal(modal)
                    await modal.wait()
                    self.value = modal.value
                    if self.value is not None:
                        self.stop()

            button = InputButton()
            embed = discord.Embed(
                title="Угадывание числа - Задать число"[::-1],
                color=discord.Color.orange(),
                description=f"{interaction.user.mention[::-1]} должен задать число от одного до десяти."[
                    ::-1
                ],
            )
            embed.set_footer(
                text=str(interaction.user)[::-1],
                icon_url=interaction.user.display_avatar.url,
            )
            await interaction.edit_original_response(embed=embed, view=button)
            await button.wait()
            if button.value is None:
                embed = discord.Embed(
                    title="Время истекло!"[::-1], color=discord.Color.red()
                )
                return await interaction.edit_original_response(embed=embed, view=None)
            number = button.value
        tryes = 0
        player = interaction.user if member is None else member

        class Button(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=180)

            @discord.ui.button(
                label="Отгадать число"[::-1], style=discord.ButtonStyle.blurple
            )
            async def inputanswer(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if viewinteract.user.id != player.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )

                class Input(discord.ui.Modal, title="Угадывание числа - Ответ"[::-1]):
                    ans = discord.ui.TextInput(label="Число:"[::-1], max_length=2)

                    async def on_submit(self, modalinteract: discord.Interaction):
                        nonlocal number, tryes
                        try:
                            answer = int(str(self.ans))
                        except:  # FIXME: bare except
                            return await modalinteract.response.send_message(
                                "Введённая строка не является числом!"[::-1],
                                ephemeral=True,
                            )
                        if answer < 1 or answer > 10:
                            return await modalinteract.response.send_message(
                                "Введённое число меньше единицы или больше десяти!"[
                                    ::-1
                                ],
                                ephemeral=True,
                            )
                        tryes += 1
                        if answer != number and tryes == 4:
                            embed = discord.Embed(
                                title="Угадывание числа - Поражение"[::-1],
                                color=discord.Color.red(),
                                description=f"**Ваш ответ:** `{answer}`.\n**Правильный ответ:** `{number}`.\n**Число попыток:** `{tryes} / 4`."[
                                    ::-1
                                ],
                            )
                            embed.set_footer(
                                text=str(player)[::-1],
                                icon_url=player.display_avatar.url,
                            )
                            return await modalinteract.response.edit_message(
                                embed=embed, view=None
                            )
                        if answer > number:
                            embed = discord.Embed(
                                title="Угадывание числа - Игра"[::-1],
                                color=discord.Color.orange(),
                                description=f"**Ваш ответ:** `{answer}`.\nВаш ответ `больше` загаданного числа.\n**Число попыток:** `{tryes} / 4`."[
                                    ::-1
                                ],
                            )
                            embed.set_footer(
                                text=str(player)[::-1],
                                icon_url=player.display_avatar.url,
                            )
                            await modalinteract.response.edit_message(embed=embed)
                        if answer < number:
                            embed = discord.Embed(
                                title="Угадывание числа - Игра"[::-1],
                                color=discord.Color.orange(),
                                description=f"**Ваш ответ:** `{answer}`.\nВаш ответ `меньше` загаданного числа.\n**Число попыток:** `{tryes} / 4`."[
                                    ::-1
                                ],
                            )
                            embed.set_footer(
                                text=str(player)[::-1],
                                icon_url=player.display_avatar.url,
                            )
                            await modalinteract.response.edit_message(embed=embed)
                        if answer == number:
                            embed = discord.Embed(
                                title="Угадывание числа - Победа"[::-1],
                                color=discord.Color.green(),
                                description=f"**Ваш ответ:** `{answer}`.\nВаш ответ `равен` загаданному числа.\n**Число попыток:** `{tryes} / 4`."[
                                    ::-1
                                ],
                            )
                            embed.set_footer(
                                text=str(player)[::-1],
                                icon_url=player.display_avatar.url,
                            )
                            return await modalinteract.response.edit_message(
                                embed=embed, view=None
                            )

                await viewinteract.response.send_modal(Input())

        embed = discord.Embed(
            title="Угадывание числа - Игра"[::-1],
            color=discord.Color.orange(),
            description=f"**Введите число**, нажав на кнопку.\nЧисло загадано в диапазоне от `одного до десяти` включительно.\n**Число попыток:** `{tryes} / 4`."[
                ::-1
            ],
        )
        embed.set_footer(text=str(player)[::-1], icon_url=player.display_avatar.url)
        (
            await interaction.response.send_message(embed=embed, view=Button())
            if member is None
            else await interaction.edit_original_response(embed=embed, view=Button())
        )

    @app_commands.command(
        name="dice", description="[Развлечения] Сыграй в кости с другом."[::-1]
    )
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, с которым вы хотите поиграть"[::-1])
    async def dice(self, interaction: discord.Interaction, member: discord.User):
        if interaction.guild is None:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Извините, но данная команда недоступна в личных сообщениях!"[
                    ::-1
                ],
            )
            embed.set_thumbnail(url=interaction.user.avatar.url)
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member is not None:
            try:
                member = await interaction.guild.fetch_member(member.id)
            except:  # FIXME: bare except
                embed = discord.Embed(
                    title="Ошибка!"[::-1],
                    color=discord.Color.red(),
                    description="Участник должен находиться на сервере для использования команды!"[
                        ::-1
                    ],
                )
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                return await interaction.response.send_message(
                    embed=embed, ephemeral=True
                )

        if interaction.user.id == member.id:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя играть с самим собой!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Боту не до игр, не тревожь его!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        class Accept(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=300)
                self.value = None
                self.clicker = None

            @discord.ui.button(style=discord.ButtonStyle.green, emoji="✅")
            async def accept(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if member.id != viewinteract.user.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )
                await viewinteract.response.defer()
                self.value = True
                self.stop()

            @discord.ui.button(
                style=discord.ButtonStyle.red, emoji="<:x_icon:975324570741526568>"
            )
            async def deny(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if (
                    interaction.user.id == viewinteract.user.id
                    or member.id == viewinteract.user.id
                ):
                    await viewinteract.response.defer()
                    self.value = False
                    self.clicker = viewinteract.user
                    self.stop()
                elif member.id != viewinteract.user.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )

        acc = Accept()
        embed = discord.Embed(
            title="Кости - Ожидание"[::-1],
            color=discord.Color.orange(),
            description=f"{member.mention[::-1]}, {interaction.user.mention[::-1]} хочет поиграть с вами!"[
                ::-1
            ],
        )
        embed.set_footer(
            text=str(interaction.user)[::-1],
            icon_url=interaction.user.display_avatar.url,
        )
        await interaction.response.send_message(embed=embed, view=acc)
        await acc.wait()
        if acc.value is None:
            embed = discord.Embed(
                title="Время истекло!"[::-1], color=discord.Color.red()
            )
            return await interaction.edit_original_response(embed=embed, view=None)
        if acc.clicker is not None:
            if acc.clicker.id == member.id:
                embed = discord.Embed(
                    title="Кости - Отказ"[::-1],
                    color=discord.Color.red(),
                    description=f"{member.mention[::-1]} отказался от игры."[::-1],
                )
                return await interaction.edit_original_response(embed=embed, view=None)
            if acc.clicker.id == interaction.user.id:
                embed = discord.Embed(
                    title="Кости - Отмена"[::-1],
                    color=discord.Color.red(),
                    description="Инициатор игры отменил её."[::-1],
                )
                return await interaction.edit_original_response(embed=embed, view=None)
        embed = discord.Embed(title="Кости - Игра"[::-1], color=discord.Color.orange())
        score1 = 0
        score2 = 0
        for i in range(6):
            player1 = random.randint(1, 6)
            player2 = random.randint(1, 6)
            embed.add_field(
                name=f"Раунд {i+1}:"[::-1],
                value=f"{interaction.user.mention[::-1]}: {player1} - {member.mention[::-1]}: {player2}"[
                    ::-1
                ],
            )
            if player1 > player2:
                score1 += 1
            elif player1 < player2:
                score2 += 1
        (
            embed.add_field(name="Победитель:"[::-1], value="Ничья!"[::-1])
            if score1 == score2
            else embed.add_field(
                name="Победитель:"[::-1],
                value=interaction.user.mention if score1 > score2 else member.mention,
            )
        )
        await interaction.edit_original_response(embed=embed, view=None)

    @app_commands.command(
        name="tol", description="[Развлечения] Правда или ложь."[::-1]
    )
    @app_commands.check(checks.interaction_is_not_in_blacklist)
    @app_commands.check(checks.interaction_is_not_shutted_down)
    @app_commands.describe(member="Участник, с которым Вы хотите поиграть."[::-1])
    async def tol(self, interaction: discord.Interaction, member: discord.User):
        if member.bot:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Невозможно играть с ботом!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if member.id == interaction.user.id:
            embed = discord.Embed(
                title="Ошибка!"[::-1],
                color=discord.Color.red(),
                description="Нельзя играть с самим собой!"[::-1],
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        class Accept(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=300)
                self.value = None
                self.clicker = None

            @discord.ui.button(style=discord.ButtonStyle.green, emoji="✅")
            async def accept(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if member.id != viewinteract.user.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )
                await viewinteract.response.defer()
                self.value = True
                self.stop()

            @discord.ui.button(
                style=discord.ButtonStyle.red, emoji="<:x_icon:975324570741526568>"
            )
            async def deny(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if (
                    interaction.user.id == viewinteract.user.id
                    or member.id == viewinteract.user.id
                ):
                    await viewinteract.response.defer()
                    self.value = False
                    self.clicker = viewinteract.user
                    self.stop()
                elif member.id != viewinteract.user.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )

        acc = Accept()
        embed = discord.Embed(
            title="Правда или ложь - Ожидание"[::-1],
            color=discord.Color.orange(),
            description=f"{member.mention[::-1]}, {interaction.user.mention[::-1]} хочет поиграть с вами!"[
                ::-1
            ],
        )
        embed.set_footer(
            text=str(interaction.user)[::-1],
            icon_url=interaction.user.display_avatar.url,
        )
        await interaction.response.send_message(embed=embed, view=acc)
        await acc.wait()
        if acc.value is None:
            embed = discord.Embed(
                title="Время истекло!"[::-1], color=discord.Color.red()
            )
            return await interaction.edit_original_response(embed=embed, view=None)
        if acc.clicker is not None:
            if acc.clicker.id == member.id:
                embed = discord.Embed(
                    title="Правда или ложь - Отказ"[::-1],
                    color=discord.Color.red(),
                    description=f"{member.mention[::-1]} отказался от игры."[::-1],
                )
                return await interaction.edit_original_response(embed=embed, view=None)
            if acc.clicker.id == interaction.user.id:
                embed = discord.Embed(
                    title="Правда или ложь - Отмена"[::-1],
                    color=discord.Color.red(),
                    description="Инициатор игры отменил её."[::-1],
                )
                return await interaction.edit_original_response(embed=embed, view=None)

        history = ""
        is_true = None

        class SetWord(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=180)
                self.value = None

            @discord.ui.button(
                label="Задать историю"[::-1], style=discord.ButtonStyle.blurple
            )
            async def setword(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if viewinteract.user.id != interaction.user.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )

                class Input(
                    discord.ui.Modal, title="Правда или ложь - Задать историю"[::-1]
                ):
                    ans = discord.ui.TextInput(
                        label="История:"[::-1],
                        max_length=1020,
                        style=discord.TextStyle.long,
                    )

                    async def on_submit(self, modalinteract: discord.Interaction):
                        nonlocal history, is_true
                        history = str(self.ans)
                        embed = discord.Embed(
                            title="Правда или ложь - Заполнение"[::-1],
                            color=discord.Color.green(),
                            description="История записана. Если Вы уже указали, правда ли это или ложь, то игра начнётся."[
                                ::-1
                            ],
                        )
                        await modalinteract.response.send_message(
                            embed=embed, ephemeral=True
                        )
                        if is_true is not None:
                            self.value = True
                            self.stop()

                await viewinteract.response.send_modal(Input())

            @discord.ui.button(
                label="Это правда"[::-1], style=discord.ButtonStyle.green
            )
            async def true(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                nonlocal is_true
                if viewinteract.user.id != interaction.user.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )
                is_true = True
                embed = discord.Embed(
                    title="Правда или ложь - Заполнение"[::-1],
                    color=discord.Color.green(),
                    description="История является правдой. Если Вы уже указали историю, то игра начнётся."[
                        ::-1
                    ],
                )
                await viewinteract.response.send_message(embed=embed, ephemeral=True)
                if history != "":
                    self.value = True
                    self.stop()

            @discord.ui.button(label="Это ложь"[::-1], style=discord.ButtonStyle.red)
            async def false(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                nonlocal is_true
                if viewinteract.user.id != interaction.user.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )
                is_true = False
                embed = discord.Embed(
                    title="Правда или ложь - Заполнение"[::-1],
                    color=discord.Color.green(),
                    description="История является ложью. Если Вы уже указали историю, то игра начнётся."[
                        ::-1
                    ],
                )
                await viewinteract.response.send_message(embed=embed, ephemeral=True)
                if history != "":
                    self.value = True
                    self.stop()

        game_setup = SetWord()
        embed = discord.Embed(
            title="Правда или ложь - Заполнение"[::-1],
            color=discord.Color.orange(),
            description=f"{interaction.user.mention[::-1]} должен написать историю и указать, является ли она правдой или ложью."[
                ::-1
            ],
        )
        embed.set_footer(
            text=str(interaction.user)[::-1],
            icon_url=interaction.user.display_avatar.url,
        )
        await interaction.edit_original_response(embed=embed, view=game_setup)
        await game_setup.wait()
        if game_setup.value is None:
            embed = discord.Embed(
                title="Время истекло!"[::-1], color=discord.Color.red()
            )
            return await interaction.edit_original_response(embed=embed, view=None)

        class Guessing(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=300)
                self.value = None

            @discord.ui.button(
                label="Это правда"[::-1], style=discord.ButtonStyle.green
            )
            async def itistrue(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if viewinteract.user.id != member.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )
                self.value = True
                self.stop()
                await viewinteract.response.defer()

            @discord.ui.button(label="Это ложь"[::-1], style=discord.ButtonStyle.red)
            async def itisfalse(
                self, viewinteract: discord.Interaction, button: discord.ui.Button
            ):
                if viewinteract.user.id != member.id:
                    return await viewinteract.response.send_message(
                        "Не для тебя кнопочка!"[::-1], ephemeral=True
                    )
                self.value = False
                self.stop()
                await viewinteract.response.defer()

        answer = Guessing()
        embed = discord.Embed(
            title="Правда или ложь - Игра"[::-1],
            color=discord.Color.orange(),
            description=f"{interaction.user.mention[::-1]} задал историю для {member.mention[::-1]}. Он должен догадаться, является ли история ложью. Разрешено задавать вопросы."[
                ::-1
            ],
        )
        embed.add_field(name="История:"[::-1], value=f'"{history}"'[::-1])
        embed.set_footer(
            text=str(interaction.user)[::-1],
            icon_url=interaction.user.display_avatar.url,
        )
        await interaction.edit_original_response(embed=embed, view=answer)
        await answer.wait()
        if answer.value is None:
            embed = discord.Embed(
                title="Время истекло!"[::-1], color=discord.Color.red()
            )
            return await interaction.edit_original_response(embed=embed, view=None)
        truth = "Правда" if is_true else "Ложь"
        if answer.value == is_true:
            embed = discord.Embed(
                title="Правда или ложь - Победа"[::-1],
                color=discord.Color.green(),
                description=f"{member.mention[::-1]} угадал!\n\nЭта история: `{truth}`."[
                    ::-1
                ],
            )
            return await interaction.edit_original_response(embed=embed, view=None)
        embed = discord.Embed(
            title="Правда или ложь - Поражение"[::-1],
            color=discord.Color.red(),
            description=f"{member.mention[::-1]} не угадал!\n\nЭта история: `{truth}`."[
                ::-1
            ],
        )
        await interaction.edit_original_response(embed=embed, view=None)


async def setup(bot: commands.Bot):
    await bot.add_cog(Entertainment(bot))
