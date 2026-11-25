"""Full-screen vertical Shorts (1080x1920) from clean renders (render.py --nocap).

The 16:9 frame is cropped to 9:16 with a camera that pans smoothly to whoever matters at that moment
(keyframes below, as fractions of the frame width). Captions are redrawn for vertical: big words in the
lower third with the spoken word filling yellow, a coloured name tag for characters, a hook line at the top
for the first seconds, and a Moonlit Tales end card.

    python3 render.py 0 1 --nocap --clip 38.5,65.5 --out out/shorts/clean_1.mp4
    python3 make_shorts.py 1
"""
import json, math, subprocess, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FPS, OW, OH = 24, 1080, 1920
tl = json.load(open('timeline.json'))
WT = json.load(open('word_times.json'))
exec(open('script.py').read())
F_BOLD = 'assets/fonts/fredoka-latin-600-normal.woff'
F_HOOK = 'assets/fonts/amatic-sc-latin-700-normal.woff'
GOLD, CREAM, YELLOW = (246, 196, 82), (250, 240, 220), (255, 210, 60)
TAG = {'MIA': ('Mia', (226, 96, 112)), 'ECHO': ('Echo', (38, 168, 196)), 'OP': ('Radio', (220, 150, 40))}

SHORTS = {
    1: dict(start=38.5, length=25.8, clean='out/shorts/clean_1.mp4', out='out/shorts/Short_1_the_lie_fullscreen.mp4',
            hook=('Every night he told her', '"Mommy comes home tomorrow"'),
            keys=[(0, .30), (1.6, .30), (2.2, .66), (2.8, .66), (3.3, .32), (5.5, .32), (6.5, .55), (8.5, .55),
                  (10.5, .22), (12.6, .22), (13.6, .55), (15.8, .55), (16.6, .30), (20.4, .30), (21.0, .66),
                  (22.0, .66), (23.0, .64), (27.0, .64)]),
    2: dict(start=536.5, length=36.5, clean='out/shorts/clean_2.mp4', out='out/shorts/Short_2_the_promise_fullscreen.mp4',
            hook=('His battery is almost gone...', 'but he made a promise'),
            keys=[(0, .20), (1.5, .33), (8.4, .33), (9.2, .62), (10.0, .30), (13.6, .30), (14.6, .45), (17.6, .45),
                  (18.2, .30), (20.4, .33), (21.6, .50), (26.0, .50), (27.5, .60), (31.8, .60), (32.4, .20),
                  (34.4, .20), (35.2, .40), (36.5, .40)]),
}


