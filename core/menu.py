import arcade
from core import constants as const
import math

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.pulse = 0.0
        
    def on_show(self):
        arcade.set_background_color(const.COLOR_BACKGROUND)
    
    def on_update(self, delta_time):
        self.pulse += delta_time
    
    def on_draw(self):
        self.clear()
                
        arcade.draw_text(
            "Void Caller",
            self.window.width // 2,
            self.window.height // 2 + 100,
            arcade.color.WHITE,
            60,
            anchor_x="center",
            bold=True
        )
        
        arcade.draw_text(
            "Нажмите ПРОБЕЛ для начала",
            self.window.width // 2,
            self.window.height // 2,
            (*arcade.color.WHITE[:3], 255),
            24,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "Управление:",
            self.window.width // 2,
            self.window.height // 2 - 80,
            arcade.color.GRAY,
            18,
            anchor_x="center",
            bold=True
        )
        
        controls = [
            "WASD - Движение",
            "Мышь - Прицеливание",
            "ЛКМ - Эхолокация",
            "E - Активировать генератор",
            "ESC - Выход"
        ]
        
        y_offset = self.window.height // 2 - 120
        for control in controls:
            arcade.draw_text(
                control,
                self.window.width // 2,
                y_offset,
                arcade.color.GRAY,
                14,
                anchor_x="center"
            )
            y_offset -= 25
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            from core.game_window import VoidCallerWindow
            game_view = VoidCallerWindow()
            self.window.show_view(game_view)
            game_view.setup()
        elif key == arcade.key.ESCAPE:
            arcade.close_window()
