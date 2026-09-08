"""
Items, Diverse Foods, and Power-ups for 3D Snake Adventure.
Handles 10 diverse 3D food items: Red Apple, Juicy Pear, Ripe Banana, Sweet Strawberry,
Fresh Orange, Watermelon Slice, Twin Cherries, Tropical Pineapple, Starfruit, and Golden Apple.
Power-ups: Speed Boost (+25% for 10s), Slow Motion (-25% for 10s), Magnet (10s),
Shield (12s), +1 Life Heart, and Mega Food (+10 Food Feast).
Both Player and AI opponents eat food and power-ups in the arena.
"""
import random
import math
from ursina import Entity, Vec3, color, destroy, time
from ursina.models.procedural.cylinder import Cylinder
from ursina.models.procedural.cone import Cone
import config

class ParticleBurst:
    """Explosive spark particle effect upon picking up food or severing tail."""
    def __init__(self, position, tint_color, count=7):
        self.particles = []
        self.velocities = []
        self.lifespan = 0.40
        self.timer = 0.0
        self.is_finished = False

        for _ in range(count):
            p = Entity(
                model='cube',
                color=tint_color,
                unlit=True,
                collider=None,
                scale=random.uniform(0.12, 0.20),
                position=position + Vec3(random.uniform(-0.15, 0.15), random.uniform(0.0, 0.15), random.uniform(-0.15, 0.15))
            )
            vel = Vec3(
                random.uniform(-3.5, 3.5),
                random.uniform(2.5, 6.0),
                random.uniform(-3.5, 3.5)
            )
            self.particles.append(p)
            self.velocities.append(vel)

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.lifespan:
            self.destroy_all()
            return

        for i, p in enumerate(self.particles):
            self.velocities[i].y -= 14.0 * dt
            p.position += self.velocities[i] * dt
            p.scale *= max(0.0, 1.0 - (dt / self.lifespan) * 1.8)
            if p.scale_x < 0.03:
                p.visible = False

    def destroy_all(self):
        self.is_finished = True
        for p in self.particles:
            destroy(p)
        self.particles.clear()


class BaseItem(Entity):
    """Base class for floating, spinning 3D collectible items."""
    def __init__(self, item_type="apple", position=Vec3(0, 0.5, 0), item_color=color.white):
        super().__init__(position=position)
        self.item_type = item_type
        self.base_y = position.y
        self.time_offset = random.uniform(0, math.pi * 2)
        self.color_tint = item_color
        self.lifespan = -1.0  # -1 means infinite until collected
        self.points = 10
        self.growth = 1
        self.quota_value = 1
        self.food_name = "Їжа"

    def on_destroy(self):
        """Recursively destroy all child model components to eliminate entity/memory leaks."""
        if hasattr(self, 'children'):
            for child in list(self.children):
                destroy(child)

    def update_animation(self, dt):
        """Floating hover and smooth rotation."""
        self.time_offset += dt * 3.5
        self.y = self.base_y + math.sin(self.time_offset) * 0.18
        self.rotation_y += dt * 90.0


# ================= 10 DIVERSE 3D FOOD ITEMS =================

class Apple(BaseItem):
    """1. Red Apple: +10 Score, +1 Length, +1 Quota."""
    def __init__(self, position=Vec3(0, 0.5, 0)):
        super().__init__(item_type="apple", position=position, item_color=config.COLOR_APPLE_NORMAL)
        self.points = 10
        self.growth = 1
        self.quota_value = 1
        self.food_name = "Яблуко"
        
        self.body = Entity(parent=self, model='sphere', color=config.COLOR_APPLE_NORMAL, scale=(0.85, 0.85, 0.85))
        self.stem = Entity(parent=self, model=Cylinder(resolution=6), color=color.rgb32(110, 60, 30), scale=(0.1, 0.35, 0.1), position=(0, 0.45, 0), rotation=(15, 0, 10))
        self.leaf = Entity(parent=self, model='quad', color=color.rgb32(50, 200, 60), scale=(0.28, 0.16), position=(0.12, 0.55, 0), rotation=(0, 45, 30), double_sided=True)


