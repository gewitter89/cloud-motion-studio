#!/usr/bin/env python3
"""
Generate 3 calibrated male voice auditions (A/B/C) on the exact same Scene 2 paragraph.
Mastered via FFmpeg with studio EQ & two-pass loudnorm to -16 LUFS, True Peak <= -1.5 dBTP.
"""

import os
import sys
import json
import subprocess
import asyncio
import httpx

TEXT = (
    "9 ноября 1989 года вошло в историю как день, когда пала Берлинская стена. "
    "В одну ночь то, что десятилетиями разделяло семьи и держало мир в напряжении, "
    "рассыпалось в пыль перед напором тысяч безоружных людей. "
    "Они поднялись на бетонные плиты не ради разрушения, а ради свободы, "
    "доказав всему миру: ни одна граница не устоит перед единством и верой."
)

OPTIONS = {
    "A": {
        "title": "Вариант A: Документальный академический",
        "desc": "Сдержанный, четкий тон хроники, нейтральный темп (100%), ровная студийная АЧХ",
        "voice": "ru-RU-DmitryNeural",
        "rate": "+0%",
        "eq_filter": "highpass=f=60,lowpass=f=12000"
    },
    "B": {
        "title": "Вариант B: Глубокий драматический нарратор",
        "desc": "Замедленный на 5% темп, теплый глубокий тембр (интимный low-end +2.5dB на 120Hz), весомость и паузы",
        "voice": "ru-RU-DmitryNeural",
        "rate": "-5%",
        "eq_filter": "highpass=f=60,equalizer=f=120:width_type=o:width=1.2:g=2.8,equalizer=f=3500:width_type=o:width=1:g=-1.5,lowpass=f=11000"
    },
    "C": {
        "title": "Вариант C: Динамичный эксплейнер",
        "desc": "Энергичная подача (+4% к темпу), четкий аналитический фокус на согласных (+2dB на 2.8kHz)",
        "voice": "ru-RU-DmitryNeural",
        "rate": "+4%",
        "eq_filter": "highpass=f=75,equalizer=f=2800:width_type=o:width=1:g=2.2,lowpass=f=13000"
    }
}

async def generate_raw_tts(text: str, out_raw: str, voice: str, rate: str):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(out_raw)

def master_audio(raw_path: str, norm_path: str, eq_filter: str):
    # Two-pass loudnorm to guarantee exact -16 LUFS and True Peak <= -1.5 dBTP
    combined_filter = f"{eq_filter},loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json"
    cmd_measure = [
        "ffmpeg", "-y", "-i", raw_path,
        "-af", combined_filter,
        "-f", "null", "-"
    ]
    p = subprocess.run(cmd_measure, capture_output=True, text=True, encoding="utf-8", errors="replace")
    
    lines = p.stderr.splitlines()
    json_lines = []
    recording = False
    for line in lines:
        if line.strip().startswith("{"):
            recording = True
        if recording:
            json_lines.append(line)
        if recording and line.strip().startswith("}"):
            break
            
    stats = {}
    if json_lines:
        try:
            stats = json.loads("\n".join(json_lines))
        except Exception:
            pass

    if stats and "input_i" in stats:
        final_af = (
            f"{eq_filter},"
            f"loudnorm=I=-16:TP=-1.5:LRA=11:"
            f"measured_I={stats.get('input_i')}:"
            f"measured_TP={stats.get('input_tp')}:"
            f"measured_LRA={stats.get('input_lra')}:"
            f"measured_thresh={stats.get('input_thresh')}:"
            f"offset={stats.get('target_offset')}:linear=true"
        )
    else:
        final_af = f"{eq_filter},loudnorm=I=-16:TP=-1.5:LRA=11"

    cmd_apply = [
        "ffmpeg", "-y", "-i", raw_path,
        "-af", final_af,
        "-ar", "44100",
        "-b:a", "192k",
        norm_path
    ]
    subprocess.run(cmd_apply, check=True, capture_output=True)

    # Verification pass
    cmd_verify = [
        "ffmpeg", "-i", norm_path,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
        "-f", "null", "-"
    ]
    p_ver = subprocess.run(cmd_verify, capture_output=True, text=True, encoding="utf-8", errors="replace")
    
    ver_lines = p_ver.stderr.splitlines()
    ver_json_lines = []
    rec = False
    for line in ver_lines:
        if line.strip().startswith("{"):
            rec = True
        if rec:
            ver_json_lines.append(line)
        if rec and line.strip().startswith("}"):
            break
    ver_stats = {}
    if ver_json_lines:
        try:
            ver_stats = json.loads("\n".join(ver_json_lines))
        except Exception:
            pass

    return ver_stats

def send_telegram_audio(filepath: str, title: str, caption: str):
    bot_token = "8976290222:AAGGiziDbhsKPbapeWLuSDBU7OCaDon0B9A"
    chat_id = "8531839081"
    url = f"https://api.telegram.org/bot{bot_token}/sendAudio"
    try:
        with open(filepath, "rb") as f:
            resp = httpx.post(
                url,
                data={"chat_id": chat_id, "caption": caption, "title": title, "performer": "Диктор A/B/C", "parse_mode": "HTML"},
                files={"audio": (os.path.basename(filepath), f, "audio/mpeg")},
                timeout=60
            )
            print(f"Telegram sent: {resp.status_code}")
    except Exception as e:
        print(f"Telegram error: {e}")

def main():
    out_dir = os.path.abspath("production/auditions")
    os.makedirs(out_dir, exist_ok=True)
    web_dir = "/var/www/signals"
    
    results = {}
    for opt_id, cfg in OPTIONS.items():
        print(f"\n=== Generating Option {opt_id}: {cfg['title']} ===")
        raw_path = os.path.join(out_dir, f"voice_{opt_id}_raw.mp3")
        norm_path = os.path.join(out_dir, f"voice_audition_{opt_id}.mp3")
        
        asyncio.run(generate_raw_tts(TEXT, raw_path, cfg["voice"], cfg["rate"]))
        stats = master_audio(raw_path, norm_path, cfg["eq_filter"])
        
        # probe duration
        dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", norm_path]
        dur_out = subprocess.run(dur_cmd, capture_output=True, text=True).stdout.strip()
        duration = float(dur_out) if dur_out else 0.0

        web_url = f"https://signals-sacramento-enquiry-looks.trycloudflare.com/audition_{opt_id}.mp3"
        if os.path.exists(web_dir):
            import shutil
            shutil.copy(norm_path, os.path.join(web_dir, f"audition_{opt_id}.mp3"))

        results[opt_id] = {
            "title": cfg["title"],
            "desc": cfg["desc"],
            "voice": cfg["voice"],
            "rate": cfg["rate"],
            "duration": round(duration, 2),
            "file": norm_path,
            "web_url": web_url,
            "integrated_lufs": stats.get("input_i"),
            "true_peak": stats.get("input_tp")
        }
        print(f"Result {opt_id}: {duration}s | Integrated: {stats.get('input_i')} LUFS | TP: {stats.get('input_tp')} dBTP")
        
        caption = (
            f"🎙 <b>{cfg['title']}</b>\n"
            f"ℹ️ {cfg['desc']}\n"
            f"⏱ Хронометраж: {duration:.1f} сек\n"
            f"🎚 Громкость: {stats.get('input_i')} LUFS (Цель: -16.0)\n"
            f"🌐 Ссылка: {web_url}"
        )
        send_telegram_audio(norm_path, f"Прослушивание {opt_id}", caption)

    report_path = os.path.join(out_dir, "auditions_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nAll auditions generated and dispatched. Report saved to {report_path}")

if __name__ == "__main__":
    main()
