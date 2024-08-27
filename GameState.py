import pygame
import time
import random

import Defaults as Defaults
import DrawUtils as DrawUtils
import GameObjects as GameObjects
import Grid as Grid
import GameStates as GameStates
import Units as Units
import Cards as Cards

from GameStates import GameState
from GameStates import RoundState

pygame.init()

GAMEPLAY_FRAME_TIME = 1.0 / 60.0
VISUAL_FRAME_TIME = 1.0 / 60.0

# TODO: Code cleanup
# Make functions private where possible...
# Class for handling ticking

# TODO: Large features
# Deck building
# Screens (main menu/settings/etc)
# Save (decks + settings)
# Sizing across the board. Support different resolutions and ratios
# Multiplayer? (cards for sending / enhancing units / etc)
# Online?
# Keyboard shortcuts?
# Cards for tower upgrades etc?

# TODO: Gameplay mechanics
# Sell towers for gold?
# ability to 'remove' card (full cost?)?
# How should mid round tower placing work (currently units make their path when spawned, goes through towers added after)?
# Many more towers!

# TODO: Non-Gameplay mechanics
# add visual location to GameObjects, and allow for visual tick sampling... (ie, allow for faster visual frame-rates then gameplay...)


class GameObjectManager:
    def __init__(self):
        self._game_objects = {}
        for t in GameObjects.ObjectType:
            self._game_objects[t] = []

    def _get_all_objects(self):
        objects = []
        for v in self._game_objects.values():
            objects += v
        return objects

    def debug_verify_tiles(self):
        for game_obj in self._get_all_objects():
            game_obj.verify_tile()

    def get_clickable_objects(self, pos=None):
        if pos:
            return [g for g in self._get_all_objects() if g.is_clickable() and g.check_collision(pos)]
        else:
            return [g for g in self._get_all_objects() if g.is_clickable()]

    def get_tickable_objects(self):
        return [g for g in self._get_all_objects() if g.is_tickable()]

    def get_visible_objects(self):
        return [g for g in self._get_all_objects() if g.is_visible()]

    def get_objects_of_type(self, object_type):
        return self._game_objects[object_type]

    def remove_game_object(self, game_object):
        self._game_objects[game_object.get_type()].remove(game_object)

    def add_game_object(self, game_object: GameObjects.GameObject):
        self._game_objects[game_object.get_type()].append(game_object)


