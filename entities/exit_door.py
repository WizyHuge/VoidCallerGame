import arcade
from core import constants as const
import math

class ExitDoor(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.width = const.TILE_SIZE * 2 / 3
        self.height = const.TILE_SIZE * 3 / 3
        self.is_open = False
        self.open_progress = 0.0
        self.glow_intensity = 0.0
    
    def update(self, delta_time, all_generators_activated):
        if all_generators_activated and not self.is_open:
            self.open_progress = min(1.0, self.open_progress + delta_time * 2.0)
            if self.open_progress >= 1.0:
                self.is_open = True
        self.glow_intensity = (self.glow_intensity + delta_time * 3) % 6.28
    
    def draw(self):
        door_color = (80, 80, 100) if not self.is_open else (100, 150, 180)
        left = self.center_x - self.width / 2
        right = self.center_x + self.width / 2
        bottom = self.center_y - self.height / 2
        top = self.center_y + self.height / 2
        
        glow_alpha = int(60 + 40 * abs(math.sin(self.glow_intensity)))
        glow_size = self.width * (1.3 + 0.2 * abs(math.sin(self.glow_intensity)))
        glow_color = (150, 150, 200) if not self.is_open else (100, 200, 255)
        
        arcade.draw_circle_filled(self.center_x, self.center_y, glow_size, (*glow_color, glow_alpha))
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, door_color)
        
        if self.is_open or self.open_progress > 0:
            open_glow_alpha = int(100 * (1.0 if self.is_open else self.open_progress))
            open_glow_size = self.width * (1.5 + 0.3 * abs(math.sin(self.glow_intensity)))
            arcade.draw_circle_filled(self.center_x, self.center_y, open_glow_size, (0, 200, 255, open_glow_alpha))
        
        indicator_color = (255, 0, 0, 200) if not self.is_open else (0, 255, 0, 200)
        arcade.draw_circle_filled(self.center_x, self.center_y + self.height // 2 - 20, 10, indicator_color)
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, (255, 255, 255, 150), 3)
        
        text = "ЗАБЛОКИРОВАНО" if not self.is_open else "ВЫХОД"
        color = (255, 100, 100) if not self.is_open else (100, 255, 100)
        arcade.draw_text(text, self.center_x, self.center_y - self.height // 2 - 30, color, 16, anchor_x="center", bold=True)