class Pear(BaseItem):
    """2. Juicy Pear: +15 Score, +1 Length, +1 Quota."""
    def __init__(self, position=Vec3(0, 0.5, 0)):
        col = color.rgb32(175, 215, 45)
        super().__init__(item_type="pear", position=position, item_color=col)
        self.points = 15
        self.growth = 1
        self.quota_value = 1
        self.food_name = "Соковита Груша"
        
        # Teardrop shape: bottom sphere + upper tapered sphere
        self.body_bottom = Entity(parent=self, model='sphere', color=col, scale=(0.85, 0.8, 0.85), position=(0, 0, 0))
        self.body_top = Entity(parent=self, model='sphere', color=color.rgb32(190, 225, 55), scale=(0.6, 0.65, 0.6), position=(0, 0.42, 0))
        self.stem = Entity(parent=self, model=Cylinder(resolution=6), color=color.rgb32(95, 55, 25), scale=(0.08, 0.35, 0.08), position=(0, 0.72, 0), rotation=(12, 0, -10))
        self.leaf = Entity(parent=self, model='quad', color=color.rgb32(40, 180, 50), scale=(0.26, 0.15), position=(0.1, 0.8, 0), rotation=(0, 30, 20), double_sided=True)


class Banana(BaseItem):
    """3. Ripe Banana: +20 Score, +1 Length, +1 Quota."""
    def __init__(self, position=Vec3(0, 0.5, 0)):
        col = color.rgb32(250, 215, 30)
        super().__init__(item_type="banana", position=position, item_color=col)
        self.points = 20
        self.growth = 1
        self.quota_value = 1
        self.food_name = "Стиглий Банан"
        
        # Curved 3-segment banana arc
        for dx, dy, rot_z in [(-0.32, 0.14, -28), (0, 0, 0), (0.32, 0.14, 28)]:
            Entity(parent=self, model=Cylinder(resolution=8), color=col, scale=(0.26, 0.52, 0.26), position=(dx, dy, 0), rotation=(0, 0, rot_z))
        # Brown banana tips
        Entity(parent=self, model='sphere', color=color.rgb32(90, 60, 20), scale=(0.18, 0.18, 0.18), position=(-0.46, 0.24, 0))
        Entity(parent=self, model='sphere', color=color.rgb32(120, 90, 30), scale=(0.16, 0.16, 0.16), position=(0.46, 0.24, 0))


class Strawberry(BaseItem):
    """4. Sweet Strawberry: +25 Score, +1 Length, +2 Quota."""
    def __init__(self, position=Vec3(0, 0.5, 0)):
        col = color.rgb32(235, 35, 55)
        super().__init__(item_type="strawberry", position=position, item_color=col)
        self.points = 25
        self.growth = 1
        self.quota_value = 2
        self.food_name = "Полуниця"
        
        # Inverted cone berry body
        self.cone = Entity(parent=self, model=Cone(resolution=10), color=col, scale=(0.85, 1.05, 0.85), position=(0, 0.1, 0), rotation=(180, 0, 0))
        # Top green leaves / sepals
        for i in range(5):
            ang = i * 72
            rad = math.radians(ang)
            Entity(parent=self, model='quad', color=color.rgb32(35, 185, 55), scale=(0.28, 0.14), position=(math.sin(rad) * 0.28, 0.62, math.cos(rad) * 0.28), rotation=(0, ang, 30), double_sided=True)
        self.stem = Entity(parent=self, model=Cylinder(resolution=6), color=color.rgb32(30, 160, 45), scale=(0.08, 0.25, 0.08), position=(0, 0.72, 0))


class Orange(BaseItem):
    """5. Fresh Orange: +20 Score, +1 Length, +1 Quota."""
    def __init__(self, position=Vec3(0, 0.5, 0)):
        col = color.rgb32(255, 130, 15)
        super().__init__(item_type="orange", position=position, item_color=col)
        self.points = 20
        self.growth = 1
        self.quota_value = 1
        self.food_name = "Апельсин"
        
        self.body = Entity(parent=self, model='sphere', color=col, scale=(0.88, 0.82, 0.88))
        self.leaf = Entity(parent=self, model='quad', color=color.rgb32(40, 175, 45), scale=(0.28, 0.16), position=(0.1, 0.48, 0), rotation=(0, 45, 20), double_sided=True)
        self.stem = Entity(parent=self, model=Cylinder(resolution=6), color=color.rgb32(80, 50, 20), scale=(0.08, 0.22, 0.08), position=(0, 0.44, 0))


