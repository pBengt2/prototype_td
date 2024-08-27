from enum import Enum

import DrawUtils as DrawUtils
import Defaults as Defaults
import GameObjects as GameObjects
import MathUtils as Math


class Direction(Enum):
    UNKNOWN = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


class Tile(GameObjects.GameObject):
    def __init__(self, grid, loc=(0, 0), grid_loc=(0, 0), size=(0, 0), node_id=-1):
        GameObjects.GameObject.__init__(self, loc, False)
        self._object_type = GameObjects.ObjectType.TILE
        self._grid = grid
        self._game_objects = []
        self._grid_loc = grid_loc
        self._location = (loc[0] - size[0]/2, loc[1] - size[1]/2)  # loc
        self._left_tile = None
        self._right_tile = None
        self._up_tile = None
        self._down_tile = None
        self._linked_tiles = []
        self._node_id = node_id  # TODO: Node id's for optimizations (shortest path, etc)

        self._visible = False
        self._color = DrawUtils.Colors.RED
        self._shape = DrawUtils.Shapes.RECT
        self._size = size

    def get_size(self):
        return self._size

    def draw_object(self, screen):
        DrawUtils.draw_shape(screen, self.get_location(), self.get_center_location(), self._shape, self._size, self._color, True)

    def get_left(self):
        return self._left_tile

    def get_right(self):
        return self._right_tile

    def get_up(self):
        return self._up_tile

    def get_down(self):
        return self._down_tile

    def get_path_to_tile(self, end_tile):
        return self._grid.get_shortest_path(tile1=self, tile2=end_tile)

    def get_path_to_exit_tile(self):
        return self._grid.get_shortest_path(tile1=self, tile2=None)

    def debug_get_objects(self):
        return self._game_objects

    def add_mouse_hover(self):
        # self._visible = True
        pass

    def remove_mouse_hover(self):
        # self._visible = False
        pass

    def link_tiles(self, left_tile, right_tile, up_tile, down_tile):
        self._left_tile = left_tile
        self._right_tile = right_tile
        self._up_tile = up_tile
        self._down_tile = down_tile
        self._linked_tiles = [x for x in [left_tile, right_tile, up_tile, down_tile] if x is not None]

    def get_location(self):
        return self._location

    def is_occupied(self):
        for game_obj in self._game_objects:
            if game_obj.get_type() == GameObjects.ObjectType.TOWER:
                return True
        return False

    def get_neighbors(self):
        return self._linked_tiles

    def get_unoccupied_neighbors(self):
        neighbors = [x for x in self._linked_tiles if not x.is_occupied()]
        return neighbors

    def get_tiles_in_range(self, distance):
        tiles_in_range = []
        grid_range = [[self._grid_loc[0] - distance, self._grid_loc[1] - distance], [self._grid_loc[0] + distance, self._grid_loc[1] + distance]]

        x1 = max(grid_range[0][0], 0)
        y1 = max(grid_range[0][1], 0)

        for i in range(x1, grid_range[1][0]):
            for j in range(y1, grid_range[1][1]):
                cur_tile = self._grid.get_tile_by_index([i, j])
                if cur_tile:
                    if Math.distance(cur_tile.get_center_location(), self.get_center_location()) <= distance:
                        tiles_in_range.append(cur_tile)
        return tiles_in_range

    def add_object(self, game_obj):
        was_occupied = self.is_occupied()
        self._game_objects.append(game_obj)
        game_obj.set_tile(self)
        if self.is_occupied() != was_occupied:
            self._grid.update_shortest_path_cache()

    def remove_tower(self):
        for game_obj in self._game_objects:
            if game_obj.get_type() == GameObjects.ObjectType.TOWER:
                self.remove_object(game_obj)
                return game_obj
        return None

    def remove_object(self, game_obj):
        was_occupied = self.is_occupied()
        self._game_objects.remove(game_obj)
        if was_occupied != self.is_occupied():
            self._grid.update_shortest_path_cache()

    def is_unit_in_range(self, inner_range, outer_range):
        pass

    def get_objects_of_type(self, object_type):
        objects = []
        for game_obj in self._game_objects:
            if game_obj.get_type() == object_type:
                objects.append(game_obj)
        return objects

    def contains_type(self, object_type):
        for game_obj in self._game_objects:
            if game_obj.get_type() == object_type:
                return True
        return False

    def get_tower(self):
        towers = self.get_objects_of_type(GameObjects.ObjectType.TOWER)
        if len(towers) == 0:
            return None
        return towers[0]

    def contains_tower(self):
        return self.contains_type(GameObjects.ObjectType.TOWER)

    def contains_units(self):
        return self.contains_type(GameObjects.ObjectType.UNIT)

    def get_units(self):
        return [x for x in self._game_objects if x.get_type() == GameObjects.ObjectType.UNIT]


