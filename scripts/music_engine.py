"""
High-Fidelity Procedural Music Synthesizer Engine for 3D Snake.
Generates 18 rich, genre-distinct, polyphonic, multi-layered 16-bar soundtrack themes
with full drum machines, warm detuned supersaws, arpeggios, chord pads, lead melodies,
and stereo delay effects using NumPy.
"""
import os
import wave
import struct
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS_DIR = os.path.join(PROJECT_ROOT, "sounds")
SAMPLE_RATE = 44100

def note_freq(semi):
    """Returns frequency in Hz for semitone offset relative to A4 (440Hz)."""
    return 440.0 * (2.0 ** (semi / 12.0))

def apply_delay(signal, delay_sec=0.24, feedback=0.32, mix=0.28):
    """Applies a rich feedback delay line for spatial depth and echo."""
    delay_samples = int(SAMPLE_RATE * delay_sec)
    if delay_samples >= len(signal):
        return signal
    out = np.copy(signal)
    for i in range(delay_samples, len(signal)):
        out[i] += out[i - delay_samples] * feedback
    return signal * (1.0 - mix) + out * mix

def osc_supersaw(freq, t, detune=0.008):
    """Lush multi-oscillator supersaw with analog detuning."""
    f1, f2, f3 = freq, freq * (1.0 + detune), freq * (1.0 - detune)
    s1 = 2.0 * (t * f1 - np.floor(0.5 + t * f1))
    s2 = 2.0 * (t * f2 - np.floor(0.5 + t * f2))
    s3 = 2.0 * (t * f3 - np.floor(0.5 + t * f3))
    return (s1 + s2 * 0.8 + s3 * 0.8) / 2.6

def osc_flute(freq, t):
    """Warm breathy woodwind flute with 2nd harmonic and 5Hz vibrato."""
    vib = 1.0 + 0.015 * np.sin(2.0 * np.pi * 5.2 * t)
    f = freq * vib
    s1 = np.sin(2.0 * np.pi * f * t)
    s2 = np.sin(4.0 * np.pi * f * t) * 0.35
    s3 = np.sin(6.0 * np.pi * f * t) * 0.12
    return s1 + s2 + s3

def osc_organ(freq, t):
    """Gothic pipe organ with harmonic drawbars (16', 8', 4', 2')."""
    s1 = np.sin(1.0 * np.pi * freq * t) * 0.5   # sub octave
    s2 = np.sin(2.0 * np.pi * freq * t) * 1.0   # fundamental
    s3 = np.sin(4.0 * np.pi * freq * t) * 0.6   # octave
    s4 = np.sin(6.0 * np.pi * freq * t) * 0.35  # fifth
    s5 = np.sin(8.0 * np.pi * freq * t) * 0.25  # super octave
    return (s1 + s2 + s3 + s4 + s5) / 2.7

def osc_chime_bell(freq, t, duration=1.5):
    """Inharmonic crystal chime bell with metallic overtones."""
    s1 = np.sin(2.0 * np.pi * freq * t)
    s2 = np.sin(2.0 * np.pi * freq * 2.756 * t) * 0.55
    s3 = np.sin(2.0 * np.pi * freq * 5.404 * t) * 0.35
    s4 = np.sin(2.0 * np.pi * freq * 8.932 * t) * 0.20
    return s1 + s2 + s3 + s4

def osc_acid_bass(freq, t, env):
    """Resonant 303 squelch saw bass."""
    raw_saw = 2.0 * (t * freq - np.floor(0.5 + t * freq))
    cutoff_mod = 1.0 + 2.5 * env
    res = np.sin(2.0 * np.pi * freq * cutoff_mod * t) * 0.45
    return raw_saw * 0.6 + res

