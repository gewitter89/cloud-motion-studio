"""
Vertical 9:16 (1080x1920) Render Engine for Autonomous Shorts / Reels / TikTok Factory.
Renders high-retention procedural sci-fi visuals, hero animations,
and millisecond-accurate kinetic typography subtitles directly into FFmpeg pipe.
"""

import os
import sys
import json
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1080
HEIGHT = 1920
FPS = 30.0

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTION_DIR = os.path.join(os.path.dirname(TOOLS_DIR), "production")
AUDIO_DIR = os.path.join(PRODUCTION_DIR, "shorts_audio")

# Fonts
FONT_HEADLINE_BADGE = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 28)
FONT_HEADLINE_TITLE = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 46)
FONT_SUBTITLE = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 54)
FONT_SUBTITLE_HIGHLIGHT = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 56)
FONT_TECH_HUD = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 22)

class Starfield3D:
    def __init__(self, count=1200):
        self.count = count
        # Random positions in 3D box
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
        # Perspective projection
        fov = 650.0
        sx = cx + (self.x * fov) / self.z
        sy = cy + (self.y * fov) / self.z
        
        # Valid on-screen stars
        valid = (sx >= 0) & (sx < WIDTH) & (sy >= 0) & (sy < HEIGHT)
        sx_v = sx[valid]
        sy_v = sy[valid]
        z_v = self.z[valid]
        
        # Brightness and radius based on depth
        radii = np.clip((1500.0 - z_v) / 350.0, 1.0, 4.0)
        alphas = np.clip((1500.0 - z_v) / 1500.0 * 255.0, 40.0, 255.0).astype(int)
        
        for px, py, r, a in zip(sx_v, sy_v, radii, alphas):
            color = (int(a * 0.9), int(a * 0.95), a)
            draw.ellipse([px - r, py - r, px + r, py + r], fill=color)

def draw_vignette(img):
    """Draws a cinematic subtle edge vignette."""
    draw = ImageDraw.Draw(img)
    # Top and bottom letterbox shadows
    for y in range(80):
        alpha = int((1.0 - (y / 80.0)) * 140)
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0))
    for y in range(HEIGHT - 120, HEIGHT):
        alpha = int(((y - (HEIGHT - 120)) / 120.0) * 160)
        draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0))

