#!/usr/bin/env python3
"""
render_berlin_master_viral_film.py
Master Cinematic Video Assembler for Scene 2: The Fall of the Berlin Wall (Nov 9, 1989).
Total duration: 24.62 seconds (739 frames @ 30 FPS).

Features:
- 5 Distinct Cinematic Shots across historical arc:
  * Shot 1: Establishing Checkpoint Bornholmer Straße in fog (push-in, searchlights).
  * Shot 2: True Character Animation (4 keyframes with DIS Optical Flow, cold breath).
  * Shot 3: Harald Jäger booth tension (focus push-in, glass reflections).
  * Shot 4/5: Barrier rises & Trabant rolls through cheering crowd (lateral tracking).
  * Shot 6: Historic climax atop the wall at Brandenburg Gate (crane out, sunrise glow, sparklers).
- Multitrack Sound Design (Master Voiceover + Sub-bass rumble + Radio static + Crowd roar + Climax chord).
- Modern viral typography (clean subtitles with gold highlight, zero black borders).
- Pure ASCII paths for zero Windows encoding bugs.
"""

import os
import sys
import cv2
import numpy as np
import subprocess
from PIL import Image, ImageDraw, ImageFont

OUT_W = 1920
OUT_H = 1080
FPS = 30
TOTAL_FRAMES = 739

BASE_ASCII_DIR = r"C:\Users\Home\.gemini\antigravity\brain\2177e9db-9f8b-4370-a527-9c6f76ef18d2"
FRAMES_DIR = os.path.join(BASE_ASCII_DIR, "master_viral_frames")
OUTPUT_VIDEO = os.path.join(BASE_ASCII_DIR, "berlin_1989_final_viral_master.mp4")
GIT_OUTPUT_VIDEO = r"d:\II\ГИТхаБ\cloud-motion-studio\production\berlin_1989_final_viral_master.mp4"

AUDIO_MASTER = os.path.join(BASE_ASCII_DIR, "master_act2_cinematic_audio.mp3")

# Keyframe image paths
K1 = os.path.join(BASE_ASCII_DIR, "berlin_wall_shot_1_bornholmer_strasse_1794247663553.jpg")
K2_A = os.path.join(BASE_ASCII_DIR, "berlin_1989_shot_2_clean_1794247704737.jpg")
K2_B = os.path.join(BASE_ASCII_DIR, "berlin_1989_shot_2_keyframe_b_1794250565864.jpg")
K2_C = os.path.join(BASE_ASCII_DIR, "berlin_1989_shot_2_keyframe_c_1794250677333.jpg")
K2_D = os.path.join(BASE_ASCII_DIR, "berlin_1989_shot_2_keyframe_d_v2_1794250742104.jpg")
K3 = os.path.join(BASE_ASCII_DIR, "berlin_1989_shot_3_jpg_1794247686096.jpg")
K5 = os.path.join(BASE_ASCII_DIR, "berlin_1989_shot_5_1794247694439.jpg")
K6 = os.path.join(BASE_ASCII_DIR, "berlin_wall_celebration_shot6_clean_1794247713966.jpg")

os.makedirs(FRAMES_DIR, exist_ok=True)

def load_and_standardize(path):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Missing image: {path}")
    h, w = img.shape[:2]
    target_ratio = OUT_W / OUT_H
    current_ratio = w / h
    if abs(current_ratio - target_ratio) > 0.01:
        if current_ratio > target_ratio:
            new_w = int(h * target_ratio)
            start_x = (w - new_w) // 2
            img = img[:, start_x:start_x+new_w]
        else:
            new_h = int(w / target_ratio)
            start_y = (h - new_h) // 2
            img = img[start_y:start_y+new_h, :]
    return cv2.resize(img, (OUT_W, OUT_H), interpolation=cv2.INTER_LANCZOS4)

print("1. Loading all master shot illustrations...")
img_k1 = load_and_standardize(K1)
img_k2a = load_and_standardize(K2_A)
img_k2b = load_and_standardize(K2_B)
img_k2c = load_and_standardize(K2_C)
img_k2d = load_and_standardize(K2_D)
img_k3 = load_and_standardize(K3)
img_k5 = load_and_standardize(K5)
img_k6 = load_and_standardize(K6)

# Setup DIS Optical Flow for Shot 2
print("2. Precomputing Optical Flow fields for Shot 2 character action...")
dis = cv2.DISOpticalFlow.create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
def compute_flows(im1, im2):
    g1 = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    g2 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
    return dis.calc(g1, g2, None), dis.calc(g2, g1, None)

flow_ab_fwd, flow_ab_bwd = compute_flows(img_k2a, img_k2b)
flow_bc_fwd, flow_bc_bwd = compute_flows(img_k2b, img_k2c)
flow_cd_fwd, flow_cd_bwd = compute_flows(img_k2c, img_k2d)

