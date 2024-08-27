from enum import Enum
import random

import Defaults as Defaults
import GameObjects as GameObjects
import Towers
from DrawUtils import Shapes


class Deck:
    def __init__(self):
        self._base_card_list = []
        self._max_cards = 30

        self._current_card_list = []

    def draw_card(self):
        return self._current_card_list.pop()

    def shuffle_cards(self):
        random.shuffle(self._current_card_list)


class CardIDs(Enum):
    StompCard = 0
    ProjectileCard = 1


class BaseCard(GameObjects.GameObject):
    def __init__(self, location=None, visible=False):
        GameObjects.GameObject.__init__(self, location, visible)
        self._shape = Shapes.RECT
        self._size = (Defaults.DEFAULT_OBJ_SIZE*3, Defaults.DEFAULT_OBJ_SIZE*4)
        self._start_loc = location
        self._held = False
        self._object_type = GameObjects.ObjectType.CARD

    def initialize(self):
        print("err initializing base card")
        exit(-1)

    def is_draggable(self):
        return True

    def is_clickable(self):
        return True

    def standard_click(self):
        self._held = True

    def set_location(self, loc, update_start=True):
        self._location = loc
        self._start_loc = loc

    def get_start_loc(self):
        return self._start_loc

    def click_release(self):
        self._location = self._start_loc
        self._held = False

    def visual_tick_held(self, held_loc):
        self._location = (held_loc[0] - self._size[0]/2, held_loc[1] - self._size[1]/2)

    def get_tower_type(self):
        print("base card get_tower_type")
        exit(-1)
        return None


class MazeCard(BaseCard):
    def __init__(self, location=None, visible=False):
        BaseCard.__init__(self, location=location, visible=visible)
        self._color = Towers.MazeTower.COLOR

    def get_tower_type(self):
        return Towers.MazeTower


class StompCard(BaseCard):
    def __init__(self, location=None, visible=False):
        BaseCard.__init__(self, location=location, visible=visible)
        self._color = Towers.StompTower.COLOR

    def get_tower_type(self):
        return Towers.StompTower


class ShootCard(BaseCard):
    def __init__(self, location=None, visible=False):
        BaseCard.__init__(self, location=location, visible=visible)
        self._color = Towers.ShootTower.COLOR

    def get_tower_type(self):
        return Towers.ShootTower
