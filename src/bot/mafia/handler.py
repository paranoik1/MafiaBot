import asyncio
import io

from typing import TYPE_CHECKING

from disnake import Embed, MessageInteraction, User, VoiceClient, VoiceChannel, Event, Member, VoiceState, \
    FFmpegPCMAudio

from src.mafia.player import Player
from .decorators import is_voice_accompaniment, is_game_mode

from ..config import GENERAL_COLOR
from ...enums import GameMode
from ...store.config import MafiaConfig

if TYPE_CHECKING:
    from .server import MafiaDiscordServer


class Handler:
    def __init__(self, server: "MafiaDiscordServer"):
        self.server = server


class GameHandler(Handler):
    def __init__(self, server: "MafiaDiscordServer"):
        super().__init__(server)

        self.settings = self.server.settings

    async def get_other_user(self, inter: MessageInteraction, player: "Player", user: User) -> User:
        match self.settings.game_mode:
            case GameMode.MODERATOR:
                await inter.send(
                    f"Не удалось отправить роль игроку {user.mention}. "
                    f"Все сообщения для вас буду присылаться ведущему. "
                    f"Обращайтесь к нему"
                )
                user = self.server.leader
            case GameMode.AUTOMATIC:
                await inter.send(
                    f"Не удалось отправить роль игрока {player.username} пользователю {user.mention}. "
                    f"Откройте личные сообщения и упомините себя в "
                    f"этом чате или же упомините пользователя, который будет выступать "
                    f"посредником между ботом и тобой."
                )

                new_inter = await inter.bot.wait_for(
                    "message",
                    check=lambda i: user.id == i.user.id
                                    and i.channel.id == inter.channel_id
                                    and len(i.message.mentions) > 0
                )

                user = new_inter.message.mentions[0]
            case _:
                raise Exception("Неизвестный режим")

        return user

    @is_game_mode(GameMode.MODERATOR)
    async def after_send_roles(self):
        leader_embed = Embed(
            title="Роли участников",
            color=GENERAL_COLOR,
            description="\n".join([f"- {player.username} - **{player.role}**" for player in self.server.players])
        )

        await self.server.leader.send(embed=leader_embed)

    def edit_embed_results_voting(self, target: "Player", embed: Embed):
        if not self.settings.revealed_roles_mode:
            return embed

        embed.description += f"\n Его роль - **{target.role}**."
        return embed

    def get_player_line(self, player: "Player"):
        line = f"- {player.username}"
        if self.settings.revealed_roles_mode:
            line += f" - **{player.role}**"

        return line

    @is_game_mode(GameMode.MODERATOR)
    async def send_leader_message(self, message: str):
        await self.server.leader.send(message)

    @is_game_mode(GameMode.AUTOMATIC)
    async def automate_night(self):
        await self.server.exec_night(self.server.channel_interaction)

    @is_game_mode(GameMode.AUTOMATIC)
    async def wait_discussion_time(self):
        embed = Embed(
            title="Обсуждение",
            description=f"У вас есть {MafiaConfig.DISCUSSION_TIME} секунд на обсуждение, после чего начнется голосование",
            color=GENERAL_COLOR
        )

        await self.server.channel_interaction.send(embed=embed)

        await asyncio.sleep(MafiaConfig.DISCUSSION_TIME)

        await self.server.exec_voting(self.server.channel_interaction)


class VoiceHandler(Handler):
    def __init__(self, server: "MafiaDiscordServer"):
        super().__init__(server)

        self.bot = self.server.channel_interaction.bot
        self.voice_client: VoiceClient | None = None
        self.connected_players: list[int] = []

    @is_voice_accompaniment
    async def create_voice(self):
        guild = self.bot.get_guild(self.server.id)

        voice_channel = await guild.create_voice_channel(name="Мафия")
        self.voice_client = await voice_channel.connect()

        everyone_role = voice_channel.guild.default_role

        await voice_channel.set_permissions(everyone_role, connect=False)

        for player in self.server.players:
            member = guild.get_member(player.id)
            await voice_channel.set_permissions(member, connect=True)

        await self.server.channel_interaction.send(
            "Подключайтесь к голосовому каналу "
            "(нужно подключиться всем игрокам, иначе игра не начнется)\n"
            + voice_channel.mention
        )

    @is_voice_accompaniment
    async def delete_voice(self):
        await self.voice_client.channel.delete()

    @is_voice_accompaniment
    @is_game_mode(GameMode.AUTOMATIC)
    async def wait_players(self):
        await self.bot.wait_for(
            Event.voice_state_update,
            check=self._is_all_players_connected_voice_channel
        )

        await self.server.channel_interaction.send("Все игроки в сборе! Приступаем к игре.")

    def _is_mafia_voice(self, channel: VoiceChannel | None):
        return self.voice_client and channel.id == self.voice_client.channel.id

    def _is_all_players_connected_voice_channel(
            self, member: Member, before: VoiceState, after: VoiceState
    ):
        if self.server.is_started:
            return
        if after.channel == before.channel:
            return
        
        player_list = [player.id for player in self.server.players]

        if after.channel is not None:
            if member.id in player_list and self._is_mafia_voice(after.channel):
                self.connected_players.append(member.id)
                asyncio.create_task(
                    self.server.channel_interaction.send(
                        member.mention + " присоединился"
                    )
                )
        elif before.channel is not None:
            if member.id in player_list and self._is_mafia_voice(before.channel) and member.id in self.connected_players:
                self.connected_players.remove(member.id)
                asyncio.create_task(
                    self.server.channel_interaction.send(
                        member.mention + " отключился"
                    )
                )

        self.connected_players.sort()
        player_list.sort()

        return self.connected_players == player_list

    def _play(self, source: str | io.BufferedIOBase, *args, **kwargs):
        if self.voice_client.is_playing():
            self.voice_client.stop()

        source = FFmpegPCMAudio(source, *args, **kwargs)

        self.voice_client.play(source)

    @is_voice_accompaniment
    async def play_ready(self):
        self._play("audio/ready.ogg")
        await asyncio.sleep(13)

    @is_voice_accompaniment
    async def play_result_night_and_discussion(self):
        self._play("audio/day.ogg")
        await asyncio.sleep(10)

    @is_voice_accompaniment
    def play_voting(self):
        self._play("audio/voting.ogg")

    @is_voice_accompaniment
    async def play_result_voting(self):
        self._play("audio/result_voting.ogg")
        await asyncio.sleep(8)

    @is_voice_accompaniment
    def play_night(self):
        self._play("audio/night.ogg")

    @is_voice_accompaniment
    async def play_win(self):
        self._play("audio/win.ogg")
        await asyncio.sleep(20)
