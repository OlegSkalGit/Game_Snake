"""
Game Configuration and Constants for 3D Snake.
Supports 18 detailed themed levels with 3x apple quotas, procedural textures,
AI enemies, dynamic zoom, lives system, and tail severance mechanics.
"""
from ursina import color, Vec3

# Screen & Window Settings
WINDOW_TITLE = "3D Snake Adventure"
WINDOW_SIZE = (1280, 720)
WINDOW_BORDERLESS = False
SHOW_FPS = True

# Snake Physics & Movement Settings
DEFAULT_SPEED = 9.2
BOOST_SPEED = 16.8
TURN_SPEED = 145.0  # degrees per second
MAX_TILT_ANGLE = 22.0  # banking angle on turns
TILT_LERP_SPEED = 8.0

SEGMENT_DISTANCE = 0.55  # distance between body segments
HEAD_RADIUS = 0.55
SEGMENT_RADIUS = 0.48
TAIL_MIN_SCALE = 0.55  # tail scale factor at end

BOOST_MAX_ENERGY = 100.0
BOOST_DRAIN_RATE = 35.0  # energy per second while boosting
BOOST_RECHARGE_RATE = 20.0  # energy per second while not boosting

# Camera & Zoom Settings (Grand, wider field of view)
DEFAULT_CAMERA_FOV = 52
DEFAULT_ZOOM_LEVEL = 1.65
MIN_ZOOM_LEVEL = 0.65
MAX_ZOOM_LEVEL = 3.20
CAMERA_CHASE_DIST = 24.0
CAMERA_CHASE_HEIGHT = 17.0
CAMERA_TOPDOWN_HEIGHT = 50.0

# Power-up Durations & Lives
DEFAULT_LIVES = 3
MAX_LIVES = 5
RESPAWN_IMMUNITY_DURATION = 2.5
DURATION_SPEED_BOOST = 10.0      # +25% speed for 10 seconds
SPEED_BOOST_FACTOR = 1.25
DURATION_SLOW_MOTION = 10.0      # -25% speed for 10 seconds
SLOW_MOTION_FACTOR = 0.75
DURATION_MAGNET = 10.0           # Magnet for 10 seconds
DURATION_SHIELD = 12.0           # Shield protection
MAGNET_RADIUS = 11.0           # Balanced magnetic vacuum field (half of previous 22.0m)

# Audio Volume Settings
AUDIO_MASTER_VOLUME = 1.0        # Full Ursina master headroom (default was 0.5)
AUDIO_MUSIC_VOLUME = 0.95         # Loud, clear, prominent background music
AUDIO_SFX_VOLUME = 0.65           # Balanced sound effects volume

# Enemy Settings
ENEMY_DEFAULT_SPEED = 7.4
ENEMY_TURN_SPEED = 125.0
ENEMY_DETECTION_DIST = 14.5

