"""
Vertical 9:16 (1080x1920) Render Engine for Autonomous Shorts / Reels / TikTok Factory (v2.0.0 High-End).
Applies visual-physics-audit, motion-design principles, and zero-defect typography.
Blends high-res cinema-grade illustrated artwork with procedural motion graphics.
"""

import os
import sys
import json
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WIDTH = 1080
HEIGHT = 1920
FPS = 30.0

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTION_DIR = os.path.join(os.path.dirname(TOOLS_DIR), "production")
AUDIO_DIR = os.path.join(PRODUCTION_DIR, "shorts_audio")
BRAIN_DIR = r"C:\Users\Home\.gemini\antigravity\brain\2177e9db-9f8b-4370-a527-9c6f76ef18d2"

# Asset paths
VOYAGER_ART_PATH = os.path.join(BRAIN_DIR, "cloud_motion_studio_voyager_1794393655520.jpg")
GOLDEN_RECORD_ART_PATH = os.path.join(BRAIN_DIR, "voyager_golden_record_1794394826935.jpg")

# Fonts (Standard Windows clean fonts)
FONT_HEADLINE_BADGE = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 26)
FONT_HEADLINE_TITLE = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 46)
FONT_SUBTITLE = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 52)
FONT_SUBTITLE_HIGHLIGHT = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 54)
FONT_TECH_HUD = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 20)

class Starfield3D:
    def __init__(self, count=1000):
        self.count = count
        self.x = np.random.uniform(-WIDTH, WIDTH, count)
        self.y = np.random.uniform(-HEIGHT, HEIGHT, count)
        self.z = np.random.uniform(50, 1500, count)
        self.speed = np.random.uniform(3.0, 7.0, count)

    def update(self):
        self.z -= self.speed
        mask = self.z <= 10
        self.z[mask] = np.random.uniform(1200, 1500, np.sum(mask))
        self.x[mask] = np.random.uniform(-WIDTH, WIDTH, np.sum(mask))
        self.y[mask] = np.random.uniform(-HEIGHT, HEIGHT, np.sum(mask))

    def render(self, draw, cx=WIDTH//2, cy=HEIGHT//2):
        self.update()
        fov = 650.0
        sx = cx + (self.x * fov) / self.z
        sy = cy + (self.y * fov) / self.z
        
        valid = (sx >= 0) & (sx < WIDTH) & (sy >= 0) & (sy < HEIGHT)
        sx_v = sx[valid]
        sy_v = sy[valid]
        z_v = self.z[valid]
        
        radii = np.clip((1500.0 - z_v) / 380.0, 1.0, 3.5)
        alphas = np.clip((1500.0 - z_v) / 1500.0 * 255.0, 30.0, 255.0).astype(int)
        
        for px, py, r, a in zip(sx_v, sy_v, radii, alphas):
            color = (int(a * 0.9), int(a * 0.95), a)
            draw.ellipse([px - r, py - r, px + r, py + r], fill=color)

def draw_star_glyph(draw, cx, cy, radius=8, fill=(255, 215, 60)):
    """Draws an authentic sharp 4-pointed vector star (NO font encoding dependencies, NO tofu boxes)."""
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

def render_header_hook(draw, timing_data, t_sec):
    """Renders top attention-grabbing hook badge in safe zone with ZERO tofu glyph bugs."""
    cx = WIDTH // 2
    badge_y = 195
    title_y = 255
    
    # 1. Top Category Badge
    badge_text = timing_data.get('headline_badge', 'ВНИМАНИЕ')
    bbox = FONT_HEADLINE_BADGE.getbbox(badge_text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    pad_x = 36
    pad_y = 10
    pill_rect = [cx - tw//2 - pad_x, badge_y - th//2 - pad_y, cx + tw//2 + pad_x, badge_y + th//2 + pad_y]
    
    # Glowing pill outline
    draw.rounded_rectangle(pill_rect, radius=8, fill=(20, 16, 5), outline=(255, 215, 60), width=2)
    draw.text((cx, badge_y), badge_text, font=FONT_HEADLINE_BADGE, fill=(255, 215, 60), anchor="mm")
    
    # Draw vector gold stars on left and right of badge text
    star_offset = tw // 2 + 18
    draw_star_glyph(draw, cx - star_offset, badge_y, radius=8, fill=(255, 215, 60))
    draw_star_glyph(draw, cx + star_offset, badge_y, radius=8, fill=(255, 215, 60))
    
    # 2. Main Title
    title_text = timing_data.get("title", "ТАЙНА ЗОЛОТОГО ДИСКА")
    draw.text((cx, title_y), title_text, font=FONT_HEADLINE_TITLE, fill=(255, 255, 255), anchor="mm")
    
    # Underline accent
    draw.line([(cx - 240, title_y + 36), (cx + 240, title_y + 36)], fill=(255, 215, 60), width=3)

def render_subtitles(draw, timing_data, t_sec):
    """Draws kinetic subtitle pills with word-level highlight."""
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
    
    font = FONT_SUBTITLE_HIGHLIGHT if has_high else FONT_SUBTITLE
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
    
    # Draw text with subtle shadow
    draw.text((cx + 2, cy + 2), text, font=font, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, cy), text, font=font, fill=text_color, anchor="mm")

def render_progress_bar(draw, t_sec, total_duration):
    """Draws top completion progress line for viewer retention."""
    pct = min(1.0, max(0.0, t_sec / total_duration))
    bar_w = int(WIDTH * pct)
    draw.line([(0, 6), (WIDTH, 6)], fill=(25, 35, 50), width=8)
    draw.line([(0, 6), (bar_w, 6)], fill=(0, 240, 255), width=8)

def draw_vignette(img):
    """Draws a cinematic subtle edge vignette."""
    draw = ImageDraw.Draw(img)
    for y in range(80):
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0))
    for y in range(HEIGHT - 120, HEIGHT):
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0))

