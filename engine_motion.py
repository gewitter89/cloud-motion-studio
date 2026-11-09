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
    font_large = ImageFont.truetype(FONT_PATH_TITLE, 52)
    font_sub = ImageFont.truetype(FONT_PATH_TITLE, 26)
    font_meta = ImageFont.truetype(FONT_PATH_TEXT, 22)
    font_small = ImageFont.truetype(FONT_PATH_TEXT, 18)
except Exception:
    font_large = font_sub = font_meta = font_small = ImageFont.load_default()

def draw_person(draw, x, y, scale=1.0, walk_phase=0.0, color=(240, 245, 255), has_phone=True, phone_glow=(0, 240, 255)):
    # Head
    head_r = int(14 * scale)
    head_y = int(y - 120 * scale)
    draw.ellipse([x - head_r, head_y - head_r, x + head_r, head_y + head_r], fill=color)
    
    # Body
    neck_y = head_y + head_r
    pelvis_y = int(y - 55 * scale)
    draw.line([x, neck_y, x, pelvis_y], fill=color, width=max(2, int(6 * scale)))
    
    # Legs (walking cycle with sine/cosine)
    leg_len = int(55 * scale)
    leg1_angle = math.sin(walk_phase) * 0.45
    leg2_angle = -math.sin(walk_phase) * 0.45
    
    k1_x = x + math.sin(leg1_angle) * (leg_len * 0.55)
    k1_y = pelvis_y + math.cos(leg1_angle) * (leg_len * 0.55)
    f1_x = k1_x + math.sin(leg1_angle * 0.8) * (leg_len * 0.45)
    f1_y = k1_y + math.cos(leg1_angle * 0.8) * (leg_len * 0.45)
    
    k2_x = x + math.sin(leg2_angle) * (leg_len * 0.55)
    k2_y = pelvis_y + math.cos(leg2_angle) * (leg_len * 0.55)
    f2_x = k2_x + math.sin(leg2_angle * 0.8) * (leg_len * 0.45)
    f2_y = k2_y + math.cos(leg2_angle * 0.8) * (leg_len * 0.45)
    
    draw.line([x, pelvis_y, k1_x, k1_y, f1_x, f1_y], fill=color, width=max(2, int(5 * scale)))
    draw.line([x, pelvis_y, k2_x, k2_y, f2_x, f2_y], fill=color, width=max(2, int(5 * scale)))
    
    # Arms
    shoulder_y = neck_y + int(10 * scale)
    if has_phone:
        # Left arm swings, right arm holds glowing phone
        arm1_angle = -math.sin(walk_phase) * 0.4
        a1_x = x + math.sin(arm1_angle) * (40 * scale)
        a1_y = shoulder_y + math.cos(arm1_angle) * (40 * scale)
        draw.line([x, shoulder_y, a1_x, a1_y], fill=color, width=max(2, int(4 * scale)))
        
        # Phone arm (bent toward face)
        elbow_x = x + int(16 * scale)
        elbow_y = shoulder_y + int(22 * scale)
        hand_x = x + int(24 * scale)
        hand_y = shoulder_y + int(6 * scale)
        draw.line([x, shoulder_y, elbow_x, elbow_y, hand_x, hand_y], fill=color, width=max(2, int(4 * scale)))
        
        # Phone + screen glow
        phone_w = int(7 * scale)
        phone_h = int(12 * scale)
        draw.rectangle([hand_x, hand_y - phone_h, hand_x + phone_w, hand_y], fill=(20, 20, 25))
        draw.rectangle([hand_x + 1, hand_y - phone_h + 1, hand_x + phone_w - 1, hand_y - 1], fill=phone_glow)
    else:
        # Both arms swing or gesture
        arm1_angle = math.sin(walk_phase) * 0.5
        arm2_angle = -math.sin(walk_phase) * 0.5
        draw.line([x, shoulder_y, x + math.sin(arm1_angle) * 40 * scale, shoulder_y + math.cos(arm1_angle) * 40 * scale], fill=color, width=max(2, int(4 * scale)))
        draw.line([x, shoulder_y, x + math.sin(arm2_angle) * 40 * scale, shoulder_y + math.cos(arm2_angle) * 40 * scale], fill=color, width=max(2, int(4 * scale)))

