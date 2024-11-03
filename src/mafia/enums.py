from enum import StrEnum, IntEnum, Enum


class ServerState(Enum):
    DAY = 0
    NIGHT = 1


class TeamEnum(StrEnum):
    CIVILIAN = "Мирные жители"
    MAFIA = "Мафия"
    OTHER = "other"
    

class ActionNightEnum(IntEnum):
    DATE_NIGHT = 0
    RAPINE = 1
    KILL = 2
    GUARD = 3
    TREAT = 4
    INVESTIGATE = 5
    GUT = 6
    OBSERVATION = 7
    RETRIBUTION = 8
    AWAKENED = 9
