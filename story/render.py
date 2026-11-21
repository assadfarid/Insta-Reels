"""Render the video frames for "The Robot That Learned to Lie".

usage: python3 render.py <part> <nparts> [--fast]
Writes out/part_<part>.mp4 (video only). Frames are split into equal ranges.
"""
import json, sys, math, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from effects import SceneFX
from captions import Captions

W, H, FPS = 1920, 1080, 24
XF = 0.9  # crossfade seconds
tl = json.load(open('timeline.json'))
part, nparts = int(sys.argv[1]), int(sys.argv[2])
FAST = '--fast' in sys.argv
if FAST:
    W, H = 960, 540

FONT_DIR = 'assets/fonts/'
F_TITLE = FONT_DIR + 'cormorant-garamond-latin-600-normal.woff'
F_ITAL = FONT_DIR + 'cormorant-garamond-latin-500-italic.woff'
F_HAND = FONT_DIR + 'caveat-latin-600-normal.woff'
F_MONO = '/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf'
S = W / 1920

_img_cache = {}


def src_img(name):
    if name not in _img_cache:
        if len(_img_cache) > 6:
            _img_cache.pop(next(iter(_img_cache)))
        im = cv2.imread(f'assets/img/{name}.png', cv2.IMREAD_COLOR)
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        if FAST:
            im = cv2.resize(im, (im.shape[1] // 2, im.shape[0] // 2), interpolation=cv2.INTER_AREA)
        _img_cache[name] = im
    return _img_cache[name]


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def kenburns(shot, t):
    im = src_img(shot['img'])
    M = camera_M(shot, t)
    return cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT), M


exec(open('script.py').read())
_KEY_TXT = ["Yes, Mia. [pause] Tomorrow.", "You lied to me!", "I hate you.", "You're my family too.",
            "[whispers] I promise.", "Echo? [shouting] Echo!", "You remember me?",
            "I remember... that you prefer your toast unburned.", "Promise me you'll be okay."]
KEY_PUSH = []   # (scene, start, dur)
for _ln in tl['lines']:
    _sc, _sp, _tx, _h = LINES[_ln['idx']]
    if any(k in _tx for k in _KEY_TXT):
        KEY_PUSH.append((_sc, _ln['start'], _ln['dur']))
SHAKE = [(_ln['start'] + _ln['dur'] * 0.72, LINES[_ln['idx']][0]) for _ln in tl['lines']
         if 'collapses onto the bridge' in LINES[_ln['idx']][2]]


import os as _os
CLIP_SPEED = {'s37': None, 's07': 0.85, 's39': 0.6, 's03': 'h', 's22': 'h', 's30': 'h', 's32': 'h', 's47': 'h', 's55': 'h', 's10': 'h', 's14': 'h', 's43': 'h', 's51': 'h', 's29': 'h', 's06': 'h', 's45': 'h'}      # None = stretch to fill the whole shot
import re as _re
_WT = json.load(open('word_times.json'))


def _norm(w):
    return _re.sub(r"[^a-z0-9']", '', w.lower())


def phrase_time(phrase):
    """Time the narrator (or a character) starts saying `phrase`."""
    ph = [_norm(w) for w in phrase.split()]
    for l in tl['lines']:
        if phrase.lower() in l['text'].lower():
            ws = _WT.get(str(l['idx']))
            if ws:
                nw = [_norm(w[0]) for w in ws]
                for k in range(len(nw) - len(ph) + 1):
                    if nw[k:k + len(ph)] == ph:
                        return ws[k][1]
            return l['start']
    raise KeyError(phrase)


# (phrase in the narration, second inside the clip where that action happens)
SYNC = {
    's03': ('slowly opens her eyes', 0.3),
    's06': ('proudly places a plate', 2.6),
    's07': ('You burned it again', 0.2),
    's10': ('draws a crayon picture', 0.3),
    's14': ('Echo rushes into the corridor', 2.4),
    's22': ('Startled, Mia knocks', 0.2),
    's29': ('warm golden sunlight floods', 5.3),
    's30': ('step out into a breathtaking', 0.3),
    's32': ('lands on Mia', 0.3),
    's37': ('he collapses onto the bridge', 0.0),
    's39': ('Mia holds out her hand', 0.6),
    's43': ('Blue lights glow', 2.4),
    's45': ('Mia takes his hand', 0.2),
    's47': ('slowly dim to black', 4.6),
    's51': ('cyan eyes light up', 1.5),
    's55': ('runs to him', 0.3),
}
CLIPS = {}
for _s in tl['shots']:
    _n = _s.get('img')
    if _s['kind'] == 'img' and _n in CLIP_SPEED and _os.path.exists(f'assets/clips/{_n}.mp4') and _n not in CLIPS:
        _cdur = {'s39': 5.0, 's45': 1.55, 's06': 10.0}.get(_n, (7.93 if _n in ('s10','s14','s43','s51','s29') else 7.85) if CLIP_SPEED[_n] == 'h' else 10.0)
        _span = _s['end'] - _s['start'] + XF
        _sp = (0.4 if _n == 's45' else max(0.6, min(1.0, _cdur / _span))) if CLIP_SPEED[_n] == 'h' else (CLIP_SPEED[_n] or min(1.0, _cdur / _span))
        if _n == 's37':
            _sp = 0.85
        _ph, _act = SYNC.get(_n, (None, 0.0))
        _st = (phrase_time(_ph) - _act / _sp) if _ph else _s['start']
        CLIPS[_n] = {'start': _st, 'speed': _sp, 'end': _st + _cdur / _sp - 0.05, 'shot_start': _s['start'],
                     'fill': False, 'hold': True, 'pre': 'still' if _n == 's37' else 'first'}


class _ClipReader:
    def __init__(self, path):
        self.path = path; self.cap = cv2.VideoCapture(path); self.idx = -1; self.frame = None
        self.n = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def get(self, i):
        i = max(0, min(self.n - 1, i))
        if i < self.idx:
            self.cap.release(); self.cap = cv2.VideoCapture(self.path); self.idx = -1
        while self.idx < i:
            ok, fr = self.cap.read()
            if not ok:
                break
            self.idx += 1; self.frame = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
        return self.frame


_readers = {}


_cmatch = {}
CM_STRENGTH = 0.75


def _lab_stats(img):
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB).astype(np.float32)
    return lab.reshape(-1, 3).mean(0), lab.reshape(-1, 3).std(0) + 1e-3


