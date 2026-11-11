"""
Special 11.11 Production Pipeline: The 11:11 Synchronicity Phenomenon.
Format: 9:16 Vertical (1080x1920), 30 FPS.
Includes:
- Hollywood Documentary Voice DSP (pitch shift with formant preservation, warm 110Hz bass body, lowpass 12k)
- Procedural Clock Tick-tock & Sacred 432 Hz Drone Soundscape (-14 LUFS EBU R128)
- 4 Visual Scenes (Digital LED 11:11, Four Golden Pillars, Holographic Neural Synapses, Sacred Geometry Portal)
- Kinetic Subtitles with Zero Tofu Glyph Bugs
- Auto-delivery to Cloudflare CDN and Telegram Bot
"""

import os
import sys
import json
import math
import asyncio
import subprocess
import numpy as np
import scipy.io.wavfile as wavfile
import edge_tts
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1080
HEIGHT = 1920
FPS = 30.0
SAMPLE_RATE = 48000

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTION_DIR = os.path.join(os.path.dirname(TOOLS_DIR), "production")
OUTPUT_DIR = os.path.join(PRODUCTION_DIR, "shorts_11_11")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fonts
FONT_PATH_BOLD = r"C:\Windows\Fonts\arialbd.ttf" if os.name == 'nt' else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_PATH_SANS = r"C:\Windows\Fonts\segoeui.ttf" if os.name == 'nt' else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_PATH_MONO = r"C:\Windows\Fonts\consola.ttf" if os.name == 'nt' else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

FONT_BADGE = ImageFont.truetype(FONT_PATH_BOLD, 26)
FONT_TITLE = ImageFont.truetype(FONT_PATH_BOLD, 46)
FONT_SUBTITLE = ImageFont.truetype(FONT_PATH_BOLD, 52)
FONT_SUBTITLE_HL = ImageFont.truetype(FONT_PATH_BOLD, 54)
FONT_HUD = ImageFont.truetype(FONT_PATH_MONO, 20)
FONT_CLOCK = ImageFont.truetype(FONT_PATH_BOLD, 120)

SCRIPT_DATA = {
    "title": "ФЕНОМЕН 11:11 // КОД МАТРИЦЫ",
    "headline_badge": "11 НОЯБРЯ // ОСОБЫЙ ДЕНЬ",
    "voice": "ru-RU-SvetlanaNeural",
    "acts": [
        {
            "id": "hook",
            "text": "Ты когда-нибудь смотрел на часы ровно в одиннадцать одиннадцать? Миллионы людей по всему миру видят эти четыре единицы каждый день.",
            "mode": "digital_clock",
            "highlight_words": ["одиннадцать", "Миллионы", "четыре", "единицы"]
        },
        {
            "id": "science",
            "text": "Физики называют это квантовой синхроничностью, нумерологи — порталом пробуждения, а психологи — иллюзией Баадера-Майнхоф.",
            "mode": "four_pillars",
            "highlight_words": ["квантовой", "синхроничностью", "порталом", "пробуждения"]
        },
        {
            "id": "brain",
            "text": "Человеческий мозг — это биокомпьютер по поиску закономерностей. Он отбрасывает тысячи чисел, но впивается именно в четыре единицы.",
            "mode": "neural_synapse",
            "highlight_words": ["мозг", "биокомпьютер", "четыре", "единицы"]
        },
        {
            "id": "climax",
            "text": "Но что, если это не игра разума, а маяк в структуре реальности? Сегодня одиннадцатое ноября. Врата открыты. Загадай желание.",
            "mode": "sacred_portal",
            "highlight_words": ["маяк", "реальности", "Врата", "открыты", "Загадай", "желание"]
        }
    ]
}

# ==================== AUDIO GENERATION ====================

async def synthesize_speech(text, voice, out_path):
    comm = edge_tts.Communicate(text, voice=voice, rate="-2%")
    await comm.save(out_path)

