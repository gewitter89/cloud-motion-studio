#!/usr/bin/env python3
"""
Generate 3 calibrated male voice auditions (A/B/C) on the exact same Scene 2 paragraph.
Normalize to -16 LUFS, True Peak <= -1.5 dBTP.
"""

import os
import sys
import json
import subprocess
import asyncio

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
        "desc": "Нейтральный, сдержанный, четкий тон хроники, ровный темп",
        "voice": "ru-RU-DmitryNeural",
        "rate": "+0%",
        "pitch": "-1Hz",
        "volume": "+0%"
    },
    "B": {
        "title": "Вариант B: Глубокий драматический нарратор",
        "desc": "Замедленный на 4% темп, теплый глубокий регистр (-4Hz), весомость и паузы",
        "voice": "ru-RU-DmitryNeural",
        "rate": "-4%",
        "pitch": "-4Hz",
        "volume": "+0%"
    },
    "C": {
        "title": "Вариант C: Динамичный современный эксплейнер",
        "desc": "Энергичная подача (+3% темп), аналитический уверенный голос",
        "voice": "ru-RU-DmitryNeural",
        "rate": "+3%",
        "pitch": "+0Hz",
        "volume": "+0%"
    }
}

async def generate_tts(text: str, out_raw: str, voice: str, rate: str, pitch: str, volume: str):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=volume)
    await communicate.save(out_raw)

def normalize_audio(raw_path: str, norm_path: str):
    # Two-pass loudnorm to guarantee exact -16 LUFS and True Peak <= -1.5 dBTP
    # Pass 1: measure
    cmd_measure = [
        "ffmpeg", "-y", "-i", raw_path,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
        "-f", "null", "-"
    ]
    p = subprocess.run(cmd_measure, capture_output=True, text=True, encoding="utf-8", errors="replace")
    
    # Extract json
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

    # Pass 2: apply
    if stats and "input_i" in stats:
        filter_str = (
            f"loudnorm=I=-16:TP=-1.5:LRA=11:"
            f"measured_I={stats.get('input_i')}:"
            f"measured_TP={stats.get('input_tp')}:"
            f"measured_LRA={stats.get('input_lra')}:"
            f"measured_thresh={stats.get('input_thresh')}:"
            f"offset={stats.get('target_offset')}:linear=true"
        )
    else:
        filter_str = "loudnorm=I=-16:TP=-1.5:LRA=11"

    cmd_apply = [
        "ffmpeg", "-y", "-i", raw_path,
        "-af", filter_str,
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

def main():
    out_dir = os.path.abspath("production/auditions")
    os.makedirs(out_dir, exist_ok=True)
    
    results = {}
    for opt_id, cfg in OPTIONS.items():
        print(f"=== Generating Option {opt_id}: {cfg['title']} ===")
        raw_path = os.path.join(out_dir, f"voice_{opt_id}_raw.mp3")
        norm_path = os.path.join(out_dir, f"voice_audition_{opt_id}.mp3")
        
        asyncio.run(generate_tts(TEXT, raw_path, cfg["voice"], cfg["rate"], cfg["pitch"], cfg["volume"]))
        stats = normalize_audio(raw_path, norm_path)
        
        # probe duration
        dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", norm_path]
        dur_out = subprocess.run(dur_cmd, capture_output=True, text=True).stdout.strip()
        duration = float(dur_out) if dur_out else 0.0

        results[opt_id] = {
            "title": cfg["title"],
            "desc": cfg["desc"],
            "voice": cfg["voice"],
            "rate": cfg["rate"],
            "pitch": cfg["pitch"],
            "duration": round(duration, 2),
            "file": norm_path,
            "integrated_lufs": stats.get("input_i"),
            "true_peak": stats.get("input_tp")
        }
        print(f"Result {opt_id}: {duration}s, LUFS: {stats.get('input_i')}, TP: {stats.get('input_tp')}")

    report_path = os.path.join(out_dir, "auditions_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nAll auditions generated. Saved to {out_dir}")

if __name__ == "__main__":
    main()
