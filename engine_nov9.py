import os
import sys
import math
import subprocess
import time
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1920
HEIGHT = 1080
FPS = 30

FONT_PATH_TITLE = "C:/Windows/Fonts/arialbd.ttf" if sys.platform == "win32" else "/usr/share/fonts/opentype/montserrat/MontserratAlternates-Bold.otf"
FONT_PATH_TEXT = "C:/Windows/Fonts/arial.ttf" if sys.platform == "win32" else "/usr/share/fonts/truetype/roboto/unhinted/RobotoCondensed-Medium.ttf"

try:
    font_bold = ImageFont.truetype(FONT_PATH_TITLE, 34)
    font_badge = ImageFont.truetype(FONT_PATH_TITLE, 22)
    font_small = ImageFont.truetype(FONT_PATH_TEXT, 18)
except Exception:
    font_bold = font_badge = font_small = ImageFont.load_default()


# ==========================================
# VECTOR ICONS (100% PURE VECTOR, NO EMOJIS, NO TOFU)
# ==========================================

def draw_vector_scissors(draw, cx, cy, scale=1.0, color=(245, 158, 11)):
    """Crisp vector scissors icon - guaranteed zero missing font glyphs."""
    r = int(8 * scale)
    # Finger rings
    draw.ellipse([cx - int(16 * scale) - r, cy + int(8 * scale) - r, 
                  cx - int(16 * scale) + r, cy + int(8 * scale) + r], outline=color, width=max(2, int(3 * scale)))
    draw.ellipse([cx + int(16 * scale) - r, cy + int(8 * scale) - r, 
                  cx + int(16 * scale) + r, cy + int(8 * scale) + r], outline=color, width=max(2, int(3 * scale)))
    # Pivot screw
    draw.ellipse([cx - int(3 * scale), cy - int(3 * scale), cx + int(3 * scale), cy + int(3 * scale)], fill=color)
    # Blades crossing
    draw.line([cx - int(16 * scale), cy + int(8 * scale), cx + int(14 * scale), cy - int(24 * scale)], fill=color, width=max(2, int(3 * scale)))
    draw.line([cx + int(16 * scale), cy + int(8 * scale), cx - int(14 * scale), cy - int(24 * scale)], fill=color, width=max(2, int(3 * scale)))


# ==========================================
# ADVANCED ARTICULATED CHARACTER RENDERER
# ==========================================

