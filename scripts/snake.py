"""
Snake Entity and Physics for 3D Snake.
Handles continuous steering, smooth spline/trail body following, detailed reptilian textures,
power-up states, and tail-biting / severance mechanics.
"""
import math
from ursina import Entity, Vec3, color, time, destroy, lerp
import config

class Snake:
    def __init__(self, start_pos=Vec3(0, 0.45, 0), start_rot_y=0.0):
        self.initial_pos = start_pos
        self.initial_rot_y = start_rot_y
        
        # State
        self.speed = config.DEFAULT_SPEED
        self.base_speed = config.DEFAULT_SPEED
        self.is_boosting = False
        self.boost_energy = config.BOOST_MAX_ENERGY
        self.is_alive = True
        
        # Power-ups
        self.shield_timer = 0.0
        self.magnet_timer = 0.0
        self.speed_timer = 0.0
        self.slow_timer = 0.0
        self.elapsed_time = 0.0
        
        # Trail history: list of tuples (Vec3 pos, rot_y, rot_z, cumulative_dist)
        self.trail = []
        self.total_distance = 0.0
        self.last_pos = Vec3(start_pos)
        
        # Segments
        self.segments = []  # Entity list for body
        self.initial_length = 5
        self.target_length = self.initial_length
        
        # Build 3D Visuals
        self.build_head(start_pos, start_rot_y)
        self.build_initial_body()
        
    def build_head(self, start_pos, start_rot_y):
        """Constructs the 3D Snake Head with detailed features and scales texture."""
        self.head = Entity(
            model='sphere',
            texture='textures/snake_scales.png',
            color=color.rgb32(230, 255, 230),
            scale=(config.HEAD_RADIUS * 1.9, config.HEAD_RADIUS * 1.5, config.HEAD_RADIUS * 2.3),
            position=start_pos,
            rotation=(0, start_rot_y, 0)
        )
        
        # Eye Left
        self.eye_l = Entity(
            parent=self.head,
            model='sphere',
            color=config.COLOR_SNAKE_EYES,
            scale=(0.28, 0.28, 0.28),
            position=(-0.35, 0.32, 0.25)
        )
        self.pupil_l = Entity(
            parent=self.eye_l,
            model='sphere',
            color=config.COLOR_SNAKE_PUPILS,
            scale=(0.55, 0.55, 0.55),
            position=(0, 0, 0.35)
        )
        
        # Eye Right
        self.eye_r = Entity(
            parent=self.head,
            model='sphere',
            color=config.COLOR_SNAKE_EYES,
            scale=(0.28, 0.28, 0.28),
            position=(0.35, 0.32, 0.25)
        )
        self.pupil_r = Entity(
            parent=self.eye_r,
            model='sphere',
            color=config.COLOR_SNAKE_PUPILS,
            scale=(0.55, 0.55, 0.55),
            position=(0, 0, 0.35)
        )
        
        # Flickering Tongue
        self.tongue = Entity(
            parent=self.head,
            model='cube',
            color=config.COLOR_SNAKE_TONGUE,
            scale=(0.14, 0.03, 0.5),
            position=(0, -0.05, 0.52)
        )
        
        # Shield Aura (Hidden until active)
        self.shield_aura = Entity(
            parent=self.head,
            model='sphere',
            color=color.rgba32(0, 200, 255, 100),
            scale=(2.4, 2.4, 2.4),
            visible=False
        )
        
        # Magnet Aura (Purple pulsing magnetic field)
        self.magnet_aura = Entity(
            parent=self.head,
            model='sphere',
            color=color.rgba32(180, 50, 255, 95),
            scale=(2.6, 2.6, 2.6),
            visible=False
        )
        self.magnet_ring = Entity(
            parent=self.head,
            model='cube',
            color=color.rgba32(230, 110, 255, 180),
            scale=(2.9, 0.08, 2.9),
            rotation=(25, 0, 25),
            visible=False
        )
        
        # Seed initial trail
        for d in range(100):
            dist_back = d * 0.1
            rad = math.radians(start_rot_y)
            back_dir = Vec3(-math.sin(rad), 0, -math.cos(rad))
            pos = start_pos + back_dir * dist_back
            self.trail.append((pos, start_rot_y, 0.0, -dist_back))
        self.trail.reverse()
        self.total_distance = 0.0

    def build_initial_body(self):
        """Builds the initial body segments."""
        for i in range(self.initial_length):
            self.add_segment()

    def add_segment(self):
        """Instantiates a new 3D body segment with detailed scales texture and gradient."""
        idx = len(self.segments)
        
        # Color gradient
        factor = (idx % 6) / 5.0
        seg_color = lerp(config.COLOR_SNAKE_BODY_1, config.COLOR_SNAKE_BODY_2, factor)
        
        # Position accurately at tail along recorded trail history
        target_dist = self.total_distance - (idx + 1) * config.SEGMENT_DISTANCE
        init_pos, init_rot_y, init_rot_z = self.sample_trail(target_dist)
        
        seg = Entity(
            model='sphere',
            texture='textures/snake_scales.png',
            color=seg_color,
            scale=config.SEGMENT_RADIUS * 2.0,
            position=init_pos,
            rotation=(0, init_rot_y, init_rot_z * 0.7)
        )
        self.segments.append(seg)
        self.update_segment_scales()

    def update_segment_scales(self):
        """Gradually tapers the body segments toward the tail."""
        num = len(self.segments)
        if num == 0:
            return
        for i, seg in enumerate(self.segments):
            t = i / max(1, num - 1)
            scale_mult = lerp(1.0, config.TAIL_MIN_SCALE, t)
            r = config.SEGMENT_RADIUS * 2.0 * scale_mult
            seg.scale = (r, r * 0.9, r)

    def grow(self, amount=1):
        """Increases snake target length."""
        self.target_length += amount
        for _ in range(amount):
            self.add_segment()

    def cut_tail(self, hit_index):
        """
        Severes the snake's tail starting from hit_index to the end.
        Returns a list of Vec3 positions of the severed segments (for loot dropping and particles).
        Keeps at least 3 segments to stay alive.
        """
        cutoff = max(3, hit_index)
        if cutoff >= len(self.segments):
            return []

        severed = self.segments[cutoff:]
        self.segments = self.segments[:cutoff]
        self.target_length = len(self.segments)

        severed_positions = []
        for seg in severed:
            severed_positions.append(Vec3(seg.position))
            destroy(seg)

        self.update_segment_scales()
        return severed_positions

    def update_movement(self, turn_input, boost_requested, dt):
        """
        Updates heading, continuous position, trail recording, and body positioning.
        """
        if not self.is_alive:
            return

        # Power-up timer countdowns
        self.elapsed_time += dt
        if self.shield_timer > 0:
            self.shield_timer -= dt
            self.shield_aura.visible = True
            pulse = 1.0 + 0.08 * math.sin(self.elapsed_time * 8.0)
            self.shield_aura.scale = Vec3(2.4, 2.4, 2.4) * pulse
        else:
            self.shield_aura.visible = False

        if self.magnet_timer > 0:
            self.magnet_timer -= dt
            self.magnet_aura.visible = True
            self.magnet_ring.visible = True
            m_pulse = 1.0 + 0.12 * math.sin(self.elapsed_time * 9.0)
            self.magnet_aura.scale = Vec3(2.6, 2.6, 2.6) * m_pulse
            self.magnet_ring.rotation_y += dt * 170.0
        else:
            self.magnet_aura.visible = False
            self.magnet_ring.visible = False

        if self.speed_timer > 0:
            self.speed_timer -= dt

        if self.slow_timer > 0:
            self.slow_timer -= dt

        # Boost energy handling
        if boost_requested and self.boost_energy > 0:
            self.is_boosting = True
            self.boost_energy = max(0.0, self.boost_energy - config.BOOST_DRAIN_RATE * dt)
        else:
            self.is_boosting = False
            self.boost_energy = min(config.BOOST_MAX_ENERGY, self.boost_energy + config.BOOST_RECHARGE_RATE * dt)

        # Speed calculation
        current_speed = self.base_speed
        if self.speed_timer > 0:
            current_speed *= config.SPEED_BOOST_FACTOR  # +25%
        if self.slow_timer > 0:
            current_speed *= config.SLOW_MOTION_FACTOR  # -25%
        if self.is_boosting:
            current_speed *= (config.BOOST_SPEED / config.DEFAULT_SPEED)
        self.speed = current_speed

        # Rotation update (smooth steering)
        self.head.rotation_y += turn_input * config.TURN_SPEED * dt

        # Smooth banking tilt on turns
        target_tilt = -turn_input * config.MAX_TILT_ANGLE
        self.head.rotation_z = lerp(self.head.rotation_z, target_tilt, dt * config.TILT_LERP_SPEED)

        # Forward movement vector
        rad = math.radians(self.head.rotation_y)
        forward = Vec3(math.sin(rad), 0, math.cos(rad))
        step = forward * (current_speed * dt)
        self.head.position += step

        # Flickering tongue animation
        tongue_flick = 0.5 + 0.35 * math.sin(self.elapsed_time * 12.0)
        if tongue_flick > 0.65:
            self.tongue.scale_z = 0.5 + (tongue_flick - 0.65) * 1.5
            self.tongue.visible = True
        else:
            self.tongue.visible = False

        # Trail recording
        dist_moved = (self.head.position - self.last_pos).length()
        if dist_moved >= 0.04:
            self.total_distance += dist_moved
            self.trail.append((Vec3(self.head.position), self.head.rotation_y, self.head.rotation_z, self.total_distance))
            self.last_pos = Vec3(self.head.position)
            
            # Prune old trail points with fast slice rather than O(N) pop(0)
            max_needed_dist = (len(self.segments) + 2) * config.SEGMENT_DISTANCE
            cutoff_dist = self.total_distance - (max_needed_dist + 5.0)
            cut_idx = 0
            limit = len(self.trail) - 4
            while cut_idx < limit and self.trail[cut_idx][3] < cutoff_dist:
                cut_idx += 1
            if cut_idx > 0:
                self.trail = self.trail[cut_idx:]

        # Update Body Segments along the recorded trail
        self.update_body_positions()

    def update_body_positions(self):
        """Positions body segments by sampling the distance trail with natural serpentine wave undulation."""
        if not self.trail:
            return

        for i, seg in enumerate(self.segments):
            target_dist = self.total_distance - (i + 1) * config.SEGMENT_DISTANCE
            pos, rot_y, rot_z = self.sample_trail(target_dist)

            # Natural serpentine wave undulation (harmonic slither even during straight movement)
            rad_y = math.radians(rot_y)
            right = Vec3(math.cos(rad_y), 0, -math.sin(rad_y))
            
            # Smooth neck ramp so head remains stable and predictable
            ramp = min(1.0, (i + 1) / 4.0)
            wave_phase = (self.total_distance * 1.75) - (i * 0.52)
            lateral_offset = math.sin(wave_phase) * (0.24 * ramp)
            yaw_tilt = math.cos(wave_phase) * (13.5 * ramp)
            roll_tilt = math.sin(wave_phase) * (4.5 * ramp)

            seg.position = pos + right * lateral_offset
            seg.rotation_y = rot_y + yaw_tilt
            seg.rotation_z = (rot_z + roll_tilt) * 0.7

    def sample_trail(self, target_dist):
        """Interpolates trail position and rotation at a specific cumulative distance."""
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

    def check_self_collision(self):
        """
        Checks if the head collides with any of its own body segments.
        Returns (True, hit_segment_index) if collision occurred, else (False, -1).
        """
        if not self.is_alive or len(self.segments) < 8:
            return False, -1

        hx = self.head.x
        hz = self.head.z
        thresh = (config.HEAD_RADIUS + config.SEGMENT_RADIUS) * 0.70
        thresh_sq = thresh * thresh

        # Ignore first 7 neck segments
        for i, seg in enumerate(self.segments[7:], start=7):
            dx = hx - seg.x
            dz = hz - seg.z
            if (dx * dx + dz * dz) < thresh_sq:
                return True, i
        return False, -1

    def activate_powerup(self, powerup_type):
        """Applies a powerup effect."""
        if powerup_type == "golden":
            self.grow(2)
        elif powerup_type == "speed":
            self.speed_timer = config.DURATION_SPEED_BOOST
        elif powerup_type == "slow":
            self.slow_timer = config.DURATION_SLOW_MOTION
        elif powerup_type == "magnet":
            self.magnet_timer = config.DURATION_MAGNET
        elif powerup_type == "shield":
            self.shield_timer = config.DURATION_SHIELD
        elif powerup_type == "mega_food":
            self.grow(3)

    def set_visible(self, is_visible):
        """Toggles visibility of head and all body segments for rhythmic arcade blinking."""
        if self.head:
            self.head.visible = is_visible
        for seg in self.segments:
            seg.visible = is_visible

    def destroy_entities(self):
        """Cleans up all Ursina entities associated with this Snake."""
        for seg in self.segments:
            destroy(seg)
        self.segments.clear()
        if self.head:
            if hasattr(self.head, 'children'):
                for child in list(self.head.children):
                    destroy(child)
            destroy(self.head)
            self.head = None
