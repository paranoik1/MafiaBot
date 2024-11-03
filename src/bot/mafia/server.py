import asyncio
from asyncio import gather

import disnake
from disnake import Guild, Interaction, MessageInteraction

from src.bot.mafia.team import MafiaTeamDiscord, ActiveTeamDiscord
from src.bot.mafia.utils import *
from src.mafia.active_player import ActivePlayer
from src.mafia.enums import TeamEnum
from src.mafia.player import PrePlayer, Player
from src.mafia.roles import Witness, Necromancer
from src.mafia.server import Server
from src.store.config import MafiaConfig
from src.store.repository import Repository
from src.store.utils import add_server, remove_server

from .handler import GameHandler, VoiceHandler
from ..texts import DESCRIPTION_VOTING


class MafiaDiscordServer(Server):
    def __init__(self, guild: Guild, leader: User, channel_interaction: Interaction):
        super().__init__()

        self.pre_players = Repository[PrePlayer]()
        self.channel_interaction = channel_interaction
        self.bot = channel_interaction.bot
        self.leader = leader
        self.id = guild.id

        self.is_started = False

        self.active_teams[TeamEnum.MAFIA] = MafiaTeamDiscord(self)

        self._repository_discord_user = Repository[User]()

        self._game_handler = GameHandler(self)
        self._voice_handler = VoiceHandler(self)

        self._game_task = None

        self.night_players_choose = Repository[Player]()
        self.night_team_choose: list[ActiveTeamDiscord] = []

        self._killed_players = []

        self.night_priority = MafiaConfig.MIN_PRIORITY

        add_server(guild.id, self)

        self.signals.on_killed_player.subscribe(self.on_killed_player)
        self.signals.on_witness_saw_killer.subscribe(self.on_witness_saw_killer)
        self.signals.on_necromancer_awakened_player.subscribe(self.on_necromancer_awakened_player)

    async def on_necromancer_awakened_player(self, necromancer: Necromancer, player: Player):
        necromancer_user = self._repository_discord_user.get(necromancer.id)
        self._repository_discord_user.set(player.id, necromancer_user)

    def add_discord_user(self, user_id: int, user: User):
        self._repository_discord_user.add(user_id, user)

    def get_discord_user(self, user_id: int) -> User:
        return self._repository_discord_user.get(user_id)

    async def day(self):
        await super().day()
        self.night_priority = MafiaConfig.MIN_PRIORITY
        self.night_players_choose = []
        self.night_team_choose = []

    def check_night_step_choosed(self):
        return not (bool(self.night_players_choose) or bool(self.night_team_choose))

    async def send_input_active_role(self, player: ActivePlayer):
        user = self.get_discord_user(player.id)
        role_info = ROLES_INFO[player.role]

        embed = Embed(title="Выбор", color=GENERAL_COLOR)
        if role_info.embed_description:
            embed.description = role_info.embed_description

        buttons = self._create_buttons_player(player)

        await user.send(embed=embed, components=buttons)

    def _create_buttons_player(self, author: ActivePlayer):
        players = author.get_target_list()

        btns = []
        for player in players:
            button = Button(
                style=BUTTON_STYLE,
                label=get_player_username(self.bot, player.id),
                custom_id=f"select-{self.id}-{author.id}-{player.id}"
            )

            btns.append(button)

        return btns

    async def night_step(self):
        self.night_priority += 1

        self.night_players_choose = self.get_active_night_players(self.night_priority)
        self.night_team_choose = []

        for team in self.active_teams.values():
            players_team = team.get_players_participating_in_voting()
            if len(players_team) > 0 and players_team[0].priority == self.night_priority:
                self.night_team_choose.append(team)

        if self.night_team_choose:
            self.night_team_choose = self.night_team_choose
            await asyncio.gather(*[team.start_vote() for team in self.night_team_choose])

        if self.night_players_choose:
            await asyncio.gather(*[self.send_input_active_role(player) for player in self.night_players_choose])

        if not self.night_players_choose and not self.night_team_choose:
            if self.night_priority > MafiaConfig.MAX_PRIORITY:
                await self.results_night()
            else:
                await self.night_step()

    async def on_killed_player(self, player: Player):
        self._killed_players.append(player)

    async def on_witness_saw_killer(self, witness: Witness, killer: ActivePlayer, target: Player):
        user = self.get_discord_user(witness.id)

        await user.send(f"Вы увидели, как {killer.username} убил {target.username}")

    async def check_win(self):
        team = super().check_win()
        if not team:
            return False

        embed = Embed(title="Конец игры", color=GENERAL_COLOR, description="")

        if team.title == TeamEnum.OTHER:
            player = team.get_players_alive()[0]
            embed.description = f"В этой игре одержал победу {player.role} {player.username}"
        else:
            embed.description = f"В этой игре одержала победу команда **'{team.title}'**"

        players_alive = get_players_list_string(self.get_players_alive())

        embed.add_field("Выжившие игроки:", players_alive)

        await self.channel_interaction.send(embed=embed)
        await self._voice_handler.play_win()

        await self.stop()

        return True

    async def results_night(self):
        await self.process_night_events()

        embed = Embed(title="Итоги ночи", color=GENERAL_COLOR)

        self._killed_players = [player for player in self._killed_players if not player.is_alive]

        field_value = "Сегодня ночью никого не убили"
        if self._killed_players:
            field_value = "Сегодня ночью были убиты:\n"
            field_value += '\n'.join(
                self._game_handler.get_player_line(player) for player in self._killed_players
            )

        self._killed_players.clear()

        embed.add_field("Убийства", field_value)

        if not await self.__general_end_results(embed):
            await self._voice_handler.play_result_night_and_discussion()

            await self._game_handler.wait_discussion_time()

    async def results_voting(self):
        targets = self.get_result_voting()
        if len(targets) > 1:
            return False

        target = targets[0]
        await target.imprison()

        embed = Embed(
            title="Итоги голосования",
            color=GENERAL_COLOR,
            description="По итогу голосования в тюрьму был посажен {}".format(target.username)
        )

        embed = self._game_handler.edit_embed_results_voting(target, embed)

        if not await self.__general_end_results(embed):
            await self._voice_handler.play_result_voting()

            await self._game_handler.automate_night()

        return True

    async def __general_end_results(self, embed: Embed):
        players_alive = get_players_list_string(self.get_players_alive())
        embed.add_field("Выжившие игроки:", players_alive)

        await self.channel_interaction.send(embed=embed)
        return await self.check_win()

    async def start(self, inter: MessageInteraction):
        role_counts = self.settings.get_roles_count(len(self.pre_players))
        players = self.distribute_roles(self.pre_players.to_list(), role_counts)

        async def send_role(player: Player):
            user = inter.bot.get_user(player.id)

            while True:
                try:
                    await send_embed_role(user, player.role)
                    break
                except disnake.errors.Forbidden:
                    user = await self._game_handler.get_other_user(
                        inter, player, user
                    )

            self.add_discord_user(player.id, user)

        await gather(*[send_role(player) for player in players])

        for active_team in self.active_teams.values():
            await active_team.send_team_roles()

        await self._game_handler.after_send_roles()

        embed = Embed(
            title="Роли распределены",
            description="Роли отправленны в личные сообщения",
            color=GENERAL_COLOR
        )
        await inter.send(embed=embed)

        self._game_task = asyncio.current_task()

        await self._voice_handler.create_voice()
        await self._voice_handler.wait_players()

        self.is_started = True

        await self._voice_handler.play_ready()

        await self._game_handler.automate_night()

    async def stop(self):
        remove_server(self.id)

        await self._voice_handler.delete_voice()
        self._game_task.cancel()

    async def exec_night(self, inter: Interaction):
        self._voice_handler.play_night()

        await self.night()

        embed = Embed(
            title="Ночь",
            description="Наступает ночь. Город засыпает. Просыпаются активные роли. Ждите своего часа остальные.",
            color=GENERAL_COLOR
        )

        await inter.send(embed=embed)

        await self.night_step()

    async def exec_voting(self, inter: Interaction):
        await self.day()

        self._voice_handler.play_voting()

        players = self.get_players_participating_in_voting()
        embed = get_embed_voting(
            server=self,
            voting_instance=self,
            players=players,
            description=DESCRIPTION_VOTING
        )
        components = get_component_list_players(
            server=self,
            players=self.get_players_participating_in_voting(),
            custom_id_template=get_custom_id("vote", self.id, "author_id", "{}")
        )

        await inter.send(embed=embed, components=components)