def draw_hud(draw, scene_num, scene_title, scene_sub, current_time, total_time, accent_rgb):
    # Top Bar
    draw.rectangle([0, 0, WIDTH, 80], fill=(7, 10, 16))
    draw.line([0, 80, WIDTH, 80], fill=accent_rgb, width=2)
    
    draw.text((60, 25), "KINETIC MOTION ENGINE // CLOUD AUTONOMOUS ANIMATION", fill=accent_rgb, font=font_meta)
    
    mins = int(current_time // 60)
    secs = int(current_time % 60)
    tmins = int(total_time // 60)
    tsecs = int(total_time % 60)
    tc_str = f"TIMECODE: {mins:02d}:{secs:02d} / {tmins:02d}:{tsecs:02d}"
    draw.text((WIDTH - 360, 25), tc_str, fill=(160, 175, 200), font=font_meta)
    
    # Bottom HUD Bar
    draw.rectangle([0, HEIGHT - 100, WIDTH, HEIGHT], fill=(7, 10, 16))
    draw.line([0, HEIGHT - 100, WIDTH, HEIGHT - 100], fill=accent_rgb, width=2)
    
    # Progress line
    prog_w = int((current_time / max(1, total_time)) * (WIDTH - 120))
    draw.rectangle([60, HEIGHT - 92, WIDTH - 60, HEIGHT - 88], fill=(30, 40, 60))
    draw.rectangle([60, HEIGHT - 92, 60 + prog_w, HEIGHT - 88], fill=accent_rgb)
    
    # Titles
    draw.text((60, HEIGHT - 75), f"ГЛАВА {scene_num}: {scene_title}", fill=(255, 255, 255), font=font_sub)
    draw.text((60, HEIGHT - 42), scene_sub, fill=accent_rgb, font=font_small)
    
    # Mini Equalizer (audio reactive simulation)
    eq_x = WIDTH - 260
    for b in range(16):
        h_bar = int(12 + math.sin(current_time * 8 + b * 0.7) * 10 + math.cos(current_time * 14 - b) * 6)
        draw.rectangle([eq_x + b * 11, HEIGHT - 35 - h_bar, eq_x + b * 11 + 6, HEIGHT - 35], fill=accent_rgb)

def render_scene_1_frame(t, dur):
    # Scene 1: Chaos & City (Homes, Buildings, Street, People walking with phones)
    img = Image.new("RGBA", (WIDTH, HEIGHT), (12, 14, 22))
    draw = ImageDraw.Draw(img)
    
    cam_x = t * 45  # Camera pans right
    
    # Far Skyline (dark buildings)
    for bx in range(-400, WIDTH + 600, 140):
        screen_bx = bx - int(cam_x * 0.3) % 800
        b_h = 420 + (bx % 230)
        draw.rectangle([screen_bx, HEIGHT - 100 - b_h, screen_bx + 110, HEIGHT - 100], fill=(18, 22, 34))
    
    # Midground Buildings (Homes & High-rises)
    building_configs = [
        (100, 560, 200, "#161b2b"), (340, 680, 240, "#1a2136"), (620, 500, 180, "#141926"),
        (840, 740, 260, "#1c243a"), (1140, 590, 210, "#171e2e"), (1390, 650, 230, "#192238"),
        (1660, 530, 190, "#151b2a"), (1890, 710, 250, "#1d263f"), (2180, 570, 220, "#171e2e")
    ]
    
    for (orig_bx, b_h, b_w, col) in building_configs:
        bx = int(orig_bx - (cam_x * 0.75) % 2100)
        top_y = HEIGHT - 100 - b_h
        draw.rectangle([bx, top_y, bx + b_w, HEIGHT - 100], fill=col)
        
        # Rooftop antenna with blinking red beacon
        ant_x = bx + b_w // 2
        draw.line([ant_x, top_y, ant_x, top_y - 45], fill=(80, 90, 110), width=2)
        if int(t * 3) % 2 == 0:
            draw.ellipse([ant_x - 4, top_y - 49, ant_x + 4, top_y - 41], fill=(255, 60, 60))
            draw.arc([ant_x - 12, top_y - 57, ant_x + 12, top_y - 33], 0, 360, fill=(255, 80, 80))
            
        # Lighted windows grid
        for wy in range(top_y + 35, HEIGHT - 120, 42):
            for wx in range(bx + 20, bx + b_w - 25, 36):
                win_hash = (wx * 17 + wy * 31) % 10
                if win_hash < 4:
                    win_color = (255, 230, 140) if win_hash < 3 else (0, 220, 255)
                    draw.rectangle([wx, wy, wx + 18, wy + 24], fill=win_color)
                else:
                    draw.rectangle([wx, wy, wx + 18, wy + 24], fill=(30, 38, 55))
                    
    # Street pavement & sidewalk
    draw.rectangle([0, HEIGHT - 160, WIDTH, HEIGHT - 100], fill=(25, 30, 45))
    draw.line([0, HEIGHT - 160, WIDTH, HEIGHT - 160], fill=(60, 75, 105), width=3)
    
    # Streetlights
    for lx in range(80, WIDTH + 400, 380):
        sl_x = int(lx - (cam_x * 0.9) % 1200)
        draw.line([sl_x, HEIGHT - 160, sl_x, HEIGHT - 330], fill=(90, 100, 120), width=4)
        draw.line([sl_x, HEIGHT - 330, sl_x + 35, HEIGHT - 330], fill=(90, 100, 120), width=4)
        draw.polygon([(sl_x + 35, HEIGHT - 330), (sl_x - 30, HEIGHT - 160), (sl_x + 100, HEIGHT - 160)], fill=(255, 240, 160, 35))
        draw.ellipse([sl_x + 30, HEIGHT - 334, sl_x + 40, HEIGHT - 326], fill=(255, 255, 200))
        
    # Moving people (человечки) walking with smartphones
    for p_idx in range(5):
        base_px = 120 + p_idx * 340
        person_x = int((base_px + t * (40 + p_idx * 15)) % (WIDTH + 200) - 100)
        walk_phase = t * 6 + p_idx
        draw_person(draw, person_x, HEIGHT - 158, scale=1.1, walk_phase=walk_phase, color=(240, 245, 255), has_phone=True, phone_glow=(255, 60, 60))
        
        # Flying red exclamation / notification badges over their heads (Chaos)
        badge_y = int(HEIGHT - 310 - math.sin(t * 4 + p_idx) * 15)
        draw.ellipse([person_x + 15, badge_y - 12, person_x + 39, badge_y + 12], fill=(255, 50, 75))
        draw.text((person_x + 23, badge_y - 8), "!", fill=(255, 255, 255), font=font_small)

    draw_hud(draw, 1, "ЦИФРОВОЙ ХАОС", "Бесконечный спам и перегрузка систем", t, dur, (255, 75, 100))
    return img

def render_scene_2_frame(t, dur):
    # Scene 2: Antigravity Strategic Core (Holographic Lab & Architect)
    img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 16, 28))
    draw = ImageDraw.Draw(img)
    
    # 3D Grid Floor
    vanish_x, vanish_y = WIDTH // 2, HEIGHT // 2 - 40
    for gx in range(-600, WIDTH + 700, 100):
        draw.line([gx, HEIGHT - 100, vanish_x + (gx - vanish_x) * 0.15, vanish_y + 160], fill=(20, 60, 90), width=1)
    for gy in range(HEIGHT - 100, vanish_y + 160, -35):
        draw.line([0, gy, WIDTH, gy], fill=(20, 60, 90), width=1)
        
    # Holographic Architectural Matrix (Floating assembling blocks)
    center_x = WIDTH // 2 + 180
    center_y = HEIGHT // 2 - 50
    rot = t * 0.8
    nodes = []
    for deg in range(0, 360, 60):
        rad = math.radians(deg + rot * 40)
        nx = center_x + math.cos(rad) * 180
        ny = center_y + math.sin(rad) * 90
        nodes.append((nx, ny))
        draw.ellipse([nx - 12, ny - 12, nx + 12, ny + 12], fill=(0, 240, 255))
        draw.rectangle([nx - 20, ny - 20, nx + 20, ny + 20], outline=(0, 240, 255), width=2)
        
    for i in range(len(nodes)):
        nxt = nodes[(i + 1) % len(nodes)]
        draw.line([nodes[i][0], nodes[i][1], nxt[0], nxt[1]], fill=(0, 200, 255), width=3)
        draw.line([nodes[i][0], nodes[i][1], center_x, center_y], fill=(0, 240, 255, 120), width=2)
        
    draw.ellipse([center_x - 30, center_y - 30, center_x + 30, center_y + 30], fill=(0, 240, 255, 200), outline=(255, 255, 255), width=3)
    
    # The Architect Character (standing in front of holographic console)
    arch_x = WIDTH // 2 - 280
    arch_y = HEIGHT - 220
    draw_person(draw, arch_x, arch_y, scale=1.7, walk_phase=0, color=(240, 250, 255), has_phone=False)
    
    # Holographic terminal screen in front of Architect
    term_x = arch_x + 60
    term_y = arch_y - 180
    draw.rectangle([term_x, term_y, term_x + 180, term_y + 110], fill=(0, 40, 70, 160), outline=(0, 240, 255), width=2)
    for ly in range(term_y + 15, term_y + 95, 18):
        l_len = int(60 + math.sin(t * 5 + ly) * 45)
        draw.line([term_x + 15, ly, term_x + 15 + l_len, ly], fill=(0, 240, 255), width=2)
        
    draw_hud(draw, 2, "АРХИТЕКТУРА ANTIGRAVITY", "Стратегический мозг и нерушимый фундамент", t, dur, (0, 240, 255))
    return img

