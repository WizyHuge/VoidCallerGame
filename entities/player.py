import arcade
import math
from core import constants as const

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()
        self.pressed_keys = set()
        self.angle = 0
        self.moving = False
        self.texture = arcade.make_soft_square_texture(32, arcade.color.BLUE, outer_alpha=255)
        self.width = const.TILE_SIZE * 0.5
        self.height = const.TILE_SIZE * 0.5
        
        try:
            self.footstep_left = arcade.load_sound(const.FOOTSTEP_LEFT_SOUND_PATH)
            self.footstep_right = arcade.load_sound(const.FOOTSTEP_RIGHT_SOUND_PATH)
        except:
            self.footstep_left = None
            self.footstep_right = None
        
        self.footstep_timer = 0.0
        self.is_left_foot = True
        self.volume = 1.0
    
    def update(self, delta_time):
        speed = const.PLAYER_SPEED
        dx = dy = 0
        
        if arcade.key.W in self.pressed_keys:
            dy += speed
        if arcade.key.S in self.pressed_keys:
            dy -= speed
        if arcade.key.A in self.pressed_keys:
            dx -= speed
        if arcade.key.D in self.pressed_keys:
            dx += speed
        
        self.moving = (dx != 0 or dy != 0)
        
        if self.moving:
            self.angle = math.degrees(math.atan2(dy, dx))
            self.footstep_timer += delta_time
            if self.footstep_timer >= const.FOOTSTEP_INTERVAL:
                self.footstep_timer = 0.0
                if self.footstep_left and self.footstep_right:
                    if self.is_left_foot:
                        arcade.play_sound(self.footstep_left, volume=self.volume)
                    else:
                        arcade.play_sound(self.footstep_right, volume=self.volume)
                    self.is_left_foot = not self.is_left_foot
        else:
            self.footstep_timer = 0.0
            self.is_left_foot = True
        
        self.change_x = dx * delta_time
        self.change_y = dy * delta_time
    
    def draw(self):
        if not self.center_x or not self.center_y:
            return
        
        size = const.TILE_SIZE * 0.3
        angle_rad = math.radians(self.angle)
        local_points = [(size, 0), (-size * 0.5, -size * 0.5), (-size * 0.5, size * 0.5)]
        world_points = []
        
        for lx, ly in local_points:
            rx = lx * math.cos(angle_rad) - ly * math.sin(angle_rad)
            ry = lx * math.sin(angle_rad) + ly * math.cos(angle_rad)
            world_points.append((self.center_x + rx, self.center_y + ry))
        
        arcade.draw_polygon_filled(world_points, arcade.color.BLUE)
        arcade.draw_polygon_outline(world_points, arcade.color.WHITE, 2)
    
    def on_key_press(self, key, modifiers):
        self.pressed_keys.add(key)
    
    def on_key_release(self, key, modifiers):
        self.pressed_keys.discard(key)
