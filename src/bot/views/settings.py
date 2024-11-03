from disnake import MessageInteraction
from disnake.ui import View, button

from src.bot.mafia.utils import *
from src.bot.modals.quantity_players import QuantityPlayersModal
from src.bot.views.game_roles import GameManageRoles
from src.enums import GameMode
from src.mafia.settings import Settings
from src.bot.mafia.server import MafiaDiscordServer


class ServerSettingsView(View):
    def __init__(self, settings: Settings):
        self.settings = settings
        self.server: MafiaDiscordServer = settings.server

        super().__init__()

    @button(label="Кол-во игроков", style=BUTTON_STYLE)
    async def quantity_players(self, btn: Button, inter: MessageInteraction):
        await inter.response.send_modal(
            modal=QuantityPlayersModal(self.settings),
        )

        await inter.bot.wait_for(
            "modal_submit",
            check=lambda i: i.custom_id == "quantity_players_modal" and i.author.id == inter.author.id,
            timeout=300,
        )

        if len(self.server.pre_players) > self.settings.maximum_players:
            extra_players = len(self.server.pre_players) - self.settings.maximum_players
            for i in range(extra_players, len(self.server.pre_players)):
                self.server.pre_players.remove(self.server.pre_players[i].id)

            embed = get_pre_start_mafia_embed(self.server)
            await self.server.channel_interaction.edit_original_message(embed=embed)

    @button(label="Роли в игре", style=BUTTON_STYLE)
    async def possible_roles(self, btn: Button, inter: MessageInteraction):
        view = GameManageRoles(self.settings)
        await inter.send(
            view=view,
            embed=view.get_roles_embed(self.server),
            ephemeral=True
        )

    @button(label="Смена режима игры", style=BUTTON_STYLE)
    async def game_mode(self, btn: Button, inter: MessageInteraction):
        self.settings.game_mode = GameMode.AUTOMATIC if self.settings.game_mode == GameMode.MODERATOR else GameMode.MODERATOR

        if self.settings.game_mode == GameMode.MODERATOR and self.server.leader in self.server.pre_players:
            self.server.pre_players.remove(self.server.leader.id)

        await inter.send("Режим игры был изменен на " + self.settings.game_mode, ephemeral=True)

        embed = get_pre_start_mafia_embed(self.server)
        await self.server.channel_interaction.edit_original_message(embed=embed)

    @button(label="Режим раскрытия ролей", style=BUTTON_STYLE)
    async def revealed_roles_mode(self, btn: Button, inter: MessageInteraction):
        self.settings.revealed_roles_mode = not self.settings.revealed_roles_mode

        await inter.send(
            "Режим раскрытия ролей был " + ("включен" if self.settings.revealed_roles_mode else "выключен"),
            ephemeral=True
        )

    @button(label="Голосовое сопровождение", style=BUTTON_STYLE)
    async def voice_accompaniment(self, btn: Button, inter: MessageInteraction):
        self.settings.voice_accompaniment = not self.settings.voice_accompaniment

        await inter.send(
            "Голосове сопрождение было " + ("включено" if self.settings.voice_accompaniment else "выключено"),
            ephemeral=True
        )