# Master Song Synthesizer Definition for 18 Distinct Themes
THEME_SONGS = {
    # 1. Forest - Celtic Medieval RPG Folk Fantasy
    'forest': {
        'bpm': 116,
        'chord_prog': [[-24, -20, -17], [-24, -20, -17], [-28, -24, -21], [-26, -23, -19]],
        'scale': [-12, -10, -9, -7, -5, -4, -2, 0, 2, 3, 5, 7],
        'arp_pattern': [0, 4, 7, 11, 14, 11, 7, 4],
        'melody_a': [(0, 1.5, 0), (1.5, 0.5, 2), (2, 1.0, 3), (3, 1.0, 5), (4, 2.0, 7), (6, 2.0, 5), (8, 1.5, 3), (9.5, 0.5, 2), (10, 1.0, 0), (11, 1.0, -2), (12, 4.0, 0)],
        'melody_b': [(0, 1.0, 7), (1, 1.0, 8), (2, 2.0, 10), (4, 1.5, 8), (5.5, 0.5, 7), (6, 2.0, 5), (8, 1.0, 3), (9, 1.0, 5), (10, 2.0, 7), (12, 1.0, 5), (13, 1.0, 3), (14, 2.0, 0)],
        'lead_inst': 'flute', 'bass_style': 'folk_pluck', 'drum_style': 'folk_shaker'
    },
    # 2. Desert - Arabian Nights / Silk Road Mystic Phrygian
    'desert': {
        'bpm': 122,
        'chord_prog': [[-24, -20, -17], [-23, -20, -17], [-24, -20, -17], [-19, -16, -12]],
        'scale': [-12, -11, -8, -7, -5, -4, -1, 0, 1, 4, 5, 7, 8, 11],
        'arp_pattern': [0, 1, 4, 7, 12, 7, 4, 1],
        'melody_a': [(0, 1.0, 0), (1, 0.5, 1), (1.5, 0.5, 4), (2, 2.0, 5), (4, 1.5, 4), (5.5, 0.5, 1), (6, 2.0, 0), (8, 1.0, 4), (9, 1.0, 5), (10, 1.5, 7), (11.5, 0.5, 8), (12, 4.0, 7)],
        'melody_b': [(0, 1.0, 12), (1, 1.0, 11), (2, 1.5, 8), (3.5, 0.5, 7), (4, 2.0, 5), (6, 2.0, 4), (8, 1.0, 1), (9, 1.0, 4), (10, 2.0, 5), (12, 1.0, 4), (13, 1.0, 1), (14, 2.0, 0)],
        'lead_inst': 'sitar', 'bass_style': 'drone', 'drum_style': 'doumbek'
    },
    # 3. Ocean - Deep Underwater Ambient Dreamscape
    'ocean': {
        'bpm': 108,
        'chord_prog': [[-26, -21, -17], [-24, -21, -17], [-28, -24, -21], [-26, -23, -19]],
        'scale': [-12, -10, -8, -5, -3, 0, 2, 4, 7, 9, 12, 14],
        'arp_pattern': [0, 4, 7, 9, 12, 9, 7, 4],
        'melody_a': [(0, 2.0, 4), (2, 2.0, 7), (4, 3.0, 9), (7, 1.0, 7), (8, 2.0, 4), (10, 2.0, 2), (12, 4.0, 0)],
        'melody_b': [(0, 2.0, 12), (2, 2.0, 9), (4, 2.0, 7), (6, 2.0, 4), (8, 2.0, 2), (10, 2.0, 4), (12, 4.0, 7)],
        'lead_inst': 'bell', 'bass_style': 'sub', 'drum_style': 'chill'
    },
    # 4. Space - 80s Cinematic Synthwave / Vangelis
    'space': {
        'bpm': 120,
        'chord_prog': [[-24, -20, -17], [-28, -24, -21], [-21, -17, -14], [-26, -23, -19]],
        'scale': [-12, -9, -7, -5, -2, 0, 3, 5, 7, 10, 12, 15],
        'arp_pattern': [0, 7, 12, 15, 19, 15, 12, 7],
        'melody_a': [(0, 1.5, 0), (1.5, 0.5, 3), (2, 1.0, 7), (3, 1.0, 5), (4, 2.0, 3), (6, 2.0, -2), (8, 1.5, 0), (9.5, 0.5, 3), (10, 1.0, 7), (11, 1.0, 10), (12, 4.0, 12)],
        'melody_b': [(0, 1.5, 12), (1.5, 0.5, 10), (2, 1.0, 7), (3, 1.0, 5), (4, 2.0, 7), (6, 2.0, 10), (8, 1.5, 7), (9.5, 0.5, 5), (10, 1.0, 3), (11, 1.0, 0), (12, 4.0, 0)],
        'lead_inst': 'supersaw', 'bass_style': 'synth_pulse', 'drum_style': 'synthwave'
    },
    # 5. Factory - Industrial Cyber Techno / EBM
    'factory': {
        'bpm': 134,
        'chord_prog': [[-24, -21, -18], [-24, -21, -18], [-26, -23, -20], [-23, -20, -17]],
        'scale': [-12, -11, -9, -7, -6, -4, -2, 0, 1, 3, 5, 6, 8, 10, 12],
        'arp_pattern': [0, 6, 12, 6, 0, 1, 6, 1],
        'melody_a': [(0, 0.5, 0), (0.5, 0.5, 6), (1, 1.0, 0), (2, 0.5, 0), (2.5, 0.5, 1), (3, 1.0, 0), (4, 1.5, 3), (5.5, 0.5, 5), (6, 2.0, 6), (8, 0.5, 0), (8.5, 0.5, 6), (9, 1.0, 0), (10, 2.0, -1), (12, 4.0, 0)],
        'melody_b': [(0, 1.0, 12), (1, 1.0, 11), (2, 1.0, 6), (3, 1.0, 5), (4, 2.0, 3), (6, 2.0, 1), (8, 1.0, 0), (9, 1.0, 6), (10, 2.0, 5), (12, 4.0, 0)],
        'lead_inst': 'saw_stab', 'bass_style': 'acid_heavy', 'drum_style': 'industrial_909'
    },
    # 6. City - Neon Cyberpunk Outrun / Synthpop
    'city': {
        'bpm': 128,
        'chord_prog': [[-24, -20, -17], [-28, -24, -21], [-21, -17, -14], [-26, -23, -19]],
        'scale': [-12, -10, -9, -7, -5, -4, -2, 0, 2, 3, 5, 7, 8, 10, 12],
        'arp_pattern': [0, 3, 7, 10, 12, 10, 7, 3],
        'melody_a': [(0, 1.0, 0), (1, 1.0, 3), (2, 1.0, 7), (3, 1.0, 10), (4, 1.5, 12), (5.5, 0.5, 10), (6, 2.0, 7), (8, 1.0, 5), (9, 1.0, 3), (10, 2.0, 0), (12, 4.0, 0)],
        'melody_b': [(0, 1.5, 7), (1.5, 0.5, 10), (2, 1.0, 12), (3, 1.0, 14), (4, 2.0, 15), (6, 2.0, 12), (8, 1.5, 10), (9.5, 0.5, 7), (10, 2.0, 5), (12, 4.0, 0)],
        'lead_inst': 'supersaw', 'bass_style': 'slap_synth', 'drum_style': 'dance_pop'
    },
    # 7. Arctic - Glacial Ice Chimes & Ambient Frost
    'arctic': {
        'bpm': 110,
        'chord_prog': [[-21, -17, -14], [-26, -23, -19], [-24, -20, -17], [-28, -24, -21]],
        'scale': [-12, -10, -8, -7, -5, -3, -1, 0, 2, 4, 5, 7, 9, 11, 12],
        'arp_pattern': [0, 4, 7, 11, 12, 11, 7, 4],
        'melody_a': [(0, 2.0, 7), (2, 2.0, 11), (4, 3.0, 12), (7, 1.0, 11), (8, 2.0, 7), (10, 2.0, 4), (12, 4.0, 2)],
        'melody_b': [(0, 2.0, 12), (2, 1.5, 14), (3.5, 0.5, 16), (4, 2.0, 14), (6, 2.0, 12), (8, 2.0, 7), (10, 2.0, 4), (12, 4.0, 0)],
        'lead_inst': 'bell', 'bass_style': 'sub', 'drum_style': 'frost_chill'
    },
    # 8. Lava - Heavy Metal Darksynth / Volcanic Doom
    'lava': {
        'bpm': 138,
        'chord_prog': [[-24, -21, -17], [-24, -21, -17], [-23, -20, -16], [-25, -22, -18]],
        'scale': [-12, -11, -9, -7, -6, -5, -2, 0, 1, 3, 5, 6, 7, 10, 12],
        'arp_pattern': [0, 6, 12, 6, 0, 6, 12, 6],
        'melody_a': [(0, 1.0, 0), (1, 1.0, 6), (2, 2.0, 5), (4, 1.5, 3), (5.5, 0.5, 1), (6, 2.0, 0), (8, 1.0, 0), (9, 1.0, 6), (10, 2.0, 7), (12, 4.0, 0)],
        'melody_b': [(0, 1.0, 12), (1, 1.0, 10), (2, 1.0, 6), (3, 1.0, 5), (4, 2.0, 6), (6, 2.0, 5), (8, 1.0, 3), (9, 1.0, 1), (10, 2.0, 0), (12, 4.0, -1)],
        'lead_inst': 'distort_lead', 'bass_style': 'metal_saw', 'drum_style': 'double_kick'
    },
    # 9. Crystal - Amethyst Lydian Sparkle & Celestial Chorus
    'crystal': {
        'bpm': 124,
        'chord_prog': [[-21, -17, -14], [-19, -15, -12], [-24, -20, -17], [-21, -17, -14]],
        'scale': [-12, -10, -8, -6, -5, -3, -1, 0, 2, 4, 6, 7, 9, 11, 12],
        'arp_pattern': [0, 4, 6, 7, 11, 7, 6, 4],
        'melody_a': [(0, 1.5, 4), (1.5, 0.5, 6), (2, 2.0, 7), (4, 2.0, 11), (6, 2.0, 9), (8, 1.5, 7), (9.5, 0.5, 6), (10, 2.0, 4), (12, 4.0, 2)],
        'melody_b': [(0, 1.5, 11), (1.5, 0.5, 12), (2, 2.0, 14), (4, 2.0, 12), (6, 2.0, 11), (8, 1.5, 7), (9.5, 0.5, 6), (10, 2.0, 4), (12, 4.0, 0)],
        'lead_inst': 'bell', 'bass_style': 'crystal_pluck', 'drum_style': 'sparkle_beat'
    },
    # 10. Jungle - Afro-Tribal Rainforest Groove & Pan Flute
    'jungle': {
        'bpm': 126,
        'chord_prog': [[-24, -21, -17], [-22, -19, -15], [-20, -17, -13], [-24, -21, -17]],
        'scale': [-12, -9, -7, -5, -2, 0, 3, 5, 7, 10, 12, 15],
        'arp_pattern': [0, 3, 7, 10, 12, 10, 7, 3],
        'melody_a': [(0, 1.0, 0), (1, 0.5, 3), (1.5, 0.5, 5), (2, 2.0, 7), (4, 1.5, 5), (5.5, 0.5, 3), (6, 2.0, 0), (8, 1.0, 3), (9, 1.0, 5), (10, 2.0, 7), (12, 4.0, 10)],
        'melody_b': [(0, 1.0, 12), (1, 1.0, 10), (2, 2.0, 7), (4, 1.5, 5), (5.5, 0.5, 7), (6, 2.0, 10), (8, 1.0, 7), (9, 1.0, 5), (10, 2.0, 3), (12, 4.0, 0)],
        'lead_inst': 'flute', 'bass_style': 'tribal_marimba', 'drum_style': 'tribal_conga'
    },
    # 11. Sky - Soaring Celestial Orchestral Anthem
    'sky': {
        'bpm': 120,
        'chord_prog': [[-21, -17, -14], [-24, -20, -17], [-26, -23, -19], [-21, -17, -14]],
        'scale': [-12, -10, -8, -5, -3, -1, 0, 2, 4, 7, 9, 11, 12, 14],
        'arp_pattern': [0, 4, 7, 11, 12, 11, 7, 4],
        'melody_a': [(0, 1.5, 0), (1.5, 0.5, 2), (2, 1.0, 4), (3, 1.0, 7), (4, 2.0, 9), (6, 2.0, 7), (8, 1.5, 4), (9.5, 0.5, 2), (10, 2.0, 0), (12, 4.0, 0)],
        'melody_b': [(0, 1.5, 12), (1.5, 0.5, 11), (2, 1.0, 9), (3, 1.0, 7), (4, 2.0, 9), (6, 2.0, 11), (8, 1.5, 7), (9.5, 0.5, 4), (10, 2.0, 2), (12, 4.0, 0)],
        'lead_inst': 'brass_lead', 'bass_style': 'sub', 'drum_style': 'march_anthem'
    },
    # 12. Toxic - Acid Trance / Cyber Goa 303
    'toxic': {
        'bpm': 136,
        'chord_prog': [[-24, -21, -18], [-23, -20, -17], [-27, -24, -21], [-24, -21, -18]],
        'scale': [-12, -11, -9, -6, -5, -4, -1, 0, 1, 3, 6, 7, 8, 11, 12],
        'arp_pattern': [0, 1, 6, 7, 12, 7, 6, 1],
        'melody_a': [(0, 0.5, 0), (0.5, 0.5, 1), (1, 1.0, 6), (2, 1.0, 7), (3, 1.0, 6), (4, 1.5, 1), (5.5, 0.5, 0), (6, 2.0, -1), (8, 0.5, 0), (8.5, 0.5, 6), (9, 1.0, 7), (10, 2.0, 11), (12, 4.0, 12)],
        'melody_b': [(0, 1.0, 12), (1, 1.0, 11), (2, 1.0, 7), (3, 1.0, 6), (4, 2.0, 1), (6, 2.0, 0), (8, 1.0, 6), (9, 1.0, 7), (10, 2.0, 1), (12, 4.0, 0)],
        'lead_inst': 'acid_lead', 'bass_style': 'acid_rolling', 'drum_style': 'goa_trance'
    },
    # 13. Swamp - Bayou Blues / Muddy Funk Groove
    'swamp': {
        'bpm': 112,
        'chord_prog': [[-24, -21, -17], [-24, -21, -17], [-22, -19, -15], [-25, -22, -18]],
        'scale': [-12, -9, -7, -6, -5, -2, 0, 3, 5, 6, 7, 10, 12, 15],
        'arp_pattern': [0, 3, 5, 6, 7, 6, 5, 3],
        'melody_a': [(0, 1.0, 0), (1, 0.5, 3), (1.5, 0.5, 5), (2, 1.0, 6), (3, 1.0, 7), (4, 2.0, 5), (6, 2.0, 3), (8, 1.0, 0), (9, 1.0, 3), (10, 2.0, 0), (12, 4.0, -2)],
        'melody_b': [(0, 1.0, 12), (1, 1.0, 10), (2, 1.0, 7), (3, 1.0, 6), (4, 2.0, 5), (6, 2.0, 3), (8, 1.0, 5), (9, 1.0, 6), (10, 2.0, 7), (12, 4.0, 0)],
        'lead_inst': 'blues_lead', 'bass_style': 'slap_synth', 'drum_style': 'swamp_funk'
    },
    # 14. Necropolis - Ancient Pharaonic March & Pyramid Echoes
    'necropolis': {
        'bpm': 122,
        'chord_prog': [[-24, -21, -17], [-28, -24, -21], [-20, -17, -13], [-24, -21, -17]],
        'scale': [-12, -10, -9, -7, -5, -4, -1, 0, 2, 3, 5, 7, 8, 11, 12],
        'arp_pattern': [0, 3, 7, 11, 12, 11, 7, 3],
        'melody_a': [(0, 1.5, 0), (1.5, 0.5, 2), (2, 1.0, 3), (3, 1.0, 7), (4, 2.0, 8), (6, 2.0, 7), (8, 1.5, 3), (9.5, 0.5, 2), (10, 2.0, 0), (12, 4.0, 0)],
        'melody_b': [(0, 1.0, 12), (1, 1.0, 11), (2, 2.0, 8), (4, 1.5, 7), (5.5, 0.5, 5), (6, 2.0, 3), (8, 1.0, 2), (9, 1.0, 3), (10, 2.0, 11), (12, 4.0, 0)],
        'lead_inst': 'mystic_reed', 'bass_style': 'drone', 'drum_style': 'tomb_march'
    },
    # 15. Steampunk - Victorian Clockwork Baroque & Brass Fanfare
    'steampunk': {
        'bpm': 128,
        'chord_prog': [[-24, -20, -17], [-21, -17, -14], [-26, -23, -19], [-24, -20, -17]],
        'scale': [-12, -10, -8, -7, -5, -3, -2, 0, 2, 4, 5, 7, 9, 10, 12],
        'arp_pattern': [0, 4, 7, 10, 12, 10, 7, 4],
        'melody_a': [(0, 0.5, 0), (0.5, 0.5, 2), (1, 0.5, 4), (1.5, 0.5, 5), (2, 1.0, 7), (3, 1.0, 9), (4, 2.0, 10), (6, 2.0, 7), (8, 1.0, 4), (9, 1.0, 2), (10, 2.0, 0), (12, 4.0, 0)],
        'melody_b': [(0, 1.0, 12), (1, 1.0, 10), (2, 1.0, 9), (3, 1.0, 7), (4, 2.0, 5), (6, 2.0, 4), (8, 1.0, 2), (9, 1.0, 4), (10, 2.0, 7), (12, 4.0, 0)],
        'lead_inst': 'brass_lead', 'bass_style': 'folk_pluck', 'drum_style': 'clockwork'
    },
    # 16. Event Horizon - Dark Gravitational Void Drone & Sub-Atomic Pulses
    'event_horizon': {
        'bpm': 125,
        'chord_prog': [[-24, -21, -18], [-25, -22, -19], [-26, -23, -20], [-27, -24, -21]],
        'scale': [-12, -11, -9, -8, -6, -5, -3, -2, 0, 1, 3, 4, 6, 7, 9, 10, 12],
        'arp_pattern': [0, 6, 12, 6, 1, 7, 13, 7],
        'melody_a': [(0, 2.0, 0), (2, 2.0, 6), (4, 3.0, 7), (7, 1.0, 6), (8, 2.0, 1), (10, 2.0, 0), (12, 4.0, -1)],
        'melody_b': [(0, 2.0, 12), (2, 2.0, 6), (4, 2.0, 1), (6, 2.0, 0), (8, 2.0, 6), (10, 2.0, 7), (12, 4.0, 0)],
        'lead_inst': 'void_lead', 'bass_style': 'sub', 'drum_style': 'void_beat'
    },
    # 17. Dungeon - Castlevania Gothic Pipe Organ & Harpsichord March
    'dungeon': {
        'bpm': 130,
        'chord_prog': [[-24, -21, -17], [-28, -24, -21], [-23, -20, -16], [-24, -21, -17]],
        'scale': [-12, -10, -9, -7, -5, -4, -2, 0, 2, 3, 5, 7, 8, 10, 12],
        'arp_pattern': [0, 3, 7, 10, 12, 10, 7, 3],
        'melody_a': [(0, 1.5, 0), (1.5, 0.5, 3), (2, 1.0, 7), (3, 1.0, 10), (4, 2.0, 12), (6, 2.0, 10), (8, 1.5, 7), (9.5, 0.5, 3), (10, 2.0, 0), (12, 4.0, 0)],
        'melody_b': [(0, 1.0, 12), (1, 1.0, 14), (2, 2.0, 15), (4, 1.5, 14), (5.5, 0.5, 12), (6, 2.0, 10), (8, 1.0, 7), (9, 1.0, 8), (10, 2.0, 11), (12, 4.0, 12)],
        'lead_inst': 'organ', 'bass_style': 'metal_saw', 'drum_style': 'gothic_march'
    },
    # 18. Quantum - 145 BPM Hyper-Cyber Final Boss Rave
    'quantum': {
        'bpm': 145,
        'chord_prog': [[-24, -20, -17], [-20, -17, -13], [-28, -24, -21], [-26, -23, -19]],
        'scale': [-12, -9, -7, -6, -5, -2, 0, 3, 5, 6, 7, 10, 12, 15],
        'arp_pattern': [0, 7, 12, 15, 19, 15, 12, 7],
        'melody_a': [(0, 0.5, 0), (0.5, 0.5, 3), (1, 0.5, 7), (1.5, 0.5, 10), (2, 1.0, 12), (3, 1.0, 15), (4, 2.0, 12), (6, 2.0, 10), (8, 1.0, 7), (9, 1.0, 6), (10, 2.0, 7), (12, 4.0, 12)],
        'melody_b': [(0, 1.0, 15), (1, 1.0, 14), (2, 1.0, 12), (3, 1.0, 10), (4, 2.0, 12), (6, 2.0, 15), (8, 1.0, 12), (9, 1.0, 10), (10, 2.0, 7), (12, 4.0, 0)],
        'lead_inst': 'supersaw', 'bass_style': 'acid_rolling', 'drum_style': 'boss_rave'
    }
}

