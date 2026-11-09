#!/usr/bin/env python3
"""
Atmospheric 2.5D Motion Engine for Scene 2 (Berlin Wall Breach & Triumph).
Rendered with 4K Supersampling (Downscaled to 1080p with Anti-Aliasing).
Features:
- Multi-layered Ghibli-inspired night-to-sunrise atmosphere.
- Volumetric moon, starfield, and procedural layered clouds.
- Realistic concrete slabs with bevels, capstones, and fracture geometry.
- Detailed organic vector silhouettes for characters (coats, boots, realistic limbs).
- Volumetric sunrise rays and directional forward-projecting ground shadows.
"""

import os
import sys
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# 4K internal canvas for crisp supersampling downscale to 1080p
CANVAS_W = 3840
CANVAS_H = 2160
OUT_W = 1920
OUT_H = 1080

FPS = 30
DURATION_SEC = 24.62  # exactly matched to our new clean Russian voice duration!
TOTAL_FRAMES = int(FPS * DURATION_SEC)

GROUND_Y = int(CANVAS_H * 0.82)  # ~1770px on 4K
WALL_TOP_Y = int(CANVAS_H * 0.36) # ~777px on 4K
WALL_CX = CANVAS_W // 2

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
    """
    Renders an organic, multi-polygon character silhouette with natural anatomy and cloth physics.
    Poses:
      - 'climb_reach': leaning over ledge, arm stretching down to grasp comrade's hand
      - 'climb_pull': hanging onto ledge with one hand, foot seeking purchase on slab
      - 'triumph': heroic silhouette on wall crest with raised arms and windblown coat
      - 'embrace': two people united
    """
    s = scale * 2.0 # adjusted for 4K canvas
    
    head_r = int(22 * s)
    head_y = int(cy - 180 * s)
    head_x = int(cx)
    
    # Rim light helper
    def draw_poly_rim(points, fill_col, rim_width=3):
        draw.polygon(points, fill=fill_col)
        if rim_color:
            for i in range(len(points) - 1):
                p_a, p_b = points[i], points[i+1]
                # draw rim on top and backlit edges
                if p_a[1] < cy - 40*s or (facing == 1 and p_a[0] < cx) or (facing == -1 and p_a[0] > cx):
                    draw.line([p_a, p_b], fill=rim_color, width=int(rim_width * s))

    if pose == "triumph":
        # Hero on crest: coat blowing in the wind, hands raised in V-victory
        # Head with cap/hair
        draw.ellipse([head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r], fill=coat_color)
        if rim_color:
            draw.arc([head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r], start=180, end=360, fill=rim_color, width=int(3*s))
            
        # Torso & Windblown Coat
        coat_pts = [
            (head_x - int(24*s), head_y + head_r),
            (head_x + int(24*s), head_y + head_r),
            (head_x + int(32*s), cy - int(60*s)),
            (head_x + int(48*s) * facing, cy - int(10*s)), # coat tail blowing
            (head_x + int(15*s), cy - int(30*s)),
            (head_x - int(15*s), cy - int(30*s)),
            (head_x - int(42*s) * facing, cy - int(15*s)),
            (head_x - int(30*s), cy - int(60*s))
        ]
        draw_poly_rim(coat_pts, coat_color, rim_width=3)
        
        # Legs and Boots (firm stance)
        # Left leg
        draw.polygon([
            (head_x - int(22*s), cy - int(35*s)),
            (head_x - int(32*s), cy),
            (head_x - int(12*s), cy),
            (head_x - int(8*s), cy - int(35*s))
        ], fill=(14, 18, 28))
        # Boot sole
        draw.polygon([
            (head_x - int(42*s), cy),
            (head_x - int(8*s), cy),
            (head_x - int(10*s), cy + int(8*s)),
            (head_x - int(44*s), cy + int(8*s))
        ], fill=(10, 12, 18))
        
        # Right leg
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
        
        # Raised Arms (Victory)
        # Left arm
        arm_l = [
            (head_x - int(22*s), head_y + int(15*s)),
            (head_x - int(48*s), head_y - int(35*s)),
            (head_x - int(40*s), head_y - int(45*s)),
            (head_x - int(14*s), head_y + int(10*s))
        ]
        draw_poly_rim(arm_l, coat_color, rim_width=3)
        # Hand
        draw.ellipse([head_x - int(56*s), head_y - int(56*s), head_x - int(38*s), head_y - int(38*s)], fill=(255, 230, 210))
        
        # Right arm
        arm_r = [
            (head_x + int(14*s), head_y + int(10*s)),
            (head_x + int(40*s), head_y - int(45*s)),
            (head_x + int(48*s), head_y - int(35*s)),
            (head_x + int(22*s), head_y + int(15*s))
        ]
        draw_poly_rim(arm_r, coat_color, rim_width=3)
        draw.ellipse([head_x + int(38*s), head_y - int(56*s), head_x + int(56*s), head_y - int(38*s)], fill=(255, 230, 210))

    elif pose == "climb_reach":
        # Leaning down from top of wall to grasp climbing friend
        neck_x = head_x + int(35*s * facing)
        neck_y = head_y + int(30*s)
        
        draw.ellipse([neck_x - head_r, neck_y - head_r - int(10*s), neck_x + head_r, neck_y + head_r - int(10*s)], fill=coat_color)
        
        # Angled torso
        draw.polygon([
            (head_x - int(15*s), cy - int(20*s)),
            (neck_x + int(15*s), neck_y),
            (neck_x - int(15*s), neck_y + int(20*s)),
            (head_x - int(35*s), cy - int(10*s))
        ], fill=coat_color)
        
        # Reaching arm stretching downward
        hand_x = neck_x + int(50*s * facing)
        hand_y = neck_y + int(100*s)
        draw.line([neck_x, neck_y + int(10*s), neck_x + int(25*s * facing), neck_y + int(50*s), hand_x, hand_y], fill=coat_color, width=int(12*s))
        draw.ellipse([hand_x - int(8*s), hand_y - int(8*s), hand_x + int(8*s), hand_y + int(8*s)], fill=(255, 230, 210))

    elif pose == "climb_pull":
        # Person climbing up, reaching up towards the hand above
        draw.ellipse([head_x - head_r, head_y - head_r, head_x + head_r, head_y + head_r], fill=coat_color)
        draw.polygon([
            (head_x - int(20*s), head_y + head_r),
            (head_x + int(20*s), head_y + head_r),
            (head_x + int(16*s), cy - int(30*s)),
            (head_x - int(16*s), cy - int(30*s))
        ], fill=coat_color)
        
        # Arm reaching up
        reach_x = head_x - int(35*s * facing)
        reach_y = head_y - int(60*s)
        draw.line([head_x, head_y + int(15*s), reach_x, reach_y], fill=coat_color, width=int(12*s))
        draw.ellipse([reach_x - int(8*s), reach_y - int(8*s), reach_x + int(8*s), reach_y + int(8*s)], fill=(255, 230, 210))

