from typing import Any, cast

from disnake import Embed, MessageInteraction
from disnake.ui import Button, StringSelect, View, button, string_select

from src.bot.config import BUTTON_STYLE, GENERAL_COLOR
from src.bot.mafia.decorators import *
from src.bot.mafia.server import MafiaDiscordServer
from src.bot.mafia.utils import get_all_roles_name
from src.mafia.settings import Settings


def is_role_selected(func):
    async def wrapper(self, button: Button, inter: MessageInteraction):
        if self.selected_role:
            return await func(self, inter)

        return await inter.send("Роль не выбрана", ephemeral=True)

    return wrapper


class GameManageRoles(View):
    def __init__(self, settings: Settings):
        super().__init__()

        self.settings = settings

        roles_dict: dict[str, Any] = {}
        for role in self.settings.get_all_roles():
            rc: Any = role
            roles_dict[rc.ROLE] = role
        self.roles_dict = roles_dict

        self.selected_role: type | None = None

    @staticmethod
    def get_roles_embed(server: MafiaDiscordServer):
        embed = Embed(title="Роли в игре", color=GENERAL_COLOR, description="")

        roles_count = server.settings.get_roles_count(len(server.pre_players))

        description = embed.description or ""
        for role, count in roles_count.items():
            rc: Any = role
            description += f"- {rc.ROLE} - {count} игрок\n"
        embed.description = description

        return embed

    async def edit_message_view(self, inter: MessageInteraction):
        await inter.response.defer()

        await inter.edit_original_message(
            embed=self.get_roles_embed(cast(MafiaDiscordServer, self.settings.server))
        )

    @string_select(options=get_all_roles_name())
    async def select_role(self, _: StringSelect, inter: MessageInteraction):
        role_name = inter.data.values[0]
        self.selected_role = self.roles_dict[role_name]

        print(self.selected_role)
        await inter.response.defer()

    @button(label="Добавить", style=BUTTON_STYLE)
    @is_role_selected
    async def add_role(self, inter: MessageInteraction):
        role: Any = self.selected_role
        if role:
            self.settings.add_role_to_white_list(role)
            await self.edit_message_view(inter)
            await inter.send(f"Роль '{role.ROLE}' добавлена в игру", ephemeral=True)

    @button(label="Удалить", style=BUTTON_STYLE)
    @is_role_selected
    async def delete_role(self, inter: MessageInteraction):
        role: Any = self.selected_role
        if role:
            self.settings.add_role_to_black_list(role)
            await self.edit_message_view(inter)
            await inter.send(f"Роль '{role.ROLE}' удалена из игры", ephemeral=True)

    @button(label="Обновить")
    async def update(self, _: Button, inter: MessageInteraction):
        await self.edit_message_view(inter)
