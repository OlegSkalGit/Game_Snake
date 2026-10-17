"""
Level Manager and 3D Environment Builder for 3D Snake Adventure.
Constructs 18 rich themed arenas with HD 512x512 procedural textures, multi-light sculptural shading,
atmospheric horizon vistas, animated landmarks, dynamic hazards, and collision resolution.
"""
import math
import random
from ursina import Entity, Vec3, color, destroy, window, scene, DirectionalLight, AmbientLight
from ursina.models.procedural.cylinder import Cylinder
from ursina.models.procedural.cone import Cone
import config


def safe_destroy_entity(entity):
    """Recursively destroys entity and all its children to prevent memory leaks and Z-fighting."""
    if not entity:
        return
    if hasattr(entity, 'children'):
        for child in list(entity.children):
            safe_destroy_entity(child)
    destroy(entity)


class MovingLaserBarrier:
    """Animated laser hazard that glides back and forth with glowing emitters."""
    def __init__(self, start_pos, end_pos, move_speed=2.5, beam_color=None):
        self.start_pos = Vec3(start_pos)
        self.end_pos = Vec3(end_pos)
        self.move_speed = move_speed
        self.time_offset = random.uniform(0.0, math.pi * 2)
        self.collision_radius = 0.85
        self.is_moving_hazard = True
        
        beam_col = beam_color or color.rgb32(255, 40, 60)
        
        self.entity = Entity(
            model='cube',
            color=beam_col,
            scale=(2.6, 0.35, 0.35),
            position=start_pos
        )
        self.emitter_l = Entity(parent=self.entity, model=Cylinder(resolution=12), color=color.rgb32(45, 50, 62), scale=(0.38, 1.45, 0.38), position=(-0.5, 0, 0), rotation=(0, 0, 90))
        self.emitter_r = Entity(parent=self.entity, model=Cylinder(resolution=12), color=color.rgb32(45, 50, 62), scale=(0.38, 1.45, 0.38), position=(0.5, 0, 0), rotation=(0, 0, 90))
        self.core_beam = Entity(parent=self.entity, model='cube', color=color.white, scale=(0.96, 0.42, 0.42))
        self.ring_c = Entity(parent=self.entity, model='cube', color=beam_col, scale=(0.18, 1.65, 1.65), rotation=(45, 0, 0))

    @property
    def position(self):
        return self.entity.position

    @property
    def x(self):
        return self.entity.x

    @property
    def z(self):
        return self.entity.z

    def update(self, dt):
        self.time_offset += dt * self.move_speed
        t = (math.sin(self.time_offset) + 1.0) / 2.0
        self.entity.position = Vec3(
            self.start_pos.x * (1 - t) + self.end_pos.x * t,
            self.start_pos.y * (1 - t) + self.end_pos.y * t,
            self.start_pos.z * (1 - t) + self.end_pos.z * t
        )
        self.entity.rotation_y += dt * 45.0
        self.ring_c.rotation_x += dt * 160.0

    def destroy(self):
        safe_destroy_entity(self.entity)


class RotatingGear:
    """Rotating industrial, cosmic or steampunk cogwheel with 8 beveled teeth and glowing hub."""
    def __init__(self, pos, rot_speed=65.0, col=None, radius=1.6):
        self.pos = Vec3(pos)
        self.rot_speed = rot_speed
        self.collision_radius = radius
        self.is_moving_hazard = True
        
        gear_col = col or color.rgb32(220, 140, 20)
        self.entity = Entity(
            model=Cylinder(resolution=16),
            color=gear_col,
            scale=(radius * 2.0, 0.62, radius * 2.0),
            position=pos
        )
        # Center hub & glowing core
        self.hub = Entity(parent=self.entity, model=Cylinder(resolution=12), color=color.tint(gear_col, -0.3), scale=(0.48, 1.45, 0.48), position=(0, 0, 0))
        Entity(parent=self.entity, model='sphere', color=color.tint(gear_col, 0.35), scale=(0.28, 1.75, 0.28), position=(0, 0.2, 0))
        # 8 Gear teeth
        for i in range(8):
            ang = i * (360.0 / 8.0)
            rad = math.radians(ang)
            Entity(
                parent=self.entity,
                model='cube',
                color=color.tint(gear_col, -0.15),
                scale=(0.24, 1.12, 0.24),
                position=(math.sin(rad) * 0.52, 0, math.cos(rad) * 0.52),
                rotation=(0, ang, 0)
            )

    @property
    def position(self):
        return self.entity.position

    @property
    def x(self):
        return self.entity.x

    @property
    def z(self):
        return self.entity.z

    def update(self, dt):
        self.entity.rotation_y += dt * self.rot_speed

    def destroy(self):
        safe_destroy_entity(self.entity)


