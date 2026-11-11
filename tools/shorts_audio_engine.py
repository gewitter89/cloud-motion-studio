"""
Vertical Audio Engine for Autonomous Shorts / Reels / TikTok Factory.
Synthesizes speech via Edge-TTS, generates procedural multi-track SFX,
masters to EBU R128 (-14 LUFS), and outputs precision timing metadata for kinetic subtitles.
"""

import os
import sys
import json
import asyncio
import subprocess
import numpy as np
import scipy.io.wavfile as wavfile
import edge_tts

# Add tools directory to path
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if TOOLS_DIR not in sys.path:
    sys.path.append(TOOLS_DIR)

from shorts_topics import get_topic

OUTPUT_DIR = os.path.join(os.path.dirname(TOOLS_DIR), "production", "shorts_audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SAMPLE_RATE = 48000

def generate_sub_bass_drop(duration_sec=2.5, sr=SAMPLE_RATE):
    """Generates a cinematic deep sub-bass drop (90 Hz down to 38 Hz)."""
    t = np.linspace(0, duration_sec, int(sr * duration_sec), endpoint=False)
    # Exponential frequency sweep
    freq = 90.0 * np.exp(-1.1 * t) + 38.0
    phase = 2 * np.pi * np.cumsum(freq) / sr
    envelope = np.exp(-1.4 * t)
    # Saturation / warmth
    sig = envelope * np.sin(phase)
    sig = np.tanh(sig * 1.5) * 0.75
    return sig

def generate_space_drone(duration_sec, sr=SAMPLE_RATE):
    """Generates a lush sci-fi space drone with subtle modulation."""
    t = np.linspace(0, duration_sec, int(sr * duration_sec), endpoint=False)
    f0 = 55.0 # A1
    drone = 0.35 * np.sin(2 * np.pi * f0 * t + 0.15 * np.sin(2 * np.pi * 0.2 * t))
    drone += 0.20 * np.sin(2 * np.pi * (f0 * 1.5) * t) # E2 fifth
    drone += 0.15 * np.sin(2 * np.pi * (f0 * 2.0) * t) # A2 octave
    
    # Filtered low noise
    noise = np.random.normal(0, 0.05, len(t))
    # Simple lowpass moving average
    kernel_size = 200
    kernel = np.ones(kernel_size) / kernel_size
    smoothed_noise = np.convolve(noise, kernel, mode='same')
    
    total = (drone + smoothed_noise * 0.8) * 0.25
    return total

def generate_record_crackle(duration_sec=8.0, sr=SAMPLE_RATE):
    """Generates vintage vinyl/record needle clicks and surface noise."""
    t = np.linspace(0, duration_sec, int(sr * duration_sec), endpoint=False)
    noise = np.random.normal(0, 0.02, len(t))
    # Sparse random impulses (clicks)
    clicks = np.zeros(len(t))
    num_clicks = int(duration_sec * 8)
    click_indices = np.random.randint(0, len(t), size=num_clicks)
    clicks[click_indices] = np.random.uniform(0.1, 0.35, size=num_clicks)
    return (noise + clicks) * 0.35

def get_audio_duration(file_path):
    """Reads audio duration using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

async def synthesize_act(text, voice, out_path, rate="+0%"):
    """Synthesizes speech for a single act via Edge-TTS."""
    comm = edge_tts.Communicate(text, voice=voice, rate=rate)
    await comm.save(out_path)

def generate_shorts_audio(slug="voyager_golden_record"):
    topic = get_topic(slug)
    voice = topic["voice"]
    
    print(f"=== Generating Audio for Shorts: '{topic['title']}' ===")
    
    act_durations = []
    act_files = []
    
    # 1. Synthesize voice acts
    for idx, act in enumerate(topic["acts"]):
        mp3_path = os.path.join(OUTPUT_DIR, f"act_{idx}_{act['id']}.mp3")
        print(f"Synthesizing Act {idx+1}/{len(topic['acts'])}: {act['id']}...")
        asyncio.run(synthesize_act(act["text"], voice, mp3_path, rate=topic["rate"]))
        dur = get_audio_duration(mp3_path)
        print(f" -> Duration: {dur:.3f} sec")
        act_durations.append(dur)
        act_files.append(mp3_path)
        
    total_voice_dur = sum(act_durations)
    # Add comfortable pauses between acts (0.5 sec) and end buffer (1.2 sec)
    pause_sec = 0.55
    end_buffer = 1.2
    
    act_timings = []
    current_time = 0.2 # small 200ms pre-roll
    
    for idx, act in enumerate(topic["acts"]):
        dur = act_durations[idx]
        start_t = current_time
        end_t = start_t + dur
        
        # Split text into bite-sized kinetic chunks (2-3 words)
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
            "hero_mode": act["hero_mode"],
            "start": round(start_t, 3),
            "end": round(end_t, 3),
            "duration": round(dur, 3),
            "text": act["text"],
            "chunks": chunks
        })
        
        current_time = end_t + pause_sec
        
    final_duration = current_time + end_buffer
    print(f"Total video planned duration: {final_duration:.2f} seconds")
    
    # Save timing metadata JSON for the visual renderer
    timing_json_path = os.path.join(OUTPUT_DIR, "shorts_timings.json")
    with open(timing_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "title": topic["title"],
            "headline_badge": topic["headline_badge"],
            "total_duration": round(final_duration, 2),
            "acts": act_timings
        }, f, indent=2, ensure_ascii=False)
    print(f"Saved timing metadata to: {timing_json_path}")
    
    # 2. Build concatenated speech track with precise offsets
    speech_concat_wav = os.path.join(OUTPUT_DIR, "speech_full.wav")
    sr = SAMPLE_RATE
    total_samples = int(final_duration * sr)
    full_speech = np.zeros(total_samples, dtype=np.float32)
    
    for idx, act in enumerate(act_timings):
        # Decode mp3 to wav array using ffmpeg
        tmp_wav = os.path.join(OUTPUT_DIR, f"tmp_act_{idx}.wav")
        subprocess.run(["ffmpeg", "-y", "-i", act_files[idx], "-ar", str(sr), "-ac", "1", tmp_wav],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        _, data = wavfile.read(tmp_wav)
        # Normalize to float -1..1
        data = data.astype(np.float32) / 32768.0
        
        start_samp = int(act["start"] * sr)
        end_samp = min(start_samp + len(data), total_samples)
        full_speech[start_samp:end_samp] += data[:end_samp - start_samp]
        
    # 3. Procedural SFX tracks
    # Sub-bass drop at 0.0s
    bass_drop = generate_sub_bass_drop(2.8, sr)
    # Ambient space drone across full duration
    drone = generate_space_drone(final_duration, sr)
    
    full_sfx = np.zeros(total_samples, dtype=np.float32)
    full_sfx += drone
    full_sfx[:len(bass_drop)] += bass_drop * 0.95
    
    # Golden record needle crackle during Act 1
    act1_start = int(act_timings[1]["start"] * sr)
    crackle = generate_record_crackle(8.0, sr)
    end_crackle = min(act1_start + len(crackle), total_samples)
    full_sfx[act1_start:end_crackle] += crackle[:end_crackle - act1_start] * 0.4
    
    # Save intermediate voice and sfx wavs
    voice_file = os.path.join(OUTPUT_DIR, "raw_voice.wav")
    sfx_file = os.path.join(OUTPUT_DIR, "raw_sfx.wav")
    
    wavfile.write(voice_file, sr, (np.clip(full_speech, -1.0, 1.0) * 32767).astype(np.int16))
    wavfile.write(sfx_file, sr, (np.clip(full_sfx, -1.0, 1.0) * 32767).astype(np.int16))
    
    # 4. Master mix through FFmpeg loudnorm to -14 LUFS
    master_audio_path = os.path.join(OUTPUT_DIR, "shorts_master_audio.mp3")
    
    mix_cmd = [
        "ffmpeg", "-y",
        "-i", voice_file,
        "-i", sfx_file,
        "-filter_complex",
        "[0:a]volume=1.25[v];[1:a]volume=0.85[s];[v][s]amix=inputs=2:duration=first:dropout_transition=2,"
        "loudnorm=I=-14:TP=-1.5:LRA=9",
        "-c:a", "libmp3lame",
        "-b:a", "256k",
        master_audio_path
    ]
    subprocess.run(mix_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    master_dur = get_audio_duration(master_audio_path)
    print(f"Master audio generated: {master_audio_path} ({master_dur:.2f}s, -14 LUFS EBU R128)")
    
    return master_audio_path, timing_json_path, master_dur

if __name__ == "__main__":
    audio_path, json_path, dur = generate_shorts_audio()
    print(f"Done! Audio: {audio_path}, Duration: {dur:.2f}s")
