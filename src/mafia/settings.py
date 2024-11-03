import importlib
from typing import TYPE_CHECKING

from src.store.config import MafiaConfig
from ..enums import GameMode

if TYPE_CHECKING:
    from .server import Server


class Settings:
    __roles_list = []
    __civilian_class = None

    @classmethod
    def lazy_import_civilian(cls):
        from .roles import Civilian
        cls.__civilian_class = Civilian

    @classmethod
    def lazy_load_roles_list(cls):
        module = importlib.import_module("src.mafia.roles")
        cls.__roles_list = [
            role_class
            for class_name, role_class in vars(module).items()
            if not class_name.startswith("__")
               and hasattr(role_class, "ROLE")
               and role_class.ROLE not in ["Мирный житель", ""]
        ]

    def __init__(self, server: "Server"):
        self.server = server
        self.minimum_players = MafiaConfig.MIN_PLAYERS
        self.maximum_players = MafiaConfig.MAX_PLAYERS

        self.game_mode = GameMode.MODERATOR
        self.revealed_roles_mode = True
        self.voice_accompaniment = False

        self._white_roles_list = []
        self._black_roles_list = []

    def update_quantity_players(self, max_players: int, min_players: int) -> tuple[bool, str]:
        if min_players > self.maximum_players or min_players < MafiaConfig.MIN_PLAYERS:
            return False, "Число минимального кол-ва игроков вышло за допустимые границы"

        if max_players > MafiaConfig.MAX_PLAYERS_PREMIUM or max_players < self.minimum_players:
            return False, "Число максимального кол-ва игроков вышло за допустимые границы"

        self.minimum_players = min_players
        self.maximum_players = max_players

        return True, ""

    @staticmethod
    def get_all_roles():
        if not Settings.__roles_list:
            Settings.lazy_load_roles_list()

        return Settings.__roles_list

    @staticmethod
    def _change_roles_list(list_append: list, list_remove: list, role_class: type):
        if role_class in list_append:
            return

        list_append.append(role_class)

        if role_class in list_remove:
            list_remove.remove(role_class)

    def add_role_to_black_list(self, role_class: type):
        self._change_roles_list(self._black_roles_list, self._white_roles_list, role_class)

    def add_role_to_white_list(self, role_class: type):
        self._change_roles_list(self._white_roles_list, self._black_roles_list, role_class)

    def get_roles_count(self, len_player_list: int) -> dict[type, int]:
        roles_count = dict()
        general_count_roles = 0

        def _calculate_count(role: type):
            if hasattr(role, "NUM_PLAYERS"):
                count = len_player_list // role.NUM_PLAYERS
            else:
                count = 1

            if role.MAX_PLAYERS == 1 or count > role.MAX_PLAYERS:
                return role.MAX_PLAYERS

            return count


        for role_class in self._white_roles_list:
            if general_count_roles >= len_player_list:
                break

            roles_count[role_class] = _calculate_count(role_class)
            general_count_roles += roles_count[role_class]


        for role_class in self.get_all_roles():
            if general_count_roles >= len_player_list:
                break

            if len_player_list < role_class.APPEARS or role_class in self._black_roles_list:
                continue

            roles_count[role_class] = _calculate_count(role_class)
            general_count_roles += roles_count[role_class]

        if not self.__civilian_class:
            self.lazy_import_civilian()

        if len_player_list - general_count_roles > 0:
            roles_count[self.__civilian_class] = len_player_list - general_count_roles

        return roles_count