def cx_at(keys, t):
    """Eased interpolation between crop-centre keyframes."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, x0), (t1, x1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            p = (t - t0) / max(1e-6, t1 - t0)
            p = 0.5 - 0.5 * math.cos(math.pi * p)
            return x0 + (x1 - x0) * p
    return keys[-1][1]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(words, f, maxw, d):
    lines, cur = [], []
    for w in words:
        test = ' '.join(cur + [w])
        if cur and d.textlength(test, font=f) > maxw:
            lines.append(cur); cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def caption_layer(t_abs):
    """Lower-third caption for whatever line is being spoken at film time t_abs."""
    lay = Image.new('RGBA', (OW, OH), (0, 0, 0, 0))
    cands = [l for l in tl['lines'] if l['start'] - 0.05 <= t_abs <= l['start'] + l['dur'] + 0.35
             and not l.get('nosub')]
    ln = max(cands, key=lambda l: l['start']) if cands else None      # newest line wins
    if not ln:
        return lay
    words = ln['text'].split()
    wt = WT.get(str(ln['idx'])) or WT.get(ln['idx'])
    starts = [w[1] for w in wt] if wt and len(wt) == len(words) else \
        [ln['start'] + ln['dur'] * i / max(1, len(words)) for i in range(len(words))]
    d = ImageDraw.Draw(lay); f = font(F_BOLD, 66)
    rows = wrap(words, f, 940, d)[:3]
    y = 1250 - (len(rows) - 1) * 40
    sp = ln['speaker']
    if sp in TAG:                                       # coloured name tag for characters
        name, col = TAG[sp]; ft = font(F_BOLD, 40); tw = d.textlength(name, font=ft)
        d.rounded_rectangle([OW / 2 - tw / 2 - 22, y - 74, OW / 2 + tw / 2 + 22, y - 18], 26, fill=col + (255,))
        d.text((OW / 2 - tw / 2, y - 70), name, font=ft, fill=(255, 255, 255, 255))
    k = 0
    for row in rows:
        line = ' '.join(row); x = OW / 2 - d.textlength(line, font=f) / 2
        for w in row:
            col = YELLOW if starts[k] <= t_abs else (255, 255, 255)
            d.text((x, y), w, font=f, fill=col + (255,), stroke_width=7, stroke_fill=(15, 12, 25, 255))
            x += d.textlength(w + ' ', font=f); k += 1
        y += 84
    return lay


def hook_layer(lines):
    lay = Image.new('RGBA', (OW, OH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i, (s, size, col) in enumerate(((lines[0], 96, GOLD), (lines[1], 96, CREAM))):
        f = font(F_HOOK, size); w = d.textlength(s, font=f)
        d.text(((OW - w) / 2, 250 + i * 110), s, font=f, fill=col + (255,), stroke_width=6, stroke_fill=(10, 10, 25, 255))
    return lay


def end_layer():
    lay = Image.new('RGBA', (OW, OH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    lg = Image.open('brand/moonlit_tales_logo_white_600.png').convert('RGBA').resize((300, 300), Image.LANCZOS)
    lay.alpha_composite(lg, ((OW - 300) // 2, 640))
    for i, (s, size, col) in enumerate((('Watch the full story', 92, CREAM), ('on Moonlit Tales', 110, GOLD))):
        f = font(F_HOOK, size); w = d.textlength(s, font=f)
        d.text(((OW - w) / 2, 990 + i * 120), s, font=f, fill=col + (255,), stroke_width=6, stroke_fill=(10, 10, 25, 255))
    return lay


def comp(frame, lay, alpha=1.0):
    a = np.asarray(lay).astype(np.float32); al = a[..., 3:4] / 255.0 * alpha
    return frame * (1 - al) + a[..., :3] * al


def make(n):
    S = SHORTS[n]
    cap = cv2.VideoCapture(S['clean']); total = int(S['length'] * FPS)
    hook = hook_layer(S['hook']); end = end_layer(); END = 2.2
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}',
                            '-r', str(FPS), '-i', '-', '-ss', f"{S['start']:.3f}", '-t', f"{S['length']:.3f}",
                            '-i', 'assets/mix.wav', '-map', '0:v', '-map', '1:a',
                            '-af', f"afade=t=in:st=0:d=0.4,afade=t=out:st={S['length'] - 1.0:.2f}:d=1.0",
                            '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p',
                            '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', S['out']],
                           stdin=subprocess.PIPE)
    for i in range(total):
        ok, fr = cap.read()
        if not ok:
            break
        t = i / FPS; t_abs = S['start'] + t
        fr = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB); h, w = fr.shape[:2]
        cw = int(h * OW / OH)                                       # 9:16 crop of the full height
        c = cx_at(S['keys'], t) * w
        x0 = int(max(0, min(w - cw, c - cw / 2)))
        v = cv2.resize(fr[:, x0:x0 + cw], (OW, OH), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
        if t < S['length'] - END:
            v = comp(v, caption_layer(t_abs))
        if t < 4.0:
            v = comp(v, hook, min(1.0, t / 0.3) * min(1.0, (4.0 - t) / 0.6))
        if t > S['length'] - END:
            k = min(1.0, (t - (S['length'] - END)) / 0.5)
            v = v * (1 - 0.55 * k)
            v = comp(v, end, k)
        enc.stdin.write(np.clip(v, 0, 255).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait()
    print('wrote', S['out'])


for a in sys.argv[1:]:
    make(int(a))
