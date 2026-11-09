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
    font_bold = ImageFont.truetype(FONT_PATH_TITLE, 32)
    font_badge = ImageFont.truetype(FONT_PATH_TITLE, 20)
    font_small = ImageFont.truetype(FONT_PATH_TEXT, 16)
except Exception:
    font_bold = font_badge = font_small = ImageFont.load_default()


# ==========================================
# ADVANCED ARTICULATED CHARACTER RENDERER
# ==========================================

def draw_kinematic_human(draw, x, y, scale=1.0, walk_phase=0.0, 
                         color=(240, 245, 255), hair_color=(45, 35, 30), 
                         clothes_color=(59, 130, 246), action="walk_phone", facing=1):
    """
    Realistic vector human with articulated 2-segment limbs (thigh+shin, bicep+forearm),
    torso, stylish clothing, hair, natural vertical bounce, and hand gestures.
    """
    bounce = math.sin(walk_phase * 2) * (3.5 * scale) if (walk_phase != 0 and action in ("walk", "walk_phone")) else 0
    cur_y = y + bounce
    
    # Head & Hair
    head_r = int(14 * scale)
    head_y = int(cur_y - 124 * scale)
    head_x = int(x)
    
    # Hair cap
    draw.ellipse([head_x - int(head_r * 1.15), head_y - int(head_r * 1.15), 
                  head_x + int(head_r * 1.15), head_y + int(head_r * 0.2)], fill=hair_color)
    # Face / Head
    draw.ellipse([head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r], fill=color)
    
    # Neck & Torso
    neck_y = head_y + head_r
    pelvis_y = int(cur_y - 56 * scale)
    
    # Torso (Jacket/Hoodie)
    draw.line([head_x, neck_y, head_x, pelvis_y], fill=clothes_color, width=max(4, int(12 * scale)))
    draw.ellipse([head_x - int(6 * scale), pelvis_y - int(5 * scale), 
                  head_x + int(6 * scale), pelvis_y + int(5 * scale)], fill=clothes_color)
    
    # Articulated Legs
    thigh_len = 33 * scale
    shin_len = 31 * scale
    leg_w = max(2, int(6 * scale))
    pants_col = (30, 41, 59)
    shoe_col = (15, 23, 42)
    
    ang1 = math.sin(walk_phase) * 0.55 * facing if action.startswith("walk") else 0.08
    ang2 = -math.sin(walk_phase) * 0.55 * facing if action.startswith("walk") else -0.08
    
    # Leg 1
    k1_x = head_x + math.sin(ang1) * thigh_len
    k1_y = pelvis_y + math.cos(ang1) * thigh_len
    bend1 = max(0.0, -math.sin(walk_phase)) * 0.45 * facing if action.startswith("walk") else 0
    f1_x = k1_x + math.sin(ang1 + bend1) * shin_len
    f1_y = k1_y + math.cos(ang1 + bend1) * shin_len
    
    draw.line([head_x - int(3 * scale), pelvis_y, k1_x, k1_y], fill=pants_col, width=leg_w)
    draw.line([k1_x, k1_y, f1_x, f1_y], fill=pants_col, width=leg_w)
    draw.line([f1_x, f1_y, f1_x + (9 * scale * facing), f1_y], fill=shoe_col, width=max(2, int(6 * scale)))
    
    # Leg 2
    k2_x = head_x + math.sin(ang2) * thigh_len
    k2_y = pelvis_y + math.cos(ang2) * thigh_len
    bend2 = max(0.0, math.sin(walk_phase)) * 0.45 * facing if action.startswith("walk") else 0
    f2_x = k2_x + math.sin(ang2 + bend2) * shin_len
    f2_y = k2_y + math.cos(ang2 + bend2) * shin_len
    
    draw.line([head_x + int(3 * scale), pelvis_y, k2_x, k2_y], fill=pants_col, width=leg_w)
    draw.line([k2_x, k2_y, f2_x, f2_y], fill=pants_col, width=leg_w)
    draw.line([f2_x, f2_y, f2_x + (9 * scale * facing), f2_y], fill=shoe_col, width=max(2, int(6 * scale)))
    
    # Articulated Arms
    shoulder_y = neck_y + int(8 * scale)
    arm_len = 25 * scale
    forearm_len = 24 * scale
    arm_w = max(2, int(5 * scale))
    
    if action == "walk_phone":
        # Back arm swings naturally
        ang_a1 = -math.sin(walk_phase) * 0.45 * facing
        e1_x = head_x + math.sin(ang_a1) * arm_len
        e1_y = shoulder_y + math.cos(ang_a1) * arm_len
        w1_x = e1_x + math.sin(ang_a1) * forearm_len
        w1_y = e1_y + math.cos(ang_a1) * forearm_len
        draw.line([head_x, shoulder_y, e1_x, e1_y], fill=clothes_color, width=arm_w)
        draw.line([e1_x, e1_y, w1_x, w1_y], fill=clothes_color, width=arm_w)
        
        # Front arm holds glowing phone
        e2_x = head_x + (16 * scale * facing)
        e2_y = shoulder_y + (18 * scale)
        w2_x = head_x + (25 * scale * facing)
        w2_y = shoulder_y + (4 * scale)
        draw.line([head_x, shoulder_y, e2_x, e2_y], fill=clothes_color, width=arm_w)
        draw.line([e2_x, e2_y, w2_x, w2_y], fill=clothes_color, width=arm_w)
        
        # Smartphone
        pw = int(6 * scale)
        ph = int(12 * scale)
        draw.rectangle([w2_x, w2_y - ph, w2_x + pw * facing, w2_y], fill=(15, 23, 42))
        draw.rectangle([w2_x + 1, w2_y - ph + 1, w2_x + (pw - 1) * facing, w2_y - 1], fill=(0, 240, 255))
        
    elif action == "stand_hero":
        # Father hero pose: confident posture with command device
        e1_x = head_x - (18 * scale)
        e1_y = shoulder_y + (16 * scale)
        w1_x = head_x - (12 * scale)
        w1_y = shoulder_y + (28 * scale)
        draw.line([head_x, shoulder_y, e1_x, e1_y, w1_x, w1_y], fill=clothes_color, width=arm_w)
        
        e2_x = head_x + (20 * scale)
        e2_y = shoulder_y + (14 * scale)
        w2_x = head_x + (32 * scale)
        w2_y = shoulder_y - (2 * scale)
        draw.line([head_x, shoulder_y, e2_x, e2_y, w2_x, w2_y], fill=clothes_color, width=arm_w)
        # Gold holographic tablet
        draw.rectangle([w2_x - 4, w2_y - int(16 * scale), w2_x + int(24 * scale), w2_y + int(6 * scale)], 
                       fill=(20, 25, 35), outline=(245, 158, 11), width=2)
        draw.rectangle([w2_x - 2, w2_y - int(14 * scale), w2_x + int(22 * scale), w2_y + int(4 * scale)], 
                       fill=(255, 215, 0))
    elif action == "barber_master":
        # Scissors arm moving up and down
        trim_angle = math.sin(walk_phase * 4) * 0.25
        e1_x = head_x - (14 * scale)
        e1_y = shoulder_y + (18 * scale)
        draw.line([head_x, shoulder_y, e1_x, e1_y], fill=clothes_color, width=arm_w)
        
        e2_x = head_x + (22 * scale)
        e2_y = shoulder_y + (14 * scale)
        w2_x = e2_x + math.cos(trim_angle) * (20 * scale)
        w2_y = e2_y - math.sin(trim_angle) * (18 * scale)
        draw.line([head_x, shoulder_y, e2_x, e2_y, w2_x, w2_y], fill=clothes_color, width=arm_w)
        # Scissors glint
        draw.ellipse([w2_x - 3, w2_y - 3, w2_x + 3, w2_y + 3], fill=(255, 215, 0))
    else:
        # Standard swing
        ang_a1 = math.sin(walk_phase) * 0.45 * facing
        ang_a2 = -math.sin(walk_phase) * 0.45 * facing
        draw.line([head_x, shoulder_y, head_x + math.sin(ang_a1) * arm_len, shoulder_y + math.cos(ang_a1) * arm_len], fill=clothes_color, width=arm_w)
        draw.line([head_x, shoulder_y, head_x + math.sin(ang_a2) * arm_len, shoulder_y + math.cos(ang_a2) * arm_len], fill=clothes_color, width=arm_w)


