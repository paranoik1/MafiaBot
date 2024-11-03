import disnake
from disnake import MessageInteraction, Embed, ButtonStyle
from disnake.ui import View, Button

from src.bot.config import GENERAL_COLOR
from src.bot.texts import INSTRUCTION_BUY_TEXT
from src.enums import PremiumType
from src.payment import *


class BuyPremiumView(View):
    async def __general_buy_method(
            self,
            inter: MessageInteraction,
            title: str,
            price: int,
            id: int,
            type: PremiumType
    ):
        embed = Embed(
            title=title,
            color=GENERAL_COLOR,
            description=INSTRUCTION_BUY_TEXT
        )

        await inter.response.defer()

        label = generate_label(id)
        link_pay = await get_link_pay(label, price)

        components = [
            Button(label="Оплатить", style=ButtonStyle.green, url=str(link_pay)),
            Button(label="Проверить", custom_id="check-" + label + "-" + type + "-" + str(inter.author.id), style=ButtonStyle.danger)
        ]

        await inter.edit_original_message(embed=embed, components=components)

    @disnake.ui.button(label="Личная премиум-версия", style=disnake.ButtonStyle.green)
    async def personal_version(self, button: Button, inter: MessageInteraction):
        await self.__general_buy_method(
            inter,
            button.label,
            YoomoneyConfig.PRICE_USER_SUBSCRIPTION,
            inter.user.id,
            PremiumType.USER
        )

    @disnake.ui.button(label="Премиум-версия для сервера", style=disnake.ButtonStyle.blurple)
    async def guild_version(self, button: Button, inter: MessageInteraction):
        await self.__general_buy_method(
            inter,
            button.label,
            YoomoneyConfig.PRICE_GUILD_SUBSCRIPTION,
            inter.guild_id,
            PremiumType.GUILD
        )

