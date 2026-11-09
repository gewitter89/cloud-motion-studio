#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full Master 125s Motion Film Engine: '9 Ноября — Эпоха Свободы'
4K Supersampling (3840x2160 -> 1080p Bicubic)
Multi-Core Parallel Rendering (ProcessPoolExecutor) for Cloud VPS.
Follows STORYBOARD.md, BEAT_SHEET.csv, and STYLE_BIBLE.md.
"""

import os
import sys
import math
import time
import subprocess
from concurrent.futures import ProcessPoolExecutor
from PIL import Image, ImageDraw, ImageFont

# Frame & Dimension Constants
CANVAS_W = 3840
CANVAS_H = 2160
OUT_W = 1920
OUT_H = 1080

FPS = 30
TOTAL_FRAMES = 3757  # ~125.23 seconds

# Act Boundaries in Frames
ACT1_END = 798   # 0.00s - 26.60s (26.60s)
ACT2_END = 1537  # 26.60s - 51.23s (24.63s)
ACT3_END = 2297  # 51.23s - 76.57s (25.34s)
ACT4_END = 3067  # 76.57s - 102.23s (25.66s)
ACT5_END = 3757  # 102.23s - 125.23s (23.00s)

GROUND_Y = int(CANVAS_H * 0.82)
WALL_TOP_Y = int(CANVAS_H * 0.36)
FRAMES_DIR = "/tmp/full_film_frames"
os.makedirs(FRAMES_DIR, exist_ok=True)


def get_font_4k(size, bold=True):
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

# -------------------------------------------------------------
# Reusable Articulated Silhouette Drawing Function
# -------------------------------------------------------------
def draw_detailed_silhouette(draw, cx, cy, scale=1.0, pose="walk", coat_color=(18, 22, 34), facing=1, rim_color=None, anim_phase=0.0):
    """
    Draws an anatomically proportioned human silhouette with coat, hat, articulated legs and arms.
    Poses: 'walk', 'reach_wall', 'climb_reach', 'climb_pull', 'triumph', 'overlook'
    """
    s = scale * 2.0
    head_r = int(22 * s)
    head_y = int(cy - 180 * s)
    head_x = int(cx)

    def draw_poly_rim(points, fill_col, rim_width=3):
        draw.polygon(points, fill=fill_col)
        if rim_color:
            for i in range(len(points)):
                p_a = points[i]
                p_b = points[(i + 1) % len(points)]
                # Rim highlight on top or facing side
                if p_a[1] < cy - 30 * s or (facing == 1 and p_a[0] < cx + 20*s) or (facing == -1 and p_a[0] > cx - 20*s):
                    draw.line([p_a, p_b], fill=rim_color, width=int(rim_width * s))

    # --- POSE: WALK ---
    if pose == "walk":
        leg_swing = math.sin(anim_phase * 6.28)
        # Head & Hat
        draw.ellipse([head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r], fill=coat_color)
        draw.polygon([
            (head_x - int(32 * s), head_y - int(12 * s)),
            (head_x + int(36 * s * facing), head_y - int(14 * s)),
            (head_x + int(30 * s * facing), head_y - int(24 * s)),
            (head_x - int(20 * s), head_y - int(22 * s))
        ], fill=(12, 14, 22))
        
        # Coat Torso
        coat_pts = [
            (head_x - int(20 * s), head_y + head_r),
            (head_x + int(20 * s), head_y + head_r),
            (head_x + int(28 * s) + int(10 * s * facing), cy - int(60 * s)),
            (head_x + int(42 * s * facing) - int(leg_swing * 12 * s), cy - int(25 * s)),
            (head_x - int(35 * s * facing) - int(leg_swing * 8 * s), cy - int(25 * s)),
            (head_x - int(26 * s), cy - int(60 * s))
        ]
        draw_poly_rim(coat_pts, coat_color, rim_width=3)
        
        # Legs
        leg1_offset = int(leg_swing * 30 * s)
        leg2_offset = -leg1_offset
        # Back leg
        draw.line([head_x - int(10 * s), cy - int(35 * s), head_x - int(15 * s) + leg2_offset, cy], fill=(12, 15, 24), width=int(14 * s))
        draw.polygon([(head_x - int(25 * s) + leg2_offset, cy), (head_x + int(5 * s) + leg2_offset, cy), (head_x + int(5 * s) + leg2_offset, cy + int(6 * s)), (head_x - int(25 * s) + leg2_offset, cy + int(6 * s))], fill=(8, 10, 16))
        # Front leg
        draw.line([head_x + int(10 * s), cy - int(35 * s), head_x + int(15 * s) + leg1_offset, cy], fill=(16, 20, 30), width=int(15 * s))
        draw.polygon([(head_x + leg1_offset, cy), (head_x + int(32 * s * facing) + leg1_offset, cy), (head_x + int(32 * s * facing) + leg1_offset, cy + int(7 * s)), (head_x + leg1_offset, cy + int(7 * s))], fill=(8, 10, 16))

        # Arms swinging
        arm_front = [
            (head_x + int(12 * s), head_y + int(15 * s)),
            (head_x + int(28 * s * facing) - int(leg_swing * 20 * s), cy - int(90 * s)),
            (head_x + int(35 * s * facing) - int(leg_swing * 25 * s), cy - int(75 * s))
        ]
        draw.line(arm_front, fill=coat_color, width=int(12 * s))

    # --- POSE: REACH WALL (Touching stone with one arm) ---
    elif pose == "reach_wall":
        draw.ellipse([head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r], fill=coat_color)
        # Coat
        coat_pts = [
            (head_x - int(18 * s), head_y + head_r),
            (head_x + int(18 * s), head_y + head_r),
            (head_x + int(24 * s), cy - int(55 * s)),
            (head_x + int(35 * s * facing), cy - int(25 * s)),
            (head_x - int(30 * s * facing), cy - int(25 * s)),
            (head_x - int(22 * s), cy - int(55 * s))
        ]
        draw_poly_rim(coat_pts, coat_color, rim_width=3)
        # Legs standing firm
        draw.line([head_x - int(12 * s), cy - int(35 * s), head_x - int(18 * s), cy], fill=(12, 15, 24), width=int(14 * s))
        draw.line([head_x + int(10 * s), cy - int(35 * s), head_x + int(16 * s), cy], fill=(16, 20, 30), width=int(15 * s))
        # Arm reaching straight to wall
        reach_hand_x = head_x + int(75 * s * facing)
        reach_hand_y = head_y + int(20 * s)
        draw.line([head_x + int(12 * s), head_y + int(15 * s), head_x + int(45 * s * facing), head_y + int(10 * s), reach_hand_x, reach_hand_y], fill=coat_color, width=int(12 * s))
        draw.ellipse([reach_hand_x - int(8 * s), reach_hand_y - int(8 * s), reach_hand_x + int(8 * s), reach_hand_y + int(8 * s)], fill=(255, 230, 210))

    # --- POSE: TRIUMPH (Both arms raised on wall top) ---
    elif pose == "triumph":
        draw.ellipse([head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r], fill=coat_color)
        coat_pts = [
            (head_x - int(24 * s), head_y + head_r),
            (head_x + int(24 * s), head_y + head_r),
            (head_x + int(32 * s), cy - int(60 * s)),
            (head_x + int(48 * s) * facing, cy - int(10 * s)),
            (head_x + int(15 * s), cy - int(30 * s)),
            (head_x - int(15 * s), cy - int(30 * s)),
            (head_x - int(42 * s) * facing, cy - int(15 * s)),
            (head_x - int(30 * s), cy - int(60 * s))
        ]
        draw_poly_rim(coat_pts, coat_color, rim_width=3)
        # Legs firmly on wall crest
        draw.polygon([(head_x - int(22 * s), cy - int(35 * s)), (head_x - int(32 * s), cy), (head_x - int(12 * s), cy), (head_x - int(8 * s), cy - int(35 * s))], fill=(14, 18, 28))
        draw.polygon([(head_x + int(8 * s), cy - int(35 * s)), (head_x + int(12 * s), cy), (head_x + int(32 * s), cy), (head_x + int(22 * s), cy - int(35 * s))], fill=(14, 18, 28))
        # Raised Arms V-shape
        arm_l = [(head_x - int(22 * s), head_y + int(15 * s)), (head_x - int(48 * s), head_y - int(35 * s)), (head_x - int(40 * s), head_y - int(45 * s)), (head_x - int(14 * s), head_y + int(10 * s))]
        draw_poly_rim(arm_l, coat_color, rim_width=3)
        draw.ellipse([head_x - int(56 * s), head_y - int(56 * s), head_x - int(38 * s), head_y - int(38 * s)], fill=(255, 230, 210))
        arm_r = [(head_x + int(14 * s), head_y + int(10 * s)), (head_x + int(40 * s), head_y - int(45 * s)), (head_x + int(48 * s), head_y - int(35 * s)), (head_x + int(22 * s), head_y + int(15 * s))]
        draw_poly_rim(arm_r, coat_color, rim_width=3)
        draw.ellipse([head_x + int(38 * s), head_y - int(56 * s), head_x + int(56 * s), head_y - int(38 * s)], fill=(255, 230, 210))

    # --- POSE: CLIMB REACH & PULL ---
    elif pose == "climb_reach":
        neck_x = head_x + int(35 * s * facing)
        neck_y = head_y + int(30 * s)
        draw.ellipse([neck_x - head_r, neck_y - head_r - int(10 * s), neck_x + head_r, neck_y + head_r - int(10 * s)], fill=coat_color)
        draw.polygon([(head_x - int(15 * s), cy - int(20 * s)), (neck_x + int(15 * s), neck_y), (neck_x - int(15 * s), neck_y + int(20 * s)), (head_x - int(35 * s), cy - int(10 * s))], fill=coat_color)
        hand_x = neck_x + int(50 * s * facing)
        hand_y = neck_y + int(100 * s)
        draw.line([neck_x, neck_y + int(10 * s), neck_x + int(25 * s * facing), neck_y + int(50 * s), hand_x, hand_y], fill=coat_color, width=int(12 * s))
        draw.ellipse([hand_x - int(8 * s), hand_y - int(8 * s), hand_x + int(8 * s), hand_y + int(8 * s)], fill=(255, 230, 210))

    elif pose == "climb_pull":
        draw.ellipse([head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r], fill=coat_color)
        draw.polygon([(head_x - int(20 * s), head_y + head_r), (head_x + int(20 * s), head_y + head_r), (head_x + int(16 * s), cy - int(30 * s)), (head_x - int(16 * s), cy - int(30 * s))], fill=coat_color)
        reach_x = head_x - int(35 * s * facing)
        reach_y = head_y - int(60 * s)
        draw.line([head_x, head_y + int(15 * s), reach_x, reach_y], fill=coat_color, width=int(12 * s))
        draw.ellipse([reach_x - int(8 * s), reach_y - int(8 * s), reach_x + int(8 * s), reach_y + int(8 * s)], fill=(255, 230, 210))

    elif pose == "overlook":
        # Dignified standing pose looking toward sunrise
        draw.ellipse([head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r], fill=coat_color)
        coat_pts = [
            (head_x - int(20 * s), head_y + head_r),
            (head_x + int(20 * s), head_y + head_r),
            (head_x + int(26 * s), cy - int(60 * s)),
            (head_x + int(45 * s * facing), cy - int(15 * s)),
            (head_x - int(25 * s * facing), cy - int(15 * s)),
            (head_x - int(22 * s), cy - int(60 * s))
        ]
        draw_poly_rim(coat_pts, coat_color, rim_width=4)
        draw.line([head_x - int(10 * s), cy - int(30 * s), head_x - int(14 * s), cy], fill=(14, 18, 28), width=int(14 * s))
        draw.line([head_x + int(10 * s), cy - int(30 * s), head_x + int(14 * s), cy], fill=(16, 20, 30), width=int(15 * s))


# -------------------------------------------------------------
# ACT 1 RENDERER (00:00 - 00:26.60): Cold Monolith & The First Crack
# -------------------------------------------------------------
def render_act1(draw, frame_idx, t):
    progress = frame_idx / ACT1_END
    
    # 1. Dark Cobalt Night Sky Gradient
    for y in range(0, GROUND_Y, 25):
        f = y / GROUND_Y
        r = int(8 + 18 * f)
        g = int(10 + 24 * f)
        b = int(22 + 45 * f)
        draw.rectangle([0, y, CANVAS_W, y + 25], fill=(r, g, b, 255))
        
    # 2. Distant Cold Moon
    moon_x = int(CANVAS_W * 0.78)
    moon_y = int(CANVAS_H * 0.22)
    moon_r = 70
    for gr in range(moon_r + 140, moon_r, -15):
        alpha = int(20 * (1.0 - (gr - moon_r) / 140.0))
        draw.ellipse([moon_x - gr, moon_y - gr, moon_x + gr, moon_y + gr], fill=(210, 225, 255, alpha))
    draw.ellipse([moon_x - moon_r, moon_y - moon_r, moon_x + moon_r, moon_y + moon_r], fill=(235, 242, 255, 255))

    # 3. Sweeping Watchtower Searchlights
    beam_angle = math.sin(t * 0.4) * 0.5 + 0.3
    tower_x = int(CANVAS_W * 0.15)
    tower_y = int(CANVAS_H * 0.38)
    # Searchlight cone
    cone_pts = [
        (tower_x, tower_y),
        (int(tower_x + math.cos(beam_angle - 0.15) * 2200), int(tower_y + math.sin(beam_angle - 0.15) * 2200)),
        (int(tower_x + math.cos(beam_angle + 0.15) * 2200), int(tower_y + math.sin(beam_angle + 0.15) * 2200))
    ]
    draw.polygon(cone_pts, fill=(180, 210, 255, 18))

    # 4. Watchtower Silhouette
    draw.rectangle([tower_x - 40, tower_y, tower_x + 40, GROUND_Y], fill=(16, 20, 30))
    draw.rectangle([tower_x - 80, tower_y - 70, tower_x + 80, tower_y], fill=(24, 30, 44))
    draw.polygon([(tower_x - 100, tower_y - 70), (tower_x + 100, tower_y - 70), (tower_x, tower_y - 130)], fill=(18, 22, 32))
    draw.ellipse([tower_x - 15, tower_y - 45, tower_x + 15, tower_y - 15], fill=(255, 240, 180, 200)) # beacon

    # 5. Massive Concrete Wall (Monolith)
    wall_left = int(CANVAS_W * 0.45)
    draw.rectangle([wall_left, WALL_TOP_Y, CANVAS_W, GROUND_Y], fill=(32, 38, 52))
    # Wall panels & vertical seams
    for px in range(wall_left, CANVAS_W, 280):
        draw.line([px, WALL_TOP_Y, px, GROUND_Y], fill=(20, 24, 34), width=6)
        # Texture lines
        for py in range(WALL_TOP_Y + 120, GROUND_Y, 160):
            draw.line([px + 30, py, px + 250, py], fill=(42, 50, 68), width=3)
    # Wall rounded top tube
    draw.rectangle([wall_left - 30, WALL_TOP_Y - 25, CANVAS_W, WALL_TOP_Y + 25], fill=(45, 54, 72))
    draw.line([wall_left - 30, WALL_TOP_Y - 25, CANVAS_W, WALL_TOP_Y - 25], fill=(80, 95, 125), width=4)

    # 6. Cold Ground with Depth
    draw.rectangle([0, GROUND_Y, CANVAS_W, CANVAS_H], fill=(14, 17, 24))
    for gy in range(GROUND_Y, CANVAS_H, 40):
        draw.line([0, gy, CANVAS_W, gy], fill=(22, 27, 38), width=2)

    # 7. Lone Silhouette Approaching and Touching Wall
    char_target_x = wall_left - 60
    char_start_x = int(CANVAS_W * 0.12)
    # Moves forward between 0s and 14s, then reaches wall
    char_progress = min(1.0, t / 14.0)
    char_x = int(char_start_x + (char_target_x - char_start_x) * char_progress)
    char_pose = "walk" if char_progress < 0.98 else "reach_wall"
    
    # Golden Crack Reaction after touch (t > 14s)
    crack_glow = 0.0
    if t > 14.0:
        crack_glow = min(1.0, (t - 14.0) / 6.0)
        
    rim = (int(251 * crack_glow), int(191 * crack_glow), int(36 * crack_glow)) if crack_glow > 0.1 else (50, 70, 100)
    draw_detailed_silhouette(draw, char_x, GROUND_Y, scale=1.3, pose=char_pose, coat_color=(20, 24, 36), facing=1, rim_color=rim, anim_phase=t * 1.5)

    # 8. Golden Fissure on Wall (t > 14s)
    if crack_glow > 0:
        crack_x = wall_left + 10
        crack_y = GROUND_Y - 240
        # Multi-stage branching crack
        pts = [
            (crack_x, crack_y),
            (crack_x + 30, crack_y - 60),
            (crack_x + 80, crack_y - 140),
            (crack_x + 60, crack_y - 240),
            (crack_x + 120, crack_y - 380),
            (crack_x + 150, WALL_TOP_Y + 40)
        ]
        # Outer glow
        glow_alpha = int(70 * crack_glow * (0.8 + 0.2 * math.sin(t * 8.0)))
        for w in [35, 20, 10]:
            draw.line(pts, fill=(245, 158, 11, glow_alpha), width=w)
        draw.line(pts, fill=(255, 235, 170, int(220 * crack_glow)), width=4)

    # 9. Typographic Title Card
    font_title = get_font_4k(72, bold=True)
    font_sub = get_font_4k(40, bold=False)
    if t < 12.0:
        alpha_t = min(1.0, t / 2.0) if t < 10.0 else max(0.0, (12.0 - t) / 2.0)
        col_t = (255, 255, 255, int(230 * alpha_t))
        col_s = (180, 200, 230, int(180 * alpha_t))
        draw.text((int(CANVAS_W * 0.08), int(CANVAS_H * 0.12)), "9 НОЯБРЯ // 1989 ГОД", font=font_title, fill=col_t)
        draw.text((int(CANVAS_W * 0.08), int(CANVAS_H * 0.17)), "БЕРЛИНСКАЯ СТЕНА КАЗАЛАСЬ ВЕЧНОЙ", font=font_sub, fill=col_s)
    elif t >= 14.0:
        alpha_t = min(1.0, (t - 14.0) / 2.0)
        col_gold = (251, 191, 36, int(240 * alpha_t))
        draw.text((int(CANVAS_W * 0.08), int(CANVAS_H * 0.12)), "ПЕРВАЯ ТРЕЩИНА В МОНОЛИТЕ", font=font_title, fill=col_gold)
        draw.text((int(CANVAS_W * 0.08), int(CANVAS_H * 0.17)), "НАЧАЛО ДВИЖЕНИЯ К СВОБОДЕ", font=font_sub, fill=(255, 255, 255, int(180 * alpha_t)))


# -------------------------------------------------------------
# ACT 2 RENDERER (00:26.60 - 00:51.23): The Breach & Triumph
# -------------------------------------------------------------
def render_act2(draw, frame_idx, t_global):
    local_idx = frame_idx - ACT1_END
    t = local_idx / FPS
    
    sun_bloom = min(1.0, max(0.0, (t - 3.0) / 14.0))
    
    # 1. Sunrise Sky Gradient
    for y in range(0, GROUND_Y, 20):
        factor = y / GROUND_Y
        r = int(12 + 45 * factor + (220 - 12) * factor * (sun_bloom ** 1.3))
        g = int(14 + 30 * factor + (150 - 14) * factor * (sun_bloom ** 1.5))
        b = int(28 + 65 * factor + (65 - 28) * factor * (sun_bloom ** 2.0))
        draw.rectangle([0, y, CANVAS_W, y + 20], fill=(min(255, r), min(255, g), min(255, b), 255))

    # 2. Moon Sinking
    moon_x = int(CANVAS_W * 0.22)
    moon_y = int(CANVAS_H * 0.20 + t * 15)
    moon_r = 70
    draw.ellipse([moon_x - moon_r, moon_y - moon_r, moon_x + moon_r, moon_y + moon_r], fill=(245, 248, 255, int(220 * (1.0 - sun_bloom * 0.5))))

    # 3. Clouds Drifting
    for c_i in range(5):
        c_x = int((c_i * 850 + t * 40) % (CANVAS_W + 600)) - 300
        c_y = int(CANVAS_H * 0.18 + c_i * 90 + math.sin(t * 0.5 + c_i) * 30)
        c_w = 420 + c_i * 120
        c_h = 110 + c_i * 30
        draw.ellipse([c_x, c_y, c_x + c_w, c_y + c_h], fill=(220, 180, 150, int(35 + sun_bloom * 50)))

    # 4. Volumetric Light Beams Bursting Through Breach
    breach_cx = CANVAS_W // 2
    if sun_bloom > 0.05:
        beam_alpha = int(45 * sun_bloom)
        for b_w, b_ang in [(-450, 0.4), (-180, 0.7), (200, 0.6), (500, 0.35)]:
            beam_pts = [
                (breach_cx - 150, WALL_TOP_Y + 120),
                (breach_cx + 150, WALL_TOP_Y + 120),
                (breach_cx + b_w + 350, CANVAS_H),
                (breach_cx + b_w - 350, CANVAS_H)
            ]
            draw.polygon(beam_pts, fill=(255, 220, 140, beam_alpha))

    # 5. Broken Berlin Wall Left & Right
    draw.polygon([(0, WALL_TOP_Y), (breach_cx - 400, WALL_TOP_Y), (breach_cx - 300, GROUND_Y), (0, GROUND_Y)], fill=(34, 40, 56))
    draw.polygon([(breach_cx + 400, WALL_TOP_Y), (CANVAS_W, WALL_TOP_Y), (CANVAS_W, GROUND_Y), (breach_cx + 300, GROUND_Y)], fill=(34, 40, 56))
    
    # 6. Fallen Concrete Slab in 2.5D Rubble
    fall_progress = min(1.0, t / 4.0)
    slab_pts = [
        (breach_cx - 280, GROUND_Y - int(140 * (1.0 - fall_progress))),
        (breach_cx + 280, GROUND_Y - int(100 * (1.0 - fall_progress))),
        (breach_cx + 340, GROUND_Y + 80),
        (breach_cx - 340, GROUND_Y + 80)
    ]
    draw.polygon(slab_pts, fill=(50, 58, 76))
    # Rubble blocks
    for rx, ry, rw, rh in [(-220, -40, 80, 60), (-80, -20, 110, 50), (140, -50, 95, 70), (250, -10, 70, 45)]:
        draw.polygon([
            (breach_cx + rx, GROUND_Y + ry),
            (breach_cx + rx + rw, GROUND_Y + ry - 15),
            (breach_cx + rx + rw + 20, GROUND_Y + ry + rh),
            (breach_cx + rx, GROUND_Y + ry + rh)
        ], fill=(65, 75, 96))

    # 7. Ground Horizon with Rim Lighting
    draw.rectangle([0, GROUND_Y, CANVAS_W, CANVAS_H], fill=(18, 22, 32))

    # 8. Articulated Silhouettes in Victory & Climbing
    rim_sun = (251, 191, 36) if sun_bloom > 0.2 else (100, 130, 180)
    
    # Hero 1: Victorious atop the fallen wall crest
    draw_detailed_silhouette(draw, breach_cx - 350, WALL_TOP_Y, scale=1.35, pose="triumph", coat_color=(16, 20, 32), facing=1, rim_color=rim_sun)
    
    # Hero 2: Pulling comrade up
    draw_detailed_silhouette(draw, breach_cx + 120, GROUND_Y - 90, scale=1.2, pose="climb_pull", coat_color=(18, 22, 34), facing=-1, rim_color=rim_sun)
    
    # Hero 3: Reaching up from rubble
    draw_detailed_silhouette(draw, breach_cx - 20, GROUND_Y - 20, scale=1.1, pose="climb_reach", coat_color=(15, 18, 28), facing=1, rim_color=rim_sun)

    # 9. Floating Golden Dust Particles
    for p_i in range(35):
        px = (breach_cx - 500 + (p_i * 97 + int(t * 70)) % 1000)
        py = (GROUND_Y - 250 + (p_i * 63 - int(t * 40)) % 300)
        pr = 4 + (p_i % 6)
        draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(255, 235, 160, int(160 * sun_bloom)))

    # 10. Act 2 Typography
    font_title = get_font_4k(74, bold=True)
    font_sub = get_font_4k(42, bold=False)
    draw.text((int(CANVAS_W * 0.08), int(CANVAS_H * 0.12)), "ПРОРЫВ И СИЛА ВОЛИ", font=font_title, fill=(255, 255, 255, 240))
    draw.text((int(CANVAS_W * 0.08), int(CANVAS_H * 0.17)), "СТЕНА ПАЛА ПОД НАПОРОМ СВОБОДЫ", font=font_sub, fill=(251, 191, 36, 220))


# -------------------------------------------------------------
# ACT 3 RENDERER (00:51.23 - 00:76.57): The Digital Bridge & Highway
# -------------------------------------------------------------
def render_act3(draw, frame_idx, t_global):
    local_idx = frame_idx - ACT2_END
    t = local_idx / FPS
    
    # 1. Cyber Midnight Gradient Sky
    for y in range(0, GROUND_Y, 20):
        f = y / GROUND_Y
        r = int(10 + 15 * f)
        g = int(14 + 25 * f)
        b = int(32 + 55 * f)
        draw.rectangle([0, y, CANVAS_W, y + 20], fill=(r, g, b, 255))

    # 2. Digital Chasm & Towering Cyber Cliffs
    cliff_left = int(CANVAS_W * 0.28)
    cliff_right = int(CANVAS_W * 0.72)
    
    # Left Cliff (Past / Rutina)
    draw.polygon([(0, CANVAS_H * 0.45), (cliff_left, CANVAS_H * 0.45), (cliff_left - 80, GROUND_Y + 150), (0, GROUND_Y + 150)], fill=(22, 28, 42))
    # Right Cliff (Future / Tech)
    draw.polygon([(cliff_right, CANVAS_H * 0.45), (CANVAS_W, CANVAS_H * 0.45), (CANVAS_W, GROUND_Y + 150), (cliff_right + 80, GROUND_Y + 150)], fill=(24, 32, 48))

    # 3. Luminous Cyan Suspension Bridge of Light
    bridge_y = int(CANVAS_H * 0.52)
    # Main Road Deck
    draw.polygon([(cliff_left - 120, bridge_y), (cliff_right + 120, bridge_y), (cliff_right + 120, bridge_y + 35), (cliff_left - 120, bridge_y + 35)], fill=(15, 23, 42))
    draw.line([cliff_left - 120, bridge_y, cliff_right + 120, bridge_y], fill=(6, 182, 212), width=8) # Cyan neon deck
    
    # Suspension Pylons
    pylon_left_x = cliff_left + 80
    pylon_right_x = cliff_right - 80
    pylon_top_y = int(CANVAS_H * 0.24)
    # Towers
    draw.line([pylon_left_x, pylon_top_y, pylon_left_x, bridge_y + 100], fill=(38, 52, 78), width=24)
    draw.line([pylon_left_x, pylon_top_y, pylon_left_x, bridge_y], fill=(56, 189, 248), width=6)
    draw.line([pylon_right_x, pylon_top_y, pylon_right_x, bridge_y + 100], fill=(38, 52, 78), width=24)
    draw.line([pylon_right_x, pylon_top_y, pylon_right_x, bridge_y], fill=(56, 189, 248), width=6)

    # Glowing Cables (Catena)
    for c_step in range(16):
        cx_cable = pylon_left_x + c_step * ((pylon_right_x - pylon_left_x) // 15)
        # Parabolic cable height
        norm_x = (c_step / 15.0) * 2.0 - 1.0
        cy_cable = int(bridge_y - 280 * (1.0 - norm_x**2 * 0.8))
        draw.line([cx_cable, cy_cable, cx_cable, bridge_y], fill=(6, 182, 212, 120), width=3)
        draw.ellipse([cx_cable - 5, cy_cable - 5, cx_cable + 5, cy_cable + 5], fill=(245, 158, 11, 200)) # Amber nodes

    # 4. Animated Data Packets / Pulses Streaming across Bridge
    for stream_i in range(12):
        packet_x = int(cliff_left - 100 + ((stream_i * 220 + t * 500) % (cliff_right - cliff_left + 200)))
        draw.ellipse([packet_x - 12, bridge_y - 8, packet_x + 12, bridge_y + 8], fill=(255, 255, 255, 240))
        draw.line([packet_x - 45, bridge_y, packet_x, bridge_y], fill=(6, 182, 212, 180), width=6)

    # 5. Clean Isometric Cyber Grid below the Chasm
    for grid_y in range(bridge_y + 90, CANVAS_H, 45):
        alpha_g = int(50 * (1.0 - (grid_y - bridge_y) / (CANVAS_H - bridge_y)))
        draw.line([0, grid_y, CANVAS_W, grid_y], fill=(139, 92, 246, alpha_g), width=2)
    for grid_x in range(0, CANVAS_W, 160):
        draw.line([grid_x, bridge_y + 90, int(CANVAS_W * 0.5 + (grid_x - CANVAS_W * 0.5) * 2.5), CANVAS_H], fill=(139, 92, 246, 30), width=2)

    # 6. Silhouette Walking Confidently onto the New Tech Bridge
    char_x = int(cliff_left - 80 + t * 45)
    draw_detailed_silhouette(draw, char_x, bridge_y, scale=1.1, pose="walk", coat_color=(20, 24, 38), facing=1, rim_color=(6, 182, 212), anim_phase=t * 2.0)

    # 7. Act 3 Typography
    font_title = get_font_4k(72, bold=True)
    font_sub = get_font_4k(42, bold=False)
    draw.text((int(CANVAS_W * 0.08), int(CANVAS_H * 0.12)), "ТЕХНОЛОГИИ — ЭТО НОВЫЙ МОСТ", font=font_title, fill=(255, 255, 255, 240))
    draw.text((int(CANVAS_W * 0.08), int(CANVAS_H * 0.17)), "АВТОМАТИЗАЦИЯ ВМЕСТО РУТИНЫ И ХАОСА", font=font_sub, fill=(6, 182, 212, 220))


# -------------------------------------------------------------
# ACT 4 RENDERER (00:76.57 - 01:02.23): Autonomy & Barber Lab TMA
# -------------------------------------------------------------
def render_act4(draw, frame_idx, t_global):
    local_idx = frame_idx - ACT3_END
    t = local_idx / FPS
    
    # 1. Modern Deep Tech Backdrop
    for y in range(0, CANVAS_H, 30):
        factor = y / CANVAS_H
        r = int(12 + 10 * factor)
        g = int(16 + 18 * factor)
        b = int(28 + 36 * factor)
        draw.rectangle([0, y, CANVAS_W, y + 30], fill=(r, g, b, 255))

    # 2. Asphalt Road with Clean Perspective
    road_top_y = int(CANVAS_H * 0.62)
    road_pts = [(0, CANVAS_H), (CANVAS_W * 0.35, road_top_y), (CANVAS_W * 0.65, road_top_y), (CANVAS_W, CANVAS_H)]
    draw.polygon(road_pts, fill=(20, 24, 32))
    # Glowing Road Lane Markers moving forward
    for marker_i in range(8):
        m_t = (t * 2.2 + marker_i * 0.4) % 3.0
        m_y = int(road_top_y + (CANVAS_H - road_top_y) * (m_t / 3.0))
        m_w = int(14 + 40 * (m_t / 3.0))
        m_h = int(20 + 70 * (m_t / 3.0))
        draw.rectangle([CANVAS_W // 2 - m_w // 2, m_y, CANVAS_W // 2 + m_w // 2, m_y + m_h], fill=(255, 235, 140, 190))

    # 3. Modern Sleek Vehicle Moving Forward (Headlights strictly FORWARD!)
    car_cx = int(CANVAS_W * 0.38)
    car_cy = int(CANVAS_H * 0.82)
    
    # Forward Headlight Cones Illuminating Road Ahead!
    # Points to the RIGHT/FORWARD (car travels to the right/forward)
    cone_pts_l = [(car_cx + 180, car_cy - 20), (CANVAS_W, car_cy - 120), (CANVAS_W, car_cy + 180)]
    draw.polygon(cone_pts_l, fill=(254, 240, 138, 45))
    # Road illumination hotspot
    draw.ellipse([car_cx + 300, car_cy - 40, car_cx + 1200, car_cy + 140], fill=(254, 240, 138, 30))

    # Car Chassis (Aerodynamic modern silhouette)
    car_pts = [
        (car_cx - 240, car_cy),
        (car_cx - 180, car_cy - 40),
        (car_cx - 80, car_cy - 95),
        (car_cx + 80, car_cy - 95),
        (car_cx + 160, car_cy - 45),
        (car_cx + 250, car_cy - 20),
        (car_cx + 250, car_cy + 30),
        (car_cx - 240, car_cy + 30)
    ]
    draw.polygon(car_pts, fill=(15, 23, 42))
    draw.line(car_pts, fill=(56, 189, 248), width=5) # Cyan neon contour
    # Wheels
    draw.ellipse([car_cx - 160, car_cy + 10, car_cx - 90, car_cy + 80], fill=(8, 10, 14))
    draw.ellipse([car_cx + 110, car_cy + 10, car_cx + 180, car_cy + 80], fill=(8, 10, 14))
    draw.ellipse([car_cx - 145, car_cy + 25, car_cx - 105, car_cy + 65], fill=(56, 189, 248, 200)) # Glowing rims
    draw.ellipse([car_cx + 125, car_cy + 25, car_cx + 165, car_cy + 65], fill=(56, 189, 248, 200))
    # Headlight Lamp Assembly
    draw.ellipse([car_cx + 235, car_cy - 25, car_cx + 255, car_cy], fill=(255, 255, 220, 255))

    # 4. Modern Storefront: BARBER LAB TMA
    shop_x = int(CANVAS_W * 0.68)
    shop_y = int(CANVAS_H * 0.28)
    shop_w = 950
    shop_h = 560
    
    # Storefront facade glass & dark frame
    draw.rectangle([shop_x, shop_y, shop_x + shop_w, shop_y + shop_h], fill=(15, 23, 42))
    draw.rectangle([shop_x, shop_y, shop_x + shop_w, shop_y + shop_h], outline=(245, 158, 11), width=6)
    
    # Storefront Header Sign
    draw.rectangle([shop_x + 30, shop_y + 30, shop_x + shop_w - 30, shop_y + 130], fill=(10, 14, 26), outline=(251, 191, 36), width=4)
    font_sign = get_font_4k(54, bold=True)
    draw.text((shop_x + 80, shop_y + 50), "BARBER LAB TMA // 24/7", font=font_sign, fill=(251, 191, 36, 255))
    
    # Rotating Barber Pole (Red / White / Blue helix stripes)
    pole_x = shop_x - 60
    pole_y = shop_y + 120
    pole_w = 40
    pole_h = 240
    draw.rectangle([pole_x, pole_y, pole_x + pole_w, pole_y + pole_h], fill=(255, 255, 255))
    draw.rectangle([pole_x - 5, pole_y - 15, pole_x + pole_w + 5, pole_y], fill=(200, 210, 220)) # Cap
    draw.rectangle([pole_x - 5, pole_y + pole_h, pole_x + pole_w + 5, pole_y + pole_h + 15], fill=(200, 210, 220))
    # Dynamic rotating stripes
    for s_i in range(6):
        stripe_offset = int((t * 60 + s_i * 40) % pole_h)
        draw.line([pole_x, pole_y + stripe_offset, pole_x + pole_w, pole_y + (stripe_offset + 25) % pole_h], fill=(239, 68, 68), width=8)
        draw.line([pole_x, pole_y + (stripe_offset + 15) % pole_h, pole_x + pole_w, pole_y + (stripe_offset + 40) % pole_h], fill=(59, 130, 246), width=8)

    # 5. Holographic Revenue Analytics Dashboard (+148% Growth)
    hud_x = shop_x + 80
    hud_y = shop_y + 160
    draw.rectangle([hud_x, hud_y, hud_x + 760, hud_y + 340], fill=(18, 24, 38, 220), outline=(56, 189, 248), width=3)
    font_hud_title = get_font_4k(36, bold=True)
    draw.text((hud_x + 30, hud_y + 25), "АВТОНОМНЫЕ СИСТЕМЫ: АКТИВНЫ", font=font_hud_title, fill=(56, 189, 248, 240))
    
    # Growth Curve Chart
    chart_pts = [
        (hud_x + 50, hud_y + 260),
        (hud_x + 180, hud_y + 220),
        (hud_x + 320, hud_y + 180),
        (hud_x + 480, hud_y + 130),
        (hud_x + 680, hud_y + 70)
    ]
    draw.line(chart_pts, fill=(251, 191, 36), width=7)
    for cx_pt, cy_pt in chart_pts:
        draw.ellipse([cx_pt - 10, cy_pt - 10, cx_pt + 10, cy_pt + 10], fill=(255, 255, 255))
        draw.ellipse([cx_pt - 6, cy_pt - 6, cx_pt + 6, cy_pt + 6], fill=(251, 191, 36))
    
    # Growth Metric
    font_metric = get_font_4k(48, bold=True)
    draw.text((hud_x + 480, hud_y + 250), "+148% АВТОНОМИЯ", font=font_metric, fill=(34, 197, 94, 250))

    # 6. Act 4 Typography
    font_title = get_font_4k(72, bold=True)
    font_sub = get_font_4k(42, bold=False)
    draw.text((int(CANVAS_W * 0.08), int(CANVAS_H * 0.10)), "КОНТРОЛЬ НАД СОБСТВЕННОЙ СУДЬБОЙ", font=font_title, fill=(255, 255, 255, 240))
    draw.text((int(CANVAS_W * 0.08), int(CANVAS_H * 0.15)), "СИСТЕМЫ РАБОТАЮТ НА ВАС 24/7", font=font_sub, fill=(251, 191, 36, 220))


# -------------------------------------------------------------
# ACT 5 RENDERER (01:02.23 - 01:25.23): The Boundless Horizon & Final Title
# -------------------------------------------------------------
def render_act5(draw, frame_idx, t_global):
    local_idx = frame_idx - ACT4_END
    t = local_idx / FPS
    
    # 1. Majestic Sunrise Sky (Brilliant Gold, Amber, Azure)
    for y in range(0, GROUND_Y, 20):
        factor = y / GROUND_Y
        r = int(24 + 180 * factor)
        g = int(32 + 120 * factor)
        b = int(64 + 40 * factor)
        draw.rectangle([0, y, CANVAS_W, y + 20], fill=(min(255, r), min(255, g), min(255, b), 255))

    # 2. Rising Zenith Sun at the Center Horizon
    sun_cx = CANVAS_W // 2
    sun_cy = int(GROUND_Y * 0.85)
    sun_r = 160
    
    # Volumetric Radiant Sunbeams Filling the Universe
    for ray_i in range(24):
        angle = (ray_i / 24.0) * math.pi + (t * 0.04)
        r_len = 2400
        ray_pts = [
            (sun_cx, sun_cy),
            (int(sun_cx + math.cos(angle - 0.06) * r_len), int(sun_cy - math.sin(angle - 0.06) * r_len)),
            (int(sun_cx + math.cos(angle + 0.06) * r_len), int(sun_cy - math.sin(angle + 0.06) * r_len))
        ]
        draw.polygon(ray_pts, fill=(255, 235, 160, 40))

    # Sun Core & Halo
    for halo in range(sun_r + 300, sun_r, -25):
        alpha_h = int(30 * (1.0 - (halo - sun_r) / 300.0))
        draw.ellipse([sun_cx - halo, sun_cy - halo, sun_cx + halo, sun_cy + halo], fill=(255, 220, 130, alpha_h))
    draw.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r], fill=(255, 252, 235, 255))

    # 3. Layered Cloud Mountain Banks on the Horizon
    for c_layer in range(4):
        layer_y = int(GROUND_Y - 200 + c_layer * 60)
        draw.ellipse([int(CANVAS_W * 0.15), layer_y, int(CANVAS_W * 0.55), layer_y + 240], fill=(250, 180, 120, 120 - c_layer * 20))
        draw.ellipse([int(CANVAS_W * 0.45), layer_y - 30, int(CANVAS_W * 0.90), layer_y + 260], fill=(245, 165, 110, 110 - c_layer * 20))

    # 4. Grand Observation Terrace & Ascending Steps
    terrace_y = int(GROUND_Y * 0.88)
    draw.polygon([(0, CANVAS_H), (CANVAS_W * 0.25, terrace_y), (CANVAS_W * 0.75, terrace_y), (CANVAS_W, CANVAS_H)], fill=(20, 25, 38))
    # Steps
    for step_i in range(5):
        sy = terrace_y + step_i * 50
        draw.line([CANVAS_W * 0.25 - step_i * 40, sy, CANVAS_W * 0.75 + step_i * 40, sy], fill=(251, 191, 36), width=4)

    # 5. Hero Silhouette Standing Tall at Summit (Looking at Sun)
    draw_detailed_silhouette(draw, sun_cx - 280, terrace_y, scale=1.4, pose="overlook", coat_color=(15, 18, 28), facing=1, rim_color=(255, 235, 150))
    # Companion Silhouette Standing in Wonder
    draw_detailed_silhouette(draw, sun_cx + 280, terrace_y, scale=1.35, pose="triumph", coat_color=(15, 18, 28), facing=-1, rim_color=(255, 235, 150))

    # 6. Grand Final Typography & Title Card (Smooth Cinematic Fade In)
    fade_in = min(1.0, max(0.0, (t - 4.0) / 4.0))
    if fade_in > 0:
        alpha_title = int(255 * fade_in)
        font_grand = get_font_4k(84, bold=True)
        font_creed = get_font_4k(46, bold=False)
        font_cta = get_font_4k(54, bold=True)
        
        # Center-aligned text block
        draw.text((int(CANVAS_W * 0.22), int(CANVAS_H * 0.16)), "9 НОЯБРЯ // ЭПОХА СВОБОДЫ", font=font_grand, fill=(255, 255, 255, alpha_title))
        draw.text((int(CANVAS_W * 0.26), int(CANVAS_H * 0.23)), "НЕТ НЕРУШИМЫХ СТЕН. ЕСТЬ ТОЛЬКО ШАГ ВПЕРЁД.", font=font_creed, fill=(251, 191, 36, alpha_title))
        
        # Call to Action Button / Plaque
        box_w = 700
        box_h = 100
        box_x = (CANVAS_W - box_w) // 2
        box_y = int(CANVAS_H * 0.31)
        draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], fill=(15, 23, 42, int(220 * fade_in)), outline=(251, 191, 36), width=4)
        draw.text((box_x + 90, box_y + 22), "СДЕЛАЙ ЕГО СЕГОДНЯ", font=font_cta, fill=(255, 255, 255, alpha_title))


# -------------------------------------------------------------
# Main Frame Dispatcher
# -------------------------------------------------------------
def render_frame_4k(frame_idx):
    out_frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_idx:05d}.jpg")
    if os.path.exists(out_frame_path):
        return out_frame_path
        
    t_global = frame_idx / FPS
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (10, 12, 22, 255))
    draw = ImageDraw.Draw(img)
    
    # Dispatch by Act
    if frame_idx <= ACT1_END:
        render_act1(draw, frame_idx, t_global)
    elif frame_idx <= ACT2_END:
        render_act2(draw, frame_idx, t_global)
    elif frame_idx <= ACT3_END:
        render_act3(draw, frame_idx, t_global)
    elif frame_idx <= ACT4_END:
        render_act4(draw, frame_idx, t_global)
    else:
        render_act5(draw, frame_idx, t_global)
        
    # High quality supersampling downscale to 1080p
    img_rgb = img.convert("RGB")
    img_1080p = img_rgb.resize((OUT_W, OUT_H), resample=Image.Resampling.BICUBIC)
    img_1080p.save(out_frame_path, "JPEG", quality=93)
    return out_frame_path


def main():
    os.makedirs(FRAMES_DIR, exist_ok=True)
    print(f"==================================================")
    print(f"STARTING FULL 5-ACT 4K MOTION RENDERER")
    print(f"Total Frames: {TOTAL_FRAMES} (~125.2s @ 30fps)")
    print(f"Canvas: {CANVAS_W}x{CANVAS_H} -> 1080p Bicubic")
    print(f"Output frames dir: {FRAMES_DIR}")
    print(f"==================================================")
    
    t0 = time.time()
    num_workers = 4
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = executor.map(render_frame_4k, range(TOTAL_FRAMES), chunksize=15)
        count = 0
        for _ in futures:
            count += 1
            if count % 150 == 0 or count == TOTAL_FRAMES:
                pct = (count / TOTAL_FRAMES) * 100
                elapsed = time.time() - t0
                fps_render = count / max(0.1, elapsed)
                eta = (TOTAL_FRAMES - count) / max(0.1, fps_render)
                print(f"[{count:04d}/{TOTAL_FRAMES}] {pct:5.1f}% | Speed: {fps_render:4.1f} fps | Elapsed: {elapsed:5.1f}s | ETA: {eta:5.1f}s")
                
    total_time = time.time() - t0
    print(f"All {TOTAL_FRAMES} frames successfully rendered in {total_time:.1f}s!")

if __name__ == "__main__":
    main()
