"""
Procedural High-Definition (512x512) Texture Synthesis Engine for 3D Snake Adventure.
Generates seamless, multi-layered, normal-shaded 512x512 textures for snake skins,
enemy armor, architectural props, obstacles, and all 18 biome terrains using NumPy & Pillow.
"""
import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXTURES_DIR = os.path.join(PROJECT_ROOT, "textures")
TEX_SIZE = 512


def ensure_dir():
    os.makedirs(TEXTURES_DIR, exist_ok=True)


def _tileable_fbm(w=TEX_SIZE, h=TEX_SIZE, octaves=4, seed=42):
    """Generates seamless tileable multi-octave 2D Fractional Brownian Motion (fBm) noise in [0, 1]."""
    rng = np.random.RandomState(seed)
    x = np.linspace(0, 2 * np.pi, w, endpoint=False)
    y = np.linspace(0, 2 * np.pi, h, endpoint=False)
    xx, yy = np.meshgrid(x, y)
    acc = np.zeros((h, w), dtype=np.float32)
    amp = 1.0
    freq = 1
    for _ in range(octaves):
        for _ in range(3):
            fx = freq * rng.randint(1, 4)
            fy = freq * rng.randint(1, 4)
            px = rng.uniform(0, 2 * np.pi)
            py = rng.uniform(0, 2 * np.pi)
            acc += amp * np.sin(fx * xx + px) * np.cos(fy * yy + py)
        # Add fine interpolated grid noise
        gw = max(4, freq * 8)
        grid = rng.uniform(-1.0, 1.0, (gw, gw)).astype(np.float32)
        grid_img = Image.fromarray(((grid + 1.0) * 127.5).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        acc += amp * ((np.asarray(grid_img, dtype=np.float32) / 127.5) - 1.0)
        amp *= 0.5
        freq *= 2

    mn, mx = acc.min(), acc.max()
    if mx - mn > 1e-6:
        acc = (acc - mn) / (mx - mn)
    return acc


def _save_rgba(arr, filename, blur=0.0):
    """Clamps float/uint8 array (H, W, 3 or 4) and saves to PNG in textures/."""
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    if arr.shape[2] == 3:
        alpha = np.full((arr.shape[0], arr.shape[1], 1), 255, dtype=np.uint8)
        arr = np.concatenate([arr, alpha], axis=2)
    img = Image.fromarray(arr, mode="RGBA")
    if blur > 0:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    img.save(os.path.join(TEXTURES_DIR, filename))
    return img


def create_snake_scales():
    """HD 512x512 3D-shaded emerald-gold overlapping reptilian diamond scales."""
    w = h = TEX_SIZE
    y_idx, x_idx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = x_idx / w
    v = y_idx / h

    # Staggered diamond/hex scale coordinates (14x14 tileable grid)
    cols, rows = 14.0, 14.0
    row_f = v * rows
    row_i = np.floor(row_f)
    col_f = u * cols + (row_i % 2) * 0.5
    local_x = (col_f - np.floor(col_f)) * 2.0 - 1.0
    local_y = (row_f - row_i) * 2.0 - 1.0

    # Overlapping scale profile with curved bottom lip
    dist = np.sqrt(local_x ** 2 * 0.95 + (local_y + 0.12 * (local_x ** 2)) ** 2)
    edge_mask = np.clip((1.02 - dist) * 6.5, 0.0, 1.0)

    # 3D Spherical Normal Lighting (light from top-left)
    nx = local_x * 0.75
    ny = local_y * 0.75
    nz = np.sqrt(np.maximum(0.05, 1.0 - np.clip(nx ** 2 + ny ** 2, 0.0, 0.95)))
    light = np.clip(-0.35 * nx - 0.45 * ny + 0.82 * nz, 0.0, 1.0)
    spec = np.power(np.clip(-0.25 * nx - 0.55 * ny + 0.80 * nz, 0.0, 1.0), 14.0)

    fbm = _tileable_fbm(w, h, octaves=4, seed=101)
    iridescence = 0.5 + 0.5 * np.sin((u * 4.0 + v * 2.0) * np.pi * 2.0 + fbm * 2.5)

    r = (16 + 38 * light + 55 * iridescence * light + 165 * spec) * edge_mask + 8 * (1.0 - edge_mask)
    g = (95 + 125 * light + 25 * fbm + 140 * spec) * edge_mask + 38 * (1.0 - edge_mask)
    b = (42 + 65 * light + 45 * iridescence + 110 * spec) * edge_mask + 18 * (1.0 - edge_mask)

    arr = np.stack([r, g, b], axis=-1)
    _save_rgba(arr, "snake_scales.png")


def create_enemy_scales():
    """HD 512x512 armored crimson-obsidian predator dragon scales with glowing magma seams."""
    w = h = TEX_SIZE
    y_idx, x_idx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = x_idx / w
    v = y_idx / h

    cols, rows = 12.0, 12.0
    row_f = v * rows
    row_i = np.floor(row_f)
    col_f = u * cols + (row_i % 2) * 0.5
    local_x = (col_f - np.floor(col_f)) * 2.0 - 1.0
    local_y = (row_f - row_i) * 2.0 - 1.0

    # Sharp dragon scale shape (diamond-shield profile)
    dist = np.abs(local_x) * 0.72 + np.abs(local_y) * 0.72 + 0.25 * (local_x ** 2 + local_y ** 2)
    edge_mask = np.clip((1.0 - dist) * 7.5, 0.0, 1.0)
    seam_glow = np.clip(1.0 - edge_mask, 0.0, 1.0)

    nx = local_x * 0.8
    ny = local_y * 0.8
    nz = np.sqrt(np.maximum(0.05, 1.0 - np.clip(nx ** 2 + ny ** 2, 0.0, 0.95)))
    light = np.clip(-0.35 * nx - 0.45 * ny + 0.82 * nz, 0.0, 1.0)
    spec = np.power(np.clip(-0.20 * nx - 0.50 * ny + 0.84 * nz, 0.0, 1.0), 16.0)

    fbm = _tileable_fbm(w, h, octaves=4, seed=102)

    r = (65 + 155 * light + 30 * fbm + 150 * spec) * edge_mask + 255 * seam_glow * (0.6 + 0.4 * fbm)
    g = (12 + 28 * light + 115 * spec) * edge_mask + 95 * seam_glow * fbm
    b = (16 + 24 * light + 75 * spec) * edge_mask + 15 * seam_glow

    arr = np.stack([r, g, b], axis=-1)
    _save_rgba(arr, "enemy_scales.png")


def create_obstacle_textures():
    """Generates high-detail 512x512 obstacle & architectural textures."""
    w = h = TEX_SIZE
    y_idx, x_idx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = x_idx / w
    v = y_idx / h

    # 1. Realistic Tree Bark (deep vertical fissures + moss specks)
    fbm_bark = _tileable_fbm(w, h, octaves=5, seed=201)
    ridges = np.sin(u * 28.0 * np.pi + fbm_bark * 6.5)
    fissure = np.clip((ridges + 1.0) * 0.5, 0.0, 1.0) ** 0.75
    moss_mask = np.clip((fbm_bark - 0.68) * 4.5, 0.0, 1.0)
    r = (38 + 78 * fissure + 18 * fbm_bark) * (1.0 - moss_mask) + 48 * moss_mask
    g = (24 + 52 * fissure + 12 * fbm_bark) * (1.0 - moss_mask) + 115 * moss_mask
    b = (14 + 28 * fissure + 8 * fbm_bark) * (1.0 - moss_mask) + 38 * moss_mask
    _save_rgba(np.stack([r, g, b], axis=-1), "bark.png")

    # 2. Pine Needles (layered conifer foliage clusters with sunlit needles)
    fbm_pine = _tileable_fbm(w, h, octaves=5, seed=202)
    needle_pat = np.sin((u * 40.0 + v * 20.0) * np.pi + fbm_pine * 8.0) * np.cos((u * 20.0 - v * 40.0) * np.pi + fbm_pine * 6.0)
    shade = 0.5 + 0.35 * fbm_pine + 0.25 * needle_pat
    r = 16 + 34 * shade
    g = 68 + 112 * shade
    b = 26 + 48 * shade
    img_pine = _save_rgba(np.stack([r, g, b], axis=-1), "pine_needles.png")
    draw = ImageDraw.Draw(img_pine)
    rng = random.Random(202)
    for _ in range(1400):
        x1, y1 = rng.randint(0, w - 1), rng.randint(0, h - 1)
        ang = rng.uniform(0, math.pi * 2)
        ln = rng.randint(8, 22)
        x2, y2 = x1 + ln * math.cos(ang), y1 + ln * math.sin(ang)
        draw.line([(x1, y1), (x2, y2)], fill=(rng.randint(25, 65), rng.randint(120, 200), rng.randint(45, 85), 210), width=2)
    img_pine.save(os.path.join(TEXTURES_DIR, "pine_needles.png"))

    # 3. Stone Brick (3D beveled castle masonry with mortar joints & weathering)
    fbm_stone = _tileable_fbm(w, h, octaves=4, seed=203)
    rows_b, cols_b = 8, 4
    by = (v * rows_b) % 1.0
    row_num = np.floor(v * rows_b)
    bx = (u * cols_b + (row_num % 2) * 0.5) % 1.0
    # Bevel mask near mortar joints
    edge_x = np.minimum(bx, 1.0 - bx) * cols_b
    edge_y = np.minimum(by, 1.0 - by) * rows_b
    mortar = np.clip(np.minimum(edge_x, edge_y) * 8.0 - 0.25, 0.0, 1.0)
    bevel_light = (1.0 - by) * 0.25 + (1.0 - bx) * 0.15
    base_val = 75 + 55 * fbm_stone + 40 * bevel_light
    r = base_val * mortar + 28 * (1.0 - mortar)
    g = (base_val + 4) * mortar + 30 * (1.0 - mortar)
    b = (base_val + 10) * mortar + 34 * (1.0 - mortar)
    _save_rgba(np.stack([r, g, b], axis=-1), "stone_brick.png")

    # 4. Industrial Metal Crate with Brushed Steel & Hazard Stripes
    fbm_metal = _tileable_fbm(w, h, octaves=4, seed=204)
    brushed = 0.5 + 0.5 * np.sin(v * 180.0 * np.pi + fbm_metal * 3.0)
    base_m = 68 + 38 * fbm_metal + 16 * brushed
    img_crate = _save_rgba(np.stack([base_m, base_m + 5, base_m + 12], axis=-1), "metal_crate.png")
    draw = ImageDraw.Draw(img_crate)
    # Recessed metallic frame & cross braces
    draw.rectangle([10, 10, w - 10, h - 10], outline=(165, 175, 190, 255), width=12)
    draw.rectangle([22, 22, w - 22, h - 22], outline=(35, 38, 45, 255), width=4)
    # Diagonal hazard band across center
    band_y1, band_y2 = int(h * 0.36), int(h * 0.64)
    draw.rectangle([16, band_y1, w - 16, band_y2], fill=(28, 30, 34, 255))
    for i in range(-h, w + h, 44):
        draw.polygon([(i, band_y1), (i + 24, band_y1), (i + 56, band_y2), (i + 32, band_y2)], fill=(245, 190, 20, 255))
    draw.rectangle([16, band_y1, w - 16, band_y2], outline=(20, 22, 25, 255), width=5)
    # Corner bolts
    for rx, ry in [(34, 34), (w - 34, 34), (34, h - 34), (w - 34, h - 34)]:
        draw.ellipse([rx - 8, ry - 8, rx + 8, ry + 8], fill=(200, 210, 220, 255), outline=(40, 45, 50, 255), width=2)
    img_crate.save(os.path.join(TEXTURES_DIR, "metal_crate.png"))

    # 5. Ancient Egyptian Hieroglyph Sandstone
    fbm_sand = _tileable_fbm(w, h, octaves=4, seed=205)
    r = 185 + 45 * fbm_sand
    g = 148 + 38 * fbm_sand
    b = 92 + 28 * fbm_sand
    img_rune = _save_rgba(np.stack([r, g, b], axis=-1), "sandstone_rune.png")
    draw = ImageDraw.Draw(img_rune)
    for y in range(32, h, 64):
        draw.line([(0, y), (w, y)], fill=(120, 88, 45, 220), width=4)
        draw.line([(0, y + 3), (w, y + 3)], fill=(245, 215, 145, 180), width=2)
        for x in range(32, w, 64):
            # Golden inlaid solar disc & ankh motif
            draw.ellipse([x - 14, y + 14, x + 14, y + 42], fill=(240, 195, 55, 210), outline=(115, 80, 35, 230), width=3)
            draw.line([(x, y + 42), (x, y + 56)], fill=(115, 80, 35, 230), width=3)
            draw.line([(x - 10, y + 48), (x + 10, y + 48)], fill=(115, 80, 35, 230), width=3)
    img_rune.save(os.path.join(TEXTURES_DIR, "sandstone_rune.png"))

    # 6. Magma / Volcanic Basalt with glowing cracks
    fbm_magma = _tileable_fbm(w, h, octaves=5, seed=206)
    cracks = np.clip(1.0 - np.abs(np.sin((u * 6.0 + fbm_magma * 2.2) * np.pi) * np.cos((v * 6.0 - fbm_magma * 2.2) * np.pi)) * 4.5, 0.0, 1.0)
    rock_shade = 28 + 38 * fbm_magma
    r = rock_shade * (1.0 - cracks) + 255 * cracks
    g = (rock_shade * 0.85) * (1.0 - cracks) + (80 + 145 * (cracks ** 2)) * cracks
    b = (rock_shade * 0.92) * (1.0 - cracks) + 20 * cracks
    _save_rgba(np.stack([r, g, b], axis=-1), "magma_rock.png", blur=0.6)

    # 7. Crystal Facet Texture (prismatic amethyst/quartz facets)
    fbm_cryst = _tileable_fbm(w, h, octaves=4, seed=207)
    facet1 = np.abs(np.sin((u * 8.0 + v * 4.0) * np.pi + fbm_cryst * 3.0))
    facet2 = np.abs(np.cos((u * 4.0 - v * 8.0) * np.pi + fbm_cryst * 3.0))
    gleam = np.power(np.clip(facet1 * facet2, 0.0, 1.0), 4.0)
    r = 130 + 95 * facet1 + 120 * gleam
    g = 80 + 110 * facet2 + 150 * gleam
    b = 200 + 55 * fbm_cryst + 55 * gleam
    _save_rgba(np.stack([r, g, b], axis=-1), "crystal_facet.png")

    # 8. Cyberpunk Skyscraper Facade (lit neon windows)
    img_bldg = Image.new("RGBA", (w, h), (16, 20, 36, 255))
    draw = ImageDraw.Draw(img_bldg)
    rng = random.Random(208)
    win_w, win_h = 20, 14
    for wy in range(12, h - 12, 24):
        for wx in range(12, w - 12, 32):
            lit = rng.random()
            if lit > 0.35:
                col = (0, 235, 255, 255) if rng.random() > 0.3 else (255, 45, 165, 255)
            else:
                col = (28, 36, 62, 255)
            draw.rectangle([wx, wy, wx + win_w, wy + win_h], fill=col, outline=(10, 14, 24, 255), width=2)
    img_bldg.save(os.path.join(TEXTURES_DIR, "cyber_building.png"))


def create_forest_ground():
    """1. Emerald Forest: Lush multi-layered moss, grass blades, clover patches & wildflowers."""
    w = h = TEX_SIZE
    fbm1 = _tileable_fbm(w, h, octaves=5, seed=1)
    fbm2 = _tileable_fbm(w, h, octaves=4, seed=11)
    r = 24 + 36 * fbm1 + 14 * fbm2
    g = 92 + 78 * fbm1 + 25 * fbm2
    b = 32 + 38 * fbm1 + 10 * fbm2
    img = _save_rgba(np.stack([r, g, b], axis=-1), "ground_forest.png")
    draw = ImageDraw.Draw(img)
    rng = random.Random(1)
    # Detailed grass blades
    for _ in range(2200):
        gx, gy = rng.randint(0, w - 1), rng.randint(0, h - 1)
        ln = rng.randint(5, 13)
        dx = rng.randint(-4, 4)
        col = (rng.randint(25, 65), rng.randint(135, 215), rng.randint(35, 75), 210)
        draw.line([(gx, gy), (gx + dx, gy - ln)], fill=col, width=2)
    # Small forest wildflowers & pebbles
    for _ in range(75):
        fx, fy = rng.randint(6, w - 6), rng.randint(6, h - 6)
        fcol = rng.choice([(255, 235, 80, 240), (240, 245, 255, 240), (190, 130, 255, 230)])
        draw.ellipse([fx - 3, fy - 3, fx + 3, fy + 3], fill=fcol)
    img.save(os.path.join(TEXTURES_DIR, "ground_forest.png"))


def create_desert_ground():
    """2. Golden Desert: Wind-sculpted 3D sand ripples with sunlit crests and desert stones."""
    w = h = TEX_SIZE
    y_idx, x_idx = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = x_idx / w, y_idx / h
    fbm = _tileable_fbm(w, h, octaves=5, seed=2)
    ripples = np.sin((v * 18.0 + u * 4.0) * np.pi + fbm * 4.2)
    crest = 0.5 + 0.5 * ripples
    r = 188 + 52 * crest + 16 * fbm
    g = 142 + 46 * crest + 14 * fbm
    b = 76 + 34 * crest + 10 * fbm
    _save_rgba(np.stack([r, g, b], axis=-1), "ground_desert.png")


def create_ocean_ground():
    """3. Abyssal Ocean: Deep turquoise seabed with bright intersecting water caustic networks."""
    w = h = TEX_SIZE
    y_idx, x_idx = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = x_idx / w, y_idx / h
    fbm1 = _tileable_fbm(w, h, octaves=4, seed=3)
    fbm2 = _tileable_fbm(w, h, octaves=4, seed=33)
    c1 = np.abs(np.sin((u * 8.0 + fbm1 * 2.5) * np.pi) + np.cos((v * 8.0 - fbm2 * 2.5) * np.pi))
    caustic = np.power(np.clip(1.0 - c1 * 0.55, 0.0, 1.0), 2.5)
    r = 10 + 35 * fbm1 + 115 * caustic
    g = 58 + 65 * fbm1 + 165 * caustic
    b = 98 + 75 * fbm1 + 150 * caustic
    _save_rgba(np.stack([r, g, b], axis=-1), "ground_ocean.png")


def create_space_ground():
    """4. Deep Space: Cosmic violet-blue nebula with starfield and starship hull deck grid."""
    w = h = TEX_SIZE
    fbm1 = _tileable_fbm(w, h, octaves=5, seed=4)
    fbm2 = _tileable_fbm(w, h, octaves=4, seed=44)
    r = 12 + 65 * (fbm1 ** 2) + 35 * fbm2
    g = 10 + 28 * fbm1 + 55 * (fbm2 ** 2)
    b = 34 + 115 * fbm1 + 85 * fbm2
    img = _save_rgba(np.stack([r, g, b], axis=-1), "ground_space.png")
    draw = ImageDraw.Draw(img)
    # Subtle starship hex/grid lines
    step = 64
    for i in range(0, w, step):
        draw.line([(i, 0), (i, h)], fill=(95, 70, 185, 90), width=2)
        draw.line([(0, i), (w, i)], fill=(95, 70, 185, 90), width=2)
    rng = random.Random(4)
    for _ in range(280):
        sx, sy = rng.randint(2, w - 3), rng.randint(2, h - 3)
        sr = rng.choice([1, 1, 2])
        scol = rng.choice([(255, 255, 255, 245), (170, 225, 255, 235), (255, 190, 250, 235)])
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=scol)
    img.save(os.path.join(TEXTURES_DIR, "ground_space.png"))


