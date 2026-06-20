import logging
from typing import TYPE_CHECKING

from disnake import Message

logger = logging.getLogger(__name__)

from src.mafia.active_player import ActivePlayer, ActiveTeamPlayer
from src.mafia.teams import ActiveTeam, MafiaTeam

from ...enums import GameMode
from ...mafia.roles import Comissar, GodFather, Kamikaze, Mafia, Werewolf
from .utils import *

if TYPE_CHECKING:
    from .server import MafiaDiscordServer


class ActiveTeamDiscord(ActiveTeam):
    def __init__(self, title, server: "MafiaDiscordServer", description_vote: str):
        super().__init__(title, server)

        self._messages: list[Message] = []
        self.description = description_vote

        self.server: MafiaDiscordServer

    async def start_vote(self):
        active_team_players = self.get_players_participating_in_voting()
        players = self.server.get_players_alive()

        for active_player in active_team_players:
            user = self.server.get_discord_user(active_player.id)
            if user is None:
                logger.warning(
                    "Игрок %s: не найден в Discord — голосование команды пропущено",
                    active_player.id,
                )
                continue

            embed = get_embed_voting(
                server=self.server,
                voting_instance=self,
                players=players,
                description=self.description,
            )
            components = self.get_components_voting(active_player, players)

            message = await user.send(embed=embed, components=components)
            self._messages.append(message)

    def _get_players_role_list_string(self, players: Repository[ActivePlayer]):
        players_string = ""
        for player in players:
            players_string += f"- {player.username} - **{player.role}**\n"

        return players_string

    async def send_team_roles(self):
        players = self.get_players_alive()
        players_participates = self.get_players_participating_in_voting()

        embed = Embed(
            title=f"Команда {self.title}",
            colour=GENERAL_COLOR,
            description="Участники:\n",
        )
        embed.description += self._get_players_role_list_string(players)

        for player in players_participates:
            user = self.server.get_discord_user(player.id)
            if user is None:
                logger.warning(
                    "Игрок %s: не найден в Discord — отправка роли команды пропущена",
                    player.id,
                )
                continue
            await user.send(embed=embed)

    async def update_info_voting(self):
        players = self.server.get_players_alive()
        embed = get_embed_voting(
            server=self.server,
            voting_instance=self,
            players=players,
            description=self.description,
        )

        for message in self._messages:
            await message.edit(
                embed=embed, components=components_convert_list(message.components)
            )

    async def process_end_voting(self):
        if not self.is_all_players_voted():
            logger.info("Не все игроки проголосовали — ожидание")
            return

        targets = self.get_result_voting()
        if len(targets) == 1:
            target = targets[0]
            await self.end_voting(target)
        else:
            await self.dispute(targets)

    async def dispute(self, targets: list):
        pass

    async def end_voting(self, target: Player):
        self.server.night_team_choose.remove(self)

        role_info = ROLES_INFO[self.players[0].role]
        await self.server._game_handler.send_leader_message(
            role_info.message_for_leader.format(target.username)
        )

        for message in self._messages:
            await message.channel.send(
                role_info.message_for_author.format(target.username)
            )

            await message.delete()

        self._messages.clear()
        self.clear_cache_voting()
        return await self.try_new_night_event(target)

    def get_components_voting(
        self, author: ActiveTeamPlayer, players: Repository[Player]
    ) -> list[Button]:
        custom_id_template = get_custom_id(
            "vote", self.server.id, author.id, "{}", self.title
        )

        components = get_component_list_players(
            self.server, players, custom_id_template
        )

        return components


class MafiaTeamDiscord(MafiaTeam, ActiveTeamDiscord):
    def __init__(self, server: "MafiaDiscordServer"):
        description_vote = "Проголосуйте за игрока, которого вы бы хотели убить"

        super().__init__(server, description_vote=description_vote)  # type: ignore

        self.roles_participating_in_voting = [Mafia.ROLE, GodFather.ROLE, Werewolf.ROLE]
        self.server.signals.on_kamikaze_found_commissar.subscribe(self.comissar_founded)

    async def dispute(self, targets: list[Player]):
        if not self.godfather:
            logger.warning("Нет Крёстного отца — разрешение ничьи мафии пропущено")
            return

        info = self.get_vote_info()
        target = info[self.godfather]

        for message in self._messages:
            await message.channel.send(
                f"Мафия не решила между собой, кого убивать. Крестный отец выбрал {target.username}"
            )

        await self.end_voting(target)

    async def _send_messages_team(self, content: str):
        players = self.get_players_participating_in_voting()
        for player in players:
            user = self.server.get_discord_user(player.id)
            if user:
                await user.send(content)
            else:
                logger.warning(
                    "Игрок %s: не найден в Discord — сообщение команды пропущено",
                    player.id,
                )

    async def comissar_founded(self, comissar: Comissar):
        await self._send_messages_team(
            f"{Kamikaze.ROLE} обнаружил Комиссара - {comissar.username}"
        )

    def get_players_participating_in_voting(self):
        players = super().get_players_participating_in_voting()
        return players.filter(
            lambda player: player.role in self.roles_participating_in_voting
        )
