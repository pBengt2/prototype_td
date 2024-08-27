import Defaults as Defaults
import GameObjects as GameObjects
import MathUtils as Math

from DrawUtils import Colors
from Grid import Direction


class Unit(GameObjects.GameObject):
    def __init__(self, health=100, speed=10.0, location=None, visible=False, death_event=None, end_tile_event=None):
        GameObjects.GameObject.__init__(self, location, visible)
        self._end_tile_event = end_tile_event  # TODO: Should be an event triggered from the end tile itself...?
        self._death_event = death_event
        self._direction = Direction.DOWN
        self._tile_queue = []
        self._object_type = GameObjects.ObjectType.UNIT
        self._color = Colors.BLUE

        self._gold_value = 1

        self._move_speed = min(speed, Defaults.DEFAULT_UNIT_SIZE)  # TODO: Moving faster than tile size not tested/supported.

        self._health = health
        self._active = False

        self._prev_tile = None

    def initialize(self):
        self.find_path()
        self._active = True

    def trigger_death(self):
        self._active = False
        self._death_event(self, self._tile)

    def get_gold_value(self):
        return self._gold_value

    def take_damage(self, damage):
        self._health -= damage
        if self._health <= 0:
            self.trigger_death()

    def sample_direction(self, direction):
        loc = self.get_center_location()

        if direction == Direction.LEFT:
            new_location = (loc[0] - self._move_speed, loc[1])
        elif direction == Direction.RIGHT:
            new_location = (loc[0] + self._move_speed, loc[1])
        elif direction == Direction.UP:
            new_location = (loc[0], loc[1] - self._move_speed)
        elif direction == Direction.DOWN:
            new_location = (loc[0], loc[1] + self._move_speed)
        else:
            new_location = None

        return new_location[0] - self._size/2, new_location[1] - self._size/2

    def find_path(self):
        self._tile_queue.clear()
        self._tile_queue = self._tile.get_path_to_exit_tile()

        if self._tile_queue is None:
            self._tile_queue = []

        if len(self._tile_queue) > 0:
            self._tile_queue.pop()

    def get_next_tile(self):
        if len(self._tile_queue) == 0:
            return None
        return self._tile_queue[-1]

    def gameplay_tick(self):
        if not self._active or self._location is None or self._tile is None or self._direction is Direction.UNKNOWN:
            return

        # Sample potential location
        new_location = self.sample_direction(self._direction)

        # Move if still moving towards center of current tile
        center_loc = (new_location[0]+self._size/2, new_location[1]+self._size/2)
        if Math.sq_dist(center_loc, self._tile.get_center_location()) <= Math.sq_dist(self.get_center_location(), self._tile.get_center_location()):
            self.set_location(new_location)
            return

        # Hit end tile...
        if len(self._tile_queue) == 0:
            self._active = False
            self._end_tile_event(self, self._tile)
            return

        next_tile = self.get_next_tile()
        if self._tile.get_right() == next_tile:
            next_direction = Direction.RIGHT
        elif self._tile.get_left() == next_tile:
            next_direction = Direction.LEFT
        elif self._tile.get_down() == next_tile:
            next_direction = Direction.DOWN
        else:
            next_direction = Direction.UP

        if next_direction != self._direction:
            self._direction = next_direction
            new_location = self.sample_direction(self._direction)

        self.set_location(new_location)

        # check if swapped tiles
        cur_tile_dist = Math.sq_dist(self.get_center_location(), self._tile.get_center_location())
        next_tile_dist = Math.sq_dist(self.get_center_location(), next_tile.get_center_location())

        if next_tile_dist <= cur_tile_dist:
            # TODO: move x or y to line up with center of tile (which one depending on direction)
            self._tile.remove_object(self)
            self._tile = self._tile_queue.pop()
            self._tile.add_object(self)

    def is_tickable(self):
        return True

    def set_tile(self, tile):
        GameObjects.GameObject.set_tile(self, tile)
        if self._location is None:
            self._location = (tile.get_center_location()[0]-self._size/2, tile.get_center_location()[1]-self._size/2)
