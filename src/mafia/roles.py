import logging
from typing import Optional

from .active_player import ActivePlayer, ActiveTeamPlayer

logger = logging.getLogger(__name__)
from .base import NightEvent
from .enums import ActionNightEnum, ServerState, TeamEnum
from .player import Player
from .server import Server
from .teams import OtherTeam


class Civilian(Player):
    ROLE = "Мирный житель"

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(id, username, server, server.civilian_team)


class Mafia(ActiveTeamPlayer):
    ROLE = "Мафия"
    APPEARS = 4
    MAX_PLAYERS = 4
    NUM_PLAYERS = 4

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(id, username, server, server.active_teams[TeamEnum.MAFIA])

    async def perform_action(self, player: Optional["Player"] = None):
        if player is not None:
            await player.kill(self)
        else:
            logger.debug("Мафия.perform_action: player is None — действие пропущено")


class Doctor(ActivePlayer):
    ROLE = "Доктор"
    APPEARS = 4
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(id, username, server, server.civilian_team)

        self.patient: Player | None = None

    async def new_night_event(self, target: Optional["Player"] = None) -> "NightEvent":
        self.patient = target
        return NightEvent(
            action=ActionNightEnum.TREAT,
            author=self,
            target=target,
        )

    async def perform_action(self, player: Optional["Player"] = None):
        if self.patient is not None:
            self.patient.is_alive = True
        else:
            logger.debug("Доктор.perform_action: patient is None — некого лечить")

    def is_valid(self, player: Player) -> bool:
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

    async def new_night_event(self, player: Optional["Player"] = None) -> "NightEvent":
        if player is None:
            raise ValueError("Comissar target cannot be None")
        if player.team.title == TeamEnum.MAFIA:
            data = f"Игрок {player.username} является участником мафии"
        else:
            data = f"Игрок {player.username} не является участником мафии"

        return NightEvent(
            action=ActionNightEnum.INVESTIGATE, author=self, target=player, data=data
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
        super().__init__(id, username, server, server.civilian_team)

        self.is_mafia = False
        server.signals.on_death_player.subscribe(self.reincarnate)

    async def die(self):
        self.server.signals.on_death_player.unsubscribe(self.reincarnate)
        return await super().die()

    async def reincarnate(self, player: Player):
        if player.team.title != TeamEnum.MAFIA:
            logger.debug(
                "Оборотень.reincarnate: убитый не мафия — перерождение пропущено"
            )
            return

        self.team = player.team
        self.is_mafia = True
        self.server.signals.on_death_player.unsubscribe(self.reincarnate)
        logger.info("Оборотень %s переродился в команду мафии", self.id)

    async def perform_action(self, player: Optional["Player"] = None):
        if self.is_mafia and player is not None:
            await player.kill(self)
        else:
            logger.debug(
                "Оборотень.perform_action: не в мафии или player is None — действие пропущено"
            )


class Bodyguard(ActivePlayer):
    ROLE = "Телохранитель"
    APPEARS = 9
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(id, username, server, server.civilian_team)

        self.target: Player | None = None
        self.server.signals.on_killed_player.subscribe(self.on_killed_player)

    async def new_night_event(self, player: Optional["Player"] = None) -> "NightEvent":
        self.target = player
        return NightEvent(action=ActionNightEnum.GUARD, author=self, target=player)

    def is_valid(self, player: "Player") -> bool:
        return self != player
    
    async def die(self):
        self.server.signals.on_killed_player.unsubscribe(self.on_killed_player)
        return await super().die()

    async def on_killed_player(self, player: Player):
        if self.target != player:
            logger.debug(
                "Телохранитель.on_killed_player: убит не подопечный — действие пропущено"
            )
            return
        
        player.is_alive = True
        if player.killer is not None:
            await self.kill(player.killer)
            return
        
        logger.debug(
            "Телохранитель.on_killed_player: killer is None — возмездие пропущено"
        )


class Maniac(ActivePlayer):
    ROLE = "Маньяк"
    APPEARS = 10
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(id, username, server, OtherTeam())

    async def new_night_event(self, player: Optional["Player"] = None) -> "NightEvent":
        return NightEvent(action=ActionNightEnum.GUT, author=self, target=player)

    async def perform_action(self, player: Optional["Player"] = None):
        if player is not None:
            await player.kill(self)
        else:
            logger.debug("Маньяк.perform_action: player is None — действие пропущено")


class Mistress(ActivePlayer):
    ROLE = "Любовница"
    APPEARS = 11
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(id, username, server, server.civilian_team, 0)

        self.target: Player | None = None

        server.signals.on_killed_player.subscribe(self.on_killed_player)
        server.signals.on_change_server_state.subscribe(self.change_target_can_vote)

    def is_valid(self, player: "Player") -> bool:
        return self != player

    async def new_night_event(self, player: Optional["Player"] = None) -> "NightEvent":
        self.target = player
        if player is not None:
            player.is_can_vote = False
            player.acquitted = True
            if isinstance(player, ActivePlayer):
                player.is_night_activity = False
            else:
                logger.debug(
                    "Любовница.new_night_event: player не ActivePlayer — ночная активность не заблокирована"
                )
        else:
            logger.debug(
                "Любовница.new_night_event: player is None — эффекты не применены"
            )

        return NightEvent(action=ActionNightEnum.DATE_NIGHT, author=self, target=player)

    async def perform_action(self, player: Optional["Player"] = None):
        if isinstance(self.target, ActivePlayer):
            self.target.is_night_activity = True
        else:
            logger.debug(
                "Любовница.perform_action: target не ActivePlayer — ночная активность не восстановлена"
            )

    async def die(self):
        self.server.signals.on_killed_player.unsubscribe(self.on_killed_player)
        self.server.signals.on_change_server_state.unsubscribe(self.change_target_can_vote)
        return await super().die()

    async def on_killed_player(self, player: Player):
        if player != self.target:
            logger.debug(
                "Любовница.on_killed_player: убит не целью — действие пропущено"
            )

        if player.killer is not None:
            await self.kill(player.killer)
            return
        
        logger.debug(
            "Любовница.on_killed_player: killer is None — месть пропущена"
        )
            
    async def change_target_can_vote(self, state: ServerState):
        if state == ServerState.NIGHT and self.target:
            self.target.is_can_vote = True
            self.target.acquitted = False
        else:
            logger.debug(
                "Любовница.change_target_can_vote: не ночь или нет цели — голос не восстановлен"
            )


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
        super().__init__(id, username, server, server.civilian_team)

        self.target: Player | None = None
        self.server.signals.on_killed_player.subscribe(self.on_killed_player)

    async def new_night_event(self, player: Optional["Player"] = None) -> "NightEvent":
        self.target = player
        return NightEvent(action=ActionNightEnum.GUARD, author=self, target=player)
    
    async def die(self):
        self.server.signals.on_killed_player.unsubscribe(self.on_killed_player)
        return await super().die()

    async def on_killed_player(self, player: Player):
        if self.target and (self.target == player or self.target == player.killer):
            await self.server.signals.on_witness_saw_killer.emit(
                self, player.killer, player
            )
        else:
            logger.debug(
                "Свидетель.on_killed_player: цель не совпадает — уведомление пропущено"
            )


class Rapist(ActivePlayer):
    ROLE = "Насильник"
    APPEARS = 15
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(id, username, server, server.active_teams[TeamEnum.MAFIA], 0)

        self.target: Player | None = None

        server.signals.on_change_server_state.subscribe(self.change_target_can_vote)

    async def new_night_event(self, player: Optional["Player"] = None) -> "NightEvent":
        self.target = player

        if player is not None:
            player.is_can_vote = False
            if isinstance(player, ActivePlayer):
                player.is_night_activity = False
            else:
                logger.debug(
                    "Насильник.new_night_event: player не ActivePlayer — ночная активность не заблокирована"
                )
        else:
            logger.debug(
                "Насильник.new_night_event: player is None — эффекты не применены"
            )

        return NightEvent(
            action=ActionNightEnum.RETRIBUTION, author=self, target=player
        )

    def is_valid(self, player: "Player") -> bool:
        return self != player

    async def perform_action(self, player: Optional["Player"] = None):
        if isinstance(self.target, ActivePlayer):
            self.target.is_night_activity = True
        else:
            logger.debug(
                "Насильник.perform_action: target не ActivePlayer — ночная активность не восстановлена"
            )

    async def die(self):
        self.server.signals.on_change_server_state.unsubscribe(self.change_target_can_vote)
        return await super().die()

    async def change_target_can_vote(self, state: ServerState):
        if state == ServerState.NIGHT and self.target:
            self.target.is_can_vote = True
        else:
            logger.debug(
                "Насильник.change_target_can_vote: не ночь или нет цели — голос не восстановлен"
            )


class Kamikaze(ActivePlayer):
    ROLE = "Камикадзе"
    APPEARS = 17
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(id, username, server, server.active_teams[TeamEnum.MAFIA])

        self.target: Player | None = None

    async def new_night_event(self, player: Optional["Player"] = None) -> "NightEvent":
        self.target = player

        if player is None:
            raise ValueError("Kamikaze target cannot be None")

        if player.role == Comissar.ROLE:
            data = "Вы обнаружили Комиссара! Да начнется же возмездие!"
            action = ActionNightEnum.RETRIBUTION

            await self.server.signals.on_kamikaze_found_commissar.emit(self.target)
        else:
            data = "Данный игрок не является Комиссаром"
            action = ActionNightEnum.INVESTIGATE

        return NightEvent(action=action, author=self, target=player, data=data)

    async def perform_action(self, player: Optional["Player"] = None):
        if self.target is not None and self.target.role == Comissar.ROLE:
            await self.target.kill(self)
            await self.kill(self)
        else:
            logger.debug(
                "Камикадзе.perform_action: цель не Комиссар или None — самоубийство пропущено"
            )


class Necromancer(ActivePlayer):
    ROLE = "Некромант"
    APPEARS = 18
    MAX_PLAYERS = 1

    def __init__(self, id: int, username: str, server: Server):
        super().__init__(id, username, server, OtherTeam(), -1)

        self.awakened_list: list[Player] = []
        server.signals.on_change_server_state.subscribe(self.change_can_new_night_event)

    def is_valid(self, player: Player) -> bool:
        return (
            player != self and player not in self.awakened_list and not player.is_alive
        )
    
    async def die(self):
        self.server.signals.on_change_server_state.unsubscribe(self.change_can_new_night_event)
        return await super().die()

    async def new_night_event(self, player: Optional["Player"] = None) -> "NightEvent":
        if player is None:
            raise ValueError("Necromancer target cannot be None")
        self.awakened_list.append(player)

        player.is_alive = True

        await self.server.signals.on_necromancer_awakened_player.emit(self, player)

        return NightEvent(action=ActionNightEnum.AWAKENED, author=self, target=player)

    def get_players_death(self):
        return self.server.players.filter(lambda player: not player.is_alive)

    async def change_can_new_night_event(self, state: ServerState):
        if state != ServerState.NIGHT:
            logger.debug("Некромант.change_can_new_night_event: не ночь — пропущено")
            return

        players_death = self.get_players_death()
        self.is_night_activity = len(players_death) != 0

    async def perform_action(self, player: Optional["Player"] = None):
        if player is not None:
            player.is_alive = False
            await self.server.signals.on_awakened_player_sleep.emit(player)
        else:
            logger.debug(
                "Некромант.perform_action: player is None — пробуждённый не усыплён"
            )

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
