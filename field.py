
import arcade
from constants import *
from sprites import Crop

class Field:
    def __init__(self, x, y, width, height, crop_type, unlock_cost=0, is_unlocked=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.crop_type = crop_type
        self.unlock_cost = unlock_cost
        self.is_unlocked = is_unlocked
        
        self.tiles = arcade.SpriteList()
        self.crops = arcade.SpriteList()
        self.workers = arcade.SpriteList()
        
        self.generate_field()

    def generate_field(self):
        for r in range(self.width):
            for c in range(self.height):
                tile = arcade.Sprite("assets/soil.png", tile_scaling)
                tile.center_x = self.x + r * grid_size + grid_size/2
                tile.center_y = self.y + c * grid_size + grid_size/2
                
                if not self.is_unlocked:
                    tile.color = (100, 100, 100)
                    
                self.tiles.append(tile)

    def unlock(self):
        self.is_unlocked = True
        for tile in self.tiles:
            tile.color = (255, 255, 255)

    def draw(self):
        self.tiles.draw(filter=arcade.gl.NEAREST)
        self.crops.draw(filter=arcade.gl.NEAREST)
        self.workers.draw(filter=arcade.gl.NEAREST)
        
        if not self.is_unlocked:
            arcade.draw_text(f"Закрыто\n${self.unlock_cost}", self.x + (self.width*grid_size)/2, self.y + (self.height*grid_size)/2, 
                             arcade.color.WHITE, 14, anchor_x="center", anchor_y="center")

    def update(self, delta_time):
        if not self.is_unlocked:
            return 0
            
        self.crops.update(delta_time)
        
        money_earned = 0
        for worker in self.workers:
            result = worker.update(delta_time, self)
            if result:
                if isinstance(result, Crop):
                     result.kill()
                     money_earned += result.sell_price
                elif isinstance(result, arcade.Sprite):
                     is_occ = False
                     for c in self.crops:
                          if abs(c.center_x - result.center_x) < 5 and abs(c.center_y - result.center_y) < 5:
                               is_occ = True
                               break
                     if not is_occ:
                          new_crop = Crop(result.center_x, result.center_y, self.crop_type)
                          self.crops.append(new_crop)
                          worker.action_cooldown = 1.0
                
        return money_earned

    def is_point_in_field(self, x, y):
         x_min = self.x
         x_max = self.x + self.width * grid_size
         y_min = self.y
         y_max = self.y + self.height * grid_size
         return x_min <= x <= x_max and y_min <= y <= y_max
