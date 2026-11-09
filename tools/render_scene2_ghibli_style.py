#!/usr/bin/env python3
"""
Atmospheric 2.5D Motion Engine for Scene 2 (Berlin Wall Breach & Triumph).
Rendered with 4K Supersampling (Downscaled to 1080p with Anti-Aliasing).
Multi-core parallel rendering (ProcessPoolExecutor) for maximum VPS throughput.
"""

import os
import sys
import math
import subprocess
from concurrent.futures import ProcessPoolExecutor
from PIL import Image, ImageDraw, ImageFont

CANVAS_W = 3840
CANVAS_H = 2160
OUT_W = 1920
OUT_H = 1080

FPS = 30
DURATION_SEC = 24.62
TOTAL_FRAMES = int(FPS * DURATION_SEC)

GROUND_Y = int(CANVAS_H * 0.82)
WALL_TOP_Y = int(CANVAS_H * 0.36)
WALL_CX = CANVAS_W // 2
FRAMES_DIR = "/tmp/scene2_ghibli_frames"

def get_font_4k(size, bold=False):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_detailed_silhouette(draw, cx, cy, scale=1.0, pose="triumph", coat_color=(20, 24, 36), facing=1, rim_color=(251, 191, 36)):
    s = scale * 2.0
    head_r = int(22 * s)
    head_y = int(cy - 180 * s)
    head_x = int(cx)
    
    def draw_poly_rim(points, fill_col, rim_width=3):
        draw.polygon(points, fill=fill_col)
        if rim_color:
            for i in range(len(points) - 1):
                p_a, p_b = points[i], points[i+1]
                if p_a[1] < cy - 40*s or (facing == 1 and p_a[0] < cx) or (facing == -1 and p_a[0] > cx):
                    draw.line([p_a, p_b], fill=rim_color, width=int(rim_width * s))

    if pose == "triumph":
        draw.ellipse([head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r], fill=coat_color)
        if rim_color:
            draw.arc([head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r], start=180, end=360, fill=rim_color, width=int(3*s))
            
        coat_pts = [
            (head_x - int(24*s), head_y + head_r),
            (head_x + int(24*s), head_y + head_r),
            (head_x + int(32*s), cy - int(60*s)),
            (head_x + int(48*s) * facing, cy - int(10*s)),
            (head_x + int(15*s), cy - int(30*s)),
            (head_x - int(15*s), cy - int(30*s)),
            (head_x - int(42*s) * facing, cy - int(15*s)),
            (head_x - int(30*s), cy - int(60*s))
        ]
        draw_poly_rim(coat_pts, coat_color, rim_width=3)
        
        # Legs and Boots
        draw.polygon([
            (head_x - int(22*s), cy - int(35*s)),
            (head_x - int(32*s), cy),
            (head_x - int(12*s), cy),
            (head_x - int(8*s), cy - int(35*s))
        ], fill=(14, 18, 28))
        draw.polygon([
            (head_x - int(42*s), cy),
            (head_x - int(8*s), cy),
            (head_x - int(10*s), cy + int(8*s)),
            (head_x - int(44*s), cy + int(8*s))
        ], fill=(10, 12, 18))
        
        draw.polygon([
            (head_x + int(8*s), cy - int(35*s)),
            (head_x + int(12*s), cy),
            (head_x + int(32*s), cy),
            (head_x + int(22*s), cy - int(35*s))
        ], fill=(14, 18, 28))
        draw.polygon([
            (head_x + int(8*s), cy),
            (head_x + int(42*s), cy),
            (head_x + int(44*s), cy + int(8*s)),
            (head_x + int(10*s), cy + int(8*s))
        ], fill=(10, 12, 18))
        
        # Raised Arms
        arm_l = [
            (head_x - int(22*s), head_y + int(15*s)),
            (head_x - int(48*s), head_y - int(35*s)),
            (head_x - int(40*s), head_y - int(45*s)),
            (head_x - int(14*s), head_y + int(10*s))
        ]
        draw_poly_rim(arm_l, coat_color, rim_width=3)
        draw.ellipse([head_x - int(56*s), head_y - int(56*s), head_x - int(38*s), head_y - int(38*s)], fill=(255, 230, 210))
        
        arm_r = [
            (head_x + int(14*s), head_y + int(10*s)),
            (head_x + int(40*s), head_y - int(45*s)),
            (head_x + int(48*s), head_y - int(35*s)),
            (head_x + int(22*s), head_y + int(15*s))
        ]
        draw_poly_rim(arm_r, coat_color, rim_width=3)
        draw.ellipse([head_x + int(38*s), head_y - int(56*s), head_x + int(56*s), head_y - int(38*s)], fill=(255, 230, 210))

    elif pose == "climb_reach":
        neck_x = head_x + int(35*s * facing)
        neck_y = head_y + int(30*s)
        draw.ellipse([neck_x - head_r, neck_y - head_r - int(10*s), neck_x + head_r, neck_y + head_r - int(10*s)], fill=coat_color)
        draw.polygon([
            (head_x - int(15*s), cy - int(20*s)),
            (neck_x + int(15*s), neck_y),
            (neck_x - int(15*s), neck_y + int(20*s)),
            (head_x - int(35*s), cy - int(10*s))
        ], fill=coat_color)
        
        hand_x = neck_x + int(50*s * facing)
        hand_y = neck_y + int(100*s)
        draw.line([neck_x, neck_y + int(10*s), neck_x + int(25*s * facing), neck_y + int(50*s), hand_x, hand_y], fill=coat_color, width=int(12*s))
        draw.ellipse([hand_x - int(8*s), hand_y - int(8*s), hand_x + int(8*s), hand_y + int(8*s)], fill=(255, 230, 210))

    elif pose == "climb_pull":
        draw.ellipse([head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r], fill=coat_color)
        draw.polygon([
            (head_x - int(20*s), head_y + head_r),
            (head_x + int(20*s), head_y + head_r),
            (head_x + int(16*s), cy - int(30*s)),
            (head_x - int(16*s), cy - int(30*s))
        ], fill=coat_color)
        
        reach_x = head_x - int(35*s * facing)
        reach_y = head_y - int(60*s)
        draw.line([head_x, head_y + int(15*s), reach_x, reach_y], fill=coat_color, width=int(12*s))
        draw.ellipse([reach_x - int(8*s), reach_y - int(8*s), reach_x + int(8*s), reach_y + int(8*s)], fill=(255, 230, 210))

