"""Quick updates: the film is kept as 30-second pieces in out/chunks/.

  python3 render_quick.py 40,60        re-render only the pieces covering 0:40-1:00, then rebuild both videos
  python3 render_quick.py all          re-render every piece (needed when the timeline changes)
  python3 render_quick.py split        cut the current full video into pieces (one-time setup)
  python3 render_quick.py assemble     rebuild both videos from the pieces

Pieces are 720 frames (30 s) with a keyframe at each start, so they join without re-encoding.
The small upload file is assembled from per-piece small encodes the same way.
"""
import json, math, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

FPS, CHUNK, WORKERS = 24, 720, 3
tl = json.load(open('timeline.json'))
total_frames = int(tl['total'] * FPS)
N = math.ceil(total_frames / CHUNK)
os.makedirs('out/chunks', exist_ok=True)
BIG = ['-c:v', 'libx264', '-preset', 'fast', '-crf', '19', '-pix_fmt', 'yuv420p', '-g', str(FPS * 4)]
SMALL = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '24', '-tune', 'animation', '-maxrate', '4M',
         '-bufsize', '8M', '-pix_fmt', 'yuv420p', '-g', str(FPS * 4)]


def run(cmd):
    subprocess.run(cmd, check=True)


def small(i):
    run(['ffmpeg', '-v', 'error', '-y', '-i', f'out/chunks/c_{i:03d}.mp4', *SMALL, '-an', f'out/chunks/s_{i:03d}.mp4'])


def render(i):
    run(['python3', 'render.py', '0', '1', '--chunk', str(i)])
    small(i)
    print(f'piece {i + 1}/{N} done', flush=True)


def split():
    src = 'out/The_Robot_That_Learned_to_Lie_1080p.mp4'

    def one(i):
        a = i * CHUNK / FPS
        n = min(CHUNK, total_frames - i * CHUNK)
        run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{a:.4f}', '-i', src, '-frames:v', str(n), *BIG, '-an',
             f'out/chunks/c_{i:03d}.mp4'])
        small(i)
    with ThreadPoolExecutor(WORKERS) as ex:
        list(ex.map(one, range(N)))


def assemble():
    for pre, out, ab in (('c', 'The_Robot_That_Learned_to_Lie_1080p.mp4', '192k'),
                         ('s', 'The_Robot_That_Learned_to_Lie.mp4', '160k')):
        with open('out/chunks/list_' + pre + '.txt', 'w') as f:
            for i in range(N):
                f.write(f"file '{pre}_{i:03d}.mp4'\n")
        run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'out/chunks/list_{pre}.txt',
             '-i', 'assets/mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', ab,
             '-shortest', '-movflags', '+faststart', 'out/' + out])
    print('assembled')


arg = sys.argv[1]
if arg == 'split':
    split()
elif arg == 'assemble':
    assemble()
else:
    if arg == 'all':
        idx = list(range(N))
    else:
        idx = set()
        for rng in arg.split(';'):                      # several ranges: "40,60;300,320"
            a, b = [float(x) for x in rng.split(',')]
            idx |= set(range(max(0, int(a * FPS) // CHUNK), min(N, int(b * FPS) // CHUNK + 1)))
        idx = sorted(idx)
    print('re-rendering pieces', idx, flush=True)
    with ThreadPoolExecutor(WORKERS) as ex:
        list(ex.map(render, idx))
    assemble()