def draw_character(draw, x, y, scale=1.0, walk_phase=0.0, 
                   skin_color=(255, 240, 230), hair_color=(45, 35, 30), 
                   clothes_color=(59, 130, 246), pants_color=(30, 41, 59),
                   action="walk", facing=1):
    """
    Articulated 2-segment vector human with natural kinematics:
    actions: 'walk', 'climb_celebrate', 'stand_hero', 'wave_flag', 'work'
    """
    bounce = math.sin(walk_phase * 2) * (3.5 * scale) if (walk_phase != 0 and action in ("walk", "walk_phone")) else 0
    cur_y = y + bounce
    
    # Head & Hair
    head_r = int(14 * scale)
    head_y = int(cur_y - 124 * scale)
    head_x = int(x)
    
    # Hair
    draw.ellipse([head_x - int(head_r * 1.15), head_y - int(head_r * 1.15), 
                  head_x + int(head_r * 1.15), head_y + int(head_r * 0.25)], fill=hair_color)
    # Face skin
    draw.ellipse([head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r], fill=skin_color)
    
    # Torso
    neck_y = head_y + head_r
    pelvis_y = int(cur_y - 56 * scale)
    torso_w = max(4, int(12 * scale))
    draw.line([head_x, neck_y, head_x, pelvis_y], fill=clothes_color, width=torso_w)
    draw.ellipse([head_x - int(6 * scale), pelvis_y - int(5 * scale), 
                  head_x + int(6 * scale), pelvis_y + int(5 * scale)], fill=clothes_color)
    
    # Legs (Articulated Thigh + Shin + Foot)
    thigh_len = 33 * scale
    shin_len = 31 * scale
    leg_w = max(2, int(6 * scale))
    shoe_col = (15, 23, 42)
    
    if action == "climb_celebrate":
        # Climbing/kneeling pose
        k1_x = head_x - (18 * scale * facing)
        k1_y = pelvis_y + (16 * scale)
        f1_x = k1_x - (8 * scale * facing)
        f1_y = k1_y + (28 * scale)
        draw.line([head_x, pelvis_y, k1_x, k1_y, f1_x, f1_y], fill=pants_color, width=leg_w)
        
        k2_x = head_x + (14 * scale * facing)
        k2_y = pelvis_y + (28 * scale)
        f2_x = k2_x + (6 * scale * facing)
        f2_y = k2_y + (26 * scale)
        draw.line([head_x, pelvis_y, k2_x, k2_y, f2_x, f2_y], fill=pants_color, width=leg_w)
        
        # Arms raised triumphantly in the air
        shoulder_y = neck_y + int(6 * scale)
        arm_w = max(2, int(5 * scale))
        draw.line([head_x, shoulder_y, head_x - int(24 * scale * facing), shoulder_y - int(38 * scale)], fill=clothes_color, width=arm_w)
        draw.line([head_x, shoulder_y, head_x + int(24 * scale * facing), shoulder_y - int(38 * scale)], fill=clothes_color, width=arm_w)
        
    elif action == "stand_hero":
        # Confident hero pose
        draw.line([head_x - int(4 * scale), pelvis_y, head_x - int(12 * scale), cur_y], fill=pants_color, width=leg_w)
        draw.line([head_x + int(4 * scale), pelvis_y, head_x + int(12 * scale), cur_y], fill=pants_color, width=leg_w)
        # Shoes
        draw.line([head_x - int(12 * scale), cur_y, head_x - int(22 * scale), cur_y], fill=shoe_col, width=max(2, int(6 * scale)))
        draw.line([head_x + int(12 * scale), cur_y, head_x + int(22 * scale), cur_y], fill=shoe_col, width=max(2, int(6 * scale)))
        
        # Arms on hips or holding tablet
        shoulder_y = neck_y + int(6 * scale)
        arm_w = max(2, int(5 * scale))
        draw.line([head_x, shoulder_y, head_x - int(20 * scale), shoulder_y + int(18 * scale), head_x - int(8 * scale), shoulder_y + int(32 * scale)], fill=clothes_color, width=arm_w)
        draw.line([head_x, shoulder_y, head_x + int(20 * scale), shoulder_y + int(16 * scale), head_x + int(32 * scale), shoulder_y - int(4 * scale)], fill=clothes_color, width=arm_w)
        # Glowing command tablet
        draw.rectangle([head_x + int(28 * scale), shoulder_y - int(16 * scale), 
                       head_x + int(52 * scale), shoulder_y + int(4 * scale)], 
                      fill=(245, 158, 11), outline=(255, 255, 255), width=2)
    else:
        # Natural Walking Cycle
        ang1 = math.sin(walk_phase) * 0.55 * facing
        ang2 = -math.sin(walk_phase) * 0.55 * facing
        
        k1_x = head_x + math.sin(ang1) * thigh_len
        k1_y = pelvis_y + math.cos(ang1) * thigh_len
        bend1 = max(0.0, -math.sin(walk_phase)) * 0.45 * facing
        f1_x = k1_x + math.sin(ang1 + bend1) * shin_len
        f1_y = k1_y + math.cos(ang1 + bend1) * shin_len
        
        draw.line([head_x - int(3 * scale), pelvis_y, k1_x, k1_y], fill=pants_color, width=leg_w)
        draw.line([k1_x, k1_y, f1_x, f1_y], fill=pants_color, width=leg_w)
        draw.line([f1_x, f1_y, f1_x + (9 * scale * facing), f1_y], fill=shoe_col, width=max(2, int(6 * scale)))
        
        k2_x = head_x + math.sin(ang2) * thigh_len
        k2_y = pelvis_y + math.cos(ang2) * thigh_len
        bend2 = max(0.0, math.sin(walk_phase)) * 0.45 * facing
        f2_x = k2_x + math.sin(ang2 + bend2) * shin_len
        f2_y = k2_y + math.cos(ang2 + bend2) * shin_len
        
        draw.line([head_x + int(3 * scale), pelvis_y, k2_x, k2_y], fill=pants_color, width=leg_w)
        draw.line([k2_x, k2_y, f2_x, f2_y], fill=pants_color, width=leg_w)
        draw.line([f2_x, f2_y, f2_x + (9 * scale * facing), f2_y], fill=shoe_col, width=max(2, int(6 * scale)))
        
        # Arms
        shoulder_y = neck_y + int(6 * scale)
        arm_len = 25 * scale
        forearm_len = 24 * scale
        arm_w = max(2, int(5 * scale))
        
        ang_a1 = -math.sin(walk_phase) * 0.45 * facing
        ang_a2 = math.sin(walk_phase) * 0.45 * facing
        draw.line([head_x, shoulder_y, head_x + math.sin(ang_a1) * arm_len, shoulder_y + math.cos(ang_a1) * arm_len], fill=clothes_color, width=arm_w)
        draw.line([head_x, shoulder_y, head_x + math.sin(ang_a2) * arm_len, shoulder_y + math.cos(ang_a2) * arm_len], fill=clothes_color, width=arm_w)