def render_frame_4k(frame_idx):
    t = frame_idx / FPS
    
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (10, 12, 22, 255))
    draw = ImageDraw.Draw(img)
    
    sun_bloom = min(1.0, max(0.0, (t - 4.5) / 12.0))
    
    # 1. Sky Gradient
    for y in range(0, GROUND_Y, 20):
        factor = y / GROUND_Y
        r = int(12 + 45 * factor + (210 - 12) * factor * (sun_bloom ** 1.3))
        g = int(14 + 30 * factor + (140 - 14) * factor * (sun_bloom ** 1.5))
        b = int(28 + 65 * factor + (60 - 28) * factor * (sun_bloom ** 2.0))
        draw.rectangle([0, y, CANVAS_W, y + 20], fill=(min(255, r), min(255, g), min(255, b), 255))
        
    # 2. Moon & Clouds
    moon_x = int(CANVAS_W * 0.22)
    moon_y = int(CANVAS_H * 0.20)
    moon_r = 75
    for gr in range(moon_r + 160, moon_r, -15):
        alpha = int(25 * (1.0 - (gr - moon_r) / 160.0))
        draw.ellipse([moon_x - gr, moon_y - gr, moon_x + gr, moon_y + gr], fill=(235, 240, 255, alpha))
    draw.ellipse([moon_x - moon_r, moon_y - moon_r, moon_x + moon_r, moon_y + moon_r], fill=(245, 248, 255, 245))
    
    for c_i in range(5):
        c_x = int((c_i * 850 + t * 35) % (CANVAS_W + 600)) - 300
        c_y = int(CANVAS_H * 0.18 + c_i * 90 + math.sin(t * 0.5 + c_i) * 30)
        c_w = 420 + c_i * 120
        c_h = 110 + c_i * 30
        c_alpha = int(35 + sun_bloom * 40)
        draw.ellipse([c_x, c_y, c_x + c_w, c_y + c_h], fill=(180, 165, 210, c_alpha))
        draw.ellipse([c_x + 80, c_y - 40, c_x + c_w - 60, c_y + c_h], fill=(210, 190, 225, c_alpha - 10))

    # 3. Rising Sun & Volumetric Rays
    if sun_bloom > 0:
        sun_cx = WALL_CX
        sun_cy = int(WALL_TOP_Y + 180 - sun_bloom * 120)
        sun_radius = int(140 + sun_bloom * 80)
        for br in range(sun_radius + 400, sun_radius, -30):
            b_alpha = int(55 * sun_bloom * (1.0 - (br - sun_radius) / 400.0))
            draw.ellipse([sun_cx - br, sun_cy - br, sun_cx + br, sun_cy + br], fill=(251, 191, 36, b_alpha))
        draw.ellipse([sun_cx - sun_radius, sun_cy - sun_radius, sun_cx + sun_radius, sun_cy + sun_radius], fill=(255, 245, 210, int(230 * sun_bloom)))
        
        num_rays = 16
        for r_i in range(num_rays):
            angle = math.radians(-75 + r_i * 10 + math.sin(t * 1.2 + r_i) * 2.5)
            ray_len = 1600 * sun_bloom
            rx = sun_cx + math.sin(angle) * ray_len
            ry = sun_cy + math.cos(angle) * ray_len * 0.75
            draw.polygon([
                (sun_cx - 40, sun_cy),
                (sun_cx + 40, sun_cy),
                (rx + 140, ry),
                (rx - 140, ry)
            ], fill=(255, 215, 0, int(38 * sun_bloom)))

    # 4. Ground Plane
    draw.rectangle([0, GROUND_Y, CANVAS_W, CANVAS_H], fill=(20, 24, 34))
    for px in range(-400, CANVAS_W + 800, 280):
        draw.line([px, GROUND_Y, px + int((px - WALL_CX) * 0.7), CANVAS_H], fill=(32, 38, 52), width=4)
    draw.line([0, GROUND_Y, CANVAS_W, GROUND_Y], fill=(50, 60, 80), width=6)

    # 5. Wall Sections & Falling Slab
    collapse_prog = min(1.0, max(0.0, (t - 4.5) / 5.5))
    slab_tilt = collapse_prog * 32.0
    slab_fall = int((collapse_prog ** 2) * 440)
    
    wall_left_w = WALL_CX - 420
    wall_right_x = WALL_CX + 420
    
    # Left Wall
    draw.polygon([
        (0, GROUND_Y),
        (wall_left_w, GROUND_Y),
        (wall_left_w, WALL_TOP_Y + 70),
        (wall_left_w - 90, WALL_TOP_Y),
        (0, WALL_TOP_Y)
    ], fill=(58, 66, 82), outline=(35, 42, 54), width=5)
    for sx in range(240, wall_left_w, 320):
        draw.line([sx, WALL_TOP_Y, sx, GROUND_Y], fill=(42, 49, 62), width=5)
        draw.line([sx - 320, WALL_TOP_Y + 280, sx, WALL_TOP_Y + 280], fill=(48, 56, 70), width=3)
    draw.rectangle([0, WALL_TOP_Y - 24, wall_left_w - 80, WALL_TOP_Y], fill=(75, 85, 105), outline=(40, 48, 60), width=3)

    # Right Wall
    draw.polygon([
        (wall_right_x, GROUND_Y),
        (CANVAS_W, GROUND_Y),
        (CANVAS_W, WALL_TOP_Y),
        (wall_right_x + 90, WALL_TOP_Y),
        (wall_right_x, WALL_TOP_Y + 70)
    ], fill=(58, 66, 82), outline=(35, 42, 54), width=5)
    for sx in range(wall_right_x, CANVAS_W, 320):
        draw.line([sx, WALL_TOP_Y, sx, GROUND_Y], fill=(42, 49, 62), width=5)
        draw.line([sx, WALL_TOP_Y + 280, sx + 320, WALL_TOP_Y + 280], fill=(48, 56, 70), width=3)
    draw.rectangle([wall_right_x + 80, WALL_TOP_Y - 24, CANVAS_W, WALL_TOP_Y], fill=(75, 85, 105), outline=(40, 48, 60), width=3)

    # Falling Central Slab
    c_slab_top = min(GROUND_Y - 80, WALL_TOP_Y + slab_fall)
    rad = math.radians(slab_tilt)
    sw = 380
    sh = 760
    
    p1 = (WALL_CX - int(sw * 0.5 * math.cos(rad)), c_slab_top + int(sw * 0.18 * math.sin(rad)))
    p2 = (WALL_CX + int(sw * 0.5 * math.cos(rad)), c_slab_top - int(sw * 0.18 * math.sin(rad)))
    p3 = (p2[0] + 50, min(GROUND_Y, p2[1] + sh))
    p4 = (p1[0] - 50, min(GROUND_Y, p1[1] + sh))
    
    if collapse_prog > 0:
        draw.polygon([(p4[0], GROUND_Y), (p3[0], GROUND_Y), (p3[0] + 120, GROUND_Y + 160), (p4[0] - 120, GROUND_Y + 160)], fill=(12, 15, 22, 190))
        
    draw.polygon([p1, p2, p3, p4], fill=(78, 88, 106), outline=(38, 45, 58), width=5)

    # 6. Rubble & Dust
    if t > 5.0:
        for b in range(24):
            bx = WALL_CX - 380 + b * 32
            bh = int(24 + math.sin(b * 1.4) * 20 + (b % 4) * 14)
            bw = 45 + (b % 3) * 16
            by = GROUND_Y - bh
            draw.polygon([
                (bx, GROUND_Y),
                (bx + 10, by),
                (bx + bw - 10, by - 6),
                (bx + bw, GROUND_Y)
            ], fill=(100, 112, 132), outline=(45, 52, 65), width=3)
            
        dust_mult = min(1.0, (t - 5.0) / 3.0) * max(0.0, 1.0 - (t - 14.0) / 9.0)
        if dust_mult > 0:
            for d in range(16):
                dx = WALL_CX - 320 + d * 45 + int(math.sin(t * 2.5 + d) * 35)
                dy = GROUND_Y - int(40 + (d % 4) * 60 * dust_mult + math.sin(t * 1.8 + d) * 25)
                dr = int((65 + (d % 3) * 30) * dust_mult)
                draw.ellipse([dx - dr, dy - dr, dx + dr, dy + dr], fill=(215, 200, 175, int(50 * dust_mult)))

    # 7. Character Silhouettes
    casters_x = [WALL_CX - 520, WALL_CX - 280, WALL_CX + 260, WALL_CX + 520]
    for cx in casters_x:
        draw.polygon([(cx - 30, GROUND_Y), (cx + 30, GROUND_Y), (cx + 120, GROUND_Y + 220), (cx - 80, GROUND_Y + 220)], fill=(12, 16, 24, 150))

    if t < 10.5:
        climb_factor = min(1.0, t / 9.5)
        draw_detailed_silhouette(draw, wall_left_w - 70, WALL_TOP_Y + 60, scale=1.1, pose="climb_reach", facing=1)
        comrade_y = int(GROUND_Y - 70 - climb_factor * 480)
        draw_detailed_silhouette(draw, wall_left_w - 30, comrade_y, scale=1.05, pose="climb_pull", facing=1)
        draw_detailed_silhouette(draw, wall_right_x + 90, WALL_TOP_Y + 60, scale=1.1, pose="triumph" if t > 6.5 else "climb_pull", facing=-1)
    else:
        draw_detailed_silhouette(draw, WALL_CX - 30, c_slab_top, scale=1.35, pose="triumph", facing=1)
        draw_detailed_silhouette(draw, wall_left_w - 80, WALL_TOP_Y + 60, scale=1.2, pose="triumph", facing=1)
        draw_detailed_silhouette(draw, wall_right_x + 90, WALL_TOP_Y + 60, scale=1.2, pose="triumph", facing=-1)
        draw_detailed_silhouette(draw, WALL_CX - 620, GROUND_Y, scale=1.5, pose="triumph", facing=1)
        draw_detailed_silhouette(draw, WALL_CX + 620, GROUND_Y, scale=1.5, pose="triumph", facing=-1)

    # 8. Sleek Title Card
    font_title = get_font_4k(64, bold=True)
    font_sub = get_font_4k(42, bold=False)
    
    title_text = "9 НОЯБРЯ 1989 // ПАДЕНИЕ СТЕНЫ"
    sub_text = "Исторический прорыв: единство и свобода перед монолитом преград"
    
    pill_w = 1520
    pill_h = 160
    pill_x = 180
    pill_y = CANVAS_H - 260
    
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=24, fill=(14, 18, 30, 235), outline=(245, 158, 11, 210), width=4)
    draw.rectangle([pill_x, pill_y + 24, pill_x + 12, pill_y + pill_h - 24], fill=(245, 158, 11))
    
    draw.text((pill_x + 48, pill_y + 24), title_text, font=font_title, fill=(248, 250, 252))
    draw.text((pill_x + 48, pill_y + 94), sub_text, font=font_sub, fill=(203, 213, 225))

    # Fast downscale with bicubic filter for smooth 1080p
    img_1080p = img.resize((OUT_W, OUT_H), Image.Resampling.BICUBIC)
    return img_1080p