# ==========================================
# VECTOR VEHICLE
# ==========================================

def draw_vector_car(draw, x, y, scale=1.0, color=(225, 29, 72), headlight_dir=1):
    cw = int(140 * scale)
    ch = int(42 * scale)
    
    body_poly = [
        (x, y),
        (x + int(20 * scale), y - int(18 * scale)),
        (x + int(45 * scale), y - int(34 * scale)),
        (x + int(105 * scale), y - int(34 * scale)),
        (x + int(128 * scale), y - int(14 * scale)),
        (x + cw, y),
        (x + cw, y + int(14 * scale)),
        (x, y + int(14 * scale))
    ]
    draw.polygon(body_poly, fill=color)
    
    # Windows
    draw.polygon([
        (x + int(46 * scale), y - int(30 * scale)),
        (x + int(70 * scale), y - int(30 * scale)),
        (x + int(70 * scale), y - int(16 * scale)),
        (x + int(30 * scale), y - int(16 * scale))
    ], fill=(15, 23, 42))
    
    draw.polygon([
        (x + int(74 * scale), y - int(30 * scale)),
        (x + int(98 * scale), y - int(30 * scale)),
        (x + int(114 * scale), y - int(16 * scale)),
        (x + int(74 * scale), y - int(16 * scale))
    ], fill=(15, 23, 42))
    
    # Wheels
    rw = int(11 * scale)
    draw.ellipse([x + int(28 * scale) - rw, y + int(14 * scale) - rw, x + int(28 * scale) + rw, y + int(14 * scale) + rw], fill=(30, 41, 59), outline=(148, 163, 184), width=2)
    draw.ellipse([x + int(112 * scale) - rw, y + int(14 * scale) - rw, x + int(112 * scale) + rw, y + int(14 * scale) + rw], fill=(30, 41, 59), outline=(148, 163, 184), width=2)
    
    if headlight_dir > 0:
        draw.ellipse([x + cw - int(8*scale), y - int(6*scale), x + cw, y + int(4*scale)], fill=(255, 240, 150))
        # Warm headlight cone
        draw.polygon([(x + cw, y), (x + cw + int(180 * scale), y - int(28 * scale)), 
                      (x + cw + int(210 * scale), y + int(36 * scale)), (x + cw, y + int(10 * scale))], 
                     fill=(255, 245, 180, 50))
        draw.rectangle([x, y - int(4*scale), x + int(6*scale), y + int(4*scale)], fill=(239, 68, 68))
    else:
        draw.ellipse([x, y - int(6*scale), x + int(8*scale), y + int(4*scale)], fill=(255, 240, 150))
        draw.polygon([(x, y), (x - int(180 * scale), y - int(28 * scale)), 
                      (x - int(210 * scale), y + int(36 * scale)), (x, y + int(10 * scale))], 
                     fill=(255, 245, 180, 50))
        draw.rectangle([x + cw - int(6*scale), y - int(4*scale), x + cw, y + int(4*scale)], fill=(239, 68, 68))


