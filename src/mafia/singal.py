class Signal:
    def __init__(self):
        self.handlers = []

    def __call__(self, func):
        self.subscribe(func)

        return func

    def unsubscribe(self, func):
        self.handlers.remove(func)

    def subscribe(self, func):
        self.handlers.append(func)

    async def emit(self, *args, **kwargs):
        for handler in self.handlers:
            await handler(*args, **kwargs)


class ServerSignals:
    on_death_player = Signal()
    on_killed_player = Signal()
    on_imprison_player = Signal()
    on_change_server_state = Signal()
    on_witness_saw_killer = Signal()
    on_kamikaze_found_commissar = Signal()
    on_necromancer_awakened_player = Signal()
    on_awakened_player_sleep = Signal()
