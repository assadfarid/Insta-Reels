"""Burned-in captions: narrator subtitles (bottom) and character speech bubbles.

Inter Bold with tight tracking. Bubbles anchor to the speaker's head (anchors.json,
normalised source-image coords) and follow the camera move via the shot's affine M.
"""
import json, re, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

INTER = 'assets/fonts/inter-latin-700-normal.woff'
KIDS = 'assets/fonts/fredoka-latin-600-normal.woff'
exec(open('script.py').read())  # LINES
ANCH = json.load(open('anchors.json'))


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def chunk(text, maxc):
    """Split into display chunks at sentence breaks, each <= maxc chars when possible."""
    parts = re.split(r'(?<=[.!?…])\s+', text.strip())
    out, cur = [], ''
    for p in parts:
        if not cur:
            cur = p
        elif len(cur) + 1 + len(p) <= maxc:
            cur += ' ' + p
        else:
            out.append(cur); cur = p
    if cur:
        out.append(cur)
    res = []
    for c in out:  # very long single sentence: split at commas/words
        while len(c) > maxc * 1.25:
            cut = c.rfind(', ', 0, maxc)
            cut = cut + 1 if cut > maxc * 0.4 else c.rfind(' ', 0, maxc)
            res.append(c[:cut].strip()); c = c[cut:].strip()
        res.append(c)
    return res


def wrap(text, font, maxw, track):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if tw(t, font, track) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines


def tw(text, font, track):
    return font.getlength(text) + track * max(0, len(text) - 1)


def draw_tracked(d, xy, text, font, fill, track):
    x, y = xy
    for i, ch in enumerate(text):
        d.text((x + font.getlength(text[:i]) + track * i, y), ch, font=font, fill=fill)


