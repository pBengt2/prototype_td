from enum import Enum
import pygame

import Defaults


class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    DARK_RED = (50, 0, 0)
    GRAY = (69, 69, 69)
    YELLOW = (150, 150, 0)


class Shapes(Enum):
    CIRCLE = 0
    RECT = 1


class VisualManager:
    def __init__(self):
        self._screen = None
        self._aspect_ratio = Defaults.DEFAULT_ASPECT_RATIO
        self._screen_width = Defaults.DEFAULT_WIDTH
        self._screen_height = self._screen_width / self._aspect_ratio[0] * self._aspect_ratio[1]
        self._ui_objects = {}

    def draw_screen(self, grid, game_objects, player_info, current_round):
        update_screen(screen=self._screen, grid=grid, game_objects=game_objects, player_info=player_info, round_info=current_round)

    def initialize(self):
        self.resize_window(self._screen_width)

    def resize_window(self, width, height=None):
        self._screen_width = width
        self._screen_height = height
        if self._screen_height is None:
            self._screen_height = width / self._aspect_ratio[0] * self._aspect_ratio[1]
        self._screen = pygame.display.set_mode([self._screen_width, self._screen_height])

    def get_location(self, width_percent, height_percent):
        return self.get_size(width_percent, height_percent)

    def get_size(self, width_percent, height_percent):
        return self._screen_width * width_percent, self._screen_height * height_percent


def draw_shape(screen, origin, center_location, shape, size, color, only_border=False):
    try:
        if only_border:
            if shape == Shapes.RECT:
                for i in range(4):
                    pygame.draw.rect(screen, color, (origin[0]-i+3, origin[1]-i+3, size[0]-1, size[1]-2), 1)
            if shape == Shapes.CIRCLE:
                pygame.draw.circle(surface=screen, color=color, center=center_location, radius=size, width=3)
            return
        if shape == Shapes.CIRCLE:
            pygame.draw.circle(surface=screen, color=color, center=center_location, radius=size)
        elif shape == Shapes.RECT:
            pygame.draw.rect(surface=screen, color=color, rect=(origin[0], origin[1], size[0], size[1]))
        else:
            print("Err: Unhandled shape: " + str(shape))
    except TypeError as e:
        print(e)
        print(screen, center_location, shape, size, color)
        exit(-5826)


def draw_grid(screen, grid):
    width, height = grid.get_size()
    origin = grid.get_location()
    rows, cols = grid.get_dimensions()
    color = grid.get_color()

    col_size = height / rows
    start_location = (origin[0], origin[1])
    for i in range(rows+1):
        pygame.draw.line(screen, Colors.WHITE, start_location, (start_location[0]+width, start_location[1]))
        start_location = (start_location[0], start_location[1] + col_size)

    row_size = width / cols
    start_location = (origin[0], origin[1])
    for i in range(cols+1):
        pygame.draw.line(screen, color, start_location, (start_location[0], start_location[1]+height))
        start_location = (start_location[0]+row_size, start_location[1])


def draw_ui(screen, player_info, round_info):
    font = Defaults.DEFAULT_FONT

    health_text = font.render("Health = " + str(player_info.health), False, Colors.WHITE)
    gold_text = font.render("Gold = " + str(player_info.gold), False, Colors.WHITE)
    round_num_text = font.render("Round = " + str(round_info.round_number), False, Colors.WHITE)
    if round_info.prep_ticks > 0:
        round_info_text = font.render("Prep Time = " + str(round_info.prep_ticks / 60.0).split(".")[0], False, Colors.WHITE)
    else:
        round_info_text = font.render("Units Remaining = " + str(round_info.units_remaining), False, Colors.WHITE)

    screen.blit(health_text, (150, 0))
    screen.blit(gold_text, (150, 20))
    screen.blit(round_num_text, (150, 40))
    screen.blit(round_info_text, (150, 60))


def update_screen(screen, grid, game_objects, player_info, round_info):
    screen.fill(Colors.BLACK)

    draw_grid(screen, grid)

    for game_object in game_objects:
        if game_object.is_visible():
            game_object.draw_object(screen)

    draw_ui(screen, player_info, round_info)
    pygame.display.flip()
