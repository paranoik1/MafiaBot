from enum import StrEnum


class PremiumType(StrEnum):
    USER = "user"
    GUILD = "guild"


class GameMode(StrEnum):
    MODERATOR = "Режим с ведущем"
    AUTOMATIC = "Автоматический режим"
