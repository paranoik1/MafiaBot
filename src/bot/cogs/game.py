from types import NoneType

from disnake import MessageInteraction, Event, Member, VoiceState
from disnake.ext import commands

from src.bot.mafia.decorators import *
from src.bot.mafia.utils import *
from src.bot.texts import DESCRIPTION_VOTING
from src.bot.views.pre_start_view import PreStartMafiaView
from src.mafia.active_player import ActiveTeamPlayer
from src.mafia.enums import ServerState
from src.mafia.player import Player
from src.store.utils import remove_server, get_server, start_cooldown, is_cooldown
from src.bot.mafia.server import MafiaDiscordServer


class GameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="start-mafia", description="Начать игру")
    @is_server_exists(text_error="Игра уже существует", is_true=False)
    async def start_mafia(self, inter: ApplicationCommandInteraction, server: NoneType):
        server = MafiaDiscordServer(inter.guild, inter.user, inter)
        embed = get_pre_start_mafia_embed(server)

        await inter.send(
            embed=embed,
            view=PreStartMafiaView(),
        )

    @commands.slash_command(name="voting", description="Начать голосование")
    @is_server_exists()
    @is_leader
    @is_game_started()
    async def voting(self, inter: ApplicationCommandInteraction, server: MafiaDiscordServer):
        await server.exec_voting(inter)

    @commands.slash_command(name="night", description="Начать ночь")
    @is_server_exists()
    @is_leader
    @is_game_started()
    async def night(self, inter: ApplicationCommandInteraction, server: MafiaDiscordServer):
        await server.exec_night(inter)

    @commands.slash_command(name="stop-mafia", description="Закончить игру")
    @is_server_exists("Игра не найдена")
    @is_leader
    async def stop_mafia(self, inter: ApplicationCommandInteraction, server: MafiaDiscordServer):
        try:
            await server.channel_interaction.delete_original_message()
        except:
            pass

        await server.stop()

        await inter.send("Игра принудительно окончена")

    # EVENTS
    # @commands.Cog.listener(Event.message)
    # async def active_chat_message(self, message: Message):
    #     if message.channel.type != ChannelType.private:
    #         return
    @commands.Cog.listener(Event.button_click)
    async def active_role_selected(self, inter: MessageInteraction):
        data = get_data_from_custom_id(inter.data.custom_id)

        if data[0] != "select":
            return

        if is_cooldown(inter.user.id):
            return await inter.send(
                "Вы слишком часто используете данную функцию",
                ephemeral=True
            )

        print(data)

        server_id, author_id, target_id = data[1:]

        server: MafiaDiscordServer = get_server(int(server_id))
        if not server:
            return await inter.send("Игра не найдена", ephemeral=True)

        start_cooldown(inter.user.id)

        players_alive = server.get_players_alive()
        author = players_alive.get(int(author_id))

        targets_list = author.get_target_list()
        target = targets_list.get(int(target_id))

        if not author:
            return await inter.send("Вы мертвы или не являетесь участником игры", ephemeral=True)

        if not author.is_valid(target):
            return await inter.send("Вы не можете выбрать данного игрока")

        night_event = await author.try_new_night_event(target)
        if night_event and night_event.data is not None:
            await inter.send(str(night_event.data))

        role_info = ROLES_INFO[author.role]

        await inter.message.delete()

        if role_info.message_for_author:
            await inter.send(role_info.message_for_author.format(target.username))
        if role_info.message_for_leader:
            await server._game_handler.send_leader_message(role_info.message_for_leader.format(target.username))

        server.night_players_choose.remove(author.id)

        if server.check_night_step_choosed():
            await server.night_step()

    @commands.Cog.listener(Event.button_click)
    async def vote(self, inter: MessageInteraction):
        data = get_data_from_custom_id(inter.data.custom_id)
        if data[0] != "vote":
            return

        if is_cooldown(inter.user.id):
            return await inter.send(
                "Вы слишком часто используете данную функцию",
                ephemeral=True
            )

        print(data)
        server_id, author_id, target_id = data[1:4]
        if author_id == "author_id":
            author_id = inter.user.id

        server: MafiaDiscordServer = get_server(int(server_id))
        if not server:
            return await inter.send("Игра не найдена", ephemeral=True)

        players_alive = server.get_players_alive()

        author = players_alive.get(int(author_id))
        target = players_alive.get(int(target_id))

        if not author:
            return await inter.send("Вы мертвы или не являетесь участником игры", ephemeral=True)

        await inter.response.defer()

        if len(data) == 5:
            team = data[4]
            await self._active_team_player_vote(
                server=server,
                author=author,
                target=target,
                team=team
            )
        else:
            await self._player_vote(
                inter=inter,
                server=server,
                author=author,
                target=target
            )

    async def _player_vote(
            self,
            inter: MessageInteraction,
            server: MafiaDiscordServer,
            author: ActiveTeamPlayer,
            target: Player
    ):
        if server.state != ServerState.DAY:
            return

        server.vote(author, target)

        if server.is_all_players_voted():
            is_success = await server.results_voting()
            if is_success:
                return await inter.delete_original_response()

        players = server.get_players_participating_in_voting()
        embed = get_embed_voting(
            server=server,
            voting_instance=server,
            players=players,
            description=DESCRIPTION_VOTING
        )

        await inter.message.edit(embed=embed, components=components_convert_list(inter.message.components))

    async def _active_team_player_vote(
            self,
            server: MafiaDiscordServer,
            author: ActiveTeamPlayer,
            target: Player,
            team: str
    ):
        if server.state != ServerState.NIGHT:
            return

        author.vote(target)

        active_team = server.active_teams[team]

        await active_team.update_info_voting()
        await active_team.process_end_voting()

        if server.check_night_step_choosed():
            await server.night_step()


def setup(bot):
    bot.add_cog(GameCog(bot))
