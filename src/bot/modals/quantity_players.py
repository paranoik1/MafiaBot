import disnake
from disnake.ui import Modal

from disnake import ModalInteraction

from src.mafia.settings import Settings
from src.store.config import MafiaConfig


class QuantityPlayersModal(Modal):
    def __init__(self, settings: Settings):
        self.settings = settings

        borders_text = f"(границы {MafiaConfig.MIN_PLAYERS}-{MafiaConfig.MAX_PLAYERS_PREMIUM})"

        components = [
            disnake.ui.TextInput(
                label="Минимальное число игроков " + borders_text,
                custom_id="minimum_players",
                max_length=2,
                placeholder=str(self.settings.minimum_players)
            ),
            disnake.ui.TextInput(
                label="Максимальное число игроков " + borders_text,
                custom_id="maximum_players",
                max_length=2,
                placeholder=str(self.settings.maximum_players)
            )
        ]

        super().__init__(title="Кол-во игроков", components=components, custom_id="quantity_players_modal")

    async def callback(self, inter: ModalInteraction) -> None:
        data = inter.text_values
        if not data["maximum_players"].isdigit() or not data["minimum_players"].isdigit():
            return await inter.send(f"Нужно вписать число", ephemeral=True)


        is_succes, error_message = self.settings.update_quantity_players(
            int(data["maximum_players"]),
            int(data["minimum_players"])
        )

        if not is_succes:
            return await inter.send(f"{error_message} Настройки не были сохранены..", ephemeral=True)

        return await inter.send(f"Настройки игры обновлены!", ephemeral=True)