y_grid, x_grid = np.mgrid[0:OUT_H, 0:OUT_W].astype(np.float32)

def morph_shot2(im1, im2, fwd_flow, bwd_flow, alpha):
    s = 3.0 * (alpha ** 2) - 2.0 * (alpha ** 3)
    map_x1 = x_grid - alpha * fwd_flow[..., 0]
    map_y1 = y_grid - alpha * fwd_flow[..., 1]
    warp1 = cv2.remap(im1, map_x1, map_y1, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    
    map_x2 = x_grid + (1.0 - alpha) * bwd_flow[..., 0]
    map_y2 = y_grid + (1.0 - alpha) * bwd_flow[..., 1]
    warp2 = cv2.remap(im2, map_x2, map_y2, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return cv2.addWeighted(warp1, 1.0 - s, warp2, s, 0)

# Typography font
try:
    font_sub = ImageFont.truetype("arialbd.ttf", 36)
except Exception:
    font_sub = ImageFont.load_default()

def draw_cinematic_subtitles(cv_img, text, highlight_word=""):
    im_pil = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(im_pil)
    
    bbox = draw.textbbox((0, 0), text, font=font_sub)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    cx = OUT_W // 2
    cy = 960
    pad_x = 24
    pad_y = 12
    box_rect = [cx - tw//2 - pad_x, cy - pad_y, cx + tw//2 + pad_x, cy + th + pad_y]
    
    # Semi-transparent dark pill background
    overlay = Image.new('RGBA', im_pil.size, (0, 0, 0, 0))
    d_over = ImageDraw.Draw(overlay)
    d_over.rounded_rectangle(box_rect, radius=12, fill=(15, 18, 24, 190))
    im_pil = Image.alpha_composite(im_pil.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(im_pil)
    
    # Draw text with highlighted word
    words = text.split()
    curr_x = cx - tw // 2
    for w in words:
        w_clean = w.strip(".,—«»")
        color = (255, 204, 50) if (highlight_word and highlight_word.lower() in w_clean.lower()) else (245, 245, 245)
        draw.text((curr_x, cy), w + " ", font=font_sub, fill=color)
        w_box = draw.textbbox((0, 0), w + " ", font=font_sub)
        curr_x += (w_box[2] - w_box[0])
        
    return cv2.cvtColor(np.array(im_pil), cv2.COLOR_RGB2BGR)

def zoom_and_pan(img, scale_start, scale_end, dx_start, dx_end, progress):
    scale = scale_start + (scale_end - scale_start) * progress
    dx = dx_start + (dx_end - dx_start) * progress
    h, w = img.shape[:2]
    new_w = int(w * scale)
    new_h = int(h * scale)
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    
    # Center crop with offset
    cx = (new_w - w) // 2 + int(dx)
    cy = (new_h - h) // 2
    cx = max(0, min(new_w - w, cx))
    cy = max(0, min(new_h - h, cy))
    return resized[cy:cy+h, cx:cx+w]

print("3. Rendering all 739 frames across 5 distinct scenes...")

# Shot 1: 0..119 (0.0s - 4.0s)
# Shot 2: 120..269 (4.0s - 9.0s)
# Shot 3: 270..389 (9.0s - 13.0s)
# Shot 4/5: 390..554 (13.0s - 18.5s)
# Shot 6: 555..738 (18.5s - 24.62s)

for i in range(TOTAL_FRAMES):
    t = i / FPS
    
    if i < 120:
        # SHOT 1: Checkpoint Bornholmer Straße
        p = i / 119.0
        frame = zoom_and_pan(img_k1, 1.00, 1.06, 0, -20, p)
        # Searchlight sweep effect
        sweep_x = int(600 + 400 * np.sin(p * 3.14159))
        cv2.circle(frame, (sweep_x, 400), 180, (230, 240, 255), -1, lineType=cv2.LINE_AA)
        frame = cv2.GaussianBlur(frame, (11, 11), 0)
        # Add subtitle
        frame = draw_cinematic_subtitles(frame, "Но одна трещина в бетоне способна разрушить монолит.", "трещина")
        
    elif i < 270:
        # SHOT 2: True Character Animation (Keyframes A -> B -> C -> D)
        idx_shot2 = i - 120
        if idx_shot2 < 50:
            alpha = idx_shot2 / 49.0
            frame = morph_shot2(img_k2a, img_k2b, flow_ab_fwd, flow_ab_bwd, alpha)
        elif idx_shot2 < 100:
            alpha = (idx_shot2 - 50) / 49.0
            frame = morph_shot2(img_k2b, img_k2c, flow_bc_fwd, flow_bc_bwd, alpha)
        else:
            alpha = (idx_shot2 - 100) / 49.0
            frame = morph_shot2(img_k2c, img_k2d, flow_cd_fwd, flow_cd_bwd, alpha)
            
        # Cold breath puff
        puff = max(0.0, np.sin((idx_shot2 / 30.0) * 3.14159 * 1.5)) ** 3
        if puff > 0.05:
            overlay = frame.copy()
            cv2.circle(overlay, (720, 470), int(25 * (1 + 0.5 * puff)), (210, 215, 225), -1)
            cv2.circle(overlay, (1140, 485), int(20 * (1 + 0.5 * puff)), (210, 215, 225), -1)
            overlay = cv2.GaussianBlur(overlay, (51, 51), 0)
            cv2.addWeighted(overlay, 0.08 * puff, frame, 1.0 - 0.08 * puff, 0, frame)
            
        frame = draw_cinematic_subtitles(frame, "Люди вышли навстречу друг другу.", "навстречу")
        
    elif i < 390:
        # SHOT 3: Harald Jäger booth tension
        p = (i - 270) / 119.0
        frame = zoom_and_pan(img_k3, 1.00, 1.05, 0, 15, p)
        # Tension pulse in lighting
        pulse = 1.0 + 0.03 * np.sin(p * 3.14159 * 4)
        frame = np.clip(frame.astype(np.float32) * pulse, 0, 255).astype(np.uint8)
        frame = draw_cinematic_subtitles(frame, "Без оружия, движимые одной силой...", "оружия")
        
    elif i < 555:
        # SHOT 4/5: Barrier rises & Trabant rolls through crowd
        p = (i - 390) / 164.0
        frame = zoom_and_pan(img_k5, 1.02, 1.08, -30, 40, p)
        # Headlight beam flare
        flare_x = int(580 + p * 30)
        cv2.ellipse(frame, (flare_x, 620), (120, 60), 15, 0, 360, (255, 250, 220), -1)
        frame = cv2.GaussianBlur(frame, (7, 7), 0)
        frame = draw_cinematic_subtitles(frame, "...движимые одной силой — жаждой свободы.", "свободы")
        
    else:
        # SHOT 6: Climax at Brandenburg Gate atop the wall
        p = (i - 555) / 183.0
        frame = zoom_and_pan(img_k6, 1.07, 1.00, 0, 0, p)
        # Golden sunrise dawn bloom rising
        bloom = (p ** 1.3) * 0.12
        overlay = np.full_like(frame, (80, 160, 255), dtype=np.uint8)
        frame = cv2.addWeighted(frame, 1.0, overlay, bloom, 0)
        
        # Sparkler flares
        for _ in range(4):
            sx = np.random.randint(400, 1500)
            sy = np.random.randint(250, 600)
            cv2.circle(frame, (sx, sy), np.random.randint(2, 5), (255, 255, 220), -1)
            
        frame = draw_cinematic_subtitles(frame, "И стена пала под напором человеческой воли.", "пала")

    # Add very fine film grain across all frames
    grain = np.random.normal(0, 1.5, (OUT_H, OUT_W, 3)).astype(np.float32)
    final_frame = np.clip(frame.astype(np.float32) + grain, 0, 255).astype(np.uint8)
    
    cv2.imwrite(os.path.join(FRAMES_DIR, f"frame_{i:04d}.png"), final_frame)
    if i % 75 == 0:
        print(f"   Rendered frame {i}/{TOTAL_FRAMES} (t={t:.2f}s)")

print("4. Encoding final video with H.264 & AAC Master Audio...")
raw_tmp = os.path.join(BASE_ASCII_DIR, "tmp_master_noaudio.mp4")

cmd_video = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", os.path.join(FRAMES_DIR, "frame_%04d.png"),
    "-c:v", "libx264",
    "-preset", "slow",
    "-crf", "16",
    "-pix_fmt", "yuv420p",
    raw_tmp
]
subprocess.run(cmd_video, check=True)

cmd_mux = [
    "ffmpeg", "-y",
    "-i", raw_tmp,
    "-i", AUDIO_MASTER,
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "256k",
    "-shortest",
    OUTPUT_VIDEO
]
subprocess.run(cmd_mux, check=True)

if os.path.exists(raw_tmp):
    os.remove(raw_tmp)

# Also copy to Git repo production folder
with open(OUTPUT_VIDEO, "rb") as src, open(GIT_OUTPUT_VIDEO, "wb") as dst:
    dst.write(src.read())

print(f"SUCCESS: Master viral film rendered at {OUTPUT_VIDEO} and saved to {GIT_OUTPUT_VIDEO}")
