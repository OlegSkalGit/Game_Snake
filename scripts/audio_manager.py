"""
Audio Manager for 3D Snake Adventure.
Generates and plays studio-grade 44.1kHz multi-harmonic procedural sound effects
and 18 unique level background music tracks with zero runtime entity leaks.
"""
import os
import wave
import struct
import math
import numpy as np
from ursina import Audio
import config

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS_DIR = os.path.join(PROJECT_ROOT, "sounds")
SFX_SAMPLE_RATE = 44100


def _apply_echo(sig, delay_s=0.075, decay=0.32):
    """Adds a short spatial room echo/reverb tail to a 1D numpy audio buffer."""
    d_samples = int(SFX_SAMPLE_RATE * delay_s)
    if d_samples <= 0 or d_samples >= len(sig):
        return sig
    out = np.copy(sig)
    for i in range(d_samples, len(out)):
        out[i] += out[i - d_samples] * decay
    return out


def _write_wav_np(filename, samples_np, force=False):
    filepath = os.path.join(SOUNDS_DIR, filename)
    if os.path.exists(filepath) and not force:
        return filepath
    # Soft saturation + peak normalization
    sig = np.tanh(samples_np * 1.45)
    peak = np.max(np.abs(sig))
    if peak > 1e-4:
        sig = (sig / peak) * 0.92
    int_data = np.clip(sig * 32767.0, -32768.0, 32767.0).astype(np.int16)
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SFX_SAMPLE_RATE)
        wav_file.writeframes(int_data.tobytes())
    return filepath


