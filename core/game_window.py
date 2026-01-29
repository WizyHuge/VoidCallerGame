import arcade
from core import constants as const
from systems.echolocation import Pulsar
from systems.vision_system import VisionSystem
from entities.generator import Generator
from entities.exit_door import ExitDoor
from systems.puzzle_system import SequencePuzzle, HoldButtonPuzzle
import random
import math

class VoidCallerWindow(arcade.View):
    def __init__(self):
        super().__init__()
        self.volume = 0.5
        self.camera = None
        self.gui_camera = None
        self.walls = None
        self.floors = None
        self.player = None
        self.physics_engine = None
        self.pulsar = None
        self.game_over = False
        self.vision = None
        self.generators = None
        self.exit_door = None
        self.generators_activated = 0
        self.total_generators = 0
        self.victory = False
        self.story_message = None
        self.story_message_time = 0.0
        self.light_intensity = const.LIGHT_INTENSITY_BASE
        self.game_time = 0.0
        self.time_limit = random.uniform(420, 600)
        self.step_timer = 0.0
        self.step_interval = const.FOOTSTEP_INTERVAL
    
    def setup(self):
        from world.map import GameMap
        from entities.player import Player
        
        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()
        self.vision = VisionSystem(self.window.width, self.window.height)
        self.walls = arcade.SpriteList(use_spatial_hash=True)
        self.floors = arcade.SpriteList(use_spatial_hash=True)
        self.generators = arcade.SpriteList()
        
        self.map = GameMap()
        self.map.create_map(self.walls, self.floors)
        self.player = Player()
        
        if len(self.map.rooms) > 0:
            spawn_room = random.choice(self.map.rooms)
            room_x1, room_x2, room_y1, room_y2 = spawn_room
            self.player.center_x = ((room_x1 + room_x2) // 2) * const.TILE_SIZE + const.TILE_SIZE // 2
            self.player.center_y = ((room_y1 + room_y2) // 2) * const.TILE_SIZE + const.TILE_SIZE // 2
        else:
            self.player.center_x = self.map.width * const.TILE_SIZE // 2
            self.player.center_y = self.map.height * const.TILE_SIZE // 2
        
        self.pulsar = Pulsar()
        self._create_generators()
        self._create_exit_door()
        
        self.physics_engine = arcade.PhysicsEngineSimple(self.player, self.walls)
        self.game_over = False
        self.victory = False
        self.game_time = 0.0
        self.camera.position = (self.player.center_x, self.player.center_y)
        self._show_story_message(const.STORY_MESSAGES[0], 3.0)
    
    def _create_generators(self):
        self.generators.clear()
        spawn_x = self.player.center_x
        spawn_y = self.player.center_y
        num_generators = random.randint(4, 6)
        
        available_rooms = []
        for room in self.map.rooms:
            room_x1, room_x2, room_y1, room_y2 = room
            room_center_x = ((room_x1 + room_x2) // 2) * const.TILE_SIZE + const.TILE_SIZE // 2
            room_center_y = ((room_y1 + room_y2) // 2) * const.TILE_SIZE + const.TILE_SIZE // 2
            dist_from_spawn = math.hypot(room_center_x - spawn_x, room_center_y - spawn_y)
            if dist_from_spawn > 300:
                available_rooms.append(room)
        
        if len(available_rooms) < num_generators:
            num_generators = max(1, len(available_rooms))
        
        selected_rooms = random.sample(available_rooms, num_generators)
        puzzle_types = ['sequence', 'hold', None]
        
        for i, room in enumerate(selected_rooms):
            room_x1, room_x2, room_y1, room_y2 = room
            try:
                px = random.randint(room_x1 + 2, max(room_x1 + 2, room_x2 - 2)) * const.TILE_SIZE + const.TILE_SIZE // 2
                py = random.randint(room_y1 + 2, max(room_y1 + 2, room_y2 - 2)) * const.TILE_SIZE + const.TILE_SIZE // 2
            except ValueError:
                px = ((room_x1 + room_x2) // 2) * const.TILE_SIZE + const.TILE_SIZE // 2
                py = ((room_y1 + room_y2) // 2) * const.TILE_SIZE + const.TILE_SIZE // 2
            
            wall_hit = False
            for wall in self.walls:
                if abs(wall.center_x - px) < const.TILE_SIZE and abs(wall.center_y - py) < const.TILE_SIZE:
                    wall_hit = True
                    break
            
            if not wall_hit:
                puzzle_type = random.choice(puzzle_types) if i > 0 else None
                puzzle = None
                if puzzle_type == 'sequence':
                    puzzle = SequencePuzzle(None)
                elif puzzle_type == 'hold':
                    puzzle = HoldButtonPuzzle(None)
                generator = Generator(px, py, puzzle)
                self.generators.append(generator)
        
        self.total_generators = len(self.generators)
        self.generators_activated = 0
    
    def _create_exit_door(self):
        if len(self.map.rooms) == 0:
            return
        
        door_room = random.choice(self.map.rooms)
        room_x1, room_x2, room_y1, room_y2 = door_room
        
        side = random.randint(0, 3)
        
        if side == 0:
            door_x = room_x1 * const.TILE_SIZE + const.TILE_SIZE // 2
            door_y = random.randint(room_y1 + 1, room_y2 - 1) * const.TILE_SIZE + const.TILE_SIZE // 2
        elif side == 1:
            door_x = room_x2 * const.TILE_SIZE + const.TILE_SIZE // 2
            door_y = random.randint(room_y1 + 1, room_y2 - 1) * const.TILE_SIZE + const.TILE_SIZE // 2
        elif side == 2:
            door_x = random.randint(room_x1 + 1, room_x2 - 1) * const.TILE_SIZE + const.TILE_SIZE // 2
            door_y = room_y1 * const.TILE_SIZE + const.TILE_SIZE // 2
        else:
            door_x = random.randint(room_x1 + 1, room_x2 - 1) * const.TILE_SIZE + const.TILE_SIZE // 2
            door_y = room_y2 * const.TILE_SIZE + const.TILE_SIZE // 2
        
        self.exit_door = ExitDoor(door_x, door_y)

    
    def _show_story_message(self, message, duration=3.0):
        self.story_message = message
        self.story_message_time = duration
    
    def _check_generator_activation(self):
        for generator in self.generators:
            if generator.activated:
                continue
            
            dist = arcade.get_distance_between_sprites(self.player, generator)
            if dist < const.GENERATOR_ACTIVATION_DISTANCE:
                was_activated = generator.activated
                if generator.activate():
                    if not was_activated:
                        self.generators_activated += 1
                        self._show_story_message(f"Генератор активирован! ({self.generators_activated}/{self.total_generators})", 2.0)
                        
                        if self.generators_activated == self.total_generators:
                            self._show_story_message("Все генераторы активированы! Дверь открыта!", 4.0)
                break
    
    def on_update(self, delta_time):
        if self.game_over or self.victory:
            return
        
        self.game_time += delta_time
        if self.game_time >= self.time_limit:
            import sys
            sys.exit(1)
        
        self.player.update(delta_time)
        self.physics_engine.update()
        
        for generator in self.generators:
            generator.update(delta_time)
        
        if self.exit_door:
            self.exit_door.update(delta_time, self.generators_activated >= self.total_generators)
        
        self.light_intensity = const.LIGHT_INTENSITY_BASE + (const.LIGHT_INTENSITY_PER_GENERATOR * self.generators_activated)
        self.light_intensity = min(const.MAX_LIGHT_INTENSITY, self.light_intensity)
        
        if self.story_message_time > 0:
            self.story_message_time -= delta_time
            if self.story_message_time <= 0:
                self.story_message = None
        
        empty_entities = arcade.SpriteList()
        self.pulsar.update(delta_time, self.walls, empty_entities)
        
        for wave in self.pulsar.waves:            
            wave_x = getattr(wave, 'center_x', getattr(wave, 'x', None))
            wave_y = getattr(wave, 'center_y', getattr(wave, 'y', None))
            wave_radius = getattr(wave, 'radius', 0)
            
            if wave_x is not None and wave_y is not None:
                if self.exit_door:
                    dist_to_door = math.hypot(self.exit_door.center_x - wave_x, self.exit_door.center_y - wave_y)
                    if abs(dist_to_door - wave_radius) < const.TILE_SIZE * 1.5:
                        self.vision.highlight_object(self.exit_door.center_x, self.exit_door.center_y, color=(0, 200, 255), duration=1.5)
        
        self.vision.update(delta_time, False)
        
        if self.exit_door and self.exit_door.is_open:
            dist = arcade.get_distance_between_sprites(self.player, self.exit_door)
            if dist < const.TILE_SIZE * 1.5:
                self.victory = True
        
        self.camera.position = arcade.math.lerp_2d(self.camera.position, (self.player.center_x, self.player.center_y), 0.1)

    
    def on_draw(self):
        self.clear()
        self.camera.use()
        
        self.floors.draw()
        self.walls.draw()
        
        for generator in self.generators:
            generator.draw()
        
        if self.exit_door:
            self.exit_door.draw()
        
        self.gui_camera.use()
        
        arcade.draw_lrbt_rectangle_filled(0, self.window.width, 0, self.window.height, (0, 0, 0, 230))
        
        px = self.player.center_x - self.camera.position[0] + self.window.width // 2
        py = self.player.center_y - self.camera.position[1] + self.window.height // 2
        
        self.vision.draw_visibility_mask(px, py, self.camera.position[0], self.camera.position[1])
        
        self.camera.use()
        self.player.draw()
        self.pulsar.draw()
        
        self.gui_camera.use()
        self.vision.draw_highlighted_objects(self.camera.position[0], self.camera.position[1])
        self.vision.draw_vision_overlay()
        
        if self.pulsar.ready:
            self.pulsar.draw_aim(px, py)
        
        if self.story_message and self.story_message_time > 0:
            alpha = int(255 * min(1.0, self.story_message_time / 0.5))
            arcade.draw_text(self.story_message, self.window.width // 2, self.window.height // 2 + 100, (255, 255, 255, alpha), 32, anchor_x="center", anchor_y="center", bold=True, align="center", width=self.window.width - 100)
        
        if self.victory:
            arcade.draw_lrbt_rectangle_filled(0, self.window.width, 0, self.window.height, (0, 0, 0, 220))
            arcade.draw_text("ПОБЕДА!", self.window.width//2, self.window.height//2 + 50, (100, 255, 100), 60, anchor_x="center", bold=True)
            arcade.draw_text("Вы сбежали из подземелья", self.window.width//2, self.window.height//2, (255, 255, 255), 32, anchor_x="center")
            arcade.draw_text("Нажмите R для перезапуска", self.window.width//2, self.window.height//2 - 60, (200, 200, 200), 24, anchor_x="center")
    
    def on_mouse_motion(self, x, y, dx, dy):
        if self.game_over:
            return
        mx = x + self.camera.position[0] - self.window.width // 2
        my = y + self.camera.position[1] - self.window.height // 2
        self.pulsar.update_aim(mx, my, self.player.center_x, self.player.center_y)
    
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT and not self.game_over:
            self.pulsar.emit_wave(self.player.center_x, self.player.center_y, self.pulsar.aim_angle)
    
    def on_key_press(self, key, modifiers):
        self.player.on_key_press(key, modifiers)
        
        if key == arcade.key.R:
            self.setup()
        elif key == arcade.key.ESCAPE:
            arcade.close_window()
        elif key == arcade.key.E:
            self._check_generator_activation()
        else:
            for generator in self.generators:
                if generator.handle_key_press(key):
                    if generator.puzzle and generator.puzzle.solved:
                        was_activated = generator.activated
                        generator.activation_progress = 1.0
                        generator.activated = True
                        
                        if not was_activated:
                            self.generators_activated += 1
                            self._show_story_message(f"Генератор активирован! ({self.generators_activated}/{self.total_generators})", 2.0)
                            
                            if self.generators_activated == self.total_generators:
                                self._show_story_message("Все генераторы активированы! Дверь открыта!", 4.0)
                    break
    
    def on_key_release(self, key, modifiers):
        self.player.on_key_release(key, modifiers)
        for generator in self.generators:
            generator.handle_key_release(key)
