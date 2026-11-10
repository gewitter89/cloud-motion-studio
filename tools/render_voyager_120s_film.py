#!/usr/bin/env python3
"""
render_voyager_120s_film.py
High-performance 120-second (3600 frames @ 30 FPS) Master Cinematic Space Film.
"VOYAGER: The Loneliest Artifact"

Optimized for headless cloud rendering (GitHub Actions / Cloud VPS).
Pure NumPy + OpenCV + PIL vector rendering pipeline with 0 external GPU requirements.
"""

import os
import sys
import cv2
import numpy as np
import subprocess
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1920
HEIGHT = 1080
FPS = 30
TOTAL_FRAMES = 3600  # Exactly 120.0 seconds

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
PROD_DIR = os.path.join(ROOT_DIR, "production", "voyager_film")
FRAMES_DIR = os.path.join(PROD_DIR, "frames")
os.makedirs(FRAMES_DIR, exist_ok=True)

MASTER_AUDIO = os.path.join(PROD_DIR, "voyager_master_audio.mp3")
FINAL_OUTPUT = os.path.join(PROD_DIR, "voyager_120s_cinematic_master.mp4")
AUDIT_SHEET = os.path.join(PROD_DIR, "voyager_120s_audit_sheet.jpg")

# 1. Precompute Deep Space Starfield (1200 3D stars with parallax depths)
np.random.seed(1977)
NUM_STARS = 1200
star_x = np.random.uniform(-WIDTH, WIDTH * 2, NUM_STARS)
star_y = np.random.uniform(-HEIGHT, HEIGHT * 2, NUM_STARS)
star_z = np.random.uniform(0.2, 3.0, NUM_STARS) # depth layer
star_brightness = np.random.uniform(140, 255, NUM_STARS)
star_size = np.random.choice([1, 1, 2, 3], NUM_STARS, p=[0.7, 0.2, 0.08, 0.02])

# Subtitle configuration
try:
    font_sub = ImageFont.truetype("arialbd.ttf", 36)
    font_hud = ImageFont.truetype("arial.ttf", 20)
    font_title = ImageFont.truetype("arialbd.ttf", 64)
except Exception:
    font_sub = font_hud = font_title = ImageFont.load_default()

SUBTITLES = [
    # Act 1
    (0, 150, "Двадцать четыре миллиарда километров от Земли.", "двадцать четыре миллиарда"),
    (150, 360, "Там, где солнечный свет превращается в тусклую точку, а холод — в абсолют.", "абсолют"),
    (360, 570, "Здесь нет ни звука, ни эха. Только ледяная бесконечная пустота.", "пустота"),
    (570, 900, "Но сквозь тьму несётся самый далёкий объект человечества: Вояджер-Один.", "Вояджер-Один"),
    
    # Act 2
    (900, 1140, "Когда его запускали в 1977-м, никто не знал, выживет ли цивилизация.", "1977"),
    (1140, 1380, "На его борту закрепили Золотую Пластинку — послание неведомым мирам.", "Золотую Пластинку"),
    (1380, 1590, "Шум прибоя, раскаты грома, смех ребёнка и бессмертная музыка Баха.", "смех"),
    (1590, 1800, "Мы отправили в бездну свидетельство того, что мы умели любить.", "любить"),
    
    # Act 3
    (1800, 2040, "14 февраля 1990 года. Вояджер развернул свою камеру назад, к дому.", "назад"),
    (2040, 2280, "Земля. Крошечная голубая пылинка, подвешенная в солнечном луче.", "голубая пылинка"),
    (2280, 2520, "Все наши войны, короли, триумфы и трагедии происходили там.", "там"),
    (2520, 2700, "На одной песчинке посреди бескрайнего космического океана.", "океана"),
    
    # Act 4
    (2700, 2940, "Сегодня его реакторы остывают. Приборы угасают один за другим.", "остывают"),
    (2940, 3180, "Но даже когда погаснет само Солнце — Вояджер продолжит свой полёт.", "Солнце"),
    (3180, 3420, "Его золотая пластинка будет дрейфовать сквозь Млечный Путь миллиарды лет.", "миллиарды лет"),
    (3420, 3600, "Как вечное доказательство того, что однажды были мы.", "были мы")
]

def render_starfield(frame, t_sec, speed_mult=1.0):
    drift_x = -t_sec * 12.0 * speed_mult
    drift_y = -t_sec * 4.0 * speed_mult
    
    for i in range(NUM_STARS):
        sx = int((star_x[i] + drift_x * star_z[i]) % (WIDTH + 200)) - 100
        sy = int((star_y[i] + drift_y * star_z[i]) % (HEIGHT + 200)) - 100
        if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
            b = int(star_brightness[i] * (0.8 + 0.2 * np.sin(t_sec * 3.0 + i)))
            color = (b, int(b * 0.95), int(b * 0.9))
            sz = star_size[i]
            if sz == 1:
                frame[sy, sx] = color
            else:
                cv2.circle(frame, (sx, sy), sz, color, -1)

