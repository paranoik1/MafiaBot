from typing import Optional

from .active_player import ActiveTeamPlayer, ActivePlayer
from .base import NightEvent
from .enums import TeamEnum, ActionNightEnum, ServerState
from .player import Player
from .server import Server
from .teams import OtherTeam


class Civilian(Player):
    ROLE = "Мирный житель"

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(
            id,
            username,
            server,
            server.civilian_team
        )


class Mafia(ActiveTeamPlayer):
    ROLE = "Мафия"
    APPEARS = 4
    MAX_PLAYERS = 4
    NUM_PLAYERS = 4

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(
            id,
            username,
            server,
            server.active_teams[TeamEnum.MAFIA]
        )

    async def perform_action(self, player=None):
        await player.kill(self)


class Doctor(ActivePlayer):
    ROLE = "Доктор"
    APPEARS = 4
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(
            id,
            username,
            server,
            server.civilian_team
        )

        self.patient = None

    async def new_night_event(self, target: Player = None) -> NightEvent:
        self.patient = target
        return NightEvent(
            action=ActionNightEnum.TREAT,
            author=self,
            target=target,
        )

    async def perform_action(self, player=None):
        self.patient.is_alive = True

    def is_valid(self, player: Player):
        return self.patient != player and player in self.server.get_players_alive()


class Comissar(ActivePlayer):
    ROLE = "Комиссар"
    APPEARS = 5
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(
            id,
            username,
            server,
            server.civilian_team,
        )

    async def new_night_event(self, player: Player = None) -> NightEvent:
        if player.team.title == TeamEnum.MAFIA:
            data = f"Игрок {player.username} является участником мафии"
        else:
            data = f"Игрок {player.username} не является участником мафии"

        return NightEvent(
            action=ActionNightEnum.INVESTIGATE,
            author=self,
            target=player,
            data=data
        )


class Immortal(Player):
    ROLE = "Бессмертный"
    APPEARS = 6
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(
            id,
            username,
            server,
            server.civilian_team,
        )

        server.signals.on_killed_player.subscribe(self.on_killed_player)

    async def on_killed_player(self, player: Player):
        if player == self:
            player.is_alive = True


class Werewolf(ActiveTeamPlayer):
    ROLE = "Оборотень"
    APPEARS = 7
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(
            id,
            username,
            server,
            server.civilian_team
        )

        self.is_mafia = False
        server.signals.on_death_player.subscribe(self.reincarnate)

    async def reincarnate(self, player: Player):
        if player.team.title != TeamEnum.MAFIA:
            return

        self.team = player.team
        self.is_mafia = True
        self.server.signals.on_death_player.unsubscribe(self.reincarnate)

    async def perform_action(self, player=None):
        if self.is_mafia:
            await player.kill(self)


class Bodyguard(ActivePlayer):
    ROLE = "Телохранитель"
    APPEARS = 9
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(
            id,
            username,
            server,
            server.civilian_team
        )

        self.target = None
        self.server.signals.on_killed_player.subscribe(self.on_killed_player)

    async def new_night_event(self, player: Optional["Player"] = None) -> "NightEvent":
        self.target = player
        return NightEvent(
            action=ActionNightEnum.GUARD,
            author=self,
            target=player
        )

    def is_valid(self, player: "Player") -> bool:
        return self != player

    async def on_killed_player(self, player: Player):
        if self.target == player:
            player.is_alive = True
            await self.kill(player.killer)


class Maniac(ActivePlayer):
    ROLE = "Маньяк"
    APPEARS = 10
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(
            id,
            username,
            server,
            OtherTeam()
        )

    async def new_night_event(self, player: Player = None) -> NightEvent:
        return NightEvent(
            action=ActionNightEnum.GUT,
            author=self,
            target=player
        )

    async def perform_action(self, player=None):
        await player.kill(self)


class Mistress(ActivePlayer):
    ROLE = "Любовница"
    APPEARS = 11
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(
            id,
            username,
            server,
            server.civilian_team,
            0
        )

        self.target = None

        server.signals.on_killed_player.subscribe(self.on_killed_player)
        server.signals.on_change_server_state.subscribe(self.change_target_can_vote)

    def is_valid(self, player: "Player") -> bool:
        return self != player

    async def new_night_event(self, player: Player = None) -> NightEvent:
        self.target = player

        self.target.is_can_vote = False
        self.target.acquitted = True
        if isinstance(self.target, ActivePlayer):
            self.target.is_night_activity = False

        return NightEvent(
            action=ActionNightEnum.DATE_NIGHT,
            author=self,
            target=player
        )

    async def perform_action(self, player: Player = None):
        self.target.is_night_activity = True

    async def on_killed_player(self, player: Player):
        if player == self.target:
            await self.kill(player.killer)

    async def change_target_can_vote(self, state: ServerState):
        if state == ServerState.NIGHT and self.target:
            self.target.is_can_vote = True
            self.target.acquitted = False