class Watermelon(BaseItem):
    """6. Watermelon Slice: +30 Score, +2 Length, +2 Quota."""
    def __init__(self, position=Vec3(0, 0.5, 0)):
        col = color.rgb32(240, 40, 65)
        super().__init__(item_type="watermelon", position=position, item_color=col)
        self.points = 30
        self.growth = 2
        self.quota_value = 2
        self.food_name = "Кавун"
        
        # Outer Green Rind
        self.rind = Entity(parent=self, model=Cylinder(resolution=14), color=color.rgb32(35, 145, 55), scale=(1.1, 0.24, 1.1), rotation=(90, 0, 0))
        # Inner Red Juicy Core
        self.pulp = Entity(parent=self, model=Cylinder(resolution=14), color=col, scale=(0.92, 0.26, 0.92), rotation=(90, 0, 0))
        # Black Seed Spheres
        for sx, sy in [(-0.25, 0.1), (0.25, 0.1), (0.0, -0.2)]:
            Entity(parent=self, model='sphere', color=color.rgb32(20, 20, 25), scale=(0.1, 0.1, 0.1), position=(sx, sy, 0.14))


class Cherries(BaseItem):
    """7. Twin Cherries: +35 Score, +2 Length, +2 Quota."""
    def __init__(self, position=Vec3(0, 0.5, 0)):
        col = color.rgb32(215, 20, 45)
        super().__init__(item_type="cherries", position=position, item_color=col)
        self.points = 35
        self.growth = 2
        self.quota_value = 2
        self.food_name = "Стиглі Вишні"
        
        # Left & Right Berry
        self.berry_l = Entity(parent=self, model='sphere', color=col, scale=(0.55, 0.55, 0.55), position=(-0.25, -0.1, 0))
        self.berry_r = Entity(parent=self, model='sphere', color=col, scale=(0.55, 0.55, 0.55), position=(0.25, -0.1, 0))
        # Arched Stems
        self.stem_l = Entity(parent=self, model=Cylinder(resolution=6), color=color.rgb32(80, 150, 40), scale=(0.06, 0.65, 0.06), position=(-0.12, 0.25, 0), rotation=(0, 0, 22))
        self.stem_r = Entity(parent=self, model=Cylinder(resolution=6), color=color.rgb32(80, 150, 40), scale=(0.06, 0.65, 0.06), position=(0.12, 0.25, 0), rotation=(0, 0, -22))
        # Joint Leaf
        self.leaf = Entity(parent=self, model='quad', color=color.rgb32(40, 185, 50), scale=(0.28, 0.16), position=(0, 0.55, 0), rotation=(0, 30, 15), double_sided=True)


class Pineapple(BaseItem):
    """8. Tropical Pineapple: +45 Score, +2 Length, +3 Quota."""
    def __init__(self, position=Vec3(0, 0.5, 0)):
        col = color.rgb32(225, 155, 20)
        super().__init__(item_type="pineapple", position=position, item_color=col)
        self.points = 45
        self.growth = 2
        self.quota_value = 3
        self.food_name = "Ананас"
        
        # Golden textured cylindrical body
        self.body = Entity(parent=self, model=Cylinder(resolution=12), color=col, scale=(0.82, 1.15, 0.82), position=(0, 0.1, 0))
        # Green spiky leaf crown
        for i in range(6):
            ang = i * 60
            rad = math.radians(ang)
            Entity(parent=self, model=Cone(resolution=4), color=color.rgb32(35, 175, 50), scale=(0.24, 0.65, 0.24), position=(math.sin(rad) * 0.22, 0.85, math.cos(rad) * 0.22), rotation=(-25, ang, 0))