class GameStuff:
    def __init__(self):
        self.visual_frame_time = VISUAL_FRAME_TIME
        self.gameplay_frame_time = GAMEPLAY_FRAME_TIME

        self.debug_uncap_frame_rate = False

        self.player_info = GameStates.PlayerInfo()
        self.gom = GameObjectManager()
        self.vm = DrawUtils.VisualManager()

        self.mouse_hover_objects = []

        self.game_state = GameState.PVE
        self.round_state = RoundState.PREP
        self.round_ticks = 0

        self.rounds = []
        for i in range(100, 0, -1):
            self.rounds.append(GameStates.RoundInfo(round_number=i, units=i*2, prep_seconds=10+i))
        self.rounds.append(GameStates.RoundInfo(round_number=0, units=1, prep_seconds=30))

        self.current_round = self.rounds.pop()

        self.held_object = None
        self.running = False

        location = self.vm.get_location(.2, .1)
        self.grid = Grid.Grid(location, self.vm.get_size(.7, .8))

        for tile in self.grid.get_tiles_flatten_list():
            self.gom.add_game_object(tile)

        self.card_area = (self.vm.get_location(.05, .05), self.vm.get_location(.25, .95))
        self.card_locations = [self.vm.get_location(.1, .15),
                               self.vm.get_location(.1, .3),
                               self.vm.get_location(.1, .45),
                               self.vm.get_location(.1, .6),
                               self.vm.get_location(.1, .75)]
        self.card_size = self.vm.get_size(.1, .1)

    def initialize(self):
        self.vm.initialize()

    def trigger_unit_end_tile(self, game_object, tile):
        self.player_info.health -= 1
        if self.player_info.health <= 0:
            print("TODO: Game Over")
            self.player_info.health = 100
        tile.remove_object(game_object)
        self.gom.remove_game_object(game_object)
        self.current_round.units_remaining -= 1

    def trigger_unit_death(self, unit_object, tile):
        self.player_info.gold += unit_object.get_gold_value()
        tile.remove_object(unit_object)
        self.gom.remove_game_object(unit_object)
        self.current_round.units_remaining -= 1

    def create_game_unit(self, tile):
        if tile.is_occupied():
            print("warn: UNIT attempted place on occupied tile")
            exit(-275)
        health = 20 + (2 * self.current_round.round_number)
        speed = 10.0 * ((self.current_round.round_number / 50) + 1.0)
        unit_obj = Units.Unit(health=health, speed=speed, location=None, visible=True, death_event=self.trigger_unit_death, end_tile_event=self.trigger_unit_end_tile)

        if unit_obj:
            self.gom.add_game_object(unit_obj)
            tile.add_object(unit_obj)
            unit_obj.initialize()

    def create_tower(self, tower_type, tile):
        if not self.grid.can_place_tower(tile):
            exit(-55)
        if not self.player_info.gold >= tower_type.COST:
            exit(-21)

        tower_obj = tower_type(visible=True, gom=self.gom)
        tile.add_object(tower_obj)

        self.gom.add_game_object(tower_obj)
        tower_obj.initialize()
        self.player_info.gold -= tower_obj.COST

    def debug_send_unit(self):
        self.create_game_unit(self.grid.get_enter_tile())

    def can_use_card_on_tile(self, card, tile):
        if tile is None:
            return False
        elif not self.grid.can_place_tower(tile):
            return False
        elif not self.player_info.gold >= card.get_tower_type().COST:
            return False
        return True

    def ingame_handle_events(self):
        self.mouse_hover_events()

        for event in pygame.event.get():
            if event.type in Defaults.IGNORED_EVENTS:
                pass
            elif event.type == pygame.MOUSEBUTTONUP:
                if self.held_object is not None and event.button == 1:  # left click
                    if self.held_object.get_type() == GameObjects.ObjectType.CARD:
                        card = self.held_object
                        tile = self.grid.get_closest_tile(pygame.mouse.get_pos())
                        if self.can_use_card_on_tile(card, tile):
                            self.create_tower(card.get_tower_type(), tile)
                            self.replace_card(card)
                    self.held_object.click_release()
                    self.held_object = None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                """
                event.button
                1 - left click
                2 - middle click
                3 - right click
                4 - scroll up
                5 - scroll down
                """
                if event.button == 1:  # left click
                    hits = self.gom.get_clickable_objects(event.pos)
                    if len(hits) > 0:
                        hits[0].standard_click()
                        if hits[0].is_draggable():
                            self.held_object = hits[0]
                        return
                elif event.button == 3:  # right click
                    tile = self.grid.get_closest_tile(event.pos)
                    if tile:
                        if tile.contains_tower():
                            tower = tile.remove_tower()
                            self.gom.remove_game_object(tower)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit()
                elif event.key == pygame.K_u:
                    self.debug_send_unit()
                elif event.key == pygame.K_SPACE:
                    if self.round_state == RoundState.PREP:
                        self.round_state = RoundState.ROUND
                        self.current_round.prep_ticks = 0
                        self.current_round.units_remaining = self.current_round.units
                        self.round_ticks = 0
                elif event.key == pygame.K_LEFT:
                    self.gameplay_frame_time = self.gameplay_frame_time * 2
                elif event.key == pygame.K_RIGHT:
                    self.gameplay_frame_time = self.gameplay_frame_time / 2
                elif event.key == pygame.K_UP:
                    self.debug_uncap_frame_rate = not self.debug_uncap_frame_rate
            elif event.type == pygame.QUIT:
                self.running = False
            else:
                print("   unassigned_event: " + str(event))

    def debug_verify_tiles(self):
        self.grid.debug_verify_objects()
        self.gom.debug_verify_tiles()

    def get_card(self):
        r = random.randint(0, 2)
        if r == 0:
            card = Cards.MazeCard()
        elif r == 1:
            card = Cards.StompCard()
        else:
            card = Cards.ShootCard()

        self.gom.add_game_object(card)
        return card

    def replace_card(self, card):
        loc = card.get_start_loc()
        self.gom.remove_game_object(card)
        new_card = self.get_card()
        new_card.set_location(loc)
        new_card.set_visible(True)

    def gameplay_tick_game_objects(self):
        for game_object in self.gom.get_tickable_objects():
            game_object.gameplay_tick()

    def visual_tick_game_objects(self):
        if self.held_object:
            self.held_object.visual_tick_held(pygame.mouse.get_pos())

        for game_object in self.gom.get_tickable_objects():
            game_object.visual_tick()

    def init_cards(self):
        for i in range(5):
            new_card = self.get_card()
            new_card.set_location(loc=self.card_locations[i])
            new_card.set_visible()

    def tick_round(self):
        self.round_ticks += 1

        if self.round_state == RoundState.PREP:
            self.current_round.prep_ticks -= 1
            if self.current_round.prep_ticks < 0:
                self.round_state = RoundState.ROUND
                self.current_round.units_remaining = self.current_round.units
                self.round_ticks = 0
        elif self.round_state == RoundState.ROUND:
            b_spawn_unit = self.round_ticks % max(10, 60 - self.current_round.round_number * 2) == 0
            if self.current_round.units_remaining <= 0:
                self.round_state = RoundState.POST
                self.round_ticks = 0
            elif b_spawn_unit and self.current_round.units_summoned < self.current_round.units:
                self.create_game_unit(self.grid.get_enter_tile())
                self.current_round.units_summoned += 1
        elif self.round_state == RoundState.POST:
            self.round_ticks = 0
            self.round_state = RoundState.PREP
            self.current_round = self.rounds.pop()
            self.player_info.gold += 10

    def mouse_hover_events(self):
        new_mouse_hover_objects = []

        pos = pygame.mouse.get_pos()
        tile = self.grid.get_closest_tile(loc=pos, b_within_grid=True)
        if tile is not None:
            new_mouse_hover_objects.append(tile)

            tower = tile.get_tower()
            if tower:
                new_mouse_hover_objects.append(tower)

        for g in self.mouse_hover_objects:
            if g not in new_mouse_hover_objects:
                g.remove_mouse_hover()
                self.mouse_hover_objects.remove(g)

        for g in new_mouse_hover_objects:
            if g not in self.mouse_hover_objects:
                g.add_mouse_hover()
                self.mouse_hover_objects.append(g)

    def pve_tick(self):
        self.tick_round()
        self.ingame_handle_events()
        self.gameplay_tick_game_objects()

        if Defaults.DEBUG_PRINT:
            self.debug_verify_tiles()

    def game_tick(self):
        if self.game_state == GameState.MENU:
            pass
        elif self.game_state == GameState.PVE:
            self.pve_tick()

    def visual_tick(self):
        self.visual_tick_game_objects()
        game_objects = self.gom.get_visible_objects()
        self.vm.draw_screen(self.grid, game_objects, self.player_info, self.current_round)

    def game_loop(self):
        self.init_cards()
        prev_visual_time = 0
        prev_gameplay_time = 0
        while self.running:
            dropped_gameplay_frame = False
            if self.gameplay_frame_time - (time.time() - prev_gameplay_time) <= 0 or self.debug_uncap_frame_rate:
                prev_gameplay_time = time.time()
                self.game_tick()
                if self.gameplay_frame_time - (time.time() - prev_gameplay_time) < 0:
                    dropped_gameplay_frame = True
                    print("dropped gameplay frame")

            if not dropped_gameplay_frame and self.visual_frame_time - (time.time() - prev_visual_time) <= 0:
                prev_visual_time = time.time()
                self.visual_tick()
                if self.visual_frame_time - (time.time() - prev_visual_time) < 0:
                    print("dropped visual frame")

    def start(self):
        self.running = True
        self.game_loop()
        pygame.quit()
