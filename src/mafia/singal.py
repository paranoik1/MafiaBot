import logging
from typing import Coroutine


logger = logging.getLogger(__name__)


class Signal:
    def __init__(self):
        self.handlers = []

    def __call__(self, func):
        self.subscribe(func)

        return func

    def unsubscribe(self, func: Coroutine):
        if func not in self.handlers:
            logger.warning(f'Функции нет в handlers: {func.__name__}')
            return
        
        self.handlers.remove(func)

    def subscribe(self, func):
        self.handlers.append(func)

    async def emit(self, *args, **kwargs):
        for handler in self.handlers:
            await handler(*args, **kwargs)


class ServerSignals:
    def __init__(self):
        self.on_death_player = Signal()
        self.on_killed_player = Signal()
        self.on_imprison_player = Signal()
        self.on_change_server_state = Signal()
        self.on_witness_saw_killer = Signal()
        self.on_kamikaze_found_commissar = Signal()
        self.on_necromancer_awakened_player = Signal()
        self.on_awakened_player_sleep = Signal()