class LevelManager:
    def __init__(self):
        self.current_level_idx = 0
        self.current_sublevel_idx = 0
        self.arena_size = (44, 44)
        
        self.floor = None
        self.walls = []
        self.obstacles = []
        self.decorations = []
        self.dynamic_hazards = []
        self.animated_spinners = []
        self.lights = []

    @property
    def current_level_data(self):
        return config.LEVELS_DATA[self.current_level_idx]

    def get_sublevel_target_apples(self):
        base = self.current_level_data["target_apples"]
        mults = [0.5, 0.7, 0.9, 1.0, 1.25]
        idx = max(0, min(self.current_sublevel_idx, len(mults) - 1))
        return max(15, int(base * mults[idx]))

    def get_sublevel_speed(self):
        base = self.current_level_data.get("base_speed", config.DEFAULT_SPEED)
        return base + self.current_sublevel_idx * 0.35

    def get_sublevel_enemy_count(self):
        base = self.current_level_data.get("enemy_count", 1)
        extra = 0 if self.current_sublevel_idx < 2 else (1 if self.current_sublevel_idx < 4 else 2)
        return base + extra

    def clear(self):
        """Destroys all active entities in the level cleanly."""
        self.animated_spinners.clear()

        if self.floor:
            safe_destroy_entity(self.floor)
            self.floor = None

        for w in self.walls:
            safe_destroy_entity(w)
        self.walls.clear()

        for haz in self.dynamic_hazards:
            haz.destroy()
        self.dynamic_hazards.clear()

        for obs in self.obstacles:
            safe_destroy_entity(obs)
        self.obstacles.clear()

        for dec in self.decorations:
            safe_destroy_entity(dec)
        self.decorations.clear()

        for l in self.lights:
            safe_destroy_entity(l)
        self.lights.clear()

    def build_level(self, level_index, sublevel_index=0):
        """Constructs the 3D level world, atmospheric lighting, perimeter architecture, and biome obstacles."""
        self.clear()
        self.current_level_idx = max(0, min(level_index, len(config.LEVELS_DATA) - 1))
        self.current_sublevel_idx = max(0, min(sublevel_index, 4))
        lvl = self.current_level_data
        
        self.arena_size = lvl["arena_size"]
        width, height = self.arena_size
        
        # Background & Atmospheric Horizon Fog
        window.color = lvl["bg_color"]
        scene.fog_color = lvl["bg_color"]
        scene.fog_density = (75.0, 260.0)

        # Multi-Light Sculptural Setup (Key Light + Rim Light + Ambient Light)
        self.dir_light = DirectionalLight(y=22, z=-14, x=10, shadows=False)
        self.dir_light.look_at(Vec3(0, 0, 0))
        self.rim_light = DirectionalLight(y=14, z=16, x=-12, color=color.rgb32(95, 105, 125), shadows=False)
        self.rim_light.look_at(Vec3(0, 0, 0))
        self.amb_light = AmbientLight(color=lvl["ambient_light"])
        self.lights.extend([self.dir_light, self.rim_light, self.amb_light])

        # Textured HD Floor
        tex_path = lvl.get("ground_texture", None)
        self.floor = Entity(
            model='plane',
            scale=(width, 1, height),
            texture=tex_path,
            color=lvl.get("ground_color", color.white),
            position=(0, 0, 0)
        )
        if hasattr(self.floor, 'texture_scale'):
            self.floor.texture_scale = (width / 8.0, height / 8.0)

        # Monumental Sub-Floor Citadel Plinth
        wall_col = lvl["wall_color"]
        grid_col = lvl.get("grid_color", color.tint(wall_col, 0.35))
        plinth = Entity(
            model='cube',
            texture='textures/stone_brick.png',
            color=color.tint(wall_col, -0.35),
            scale=(width + 3.4, 3.0, height + 3.4),
            position=(0, -1.55, 0)
        )
        self.decorations.append(plinth)

        # Boundary Walls (North, South, East, West)
        wall_thick = 1.4
        wall_h = 2.8
        hw = width / 2.0
        hh = height / 2.0

        w_north = Entity(model='cube', texture='textures/stone_brick.png', color=wall_col, scale=(width + wall_thick * 2, wall_h, wall_thick), position=(0, wall_h / 2.0, hh + wall_thick / 2.0))
        w_south = Entity(model='cube', texture='textures/stone_brick.png', color=wall_col, scale=(width + wall_thick * 2, wall_h, wall_thick), position=(0, wall_h / 2.0, -hh - wall_thick / 2.0))
        w_east = Entity(model='cube', texture='textures/stone_brick.png', color=wall_col, scale=(wall_thick, wall_h, height), position=(hw + wall_thick / 2.0, wall_h / 2.0, 0))
        w_west = Entity(model='cube', texture='textures/stone_brick.png', color=wall_col, scale=(wall_thick, wall_h, height), position=(-hw - wall_thick / 2.0, wall_h / 2.0, 0))
        self.walls.extend([w_north, w_south, w_east, w_west])

        # Wall Top Glowing Energy Rail
        rail_col = color.tint(wall_col, 0.35)
        for w in [w_north, w_south, w_east, w_west]:
            rail = Entity(model='cube', color=rail_col, scale=(w.scale_x, 0.36, w.scale_z * 0.85 if w.scale_x > w.scale_z else w.scale_z), position=(w.x, wall_h + 0.18, w.z))
            self.decorations.append(rail)

        # Perimeter Wall Battlement Buttresses
        for offset in [-width * 0.25, 0.0, width * 0.25]:
            for wz in [hh + wall_thick * 0.55, -hh - wall_thick * 0.55]:
                b_pil = Entity(model='cube', texture='textures/stone_brick.png', color=color.tint(wall_col, -0.15), scale=(1.8, wall_h * 1.18, wall_thick * 1.35), position=(offset, (wall_h * 1.18) / 2.0, wz))
                self.decorations.append(b_pil)
            for wx in [hw + wall_thick * 0.55, -hw - wall_thick * 0.55]:
                b_pil = Entity(model='cube', texture='textures/stone_brick.png', color=color.tint(wall_col, -0.15), scale=(wall_thick * 1.35, wall_h * 1.18, 1.8), position=(wx, (wall_h * 1.18) / 2.0, offset))
                self.decorations.append(b_pil)

        # 4 Corner Watchtowers with Conical Spires & Floating Beacon Crystals
        for cx, cz in [(-hw, -hh), (hw, -hh), (-hw, hh), (hw, hh)]:
            pillar = Entity(model=Cylinder(resolution=14), texture='textures/stone_brick.png', color=color.tint(wall_col, -0.18), scale=(wall_thick * 2.0, wall_h * 1.55, wall_thick * 2.0), position=(cx, 0.0, cz))
            roof = Entity(model=Cone(resolution=14), color=color.tint(wall_col, 0.15), scale=(wall_thick * 2.5, 2.2, wall_thick * 2.5), position=(cx, wall_h * 1.55, cz))
            beacon = Entity(model='cube', color=grid_col, scale=(0.75, 0.75, 0.75), position=(cx, wall_h * 1.55 + 2.8, cz), rotation=(45, 45, 45))
            self.decorations.extend([pillar, roof, beacon])
            self.animated_spinners.append((beacon, 95.0))

        # Distant Scenic Horizon Peaks outside the Arena
        self.build_outer_vista(width, height, wall_col, grid_col)

        # Build theme-specific high-detail 3D models & obstacles
        theme = lvl["theme"]
        theme_dispatch = {
            "forest": self.build_forest_obstacles,
            "desert": self.build_desert_obstacles,
            "ocean": self.build_ocean_obstacles,
            "space": self.build_space_obstacles,
            "factory": self.build_factory_obstacles,
            "city": self.build_city_obstacles,
            "arctic": self.build_arctic_obstacles,
            "lava": self.build_lava_obstacles,
            "crystal": self.build_crystal_obstacles,
            "jungle": self.build_jungle_obstacles,
            "sky": self.build_sky_obstacles,
            "toxic": self.build_toxic_obstacles,
            "swamp": self.build_swamp_obstacles,
            "necropolis": self.build_necropolis_obstacles,
            "steampunk": self.build_steampunk_obstacles,
            "event_horizon": self.build_event_horizon_obstacles,
            "dungeon": self.build_dungeon_obstacles,
            "quantum": self.build_quantum_obstacles
        }
        builder = theme_dispatch.get(theme, self.build_forest_obstacles)
        builder()

    def build_outer_vista(self, width, height, wall_col, accent_col):
        """Constructs a scenic ring of distant 3D mountains/monoliths outside the arena."""
        vista_radius = max(width, height) * 0.86
        for i in range(12):
            ang = math.radians(i * 30.0 + 15.0)
            vx = math.sin(ang) * vista_radius
            vz = math.cos(ang) * vista_radius
            peak_h = 14.0 + (i % 3) * 5.0
            peak_w = 9.0 + (i % 2) * 3.5
            peak = Entity(
                model=Cone(resolution=6),
                color=color.tint(wall_col, -0.28),
                scale=(peak_w, peak_h, peak_w),
                position=(vx, -2.0, vz),
                rotation=(0, i * 30, 0)
            )
            orb = Entity(
                model='sphere',
                color=accent_col,
                scale=(1.2, 1.2, 1.2),
                position=(vx, peak_h - 0.8, vz)
            )
            self.decorations.extend([peak, orb])

    # ================= 1. EMERALD FOREST =================
    def build_forest_obstacles(self):
        # High-Detail Conifer Pines
        for px, pz in [(-13, -13), (13, -13), (-13, 13), (13, 13), (-16, 0), (16, 0), (-8, -14), (8, 14)]:
            self.create_pine_tree(px, pz)

        # Detailed Fly Agaric Mushrooms
        for mx, mz in [(-6, -7), (7, -6), (-7, 8), (6, 7), (-5, -11), (5, 11), (-9, 2), (9, -2)]:
            self.create_mushroom(mx, mz)

        # Mossy Natural Boulders
        for rx, rz in [(-10, 5), (10, -5), (-5, -15), (5, 15), (14, 7), (-14, -7)]:
            self.create_mossy_boulder(rx, rz)

        # Fallen Hollow Logs
        for lx, lz, rot in [(-6, -11, 35), (6, 11, -25)]:
            self.create_hollow_log(lx, lz, rot)

    def create_pine_tree(self, x, z):
        # Flared Root Base grounded on arena floor (1.5x smaller)
        root_base = Entity(model=Cylinder(resolution=12), texture='textures/bark.png', color=color.rgb32(95, 60, 35), scale=(1.27, 0.53, 1.27), position=(x, 0.0, z))
        # Main tree trunk (1.5x thinner: width 0.70; tall enough so 1.8m of trunk is clearly visible below branches)
        trunk = Entity(model=Cylinder(resolution=12), texture='textures/bark.png', color=color.rgb32(115, 78, 46), scale=(0.70, 6.2, 0.70), position=(x, 0.0, z))
        # Small lower bark branch stub on visible trunk
        Entity(parent=trunk, model=Cylinder(resolution=8), texture='textures/bark.png', color=color.rgb32(100, 65, 38), scale=(0.24, 0.22, 0.24), position=(0.45, 0.18, 0), rotation=(0, 0, -55))
        trunk.collision_radius = 0.85
        self.obstacles.append(trunk)
        self.decorations.append(root_base)

        # 4 Tiers of Realistic Conical Foliage (1.5x larger crown, elevated so bottom branches hover 1.8m above ground)
        tiers = [
            (6.0, 3.6, 3.6, color.rgb32(30, 128, 50)),   # Bottom at y=1.8m (1.8m trunk clearance), top at y=5.4m
            (4.8, 3.2, 5.2, color.rgb32(36, 142, 58)),   # Bottom at y=3.6m, top at y=6.8m
            (3.6, 2.8, 6.7, color.rgb32(44, 156, 66)),   # Bottom at y=5.3m, top at y=8.1m
            (2.25, 2.4, 8.1, color.rgb32(55, 172, 75))   # Bottom at y=6.9m, top at y=9.3m
        ]
        for scale_xz, scale_y, y_pos, leaf_col in tiers:
            leaf = Entity(model=Cone(resolution=16), texture='textures/pine_needles.png', color=leaf_col, scale=(scale_xz, scale_y, scale_xz), position=(x, y_pos, z))
            self.decorations.append(leaf)

    def create_mushroom(self, x, z):
        stem = Entity(model=Cylinder(resolution=10), color=color.rgb32(245, 245, 230), scale=(0.55, 1.3, 0.55), position=(x, 0.0, z))
        # Stem skirt ring
        Entity(parent=stem, model=Cone(resolution=10), color=color.rgb32(235, 230, 210), scale=(1.55, 0.22, 1.55), position=(0, 0.62, 0))
        # Red Domed Cap
        cap = Entity(model='sphere', color=color.rgb32(235, 40, 40), scale=(1.5, 0.75, 1.5), position=(x, 1.3, z))
        # Gills underneath
        Entity(parent=cap, model=Cylinder(resolution=12), color=color.rgb32(220, 215, 190), scale=(0.9, 0.15, 0.9), position=(0, -0.2, 0))
        # 3D White Spore Studs
        for sx, sz in [(-0.35, 0.25), (0.35, -0.25), (0.25, 0.35), (-0.25, -0.35), (0, 0.45), (0, 0.0)]:
            Entity(parent=cap, model='sphere', color=color.white, scale=(0.2, 0.16, 0.2), position=(sx, 0.30, sz))
        cap.collision_radius = 0.9
        self.obstacles.append(cap)
        self.decorations.append(stem)

    def create_mossy_boulder(self, x, z):
        rock = Entity(model='sphere', texture='textures/stone_brick.png', color=color.rgb32(95, 105, 90), scale=(2.6, 1.6, 2.4), position=(x, 0.8, z))
        # Moss Patches & Small Glowing Forest Crystal
        Entity(parent=rock, model='sphere', texture='textures/pine_needles.png', color=color.rgb32(45, 140, 55), scale=(0.86, 0.38, 0.86), position=(0, 0.44, 0))
        Entity(parent=rock, model='sphere', color=color.rgb32(75, 80, 70), scale=(0.7, 0.9, 0.7), position=(0.5, -0.1, 0.3))
        rock.collision_radius = 1.3
        self.obstacles.append(rock)

    def create_hollow_log(self, x, z, rot):
        log = Entity(model=Cylinder(resolution=12), texture='textures/bark.png', color=color.rgb32(105, 70, 42), scale=(1.3, 4.2, 1.3), position=(x, 0.65, z), rotation=(90, rot, 0))
        # Dark Hollow Core + Top Moss Strip
        Entity(parent=log, model=Cylinder(resolution=10), color=color.rgb32(20, 15, 10), scale=(0.7, 1.05, 0.7))
        Entity(parent=log, model='sphere', color=color.rgb32(45, 145, 55), scale=(0.55, 0.75, 0.35), position=(0, 0.5, -0.45))
        log.collision_radius = 1.5
        self.obstacles.append(log)

    # ================= 2. GOLDEN DESERT =================
    def build_desert_obstacles(self):
        for px, pz in [(-13, -13), (13, -13), (-13, 13), (13, 13)]:
            self.create_pyramid(px, pz)

        for cx, cz in [(-6, -12), (6, -12), (-6, 12), (6, 12), (-14, 0), (14, 0), (-6, -6), (6, 6)]:
            self.create_cactus(cx, cz)

        for ox, oz in [(-7, -4), (7, 4), (-7, 4), (7, -4)]:
            self.create_obelisk(ox, oz)

    def create_pyramid(self, x, z):
        base = Entity(model='cube', texture='textures/sandstone_rune.png', color=color.rgb32(215, 175, 110), scale=(5.4, 1.2, 5.4), position=(x, 0.6, z))
        mid = Entity(model='cube', texture='textures/sandstone_rune.png', color=color.rgb32(225, 185, 120), scale=(3.8, 1.2, 3.8), position=(x, 1.8, z))
        top_step = Entity(model='cube', texture='textures/sandstone_rune.png', color=color.rgb32(235, 195, 130), scale=(2.2, 1.0, 2.2), position=(x, 2.9, z))
        # Golden Capstone (Pyramidion)
        cap = Entity(model=Cone(resolution=4), color=color.rgb32(255, 215, 50), scale=(1.8, 1.4, 1.8), position=(x, 3.4, z), rotation=(0, 45, 0))
        # 4 Corner Flame Braziers (tracked in decorations)
        for bx, bz in [(-2.2, -2.2), (2.2, -2.2), (-2.2, 2.2), (2.2, 2.2)]:
            b_stand = Entity(model=Cylinder(resolution=8), color=color.rgb32(80, 70, 60), scale=(0.42, 1.05, 0.42), position=(x + bx, 0.0, z + bz))
            b_flame = Entity(model='sphere', color=color.rgb32(255, 110, 20), scale=(0.38, 0.45, 0.38), position=(x + bx, 1.15, z + bz))
            self.decorations.extend([b_stand, b_flame])
        base.collision_radius = 2.6
        self.obstacles.append(base)
        self.decorations.extend([mid, top_step, cap])

    def create_cactus(self, x, z):
        c_col = color.rgb32(45, 145, 65)
        mound = Entity(model='sphere', color=color.rgb32(190, 155, 100), scale=(1.6, 0.4, 1.6), position=(x, 0.1, z))
        trunk = Entity(model=Cylinder(resolution=12), color=c_col, scale=(0.95, 3.8, 0.95), position=(x, 0.0, z))
        trunk.collision_radius = 1.0
        self.obstacles.append(trunk)
        self.decorations.append(mound)

        # L-shaped Branching Arms
        arm_l_h = Entity(model=Cylinder(resolution=8), color=c_col, scale=(0.5, 1.1, 0.5), position=(x - 0.7, 2.0, z), rotation=(0, 0, 90))
        arm_l_v = Entity(model=Cylinder(resolution=8), color=c_col, scale=(0.5, 1.5, 0.5), position=(x - 1.2, 2.0, z))
        arm_r_h = Entity(model=Cylinder(resolution=8), color=c_col, scale=(0.5, 1.1, 0.5), position=(x + 0.7, 1.5, z), rotation=(0, 0, 90))
        arm_r_v = Entity(model=Cylinder(resolution=8), color=c_col, scale=(0.5, 1.5, 0.5), position=(x + 1.2, 1.5, z))
        # Red desert blossom on top
        flower = Entity(model='sphere', color=color.rgb32(250, 50, 80), scale=(0.55, 0.38, 0.55), position=(x, 3.9, z))
        self.decorations.extend([arm_l_h, arm_l_v, arm_r_h, arm_r_v, flower])

    def create_obelisk(self, x, z):
        pedestal = Entity(model='cube', texture='textures/sandstone_rune.png', color=color.rgb32(180, 140, 85), scale=(1.8, 0.8, 1.8), position=(x, 0.4, z))
        shaft = Entity(model='cube', texture='textures/sandstone_rune.png', color=color.rgb32(215, 175, 110), scale=(1.2, 5.0, 1.2), position=(x, 3.2, z))
        pyramid_tip = Entity(model=Cone(resolution=4), color=color.rgb32(255, 215, 60), scale=(1.4, 1.2, 1.4), position=(x, 5.7, z), rotation=(0, 45, 0))
        sun_disc = Entity(model='cube', color=color.rgb32(255, 230, 80), scale=(0.65, 0.65, 0.15), position=(x, 7.3, z), rotation=(45, 0, 45))
        pedestal.collision_radius = 1.25
        self.obstacles.append(pedestal)
        self.decorations.extend([shaft, pyramid_tip, sun_disc])
        self.animated_spinners.append((sun_disc, 110.0))

    # ================= 3. ABYSSAL OCEAN =================
    def build_ocean_obstacles(self):
        coral_data = [
            (-13, -13, color.rgb32(255, 80, 120)),
            (13, -13, color.rgb32(255, 150, 40)),
            (-13, 13, color.rgb32(0, 230, 245)),
            (13, 13, color.rgb32(255, 110, 180)),
            (-16, 0, color.rgb32(255, 180, 50)),
            (16, 0, color.rgb32(40, 245, 180)),
        ]
        for cx, cz, col in coral_data:
            self.create_coral_reef(cx, cz, col)

        for kx, kz in [(-7, -7), (7, -7), (-7, 7), (7, 7), (-11, -11), (11, 11)]:
            self.create_giant_clam(kx, kz)

        self.dynamic_hazards.append(MovingLaserBarrier((-10, 0.6, -10), (10, 0.6, -10), move_speed=2.2, beam_color=color.rgb32(0, 230, 255)))
        self.dynamic_hazards.append(MovingLaserBarrier((10, 0.6, 10), (-10, 0.6, 10), move_speed=2.2, beam_color=color.rgb32(255, 80, 160)))

    def create_coral_reef(self, x, z, col):
        base = Entity(model='sphere', color=col, scale=(2.8, 1.8, 2.8), position=(x, 0.9, z))
        base.collision_radius = 1.45
        self.obstacles.append(base)
        for i in range(6):
            ang = i * (360.0 / 6.0)
            rad = math.radians(ang)
            bx = math.sin(rad) * 0.72
            bz = math.cos(rad) * 0.72
            branch = Entity(parent=base, model=Cylinder(resolution=8), color=color.tint(col, 0.15), scale=(0.28, 1.45, 0.28), position=(bx, 0.55, bz), rotation=(25 * math.cos(rad), ang, 25 * math.sin(rad)))
            Entity(parent=branch, model='sphere', color=color.white, scale=(1.25, 0.32, 1.25), position=(0, 0.95, 0))

    def create_giant_clam(self, x, z):
        bottom_shell = Entity(model='sphere', color=color.rgb32(90, 110, 145), scale=(2.4, 0.8, 2.0), position=(x, 0.4, z))
        top_shell = Entity(model='sphere', color=color.rgb32(115, 138, 175), scale=(2.4, 0.8, 2.0), position=(x, 1.15, z), rotation=(-28, 0, 0))
        pearl = Entity(model='sphere', color=color.rgb32(255, 250, 240), scale=(0.9, 0.9, 0.9), position=(x, 0.78, z))
        halo = Entity(parent=pearl, model='cube', color=color.rgba32(120, 240, 255, 170), scale=(1.4, 0.08, 1.4), rotation=(25, 0, 25))
        bottom_shell.collision_radius = 1.3
        self.obstacles.append(bottom_shell)
        self.decorations.extend([top_shell, pearl])
        self.animated_spinners.append((halo, 130.0))

    # ================= 4. DEEP SPACE =================
    def build_space_obstacles(self):
        for ax, az in [(-14, -14), (14, -14), (-14, 14), (14, 14), (-16, 0), (16, 0)]:
            self.create_satellite_probe(ax, az)

        for sx, sz in [(-8, -8), (8, 8), (-8, 8), (8, -8)]:
            self.create_asteroid_rock(sx, sz)

        self.dynamic_hazards.append(RotatingGear((0, 0.6, 14), rot_speed=55.0, col=color.rgb32(170, 60, 255), radius=2.2))
        self.dynamic_hazards.append(MovingLaserBarrier((-12, 0.6, -11), (12, 0.6, -11), move_speed=2.6, beam_color=color.rgb32(255, 40, 180)))

    def create_satellite_probe(self, x, z):
        core = Entity(model='sphere', color=color.rgb32(245, 200, 45), scale=(2.0, 2.0, 2.0), position=(x, 2.2, z))
        core.collision_radius = 1.4
        self.obstacles.append(core)
        Entity(parent=core, model='cube', color=color.rgb32(30, 75, 205), scale=(2.3, 0.08, 0.95), position=(-1.8, 0, 0))
        Entity(parent=core, model='cube', color=color.rgb32(30, 75, 205), scale=(2.3, 0.08, 0.95), position=(1.8, 0, 0))
        Entity(parent=core, model=Cone(resolution=14), color=color.rgb32(220, 225, 240), scale=(0.9, 0.5, 0.9), position=(0, 0.9, 0), rotation=(180, 0, 0))
        self.animated_spinners.append((core, 32.0))

    def create_asteroid_rock(self, x, z):
        ast = Entity(model='sphere', texture='textures/magma_rock.png', color=color.rgb32(125, 110, 155), scale=(2.8, 2.2, 2.8), position=(x, 1.2, z))
        ast.collision_radius = 1.45
        self.obstacles.append(ast)
        for i in range(4):
            ang = i * 90
            rad = math.radians(ang)
            Entity(parent=ast, model=Cone(resolution=5), texture='textures/crystal_facet.png', color=color.rgb32(180, 90, 255), scale=(0.35, 0.65, 0.35), position=(math.sin(rad) * 0.42, 0.25, math.cos(rad) * 0.42), rotation=(35 * math.cos(rad), ang, 35 * math.sin(rad)))

    # ================= 5. CYBER FACTORY =================
    def build_factory_obstacles(self):
        for fx, fz in [(-15, -15), (15, -15), (-15, 15), (15, 15), (-8, 0), (8, 0)]:
            self.create_cooling_tower(fx, fz)

        for tx, tz in [(-6, -10), (6, 10), (-6, 10), (6, -10)]:
            self.create_cargo_crate(tx, tz)

        self.dynamic_hazards.append(RotatingGear((-10, 0.5, -6), rot_speed=80.0, col=color.rgb32(220, 140, 20), radius=1.8))
        self.dynamic_hazards.append(RotatingGear((10, 0.5, 6), rot_speed=-80.0, col=color.rgb32(220, 140, 20), radius=1.8))
        self.dynamic_hazards.append(MovingLaserBarrier((-10, 0.6, -5), (10, 0.6, -5), move_speed=3.0, beam_color=color.rgb32(255, 60, 40)))

    def create_cooling_tower(self, x, z):
        base = Entity(model=Cylinder(resolution=16), texture='textures/metal_crate.png', color=color.rgb32(130, 138, 150), scale=(2.6, 4.8, 2.6), position=(x, 0.0, z))
        lip = Entity(model=Cylinder(resolution=16), color=color.rgb32(240, 175, 20), scale=(2.95, 0.5, 2.95), position=(x, 4.6, z))
        core = Entity(model='sphere', color=color.rgb32(255, 110, 20), scale=(1.5, 0.6, 1.5), position=(x, 5.0, z))
        base.collision_radius = 1.5
        self.obstacles.append(base)
        self.decorations.extend([lip, core])

    def create_cargo_crate(self, x, z):
        crate = Entity(model='cube', texture='textures/metal_crate.png', color=color.rgb32(225, 185, 60), scale=(2.4, 2.4, 2.4), position=(x, 1.2, z))
        crate.collision_radius = 1.35
        self.obstacles.append(crate)

    # ================= 6. NEON METROPOLIS =================
    def build_city_obstacles(self):
        sky_data = [
            (-16, -16, 12.0), (16, -16, 15.0), (-16, 16, 14.0), (16, 16, 16.0),
            (-10, -8, 9.0), (10, 8, 9.5), (-10, 8, 10.0), (10, -8, 8.5)
        ]
        for sx, sz, sh in sky_data:
            self.create_skyscraper(sx, sz, sh)

        self.dynamic_hazards.append(MovingLaserBarrier((-12, 0.6, -7), (12, 0.6, -7), move_speed=2.8, beam_color=color.rgb32(255, 0, 128)))
        self.dynamic_hazards.append(MovingLaserBarrier((12, 0.6, 7), (-12, 0.6, 7), move_speed=2.8, beam_color=color.rgb32(0, 220, 255)))
        self.dynamic_hazards.append(RotatingGear((0, 0.6, -15), rot_speed=70.0, col=color.rgb32(255, 0, 128), radius=2.0))

    def create_skyscraper(self, x, z, h):
        tower = Entity(model='cube', texture='textures/cyber_building.png', color=color.white, scale=(3.4, h, 3.4), position=(x, h / 2.0, z))
        if hasattr(tower, 'texture_scale'):
            tower.texture_scale = (1.0, max(1.0, int(h / 4.0)))
        Entity(parent=tower, model='cube', color=color.rgb32(0, 235, 255), scale=(1.04, 0.04, 1.04), position=(0, 0.5, 0))
        Entity(parent=tower, model=Cylinder(resolution=8), color=color.rgb32(255, 0, 140), scale=(0.08, 0.35, 0.08), position=(0, 0.52, 0))
        tower.collision_radius = 1.9
        self.obstacles.append(tower)

    # ================= 7. FROZEN TUNDRA =================
    def build_arctic_obstacles(self):
        for ix, iz in [(-14, -14), (14, -14), (-14, 14), (14, 14), (-16, 0), (16, 0)]:
            self.create_ice_spire(ix, iz)

        for sx, sz in [(-8, -8), (8, 8), (-8, 8), (8, -8)]:
            self.create_igloo(sx, sz)

        self.dynamic_hazards.append(MovingLaserBarrier((-10, 0.6, -10), (10, 0.6, -10), move_speed=2.5, beam_color=color.rgb32(100, 220, 255)))

    def create_ice_spire(self, x, z):
        spire = Entity(model=Cone(resolution=8), texture='textures/crystal_facet.png', color=color.rgb32(165, 235, 255), scale=(2.2, 6.5, 2.2), position=(x, 0.0, z))
        snow_base = Entity(model='sphere', color=color.rgb32(245, 250, 255), scale=(3.0, 1.0, 3.0), position=(x, 0.4, z))
        spire.collision_radius = 1.45
        self.obstacles.append(spire)
        self.decorations.append(snow_base)

    def create_igloo(self, x, z):
        dome = Entity(model='sphere', texture='textures/stone_brick.png', color=color.rgb32(225, 242, 255), scale=(3.2, 2.4, 3.2), position=(x, 1.1, z))
        tunnel = Entity(model=Cylinder(resolution=10), color=color.rgb32(210, 232, 250), scale=(1.2, 1.6, 1.2), position=(x, 0.7, z + 1.6), rotation=(90, 0, 0))
        dome.collision_radius = 1.7
        self.obstacles.append(dome)
        self.decorations.append(tunnel)

    # ================= 8. LAVA INFERNO =================
    def build_lava_obstacles(self):
        for lx, lz in [(-15, -15), (15, -15), (-15, 15), (15, 15), (-10, 0), (10, 0)]:
            self.create_volcanic_chimney(lx, lz)

        for ox, oz in [(-7, -7), (7, 7), (-7, 7), (7, -7)]:
            self.create_basalt_pillar(ox, oz)

        self.dynamic_hazards.append(MovingLaserBarrier((-12, 0.6, -8), (12, 0.6, -8), move_speed=3.2, beam_color=color.rgb32(255, 60, 10)))

    def create_volcanic_chimney(self, x, z):
        cone = Entity(model=Cone(resolution=12), texture='textures/magma_rock.png', color=color.rgb32(195, 140, 120), scale=(3.2, 4.5, 3.2), position=(x, 0.0, z))
        lava_pool = Entity(model='sphere', color=color.rgb32(255, 95, 15), scale=(3.6, 0.16, 3.6), position=(x, 0.06, z))
        molten_core = Entity(model='sphere', color=color.rgb32(255, 165, 30), scale=(1.25, 1.25, 1.25), position=(x, 4.3, z))
        cone.collision_radius = 1.65
        self.obstacles.append(cone)
        self.decorations.extend([lava_pool, molten_core])

    def create_basalt_pillar(self, x, z):
        pillar = Entity(model=Cylinder(resolution=6), texture='textures/magma_rock.png', color=color.rgb32(140, 110, 115), scale=(1.8, 5.2, 1.8), position=(x, 0.0, z))
        cap = Entity(model=Cylinder(resolution=6), color=color.rgb32(255, 110, 20), scale=(1.5, 0.25, 1.5), position=(x, 5.1, z))
        pillar.collision_radius = 1.3
        self.obstacles.append(pillar)
        self.decorations.append(cap)

    # ================= 9. CRYSTAL CAVERNS =================
    def build_crystal_obstacles(self):
        for cx, cz in [(-14, -14), (14, -14), (-14, 14), (14, 14), (-8, -8), (8, 8), (-8, 8), (8, -8)]:
            self.create_geode_cluster(cx, cz)

        self.dynamic_hazards.append(RotatingGear((0, 0.6, 12), rot_speed=65.0, col=color.rgb32(210, 80, 255), radius=2.2))
        self.dynamic_hazards.append(RotatingGear((0, 0.6, -12), rot_speed=-65.0, col=color.rgb32(210, 80, 255), radius=2.2))

    def create_geode_cluster(self, x, z):
        base = Entity(model='sphere', color=color.rgb32(75, 65, 85), scale=(2.6, 1.2, 2.6), position=(x, 0.6, z))
        base.collision_radius = 1.4
        self.obstacles.append(base)
        for i, (scale_h, rot_x, rot_z) in enumerate([(4.6, 15, 20), (3.8, -20, 15), (3.2, 10, -25), (3.5, -12, -18)]):
            Entity(parent=base, model=Cone(resolution=6), texture='textures/crystal_facet.png', color=color.rgb32(225, 95, 255), scale=(0.42, scale_h / 1.2, 0.42), position=(0, 0.2, 0), rotation=(rot_x, i * 90, rot_z))

    # ================= 10. LOST JUNGLE =================
    def build_jungle_obstacles(self):
        for tx, tz in [(-16, -16), (16, -16), (-16, 16), (16, 16)]:
            self.create_tribal_totem(tx, tz)

        for px, pz in [(-9, -9), (9, 9), (-9, 9), (9, -9), (-14, 0), (14, 0)]:
            self.create_palm_tree(px, pz)

    def create_palm_tree(self, x, z):
        mound = Entity(model='sphere', color=color.rgb32(110, 85, 45), scale=(1.2, 0.33, 1.2), position=(x, 0.1, z))
        # Slender trunk (1.5x thinner: width 0.63) with tall clear visibility below fronds
        trunk = Entity(model=Cylinder(resolution=10), texture='textures/bark.png', color=color.rgb32(125, 85, 48), scale=(0.63, 5.0, 0.63), position=(x, 0.0, z))
        trunk.collision_radius = 0.70
        self.obstacles.append(trunk)
        self.decorations.append(mound)
        # Coconuts nestled under crown
        for ci in range(3):
            c_ang = math.radians(ci * 120)
            coco = Entity(model='sphere', color=color.rgb32(90, 55, 25), scale=(0.42, 0.42, 0.42), position=(x + math.sin(c_ang) * 0.38, 4.65, z + math.cos(c_ang) * 0.38))
            self.decorations.append(coco)
        # 8 Radial Fronds (1.5x larger crown, perched atop tall trunk; properly tracked in decorations)
        for i in range(8):
            ang = i * (360.0 / 8.0)
            rad = math.radians(ang)
            frond = Entity(model='sphere', texture='textures/pine_needles.png', color=color.rgb32(38, 175, 58), scale=(4.2, 0.22, 1.2), position=(x + math.sin(rad) * 1.95, 4.95, z + math.cos(rad) * 1.95), rotation=(-18, ang, 0))
            self.decorations.append(frond)

    def create_tribal_totem(self, x, z):
        totem = Entity(model=Cylinder(resolution=12), texture='textures/sandstone_rune.png', color=color.rgb32(165, 130, 85), scale=(1.6, 5.5, 1.6), position=(x, 0.0, z))
        Entity(parent=totem, model='cube', color=color.rgb32(235, 55, 40), scale=(2.3, 0.12, 0.25), position=(0, 0.65, 0))
        Entity(parent=totem, model='sphere', color=color.rgb32(40, 255, 120), scale=(0.28, 0.08, 0.28), position=(-0.28, 0.78, 0.45))
        Entity(parent=totem, model='sphere', color=color.rgb32(40, 255, 120), scale=(0.28, 0.08, 0.28), position=(0.28, 0.78, 0.45))
        totem.collision_radius = 1.45
        self.obstacles.append(totem)

    # ================= 11. SKY SANCTUARY =================
    def build_sky_obstacles(self):
        for tx, tz in [(-15, -15), (15, -15), (-15, 15), (15, 15), (-10, 0), (10, 0)]:
            self.create_pantheon_pillar(tx, tz)

        self.dynamic_hazards.append(MovingLaserBarrier((-14, 0.6, -8), (14, 0.6, -8), move_speed=3.4, beam_color=color.rgb32(255, 255, 80)))

    def create_pantheon_pillar(self, x, z):
        plinth = Entity(model='cube', color=color.rgb32(230, 235, 245), scale=(1.8, 0.6, 1.8), position=(x, 0.3, z))
        shaft = Entity(model=Cylinder(resolution=16), color=color.rgb32(245, 250, 255), scale=(1.1, 4.8, 1.1), position=(x, 0.6, z))
        capital = Entity(model='cube', color=color.rgb32(245, 215, 90), scale=(1.9, 0.6, 1.9), position=(x, 5.7, z))
        halo = Entity(model='cube', color=color.rgba32(255, 240, 120, 190), scale=(1.6, 0.12, 1.6), position=(x, 6.6, z), rotation=(25, 0, 25))
        plinth.collision_radius = 1.3
        self.obstacles.append(plinth)
        self.decorations.extend([shaft, capital, halo])
        self.animated_spinners.append((halo, 90.0))

    # ================= 12. TOXIC WASTELAND =================
    def build_toxic_obstacles(self):
        for bx, bz in [(-15, -15), (15, -15), (-15, 15), (15, 15), (-9, -9), (9, 9), (-12, 0), (12, 0)]:
            self.create_biohazard_barrel(bx, bz)

        self.dynamic_hazards.append(MovingLaserBarrier((-12, 0.6, -8), (12, 0.6, -8), move_speed=3.2, beam_color=color.rgb32(80, 255, 40)))
        self.dynamic_hazards.append(RotatingGear((0, 0.6, 13), rot_speed=70.0, col=color.rgb32(190, 220, 30), radius=2.2))

    def create_biohazard_barrel(self, x, z):
        drum = Entity(model=Cylinder(resolution=14), texture='textures/metal_crate.png', color=color.rgb32(225, 200, 35), scale=(1.8, 3.4, 1.8), position=(x, 0.0, z))
        drum.collision_radius = 1.35
        self.obstacles.append(drum)
        puddle = Entity(model='sphere', color=color.rgb32(65, 255, 30), scale=(2.8, 0.12, 2.8), position=(x, 0.05, z))
        cap_glow = Entity(model=Cylinder(resolution=12), color=color.rgb32(90, 255, 45), scale=(1.5, 0.15, 1.5), position=(x, 3.4, z))
        self.decorations.extend([puddle, cap_glow])

    # ================= 13. MYSTIC SWAMP =================
    def build_swamp_obstacles(self):
        for sx, sz in [(-16, -16), (16, -16), (-16, 16), (16, 16), (-10, -5), (10, 5), (-5, 12), (5, -12)]:
            self.create_cypress_tree(sx, sz)

        self.dynamic_hazards.append(MovingLaserBarrier((-11, 0.6, 0), (11, 0.6, 0), move_speed=2.4, beam_color=color.rgb32(160, 240, 80)))

    def create_cypress_tree(self, x, z):
        # 1.5x thinner trunk with tall visible clearance below moss dome
        trunk = Entity(model=Cylinder(resolution=10), texture='textures/bark.png', color=color.rgb32(90, 60, 42), scale=(0.73, 4.6, 0.73), position=(x, 0.0, z))
        buttress = Entity(model=Cone(resolution=10), texture='textures/bark.png', color=color.rgb32(80, 52, 36), scale=(1.87, 1.8, 1.87), position=(x, 0.0, z))
        # 1.5x larger crown (perched at y=4.6, bottom at 3.55m)
        moss = Entity(model='sphere', texture='textures/pine_needles.png', color=color.rgb32(55, 145, 65), scale=(4.8, 2.1, 4.8), position=(x, 4.6, z))
        wisp = Entity(model='sphere', color=color.rgb32(160, 255, 90), scale=(0.45, 0.45, 0.45), position=(x + 1.1, 2.2, z))
        trunk.collision_radius = 0.95
        self.obstacles.append(trunk)
        self.decorations.extend([buttress, moss, wisp])

    # ================= 14. ANCIENT NECROPOLIS =================
    def build_necropolis_obstacles(self):
        for nx, nz in [(-16, -16), (16, -16), (-16, 16), (16, 16), (-8, -8), (8, 8), (-8, 8), (8, -8)]:
            self.create_anubis_statue(nx, nz)

        self.dynamic_hazards.append(RotatingGear((0, 0.6, -14), rot_speed=60.0, col=color.rgb32(210, 160, 60), radius=2.2))
        self.dynamic_hazards.append(MovingLaserBarrier((-12, 0.6, 8), (12, 0.6, 8), move_speed=2.8, beam_color=color.rgb32(240, 180, 40)))

    def create_anubis_statue(self, x, z):
        plinth = Entity(model='cube', texture='textures/sandstone_rune.png', color=color.rgb32(185, 145, 95), scale=(2.2, 1.8, 2.2), position=(x, 0.9, z))
        statue = Entity(model=Cylinder(resolution=10), color=color.rgb32(28, 28, 35), scale=(1.2, 3.6, 1.2), position=(x, 1.8, z))
        golden_head = Entity(model=Cone(resolution=6), color=color.rgb32(255, 210, 50), scale=(1.05, 1.35, 1.05), position=(x, 5.4, z))
        plinth.collision_radius = 1.45
        self.obstacles.append(plinth)
        self.decorations.extend([statue, golden_head])

    # ================= 15. STEAMPUNK SKY =================
    def build_steampunk_obstacles(self):
        for bx, bz in [(-17, -17), (17, -17), (-17, 17), (17, 17), (-10, 0), (10, 0), (0, 15), (0, -15)]:
            self.create_clockwork_engine(bx, bz)

        self.dynamic_hazards.append(RotatingGear((-11, 0.6, -7), rot_speed=85.0, col=color.rgb32(210, 140, 50), radius=2.0))
        self.dynamic_hazards.append(RotatingGear((11, 0.6, 7), rot_speed=-85.0, col=color.rgb32(210, 140, 50), radius=2.0))

    def create_clockwork_engine(self, x, z):
        boiler = Entity(model=Cylinder(resolution=16), texture='textures/metal_crate.png', color=color.rgb32(205, 130, 65), scale=(2.2, 4.4, 2.2), position=(x, 0.0, z))
        boiler.collision_radius = 1.5
        self.obstacles.append(boiler)
        Entity(parent=boiler, model=Cylinder(resolution=10), color=color.rgb32(235, 185, 80), scale=(0.38, 1.4, 0.38), position=(0.35, 0.6, 0))
        flywheel = Entity(parent=boiler, model='cube', color=color.rgb32(245, 200, 90), scale=(1.25, 0.14, 1.25), position=(0, 0.55, 0), rotation=(0, 45, 0))
        self.animated_spinners.append((flywheel, 120.0))

    # ================= 16. EVENT HORIZON =================
    def build_event_horizon_obstacles(self):
        for ex, ez in [(-18, -18), (18, -18), (-18, 18), (18, 18), (-9, -9), (9, 9), (-9, 9), (9, -9)]:
            self.create_void_monolith(ex, ez)

        self.dynamic_hazards.append(MovingLaserBarrier((-15, 0.6, -9), (15, 0.6, -9), move_speed=3.6, beam_color=color.rgb32(255, 80, 20)))
        self.dynamic_hazards.append(MovingLaserBarrier((15, 0.6, 9), (-15, 0.6, 9), move_speed=3.6, beam_color=color.rgb32(180, 40, 255)))

    def create_void_monolith(self, x, z):
        singularity = Entity(model='sphere', color=color.rgb32(15, 12, 25), scale=(2.6, 2.6, 2.6), position=(x, 1.8, z))
        singularity.collision_radius = 1.6
        self.obstacles.append(singularity)
        r1 = Entity(parent=singularity, model='cube', color=color.rgba32(255, 105, 30, 210), scale=(1.48, 0.08, 1.48), rotation=(30, 45, 0))
        r2 = Entity(parent=singularity, model='cube', color=color.rgba32(185, 45, 255, 210), scale=(1.65, 0.08, 1.65), rotation=(-30, -45, 0))
        self.animated_spinners.append((r1, 140.0))
        self.animated_spinners.append((r2, -110.0))

    # ================= 17. DRAGON DUNGEON =================
    def build_dungeon_obstacles(self):
        for dx, dz in [(-18, -18), (18, -18), (-18, 18), (18, 18), (-10, 0), (10, 0), (0, 15), (0, -15)]:
            self.create_dungeon_turret(dx, dz)

        self.dynamic_hazards.append(MovingLaserBarrier((-14, 0.6, -8), (14, 0.6, -8), move_speed=3.4, beam_color=color.rgb32(255, 40, 20)))
        self.dynamic_hazards.append(RotatingGear((0, 0.6, 12), rot_speed=75.0, col=color.rgb32(220, 60, 30), radius=2.4))

    def create_dungeon_turret(self, x, z):
        tower = Entity(model=Cylinder(resolution=14), texture='textures/stone_brick.png', color=color.rgb32(85, 78, 90), scale=(2.2, 5.2, 2.2), position=(x, 0.0, z))
        tower.collision_radius = 1.55
        self.obstacles.append(tower)
        Entity(parent=tower, model=Cylinder(resolution=14), color=color.rgb32(45, 40, 50), scale=(1.18, 0.18, 1.18), position=(0, 0.95, 0))
        brazier = Entity(parent=tower, model='sphere', color=color.rgb32(255, 85, 20), scale=(0.55, 0.55, 0.55), position=(0, 1.12, 0))
        self.animated_spinners.append((brazier, 90.0))

    # ================= 18. QUANTUM CITADEL =================
    def build_quantum_obstacles(self):
        for qx, qz in [(-18, -18), (18, -18), (-18, 18), (18, 18), (-12, 0), (12, 0)]:
            self.create_quantum_obelisk(qx, qz)

        self.dynamic_hazards.append(RotatingGear((0, 0.6, 15), rot_speed=95.0, col=color.rgb32(255, 0, 128), radius=2.6))
        self.dynamic_hazards.append(RotatingGear((0, 0.6, -15), rot_speed=-95.0, col=color.rgb32(0, 240, 255), radius=2.6))
        self.dynamic_hazards.append(MovingLaserBarrier((-16, 0.6, -8), (16, 0.6, -8), move_speed=3.8, beam_color=color.rgb32(255, 0, 128)))
        self.dynamic_hazards.append(MovingLaserBarrier((16, 0.6, 8), (-16, 0.6, 8), move_speed=3.8, beam_color=color.rgb32(0, 240, 255)))

    def create_quantum_obelisk(self, x, z):
        core = Entity(model='sphere', texture='textures/crystal_facet.png', color=color.rgb32(255, 40, 160), scale=(2.2, 2.2, 2.2), position=(x, 2.2, z))
        core.collision_radius = 1.6
        self.obstacles.append(core)
        r1 = Entity(parent=core, model=Cylinder(resolution=16), color=color.rgb32(0, 240, 255), scale=(1.45, 0.08, 1.45), rotation=(45, 0, 45))
        r2 = Entity(parent=core, model=Cylinder(resolution=16), color=color.rgb32(255, 230, 0), scale=(1.75, 0.08, 1.75), rotation=(-45, 0, -45))
        self.animated_spinners.append((r1, 150.0))
        self.animated_spinners.append((r2, -130.0))

    def update_dynamic_hazards(self, dt):
        """Advances animations for dynamic barriers, gears, lasers, and scenic spinners."""
        for haz in self.dynamic_hazards:
            haz.update(dt)
        for ent, spd in self.animated_spinners:
            if ent:
                ent.rotation_y += dt * spd

    def check_wall_collision(self, snake):
        """Checks if snake's head hit the outer arena boundary walls."""
        if not snake or not snake.is_alive:
            return False
        hw = (self.arena_size[0] / 2.0) - 0.4
        hh = (self.arena_size[1] / 2.0) - 0.4
        pos = snake.head.position
        return abs(pos.x) >= hw or abs(pos.z) >= hh

    def check_obstacle_collision(self, snake):
        """Checks if snake's head hit any static or dynamic obstacles (2D X-Z cylinder intersection)."""
        if not snake or not snake.is_alive:
            return False

        hx = snake.head.x
        hz = snake.head.z
        head_radius = config.HEAD_RADIUS

        # Static obstacles
        for obs in self.obstacles:
            radius = getattr(obs, 'collision_radius', 1.0)
            dx = hx - obs.x
            dz = hz - obs.z
            dist_sq = dx * dx + dz * dz
            thresh = radius + head_radius * 0.75
            if dist_sq < (thresh * thresh):
                return True

        # Dynamic hazards
        for haz in self.dynamic_hazards:
            dx = hx - haz.position.x
            dz = hz - haz.position.z
            dist_sq = dx * dx + dz * dz
            thresh = haz.collision_radius + head_radius * 0.75
            if dist_sq < (thresh * thresh):
                return True

        return False