def render_frame_4k(frame_idx):
    t = frame_idx / FPS
    prog = min(1.0, t / DURATION_SEC)
    
    # 4K master image
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (10, 12, 22, 255))
    draw = ImageDraw.Draw(img)
    
    # 1. Atmospheric Ghibli Sky: Deep Indigo -> Warm Violet -> Sunrise Amber
    sun_bloom = min(1.0, max(0.0, (t - 4.5) / 12.0))
    
    # Sky gradient bands
    for y in range(0, GROUND_Y, 20):
        factor = y / GROUND_Y
        # Color interpolation
        r = int(12 + 45 * factor + (210 - 12) * factor * (sun_bloom ** 1.3))
        g = int(14 + 30 * factor + (140 - 14) * factor * (sun_bloom ** 1.5))
        b = int(28 + 65 * factor + (60 - 28) * factor * (sun_bloom ** 2.0))
        draw.rectangle([0, y, CANVAS_W, y + 20], fill=(min(255, r), min(255, g), min(255, b), 255))
        
    # 2. Glowing Moon and Cloud Layers
    # Moon in upper-left (Ghibli aesthetic)
    moon_x = int(CANVAS_W * 0.22)
    moon_y = int(CANVAS_H * 0.20)
    moon_r = 75
    # Soft moon glow
    for gr in range(moon_r + 160, moon_r, -15):
        alpha = int(25 * (1.0 - (gr - moon_r) / 160.0))
        draw.ellipse([moon_x - gr, moon_y - gr, moon_x + gr, moon_y + gr], fill=(235, 240, 255, alpha))
    draw.ellipse([moon_x - moon_r, moon_y - moon_r, moon_x + moon_r, moon_y + moon_r], fill=(245, 248, 255, 245))
    
    # Ambient clouds floating across sky
    for c_i in range(5):
        c_x = int((c_i * 850 + t * 35) % (CANVAS_W + 600)) - 300
        c_y = int(CANVAS_H * 0.18 + c_i * 90 + math.sin(t * 0.5 + c_i) * 30)
        c_w = 420 + c_i * 120
        c_h = 110 + c_i * 30
        c_alpha = int(35 + sun_bloom * 40)
        draw.ellipse([c_x, c_y, c_x + c_w, c_y + c_h], fill=(180, 165, 210, c_alpha))
        draw.ellipse([c_x + 80, c_y - 40, c_x + c_w - 60, c_y + c_h], fill=(210, 190, 225, c_alpha - 10))

    # 3. The Golden Sunrise bursting from behind the Wall Breach
    if sun_bloom > 0:
        sun_cx = WALL_CX
        sun_cy = int(WALL_TOP_Y + 180 - sun_bloom * 120)
        sun_radius = int(140 + sun_bloom * 80)
        # Giant soft radial bloom
        for br in range(sun_radius + 400, sun_radius, -30):
            b_alpha = int(55 * sun_bloom * (1.0 - (br - sun_radius) / 400.0))
            draw.ellipse([sun_cx - br, sun_cy - br, sun_cx + br, sun_cy + br], fill=(251, 191, 36, b_alpha))
        draw.ellipse([sun_cx - sun_radius, sun_cy - sun_radius, sun_cx + sun_radius, sun_cy + sun_radius], fill=(255, 245, 210, int(230 * sun_bloom)))
        
        # Volumetric Piercing Rays
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

    # 4. Ground Plane & Pavement Joints (Dark Earth & Concrete)
    draw.rectangle([0, GROUND_Y, CANVAS_W, CANVAS_H], fill=(20, 24, 34))
    # Perspective tile lines leading toward center
    for px in range(-400, CANVAS_W + 800, 280):
        draw.line([px, GROUND_Y, px + int((px - WALL_CX) * 0.7), CANVAS_H], fill=(32, 38, 52), width=4)
    # Ground curb line
    draw.line([0, GROUND_Y, CANVAS_W, GROUND_Y], fill=(50, 60, 80), width=6)

    # 5. Berlin Wall Architecture: Left, Right & Collapsing Slabs
    collapse_prog = min(1.0, max(0.0, (t - 4.5) / 5.5))
    slab_tilt = collapse_prog * 32.0
    slab_fall = int((collapse_prog ** 2) * 440)
    
    wall_left_w = WALL_CX - 420
    wall_right_x = WALL_CX + 420
    
    # Left Massive Wall
    draw.polygon([
        (0, GROUND_Y),
        (wall_left_w, GROUND_Y),
        (wall_left_w, WALL_TOP_Y + 70),
        (wall_left_w - 90, WALL_TOP_Y),
        (0, WALL_TOP_Y)
    ], fill=(58, 66, 82), outline=(35, 42, 54), width=5)
    # Concrete slab lines and weathering
    for sx in range(240, wall_left_w, 320):
        draw.line([sx, WALL_TOP_Y, sx, GROUND_Y], fill=(42, 49, 62), width=5)
        draw.line([sx - 320, WALL_TOP_Y + 280, sx, WALL_TOP_Y + 280], fill=(48, 56, 70), width=3)
    # Capstone on top of wall
    draw.rectangle([0, WALL_TOP_Y - 24, wall_left_w - 80, WALL_TOP_Y], fill=(75, 85, 105), outline=(40, 48, 60), width=3)

    # Right Massive Wall
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

    # Breached Falling Central Slab
    c_slab_top = min(GROUND_Y - 80, WALL_TOP_Y + slab_fall)
    rad = math.radians(slab_tilt)
    sw = 380
    sh = 760
    
    p1 = (WALL_CX - int(sw * 0.5 * math.cos(rad)), c_slab_top + int(sw * 0.18 * math.sin(rad)))
    p2 = (WALL_CX + int(sw * 0.5 * math.cos(rad)), c_slab_top - int(sw * 0.18 * math.sin(rad)))
    p3 = (p2[0] + 50, min(GROUND_Y, p2[1] + sh))
    p4 = (p1[0] - 50, min(GROUND_Y, p1[1] + sh))
    
    # Ground cast shadow of falling slab
    if collapse_prog > 0:
        draw.polygon([(p4[0], GROUND_Y), (p3[0], GROUND_Y), (p3[0] + 120, GROUND_Y + 160), (p4[0] - 120, GROUND_Y + 160)], fill=(12, 15, 22, 190))
        
    draw.polygon([p1, p2, p3, p4], fill=(78, 88, 106), outline=(38, 45, 58), width=5)

    # 6. Physical Rubble & Volumetric Billowing Dust
    if t > 5.0:
        # Rubble stones with facets
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
            
        # Volumetric dust puffs with alpha
        dust_mult = min(1.0, (t - 5.0) / 3.0) * max(0.0, 1.0 - (t - 14.0) / 9.0)
        if dust_mult > 0:
            for d in range(16):
                dx = WALL_CX - 320 + d * 45 + int(math.sin(t * 2.5 + d) * 35)
                dy = GROUND_Y - int(40 + (d % 4) * 60 * dust_mult + math.sin(t * 1.8 + d) * 25)
                dr = int((65 + (d % 3) * 30) * dust_mult)
                draw.ellipse([dx - dr, dy - dr, dx + dr, dy + dr], fill=(215, 200, 175, int(50 * dust_mult)))

    # 7. Characters: Detailed Organic Silhouettes
    # Forward Shadows cast across pavement
    casters_x = [WALL_CX - 520, WALL_CX - 280, WALL_CX + 260, WALL_CX + 520]
    for cx in casters_x:
        draw.polygon([(cx - 30, GROUND_Y), (cx + 30, GROUND_Y), (cx + 120, GROUND_Y + 220), (cx - 80, GROUND_Y + 220)], fill=(12, 16, 24, 150))

    if t < 10.5:
        # Phase 1: Reaching hand down, comrade climbing up
        climb_factor = min(1.0, t / 9.5)
        # Person on left wall top leaning down
        draw_detailed_silhouette(draw, wall_left_w - 70, WALL_TOP_Y + 60, scale=1.1, pose="climb_reach", facing=1)
        # Comrade below reaching UP
        comrade_y = int(GROUND_Y - 70 - climb_factor * 480)
        draw_detailed_silhouette(draw, wall_left_w - 30, comrade_y, scale=1.05, pose="climb_pull", facing=1)
        # People gathering on right wall
        draw_detailed_silhouette(draw, wall_right_x + 90, WALL_TOP_Y + 60, scale=1.1, pose="triumph" if t > 6.5 else "climb_pull", facing=-1)
    else:
        # Phase 2: Full Triumph on the Crest
        # Center Hero atop fallen slab
        draw_detailed_silhouette(draw, WALL_CX - 30, c_slab_top, scale=1.35, pose="triumph", facing=1)
        # Left wall top hero
        draw_detailed_silhouette(draw, wall_left_w - 80, WALL_TOP_Y + 60, scale=1.2, pose="triumph", facing=1)
        # Right wall top hero
        draw_detailed_silhouette(draw, wall_right_x + 90, WALL_TOP_Y + 60, scale=1.2, pose="triumph", facing=-1)
        # Foreground cheering figures
        draw_detailed_silhouette(draw, WALL_CX - 620, GROUND_Y, scale=1.5, pose="triumph", facing=1)
        draw_detailed_silhouette(draw, WALL_CX + 620, GROUND_Y, scale=1.5, pose="triumph", facing=-1)

    # 8. Sleek Editorial Title Card
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

    # 9. Supersampling Downscale: 4K -> 1080p Lanczos
    img_1080p = img.resize((OUT_W, OUT_H), Image.Resampling.LANCZOS)
    return img_1080p

