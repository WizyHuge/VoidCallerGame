import arcade
import math
import random
from core import constants as const

class WaveParticle(arcade.Sprite):    
    def __init__(self, x, y, angle, power):
        super().__init__(const.resource_path("assets/particle.png"), scale=0.15, center_x=x, center_y=y)
        self.width = self.height = 5
        speed = const.PULSE_SPEED * power
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.age = 0.0
        self.lifetime = random.uniform(3.0, 4.0)
        self.fade_start = self.lifetime * 0.6
        self.stuck = False
        self.is_on_entity = False
        self.color = (0, 200, 255)
        self.alpha = 255
    
    def update_particle(self, delta_time, walls, entities):
        self.age += delta_time
        if self.age >= self.lifetime:
            self.kill()
        
        t = (self.age - self.fade_start) / (self.lifetime - self.fade_start)
        self.alpha = max(0, int(255 * (1 - t)))
        
        if self.stuck:
            return None
        
        self.center_x += self.vx * delta_time
        self.center_y += self.vy * delta_time
        
        wall_hits = arcade.check_for_collision_with_list(self, walls)
        if wall_hits:
            self._stick()
            return wall_hits[0]
        
        entity_hits = arcade.check_for_collision_with_list(self, entities)
        if entity_hits:
            self._stick(on_entity=True)
            return entity_hits[0]
        
        return None
    
    def _stick(self, on_entity=False):
        self.stuck = True
        self.is_on_entity = on_entity
        self.lifetime = self.age + 2.0
        self.vx = self.vy = 0
        if on_entity:
            self.color = (255, 0, 0)

class WaveFront:
    def __init__(self, x, y, angle, power):
        self.particles = arcade.SpriteList(use_spatial_hash=True)
        self.hit_objects = set()
        self.hit_entities = set()
        self.active = True
        
        count = int(150 * power)
        spread = math.pi
        for i in range(count):
            a = angle + random.uniform(-spread / 5, spread / 5)
            px = x + random.uniform(-5, 5)
            py = y + random.uniform(-5, 5)
            self.particles.append(WaveParticle(px, py, a, power))
    
    def update(self, delta_time, walls, entities):
        if not self.active:
            return [], []
        
        new_objects = []
        new_entities = []
        
        for p in self.particles:
            hit = p.update_particle(delta_time, walls, entities)
            if not hit:
                continue
            
            if hit in entities:
                if hit not in self.hit_entities:
                    self.hit_entities.add(hit)
                    new_entities.append(hit)
            else:
                if hit not in self.hit_objects:
                    self.hit_objects.add(hit)
                    new_objects.append(hit)
        
        if len(self.particles) == 0:
            self.active = False
        
        return new_objects, new_entities
    
    def draw(self):
        for particle in self.particles:
            particle.color = particle.color
            if particle.is_on_entity:
                arcade.draw_circle_filled(particle.center_x, particle.center_y, 3, (255, 0, 0, particle.alpha))
            else:
                arcade.draw_circle_filled(particle.center_x, particle.center_y, 3, (0, 200, 255, particle.alpha))

class Pulsar:
    def __init__(self):
        self.waves = []
        self.cooldown = 0.0
        self.ready = True
        self.aim_angle = 0.0
    
    def get_cooldown_percent(self):
        if self.ready:
            return 1.0
        return max(0.0, 1.0 - self.cooldown / const.PULSE_COOLDOWN)
    
    def emit_wave(self, x, y, angle, power=1.5):
        if not self.ready:
            return False
        self.waves.append(WaveFront(x, y, angle, power))
        self.cooldown = const.PULSE_COOLDOWN
        self.ready = False
        return True
    
    def update(self, delta_time, walls, entities):
        if not self.ready:
            self.cooldown -= delta_time
            if self.cooldown <= 0:
                self.ready = True
        
        for wave in self.waves[:]:
            wave.update(delta_time, walls, entities)
            if not wave.active:
                self.waves.remove(wave)
    
    def draw(self):
        for wave in self.waves:
            wave.draw()
    
    def update_aim(self, mx, my, px, py):
        self.aim_angle = math.atan2(my - py, mx - px)
    
    def draw_aim(self, px, py):
        if not self.ready:
            return
        length = 50
        ex = px + math.cos(self.aim_angle) * length
        ey = py + math.sin(self.aim_angle) * length
        arcade.draw_line(px, py, ex, ey, (0, 255, 255), 2)
