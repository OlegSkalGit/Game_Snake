"""
AI Opponents and Enemies for 3D Snake.
Autonomous enemy snakes with advanced multi-ray whisker sensors, 2D obstacle avoidance,
apple and bonus power-up hunting, dynamic growth, and loot drops.
"""
import random
import math
from ursina import Entity, Vec3, color, time, destroy, lerp
import config
from items import ParticleBurst

class EnemySnake:
    def __init__(self, start_pos, start_rot_y=0.0, length=7, speed=config.ENEMY_DEFAULT_SPEED):
        self.is_alive = True
        self.base_speed = speed
        self.speed = speed
        self.length = length
        self.turn_speed = config.ENEMY_TURN_SPEED * 1.15
        self.elapsed_time = random.uniform(0, 10.0)
        
        # Power-up timers
        self.speed_timer = 0.0
        self.slow_timer = 0.0
        self.shield_timer = 0.0
        self.magnet_timer = 0.0

        # Heading and position history
        self.trail = []
        self.total_distance = 0.0
        self.last_pos = Vec3(start_pos)
        
        # AI decision variables
        self.current_turn = 0.0
        self.wander_timer = 0.0
        self.wander_target_turn = 0.0
        
        # 3D Visuals
        self.segments = []
        self.build_head(start_pos, start_rot_y)
        self.build_body()

    def build_head(self, start_pos, start_rot_y):
        self.head = Entity(
            model='sphere',
            texture='textures/enemy_scales.png',
            color=color.rgb32(255, 230, 230),
            scale=(config.HEAD_RADIUS * 1.85, config.HEAD_RADIUS * 1.45, config.HEAD_RADIUS * 2.2),
            position=start_pos,
            rotation=(0, start_rot_y, 0)
        )
        # Evil Eyes
        self.eye_l = Entity(parent=self.head, model='sphere', color=config.COLOR_ENEMY_EYES, scale=(0.28, 0.28, 0.28), position=(-0.35, 0.3, 0.25))
        self.pupil_l = Entity(parent=self.eye_l, model='cube', color=config.COLOR_ENEMY_PUPILS, scale=(0.3, 0.7, 0.3), position=(0, 0, 0.35))
        
        self.eye_r = Entity(parent=self.head, model='sphere', color=config.COLOR_ENEMY_EYES, scale=(0.28, 0.28, 0.28), position=(0.35, 0.3, 0.25))
        self.pupil_r = Entity(parent=self.eye_r, model='cube', color=config.COLOR_ENEMY_PUPILS, scale=(0.3, 0.7, 0.3), position=(0, 0, 0.35))

        # Shield Aura
        self.shield_aura = Entity(
            parent=self.head,
            model='sphere',
            color=color.rgba32(255, 60, 60, 110),
            scale=(2.4, 2.4, 2.4),
            visible=False
        )

        # Seed initial trail
        for d in range(80):
            dist_back = d * 0.1
            rad = math.radians(start_rot_y)
            back_dir = Vec3(-math.sin(rad), 0, -math.cos(rad))
            pos = start_pos + back_dir * dist_back
            self.trail.append((pos, start_rot_y, 0.0, -dist_back))
        self.trail.reverse()
        self.total_distance = 0.0

    def build_body(self):
        for i in range(self.length):
            self.add_segment(i)

    def add_segment(self, idx):
        factor = (idx % 4) / 3.0
        seg_color = lerp(config.COLOR_ENEMY_BODY_1, config.COLOR_ENEMY_BODY_2, factor)
        
        target_dist = self.total_distance - (idx + 1) * config.SEGMENT_DISTANCE
        init_pos, init_rot_y, init_rot_z = self.sample_trail(target_dist)
        
        t = idx / max(1, self.length - 1)
        scale_mult = lerp(1.0, config.TAIL_MIN_SCALE, t)
        r = config.SEGMENT_RADIUS * 2.0 * scale_mult

        seg = Entity(
            model='sphere',
            texture='textures/enemy_scales.png',
            color=seg_color,
            scale=(r, r * 0.9, r),
            position=init_pos,
            rotation=(0, init_rot_y, init_rot_z * 0.7)
        )
        self.segments.append(seg)

    def grow(self, amount=1):
        """Adds segments to the enemy snake when eating food."""
        self.length += amount
        for _ in range(amount):
            self.add_segment(len(self.segments))
        self.update_segment_scales()

    def cut_tail(self, hit_index):
        """
        Severes the enemy snake's tail starting from hit_index to the end.
        Returns a list of Vec3 positions of the severed segments (for loot dropping and particles).
        Keeps at least 2 segments. If cutoff <= 2, caller should destroy the enemy completely.
        """
        cutoff = max(2, hit_index)
        if cutoff >= len(self.segments):
            return []

        severed = self.segments[cutoff:]
        self.segments = self.segments[:cutoff]
        self.length = len(self.segments)

        severed_positions = []
        for seg in severed:
            severed_positions.append(Vec3(seg.position))
            destroy(seg)

        self.update_segment_scales()
        return severed_positions

    def update_segment_scales(self):
        num = len(self.segments)
        if num == 0:
            return
        for i, seg in enumerate(self.segments):
            t = i / max(1, num - 1)
            scale_mult = lerp(1.0, config.TAIL_MIN_SCALE, t)
            r = config.SEGMENT_RADIUS * 2.0 * scale_mult
            seg.scale = (r, r * 0.9, r)

    def sample_trail(self, target_dist):
        if not self.trail:
            return self.head.position, self.head.rotation_y, 0.0

        if target_dist <= self.trail[0][3]:
            return self.trail[0][0], self.trail[0][1], self.trail[0][2]

        if target_dist >= self.trail[-1][3]:
            return self.trail[-1][0], self.trail[-1][1], self.trail[-1][2]

        low = 0
        high = len(self.trail) - 1
        while low <= high:
            mid = (low + high) // 2
            if self.trail[mid][3] < target_dist:
                low = mid + 1
            else:
                high = mid - 1

        idx2 = max(1, min(low, len(self.trail) - 1))
        idx1 = idx2 - 1

        p1, r1, z1, d1 = self.trail[idx1]
        p2, r2, z2, d2 = self.trail[idx2]

        denom = d2 - d1
        alpha = 0.0 if denom <= 0.0001 else (target_dist - d1) / denom
        alpha = max(0.0, min(1.0, alpha))

        interp_pos = lerp(p1, p2, alpha)
        interp_y = lerp(r1, r2, alpha)
        interp_z = lerp(z1, z2, alpha)
        return interp_pos, interp_y, interp_z

    def update_ai(self, dt, arena_size, obstacles, items, player_snake):
        """
        Advanced Multi-Ray Whisker Sensory System with Food & Bonus Seeking.
        """
        if not self.is_alive:
            return

        self.elapsed_time += dt

        # Powerup timers
        if self.speed_timer > 0:
            self.speed_timer -= dt
        if self.slow_timer > 0:
            self.slow_timer -= dt
        if self.shield_timer > 0:
            self.shield_timer -= dt
            self.shield_aura.visible = True
            pulse = 1.0 + 0.08 * math.sin(self.elapsed_time * 8.0)
            self.shield_aura.scale = Vec3(2.4, 2.4, 2.4) * pulse
        else:
            self.shield_aura.visible = False

        if self.magnet_timer > 0:
            self.magnet_timer -= dt

        # Speed calculation
        cur_speed = self.base_speed
        if self.speed_timer > 0:
            cur_speed *= config.SPEED_BOOST_FACTOR
        if self.slow_timer > 0:
            cur_speed *= config.SLOW_MOTION_FACTOR
        self.speed = cur_speed

        hx = self.head.x
        hz = self.head.z
        rot_y = self.head.rotation_y

        half_w = (arena_size[0] / 2.0) - 1.2
        half_h = (arena_size[1] / 2.0) - 1.2

        # 5 Whisker Angles: [-65°, -32°, 0°, +32°, +65°]
        whisker_angles = [-65.0, -32.0, 0.0, 32.0, 65.0]
        whisker_scores = [100.0] * 5
        ray_length = 7.5

        for i, rel_angle in enumerate(whisker_angles):
            ray_deg = rot_y + rel_angle
            rad = math.radians(ray_deg)
            dir_x = math.sin(rad)
            dir_z = math.cos(rad)

            # Check 6 step points along ray
            for step_idx in range(1, 7):
                dist = (step_idx / 6.0) * ray_length
                sample_x = hx + dir_x * dist
                sample_z = hz + dir_z * dist

                # Wall proximity
                if abs(sample_x) >= half_w or abs(sample_z) >= half_h:
                    score = (dist / ray_length) * 100.0
                    if score < whisker_scores[i]:
                        whisker_scores[i] = score
                    break

                # 2D Obstacle proximity
                hit_obs = False
                for obs in obstacles:
                    obs_r = getattr(obs, 'collision_radius', 1.2)
                    if math.hypot(sample_x - obs.x, sample_z - obs.z) < (obs_r + 0.75):
                        score = (dist / ray_length) * 100.0
                        if score < whisker_scores[i]:
                            whisker_scores[i] = score
                        hit_obs = True
                        break
                if hit_obs:
                    break

                # Player body proximity
                if player_snake and player_snake.is_alive:
                    hit_player = False
                    for p_seg in player_snake.segments:
                        if math.hypot(sample_x - p_seg.x, sample_z - p_seg.z) < 1.1:
                            score = (dist / ray_length) * 100.0
                            if score < whisker_scores[i]:
                                whisker_scores[i] = score
                            hit_player = True
                            break
                    if hit_player:
                        break

        left_clearance = min(whisker_scores[0], whisker_scores[1])
        right_clearance = min(whisker_scores[3], whisker_scores[4])
        forward_clearance = whisker_scores[2]

        target_turn = 0.0

        # Urgent Obstacle Avoidance Trigger
        if forward_clearance < 75.0 or whisker_scores[1] < 60.0 or whisker_scores[3] < 60.0:
            if left_clearance > right_clearance:
                target_turn = -1.0
            elif right_clearance > left_clearance:
                target_turn = 1.0
            else:
                angle_to_center = math.degrees(math.atan2(-hx, -hz))
                diff = (angle_to_center - rot_y + 180) % 360 - 180
                target_turn = 1.0 if diff > 0 else -1.0
        else:
            # Clear path ahead: Hunt for food/power-ups or wander
            closest_item = None
            closest_dist = config.ENEMY_DETECTION_DIST
            for it in items:
                d = math.hypot(hx - it.x, hz - it.z)
                if d < closest_dist:
                    closest_dist = d
                    closest_item = it

            if closest_item:
                dx = closest_item.x - hx
                dz = closest_item.z - hz
                angle_to_item = math.degrees(math.atan2(dx, dz))
                diff = (angle_to_item - rot_y + 180) % 360 - 180
                desired_turn = max(-1.0, min(1.0, diff / 32.0))
                
                if desired_turn < 0 and left_clearance > 50.0:
                    target_turn = desired_turn
                elif desired_turn > 0 and right_clearance > 50.0:
                    target_turn = desired_turn
                else:
                    target_turn = 0.0
            else:
                self.wander_timer -= dt
                if self.wander_timer <= 0:
                    self.wander_target_turn = random.uniform(-0.55, 0.55)
                    self.wander_timer = random.uniform(1.0, 2.2)
                target_turn = self.wander_target_turn

        # Smooth turn interpolation
        self.current_turn = lerp(self.current_turn, target_turn, dt * 7.5)
        self.head.rotation_y += self.current_turn * self.turn_speed * dt
        self.head.rotation_z = lerp(self.head.rotation_z, -self.current_turn * 16.0, dt * 6.0)

        # Forward movement
        rad_now = math.radians(self.head.rotation_y)
        forward = Vec3(math.sin(rad_now), 0, math.cos(rad_now))
        self.head.position += forward * (self.speed * dt)

        # Record trail
        dist_moved = (self.head.position - self.last_pos).length()
        if dist_moved >= 0.04:
            self.total_distance += dist_moved
            self.trail.append((Vec3(self.head.position), self.head.rotation_y, self.head.rotation_z, self.total_distance))
            self.last_pos = Vec3(self.head.position)
            
            # Prune old trail points with fast slice rather than O(N) pop(0)
            max_needed = (len(self.segments) + 2) * config.SEGMENT_DISTANCE
            cutoff_d = self.total_distance - (max_needed + 4.0)
            cut_idx = 0
            limit = len(self.trail) - 4
            while cut_idx < limit and self.trail[cut_idx][3] < cutoff_d:
                cut_idx += 1
            if cut_idx > 0:
                self.trail = self.trail[cut_idx:]

        # Update body segments with natural serpentine wave undulation
        for i, seg in enumerate(self.segments):
            target_d = self.total_distance - (i + 1) * config.SEGMENT_DISTANCE
            pos, r_y, r_z = self.sample_trail(target_d)

            rad_y = math.radians(r_y)
            right = Vec3(math.cos(rad_y), 0, -math.sin(rad_y))
            ramp = min(1.0, (i + 1) / 4.0)
            wave_phase = (self.total_distance * 1.75) - (i * 0.52)
            lateral_offset = math.sin(wave_phase) * (0.24 * ramp)
            yaw_tilt = math.cos(wave_phase) * (13.5 * ramp)
            roll_tilt = math.sin(wave_phase) * (4.5 * ramp)

            seg.position = pos + right * lateral_offset
            seg.rotation_y = r_y + yaw_tilt
            seg.rotation_z = (r_z + roll_tilt) * 0.7

    def destroy_entities(self):
        for seg in self.segments:
            destroy(seg)
        self.segments.clear()
        if self.head:
            if hasattr(self.head, 'children'):
                for child in list(self.head.children):
                    destroy(child)
            destroy(self.head)
            self.head = None


