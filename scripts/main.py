"""
Main Game Controller for 3D Snake Adventure.
Controls 18 Worlds, 5 Sublevels per World (90 total stages), 18 unique background music tracks,
game loop, smooth camera controls, HUD updates, collision resolution, and power-up states.
"""
import os
import sys
import math
import random
from pathlib import Path
from ursina import Ursina, window, camera, Vec3, color, application, time, held_keys, mouse, clamp

# Configure paths and sys.path so modules and root assets resolve correctly
SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parent

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Initialize Engine
app = Ursina(
    title="3D Snake Adventure",
    borderless=False,
    fullscreen=False,
    size=(1280, 720),
    vsync=True
)

# High-Precision Depth Buffer: prevents Z-fighting flickering / shimmering across the arena
camera.clip_plane_near = 0.5
camera.clip_plane_far = 350.0

# Patch Ursina engine to recursively clean up child entities and procedural Pipe construction helpers
def _apply_engine_optimizations():
    try:
        if 'ursina.destroy' in sys.modules:
            ud_mod = sys.modules['ursina.destroy']
            orig_destroy = ud_mod._destroy
            def safe_destroy(entity, force_destroy=False):
                if hasattr(entity, 'children'):
                    for child in list(entity.children):
                        safe_destroy(child, force_destroy=force_destroy)
                orig_destroy(entity, force_destroy=force_destroy)
            ud_mod._destroy = safe_destroy
    except Exception as ex:
        print(f"Warning: could not patch ursina destroy: {ex}")

    try:
        import ursina.models.procedural.pipe as pipe_mod
        orig_pipe_gen = pipe_mod.Pipe.generate
        def patched_pipe_gen(self):
            orig_pipe_gen(self)
            if hasattr(self, 'prev') and self.prev:
                from ursina import destroy
                destroy(self.prev)
                self.prev = None
            if hasattr(self, 'curr') and self.curr:
                from ursina import destroy
                destroy(self.curr)
                self.curr = None
        pipe_mod.Pipe.generate = patched_pipe_gen
    except Exception as ex:
        print(f"Warning: could not patch pipe generate: {ex}")

_apply_engine_optimizations()

# Direct Ursina asset folder to project root (so textures/ and sounds/ load directly)
application.asset_folder = PROJECT_ROOT

import config
from textures_gen import ensure_textures_exist
from audio_manager import AudioManager
from snake import Snake
from items import ItemManager
from enemies import EnemyManager
from level_manager import LevelManager
from ui import GameUI
from save_manager import load_save_data, save_game_data