def create_factory_ground():
    """5. Cyber Factory: Diamond-tread industrial steel plating with rivets & glowing seams."""
    w = h = TEX_SIZE
    y_idx, x_idx = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = x_idx / w, y_idx / h
    fbm = _tileable_fbm(w, h, octaves=4, seed=5)
    tread = np.abs(np.sin(u * 64 * np.pi) * np.cos(v * 64 * np.pi))
    base = 46 + 24 * fbm + 22 * tread
    img = _save_rgba(np.stack([base, base + 3, base + 8], axis=-1), "ground_factory.png")
    draw = ImageDraw.Draw(img)
    step = 128
    for x in range(0, w, step):
        for y in range(0, h, step):
            draw.rectangle([x + 3, y + 3, x + step - 3, y + step - 3], outline=(28, 30, 35, 255), width=4)
            draw.rectangle([x + 6, y + 6, x + step - 6, y + step - 6], outline=(105, 112, 125, 180), width=2)
            for rx, ry in [(x + 14, y + 14), (x + step - 14, y + 14), (x + 14, y + step - 14), (x + step - 14, y + step - 14)]:
                draw.ellipse([rx - 4, ry - 4, rx + 4, ry + 4], fill=(165, 175, 185, 255))
    img.save(os.path.join(TEXTURES_DIR, "ground_factory.png"))


