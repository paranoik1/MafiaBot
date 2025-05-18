from disnake import ApplicationCommandInteraction, Embed
from disnake.ext import commands
from disnake.ext.commands import Bot, BucketType

from src.bot.mafia.utils import get_player_username


class SupportCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.slash_command(
        name="send-owner",
        description="Предложить идею, указать на ошибку или посоветовать чего либо для улучшения бота",
        dm_permission=False
    )
    @commands.cooldown(1, 3600, BucketType.user)
    async def send_owner(
            self,
            inter: ApplicationCommandInteraction,
            content: str = commands.Param(
                name="сообщение",
                description="Сообщение"
            )
    ):
        avatar = inter.user.avatar
        guild = inter.guild

        await inter.send("Сообщение отправляется...", ephemeral=True)

        embed = Embed(description=content)
        if guild:
            embed.set_footer(text="Сервер: " + guild.name + " | " + str(guild.id), icon_url=guild.icon.url if guild.icon else None)
        embed.set_author(
            name=get_player_username(self.bot, inter.user.id),
            icon_url=avatar.url if avatar else inter.user.default_avatar
        )

        await self.bot.owner.send(embed=embed)
        await inter.edit_original_message("Сообщение отправлено!")


def setup(bot):
    bot.add_cog(SupportCog(bot))