class Captions:
    def __init__(self, tl, W, H):
        self.W, self.H = W, H
        self.S = S = W / 1920
        self.f_sub = ImageFont.truetype(KIDS, int(48 * S))
        self.f_bub = ImageFont.truetype(KIDS, int(39 * S))
        self.track_sub = -0.8 * S   # tight letter spacing
        self.track_bub = -0.6 * S
        self.items = []
        WT = json.load(open('word_times.json'))
        for ln in tl['lines']:
            scene = LINES[ln['idx']][0]
            sp = ln['speaker']
            if sp == 'N' and str(ln['idx']) in WT:
                words = WT[str(ln['idx'])]
                k = 0
                for c in chunk(ln['text'], 84):
                    n = len(c.split())
                    ws = words[k:k + n]; k += n
                    self.items.append({'sp': 'N', 'scene': scene, 'text': c, 'words': ws,
                                       'a': ws[0][1] - 0.12, 'b': ws[-1][2] + 0.35})
                continue
            maxc = 84 if sp == 'N' else 54
            chunks = chunk(ln['text'], maxc)
            total = ln['dur'] + 0.35
            L = sum(len(c) for c in chunks)
            t = ln['start'] - 0.05
            for c in chunks:
                d = total * len(c) / L
                self.items.append({'sp': sp, 'scene': scene, 'text': c, 'a': t, 'b': t + d})
                t += d
        self._cache = {}

    # ---------------- rendering of individual elements (cached RGBA) ----------
    def _subtitle(self, text):
        key = ('sub2', text)
        if key in self._cache:
            return self._cache[key]
        S, f, tr = self.S, self.f_sub, self.track_sub
        lines = wrap(text, f, 1500 * S, tr)
        lh = int(58 * S)
        w = int(max(tw(l, f, tr) for l in lines) + 80 * S)
        h = int(lh * len(lines) + 40 * S)
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ds = ImageDraw.Draw(sh)
        spans = []
        for i, l in enumerate(lines):
            x = (w - tw(l, f, tr)) / 2
            y = 18 * S + i * lh
            draw_tracked(ds, (x, y + 2 * S), l, f, (0, 0, 0, 255), tr)
            pos = 0
            for wd in l.split(' '):
                j = l.index(wd, pos)
                x0 = x + f.getlength(l[:j]) + tr * j
                x1 = x + f.getlength(l[:j + len(wd)]) + tr * (j + len(wd))
                spans.append((int(y - 4 * S), int(y + lh), x0, x1))
                pos = j + len(wd)
        sh = sh.filter(ImageFilter.GaussianBlur(5 * S))
        base = Image.alpha_composite(Image.new('RGBA', (w, h), (0, 0, 0, 0)), sh)
        base = Image.alpha_composite(base, sh)
        white, green = base.copy(), base.copy()
        dw, dg = ImageDraw.Draw(white), ImageDraw.Draw(green)
        for i, l in enumerate(lines):
            x = (w - tw(l, f, tr)) / 2
            y = 18 * S + i * lh
            draw_tracked(dw, (x, y), l, f, (255, 252, 245, 255), tr)
            draw_tracked(dg, (x, y), l, f, (120, 232, 92, 255), tr)
        res = (np.asarray(white).astype(np.float32), np.asarray(green).astype(np.float32), spans)
        self._cache[key] = res
        return res

    def _subtitle_old(self, text):
        key = ('sub', text)
        if key in self._cache:
            return self._cache[key]
        S, f, tr = self.S, self.f_sub, self.track_sub
        lines = wrap(text, f, 1500 * S, tr)
        lh = int(56 * S)
        w = int(max(tw(l, f, tr) for l in lines) + 80 * S)
        h = int(lh * len(lines) + 40 * S)
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        ds = ImageDraw.Draw(sh)
        for i, l in enumerate(lines):
            x = (w - tw(l, f, tr)) / 2
            y = 18 * S + i * lh
            draw_tracked(ds, (x, y + 2 * S), l, f, (0, 0, 0, 255), tr)
        sh = sh.filter(ImageFilter.GaussianBlur(5 * S))
        sh = Image.eval(sh, lambda v: v)  # keep
        im = Image.alpha_composite(im, sh)
        im = Image.alpha_composite(im, sh)  # stronger soft shadow
        d = ImageDraw.Draw(im)
        for i, l in enumerate(lines):
            x = (w - tw(l, f, tr)) / 2
            y = 18 * S + i * lh
            draw_tracked(d, (x, y), l, f, (255, 252, 245, 255), tr)
        arr = np.asarray(im).astype(np.float32)
        self._cache[key] = arr
        return arr

    STYLE = {
        'MIA': dict(fill=(255, 250, 240), edge=(225, 120, 95), text=(45, 32, 28)),
        'ECHO': dict(fill=(240, 252, 255), edge=(70, 205, 230), text=(18, 40, 52)),
        'ELENA': dict(fill=(225, 240, 255), edge=(120, 175, 255), text=(20, 35, 70)),
        'OP': dict(fill=(30, 36, 44), edge=(150, 230, 245), text=(215, 245, 250)),
        'TECH': dict(fill=(255, 248, 235), edge=(185, 145, 95), text=(50, 38, 25)),
    }

    def _bubble(self, text, sp):
        key = ('bub', text, sp)
        if key in self._cache:
            return self._cache[key]
        S, f, tr = self.S, self.f_bub, self.track_bub
        st = self.STYLE[sp]
        lines = wrap(text, f, 560 * S, tr)
        lh = int(48 * S)
        padx, pady = int(30 * S), int(20 * S)
        bw = int(max(tw(l, f, tr) for l in lines) + 2 * padx)
        bh = int(lh * len(lines) + 2 * pady - 4 * S)
        m = int(16 * S)  # margin for shadow
        im = Image.new('RGBA', (bw + 2 * m, bh + 2 * m), (0, 0, 0, 0))
        shadow = Image.new('RGBA', im.size, (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle([m, m + 4 * S, m + bw, m + bh + 4 * S], radius=int(26 * S),
                                                 fill=(0, 0, 0, 90))
        im = Image.alpha_composite(im, shadow.filter(ImageFilter.GaussianBlur(7 * S)))
        d = ImageDraw.Draw(im)
        rad = int(10 * S) if sp in ('OP', 'ELENA') else int(26 * S)
        d.rounded_rectangle([m, m, m + bw, m + bh], radius=rad, fill=st['fill'] + (246,),
                            outline=st['edge'] + (255,), width=max(2, int(3 * S)))
        for i, l in enumerate(lines):
            draw_tracked(d, (m + padx, m + pady + i * lh - 3 * S), l, f, st['text'] + (255,), tr)
        arr = np.asarray(im).astype(np.float32)
        self._cache[key] = (arr, m, bw, bh)
        if len(self._cache) > 300:
            self._cache.clear()
        return self._cache[key]

    # ---------------- compositing ----------------
    @staticmethod
    def _blend(out, lay, x, y, alpha):
        H, W = out.shape[:2]
        h, w = lay.shape[:2]
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + w), min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        sub = lay[y0 - y:y1 - y, x0 - x:x1 - x]
        a = sub[..., 3:4] / 255.0 * alpha
        out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - a) + sub[..., :3] * a

    def _tail(self, out, bx, by, bw, bh, hx, hy, sp, alpha, below):
        """Draw a small triangular tail from the bubble edge toward (hx, hy)."""
        st = self.STYLE[sp]
        S = self.S
        cx = min(max(hx, bx + 40 * S), bx + bw - 40 * S)
        ey = by + bh if not below else by
        dist = math.hypot(hx - cx, hy - ey)
        L = min(48 * S, max(18 * S, dist * 0.6))
        ux, uy = (hx - cx) / (dist + 1e-6), (hy - ey) / (dist + 1e-6)
        tip = (cx + ux * L, ey + uy * L)
        half = 16 * S
        pts = [(cx - half, ey), (cx + half, ey), tip]
        x0 = int(min(p[0] for p in pts) - 6); y0 = int(min(p[1] for p in pts) - 6)
        x1 = int(max(p[0] for p in pts) + 6); y1 = int(max(p[1] for p in pts) + 6)
        im = Image.new('RGBA', (x1 - x0, y1 - y0), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        rel = [(p[0] - x0, p[1] - y0) for p in pts]
        d.polygon(rel, fill=st['fill'] + (246,))
        d.line([rel[0], rel[2], rel[1]], fill=st['edge'] + (255,), width=max(2, int(3 * S)))
        # cover the bubble border where the tail joins
        jy = (ey - y0) + (-2 * S if not below else 2 * S)
        d.line([(rel[0][0] + 3 * S, jy), (rel[1][0] - 3 * S, jy)], fill=st['fill'] + (255,), width=max(3, int(5 * S)))
        self._blend(out, np.asarray(im).astype(np.float32), x0, y0, alpha)

    def draw(self, out, t, shot_M, hud_active):
        """shot_M: dict scene -> (M, src_w, src_h) for currently visible image shots."""
        W, H, S = self.W, self.H, self.S
        for it in self.items:
            if not (it['a'] - 0.15 <= t < it['b'] + 0.2):
                continue
            fade = min(ease((t - it['a'] + 0.15) / 0.18), 1 - ease((t - it['b']) / 0.2))
            if fade <= 0:
                continue
            if it['sp'] == 'N':
                white, green, spans = self._subtitle(it['text'])
                lay = white.copy()
                for (y0, y1, x0, x1), (_, ta, tb) in zip(spans, it.get('words', [])):
                    if t <= ta:
                        break
                    frac = 1.0 if t >= tb else (t - ta) / max(0.05, tb - ta)
                    xa, xb = int(x0 - 2), int(x0 + (x1 - x0) * frac + (2 if frac >= 1 else 0))
                    lay[max(0, y0):y1, max(0, xa):xb] = green[max(0, y0):y1, max(0, xa):xb]
                h, w = lay.shape[:2]
                x = int((W - w) / 2)
                y = int(H - h - 46 * S + (1 - fade) * 8 * S)
                self._blend(out, lay, x, y, fade)
                continue
            key = f"{it['scene']}:{it['sp']}"
            if it['scene'] not in shot_M or key not in ANCH:
                continue
            M, sw, sh = shot_M[it['scene']]
            ax, ay = ANCH[key]
            hx, hy = M @ np.array([ax * sw, ay * sh, 1.0])
            arr, m, bw, bh = self._bubble(it['text'], it['sp'])
            gap = 70 * S
            below = False
            bx = hx - bw * 0.35 if hx < W / 2 else hx - bw * 0.65
            by = hy - gap - bh
            if by < 30 * S:                     # no room above: put it below the head
                by = hy + gap
                below = True
            bx = min(max(bx, 40 * S), W - bw - 40 * S)
            by = min(max(by, 30 * S), H - bh - 170 * S)
            if hud_active and bx < 760 * S and by < 260 * S:
                by = 270 * S
                below = by > hy
            by += (1 - fade) * 10 * S
            self._tail(out, bx, by, bw, bh, hx, hy, it['sp'], fade, below)
            self._blend(out, arr, int(bx - m), int(by - m), fade)