# ==========================================
# SCENE 1: СТЕНА И ОГРАНИЧЕНИЯ (THE COLD BARRIER)
# ==========================================

def render_nov9_scene_1(t, dur):
    # Gloomy November dusk, cold steel-blue atmosphere, towering concrete wall
    img = Image.new("RGBA", (WIDTH, HEIGHT), (14, 18, 28))
    draw = ImageDraw.Draw(img)
    
    # 1. Cold overcast sky gradient with floating autumn leaves
    for s in range(40):
        leaf_x = int((s * 137 + t * 45) % WIDTH)
        leaf_y = int((s * 89 + t * 30 + math.sin(t * 3 + s) * 20) % (HEIGHT - 200))
        draw.ellipse([leaf_x, leaf_y, leaf_x + 5, leaf_y + 3], fill=(180, 83, 9, 140))
        
    # 2. Distant Cold Skyline & Watchtower
    tower_x = 340
    tower_y = HEIGHT - 680
    draw.rectangle([tower_x - 30, tower_y, tower_x + 30, HEIGHT - 220], fill=(24, 30, 42))
    draw.rectangle([tower_x - 55, tower_y - 45, tower_x + 55, tower_y], fill=(30, 41, 59), outline=(71, 85, 105), width=2)
    # Searchlight beam from tower sweeping across ground
    sweep_ang = math.sin(t * 1.5) * 0.4
    beam_x = tower_x + math.sin(sweep_ang) * 550
    draw.polygon([(tower_x, tower_y - 20), (beam_x - 120, HEIGHT - 180), (beam_x + 120, HEIGHT - 180)], fill=(255, 255, 230, 25))
    
    # 3. Ground & Barbed Wire Zone
    draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(20, 24, 32))
    draw.line([0, HEIGHT - 220, WIDTH, HEIGHT - 220], fill=(51, 65, 85), width=3)
    
    # 4. Massive Concrete Wall dividing the scene
    wall_x = WIDTH // 2 + 80
    wall_w = 140
    wall_h = 580
    wall_y = HEIGHT - 220 - wall_h
    
    # Concrete slabs with panel seams
    draw.rectangle([wall_x, wall_y, wall_x + wall_w, HEIGHT - 220], fill=(71, 85, 105), outline=(51, 65, 85), width=3)
    for slab_y in range(wall_y, HEIGHT - 220, 95):
        draw.line([wall_x, slab_y, wall_x + wall_w, slab_y], fill=(40, 50, 65), width=2)
        # Texture lines
        draw.line([wall_x + 20, slab_y + 35, wall_x + wall_w - 30, slab_y + 35], fill=(55, 68, 85), width=1)
        
    # Cylindrical top pipe (characteristic of Berlin Wall)
    draw.ellipse([wall_x - 8, wall_y - 22, wall_x + wall_w + 8, wall_y + 22], fill=(100, 116, 139), outline=(51, 65, 85), width=2)
    
    # 5. Cold Silhouettes of People standing and walking near wall
    draw_character(draw, wall_x - 280, HEIGHT - 220, scale=1.45, walk_phase=t * 3.5, 
                   skin_color=(200, 210, 225), clothes_color=(51, 65, 85), pants_color=(30, 41, 59), 
                   action="walk", facing=1)
    
    draw_character(draw, wall_x - 140, HEIGHT - 220, scale=1.55, walk_phase=0, 
                   skin_color=(200, 210, 225), clothes_color=(71, 85, 105), pants_color=(30, 41, 59), 
                   action="walk", facing=1)
                   
    # Distant figures on the other side
    draw_character(draw, wall_x + wall_w + 180, HEIGHT - 220, scale=1.35, walk_phase=t * 3.0, 
                   skin_color=(180, 190, 210), clothes_color=(30, 41, 59), pants_color=(20, 24, 32), 
                   action="walk", facing=-1)
                   
    return img


