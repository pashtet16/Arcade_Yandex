
import math
import arcade
import random
import os
from constants import *


class StartView(arcade.View):
    def __init__(self):
        super().__init__()

        self.show_press_text = False
        self.elapsed_time = 0
        
        if os.path.exists("assets/farm_background.png"):
            self.background = arcade.load_texture("assets/farm_background.png")
        else:
            self.background = None
            
        self.particles = []
        self._create_particles()
        
        # Load music safely
        self.bgm = None
        self.bgm_player = None
        try:
            if os.path.exists("assets/music/sound.mp3"):
                self.bgm = arcade.load_sound("assets/music/sound.mp3")
        except Exception:
            pass

    def _create_particles(self):
        for _ in range(20):
            particle = {
                'x': random.uniform(0, sc_width),
                'y': random.uniform(0, sc_height),
                'size': random.uniform(2, 6),
                'speed': random.uniform(0.5, 1.5),
                'color': random.choice([
                    arcade.color.GOLD,
                    arcade.color.YELLOW,
                    arcade.color.WHITE
                ]),
                'angle': random.uniform(0, 2 * math.pi)
            }
            self.particles.append(particle)

    def on_draw(self):
        self.clear()

        if self.background:
            arcade.draw_texture_rect(
                self.background,
                arcade.XYWH(sc_width // 2, sc_height // 2, sc_width, sc_height)
            )
        else:
             arcade.draw_rect_filled(arcade.XYWH(sc_width//2, sc_height//2, sc_width, sc_height), (30, 100, 30))

        arcade.draw_lrbt_rectangle_filled(
            left=sc_width // 2 - 300,
            right=sc_width // 2 + 300,
            top=sc_height // 2 + 100,
            bottom=sc_height // 2 - 100,
            color=(0, 0, 0, 180)
        )

        arcade.draw_text(
            "БЫТЬ ФЕРМЕРОМ ЛЕГКО?",
            sc_width // 2,
            sc_height // 2 + 40,
            arcade.color.GOLD,
            36,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        for p in self.particles:
            arcade.draw_circle_filled(p['x'], p['y'], p['size'], p['color'])

        arcade.draw_text(
            "Фермерский симулятор",
            sc_width // 2,
            sc_height // 2,
            arcade.color.WHITE,
            20,
            anchor_x="center",
            anchor_y="center"
        )

        if self.show_press_text:
            arcade.draw_text(
                "Нажмите любую клавишу",
                sc_width // 2,
                sc_height // 2 - 60,
                arcade.color.WHITE,
                18,
                anchor_x="center",
                anchor_y="center"
            )

        arcade.draw_text(
            "Нажмите ЛКМ чтобы начать",
            sc_width // 2,
            30,
            arcade.color.LIGHT_GRAY,
            14,
            anchor_x="center"
        )

    def on_update(self, delta_time):
        self.elapsed_time += delta_time

        if int(self.elapsed_time) % 2 == 0:
            self.show_press_text = True
        else:
            self.show_press_text = False

        for p in self.particles:
            p['x'] += math.cos(p['angle']) * p['speed']
            p['y'] += math.sin(p['angle']) * p['speed']
            
            if p['x'] < 0: p['x'] = sc_width
            if p['x'] > sc_width: p['x'] = 0
            if p['y'] < 0: p['y'] = sc_height
            if p['y'] > sc_height: p['y'] = 0

    def on_key_press(self, symbol, modifiers):
        self._start_game()

    def on_mouse_press(self, x, y, button, modifiers):
        self._start_game()

    def on_show_view(self):
        if self.bgm and not self.bgm_player:
            self.bgm_player = self.bgm.play(loop=True)

    def _start_game(self):
        if self.bgm_player:
            arcade.stop_sound(self.bgm_player)
            self.bgm_player = None
            
        from game_view import GameView
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)


class WinView(arcade.View):
    def __init__(self, final_money):
        super().__init__()
        self.final_money = final_money
        self.bgm = None
        self.bgm_player = None
        try:
             if os.path.exists("assets/music/sound.mp3"):
                 self.bgm = arcade.load_sound("assets/music/sound.mp3")
        except Exception:
             pass
             
        # Added particles for Win Screen
        self.particles = []
        for _ in range(50):
            self.particles.append({
                'x': random.uniform(0, sc_width),
                'y': random.uniform(sc_height, sc_height + 200),
                'speed_y': random.uniform(2, 5),
                'speed_x': random.uniform(-1, 1),
                'color': random.choice([arcade.color.RED, arcade.color.GREEN, arcade.color.BLUE, arcade.color.GOLD, arcade.color.PURPLE]),
                'size': random.uniform(3, 6)
            })

    def on_show_view(self):
        if self.bgm:
            self.bgm_player = self.bgm.play(loop=True)

    def on_draw(self):
        self.clear()
        
        # Background
        arcade.draw_rect_filled(arcade.XYWH(sc_width//2, sc_height//2, sc_width, sc_height), (20, 60, 20))
        
        # Confetti
        for p in self.particles:
             arcade.draw_rect_filled(arcade.XYWH(p['x'], p['y'], p['size'], p['size']), p['color'])
        
        arcade.draw_text(
            "ПОЗДРАВЛЯЮ!",
            sc_width // 2,
            sc_height // 2 + 100,
            arcade.color.GOLD,
            48,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
        
        arcade.draw_text(
            "ВЫ СТАЛИ БОГАТЫМ ФЕРМЕРОМ!",
            sc_width // 2,
            sc_height // 2 + 20,
            arcade.color.WHITE,
            24,
            anchor_x="center",
            anchor_y="center"
        )
        
        arcade.draw_text(
            f"Ваш капитал: {int(self.final_money)} монет",
            sc_width // 2,
            sc_height // 2 - 40,
            arcade.color.WHEAT,
            20,
            anchor_x="center",
            anchor_y="center"
        )
        
        arcade.draw_text(
            "Нажмите любую клавишу, чтобы вернуться в меню",
            sc_width // 2,
            sc_height // 2 - 120,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center",
            anchor_y="center"
        )

    def on_update(self, delta_time):
        for p in self.particles:
             p['y'] -= p['speed_y']
             p['x'] += math.sin(arcade.get_window().time * 2 + p['y']) * 0.5
             
             if p['y'] < -10:
                  p['y'] = sc_height + random.uniform(0, 100)
                  p['x'] = random.uniform(0, sc_width)

    def on_key_press(self, symbol, modifiers):
        self._back_to_menu()

    def on_mouse_press(self, x, y, button, modifiers):
        self._back_to_menu()

    def _back_to_menu(self):
        if self.bgm_player:
            arcade.stop_sound(self.bgm_player)
        
        import db_manager
        db_manager.delete_save() # Reset progress after win
        
        from menu_view import StartView
        start_view = StartView()
        self.window.show_view(start_view)
