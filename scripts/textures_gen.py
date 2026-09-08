"""
Procedural High-Detail Texture Generator for 3D Snake.
Generates tileable, detailed 256x256 and 512x512 textures for terrain, snake skins,
walls, obstacles, and biomes using Pillow.
"""
import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXTURES_DIR = os.path.join(PROJECT_ROOT, "textures")

def ensure_dir():
    if not os.path.exists(TEXTURES_DIR):
        os.makedirs(TEXTURES_DIR)

def gen_noise(width, height, factor=0.5):
    img = Image.new("RGBA", (width, height))
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            v = int(random.uniform(0, 255) * factor)
            pixels[x, y] = (v, v, v, 255)
    return img

def create_snake_scales():
    """Reptilian hexagonal scale pattern."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (40, 180, 85, 255))
    draw = ImageDraw.Draw(img)
    
    r = 16
    for row in range(-1, int(h / (r * 1.5)) + 2):
        for col in range(-1, int(w / (r * math.sqrt(3))) + 2):
            cx = col * r * math.sqrt(3) + (r * math.sqrt(3) / 2.0 if row % 2 == 1 else 0)
            cy = row * r * 1.5
            
            # Hexagon points
            points = []
            for i in range(6):
                angle = math.radians(i * 60 + 30)
                px = cx + r * 0.95 * math.cos(angle)
                py = cy + r * 0.95 * math.sin(angle)
                points.append((px, py))
            
            shade = random.randint(160, 220)
            col_scale = (int(35 * shade / 200), int(190 * shade / 200), int(85 * shade / 200), 255)
            draw.polygon(points, fill=col_scale, outline=(20, 110, 50, 255))
            
            # Highlight dot in center
            draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=(100, 240, 150, 220))
            
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img.save(os.path.join(TEXTURES_DIR, "snake_scales.png"))

def create_enemy_scales():
    """Menacing crimson dragon scale pattern."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (180, 30, 30, 255))
    draw = ImageDraw.Draw(img)
    
    r = 16
    for row in range(-1, int(h / (r * 1.5)) + 2):
        for col in range(-1, int(w / (r * math.sqrt(3))) + 2):
            cx = col * r * math.sqrt(3) + (r * math.sqrt(3) / 2.0 if row % 2 == 1 else 0)
            cy = row * r * 1.5
            
            points = []
            for i in range(6):
                angle = math.radians(i * 60 + 30)
                px = cx + r * 0.95 * math.cos(angle)
                py = cy + r * 0.95 * math.sin(angle)
                points.append((px, py))
            
            shade = random.randint(140, 230)
            col_scale = (int(200 * shade / 200), int(30 * shade / 200), int(30 * shade / 200), 255)
            draw.polygon(points, fill=col_scale, outline=(90, 15, 15, 255))
            draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=(255, 120, 60, 200))
            
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img.save(os.path.join(TEXTURES_DIR, "enemy_scales.png"))

