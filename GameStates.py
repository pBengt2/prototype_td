from enum import Enum


class GameState(Enum):
    MENU = 0
    VERSUS = 1
    PVE = 2


class RoundState(Enum):
    PAUSE = 0
    PREP = 1
    ROUND = 2
    POST = 3


class RoundInfo:
    def __init__(self, round_number, units, prep_seconds):
        self.round_number = round_number
        self.prep_ticks = prep_seconds * 60
        self.units = units
        self.units_summoned = 0
        self.units_remaining = self.units


class PlayerInfo:
    def __init__(self):
        self.health = 10
        self.gold = 50
