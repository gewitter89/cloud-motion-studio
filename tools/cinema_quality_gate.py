#!/usr/bin/env python3
"""Agent Control cinema QA gate: honest technical checks, not automated artistic approval.

Requirements: Python >=3.10, ffmpeg, ffprobe. No GPU, paid API or model needed.
    python cinema_quality_gate.py film.mp4 --kind film --target 180 --script script.txt
    python cinema_quality_gate.py short.mp4 --kind short --target 45 --draft
Exit 0 = no hard technical failures, 2 = technical failures, 3 = tool/file error.
Visual continuity, accents and voice acting ALWAYS require human review.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Only context-sensitive homographs. No automatic substitution of uncertain accents.
HOMOGRAPHS = {'замок', 'мука', 'атлас', 'плачу', 'косы', 'стоит', 'потом', 'орган', 'стрелки', 'пропасть'}


def cmd(args, timeout=120):
    r = subprocess.run(args, capture_output=True, text=True, errors='replace', timeout=timeout)
    if r.returncode: raise RuntimeError(f"{args[0]} failed ({r.returncode}): {r.stderr[-850:]}")
    return r.stdout, r.stderr


def probe(path):
    out, _ = cmd(['ffprobe', '-v', 'error', '-show_entries',
                  'format=duration,size:stream=codec_type,codec_name,width,height,avg_frame_rate,sample_rate',
                  '-of', 'json', str(path)])
    return json.loads(out)


def detect(path, video_filter, is_audio=False, timeout=400):
    args = ['ffmpeg', '-hide_banner', '-nostats', '-i', str(path)]
    if is_audio:
        args += ['-map', '0:a:0', '-vn', '-af', video_filter]
    else:
        args += ['-map', '0:v:0', '-an', '-vf', video_filter]
    args += ['-f', 'null', '-']
    _, stderr = cmd(args, timeout=timeout)
    return stderr


def sample_motion(path, duration, limit_secs=300):
    # Decode low-res grayscale frames at 2 fps; detect stagnant periods independently of codecs.
    frames = min(int(duration * 2), limit_secs * 2)
    if frames <= 1: return {'low_motion_fraction': 1, 'sample_pairs': 0, 'max_stagnant_seconds': duration}
    w, h = 120, 68
    args = ['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:v:0',
            '-vf', 'fps=2,scale=120:68,format=gray', '-frames:v', str(frames),
            '-f', 'rawvideo', 'pipe:1']
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=240)
    if result.returncode:raise RuntimeError('Motion sample decode failed: '+result.stderr.decode(errors='replace')[-500:])
    stride = w * h
    values = result.stdout
    samples = [values[i:i+stride] for i in range(0, len(values)-stride+1, stride)]
    if len(samples)<2:return {'low_motion_fraction':1,'sample_pairs':0,'max_stagnant_seconds':duration}
    low, streak, max_streak, changes = 0, 0, 0, []
    for a,b in zip(samples,samples[1:]):
        # No floats stored or untrusted shell invocations. 120*68*2*duration limited to <= 600 frames.
        delta = sum(abs(x-y) for x,y in zip(a,b))/stride
        changes.append(delta)
        if delta<0.85:low+=1;streak+=1;max_streak=max(max_streak,streak)
        else:streak=0
    return {'low_motion_fraction':round(low/len(changes),3),
            'max_stagnant_seconds':round(max_streak/2,2),
            'median_frame_delta':round(sorted(changes)[len(changes)//2],3),
            'sample_pairs':len(changes),
            'note':'Pixel variation is not a substitute for believable character or camera movement'}


def check_voice_script(path, duration):
    if path is None:return {'not_provided':True,'manual_voice_review_required':True}
    s=Path(path).read_text(encoding='utf-8')
    words=re.findall(r"[А-Яа-яЁёІіЇїЄєҐґA-Za-z]+(?:[-'][А-Яа-яЁёІіЇїЄєҐґA-Za-z]+)*",s)
    ambiguous=sorted(set(w.lower().replace('ё','е') for w in words) & HOMOGRAPHS)
    numbers=re.findall(r'(?<!\w)\d+[.,]?\d*',s)
    wpm=round(len(words)*60/max(duration,1),1)
    return {'words':len(words),'implied_wpm':wpm,'possible_ambiguous_stress':ambiguous,
            'numbers_requiring_spoken_review':numbers[:30],
            'manual_voice_review_required':True,
            'note':'Stress and intonation cannot be verified from source text or LUFS alone'}


def assess(path,kind='film',target=None,draft=False,script=None):
    if not path.is_file():raise FileNotFoundError(str(path))
    info=probe(path);meta=info.get('format',{});duration=float(meta['duration'])
    video=next((s for s in info.get('streams',[]) if s.get('codec_type')=='video'),None)
    audio=next((s for s in info.get('streams',[]) if s.get('codec_type')=='audio'),None)
    fails,warns=[],[]
    if not video:fails.append('Нет видеодорожки');return {'status':'FAIL','failures':fails}
    w,h=video.get('width',0),video.get('height',0)
    intended=(1920,1080) if kind=='film' else (1080,1920)
    if not draft and (w,h)!=intended:fails.append(f'Финальное разрешение {w}x{h}, требуется {intended[0]}x{intended[1]}')
    if draft and (w<360 or h<360):warns.append('Черновик слишком низкого разрешения для осмысленной проверки деталей')
    fr=video.get('avg_frame_rate','0/1').split('/')
    fps=float(fr[0])/max(float(fr[1]) if len(fr)>1 else 1,1)
    if not draft and fps<23.9:warns.append(f'Частота кадров {fps:.1f} ниже 24 fps')
    if not audio:fails.append('Отсутствует звуковая дорожка')
    if target is not None and abs(duration-target)>1.5:fails.append(f'Длительность {duration:.1f}с отклоняется от цели {target:.1f}с')
    if kind=='film' and not 119<=duration<=241:warns.append('Хронометраж вне диапазона 2–4 минуты')
    if kind=='short' and not 10<=duration<=181:warns.append('Хронометраж вне диапазона Shorts')
    black=detect(path,'blackdetect=d=0.7:pix_th=0.05')
    freezes=detect(path,'freezedetect=n=-53dB:d=1.5')
    black_spans=[float(v) for v in re.findall(r'black_duration:([0-9.]+)',black)]
    freeze_at=re.findall(r'lavfi.freezedetect.freeze_(?:start|end)',freezes)
    if black_spans and max(black_spans)>2.5:warns.append('Длинная почти чёрная сцена: проверьте намерение режиссёра')
    if freeze_at:warns.append('FFmpeg обнаружил застывшие видеофрагменты')
    motion=sample_motion(path,duration)
    if motion['low_motion_fraction']>0.65:fails.append('Большинство интервалов почти неподвижны: возможное слайд-шоу')
    elif motion['max_stagnant_seconds']>=3.0:warns.append('Длительная статичная последовательность; проверьте движение камеры')
    loudness={};silence=[]
    if audio:
        aud=detect(path,'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json',True)
        matches=re.findall(r'\{\s*"input_i"\s*:[\s\S]*?\}',aud)
        if matches:
            try:
                v=json.loads(matches[-1]);loudness={k:float(v[k]) for k in ('input_i','input_tp','input_lra') if k in v}
            except (ValueError,TypeError):warns.append('Не удалось разобрать измерения LUFS')
        sil=detect(path,'silencedetect=noise=-42dB:d=1.2',True)
        silence=[float(v) for v in re.findall(r'silence_duration:\s*([0-9.]+)',sil)]
        if 'input_i' in loudness and not -20<=loudness['input_i']<=-13:warns.append('Громкость вне ориентировочного диапазона -16±4 LUFS')
        if 'input_tp' in loudness and loudness['input_tp']>-1.0:warns.append('Высокий true peak; проверьте пики и клиппинг')
        if silence and max(silence)>3:warns.append('Длинная пауза в аудиодорожке')
    return {'schema':'agent-control-cinema-qa/v1','file':str(path),'kind':kind,'is_draft':draft,
            'duration_seconds':round(duration,2),'target_seconds':target,'resolution':[w,h],'fps':round(fps,2),
            'audio_present':bool(audio),'motion':motion,'black_spans_seconds':black_spans[:20],
            'freeze_events':len(freeze_at),'silence_spans_seconds':silence[:20],
            'audio_loudness':loudness,'voice_script':check_voice_script(script,duration),
            'technical_result':'FAIL' if fails else ('WARN' if warns else 'PASS'),
            'failures':fails,'warnings':warns,
            'cinematic_qa':'REQUIRES_HUMAN_REVIEW',
            'human_checks':['Плавность персонажей и стопы на поверхности','Физически последовательная камера и свет',
                            'Осмысленность каждого плана','Природная речь, ударения, паузы, интонация',
                            'Контраст и обрезка субтитров на телефоне','Соответствие кадров сценарию']}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('video',type=Path)
    p.add_argument('--kind',choices=['film','short'],default='film')
    p.add_argument('--target',type=float)
    p.add_argument('--draft',action='store_true')
    p.add_argument('--script',type=Path)
    p.add_argument('--output',type=Path)
    a=p.parse_args(argv)
    try:
        for name in ('ffmpeg','ffprobe'):
            if not shutil.which(name):raise RuntimeError(f'Установите {name}')
        report=assess(a.video,a.kind,a.target,a.draft,a.script)
        text=json.dumps(report,ensure_ascii=False,indent=2)
        if a.output:a.output.write_text(text,encoding='utf-8')
        print(text)
        return 2 if report['technical_result']=='FAIL' else 0
    except Exception as err:
        print(json.dumps({'technical_result':'ERROR','error':str(err)},ensure_ascii=False),file=sys.stderr)
        return 3

if __name__=='__main__':sys.exit(main())