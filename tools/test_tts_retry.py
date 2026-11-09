import os
import time
import subprocess

sentences = [
    "Девятое ноября 1989 года вошло в историю как день, когда пала Берлинская стена.",
    "В одну ночь то, что десятилетиями разделяло семьи и держало мир в напряжении, рассыпалось в пыль перед напором тысяч безоружных людей.",
    "Они поднялись на бетонные плиты не ради разрушения, а ради свободы, доказав всему миру: ни одна граница не устоит перед единством и верой."
]

def synthesize_sentence(text, out_path, voice="ru-RU-DmitryNeural", rate=None):
    cmd = ["/opt/agent-bot/venv/bin/edge-tts", "--text", text, "--write-media", out_path, "--voice", voice]
    if rate:
        cmd.extend(["--rate", rate])
    for attempt in range(4):
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            if res.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
                return True
        except Exception as e:
            print(f"Attempt {attempt} error: {e}")
        time.sleep(1.5 * (attempt + 1))
    return False

for i, s in enumerate(sentences):
    out = f"/tmp/part_{i}.mp3"
    ok = synthesize_sentence(s, out)
    print(f"Sentence {i}: ok={ok}, size={os.path.getsize(out) if os.path.exists(out) else 0}")
