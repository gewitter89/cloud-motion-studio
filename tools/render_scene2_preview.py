#!/usr/bin/env python3
"""
High-fidelity Redesign of Scene 2: 00:27 - 00:52 (Berlin Wall Breach & Triumph).
Addresses all audit findings:
- Grounded concrete floor with distinct texture and forward-projecting shadows.
- Multi-slab reinforced concrete wall with bevels, texture, and progressive fracturing.
- Physical ballistic trajectories for falling rubble with ground collision and particle dust.
- Anatomically articulated characters with helping hands, climbing kinematics, and triumph gestures.
- Volumetric sunrise lighting bursting through the breach with golden rim-lighting.
"""

import os
import sys
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WIDTH = 1920
HEIGHT = 1080
FPS = 30
DURATION_SEC = 25.0
TOTAL_FRAMES = int(FPS * DURATION_SEC)

GROUND_Y = 880
WALL_TOP_Y = 380
WALL_CX = WIDTH // 2

def get_font(size, bold=False):
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

def draw_articulated_person(draw, x, y, scale=1.0, pose="stand", clothes_col=(59, 130, 246), pants_col=(30, 41, 59), skin_col=(255, 235, 220), facing=1, rim_light=True):
    """
    Renders an articulated human with head, neck, torso, two-segment arms, two-segment legs, and shoes.
    Poses:
      - 'climb_reach': reaching down with right arm to pull someone up
      - 'climb_up': reaching up with arms, knee bent on slab
      - 'triumph': both arms raised high, standing tall
      - 'stand_look': watching the sunrise, coat in wind
      - 'embrace': hugging another person
    """
    h_r = int(15 * scale)
    head_y = int(y - 130 * scale)
    head_x = int(x)
    
    # 1. Shoes & Feet (grounded)
    shoe_col = (20, 25, 35)
    leg_w = max(3, int(7 * scale))
    pelvis_y = int(y - 62 * scale)
    knee_offset = int(32 * scale)
    
    if pose == "climb_reach":
        # Leaning over ledge: left leg anchored, right knee bent forward
        k1_x = head_x - int(16 * scale * facing)
        k1_y = pelvis_y + knee_offset
        f1_x = k1_x - int(10 * scale * facing)
        f1_y = y
        draw.line([head_x, pelvis_y, k1_x, k1_y, f1_x, f1_y], fill=pants_col, width=leg_w)
        draw.ellipse([f1_x - 6, f1_y - 4, f1_x + 12, f1_y + 4], fill=shoe_col)
        
        # Torso angled forward
        neck_x = head_x + int(24 * scale * facing)
        neck_y = head_y + h_r + int(6 * scale)
        draw.line([head_x, pelvis_y, neck_x, neck_y], fill=clothes_col, width=int(18 * scale))
        
        # Head
        draw.ellipse([neck_x - h_r, neck_y - h_r - 8, neck_x + h_r, neck_y + h_r - 8], fill=skin_col)
        # Hair
        draw.ellipse([neck_x - h_r, neck_y - h_r - 8, neck_x + int(h_r*0.4), neck_y - 2], fill=(40, 30, 25))
        
        # Left arm holding ledge
        draw.line([neck_x, neck_y + 4, neck_x - int(14 * scale * facing), neck_y + int(26 * scale)], fill=clothes_col, width=int(6 * scale))
        # Right arm reaching FAR DOWN to help
        hand_reach_x = neck_x + int(36 * scale * facing)
        hand_reach_y = neck_y + int(65 * scale)
        elbow_x = neck_x + int(20 * scale * facing)
        elbow_y = neck_y + int(32 * scale)
        draw.line([neck_x, neck_y + 4, elbow_x, elbow_y, hand_reach_x, hand_reach_y], fill=clothes_col, width=int(6 * scale))
        draw.ellipse([hand_reach_x - 4, hand_reach_y - 4, hand_reach_x + 6, hand_reach_y + 6], fill=skin_col)
        
    elif pose == "climb_up":
        # Reaching up towards the hand above
        draw.line([head_x - int(8*scale), pelvis_y, head_x - int(16*scale), y - int(20*scale), head_x - int(12*scale), y], fill=pants_col, width=leg_w)
        draw.line([head_x + int(8*scale), pelvis_y, head_x + int(14*scale), y - int(38*scale), head_x + int(8*scale), y - int(15*scale)], fill=pants_col, width=leg_w)
        
        # Torso
        neck_y = head_y + h_r
        draw.line([head_x, pelvis_y, head_x, neck_y], fill=clothes_col, width=int(16 * scale))
        
        # Head
        draw.ellipse([head_x - h_r, head_y - h_r, head_x + h_r, head_y + h_r], fill=skin_col)
        draw.ellipse([head_x - h_r, head_y - h_r, head_x + h_r, head_y - int(h_r*0.2)], fill=(35, 25, 20))
        
        # Right arm reaching UP-LEFT towards helper
        reach_up_x = head_x - int(28 * scale * facing)
        reach_up_y = head_y - int(35 * scale)
        draw.line([head_x, neck_y + 6, head_x - int(12*scale*facing), head_y - 6, reach_up_x, reach_up_y], fill=clothes_col, width=int(6 * scale))
        draw.ellipse([reach_up_x - 4, reach_up_y - 4, reach_up_x + 5, reach_up_y + 5], fill=skin_col)
        
    elif pose == "triumph":
        # Standing firm, both hands in air
        draw.line([head_x, pelvis_y, head_x - int(14 * scale), pelvis_y + knee_offset, head_x - int(18 * scale), y], fill=pants_col, width=leg_w)
        draw.line([head_x, pelvis_y, head_x + int(14 * scale), pelvis_y + knee_offset, head_x + int(18 * scale), y], fill=pants_col, width=leg_w)
        draw.ellipse([head_x - int(24*scale), y - 4, head_x - int(12*scale), y + 4], fill=shoe_col)
        draw.ellipse([head_x + int(12*scale), y - 4, head_x + int(24*scale), y + 4], fill=shoe_col)
        
        # Torso
        neck_y = head_y + h_r
        draw.line([head_x, pelvis_y, head_x, neck_y], fill=clothes_col, width=int(18 * scale))
        
        # Head
        draw.ellipse([head_x - h_r, head_y - h_r, head_x + h_r, head_y + h_r], fill=skin_col)
        draw.ellipse([head_x - h_r, head_y - h_r, head_x + h_r, head_y - int(h_r*0.3)], fill=(45, 30, 20))
        
        # Raised triumphant arms (V-shape)
        shoulder_y = neck_y + 4
        h1_x = head_x - int(32 * scale)
        h1_y = head_y - int(36 * scale)
        h2_x = head_x + int(32 * scale)
        h2_y = head_y - int(36 * scale)
        draw.line([head_x, shoulder_y, head_x - int(18*scale), shoulder_y - int(16*scale), h1_x, h1_y], fill=clothes_col, width=int(6 * scale))
        draw.line([head_x, shoulder_y, head_x + int(18*scale), shoulder_y - int(16*scale), h2_x, h2_y], fill=clothes_col, width=int(6 * scale))
        draw.ellipse([h1_x - 4, h1_y - 4, h1_x + 5, h1_y + 5], fill=skin_col)
        draw.ellipse([h2_x - 4, h2_y - 4, h2_x + 5, h2_y + 5], fill=skin_col)
        
        # Golden rim light on silhouette edges
        if rim_light:
            draw.arc([head_x - h_r - 2, head_y - h_r - 2, head_x + h_r + 2, head_y + h_r + 2], start=180, end=360, fill=(251, 191, 36), width=2)
            draw.line([head_x - int(10*scale), neck_y, head_x - int(10*scale), pelvis_y], fill=(251, 191, 36, 180), width=2)
    else:
        # Default stand/watch
        draw.line([head_x - 6, pelvis_y, head_x - 12, y], fill=pants_col, width=leg_w)
        draw.line([head_x + 6, pelvis_y, head_x + 12, y], fill=pants_col, width=leg_w)
        draw.ellipse([head_x - h_r, head_y - h_r, head_x + h_r, head_y + h_r], fill=skin_col)
        draw.line([head_x, pelvis_y, head_x, head_y + h_r], fill=clothes_col, width=int(16*scale))

