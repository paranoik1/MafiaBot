import contextlib
import io
import traceback
from datetime import datetime

from disnake import Embed, Color
from disnake.ext import commands
from disnake.ext.commands import Context

from src.store.globals import SERVER_REPOSITORY
from ..config import START_TIME
from ..views.owner import StateView


class OwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command("state")
    async def state(self, ctx: Context):
        emb = Embed(title="Что с ботом", color=Color.red())
        emb.add_field("Кол-во серверов:", len(self.bot.guilds))
        emb.add_field("Кол-во игр:", len(SERVER_REPOSITORY))
        emb.add_field("Время работы:", str((datetime.now() - START_TIME).seconds) + " секунд")

        await ctx.send(view=StateView(), embed=emb)

    @commands.is_owner()
    @commands.command("code")
    async def execute_code(self, ctx: Context, *, python_code: str):
        if python_code.startswith("`"):
            code_splited = python_code.split("\n")
            code_splited.pop(0)
            code_splited.pop(-1)

            python_code = "\n".join(code_splited)

        try:
            with io.StringIO() as stdout, contextlib.redirect_stdout(stdout):
                exec(python_code, {'ctx': ctx, 'bot': self.bot})
                result = stdout.getvalue()

            await ctx.send(f"```\n{result}\n```")
        except:
            await ctx.send(f"Ошибка при выполнении кода:\n```python\n{traceback.format_exc()}\n```")



def setup(bot):
    bot.add_cog(OwnerCog(bot))
