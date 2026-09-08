"""
User Interface (UI), HUD, and Encyclopedia / Help System for 3D Snake.
Contains HUD, Main Menu (18 levels selector in 3 rows), Pause Menu,
Help / Guide Modal (18 Biomes info), Level Clear, Game Over, and Victory screens.
"""
from ursina import Entity, Text, Button, color, camera, Vec2, destroy
import config

class GameUI:
    def __init__(self, callbacks=None):
        self.callbacks = callbacks or {}
        self.cb = lambda name: self.callbacks.get(name, lambda *args: None)

        # Roots
        self.hud_root = Entity(parent=camera.ui, enabled=False)
        self.menu_root = Entity(parent=camera.ui, enabled=True)
        self.pause_root = Entity(parent=camera.ui, enabled=False)
        self.help_root = Entity(parent=camera.ui, enabled=False)
        self.level_clear_root = Entity(parent=camera.ui, enabled=False)
        self.game_over_root = Entity(parent=camera.ui, enabled=False)
        self.victory_root = Entity(parent=camera.ui, enabled=False)
        
        self.current_help_tab = 0
        self.previous_screen = "MENU"

        self.build_hud()
        self.build_main_menu()
        self.build_pause_menu()
        self.build_help_screen()
        self.build_level_clear_overlay()
        self.build_game_over_overlay()
        self.build_victory_overlay()

    # ---------------- HUD ----------------
    def build_hud(self):
        # Top Header Bar
        self.header_bg = Entity(
            parent=self.hud_root,
            model='quad',
            color=color.rgba32(10, 15, 25, 220),
            scale=(1.8, 0.12),
            position=(0, 0.44, 0.01)
        )
        
        # Level Title
        self.txt_level_name = Text(
            parent=self.hud_root,
            text="Рівень 1/18: Смарагдовий Ліс",
            position=(-0.82, 0.47, -0.01),
            scale=1.18,
            color=color.rgb32(255, 220, 100)
        )
        
        # Score & Highscore
        self.txt_score = Text(
            parent=self.hud_root,
            text="Рахунок: 0",
            position=(0.32, 0.47, -0.01),
            scale=1.25,
            color=color.rgb32(100, 255, 160)
        )
        self.txt_highscore = Text(
            parent=self.hud_root,
            text="Рекорд: 0",
            position=(0.58, 0.47, -0.01),
            scale=1.0,
            color=color.rgb32(200, 200, 200)
        )
        
        # Level Progress & Enemies Counter
        self.txt_progress = Text(
            parent=self.hud_root,
            text="Ціль: 0 / 30 яблук",
            position=(-0.82, 0.41, -0.01),
            scale=1.05,
            color=color.rgb32(240, 240, 240)
        )
        self.txt_enemies_count = Text(
            parent=self.hud_root,
            text="Вороги: 1",
            position=(-0.52, 0.41, -0.01),
            scale=1.05,
            color=color.rgb32(255, 100, 100)
        )
        
        # Dedicated Lives Widget (Top Center Box)
        self.lives_card = Entity(
            parent=self.hud_root,
            model='quad',
            color=color.rgba32(25, 12, 18, 235),
            scale=(0.44, 0.075),
            position=(-0.02, 0.44, 0.005)
        )
        self.lives_card_border = Entity(
            parent=self.lives_card,
            model='quad',
            color=color.rgba32(255, 70, 90, 120),
            scale=(1.02, 1.08),
            position=(0, 0, 0.002)
        )

        self.txt_lives = Text(
            parent=self.hud_root,
            text=f"ЖИТТЯ: 3 / {config.MAX_LIVES}",
            position=(-0.22, 0.458, -0.015),
            scale=1.35,
            color=color.rgb32(255, 60, 80)
        )

        # Graphical Life Badges (Up to MAX_LIVES)
        self.life_badges = []
        for i in range(config.MAX_LIVES):
            bx = 0.01 + i * 0.038
            b_border = Entity(
                parent=self.hud_root,
                model='quad',
                color=color.rgb32(255, 200, 100),
                scale=(0.026, 0.026),
                position=(bx, 0.44, -0.008),
                rotation=(0, 0, 45)
            )
            b_fill = Entity(
                parent=self.hud_root,
                model='quad',
                color=color.rgb32(255, 45, 65),
                scale=(0.020, 0.020),
                position=(bx, 0.44, -0.012),
                rotation=(0, 0, 45)
            )
            self.life_badges.append((b_border, b_fill))

        # Temporary Life Lost Notification Banner & Backdrop
        self.life_lost_card = Entity(
            parent=self.hud_root,
            model='quad',
            color=color.rgba32(40, 10, 15, 235),
            scale=(0.85, 0.12),
            position=(0, 0.20, 0.005),
            enabled=False
        )
        self.life_lost_banner = Text(
            parent=self.hud_root,
            text="",
            position=(-0.36, 0.21, -0.02),
            scale=1.8,
            color=color.rgb32(255, 80, 80),
            enabled=False
        )
        self.banner_timer = 0.0

        # Tail Cut Notification Banner
        self.tail_cut_banner = Text(
            parent=self.hud_root,
            text="",
            position=(-0.32, 0.10, -0.02),
            scale=1.5,
            color=color.rgb32(255, 160, 40),
            enabled=False
        )
        self.tail_cut_timer = 0.0

        # Progress Bar BG & Fill
        self.prog_bar_bg = Entity(
            parent=self.hud_root,
            model='quad',
            color=color.rgba32(40, 40, 60, 200),
            scale=(0.20, 0.022),
            position=(-0.56, 0.41, 0.005)
        )
        self.prog_bar_fill = Entity(
            parent=self.hud_root,
            model='quad',
            color=color.rgb32(50, 220, 100),
            scale=(0.01, 0.018),
            position=(-0.66, 0.41, -0.005),
            origin=(-0.5, 0)
        )
        
        # Camera Mode Display
        self.txt_camera_mode = Text(
            parent=self.hud_root,
            text="[C] Камера: 3-тя особа",
            position=(0.42, 0.41, -0.01),
            scale=0.95,
            color=color.rgb32(180, 220, 255)
        )

        # Active Power-up Badges (Speed, Slow, Magnet, Shield)
        self.powerup_container = Entity(parent=self.hud_root, position=(-0.82, 0.34, -0.01))
        self.badge_speed = Text(parent=self.powerup_container, text="[SPEED] ТУРБО (+25%): 10s", position=(0, 0), scale=1.05, color=config.COLOR_POWERUP_SPEED, enabled=False)
        self.badge_slow = Text(parent=self.powerup_container, text="[SLOW] СПОВІЛЬНЕННЯ (-25%): 10s", position=(0, -0.045), scale=1.05, color=config.COLOR_POWERUP_SLOW, enabled=False)
        self.badge_magnet = Text(parent=self.powerup_container, text="[MAGNET] МАГНІТ (10s): 10s", position=(0, -0.090), scale=1.05, color=config.COLOR_POWERUP_MAGNET, enabled=False)
        self.badge_shield = Text(parent=self.powerup_container, text="[SHIELD] ЗАХИСНИЙ ЩИТ: 12s", position=(0, -0.135), scale=1.05, color=config.COLOR_POWERUP_SHIELD, enabled=False)

        # Boost Energy Gauge at Bottom Center
        self.boost_bg = Entity(parent=self.hud_root, model='quad', color=color.rgba32(20, 20, 30, 200), scale=(0.42, 0.026), position=(0, -0.42, 0.005))
        self.boost_fill = Entity(parent=self.hud_root, model='quad', color=color.rgb32(0, 220, 255), scale=(0.41, 0.020), position=(-0.205, -0.42, -0.005), origin=(-0.5, 0))
        self.txt_boost_label = Text(parent=self.hud_root, text="ПРИСКОРЕННЯ [SPACE / SHIFT]", position=(-0.16, -0.38, -0.01), scale=0.85, color=color.rgb32(180, 240, 255))

        # Controls Hint Footer
        self.footer_hint = Text(
            parent=self.hud_root,
            text="[A]/[D] Поворот  |  [SPACE] Турбо  |  [C] Камера  |  Коліщатко / [+][-] Зум  |  [M] Музика  |  [H] Довідка  |  [ESC] Пауза  |  [R] Рестарт",
            position=(-0.66, -0.47, -0.01),
            scale=0.82,
            color=color.rgb32(180, 180, 190)
        )

    # ---------------- MAIN MENU (18 LEVELS SELECTOR) ----------------
    def build_main_menu(self):
        self.menu_card = Entity(
            parent=self.menu_root,
            model='quad',
            color=color.rgba32(14, 20, 32, 240),
            scale=(1.36, 0.98),
            position=(0, 0, 0.01)
        )
        
        self.menu_title = Text(
            parent=self.menu_root,
            text=">>> 3D ЗМІЙКА: ВЕЛИКА КАМПАНІЯ <<<",
            position=(-0.42, 0.42, -0.02),
            scale=2.3,
            color=color.rgb32(80, 240, 140)
        )
        self.menu_sub = Text(
            parent=self.menu_root,
            text="18 Епічних Світів • Текстури • 3x Яблук • Відкушування хвоста • AI Вороги",
            position=(-0.44, 0.35, -0.02),
            scale=1.05,
            color=color.rgb32(200, 220, 240)
        )
        
        # Play Button
        self.btn_play = Button(
            parent=self.menu_root,
            text="ПОЧАТИ ГРУ",
            color=color.rgb32(40, 180, 80),
            highlight_color=color.rgb32(60, 210, 100),
            scale=(0.34, 0.070),
            position=(-0.18, 0.25, -0.02),
            on_click=self.cb("start_game")
        )
        # Help Button
        self.btn_menu_help = Button(
            parent=self.menu_root,
            text="ДОВІДКА [H]",
            color=color.rgb32(45, 120, 200),
            highlight_color=color.rgb32(65, 150, 230),
            scale=(0.24, 0.070),
            position=(0.18, 0.25, -0.02),
            on_click=self.cb("open_help")
        )
        
        # Level Select Grid (18 levels in 3 rows of 6)
        self.txt_select_lvl = Text(
            parent=self.menu_root,
            text="Оберіть рівень для старту (1 .. 18):",
            position=(-0.24, 0.16, -0.02),
            scale=1.05,
            color=color.rgb32(240, 220, 130)
        )
        
        self.level_buttons = []
        for i in range(18):
            row = i // 6
            col = i % 6
            x_offset = -0.4875 + col * 0.195
            y_offset = 0.09 - row * 0.062
            btn = Button(
                parent=self.menu_root,
                text=f"Світ {i+1}",
                text_size=0.60,
                color=color.rgb32(40, 140, 180),
                highlight_color=color.rgb32(65, 180, 240),
                scale=(0.182, 0.052),
                position=(x_offset, y_offset, -0.02),
                on_click=lambda l=i: self.cb("select_level")(l)
            )
            self.level_buttons.append(btn)

        # Overview Description
        self.instructions_txt = Text(
            parent=self.menu_root,
            text="Кампанія: 18 Світів • Новий світ відкривається після проходження 5 етапів попереднього!\n"
                 "• Прогрес автоматично зберігається • [A]/[D] Поворот • [SPACE] Турбо • [C] Камера\n"
                 "• Коліщатко Зум • [M] Музика • [H] Довідка • [ESC] Пауза • [R] Рестарт етапу",
            position=(-0.54, -0.16, -0.02),
            scale=0.90,
            color=color.rgb32(210, 220, 230)
        )

        # Exit Button
        self.btn_exit = Button(
            parent=self.menu_root,
            text="ВИХІД З ГРИ",
            color=color.rgb32(180, 50, 50),
            highlight_color=color.rgb32(220, 70, 70),
            scale=(0.26, 0.055),
            position=(0, -0.42, -0.02),
            on_click=self.cb("exit_game")
        )

    # ---------------- PAUSE MENU ----------------
    def build_pause_menu(self):
        self.pause_card = Entity(parent=self.pause_root, model='quad', color=color.rgba32(10, 15, 25, 230), scale=(0.76, 0.65), position=(0, 0, 0.01))
        self.txt_pause_title = Text(parent=self.pause_root, text="ГРУ ПРИЗУПИНЕНО", position=(-0.24, 0.22, -0.02), scale=1.9, color=color.rgb32(255, 220, 100))
        self.btn_resume = Button(parent=self.pause_root, text="ПРОДОВЖИТИ", color=color.rgb32(40, 180, 80), highlight_color=color.rgb32(60, 210, 100), scale=(0.34, 0.068), position=(0, 0.10, -0.02), on_click=self.cb("resume_game"))
        self.btn_help_pause = Button(parent=self.pause_root, text="ДОВІДКА [H]", color=color.rgb32(45, 120, 200), highlight_color=color.rgb32(65, 150, 230), scale=(0.34, 0.068), position=(0, 0.01, -0.02), on_click=self.cb("open_help"))
        self.btn_restart_pause = Button(parent=self.pause_root, text="СПРОБУВАТИ ЗНОВУ [R]", color=color.rgb32(50, 100, 180), highlight_color=color.rgb32(70, 130, 220), scale=(0.34, 0.068), position=(0, -0.08, -0.02), on_click=self.cb("restart_level"))
        self.btn_menu_pause = Button(parent=self.pause_root, text="ГОЛОВНЕ МЕНЮ", color=color.rgb32(180, 60, 60), highlight_color=color.rgb32(220, 80, 80), scale=(0.34, 0.068), position=(0, -0.17, -0.02), on_click=self.cb("goto_menu"))

    # ---------------- INTERACTIVE HELP / ENCYCLOPEDIA ----------------
    def build_help_screen(self):
        self.help_card = Entity(parent=self.help_root, model='quad', color=color.rgba32(12, 18, 30, 245), scale=(1.36, 0.95), position=(0, 0, 0.01))
        self.help_title = Text(parent=self.help_root, text="=== ДОВІДКА ТА КЕРІВНИЦТВО ГРИ ===", position=(-0.36, 0.40, -0.02), scale=2.0, color=color.rgb32(80, 220, 255))

        tab_names = ["1. Механіки & Життя", "2. Їжа та Бонуси", "3. 18 Світів", "4. AI Вороги"]
        self.tab_buttons = []
        for i, name in enumerate(tab_names):
            bx = -0.42 + i * 0.28
            btn = Button(
                parent=self.help_root,
                text=name,
                color=color.rgb32(40, 140, 180) if i == 0 else color.rgb32(35, 50, 75),
                highlight_color=color.rgb32(60, 170, 220),
                scale=(0.26, 0.052),
                position=(bx, 0.31, -0.02),
                on_click=lambda t=i: self.switch_help_tab(t)
            )
            self.tab_buttons.append(btn)

        self.help_content_txt = Text(parent=self.help_root, text="", position=(-0.58, 0.23, -0.02), scale=0.92, color=color.rgb32(230, 240, 250))
        self.render_help_tab_content(0)

        self.btn_close_help = Button(parent=self.help_root, text="НАЗАД [ESC / H]", color=color.rgb32(40, 180, 80), highlight_color=color.rgb32(60, 210, 100), scale=(0.32, 0.065), position=(0, -0.40, -0.02), on_click=self.cb("close_help"))

    def switch_help_tab(self, tab_idx):
        self.current_help_tab = tab_idx
        for i, btn in enumerate(self.tab_buttons):
            btn.color = color.rgb32(40, 140, 180) if i == tab_idx else color.rgb32(35, 50, 75)
        self.render_help_tab_content(tab_idx)

    def render_help_tab_content(self, tab_idx):
        if tab_idx == 0:
            self.help_content_txt.text = (
                "🎮 МЕХАНІКИ, КЕРУВАННЯ ТА ЖИТТЯ:\n\n"
                "• [A] / [D] — Плавні повороти  |  [SPACE] / [SHIFT] — Турбо-прискорення\n"
                "• ✂️ [ВІДКУШУВАННЯ ХВОСТА]: Якщо ви врізаєтесь у власне тіло — гра НЕ припиняється!\n"
                "    Хвіст на місці удару відкушується, розсипаючись на бонусні плоди, а змійка вкорочується.\n"
                "• ❤️ [3 Життя на кожному рівні]: На початку рівня надається 3 життя.\n"
                "    При зіткненні зі стіною змійка відроджується з 2.5с захисного імунітету (яблука зберігаються!).\n"
                "• [C] — Камера (3-тя особа, Зверху, 1-ша особа)  |  Коліщатко — Зум  |  [H] — Довідка  |  [ESC] — Пауза."
            )
        elif tab_idx == 1:
            self.help_content_txt.text = (
                "🍎 РІЗНОМАНІТНІ ФРУКТИ ТА СУПЕРБОНУСИ (ГРАВЕЦЬ І AI ВОРОГИ):\n\n"
                "• 🍎 Яблуко (+10), 🍐 Груша (+15), 🍌 Банан (+20), 🍊 Апельсин (+20)\n"
                "• 🍓 Полуниця (+25, +2 їжі), 🍉 Кавун (+30, +2 їжі), 🍒 Вишні (+35, +2 їжі)\n"
                "• 🍍 Ананас (+45, +3 їжі), ⭐ Зоряний Фрукт (+50, +4 їжі), 👑 Золоте Яблуко (+60, +5 їжі)\n\n"
                "• ⚡ [SPEED] Турбо-Режим (+25% на 10с)  |  ❄️ [SLOW] Сповільнення (-25% на 10с)\n"
                "• 🧲 [MAGNET] Магніт для Їжі (10с)  |  🛡️ [SHIELD] Захисний Щит (12с)\n"
                "• ❤️ [+1 ЖИТТЯ] Серце 1-Up  |  🍉 [+10 ЇЖІ] Велетенський Кавун / Бенкет (+100 очок)\n"
                "⚠️ УВАГА: Ворожі змійки також полюють та поїдають усі фрукти і бонуси на арені!"
            )
        elif tab_idx == 2:
            self.help_content_txt.text = (
                "🌍 18 УНІКАЛЬНИХ 3D СВІТІВ (ВЕЛИКА КАМПАНІЯ З ТЕКСТУРАМИ):\n\n"
                "1. Ліс | 2. Пустеля | 3. Океан | 4. Космос | 5. Фабрика | 6. Мегаполіс\n"
                "7. Арктика | 8. Лава | 9. Кришталеві Печери | 10. Джунглі | 11. Штормове Святилище\n"
                "12. Радіоактивна Зона | 13. Містичне Болото | 14. Давній Некрополь\n"
                "15. Острови Стімпанку | 16. Горизонт Подій | 17. Підземелля Дракона\n"
                "18. Квантова Цитадель (ФІНАЛЬНИЙ БОС-РІВЕНЬ з 5 елітними дронами)!"
            )
        elif tab_idx == 3:
            self.help_content_txt.text = (
                "⚔️ AI ВОРОГИ ТА ТАКТИКА БОРОТЬБИ:\n\n"
                "• На арені полюють ворожі змійки з сенсорною системою 5 далекомірів.\n"
                "• Вороги самостійно збирають їжу та оминають стіни й перешкоди.\n"
                "• [ВІДКУСУВАННЯ ХВОСТА ВОРОГА]:\n"
                "    - Ви можете ВІДКУСУВАТИ ХВІСТ іншим змійкам! Атакуйте ворога у хвіст чи бік:\n"
                "      відкушена частина розсипається на бонусний лут, який можна з'їсти!\n"
                "    - Укус у шию чи коротку змійку ПОВНІСТЮ ЗНИЩУЄ ворога (+100 очок)!\n"
                "• [Лобове зіткнення]:\n"
                "    - Прямий удар лоб-у-лоб без щита завдає шкоди гравцю. Бережіть голову!\n"
                "    - Якщо активний [ЩИТ] — ви трощите ворога при будь-якому зіткненні!"
            )

    # ---------------- LEVEL CLEAR OVERLAY ----------------
    def build_level_clear_overlay(self):
        self.clear_card = Entity(parent=self.level_clear_root, model='quad', color=color.rgba32(12, 28, 20, 235), scale=(0.85, 0.65), position=(0, 0, 0.01))
        self.txt_clear_title = Text(parent=self.level_clear_root, text="* РІВЕНЬ ПРОЙДЕНО! *", position=(-0.28, 0.22, -0.02), scale=2.1, color=color.rgb32(100, 255, 140))
        self.txt_clear_info = Text(parent=self.level_clear_root, text="Чудова робота! Наступний виклик попереду.", position=(-0.26, 0.12, -0.02), scale=1.1, color=color.rgb32(230, 245, 230))
        self.txt_clear_stats = Text(parent=self.level_clear_root, text="Поточний рахунок: 0", position=(-0.16, 0.04, -0.02), scale=1.2, color=color.rgb32(255, 225, 90))
        self.btn_next_level = Button(parent=self.level_clear_root, text="НАСТУПНИЙ РІВЕНЬ", color=color.rgb32(40, 180, 80), highlight_color=color.rgb32(60, 220, 100), scale=(0.36, 0.08), position=(0, -0.08, -0.02), on_click=self.cb("next_level"))
        self.btn_menu_clear = Button(parent=self.level_clear_root, text="ГОЛОВНЕ МЕНЮ", color=color.rgb32(70, 80, 100), highlight_color=color.rgb32(90, 105, 130), scale=(0.28, 0.06), position=(0, -0.19, -0.02), on_click=self.cb("goto_menu"))

    # ---------------- GAME OVER OVERLAY ----------------
    def build_game_over_overlay(self):
        self.over_card = Entity(parent=self.game_over_root, model='quad', color=color.rgba32(30, 12, 15, 240), scale=(0.85, 0.65), position=(0, 0, 0.01))
        self.txt_over_title = Text(parent=self.game_over_root, text="[!] ГРА ЗАКІНЧЕНА", position=(-0.24, 0.22, -0.02), scale=2.2, color=color.rgb32(255, 75, 75))
        self.txt_over_reason = Text(parent=self.game_over_root, text="Зіткнення з перешкодою!", position=(-0.20, 0.12, -0.02), scale=1.15, color=color.rgb32(255, 200, 200))
        self.txt_over_score = Text(parent=self.game_over_root, text="Фінальний рахунок: 0", position=(-0.17, 0.03, -0.02), scale=1.25, color=color.rgb32(255, 220, 90))
        self.btn_retry = Button(parent=self.game_over_root, text="СПРОБУВАТИ ЗНОВУ [R]", color=color.rgb32(200, 60, 60), highlight_color=color.rgb32(240, 80, 80), scale=(0.36, 0.08), position=(0, -0.08, -0.02), on_click=self.cb("restart_level"))
        self.btn_menu_over = Button(parent=self.game_over_root, text="ГОЛОВНЕ МЕНЮ", color=color.rgb32(70, 80, 100), highlight_color=color.rgb32(90, 105, 130), scale=(0.28, 0.06), position=(0, -0.19, -0.02), on_click=self.cb("goto_menu"))

    # ---------------- VICTORY OVERLAY ----------------
    def build_victory_overlay(self):
        self.vic_card = Entity(parent=self.victory_root, model='quad', color=color.rgba32(20, 15, 35, 245), scale=(0.98, 0.78), position=(0, 0, 0.01))
        self.txt_vic_title = Text(parent=self.victory_root, text="*** АБСОЛЮТНА ПЕРЕМОГА! ***", position=(-0.38, 0.28, -0.02), scale=2.3, color=color.rgb32(255, 220, 50))
        self.txt_vic_desc = Text(parent=self.victory_root, text="Вітаємо! Ви успішно подолали ВСІ 18 3D світів великої кампанії!", position=(-0.44, 0.18, -0.02), scale=1.1, color=color.rgb32(220, 240, 255))
        self.txt_vic_score = Text(parent=self.victory_root, text="Загальний рекордний рахунок: 0", position=(-0.25, 0.07, -0.02), scale=1.3, color=color.rgb32(100, 255, 160))
        self.btn_vic_restart = Button(parent=self.victory_root, text="ГРАТИ ЗНОВУ", color=color.rgb32(50, 180, 90), highlight_color=color.rgb32(70, 220, 110), scale=(0.34, 0.08), position=(0, -0.06, -0.02), on_click=lambda: self.cb("select_level")(0))
        self.btn_vic_menu = Button(parent=self.victory_root, text="ГОЛОВНЕ МЕНЮ", color=color.rgb32(70, 80, 100), highlight_color=color.rgb32(90, 105, 130), scale=(0.28, 0.06), position=(0, -0.18, -0.02), on_click=self.cb("goto_menu"))

    # ---------------- HUD UPDATES ----------------
    def update_hud(self, score, highscore, level_idx, sublevel_idx, apples_collected, target_apples, boost_energy, snake, camera_mode, enemies_count=0, lives=3):
        lvl_data = config.LEVELS_DATA[level_idx]
        
        self.txt_level_name.text = f"Світ {level_idx + 1}/18 [Етап {sublevel_idx + 1}/5]: {lvl_data['name']}"
        self.txt_score.text = f"Рахунок: {score}"
        self.txt_highscore.text = f"Рекорд: {highscore}"
        self.txt_progress.text = f"Ціль: {apples_collected} / {target_apples} яблук"
        self.txt_enemies_count.text = f"Вороги: {enemies_count}"

        # Update text lives (clean standard ASCII/Ukrainian)
        self.txt_lives.text = f"ЖИТТЯ: {max(0, lives)} / {config.MAX_LIVES}"
        if lives >= 3:
            self.txt_lives.color = color.rgb32(255, 65, 85)
        elif lives == 2:
            self.txt_lives.color = color.rgb32(255, 185, 45)
        elif lives == 1:
            self.txt_lives.color = color.rgb32(255, 45, 45)
        else:
            self.txt_lives.color = color.rgb32(140, 140, 150)

        # Update graphical diamond badges
        for i, (b_border, b_fill) in enumerate(self.life_badges):
            if i < lives:
                b_border.color = color.rgb32(255, 215, 100)
                b_fill.color = color.rgb32(255, 45, 65)
                b_fill.scale = (0.020, 0.020)
            else:
                b_border.color = color.rgb32(75, 75, 85)
                b_fill.color = color.rgb32(35, 35, 42)
                b_fill.scale = (0.014, 0.014)

        # Life lost notification banner timer
        if self.banner_timer > 0:
            self.banner_timer -= 0.016
            if self.banner_timer <= 0:
                self.life_lost_banner.enabled = False
                self.life_lost_card.enabled = False

        # Tail cut banner timer
        if self.tail_cut_timer > 0:
            self.tail_cut_timer -= 0.016
            if self.tail_cut_timer <= 0:
                self.tail_cut_banner.enabled = False

        # Progress bar fill
        progress = min(1.0, apples_collected / max(1, target_apples))
        self.prog_bar_fill.scale_x = max(0.001, 0.218 * progress)

        # Boost gauge fill
        boost_ratio = max(0.0, min(1.0, boost_energy / config.BOOST_MAX_ENERGY))
        self.boost_fill.scale_x = max(0.001, 0.408 * boost_ratio)
        if boost_ratio < 0.2:
            self.boost_fill.color = color.rgb32(255, 70, 70)
        else:
            self.boost_fill.color = color.rgb32(0, 220, 255)

        # Camera mode text
        cam_names = ["3-тя особа (Chase)", "Зверху (Top-Down)", "1-ша особа (FPS)"]
        self.txt_camera_mode.text = f"[C] {cam_names[camera_mode]}"

        # Power-up badges
        if snake:
            if snake.speed_timer > 0:
                self.badge_speed.enabled = True
                self.badge_speed.text = f"[SPEED] ТУРБО (+25%): {snake.speed_timer:.1f}s"
            else:
                self.badge_speed.enabled = False

            if getattr(snake, 'slow_timer', 0) > 0:
                self.badge_slow.enabled = True
                self.badge_slow.text = f"[SLOW] СПОВІЛЬНЕННЯ (-25%): {snake.slow_timer:.1f}s"
            else:
                self.badge_slow.enabled = False

            if snake.magnet_timer > 0:
                self.badge_magnet.enabled = True
                self.badge_magnet.text = f"[MAGNET] МАГНІТ (10s): {snake.magnet_timer:.1f}s"
            else:
                self.badge_magnet.enabled = False

            if snake.shield_timer > 0:
                self.badge_shield.enabled = True
                self.badge_shield.text = f"[SHIELD] ЗАХИСНИЙ ЩИТ: {snake.shield_timer:.1f}s"
            else:
                self.badge_shield.enabled = False

    def notify_bonus(self, message):
        """Displays short bonus pickup notification."""
        self.tail_cut_banner.text = message
        self.tail_cut_banner.enabled = True
        self.tail_cut_timer = 2.0

    def notify_life_lost(self, remaining_lives):
        """Displays prominent visual banner indicating life deducted and respawn."""
        self.life_lost_banner.text = f"[ ! ] ВТРАЧЕНО 1 ЖИТТЯ (ЗАЛИШИЛОСЯ: {remaining_lives}) [ ! ]"
        self.life_lost_banner.enabled = True
        self.life_lost_card.enabled = True
        self.banner_timer = 2.4

    def notify_tail_cut(self, lost_segments, is_enemy=False):
        """Displays quick notification when tail is severed (player or enemy)."""
        if is_enemy:
            self.tail_cut_banner.text = f"✂️ ВІДКУШЕНО ХВІСТ ВОРОГА! (-{lost_segments} сегм. -> бонусний лут!)"
            self.tail_cut_banner.color = color.rgb32(255, 235, 50)
        else:
            self.tail_cut_banner.text = f"✂️ ВІДКУШЕНО ВЛАСНИЙ ХВІСТ! (-{lost_segments} сегментів -> бонусні яблука)"
            self.tail_cut_banner.color = color.rgb32(255, 175, 45)
        self.tail_cut_banner.enabled = True
        self.tail_cut_timer = 2.4

    def show_screen(self, screen_name):
        if screen_name != "HELP":
            self.previous_screen = screen_name
        self.hud_root.enabled = (screen_name == "HUD")
        self.menu_root.enabled = (screen_name == "MENU")
        self.pause_root.enabled = (screen_name == "PAUSE")
        self.help_root.enabled = (screen_name == "HELP")
        self.level_clear_root.enabled = (screen_name == "LEVEL_CLEAR")
        self.game_over_root.enabled = (screen_name == "GAME_OVER")
        self.victory_root.enabled = (screen_name == "VICTORY")

    def show_game_over(self, reason, final_score):
        self.txt_over_reason.text = reason
        self.txt_over_score.text = f"Фінальний рахунок: {final_score}"
        self.show_screen("GAME_OVER")

    def show_level_clear(self, score, world_idx, sublevel_idx):
        self.txt_clear_stats.text = f"Поточний рахунок: {score}"
        if sublevel_idx < 4:
            self.txt_clear_title.text = f"* ЕТАП {world_idx + 1}-{sublevel_idx + 1} ПРОЙДЕНО! *"
            self.txt_clear_info.text = f"Наступний виклик: Етап {world_idx + 1}-{sublevel_idx + 2} / 5"
            self.btn_next_level.text = "НАСТУПНИЙ ЕТАП"
        else:
            self.txt_clear_title.text = f"*** СВІТ {world_idx + 1} ЦІЛКОВИТО ПРОЙДЕНО! ***"
            if (world_idx + 1) < len(config.LEVELS_DATA):
                next_name = config.LEVELS_DATA[world_idx + 1]["name"]
                self.txt_clear_info.text = f"Наступний світ: {next_name}"
            else:
                self.txt_clear_info.text = "Фінал грандіозної кампанії!"
            self.btn_next_level.text = "НАСТУПНИЙ СВІТ"
        self.show_screen("LEVEL_CLEAR")

    def show_victory(self, final_score):
        self.txt_vic_score.text = f"Загальний рахунок переможця: {final_score}"
        self.show_screen("VICTORY")

    def update_menu_levels(self, unlocked_world):
        """Updates main menu buttons appearance and click handlers based on unlocked world progression."""
        for i, btn in enumerate(self.level_buttons):
            btn.text_size = 0.58
            if i <= unlocked_world:
                if i < unlocked_world:
                    btn.text = f"Світ {i+1} [Пройдено]"
                    btn.color = color.rgb32(28, 115, 80)
                    btn.highlight_color = color.rgb32(40, 155, 110)
                else:
                    btn.text = f"Світ {i+1} [Грати]"
                    btn.color = color.rgb32(35, 135, 210)
                    btn.highlight_color = color.rgb32(55, 175, 255)
                btn.on_click = lambda l=i: self.cb("select_level")(l)
            else:
                btn.text = f"Світ {i+1} [Закрито]"
                btn.color = color.rgb32(38, 42, 50)
                btn.highlight_color = color.rgb32(52, 56, 66)
                btn.on_click = lambda l=i: self.notify_locked_world(l)

    def notify_locked_world(self, world_idx):
        """Displays warning when player clicks a locked world button."""
        self.notify_bonus(f"[ ! ] Світ {world_idx + 1} заблоковано! Спершу пройдіть Світ {world_idx}.")