def render_scene_3_frame(t, dur):
    # Scene 3: Claude Precision Engineering (Laser Surgery & Code Perfection)
    img = Image.new("RGBA", (WIDTH, HEIGHT), (16, 8, 28))
    draw = ImageDraw.Draw(img)
    
    # Holographic circuit lines on background
    for y_line in range(120, HEIGHT - 140, 80):
        draw.line([0, y_line, WIDTH, y_line], fill=(45, 20, 70), width=1)
        
    # Precision Laser Beam scanning
    laser_x = int((t * 180) % WIDTH)
    draw.line([laser_x, 80, laser_x, HEIGHT - 100], fill=(220, 100, 255), width=4)
    draw.line([laser_x - 8, 80, laser_x - 8, HEIGHT - 100], fill=(160, 50, 220, 80), width=12)
    
    # Coder Character at curved workstation
    coder_x = 420
    coder_y = HEIGHT - 240
    draw_person(draw, coder_x, coder_y, scale=1.6, walk_phase=0, color=(245, 235, 255), has_phone=False)
    
    # Massive Ultra-wide Curved Screen
    scr_x, scr_y, scr_w, scr_h = 560, 220, 950, 480
    draw.rectangle([scr_x, scr_y, scr_x + scr_w, scr_y + scr_h], fill=(12, 10, 22, 220), outline=(180, 80, 255), width=3)
    
    # Clean Code Lines
    code_lines = [
        "export async function deployAutonomousFleet() {",
        "  const kernel = await Antigravity.initCore();",
        "  const claudePrecision = new PrecisionEngine({ zeroLag: true });",
        "  await claudePrecision.neutralizeScanlines(); // CRT fixed",
        "  await kernel.bindSystemdFleet(['barber', 'radar', 'hud']);",
        "  return { status: 'ONLINE', freeDisk: '16GB', freeRAM: '3.5GB' };",
        "}"
    ]
    
    for i, line in enumerate(code_lines):
        col = (255, 200, 100) if "export" in line else ((0, 240, 255) if "await" in line else (220, 225, 240))
        draw.text((scr_x + 40, scr_y + 40 + i * 42), line, fill=col, font=font_sub)
        
    # Spinning Golden Precision Gear
    gx, gy = scr_x + scr_w - 120, scr_y + scr_h - 110
    rot = t * 2.5
    for a in range(0, 360, 45):
        rad = math.radians(a + rot * 30)
        draw.line([gx, gy, gx + math.cos(rad) * 45, gy + math.sin(rad) * 45], fill=(255, 190, 40), width=6)
    draw.ellipse([gx - 28, gy - 28, gx + 28, gy + 28], fill=(255, 190, 40))
    draw.ellipse([gx - 12, gy - 12, gx + 12, gy + 12], fill=(16, 8, 28))
    
    draw_hud(draw, 3, "ХИРУРГИЯ КОДА CLAUDE", "Устранение багов, полировка и чистый глянец", t, dur, (180, 90, 255))
    return img

