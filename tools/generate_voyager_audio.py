#!/usr/bin/env python3
"""
generate_voyager_audio.py
Synthesizes professional voiceover and multi-track cinematic soundscape
for the 120-second documentary film: "VOYAGER: The Loneliest Artifact".
Broadcast loudness: -14 LUFS.
"""

import os
import sys
import asyncio
import numpy as np
import wave
import subprocess
import edge_tts

TOTAL_DURATION = 120.0
SR = 44100

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
PROD_DIR = os.path.join(os.path.dirname(OUTPUT_DIR), "production", "voyager_film")
os.makedirs(PROD_DIR, exist_ok=True)

VOICE_PATH = os.path.join(PROD_DIR, "voyager_voice_raw.mp3")
MUSIC_WAV = os.path.join(PROD_DIR, "voyager_music_sfx.wav")
MASTER_AUDIO = os.path.join(PROD_DIR, "voyager_master_audio.mp3")

# Script timed for 120 seconds
SCRIPT_SECTIONS = [
    # Act 1: 00:00 - 00:30
    ("Двадцать четыре миллиарда километров от Земли. "
     "Там, где солнечный свет превращается в холодную тусклую точку, а температура падает до минус двухсот семидесяти градусов. "
     "Здесь нет ни звука, ни эха. Только ледяная бесконечная пустота. "
     "Но прямо сейчас, сквозь межзвёздную тьму, несётся одинокий кусок земного металла. Самый далёкий объект во Вселенной. "
     "Вояджер-один.", 0.0),
    
    # Act 2: 00:30 - 01:00
    ("Когда его запускали в семьдесят седьмом, никто не знал, выживет ли человечество. "
     "Но на его борту закрепили золотую пластинку — послание неведомым мирам. "
     "Шум океанского прибоя, раскаты грома, смех ребёнка. Приветствия на пятидесяти пяти языках Земли и бессмертная музыка Баха. "
     "Мы отправили в бездну самое дорогое — свидетельство того, что мы умели любить и чувствовать.", 30.0),
     
    # Act 3: 01:00 - 01:30
    ("Четырнадцатое февраля тысяча девятьсот девяностого года. "
     "По просьбе астронома Карла Сагана, Вояджер развернул свою камеру назад, к дому. "
     "И сделал последний снимок. "
     "Земля. Крошечная, едва различимая голубая пылинка, подвешенная в косом солнечном луче. "
     "Все наши войны, триумфы и трагедии — всё это происходило там. На одной песчинке посреди космического океана.", 60.0),
     
    # Act 4: 01:30 - 02:00
    ("Сегодня его генераторы остывают. Приборы угасают один за другим. "
     "Но даже когда на Земле погаснут все города, а само Солнце станет белым карликом — Вояджер продолжит свой полёт. "
     "Его золотая пластинка будет дрейфовать сквозь звёзды миллиарды лет. "
     "Как вечное доказательство того, что в холодном океане Вселенной однажды были мы.", 90.0)
]

async def synthesize_voice():
    print("1. Synthesizing cinematic voiceover with DmitryNeural...")
    temp_files = []
    for idx, (text, start_time) in enumerate(SCRIPT_SECTIONS):
        part_path = os.path.join(PROD_DIR, f"part_{idx}.mp3")
        comm = edge_tts.Communicate(text, voice="ru-RU-DmitryNeural", rate="-3%", pitch="-2Hz")
        await comm.save(part_path)
        temp_files.append((part_path, start_time))
        print(f"   Synthesized Section {idx+1} (target t={start_time}s)")
        
    # Assemble into full 120s track with exact timed padding
    inputs = []
    filter_complex = []
    for idx, (fpath, start_time) in enumerate(temp_files):
        inputs.extend(["-i", fpath])
        delay_ms = int(start_time * 1000)
        filter_complex.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms}[a{idx}];")
        
    mix_sources = "".join(f"[a{i}]" for i in range(len(temp_files)))
    filter_complex.append(f"{mix_sources}amix=inputs={len(temp_files)}:dropout_transition=0,apad=whole_dur={TOTAL_DURATION}[out]")
    
    cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", "".join(filter_complex), "-map", "[out]", "-c:a", "mp3", "-b:a", "192k", VOICE_PATH]
    subprocess.run(cmd, check=True)
    print("   Combined voice track assembled:", VOICE_PATH)

