import arcade
import math
from core import constants as const

class Generator(arcade.Sprite):
    def __init__(self, x, y, puzzle=None):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.width = const.TILE_SIZE * 0.6
        self.height = const.TILE_SIZE * 0.6
        self.activated = False
        self.activation_progress = 0.0
        self.pulse_time = 0.0
        self.activation_speed = 2.0
        self.puzzle = puzzle
        
        if self.puzzle:
            self.puzzle.generator = self
            if hasattr(self.puzzle, '_init_buttons'):
                self.puzzle._init_buttons()
    
    def update(self, delta_time):
        self.pulse_time += delta_time * 2
        if self.puzzle:
            self.puzzle.update(delta_time)
        
        if self.activated:
            self.activation_progress = min(1.0, self.activation_progress + delta_time * self.activation_speed)
        else:
            self.activation_progress = max(0.0, self.activation_progress - delta_time * self.activation_speed)
    
    def activate(self):
        if self.activated:
            return False
        
        if self.puzzle:
            if not self.puzzle.active:
                self.puzzle.activate()
                return False
            if self.puzzle.solved:
                self.activation_progress = 1.0
                self.activated = True
                return True
        else:
            self.activation_progress = 1.0
            self.activated = True
            return True
        return False
    
    def handle_key_press(self, key):
        if self.puzzle and self.puzzle.active:
            return self.puzzle.on_key_press(key)
        return False
    
    def handle_key_release(self, key):
        if self.puzzle and self.puzzle.active:
            if hasattr(self.puzzle, 'on_key_release'):
                return self.puzzle.on_key_release(key)
        return False
    
    def draw(self):
        base_color = (50, 50, 50) if not self.activated else (100, 150, 200)
        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        bottom = self.center_y - self.height / 2
        top = self.center_y + self.height / 2
        
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, base_color)
        
        pulse = (math.sin(self.pulse_time) + 1) / 2
        color = (0, 255, 100) if self.activated else (255, 100, 0)
        alpha = (200 if self.activated else 100) + int(55 * pulse)
        indicator_size = self.width * 0.3 * (0.8 + 0.2 * pulse)
        arcade.draw_circle_filled(self.center_x, self.center_y, indicator_size, (*color, alpha))
        
        if self.activation_progress > 0 and not self.activated:
            bar_width = self.width * 0.8
            bar_height = 8
            bar_y = self.center_y - self.height // 2 - 15
            bar_left = self.center_x - bar_width / 2
            bar_right = self.center_x + bar_width / 2
            bar_bottom = bar_y - bar_height / 2
            bar_top = bar_y + bar_height / 2
            
            arcade.draw_lrbt_rectangle_filled(bar_left, bar_right, bar_bottom, bar_top, (100, 100, 100, 200))
            progress_right = bar_left + bar_width * self.activation_progress
            arcade.draw_lrbt_rectangle_filled(bar_left, progress_right, bar_bottom, bar_top, (0, 200, 255, 255))
        
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, (255, 255, 255, 150), 2)
        
        if self.puzzle and self.puzzle.active and not self.activated:
            self.puzzle.draw()