def render_scene_4_frame(t, dur):
    # Scene 4: Autonomous Fleet in Action (Barber Lab Shop, Radar Tower, Server Racks)
    img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 24, 20))
    draw = ImageDraw.Draw(img)
    
    # Ground
    draw.rectangle([0, HEIGHT - 180, WIDTH, HEIGHT - 100], fill=(20, 35, 30))
    draw.line([0, HEIGHT - 180, WIDTH, HEIGHT - 180], fill=(40, 80, 65), width=3)
    
    # 1. Barber Shop Building (Left)
    shop_x, shop_y, shop_w, shop_h = 100, HEIGHT - 680, 520, 500
    draw.rectangle([shop_x, shop_y, shop_x + shop_w, shop_y + shop_h], fill=(28, 42, 38), outline=(50, 180, 120), width=3)
    
    # Neon Sign
    draw.rectangle([shop_x + 60, shop_y - 50, shop_x + shop_w - 60, shop_y], fill=(10, 20, 16), outline=(245, 158, 11), width=2)
    draw.text((shop_x + 95, shop_y - 42), "💈 BARBER LAB TMA", fill=(245, 158, 11), font=font_sub)
    
    # Rotating Barber Pole
    pole_x = shop_x + shop_w - 35
    draw.rectangle([pole_x, shop_y + 40, pole_x + 22, shop_y + 160], fill=(255, 255, 255), outline=(100, 100, 100), width=2)
    for s in range(6):
        stripe_y = shop_y + 40 + (int(t * 60 + s * 22) % 120)
        draw.line([pole_x, stripe_y, pole_x + 22, stripe_y - 12], fill=(220, 40, 40), width=5)
        
    # Large Glass Window with Master and Client
    win_x, win_y, win_w, win_h = shop_x + 40, shop_y + 80, shop_w - 100, 300
    draw.rectangle([win_x, win_y, win_x + win_w, win_y + win_h], fill=(15, 30, 26, 230), outline=(0, 240, 200), width=2)
    
    # Client in barber chair
    draw_person(draw, win_x + 130, win_y + win_h - 20, scale=1.2, walk_phase=0, color=(200, 230, 220), has_phone=False)
    # Master cutting hair
    draw_person(draw, win_x + 230, win_y + win_h - 20, scale=1.35, walk_phase=math.sin(t * 4) * 0.2, color=(255, 255, 255), has_phone=False)
    # Scissors glow
    draw.ellipse([win_x + 195, win_y + win_h - 130, win_x + 215, win_y + win_h - 110], fill=(255, 215, 0))
    
    # 2. Server Cloud Rack (Center)
    srv_x = 720
    srv_y = HEIGHT - 640
    draw.rectangle([srv_x, srv_y, srv_x + 360, srv_y + 460], fill=(12, 18, 22), outline=(0, 240, 255), width=2)
    draw.text((srv_x + 45, srv_y + 20), "VPS 169.58.30.140", fill=(0, 240, 255), font=font_sub)
    for rack in range(7):
        ry = srv_y + 70 + rack * 52
        draw.rectangle([srv_x + 20, ry, srv_x + 340, ry + 40], fill=(20, 28, 35))
        for led in range(8):
            led_col = (16, 185, 129) if (int(t * 10 + rack + led) % 3 != 0) else (0, 240, 255)
            draw.ellipse([srv_x + 40 + led * 34, ry + 15, srv_x + 50 + led * 34, ry + 25], fill=led_col)
            
    # 3. Radar Tower (Right)
    rad_x = 1450
    rad_y = HEIGHT - 650
    draw.line([rad_x - 60, HEIGHT - 180, rad_x, rad_y], fill=(80, 160, 120), width=4)
    draw.line([rad_x + 60, HEIGHT - 180, rad_x, rad_y], fill=(80, 160, 120), width=4)
    draw.line([rad_x - 35, HEIGHT - 320, rad_x + 35, HEIGHT - 320], fill=(80, 160, 120), width=3)
    draw.line([rad_x - 20, HEIGHT - 450, rad_x + 20, HEIGHT - 450], fill=(80, 160, 120), width=3)
    
    # Concentric Expanding Radar Waves
    for ring in range(3):
        r_size = int((t * 90 + ring * 80) % 240)
        draw.arc([rad_x - r_size, rad_y - r_size, rad_x + r_size, rad_y + r_size], 180, 360, fill=(16, 185, 129), width=3)
    draw.ellipse([rad_x - 16, rad_y - 16, rad_x + 16, rad_y + 16], fill=(255, 255, 255))
    draw.text((rad_x - 70, HEIGHT - 160), "RESELL RADAR", fill=(16, 185, 129), font=font_sub)

    draw_hud(draw, 4, "БОЕВОЙ ФЛОТ НА VPS", "Barber Lab TMA, радары и службы 24/7", t, dur, (16, 185, 129))
    return img