# ==========================================
# SCENE 2: 9 НОЯБРЯ — ПАДЕНИЕ СТЕНЫ (THE BREAKTHROUGH)
# ==========================================

def render_nov9_scene_2(t, dur):
    # Dynamic breach: golden cracks bursting through concrete, crumbling rubble, rejoicing crowds
    img = Image.new("RGBA", (WIDTH, HEIGHT), (22, 14, 10))
    draw = ImageDraw.Draw(img)
    
    # 1. Warm sunset glow breaking from behind the wall
    for gy in range(180, 540, 20):
        glow_a = int(65 * (1.0 - (gy - 180) / 360.0))
        draw.rectangle([0, gy, WIDTH, gy + 20], fill=(245, 158, 11, glow_a))
        
    # Ground
    draw.rectangle([0, HEIGHT - 220, WIDTH, HEIGHT], fill=(28, 22, 16))
    
    wall_cx = WIDTH // 2
    wall_w = 480
    wall_y = HEIGHT - 760
    
    # 2. Golden Rays of Light bursting through the center breach
    breach_prog = min(1.0, t / (dur * 0.75))
    num_rays = 12
    for r in range(num_rays):
        ray_ang = math.radians(-75 + r * 15 + math.sin(t * 3 + r) * 4)
        ray_len = 700 * breach_prog
        rx = wall_cx + math.sin(ray_ang) * ray_len
        ry = (wall_y + 280) + math.cos(ray_ang) * ray_len * 0.6
        draw.polygon([(wall_cx - 40, wall_y + 240), (wall_cx + 40, wall_y + 240), (rx + 60, ry), (rx - 60, ry)], 
                     fill=(255, 215, 0, int(80 * breach_prog)))
        
    # 3. Breached Concrete Wall with Jagged Opening
    # Left wall section
    draw.polygon([(wall_cx - wall_w, HEIGHT - 220), (wall_cx - wall_w, wall_y), 
                  (wall_cx - 140, wall_y), (wall_cx - 70 + int(breach_prog * 40), HEIGHT - 340), 
                  (wall_cx - 160, HEIGHT - 220)], fill=(71, 85, 105), outline=(51, 65, 85), width=3)
                  
    # Right wall section
    draw.polygon([(wall_cx + wall_w, HEIGHT - 220), (wall_cx + wall_w, wall_y), 
                  (wall_cx + 140, wall_y), (wall_cx + 70 - int(breach_prog * 40), HEIGHT - 340), 
                  (wall_cx + 160, HEIGHT - 220)], fill=(71, 85, 105), outline=(51, 65, 85), width=3)
                  
    # Crumbling concrete rubble at base
    for b in range(16):
        bx = wall_cx - 180 + b * 24
        by = HEIGHT - 220 - int(math.sin(b * 0.4) * 45) - (b % 3) * 12
        bw = 28 + (b % 4) * 8
        draw.rectangle([bx, by, bx + bw, HEIGHT - 220], fill=(100, 116, 139), outline=(51, 65, 85), width=2)
        
    # 4. People atop the wall celebrating with raised arms and flags
    climbers = [
        {"x": wall_cx - 180, "y": wall_y + 12, "scale": 1.15, "col": (239, 68, 68)},
        {"x": wall_cx - 110, "y": wall_y - 20, "scale": 1.25, "col": (245, 158, 11)},
        {"x": wall_cx + 110, "y": wall_y - 20, "scale": 1.25, "col": (59, 130, 246)},
        {"x": wall_cx + 190, "y": wall_y + 12, "scale": 1.15, "col": (16, 185, 129)}
    ]
    for c in climbers:
        draw_character(draw, c["x"], c["y"], scale=c["scale"], walk_phase=t * 4, 
                       skin_color=(255, 235, 220), clothes_color=c["col"], action="climb_celebrate", facing=1)
                       
    # 5. Welcoming crowd reaching out and embracing in foreground
    draw_character(draw, wall_cx - 280, HEIGHT - 220, scale=1.5, walk_phase=t * 3, 
                   skin_color=(255, 240, 230), clothes_color=(234, 88, 12), action="climb_celebrate", facing=1)
                   
    draw_character(draw, wall_cx + 280, HEIGHT - 220, scale=1.5, walk_phase=t * 3, 
                   skin_color=(255, 240, 230), clothes_color=(14, 165, 233), action="climb_celebrate", facing=-1)
                   
    # Golden Celebration Sparkles
    for sp in range(30):
        spx = (wall_cx - 240 + sp * 18 + int(math.sin(t * 4 + sp) * 45))
        spy = HEIGHT - 480 - int((t * 80 + sp * 25) % 400)
        draw.ellipse([spx, spy, spx + 4, spy + 4], fill=(255, 240, 160, 220))
        
    return img