def color_match(name, fr):
    """Pull the AI clip's colour, contrast and light toward the watercolour illustration so the
    clip sits in the same look as the still pictures around it."""
    if name not in _cmatch:
        ref = cv2.resize(src_img(name), (fr.shape[1], fr.shape[0]), interpolation=cv2.INTER_AREA)
        rd = _ClipReader(f'assets/clips/{name}.mp4')
        smp = [rd.get(k) for k in range(0, rd.n, max(1, rd.n // 6))]
        ms = [_lab_stats(f) for f in smp if f is not None]
        cm = np.mean([m for m, _ in ms], 0); cs = np.mean([v for _, v in ms], 0)
        rm, rs = _lab_stats(ref)
        _cmatch[name] = (cm, cs, rm, rs)
    cm, cs, rm, rs = _cmatch[name]
    lab = cv2.cvtColor(fr, cv2.COLOR_RGB2LAB).astype(np.float32)
    out = (lab - cm) * (rs / cs) + rm
    out = lab + (out - lab) * CM_STRENGTH
    return cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)


def clip_frame(name, t, M):
    c = CLIPS[name]
    if name not in _readers:
        _readers[name] = _ClipReader(f'assets/clips/{name}.mp4')
    rd = _readers[name]
    fr = color_match(name, rd.get(max(0, int((t - c['start']) * c['speed'] * 24))))
    ih, iw = src_img(name).shape[:2]
    fh, fw = fr.shape[:2]
    Mv = (np.vstack([M, [0, 0, 1]]) @ np.diag([iw / fw, ih / fh, 1.0]))[:2].astype(np.float32)
    return cv2.warpAffine(fr, Mv, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def camera_M(shot, t):
    if shot.get('img') in CLIPS:
        t = max(t, CLIPS[shot['img']]['end'])      # camera holds still while the video plays
    ih, iw = src_img(shot['img']).shape[:2]
    m = shot['motion']
    p = ease((t - shot['start']) / max(0.01, shot['end'] - shot['start']))
    z = m['z0'] + (m['z1'] - m['z0']) * p + 0.05   # headroom for handheld float
    for sc_, st_, du_ in KEY_PUSH:                  # slow push-in on emotional lines
        if sc_ == shot['img'] and t > st_ - 0.3:
            z *= 1 + 0.08 * ease((t - st_ + 0.3) / (du_ + 1.2))
    cw = iw / z
    ch = cw * H / W
    if ch > ih:
        ch = ih / z; cw = ch * W / H
    cx = iw / 2 + m['dx'] * iw * (p - 0.5)
    cy = ih / 2 + m['dy'] * ih * (p - 0.5)
    # gentle handheld float (two slow sines per axis, phase per shot)
    ph = (int(shot['img'][1:]) * 37 % 100) / 10.0
    cx += iw * 0.006 * (math.sin(t * 0.37 + ph) + 0.5 * math.sin(t * 0.83 + ph * 2))
    cy += ih * 0.006 * (math.sin(t * 0.29 + ph * 1.3) + 0.5 * math.sin(t * 0.71 + ph))
    rot = 0.25 * math.sin(t * 0.21 + ph)
    for st_, sc_ in SHAKE:                          # impact shake when Echo collapses
        if sc_ == shot['img'] and 0 <= t - st_ < 0.7:
            k_ = (1 - (t - st_) / 0.7) ** 2
            cx += iw * 0.006 * k_ * math.sin((t - st_) * 55)
            cy += ih * 0.008 * k_ * math.sin((t - st_) * 47 + 1)
    cx = min(max(cx, cw / 2), iw - cw / 2)
    cy = min(max(cy, ch / 2), ih - ch / 2)
    sc = W / cw
    M = np.array([[sc, 0, -(cx - cw / 2) * sc], [0, sc, -(cy - ch / 2) * sc]], np.float32)
    R = cv2.getRotationMatrix2D((W / 2, H / 2), rot, 1.0)
    M = (np.vstack([R, [0, 0, 1]]) @ np.vstack([M, [0, 0, 1]]))[:2].astype(np.float32)
    return M


def scene_M(scene, t):
    for s in tl['shots']:
        if s.get('img') == scene and s['kind'] == 'img' and s['start'] - 1 <= t <= s['end'] + 1:
            ih, iw = src_img(scene).shape[:2]
            return camera_M(s, t), iw, ih
    return None


def centered(draw, y, text, font, fill, shadow=True):
    w = draw.textlength(text, font=font)
    x = (W - w) / 2
    if shadow:
        draw.text((x + 2 * S, y + 3 * S), text, font=font, fill=(0, 0, 0, 150))
    draw.text((x, y), text, font=font, fill=fill)


_title_cache = {}


def first_img_of_chapter(c):
    for s in tl['shots']:
        if s['kind'] == 'img' and s['chapter'] == c:
            return s['img']


def title_frame(shot):
    key = (shot['kind'], shot['chapter'])
    if key in _title_cache:
        return _title_cache[key]
    bgname = {'main': 's01', 'end': 's55'}.get(shot['kind']) or first_img_of_chapter(shot['chapter'])
    bg = Image.fromarray(cv2.resize(src_img(bgname), (W, H), interpolation=cv2.INTER_AREA))
    bg = bg.filter(ImageFilter.GaussianBlur(14 * S))
    arr = np.asarray(bg).astype(np.float32) * 0.42
    # warm paper tint
    arr = arr * np.array([1.0, 0.95, 0.88]) + np.array([14, 10, 6])
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    over = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    if shot['kind'] == 'end':
        f2 = ImageFont.truetype('assets/fonts/fredoka-latin-600-normal.woff', int(150 * S))
        f1 = ImageFont.truetype('assets/fonts/fredoka-latin-500-normal.woff', int(46 * S))
        centered(d, H * 0.38, 'The End', f2, (248, 240, 225, 255))
        d.line([(W * 0.44, H * 0.60), (W * 0.56, H * 0.60)], fill=(160, 232, 242, 220), width=max(1, int(2 * S)))
        centered(d, H * 0.64, 'The Robot That Learned to Lie', f1, (160, 232, 242, 255))
    elif shot['kind'] == 'main':
        f1 = ImageFont.truetype(F_HAND, int(54 * S))
        f2 = ImageFont.truetype(F_TITLE, int(120 * S))
        centered(d, H * 0.30, 'a short story', f1, (150, 225, 235, 255))
        centered(d, H * 0.38, 'The Robot That', f2, (246, 238, 222, 255))
        centered(d, H * 0.52, 'Learned to Lie', f2, (246, 238, 222, 255))
        # thin rule
        d.line([(W * 0.42, H * 0.70), (W * 0.58, H * 0.70)], fill=(150, 225, 235, 200), width=max(1, int(2 * S)))
    else:
        num, name = shot['title']
        f1 = ImageFont.truetype(F_HAND, int(62 * S))
        f2 = ImageFont.truetype(F_TITLE, int(104 * S))
        centered(d, H * 0.36, num, f1, (150, 225, 235, 255))
        centered(d, H * 0.45, name, f2, (246, 238, 222, 255))
        d.line([(W * 0.44, H * 0.62), (W * 0.56, H * 0.62)], fill=(150, 225, 235, 200), width=max(1, int(2 * S)))
    img = Image.alpha_composite(img, over).convert('RGB')
    _title_cache[key] = np.asarray(img).astype(np.float32)
    return _title_cache[key]


_hud_cache = {}


def hud_layer(text, t_in):
    """RGBA overlay with an Echo-style diagnostic readout; typed on over 0.6s."""
    nchars = len(text)
    shown = min(nchars, int(nchars * min(1.0, t_in / 0.6)) + 1)
    blink = int(t_in * 2.5) % 2 == 0
    key = (text, shown, blink)
    if key in _hud_cache:
        return _hud_cache[key]
    font = ImageFont.truetype(F_MONO, int(30 * S))
    lines = text.split('\n')
    pad = int(26 * S)
    lh = int(44 * S)
    tw = max(ImageDraw.Draw(Image.new('RGB', (1, 1))).textlength(l, font=font) for l in lines)
    bw, bh = int(tw + pad * 2 + 40 * S), int(lh * len(lines) + pad * 2 + 30 * S)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, y0 = int(70 * S), int(64 * S)
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=int(10 * S), fill=(4, 18, 24, 175),
                        outline=(90, 230, 245, 200), width=max(1, int(2 * S)))
    small = ImageFont.truetype(F_MONO, int(18 * S))
    d.text((x0 + pad, y0 + int(10 * S)), 'ECHO-07 // DIAGNOSTIC', font=small, fill=(90, 230, 245, 170))
    remaining = shown
    for k, l in enumerate(lines):
        seg = l[:max(0, remaining)]
        remaining -= len(l) + 1
        col = (255, 110, 100, 255) if any(w in l for w in ('CRITICAL', 'WARNING', 'FAILURE', '0%', '1%', '2%', '5%')) else (120, 240, 250, 255)
        y = y0 + pad + int(22 * S) + k * lh
        d.text((x0 + pad, y), seg, font=font, fill=col)
        if 0 <= remaining + len(l) + 1 <= len(l) and blink:
            cx = x0 + pad + d.textlength(seg, font=font) + 4
            d.rectangle([cx, y + 4 * S, cx + 14 * S, y + 34 * S], fill=(120, 240, 250, 220))
    glow = lay.filter(ImageFilter.GaussianBlur(6 * S))
    out = Image.alpha_composite(glow, lay)
    a = np.asarray(out).astype(np.float32)
    _hud_cache[key] = a
    if len(_hud_cache) > 400:
        _hud_cache.clear()
    return a


# vignette + grain
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIG = (1.0 - 0.28 * np.clip(r - 0.55, 0, 1) ** 1.5)[..., None].astype(np.float32)
rng = np.random.default_rng(part)
GRAIN = [(rng.standard_normal((H // 2, W // 2, 1)) * 2.5).astype(np.float32) for _ in range(6)]


_fx = {}
CUR_M = {}
CAP = None


def shot_frame(shot, t):
    if shot['kind'] in ('main', 'title', 'end'):
        base = title_frame(shot)
        # slow drift so titles aren't static
        return base
    name = shot['img']
    ih, iw = src_img(name).shape[:2]
    if name in CLIPS:
        c = CLIPS[name]
        M = camera_M(shot, t)
        CUR_M[name] = (M, iw, ih)
        if t >= c['start'] or c['pre'] == 'first':
            vid = clip_frame(name, min(max(t, c['start']), c['end']), M).astype(np.float32)
            if c['pre'] == 'still' and t < c['start'] + 0.4:
                a = ease((t - c['start']) / 0.4)
                fr, M2 = kenburns(shot, t)
                if name not in _fx:
                    _fx[name] = SceneFX(name, src_img(name), W, H)
                still = _fx[name].apply(fr.astype(np.float32), M2, t, t - shot['start'], shot['end'] - shot['start'])
                return vid * a + still * (1 - a)
            return vid
    fr, M = kenburns(shot, t)
    fr = fr.astype(np.float32)
    CUR_M[name] = (M, iw, ih)
    if name not in _fx:
        _fx[name] = SceneFX(name, src_img(name), W, H)
    return _fx[name].apply(fr, M, t, t - shot['start'], shot['end'] - shot['start'])


_chap_cache = {}


def chapter_layer(title):
    if title in _chap_cache:
        return _chap_cache[title]
    num, name = title
    f1 = ImageFont.truetype('assets/fonts/fredoka-latin-500-normal.woff', int(52 * S))
    f2 = ImageFont.truetype('assets/fonts/fredoka-latin-600-normal.woff', int(100 * S))
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    # soft dark glow behind the text for legibility
    glow = Image.new('L', (W, H), 0)
    ImageDraw.Draw(glow).ellipse([W * 0.22, H * 0.30, W * 0.78, H * 0.66], fill=150)
    glow = glow.filter(ImageFilter.GaussianBlur(70 * S))
    lay.putalpha(glow)
    d = ImageDraw.Draw(lay)
    centered(d, H * 0.36, num, f1, (160, 232, 242, 255))
    centered(d, H * 0.43, name, f2, (248, 240, 225, 255))
    d.line([(W * 0.45, H * 0.585), (W * 0.55, H * 0.585)], fill=(160, 232, 242, 220), width=max(1, int(2 * S)))
    _chap_cache[title] = np.asarray(lay).astype(np.float32)
    return _chap_cache[title]


def frame_at(t):
    global CAP
    if CAP is None:
        CAP = Captions(tl, W, H)
    CUR_M.clear()
    active = [s for s in tl['shots'] if s['start'] - 1e-6 <= t < s['end'] + XF]
    out = np.zeros((H, W, 3), np.float32)
    for s in active:
        a_in = ease((t - s['start']) / XF)
        a_out = 1.0 - ease((t - s['end']) / XF) if t > s['end'] else 1.0
        a = a_in * a_out
        if a <= 0:
            continue
        fr = shot_frame(s, t)
        out = out * (1 - a) + fr * a if out.any() else fr * a
    # HUD overlays
    for h in tl['huds']:
        if h['start'] <= t < h['end'] + 0.4:
            lay = hud_layer(h['text'], t - h['start'])
            fade = min(ease((t - h['start']) / 0.25), 1 - ease((t - h['end']) / 0.4))
            al = lay[..., 3:4] / 255.0 * fade
            out = out * (1 - al) + lay[..., :3] * al
    # chapter title overlays
    for c in tl.get('chapters', []):
        if c['start'] - 0.1 <= t < c['end'] + 0.6:
            fade = min(ease((t - c['start']) / 0.5), 1 - ease((t - c['end']) / 0.6))
            lay = chapter_layer(tuple(c['title']))
            al = lay[..., 3:4] / 255.0 * fade
            out = out * (1 - al) + lay[..., :3] * al
    # global fade in/out
    g = min(ease(t / 1.5), 1 - ease((t - (tl['total'] - 3.0)) / 3.0))
    out *= VIG * g
    gr = GRAIN[int(t * FPS) % len(GRAIN)]
    out += cv2.resize(gr, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    hud_on = any(h['start'] <= t < h['end'] + 0.4 for h in tl['huds'])
    CAP.draw(out, t, CUR_M, hud_on, scene_M)
    return np.clip(out, 0, 255).astype(np.uint8)


if '--stills' in sys.argv:
    ts = [float(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(',')]
    for tt in ts:
        Image.fromarray(frame_at(tt)).save(f'test/still_{tt:07.2f}.jpg', quality=88)
    sys.exit(0)

total_frames = int(tl['total'] * FPS)
per = math.ceil(total_frames / nparts)
f0, f1 = part * per, min(total_frames, (part + 1) * per)
if '--clip' in sys.argv:
    a, b = [float(x) for x in sys.argv[sys.argv.index('--clip') + 1].split(',')]
    f0, f1 = int(a * FPS), int(b * FPS)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                        '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast' if FAST else 'fast',
                        '-crf', '19', '-pix_fmt', 'yuv420p', '-threads', '2', '-g', str(FPS * 4),
                        f'out/part_{part}.mp4'], stdin=subprocess.PIPE)
for f in range(f0, f1):
    enc.stdin.write(frame_at(f / FPS).tobytes())
    if (f - f0) % 240 == 0:
        print(f'part {part}: {f - f0}/{f1 - f0}', flush=True)
enc.stdin.close()
enc.wait()
print(f'part {part} done')