def render_scene_5_frame(t, dur):
    # Scene 5: The Master Command & Digital Empire (Father at panoramic rooftop)
    img = Image.new("RGBA", (WIDTH, HEIGHT), (22, 16, 8))
    draw = ImageDraw.Draw(img)
    
    # Starfield & Deep Horizon
    for s_idx in range(60):
        sx = (s_idx * 137) % WIDTH
        sy = (s_idx * 93) % (HEIGHT - 400)
        s_bright = int(180 + math.sin(t * 3 + s_idx) * 75)
        draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(s_bright, s_bright, s_bright))
        
    # Full Cybernetic City Skyline in the background below
    for bx in range(0, WIDTH, 90):
        b_h = 240 + (bx % 160)
        draw.rectangle([bx, HEIGHT - 200 - b_h, bx + 75, HEIGHT - 200], fill=(35, 28, 16))
        for wy in range(HEIGHT - 190 - b_h, HEIGHT - 210, 32):
            draw.rectangle([bx + 15, wy, bx + 30, wy + 16], fill=(255, 180, 50, 160))
            
    # Observation Terrace (Foreground)
    draw.rectangle([0, HEIGHT - 260, WIDTH, HEIGHT - 100], fill=(28, 22, 14))
    draw.line([0, HEIGHT - 260, WIDTH, HEIGHT - 260], fill=(245, 158, 11), width=4)
    # Glass railing
    draw.rectangle([0, HEIGHT - 330, WIDTH, HEIGHT - 260], fill=(245, 158, 11, 25), outline=(245, 158, 11, 120), width=2)
    
    # Father Figure (standing majestically at center with glowing phone)
    f_x = WIDTH // 2
    f_y = HEIGHT - 260
    draw_person(draw, f_x, f_y, scale=2.1, walk_phase=0, color=(255, 245, 220), has_phone=True, phone_glow=(255, 215, 0))
    
    # Energy rays streaming from city into Father's device
    dev_x = f_x + 50
    dev_y = f_y - 250
    for ray_idx in range(6):
        src_x = 100 + ray_idx * 320
        src_y = HEIGHT - 220
        draw.line([src_x, src_y, dev_x, dev_y], fill=(245, 158, 11, 140), width=2)
        
    # Expanding Golden Imperial Ring
    pulse_r = int((t * 70) % 200) + 20
    draw.ellipse([dev_x - pulse_r, dev_y - pulse_r, dev_x + pulse_r, dev_y + pulse_r], outline=(255, 215, 0, max(0, 255 - pulse_r)), width=3)
    
    draw_hud(draw, 5, "АБСОЛЮТНЫЙ РЕЗУЛЬТАТ", "Твоя цифровая империя: факты, скорость, порядок", t, dur, (245, 158, 11))
    return img

SCENE_RENDERERS = [
    render_scene_1_frame,
    render_scene_2_frame,
    render_scene_3_frame,
    render_scene_4_frame,
    render_scene_5_frame
]