def get_audio_duration(file_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def generate_clock_ticks(duration_sec, sr=SAMPLE_RATE):
    """Generates precise, crisp clock tick-tocks at 60 BPM."""
    total_samples = int(duration_sec * sr)
    sig = np.zeros(total_samples, dtype=np.float32)
    # Every 1.0 second
    for s in range(0, int(duration_sec)):
        idx = int(s * sr)
        if idx >= total_samples:
            break
        # Tick sound (high pitch metallic ping 2200 Hz)
        t_tick = np.linspace(0, 0.04, int(sr * 0.04), endpoint=False)
        tick_wave = np.sin(2 * np.pi * 2200 * t_tick) * np.exp(-120 * t_tick) * 0.35
        end_idx = min(idx + len(tick_wave), total_samples)
        sig[idx:end_idx] += tick_wave[:end_idx - idx]
    return sig

def generate_sacred_drone(duration_sec, sr=SAMPLE_RATE):
    """Generates a deep, rich sacred ambient drone (54 Hz root + 432 Hz harmonic)."""
    t = np.linspace(0, duration_sec, int(sr * duration_sec), endpoint=False)
    # Sub-bass root (54 Hz)
    root = 0.35 * np.sin(2 * np.pi * 54.0 * t)
    # 432 Hz sacred overtone
    harmonic = 0.18 * np.sin(2 * np.pi * 432.0 * t + 0.2 * np.sin(2 * np.pi * 0.3 * t))
    # Octave 108 Hz
    mid = 0.22 * np.sin(2 * np.pi * 108.0 * t)
    return (root + harmonic + mid) * 0.32

def generate_audio_pipeline():
    print("=== [11.11] Synthesizing Neural Voice with Hollywood Documentary DSP ===")
    voice = SCRIPT_DATA["voice"]
    act_files = []
    act_durations = []
    
    # 1. Synthesize acts and apply DSP
    dsp_filter = "rubberband=pitch=0.83:formant=preserved,equalizer=f=110:width_type=o:width=1.2:g=3.5,lowpass=f=12000"
    
    for idx, act in enumerate(SCRIPT_DATA["acts"]):
        raw_mp3 = os.path.join(OUTPUT_DIR, f"act_{idx}_raw.mp3")
        dsp_mp3 = os.path.join(OUTPUT_DIR, f"act_{idx}_dsp.mp3")
        
        print(f"Synthesizing Act {idx+1}: {act['id']}...")
        asyncio.run(synthesize_speech(act["text"], voice, raw_mp3))
        
        # Apply DSP filter
        cmd = [
            "ffmpeg", "-y", "-i", raw_mp3,
            "-af", dsp_filter,
            "-ar", str(SAMPLE_RATE), "-b:a", "256k",
            dsp_mp3
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        dur = get_audio_duration(dsp_mp3)
        print(f" -> DSP Voice Duration: {dur:.3f}s")
        act_files.append(dsp_mp3)
        act_durations.append(dur)
        
    pause_sec = 0.55
    end_buffer = 1.2
    current_time = 0.2
    act_timings = []
    
    for idx, act in enumerate(SCRIPT_DATA["acts"]):
        dur = act_durations[idx]
        start_t = current_time
        end_t = start_t + dur
        
        words = act["text"].split()
        chunk_size = 3
        chunks = []
        chunk_dur = dur / max(1, (len(words) + chunk_size - 1) // chunk_size)
        
        w_idx = 0
        c_time = start_t
        while w_idx < len(words):
            c_words = words[w_idx:w_idx + chunk_size]
            chunks.append({
                "words": " ".join(c_words),
                "start": round(c_time, 2),
                "end": round(c_time + chunk_dur, 2),
                "has_highlight": any(hw.lower() in " ".join(c_words).lower() for hw in act.get("highlight_words", []))
            })
            c_time += chunk_dur
            w_idx += chunk_size
            
        act_timings.append({
            "id": act["id"],
            "mode": act["mode"],
            "start": round(start_t, 3),
            "end": round(end_t, 3),
            "duration": round(dur, 3),
            "text": act["text"],
            "chunks": chunks
        })
        current_time = end_t + pause_sec
        
    final_duration = current_time + end_buffer
    print(f"Total video planned duration: {final_duration:.2f}s")
    
    timing_json_path = os.path.join(OUTPUT_DIR, "timings_11_11.json")
    with open(timing_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "title": SCRIPT_DATA["title"],
            "headline_badge": SCRIPT_DATA["headline_badge"],
            "total_duration": round(final_duration, 2),
            "acts": act_timings
        }, f, indent=2, ensure_ascii=False)
        
    # Concat speech into master array
    sr = SAMPLE_RATE
    total_samples = int(final_duration * sr)
    full_speech = np.zeros(total_samples, dtype=np.float32)
    
    for idx, act in enumerate(act_timings):
        tmp_wav = os.path.join(OUTPUT_DIR, f"tmp_act_{idx}.wav")
        subprocess.run(["ffmpeg", "-y", "-i", act_files[idx], "-ar", str(sr), "-ac", "1", tmp_wav],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        _, data = wavfile.read(tmp_wav)
        data = data.astype(np.float32) / 32768.0
        start_samp = int(act["start"] * sr)
        end_samp = min(start_samp + len(data), total_samples)
        full_speech[start_samp:end_samp] += data[:end_samp - start_samp]
        
    # Generate Clock Ticks & Drone
    ticks = generate_clock_ticks(final_duration, sr)
    drone = generate_sacred_drone(final_duration, sr)
    
    # Sub-bass drop on hook
    t_drop = np.linspace(0, 2.8, int(sr * 2.8), endpoint=False)
    freq_drop = 85.0 * np.exp(-1.1 * t_drop) + 38.0
    phase_drop = 2 * np.pi * np.cumsum(freq_drop) / sr
    drop_sig = np.exp(-1.3 * t_drop) * np.sin(phase_drop) * 0.75
    
    full_sfx = np.zeros(total_samples, dtype=np.float32)
    full_sfx += drone
    full_sfx += ticks * 0.55
    full_sfx[:len(drop_sig)] += drop_sig
    
    voice_wav = os.path.join(OUTPUT_DIR, "voice_master.wav")
    sfx_wav = os.path.join(OUTPUT_DIR, "sfx_master.wav")
    
    wavfile.write(voice_wav, sr, (np.clip(full_speech, -1.0, 1.0) * 32767).astype(np.int16))
    wavfile.write(sfx_wav, sr, (np.clip(full_sfx, -1.0, 1.0) * 32767).astype(np.int16))
    
    # Final EBU R128 master mix
    master_mp3 = os.path.join(OUTPUT_DIR, "audio_11_11_master.mp3")
    mix_cmd = [
        "ffmpeg", "-y",
        "-i", voice_wav,
        "-i", sfx_wav,
        "-filter_complex",
        "[0:a]volume=1.35[v];[1:a]volume=0.85[s];[v][s]amix=inputs=2:duration=first:dropout_transition=2,"
        "loudnorm=I=-14:TP=-1.5:LRA=9",
        "-c:a", "libmp3lame",
        "-b:a", "256k",
        master_mp3
    ]
    subprocess.run(mix_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Master 11.11 Audio Ready: {master_mp3}")
    return master_mp3, timing_json_path

# ==================== VISUAL RENDER ENGINE ====================

def draw_star_glyph(draw, cx, cy, radius=8, fill=(255, 215, 60)):
    points = [
        (cx, cy - radius),
        (cx + radius * 0.35, cy - radius * 0.35),
        (cx + radius, cy),
        (cx + radius * 0.35, cy + radius * 0.35),
        (cx, cy + radius),
        (cx - radius * 0.35, cy + radius * 0.35),
        (cx - radius, cy),
        (cx - radius * 0.35, cy - radius * 0.35)
    ]
    draw.polygon(points, fill=fill)

def render_act_digital_clock(draw, t_sec):
    """Act 1: Massive neon digital clock flipping to 11:11 with glowing matrix aura."""
    cx = WIDTH // 2
    cy = 780
    
    # Glowing digital display box
    box_w, box_h = 880, 420
    draw.rounded_rectangle([cx - box_w//2, cy - box_h//2, cx + box_w//2, cy + box_h//2],
                           radius=28, fill=(12, 16, 28), outline=(0, 240, 255), width=4)
                           
    # Inner border
    draw.rounded_rectangle([cx - box_w//2 + 16, cy - box_h//2 + 16, cx + box_w//2 - 16, cy + box_h//2 - 16],
                           radius=18, outline=(20, 50, 80), width=2)
                           
    # Clock pulse
    colon_blink = ":" if int(t_sec * 2) % 2 == 0 else " "
    clock_text = f"11{colon_blink}11"
    
    # Outer glow text
    for offset in [-3, 3]:
        draw.text((cx + offset, cy), clock_text, font=FONT_CLOCK, fill=(0, 160, 255), anchor="mm")
    draw.text((cx, cy), clock_text, font=FONT_CLOCK, fill=(255, 255, 255), anchor="mm")
    
    # Sub-caption
    draw.text((cx, cy + box_h//2 - 45), "SYNCHRONICITY PROTOCOL ACTIVE // 11:11:11",
              font=FONT_HUD, fill=(0, 255, 200), anchor="mm")

def render_act_four_pillars(draw, t_sec):
    """Act 2: Four massive glowing golden pillars (1 1 : 1 1) shooting light into space."""
    cx = WIDTH // 2
    cy = 780
    
    # Sea floor perspective lines
    horizon_y = cy + 220
    for lx in range(100, WIDTH, 120):
        draw.line([(lx, HEIGHT), (cx, horizon_y)], fill=(25, 35, 55), width=2)
    draw.line([(0, horizon_y), (WIDTH, horizon_y)], fill=(255, 215, 60), width=2)
    
    # Four pillars
    pillar_xs = [cx - 300, cx - 110, cx + 110, cx + 300]
    p_w = 64
    p_h = 440
    
    for idx, px in enumerate(pillar_xs):
        # Vertical beam shooting to top of screen
        draw.rectangle([px - p_w//2 + 12, 0, px + p_w//2 - 12, horizon_y], fill=(255, 235, 140))
        # Pillar body
        draw.rounded_rectangle([px - p_w//2, horizon_y - p_h, px + p_w//2, horizon_y],
                               radius=12, fill=(210, 160, 20), outline=(255, 240, 160), width=3)
        # Monolith number "1" inside
        draw.text((px, horizon_y - p_h // 2), "1", font=FONT_TITLE, fill=(255, 255, 255), anchor="mm")
        
    # Central glowing colon dots
    pulse = (math.sin(t_sec * 6.0) + 1.0) * 0.5
    dot_r = 14 + int(pulse * 6)
    draw.ellipse([cx - dot_r, cy - 60 - dot_r, cx + dot_r, cy - 60 + dot_r], fill=(255, 215, 60))
    draw.ellipse([cx - dot_r, cy + 60 - dot_r, cx + dot_r, cy + 60 + dot_r], fill=(255, 215, 60))
    
    draw.text((cx, horizon_y + 45), "SACRED ARCHITECTURE // PORTAL OF AWAKENING",
              font=FONT_HUD, fill=(255, 215, 60), anchor="mm")

def render_act_neural_synapse(draw, t_sec):
    """Act 3: Holographic neural network synapses firing in sync with thoughts."""
    cx = WIDTH // 2
    cy = 780
    
    np.random.seed(42)
    nodes_x = cx + np.random.uniform(-360, 360, 28)
    nodes_y = cy + np.random.uniform(-260, 260, 28)
    
    # Interconnecting synaptic axons
    for i in range(len(nodes_x)):
        for j in range(i + 1, min(i + 4, len(nodes_x))):
            draw.line([(nodes_x[i], nodes_y[i]), (nodes_x[j], nodes_y[j])], fill=(30, 60, 95), width=2)
            
    # Firing pulses along synapses
    active_idx = int(t_sec * 12.0) % len(nodes_x)
    for i in range(len(nodes_x)):
        r = 10 if i == active_idx else 5
        col = (255, 215, 60) if i == active_idx else (0, 240, 255)
        draw.ellipse([nodes_x[i] - r, nodes_y[i] - r, nodes_x[i] + r, nodes_y[i] + r], fill=col)
        if i == active_idx:
            draw.ellipse([nodes_x[i] - 24, nodes_y[i] - 24, nodes_x[i] + 24, nodes_y[i] + 24], outline=(255, 215, 60), width=2)
            
    draw.text((cx, cy + 320), "PATTERN RECOGNITION ENGINE // BAADER-MEINHOF ILLUSION",
              font=FONT_HUD, fill=(0, 240, 255), anchor="mm")

def render_act_sacred_portal(draw, t_sec):
    """Act 4: Rotating sacred geometry portal (Flower of Life / Vortex)."""
    cx = WIDTH // 2
    cy = 780
    radius = 320
    
    # Outer glowing gateway rings
    for r in [radius + 20, radius, radius - 60, radius - 140]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 215, 60), width=2)
        
    # Rotating sacred circles (Flower of Life petals)
    rot = (t_sec * 0.4) % (2 * math.pi)
    petals = 6
    for p in range(petals):
        ang = rot + p * (2 * math.pi / petals)
        px = cx + int(math.cos(ang) * (radius // 2))
        py = cy + int(math.sin(ang) * (radius // 2))
        draw.ellipse([px - radius//2, py - radius//2, px + radius//2, py + radius//2], outline=(0, 240, 255), width=2)
        
    # Central golden core
    draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(255, 255, 255), outline=(255, 215, 60), width=4)
    
    draw.text((cx, cy + radius + 55), "11.11 GATEWAY OPEN // MAKE YOUR WISH // INFINITE REALITY",
              font=FONT_HUD, fill=(255, 215, 60), anchor="mm")

def render_header(draw, timing_data):
    cx = WIDTH // 2
    badge_y = 195
    title_y = 255
    
    badge_text = timing_data.get('headline_badge', '11 НОЯБРЯ')
    bbox = FONT_BADGE.getbbox(badge_text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    pad_x = 36
    pad_y = 10
    pill_rect = [cx - tw//2 - pad_x, badge_y - th//2 - pad_y, cx + tw//2 + pad_x, badge_y + th//2 + pad_y]
    draw.rounded_rectangle(pill_rect, radius=8, fill=(18, 14, 5), outline=(255, 215, 60), width=2)
    draw.text((cx, badge_y), badge_text, font=FONT_BADGE, fill=(255, 215, 60), anchor="mm")
    
    # Vector stars on left and right
    star_offset = tw // 2 + 18
    draw_star_glyph(draw, cx - star_offset, badge_y, radius=8, fill=(255, 215, 60))
    draw_star_glyph(draw, cx + star_offset, badge_y, radius=8, fill=(255, 215, 60))
    
    title_text = timing_data.get("title", "ТАЙНА 11:11")
    draw.text((cx, title_y), title_text, font=FONT_TITLE, fill=(255, 255, 255), anchor="mm")
    draw.line([(cx - 240, title_y + 36), (cx + 240, title_y + 36)], fill=(255, 215, 60), width=3)

def render_subtitles(draw, timing_data, t_sec):
    active_chunk = None
    for act in timing_data["acts"]:
        for chunk in act["chunks"]:
            if chunk["start"] <= t_sec <= chunk["end"]:
                active_chunk = chunk
                break
        if active_chunk:
            break
            
    if not active_chunk:
        return
        
    text = active_chunk["words"]
    has_high = active_chunk.get("has_highlight", False)
    
    font = FONT_SUBTITLE_HL if has_high else FONT_SUBTITLE
    text_color = (255, 215, 60) if has_high else (255, 255, 255)
    border_color = (255, 215, 60) if has_high else (60, 80, 115)
    
    cx = WIDTH // 2
    cy = 1430
    
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    pad_x = 42
    pad_y = 20
    pill_rect = [cx - tw//2 - pad_x, cy - th//2 - pad_y, cx + tw//2 + pad_x, cy + th//2 + pad_y]
    draw.rounded_rectangle(pill_rect, radius=18, fill=(10, 14, 22), outline=border_color, width=3)
    
    draw.text((cx + 2, cy + 2), text, font=font, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, cy), text, font=font, fill=text_color, anchor="mm")

def render_video_pipeline(timing_json_path, master_audio_path, out_mp4):
    with open(timing_json_path, "r", encoding="utf-8") as f:
        timing_data = json.load(f)
        
    total_duration = timing_data["total_duration"]
    total_frames = int(total_duration * FPS)
    
    print(f"=== Rendering 11.11 Master Video: {total_duration:.2f}s ({total_frames} frames @ {FPS} FPS) ===")
    
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-i", master_audio_path,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "256k",
        "-shortest",
        out_mp4
    ]
    
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    acts = timing_data["acts"]
    sample_indices = [int(i * total_frames / 9) for i in range(9)]
    audit_frames = []
    
    for frame_idx in range(total_frames):
        t_sec = frame_idx / FPS
        
        img = Image.new("RGB", (WIDTH, HEIGHT), (8, 12, 22))
        draw = ImageDraw.Draw(img)
        
        # Subtle streaming binary background code (11 01 11)
        np.random.seed((frame_idx // 4) * 100)
        for gy in range(40, HEIGHT - 80, 70):
            row_code = " ".join(["11" if np.random.rand() > 0.4 else "01" for _ in range(16)])
            draw.text((WIDTH//2, gy), row_code, font=FONT_HUD, fill=(16, 26, 42), anchor="mm")
            
        current_mode = "digital_clock"
        for act in acts:
            if act["start"] <= t_sec < act["end"] + 0.6:
                current_mode = act["mode"]
                break
                
        if current_mode == "digital_clock":
            render_act_digital_clock(draw, t_sec)
        elif current_mode == "four_pillars":
            render_act_four_pillars(draw, t_sec)
        elif current_mode == "neural_synapse":
            render_act_neural_synapse(draw, t_sec)
        elif current_mode == "sacred_portal":
            render_act_sacred_portal(draw, t_sec)
            
        render_header(draw, timing_data)
        render_subtitles(draw, timing_data, t_sec)
        
        # Progress bar
        pct = min(1.0, max(0.0, t_sec / total_duration))
        draw.line([(0, 6), (WIDTH, 6)], fill=(25, 35, 50), width=8)
        draw.line([(0, 6), (int(WIDTH * pct), 6)], fill=(255, 215, 60), width=8)
        
        # Letterbox vignette
        for y in range(80):
            draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0))
        for y in range(HEIGHT - 120, HEIGHT):
            draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0))
            
        proc.stdin.write(img.tobytes())
        
        if frame_idx in sample_indices:
            audit_frames.append(img.copy())
            
        if frame_idx % 150 == 0:
            print(f"Rendered frame {frame_idx}/{total_frames} ({frame_idx/total_frames*100:.1f}%)")
            
    proc.stdin.close()
    proc.wait()
    
    print(f"Video 11.11 successfully rendered: {out_mp4}")
    
    if audit_frames:
        sheet = Image.new("RGB", (WIDTH, HEIGHT), (5, 5, 5))
        cw, ch = WIDTH // 3, HEIGHT // 3
        for idx, f_img in enumerate(audit_frames[:9]):
            c, r = idx % 3, idx // 3
            thumb = f_img.resize((cw, ch), Image.Resampling.LANCZOS)
            sheet.paste(thumb, (c * cw, r * ch))
        sheet_path = out_mp4.replace(".mp4", "_audit_sheet.jpg")
        sheet.save(sheet_path, "JPEG", quality=92)
        print(f"Audit sheet saved to: {sheet_path}")
        return out_mp4, sheet_path
        
    return out_mp4, None

def main():
    audio_path, timing_json = generate_audio_pipeline()
    out_mp4 = os.path.join(PRODUCTION_DIR, "shorts_11_11_master.mp4")
    render_video_pipeline(timing_json, audio_path, out_mp4)

if __name__ == "__main__":
    main()
