from os import listdir
from random import choice
from typing import TYPE_CHECKING

from disnake import Embed, ApplicationCommandInteraction, User, ActionRow, Color, File
from disnake.ext.commands import Bot
from disnake.ui import Button

from src.bot.config import ROLES_INFO, GENERAL_COLOR, CARDS_URL, BUTTON_STYLE
from src.mafia.interfaces import IVote
from src.mafia.player import Player
from src.store.repository import Repository

if TYPE_CHECKING:
    from src.bot.mafia.server import MafiaDiscordServer


def get_pre_start_mafia_embed(server: "MafiaDiscordServer"):
    leader = server.leader
    leader_name = leader.global_name if leader.global_name else leader.name
    leader_avatar = leader.avatar.url if leader.avatar else leader.default_avatar

    embed = Embed(
        title="Мафия",
        description="Нажмите на кнопку, чтобы принять участие в игре",
        color=GENERAL_COLOR
    )

    players_string = ""
    for player in server.pre_players:
        players_string += "- " + player.username + "\n"

    embed.add_field(name="Участники", value=players_string)
    embed.set_author(name=leader_name, icon_url=leader_avatar)

    return embed


async def send_embed_role(inter: ApplicationCommandInteraction | User, role: str):
    role_info = ROLES_INFO[role]

    filename = role_info.image_file
    if filename.endswith("/"):
        filename = filename + "/" + choice(listdir("cards/" + filename))

    path = CARDS_URL + filename

    embed = Embed(
        title=role,
        color=role_info.color,
        description=role_info.description
    )
    embed.set_image(file=File(path))

    await inter.send(embed=embed)


def get_embed_voting(server: "MafiaDiscordServer", voting_instance: IVote, players: Repository[Player], description: str):
    info_vote = voting_instance.get_vote_info()

    embed = Embed(
        title="Голосование",
        description=description,
        color=Color.red()
    )

    for player in players:
        username = get_player_username(server.bot, player.id)

        players_voted = ""
        for _author, target in info_vote.items():
            if player.id == target.id:
                players_voted += f"- {_author.username}\n"

        embed.add_field(username, players_voted)

    return embed


def components_convert_list(components: list[ActionRow[Button]]) -> list[Button]:
    component_list = []
    for component in components[0].children:
        component_list.append(
            Button(style=component.style, label=component.label, custom_id=component.custom_id)
        )

    return component_list


def get_custom_id(*args):
    string_list = list(map(str, args))

    return "-".join(string_list)


def get_data_from_custom_id(custom_id: str):
    return custom_id.split("-")


def get_component_list_players(server: "MafiaDiscordServer", players: Repository[Player], custom_id_template: str) -> list[Button]:
    components = []
    for player in players:
        username = get_player_username(server.bot, player.id)

        button = Button(
            style=BUTTON_STYLE,
            label=username,
            custom_id=custom_id_template.format(player.id)
        )

        components.append(button)

    return components


def get_players_list_string(players: Repository[Player]):
    players_list_string = ""
    for player in players:
        players_list_string += f"- {player.username}\n"

    return players_list_string


def get_all_roles_name():
    return list(ROLES_INFO.keys())


def get_player_username(bot: Bot, user_id: int):
    user = bot.get_user(user_id)
    return user.global_name if user.global_name else user.name