# ==========================================
# SCENE 1: THE URBAN MATRIX (NO HUD, PURE CINEMATIC)
# ==========================================

def render_scene_1_frame(t, dur):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (10, 13, 22))
    draw = ImageDraw.Draw(img)
    
    # 1. Sky Gradient & Ambient Stars
    for s in range(50):
        sx = (s * 173) % WIDTH
        sy = (s * 89) % 380
        alpha = int(140 + math.sin(t * 3 + s) * 90)
        draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(200, 220, 255, alpha))
        
    cam_x = t * 50
    
    # 2. Distant Parallax Skyline
    for b_idx in range(24):
        bx = int((b_idx * 130 - cam_x * 0.25) % (WIDTH + 260)) - 130
        bw = 110
        bh = 380 + (b_idx * 47) % 240
        draw.rectangle([bx, HEIGHT - 240 - bh, bx + bw, HEIGHT - 240], fill=(18, 24, 38))
        # Subtle rooftop antenna
        if b_idx % 3 == 0:
            draw.line([bx + bw // 2, HEIGHT - 240 - bh, bx + bw // 2, HEIGHT - 240 - bh - 40], fill=(40, 60, 90), width=2)
            if int(t * 2) % 2 == 0:
                draw.ellipse([bx + bw // 2 - 3, HEIGHT - 240 - bh - 43, bx + bw // 2 + 3, HEIGHT - 240 - bh - 37], fill=(239, 68, 68))
                
    # 3. Mid-ground Detailed Buildings with Warm & Cyan Windows
    for m_idx in range(16):
        mx = int((m_idx * 210 - cam_x * 0.55) % (WIDTH + 420)) - 210
        mw = 180
        mh = 480 + (m_idx * 63) % 200
        draw.rectangle([mx, HEIGHT - 200 - mh, mx + mw, HEIGHT - 200], fill=(25, 34, 52), outline=(38, 52, 78), width=2)
        
        # Windows grid
        for wx in range(mx + 20, mx + mw - 25, 34):
            for wy in range(HEIGHT - 180 - mh, HEIGHT - 220, 48):
                is_lit = ((m_idx * 7 + (wx - mx) + wy) % 5 != 0)
                win_col = (255, 215, 120, 220) if (wx + wy) % 3 != 0 else (0, 240, 255, 180)
                if is_lit:
                    draw.rectangle([wx, wy, wx + 18, wy + 26], fill=win_col)
                else:
                    draw.rectangle([wx, wy, wx + 18, wy + 26], fill=(16, 22, 34))
                    
    # 4. Street Infrastructure & Sidewalk
    draw.rectangle([0, HEIGHT - 200, WIDTH, HEIGHT], fill=(14, 18, 26))
    # Sidewalk paving
    draw.rectangle([0, HEIGHT - 200, WIDTH, HEIGHT - 130], fill=(30, 41, 59))
    draw.line([0, HEIGHT - 200, WIDTH, HEIGHT - 200], fill=(71, 85, 105), width=3)
    draw.line([0, HEIGHT - 130, WIDTH, HEIGHT - 130], fill=(100, 116, 139), width=4)
    
    # Street road markings
    for lx in range(0, WIDTH + 120, 140):
        cur_lx = int((lx - cam_x * 2.2) % (WIDTH + 140)) - 70
        draw.rectangle([cur_lx, HEIGHT - 65, cur_lx + 80, HEIGHT - 55], fill=(245, 158, 11, 200))
        
    # Streetlamps casting soft gradient light cones
    for lp in range(6):
        lx = int((lp * 380 - cam_x * 0.9) % (WIDTH + 400)) - 100
        draw.line([lx, HEIGHT - 200, lx, HEIGHT - 420], fill=(71, 85, 105), width=6)
        draw.line([lx, HEIGHT - 420, lx + 45, HEIGHT - 420], fill=(71, 85, 105), width=5)
        # Lamp head
        draw.ellipse([lx + 40, HEIGHT - 425, lx + 55, HEIGHT - 415], fill=(255, 245, 180))
        # Warm light cone on pavement
        draw.polygon([(lx + 48, HEIGHT - 420), (lx - 70, HEIGHT - 130), (lx + 160, HEIGHT - 130)], fill=(255, 235, 150, 25))
        
    # 5. Moving Cars
    car1_x = int((t * 360) % (WIDTH + 400)) - 200
    draw_vector_car(draw, car1_x, HEIGHT - 110, scale=1.15, color=(225, 29, 72), headlight_dir=1)
    
    car2_x = int((WIDTH + 200 - t * 290) % (WIDTH + 400)) - 200
    draw_vector_car(draw, car2_x, HEIGHT - 50, scale=1.0, color=(14, 165, 233), headlight_dir=-1)
    
    # 6. Diverse Articulated Pedestrians Walking
    crowd_defs = [
        {"base_x": 180, "spd": 85, "scale": 1.25, "dir": 1, "col": (245, 240, 230), "hair": (35, 25, 20), "jacket": (239, 68, 68)},
        {"base_x": 580, "spd": 70, "scale": 1.15, "dir": 1, "col": (235, 245, 255), "hair": (80, 50, 30), "jacket": (16, 185, 129)},
        {"base_x": 980, "spd": 95, "scale": 1.30, "dir": 1, "col": (255, 235, 220), "hair": (20, 20, 20), "jacket": (59, 130, 246)},
        {"base_x": 1420, "spd": 75, "scale": 1.20, "dir": 1, "col": (240, 240, 250), "hair": (160, 80, 40), "jacket": (245, 158, 11)},
        {"base_x": 1780, "spd": 80, "scale": 1.22, "dir": 1, "col": (245, 245, 245), "hair": (40, 30, 25), "jacket": (168, 85, 247)},
    ]
    
    for cd in crowd_defs:
        px = int((cd["base_x"] + t * cd["spd"] - cam_x * 0.8) % (WIDTH + 300)) - 150
        w_phase = t * 6.5 + cd["base_x"]
        draw_kinematic_human(
            draw, px, HEIGHT - 150, scale=cd["scale"], 
            walk_phase=w_phase, color=cd["col"], hair_color=cd["hair"], 
            clothes_color=cd["jacket"], action="walk_phone", facing=cd["dir"]
        )
        # Pulsing notification badge floating above smartphone
        badge_y = HEIGHT - 280 - int(math.sin(t * 5 + cd["base_x"]) * 10)
        draw.ellipse([px + 20, badge_y, px + 36, badge_y + 16], fill=(239, 68, 68))
        draw.text((px + 26, badge_y + 1), "!", fill=(255, 255, 255), font=font_small)
        
    return img


# ==========================================
# SCENE 2: HOLOGRAPHIC ARCHITECTURE (NO HUD)
# ==========================================

def render_scene_2_frame(t, dur):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (6, 16, 28))
    draw = ImageDraw.Draw(img)
    
    # 1. Perspective Grid Floor
    vp_x, vp_y = WIDTH // 2, 420
    for grid_x in range(-WIDTH, WIDTH * 2, 120):
        draw.line([vp_x, vp_y, grid_x, HEIGHT], fill=(0, 100, 180, 70), width=1)
    for gy in range(HEIGHT - 400, HEIGHT, 45):
        draw.line([0, gy, WIDTH, gy], fill=(0, 120, 200, 80), width=1)
        
    # 2. Central 3D Rotating Hologram Sphere & Orbital Rings
    cx, cy = WIDTH // 2 + 120, 380
    rot = t * 1.8
    
    # Outer Ring
    for deg in range(0, 360, 8):
        rad = math.radians(deg + rot * 25)
        rx = cx + math.cos(rad) * 340
        ry = cy + math.sin(rad) * 110
        draw.ellipse([rx - 3, ry - 3, rx + 3, ry + 3], fill=(0, 240, 255, 180))
        
    # Inner Tilted Ring
    for deg in range(0, 360, 10):
        rad = math.radians(deg - rot * 35)
        rx = cx + math.cos(rad) * 260
        ry = cy + math.sin(rad) * 170
        draw.ellipse([rx - 4, ry - 4, rx + 4, ry + 4], fill=(16, 185, 129, 200))
        
    # Central Holographic Core
    draw.ellipse([cx - 90, cy - 90, cx + 90, cy + 90], fill=(0, 60, 110, 140), outline=(0, 240, 255), width=3)
    draw.ellipse([cx - 45, cy - 45, cx + 45, cy + 45], fill=(0, 240, 255, 220), outline=(255, 255, 255), width=2)
    
    # Connecting spline beams with dynamic data pulses
    nodes = []
    for i, a in enumerate([30, 90, 150, 210, 270, 330]):
        ang = math.radians(a + rot * 20)
        nx = cx + math.cos(ang) * 240
        ny = cy + math.sin(ang) * 100
        nodes.append((nx, ny))
        # Floating data node
        draw.rectangle([nx - 22, ny - 16, nx + 22, ny + 16], fill=(10, 25, 45), outline=(0, 240, 255), width=2)
        draw.ellipse([nx - 6, ny - 6, nx + 6, ny + 6], fill=(16, 185, 129))
        draw.line([nx, ny, cx, cy], fill=(0, 240, 255, 110), width=2)
        
    for i in range(len(nodes)):
        nxt = nodes[(i + 1) % len(nodes)]
        draw.line([nodes[i][0], nodes[i][1], nxt[0], nxt[1]], fill=(0, 200, 255, 180), width=2)
        # Traveling pulse particle
        pulse_pos = (t * 2 + i * 0.35) % 1.0
        pp_x = nodes[i][0] + (nxt[0] - nodes[i][0]) * pulse_pos
        pp_y = nodes[i][1] + (nxt[1] - nodes[i][1]) * pulse_pos
        draw.ellipse([pp_x - 6, pp_y - 6, pp_x + 6, pp_y + 6], fill=(255, 255, 255))
        
    # 3. Architect Figure at Command Deck
    arch_x = WIDTH // 2 - 380
    arch_y = HEIGHT - 180
    draw_kinematic_human(
        draw, arch_x, arch_y, scale=1.9, walk_phase=0,
        color=(255, 245, 235), hair_color=(40, 30, 25), clothes_color=(30, 58, 138),
        action="stand_hero", facing=1
    )
    
    # Floating Holographic UI Arc in front of Architect
    for ui_idx in range(3):
        ux = arch_x + 90 + ui_idx * 95
        uy = arch_y - 250 - ui_idx * 25
        draw.rectangle([ux, uy, ux + 80, uy + 110], fill=(0, 35, 60, 160), outline=(0, 240, 255), width=2)
        for ly in range(uy + 15, uy + 95, 16):
            lw = int(35 + math.sin(t * 6 + ly + ui_idx) * 25)
            draw.line([ux + 10, ly, ux + 10 + lw, ly], fill=(0, 240, 255), width=2)
            
    return img


# ==========================================
# SCENE 3: AI PRECISION ROBOTICS (NO CODE BLOCKS!)
# ==========================================

def render_scene_3_frame(t, dur):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (16, 7, 28))
    draw = ImageDraw.Draw(img)
    
    # 1. Clean Isometric Circuit Grid
    for y_line in range(60, HEIGHT, 70):
        draw.line([0, y_line, WIDTH, y_line], fill=(42, 18, 70), width=1)
    for x_line in range(60, WIDTH, 120):
        draw.line([x_line, 0, x_line, HEIGHT], fill=(42, 18, 70), width=1)
        
    # 2. Central 3D Rotating Polyhedral Algorithm Core
    cx, cy = WIDTH // 2 + 100, HEIGHT // 2 - 30
    rot = t * 1.5
    
    # Draw faceted crystal / algorithm core
    facets = []
    num_pts = 8
    r_core = 160
    for i in range(num_pts):
        ang = math.radians(i * (360 / num_pts) + rot * 30)
        px = cx + math.cos(ang) * r_core
        py = cy + math.sin(ang) * (r_core * 0.55)
        facets.append((px, py))
        
    # Draw geometric structure
    for i in range(num_pts):
        nxt = facets[(i + 1) % num_pts]
        draw.polygon([(cx, cy - 140), facets[i], nxt], fill=(147, 51, 234, 90), outline=(216, 180, 254), width=2)
        draw.polygon([(cx, cy + 140), facets[i], nxt], fill=(126, 34, 206, 110), outline=(192, 132, 252), width=2)
        
    # Glowing center core
    draw.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(255, 215, 0), outline=(255, 255, 255), width=3)
    
    # 3. Precision Robotic Laser Arms
    arms = [
        {"root": (cx - 360, cy - 220), "col": (236, 72, 153)},
        {"root": (cx + 360, cy - 220), "col": (59, 130, 246)},
        {"root": (cx + 380, cy + 190), "col": (16, 185, 129)}
    ]
    
    for a_idx, arm in enumerate(arms):
        rx, ry = arm["root"]
        target_pt = facets[(int(t * 3 + a_idx * 3)) % num_pts]
        
        # 2-segment articulated robotic arm
        mid_x = (rx + target_pt[0]) // 2 + (40 if a_idx % 2 == 0 else -40)
        mid_y = min(ry, target_pt[1]) - 60
        
        # Base mount
        draw.rectangle([rx - 25, ry - 25, rx + 25, ry + 25], fill=(55, 65, 81), outline=(156, 163, 175), width=2)
        # Joints & links
        draw.line([rx, ry, mid_x, mid_y], fill=(107, 114, 128), width=10)
        draw.ellipse([mid_x - 10, mid_y - 10, mid_x + 10, mid_y + 10], fill=(209, 213, 219))
        draw.line([mid_x, mid_y, target_pt[0], target_pt[1]], fill=(156, 163, 175), width=7)
        
        # Precision laser beam firing from nozzle
        draw.line([target_pt[0], target_pt[1], cx, cy], fill=arm["col"], width=4)
        draw.line([target_pt[0], target_pt[1], cx, cy], fill=(255, 255, 255), width=1)
        
        # Flying welding sparks
        for sp in range(6):
            spark_ang = math.radians((sp * 60 + t * 400) % 360)
            spark_dist = int((t * 120 + sp * 18) % 65)
            sp_x = target_pt[0] + math.cos(spark_ang) * spark_dist
            sp_y = target_pt[1] + math.sin(spark_ang) * spark_dist
            draw.ellipse([sp_x - 2, sp_y - 2, sp_x + 2, sp_y + 2], fill=(255, 240, 160))
            
    # 4. Spinning Golden Precision Gears
    gear_x, gear_y = 280, HEIGHT - 260
    gear_r = 75
    rot_g = t * 2.2
    for tooth in range(0, 360, 30):
        t_rad = math.radians(tooth + rot_g * 25)
        tx = gear_x + math.cos(t_rad) * (gear_r + 14)
        ty = gear_y + math.sin(t_rad) * (gear_r + 14)
        draw.line([gear_x, gear_y, tx, ty], fill=(245, 158, 11), width=8)
    draw.ellipse([gear_x - gear_r, gear_y - gear_r, gear_x + gear_r, gear_y + gear_r], fill=(245, 158, 11), outline=(255, 255, 255), width=3)
    draw.ellipse([gear_x - 28, gear_y - 28, gear_x + 28, gear_y + 28], fill=(16, 7, 28))
    
    # 5. Coder/Engineer Inspector Character
    draw_kinematic_human(
        draw, 420, HEIGHT - 180, scale=1.75, walk_phase=0,
        color=(255, 245, 235), hair_color=(30, 25, 20), clothes_color=(124, 58, 237),
        action="stand_hero", facing=1
    )
    
    return img


# ==========================================
# SCENE 4: COMMERCIAL FLEET & BARBER LAB MONETIZATION
# ==========================================

def render_scene_4_frame(t, dur):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 20, 24))
    draw = ImageDraw.Draw(img)
    
    # 1. Ground & Street Pavement
    draw.rectangle([0, HEIGHT - 180, WIDTH, HEIGHT], fill=(15, 23, 42))
    draw.line([0, HEIGHT - 180, WIDTH, HEIGHT - 180], fill=(45, 60, 80), width=4)
    
    # 2. BARBER LAB STOREFRONT (Commercial Showcase)
    shop_x, shop_y, shop_w, shop_h = 120, HEIGHT - 720, 680, 540
    # Store facade
    draw.rectangle([shop_x, shop_y, shop_x + shop_w, shop_y + shop_h], fill=(24, 32, 42), outline=(50, 70, 95), width=3)
    
    # Glowing Neon Store Sign
    sign_h = 80
    draw.rectangle([shop_x + 40, shop_y - 45, shop_x + shop_w - 40, shop_y + sign_h - 45], 
                   fill=(15, 23, 42), outline=(245, 158, 11), width=3)
    # Animated neon text glow
    neon_glow = (255, 215, 0) if int(t * 6) % 10 != 0 else (180, 130, 0)
    draw.text((shop_x + 130, shop_y - 25), "💈 BARBER LAB TMA", fill=neon_glow, font=font_bold)
    
    # Rotating Barber Pole
    pole_x = shop_x + shop_w - 55
    pole_y = shop_y + 110
    draw.rectangle([pole_x, pole_y, pole_x + 28, pole_y + 190], fill=(255, 255, 255), outline=(100, 116, 139), width=2)
    # Spiraling red & blue stripes
    for s in range(8):
        sy = pole_y + (int(t * 80 + s * 26) % 170)
        draw.line([pole_x, sy, pole_x + 28, sy - 14], fill=(225, 29, 72), width=6)
        draw.line([pole_x, sy + 13, pole_x + 28, sy - 1], fill=(37, 99, 235), width=6)
        
    # Large Glass Showroom Window (warm illuminated interior)
    win_x, win_y, win_w, win_h = shop_x + 45, shop_y + 110, shop_w - 130, 360
    draw.rectangle([win_x, win_y, win_x + win_w, win_y + win_h], fill=(35, 45, 38, 235), outline=(0, 240, 200), width=3)
    # Interior ambient glow
    draw.rectangle([win_x + 10, win_y + 10, win_x + win_w - 10, win_y + win_h - 10], fill=(255, 245, 220, 30))
    
    # Interior: Customer in Barber Chair
    draw_kinematic_human(
        draw, win_x + 160, win_y + win_h - 20, scale=1.35, walk_phase=0,
        color=(255, 235, 220), hair_color=(35, 25, 20), clothes_color=(51, 65, 85),
        action="stand_hero", facing=1
    )
    # Master Barber actively styling hair with animated hands
    draw_kinematic_human(
        draw, win_x + 270, win_y + win_h - 20, scale=1.45, walk_phase=t,
        color=(255, 240, 230), hair_color=(120, 60, 25), clothes_color=(15, 23, 42),
        action="barber_master", facing=-1
    )
    
    # 3. Modern Customer Entering the Shop
    cust_x = int(shop_x - 120 + (t * 40) % 180)
    draw_kinematic_human(
        draw, cust_x, HEIGHT - 180, scale=1.4, walk_phase=t * 5.5,
        color=(245, 240, 230), hair_color=(30, 30, 30), clothes_color=(234, 88, 12),
        action="walk_phone", facing=1
    )
    
    # 4. Autonomous Cloud Server Tower (Center-Right)
    srv_x, srv_y, srv_w, srv_h = 880, HEIGHT - 700, 420, 520
    draw.rectangle([srv_x, srv_y, srv_x + srv_w, srv_y + srv_h], fill=(12, 18, 26), outline=(0, 240, 255), width=2)
    # Server bays
    for rack in range(8):
        ry = srv_y + 35 + rack * 58
        draw.rectangle([srv_x + 25, ry, srv_x + srv_w - 25, ry + 44], fill=(20, 30, 42), outline=(35, 50, 70), width=1)
        # Blinking activity LEDs
        for led in range(10):
            l_col = (16, 185, 129) if ((int(t * 12 + rack + led)) % 3 != 0) else (0, 240, 255)
            draw.ellipse([srv_x + 50 + led * 34, ry + 16, srv_x + 62 + led * 34, ry + 28], fill=l_col)
            
    # 5. Resell Radar & Opportunity Scanner (Far Right)
    rad_x, rad_y = 1560, HEIGHT - 640
    # Radar Mast Structure
    draw.line([rad_x - 70, HEIGHT - 180, rad_x, rad_y], fill=(71, 85, 105), width=4)
    draw.line([rad_x + 70, HEIGHT - 180, rad_x, rad_y], fill=(71, 85, 105), width=4)
    draw.line([rad_x - 45, HEIGHT - 330, rad_x + 45, HEIGHT - 330], fill=(71, 85, 105), width=3)
    draw.line([rad_x - 25, HEIGHT - 480, rad_x + 25, HEIGHT - 480], fill=(71, 85, 105), width=3)
    
    # Smooth Expanding Radar Cones
    for ring in range(3):
        r_dist = int((t * 110 + ring * 90) % 270)
        draw.arc([rad_x - r_dist, rad_y - r_dist, rad_x + r_dist, rad_y + r_dist], 180, 360, fill=(16, 185, 129, max(0, 255 - r_dist)), width=3)
    draw.ellipse([rad_x - 18, rad_y - 18, rad_x + 18, rad_y + 18], fill=(255, 255, 255))
    
    # 6. Stream of Golden Coins / Profit Floating into Digital Vault
    for coin_idx in range(9):
        c_prog = (t * 0.9 + coin_idx * 0.12) % 1.0
        # Curved bezier trajectory from Barber Lab and Radar to Central Server
        coin_x = int(shop_x + 350 + c_prog * 480)
        coin_y = int(HEIGHT - 450 - math.sin(c_prog * math.pi) * 160)
        draw.ellipse([coin_x - 14, coin_y - 14, coin_x + 14, coin_y + 14], fill=(245, 158, 11), outline=(255, 255, 255), width=2)
        draw.text((coin_x - 5, coin_y - 8), "$", fill=(255, 255, 255), font=font_small)
        
    return img


