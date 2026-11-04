"""Build the fraction-bar lesson from retained natural-speed narration.

Run with Python 3 + Pillow and FFmpeg. The accepted narration can be recovered
from the published MP4 with FFmpeg; no credentials or speech regeneration are
needed. Timings in fractions-timing.json are aligned to that narration.
"""
import json
import math
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE.parents[1] / 'classroom/assets/videos'
W, H, FPS = 1280, 720, 12
BLUE, TEAL, INK = '#075bcd', '#00836d', '#17364b'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def text(d, xy, value, size=48, fill=INK, bold=False, anchor='la'):
    font = ImageFont.truetype(BOLD if bold else FONT, size)
    d.text(xy, value, font=font, fill=fill, anchor=anchor)


def bar(d, y, parts, filled, color=BLUE, split=None):
    """One whole is always exactly 720 pixels, for every denominator."""
    x, width, height = 300, 720, 92
    d.rectangle((x, y, x + width, y + height), fill='#edf2f8')
    for i in range(filled):
        shade = TEAL if split is not None and i >= split else color
        d.rectangle((x+i*width/parts, y, x+(i+1)*width/parts, y+height), fill=shade)
    for i in range(parts+1):
        px=x+i*width/parts
        d.line((px,y,px,y+height), fill='white', width=6)
    d.rectangle((x,y,x+width,y+height), outline=INK, width=3)


def frame(scene):
    im=Image.new('RGB',(W,H),'#f7faff');d=ImageDraw.Draw(im)
    text(d,(64,36),'ROBO-TEACHER  /  WORKED EXAMPLE',24,TEAL,bold=True)
    titles=['Add unlike fractions','The wholes are the same size','Make equal-sized pieces','One half is three sixths','One third is two sixths','Add the sixths','1/2 + 1/3 = 5/6','Your turn']
    text(d,(64,104),titles[scene],52,bold=True)
    if scene < 2:
        text(d,(112,245),'1/2',68,BLUE,bold=True);bar(d,238,2,1)
        text(d,(112,407),'1/3',68,TEAL,bold=True);bar(d,400,3,1,TEAL)
        if scene==0:text(d,(640,525),'1/2  +  1/3  =  ?',56,anchor='ma',bold=True)
        else:text(d,(640,525),'Different pieces cannot be counted together yet.',34,anchor='ma')
    elif scene < 5:
        text(d,(100,245),'3/6' if scene>=3 else '1/2',68,BLUE,bold=True);bar(d,238,6,3)
        text(d,(100,407),'2/6' if scene>=4 else '1/3',68,TEAL,bold=True);bar(d,400,6,2,TEAL)
        label=['Six equal pieces in each whole','1/2 = 3/6  (same shaded amount)','1/3 = 2/6  (same shaded amount)'][scene-2]
        text(d,(640,525),label,42,anchor='ma',bold=True)
    elif scene == 5:
        text(d,(640,190),'3/6 + 2/6 = ?',64,anchor='ma',bold=True)
        bar(d,300,6,3);bar(d,445,6,2,TEAL)
        text(d,(640,550),'Count equal sixths together.',38,anchor='ma')
    elif scene == 6:
        bar(d,280,6,5,split=3)
        text(d,(640,185),'3/6 + 2/6 = 5/6',68,anchor='ma',bold=True)
        text(d,(640,435),'3 blue sixths + 2 green sixths',40,anchor='ma')
        text(d,(640,510),'The denominator stays 6.',46,TEAL,anchor='ma',bold=True)
    else:
        text(d,(640,220),'1/2  +  1/6  =  ?',78,anchor='ma',bold=True)
        bar(d,355,6,3)
        text(d,(640,515),'Write both fractions in sixths first.',42,anchor='ma')
    return im


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    timing=json.loads((HERE/'fractions-timing.json').read_text())
    duration=timing['duration'];events=timing['scenes']
    audio=HERE/'fractions-narration.pcm'
    if not audio.exists():
        subprocess.run(['ffmpeg','-v','error','-i',str(OUT/'adding-unlike-fractions.mp4'),'-f','s16le','-ar','24000','-ac','1',str(audio)],check=True)
    frames=[frame(i) for i in range(8)]
    for i,im in enumerate(frames):im.save(HERE/f'fraction-scene-{i}.png')
    cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-f','s16le','-ar','24000','-ac','1','-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','27','-pix_fmt','yuv420p','-c:a','aac','-b:a','64k','-movflags','+faststart',str(OUT/'adding-unlike-fractions.mp4')]
    with subprocess.Popen(cmd,stdin=subprocess.PIPE) as proc:
        for n in range(math.ceil(duration*FPS)):
            t=n/FPS
            scene=max(i for i,e in enumerate(events) if e['start']<=t)
            proc.stdin.write(frames[scene].tobytes())
        proc.stdin.close()
        if proc.wait():raise RuntimeError('Video encoding failed')
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(OUT/'adding-unlike-fractions.mp4'),'-c:v','libvpx-vp9','-crf','35','-b:v','0','-row-mt','1','-c:a','libopus','-b:a','48k',str(OUT/'adding-unlike-fractions.webm')],check=True)
    (OUT/'adding-unlike-fractions-transcript.txt').write_text((HERE/'fractions-script.txt').read_text()+'\n')
    def stamp(t):
        ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}'
    cues=['WEBVTT','']
    for cue in timing['captions']:
        cues.extend([f"{stamp(cue['start'])} --> {stamp(cue['end'])}",cue['text'],''])
    (OUT/'adding-unlike-fractions.vtt').write_text('\n'.join(cues))
    print(json.dumps({'duration':duration,'files':[p.name for p in OUT.glob('adding-unlike-fractions*')]}))


if __name__=='__main__':main()
