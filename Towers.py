from enum import Enum
import math

import Defaults as Defaults
import GameObjects as GameObjects
import Projectiles as Projectiles
import DrawUtils as DrawUtils

from DrawUtils import Colors


# TODO: Towers of different shapes!!
# TODO: 'Flame tower' (ie, like directional stomp tower.

class TowerVersions(Enum):
    BASE = 0
    STD_1 = 1


class BaseTower(GameObjects.GameObject):
    def __init__(self, location=None, visible=False, gom=None):
        GameObjects.GameObject.__init__(self, location, visible)
        self._object_type = GameObjects.ObjectType.TOWER
        self._color = Colors.YELLOW

        self._gom = gom  # TODO: Passing in GOM is ugly.

        self._size = Defaults.DEFAULT_TOWER_SIZE

        self.READY_COLOR = Colors.YELLOW
        self.ATTACK_COLOR = Colors.RED
        self.OTHER_COLOR = Colors.DARK_RED

        self._attack_damage = 5

        self._current_tick = 0

        self._attack_startup_ticks = 10
        self._attack_active_ticks = 60
        self._attack_end_ticks = 10
        self._reload_tick = 20
        self._reset_tick = self._reload_tick + self._attack_startup_ticks + self._attack_active_ticks + self._attack_end_ticks

        self._target_units = []

        self._visible_tiles = []

    def initialize(self):
        print("err initializing base tower")
        exit(-1)

    def ready_tick(self):
        if self.should_attack():
            self._current_tick += 1
        else:
            self._color = self.READY_COLOR

    def attack_active_tick(self):
        self._color = self.ATTACK_COLOR

    def attack_pre_tick(self):
        self._color = self.OTHER_COLOR

    def attack_post_tick(self):
        self._color = self.OTHER_COLOR

    def attack_reload_tick(self):
        self._color = self.OTHER_COLOR

    def attack_tick(self):
        if self._current_tick < self._attack_startup_ticks:
            self.attack_pre_tick()
        elif self._current_tick < self.get_active_tick_end_frame():
            self.attack_active_tick()
        elif self._current_tick < self.get_active_tick_end_frame() + self._attack_end_ticks:
            self.attack_post_tick()
        else:
            self.attack_reload_tick()

    def should_attack(self):
        self._target_units = []
        for tile in self._visible_tiles:
            for unit in tile.get_units():
                self._target_units.append(unit)

        if len(self._target_units) > 0:
            return True
        return False

    def get_active_tick_end_frame(self):
        return self._attack_startup_ticks + self._attack_active_ticks

    def is_tickable(self):
        return True

    def gameplay_tick(self):
        if self._current_tick == 0:
            self.ready_tick()
            return
        else:
            self.attack_tick()
            self._current_tick += 1

            if self._current_tick >= self._reset_tick:
                self._current_tick = 0


class MazeTower(BaseTower):
    COST = 5
    UPGRADE_COST = 5
    COLOR = Colors.GRAY

    def __init__(self, location=None, visible=False, gom=None):
        BaseTower.__init__(self, location=location, visible=visible, gom=gom)
        self.READY_COLOR = Colors.GRAY

    def initialize(self):
        pass

    def should_attack(self):
        return False


class StompTower(BaseTower):
    COST = 20
    UPGRADE_COST = 20
    COLOR = Colors.YELLOW

    def __init__(self, location=None, visible=False, gom=None):
        BaseTower.__init__(self, location=location, visible=visible, gom=gom)
        self.reset_tick = self._reload_tick + self._attack_startup_ticks + self._attack_active_ticks + self._attack_end_ticks
        self.UPGRADE_TOWER_TYPE = StompPlusTower
        self.tower_type = TowerVersions.BASE

    def draw_object(self, screen):
        DrawUtils.draw_shape(screen, self.get_location(), self.get_center_location(), self._shape, self._size, self._color)

        if self._hovered:
            min_x, min_y, max_x, max_y = 999999, 999999, 0, 0
            for t in self._visible_tiles:
                x, y = t.get_location()
                min_x = min(x, min_x)
                min_y = min(y, min_y)
                max_x = max(x, max_x)
                max_y = max(y, max_y)
            max_x += self._visible_tiles[0].get_size()[0]
            max_y += self._visible_tiles[0].get_size()[1]

            center = ((min_x+max_x)/2, (min_y+max_y)/2)
            DrawUtils.draw_shape(screen, (min_x, min_y), center, DrawUtils.Shapes.RECT, (max_x-min_x, max_y-min_y), Colors.RED, True)

    def initialize(self):
        self._visible_tiles = self._tile.get_neighbors()

    def attack_active_tick(self):
        self._color = self.ATTACK_COLOR
        tiles = self._tile.get_neighbors()
        for tile in tiles:
            for unit in tile.get_units():
                unit.take_damage(self._attack_damage)

    def upgrade_tower(self):
        if self.tower_type == TowerVersions.BASE:
            self.tower_type = TowerVersions.STD_1
            self._size *= 1.5
            self._attack_damage *= 1.5