class EnemyManager:
    """Manages spawning, updating AI, and collisions for all enemies on the level."""
    def __init__(self):
        self.enemies = []
        self.spawn_cooldown = 0.0

    def clear(self):
        for e in self.enemies:
            e.destroy_entities()
        self.enemies.clear()

    def spawn_enemy(self, arena_size, obstacles, player_snake):
        """Spawns an enemy at a safe distance from player and obstacles."""
        hw = (arena_size[0] / 2.0) - 5.0
        hh = (arena_size[1] / 2.0) - 5.0

        for _ in range(40):
            x = random.uniform(-hw, hw)
            z = random.uniform(-hh, hh)
            if player_snake and math.hypot(x - player_snake.head.x, z - player_snake.head.z) < 14.0:
                continue
            
            collides_obs = False
            for obs in obstacles:
                obs_r = getattr(obs, 'collision_radius', 1.2)
                if math.hypot(x - obs.x, z - obs.z) < (obs_r + 2.0):
                    collides_obs = True
                    break
            if collides_obs:
                continue

            rot = random.uniform(0, 360)
            enemy = EnemySnake(start_pos=Vec3(x, 0.45, z), start_rot_y=rot)
            self.enemies.append(enemy)
            return enemy
        return None

    def update(self, dt, arena_size, obstacles, items, player_snake):
        """Updates AI for all active enemies and handles enemy death drops."""
        alive_enemies = []
        for e in self.enemies:
            if not e.is_alive:
                e.destroy_entities()
                continue
            
            e.update_ai(dt, arena_size, obstacles, items, player_snake)
            alive_enemies.append(e)

        self.enemies = alive_enemies

    def check_enemy_obstacle_collisions(self, obstacles, arena_size, item_mgr, audio_mgr):
        """Destroys enemies that crash into arena walls or obstacles, dropping loot."""
        hw = (arena_size[0] / 2.0) - 0.4
        hh = (arena_size[1] / 2.0) - 0.4

        for e in self.enemies:
            if not e.is_alive:
                continue
            
            # Wall crash
            if abs(e.head.x) >= hw or abs(e.head.z) >= hh:
                if e.shield_timer > 0:
                    e.shield_timer = 0.0
                    e.shield_aura.visible = False
                    e.head.x = max(-hw + 1.0, min(hw - 1.0, e.head.x))
                    e.head.z = max(-hh + 1.0, min(hh - 1.0, e.head.z))
                else:
                    self.kill_enemy(e, item_mgr, audio_mgr)
                continue

            # Obstacle crash (2D X-Z distance)
            for obs in obstacles:
                obs_r = getattr(obs, 'collision_radius', 1.2)
                if math.hypot(e.head.x - obs.x, e.head.z - obs.z) < (obs_r + config.HEAD_RADIUS * 0.75):
                    if e.shield_timer > 0:
                        e.shield_timer = 0.0
                        e.shield_aura.visible = False
                    else:
                        self.kill_enemy(e, item_mgr, audio_mgr)
                    break

    def check_player_collision(self, player_snake):
        """
        Checks detailed collision between player and active enemies:
        Returns a dict:
        - "type": "head_on" (both heads collided)
        - "type": "bite_enemy" (player head bit enemy body at segment_idx)
        - "type": "enemy_bite_player" (enemy head bit player body at segment_idx)
        """
        if not player_snake or not player_snake.is_alive:
            return None

        phx = player_snake.head.x
        phz = player_snake.head.z
        head_thresh = config.HEAD_RADIUS * 2.0 * 0.85
        body_thresh = (config.HEAD_RADIUS + config.SEGMENT_RADIUS) * 0.78

        for enemy in self.enemies:
            if not enemy.is_alive:
                continue

            ehx = enemy.head.x
            ehz = enemy.head.z

            # 1. Head-on collision
            if math.hypot(phx - ehx, phz - ehz) < head_thresh:
                return {
                    "enemy": enemy,
                    "type": "head_on",
                    "segment_idx": 0
                }

            # 2. Player head biting enemy body/tail
            for idx, seg in enumerate(enemy.segments):
                if math.hypot(phx - seg.x, phz - seg.z) < body_thresh:
                    return {
                        "enemy": enemy,
                        "type": "bite_enemy",
                        "segment_idx": idx
                    }

            # 3. Enemy head biting player body/tail
            for p_idx, p_seg in enumerate(player_snake.segments):
                if math.hypot(ehx - p_seg.x, ehz - p_seg.z) < body_thresh:
                    return {
                        "enemy": enemy,
                        "type": "enemy_bite_player",
                        "segment_idx": p_idx
                    }

        return None

    def kill_enemy(self, enemy, item_mgr, audio_mgr):
        """Kills an enemy snake, creating explosive particles and dropping bonus loot."""
        enemy.is_alive = False
        audio_mgr.play_enemy_hit()
        
        # Spawn loot from enemy body segments
        severed_positions = [Vec3(enemy.head.position)] + [Vec3(s.position) for s in enemy.segments]
        item_mgr.spawn_severed_tail_loot(severed_positions)
        enemy.destroy_entities()
