"""
Audio Manager for 3D Snake.
Generates and plays synthesized procedural sound effects and 18 unique level background music tracks.
"""
import os
import wave
import struct
import math
from ursina import Audio
import config

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS_DIR = os.path.join(PROJECT_ROOT, "sounds")

THEMES_MUSIC_PARAMS = {
    'forest':        {'bpm': 118, 'scale': [0, 2, 3, 5, 7, 9, 10, 12], 'roots': [-24, -20, -22, -24]},
    'desert':        {'bpm': 122, 'scale': [0, 1, 4, 5, 7, 8, 11, 12], 'roots': [-24, -23, -24, -20]},
    'ocean':         {'bpm': 112, 'scale': [0, 2, 4, 7, 9, 12, 14, 16], 'roots': [-26, -21, -23, -26]},
    'space':         {'bpm': 120, 'scale': [0, 3, 5, 7, 10, 12, 15, 17], 'roots': [-24, -28, -21, -26]},
    'factory':       {'bpm': 132, 'scale': [0, 1, 3, 5, 6, 8, 10, 12], 'roots': [-24, -24, -26, -23]},
    'city':          {'bpm': 130, 'scale': [0, 2, 3, 5, 7, 8, 10, 12], 'roots': [-24, -28, -21, -26]},
    'arctic':        {'bpm': 114, 'scale': [0, 2, 4, 5, 7, 9, 11, 12], 'roots': [-21, -26, -24, -28]},
    'lava':          {'bpm': 136, 'scale': [0, 1, 3, 5, 7, 8, 10, 12], 'roots': [-24, -24, -23, -25]},
    'crystal':       {'bpm': 124, 'scale': [0, 2, 4, 6, 7, 9, 11, 12], 'roots': [-21, -19, -24, -21]},
    'jungle':        {'bpm': 126, 'scale': [0, 3, 5, 7, 10, 12, 15, 17], 'roots': [-24, -22, -20, -24]},
    'sky':           {'bpm': 120, 'scale': [0, 2, 4, 7, 9, 11, 12, 14], 'roots': [-21, -24, -26, -21]},
    'toxic':         {'bpm': 134, 'scale': [0, 1, 3, 6, 7, 8, 11, 12], 'roots': [-24, -23, -27, -24]},
    'swamp':         {'bpm': 110, 'scale': [0, 3, 5, 6, 7, 10, 12, 15], 'roots': [-24, -24, -22, -25]},
    'necropolis':    {'bpm': 122, 'scale': [0, 2, 3, 5, 7, 8, 11, 12], 'roots': [-24, -28, -20, -24]},
    'steampunk':     {'bpm': 128, 'scale': [0, 2, 4, 5, 7, 9, 10, 12], 'roots': [-24, -21, -26, -24]},
    'event_horizon': {'bpm': 125, 'scale': [0, 1, 3, 4, 6, 7, 9, 10], 'roots': [-24, -25, -26, -27]},
    'dungeon':       {'bpm': 126, 'scale': [0, 2, 3, 5, 7, 8, 10, 12], 'roots': [-24, -28, -23, -24]},
    'quantum':       {'bpm': 142, 'scale': [0, 3, 5, 6, 7, 10, 12, 15], 'roots': [-24, -20, -28, -26]}
}

def note_freq(semi):
    return 440.0 * (2.0 ** (semi / 12.0))

