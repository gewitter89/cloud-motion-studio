#!/usr/bin/env python3
"""Video metadata, audio loudness, and contact sheet audit. Requires ffmpeg & ffprobe.
Use: python tools/video_audit.py input.mp4 --out production/audit_original
Optional: pip install pillow for contact sheet rendering.
"""
import argparse, json, re, shutil, subprocess
from pathlib import Path

def run(cmd):
    p=subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', check=False)
    if p.returncode != 0:
        raise RuntimeError('Command failed: '+ ' '.join(cmd)+'\n'+(p.stderr or '')[-2000:])
    return p.stdout, p.stderr

def ffprobe(path):
    stdout,_=run(['ffprobe','-v','error','-show_entries','format=duration,size:stream=index,codec_name,codec_type,width,height,r_frame_rate,sample_rate,channels','-of','json',str(path)])
    return json.loads(stdout)

def sound_stats(path):
    proc=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-map','0:a:0','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,encoding='utf-8',errors='replace')
    if proc.returncode:
        return {'error':'Audio absent or loudness measurement failed','ffmpeg_error':(proc.stderr or '')[-500:]}
    matches=re.findall(r'\{\s*"input_i"\s*:\s*"[^"}]+"[\s\S]*?\}',proc.stderr or '')
    if not matches:
        return {'warning':'FFmpeg produced no loudnorm JSON'}
    vals=json.loads(matches[-1]);return {k:float(vals[k]) for k in ['input_i','input_tp','input_lra'] if k in vals}

def contact_sheet(path,out,duration,interval=5):
    try:
        from PIL import Image, ImageOps, ImageDraw
    except ImportError:
        return 'Pillow missing: skip contact sheet (pip install pillow)'
    shots=[]
    for i,t in enumerate(range(0,max(1,int(duration)),interval)):
        snap=out/f'frame_{i:03d}_{t:04d}s.jpg'
        proc=subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(path),'-frames:v','1','-vf','scale=480:-2','-q:v','3',str(snap)],capture_output=True,text=True)
        if proc.returncode==0 and snap.exists() and snap.stat().st_size:
            with Image.open(snap) as im: shots.append((t,im.convert('RGB').copy()))
    if not shots:
        return 'Could not extract frames'
    columns=4; tile_w=480; tile_h=300; rows=(len(shots)+columns-1)//columns
    result=Image.new('RGB',(columns*tile_w,rows*tile_h),(18,22,28));d=ImageDraw.Draw(result)
    for i,(t,im) in enumerate(shots):
        x=(i%columns)*tile_w;y=(i//columns)*tile_h
        im.thumbnail((tile_w,270));result.paste(im,(x,y+25))
        d.text((x+8,y+5),f'{t//60:02d}:{t%60:02d}',fill=(245,245,245))
    dest=out/'contact_sheet.jpg';result.save(dest,quality=90)
    return str(dest)

def main():
    p=argparse.ArgumentParser();p.add_argument('video');p.add_argument('--out',default='production/video_audit');p.add_argument('--interval',type=int,default=5)
    a=p.parse_args();video=Path(a.video).resolve();out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
    if not video.is_file(): raise SystemExit(f'Video missing: {video}')
    for cmd in ['ffmpeg','ffprobe']:
        if not shutil.which(cmd): raise SystemExit(f'Missing {cmd} in PATH')
    info=ffprobe(video);dur=float(info['format']['duration']);streams=info.get('streams',[])
    aud=next((s for s in streams if s.get('codec_type')=='audio'),None)
    loud=sound_stats(video) if aud else {'error':'No audio stream'}
    sheet=contact_sheet(video,out,dur,a.interval)
    warns=[]
    if not 115 <= dur <= 125: warns.append('Length outside 120 +/- 5 seconds')
    v=next((s for s in streams if s.get('codec_type')=='video'),{})
    if (v.get('width'),v.get('height')) != (1920,1080): warns.append('Unexpected output resolution')
    if 'input_i' in loud and loud['input_i'] < -18: warns.append('Low integrated loudness for target around -16 LUFS')
    if 'input_tp' in loud and loud['input_tp'] > -1.5: warns.append('True peak above -1.5 dBTP target')
    report={'file':str(video),'duration_s':dur,'video':v,'audio':aud,'loudness':loud,'contact_sheet':sheet,'warnings':warns,
            'manual_review_required':['Actual voice tone/intonation and intelligibility','Narrative match between narration and visuals','Geometry, rigging, anatomy, perspective, lighting and collision','Mobile phone legibility','Temporal scene continuity']}
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