class HeroCinemaCompositor:
    def __init__(self):
        print("Loading high-res cinema artwork...")
        self.raw_voyager = Image.open(VOYAGER_ART_PATH).convert("RGB")
        self.raw_record = Image.open(GOLDEN_RECORD_ART_PATH).convert("RGB")
        print("Artwork loaded successfully.")

    def render_act0_voyager(self, base_img, t_sec):
        """Act 0: Voyager cinema flyby with smooth Ken Burns zoom and HUD brackets."""
        cx = WIDTH // 2
        cy = 780
        view_w = 920
        view_h = 580
        
        # Ken Burns zoom (1.0 -> 1.15)
        zoom = 1.0 + (t_sec / 7.0) * 0.12
        crop_w = int(self.raw_voyager.width / zoom)
        crop_h = int(self.raw_voyager.height / zoom)
        
        drift_y = int(math.sin(t_sec * 0.8) * 15)
        crop_x0 = max(0, (self.raw_voyager.width - crop_w) // 2)
        crop_y0 = max(0, (self.raw_voyager.height - crop_h) // 2 + drift_y)
        cropped = self.raw_voyager.crop((crop_x0, crop_y0, crop_x0 + crop_w, crop_y0 + crop_h))
        resized = cropped.resize((view_w, view_h), Image.Resampling.LANCZOS)
        
        mask = Image.new("L", (view_w, view_h), 0)
        m_draw = ImageDraw.Draw(mask)
        m_draw.rounded_rectangle([0, 0, view_w, view_h], radius=24, fill=255)
        
        top_left_x = cx - view_w // 2
        top_left_y = cy - view_h // 2
        base_img.paste(resized, (top_left_x, top_left_y), mask)
        
        draw = ImageDraw.Draw(base_img)
        draw.rounded_rectangle([top_left_x, top_left_y, top_left_x + view_w, top_left_y + view_h],
                               radius=24, outline=(0, 240, 255), width=3)
        
        draw.text((cx, top_left_y + view_h + 35),
                  "VOYAGER 1 // INTERSTELLAR MISSION // SPEED: 17.0 km/s",
                  font=FONT_TECH_HUD, fill=(0, 240, 255), anchor="mm")

    def render_act1_record(self, base_img, t_sec):
        """Act 1: Golden Record macro close-up with rotating specular sheen."""
        cx = WIDTH // 2
        cy = 780
        view_size = 720
        
        rw = min(self.raw_record.width, self.raw_record.height)
        crop_x0 = (self.raw_record.width - rw) // 2
        crop_y0 = (self.raw_record.height - rw) // 2
        sq_record = self.raw_record.crop((crop_x0, crop_y0, crop_x0 + rw, crop_y0 + rw))
        
        rot_angle = -(t_sec * 4.0) % 360
        rotated = sq_record.rotate(rot_angle, resample=Image.Resampling.BICUBIC)
        resized = rotated.resize((view_size, view_size), Image.Resampling.LANCZOS)
        
        mask = Image.new("L", (view_size, view_size), 0)
        m_draw = ImageDraw.Draw(mask)
        m_draw.ellipse([0, 0, view_size, view_size], fill=255)
        
        top_left_x = cx - view_size // 2
        top_left_y = cy - view_size // 2
        base_img.paste(resized, (top_left_x, top_left_y), mask)
        
        draw = ImageDraw.Draw(base_img)
        draw.ellipse([top_left_x, top_left_y, top_left_x + view_size, top_left_y + view_size],
                     outline=(255, 215, 60), width=4)
        draw.ellipse([top_left_x - 14, top_left_y - 14, top_left_x + view_size + 14, top_left_y + view_size + 14],
                     outline=(140, 110, 30), width=2)
                     
        draw.text((cx, top_left_y + view_size + 45),
                  "GOLDEN PHONOGRAPH RECORD // 115 IMAGES & SOUNDS OF EARTH",
                  font=FONT_TECH_HUD, fill=(255, 215, 60), anchor="mm")

    def render_act2_pulsar(self, base_img, t_sec):
        """Act 2: Macro pulsar map scan on gold record surface."""
        cx = WIDTH // 2
        cy = 780
        view_size = 720
        
        zoom = 1.35
        rw = int(min(self.raw_record.width, self.raw_record.height) / zoom)
        crop_x0 = (self.raw_record.width - rw) // 2
        crop_y0 = (self.raw_record.height - rw) // 2
        sq_record = self.raw_record.crop((crop_x0, crop_y0, crop_x0 + rw, crop_y0 + rw))
        resized = sq_record.resize((view_size, view_size), Image.Resampling.LANCZOS)
        
        mask = Image.new("L", (view_size, view_size), 0)
        m_draw = ImageDraw.Draw(mask)
        m_draw.ellipse([0, 0, view_size, view_size], fill=255)
        
        top_left_x = cx - view_size // 2
        top_left_y = cy - view_size // 2
        base_img.paste(resized, (top_left_x, top_left_y), mask)
        
        draw = ImageDraw.Draw(base_img)
        laser_y = top_left_y + int(((t_sec * 240) % view_size))
        draw.line([(top_left_x + 40, laser_y), (top_left_x + view_size - 40, laser_y)], fill=(0, 255, 180), width=3)
        
        draw.ellipse([top_left_x, top_left_y, top_left_x + view_size, top_left_y + view_size],
                     outline=(0, 255, 180), width=4)
                     
        draw.text((cx, top_left_y + view_size + 45),
                  "14 PULSARS TRIANGULATION MAP // ACCURACY: 1 SECOND IN 100M YEARS",
                  font=FONT_TECH_HUD, fill=(0, 255, 180), anchor="mm")

    def render_act3_pale_blue_dot(self, base_img, t_sec):
        """Act 3: Pale Blue Dot scattered in authentic sunbeam column."""
        cx = WIDTH // 2
        cy = 780
        
        beam_surface = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        b_draw = ImageDraw.Draw(beam_surface)
        
        points = [
            (cx - 300, 320),
            (cx - 160, 320),
            (cx + 340, 1260),
            (cx + 170, 1260)
        ]
        b_draw.polygon(points, fill=(255, 230, 180, 26))
        
        points2 = [
            (cx - 110, 320),
            (cx - 30, 320),
            (cx + 200, 1260),
            (cx + 110, 1260)
        ]
        b_draw.polygon(points2, fill=(255, 240, 200, 34))
        
        base_img.paste(Image.alpha_composite(base_img.convert("RGBA"), beam_surface).convert("RGB"), (0, 0))
        
        draw = ImageDraw.Draw(base_img)
        earth_x = cx + 80
        earth_y = 780
        
        pulse = (math.sin(t_sec * 4.0) + 1.0) * 0.5
        earth_r = 5 + int(pulse * 3)
        
        for r_glow in [32, 20, 12]:
            draw.ellipse([earth_x - r_glow, earth_y - r_glow, earth_x + r_glow, earth_y + r_glow],
                         outline=(0, 200, 255), width=1)
        draw.ellipse([earth_x - earth_r, earth_y - earth_r, earth_x + earth_r, earth_y + earth_r],
                     fill=(210, 245, 255))
                     
        bg = 28
        bl = 20
        draw.line([(earth_x - bg, earth_y - bg), (earth_x - bg + bl, earth_y - bg)], fill=(0, 240, 255), width=2)
        draw.line([(earth_x - bg, earth_y - bg), (earth_x - bg, earth_y - bg + bl)], fill=(0, 240, 255), width=2)
        draw.line([(earth_x + bg, earth_y + bg), (earth_x + bg - bl, earth_y + bg)], fill=(0, 240, 255), width=2)
        draw.line([(earth_x + bg, earth_y + bg), (earth_x + bg, earth_y + bg - bl)], fill=(0, 240, 255), width=2)
        
        draw.text((cx, cy + 340), "PALE BLUE DOT // 6.0 BILLION KM // OUR ONLY HOME",
                  font=FONT_TECH_HUD, fill=(180, 220, 255), anchor="mm")

def render_shorts_video(timing_json_path, master_audio_path, output_mp4_path):
    with open(timing_json_path, "r", encoding="utf-8") as f:
        timing_data = json.load(f)
        
    total_duration = timing_data["total_duration"]
    total_frames = int(total_duration * FPS)
    
    print(f"=== Rendering 9:16 Shorts Video (v2.0 Cinema): {total_duration:.2f}s ({total_frames} frames @ {FPS} FPS) ===")
    
    starfield = Starfield3D(1000)
    compositor = HeroCinemaCompositor()
    
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-", # Stdin pipe
        "-i", master_audio_path,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "256k",
        "-shortest",
        output_mp4_path
    ]
    
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    acts = timing_data["acts"]
    
    sample_indices = [int(i * total_frames / 9) for i in range(9)]
    audit_frames = []
    
    for frame_idx in range(total_frames):
        t_sec = frame_idx / FPS
        
        img = Image.new("RGB", (WIDTH, HEIGHT), (8, 12, 20))
        draw = ImageDraw.Draw(img)
        
        starfield.render(draw)
        
        current_hero = "voyager_flyby"
        for act in acts:
            if act["start"] <= t_sec < act["end"] + 0.6:
                current_hero = act["hero_mode"]
                break
                
        if current_hero == "voyager_flyby":
            compositor.render_act0_voyager(img, t_sec)
        elif current_hero == "golden_record_macro":
            compositor.render_act1_record(img, t_sec)
        elif current_hero == "pulsar_map_scan":
            compositor.render_act2_pulsar(img, t_sec)
        elif current_hero == "pale_blue_dot_fade":
            compositor.render_act3_pale_blue_dot(img, t_sec)
            
        draw = ImageDraw.Draw(img)
        
        render_header_hook(draw, timing_data, t_sec)
        render_subtitles(draw, timing_data, t_sec)
        render_progress_bar(draw, t_sec, total_duration)
        draw_vignette(img)
        
        proc.stdin.write(img.tobytes())
        
        if frame_idx in sample_indices:
            audit_frames.append(img.copy())
            
        if frame_idx % 150 == 0:
            print(f"Rendered frame {frame_idx}/{total_frames} ({frame_idx/total_frames*100:.1f}%)")
            
    proc.stdin.close()
    proc.wait()
    
    print(f"Video rendered successfully: {output_mp4_path}")
    
    if audit_frames:
        sheet_w = 1080
        sheet_h = 1920
        cw = sheet_w // 3
        ch = sheet_h // 3
        sheet = Image.new("RGB", (sheet_w, sheet_h), (5, 5, 5))
        for idx, f_img in enumerate(audit_frames[:9]):
            c = idx % 3
            r = idx // 3
            thumb = f_img.resize((cw, ch), Image.Resampling.LANCZOS)
            sheet.paste(thumb, (c * cw, r * ch))
            
        sheet_path = output_mp4_path.replace(".mp4", "_audit_sheet.jpg")
        sheet.save(sheet_path, "JPEG", quality=92)
        print(f"Saved audit contact sheet to: {sheet_path}")
        return output_mp4_path, sheet_path

    return output_mp4_path, None

if __name__ == "__main__":
    t_json = os.path.join(AUDIO_DIR, "shorts_timings.json")
    m_audio = os.path.join(AUDIO_DIR, "shorts_master_audio.mp3")
    out_mp4 = os.path.join(PRODUCTION_DIR, "pilot_shorts_voyager_9x16.mp4")
    
    render_shorts_video(t_json, m_audio, out_mp4)