# 18 Detailed Levels Configuration (Grand 18-Level Campaign with 3x Apple Quotas)
LEVELS_DATA = [
    # 1. Emerald Forest (90 apples)
    {
        "id": 1,
        "name": "Смарагдовий Ліс (Emerald Forest)",
        "subtitle": "3D ялинки, мухомори, мохові скелі та лісові галявини",
        "arena_size": (44, 44),
        "target_apples": 90,
        "base_speed": 8.5,
        "bg_color": color.rgb32(14, 26, 20),
        "ground_color": color.rgb32(255, 255, 255),
        "ground_texture": "textures/ground_forest.png",
        "grid_color": color.rgb32(40, 138, 58),
        "wall_color": color.rgb32(95, 65, 38),
        "ambient_light": color.rgb32(165, 180, 165),
        "enemy_count": 1,
        "theme": "forest"
    },
    # 2. Golden Desert (126 apples)
    {
        "id": 2,
        "name": "Золота Пустеля (Golden Desert)",
        "subtitle": "Піщані піраміди, 3D кактуси та давні обеліски",
        "arena_size": (46, 46),
        "target_apples": 126,
        "base_speed": 9.0,
        "bg_color": color.rgb32(45, 30, 16),
        "ground_color": color.rgb32(255, 255, 255),
        "ground_texture": "textures/ground_desert.png",
        "grid_color": color.rgb32(230, 180, 95),
        "wall_color": color.rgb32(150, 105, 55),
        "ambient_light": color.rgb32(200, 185, 150),
        "enemy_count": 1,
        "theme": "desert"
    },
    # 3. Abyssal Ocean (162 apples)
    {
        "id": 3,
        "name": "Підводний Океан (Abyssal Ocean)",
        "subtitle": "Коралові рифи, водорості та затонулі скарби",
        "arena_size": (48, 48),
        "target_apples": 162,
        "base_speed": 9.5,
        "bg_color": color.rgb32(8, 22, 38),
        "ground_color": color.rgb32(255, 255, 255),
        "ground_texture": "textures/ground_ocean.png",
        "grid_color": color.rgb32(28, 85, 115),
        "wall_color": color.rgb32(20, 120, 140),
        "ambient_light": color.rgb32(130, 175, 200),
        "enemy_count": 2,
        "theme": "ocean"
    },
    # 4. Deep Space (198 apples)
    {
        "id": 4,
        "name": "Глибокий Космос (Deep Space)",
        "subtitle": "Астероїдні пояси, орбітальні супутники та енергетичні кільця",
        "arena_size": (50, 50),
        "target_apples": 198,
        "base_speed": 10.0,
        "bg_color": color.rgb32(6, 6, 18),
        "ground_color": color.rgb32(255, 255, 255),
        "ground_texture": "textures/ground_space.png",
        "grid_color": color.rgb32(75, 45, 140),
        "wall_color": color.rgb32(130, 70, 220),
        "ambient_light": color.rgb32(150, 140, 190),
        "enemy_count": 2,
        "theme": "space"
    },
    # 5. Cyber Factory (225 apples)
    {
        "id": 5,
        "name": "Кібер-Фабрика (Cyber Factory)",
        "subtitle": "Парові труби, попереджувальні смуги та токсичні чани",
        "arena_size": (52, 52),
        "target_apples": 225,
        "base_speed": 10.5,
        "bg_color": color.rgb32(22, 20, 22),
        "ground_color": color.rgb32(255, 255, 255),
        "ground_texture": "textures/ground_factory.png",
        "grid_color": color.rgb32(220, 140, 20),
        "wall_color": color.rgb32(180, 50, 30),
        "ambient_light": color.rgb32(180, 160, 140),
        "enemy_count": 2,
        "theme": "factory"
    },
    # 6. Neon Metropolis (252 apples)
    {
        "id": 6,
        "name": "Неоновий Мегаполіс (Neon Metropolis)",
        "subtitle": "Хмарочоси з вікнами, що світяться, ліхтарі та лазерні брами",
        "arena_size": (54, 54),
        "target_apples": 252,
        "base_speed": 11.0,
        "bg_color": color.rgb32(12, 10, 28),
        "ground_color": color.rgb32(255, 255, 255),
        "ground_texture": "textures/ground_city.png",
        "grid_color": color.rgb32(0, 220, 255),
        "wall_color": color.rgb32(255, 0, 128),
        "ambient_light": color.rgb32(170, 160, 210),
        "enemy_count": 3,
        "theme": "city"
    },
    # 7. Frozen Tundra (270 apples)
    {
        "id": 7,
        "name": "Крижана Арктика (Frozen Tundra)",
        "subtitle": "Кришталеві айсберги, 3D сніговики та льодовикові обеліски",
        "arena_size": (54, 54),
        "target_apples": 270,
        "base_speed": 11.5,
        "bg_color": color.rgb32(15, 30, 45),
        "ground_color": color.rgb32(255, 255, 255),
        "ground_texture": "textures/ground_arctic.png",
        "grid_color": color.rgb32(120, 190, 230),
        "wall_color": color.rgb32(70, 140, 190),
        "ambient_light": color.rgb32(210, 230, 255),
        "enemy_count": 3,
        "theme": "arctic"
    },
    # 8. Lava Inferno (288 apples)
    {
        "id": 8,
        "name": "Пекельна Лава (Lava Inferno)",
        "subtitle": "Вулканічні жерла, колони магми та обсидіанові вежі",
        "arena_size": (56, 56),
        "target_apples": 288,
        "base_speed": 12.0,
        "bg_color": color.rgb32(35, 10, 8),
        "ground_color": color.rgb32(255, 255, 255),
        "ground_texture": "textures/ground_lava.png",
        "grid_color": color.rgb32(255, 70, 20),
        "wall_color": color.rgb32(160, 30, 15),
        "ambient_light": color.rgb32(210, 130, 90),
        "enemy_count": 3,
        "theme": "lava"
    },
    # 9. Crystal Caverns (315 apples)
    {
        "id": 9,
        "name": "Кришталеві Печери (Crystal Caverns)",
        "subtitle": "Сяючі аметистові друзи, кварцові сталагміти та кристали",
        "arena_size": (56, 56),
        "target_apples": 315,
        "base_speed": 12.5,
        "bg_color": color.rgb32(18, 8, 30),
        "ground_color": color.rgb32(255, 255, 255),
        "ground_texture": "textures/ground_crystal.png",
        "grid_color": color.rgb32(190, 60, 255),
        "wall_color": color.rgb32(140, 30, 200),
        "ambient_light": color.rgb32(180, 140, 220),
        "enemy_count": 3,
        "theme": "crystal"
    },
    # 10. Lost Jungle (342 apples)
    {
        "id": 10,
        "name": "Загублені Джунглі (Lost Jungle)",
        "subtitle": "Стародавні храми Майя, пальми та кам'яні тотеми",
        "arena_size": (58, 58),
        "target_apples": 342,
        "base_speed": 13.0,
        "bg_color": color.rgb32(10, 28, 14),
        "ground_color": color.rgb32(255, 255, 255),
        "ground_texture": "textures/ground_jungle.png",
        "grid_color": color.rgb32(60, 160, 80),
        "wall_color": color.rgb32(110, 80, 45),
        "ambient_light": color.rgb32(170, 200, 160),
        "enemy_count": 4,
        "theme": "jungle"
    },
    # 11. Sky Sanctuary (360 apples)
    {
        "id": 11,
        "name": "Штормове Святилище (Sky Sanctuary)",
        "subtitle": "Ширяючі платформи, блискавичні пілони та розряди",
        "arena_size": (60, 60),
        "target_apples": 360,
        "base_speed": 13.4,
        "bg_color": color.rgb32(20, 35, 60),
        "ground_color": color.rgb32(255, 255, 255),
        "ground_texture": "textures/ground_sky.png",
        "grid_color": color.rgb32(240, 240, 100),
        "wall_color": color.rgb32(90, 130, 200),
        "ambient_light": color.rgb32(200, 215, 245),
        "enemy_count": 4,
        "theme": "sky"
    },
    # 12. Toxic Wasteland (378 apples) - NEW
    {
        "id": 12,
        "name": "Радіоактивна Зона (Toxic Wasteland)",
        "subtitle": "Бочки з ядерними відходами, кислотні гейзери та біолазери",
        "arena_size": (60, 60),
        "target_apples": 378,
        "base_speed": 13.8,
        "bg_color": color.rgb32(16, 25, 12),
        "ground_color": color.rgb32(255, 255, 255),
        "ground_texture": "textures/ground_toxic.png",
        "grid_color": color.rgb32(80, 255, 50),
        "wall_color": color.rgb32(140, 160, 30),
        "ambient_light": color.rgb32(170, 220, 140),
        "enemy_count": 4,
        "theme": "toxic"
    },
    # 13. Mystic Swamp (396 apples) - NEW
    {
        "id": 13,
        "name": "Містичне Болото (Mystic Swamp)",
        "subtitle": "Порослі мохом корчі, отруйні спори та блукаючі вогні",
        "arena_size": (62, 62),
        "target_apples": 396,
        "base_speed": 14.0,
        "bg_color": color.rgb32(18, 22, 16),
        "ground_color": color.rgb32(255, 255, 255),
        "ground_texture": "textures/ground_swamp.png",
        "grid_color": color.rgb32(120, 160, 60),
        "wall_color": color.rgb32(75, 95, 45),
        "ambient_light": color.rgb32(150, 180, 140),
        "enemy_count": 4,
        "theme": "swamp"
    },
    # 14. Ancient Necropolis (414 apples) - NEW
    {
        "id": 14,
        "name": "Давній Некрополь (Ancient Necropolis)",
        "subtitle": "Гробниці фараонів, кам'яні саркофаги та піщані пастки",
        "arena_size": (62, 62),
        "target_apples": 414,
        "base_speed": 14.3,
        "bg_color": color.rgb32(32, 24, 15),
        "ground_color": color.rgb32(255, 255, 255),
        "ground_texture": "textures/ground_necropolis.png",
        "grid_color": color.rgb32(220, 170, 70),
        "wall_color": color.rgb32(140, 95, 40),
        "ambient_light": color.rgb32(190, 170, 130),
        "enemy_count": 4,
        "theme": "necropolis"
    },
    # 15. Steampunk Sky-Islands (432 apples) - NEW
    {
        "id": 15,
        "name": "Острови Стімпанку (Steampunk Sky)",
        "subtitle": "Мідні парові котли, масивні шестерні та мідні труби",
        "arena_size": (64, 64),
        "target_apples": 432,
        "base_speed": 14.6,
        "bg_color": color.rgb32(35, 25, 18),
        "ground_color": color.rgb32(255, 255, 255),
        "ground_texture": "textures/ground_steampunk.png",
        "grid_color": color.rgb32(230, 160, 50),
        "wall_color": color.rgb32(170, 90, 35),
        "ambient_light": color.rgb32(200, 170, 130),
        "enemy_count": 5,
        "theme": "steampunk"
    },
    # 16. Event Horizon (450 apples) - NEW
    {
        "id": 16,
        "name": "Горизонт Подій (Event Horizon)",
        "subtitle": "Акреційний диск чорної діри, квантова гравітація та плазма",
        "arena_size": (64, 64),
        "target_apples": 450,
        "base_speed": 14.9,
        "bg_color": color.rgb32(4, 4, 10),
        "ground_color": color.rgb32(255, 255, 255),
        "ground_texture": "textures/ground_event_horizon.png",
        "grid_color": color.rgb32(255, 100, 30),
        "wall_color": color.rgb32(160, 40, 220),
        "ambient_light": color.rgb32(170, 120, 220),
        "enemy_count": 5,
        "theme": "event_horizon"
    },
    # 17. Dragon's Dungeon (468 apples) - NEW
    {
        "id": 17,
        "name": "Підземелля Дракона (Dragon Dungeon)",
        "subtitle": "Готичні колонади, палаючі жаровні та кам'яні пастки",
        "arena_size": (66, 66),
        "target_apples": 468,
        "base_speed": 15.2,
        "bg_color": color.rgb32(20, 12, 14),
        "ground_color": color.rgb32(255, 255, 255),
        "ground_texture": "textures/ground_dungeon.png",
        "grid_color": color.rgb32(220, 50, 40),
        "wall_color": color.rgb32(110, 30, 25),
        "ambient_light": color.rgb32(190, 120, 110),
        "enemy_count": 5,
        "theme": "dungeon"
    },
    # 18. Quantum Citadel Boss (495 apples)
    {
        "id": 18,
        "name": "Квантова Цитадель (Quantum Citadel — FINAL BOSS)",
        "subtitle": "ВЕЛИКИЙ ФІНАЛ: Квантові ядра, гіпер-лазери та 5 бос-дронів!",
        "arena_size": (68, 68),
        "target_apples": 495,
        "base_speed": 15.5,
        "bg_color": color.rgb32(5, 5, 12),
        "ground_color": color.rgb32(255, 255, 255),
        "ground_texture": "textures/ground_quantum.png",
        "grid_color": color.rgb32(255, 0, 128),
        "wall_color": color.rgb32(0, 240, 255),
        "ambient_light": color.rgb32(190, 170, 220),
        "enemy_count": 5,
        "theme": "quantum"
    }
]