def create_city_ground():
    """6. Neon Metropolis: Wet dark cyberpunk asphalt with glowing cyan & magenta circuit reflections."""
    w = h = TEX_SIZE
    fbm = _tileable_fbm(w, h, octaves=5, seed=6)
    r = 14 + 26 * (fbm ** 2)
    g = 16 + 32 * fbm
    b = 34 + 55 * fbm
    img = _save_rgba(np.stack([r, g, b], axis=-1), "ground_city.png")
    draw = ImageDraw.Draw(img)
    step = 64
    for i in range(0, w, step):
        col_v = (0, 230, 255, 150) if (i // step) % 2 == 0 else (255, 0, 140, 150)
        draw.line([(i, 0), (i, h)], fill=col_v, width=2)
        draw.line([(0, i), (w, i)], fill=col_v, width=2)
    for x in range(0, w, step):
        for y in range(0, h, step):
            draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(200, 250, 255, 220))
    img.save(os.path.join(TEXTURES_DIR, "ground_city.png"))


def create_arctic_ground():
    """7. Frozen Tundra: Translucent fractured glacier ice with deep blue crevices & snow drifts."""
    w = h = TEX_SIZE
    y_idx, x_idx = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = x_idx / w, y_idx / h
    fbm1 = _tileable_fbm(w, h, octaves=5, seed=7)
    fbm2 = _tileable_fbm(w, h, octaves=4, seed=77)
    crack = np.clip(1.0 - np.abs(np.sin((u * 5.0 + fbm1 * 2.0) * np.pi) * np.cos((v * 5.0 - fbm2 * 2.0) * np.pi)) * 6.0, 0.0, 1.0)
    r = (165 + 78 * fbm1) * (1.0 - crack) + 65 * crack
    g = (210 + 42 * fbm1) * (1.0 - crack) + 155 * crack
    b = (238 + 17 * fbm1) * (1.0 - crack) + 235 * crack
    _save_rgba(np.stack([r, g, b], axis=-1), "ground_arctic.png")


