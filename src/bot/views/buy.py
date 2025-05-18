import disnake
from disnake import MessageInteraction, Embed, ButtonStyle
from disnake.ui import View, Button

from src.bot.config import GENERAL_COLOR
from src.bot.texts import INSTRUCTION_BUY_TEXT
from src.enums import PremiumType
from src.payment import *


class BuyPremiumView(View):
    @disnake.ui.button(label="Личная премиум-версия", style=disnake.ButtonStyle.green)
    async def personal_version(self, button: Button, inter: MessageInteraction):
        await self.__buy_method(
            inter,
            button.label,
            YoomoneyConfig.PRICE_USER_SUBSCRIPTION,
            inter.user.id,
            PremiumType.USER
        )

    @disnake.ui.button(label="Премиум-версия для сервера", style=disnake.ButtonStyle.blurple)
    async def guild_version(self, button: Button, inter: MessageInteraction):
        if inter.guild_id is None:
            return await inter.send("Чтобы приобрести подписку для сервера, необходима проводить операцию на сервере, подписку для которого вы хотите приобрести", ephemeral=True)
        
        await self.__buy_method(
            inter,
            button.label,
            YoomoneyConfig.PRICE_GUILD_SUBSCRIPTION,
            inter.guild_id,
            PremiumType.GUILD
        )

    async def __buy_method(
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
            Button(label="Проверить", custom_id="check-" + label + "-" + type, style=ButtonStyle.danger) #  + "-" + str(inter.author.id)
        ]

        await inter.send(embed=embed, components=components, ephemeral=True)