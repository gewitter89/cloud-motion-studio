#!/usr/bin/env python3
"""
Generate 3 calibrated male voice auditions (A/B/C) on the exact same Scene 2 paragraph.
Mastered via FFmpeg with studio EQ, calibrated tempo & two-pass loudnorm to -16 LUFS, True Peak <= -1.5 dBTP.
Dispatches directly to Telegram chat and Web URL.
"""

import os
import sys
import json
import subprocess
import httpx

OUT_DIR = os.path.abspath("production/auditions")
os.makedirs(OUT_DIR, exist_ok=True)
WEB_DIR = "/var/www/signals"

SRC_AUDIO = "/tmp/test_ostap_full.mp3"

OPTIONS = {
    "A": {
        "title": "Вариант A: Документальный академический",
        "desc": "Сдержанный, четкий тон хроники, естественный темп (100%), чистая студийная АЧХ",
        "filter": "highpass=f=65,lowpass=f=12000"
    },
    "B": {
        "title": "Вариант B: Глубокий драматический нарратор",
        "desc": "Замедленный темп (95%), теплый глубокий тембр (low-end +3dB на 120Hz), весомость и паузы",
        "filter": "atempo=0.95,highpass=f=60,equalizer=f=120:width_type=o:width=1.2:g=3.0,equalizer=f=3500:width_type=o:width=1:g=-1.5,lowpass=f=11000"
    },
    "C": {
        "title": "Вариант C: Динамичный современный эксплейнер",
        "desc": "Энергичная подача (+5% к темпу), четкий аналитический фокус на дикции (+2.5dB на 2.8kHz)",
        "filter": "atempo=1.05,highpass=f=75,equalizer=f=2800:width_type=o:width=1:g=2.5,lowpass=f=13000"
    }
}

def master_audio(src_path: str, norm_path: str, dsp_filter: str):
    combined_filter = f"{dsp_filter},loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json"
    cmd_measure = [
        "ffmpeg", "-y", "-i", src_path,
        "-af", combined_filter,
        "-f", "null", "-"
    ]
    p = subprocess.run(cmd_measure, capture_output=True, text=True, encoding="utf-8", errors="replace")
    
    lines = p.stderr.splitlines()
    json_lines = []
    rec = False
    for line in lines:
        if line.strip().startswith("{"):
            rec = True
        if rec:
            json_lines.append(line)
        if rec and line.strip().startswith("}"):
            break
            
    stats = {}
    if json_lines:
        try:
            stats = json.loads("\n".join(json_lines))
        except Exception:
            pass

    if stats and "input_i" in stats:
        final_af = (
            f"{dsp_filter},"
            f"loudnorm=I=-16:TP=-1.5:LRA=11:"
            f"measured_I={stats.get('input_i')}:"
            f"measured_TP={stats.get('input_tp')}:"
            f"measured_LRA={stats.get('input_lra')}:"
            f"measured_thresh={stats.get('input_thresh')}:"
            f"offset={stats.get('target_offset')}:linear=true"
        )
    else:
        final_af = f"{dsp_filter},loudnorm=I=-16:TP=-1.5:LRA=11"

    cmd_apply = [
        "ffmpeg", "-y", "-i", src_path,
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
                data={"chat_id": chat_id, "caption": caption, "title": title, "performer": "Дикторский кастинг (9 Ноября)", "parse_mode": "HTML"},
                files={"audio": (os.path.basename(filepath), f, "audio/mpeg")},
                timeout=60
            )
            print(f"Telegram sent: {resp.status_code}")
    except Exception as e:
        print(f"Telegram error: {e}")

def main():
    if not os.path.exists(SRC_AUDIO) or os.path.getsize(SRC_AUDIO) < 1000:
        print("Source audio not found, synthesizing...")
        text = (
            "Девятое ноября 1989 года вошло в историю как день, когда пала Берлинская стена. "
            "В одну ночь то, что десятилетиями разделяло семьи и держало мир в напряжении, "
            "рассыпалось в пыль перед напором тысяч безоружных людей. "
            "Они поднялись на бетонные плиты не ради разрушения, а ради свободы, "
            "доказав всему миру: ни одна граница не устоит перед единством и верой."
        )
        cmd = ["/opt/agent-bot/venv/bin/edge-tts", "--text", text, "--write-media", SRC_AUDIO, "--voice", "uk-UA-OstapNeural"]
        subprocess.run(cmd, check=True)

    results = {}
    for opt_id, cfg in OPTIONS.items():
        print(f"\n=== Mastering Option {opt_id}: {cfg['title']} ===")
        norm_path = os.path.join(OUT_DIR, f"voice_audition_{opt_id}.mp3")
        stats = master_audio(SRC_AUDIO, norm_path, cfg["filter"])
        
        # probe duration
        dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", norm_path]
        dur_out = subprocess.run(dur_cmd, capture_output=True, text=True).stdout.strip()
        duration = float(dur_out) if dur_out else 0.0

        web_url = f"https://signals-sacramento-enquiry-looks.trycloudflare.com/audition_{opt_id}.mp3"
        if os.path.exists(WEB_DIR):
            import shutil
            shutil.copy(norm_path, os.path.join(WEB_DIR, f"audition_{opt_id}.mp3"))

        results[opt_id] = {
            "title": cfg["title"],
            "desc": cfg["desc"],
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
            f"🎚 Громкость: {stats.get('input_i')} LUFS (Целевая: -16.0, True Peak: {stats.get('input_tp')} dBTP)\n"
            f"🌐 Слушать онлайн: {web_url}"
        )
        send_telegram_audio(norm_path, f"Прослушивание {opt_id}", caption)

    report_path = os.path.join(OUT_DIR, "auditions_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nAll auditions mastered and dispatched. Report saved to {report_path}")

if __name__ == "__main__":
    main()