# ==========================================
# SCENE 3: ИНЖЕНЕРИЯ СВОБОДЫ (BRIDGES OF LIGHT & CODE)
# ==========================================

def render_nov9_scene_3(t, dur):
    # High-tech synthesis: glowing golden bridges assembling, data conduits, precision architecture
    img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 22, 32))
    draw = ImageDraw.Draw(img)
    
    # 1. Clean Perspective Grid
    vp_x, vp_y = WIDTH // 2, 440
    for gx in range(-WIDTH, WIDTH * 2, 130):
        draw.line([vp_x, vp_y, gx, HEIGHT], fill=(0, 140, 200, 65), width=1)
    for gy in range(HEIGHT - 380, HEIGHT, 45):
        draw.line([0, gy, WIDTH, gy], fill=(0, 160, 220, 75), width=1)
        
    # 2. Glowing Golden Vector Bridge Spanning Across Chasm
    bridge_y = HEIGHT - 360
    draw.line([0, bridge_y, WIDTH, bridge_y], fill=(245, 158, 11), width=6)
    draw.line([0, bridge_y + 14, WIDTH, bridge_y + 14], fill=(217, 119, 6), width=4)
    
    # Bridge Truss Structure (Triangular Vector Arches)
    truss_w = 120
    for tx in range(0, WIDTH + truss_w, truss_w):
        draw.line([tx, bridge_y, tx + truss_w // 2, bridge_y - 95], fill=(255, 215, 0, 180), width=3)
        draw.line([tx + truss_w // 2, bridge_y - 95, tx + truss_w, bridge_y], fill=(255, 215, 0, 180), width=3)
        draw.line([tx + truss_w // 2, bridge_y - 95, tx + truss_w // 2, bridge_y], fill=(245, 158, 11, 140), width=2)
        
    # 3. High-Speed Luminous Data Conduits & Traveling Light Packets
    num_cables = 4
    for c_idx in range(num_cables):
        cy_cable = bridge_y - 120 - c_idx * 30
        draw.line([0, cy_cable, WIDTH, cy_cable], fill=(0, 240, 255, 120), width=2)
        # Traveling light packets
        for pkt in range(5):
            pkt_x = int((t * 480 + pkt * 380 + c_idx * 90) % (WIDTH + 100)) - 50
            draw.ellipse([pkt_x - 8, cy_cable - 4, pkt_x + 8, cy_cable + 4], fill=(255, 255, 255))
            draw.ellipse([pkt_x - 16, cy_cable - 6, pkt_x + 16, cy_cable + 6], fill=(0, 240, 255, 100))
            
    # 4. Central Synthesis Core (Reconnecting the Worlds)
    core_cx = WIDTH // 2
    core_cy = bridge_y - 180
    rot = t * 2.0
    for deg in range(0, 360, 20):
        rad = math.radians(deg + rot * 25)
        px = core_cx + math.cos(rad) * 140
        py = core_cy + math.sin(rad) * 60
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(16, 185, 129))
    draw.ellipse([core_cx - 40, core_cy - 40, core_cx + 40, core_cy + 40], fill=(0, 240, 255, 220), outline=(255, 255, 255), width=2)
    
    # 5. Architects of Freedom standing on the bridge
    draw_character(draw, core_cx - 260, bridge_y, scale=1.75, walk_phase=0, 
                   skin_color=(255, 240, 230), clothes_color=(30, 58, 138), action="stand_hero", facing=1)
                   
    draw_character(draw, core_cx + 260, bridge_y, scale=1.75, walk_phase=0, 
                   skin_color=(255, 240, 230), clothes_color=(124, 58, 237), action="stand_hero", facing=-1)
                   
    return img


# ==========================================
# SCENE 4: РАЗРУШАЯ ВНУТРЕННИЕ БАРЬЕРЫ (SPEED & COMMERCE)
# ==========================================

def render_nov9_scene_4(t, dur):
    # Vibrant modern commercial avenue: Barber Lab, vector scissors icon, speed cars, profit flow
    img = Image.new("RGBA", (WIDTH, HEIGHT), (10, 24, 22))
    draw = ImageDraw.Draw(img)
    
    # 1. Ground & Highway
    draw.rectangle([0, HEIGHT - 180, WIDTH, HEIGHT], fill=(15, 23, 42))
    draw.line([0, HEIGHT - 180, WIDTH, HEIGHT - 180], fill=(45, 60, 80), width=4)
    # Road lane dash
    for lx in range(0, WIDTH + 140, 140):
        cur_lx = int((lx - t * 320) % (WIDTH + 140)) - 70
        draw.rectangle([cur_lx, HEIGHT - 65, cur_lx + 75, HEIGHT - 55], fill=(245, 158, 11, 200))
        
    # 2. Storefront (Commercial Freedom)
    shop_x, shop_y, shop_w, shop_h = 100, HEIGHT - 700, 680, 520
    draw.rectangle([shop_x, shop_y, shop_x + shop_w, shop_y + shop_h], fill=(24, 32, 42), outline=(50, 70, 95), width=3)
    
    # Clean Signage with Vector Scissors (NO EMOJIS, ZERO TOFU)
    sign_h = 75
    draw.rectangle([shop_x + 40, shop_y - 40, shop_x + shop_w - 40, shop_y + sign_h - 40], 
                   fill=(15, 23, 42), outline=(245, 158, 11), width=3)
                   
    # Draw vector scissors directly inside the sign box
    draw_vector_scissors(draw, shop_x + 95, shop_y - 2, scale=1.1, color=(245, 158, 11))
    draw.text((shop_x + 130, shop_y - 22), "BARBER LAB TMA", fill=(245, 158, 11), font=font_bold)
    
    # Rotating Barber Pole
    pole_x = shop_x + shop_w - 55
    pole_y = shop_y + 110
    draw.rectangle([pole_x, pole_y, pole_x + 28, pole_y + 180], fill=(255, 255, 255), outline=(100, 116, 139), width=2)
    for s in range(7):
        sy = pole_y + (int(t * 80 + s * 26) % 160)
        draw.line([pole_x, sy, pole_x + 28, sy - 14], fill=(225, 29, 72), width=6)
        draw.line([pole_x, sy + 13, pole_x + 28, sy - 1], fill=(37, 99, 235), width=6)
        
    # Large Glass Showroom with warm interior
    win_x, win_y, win_w, win_h = shop_x + 45, shop_y + 105, shop_w - 130, 350
    draw.rectangle([win_x, win_y, win_x + win_w, win_y + win_h], fill=(35, 45, 38, 235), outline=(0, 240, 200), width=3)
    draw_character(draw, win_x + 160, win_y + win_h - 20, scale=1.35, walk_phase=0, 
                   clothes_color=(51, 65, 85), action="stand_hero", facing=1)
    draw_character(draw, win_x + 270, win_y + win_h - 20, scale=1.45, walk_phase=t * 4, 
                   clothes_color=(15, 23, 42), action="walk", facing=-1)
                   
    # 3. Fast Vector Vehicles Moving along open road (Freedom of Motion)
    car1_x = int((t * 420) % (WIDTH + 400)) - 200
    # Red sports car
    draw.polygon([(car1_x, HEIGHT - 110), (car1_x + 25, HEIGHT - 135), 
                  (car1_x + 120, HEIGHT - 135), (car1_x + 160, HEIGHT - 110)], fill=(225, 29, 72))
    draw.rectangle([car1_x, HEIGHT - 110, car1_x + 160, HEIGHT - 85], fill=(225, 29, 72))
    draw.ellipse([car1_x + 25, HEIGHT - 92, car1_x + 55, HEIGHT - 62], fill=(30, 41, 59))
    draw.ellipse([car1_x + 105, HEIGHT - 92, car1_x + 135, HEIGHT - 62], fill=(30, 41, 59))
    draw.polygon([(car1_x + 160, HEIGHT - 100), (car1_x + 360, HEIGHT - 140), (car1_x + 390, HEIGHT - 70)], fill=(255, 240, 160, 40))
    
    # 4. Cash Flow & Opportunity Particles streaming into digital treasury
    for coin in range(8):
        c_prog = (t * 0.9 + coin * 0.14) % 1.0
        cx = int(shop_x + 320 + c_prog * 600)
        cy = int(HEIGHT - 440 - math.sin(c_prog * math.pi) * 150)
        draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(245, 158, 11), outline=(255, 255, 255), width=2)
        draw.text((cx - 5, cy - 8), "$", fill=(255, 255, 255), font=font_small)
        
    # Free walking pedestrian
    draw_character(draw, int(shop_x - 80 + (t * 50) % 180), HEIGHT - 180, scale=1.4, walk_phase=t * 5.5, 
                   clothes_color=(234, 88, 12), action="walk", facing=1)
                   
    return img


# ==========================================
# SCENE 5: ПРОРЫВ В БУДУЩЕЕ (THE SUMMIT OF FREEDOM)
# ==========================================

def render_nov9_scene_5(t, dur):
    # Epic golden sunrise, panoramic terrace, Father commanding a world without borders
    img = Image.new("RGBA", (WIDTH, HEIGHT), (28, 16, 10))
    draw = ImageDraw.Draw(img)
    
    # 1. Sunrise Sky Gradient
    for gy in range(200, 560, 18):
        alpha = int(55 * (1.0 - (gy - 200) / 360.0))
        draw.rectangle([0, gy, WIDTH, gy + 18], fill=(245, 158, 11, alpha))
        
    # Stars fading in morning dawn
    for s in range(50):
        sx = (s * 163) % WIDTH
        sy = (s * 79) % 360
        draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 245, 220, 160))
        
    # 2. Limitless City Skyline Below
    for bx in range(0, WIDTH + 90, 85):
        bh = 300 + (bx * 41) % 280
        draw.rectangle([bx, HEIGHT - 220 - bh, bx + 70, HEIGHT - 220], fill=(35, 24, 16))
        for wy in range(HEIGHT - 210 - bh, HEIGHT - 230, 36):
            if (bx + wy) % 2 == 0:
                draw.rectangle([bx + 14, wy, bx + 32, wy + 18], fill=(255, 205, 80, 180))
                
    # 3. High-altitude Observation Penthouse Terrace
    deck_y = HEIGHT - 240
    draw.rectangle([0, deck_y, WIDTH, HEIGHT], fill=(30, 22, 14))
    draw.line([0, deck_y, WIDTH, deck_y], fill=(245, 158, 11), width=4)
    # Glass railing
    draw.rectangle([0, deck_y - 85, WIDTH, deck_y], fill=(245, 158, 11, 25), outline=(245, 158, 11, 140), width=2)
    
    # 4. FATHER FIGURE (Hero Stance, Absolute Command & Freedom)
    f_x = WIDTH // 2
    f_y = deck_y
    draw_character(
        draw, f_x, f_y, scale=2.35, walk_phase=0,
        skin_color=(255, 245, 235), hair_color=(45, 30, 20), clothes_color=(180, 83, 9),
        pants_color=(20, 25, 35), action="stand_hero", facing=1
    )
    
    # 5. Expanding Golden Radiance Rings & Network of Freedom
    tab_x = f_x + 75
    tab_y = f_y - 275
    for ray in range(9):
        rx = 100 + ray * 220
        ry = HEIGHT - 260
        ray_a = int(140 + math.sin(t * 4 + ray) * 90)
        draw.line([rx, ry, tab_x, tab_y], fill=(245, 158, 11, ray_a), width=2)
        
    for ring in range(3):
        r_dist = int((t * 85 + ring * 80) % 240) + 25
        alpha_ring = max(0, int(255 * (1.0 - r_dist / 265.0)))
        draw.ellipse([tab_x - r_dist, tab_y - r_dist, tab_x + r_dist, tab_y + r_dist], 
                     outline=(255, 215, 0, alpha_ring), width=3)
                     
    # Floating Golden Particles Drifting into the Sky
    for sp in range(30):
        spx = (sp * 89 + int(math.sin(t * 2 + sp) * 45)) % WIDTH
        spy = int((HEIGHT - (t * 75 + sp * 32)) % HEIGHT)
        draw.ellipse([spx, spy, spx + 3, spy + 3], fill=(255, 230, 140, 210))
        
    return img


SCENE_RENDERERS_NOV9 = [
    render_nov9_scene_1,
    render_nov9_scene_2,
    render_nov9_scene_3,
    render_nov9_scene_4,
    render_nov9_scene_5
]
