import arcade
import math
import random
from core import constants as const

class VisionSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.vision_radius = 300
        self.echo_holes = []
        self.static_intensity = 0.0
        self.shock = 0.0
        self.light_sources = []
        self.base_light_intensity = 0.3
        self.highlighted_objects = []
    
    def update(self, delta_time, player_damaged):
        self.echo_holes = [hole for hole in self.echo_holes if hole[3] > 0]
        for i in range(len(self.echo_holes)):
            x, y, r, alpha = self.echo_holes[i]
            self.echo_holes[i] = (x, y, r, alpha - delta_time * 2)
        
        self.highlighted_objects = [(x, y, color, alpha - delta_time * 1.5) 
                                     for x, y, color, alpha in self.highlighted_objects 
                                     if alpha - delta_time * 1.5 > 0]
        
        self.static_intensity = max(0, self.static_intensity - delta_time * 1.5)
        
        if player_damaged:
            self.shock = 1.0
        self.shock = max(0, self.shock - delta_time * 3)
    
    def highlight_object(self, x, y, color=(0, 255, 0), duration=1.0):
        self.highlighted_objects.append((x, y, color, duration))
    
    def get_visibility_alpha(self, target_x, target_y, player_x, player_y, wall_list):
        distance = math.hypot(target_x - player_x, target_y - player_y)
        vision_radius = self.vision_radius * (0.7 + 0.3 * self.base_light_intensity)
        
        if distance > vision_radius:
            alpha = 0
        else:
            alpha = int(255 * (1.0 - (distance / vision_radius)))
            
            if alpha > 0 and not self.is_visible_through_walls(player_x, player_y, target_x, target_y, wall_list):
                alpha = int(alpha * 0.1)
        
        for gen_x, gen_y, radius in self.light_sources:
            dist_to_gen = math.hypot(target_x - gen_x, target_y - gen_y)
            if dist_to_gen < radius:
                gen_alpha = int(255 * (1.0 - (dist_to_gen / radius)))
                alpha = max(alpha, gen_alpha)
        
        for hole_x, hole_y, hole_radius, hole_alpha in self.echo_holes:
            dist_to_hole = math.hypot(target_x - hole_x, target_y - hole_y)
            if dist_to_hole < hole_radius:
                echo_alpha = int(200 * hole_alpha * (1.0 - (dist_to_hole / hole_radius)))
                alpha = max(alpha, echo_alpha)
        
        return min(255, alpha)
    
    def is_visible_through_walls(self, player_x, player_y, target_x, target_y, wall_list):
        distance = math.hypot(target_x - player_x, target_y - player_y)
        if distance < const.TILE_SIZE:
            return True
        
        steps = max(int(distance / (const.TILE_SIZE * 0.5)), 1)
        dx = (target_x - player_x) / steps
        dy = (target_y - player_y) / steps
        
        for i in range(1, steps):
            check_x = player_x + dx * i
            check_y = player_y + dy * i
            for wall in wall_list:
                if (abs(wall.center_x - check_x) < const.TILE_SIZE * 0.4 and 
                    abs(wall.center_y - check_y) < const.TILE_SIZE * 0.4):
                    return False
        return True
    
    def draw_visibility_mask(self, player_x, player_y, camera_x=0, camera_y=0):
        vision_radius = self.vision_radius * (0.7 + 0.3 * self.base_light_intensity)
        num_rings = 50
        
        arcade.draw_circle_outline(player_x, player_y, self.screen_width // 1.5, (0, 0, 0, 255), self.screen_width // 2)
        
        for i in range(num_rings - 1, -1, -1):
            outer_radius = vision_radius * (i + 1) / num_rings
            inner_radius = vision_radius * i / num_rings
            alpha = int(255 * (i / num_rings))
            ring_width = outer_radius - inner_radius
            
            if ring_width > 0:
                arcade.draw_circle_outline(player_x, player_y, (outer_radius + inner_radius) / 2, (0, 0, 0, alpha), border_width=int(ring_width) + 1)
        
        for gen_x, gen_y, radius in self.light_sources:
            screen_x = gen_x - camera_x + self.screen_width // 2
            screen_y = gen_y - camera_y + self.screen_height // 2
            
            if -radius*2 <= screen_x <= self.screen_width + radius*2 and -radius*2 <= screen_y <= self.screen_height + radius*2:
                num_gen_rings = 40
                for i in range(num_gen_rings - 1, -1, -1):
                    outer_radius = radius * (i + 1) / num_gen_rings
                    inner_radius = radius * i / num_gen_rings
                    alpha = int(220 * (i / num_gen_rings))
                    ring_width = outer_radius - inner_radius
                    
                    if ring_width > 0:
                        arcade.draw_circle_outline(screen_x, screen_y, (outer_radius + inner_radius) / 2, (0, 0, 0, alpha), border_width=int(ring_width) + 1)
    
    def draw_highlighted_objects(self, camera_x, camera_y):
        for obj_x, obj_y, color, alpha in self.highlighted_objects:
            screen_x = obj_x - camera_x + self.screen_width // 2
            screen_y = obj_y - camera_y + self.screen_height // 2
            
            if -100 <= screen_x <= self.screen_width + 100 and -100 <= screen_y <= self.screen_height + 100:
                glow_alpha = int(alpha * 255)
                arcade.draw_circle_filled(screen_x, screen_y, 60, (*color, glow_alpha // 3))
                arcade.draw_circle_filled(screen_x, screen_y, 40, (*color, glow_alpha // 2))
                arcade.draw_circle_filled(screen_x, screen_y, 25, (*color, glow_alpha))
    
    def draw_vision_overlay(self):
        intensity = 0.2 + self.static_intensity * 0.2
        edge_width = 40 + intensity * 20
        particle_count = int(80 * intensity)
        
        for _ in range(particle_count // 4):
            arcade.draw_point(random.uniform(0, edge_width), random.uniform(0, self.screen_height), (200, 200, 255, 90), 2)
        
        for _ in range(particle_count // 4):
            arcade.draw_point(random.uniform(self.screen_width - edge_width, self.screen_width), random.uniform(0, self.screen_height), (200, 200, 255, 90), 2)
        
        for _ in range(particle_count // 4):
            arcade.draw_point(random.uniform(0, self.screen_width), random.uniform(self.screen_height - edge_width, self.screen_height), (200, 200, 255, 90), 2)
        
        for _ in range(particle_count // 4):
            arcade.draw_point(random.uniform(0, self.screen_width), random.uniform(0, edge_width), (200, 200, 255, 90), 2)
        
        corner_size = edge_width * 1.5
        for _ in range(int(particle_count * 0.3)):
            rand = random.random()
            if rand < 0.25:
                x = random.uniform(0, corner_size)
                y = random.uniform(self.screen_height - corner_size, self.screen_height)
            elif rand < 0.5:
                x = random.uniform(self.screen_width - corner_size, self.screen_width)
                y = random.uniform(self.screen_height - corner_size, self.screen_height)
            elif rand < 0.75:
                x = random.uniform(0, corner_size)
                y = random.uniform(0, corner_size)
            else:
                x = random.uniform(self.screen_width - corner_size, self.screen_width)
                y = random.uniform(0, corner_size)
            arcade.draw_point(x, y, (200, 200, 255, 70), 2)
