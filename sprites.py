
import arcade
import time
import random
from constants import *

class Crop(arcade.Sprite):
    def __init__(self, x, y, crop_type="wheat"):
        self.crop_type = crop_type
        self.textures_list = [
            arcade.load_texture(f"assets/{crop_type}_seed.png"),
            arcade.load_texture(f"assets/{crop_type}_growing.png"),
            arcade.load_texture(f"assets/{crop_type}_ripe.png")
        ]
        
        super().__init__(self.textures_list[0], tile_scaling)
        self.center_x = x
        self.center_y = y
        self.state = "seed"
        
        if crop_type == "wheat":
             self.stage_duration = 15.0
             self.sell_price = 15
        elif crop_type == "carrot":
             self.stage_duration = 25.0
             self.sell_price = 40
        elif crop_type == "cauliflower":
             self.stage_duration = 40.0
             self.sell_price = 80
        else:
             self.stage_duration = 15.0
             self.sell_price = 15
             
        self.growth_timer = 0
        
    def update(self, delta_time: float = 1/60):
        if self.state == "ripe":
            self.scale = tile_scaling
            return

        self.growth_timer += delta_time
        
        total_time = self.stage_duration * 2
        overall_progress = min(1.0, self.growth_timer / total_time)
        self.scale = tile_scaling * (0.4 + overall_progress * 0.6)
        
        if self.state == "seed" and self.growth_timer > self.stage_duration:
            self.state = "growing"
            self.texture = self.textures_list[1]
            if self.crop_type == "carrot": self.color = (100, 255, 100)
            elif self.crop_type == "cauliflower": self.color = (150, 200, 150)
            
        elif self.state == "growing" and self.growth_timer > self.stage_duration * 2:
            self.state = "ripe"
            self.texture = self.textures_list[2]
            self.scale = tile_scaling
            if self.crop_type == "carrot": self.color = (255, 150, 50)
            elif self.crop_type == "cauliflower": self.color = (255, 255, 255)
            elif self.crop_type == "wheat": self.color = (255, 220, 100)


    def is_ripe(self):
        return self.state == "ripe"

class Farmer(arcade.Sprite):
    def __init__(self, filename, scale):
        super().__init__(filename, scale)
        self.speed = 5
        self.facing_left = False
        
    def update(self):
        # Movement is now handled by PhysicsEngineSimple in GameView.
        # We only handle animation flipping here.
        
        if self.change_x < 0 and not self.facing_left:
            self.texture = self.texture.flip_left_right()
            self.facing_left = True
        elif self.change_x > 0 and self.facing_left:
            self.texture = self.texture.flip_left_right()
            self.facing_left = False

class Worker(arcade.Sprite):
    def __init__(self, x, y, worker_type="harvester"):
        super().__init__("assets/worker.png", tile_scaling)
        self.center_x = x
        self.center_y = y
        self.worker_type = worker_type
        self.target = None
        self.facing_left = False
        
        # Base Stats
        self.level = 1
        self.walk_speed = 2.0
        self.action_speed = 1.5
        self.max_stamina = 50
        self.stamina = self.max_stamina
        self.qty = 1
        
        self.is_sleeping = False
        self.sleep_timer = 0
        self.action_cooldown = 0
        
        # Tint
        if worker_type == "planter":
            self.color = (200, 200, 255)
        else:
            self.color = (255, 200, 200)
            
    def update(self, delta_time, field):
        if self.is_sleeping:
            self.sleep_timer -= delta_time
            if self.sleep_timer <= 0:
                self.is_sleeping = False
                self.stamina = self.max_stamina
            return None

        if self.action_cooldown > 0:
            self.action_cooldown -= delta_time
            return None

        if self.worker_type == "harvester":
            return self.handle_harvesting(field)
        elif self.worker_type == "planter":
            return self.handle_planting(field)
        return None

    def consume_stamina(self):
        self.stamina -= 1
        if self.stamina <= 0:
            self.is_sleeping = True
            self.sleep_timer = 20.0
            self.target = None

    def handle_harvesting(self, field):
        if not self.target or self.target not in field.crops or not self.target.is_ripe():
             ripe_crops = [c for c in field.crops if c.is_ripe()]
             if ripe_crops:
                 self.target = random.choice(ripe_crops)
             else:
                 self.target = None
        
        if self.target:
             self.move_towards(self.target)
             if arcade.check_for_collision(self, self.target):
                 if self.target.is_ripe():
                      target = self.target
                      self.target = None
                      self.action_cooldown = self.action_speed
                      self.consume_stamina()
                      return target
        return None

    def handle_planting(self, field):
        if not self.target:
            empty_tiles = []
            for tile in field.tiles:
                is_occupied = False
                for crop in field.crops:
                    if abs(crop.center_x - tile.center_x) < 5 and abs(crop.center_y - tile.center_y) < 5:
                         is_occupied = True
                         break
                if not is_occupied:
                    empty_tiles.append(tile)
            
            if empty_tiles:
                 self.target = random.choice(empty_tiles)
            else:
                 self.target = None
                 
        if self.target:
            self.move_towards(self.target)
            if arcade.check_for_collision(self, self.target):
                 target = self.target
                 self.target = None
                 self.action_cooldown = self.action_speed
                 self.consume_stamina()
                 return target
        return None

    def move_towards(self, target_sprite):
        prev_x = self.center_x
        
        if abs(self.center_x - target_sprite.center_x) > self.walk_speed:
            if self.center_x < target_sprite.center_x:
                self.center_x += self.walk_speed
            else:
                self.center_x -= self.walk_speed
        else:
            self.center_x = target_sprite.center_x

        if abs(self.center_y - target_sprite.center_y) > self.walk_speed:
            if self.center_y < target_sprite.center_y:
                self.center_y += self.walk_speed
            else:
                self.center_y -= self.walk_speed
        else:
            self.center_y = target_sprite.center_y
            
        move_x = self.center_x - prev_x
        if move_x < -0.1 and not self.facing_left:
            self.texture = self.texture.flip_left_right()
            self.facing_left = True
        elif move_x > 0.1 and self.facing_left:
            self.texture = self.texture.flip_left_right()
            self.facing_left = False