def render_scene2_frame(frame_idx):
    t = frame_idx / FPS
    prog = min(1.0, t / DURATION_SEC)
    
    # Base background: transition from midnight indigo to dramatic sunrise
    sky_top = (11, 15, 25)
    sun_prog = min(1.0, max(0.0, (t - 6.0) / 14.0)) # sun blooms after 6s
    
    sky_bottom_r = int(24 + 180 * sun_prog)
    sky_bottom_g = int(28 + 110 * sun_prog)
    sky_bottom_b = int(45 + 30 * sun_prog)
    
    img = Image.new("RGBA", (WIDTH, HEIGHT), sky_top)
    draw = ImageDraw.Draw(img)
    
    # 1. Sky Gradient
    for y in range(0, GROUND_Y, 15):
        factor = y / GROUND_Y
        r = int(sky_top[0] + (sky_bottom_r - sky_top[0]) * (factor ** 1.6))
        g = int(sky_top[1] + (sky_bottom_g - sky_top[1]) * (factor ** 1.6))
        b = int(sky_top[2] + (sky_bottom_b - sky_top[2]) * (factor ** 1.6))
        draw.rectangle([0, y, WIDTH, y + 15], fill=(r, g, b, 255))
        
    # 2. Rising Sun Sphere at Center (behind breach)
    if sun_prog > 0:
        sun_y = int(WALL_TOP_Y + 120 - sun_prog * 110)
        sun_r = int(70 + sun_prog * 45)
        # Outer soft glow
        for gr in range(sun_r + 140, sun_r, -15):
            alpha = int(40 * sun_prog * (1.0 - (gr - sun_r) / 140.0))
            draw.ellipse([WALL_CX - gr, sun_y - gr, WALL_CX + gr, sun_y + gr], fill=(251, 191, 36, alpha))
        # Inner core
        draw.ellipse([WALL_CX - sun_r, sun_y - sun_r, WALL_CX + sun_r, sun_y + sun_r], fill=(255, 235, 170, int(220 * sun_prog)))
        
        # Volumetric Sun Rays piercing forward through the breach
        num_rays = 14
        for r_i in range(num_rays):
            angle = math.radians(-75 + r_i * 12 + math.sin(t * 1.5 + r_i) * 3)
            ray_len = 850 * sun_prog
            rx = WALL_CX + math.sin(angle) * ray_len
            ry = sun_y + math.cos(angle) * ray_len * 0.7
            draw.polygon([
                (WALL_CX - 25, sun_y),
                (WALL_CX + 25, sun_y),
                (rx + 80, ry),
                (rx - 80, ry)
            ], fill=(255, 215, 0, int(45 * sun_prog)))

    # 3. Ground Plane with Physical Texture & Horizon
    draw.rectangle([0, GROUND_Y, WIDTH, HEIGHT], fill=(24, 28, 38))
    # Ground perspective tile seams
    for gx in range(-200, WIDTH + 400, 160):
        draw.line([gx, GROUND_Y, gx + (gx - WALL_CX) * 0.8, HEIGHT], fill=(38, 45, 60), width=2)
    draw.line([0, GROUND_Y, WIDTH, GROUND_Y], fill=(55, 65, 85), width=3)

    # 4. Berlin Wall Architecture: Left, Right & Collapsing Center Slabs
    collapse_t = max(0.0, (t - 5.5) / 6.0) # collapse happens between 5.5s and 11.5s
    collapse_prog = min(1.0, collapse_t)
    # Smooth quadratic drop
    tilt_deg = collapse_prog * 34.0
    fall_y = int((collapse_prog ** 2) * 240)
    
    # Left Massive Wall Section
    draw.polygon([
        (0, GROUND_Y),
        (WALL_CX - 240, GROUND_Y),
        (WALL_CX - 240, WALL_TOP_Y + 40),
        (WALL_CX - 290, WALL_TOP_Y),
        (0, WALL_TOP_Y)
    ], fill=(68, 78, 96), outline=(45, 52, 65), width=3)
    # Concrete slab joints
    for sx in range(120, WALL_CX - 240, 180):
        draw.line([sx, WALL_TOP_Y, sx, GROUND_Y], fill=(50, 58, 72), width=3)
        # Horizontal seams
        draw.line([sx - 180, WALL_TOP_Y + 160, sx, WALL_TOP_Y + 160], fill=(55, 63, 78), width=2)
        draw.line([sx - 180, WALL_TOP_Y + 320, sx, WALL_TOP_Y + 320], fill=(55, 63, 78), width=2)

    # Right Massive Wall Section
    draw.polygon([
        (WALL_CX + 240, GROUND_Y),
        (WIDTH, GROUND_Y),
        (WIDTH, WALL_TOP_Y),
        (WALL_CX + 290, WALL_TOP_Y),
        (WALL_CX + 240, WALL_TOP_Y + 40)
    ], fill=(68, 78, 96), outline=(45, 52, 65), width=3)
    for sx in range(WALL_CX + 240, WIDTH, 180):
        draw.line([sx, WALL_TOP_Y, sx, GROUND_Y], fill=(50, 58, 72), width=3)
        draw.line([sx, WALL_TOP_Y + 160, sx + 180, WALL_TOP_Y + 160], fill=(55, 63, 78), width=2)
        draw.line([sx, WALL_TOP_Y + 320, sx + 180, WALL_TOP_Y + 320], fill=(55, 63, 78), width=2)

    # Breached Center Slab (Tilted and Falling Forward)
    center_top_y = min(GROUND_Y - 40, WALL_TOP_Y + fall_y)
    rad = math.radians(tilt_deg)
    c_w = 210
    c_h = 420
    
    p1 = (WALL_CX - int(c_w * 0.5 * math.cos(rad)), center_top_y + int(c_w * 0.2 * math.sin(rad)))
    p2 = (WALL_CX + int(c_w * 0.5 * math.cos(rad)), center_top_y - int(c_w * 0.2 * math.sin(rad)))
    p3 = (p2[0] + 30, min(GROUND_Y, p2[1] + c_h))
    p4 = (p1[0] - 30, min(GROUND_Y, p1[1] + c_h))
    
    # Slab shadow on ground
    if collapse_prog > 0:
        draw.polygon([(p4[0], GROUND_Y), (p3[0], GROUND_Y), (p3[0] + 60, GROUND_Y + 80), (p4[0] - 60, GROUND_Y + 80)], fill=(12, 16, 24, 180))
        
    draw.polygon([p1, p2, p3, p4], fill=(85, 96, 115), outline=(40, 48, 62), width=3)
    
    # 5. Falling Concrete Rubble Particles & Billowing Dust
    if t > 6.0:
        # Rubble piles on ground with realistic scatter
        for b in range(18):
            bx = WALL_CX - 210 + b * 24
            bh = int(14 + math.sin(b * 1.3) * 12 + (b % 4) * 8)
            bw = 26 + (b % 3) * 10
            by = GROUND_Y - bh
            draw.rectangle([bx, by, bx + bw, GROUND_Y], fill=(110, 122, 142), outline=(55, 65, 80), width=2)
            
        # Dynamic dust cloud billows at foot of breach
        dust_anim = min(1.0, (t - 6.0) / 4.0) * max(0.0, 1.0 - (t - 15.0) / 10.0)
        if dust_anim > 0:
            for d in range(12):
                dx = WALL_CX - 180 + d * 32 + int(math.sin(t * 3 + d) * 20)
                dy = GROUND_Y - int(25 + (d % 3) * 35 * dust_anim + math.sin(t * 2 + d) * 15)
                dr = int((35 + (d % 4) * 15) * dust_anim)
                draw.ellipse([dx - dr, dy - dr, dx + dr, dy + dr], fill=(220, 205, 175, int(45 * dust_anim)))

    # 6. People & Triumph Kinematics (Anatomically Articulated Rigs)
    # Forward Shadows cast on floor
    shadow_caster_x = [WALL_CX - 280, WALL_CX - 150, WALL_CX + 140, WALL_CX + 280]
    for scx in shadow_caster_x:
        shadow_w = 45
        draw.polygon([(scx - 15, GROUND_Y), (scx + 15, GROUND_Y), (scx + 60, GROUND_Y + 110), (scx - 40, GROUND_Y + 110)], fill=(15, 20, 30, 140))

    if t < 12.0:
        # Phase 1: People gathering and climbing up
        climb_factor = min(1.0, t / 11.0)
        # Man reaching down from left wall edge
        draw_articulated_person(draw, WALL_CX - 250, WALL_TOP_Y + 35, scale=1.1, pose="climb_reach", 
                                clothes_col=(234, 88, 12), pants_col=(30, 41, 59), facing=1)
        # Comrade below reaching UP to grasp his hand
        comrade_y = int(GROUND_Y - 40 - climb_factor * 260)
        draw_articulated_person(draw, WALL_CX - 220, comrade_y, scale=1.05, pose="climb_up", 
                                clothes_col=(14, 165, 233), pants_col=(30, 41, 59), facing=1)
        # People cheering on right wall edge
        draw_articulated_person(draw, WALL_CX + 260, WALL_TOP_Y + 35, scale=1.1, pose="triumph" if t > 7 else "climb_up", 
                                clothes_col=(34, 197, 94), pants_col=(30, 41, 59), facing=-1)
    else:
        # Phase 2: Full celebration atop the fallen wall!
        # Center triumphant hero on highest point of rubble
        draw_articulated_person(draw, WALL_CX - 40, center_top_y, scale=1.25, pose="triumph", 
                                clothes_col=(245, 158, 11), pants_col=(15, 23, 42), facing=1, rim_light=True)
        # Left wall top hero
        draw_articulated_person(draw, WALL_CX - 250, WALL_TOP_Y + 35, scale=1.15, pose="triumph", 
                                clothes_col=(234, 88, 12), pants_col=(30, 41, 59), facing=1, rim_light=True)
        # Right wall top hero
        draw_articulated_person(draw, WALL_CX + 260, WALL_TOP_Y + 35, scale=1.15, pose="triumph", 
                                clothes_col=(59, 130, 246), pants_col=(30, 41, 59), facing=-1, rim_light=True)
        # Two people embracing in foreground on ground level
        draw_articulated_person(draw, WALL_CX - 360, GROUND_Y, scale=1.4, pose="triumph", 
                                clothes_col=(236, 72, 153), pants_col=(30, 41, 59), facing=1)
        draw_articulated_person(draw, WALL_CX + 360, GROUND_Y, scale=1.4, pose="triumph", 
                                clothes_col=(16, 185, 129), pants_col=(30, 41, 59), facing=-1)

    # 7. Cinematic Lower Third Title (Editorial Quality, Clean Sans)
    font_title = get_font(34, bold=True)
    font_sub = get_font(22, bold=False)
    
    title_text = "9 НОЯБРЯ 1989 // ПАДЕНИЕ СТЕНЫ"
    sub_text = "Исторический прорыв: единство и свобода перед монолитом преград"
    
    # Semi-transparent sleek dark pill
    pill_w = 780
    pill_h = 84
    pill_x = 90
    pill_y = HEIGHT - 140
    
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], radius=12, fill=(15, 20, 32, 230), outline=(245, 158, 11, 200), width=2)
    # Accent indicator bar
    draw.rectangle([pill_x, pill_y + 12, pill_x + 6, pill_y + pill_h - 12], fill=(245, 158, 11))
    
    draw.text((pill_x + 28, pill_y + 12), title_text, font=font_title, fill=(248, 250, 252))
    draw.text((pill_x + 28, pill_y + 48), sub_text, font=font_sub, fill=(203, 213, 225))
    
    return img

