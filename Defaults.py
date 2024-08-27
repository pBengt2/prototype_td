import pygame


# Window properties
DEFAULT_ASPECT_RATIO = [16, 9]
DEFAULT_WIDTH = 1440


DEFAULT_GRID_ROWS = 9
DEFAULT_GRID_COLS = 16
DEFAULT_OBJ_SIZE = 25
DEFAULT_TOWER_SIZE = 25
DEFAULT_UNIT_SIZE = 50

# Debug
DEBUG_PRINT = True
IGNORED_EVENTS = [pygame.MOUSEMOTION, pygame.KEYUP, pygame.WINDOWENTER, pygame.WINDOWLEAVE, pygame.ACTIVEEVENT, pygame.TEXTINPUT, pygame.AUDIODEVICEADDED, pygame.WINDOWSHOWN, pygame.WINDOWFOCUSLOST, pygame.WINDOWFOCUSGAINED, pygame.TEXTEDITING, pygame.VIDEOEXPOSE, pygame.WINDOWEXPOSED, pygame.WINDOWMOVED, pygame.WINDOWCLOSE]

# Default other
pygame.font.init()
DEFAULT_FONT = pygame.font.SysFont(name=pygame.font.get_default_font(), size=32)
