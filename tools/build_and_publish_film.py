#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
End-to-End Orchestrator for 125s Master Video '9 Ноября — Эпоха Свободы'
1. 4K Supersampling Rendering (ProcessPoolExecutor, 4 workers)
2. High-Quality H.264 / AAC 1080p Encoding
3. 16-Frame 4x4 Contact Sheet Generator
4. Cloudflare Web Hosting Deployment (/opt/cyberdeck/public)
5. Direct Telegram Dispatch to Father (Chat ID: 0)
"""

import os
import sys
import time
import math
import subprocess
from concurrent.futures import ProcessPoolExecutor
from PIL import Image, ImageDraw, ImageFont

sys.path.append("/tmp")
from render_full_film_4k import render_frame_4k, TOTAL_FRAMES, FRAMES_DIR, OUT_W, OUT_H, get_font_4k

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
FATHER_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
AUDIO_MASTER_PATH = "/tmp/full_narration_master.mp3"
OUTPUT_VIDEO_PATH = "/tmp/film_nov9_freedom_final.mp4"
CONTACT_SHEET_PATH = "/tmp/film_nov9_contact_sheet.jpg"
PUBLIC_WEB_DIR = "/opt/cyberdeck/public"
PUBLIC_BASE_URL = "https://signals-sacramento-enquiry-looks.trycloudflare.com"

def render_all_frames():
    os.makedirs(FRAMES_DIR, exist_ok=True)
    print(f"==================================================")
    print(f"STEP 1: RENDERING {TOTAL_FRAMES} FRAMES (4K -> 1080p)")
    print(f"==================================================")
    t0 = time.time()
    num_workers = 4
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Check what frames are already rendered
        existing_frames = set(os.listdir(FRAMES_DIR))
        pending_indices = [i for i in range(TOTAL_FRAMES) if f"frame_{i:05d}.jpg" not in existing_frames]
        print(f"Already rendered: {TOTAL_FRAMES - len(pending_indices)} frames. To render: {len(pending_indices)} frames.")
        
        futures = executor.map(render_frame_4k, pending_indices, chunksize=15)
        count = TOTAL_FRAMES - len(pending_indices)
        for _ in futures:
            count += 1
            if count % 150 == 0 or count == TOTAL_FRAMES:
                pct = (count / TOTAL_FRAMES) * 100
                elapsed = time.time() - t0
                fps_render = (count - (TOTAL_FRAMES - len(pending_indices))) / max(0.1, elapsed)
                eta = (TOTAL_FRAMES - count) / max(0.1, fps_render) if fps_render > 0 else 0
                print(f"[{count:04d}/{TOTAL_FRAMES}] {pct:5.1f}% | Speed: {fps_render:4.1f} fps | Elapsed: {elapsed:5.1f}s | ETA: {eta:5.1f}s")
    
    total_time = time.time() - t0
    print(f"Rendering complete in {total_time:.1f}s!")

def generate_contact_sheet():
    print(f"\n==================================================")
    print(f"STEP 2: GENERATING 16-FRAME DIRECTORS CONTACT SHEET (4x4)")
    print(f"==================================================")
    # Select 16 keyframe indices across the 5 acts
    indices = [
        120, 360, 580, 750,      # Act 1: Cold wall, approach, touch, crack
        900, 1100, 1300, 1500,   # Act 2: Breach, slab falling, climbing, triumph
        1680, 1880, 2080, 2250,  # Act 3: Digital metamorphosis, cyber bridge, data streams, transition
        2420, 2620, 2820, 3020,  # Act 4: Road ahead, headlights forward, Barber Lab TMA, revenue HUD
    ]
    # Add Act 5 keyframes
    indices_act5 = [3180, 3350, 3550, 3720]
    # Replace last row with Act 5
    indices = indices[:12] + indices_act5
    
    thumb_w, thumb_h = 480, 270
    grid_w = thumb_w * 4
    grid_h = thumb_h * 4 + 120 # Extra header
    
    sheet = Image.new("RGB", (grid_w, grid_h), (10, 14, 24))
    draw = ImageDraw.Draw(sheet)
    
    font_header = get_font_4k(42, bold=True)
    font_badge = get_font_4k(22, bold=True)
    
    # Header Banner
    draw.rectangle([0, 0, grid_w, 120], fill=(16, 22, 38))
    draw.line([0, 120, grid_w, 120], fill=(251, 191, 36), width=3)
    draw.text((40, 25), "9 НОЯБРЯ // ЭПОХА СВОБОДЫ — РЕЖИССЁРСКИЙ КОНТАКТ-ЛИСТ (16 КЛЮЧЕВЫХ КАДРОВ)", font=font_header, fill=(255, 255, 255))
    draw.text((40, 75), "5 АКТОВ: МОНОЛИТ -> ПРОРЫВ -> ЦИФРОВОЙ МОСТ -> АВТОНОМИЯ / BARBER LAB -> ГОРИЗОНТ", font=get_font_4k(26, bold=False), fill=(251, 191, 36))
    
    act_labels = [
        "АКТ 1: МОНОЛИТ И ТРЕЩИНА (00:00-00:27)",
        "АКТ 2: ПАДЕНИЕ СТЕНЫ И ТРИУМФ (00:27-00:51)",
        "АКТ 3: ЦИФРОВОЙ МОСТ И ДАННЫЕ (00:51-01:17)",
        "АКТ 4: АВТОНОМИЯ И BARBER LAB (01:17-01:43)",
        "АКТ 5: ЗЕНИТ И СВОБОДА (01:43-02:05)"
    ]
    
    for idx, f_idx in enumerate(indices):
        r = idx // 4
        c = idx % 4
        x = c * thumb_w
        y = 120 + r * thumb_h
        
        f_path = os.path.join(FRAMES_DIR, f"frame_{f_idx:05d}.jpg")
        if os.path.exists(f_path):
            with Image.open(f_path) as im:
                thumb = im.resize((thumb_w, thumb_h), Image.Resampling.BILINEAR)
                sheet.paste(thumb, (x, y))
        else:
            draw.rectangle([x, y, x + thumb_w, y + thumb_h], fill=(20, 20, 20))
            
        # Draw frame border & timecode badge
        draw.rectangle([x, y, x + thumb_w, y + thumb_h], outline=(30, 42, 64), width=1)
        t_sec = f_idx / 30.0
        tc_str = f"#{idx+1:02d} | {int(t_sec//60):02d}:{t_sec%60:04.1f} (k#{f_idx})"
        draw.rectangle([x + 10, y + 10, x + 230, y + 40], fill=(0, 0, 0, 200))
        draw.text((x + 16, y + 14), tc_str, font=font_badge, fill=(251, 191, 36))
        
    sheet.save(CONTACT_SHEET_PATH, "JPEG", quality=92)
    print(f"Contact sheet saved to {CONTACT_SHEET_PATH} ({grid_w}x{grid_h})")

def encode_video():
    print(f"\n==================================================")
    print(f"STEP 3: ENCODING MASTER MP4 VIDEO (H.264 CRF 18 + AAC)")
    print(f"==================================================")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", "30",
        "-i", f"{FRAMES_DIR}/frame_%05d.jpg",
        "-i", AUDIO_MASTER_PATH,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        OUTPUT_VIDEO_PATH
    ]
    print("Running FFmpeg mux...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print("FFmpeg Error:", res.stderr[-500:])
        raise RuntimeError("FFmpeg encoding failed!")
    
    file_size_mb = os.path.getsize(OUTPUT_VIDEO_PATH) / (1024 * 1024)
    print(f"Master MP4 successfully generated: {OUTPUT_VIDEO_PATH} ({file_size_mb:.2f} MB)")

def deploy_to_web():
    print(f"\n==================================================")
    print(f"STEP 4: DEPLOYING TO PUBLIC WEB DIRECTORY")
    print(f"==================================================")
    os.makedirs(PUBLIC_WEB_DIR, exist_ok=True)
    shutil_targets = [
        (OUTPUT_VIDEO_PATH, os.path.join(PUBLIC_WEB_DIR, "motion_nov9_2026.mp4")),
        (OUTPUT_VIDEO_PATH, os.path.join(PUBLIC_WEB_DIR, "motion_film_2026.mp4")),
        (CONTACT_SHEET_PATH, os.path.join(PUBLIC_WEB_DIR, "film_nov9_contact_sheet.jpg")),
        (AUDIO_MASTER_PATH, os.path.join(PUBLIC_WEB_DIR, "full_narration_master.mp3"))
    ]
    for src, dst in shutil_targets:
        subprocess.run(["cp", src, dst], check=True)
        print(f"Copied {src} -> {dst}")
        
    print(f"Public Web URLs:")
    print(f"Direct MP4: {PUBLIC_BASE_URL}/motion_nov9_2026.mp4")
    print(f"Contact Sheet: {PUBLIC_BASE_URL}/film_nov9_contact_sheet.jpg")

def dispatch_to_telegram():
    if not TELEGRAM_BOT_TOKEN or not FATHER_CHAT_ID:
        print("Telegram не настроен; файл MP4 остаётся сохранённым. Установите TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID.")
        return
    print(f"\n==================================================")
    print(f"STEP 5: DISPATCHING TO FATHER VIA TELEGRAM BOT")
    print(f"==================================================")
    caption_photo = (
        "🎬 *9 НОЯБРЯ // ЭПОХА СВОБОДЫ — РЕЖИССЁРСКИЙ КОНТАКТ-ЛИСТ*\n\n"
        "Отец, принимай работу! Видео полностью пересобрано и отрисовано с нуля по всем 5 актам:\n\n"
        "1️⃣ *00:00–00:27*: Монолитная стена, глубокая синяя ночь, прожектора, силуэт подходит и касается камня — вспыхивает первая золотая трещина надежды.\n"
        "2️⃣ *00:27–00:51*: Прорыв! Падение бетонной плиты, физический щебень, пыль, золотой восход сквозь пролом, люди взбираются и тянут друг друга вверх, триумф на вершине.\n"
        "3️⃣ *00:51–01:17*: Цифровой вантовый мост над пропастью рутины, неоновые потоки данных (Cyan & Gold), уверенный шаг в будущее.\n"
        "4️⃣ *01:17–01:43*: Автономия! Современный автомобиль (фары светят ВПЕРЁД на асфальт!), стильный фасад *Barber Lab TMA*, вращающийся цилиндр, голографический график +148% роста 24/7.\n"
        "5️⃣ *01:43–02:05*: Восходящее зенитное солнце, разгон тьмы, силуэты на смотровой площадке и финальный кинематографичный манифест свободы.\n\n"
        "🌐 Веб-версия: https://signals-sacramento-enquiry-looks.trycloudflare.com/motion_nov9_2026.mp4"
    )
    
    # 1. Send Photo Contact Sheet
    cmd_photo = [
        "curl", "-s", "-F", f"chat_id={FATHER_CHAT_ID}",
        "-F", f"photo=@{CONTACT_SHEET_PATH}",
        "-F", f"caption={caption_photo}",
        "-F", "parse_mode=Markdown",
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    ]
    res_p = subprocess.run(cmd_photo, stdout=subprocess.PIPE, text=True)
    print("Telegram Photo API Response:", res_p.stdout[:200])
    
    # 2. Send Video MP4
    caption_video = "🎥 *Фильм '9 Ноября — Эпоха Свободы' (Full 1080p Master, 125s)*"
    cmd_video = [
        "curl", "-s", "-F", f"chat_id={FATHER_CHAT_ID}",
        "-F", f"video=@{OUTPUT_VIDEO_PATH}",
        "-F", f"caption={caption_video}",
        "-F", "parse_mode=Markdown",
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    ]
    res_v = subprocess.run(cmd_video, stdout=subprocess.PIPE, text=True)
    print("Telegram Video API Response:", res_v.stdout[:200])

def main():
    t_start = time.time()
    render_all_frames()
    generate_contact_sheet()
    encode_video()
    deploy_to_web()
    dispatch_to_telegram()
    total_elapsed = time.time() - t_start
    print(f"\n==================================================")
    print(f"ALL STEPS COMPLETED IN {total_elapsed:.1f}s ({total_elapsed/60:.2f} min)!")
    print(f"==================================================")

if __name__ == "__main__":
    main()