def ensure_sounds_exist(force_sfx=False):
    """Generates high-definition 44.1kHz procedural sound effects and ensures all 18 BGM tracks exist."""
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    rng = np.random.RandomState(777)

    # 1. EAT SFX: Juicy bite crunch + bright ascending harmonic marimba pop
    def gen_eat():
        dur = 0.18
        n = int(SFX_SAMPLE_RATE * dur)
        t = np.linspace(0, dur, n, endpoint=False)
        # Crisp initial bite crunch (first 25ms)
        crunch_env = np.exp(-t * 95.0)
        crunch = rng.uniform(-1.0, 1.0, n) * crunch_env * 0.45
        # Dual-note ascending pop (G5 -> D6)
        f1 = np.where(t < 0.055, 783.99, 1174.66)
        env = np.exp(-t * 22.0)
        tone = (np.sin(2 * np.pi * f1 * t) + 0.45 * np.sin(4 * np.pi * f1 * t) + 0.2 * np.sin(6 * np.pi * f1 * t)) * env
        sig = _apply_echo(crunch + tone * 0.85, delay_s=0.045, decay=0.25)
        return _write_wav_np("eat.wav", sig, force=force_sfx)

    # 2. GOLDEN APPLE / MEGA FOOD SFX: Shimmering celestial major-9th bell arpeggio
    def gen_golden():
        dur = 0.55
        n = int(SFX_SAMPLE_RATE * dur)
        t = np.linspace(0, dur, n, endpoint=False)
        notes = [523.25, 659.25, 783.99, 987.77, 1174.66, 1567.98]  # C5 E5 G5 B5 D6 G6
        sig = np.zeros(n, dtype=np.float32)
        for idx, freq in enumerate(notes):
            start = idx * 0.045
            mask = t >= start
            lt = t[mask] - start
            env = np.exp(-lt * 6.5)
            bell = (
                np.sin(2 * np.pi * freq * lt)
                + 0.5 * np.sin(2 * np.pi * freq * 2.0 * lt)
                + 0.25 * np.sin(2 * np.pi * freq * 2.756 * lt)
            )
            sig[mask] += bell * env * 0.35
        sig = _apply_echo(sig, delay_s=0.08, decay=0.38)
        return _write_wav_np("golden.wav", sig, force=force_sfx)

    # 3. POWERUP SFX: Sci-fi harmonic synth riser + FM shimmer chord
    def gen_powerup():
        dur = 0.44
        n = int(SFX_SAMPLE_RATE * dur)
        t = np.linspace(0, dur, n, endpoint=False)
        env = np.sin(np.pi * (t / dur)) ** 0.7
        sweep_f = 320.0 + 980.0 * ((t / dur) ** 1.4)
        phase = 2 * np.pi * np.cumsum(sweep_f) / SFX_SAMPLE_RATE
        fm_mod = np.sin(2 * np.pi * 28.0 * t) * 1.2
        riser = np.sin(phase + fm_mod) + 0.5 * np.sin(phase * 1.5) + 0.35 * np.sin(phase * 2.0)
        sig = _apply_echo(riser * env, delay_s=0.06, decay=0.32)
        return _write_wav_np("powerup.wav", sig, force=force_sfx)

    # 4. HIT / CRASH SFX: Deep cinematic sub-bass drop + impact crunch
    def gen_hit():
        dur = 0.50
        n = int(SFX_SAMPLE_RATE * dur)
        t = np.linspace(0, dur, n, endpoint=False)
        # Sub-bass pitch drop (140Hz -> 34Hz)
        f_sub = 34.0 + 115.0 * np.exp(-t * 14.0)
        p_sub = 2 * np.pi * np.cumsum(f_sub) / SFX_SAMPLE_RATE
        sub = np.sin(p_sub) * np.exp(-t * 6.5) * 0.95
        # Mid punch & metallic debris noise
        punch = np.sin(2 * np.pi * 210.0 * np.exp(-t * 18.0) * t) * np.exp(-t * 16.0) * 0.55
        noise = rng.uniform(-1.0, 1.0, n) * np.exp(-t * 18.0) * 0.48
        sig = _apply_echo(sub + punch + noise, delay_s=0.07, decay=0.28)
        return _write_wav_np("hit.wav", sig, force=force_sfx)

    # 5. LEVEL UP / VICTORY SFX: Triumphant polyphonic brass/synth fanfare
    def gen_levelup():
        dur = 0.85
        n = int(SFX_SAMPLE_RATE * dur)
        t = np.linspace(0, dur, n, endpoint=False)
        # Fanfare notes: C5 -> E5 -> G5 -> C6 (held with fifth G5)
        events = [
            (0.00, 0.14, [523.25, 261.63]),
            (0.13, 0.14, [659.25, 329.63]),
            (0.26, 0.14, [783.99, 392.00]),
            (0.39, 0.46, [1046.50, 783.99, 523.25])
        ]
        sig = np.zeros(n, dtype=np.float32)
        for st, d_len, freqs in events:
            mask = (t >= st) & (t < st + d_len + 0.15)
            lt = t[mask] - st
            env = np.minimum(1.0, lt / 0.012) * np.exp(-lt * 4.2)
            for f in freqs:
                saw = (
                    np.sin(2 * np.pi * f * lt)
                    + 0.55 * np.sin(4 * np.pi * f * lt)
                    + 0.30 * np.sin(6 * np.pi * f * lt)
                )
                sig[mask] += saw * env * 0.28
        sig = _apply_echo(sig, delay_s=0.09, decay=0.35)
        return _write_wav_np("levelup.wav", sig, force=force_sfx)

    # 6. UI CLICK SFX: Crisp tactile crystalline UI tap
    def gen_click():
        dur = 0.065
        n = int(SFX_SAMPLE_RATE * dur)
        t = np.linspace(0, dur, n, endpoint=False)
        env = np.exp(-t * 85.0)
        sig = (np.sin(2 * np.pi * 1480.0 * t) + 0.5 * np.sin(2 * np.pi * 2960.0 * t)) * env
        return _write_wav_np("click.wav", sig, force=force_sfx)

    # 7. ENEMY HIT / KILL SFX: Explosive predator shatter + plasma down-sweep + boom
    def gen_enemy_hit():
        dur = 0.46
        n = int(SFX_SAMPLE_RATE * dur)
        t = np.linspace(0, dur, n, endpoint=False)
        env = np.exp(-t * 10.5)
        f_sweep = 520.0 * np.exp(-t * 9.0) + 48.0
        p_sweep = 2 * np.pi * np.cumsum(f_sweep) / SFX_SAMPLE_RATE
        plasma = (np.sin(p_sweep) + 0.5 * np.sin(p_sweep * 2.0)) * env * 0.70
        shatter = rng.uniform(-1.0, 1.0, n) * np.exp(-t * 15.0) * 0.55
        sig = _apply_echo(plasma + shatter, delay_s=0.065, decay=0.30)
        return _write_wav_np("enemy_hit.wav", sig, force=force_sfx)

    # 8. TAIL CUT SFX: Sharp scissor/fang snap transient + resonant slice sweep
    def gen_tail_cut():
        dur = 0.30
        n = int(SFX_SAMPLE_RATE * dur)
        t = np.linspace(0, dur, n, endpoint=False)
        env = np.exp(-t * 18.0)
        f_slice = 980.0 * np.exp(-t * 16.0) + 160.0
        p_slice = 2 * np.pi * np.cumsum(f_slice) / SFX_SAMPLE_RATE
        blade = (np.sin(p_slice) + 0.6 * np.sin(p_slice * 2.4)) * env * 0.75
        snap = rng.uniform(-1.0, 1.0, n) * np.exp(-t * 45.0) * 0.65
        sig = _apply_echo(blade + snap, delay_s=0.05, decay=0.25)
        return _write_wav_np("tail_cut.wav", sig, force=force_sfx)

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


if __name__ == "__main__":
    print("Regenerating 44.1kHz multi-harmonic SFX files...")
    ensure_sounds_exist(force_sfx=True)
    print("All 8 studio-grade SFX files regenerated in 'sounds/'!")