def render_hero_voyager(draw, frame_idx, total_frames, t_sec):
    """Act 0: Voyager probe flyby and thruster flare."""
    cx = WIDTH // 2
    cy = 760 + int(math.sin(t_sec * 1.5) * 18)
    
    # Scale zooms in slightly as camera tracks
    scale = 1.0 + (t_sec / 8.0) * 0.18
    
    # 1. High-Gain Antenna Dish (large white-gold dish)
    dish_rx = int(220 * scale)
    dish_ry = int(95 * scale)
    # Dish body
    draw.ellipse([cx - dish_rx, cy - dish_ry, cx + dish_rx, cy + dish_ry],
                 fill=(220, 225, 235), outline=(255, 215, 60), width=4)
    # Sub-reflector support struts (tripod)
    feed_y = cy - int(90 * scale)
    draw.line([(cx - int(120 * scale), cy), (cx, feed_y)], fill=(180, 190, 205), width=3)
    draw.line([(cx + int(120 * scale), cy), (cx, feed_y)], fill=(180, 190, 205), width=3)
    draw.line([(cx, cy + int(40 * scale)), (cx, feed_y)], fill=(180, 190, 205), width=3)
    # Sub-reflector feed horn
    draw.ellipse([cx - 16, feed_y - 12, cx + 16, feed_y + 12], fill=(255, 215, 60))
    
    # 2. Main Bus (10-sided equipment polygon underneath)
    bus_y = cy + int(50 * scale)
    bus_w = int(140 * scale)
    bus_h = int(70 * scale)
    draw.rectangle([cx - bus_w//2, bus_y, cx + bus_w//2, bus_y + bus_h],
                   fill=(35, 42, 58), outline=(255, 180, 0), width=3)
    
    # Gold foil thermal blanket patches
    draw.rectangle([cx - bus_w//2 + 10, bus_y + 10, cx - 10, bus_y + bus_h - 10], fill=(210, 150, 20))
    draw.rectangle([cx + 10, bus_y + 10, cx + bus_w//2 - 10, bus_y + bus_h - 10], fill=(190, 135, 15))
    
    # 3. Science Boom & Magnetometer Boom
    boom_len = int(320 * scale)
    draw.line([(cx - bus_w//2, bus_y + 20), (cx - boom_len, bus_y - 60)], fill=(150, 165, 185), width=4)
    draw.line([(cx + bus_w//2, bus_y + 20), (cx + boom_len, bus_y + 120)], fill=(150, 165, 185), width=4)
    
    # RTG Power canisters on left boom
    rtg_x = cx - boom_len + 30
    rtg_y = bus_y - 50
    draw.rectangle([rtg_x - 15, rtg_y - 25, rtg_x + 15, rtg_y + 25], fill=(80, 90, 110), outline=(255, 100, 50), width=2)
    
    # 4. Thruster pulse flare
    pulse = (math.sin(t_sec * 6.0) + 1.0) * 0.5
    flare_r = int((20 + pulse * 18) * scale)
    draw.ellipse([cx - flare_r, bus_y + bus_h + 5, cx + flare_r, bus_y + bus_h + 5 + flare_r * 2],
                 fill=(0, int(200 + pulse*55), 255))
    
    # HUD Telemetry
    draw.text((cx, cy + 240), f"VOYAGER 1 // SPEED: 17.0 km/s // DISTANCE: 24.3 BILLION KM",
              font=FONT_TECH_HUD, fill=(0, 240, 255), anchor="mm")

def render_hero_golden_record(draw, frame_idx, t_sec):
    """Act 1: Rotating Golden Record macro close-up with specular gleam."""
    cx = WIDTH // 2
    cy = 760
    radius = 340
    
    # Base dark gold record surface
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 fill=(45, 34, 10), outline=(255, 215, 60), width=6)
                 
    # Concentric high-density audio grooves
    for r in range(110, radius - 15, 14):
        w = 1 if r % 28 != 0 else 2
        col = (180, 145, 40) if r % 28 != 0 else (255, 215, 80)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=w)
        
    # Center label hub (aluminum mounting ring)
    hub_r = 90
    draw.ellipse([cx - hub_r, cy - hub_r, cx + hub_r, cy + hub_r],
                 fill=(30, 24, 8), outline=(255, 235, 120), width=3)
    draw.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=(12, 16, 26), outline=(200, 200, 200), width=2)
    
    # Rotating specular light reflection sheen
    angle = (t_sec * 0.75) % (2 * math.pi)
    for spread in [-0.25, -0.12, 0.0, 0.12, 0.25]:
        a = angle + spread
        x_end = cx + int(math.cos(a) * (radius - 10))
        y_end = cy + int(math.sin(a) * (radius - 10))
        alpha = int((1.0 - abs(spread) / 0.3) * 160)
        draw.line([(cx, cy), (x_end, y_end)], fill=(255, 250, 180), width=3)
        
    # Needle cartridge tracking the groove
    needle_x = cx + int(radius * 0.65)
    needle_y = cy - int(radius * 0.65)
    draw.line([(cx + radius + 40, cy - radius - 30), (needle_x, needle_y)], fill=(200, 210, 225), width=5)
    draw.rectangle([needle_x - 12, needle_y - 12, needle_x + 12, needle_y + 12], fill=(255, 60, 60))
    # Sparkle at needle contact point
    spark = int((math.sin(t_sec * 12.0) + 1.0) * 6)
    draw.ellipse([needle_x - spark, needle_y - spark, needle_x + spark, needle_y + spark], fill=(255, 255, 255))
    
    draw.text((cx, cy + radius + 45), "THE SOUNDS OF EARTH // 16⅔ RPM // 115 IMAGES & SOUNDS",
              font=FONT_TECH_HUD, fill=(255, 215, 60), anchor="mm")

def render_hero_pulsar_map(draw, frame_idx, t_sec):
    """Act 2: The 14-pulsar map engraving with scanning laser lines."""
    cx = WIDTH // 2
    cy = 760
    
    # Outer circular reticle
    draw.ellipse([cx - 360, cy - 360, cx + 360, cy + 360], outline=(30, 60, 95), width=2)
    draw.ellipse([cx - 220, cy - 220, cx + 220, cy + 220], outline=(40, 80, 125), width=1)
    
    # 14 Pulsar lines extending from central Sun position
    # The actual Voyager pulsar map has 14 lines of specific lengths and binary tick markings
    pulsar_angles = [0.0, 0.42, 0.85, 1.34, 1.88, 2.31, 2.76, 3.25, 3.78, 4.21, 4.65, 5.12, 5.61, 6.05]
    pulsar_lengths = [320, 240, 380, 190, 310, 280, 360, 210, 340, 270, 390, 230, 300, 260]
    
    for idx, (ang, length) in enumerate(zip(pulsar_angles, pulsar_lengths)):
        ex = cx + int(math.cos(ang) * length)
        ey = cy + int(math.sin(ang) * length)
        
        # Draw line
        draw.line([(cx, cy), (ex, ey)], fill=(0, 240, 255), width=2)
        
        # Binary frequency tick marks along line
        ticks = 5 + (idx % 4)
        for t_step in range(1, ticks):
            frac = t_step / float(ticks)
            tx = cx + int(math.cos(ang) * length * frac)
            ty = cy + int(math.sin(ang) * length * frac)
            # Perpendicular tick
            perp_ang = ang + math.pi / 2
            dx = int(math.cos(perp_ang) * 6)
            dy = int(math.sin(perp_ang) * 6)
            draw.line([(tx - dx, ty - dy), (tx + dx, ty + dy)], fill=(255, 215, 60), width=2)
            
        # Pulsar end node
        draw.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(255, 255, 255))
        
    # Central Sun circle
    draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(255, 215, 60), outline=(255, 255, 255), width=3)
    
    # Scanning laser sweep across the map
    laser_y = int(cy - 360 + ((t_sec * 180) % 720))
    draw.line([(cx - 360, laser_y), (cx + 360, laser_y)], fill=(0, 255, 180), width=3)
    
    draw.text((cx, cy + 390), "PULSAR FREQUENCY MAP // 14 TIMING BEACONS // EARTH PINPOINTED",
              font=FONT_TECH_HUD, fill=(0, 255, 180), anchor="mm")

def render_hero_pale_blue_dot(draw, frame_idx, t_sec):
    """Act 3: Pale Blue Dot scattered in authentic sunbeam column."""
    cx = WIDTH // 2
    cy = 760
    
    # Sunbeam ray (45-degree angled scattering light band)
    beam_surface = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(beam_surface)
    
    # Diagonal sunbeam polygon
    points = [
        (cx - 320, 300),
        (cx - 180, 300),
        (cx + 350, 1250),
        (cx + 180, 1250)
    ]
    b_draw.polygon(points, fill=(255, 230, 180, 28))
    
    # Secondary sharper ray
    points2 = [
        (cx - 120, 300),
        (cx - 40, 300),
        (cx + 210, 1250),
        (cx + 120, 1250)
    ]
    b_draw.polygon(points2, fill=(255, 240, 200, 36))
    
    # Earth position precisely centered in the sunbeam
    earth_x = cx + 80
    earth_y = 780
    
    # Pulsating cyan Earth pixel
    pulse = (math.sin(t_sec * 4.0) + 1.0) * 0.5
    earth_r = 5 + int(pulse * 3)
    
    # Glow halo
    for r_glow in [28, 18, 10]:
        b_draw.ellipse([earth_x - r_glow, earth_y - r_glow, earth_x + r_glow, earth_y + r_glow],
                       fill=(0, 220, 255, int(45 * (1.0 - r_glow/35.0))))
    b_draw.ellipse([earth_x - earth_r, earth_y - earth_r, earth_x + earth_r, earth_y + earth_r],
                   fill=(210, 245, 255, 255))
                   
    # Brackets around Earth
    bracket_len = 22
    bracket_gap = 26
    # Top-left
    draw.line([(earth_x - bracket_gap, earth_y - bracket_gap), (earth_x - bracket_gap + bracket_len, earth_y - bracket_gap)], fill=(0, 240, 255), width=2)
    draw.line([(earth_x - bracket_gap, earth_y - bracket_gap), (earth_x - bracket_gap, earth_y - bracket_gap + bracket_len)], fill=(0, 240, 255), width=2)
    # Bottom-right
    draw.line([(earth_x + bracket_gap, earth_y + bracket_gap), (earth_x + bracket_gap - bracket_len, earth_y + bracket_gap)], fill=(0, 240, 255), width=2)
    draw.line([(earth_x + bracket_gap, earth_y + bracket_gap), (earth_x + bracket_gap, earth_y + bracket_gap - bracket_len)], fill=(0, 240, 255), width=2)
    
    draw.text((cx, cy + 340), "PALE BLUE DOT // 6.0 BILLION KM // OUR ONLY HOME",
              font=FONT_TECH_HUD, fill=(180, 220, 255), anchor="mm")

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
    border_color = (255, 215, 60) if has_high else (50, 70, 100)
    
    # Calculate text box width and height
    cx = WIDTH // 2
    cy = 1420
    
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    pad_x = 36
    pad_y = 18
    
    # Draw dark translucent rounded pill
    pill_rect = [cx - tw//2 - pad_x, cy - th//2 - pad_y, cx + tw//2 + pad_x, cy + th//2 + pad_y]
    draw.rounded_rectangle(pill_rect, radius=18, fill=(10, 14, 22), outline=border_color, width=3)
    
    # Draw text with subtle shadow
    draw.text((cx + 2, cy + 2), text, font=font, fill=(0, 0, 0), anchor="mm")
    draw.text((cx, cy), text, font=font, fill=text_color, anchor="mm")

def render_header_hook(draw, timing_data, t_sec):
    """Renders top attention-grabbing hook badge in safe zone."""
    cx = WIDTH // 2
    badge_y = 190
    title_y = 250
    
    badge_text = f"✦ {timing_data.get('headline_badge', 'ВНИМАНИЕ')} ✦"
    draw.text((cx, badge_y), badge_text, font=FONT_HEADLINE_BADGE, fill=(255, 215, 60), anchor="mm")
    
    title_text = timing_data.get("title", "ТАЙНА ЗОЛОТОГО ДИСКА")
    draw.text((cx, title_y), title_text, font=FONT_HEADLINE_TITLE, fill=(255, 255, 255), anchor="mm")
    
    # Underline accent
    draw.line([(cx - 260, title_y + 36), (cx + 260, title_y + 36)], fill=(255, 215, 60), width=4)

def render_progress_bar(draw, t_sec, total_duration):
    """Draws top completion progress line for viewer retention."""
    pct = min(1.0, max(0.0, t_sec / total_duration))
    bar_w = int(WIDTH * pct)
    draw.line([(0, 6), (WIDTH, 6)], fill=(25, 35, 50), width=8)
    draw.line([(0, 6), (bar_w, 6)], fill=(0, 240, 255), width=8)

def render_shorts_video(timing_json_path, master_audio_path, output_mp4_path):
    with open(timing_json_path, "r", encoding="utf-8") as f:
        timing_data = json.load(f)
        
    total_duration = timing_data["total_duration"]
    total_frames = int(total_duration * FPS)
    
    print(f"=== Rendering 9:16 Shorts Video: {total_duration:.2f}s ({total_frames} frames @ {FPS} FPS) ===")
    
    starfield = Starfield3D(1000)
    
    # FFmpeg pipe process
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-", # Stdin pipe
        "-i", master_audio_path, # Audio track
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "256k",
        "-shortest",
        output_mp4_path
    ]
    
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Act boundary lookups
    acts = timing_data["acts"]
    
    # Contact sheet preview frames
    sample_indices = [int(i * total_frames / 9) for i in range(9)]
    audit_frames = []
    
    for frame_idx in range(total_frames):
        t_sec = frame_idx / FPS
        
        # 1. Base dark background
        img = Image.new("RGB", (WIDTH, HEIGHT), (8, 12, 20))
        draw = ImageDraw.Draw(img)
        
        # 2. 3D Starfield
        starfield.render(draw)
        
        # 3. Determine active act hero mode
        current_hero = "voyager_flyby"
        for act in acts:
            if act["start"] <= t_sec < act["end"] + 0.6:
                current_hero = act["hero_mode"]
                break
                
        # 4. Render central hero visual
        if current_hero == "voyager_flyby":
            render_hero_voyager(draw, frame_idx, total_frames, t_sec)
        elif current_hero == "golden_record_macro":
            render_hero_golden_record(draw, frame_idx, t_sec)
        elif current_hero == "pulsar_map_scan":
            render_hero_pulsar_map(draw, frame_idx, t_sec)
        elif current_hero == "pale_blue_dot_fade":
            render_hero_pale_blue_dot(draw, frame_idx, t_sec)
            
        # 5. Header Hook
        render_header_hook(draw, timing_data, t_sec)
        
        # 6. Kinetic Subtitles
        render_subtitles(draw, timing_data, t_sec)
        
        # 7. Progress Bar
        render_progress_bar(draw, t_sec, total_duration)
        
        # 8. Vignette
        draw_vignette(img)
        
        # Write to pipe
        proc.stdin.write(img.tobytes())
        
        # Save audit sample
        if frame_idx in sample_indices:
            audit_frames.append(img.copy())
            
        if frame_idx % 100 == 0:
            print(f"Rendered frame {frame_idx}/{total_frames} ({frame_idx/total_frames*100:.1f}%)")
            
    proc.stdin.close()
    proc.wait()
    
    print(f"Video rendered successfully: {output_mp4_path}")
    
    # Create 3x3 audit contact sheet
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
        sheet.save(sheet_path, "JPEG", quality=90)
        print(f"Saved audit contact sheet to: {sheet_path}")
        return output_mp4_path, sheet_path

    return output_mp4_path, None

if __name__ == "__main__":
    t_json = os.path.join(AUDIO_DIR, "shorts_timings.json")
    m_audio = os.path.join(AUDIO_DIR, "shorts_master_audio.mp3")
    out_mp4 = os.path.join(PRODUCTION_DIR, "pilot_shorts_voyager_9x16.mp4")
    
    render_shorts_video(t_json, m_audio, out_mp4)