# Color Palettes
COLOR_SNAKE_HEAD = color.rgb32(50, 220, 110)
COLOR_SNAKE_BODY_1 = color.rgb32(40, 190, 95)
COLOR_SNAKE_BODY_2 = color.rgb32(30, 160, 80)
COLOR_SNAKE_EYES = color.rgb32(255, 255, 255)
COLOR_SNAKE_PUPILS = color.rgb32(15, 15, 15)
COLOR_SNAKE_TONGUE = color.rgb32(240, 60, 80)

COLOR_ENEMY_HEAD = color.rgb32(220, 45, 45)
COLOR_ENEMY_BODY_1 = color.rgb32(180, 30, 30)
COLOR_ENEMY_BODY_2 = color.rgb32(130, 20, 20)
COLOR_ENEMY_EYES = color.rgb32(255, 220, 50)
COLOR_ENEMY_PUPILS = color.rgb32(20, 0, 0)

COLOR_APPLE_NORMAL = color.rgb32(235, 45, 45)
COLOR_APPLE_GOLDEN = color.rgb32(255, 215, 0)
COLOR_POWERUP_SPEED = color.rgb32(255, 140, 20)
COLOR_POWERUP_SLOW = color.rgb32(0, 220, 255)
COLOR_POWERUP_MAGNET = color.rgb32(170, 45, 245)
COLOR_POWERUP_SHIELD = color.rgb32(0, 180, 255)
COLOR_POWERUP_LIFE = color.rgb32(255, 45, 85)
COLOR_POWERUP_MEGA_FOOD = color.rgb32(255, 210, 40)

# Camera Modes
CAMERA_MODE_CHASE = 0
CAMERA_MODE_TOPDOWN = 1
CAMERA_MODE_FIRSTPERSON = 2