class Starfruit(BaseItem):
    """9. Golden Starfruit: +50 Score, +2 Length, +4 Quota."""
    def __init__(self, position=Vec3(0, 0.5, 0)):
        col = color.rgb32(255, 225, 40)
        super().__init__(item_type="starfruit", position=position, item_color=col)
        self.points = 50
        self.growth = 2
        self.quota_value = 4
        self.food_name = "Зоряний Фрукт"
        
        # Central glowing star node
        self.core = Entity(parent=self, model='cube', color=col, scale=(0.55, 0.55, 0.55), rotation=(45, 45, 45))
        for i in range(5):
            ang = i * 72
            rad = math.radians(ang)
            Entity(parent=self, model=Cone(resolution=4), color=color.rgb32(255, 240, 80), scale=(0.3, 0.65, 0.3), position=(math.sin(rad) * 0.35, 0, math.cos(rad) * 0.35), rotation=(0, 0, -ang + 90))
        # Sparkling halo ring
        self.halo = Entity(parent=self, model='cube', color=color.rgba32(255, 255, 160, 180), scale=(1.25, 0.06, 1.25), rotation=(30, 0, 30))

    def update_animation(self, dt):
        super().update_animation(dt)
        self.halo.rotation_y += dt * 180.0


class GoldenApple(BaseItem):
    """10. Golden Apple: +60 Score, +3 Length, +5 Quota."""
    def __init__(self, position=Vec3(0, 0.5, 0)):
        super().__init__(item_type="golden", position=position, item_color=config.COLOR_APPLE_GOLDEN)
        self.lifespan = 22.0
        self.points = 60
        self.growth = 3
        self.quota_value = 5
        self.food_name = "Золоте Яблуко"
        
        self.body = Entity(parent=self, model='sphere', color=config.COLOR_APPLE_GOLDEN, scale=(1.05, 1.05, 1.05))
        self.stem = Entity(parent=self, model=Cylinder(resolution=6), color=color.rgb32(150, 100, 20), scale=(0.12, 0.42, 0.12), position=(0, 0.55, 0))
        self.halo = Entity(parent=self, model='cube', color=color.rgba32(255, 255, 180, 180), scale=(1.35, 0.08, 1.35), rotation=(35, 0, 35))

    def update_animation(self, dt):
        super().update_animation(dt)
        self.halo.rotation_y += dt * 160.0


# ================= POWER-UP ITEMS =================