class GodFather(Mafia):
    ROLE = "Крестный отец"
    APPEARS = 12
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(
            id,
            username,
            server,
        )

        server.active_teams[TeamEnum.MAFIA].godfather = self


class Witness(ActivePlayer):
    ROLE = "Свидетель"
    APPEARS = 14
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(
            id,
            username,
            server,
            server.civilian_team
        )

        self.target = None
        self.server.signals.on_killed_player.subscribe(self.on_killed_player)

    async def new_night_event(self, player: Optional["Player"] = None) -> "NightEvent":
        self.target = player
        return NightEvent(
            action=ActionNightEnum.GUARD,
            author=self,
            target=player
        )

    async def on_killed_player(self, player: Player):
        if self.target and (self.target == player or self.target == player.killer):
            await self.server.signals.on_witness_saw_killer.emit(self, player.killer, player)


class Rapist(ActivePlayer):
    ROLE = "Насильник"
    APPEARS = 15
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(
            id,
            username,
            server,
            server.active_teams[TeamEnum.MAFIA],
            0
        )

        self.target = None

        server.signals.on_change_server_state.subscribe(self.change_target_can_vote)

    async def new_night_event(self, player: Player = None) -> NightEvent:
        self.target = player

        self.target.is_can_vote = False
        if isinstance(self.target, ActivePlayer):
            self.target.is_night_activity = False

        return NightEvent(
            action=ActionNightEnum.RETRIBUTION,
            author=self,
            target=player
        )

    def is_valid(self, player: "Player") -> bool:
        return self != player

    async def perform_action(self, player: Player = None):
        self.target.is_night_activity = True

    async def change_target_can_vote(self, state: ServerState):
        if state == ServerState.NIGHT and self.target:
            self.target.is_can_vote = True


class Kamikaze(ActivePlayer):
    ROLE = "Камикадзе"
    APPEARS = 17
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(
            id,
            username,
            server,
            server.active_teams[TeamEnum.MAFIA]
        )

        self.target = None

    async def new_night_event(self, player: Optional["Player"] = None) -> "NightEvent":
        self.target = player

        if player.role == Comissar.ROLE:
            data = "Вы обнаружили Комиссара! Да начнется же возмездие!"
            action = ActionNightEnum.RETRIBUTION

            await self.server.signals.on_kamikaze_found_commissar.emit(self.target)
        else:
            data = "Данный игрок не является Комиссаром"
            action = ActionNightEnum.INVESTIGATE

        return NightEvent(
            action=action,
            author=self,
            target=player,
            data=data
        )

    async def perform_action(self, player: Optional["Player"] = None):
        if self.target.role == Comissar.ROLE:
            self.target.kill(self)
            await self.kill(self)


class Necromancer(ActivePlayer):
    ROLE = "Некромант"
    APPEARS = 18
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(
            id,
            username,
            server,
            OtherTeam(),
            -1
        )

        self.awakened_list = []
        server.signals.on_change_server_state.subscribe(self.change_can_new_night_event)

    def is_valid(self, player: Player) -> bool:
        return player != self and player not in self.awakened_list and not player.is_alive

    async def new_night_event(self, player: Optional["Player"] = None) -> "NightEvent":
        self.awakened_list.append(player)

        player.is_alive = True

        await self.server.signals.on_necromancer_awakened_player.emit(self, player)

        return NightEvent(
            action=ActionNightEnum.AWAKENED,
            author=self,
            target=player
        )

    def get_players_death(self):
        return self.server.players.filter(lambda player: not player.is_alive)

    async def change_can_new_night_event(self, state: ServerState):
        if state != ServerState.NIGHT:
            return

        players_death = self.get_players_death()
        self.is_night_activity = len(players_death) != 0

    async def perform_action(self, player: Optional["Player"] = None):
        player.is_alive = False
        await self.server.signals.on_awakened_player_sleep.emit(player)

    def get_target_list(self):
        return self.get_players_death()


# class Alchemist(ActivePlayer):
#     ROLE = "Алхимик"
#     APPEARS = 20
#     MAX_PLAYERS = 1
#
#     def __init__(self, id: int, username: str, server: Server):
#         super().__init__(
#             id,
#             username,
#             server,
#             OtherTeam()
#         )
#
#     def new_night_event(self, player: Optional["Player"] = None) -> "NightEvent":
#         pass
#
#     def perform_action(self, player: Optional["Player"] = None):
#         pass
