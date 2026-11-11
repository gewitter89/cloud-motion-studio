import os
import sys
import subprocess
import time
import httpx
from engine_nov9 import SCENE_RENDERERS_NOV9, WIDTH, HEIGHT, FPS

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
AUDIO_DIR = "/tmp/story_scenes_nov9"
OUT_SCENES_DIR = "/tmp/story_scenes_nov9_render"

def render_scene(scene_idx):
    audio_path = f"{AUDIO_DIR}/scene_{scene_idx}.mp3"
    out_video = f"{OUT_SCENES_DIR}/motion_scene_{scene_idx}.mp4"
    
    dur_cmd = ["ffprobe", "-i", audio_path, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"]
    dur = float(subprocess.check_output(dur_cmd).decode().strip())
    total_frames = int(dur * FPS)
    
    print(f"Rendering Scene {scene_idx+1}/5: {total_frames} frames ({dur:.2f}s) at {FPS} FPS...")
    
    ffmpeg_cmd = [
        "nice", "-n", "19",
        "ffmpeg", "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}", "-pix_fmt", "rgba", "-r", str(FPS),
        "-i", "-",
        "-i", audio_path,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        out_video
    ]
    
    p = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    renderer = SCENE_RENDERERS_NOV9[scene_idx]
    t0 = time.time()
    
    for f in range(total_frames):
        current_t = f / FPS
        img = renderer(current_t, dur)
        p.stdin.write(img.tobytes())
        
    p.stdin.close()
    p.wait()
    
    elapsed = time.time() - t0
    fps_render = total_frames / max(0.1, elapsed)
    size_mb = os.path.getsize(out_video) / (1024 * 1024)
    print(f"Scene {scene_idx+1} DONE in {elapsed:.1f}s ({fps_render:.1f} fps) | Size: {size_mb:.2f} MB")
    return out_video

def main():
    print("=== STARTING CLOUD MOTION GENERATOR: 9 НОЯБРЯ ===")
    t_start = time.time()
    os.makedirs(OUT_SCENES_DIR, exist_ok=True)
    
    scene_videos = []
    for s_idx in range(5):
        v = render_scene(s_idx)
        scene_videos.append(v)
        
    concat_list = f"{OUT_SCENES_DIR}/concat_nov9.txt"
    with open(concat_list, "w") as f:
        for vf in scene_videos:
            f.write(f"file '{vf}'\n")
            
    raw_video = "/opt/cyberdeck/public/motion_nov9_raw.mp4"
    final_video = "/opt/cyberdeck/public/motion_nov9_2026.mp4"
    
    print("Concatenating scenes into full film...")
    concat_cmd = [
        "nice", "-n", "19",
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list,
        "-c", "copy",
        "-movflags", "+faststart",
        raw_video
    ]
    subprocess.run(concat_cmd, check=True)
    
    print("Optimizing video (<40 MB) for instant Telegram delivery and mobile playback...")
    compress_cmd = [
        "nice", "-n", "19",
        "ffmpeg", "-y", "-i", raw_video,
        "-c:v", "libx264", "-crf", "27", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        final_video
    ]
    subprocess.run(compress_cmd, check=True)
    
    total_size = os.path.getsize(final_video) / (1024 * 1024)
    dur_cmd = ["ffprobe", "-i", final_video, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"]
    final_dur = float(subprocess.check_output(dur_cmd).decode().strip())
    total_time = time.time() - t_start
    
    print(f"\n🎉 9 НОЯБРЯ: ФИЛЬМ ГОТОВ ЗА {total_time:.1f}s!")
    print(f"Path: {final_video}")
    print(f"Duration: {int(final_dur//60)}m {int(final_dur%60)}s ({final_dur:.2f}s)")
    print(f"Size: {total_size:.2f} MB | Resolution: 1920x1080 @ 30 FPS")
    
    # Send to Father Telegram
    print("\nDispatching full motion video to Father Telegram...")
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram не настроен: установите TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID в переменных окружения; видео сохранено локально.")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    caption = (
        "🎬 <b>9 НОЯБРЯ: ДЕНЬ ПРОРЫВА (2-МИНУТНЫЙ АНИМАЦИОННЫЙ ФИЛЬМ)</b>\n\n"
        "⚡ <b>Сюжетная линия:</b>\n"
        "1. <b>Стена:</b> ноябрьские сумерки, серый монолит, разделение и ограничения.\n"
        "2. <b>Падение стены:</b> 9 ноября 1989 г., лучи света сквозь трещины, ликование и свобода.\n"
        "3. <b>Инженерия:</b> золотые вантовые мосты, оптоволокно и чистый цифровой синтез.\n"
        "4. <b>Скорость и Бизнес:</b> скоростное шоссе, Barber Lab с векторными ножницами (без битых символов!), поток клиентов и прибыли.\n"
        "5. <b>Вершина:</b> рассвет над свободным мегаполисом, Отец во главе масштаба.\n\n"
        f"⏱ <b>Хронометраж:</b> {int(final_dur//60)} мин {int(final_dur%60)} сек (Full HD 1080p, 30 FPS)\n"
        "🎙 <b>Озвучка:</b> Svetlana Neural (студийное качество)\n"
        "🌐 <b>GitHub:</b> https://github.com/gewitter89/cloud-motion-studio\n"
        "💻 <b>Смотреть онлайн:</b> https://signals-sacramento-enquiry-looks.trycloudflare.com/nov9.html\n\n"
        "<i>Смонтировано и отрендерено полностью в облаке Antigravity на VPS. Компьютер свободен на 100%.</i>"
    )
    
    with open(final_video, "rb") as f:
        r = httpx.post(
            url,
            data={"chat_id": CHAT_ID, "caption": caption, "parse_mode": "HTML"},
            files={"video": f},
            timeout=300
        )
        print("Telegram API Response:", r.status_code)
        if r.status_code == 200:
            print("DELIVERED_TO_TELEGRAM_SUCCESSFULLY")
        else:
            print("Telegram Error:", r.text[:200])

if __name__ == "__main__":
    main()