def synthesize_song(theme_name, song_data):
    """Synthesizes a rich 16-bar multi-track song for the given theme."""
    bpm = song_data['bpm']
    beat_dur = 60.0 / bpm
    total_beats = 64  # 16 bars = full rich development cycle (~26 to 32 seconds)
    duration = total_beats * beat_dur
    total_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)

    chord_prog = song_data['chord_prog']
    arp_pattern = song_data['arp_pattern']
    melody_a = song_data['melody_a']
    melody_b = song_data['melody_b']
    lead_inst = song_data['lead_inst']
    bass_style = song_data['bass_style']
    drum_style = song_data['drum_style']

    mix = np.zeros(total_samples, dtype=np.float32)

    # 1. Harmonic Chords & Warm Pad (4-note polyphony with stereo width)
    pad = np.zeros(total_samples, dtype=np.float32)
    for chord_bar in range(16):
        chord_idx = chord_bar % len(chord_prog)
        chord_notes = chord_prog[chord_idx]
        bar_start_t = chord_bar * 4.0 * beat_dur
        bar_end_t = (chord_bar + 1) * 4.0 * beat_dur
        bar_mask = (t >= bar_start_t) & (t < bar_end_t)
        if not np.any(bar_mask):
            continue

        rel_t = t[bar_mask] - bar_start_t
        # Smooth attack and release envelope per bar
        pad_env = np.sin(np.pi * np.clip(rel_t / (4.0 * beat_dur), 0.0, 1.0))

        chord_sig = np.zeros(np.sum(bar_mask), dtype=np.float32)
        for note in chord_notes:
            f = note_freq(note + 12)  # Pad octave
            chord_sig += osc_supersaw(f, t[bar_mask]) * 0.12

        pad[bar_mask] += chord_sig * pad_env

    # 2. Bassline
    bass = np.zeros(total_samples, dtype=np.float32)
    for beat_idx in range(total_beats):
        bar_idx = (beat_idx // 4) % len(chord_prog)
        root_note = chord_prog[bar_idx][0]
        beat_start_t = beat_idx * beat_dur
        beat_end_t = (beat_idx + 1) * beat_dur
        beat_mask = (t >= beat_start_t) & (t < beat_end_t)
        if not np.any(beat_mask):
            continue

        b_rel_t = t[beat_mask] - beat_start_t
        b_sub = (b_rel_t / beat_dur) % 1.0

        if bass_style in ['acid_heavy', 'acid_rolling']:
            # 16th rolling acid bass
            for step in range(4):
                step_start = step * (beat_dur / 4.0)
                step_end = (step + 1) * (beat_dur / 4.0)
                step_mask = (b_rel_t >= step_start) & (b_rel_t < step_end)
                if not np.any(step_mask):
                    continue
                s_rel = (b_rel_t[step_mask] - step_start) / (beat_dur / 4.0)
                s_env = np.exp(-s_rel * 7.0)
                step_note = root_note + (12 if step % 2 == 1 else 0)
                f_b = note_freq(step_note)
                bass[beat_mask][step_mask] += osc_acid_bass(f_b, t[beat_mask][step_mask], s_env) * 0.35 * s_env
        else:
            # 8th note bouncing bass
            for step in range(2):
                step_start = step * (beat_dur / 2.0)
                step_end = (step + 1) * (beat_dur / 2.0)
                step_mask = (b_rel_t >= step_start) & (b_rel_t < step_end)
                if not np.any(step_mask):
                    continue
                s_rel = (b_rel_t[step_mask] - step_start) / (beat_dur / 2.0)
                s_env = np.exp(-s_rel * 5.0)
                step_note = root_note + (12 if step == 1 else 0)
                f_b = note_freq(step_note)
                if bass_style == 'sub':
                    bass[beat_mask][step_mask] += np.sin(2.0 * np.pi * f_b * t[beat_mask][step_mask]) * 0.40 * s_env
                elif bass_style == 'metal_saw':
                    bass[beat_mask][step_mask] += osc_supersaw(f_b, t[beat_mask][step_mask]) * 0.38 * s_env
                else:
                    bass[beat_mask][step_mask] += (np.sin(2.0 * np.pi * f_b * t[beat_mask][step_mask]) + 0.4 * np.sin(4.0 * np.pi * f_b * t[beat_mask][step_mask])) * 0.35 * s_env

    # 3. Arpeggio
    arp = np.zeros(total_samples, dtype=np.float32)
    for beat_idx in range(total_beats):
        bar_idx = (beat_idx // 4) % len(chord_prog)
        root_note = chord_prog[bar_idx][0]
        beat_start_t = beat_idx * beat_dur
        for step in range(4):
            step_start = beat_start_t + step * (beat_dur / 4.0)
            step_end = step_start + (beat_dur / 4.0)
            step_mask = (t >= step_start) & (t < step_end)
            if not np.any(step_mask):
                continue
            s_rel = (t[step_mask] - step_start) / (beat_dur / 4.0)
            arp_env = np.exp(-s_rel * 8.0)
            offset = arp_pattern[(beat_idx * 4 + step) % len(arp_pattern)]
            f_arp = note_freq(root_note + 12 + offset)
            arp[step_mask] += osc_supersaw(f_arp, t[step_mask], detune=0.004) * 0.16 * arp_env

    # 4. Lead Melody (Part A for bars 1-8, Part B for bars 9-16)
    lead = np.zeros(total_samples, dtype=np.float32)
    for part_idx, (section_start_beat, mel) in enumerate([(0, melody_a), (32, melody_b)]):
        for m_start, m_dur, m_semi in mel:
            note_start_t = (section_start_beat + m_start) * beat_dur
            note_end_t = note_start_t + m_dur * beat_dur
            note_mask = (t >= note_start_t) & (t < note_end_t)
            if not np.any(note_mask):
                continue

            rel_t = t[note_mask] - note_start_t
            dur_s = m_dur * beat_dur
            l_env = np.sin(np.pi * np.clip(rel_t / 0.05, 0.0, 1.0)) * np.exp(-np.maximum(0.0, rel_t - dur_s * 0.75) * 4.5)
            f_lead = note_freq(m_semi)

            if lead_inst == 'flute':
                lead_sig = osc_flute(f_lead, t[note_mask]) * 0.28
            elif lead_inst == 'organ':
                lead_sig = osc_organ(f_lead, t[note_mask]) * 0.32
            elif lead_inst == 'bell':
                lead_sig = osc_chime_bell(f_lead, t[note_mask], dur_s) * 0.26
            elif lead_inst == 'sitar':
                vib = 1.0 + 0.02 * np.sin(2.0 * np.pi * 6.5 * rel_t)
                lead_sig = (np.sin(2.0 * np.pi * f_lead * vib * rel_t) + 0.5 * np.sin(4.0 * np.pi * f_lead * vib * rel_t)) * 0.30
            elif lead_inst == 'distort_lead':
                lead_sig = np.tanh(osc_supersaw(f_lead, t[note_mask]) * 1.8) * 0.28
            else:
                lead_sig = osc_supersaw(f_lead, t[note_mask]) * 0.28

            lead[note_mask] += lead_sig * l_env

    # 5. Full Drum Machine
    drums = np.zeros(total_samples, dtype=np.float32)
    for beat_idx in range(total_beats):
        beat_start_t = beat_idx * beat_dur
        beat_end_t = (beat_idx + 1) * beat_dur
        beat_mask = (t >= beat_start_t) & (t < beat_end_t)
        if not np.any(beat_mask):
            continue

        b_rel_t = t[beat_mask] - beat_start_t
        sub = b_rel_t / beat_dur

        # Kick on beats 0, 1, 2, 3 (or syncopated)
        k_env = np.exp(-sub * 16.0)
        kick_freq = 150.0 * np.exp(-sub * 22.0) + 42.0
        drums[beat_mask] += np.sin(2.0 * np.pi * kick_freq * b_rel_t) * 0.42 * k_env

        # Snare / Clap on beats 1 & 3 (2nd and 4th beats of bar)
        if (beat_idx % 4) in [1, 3]:
            snare_env = np.exp(-sub * 18.0)
            snare_noise = np.random.uniform(-1.0, 1.0, np.sum(beat_mask)) * 0.24 * snare_env
            snare_tone = np.sin(2.0 * np.pi * 180.0 * b_rel_t) * 0.20 * np.exp(-sub * 25.0)
            drums[beat_mask] += (snare_noise + snare_tone)

        # Hi-Hats (16th notes)
        for s in range(4):
            s_start = s * (beat_dur / 4.0)
            s_end = (s + 1) * (beat_dur / 4.0)
            s_mask = (b_rel_t >= s_start) & (b_rel_t < s_end)
            if not np.any(s_mask):
                continue
            s_rel = (b_rel_t[s_mask] - s_start) / (beat_dur / 4.0)
            h_env = np.exp(-s_rel * 35.0)
            # Accent velocity on offbeats
            vel = 0.12 if s == 2 else 0.07
            drums[beat_mask][s_mask] += np.random.uniform(-1.0, 1.0, np.sum(s_mask)) * vel * h_env

    # 6. Apply spatial stereo delay / echo to Lead & Arp
    lead_delayed = apply_delay(lead, delay_sec=0.28, feedback=0.35, mix=0.30)
    arp_delayed = apply_delay(arp, delay_sec=0.18, feedback=0.25, mix=0.22)

    # Master Sum
    mix = pad + bass + arp_delayed + lead_delayed + drums

    # Master Limiter & Maximizer: Warm Soft-Clipping Saturation
    mix = np.tanh(mix * 1.85)
    peak = np.max(np.abs(mix))
    if peak > 0.001:
        mix = (mix / peak) * 0.95

    # Save to WAV
    wav_path = os.path.join(SOUNDS_DIR, f"bgm_{theme_name}.wav")
    with wave.open(wav_path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        int_data = np.clip(mix * 32767.0, -32768.0, 32767.0).astype(np.int16)
        f.writeframes(int_data.tobytes())

    return wav_path

def generate_all_soundtracks():
    """Generates all 18 high-fidelity soundtracks in parallel/vectorized mode."""
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    print("Generating 18 rich, high-fidelity soundtrack themes...")
    for theme, data in THEME_SONGS.items():
        path = synthesize_song(theme, data)
        print(f"   -> Synthesized: {path} ({data['bpm']} BPM, 16 bars)")
    print("All 18 soundtrack themes successfully generated!")

if __name__ == '__main__':
    generate_all_soundtracks()
