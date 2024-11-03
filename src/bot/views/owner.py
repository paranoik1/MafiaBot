import disnake
from disnake import MessageInteraction, Embed
from disnake.ui import View

from ..config import BUTTON_STYLE
from ...store.globals import SERVER_REPOSITORY


def is_owner_button(func):
    async def predicate(view, button, inter: MessageInteraction):
        if not await inter.bot.is_owner(inter.author):
            return False

        return await func(view, button, inter)

    return predicate


def get_game_emb(index: int):
    try:
        server = SERVER_REPOSITORY[index]
    except:
        return None

    emb = Embed(title=f"Игра №{index}")
    emb.add_field("Кол-во игроков:", len(server.players))
    emb.add_field("Роли:", ", ".join([player.role for player in server.players]))

    return emb


class GameView(View):
    def __init__(self, num):
        super().__init__(timeout=None)
        self.num = num

    @disnake.ui.button(label="Далее", style=BUTTON_STYLE)
    @is_owner_button
    async def get_games(self, button: disnake.ui.Button, inter: MessageInteraction):
        emb = get_game_emb(self.num)
        if emb:
            return await inter.response.edit_message(view=GameView(self.num + 1), embed=emb)

        return await inter.response.send_message("Игра не найдена")

    @disnake.ui.button(label="Назад", style=BUTTON_STYLE)
    @is_owner_button
    async def get_games(self, button: disnake.ui.Button, inter: MessageInteraction):
        emb = get_game_emb(self.num - 1)
        if emb:
            return await inter.response.edit_message(view=GameView(self.num), embed=emb)

        return await inter.response.send_message("Игра не найдена")


class StateView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Игры", style=BUTTON_STYLE)
    @is_owner_button
    async def get_games(self, button: disnake.ui.Button, inter: MessageInteraction):
        emb = get_game_emb(0)
        if emb:
            return await inter.response.send_message(view=GameView(1), embed=emb)

        return await inter.response.send_message("Игра не найдена")