def create_lava_ground():
    """8. Lava Inferno: Cooled dark volcanic basalt crust floating over glowing rivers of magma."""
    w = h = TEX_SIZE
    y_idx, x_idx = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = x_idx / w, y_idx / h
    fbm1 = _tileable_fbm(w, h, octaves=5, seed=8)
    fbm2 = _tileable_fbm(w, h, octaves=4, seed=88)
    veins = np.clip(1.0 - np.abs(np.sin((u * 5.0 + fbm1 * 2.4) * np.pi) + np.cos((v * 5.0 - fbm2 * 2.4) * np.pi)) * 1.4, 0.0, 1.0)
    crust = 28 + 35 * fbm1
    r = crust * (1.0 - veins) + 255 * veins
    g = (crust * 0.75) * (1.0 - veins) + (65 + 165 * (veins ** 2)) * veins
    b = (crust * 0.80) * (1.0 - veins) + 15 * veins
    _save_rgba(np.stack([r, g, b], axis=-1), "ground_lava.png", blur=0.5)


def create_crystal_ground():
    """9. Crystal Caverns: Prismatic amethyst crystal floor with geometric facets & sparkles."""
    w = h = TEX_SIZE
    y_idx, x_idx = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = x_idx / w, y_idx / h
    fbm = _tileable_fbm(w, h, octaves=5, seed=9)
    f1 = np.abs(np.sin((u * 10.0 + v * 6.0) * np.pi + fbm * 3.0))
    f2 = np.abs(np.cos((u * 6.0 - v * 10.0) * np.pi + fbm * 3.0))
    spark = np.power(f1 * f2, 5.0)
    r = 48 + 95 * f1 + 110 * spark
    g = 20 + 55 * f2 + 135 * spark
    b = 85 + 125 * fbm + 70 * spark
    _save_rgba(np.stack([r, g, b], axis=-1), "ground_crystal.png")


