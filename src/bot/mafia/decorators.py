from asyncio import iscoroutinefunction
from typing import Coroutine, TYPE_CHECKING

from disnake import ApplicationCommandInteraction, Interaction, MessageInteraction
from disnake.ui import Button

from src.db.engine import get_premium
from src.enums import GameMode
from src.store.globals import COOLDOWN_LIST
from src.store.utils import get_server

if TYPE_CHECKING:
    from src.bot.mafia.server import MafiaDiscordServer


def is_server_exists(text_error: str = "Игра не найдена", is_true: bool = True):
    def wrapper(func):
        async def predicate(self, inter: ApplicationCommandInteraction | Button, *args):
            if not isinstance(inter, Interaction):
                inter = args[0]

            server = get_server(inter.guild_id)
            if bool(server) == is_true:
                await func(self, inter=inter, server=server)
            else:
                await inter.send(text_error, ephemeral=True)

        return predicate

    return wrapper


def is_game_started(is_true: bool = True):
    def predicate(func):
        async def wrapper(self, inter: ApplicationCommandInteraction, server: "MafiaDiscordServer"):
            if server.is_started == is_true:
                await func(self, inter=inter, server=server)
            else:
                await inter.send("Игра не запущена", ephemeral=True)

        return wrapper
    return predicate


def is_premium(message: str = "Приобретите премиум версию, чтобы получить доступ к данной функции"):
    def predicate(func):
        async def wrapper(self, inter: ApplicationCommandInteraction, server: "MafiaDiscordServer"):
            if not await get_premium(inter.guild.id) and not await get_premium(inter.user.id):
                return await inter.send(message, ephemeral=True)

            return await func(self, inter=inter, server=server)

        return wrapper
    return predicate


def is_leader(func):
    async def wrapper(self, inter: ApplicationCommandInteraction, server: "MafiaDiscordServer"):
        if server.leader == inter.user:
            await func(self, inter=inter, server=server)
        else:
            await inter.send("Доступ к этим командам есть только у ведущего текущей игры", ephemeral=True)

    return wrapper


def is_game_mode(game_mode: GameMode):
    def check(server: "MafiaDiscordServer"):
        return server.settings.game_mode == game_mode

    def predicate(func):
        async def aio_wrapper(self, *args, **kwargs):
            if check(self.server):
                return await func(self, *args, **kwargs)

        def wrapper(self, *args, **kwargs):
            if check(self.server):
                return func(self, *args, **kwargs)

        if iscoroutinefunction(func):
            return aio_wrapper

        return wrapper

    return predicate


def is_voice_accompaniment(func):
    def check(server: "MafiaDiscordServer"):
        return server.settings.voice_accompaniment

    async def aio_wrapper(self, *args, **kwargs):
        if check(self.server):
            return await func(self, *args, **kwargs)

    def wrapper(self, *args, **kwargs):
        if check(self.server):
            return func(self, *args, **kwargs)

    if iscoroutinefunction(func):
        return aio_wrapper

    return wrapper
