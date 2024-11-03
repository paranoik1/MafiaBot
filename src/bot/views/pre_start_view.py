from asyncio import gather

import disnake
from disnake import MessageInteraction, Event
from disnake.ui import View

from src.bot.mafia.decorators import *
from src.bot.mafia.utils import *
from src.bot.texts import SETTINGS_FIELDS
from src.bot.views.settings import ServerSettingsView
from src.enums import GameMode
from src.mafia.player import PrePlayer, Player
from src.bot.mafia.server import MafiaDiscordServer
from src.store.repository import ExistsKey


class PreStartMafiaView(View):
    def __init__(self):
        super().__init__()

    @disnake.ui.button(label="Присоединится", style=disnake.ButtonStyle.green)
    @is_server_exists("Игра не найдена")
    async def join_mafia(self, inter: MessageInteraction, server: MafiaDiscordServer):
        # if inter.user == server.leader and server.settings.game_mode == GameMode.MODERATOR:
        #     return await inter.send("Ведущий не может принять участие в игре", ephemeral=True)

        await inter.response.defer()

        pre_player = PrePlayer(inter.user.id, inter.user.mention)
        if pre_player in server.pre_players:
            server.pre_players.remove(pre_player.id)
        else:
            server.pre_players.add(pre_player.id, pre_player)

        embed = get_pre_start_mafia_embed(server)

        await inter.message.edit(embed=embed)

    @disnake.ui.button(label="Начать игру", style=BUTTON_STYLE)
    @is_server_exists("Игра не найдена")
    @is_leader
    async def start_mafia(self, inter: MessageInteraction, server: MafiaDiscordServer):
        pre_players_list = server.pre_players.to_list()
        if len(pre_players_list) < server.settings.minimum_players:
            return await inter.send(f"Недостаточно игроков. Минимальное кол-во - {server.settings.minimum_players}")
        elif len(pre_players_list) > server.settings.maximum_players:
            return await inter.send(f"Превышен допустимый лимит игроков. Максимальное кол-во - {server.settings.maximum_players}")

        await inter.response.defer()
        await inter.delete_original_message()

        await server.start(inter)

    @disnake.ui.button(label="Настройки")
    @is_server_exists("Игра не найдена")
    @is_leader
    @is_game_started(False)
    @is_premium()
    async def settings(self, inter: MessageInteraction, server: MafiaDiscordServer):
        embed = Embed(
            title="Настройки",
            color=GENERAL_COLOR
        )

        for field_name, field_value in SETTINGS_FIELDS.items():
            embed.add_field(field_name, field_value)

        await inter.send(
            embed=embed,
            view=ServerSettingsView(server.settings),
            ephemeral=True
        )