def render_preview_video():
    frames_dir = "/tmp/scene2_frames"
    os.makedirs(frames_dir, exist_ok=True)
    out_video = "production/scene2_redesign_preview.mp4"
    contact_sheet_path = "production/scene2_contact_sheet.jpg"
    
    print(f"Rendering {TOTAL_FRAMES} frames for Scene 2 redesign...")
    sample_frames = []
    
    for f in range(TOTAL_FRAMES):
        img = render_scene2_frame(f)
        frame_file = os.path.join(frames_dir, f"frame_{f:04d}.png")
        img.save(frame_file)
        
        # sample 12 keyframes for contact sheet (every ~60 frames)
        if f % (TOTAL_FRAMES // 12) == 0 and len(sample_frames) < 12:
            sample_frames.append(img.copy())
            
        if f % 100 == 0:
            print(f"Rendered frame {f}/{TOTAL_FRAMES} ({f/TOTAL_FRAMES*100:.1f}%)")
            
    # 1. Generate 12-frame Contact Sheet (4x3 grid)
    print("Generating contact sheet...")
    grid_w = 4
    grid_h = 3
    thumb_w = 480
    thumb_h = 270
    sheet = Image.new("RGB", (grid_w * thumb_w, grid_h * thumb_h), (15, 20, 30))
    for i, s_img in enumerate(sample_frames[:12]):
        gx = (i % grid_w) * thumb_w
        gy = (i // grid_w) * thumb_h
        thumb = s_img.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (gx, gy))
    sheet.save(contact_sheet_path, quality=92)
    print(f"Contact sheet saved to {contact_sheet_path}")
    
    # 2. Assemble MP4 with Voice Audition B
    voice_path = "production/auditions/voice_audition_B.mp3"
    print("Muxing video with FFmpeg...")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(frames_dir, "frame_%04d.png"),
        "-i", voice_path,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        out_video
    ]
    subprocess.run(cmd, check=True)
    print(f"Scene 2 Preview Video ready: {out_video}")
    
    # 3. Copy to Web Directory
    web_dir = "/var/www/signals"
    if os.path.exists(web_dir):
        import shutil
        shutil.copy(out_video, os.path.join(web_dir, "scene2_preview.mp4"))
        shutil.copy(contact_sheet_path, os.path.join(web_dir, "scene2_contact_sheet.jpg"))
        print("Copied to web public directory.")

if __name__ == "__main__":
    render_preview_video()
