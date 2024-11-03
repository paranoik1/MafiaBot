import inspect

from disnake import Embed, Color, ApplicationCommandInteraction, File, Event
from disnake.ext import commands
from disnake.ext.commands import Bot

from ..config import GENERAL_COLOR
from ..mafia.utils import send_embed_role, get_all_roles_name
from ..texts import *
from ...store.config import YoomoneyConfig


class InfoCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener(Event.ready)
    async def ready(self):
        self.bot.owner = self.bot.get_user(self.bot.owner_id)
        await self.bot.owner.send("Бот готов к работе")

    @commands.Cog.listener(Event.error)
    async def error(self, error):
        print(error)

    async def send_embed(
            self: commands.Cog,
            inter: ApplicationCommandInteraction,
            *,
            title: str = None,
            description: str = None,
            fields: dict[str, str] = None,
            image: File = None,
            color: Color = None
    ):
        if not title:
            current_frame = inspect.currentframe()
            function_caller_name = inspect.getouterframes(current_frame, 2)[1].function
            title = self.__getattribute__(function_caller_name).description

        embed = Embed(title=title, color=color or GENERAL_COLOR, description=description)
        if image:
            embed.set_image(file=image)

        if fields:
            for field_title, field_content in fields.items():
                embed.add_field(field_title, field_content)

        await inter.send(embed=embed)

    @commands.slash_command(name="help", description="Инструкция по использованию")
    async def help(self, inter: ApplicationCommandInteraction):
        await self.send_embed(inter, fields=HELP_FIELDS)

    @commands.slash_command(name="author", description="Об авторе")
    async def author(self, inter: ApplicationCommandInteraction):
        await self.send_embed(inter, description=AUTHOR_TEXT)

    @commands.slash_command(name="game", description="Об игре \"Мафия\"")
    async def game(self, inter: ApplicationCommandInteraction):
        await self.send_embed(inter, description=GAME_TEXT)

    @commands.slash_command(name="subscription", description="Об платной подписке")
    async def subscription(self, inter: ApplicationCommandInteraction):
        await self.send_embed(inter, description=SUBSCRIPTION_TEXT.format(YoomoneyConfig.PRICE_USER_SUBSCRIPTION))

    @commands.slash_command(name="roles", description="Роли в игре")
    async def roles(
            self,
            inter: ApplicationCommandInteraction,
            role: str = commands.Param(
                name="роль", description="Роль", choices=get_all_roles_name()
            )
    ):
        await send_embed_role(inter, role)


def setup(bot):
    bot.add_cog(InfoCog(bot))