def create_jungle_ground():
    """10. Lost Jungle: Overgrown Mayan temple flagstones with rich rainforest moss & vines."""
    w = h = TEX_SIZE
    fbm1 = _tileable_fbm(w, h, octaves=5, seed=10)
    fbm2 = _tileable_fbm(w, h, octaves=4, seed=110)
    stone_mask = np.clip((fbm2 - 0.52) * 5.0, 0.0, 1.0)
    r = (22 + 38 * fbm1) * (1.0 - stone_mask) + (95 + 35 * fbm1) * stone_mask
    g = (85 + 85 * fbm1) * (1.0 - stone_mask) + (100 + 30 * fbm1) * stone_mask
    b = (28 + 32 * fbm1) * (1.0 - stone_mask) + (75 + 25 * fbm1) * stone_mask
    img = _save_rgba(np.stack([r, g, b], axis=-1), "ground_jungle.png")
    draw = ImageDraw.Draw(img)
    rng = random.Random(10)
    for _ in range(900):
        x, y = rng.randint(0, w - 1), rng.randint(0, h - 1)
        ang = rng.uniform(0, math.pi * 2)
        ln = rng.randint(8, 20)
        draw.line([(x, y), (x + ln * math.cos(ang), y + ln * math.sin(ang))], fill=(20, rng.randint(120, 195), 40, 190), width=2)
    img.save(os.path.join(TEXTURES_DIR, "ground_jungle.png"))


