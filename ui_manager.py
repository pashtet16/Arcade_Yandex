
import arcade
from constants import *

class UIManager:
    def __init__(self, window):
        self.window = window
        self.active_window = None
        self.selected_field = None
        
    def show_field_upgrade(self, field):
        self.active_window = "field_upgrade"
        self.selected_field = field

    def close_window(self):
        self.active_window = None
        self.selected_field = None

    def draw(self):
        if self.active_window == "field_upgrade" and self.selected_field:
            # Darken background
            arcade.draw_rect_filled(arcade.XYWH(self.window.width/2, self.window.height/2, 
                                         self.window.width, self.window.height), (0, 0, 0, 180))
            
            cx, cy = self.window.width/2, self.window.height/2
            w, h = 800, 550 # Slightly taller to fit info
            
            # Main panel background
            arcade.draw_rect_filled(arcade.XYWH(cx, cy, w, h), (40, 30, 20))
            arcade.draw_rect_outline(arcade.XYWH(cx, cy, w, h), arcade.color.WHEAT, 4)
            
            # Header
            crop_name = {"wheat": "ПШЕНИЦА", "carrot": "МОРКОВЬ", "cauliflower": "КАПУСТА"}.get(self.selected_field.crop_type, "ПОЛЕ")
            arcade.draw_text(f"УПРАВЛЕНИЕ: {crop_name}", cx, cy + h/2 - 40, 
                             arcade.color.WHEAT, 24, anchor_x="center", bold=True)
            
            # Close button
            close_btn_x = cx + w/2 - 25
            close_btn_y = cy + h/2 - 25
            arcade.draw_rect_filled(arcade.XYWH(close_btn_x, close_btn_y, 30, 30), arcade.color.DARK_RED)
            arcade.draw_rect_outline(arcade.XYWH(close_btn_x, close_btn_y, 30, 30), arcade.color.RED, 2)
            arcade.draw_text("X", close_btn_x, close_btn_y, arcade.color.WHITE, 16, anchor_x="center", anchor_y="center", bold=True)

            # Workers columns
            workers = self.selected_field.workers
            if len(workers) >= 2:
                # Left Worker
                self.draw_worker_col(workers[0], cx - 200, cy)
                # Separator
                arcade.draw_line(cx, cy - h/2 + 20, cx, cy + h/2 - 80, arcade.color.WHEAT, 2)
                # Right Worker
                self.draw_worker_col(workers[1], cx + 200, cy)
            else:
                arcade.draw_text("Нет рабочих на поле.", cx, cy, arcade.color.WHITE, 20, anchor_x="center")

    def draw_worker_col(self, worker, x, y):
        # Title
        title = "САЖАТЕЛЬ" if worker.worker_type == "planter" else "СБОРЩИК"
        arcade.draw_text(title, x, y + 180, arcade.color.GOLD, 20, anchor_x="center", bold=True)
        
        # Level & Status Section
        arcade.draw_text(f"Уровень: {worker.level}", x, y + 150, arcade.color.WHITE, 16, anchor_x="center")
        
        status_text = "СПИТ" if worker.is_sleeping else "РАБОТАЕТ"
        status_color = arcade.color.RED if worker.is_sleeping else arcade.color.GREEN
        arcade.draw_text(f"Статус: {status_text}", x, y + 125, status_color, 14, anchor_x="center", bold=True)

        # Stamina Bar
        bar_w = 200
        bar_h = 16
        bar_y = y + 100
        
        # Background bar
        arcade.draw_rect_filled(arcade.XYWH(x, bar_y, bar_w, bar_h), arcade.color.DARK_GRAY)
        arcade.draw_rect_outline(arcade.XYWH(x, bar_y, bar_w, bar_h), arcade.color.WHITE, 1)
        
        # Fill
        fill_pct = max(0, min(1, worker.stamina / worker.max_stamina))
        fill_w = bar_w * fill_pct
        
        fill_color = arcade.color.YELLOW
        if fill_pct < 0.3: fill_color = arcade.color.RED
        elif fill_pct > 0.7: fill_color = arcade.color.GREEN
            
        if fill_w > 0:
            # Align left relative to center x
            # Center of bar is x. Left edge is x - bar_w/2.
            # Center of fill rect needs to be calculated.
            fill_center_x = (x - bar_w/2) + fill_w/2
            arcade.draw_rect_filled(arcade.XYWH(fill_center_x, bar_y, fill_w, bar_h), fill_color)
            
        # Text on bar
        arcade.draw_text(f"{int(worker.stamina)} / {worker.max_stamina}", x, bar_y, arcade.color.BLACK, 10, anchor_x="center", anchor_y="center", bold=True)
        arcade.draw_text("Выносливость", x, bar_y + 15, arcade.color.LIGHT_GRAY, 10, anchor_x="center")

        # Upgrades Section
        stats = [
            ("Скор. ходьбы", worker.walk_speed, 20 * worker.level, "walk_speed"),
            ("Скор. работы", worker.action_speed, 30 * worker.level, "action_speed"),
            ("Вместимость", worker.qty, 40 * worker.level, "qty"),
            ("Макс. сил", worker.max_stamina, 25 * worker.level, "max_stamina")
        ]
        
        start_y = y + 50
        row_h = 50
        
        for i, (name, val, cost, stat_key) in enumerate(stats):
            row_y = start_y - i * row_h
            
            # Stat name and value
            val_fmt = f"{val:.1f}" if isinstance(val, float) else f"{val}"
            arcade.draw_text(f"{name}", x - 90, row_y + 10, arcade.color.LIGHT_BLUE, 12, anchor_x="left")
            arcade.draw_text(val_fmt, x - 90, row_y - 8, arcade.color.WHITE, 14, anchor_x="left", bold=True)
            
            # Upgrade Button
            btn_x = x + 60
            btn_y = row_y + 10
            btn_w = 100
            btn_h = 30
            
            arcade.draw_rect_filled(arcade.XYWH(btn_x, btn_y, btn_w, btn_h), (60, 100, 60))
            arcade.draw_rect_outline(arcade.XYWH(btn_x, btn_y, btn_w, btn_h), arcade.color.GREEN, 1)
            arcade.draw_text(f"Улучш: ${cost}", btn_x, btn_y, arcade.color.WHITE, 12, anchor_x="center", anchor_y="center", bold=True)

    def draw_worker_hud(self, worker):
        """Рисует мини-инфо панель в левом нижнем углу при наведении"""
        if not worker: return
        
        # Размеры и позиция панели
        panel_w = 250
        panel_h = 80
        padding = 10
        x = panel_w / 2 + padding
        y = panel_h / 2 + padding
        
        # Фон панели
        arcade.draw_rect_filled(arcade.XYWH(x, y, panel_w, panel_h), (30, 30, 40, 200)) # Полупрозрачный фон
        arcade.draw_rect_outline(arcade.XYWH(x, y, panel_w, panel_h), arcade.color.WHEAT, 2)
        
        # Аватарка (используем текстуру работника)
        avatar_x = x - panel_w/2 + 40
        avatar_y = y
        arcade.draw_texture_rect(worker.texture, arcade.XYWH(avatar_x, avatar_y, 48, 48), alpha=255)
        # Рамка для аватарки
        arcade.draw_rect_outline(arcade.XYWH(avatar_x, avatar_y, 50, 50), worker.color, 2)
        
        # Текстовая информация
        text_start_x = x - panel_w/2 + 80
        
        role_name = "Сажатель" if worker.worker_type == "planter" else "Сборщик"
        arcade.draw_text(f"{role_name} (Ур. {worker.level})", text_start_x, y + 15, arcade.color.GOLD, 14, bold=True)
        
        if worker.is_sleeping:
            arcade.draw_text(f"Статус: СПИТ", text_start_x, y - 5, arcade.color.RED, 12)
            arcade.draw_text(f"Осталось: {worker.sleep_timer:.1f} сек", text_start_x, y - 25, arcade.color.WHITE, 12)
        else:
            arcade.draw_text(f"Статус: РАБОТАЕТ", text_start_x, y - 5, arcade.color.GREEN, 12)
            arcade.draw_text(f"Действий: {int(worker.stamina)}/{worker.max_stamina}", text_start_x, y - 25, arcade.color.WHITE, 12)


    def on_mouse_press(self, x, y):
        if self.active_window == "field_upgrade":
            cx, cy = self.window.width/2, self.window.height/2
            w, h = 800, 550
            
            # Close button logic
            close_btn_x = cx + w/2 - 25
            close_btn_y = cy + h/2 - 25
            if abs(x - close_btn_x) < 15 and abs(y - close_btn_y) < 15:
                self.close_window()
                return "handled"
                
            workers = self.selected_field.workers
            if len(workers) >= 2:
                # Check left col
                res = self.check_col_clicks(workers[0], x, y, cx - 200, cy)
                if res: return res
                
                # Check right col
                res = self.check_col_clicks(workers[1], x, y, cx + 200, cy)
                if res: return res
                
            return "handled" # Consume click if window is open
        return None

    def check_col_clicks(self, worker, mouse_x, mouse_y, col_x, col_y):
        start_y = col_y + 50
        row_h = 50
        
        stats_keys = ["walk_speed", "action_speed", "qty", "max_stamina"]
        costs_base = [20, 30, 40, 25]

        for i in range(4):
            btn_x = col_x + 60
            row_y = start_y - i * row_h
            
            # Button dim: 100x30
            if abs(mouse_x - btn_x) < 50 and abs(mouse_y - row_y) < 15:
                cost = costs_base[i] * worker.level
                return ("upgrade_stat", worker, stats_keys[i], cost)
        return None