class PowerupItem(BaseItem):
    """
    Power-up Items:
    - 'speed': +25% Speed Boost for 10s (Orange Diamond)
    - 'slow': -25% Slow Motion for 10s (Ice Cyan Snowflake)
    - 'magnet': Food Magnet for 10s (Purple Horseshoe Ring)
    - 'shield': Invincible Shield for 12s (Cyan Shield Orb)
    - 'life': +1 Life Heart / 1-Up (Crimson Heart)
    - 'mega_food': +10 Food Feast (+100 Score, +10 Apples, +3 Length) (Golden Watermelon)
    """
    def __init__(self, item_type="speed", position=Vec3(0, 0.5, 0)):
        col_map = {
            "speed": config.COLOR_POWERUP_SPEED,
            "slow": config.COLOR_POWERUP_SLOW,
            "magnet": config.COLOR_POWERUP_MAGNET,
            "shield": config.COLOR_POWERUP_SHIELD,
            "life": config.COLOR_POWERUP_LIFE,
            "mega_food": config.COLOR_POWERUP_MEGA_FOOD
        }
        col = col_map.get(item_type, config.COLOR_POWERUP_SPEED)
        super().__init__(item_type=item_type, position=position, item_color=col)
        self.lifespan = 18.0
        self.points = 25
        self.growth = 0
        self.quota_value = 0

        if item_type == "speed":
            self.food_name = "Турбо-Прискорення"
            self.mesh_obj = Entity(parent=self, model='cube', color=col, scale=(0.7, 0.95, 0.7), rotation=(45, 45, 45))
            Entity(parent=self.mesh_obj, model='cube', color=color.rgb32(255, 240, 80), scale=(0.3, 0.7, 0.1), position=(-0.45, 0, 0))
            Entity(parent=self.mesh_obj, model='cube', color=color.rgb32(255, 240, 80), scale=(0.3, 0.7, 0.1), position=(0.45, 0, 0))

        elif item_type == "slow":
            self.food_name = "Сповільнення Часу"
            self.mesh_obj = Entity(parent=self, model='cube', color=col, scale=(0.65, 0.65, 0.65), rotation=(45, 45, 45))
            Entity(parent=self, model='cube', color=color.rgb32(220, 255, 255), scale=(1.2, 0.18, 0.18), rotation=(0, 45, 0))
            Entity(parent=self, model='cube', color=color.rgb32(220, 255, 255), scale=(0.18, 1.2, 0.18), rotation=(0, 45, 0))

        elif item_type == "magnet":
            self.food_name = "Магніт для Їжі"
            self.mesh_obj = Entity(parent=self, model='sphere', color=col, scale=(0.75, 0.75, 0.75))
            Entity(parent=self, model=Cylinder(resolution=14), color=color.rgb32(255, 255, 255), scale=(0.95, 0.14, 0.95))

        elif item_type == "shield":
            self.food_name = "Захисний Щит"
            self.mesh_obj = Entity(parent=self, model='sphere', color=color.rgba32(0, 220, 255, 210), scale=(0.85, 0.85, 0.85))
            self.orbit_ring = Entity(parent=self, model='cube', color=color.rgb32(255, 255, 255), scale=(1.15, 0.08, 1.15), rotation=(25, 0, 25))

        elif item_type == "life":
            self.food_name = "+1 Життя"
            self.mesh_obj = Entity(parent=self, model='sphere', color=col, scale=(0.85, 0.85, 0.85))
            Entity(parent=self.mesh_obj, model='sphere', color=color.rgb32(255, 75, 110), scale=(0.6, 0.6, 0.6), position=(-0.25, 0.25, 0))
            Entity(parent=self.mesh_obj, model='sphere', color=color.rgb32(255, 75, 110), scale=(0.6, 0.6, 0.6), position=(0.25, 0.25, 0))
            self.orbit_ring = Entity(parent=self, model='cube', color=color.rgb32(255, 220, 150), scale=(1.2, 0.07, 1.2), rotation=(35, 0, 35))

        elif item_type == "mega_food":
            self.food_name = "Мега-Кавун (+10 Їжі)"
            self.points = 100
            self.growth = 3
            self.quota_value = 10
            self.mesh_obj = Entity(parent=self, model='sphere', color=col, scale=(1.1, 1.1, 1.1))
            Entity(parent=self.mesh_obj, model=Cylinder(resolution=12), color=color.rgb32(40, 180, 50), scale=(1.03, 0.2, 1.03), position=(0, 0, 0))
            Entity(parent=self.mesh_obj, model=Cylinder(resolution=12), color=color.rgb32(40, 180, 50), scale=(0.8, 0.18, 0.8), position=(0, 0.35, 0))
            self.star_node = Entity(parent=self, model='cube', color=color.rgb32(255, 255, 100), scale=(0.4, 0.4, 0.4), position=(0, 0.65, 0), rotation=(45, 45, 45))

    def update_animation(self, dt):
        super().update_animation(dt)
        if hasattr(self, 'orbit_ring') and self.orbit_ring:
            self.orbit_ring.rotation_y += dt * 140.0
        if hasattr(self, 'star_node') and self.star_node:
            self.star_node.rotation_y += dt * 180.0


# ================= ITEM MANAGER =================