def generate_cinematic_music_and_sfx():
    print("2. Synthesizing Interstellar music bed and cosmic SFX (120s)...")
    n_samples = int(TOTAL_DURATION * SR)
    t = np.linspace(0, TOTAL_DURATION, n_samples, endpoint=False)
    
    # Track 1: Sub-bass interstellar drone (48 Hz fundamental with 5th harmonic)
    drone_f = 48.0 + 1.5 * np.sin(2 * np.pi * 0.05 * t)
    drone = 0.16 * np.sin(2 * np.pi * drone_f * t)
    drone += 0.08 * np.sin(2 * np.pi * drone_f * 1.5 * t)
    # Slow dynamic pulse
    drone_env = 0.4 + 0.6 * np.clip(t / TOTAL_DURATION, 0, 1.0)
    drone = drone * drone_env
    
    # Track 2: Interstellar wind / plasma rumble (lowpass filtered noise)
    noise = np.random.normal(0, 0.05, n_samples)
    kernel_size = 120
    wind = np.convolve(noise, np.ones(kernel_size)/kernel_size, mode='same')
    wind = wind * (0.5 + 0.5 * np.sin(2 * np.pi * 0.08 * t))
    
    # Track 3: Telemetry pulses / radio pulsars (periodic clicks like deep space probe)
    telemetry = np.zeros(n_samples)
    click_interval = int(1.2 * SR) # every 1.2s
    click_decay = int(0.04 * SR)
    click_env = np.exp(-np.linspace(0, 5, click_decay))
    for c in range(10, n_samples - click_decay, click_interval):
        # Sine blip at 1200 Hz
        blip = 0.06 * np.sin(2 * np.pi * 1200 * t[c:c+click_decay]) * click_env
        telemetry[c:c+click_decay] += blip
        
    # Track 4: Golden Record Needle Crackle in Act 2 (t: 30s to 55s)
    vinyl_mask = np.exp(-((t - 42.5) / 12.0)**4)
    crackle_noise = np.random.choice([-1.0, 0.0, 1.0], size=n_samples, p=[0.02, 0.96, 0.02])
    vinyl_sfx = crackle_noise * vinyl_mask * 0.08
    
    # Track 5: Orchestral emotional progression (C minor / Ab major chords)
    # Chord 1: Cm (00-30s), Chord 2: Ab (30-60s), Chord 3: Eb/G (60-90s), Chord 4: Bb / Cm climax (90-120s)
    def chord_tone(freq, start, end):
        mask = np.clip((t - start) / 3.0, 0, 1.0) * np.clip((end - t) / 3.0, 0, 1.0)
        return 0.06 * (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 2 * t)) * mask

    music = np.zeros(n_samples)
    # Section 1 (0-30s): C (130.8), Eb (155.6), G (196.0)
    music += chord_tone(130.81, 2, 30) + chord_tone(155.56, 4, 30) + chord_tone(196.00, 6, 30)
    # Section 2 (30-60s): Ab (103.8), C (130.8), Eb (155.6)
    music += chord_tone(103.83, 30, 60) + chord_tone(130.81, 30, 60) + chord_tone(155.56, 32, 60)
    # Section 3 (60-90s): Eb (155.6), G (196.0), Bb (233.1) - Pale Blue Dot
    music += chord_tone(155.56, 60, 90) + chord_tone(196.00, 60, 90) + chord_tone(233.08, 62, 90)
    # Section 4 (90-120s): Climax & eternal fadeout
    climax_swell = np.clip((t - 90) / 10.0, 0, 1.0) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.1 * t))
    music += (chord_tone(130.81, 90, 118) + chord_tone(196.00, 90, 118) + chord_tone(261.63, 92, 118)) * (1.0 + climax_swell)
    
    # Master SFX mix
    total_mix = drone + wind + telemetry + vinyl_sfx + music
    total_mix = np.clip(total_mix, -0.85, 0.85)
    
    with wave.open(MUSIC_WAV, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((total_mix * 32767).astype(np.int16).tobytes())
    print("   Music & SFX track saved:", MUSIC_WAV)

def master_audio():
    print("3. Final Audio Mastering (Voiceover + Music/SFX + EBU R128 -14 LUFS)...")
    cmd = [
        "ffmpeg", "-y",
        "-i", VOICE_PATH,
        "-i", MUSIC_WAV,
        "-filter_complex",
        "[0:a]volume=1.15[v];[1:a]volume=0.85[m];[v][m]amix=inputs=2:duration=first:dropout_transition=3,loudnorm=I=-14:TP=-1.5:LRA=10[out]",
        "-map", "[out]",
        "-c:a", "mp3",
        "-b:a", "256k",
        MASTER_AUDIO
    ]
    subprocess.run(cmd, check=True)
    print(f"SUCCESS: Master audio ready at {MASTER_AUDIO}")

if __name__ == "__main__":
    asyncio.run(synthesize_voice())
    generate_cinematic_music_and_sfx()
    master_audio()
