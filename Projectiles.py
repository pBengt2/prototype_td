import GameObjects as GameObjects
import MathUtils as Math

from DrawUtils import Colors


class ProjectileBase(GameObjects.GameObject):
    def __init__(self, speed=10.0, location=None, visible=False, tile=None, damage=10):
        GameObjects.GameObject.__init__(self, location=location, visible=visible)
        self._direction = [0, 1]
        self._tile = tile
        self._object_type = GameObjects.ObjectType.PROJECTILE
        self._color = Colors.BLUE
        self._size = 5
        self._move_speed = speed
        self._damage = damage
        self._active = False
        self._prev_tile = None

    def initialize(self):
        self._tile.add_object(self)
        self._active = True

    def set_direction(self, new_direction):
        self._direction = Math.normalize(new_direction)

    def sample_direction(self, sample_direction):
        loc = self.get_center_location()
        new_location = (loc[0] + self._move_speed * sample_direction[0], loc[1] + self._move_speed * sample_direction[1])
        return new_location[0]-self._size/2, new_location[1]-self._size/2

    def attempt_hit(self):
        try:
            self._tile.get_units()[0].take_damage(self._damage)
            return True
        except IndexError:
            return False

    def destroy_projectile(self):
        self._tile.remove_object(self)
        self._tile = None
        self._visible = False
        self._active = False

    def gameplay_tick(self):
        if not self._active or self.get_location() is None or self._tile is None:
            return

        # Sample potential location
        new_location = self.sample_direction(self._direction)

        if not self._tile._grid.in_bounds(new_location):  # TODO: _grid
            self.destroy_projectile()
            return

        self.set_location(new_location)

        # check if swapped tiles
        shortest_tile_dist = Math.sq_dist(self.get_center_location(), self._tile.get_center_location())
        closest_tile = self._tile
        for tile in self._tile.get_neighbors():
            tile_dist = Math.sq_dist(self.get_center_location(), tile.get_center_location())
            if tile_dist < shortest_tile_dist:
                shortest_tile_dist = tile_dist
                closest_tile = tile

        if closest_tile != self._tile:
            self._tile.remove_object(self)
            self._tile = closest_tile
            self._tile.add_object(self)

        if self.attempt_hit():
            self.destroy_projectile()

    def is_tickable(self):
        return True

    def set_tile(self, tile):
        GameObjects.GameObject.set_tile(self, tile)
        if self.get_location() is None:
            self.set_location(tile.get_center_location())