# ==========================================
# SCENE 5: THE IMPERIAL METROPOLIS (FATHER AT SUMMIT)
# ==========================================

def render_scene_5_frame(t, dur):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (24, 15, 10))
    draw = ImageDraw.Draw(img)
    
    # 1. Sunset/Twilight Horizon & Starfield
    for s in range(80):
        sx = (s * 157) % WIDTH
        sy = (s * 73) % 420
        bright = int(170 + math.sin(t * 2.5 + s) * 85)
        draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 235, 200, bright))
        
    # Horizon golden glow
    for gy in range(260, 520, 20):
        alpha = int(45 * (1.0 - (gy - 260) / 260.0))
        draw.rectangle([0, gy, WIDTH, gy + 20], fill=(245, 158, 11, alpha))
        
    # 2. Epic Metropolis Skyline Below
    for bx in range(0, WIDTH + 90, 85):
        bh = 320 + (bx * 37) % 260
        draw.rectangle([bx, HEIGHT - 220 - bh, bx + 70, HEIGHT - 220], fill=(32, 22, 16))
        for wy in range(HEIGHT - 210 - bh, HEIGHT - 230, 36):
            if (bx + wy) % 2 == 0:
                draw.rectangle([bx + 14, wy, bx + 32, wy + 18], fill=(255, 195, 60, 190))
                
    # 3. High-altitude Penthouse Observation Terrace (Foreground)
    deck_y = HEIGHT - 240
    draw.rectangle([0, deck_y, WIDTH, HEIGHT], fill=(28, 20, 14))
    draw.line([0, deck_y, WIDTH, deck_y], fill=(245, 158, 11), width=4)
    # Sleek frameless glass railing with reflections
    draw.rectangle([0, deck_y - 80, WIDTH, deck_y], fill=(245, 158, 11, 25), outline=(245, 158, 11, 140), width=2)
    
    # 4. FATHER FIGURE (Majestic, Confident, Command Tablet)
    f_x = WIDTH // 2
    f_y = deck_y
    draw_kinematic_human(
        draw, f_x, f_y, scale=2.3, walk_phase=0,
        color=(255, 245, 235), hair_color=(45, 30, 20), clothes_color=(180, 83, 9),
        action="stand_hero", facing=1
    )
    
    # 5. Beams of Golden Power & Client Data Connecting City to Father
    tab_x = f_x + 75
    tab_y = f_y - 270
    for ray_idx in range(8):
        rx = 120 + ray_idx * 240
        ry = HEIGHT - 260
        ray_alpha = int(140 + math.sin(t * 4 + ray_idx) * 90)
        draw.line([rx, ry, tab_x, tab_y], fill=(245, 158, 11, ray_alpha), width=2)
        
    # Expanding Golden Radiance Rings
    for ring in range(3):
        r_rad = int((t * 85 + ring * 75) % 220) + 25
        alpha_ring = max(0, int(255 * (1.0 - r_rad / 245.0)))
        draw.ellipse([tab_x - r_rad, tab_y - r_rad, tab_x + r_rad, tab_y + r_rad], 
                     outline=(255, 215, 0, alpha_ring), width=3)
        
    # Floating Golden Sparks Drifting Upwards
    for sp in range(25):
        sp_x = (sp * 83 + int(math.sin(t * 2 + sp) * 40)) % WIDTH
        sp_y = int((HEIGHT - (t * 70 + sp * 35)) % HEIGHT)
        draw.ellipse([sp_x, sp_y, sp_x + 3, sp_y + 3], fill=(255, 225, 120, 200))
        
    return img


SCENE_RENDERERS = [
    render_scene_1_frame,
    render_scene_2_frame,
    render_scene_3_frame,
    render_scene_4_frame,
    render_scene_5_frame
]
