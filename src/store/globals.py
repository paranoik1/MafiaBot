from src.mafia.server import Server
from src.store.repository import Repository


SERVER_REPOSITORY = Repository[Server]()

COOLDOWN = 2
COOLDOWN_LIST = []
