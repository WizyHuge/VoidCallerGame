import arcade
import random
from core import constants as const

class GameMap:
    def __init__(self):
        self.width = 70
        self.height = 50
        self.tile_size = const.TILE_SIZE
        self.rooms = []
        self.tunnels = []
    
    def create_map(self, wall_list, floor_list):
        wall_list.clear()
        floor_list.clear()
        self.rooms = []
        self.tunnels = []
        
        num_rooms = random.randint(10, 15)
        min_size = 6
        max_size = 14
        
        for _ in range(num_rooms):
            w = random.randint(min_size, max_size)
            h = random.randint(min_size, max_size)
            x1 = random.randint(2, self.width - w - 3)
            y1 = random.randint(2, self.height - h - 3)
            x2 = x1 + w - 1
            y2 = y1 + h - 1
            new_room = (x1, x2, y1, y2)
            
            can_place = True
            for other_room in self.rooms:
                if self.per_rooms(new_room, other_room):
                    can_place = False
                    break
            
            if can_place:
                self.rooms.append(new_room)
                if len(self.rooms) > 1:
                    self.create_tunnel(new_room, self.rooms[-2])
        
        self.create_connections()
        self.build_sprites(wall_list, floor_list)
    
    def per_rooms(self, room1, room2):
        x1_1, x2_1, y1_1, y2_1 = room1
        x1_2, x2_2, y1_2, y2_2 = room2
        return (x1_1 <= x2_2 + 2 and x2_1 >= x1_2 - 2 and y1_1 <= y2_2 + 2 and y2_1 >= y1_2 - 2)
    
    def create_tunnel(self, room1, room2):
        x1_1, x2_1, y1_1, y2_1 = room1
        x1_2, x2_2, y1_2, y2_2 = room2
        
        cx1 = (x1_1 + x2_1) // 2
        cy1 = (y1_1 + y2_1) // 2
        cx2 = (x1_2 + x2_2) // 2
        cy2 = (y1_2 + y2_2) // 2
        
        if random.random() < 0.5:
            for x in range(min(cx1, cx2), max(cx1, cx2) + 1):
                self.tunnels.append((x, cy1))
                self.tunnels.append((x, cy1 + 1))
            for y in range(min(cy1, cy2), max(cy1, cy2) + 1):
                self.tunnels.append((cx2, y))
                self.tunnels.append((cx2 + 1, y))
        else:
            for y in range(min(cy1, cy2), max(cy1, cy2) + 1):
                self.tunnels.append((cx1, y))
                self.tunnels.append((cx1 + 1, y))
            for x in range(min(cx1, cx2), max(cx1, cx2) + 1):
                self.tunnels.append((x, cy2))
                self.tunnels.append((x, cy2 + 1))
    
    def create_connections(self):
        if len(self.rooms) < 3:
            return
        
        num_extra = random.randint(2, min(4, len(self.rooms) - 1))
        for _ in range(num_extra):
            room1 = random.choice(self.rooms)
            room2 = random.choice(self.rooms)
            if room1 != room2:
                self.create_tunnel(room1, room2)
    
    def build_sprites(self, wall_list, floor_list):
        grid = [[0 for _ in range(self.height)] for _ in range(self.width)]
        
        for room in self.rooms:
            x1, x2, y1, y2 = room
            for x in range(x1, x2 + 1):
                for y in range(y1, y2 + 1):
                    if 0 <= x < self.width and 0 <= y < self.height:
                        grid[x][y] = 1
        
        for x, y in self.tunnels:
            if 0 <= x < self.width and 0 <= y < self.height:
                grid[x][y] = 1
        
        for x in range(self.width):
            for y in range(self.height):
                world_x = x * self.tile_size + self.tile_size // 2
                world_y = y * self.tile_size + self.tile_size // 2
                
                if grid[x][y] == 1:
                    floor = arcade.SpriteSolidColor(self.tile_size, self.tile_size, color=arcade.color.DARK_SLATE_GRAY)
                    floor.center_x = world_x
                    floor.center_y = world_y
                    floor_list.append(floor)
                else:
                    wall = arcade.SpriteSolidColor(self.tile_size, self.tile_size, color=arcade.color.BLACK)
                    wall.center_x = world_x
                    wall.center_y = world_y
                    wall_list.append(wall)