def create_sky_ground():
    """11. Sky Sanctuary: Celestial white-and-gold marble plaza tiles with golden filigree."""
    w = h = TEX_SIZE
    y_idx, x_idx = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = x_idx / w, y_idx / h
    fbm = _tileable_fbm(w, h, octaves=5, seed=11)
    vein = np.power(np.abs(np.sin((u * 4.0 + v * 4.0) * np.pi + fbm * 4.5)), 8.0)
    r = 215 + 32 * fbm + 15 * vein
    g = 225 + 25 * fbm - 10 * vein
    b = 242 + 13 * fbm - 65 * vein
    img = _save_rgba(np.stack([r, g, b], axis=-1), "ground_sky.png")
    draw = ImageDraw.Draw(img)
    step = 128
    for i in range(0, w, step):
        draw.line([(i, 0), (i, h)], fill=(235, 195, 75, 200), width=3)
        draw.line([(0, i), (w, i)], fill=(235, 195, 75, 200), width=3)
    img.save(os.path.join(TEXTURES_DIR, "ground_sky.png"))


def create_toxic_ground():
    """12. Toxic Wasteland: Corroded industrial grating over bubbling neon-green radioactive sludge."""
    w = h = TEX_SIZE
    fbm1 = _tileable_fbm(w, h, octaves=5, seed=12)
    fbm2 = _tileable_fbm(w, h, octaves=4, seed=120)
    pool = np.clip((fbm1 - 0.42) * 3.8, 0.0, 1.0)
    r = (42 + 28 * fbm2) * (1.0 - pool) + (55 + 85 * (pool ** 2)) * pool
    g = (48 + 32 * fbm2) * (1.0 - pool) + (185 + 70 * pool) * pool
    b = (32 + 22 * fbm2) * (1.0 - pool) + (25 + 45 * pool) * pool
    img = _save_rgba(np.stack([r, g, b], axis=-1), "ground_toxic.png")
    draw = ImageDraw.Draw(img)
    rng = random.Random(12)
    for _ in range(65):
        bx, by = rng.randint(10, w - 10), rng.randint(10, h - 10)
        br = rng.randint(4, 14)
        draw.ellipse([bx - br, by - br, bx + br, by + br], outline=(160, 255, 80, 190), width=2)
    img.save(os.path.join(TEXTURES_DIR, "ground_toxic.png"))


