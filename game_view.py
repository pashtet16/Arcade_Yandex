
import arcade
import random
import math
import os
from constants import *
from sprites import Crop, Worker, Farmer
from field import Field
from ui_manager import UIManager
from arcade.particles import Emitter, EmitBurst, FadeParticle


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.money = starting_money
        # Use standard Camera for better compatibility with Arcade 2.6+
        self.camera = None 
        self.gui_camera = None
        self.ui_manager = None
        self.farmer = None
        self.farmer_list = None
        self.grass_list = None
        self.wall_list = None
        self.fields = []
        self.all_workers = arcade.SpriteList()
        self.emitters = []
        
        self.physics_engine = None
        self.hovered_worker = None # Worker under cursor
        
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        
        self.level_message = ""
        self.level_timer = 0
        
        # Sounds
        self.sound_harvest = None
        self.sound_plant = None
        self.sound_unlock = None

    def setup(self):
        import db_manager
        save_data = db_manager.load_game()
        
        # Load sounds safely
        try:
            if os.path.exists("assets/sounds/harvest.wav"):
                self.sound_harvest = arcade.load_sound("assets/sounds/harvest.wav")
            if os.path.exists("assets/sounds/plant.wav"):
                self.sound_plant = arcade.load_sound("assets/sounds/plant.wav")
            if os.path.exists("assets/sounds/unlock.wav"):
                self.sound_unlock = arcade.load_sound("assets/sounds/unlock.wav")
        except Exception:
            print("Warning: Sound files not found.")

        # Initialize Cameras
        self.camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        
        self.ui_manager = UIManager(self.window)
        self.background_color = (30, 180, 50)
        self.grass_list = arcade.SpriteList()
        
        # Generate background
        for x in range(-25, 35):
            for y in range(-15, 30):
                grass = arcade.Sprite("assets/grass.png", tile_scaling)
                grass.center_x = x * grid_size + grid_size/2
                grass.center_y = y * grid_size + grid_size/2
                self.grass_list.append(grass)

        # Physics Bounds
        self.min_x, self.max_x = -500, 1500
        self.min_y, self.max_y = -300, 1000
        
        self.wall_list = arcade.SpriteList()
        self.create_bounds()

        self.farmer = Farmer("assets/farmer.png", character_scaling)
        self.farmer.center_x = 400
        self.farmer.center_y = 300
        self.farmer_list = arcade.SpriteList()
        self.farmer_list.append(self.farmer)
        
        # Initialize Physics Engine
        self.physics_engine = arcade.PhysicsEngineSimple(self.farmer, [self.wall_list, self.all_workers])
        
        # Load save
        worker_data = {}
        if save_data:
            self.money = save_data["money"]
            unlocked_indices = save_data["unlocked_fields"]
            worker_data = save_data.get("worker_data", {})
        else:
            self.money = starting_money
            unlocked_indices = ["0"] 
            
        self.fields = []
            
        # Field 1 (Wheat)
        f1 = Field(150, 200, 5, 4, "wheat", is_unlocked=("0" in unlocked_indices))
        w1_1 = Worker(150, 250, "planter")
        w1_2 = Worker(250, 250, "harvester")
        f1.workers.append(w1_1)
        f1.workers.append(w1_2)
        self.all_workers.append(w1_1)
        self.all_workers.append(w1_2)
        self.fields.append(f1)
        
        # Field 2 (Carrot)
        f2 = Field(500, 200, 5, 4, "carrot", unlock_cost=50, is_unlocked=("1" in unlocked_indices))
        if f2.is_unlocked:
            w2_1 = Worker(f2.x + grid_size, f2.y + grid_size, "planter")
            w2_2 = Worker(f2.x + grid_size*2, f2.y + grid_size, "harvester")
            f2.workers.append(w2_1)
            f2.workers.append(w2_2)
            self.all_workers.append(w2_1)
            self.all_workers.append(w2_2)
        self.fields.append(f2)

        # Field 3 (Cauliflower)
        f3 = Field(850, 200, 5, 4, "cauliflower", unlock_cost=150, is_unlocked=("2" in unlocked_indices))
        if f3.is_unlocked:
            w3_1 = Worker(f3.x + grid_size, f3.y + grid_size, "planter")
            w3_2 = Worker(f3.x + grid_size*2, f3.y + grid_size, "harvester")
            f3.workers.append(w3_1)
            f3.workers.append(w3_2)
            self.all_workers.append(w3_1)
            self.all_workers.append(w3_2)
        self.fields.append(f3)

        # Restore workers
        for f_idx, field in enumerate(self.fields):
            for w_idx, worker in enumerate(field.workers):
                key = f"{f_idx}_{w_idx}"
                if key in worker_data:
                    w_stats = worker_data[key]
                    worker.level = w_stats.get("level", 1)
                    worker.walk_speed = w_stats.get("walk_speed", 2.0)
                    worker.action_speed = w_stats.get("action_speed", 1.5)
                    worker.max_stamina = w_stats.get("max_stamina", 50)
                    worker.stamina = worker.max_stamina
                    worker.qty = w_stats.get("qty", 1)

    def create_bounds(self):
        """Creates invisible walls for physics engine"""
        thickness = 50
        width = self.max_x - self.min_x
        height = self.max_y - self.min_y
        cx = (self.min_x + self.max_x) / 2
        cy = (self.min_y + self.max_y) / 2
        
        # Walls
        walls_data = [
            (cx, self.min_y - thickness/2, width, thickness), # Bottom
            (cx, self.max_y + thickness/2, width, thickness), # Top
            (self.min_x - thickness/2, cy, thickness, height), # Left
            (self.max_x + thickness/2, cy, thickness, height), # Right
        ]
        
        for wx, wy, w, h in walls_data:
             wall = arcade.SpriteSolidColor(int(w), int(h), arcade.color.TRANSPARENT_BLACK)
             wall.center_x = wx
             wall.center_y = wy
             self.wall_list.append(wall)

    def spawn_particles(self, x, y, color):
        """Emits particles for visual effect"""
        emitter = Emitter(
            center_xy=(x, y),
            emit_controller=EmitBurst(15),
            particle_factory=lambda emitter: FadeParticle(
                filename_or_texture=arcade.make_circle_texture(8, color),
                change_xy=(random.uniform(-2.5, 2.5), random.uniform(-2.5, 2.5)),
                lifetime=0.6
            )
        )
        self.emitters.append(emitter)
        
    def on_draw(self):
        self.clear()
        
        self.camera.use()
        
        self.grass_list.draw(filter=arcade.gl.NEAREST)
        
        for field in self.fields:
            field.draw()
            
            for worker in field.workers:
                if worker.is_sleeping:
                    bounce = math.sin(arcade.get_window().time * 3) * 5
                    arcade.draw_text("Zzz...", worker.center_x, worker.center_y + 40 + bounce, 
                                     arcade.color.WHITE, 14, anchor_x="center")
                    arcade.draw_rect_filled(arcade.XYWH(worker.center_x, worker.center_y + 35, 30, 4), arcade.color.RED)
                    progress = worker.sleep_timer / 20.0
                    arcade.draw_rect_filled(arcade.XYWH(worker.center_x - (1-progress)*15, worker.center_y + 35, 30 * progress, 4), arcade.color.CYAN)
            
        self.farmer_list.draw(filter=arcade.gl.NEAREST)
        
        # Draw particles
        for emitter in self.emitters:
            emitter.draw()
        
        self.gui_camera.use()
        
        arcade.draw_text(f"Деньги: ${int(self.money)}", 30, self.window.height - 45, (255, 255, 255), 24, bold=True)
        arcade.draw_text("ЛКМ - Действие", self.window.width - 250, self.window.height - 45, (200, 200, 200), 14)
        
        if self.level_message:
            arcade.draw_text(self.level_message, self.window.width/2, self.window.height - 100,
                             arcade.color.GOLD, 24, anchor_x="center", bold=True)

        self.ui_manager.draw()
        # Draw HUD if hovering over worker and menu is closed
        if self.hovered_worker and not self.ui_manager.active_window:
            self.ui_manager.draw_worker_hud(self.hovered_worker)

    def on_update(self, delta_time):
        if self.money >= 1000:
            from menu_view import WinView
            win_view = WinView(self.money)
            self.window.show_view(win_view)
            return

        # Player Movement
        self.farmer.change_x = 0
        self.farmer.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.farmer.change_y = self.farmer.speed
        elif self.down_pressed and not self.up_pressed:
            self.farmer.change_y = -self.farmer.speed
        
        if self.left_pressed and not self.right_pressed:
            self.farmer.change_x = -self.farmer.speed
        elif self.right_pressed and not self.left_pressed:
            self.farmer.change_x = self.farmer.speed

        if self.farmer.change_x != 0 and self.farmer.change_y != 0:
            self.farmer.change_x *= 0.707
            self.farmer.change_y *= 0.707

        # Physics Engine Update (Handles collision and movement)
        self.physics_engine.update()
        self.farmer.update() # Animation only

        # Update fields
        for field in self.fields:
            money_earned = field.update(delta_time)
            self.money += money_earned

        # Update particles
        self.emitters = [e for e in self.emitters if not e.can_reap()]
        for emitter in self.emitters:
            emitter.update()

        # Autosave
        if arcade.get_window().time % 5 < delta_time:
            self.save_progress()

        if self.level_timer > 0:
            self.level_timer -= delta_time
            if self.level_timer <= 0:
                self.level_message = ""

        self.scroll_to_player()

    def scroll_to_player(self):
        target_x, target_y = self.farmer.position
        curr_x, curr_y = self.camera.position
        
        # Smooth camera follow
        self.camera.position = (
            curr_x + (target_x - curr_x) * 0.1,
            curr_y + (target_y - curr_y) * 0.1
        )

    def on_mouse_motion(self, x, y, dx, dy):
        """Track mouse for HUD"""
        world_x, world_y, _ = self.camera.unproject((x, y))
        
        found = False
        for field in self.fields:
            hit_list = arcade.get_sprites_at_point((world_x, world_y), field.workers)
            if hit_list:
                self.hovered_worker = hit_list[0]
                found = True
                break
        
        if not found:
            self.hovered_worker = None

    def on_mouse_press(self, x, y, button, modifiers):
        ui_res = self.ui_manager.on_mouse_press(x, y)
        if ui_res == "handled":
            return
        elif ui_res and ui_res[0] == "upgrade_stat":
            _, worker, stat, cost = ui_res
            if self.money >= cost:
                self.money -= cost
                self.apply_upgrade(worker, stat)
                self.save_progress()
            return
        
        world_x, world_y, _ = self.camera.unproject((x, y))
        
        for field in self.fields:
            workers_clicked = arcade.get_sprites_at_point((world_x, world_y), field.workers)
            if workers_clicked:
                self.ui_manager.show_field_upgrade(field)
                return
            
            if not field.is_unlocked:
                if field.is_point_in_field(world_x, world_y):
                    if self.money >= field.unlock_cost:
                        self.money -= field.unlock_cost
                        field.unlock()
                        w_p = Worker(field.x + grid_size, field.y + grid_size, "planter")
                        w_h = Worker(field.x + grid_size*2, field.y + grid_size, "harvester")
                        field.workers.append(w_p)
                        field.workers.append(w_h)
                        self.all_workers.append(w_p)
                        self.all_workers.append(w_h)
                        self.save_progress()
                        
                        lvl = sum(1 for f in self.fields if f.is_unlocked)
                        self.level_message = f"УРОВЕНЬ {lvl} ОТКРЫТ!"
                        self.level_timer = 3.0
                        if self.sound_unlock: arcade.play_sound(self.sound_unlock)
                    return
            else:
                # Harvest
                crops_clicked = arcade.get_sprites_at_point((world_x, world_y), field.crops)
                for crop in crops_clicked:
                    if crop.is_ripe():
                        crop.kill()
                        self.money += crop.sell_price
                        self.spawn_particles(crop.center_x, crop.center_y, arcade.color.GOLD)
                        if self.sound_harvest: arcade.play_sound(self.sound_harvest)
                        return
                
                # Plant
                if field.is_point_in_field(world_x, world_y):
                    local_x = world_x - field.x
                    local_y = world_y - field.y
                    grid_r = int(local_x // grid_size)
                    grid_c = int(local_y // grid_size)
                    
                    tx = field.x + grid_r * grid_size + grid_size/2
                    ty = field.y + grid_c * grid_size + grid_size/2
                    
                    if field.is_point_in_field(tx, ty):
                        occ = any(abs(c.center_x - tx) < 5 and abs(c.center_y - ty) < 5 for c in field.crops)
                        if not occ and self.money >= seed_cost:
                            self.money -= seed_cost
                            field.crops.append(Crop(tx, ty, field.crop_type))
                            self.spawn_particles(tx, ty, arcade.color.DARK_BROWN)
                            if self.sound_plant: arcade.play_sound(self.sound_plant)
                    return

    def save_progress(self):
        import db_manager
        unlocked = [str(i) for i, f in enumerate(self.fields) if f.is_unlocked]
        
        worker_data = {}
        for f_idx, field in enumerate(self.fields):
            for w_idx, worker in enumerate(field.workers):
                key = f"{f_idx}_{w_idx}"
                worker_data[key] = {
                    "level": worker.level,
                    "walk_speed": worker.walk_speed,
                    "action_speed": worker.action_speed,
                    "max_stamina": worker.max_stamina,
                    "qty": worker.qty
                }
        
        db_manager.save_game(self.money, unlocked, worker_data)

    def apply_upgrade(self, worker, stat):
        worker.level += 1
        if stat == "walk_speed":
            worker.walk_speed += 0.5
        elif stat == "action_speed":
            worker.action_speed = max(0.2, worker.action_speed - 0.2)
        elif stat == "qty":
            worker.qty += 1
        elif stat == "max_stamina":
            worker.max_stamina += 25
            worker.stamina = worker.max_stamina

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W: self.up_pressed = True
        elif key == arcade.key.S: self.down_pressed = True
        elif key == arcade.key.A: self.left_pressed = True
        elif key == arcade.key.D: self.right_pressed = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W: self.up_pressed = False
        elif key == arcade.key.S: self.down_pressed = False
        elif key == arcade.key.A: self.left_pressed = False
        elif key == arcade.key.D: self.right_pressed = False
