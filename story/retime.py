"""Make a forward-only, slowed copy of each clip that exactly fills its scene (assets/retimed/<name>.mp4).
The clip's key action still lands on the narrated phrase; slowed parts get motion-interpolated
in-between frames (ffmpeg minterpolate) so nothing rewinds or freezes.

  python3 retime.py            all clips (3 in parallel)
  python3 retime.py s14 s36    only these
"""
import os, subprocess, sys, json
from concurrent.futures import ThreadPoolExecutor

sys.argv_saved = sys.argv[:]
sys.argv = ['render.py', '0', '1', '--x']
g = {}
exec(open('render.py').read().split("if '--stills' in sys.argv:")[0], g)
sys.argv = sys.argv_saved
CLIPS, tl, XF = g['CLIPS'], g['tl'], g['XF']
os.makedirs('assets/retimed', exist_ok=True)


def sync_shot(name):
    ts = CLIPS[name]['ts']
    for s in tl['shots']:
        if s.get('img') == name and s['kind'] == 'img' and s['start'] - 0.01 <= ts <= s['end'] + XF:
            return s
    return next(s for s in tl['shots'] if s.get('img') == name)


def seg(src, a, b, dur, out):
    """clip seconds [a, b] -> exactly `dur` seconds at 24 fps."""
    n = max(1, int(round(dur * 24)))
    k = dur / max(0.04, b - a)
    vf = f"scale=1280:720,setpts={k:.5f}*(PTS-STARTPTS)"
    if k > 1.15:
        vf += ",minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
    else:
        vf += ",fps=24"
    vf += ",tpad=stop_mode=clone:stop_duration=2"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.3f}', '-t', f'{b - a:.3f}', '-i', src, '-vf', vf,
                    '-frames:v', str(n), '-c:v', 'libx264', '-crf', '15', '-preset', 'fast', '-pix_fmt', 'yuv420p',
                    '-an', out], check=True)


def one(name):
    c = CLIPS[name]; cd = c['cdur'] - 0.05; act = min(c['act'], cd - 0.1); ts = c['ts']
    s = sync_shot(name); s0, s1 = s['start'], s['end'] + XF
    src = f'assets/clips/{name}.mp4'
    pre, post = max(0.0, ts - s0), max(0.1, s1 - ts)
    tmp = f'assets/retimed/_{name}'
    parts = []
    # before the sync point: clip [a0, act] fills `pre` seconds (never faster than real time)
    # the lead-in always gets real clip motion (at least ~0.8 s of it, gently slowed)
    split = max(act, min(0.8, cd * 0.12)) if pre > 0.05 else act
    if pre > 0.05:
        a0 = max(0.0, split - pre)
        seg(src, a0, split, pre, tmp + '_a.mp4'); parts.append(tmp + '_a.mp4')
    b1 = min(cd, split + post)
    seg(src, split, max(split + 0.3, b1), post, tmp + '_b.mp4'); parts.append(tmp + '_b.mp4')
    with open(tmp + '.txt', 'w') as f:
        for p in parts:
            f.write(f"file '{os.path.basename(p)}'\n")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', tmp + '.txt', '-c', 'copy',
                    f'assets/retimed/{name}.mp4'], check=True)
    for p in parts + [tmp + '.txt']:
        os.remove(p)
    json.dump({'s0': s0, 'len': pre + post}, open(f'assets/retimed/{name}.json', 'w'))
    print(name, 'done', round(pre + post, 1), 's', flush=True)


names = sys.argv[1:] or sorted(CLIPS)
with ThreadPoolExecutor(3) as ex:
    list(ex.map(one, names))