class Grid:
    def __init__(self, loc, size, rows=Defaults.DEFAULT_GRID_ROWS, cols=Defaults.DEFAULT_GRID_COLS):
        self._location = loc
        self._width = size[0]
        self._height = size[1]

        self._color = DrawUtils.Colors.WHITE

        self._enter_tile = None
        self._exit_tile = None
        self._shortest_path_cache = []  # stores the shortest distance to tile from enter_tile

        w = self._width / cols
        h = self._height / rows
        l0, l1 = (self._location[0] + w/2, self._location[1] + h/2)
        self._tiles = [[Tile(self, (l0+w*i, l1+h*j), (i, j), (w, h), (i*cols+j)) for j in range(rows)] for i in range(cols)]

        # Link tiles (can be optimized)
        for i in range(len(self._tiles)):
            for j in range(len(self._tiles[i])):
                up, left, right, down = None, None, None, None
                if i > 0:
                    left = self._tiles[i-1][j]
                if i + 1 < len(self._tiles):
                    right = self._tiles[i + 1][j]
                if j > 0:
                    up = self._tiles[i][j - 1]
                if j+1 < len(self._tiles[i]):
                    down = self._tiles[i][j + 1]

                self._tiles[i][j].link_tiles(left, right, up, down)

        self._enter_tile = self._tiles[0][0]
        self._exit_tile = self._tiles[-1][-1]

        self.update_shortest_path_cache()

        self._rows = rows
        self._cols = cols

    def get_enter_tile(self):
        return self._enter_tile

    def get_location(self):
        return self._location

    def get_color(self):
        return self._color

    def get_size(self):
        return self._width, self._height

    def get_dimensions(self):
        return self._rows, self._cols

    def get_shortest_path(self, tile1=None, tile2=None):
        if tile1 is None:
            tile1 = self._enter_tile
        if tile2 is None:
            tile2 = self._exit_tile

        if tile1 == self._enter_tile:
            previous_nodes = self._shortest_path_cache
        else:
            # TODO: Can be optimized farther to use cache if it contains the tile
            _, previous_nodes, unreachable_nodes = Math.pseudo_dijkstra(self.get_tiles_flatten_list(), tile1)

        # reverse traverse previous nodes...
        tile_list = [tile2]
        previous_node = previous_nodes[tile2]
        if previous_node is None:
            return None
        while previous_node:
            tile_list.append(previous_node)
            previous_node = previous_nodes[previous_node]

        return tile_list

    def update_shortest_path_cache(self):
        _, previous_nodes, unreachable_nodes = Math.pseudo_dijkstra(self.get_tiles_flatten_list(), self._enter_tile)
        if self._exit_tile in unreachable_nodes:
            # print('could not reach exit...')
            return False

        self._shortest_path_cache = previous_nodes
        return True

    def test_for_valid_path(self, negate_tiles=None):
        tile_list = self.get_tiles_flatten_list()
        if negate_tiles is not None:
            for t in negate_tiles:
                tile_list.remove(t)
        _, previous_nodes, unreachable_nodes = Math.pseudo_dijkstra(tile_list, self._enter_tile)
        if self._exit_tile in unreachable_nodes:
            # print('could not reach exit...')
            return False
        return True

    def debug_verify_objects(self):
        for i in range(len(self._tiles)):
            for j in range(len(self._tiles[i])):
                tile = self._tiles[i][j]
                for game_obj in tile.debug_get_objects():
                    if game_obj.debug_get_tile() != self._tiles[i][j]:
                        print("err: err game tile")
                        print("     " + str(game_obj))
                        print("     " + str(self))

    def can_place_tower(self, tile):
        if tile.is_occupied():
            return False
        if not self.test_for_valid_path(negate_tiles=[tile]):
            return False
        return True

    def remove_all_obj(self, tile):
        was_occupied = tile.is_occupied()

        tile.game_objects.clear()

        if was_occupied != tile.is_occupied():
            self.update_shortest_path_cache()

        return True

    def get_grid_bounds(self):
        return [[self._location[0], self._location[1]], [self._location[0]+self._width, self._location[1]+self._height]]

    def in_bounds(self, check_location):
        c_x = check_location[0]
        c_y = check_location[1]
        x1 = self._location[0]
        x2 = self._location[0] + self._width
        y1 = self._location[1]
        y2 = self._location[1] + self._height
        if x1 <= c_x <= x2 and y1 <= c_y <= y2:
            return True
        return False

    def get_closest_tile(self, loc, b_within_grid=True):
        # TODO: optimize
        x, y = loc
        if self._tiles is None:
            return None
        if b_within_grid:
            grid_bounds = self.get_grid_bounds()
            if x < grid_bounds[0][0] or x > grid_bounds[1][0] or y < grid_bounds[0][1] or y > grid_bounds[1][1]:
                return None
        closest_tile = self._tiles[0][0]
        loc = closest_tile.get_center_location()
        lowest_dist = (loc[0]-x)*(loc[0]-x) + (loc[1]-y)*(loc[1]-y)

        for tiles in self._tiles:
            for tile in tiles:
                loc = tile.get_center_location()
                dist = (loc[0]-x)*(loc[0]-x) + (loc[1]-y) * (loc[1]-y)
                if dist < lowest_dist:
                    closest_tile = tile
                    lowest_dist = dist
        return closest_tile

    def get_tiles_flatten_list(self):
        tiles = []
        for tile_row in self._tiles:
            for t in tile_row:
                tiles.append(t)
        return tiles

    def get_tile_by_index(self, tile_indices):
        try:
            return self._tiles[tile_indices[0]][tile_indices[1]]
        except IndexError:
            return None