class GameController:
    def __init__(self):
        # Ensure HD textures & sounds exist
        ensure_textures_exist()
        self.audio = AudioManager()
        self.level_mgr = LevelManager()
        self.item_mgr = ItemManager()
        self.enemy_mgr = EnemyManager()
        
        # Load persistent save data
        save = load_save_data()
        self.unlocked_world = save.get("unlocked_world", 0)
        self.highscore = save.get("high_score", 0)
        self.completed_worlds = save.get("completed_worlds", [])

        # State
        self.state = "MENU"  # MENU, PLAYING, PAUSED, LEVEL_CLEAR, GAME_OVER, VICTORY
        self.current_level = min(0, self.unlocked_world) # World index (0 to 17)
        self.current_sublevel = 0   # Sublevel stage (0 to 4)
        self.score = 0
        self.apples_collected = 0
        self.lives = config.DEFAULT_LIVES
        
        # Gameplay entities
        self.snake = None
        self.shield_immunity_timer = 0.0
        
        # Camera
        self.camera_mode = config.CAMERA_MODE_CHASE
        self.zoom_level = config.DEFAULT_ZOOM_LEVEL
        self.camera_yaw = 0.0
        
        # UI Callbacks
        callbacks = {
            "start_game": self.start_game,
            "select_level": self.select_level,
            "resume_game": self.resume_game,
            "open_help": self.open_help,
            "close_help": self.close_help,
            "restart_level": self.restart_level,
            "next_level": self.next_level,
            "goto_menu": self.goto_menu,
            "exit_game": self.exit_game
        }
        self.ui = GameUI(callbacks)
        self.goto_menu()

    # ---------------- STATE TRANSITIONS ----------------
    def goto_menu(self):
        self.state = "MENU"
        self.ui.show_screen("MENU")
        self.ui.update_menu_levels(self.unlocked_world)
        self.cleanup_gameplay()
        self.level_mgr.build_level(self.current_level, self.current_sublevel)
        self.audio.play_level_bgm(self.level_mgr.current_level_data["theme"])
        camera.position = Vec3(0, 38, -42)
        camera.rotation = (44, 0, 0)

    def select_level(self, lvl_idx):
        if lvl_idx <= self.unlocked_world:
            self.current_level = lvl_idx
            self.current_sublevel = 0
            self.start_game()
        else:
            self.ui.notify_locked_world(lvl_idx)
            self.audio.play_hit()

    def start_game(self):
        self.state = "PLAYING"
        self.apples_collected = 0
        self.lives = config.DEFAULT_LIVES
        self.cleanup_gameplay()

        # Build World & Sublevel
        self.level_mgr.build_level(self.current_level, self.current_sublevel)
        lvl_data = self.level_mgr.current_level_data
        self.item_mgr.set_arena_size(lvl_data["arena_size"])

        # Switch to this level's unique music track
        self.audio.play_level_bgm(lvl_data["theme"])

        # Spawn Snake with sublevel speed
        sub_speed = self.level_mgr.get_sublevel_speed()
        self.snake = Snake(start_pos=Vec3(0, 0.45, 0), start_rot_y=0.0)
        self.snake.base_speed = sub_speed
        self.snake.speed = sub_speed

        # Spawn Initial Items (5 diverse fruits)
        self.item_mgr.clear()
        for _ in range(5):
            self.item_mgr.spawn_food(self.level_mgr.obstacles, self.snake)

        # Spawn AI Enemies scaled by sublevel
        self.enemy_mgr.clear()
        enemy_count = self.level_mgr.get_sublevel_enemy_count()
        for _ in range(enemy_count):
            self.enemy_mgr.spawn_enemy(lvl_data["arena_size"], self.level_mgr.obstacles, self.snake)

        # 2.0s spawn immunity grace period
        self.shield_immunity_timer = 2.0

        # Camera setup
        self.reset_camera_instant()

        self.ui.show_screen("HUD")
        self.audio.play_click()

    def cleanup_gameplay(self):
        if self.snake:
            self.snake.destroy_entities()
            self.snake = None
        self.item_mgr.clear()
        self.enemy_mgr.clear()
        self.shield_immunity_timer = 0.0

    def pause_game(self):
        if self.state == "PLAYING":
            self.state = "PAUSED"
            self.ui.show_screen("PAUSE")
            self.audio.play_click()

    def resume_game(self):
        if self.state == "PAUSED":
            self.state = "PLAYING"
            self.ui.show_screen("HUD")
            self.audio.play_click()

    def open_help(self):
        self.ui.show_screen("HELP")
        self.audio.play_click()

    def close_help(self):
        if self.state == "PLAYING":
            self.ui.show_screen("HUD")
        elif self.state == "PAUSED":
            self.ui.show_screen("PAUSE")
        else:
            self.ui.show_screen("MENU")
        self.audio.play_click()

    def restart_level(self):
        self.start_game()

    def next_level(self):
        """Advances to next sublevel, or next world (saving unlocked progress), or victory."""
        if self.current_sublevel < 4:
            self.current_sublevel += 1
            self.start_game()
        else:
            # Completed World!
            if self.current_level not in self.completed_worlds:
                self.completed_worlds.append(self.current_level)
            if self.current_level + 1 > self.unlocked_world and self.current_level < len(config.LEVELS_DATA) - 1:
                self.unlocked_world = self.current_level + 1
            # Save progression immediately
            save_game_data(self.unlocked_world, max(self.score, self.highscore), self.completed_worlds)
            
            if self.current_level < len(config.LEVELS_DATA) - 1:
                self.current_level += 1
                self.current_sublevel = 0
                self.start_game()
            else:
                self.state = "VICTORY"
                self.ui.show_victory(self.score)
                self.audio.play_levelup()

    def exit_game(self):
        application.quit()
        sys.exit(0)

    # ---------------- CAMERA CONTROLLER ----------------
    def toggle_camera(self):
        self.camera_mode = (self.camera_mode + 1) % 3
        self.audio.play_click()

    def adjust_zoom(self, delta):
        self.zoom_level = max(config.MIN_ZOOM_LEVEL, min(config.MAX_ZOOM_LEVEL, self.zoom_level + delta))

    def reset_camera_instant(self):
        if not self.snake:
            return
        if self.camera_mode == config.CAMERA_MODE_CHASE:
            rad = math.radians(self.snake.head.rotation_y)
            dist = config.CAMERA_CHASE_DIST * self.zoom_level
            height = config.CAMERA_CHASE_HEIGHT * self.zoom_level
            cam_back = Vec3(-math.sin(rad), 0, -math.cos(rad)) * dist
            camera.position = self.snake.head.position + cam_back + Vec3(0, height, 0)
            
            look_target = self.snake.head.position + Vec3(0, 0.6, 0)
            to_target = look_target - camera.position
            horiz_dist = math.sqrt(to_target.x**2 + to_target.z**2)
            yaw = math.degrees(math.atan2(to_target.x, to_target.z))
            pitch = math.degrees(math.atan2(-to_target.y, horiz_dist))
            camera.rotation = (pitch, yaw, 0.0)
        elif self.camera_mode == config.CAMERA_MODE_TOPDOWN:
            top_h = config.CAMERA_TOPDOWN_HEIGHT * self.zoom_level
            top_z = -16.0 * self.zoom_level
            camera.position = Vec3(self.snake.head.x * 0.25, top_h, self.snake.head.z * 0.25 + top_z)
            camera.rotation = (68, 0, 0)
        elif self.camera_mode == config.CAMERA_MODE_FIRSTPERSON:
            camera.position = self.snake.head.position + Vec3(0, 0.45, 0)
            camera.rotation_y = self.snake.head.rotation_y
            camera.rotation_x = 5.0
            camera.rotation_z = 0.0

    def update_camera(self, dt):
        if not self.snake or not self.snake.is_alive:
            return

        if self.camera_mode == config.CAMERA_MODE_CHASE:
            # Smooth position follow behind snake
            rad = math.radians(self.snake.head.rotation_y)
            dist = config.CAMERA_CHASE_DIST * self.zoom_level
            height = config.CAMERA_CHASE_HEIGHT * self.zoom_level
            cam_back = Vec3(-math.sin(rad), 0, -math.cos(rad)) * dist
            target_pos = self.snake.head.position + cam_back + Vec3(0, height, 0)
            
            # Smoothly glide camera position
            camera.position = lerp(camera.position, target_pos, min(1.0, dt * 6.5))

            # Dynamically look directly from current camera position to snake head
            look_target = self.snake.head.position + Vec3(0, 0.6, 0)
            to_target = look_target - camera.position
            horiz_dist = math.sqrt(to_target.x**2 + to_target.z**2)
            
            if horiz_dist > 0.01:
                yaw = math.degrees(math.atan2(to_target.x, to_target.z))
                pitch = math.degrees(math.atan2(-to_target.y, horiz_dist))
                camera.rotation_x = pitch
                camera.rotation_y = yaw
                camera.rotation_z = 0.0  # Zero roll keeps horizon perfectly level and calm

        elif self.camera_mode == config.CAMERA_MODE_TOPDOWN:
            top_h = config.CAMERA_TOPDOWN_HEIGHT * self.zoom_level
            top_z = -16.0 * self.zoom_level
            target_pos = Vec3(self.snake.head.x * 0.25, top_h, self.snake.head.z * 0.25 + top_z)
            camera.position = lerp(camera.position, target_pos, dt * 5.0)
            camera.rotation = (68, 0, 0)

        elif self.camera_mode == config.CAMERA_MODE_FIRSTPERSON:
            camera.position = self.snake.head.position + Vec3(0, 0.45, 0)
            camera.rotation_y = self.snake.head.rotation_y
            camera.rotation_x = 5.0
            camera.rotation_z = 0.0

    # ---------------- GAME LOOP UPDATE ----------------
    def update(self):
        dt = time.dt
        if dt > 0.1:
            dt = 0.1

        if self.state == "MENU":
            self.level_mgr.update_dynamic_hazards(dt)
            self.camera_yaw = (self.camera_yaw + dt * 7.5) % 360.0
            rad = math.radians(self.camera_yaw)
            camera.position = Vec3(-math.sin(rad) * 42.0, 36.0, -math.cos(rad) * 42.0)
            camera.rotation = (41.0, self.camera_yaw, 0.0)
            return

        if self.state != "PLAYING":
            return

        # 1. Update Immunity Timer & Full Snake Blinking Effect
        if self.shield_immunity_timer > 0:
            self.shield_immunity_timer -= dt
            # Fast rhythmic arcade blinking for head and all body segments (12 Hz)
            is_visible = int(self.shield_immunity_timer * 12) % 2 == 0
            self.snake.set_visible(is_visible)
        else:
            self.snake.set_visible(True)

        # 2. Player Input Handling (Keyboard: A/D, Left/Right arrows, Space/Shift to boost)
        turn_input = 0.0
        if held_keys['a'] or held_keys['left arrow']:
            turn_input -= 1.0
        if held_keys['d'] or held_keys['right arrow']:
            turn_input += 1.0

        boost_requested = held_keys['space'] or held_keys['shift']

        # 3. Update Snake Physics & Movement
        self.snake.update_movement(turn_input, boost_requested, dt)

        # 4. Update Dynamic Level Hazards
        self.level_mgr.update_dynamic_hazards(dt)

        # 5. Update AI Enemies
        lvl_data = self.level_mgr.current_level_data
        self.enemy_mgr.update(
            dt=dt,
            arena_size=lvl_data["arena_size"],
            obstacles=self.level_mgr.obstacles,
            items=self.item_mgr.items,
            player_snake=self.snake
        )
        self.enemy_mgr.check_enemy_obstacle_collisions(
            obstacles=self.level_mgr.obstacles,
            arena_size=lvl_data["arena_size"],
            item_mgr=self.item_mgr,
            audio_mgr=self.audio
        )

        # Enemy vs Player Collision Resolution (Support biting enemy tails!)
        collision = self.enemy_mgr.check_player_collision(self.snake)
        if collision:
            c_type = collision["type"]
            c_enemy = collision["enemy"]
            c_idx = collision["segment_idx"]

            # --- CASE A: Player bites enemy's body or tail! ---
            if c_type == "bite_enemy":
                if c_enemy.shield_timer > 0:
                    c_enemy.shield_timer = 0.0
                    c_enemy.shield_aura.visible = False
                    self.item_mgr.add_burst(c_enemy.head.position, config.COLOR_POWERUP_SHIELD, count=12)
                    self.audio.play_hit()
                    self.ui.notify_bonus("🛡️ ЩИТ ВОРОГА ЗНИЩЕНО ВАШИМ УКУСОМ!")
                    self.shield_immunity_timer = 0.6
                else:
                    # If bitten at base/neck (segment 0 or 1) or enemy has <= 3 segments total: kill enemy!
                    if c_idx <= 1 or len(c_enemy.segments) <= 3:
                        self.enemy_mgr.kill_enemy(c_enemy, self.item_mgr, self.audio)
                        pts = 100
                        self.score += pts
                        self.ui.notify_bonus(f"💥 ВОРОЖУ ЗМІЙКУ ПОВНІСТЮ ЗНИЩЕНО! (+{pts} очок)")
                        self.shield_immunity_timer = 0.6
                    else:
                        # Sever the enemy's tail from c_idx!
                        severed_positions = c_enemy.cut_tail(c_idx)
                        if severed_positions:
                            num_cut = len(severed_positions)
                            pts = num_cut * 15
                            self.score += pts
                            self.audio.play_tail_cut()
                            self.item_mgr.spawn_severed_tail_loot(severed_positions)
                            self.item_mgr.add_burst(severed_positions[0], config.COLOR_ENEMY_BODY_1, count=10)
                            self.ui.notify_tail_cut(num_cut, is_enemy=True)
                            self.ui.notify_bonus(f"✂️ ВІДКУШЕНО ХВІСТ ВОРОГА! (-{num_cut} сегм., +{pts} очок)")
                            # Frightened enemy flees in panic with speed boost
                            c_enemy.speed_timer = 2.0
                            self.shield_immunity_timer = 0.6

            # --- CASE B: Direct Head-on collision ---
            elif c_type == "head_on":
                if self.snake.shield_timer > 0 or self.shield_immunity_timer > 0:
                    self.break_shield()
                    self.enemy_mgr.kill_enemy(c_enemy, self.item_mgr, self.audio)
                    self.score += 50
                    self.ui.notify_bonus("🛡️ Ворожу змійку розтрощено щитом! (+50 очок)")
                elif c_enemy.shield_timer > 0:
                    c_enemy.shield_timer = 0.0
                    c_enemy.shield_aura.visible = False
                    self.handle_player_hit("Лобове зіткнення з захищеним ворогом!")
                    return
                else:
                    self.handle_player_hit("Лобове зіткнення з ворожою змійкою!")
                    return

            # --- CASE C: Enemy head bites player's body/tail ---
            elif c_type == "enemy_bite_player":
                if self.snake.shield_timer > 0 or self.shield_immunity_timer > 0:
                    self.break_shield()
                    self.enemy_mgr.kill_enemy(c_enemy, self.item_mgr, self.audio)
                    self.score += 40
                    self.ui.notify_bonus("🛡️ Щит захистив ваш хвіст і знищив ворога!")
                elif self.shield_immunity_timer <= 0:
                    # If player has enough segments and bitten on tail: cut player tail instead of killing!
                    if len(self.snake.segments) > 4 and c_idx >= 3:
                        severed_positions = self.snake.cut_tail(c_idx)
                        if severed_positions:
                            self.audio.play_tail_cut()
                            self.item_mgr.spawn_severed_tail_loot(severed_positions)
                            self.ui.notify_tail_cut(len(severed_positions), is_enemy=False)
                            self.shield_immunity_timer = 1.4
                    else:
                        self.handle_player_hit("Ворожа змійка смертельно вкусила вас за шию!")
                        return

        # 6. Update Items & Powerups (Player and AI enemies eating)
        events = self.item_mgr.update(dt, self.level_mgr.obstacles, self.snake, self.audio, enemies=self.enemy_mgr.enemies)
        for ev in events:
            if isinstance(ev, dict):
                ev_type = ev.get("type", "apple")
                pts = ev.get("points", 10)
                quota = ev.get("quota", 1)
                name = ev.get("name", "Їжа")

                self.score += pts
                if quota > 0:
                    self.apples_collected += quota

                if ev_type == "apple":
                    pass
                elif ev_type == "golden":
                    self.shield_immunity_timer = 2.0
                    self.ui.notify_bonus(f"⭐ ЗОЛОТЕ ЯБЛУКО! (+{pts} очок, +{quota} їжі)")
                elif ev_type == "mega_food":
                    self.shield_immunity_timer = 2.5
                    self.ui.notify_bonus(f"🍉 ВЕЛЕТЕНСЬКИЙ КАВУН! (+{quota} ЇЖІ, +{pts} очок) + ІМУНІТЕТ!")
                elif ev_type == "life":
                    if self.lives < config.MAX_LIVES:
                        self.lives += 1
                        self.shield_immunity_timer = 2.5
                        self.ui.notify_bonus(f"❤️ +1 ЖИТТЯ! (Залишилося: {self.lives}/{config.MAX_LIVES}) + ІМУНІТЕТ!")
                    else:
                        self.score += 200
                        self.shield_immunity_timer = 2.5
                        self.ui.notify_bonus(f"❤️ МАКСИМУМ ЖИТТІВ ({config.MAX_LIVES}/{config.MAX_LIVES})! (+200 очок) + ІМУНІТЕТ!")
                elif ev_type == "speed":
                    self.shield_immunity_timer = 2.0
                    self.ui.notify_bonus("⚡ ТУРБО-РЕЖИМ (+25% на 10 с) + ІМУНІТЕТ!")
                elif ev_type == "slow":
                    self.shield_immunity_timer = 2.0
                    self.ui.notify_bonus("❄️ СПОВІЛЬНЕННЯ (-25% на 10 с) + ІМУНІТЕТ!")
                elif ev_type == "magnet":
                    self.shield_immunity_timer = 2.0
                    self.ui.notify_bonus("🧲 МАГНІТ ДЛЯ ЇЖІ (10 с) + ІМУНІТЕТ!")
                elif ev_type == "shield":
                    self.shield_immunity_timer = 2.0
                    self.ui.notify_bonus("🛡️ ЗАХИСНИЙ ЩИТ (12 с) + ІМУНІТЕТ!")
                else:
                    fruit_icons = {
                        "pear": "🍐",
                        "banana": "🍌",
                        "strawberry": "🍓",
                        "orange": "🍊",
                        "watermelon": "🍉",
                        "cherries": "🍒",
                        "pineapple": "🍍",
                        "starfruit": "⭐"
                    }
                    ic = fruit_icons.get(ev_type, "🍎")
                    self.ui.notify_bonus(f"{ic} {name.upper()}! (+{pts} очок, +{quota} їжі)")
            elif ev == "apple":
                self.score += 10
                self.apples_collected += 1
            elif ev == "golden":
                self.score += 50
                self.apples_collected += 2
                self.ui.notify_bonus("⭐ ЗОЛОТЕ ЯБЛУКО! (+50 очок, +2 яблука)")
            elif ev == "mega_food":
                self.score += 100
                self.apples_collected += 10
                self.ui.notify_bonus("🍉 ВЕЛЕТЕНСЬКИЙ КАВУН! (+10 ЇЖІ, +100 очок)")
            elif ev == "life":
                self.shield_immunity_timer = 2.5
                if self.lives < config.MAX_LIVES:
                    self.lives += 1
                    self.ui.notify_bonus(f"❤️ +1 ЖИТТЯ! (Залишилося: {self.lives}/{config.MAX_LIVES}) + ІМУНІТЕТ!")
                else:
                    self.score += 200
                    self.ui.notify_bonus(f"❤️ МАКСИМУМ ЖИТТІВ ({config.MAX_LIVES}/{config.MAX_LIVES})! (+200 очок) + ІМУНІТЕТ!")
            elif ev == "speed":
                self.score += 25
                self.shield_immunity_timer = 2.0
                self.ui.notify_bonus("⚡ ТУРБО-РЕЖИМ (+25% на 10 с) + ІМУНІТЕТ!")
            elif ev == "slow":
                self.score += 25
                self.shield_immunity_timer = 2.0
                self.ui.notify_bonus("❄️ СПОВІЛЬНЕННЯ (-25% на 10 с) + ІМУНІТЕТ!")
            elif ev == "magnet":
                self.score += 25
                self.shield_immunity_timer = 2.0
                self.ui.notify_bonus("🧲 МАГНІТ ДЛЯ ЇЖІ (10 с) + ІМУНІТЕТ!")
            elif ev == "shield":
                self.score += 25
                self.shield_immunity_timer = 2.0
                self.ui.notify_bonus("🛡️ ЗАХИСНИЙ ЩИТ (12 с) + ІМУНІТЕТ!")

        if self.score > self.highscore:
            self.highscore = self.score

        # 7. Check Collisions (Self, Wall, Obstacles)
        target_apples = self.level_mgr.get_sublevel_target_apples()

        # Check self collision (Biting own tail: cuts tail at hit location, drops bonus apples, game continues!)
        if self.shield_immunity_timer <= 0:
            collided_self, hit_idx = self.snake.check_self_collision()
            if collided_self:
                severed_positions = self.snake.cut_tail(hit_idx)
                if severed_positions:
                    self.audio.play_tail_cut()
                    self.item_mgr.spawn_severed_tail_loot(severed_positions)
                    self.ui.notify_tail_cut(len(severed_positions))
                    self.shield_immunity_timer = 1.0

        # Check wall collision
        if self.level_mgr.check_wall_collision(self.snake):
            if self.snake.shield_timer > 0 and self.shield_immunity_timer <= 0:
                self.break_shield()
            elif self.shield_immunity_timer <= 0:
                self.handle_player_hit("Зіткнення з огорожею арени!")
                return

        # Check obstacle collision
        if self.level_mgr.check_obstacle_collision(self.snake):
            if self.snake.shield_timer > 0 and self.shield_immunity_timer <= 0:
                self.break_shield()
            elif self.shield_immunity_timer <= 0:
                self.handle_player_hit("Зіткнення з перешкодою!")
                return

        # 8. Check Sublevel / World Completion
        if self.apples_collected >= target_apples:
            self.trigger_level_clear()
            return

        # 9. Update Camera
        self.update_camera(dt)

        # 10. Update HUD
        self.ui.update_hud(
            score=self.score,
            highscore=self.highscore,
            level_idx=self.current_level,
            sublevel_idx=self.current_sublevel,
            apples_collected=self.apples_collected,
            target_apples=target_apples,
            boost_energy=self.snake.boost_energy,
            snake=self.snake,
            camera_mode=self.camera_mode,
            enemies_count=len(self.enemy_mgr.enemies),
            lives=self.lives
        )

    def break_shield(self):
        """Consumes shield upon impact, preventing instant death."""
        self.snake.shield_timer = 0.0
        self.shield_immunity_timer = max(self.shield_immunity_timer, 1.2)
        self.item_mgr.add_burst(self.snake.head.position, config.COLOR_POWERUP_SHIELD, count=12)
        self.audio.play_hit()

    def handle_player_hit(self, reason):
        """Deducts 1 life and respawns snake safely, or triggers Game Over if out of lives."""
        self.lives -= 1
        self.audio.play_hit()
        self.item_mgr.add_burst(self.snake.head.position, config.COLOR_SNAKE_HEAD, count=14)

        if self.lives > 0:
            self.ui.notify_life_lost(self.lives)
            self.respawn_snake_safe()
        else:
            self.trigger_game_over(reason)

    def respawn_snake_safe(self):
        """Safely respawns snake in arena center with temporary invulnerability."""
        if not self.snake:
            return
        self.snake.head.position = Vec3(0, 0.45, 0)
        self.snake.head.rotation = (0, 0, 0)
        self.snake.current_turn = 0.0
        self.snake.last_pos = Vec3(0, 0.45, 0)
        self.snake.trail.clear()
        self.snake.total_distance = 0.0

        for d in range(80):
            dist_back = d * 0.1
            self.snake.trail.append((Vec3(0, 0.45, -dist_back), 0.0, 0.0, -dist_back))
        self.snake.trail.reverse()

        for i, seg in enumerate(self.snake.segments):
            target_d = self.snake.total_distance - (i + 1) * config.SEGMENT_DISTANCE
            pos, r_y, r_z = self.snake.sample_trail(target_d)
            seg.position = pos
            seg.rotation_y = r_y
            seg.rotation_z = 0.0

        self.shield_immunity_timer = config.RESPAWN_IMMUNITY_DURATION
        self.reset_camera_instant()

    def trigger_game_over(self, reason):
        self.state = "GAME_OVER"
        self.snake.is_alive = False
        self.item_mgr.add_burst(self.snake.head.position, config.COLOR_SNAKE_HEAD, count=14)
        self.audio.play_hit()
        if self.score > self.highscore:
            self.highscore = self.score
        save_game_data(self.unlocked_world, self.highscore, self.completed_worlds)
        self.ui.show_game_over(reason, self.score)

    def trigger_level_clear(self):
        self.state = "LEVEL_CLEAR"
        self.audio.play_levelup()
        self.ui.show_level_clear(self.score, self.current_level, self.current_sublevel)

    def handle_input(self, key):
        if key in ['c', 'c up']:
            if self.state == "PLAYING":
                self.toggle_camera()
        elif key in ['scroll up', '+', '=', 'page up']:
            self.adjust_zoom(-0.15)
        elif key in ['scroll down', '-', '_', 'page down']:
            self.adjust_zoom(0.15)
        elif key in ['h', 'f1']:
            if self.ui.help_root.enabled:
                self.close_help()
            else:
                self.open_help()
        elif key in ['escape', 'p']:
            if self.ui.help_root.enabled:
                self.close_help()
            elif self.state == "PLAYING":
                self.pause_game()
            elif self.state == "PAUSED":
                self.resume_game()
        elif key in ['m', 'm up']:
            is_on = self.audio.toggle_music()
            msg = "🎵 Музика: УВІМКНЕНО" if is_on else "🔇 Музика: ВИМКНЕНО"
            self.ui.notify_bonus(msg)
        elif key == 'r':
            if self.state in ["PLAYING", "GAME_OVER"]:
                self.restart_level()


# Global Game Instance
game_controller = GameController()

def update():
    game_controller.update()

def input(key):
    game_controller.handle_input(key)

if __name__ == '__main__':
    app.run()