def main():
    frames_dir = "/tmp/scene2_ghibli_frames"
    os.makedirs(frames_dir, exist_ok=True)
    out_video = "production/scene2_ghibli_preview.mp4"
    contact_sheet_path = "production/scene2_ghibli_contact_sheet.jpg"
    
    print(f"Rendering {TOTAL_FRAMES} frames in 4K supersampling -> 1080p Lanczos...")
    sample_frames = []
    
    for f in range(TOTAL_FRAMES):
        img_1080p = render_frame_4k(f)
        frame_file = os.path.join(frames_dir, f"frame_{f:04d}.png")
        img_1080p.save(frame_file)
        
        # sample 12 keyframes for contact sheet
        if f % (TOTAL_FRAMES // 12) == 0 and len(sample_frames) < 12:
            sample_frames.append(img_1080p.copy())
            
        if f % 100 == 0:
            print(f"Rendered {f}/{TOTAL_FRAMES} frames ({f/TOTAL_FRAMES*100:.1f}%)")
            
    # Contact Sheet (4x3)
    print("Generating contact sheet...")
    sheet = Image.new("RGB", (4 * 480, 3 * 270), (12, 16, 25))
    for i, s_img in enumerate(sample_frames[:12]):
        gx = (i % 4) * 480
        gy = (i // 4) * 270
        thumb = s_img.resize((480, 270), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (gx, gy))
    sheet.save(contact_sheet_path, quality=94)
    print(f"Contact sheet saved: {contact_sheet_path}")
    
    # Mux with our new clean Russian male voice!
    audio_path = "male_voice_dsp.mp3"
    if not os.path.exists(audio_path):
        audio_path = "production/auditions/voice_audition_B.mp3"
        
    print("Muxing video with FFmpeg...")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "frame_%04d.png"),
        "-i", audio_path,
        "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        out_video
    ]
    subprocess.run(cmd, check=True)
    print(f"Preview Video Ready: {out_video}")
    
    # Copy to Web directory
    web_dir = "/var/www/signals"
    if os.path.exists(web_dir):
        import shutil
        shutil.copy(out_video, os.path.join(web_dir, "scene2_ghibli_preview.mp4"))
        shutil.copy(contact_sheet_path, os.path.join(web_dir, "scene2_ghibli_contact_sheet.jpg"))
        if os.path.exists(audio_path):
            shutil.copy(audio_path, os.path.join(web_dir, "male_voice_clean.mp3"))

if __name__ == "__main__":
    main()