def create_forest_ground():
    """Forest ground: Rich moss, grass tufts, fallen pine needles."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (38, 125, 52, 255))
    draw = ImageDraw.Draw(img)
    
    # Grass tufts
    for _ in range(800):
        gx = random.randint(0, w)
        gy = random.randint(0, h)
        length = random.randint(4, 9)
        c = (random.randint(25, 50), random.randint(140, 210), random.randint(35, 70), 220)
        draw.line((gx, gy, gx + random.randint(-3, 3), gy - length), fill=c, width=1)
        
    # Dark moss patches
    for _ in range(40):
        mx = random.randint(0, w)
        my = random.randint(0, h)
        rad = random.randint(8, 18)
        draw.ellipse((mx - rad, my - rad, mx + rad, my + rad), fill=(28, 90, 40, 90))
        
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    img.save(os.path.join(TEXTURES_DIR, "ground_forest.png"))

def create_desert_ground():
    """Desert sand: Smooth wind ripple dunes and golden grains."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (220, 175, 95, 255))
    draw = ImageDraw.Draw(img)
    
    # Sand dune ripples
    for y in range(0, h, 8):
        for x in range(w):
            offset = int(math.sin(x * 0.08) * 3)
            c = (235, 195, 115, 140) if (y // 8) % 2 == 0 else (195, 145, 75, 140)
            draw.point((x, y + offset), fill=c)
            
    # Grains
    for _ in range(1200):
        gx = random.randint(0, w - 1)
        gy = random.randint(0, h - 1)
        c = (random.randint(210, 245), random.randint(165, 205), random.randint(80, 120), 180)
        draw.point((gx, gy), fill=c)
        
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    img.save(os.path.join(TEXTURES_DIR, "ground_desert.png"))

def create_ocean_ground():
    """Ocean caustics pattern with deep sea gradients."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (18, 65, 95, 255))
    draw = ImageDraw.Draw(img)
    
    # Water caustic rings
    for _ in range(70):
        cx = random.randint(0, w)
        cy = random.randint(0, h)
        rw = random.randint(12, 35)
        rh = random.randint(8, 25)
        draw.ellipse((cx - rw, cy - rh, cx + rw, cy + rh), outline=(0, 220, 255, 90), width=2)
        
    img = img.filter(ImageFilter.GaussianBlur(2.0))
    img.save(os.path.join(TEXTURES_DIR, "ground_ocean.png"))

def create_space_ground():
    """Deep space starfield, nebulae and cosmic dust."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (12, 10, 28, 255))
    draw = ImageDraw.Draw(img)
    
    # Nebula cloud
    for _ in range(50):
        nx = random.randint(0, w)
        ny = random.randint(0, h)
        nr = random.randint(20, 60)
        draw.ellipse((nx - nr, ny - nr, nx + nr, ny + nr), fill=(120, 40, 200, 30))
        draw.ellipse((nx - nr//2, ny - nr//2, nx + nr//2, ny + nr//2), fill=(40, 100, 240, 35))
        
    # Stars
    for _ in range(250):
        sx = random.randint(0, w - 1)
        sy = random.randint(0, h - 1)
        bright = random.randint(180, 255)
        draw.point((sx, sy), fill=(bright, bright, 255, 255))
        if random.random() < 0.08:
            draw.ellipse((sx - 1, sy - 1, sx + 1, sy + 1), fill=(255, 255, 255, 240))
            
    img.save(os.path.join(TEXTURES_DIR, "ground_space.png"))

def create_factory_ground():
    """Industrial metal tread plate with warning stripes."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (55, 58, 65, 255))
    draw = ImageDraw.Draw(img)
    
    # Metal grid plates
    step = 32
    for x in range(0, w, step):
        draw.line((x, 0, x, h), fill=(35, 38, 42, 255), width=2)
    for y in range(0, h, step):
        draw.line((0, y, w, y), fill=(35, 38, 42, 255), width=2)
        
    # Tread rivets
    for y in range(step // 2, h, step):
        for x in range(step // 2, w, step):
            draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(180, 185, 195, 255), outline=(20, 20, 25, 255))
            
    img.save(os.path.join(TEXTURES_DIR, "ground_factory.png"))

def create_city_ground():
    """Dark asphalt with neon cyber circuitry."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (26, 24, 40, 255))
    draw = ImageDraw.Draw(img)
    
    # Asphalt noise
    for _ in range(1500):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        v = random.randint(18, 45)
        draw.point((x, y), fill=(v, v, v + 8, 255))
        
    # Neon grid lines
    step = 64
    for x in range(0, w, step):
        draw.line((x, 0, x, h), fill=(0, 210, 255, 160), width=2)
    for y in range(0, h, step):
        draw.line((0, y, w, y), fill=(255, 0, 128, 160), width=2)
        
    img.save(os.path.join(TEXTURES_DIR, "ground_city.png"))

def create_arctic_ground():
    """Glacial ice crystals and packed snow."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (205, 235, 250, 255))
    draw = ImageDraw.Draw(img)
    
    # Ice cracks
    for _ in range(25):
        x1 = random.randint(0, w)
        y1 = random.randint(0, h)
        x2 = x1 + random.randint(-40, 40)
        y2 = y1 + random.randint(-40, 40)
        draw.line((x1, y1, x2, y2), fill=(130, 190, 235, 180), width=2)
        
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    img.save(os.path.join(TEXTURES_DIR, "ground_arctic.png"))

def create_lava_ground():
    """Basalt rock with glowing magma fissures."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (38, 20, 18, 255))
    draw = ImageDraw.Draw(img)
    
    # Magma fissures
    for _ in range(35):
        x1 = random.randint(0, w)
        y1 = random.randint(0, h)
        x2 = x1 + random.randint(-50, 50)
        y2 = y1 + random.randint(-50, 50)
        draw.line((x1, y1, x2, y2), fill=(255, 90, 20, 230), width=3)
        draw.line((x1, y1, x2, y2), fill=(255, 220, 40, 255), width=1)
        
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    img.save(os.path.join(TEXTURES_DIR, "ground_lava.png"))

def create_crystal_ground():
    """Amethyst and quartz geometric crystal facets."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (45, 20, 68, 255))
    draw = ImageDraw.Draw(img)
    
    step = 32
    for y in range(0, h, step):
        for x in range(0, w, step):
            c = (random.randint(130, 190), random.randint(40, 80), random.randint(210, 255), 180)
            draw.polygon([(x, y + step//2), (x + step//2, y), (x + step, y + step//2), (x + step//2, y + step)], fill=c, outline=(80, 20, 110, 255))
            
    img = img.filter(ImageFilter.GaussianBlur(0.5))
    img.save(os.path.join(TEXTURES_DIR, "ground_crystal.png"))

def create_jungle_ground():
    """Deep rainforest foliage with moss and soil."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (25, 80, 36, 255))
    draw = ImageDraw.Draw(img)
    
    for _ in range(800):
        x = random.randint(0, w)
        y = random.randint(0, h)
        r = random.randint(3, 7)
        draw.ellipse((x, y, x + r, y + r//2), fill=(40, random.randint(120, 180), 55, 180))
        
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    img.save(os.path.join(TEXTURES_DIR, "ground_jungle.png"))

def create_sky_ground():
    """Celestial clouds with gold filigree grid."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (170, 195, 230, 255))
    draw = ImageDraw.Draw(img)
    
    # Soft clouds
    for _ in range(40):
        cx = random.randint(0, w)
        cy = random.randint(0, h)
        cr = random.randint(25, 60)
        draw.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), fill=(245, 250, 255, 120))
        
    # Gold lines
    step = 48
    for x in range(0, w, step):
        draw.line((x, 0, x, h), fill=(240, 215, 80, 150), width=2)
    for y in range(0, h, step):
        draw.line((0, y, w, y), fill=(240, 215, 80, 150), width=2)
        
    img = img.filter(ImageFilter.GaussianBlur(0.7))
    img.save(os.path.join(TEXTURES_DIR, "ground_sky.png"))

def create_toxic_ground():
    """Toxic radioactive sludge with biohazard markings."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (30, 45, 20, 255))
    draw = ImageDraw.Draw(img)
    
    for _ in range(50):
        cx = random.randint(0, w)
        cy = random.randint(0, h)
        cr = random.randint(15, 45)
        draw.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), fill=(50, 235, 70, 100))
        
    # Yellow hazard lines
    for i in range(-w, w * 2, 40):
        draw.line((i, 0, i + h, h), fill=(220, 200, 30, 80), width=8)
        
    img = img.filter(ImageFilter.GaussianBlur(1.0))
    img.save(os.path.join(TEXTURES_DIR, "ground_toxic.png"))

def create_swamp_ground():
    """Murky swamp mud and algae blooms."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (38, 48, 30, 255))
    draw = ImageDraw.Draw(img)
    
    for _ in range(60):
        x = random.randint(0, w)
        y = random.randint(0, h)
        r = random.randint(10, 30)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(65, 85, 40, 140))
        
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    img.save(os.path.join(TEXTURES_DIR, "ground_swamp.png"))

def create_necropolis_ground():
    """Ancient cracked sandstone tiles."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (160, 125, 80, 255))
    draw = ImageDraw.Draw(img)
    
    step = 40
    for x in range(0, w, step):
        draw.line((x, 0, x, h), fill=(100, 75, 45, 255), width=2)
    for y in range(0, h, step):
        draw.line((0, y, w, y), fill=(100, 75, 45, 255), width=2)
        
    # Weathering cracks
    for _ in range(20):
        x = random.randint(0, w)
        y = random.randint(0, h)
        draw.line((x, y, x + random.randint(-15, 15), y + random.randint(-15, 15)), fill=(80, 55, 30, 200), width=1)
        
    img.save(os.path.join(TEXTURES_DIR, "ground_necropolis.png"))

def create_steampunk_ground():
    """Riveted brass plates and cogwork motifs."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (140, 95, 55, 255))
    draw = ImageDraw.Draw(img)
    
    step = 64
    for x in range(0, w, step):
        for y in range(0, h, step):
            draw.rectangle((x + 2, y + 2, x + step - 2, y + step - 2), fill=(160, 110, 65, 255), outline=(90, 60, 35, 255))
            # Corner rivets
            for rx, ry in [(x + 6, y + 6), (x + step - 6, y + 6), (x + 6, y + step - 6), (x + step - 6, y + step - 6)]:
                draw.ellipse((rx - 2, ry - 2, rx + 2, ry + 2), fill=(220, 180, 90, 255))
                
    img.save(os.path.join(TEXTURES_DIR, "ground_steampunk.png"))

def create_event_horizon_ground():
    """Black hole singularity accretion disk."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (8, 6, 16, 255))
    draw = ImageDraw.Draw(img)
    
    cx, cy = w // 2, h // 2
    for r in range(120, 10, -8):
        alpha = int((120 - r) * 2.1)
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 120, 30, alpha), width=3)
        draw.ellipse((cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4), outline=(160, 40, 255, alpha), width=2)
        
    img = img.filter(ImageFilter.GaussianBlur(1.0))
    img.save(os.path.join(TEXTURES_DIR, "ground_event_horizon.png"))

def create_dungeon_ground():
    """Medieval dungeon flagstones with moss."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (60, 62, 68, 255))
    draw = ImageDraw.Draw(img)
    
    step_x, step_y = 42, 28
    for row, y in enumerate(range(0, h, step_y)):
        x_shift = (step_x // 2) if row % 2 == 1 else 0
        for x in range(-step_x, w + step_x, step_x):
            bx = x + x_shift
            shade = random.randint(45, 75)
            draw.rectangle((bx + 2, y + 2, bx + step_x - 2, y + step_y - 2), fill=(shade, shade + 2, shade + 5, 255), outline=(30, 32, 36, 255))
            
    img.save(os.path.join(TEXTURES_DIR, "ground_dungeon.png"))

def create_quantum_ground():
    """Futuristic glowing quantum holographic matrix."""
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (10, 8, 22, 255))
    draw = ImageDraw.Draw(img)
    
    step = 32
    for x in range(0, w, step):
        draw.line((x, 0, x, h), fill=(0, 240, 255, 180), width=1)
    for y in range(0, h, step):
        draw.line((0, y, w, y), fill=(255, 0, 140, 180), width=1)
        
    for x in range(0, w, step):
        for y in range(0, h, step):
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 255, 255, 240))
            
    img.save(os.path.join(TEXTURES_DIR, "ground_quantum.png"))

def create_obstacle_textures():
    # 1. Tree Bark Texture
    w, h = 256, 256
    img = Image.new("RGBA", (w, h), (85, 55, 30, 255))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        for x in range(w):
            v = int(random.uniform(-18, 18))
            draw.point((x, y), fill=(max(0, 85 + v), max(0, 55 + v), max(0, 30 + v), 255))
    for x in range(0, w, 8):
        offset = random.randint(-2, 2)
        draw.line([(x + offset, 0), (x - offset, h)], fill=(45, 28, 15, 220), width=random.randint(1, 3))
    img = img.filter(ImageFilter.SMOOTH)
    img.save(os.path.join(TEXTURES_DIR, "bark.png"))

    # 2. Pine Needles Texture
    img = Image.new("RGBA", (w, h), (24, 95, 42, 255))
    draw = ImageDraw.Draw(img)
    for _ in range(600):
        x1 = random.randint(0, w)
        y1 = random.randint(0, h)
        length = random.randint(8, 20)
        angle = random.uniform(0, math.pi * 2)
        x2 = x1 + length * math.cos(angle)
        y2 = y1 + length * math.sin(angle)
        draw.line([(x1, y1), (x2, y2)], fill=(random.randint(15, 35), random.randint(110, 160), random.randint(40, 70), 255), width=2)
    img.save(os.path.join(TEXTURES_DIR, "pine_needles.png"))

    # 3. Dungeon & Castle Stone Bricks
    img = Image.new("RGBA", (w, h), (90, 95, 105, 255))
    draw = ImageDraw.Draw(img)
    brick_h, brick_w = 32, 64
    for row in range(h // brick_h + 1):
        y = row * brick_h
        draw.line([(0, y), (w, y)], fill=(40, 42, 48, 255), width=3)
        x_shift = (brick_w // 2) if row % 2 == 1 else 0
        for col in range(w // brick_w + 2):
            x = col * brick_w - x_shift
            draw.line([(x, y), (x, y + brick_h)], fill=(40, 42, 48, 255), width=3)
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img.save(os.path.join(TEXTURES_DIR, "stone_brick.png"))

    # 4. Industrial Metal Crate with Hazard Stripes
    img = Image.new("RGBA", (w, h), (70, 75, 85, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([6, 6, w - 6, h - 6], outline=(140, 150, 165, 255), width=8)
    for i in range(-50, w + 50, 24):
        draw.polygon([(i, 90), (i + 14, 90), (i + 34, 166), (i + 20, 166)], fill=(230, 180, 20, 255))
    draw.rectangle([6, 90, w - 6, 166], outline=(30, 30, 35, 255), width=3)
    img.save(os.path.join(TEXTURES_DIR, "metal_crate.png"))

    # 5. Ancient Egyptian Hieroglyph Sandstone
    img = Image.new("RGBA", (w, h), (210, 175, 115, 255))
    draw = ImageDraw.Draw(img)
    for y in range(20, h, 40):
        draw.line([(10, y), (w - 10, y)], fill=(150, 115, 65, 180), width=2)
        for x in range(30, w, 45):
            draw.ellipse([x - 8, y - 8, x + 8, y + 8], outline=(140, 105, 55, 220), width=2)
            draw.line([(x, y - 12), (x, y + 12)], fill=(140, 105, 55, 220), width=2)
    img.save(os.path.join(TEXTURES_DIR, "sandstone_rune.png"))

    # 6. Magma / Volcanic Basalt
    img = Image.new("RGBA", (w, h), (35, 30, 35, 255))
    draw = ImageDraw.Draw(img)
    for _ in range(40):
        x1 = random.randint(0, w)
        y1 = random.randint(0, h)
        x2 = x1 + random.randint(-40, 40)
        y2 = y1 + random.randint(-40, 40)
        draw.line([(x1, y1), (x2, y2)], fill=(255, random.randint(60, 140), 10, 255), width=random.randint(2, 4))
    img = img.filter(ImageFilter.GaussianBlur(radius=1.5))
    img.save(os.path.join(TEXTURES_DIR, "magma_rock.png"))

def create_all_textures():
    ensure_dir()
    print("Generating procedural textures...")
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
    print("All textures successfully generated in 'textures/' directory!")

if __name__ == "__main__":
    create_all_textures()
