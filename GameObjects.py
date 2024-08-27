from enum import Enum

import Defaults as Defaults
import DrawUtils as DrawUtils
import MathUtils

from DrawUtils import Colors
from DrawUtils import Shapes


class ObjectType(Enum):
    TOWER = 0
    UNIT = 1
    PROJECTILE = 2
    CARD = 3
    TILE = 4
    NOT_IMPLEMENTED = 5
    INVALID = 6


class GameObject:
    def __init__(self, location=None, visible=False):
        self._visible = visible
        self._location = location  # if None use tile location
        self._visual_location = location
        self._color = Colors.GRAY
        self._shape = Shapes.CIRCLE
        self._size = Defaults.DEFAULT_OBJ_SIZE
        self._tile = None
        self._object_type = ObjectType.INVALID
        self._hovered = False

    def initialize(self):
        pass

    def debug_get_tile(self):
        return self._tile

    def get_type(self):
        return self._object_type

    def get_visible_location(self):
        return self._visual_location

    def is_visible(self):
        return self._visible

    def set_visible(self, visible=True):
        self._visible = visible

    def add_mouse_hover(self):
        self._hovered = True

    def remove_mouse_hover(self):
        self._hovered = False

    def get_center_location(self):
        if self._location is None and self._tile is not None:
            return self._tile.get_center_location()

        if self._location is not None:
            if self._shape == Shapes.CIRCLE:
                loc = self.get_location()
                return loc[0] + (self._size/2), loc[1] + (self._size/2)
            elif self._shape == Shapes.RECT:
                loc = self.get_location()
                return loc[0] + (self._size[0]/2), loc[1] + (self._size[1]/2)
            print("TODO: center location not implemented...")
        return self.get_location()

    def set_location(self, new_location):
        self._location = new_location

    def get_location(self):
        if self._location is None and self._tile is not None:
            return self._tile.get_location()
        return self._location

    def check_collision(self, pos):
        # Can potentially cache collision areas for performance improvement...
        if self.get_location() is None:
            return False
        if self._shape == Shapes.CIRCLE:
            return MathUtils.distance(self.get_center_location(), pos) < self._size
        elif self._shape == Shapes.RECT:
            x1, y1 = self.get_location()
            x2 = x1 + self._size[0]
            y2 = y1 + self._size[1]
            x, y = pos
            return x1 < x < x2 and y1 < y < y2
        print(str(self._shape) + " collision not implemented...")
        return False

    def is_draggable(self):
        return False

    def is_clickable(self):
        return False

    def set_color(self, color):
        self._color = color

    def set_shape(self, shape, size):
        self._shape = shape
        self._size = size

    def draw_object(self, screen):
        DrawUtils.draw_shape(screen, self.get_location(), self.get_center_location(), self._shape, self._size, self._color)

    def verify_tile(self):
        if self._tile is not None:
            if self not in self._tile.debug_get_objects():
                print("Err: invalid tile...")

    def set_tile(self, tile):
        self._tile = tile

    def is_tickable(self):
        return False

    def gameplay_tick(self):
        pass

    def visual_tick(self):
        pass

    def standard_click(self):
        print("base game obj clicked...")
