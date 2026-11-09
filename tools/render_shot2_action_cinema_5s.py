#!/usr/bin/env python3
"""
render_shot2_action_cinema_5s.py
Renders Shot 2: Checkpoint Bornholmer Straße (November 9, 1989).
Fixed Camera True Character Animation over 4 consecutive Keyframes (A -> B -> C -> D)
using Dense Optical Flow (OpenCV DISOpticalFlow) non-linear interpolation.

Pure ASCII working paths to prevent Windows Cyrillic encoding bugs.
"""

import os
import sys
import cv2
import numpy as np
import subprocess

OUT_W = 1920
OUT_H = 1080
FPS = 30
TOTAL_FRAMES = 150

BASE_ASCII_DIR = r"C:\Users\Home\.gemini\antigravity\brain\2177e9db-9f8b-4370-a527-9c6f76ef18d2"
FRAMES_DIR = os.path.join(BASE_ASCII_DIR, "shot2_action_frames")
OUTPUT_VIDEO = os.path.join(BASE_ASCII_DIR, "berlin_action_cinema_5s.mp4")

KEYFRAME_A = os.path.join(BASE_ASCII_DIR, "berlin_1989_shot_2_clean_1794247704737.jpg")
KEYFRAME_B = os.path.join(BASE_ASCII_DIR, "berlin_1989_shot_2_keyframe_b_1794250565864.jpg")
KEYFRAME_C = os.path.join(BASE_ASCII_DIR, "berlin_1989_shot_2_keyframe_c_1794250677333.jpg")
KEYFRAME_D = os.path.join(BASE_ASCII_DIR, "berlin_1989_shot_2_keyframe_d_v2_1794250742104.jpg")

AUDIO_FILE = r"d:\II\ГИТхаБ\cloud-motion-studio\production\shot2_5s_audio.mp3"
# Copy audio to ascii dir as well to guarantee zero encoding issues
AUDIO_ASCII = os.path.join(BASE_ASCII_DIR, "shot2_5s_audio.mp3")

if os.path.exists(AUDIO_FILE) and not os.path.exists(AUDIO_ASCII):
    with open(AUDIO_FILE, "rb") as src, open(AUDIO_ASCII, "wb") as dst:
        dst.write(src.read())

os.makedirs(FRAMES_DIR, exist_ok=True)

def load_and_standardize(path):
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Cannot load image: {path}")
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
    img = cv2.resize(img, (OUT_W, OUT_H), interpolation=cv2.INTER_LANCZOS4)
    return img

print("1. Loading keyframes...")
img_a = load_and_standardize(KEYFRAME_A)
img_b = load_and_standardize(KEYFRAME_B)
img_c = load_and_standardize(KEYFRAME_C)
img_d = load_and_standardize(KEYFRAME_D)

dis = cv2.DISOpticalFlow.create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)

print("2. Precomputing DIS optical flow fields...")
def compute_flows(im1, im2):
    g1 = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    g2 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
    fwd = dis.calc(g1, g2, None)
    bwd = dis.calc(g2, g1, None)
    return fwd, bwd

flow_ab_fwd, flow_ab_bwd = compute_flows(img_a, img_b)
flow_bc_fwd, flow_bc_bwd = compute_flows(img_b, img_c)
flow_cd_fwd, flow_cd_bwd = compute_flows(img_c, img_d)

y_grid, x_grid = np.mgrid[0:OUT_H, 0:OUT_W].astype(np.float32)

def morph(im1, im2, fwd_flow, bwd_flow, alpha):
    s = 3.0 * (alpha ** 2) - 2.0 * (alpha ** 3)
    
    map_x1 = x_grid - alpha * fwd_flow[..., 0]
    map_y1 = y_grid - alpha * fwd_flow[..., 1]
    warp1 = cv2.remap(im1, map_x1, map_y1, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    
    map_x2 = x_grid + (1.0 - alpha) * bwd_flow[..., 0]
    map_y2 = y_grid + (1.0 - alpha) * bwd_flow[..., 1]
    warp2 = cv2.remap(im2, map_x2, map_y2, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    
    return cv2.addWeighted(warp1, 1.0 - s, warp2, s, 0)

def add_atmospheric_effects(frame, frame_idx):
    t = frame_idx / FPS
    puff = max(0.0, np.sin(t * 3.14159 * 1.5)) ** 3
    if puff > 0.05:
        overlay = frame.copy()
        cv2.circle(overlay, (720, 470), int(25 * (1 + 0.5 * puff)), (210, 215, 225), -1)
        cv2.circle(overlay, (1140, 485), int(20 * (1 + 0.5 * puff)), (210, 215, 225), -1)
        overlay = cv2.GaussianBlur(overlay, (51, 51), 0)
        cv2.addWeighted(overlay, 0.08 * puff, frame, 1.0 - 0.08 * puff, 0, frame)
    
    grain = np.random.normal(0, 1.5, (OUT_H, OUT_W, 3)).astype(np.float32)
    return np.clip(frame.astype(np.float32) + grain, 0, 255).astype(np.uint8)

print(f"3. Rendering {TOTAL_FRAMES} frames...")
for i in range(TOTAL_FRAMES):
    if i < 50:
        alpha = i / 49.0
        frame = morph(img_a, img_b, flow_ab_fwd, flow_ab_bwd, alpha)
    elif i < 100:
        alpha = (i - 50) / 49.0
        frame = morph(img_b, img_c, flow_bc_fwd, flow_bc_bwd, alpha)
    else:
        alpha = (i - 100) / 49.0
        frame = morph(img_c, img_d, flow_cd_fwd, flow_cd_bwd, alpha)
        
    final_frame = add_atmospheric_effects(frame, i)
    frame_path = os.path.join(FRAMES_DIR, f"frame_{i:04d}.png")
    cv2.imwrite(frame_path, final_frame)
    if i % 30 == 0:
        print(f"   Rendered frame {i}/{TOTAL_FRAMES}")

print("4. Encoding MP4 video...")
raw_tmp = os.path.join(BASE_ASCII_DIR, "tmp_noaudio.mp4")

cmd_video = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", os.path.join(FRAMES_DIR, "frame_%04d.png"),
    "-c:v", "libx264",
    "-preset", "slow",
    "-crf", "17",
    "-pix_fmt", "yuv420p",
    raw_tmp
]
subprocess.run(cmd_video, check=True)

cmd_mux = [
    "ffmpeg", "-y",
    "-i", raw_tmp,
    "-i", AUDIO_ASCII,
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "192k",
    "-shortest",
    OUTPUT_VIDEO
]
subprocess.run(cmd_mux, check=True)

if os.path.exists(raw_tmp):
    os.remove(raw_tmp)

print(f"SUCCESS: {OUTPUT_VIDEO}")