class ItemManager:
    """Manages spawning, updating, and collecting diverse food and power-ups for player and AI opponents."""
    def __init__(self, arena_size=(36, 36)):
        self.arena_size = arena_size
        self.items = []
        self.particle_bursts = []
        
        self.golden_spawn_timer = random.uniform(12.0, 18.0)
        self.powerup_spawn_timer = random.uniform(10.0, 18.0)
        
    def set_arena_size(self, arena_size):
        self.arena_size = arena_size

    def add_burst(self, position, tint_color, count=7):
        """Spawns a particle burst with a cap on active bursts to prevent frame drops."""
        if len(self.particle_bursts) >= 4:
            oldest = self.particle_bursts.pop(0)
            oldest.destroy_all()
        self.particle_bursts.append(ParticleBurst(position, tint_color, count))

    def clear(self):
        """Removes all active items and particles cleanly."""
        for item in self.items:
            destroy(item)
        self.items.clear()
        
        for burst in self.particle_bursts:
            burst.destroy_all()
        self.particle_bursts.clear()

    def get_valid_spawn_pos(self, obstacles, snake, min_dist_from_snake=4.0):
        """Finds an unobstructed random position on the arena floor."""
        half_w = (self.arena_size[0] / 2.0) - 2.5
        half_h = (self.arena_size[1] / 2.0) - 2.5

        for _ in range(50):
            x = random.uniform(-half_w, half_w)
            z = random.uniform(-half_h, half_h)
            pos = Vec3(x, 0.5, z)

            # Check distance from snake head
            if snake and math.hypot(x - snake.head.x, z - snake.head.z) < min_dist_from_snake:
                continue

            # Check distance from obstacles (2D X-Z)
            collision = False
            for obs in obstacles:
                obs_radius = getattr(obs, 'collision_radius', 1.2)
                if math.hypot(x - obs.x, z - obs.z) < (obs_radius + 1.4):
                    collision = True
                    break
            if collision:
                continue

            # Check distance from other items (2D X-Z)
            for it in self.items:
                if math.hypot(x - it.x, z - it.z) < 2.0:
                    collision = True
                    break
            if collision:
                continue

            return pos

        return Vec3(random.uniform(-half_w, half_w), 0.5, random.uniform(-half_h, half_h))

    def spawn_food(self, obstacles, snake):
        """Spawns a random diverse fruit/food item based on weighted probability."""
        pos = self.get_valid_spawn_pos(obstacles, snake)
        food_classes = [
            (Apple, 22),
            (Pear, 15),
            (Banana, 14),
            (Orange, 13),
            (Strawberry, 11),
            (Watermelon, 9),
            (Cherries, 7),
            (Pineapple, 5),
            (Starfruit, 4)
        ]
        classes, weights = zip(*food_classes)
        chosen_cls = random.choices(classes, weights=weights, k=1)[0]
        item = chosen_cls(position=pos)
        self.items.append(item)
        return item

    def spawn_apple(self, obstacles, snake):
        """Alias for spawn_food to maintain compatibility."""
        return self.spawn_food(obstacles, snake)

    def spawn_golden_apple(self, obstacles, snake):
        pos = self.get_valid_spawn_pos(obstacles, snake)
        g_apple = GoldenApple(position=pos)
        self.items.append(g_apple)
        return g_apple

    def spawn_random_powerup(self, obstacles, snake):
        types = ["speed", "slow", "magnet", "shield", "life", "mega_food"]
        weights = [20, 18, 18, 16, 16, 12]
        choice = random.choices(types, weights=weights, k=1)[0]
        pos = self.get_valid_spawn_pos(obstacles, snake)
        pw = PowerupItem(item_type=choice, position=pos)
        self.items.append(pw)
        return pw

    def spawn_severed_tail_loot(self, positions):
        """Spawns particle bursts and dropped loot food at severed segment locations."""
        step = max(1, len(positions) // 3)
        for i, pos in enumerate(positions):
            if i % step == 0:
                self.add_burst(pos, config.COLOR_SNAKE_BODY_1, count=8)
            if random.random() < 0.60:
                food = self.spawn_food([], None)
                food.position = Vec3(pos.x, 0.5, pos.z)
                food.base_y = 0.5

    def update(self, dt, obstacles, snake, audio_mgr, enemies=None):
        """Updates all items, handles timers, magnet pulling, and collisions for player and enemies."""
        # 1. Update particle bursts
        alive_bursts = []
        for burst in self.particle_bursts:
            burst.update(dt)
            if not burst.is_finished:
                alive_bursts.append(burst)
        self.particle_bursts = alive_bursts

        # 2. Spawning timers
        self.golden_spawn_timer -= dt
        if self.golden_spawn_timer <= 0:
            if not any(it.item_type == "golden" for it in self.items):
                self.spawn_golden_apple(obstacles, snake)
            self.golden_spawn_timer = random.uniform(14.0, 22.0)

        self.powerup_spawn_timer -= dt
        if self.powerup_spawn_timer <= 0:
            active_powerups = sum(1 for it in self.items if it.item_type in ["speed", "slow", "magnet", "shield", "life", "mega_food"])
            if active_powerups < 2:
                self.spawn_random_powerup(obstacles, snake)
            self.powerup_spawn_timer = random.uniform(12.0, 20.0)

        # 3. Update active items
        alive_items = []
        collected_events = []

        is_player_magnet = snake and snake.magnet_timer > 0

        for item in self.items:
            item.update_animation(dt)

            if item.lifespan > 0:
                item.lifespan -= dt
                if item.lifespan <= 0:
                    destroy(item)
                    continue
            elif item.lifespan == 0:
                destroy(item)
                continue

            # Player Magnet suction effect (2D plane pull)
            if is_player_magnet and snake and snake.is_alive:
                dx = snake.head.x - item.x
                dz = snake.head.z - item.z
                dist_2d = math.hypot(dx, dz)
                if dist_2d < config.MAGNET_RADIUS and dist_2d > 0.05:
                    pull_speed = max(18.0, (config.MAGNET_RADIUS - dist_2d) * 2.8 + 14.0)
                    inv_d = 1.0 / dist_2d
                    item.x += dx * inv_d * (pull_speed * dt)
                    item.z += dz * inv_d * (pull_speed * dt)

            # Enemy Magnet suction effect
            if enemies:
                for enemy in enemies:
                    if enemy.is_alive and getattr(enemy, 'magnet_timer', 0) > 0:
                        edx = enemy.head.x - item.x
                        edz = enemy.head.z - item.z
                        e_dist_2d = math.hypot(edx, edz)
                        if e_dist_2d < config.MAGNET_RADIUS and e_dist_2d > 0.05:
                            pull_speed = max(16.0, (config.MAGNET_RADIUS - e_dist_2d) * 2.5 + 12.0)
                            inv_d = 1.0 / e_dist_2d
                            item.x += edx * inv_d * (pull_speed * dt)
                            item.z += edz * inv_d * (pull_speed * dt)

            item_consumed = False

            # Check collision with PLAYER snake head
            if snake and snake.is_alive:
                dist_2d = math.hypot(snake.head.x - item.x, snake.head.z - item.z)
                pickup_radius = config.HEAD_RADIUS + (1.3 if is_player_magnet else 0.65)

                if dist_2d < pickup_radius:
                    item_type = item.item_type
                    self.add_burst(item.position, item.color_tint)

                    is_powerup = item_type in ["speed", "slow", "magnet", "shield", "life", "mega_food"]
                    
                    if is_powerup:
                        if item_type == "mega_food":
                            audio_mgr.play_golden()
                            snake.activate_powerup("mega_food")
                        else:
                            audio_mgr.play_powerup()
                            snake.activate_powerup(item_type)
                    else:
                        # Standard food / fruits
                        if item_type == "golden":
                            audio_mgr.play_golden()
                            snake.activate_powerup("golden")
                        else:
                            audio_mgr.play_eat()
                        
                        growth = getattr(item, 'growth', 1)
                        snake.grow(growth)

                    collected_events.append({
                        "type": item_type,
                        "points": getattr(item, 'points', 10),
                        "growth": getattr(item, 'growth', 1),
                        "quota": getattr(item, 'quota_value', 1),
                        "name": getattr(item, 'food_name', item_type)
                    })
                    destroy(item)
                    item_consumed = True

            # Check collision with AI ENEMY snakes
            if not item_consumed and enemies:
                for enemy in enemies:
                    if not enemy.is_alive:
                        continue
                    e_dist = math.hypot(enemy.head.x - item.x, enemy.head.z - item.z)
                    e_pickup_radius = config.HEAD_RADIUS + 0.65

                    if e_dist < e_pickup_radius:
                        item_type = item.item_type
                        self.add_burst(item.position, item.color_tint)

                        growth = getattr(item, 'growth', 1)
                        if item_type in ["speed", "slow", "magnet", "shield"]:
                            if item_type == "speed": enemy.speed_timer = config.DURATION_SPEED_BOOST
                            elif item_type == "slow": enemy.slow_timer = config.DURATION_SLOW_MOTION
                            elif item_type == "magnet": enemy.magnet_timer = config.DURATION_MAGNET
                            elif item_type == "shield": enemy.shield_timer = config.DURATION_SHIELD
                        else:
                            enemy.grow(growth)

                        audio_mgr.play_eat()
                        destroy(item)
                        item_consumed = True
                        break

            if not item_consumed:
                alive_items.append(item)

        self.items = alive_items

        # Ensure active dynamic food population on arena (DOUBLED: 5 to 8 food items concurrently)
        desired_food = max(5, int(self.arena_size[0] / 8.5))
        food_count = sum(1 for it in self.items if it.item_type not in ["speed", "slow", "magnet", "shield", "life"])
        while food_count < desired_food:
            self.spawn_food(obstacles, snake)
            food_count += 1

        return collected_events
