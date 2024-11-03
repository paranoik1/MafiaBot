from disnake import ApplicationCommandInteraction, Embed, Event, MessageInteraction
from disnake.ext import commands

from src.bot.config import GENERAL_COLOR
from src.bot.mafia.utils import get_data_from_custom_id
from src.bot.texts import BUY_TEXT, PAYMENT_SUCCESS_TEXT
from src.bot.views.buy import BuyPremiumView
from src.db.engine import insert_premium, get_premium
from src.enums import PremiumType
from src.payment.utils import check_pay
from src.store.config import YoomoneyConfig


class PaymentCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="buy", description="Приобрести премиум версию")
    async def buy(self, inter: ApplicationCommandInteraction):
        embed = Embed(
            title="Премиум версия",
            color=GENERAL_COLOR,
            description=BUY_TEXT.format(
                user_price=YoomoneyConfig.PRICE_USER_SUBSCRIPTION,
                guild_price=YoomoneyConfig.PRICE_GUILD_SUBSCRIPTION
            )
        )

        await inter.send(embed=embed, view=BuyPremiumView())

    @commands.Cog.listener(Event.button_click)
    async def check_payment(self, inter: MessageInteraction):
        data = get_data_from_custom_id(inter.data.custom_id)
        if data[0] != "check":
            return

        await inter.response.defer()

        label, type, author_id = data[1:]

        if str(inter.author.id) != author_id:
            return await inter.send("Данную операцию продолжить может только человек, запустивший данную команду", ephemeral=True)
        
        premium_id = inter.user.id if type == PremiumType.USER else inter.guild_id

        if await get_premium(premium_id):
            return await inter.send("Вы уже есть в базе", ephemeral=True)

        is_success = await check_pay(label)
        if is_success:
            return await self.payment_success(inter, premium_id, type)

        await inter.send("Не оплачено", ephemeral=True)

    async def payment_success(self, inter: MessageInteraction, id: int, type: PremiumType):
        await insert_premium(id, type)

        embed = Embed(
            title="Вы приобрели платную версию бота!",
            description=PAYMENT_SUCCESS_TEXT
        )

        await inter.edit_original_message(embed=embed)


def setup(bot):
    bot.add_cog(PaymentCog(bot))