class StompPlusTower(StompTower):
    COST = 10
    COLOR = Colors.YELLOW

    def __init__(self, location=None, visible=False, gom=None):
        BaseTower.__init__(self, location=location, visible=visible, gom=gom)
        self._reset_tick = self._reload_tick + self._attack_startup_ticks + self._attack_active_ticks + self._attack_end_ticks

    def attack_active_tick(self):
        self._color = self.ATTACK_COLOR
        tiles = self._tile.get_neighbors()
        for tile in tiles:
            for unit in tile.get_units():
                unit.take_damage(self._attack_damage)

    def upgrade_tower(self):
        print("already fully upgrade...")


class ShootTower(BaseTower):
    COST = 20
    UPGRADE_COST = math.inf
    COLOR = Colors.GREEN

    def __init__(self, location=None, visible=False, gom=None):
        BaseTower.__init__(self, location=location, visible=visible, gom=gom)

        self._attack_range = Defaults.DEFAULT_UNIT_SIZE * 3
        self._attack_startup_ticks = 10
        self._attack_active_ticks = 1
        self._attack_end_ticks = 10
        self._reload_tick = 20

        self._reset_tick = self._reload_tick + self._attack_startup_ticks + self._attack_active_ticks + self._attack_end_ticks
        self.UPGRADE_TOWER_TYPE = None
        self._tower_type = TowerVersions.BASE
        self._color = self.COLOR
        self.READY_COLOR = self.COLOR
        self.ATTACK_COLOR = Colors.RED
        self.OTHER_COLOR = Colors.DARK_RED

        self._projectile_type = Projectiles.ProjectileBase
        self._projectile_speed = 20
        self._projectile_damage = 20

    def draw_object(self, screen):
        DrawUtils.draw_shape(screen, self.get_location(), self.get_center_location(), self._shape, self._size, self._color)

        if self._hovered:
            DrawUtils.draw_shape(screen, None, self.get_center_location(), DrawUtils.Shapes.CIRCLE, self._attack_range, Colors.RED, True)

    def initialize(self):
        self._visible_tiles = self._tile.get_tiles_in_range(self._attack_range)

    def attack_active_tick(self):
        self._color = self.ATTACK_COLOR

        proj = self._projectile_type(speed=self._projectile_speed, location=self._tile.get_center_location(), visible=True, tile=self._tile, damage=self._projectile_damage)
        self._gom.add_game_object(proj)
        proj.initialize()

        # Don't shoot if all targets have left range
        if len(self._target_units) == 0:
            return

        unit_loc = self._target_units[0].get_center_location()
        tile_loc = self._tile.get_center_location()
        # TODO: This mess is not how direction should be done....
        target_direction = [unit_loc[0] - tile_loc[0], unit_loc[1] - tile_loc[1]]
        scalar = max(math.fabs(target_direction[0]), math.fabs(target_direction[1]))
        if scalar > 1:
            target_direction = [target_direction[0]/scalar, target_direction[1]/scalar]
        proj.set_direction(target_direction)

    def upgrade_tower(self):
        if self._tower_type == TowerVersions.BASE:
            self._tower_type = TowerVersions.STD_1
            self._size *= 1.5
            self._attack_damage *= 1.5
