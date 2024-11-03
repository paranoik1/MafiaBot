from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .server import Server
    from .teams import Team


class PrePlayer:
    def __init__(self, id: int, username: str):
        self.id = id
        self.username = username

    def __repr__(self):
        return "<%s: username=%s>" % (self.__class__.__name__, self.username)

    def __eq__(self, other):
        if not other:
            return False

        return other.id == self.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)


class Player(PrePlayer):
    ROLE = ""

    def __init__(self, id: int, username: str, server: "Server", team: "Team"):
        super().__init__(id, username)

        self.server = server
        self.role = self.ROLE

        self.killer: Player | None = None
        self.is_alive = True
        self.is_can_vote = True
        self.acquitted = False

        self._team = team
        team.add_player(id, self)

    @property
    def team(self):
        return self._team

    @team.setter
    def team(self, new_team: "Team"):
        self.team.players.remove(self.id)
        new_team.add_player(self.id, self)

        self._team = new_team

    async def kill(self, killer: "Player"):
        self.killer = killer
        await self.die()
        await self.server.signals.on_killed_player.emit(self)

    async def imprison(self):
        await self.die()
        await self.server.signals.on_imprison_player.emit(self)

    async def die(self):
        self.is_alive = False
        await self.server.signals.on_death_player.emit(self)