def ensure_sounds_exist():
    """Generates procedural sound effects and 18 background music tracks."""
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    sample_rate = 22050

    def write_wav(filename, samples, srate=22050):
        filepath = os.path.join(SOUNDS_DIR, filename)
        if os.path.exists(filepath):
            return filepath
        with wave.open(filepath, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(srate)
            raw_data = bytearray()
            for s in samples:
                val = max(-1.0, min(1.0, s))
                int_val = int(val * 32767.0)
                raw_data.extend(struct.pack('<h', int_val))
            wav_file.writeframes(raw_data)
        return filepath

    # SFX
    def gen_eat():
        duration = 0.12
        total_samples = int(sample_rate * duration)
        samples = []
        for i in range(total_samples):
            t = i / sample_rate
            env = math.exp(-t * 28.0)
            freq = 520.0 + (t / duration) * 440.0
            s = math.sin(2.0 * math.pi * freq * t) * env * 0.7
            samples.append(s)
        return write_wav("eat.wav", samples)

    def gen_golden():
        duration = 0.35
        total_samples = int(sample_rate * duration)
        samples = []
        for i in range(total_samples):
            t = i / sample_rate
            env = math.exp(-t * 8.0)
            s1 = math.sin(2.0 * math.pi * 880.0 * t)
            s2 = math.sin(2.0 * math.pi * 1320.0 * t)
            s3 = math.sin(2.0 * math.pi * 1760.0 * t)
            v = (s1 * 0.4 + s2 * 0.35 + s3 * 0.25) * env * 0.8
            samples.append(v)
        return write_wav("golden.wav", samples)

    def gen_powerup():
        duration = 0.32
        total_samples = int(sample_rate * duration)
        samples = []
        for i in range(total_samples):
            t = i / sample_rate
            env = math.sin(math.pi * (i / total_samples))
            freq = 400.0 + math.sin(t * 50.0) * 150.0 + (t / duration) * 800.0
            v = math.sin(2.0 * math.pi * freq * t) * env * 0.65
            samples.append(v)
        return write_wav("powerup.wav", samples)

    def gen_hit():
        duration = 0.45
        total_samples = int(sample_rate * duration)
        samples = []
        for i in range(total_samples):
            t = i / sample_rate
            env = math.exp(-t * 12.0)
            noise = ((math.sin(i * 999.0) * 43758.5453) % 1.0) * 2.0 - 1.0
            bass = math.sin(2.0 * math.pi * 80.0 * (1.0 - t * 1.5) * t)
            v = (bass * 0.7 + noise * 0.3 * env) * env * 0.85
            samples.append(v)
        return write_wav("hit.wav", samples)

    def gen_levelup():
        duration = 0.6
        total_samples = int(sample_rate * duration)
        samples = []
        notes = [523.25, 659.25, 783.99, 1046.50]
        note_dur = duration / len(notes)
        for i in range(total_samples):
            t = i / sample_rate
            note_idx = min(int(t / note_dur), len(notes) - 1)
            freq = notes[note_idx]
            local_t = t - note_idx * note_dur
            env = math.exp(-local_t * 6.0)
            v = math.sin(2.0 * math.pi * freq * t) * env * 0.75
            samples.append(v)
        return write_wav("levelup.wav", samples)

    def gen_click():
        duration = 0.05
        total_samples = int(sample_rate * duration)
        samples = []
        for i in range(total_samples):
            t = i / sample_rate
            env = math.exp(-t * 90.0)
            v = math.sin(2.0 * math.pi * 1200.0 * t) * env * 0.5
            samples.append(v)
        return write_wav("click.wav", samples)

    def gen_enemy_hit():
        duration = 0.38
        total_samples = int(sample_rate * duration)
        samples = []
        for i in range(total_samples):
            t = i / sample_rate
            env = math.exp(-t * 14.0)
            noise = ((math.sin(i * 1234.56) * 43758.5453) % 1.0) * 2.0 - 1.0
            sweep = math.sin(2.0 * math.pi * (340.0 - t * 600.0) * t)
            v = (noise * 0.6 + sweep * 0.4) * env * 0.9
            samples.append(v)
        return write_wav("enemy_hit.wav", samples)

    def gen_tail_cut():
        duration = 0.28
        total_samples = int(sample_rate * duration)
        samples = []
        for i in range(total_samples):
            t = i / sample_rate
            env = math.exp(-t * 22.0)
            noise = ((math.sin(i * 3456.78) * 43758.5453) % 1.0) * 2.0 - 1.0
            sweep = math.sin(2.0 * math.pi * (700.0 - t * 1800.0) * t)
            v = (noise * 0.45 + sweep * 0.55) * env * 0.9
            samples.append(v)
        return write_wav("tail_cut.wav", samples)

    def gen_theme_bgm(theme, params):
        bpm = params['bpm']
        beat_dur = 60.0 / bpm
        total_beats = 16
        duration = total_beats * beat_dur
        total_samples = int(sample_rate * duration)
        scale = params['scale']
        roots = params['roots']
        
        samples = [0.0] * total_samples
        for i in range(total_samples):
            t = i / sample_rate
            beat = t / beat_dur
            bar_idx = min(int(beat / 4.0), len(roots) - 1)
            root = roots[bar_idx]
            
            # Bass
            sub_beat = beat % 1.0
            b_env = math.exp(-sub_beat * 5.5)
            f_bass = note_freq(root + (12 if (beat * 2.0) % 2.0 >= 1.0 else 0))
            bass = math.sin(2.0 * math.pi * f_bass * t) * 0.34 * b_env
            
            # Arp
            arp_idx = int(beat * 4.0) % len(scale)
            f_arp = note_freq(root + 12 + scale[arp_idx])
            arp_env = math.exp(-((beat * 4.0) % 1.0) * 8.0)
            arp = (math.sin(2.0 * math.pi * f_arp * t) + 0.4 * math.sin(4.0 * math.pi * f_arp * t)) * 0.16 * arp_env
            
            # Drums
            k_env = math.exp(-(beat % 1.0) * 16.0)
            kick = math.sin(2.0 * math.pi * (140.0 * math.exp(-(beat % 1.0) * 20.0) + 40.0) * (beat % 1.0) * beat_dur) * 0.42 * k_env
            
            hat_env = math.exp(-((beat * 2.0) % 1.0) * 30.0) if ((beat * 2.0) % 1.0) < 0.35 else 0.0
            noise = ((math.sin(i * 345.67) * 43758.5453) % 1.0) * 2.0 - 1.0
            hat = noise * 0.09 * hat_env
            
            # Lead Melody
            lead_note_idx = int(beat * 1.5) % len(scale)
            f_lead = note_freq(scale[lead_note_idx])
            lead_sub = (beat * 1.5) % 1.0
            l_env = math.sin(math.pi * min(1.0, lead_sub / 0.1)) * math.exp(-lead_sub * 2.5)
            lead = (math.sin(2.0 * math.pi * f_lead * t) + 0.5 * math.sin(4.0 * math.pi * f_lead * t)) * 0.22 * l_env
            
            samples[i] = (bass + arp + kick + hat + lead) * 0.85

        return write_wav(f"bgm_{theme}.wav", samples)

    # Generate all SFX
    gen_eat()
    gen_golden()
    gen_powerup()
    gen_hit()
    gen_levelup()
    gen_click()
    gen_enemy_hit()
    gen_tail_cut()

    # Generate rich soundtracks via music engine if needed
    try:
        from music_engine import generate_all_soundtracks, THEME_SONGS
        missing = any(not os.path.exists(os.path.join(SOUNDS_DIR, f"bgm_{th}.wav")) for th in THEME_SONGS)
        if missing:
            generate_all_soundtracks()
    except Exception as e:
        print("Music engine notice:", e)


class AudioManager:
    """Manages playing game sound effects and 18 unique looping level soundtracks."""
    def __init__(self):
        Audio.volume_multiplier = getattr(config, 'AUDIO_MASTER_VOLUME', 1.0)
        ensure_sounds_exist()
        self.enabled = True
        self.music_enabled = True
        self.volume = getattr(config, 'AUDIO_SFX_VOLUME', 0.65)
        self.music_volume = getattr(config, 'AUDIO_MUSIC_VOLUME', 0.95)
        self.bgm = None
        self.current_theme = "forest"

        # Pre-allocate reusable sound channels (2 per SFX) to eliminate runtime Entity leaks
        self.sfx_pool = {}
        self.sfx_indices = {}
        for sfx_name in ["eat", "golden", "powerup", "hit", "levelup", "click", "enemy_hit", "tail_cut"]:
            rel_path = f"sounds/{sfx_name}.wav"
            full_path = os.path.join(SOUNDS_DIR, f"{sfx_name}.wav")
            if os.path.exists(full_path):
                try:
                    self.sfx_pool[sfx_name] = [
                        Audio(rel_path, autoplay=False, loop=False, volume=self.volume, group='sfx'),
                        Audio(rel_path, autoplay=False, loop=False, volume=self.volume, group='sfx')
                    ]
                    self.sfx_indices[sfx_name] = 0
                except Exception:
                    pass

    def play_level_bgm(self, theme):
        """Switches and plays the unique background music corresponding to the level theme."""
        self.current_theme = theme
        if not self.music_enabled:
            return
        self.stop_bgm()
        
        # Check for audio file (wav or mp3)
        wav_file = os.path.join(SOUNDS_DIR, f"bgm_{theme}.wav")
        mp3_file = os.path.join(SOUNDS_DIR, f"bgm_{theme}.mp3")
        rel_path = None
        if os.path.exists(wav_file):
            rel_path = f"sounds/bgm_{theme}.wav"
        elif os.path.exists(mp3_file):
            rel_path = f"sounds/bgm_{theme}.mp3"

        if rel_path:
            try:
                self.bgm = Audio(rel_path, loop=True, autoplay=True, volume=self.music_volume, group='music')
            except Exception:
                pass

    def stop_bgm(self):
        """Stops current background music and destroys its entity to prevent memory leaks."""
        if self.bgm:
            try:
                self.bgm.stop(destroy=True)
            except Exception:
                pass
            self.bgm = None

    def toggle_music(self):
        """Toggles background music on or off."""
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.play_level_bgm(self.current_theme)
        else:
            self.stop_bgm()
        return self.music_enabled

    def set_music_volume(self, vol):
        self.music_volume = max(0.0, min(1.0, vol))
        if self.bgm:
            try:
                self.bgm.volume = self.music_volume
            except Exception:
                pass

    def play(self, sound_name):
        if not self.enabled:
            return
        if sound_name in self.sfx_pool and self.sfx_pool[sound_name]:
            channels = self.sfx_pool[sound_name]
            idx = self.sfx_indices[sound_name]
            chan = channels[idx]
            self.sfx_indices[sound_name] = (idx + 1) % len(channels)
            try:
                chan.volume = self.volume
                chan.play()
            except Exception:
                pass
        else:
            rel_path = f"sounds/{sound_name}.wav"
            if os.path.exists(os.path.join(SOUNDS_DIR, f"{sound_name}.wav")):
                try:
                    Audio(rel_path, autoplay=True, loop=False, auto_destroy=True, volume=self.volume)
                except Exception:
                    pass

    def play_eat(self):
        self.play("eat")

    def play_golden(self):
        self.play("golden")

    def play_powerup(self):
        self.play("powerup")

    def play_hit(self):
        self.play("hit")

    def play_levelup(self):
        self.play("levelup")

    def play_click(self):
        self.play("click")

    def play_enemy_hit(self):
        self.play("enemy_hit")

    def play_tail_cut(self):
        self.play("tail_cut")