def render_worker(frame_idx):
    frame_file = os.path.join(FRAMES_DIR, f"frame_{frame_idx:04d}.png")
    if os.path.exists(frame_file) and os.path.getsize(frame_file) > 5000:
        return frame_idx
    img_1080p = render_frame_4k(frame_idx)
    img_1080p.save(frame_file)
    return frame_idx

def main():
    os.makedirs(FRAMES_DIR, exist_ok=True)
    out_video = "production/scene2_ghibli_preview.mp4"
    contact_sheet_path = "production/scene2_ghibli_contact_sheet.jpg"
    
    print(f"Parallel rendering {TOTAL_FRAMES} frames across 4 CPU cores...")
    with ProcessPoolExecutor(max_workers=4) as executor:
        for idx in executor.map(render_worker, range(TOTAL_FRAMES)):
            if idx % 100 == 0:
                print(f"Finished frame {idx}/{TOTAL_FRAMES} ({idx/TOTAL_FRAMES*100:.1f}%)")
                
    # Build Contact sheet
    print("Generating contact sheet...")
    sheet = Image.new("RGB", (4 * 480, 3 * 270), (12, 16, 25))
    step = TOTAL_FRAMES // 12
    for i in range(12):
        f_idx = min(TOTAL_FRAMES - 1, i * step)
        f_path = os.path.join(FRAMES_DIR, f"frame_{f_idx:04d}.png")
        if os.path.exists(f_path):
            img = Image.open(f_path)
            thumb = img.resize((480, 270), Image.Resampling.LANCZOS)
            sheet.paste(thumb, ((i % 4) * 480, (i // 4) * 270))
    sheet.save(contact_sheet_path, quality=94)
    print(f"Contact sheet saved: {contact_sheet_path}")
    
    # Mux with clean Russian audio
    audio_path = "male_voice_dsp.mp3"
    print("Muxing video with FFmpeg...")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(FRAMES_DIR, "frame_%04d.png"),
        "-i", audio_path,
        "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        out_video
    ]
    subprocess.run(cmd, check=True)
    print(f"Preview Video Ready: {out_video}")
    
    web_dir = "/var/www/signals"
    if os.path.exists(web_dir):
        import shutil
        shutil.copy(out_video, os.path.join(web_dir, "scene2_ghibli_preview.mp4"))
        shutil.copy(contact_sheet_path, os.path.join(web_dir, "scene2_ghibli_contact_sheet.jpg"))
        if os.path.exists(audio_path):
            shutil.copy(audio_path, os.path.join(web_dir, "male_voice_clean.mp3"))

if __name__ == "__main__":
    main()