def create_swamp_ground():
    """13. Mystic Swamp: Murky bayou mud, mossy algae mats, and bioluminescent spore ripples."""
    w = h = TEX_SIZE
    fbm1 = _tileable_fbm(w, h, octaves=5, seed=13)
    fbm2 = _tileable_fbm(w, h, octaves=4, seed=130)
    algae = np.clip((fbm1 - 0.48) * 3.5, 0.0, 1.0)
    r = (38 + 25 * fbm2) * (1.0 - algae) + (52 + 35 * fbm1) * algae
    g = (42 + 28 * fbm2) * (1.0 - algae) + (98 + 55 * fbm1) * algae
    b = (28 + 20 * fbm2) * (1.0 - algae) + (36 + 25 * fbm1) * algae
    _save_rgba(np.stack([r, g, b], axis=-1), "ground_swamp.png")


def create_necropolis_ground():
    """14. Ancient Necropolis: Carved pharaonic sandstone slabs with golden hieroglyph inlays."""
    w = h = TEX_SIZE
    fbm = _tileable_fbm(w, h, octaves=5, seed=14)
    r = 152 + 48 * fbm
    g = 118 + 38 * fbm
    b = 72 + 28 * fbm
    img = _save_rgba(np.stack([r, g, b], axis=-1), "ground_necropolis.png")
    draw = ImageDraw.Draw(img)
    step = 85
    for x in range(0, w, step):
        draw.line([(x, 0), (x, h)], fill=(85, 62, 34, 240), width=3)
    for y in range(0, h, step):
        draw.line([(0, y), (w, y)], fill=(85, 62, 34, 240), width=3)
    img.save(os.path.join(TEXTURES_DIR, "ground_necropolis.png"))


def create_steampunk_ground():
    """15. Steampunk Sky: Polished riveted brass & copper deck plates with engraved clockwork rings."""
    w = h = TEX_SIZE
    fbm = _tileable_fbm(w, h, octaves=4, seed=15)
    r = 148 + 46 * fbm
    g = 98 + 36 * fbm
    b = 48 + 22 * fbm
    img = _save_rgba(np.stack([r, g, b], axis=-1), "ground_steampunk.png")
    draw = ImageDraw.Draw(img)
    step = 128
    for x in range(0, w, step):
        for y in range(0, h, step):
            draw.rectangle([x + 4, y + 4, x + step - 4, y + step - 4], outline=(85, 52, 24, 255), width=4)
            cx, cy = x + step // 2, y + step // 2
            draw.ellipse([cx - 36, cy - 36, cx + 36, cy + 36], outline=(215, 165, 75, 160), width=3)
            for rx, ry in [(x + 14, y + 14), (x + step - 14, y + 14), (x + 14, y + step - 14), (x + step - 14, y + step - 14)]:
                draw.ellipse([rx - 4, ry - 4, rx + 4, ry + 4], fill=(235, 195, 95, 255))
    img.save(os.path.join(TEXTURES_DIR, "ground_steampunk.png"))


