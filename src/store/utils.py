import asyncio
from typing import Any

from disnake import User

from src.mafia.server import Server
from .globals import SERVER_REPOSITORY, COOLDOWN_LIST, COOLDOWN


def get_server(id: int) -> Server:
    return SERVER_REPOSITORY.get(id)


def add_server(id: int, server: Server):
    SERVER_REPOSITORY.add(id, server)


def remove_server(id: int):
    SERVER_REPOSITORY.remove(id)


async def stop_cooldown(target: Any):
    await asyncio.sleep(COOLDOWN)
    COOLDOWN_LIST.remove(target)


def start_cooldown(target: Any):
    COOLDOWN_LIST.append(target)
    asyncio.create_task(stop_cooldown(target))


def is_cooldown(target: Any) -> bool:
    return target in COOLDOWN_LIST