def draw_hud(im_pil, frame_idx):
    draw = ImageDraw.Draw(im_pil)
    t = frame_idx / FPS
    dist_km = 24192840000 + int(t * 17000) # moving at 17 km/s
    hud_text = f"VOYAGER 1 // DISTANCE: {dist_km:,} KM // TELEMETRY: ACTIVE"
    draw.text((60, 50), hud_text, font=font_hud, fill=(120, 200, 255))
    draw.line([(60, 80), (600, 80)], fill=(80, 140, 200), width=1)

def draw_subtitles(im_pil, frame_idx):
    for start_f, end_f, text, highlight in SUBTITLES:
        if start_f <= frame_idx < end_f:
            draw = ImageDraw.Draw(im_pil)
            bbox = draw.textbbox((0, 0), text, font=font_sub)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            cx = WIDTH // 2
            cy = 950
            
            # Dark pill background
            pad_x, pad_y = 26, 12
            overlay = Image.new('RGBA', im_pil.size, (0, 0, 0, 0))
            d_over = ImageDraw.Draw(overlay)
            d_over.rounded_rectangle([cx - tw//2 - pad_x, cy - pad_y, cx + tw//2 + pad_x, cy + th + pad_y], radius=14, fill=(10, 14, 22, 200))
            im_pil.paste(Image.alpha_composite(im_pil.convert('RGBA'), overlay).convert('RGB'))
            
            # Colored words
            draw = ImageDraw.Draw(im_pil)
            words = text.split()
            curr_x = cx - tw // 2
            for w in words:
                w_clean = w.strip(".,—«»").lower()
                is_hl = highlight.lower() in w_clean or any(hw in w_clean for hw in highlight.lower().split())
                fill = (255, 215, 60) if is_hl else (240, 245, 250)
                draw.text((curr_x, cy), w + " ", font=font_sub, fill=fill)
                w_box = draw.textbbox((0, 0), w + " ", font=font_sub)
                curr_x += (w_box[2] - w_box[0])
            break

print(f"Starting render of {TOTAL_FRAMES} frames (120s @ 30 FPS)...")

for f in range(TOTAL_FRAMES):
    t = f / FPS
    # Base dark interstellar background with soft nebular gradient
    frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    
    # -------------------------------------------------------------
    # ACT 1 (00:00 - 00:30): DEEP SPACE VOID & VOYAGER 1
    # -------------------------------------------------------------
    if f < 900:
        render_starfield(frame, t, 1.0)
        # Deep space nebula glow (cyan/magenta dust)
        nebula_alpha = 0.25
        cy, cx = int(HEIGHT * 0.4), int(WIDTH * 0.6)
        cv2.circle(frame, (cx, cy), 500, (60, 20, 40), -1)
        cv2.circle(frame, (cx - 150, cy + 100), 380, (40, 50, 20), -1)
        frame = cv2.GaussianBlur(frame, (81, 81), 0)
        
        # Draw Voyager 1 Probe Model
        # Slow cinematic drift: probe moves from bottom-left towards upper-right
        p = f / 899.0
        vx = int(450 + p * 200)
        vy = int(580 - p * 120)
        v_scale = 1.0 + p * 0.15
        
        # Parabolic High-Gain Antenna (White dish with specular rim)
        dish_r = int(140 * v_scale)
        cv2.ellipse(frame, (vx, vy), (dish_r, int(dish_r * 0.45)), -25, 0, 360, (230, 235, 245), -1, lineType=cv2.LINE_AA)
        cv2.ellipse(frame, (vx, vy), (dish_r, int(dish_r * 0.45)), -25, 0, 360, (140, 150, 170), 3, lineType=cv2.LINE_AA)
        # Sub-reflector tripod
        feed_x = int(vx + 45 * v_scale)
        feed_y = int(vy - 65 * v_scale)
        cv2.circle(frame, (feed_x, feed_y), int(14 * v_scale), (240, 240, 240), -1, lineType=cv2.LINE_AA)
        cv2.line(frame, (vx - int(60*v_scale), vy), (feed_x, feed_y), (160, 165, 175), 2, lineType=cv2.LINE_AA)
        cv2.line(frame, (vx + int(60*v_scale), vy), (feed_x, feed_y), (160, 165, 175), 2, lineType=cv2.LINE_AA)
        # Main bus body (octagonal gold-wrapped chassis)
        bx, by = int(vx - 20 * v_scale), int(vy + 45 * v_scale)
        cv2.rectangle(frame, (bx - int(45*v_scale), by - int(30*v_scale)), (bx + int(45*v_scale), by + int(30*v_scale)), (40, 120, 180), -1)
        # Magnetometer boom extending to right
        cv2.line(frame, (bx + int(45*v_scale), by), (bx + int(320*v_scale), by - int(90*v_scale)), (180, 190, 200), 2, lineType=cv2.LINE_AA)
        # RTG Nuclear Generators (3 dark cylinders)
        cv2.line(frame, (bx - int(45*v_scale), by), (bx - int(180*v_scale), by + int(70*v_scale)), (100, 110, 120), 4, lineType=cv2.LINE_AA)
        cv2.circle(frame, (bx - int(180*v_scale), by + int(70*v_scale)), int(18*v_scale), (60, 65, 75), -1, lineType=cv2.LINE_AA)
        
    # -------------------------------------------------------------
    # ACT 2 (00:30 - 01:00): THE GOLDEN RECORD
    # -------------------------------------------------------------
    elif f < 1800:
        render_starfield(frame, t, 0.4)
        p = (f - 900) / 899.0
        # Macro rotating Golden Record
        rcx, rcy = WIDTH // 2, HEIGHT // 2
        r_radius = int(380 + p * 40)
        
        # Outer Gold disc
        cv2.circle(frame, (rcx, rcy), r_radius, (30, 160, 220), -1, lineType=cv2.LINE_AA)
        # Fine concentric audio grooves
        for gr in range(120, r_radius - 20, 12):
            cv2.circle(frame, (rcx, rcy), gr, (20, 130, 185), 1, lineType=cv2.LINE_AA)
            
        # Center spindle hole & mounting bracket
        cv2.circle(frame, (rcx, rcy), 45, (15, 80, 120), -1, lineType=cv2.LINE_AA)
        cv2.circle(frame, (rcx, rcy), 12, (240, 240, 240), -1, lineType=cv2.LINE_AA)
        
        # Pulsar Map engraving (lines radiating from center)
        rot_angle = p * 0.4
        for a_idx, ang in enumerate(np.linspace(0, 2 * np.pi, 14, endpoint=False)):
            cur_ang = ang + rot_angle
            line_len = 110 + (a_idx % 5) * 35
            lx = int(rcx + line_len * np.cos(cur_ang))
            ly = int(rcy + line_len * np.sin(cur_ang))
            cv2.line(frame, (rcx, rcy), (lx, ly), (220, 240, 255), 2, lineType=cv2.LINE_AA)
            # Binary tick marks at line ends
            cv2.circle(frame, (lx, ly), 3, (255, 255, 255), -1)
            
        # Specular light gleam sweeping across the golden surface
        sweep_x = int(rcx - r_radius + (r_radius * 2) * p)
        gleam = frame.copy()
        cv2.line(gleam, (sweep_x - 100, 0), (sweep_x + 100, HEIGHT), (255, 255, 255), 60)
        gleam = cv2.GaussianBlur(gleam, (41, 41), 0)
        cv2.addWeighted(frame, 0.85, gleam, 0.15, 0, frame)

    # -------------------------------------------------------------
    # ACT 3 (01:00 - 01:30): THE PALE BLUE DOT (1990)
    # -------------------------------------------------------------
    elif f < 2700:
        render_starfield(frame, t, 0.2)
        p = (f - 1800) / 899.0
        
        # The iconic 45-degree sunbeam scattering through camera lens
        beam_overlay = frame.copy()
        pts = np.array([
            [WIDTH * 0.35, 0], [WIDTH * 0.52, 0],
            [WIDTH * 0.75, HEIGHT], [WIDTH * 0.58, HEIGHT]
        ], np.int32)
        cv2.fillPoly(beam_overlay, [pts], (40, 100, 180)) # Warm golden brown ray
        beam_overlay = cv2.GaussianBlur(beam_overlay, (51, 51), 0)
        cv2.addWeighted(frame, 0.82, beam_overlay, 0.18, 0, frame)
        
        # Second softer sunbeam
        pts2 = np.array([
            [WIDTH * 0.15, 0], [WIDTH * 0.26, 0],
            [WIDTH * 0.45, HEIGHT], [WIDTH * 0.34, HEIGHT]
        ], np.int32)
        beam_overlay2 = frame.copy()
        cv2.fillPoly(beam_overlay2, [pts2], (30, 80, 150))
        beam_overlay2 = cv2.GaussianBlur(beam_overlay2, (41, 41), 0)
        cv2.addWeighted(frame, 0.9, beam_overlay2, 0.10, 0, frame)
        
        # The Pale Blue Dot (Earth: a single vibrant cyan pixel suspended in the ray)
        dot_x = int(WIDTH * 0.58 + p * 15)
        dot_y = int(HEIGHT * 0.52 - p * 10)
        
        # Diffuse glow ring around Earth
        pulse = 0.8 + 0.2 * np.sin(t * 4.0)
        cv2.circle(frame, (dot_x, dot_y), int(12 * pulse), (200, 160, 60), -1, lineType=cv2.LINE_AA)
        cv2.circle(frame, (dot_x, dot_y), int(6 * pulse), (255, 230, 140), -1, lineType=cv2.LINE_AA)
        # Center core Earth pixel: Cyan/Blue (RGB: 100, 200, 255)
        cv2.circle(frame, (dot_x, dot_y), 2, (255, 220, 120), -1)

    # -------------------------------------------------------------
    # ACT 4 (01:30 - 02:00): ETERNAL IMMORTALITY
    # -------------------------------------------------------------
    else:
        p = (f - 2700) / 899.0
        render_starfield(frame, t, 1.2)
        
        # Dense Milky Way galactic dust band in background
        dust_overlay = frame.copy()
        cv2.ellipse(dust_overlay, (WIDTH//2, HEIGHT//2), (WIDTH, int(HEIGHT * 0.4)), -18, 0, 360, (70, 40, 60), -1)
        dust_overlay = cv2.GaussianBlur(dust_overlay, (101, 101), 0)
        cv2.addWeighted(frame, 0.8, dust_overlay, 0.2, 0, frame)
        
        # Pullback: Voyager shrinks into a tiny distant beacon
        vx = int(WIDTH * 0.55 + p * 80)
        vy = int(HEIGHT * 0.45 - p * 60)
        v_size = max(2, int(20 * (1.0 - p * 0.85)))
        
        # Fading beacon pulse
        cv2.circle(frame, (vx, vy), v_size + 4, (100, 180, 240), -1, lineType=cv2.LINE_AA)
        cv2.circle(frame, (vx, vy), v_size, (255, 255, 255), -1, lineType=cv2.LINE_AA)
        
        # Final fade to black in the last 2 seconds
        if f > 3540:
            fade = (3600 - f) / 60.0
            frame = (frame * fade).astype(np.uint8)

    # Add HUD and Subtitles via PIL
    im_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw_hud(im_pil, f)
    draw_subtitles(im_pil, f)
    final_frame = cv2.cvtColor(np.array(im_pil), cv2.COLOR_RGB2BGR)

    frame_path = os.path.join(FRAMES_DIR, f"frame_{f:04d}.png")
    cv2.imwrite(frame_path, final_frame)
    if f % 300 == 0:
        print(f"   Rendered frame {f}/{TOTAL_FRAMES} (t={t:.1f}s)")

print("All 3600 frames rendered! Encoding final master H.264 video with audio muxing...")

raw_tmp = os.path.join(PROD_DIR, "tmp_voyager_noaudio.mp4")

# Encode video
cmd_video = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", os.path.join(FRAMES_DIR, "frame_%04d.png"),
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    raw_tmp
]
subprocess.run(cmd_video, check=True)

# Mux with master audio
cmd_mux = [
    "ffmpeg", "-y",
    "-i", raw_tmp,
    "-i", MASTER_AUDIO,
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "256k",
    "-shortest",
    FINAL_OUTPUT
]
subprocess.run(cmd_mux, check=True)

if os.path.exists(raw_tmp):
    os.remove(raw_tmp)

print("Generating 12-frame audit contact sheet...")
cap = cv2.VideoCapture(FINAL_OUTPUT)
fps = cap.get(cv2.CAP_PROP_FPS)
sample_indices = [int(i * FPS * 10) for i in range(12)] # every 10s
sampled = []
for idx in sample_indices:
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ret, fr = cap.read()
    if ret:
        im = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).resize((480, 270), Image.Resampling.LANCZOS)
        d = ImageDraw.Draw(im)
        d.text((10, 10), f"t = {idx/FPS:.0f}s", fill=(255, 215, 60))
        sampled.append(im)
cap.release()

sheet = Image.new('RGB', (1920, 810), (12, 16, 24))
for i in range(4):
    for j in range(3):
        idx = j * 4 + i
        if idx < len(sampled):
            sheet.paste(sampled[idx], (i * 480, j * 270))
sheet.save(AUDIT_SHEET, quality=95)

print(f"SUCCESS: Voyager Master Film rendered at {FINAL_OUTPUT}")
print(f"Audit sheet saved at {AUDIT_SHEET}")