def create_event_horizon_ground():
    """16. Event Horizon: Swirling black-hole accretion plasma filaments & warped gravity grid."""
    w = h = TEX_SIZE
    y_idx, x_idx = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = x_idx / w, y_idx / h
    fbm = _tileable_fbm(w, h, octaves=5, seed=16)
    swirl = 0.5 + 0.5 * np.sin((u * 6.0 + v * 6.0) * np.pi + fbm * 6.0)
    r = 10 + 185 * (swirl ** 3)
    g = 8 + 65 * (swirl ** 4)
    b = 22 + 165 * ((1.0 - swirl) ** 2) * fbm
    _save_rgba(np.stack([r, g, b], axis=-1), "ground_event_horizon.png")


def create_dungeon_ground():
    """17. Dragon Dungeon: Dark gothic flagstones with glowing ember mortar cracks."""
    w = h = TEX_SIZE
    y_idx, x_idx = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = x_idx / w, y_idx / h
    fbm = _tileable_fbm(w, h, octaves=4, seed=17)
    rows_b, cols_b = 8, 6
    by = (v * rows_b) % 1.0
    row_num = np.floor(v * rows_b)
    bx = (u * cols_b + (row_num % 2) * 0.5) % 1.0
    edge = np.minimum(np.minimum(bx, 1.0 - bx) * cols_b, np.minimum(by, 1.0 - by) * rows_b)
    stone = np.clip(edge * 9.0 - 0.3, 0.0, 1.0)
    ember = (1.0 - stone) * fbm
    base = 44 + 34 * fbm
    r = base * stone + 220 * ember
    g = (base + 2) * stone + 55 * ember
    b = (base + 8) * stone + 25 * ember
    _save_rgba(np.stack([r, g, b], axis=-1), "ground_dungeon.png")


def create_quantum_ground():
    """18. Quantum Citadel: High-tech holographic quantum circuit matrix with cyan & magenta nodes."""
    w = h = TEX_SIZE
    fbm = _tileable_fbm(w, h, octaves=4, seed=18)
    r = 8 + 25 * fbm
    g = 10 + 30 * fbm
    b = 26 + 55 * fbm
    img = _save_rgba(np.stack([r, g, b], axis=-1), "ground_quantum.png")
    draw = ImageDraw.Draw(img)
    step = 64
    for x in range(0, w, step):
        draw.line([(x, 0), (x, h)], fill=(0, 240, 255, 190), width=2)
    for y in range(0, h, step):
        draw.line([(0, y), (w, y)], fill=(255, 0, 150, 190), width=2)
    for x in range(0, w, step):
        for y in range(0, h, step):
            draw.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 255, 255, 245), outline=(0, 240, 255, 255), width=2)
    img.save(os.path.join(TEXTURES_DIR, "ground_quantum.png"))


def ensure_textures_exist(force=False):
    ensure_dir()
    required = [
        "snake_scales.png", "enemy_scales.png", "bark.png", "pine_needles.png",
        "stone_brick.png", "metal_crate.png", "sandstone_rune.png", "magma_rock.png",
        "crystal_facet.png", "cyber_building.png", "ground_forest.png", "ground_desert.png",
        "ground_ocean.png", "ground_space.png", "ground_factory.png", "ground_city.png",
        "ground_arctic.png", "ground_lava.png", "ground_crystal.png", "ground_jungle.png",
        "ground_sky.png", "ground_toxic.png", "ground_swamp.png", "ground_necropolis.png",
        "ground_steampunk.png", "ground_event_horizon.png", "ground_dungeon.png", "ground_quantum.png"
    ]
    if force or any(not os.path.exists(os.path.join(TEXTURES_DIR, f)) for f in required):
        create_all_textures()


def create_all_textures():
    ensure_dir()
    print("Generating HD 512x512 procedural textures...")
    create_snake_scales()
    create_enemy_scales()
    create_obstacle_textures()
    create_forest_ground()
    create_desert_ground()
    create_ocean_ground()
    create_space_ground()
    create_factory_ground()
    create_city_ground()
    create_arctic_ground()
    create_lava_ground()
    create_crystal_ground()
    create_jungle_ground()
    create_sky_ground()
    create_toxic_ground()
    create_swamp_ground()
    create_necropolis_ground()
    create_steampunk_ground()
    create_event_horizon_ground()
    create_dungeon_ground()
    create_quantum_ground()
    print("All 28 HD 512x512 textures successfully generated in 'textures/' directory!")


if __name__ == "__main__":
    create_all_textures()
