import arcade
import random

class Puzzle:
    def __init__(self, generator):
        self.generator = generator
        self.solved = False
        self.active = False
    
    def activate(self):
        self.active = True
    
    def solve(self):
        if not self.solved:
            self.solved = True
            return True
        return False
    
    def update(self, delta_time):
        pass
    
    def draw(self):
        pass
    
    def on_key_press(self, key):
        return False

class SequencePuzzle(Puzzle):
    def __init__(self, generator):
        super().__init__(generator)
        self.sequence = [1, 2, 3, 4]
        random.shuffle(self.sequence)
        self.player_sequence = []
        self.buttons = []
        self.show_sequence = True
        self.sequence_timer = 0.0
        self.current_sequence_index = 0
    
    def _init_buttons(self):
        if self.generator:
            self.buttons = [
                {'x': self.generator.center_x - 60, 'y': self.generator.center_y - 40, 'num': 1},
                {'x': self.generator.center_x - 20, 'y': self.generator.center_y - 40, 'num': 2},
                {'x': self.generator.center_x + 20, 'y': self.generator.center_y - 40, 'num': 3},
                {'x': self.generator.center_x + 60, 'y': self.generator.center_y - 40, 'num': 4},
            ]
    
    def activate(self):
        super().activate()
        if not self.buttons and self.generator:
            self._init_buttons()
        self.show_sequence = True
        self.sequence_timer = 0.0
        self.current_sequence_index = 0
    
    def update(self, delta_time):
        if self.show_sequence and not self.solved:
            self.sequence_timer += delta_time
            if self.sequence_timer >= 0.5:
                self.sequence_timer = 0.0
                self.current_sequence_index = (self.current_sequence_index + 1) % len(self.sequence)
                if self.current_sequence_index == 0:
                    self.show_sequence = False
    
    def on_key_press(self, key):
        if self.solved or not self.active:
            return False
        
        pressed_num = None
        if key == arcade.key.KEY_1:
            pressed_num = 1
        elif key == arcade.key.KEY_2:
            pressed_num = 2
        elif key == arcade.key.KEY_3:
            pressed_num = 3
        elif key == arcade.key.KEY_4:
            pressed_num = 4
        
        if pressed_num:
            self.player_sequence.append(pressed_num)
            
            if len(self.player_sequence) > len(self.sequence):
                self.player_sequence = []
                return False
            
            for i, num in enumerate(self.player_sequence):
                if num != self.sequence[i]:
                    self.player_sequence = []
                    return False
            
            if len(self.player_sequence) == len(self.sequence):
                self.solve()
                return True
        
        return False
    
    def draw(self):
        if not self.active or self.solved:
            return
        
        if not self.buttons and self.generator:
            self._init_buttons()
        
        for btn in self.buttons:
            color = (100, 200, 100) if btn['num'] in self.player_sequence else (100, 100, 100)
            if self.show_sequence and btn['num'] == self.sequence[self.current_sequence_index]:
                color = (255, 255, 0)
            
            arcade.draw_circle_filled(btn['x'], btn['y'], 15, color)
            arcade.draw_text(str(btn['num']), btn['x'], btn['y'], (255, 255, 255), 14, anchor_x="center", anchor_y="center")

class HoldButtonPuzzle(Puzzle):
    def __init__(self, generator):
        super().__init__(generator)
        self.hold_time = 0.0
        self.required_time = 3.0
        self.holding = False
    
    def update(self, delta_time):
        if self.holding and not self.solved:
            self.hold_time += delta_time
            if self.hold_time >= self.required_time:
                self.solve()
    
    def on_key_press(self, key):
        if key == arcade.key.SPACE and not self.solved:
            self.holding = True
            return True
        return False
    
    def on_key_release(self, key):
        if key == arcade.key.SPACE:
            self.holding = False
            if not self.solved:
                self.hold_time = 0.0
            return True
        return False
    
    def draw(self):
        if not self.active or self.solved:
            return
        
        progress = self.hold_time / self.required_time
        bar_width = 100
        bar_height = 10
        x = self.generator.center_x
        y = self.generator.center_y - 50
        
        arcade.draw_lrbt_rectangle_filled(x - bar_width/2, x + bar_width/2, y - bar_height/2, y + bar_height/2, (50, 50, 50, 200))
        
        if progress > 0:
            arcade.draw_lrbt_rectangle_filled(x - bar_width/2, x - bar_width/2 + bar_width * progress, y - bar_height/2, y + bar_height/2, (0, 255, 0, 200))
        
        if self.holding:
            arcade.draw_text("Удерживайте ПРОБЕЛ", x, y - 25, (255, 255, 255), 16, anchor_x="center")
