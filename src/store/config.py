from os import getenv, environ

from dotenv import load_dotenv

load_dotenv()


class MafiaConfig:
    MIN_PRIORITY = -2
    MAX_PRIORITY = 2

    MIN_PLAYERS = 1
    MAX_PLAYERS = 12

    MAX_PLAYERS_PREMIUM = 25
    DISCUSSION_TIME = 60


class DBConfig:
    URL_DATABASE = "sqlite+aiosqlite:///db.sqlite3"


class DiscordConfig:
    TOKEN = getenv("BOT_TOKEN")
    OWNER = int(getenv("OWNER_ID"))


class YoomoneyConfig:
    TOKEN = getenv("YOOMONEY_TOKEN")
    RECEIVER = getenv("YOOMONEY_RECEIVER")
    PRICE_USER_SUBSCRIPTION = 100
    PRICE_GUILD_SUBSCRIPTION = 300
