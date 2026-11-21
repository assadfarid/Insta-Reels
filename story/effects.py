"""Per-scene 'living illustration' effects for render.py.

Everything is procedural and deterministic (seeded by scene), so parallel
render parts stay consistent.
"""
import math
import numpy as np
import cv2

# ---- which effects each scene gets --------------------------------------
RED = {'s01', 's02', 's03', 's04', 's05', 's14', 's18', 's24', 's26', 's27', 's28'}
DUST = {'s06', 's07', 's08', 's09', 's10', 's11', 's12', 's13', 's15', 's16', 's17', 's19', 's20',
        's22', 's23', 's25', 's41', 's42', 's50', 's51', 's52', 's53', 's54', 's55'}
POLLEN = {'s29', 's30', 's31', 's32', 's33', 's34', 's35', 's49'}
EMBERS = {'s36', 's37', 's38', 's39', 's40'}           # warm sunset motes
RAYS = {'s06', 's07', 's29', 's30', 's31', 's32', 's35', 's49', 's50', 's51', 's52', 's53', 's54', 's55'}
SPARKS = {'s19', 's22', 's23'}
HOLO = {'s21'}
SCREEN = {'s20', 's43', 's44', 's45', 's46'}
HEADLIGHTS = {'s48'}
ALARM = {'s14'}
EYES_FADE = {'s47'}
EYES_ON = {'s51'}


def _rng(name, salt=0):
    return np.random.default_rng(int(name[1:]) * 7919 + salt)


class SceneFX:
    """Holds per-scene precomputed data (masks, particle seeds)."""

    def __init__(self, name, src, W, H):
        self.name, self.W, self.H = name, W, H
        hsv = cv2.cvtColor(src, cv2.COLOR_RGB2HSV)
        m = cv2.inRange(hsv, (78, 90, 170), (100, 255, 255))
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        self.cyan = m
        n, lab, st, _ = cv2.connectedComponentsWithStats(m)
        blobs = [s for s in st[1:] if s[4] > 150]
        self.has_eyes = 0 < len(blobs) <= 5 and m.sum() / 255 < 20000
        self.screenish = (m.sum() / 255) >= 20000
        # bright warm spot (sparks / headlights source), in source coords
        v = hsv[..., 2].astype(np.float32)
        warm = ((hsv[..., 0] < 40) | (hsv[..., 0] > 160)) & (hsv[..., 1] < 140)
        score = cv2.GaussianBlur(v * warm, (0, 0), 25)
        y, x = np.unravel_index(np.argmax(score), score.shape)
        self.hot = (float(x), float(y))
        r = _rng(name)
        self.seed = r
        # particles in normalised screen space
        n = 70 if name in DUST else 90 if (name in POLLEN or name in EMBERS) else 0
        self.p = r.random((n, 2)).astype(np.float32)
        self.pv = (r.random((n, 2)).astype(np.float32) - 0.5) * 0.02
        self.ps = (0.6 + r.random(n) * 1.6).astype(np.float32)
        self.pph = (r.random(n) * 6.28).astype(np.float32)
        # blink schedule
        self.blinks = np.cumsum(r.uniform(2.5, 5.5, 20)).astype(np.float32)
        # sparks
        self.spark_bursts = np.cumsum(r.uniform(0.6, 1.8, 40)).astype(np.float32)

    # -------------------------------------------------------------------
    def apply(self, frame, M, t, local_t, dur):
        """frame: float32 HxWx3 (0..255). M: 2x3 affine used to map src->screen."""
        W, H, name = self.W, self.H, self.name
        hw, hh = W // 2, H // 2
        add = np.zeros((hh, hw, 3), np.float32)   # additive light layer at half res

        # --- Echo eyes / screens glow --------------------------------
        if self.cyan.any():
            mask = cv2.warpAffine(self.cyan, M, (W, H), flags=cv2.INTER_LINEAR).astype(np.float32) / 255.0
            pulse = 0.75 + 0.25 * math.sin(t * 2.1)
            level = 1.0
            if name in EYES_FADE:
                level = max(0.0, 1.0 - local_t / max(1.0, dur * 0.7))
            if name in EYES_ON:
                level = min(1.0, max(0.0, (local_t - 0.8) / 1.2))
            if self.has_eyes and name not in EYES_FADE and name not in EYES_ON:
                # screen-eyes blink: brief dim
                for b in self.blinks:
                    if 0 <= local_t - b < 0.18:
                        level = 0.15
                        break
            if level < 1.0:
                # darken the eyes themselves
                dark = mask[..., None] * (1 - level) * 0.85
                frame *= (1 - dark)
            glow = cv2.resize(mask, (hw, hh), interpolation=cv2.INTER_AREA)
            glow = cv2.GaussianBlur(glow, (0, 0), 9 if self.has_eyes else 14)
            amt = (60 if self.has_eyes else 35) * pulse * level * (1 + 1.3 * getattr(self, '_talk', 0.0))
            if name in SCREEN or name in HOLO:
                amt *= 0.8 + 0.4 * (0.5 + 0.5 * math.sin(t * 13) * math.sin(t * 7.3))
            add += glow[..., None] * np.array([40, 230, 255], np.float32) / 255 * amt

        # --- emergency red flicker -----------------------------------
        if name in RED:
            n = 0.5 + 0.5 * math.sin(t * 1.7) * math.sin(t * 5.3 + 1)
            flick = 1.0 if (int(t * 12) * 2654435761) % 97 > 6 else 0.82
            g = (0.9 + 0.1 * n) * flick
            frame *= np.array([1.0 * (0.94 + 0.08 * n) * flick, g, g], np.float32)
        if name in ALARM:
            a = max(0.0, math.sin(t * 6.0)) ** 3
            frame *= np.array([1 + 0.12 * a, 1 - 0.06 * a, 1 - 0.06 * a], np.float32)

        # --- screens / hologram flicker & scanlines ------------------
        if name in HOLO:
            sl = (np.sin((np.arange(H, dtype=np.float32) + t * 120) * 0.6) * 0.5 + 0.5)
            frame *= (0.93 + 0.07 * sl)[:, None, None]
            if (int(t * 8) * 40503) % 23 == 0:  # occasional glitch band
                y0 = int((t * 997) % (H - 60))
                frame[y0:y0 + 40] = np.roll(frame[y0:y0 + 40], 18, axis=1)
            frame *= 0.95 + 0.05 * math.sin(t * 31)

        # --- headlights sweep ----------------------------------------
        if name in HEADLIGHTS:
            hx, hy = M @ np.array([self.hot[0], self.hot[1], 1.0])
            strength = 0.6 + 0.4 * min(1.0, local_t / 3.0)
            yy, xx = np.mgrid[0:hh, 0:hw].astype(np.float32)
            d = np.sqrt((xx - hx / 2) ** 2 + (yy - hy / 2) ** 2)
            add += (np.exp(-d / 110.0) * 120 * strength)[..., None] * np.array([1.0, 0.97, 0.85], np.float32)
            streak = np.exp(-np.abs(yy - hy / 2) / 6.0) * np.exp(-np.abs(xx - hx / 2) / 400.0)
            add += (streak * 70 * strength)[..., None]

        # --- light rays ----------------------------------------------
        if name in RAYS:
            add += self._rays(t, hw, hh)

        # --- particles -----------------------------------------------
        if len(self.p):
            self._particles(add, t, hw, hh)

        # --- sparks --------------------------------------------------
        if name in SPARKS:
            self._sparks(add, M, local_t, hw, hh)

        if add.any():
            frame += cv2.resize(add, (W, H), interpolation=cv2.INTER_LINEAR)
        return frame

    # -------------------------------------------------------------------
    _ray_tex = {}

    def _rays(self, t, hw, hh):
        key = (hw, hh)
        if key not in self._ray_tex:
            r = np.random.default_rng(3)
            big = np.zeros((hh * 2, hw * 2), np.float32)
            for _ in range(9):
                x = r.uniform(0, hw * 2)
                w = r.uniform(10, 45)
                cv2.line(big, (int(x), 0), (int(x), hh * 2), float(r.uniform(0.4, 1.0)), int(w))
            big = cv2.GaussianBlur(big, (0, 0), 18)
            Mrot = cv2.getRotationMatrix2D((hw, hh), -28, 1.0)
            self._ray_tex[key] = cv2.warpAffine(big, Mrot, (hw * 2, hh * 2))
        tex = self._ray_tex[key]
        off = int((t * 6) % hw)
        crop = tex[hh // 2:hh // 2 + hh, off:off + hw]
        fade = np.linspace(1.0, 0.25, hh, dtype=np.float32)[:, None]
        breathe = 0.75 + 0.25 * math.sin(t * 0.7)
        return (crop * fade * 26 * breathe)[..., None] * np.array([1.0, 0.92, 0.7], np.float32)

    def _particles(self, add, t, hw, hh):
        name = self.name
        pos = (self.p + self.pv * t) % 1.0
        if name in POLLEN or name in EMBERS:
            pos[:, 1] = (self.p[:, 1] - 0.012 * t * self.ps) % 1.0  # drift upward
        sway = np.sin(t * 0.8 + self.pph) * 0.01
        xs = ((pos[:, 0] + sway) * hw).astype(np.int32)
        ys = (pos[:, 1] * hh).astype(np.int32)
        tw = 0.55 + 0.45 * np.sin(t * 1.3 + self.pph * 3)
        if name in EMBERS:
            col = np.array([255, 170, 90], np.float32)
        elif name in POLLEN:
            col = np.array([255, 245, 200], np.float32)
        else:
            col = np.array([235, 225, 205], np.float32)
        lay = np.zeros((hh, hw), np.float32)
        for x, y, s, b in zip(xs, ys, self.ps, tw):
            cv2.circle(lay, (int(x), int(y)), max(1, int(s * 1.4)), float(b), -1, cv2.LINE_AA)
        lay = cv2.GaussianBlur(lay, (0, 0), 1.6)
        strength = 55 if name in DUST else 85
        add += lay[..., None] * col / 255 * strength

    def _sparks(self, add, M, lt, hw, hh):
        sx, sy = M @ np.array([self.hot[0], self.hot[1], 1.0])
        sx, sy = sx / 2, sy / 2
        lay = np.zeros((hh, hw), np.float32)
        for bi, b in enumerate(self.spark_bursts):
            age = lt - b
            if not (0 <= age < 0.9):
                continue
            r = np.random.default_rng(int(b * 1000) + bi)
            n = 14
            ang = r.uniform(-math.pi, 0, n)
            spd = r.uniform(60, 220, n)
            for a, s in zip(ang, spd):
                x = sx + math.cos(a) * s * age
                y = sy + math.sin(a) * s * age + 160 * age * age
                x2 = x - math.cos(a) * 8
                y2 = y - math.sin(a) * 8 + 4
                cv2.line(lay, (int(x), int(y)), (int(x2), int(y2)), float(1 - age / 0.9), 2, cv2.LINE_AA)
        lay = cv2.GaussianBlur(lay, (0, 0), 1.2)
        add += lay[..., None] * np.array([255, 200, 110], np.float32) / 255 * 220


# =====================================================================
#  Environment motion: wind, water, waterfalls, clouds, scarf, smoke,
#  birds, butterfly, lamp flicker and hand-drawn "boiling" lines.
# =====================================================================
OUTDOOR = {'s29', 's30', 's31', 's32', 's33', 's34', 's35', 's36', 's37', 's38', 's39', 's40', 's49'}
FOLIAGE = {'s30', 's31', 's32', 's33', 's34', 's35', 's49', 's37', 's39'}
SKY = {'s30', 's33', 's34', 's36', 's37', 's38', 's39', 's40', 's49'}
SCARF = {'s30', 's31', 's32', 's33', 's34', 's35', 's36', 's37', 's38', 's39', 's40'}
BIRDS = {'s30': 4, 's34': 3, 's36': 3, 's49': 3, 's33': 2, 's40': 2}
# water boxes (x0, y0, x1, y1) in normalised source coords
WATER = {
    's30': [(0.36, 0.60, 0.62, 0.76)],
    's36': [(0.0, 0.40, 0.48, 0.62), (0.78, 0.55, 1.0, 0.95)],
    's39': [(0.0, 0.52, 0.30, 0.78), (0.70, 0.52, 1.0, 0.78)],
    's49': [(0.40, 0.55, 0.55, 0.62)],
}
FALLS = {
    's30': [(0.08, 0.60, 0.20, 0.78), (0.20, 0.76, 0.36, 1.0), (0.40, 0.76, 0.54, 1.0),
            (0.62, 0.40, 0.72, 0.60), (0.73, 0.46, 0.84, 0.64)],
    's49': [(0.44, 0.52, 0.53, 0.60)],
}
SMOKE = {'s06': [(0.14, 0.43), (0.43, 0.24)], 's07': [(0.70, 0.40)]}
LAMP = {'s06', 's09', 's41', 's42'}
BUTTERFLY = {'s32': (0.245, 0.38, 0.045)}


def _tile_noise(seed, size=256, sx=6.0, sy=6.0):
    r = np.random.default_rng(seed)
    n = r.standard_normal((size, size)).astype(np.float32)
    big = cv2.GaussianBlur(np.tile(n, (3, 3)), (0, 0), sigmaX=sx, sigmaY=sy)[size:2 * size, size:2 * size]
    return big / (np.abs(big).max() + 1e-6)


NZ = {k: _tile_noise(i + 11) for i, k in enumerate(('boil_a', 'boil_b', 'fol', 'water', 'sky', 'fall'))}
NZ['streak'] = _tile_noise(40, sx=1.2, sy=14)
NZ['spark'] = _tile_noise(41, sx=1.5, sy=1.5)
NZ['smoke'] = _tile_noise(42, sx=7, sy=7)


def _samp(n, X, Y):
    s = n.shape[0]
    return n[Y.astype(np.int32) % s, X.astype(np.int32) % s]


_grids = {}


def _grid(w, h):
    if (w, h) not in _grids:
        _grids[(w, h)] = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    return _grids[(w, h)]


def _box_mask(shape, boxes, feather):
    h, w = shape
    m = np.zeros((h, w), np.float32)
    for x0, y0, x1, y1 in boxes:
        m[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)] = 1
    return cv2.GaussianBlur(m, (0, 0), feather)


def _init_env(self, src):
    h, w = src.shape[:2]
    name = self.name
    hsv = cv2.cvtColor(src, cv2.COLOR_RGB2HSV)
    H_, S_, V_ = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    gray = cv2.cvtColor(src, cv2.COLOR_RGB2GRAY).astype(np.float32)
    grad = cv2.GaussianBlur(np.abs(cv2.Sobel(gray, cv2.CV_32F, 1, 0)) + np.abs(cv2.Sobel(gray, cv2.CV_32F, 0, 1)), (0, 0), 6)
    f = w / 2720.0
    self.env = {}
    if name in FOLIAGE:
        m = ((H_ > 28) & (H_ < 90) & (S_ > 55) & (V_ > 40)).astype(np.float32)
        if name == 's32':  # flowers too
            m = np.maximum(m, ((S_ > 120) & (V_ > 120) & ((H_ < 25) | (H_ > 160))).astype(np.float32))
            m[int(h * 0.15):, int(w * 0.33):int(w * 0.85)] *= 0  # keep the girl/robot still
        self.env['fol'] = cv2.GaussianBlur(m, (0, 0), 5 * f)
    if name in SKY:
        low = (grad < 18).astype(np.uint8)
        low[int(h * 0.6):] = 0
        n, lab = cv2.connectedComponents(low)
        top = set(np.unique(lab[0])) - {0}
        m = np.isin(lab, list(top)).astype(np.uint8)
        m = cv2.erode(m, np.ones((int(30 * f) | 1, int(30 * f) | 1), np.uint8))
        self.env['sky'] = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 25 * f)
    if name in SCARF:
        m = ((S_ > 110) & (V_ > 50) & ((H_ < 9) | (H_ > 170))).astype(np.uint8)
        m = cv2.dilate(m, np.ones((int(9 * f) | 1, int(9 * f) | 1), np.uint8))
        self.env['scarf'] = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 4 * f)
    if name in WATER:
        bm = _box_mask((h, w), WATER[name], 12 * f)
        calm = np.clip(1.0 - grad / 60.0, 0, 1)
        self.env['water'] = bm * cv2.GaussianBlur(calm, (0, 0), 4 * f)
    if name in FALLS:
        bm = _box_mask((h, w), FALLS[name], 6 * f)
        white = ((V_ > 170) & (S_ < 90)).astype(np.float32)
        self.env['fall'] = bm * cv2.GaussianBlur(white, (0, 0), 3 * f)
    # downscale masks to half source res to keep warps cheap
    for k in list(self.env):
        self.env[k] = cv2.resize(self.env[k], (w // 2, h // 2), interpolation=cv2.INTER_AREA)
    self.src_wh = (w, h)


def _warp_mask(m, M, hw, hh):
    Mh = M.copy() * 0.5
    Mh[:, :2] *= 2.0     # mask is half source res
    return cv2.warpAffine(m, Mh, (hw, hh), flags=cv2.INTER_LINEAR)


def motion(self, frame, M, t, lt):
    """Displacement-based animation of the environment + additive layers."""
    if not hasattr(self, 'env'):
        return frame
    W, H = self.W, self.H
    hw, hh = W // 2, H // 2
    S = W / 1920.0
    X, Y = _grid(hw, hh)
    dx = np.zeros((hh, hw), np.float32)
    dy = np.zeros((hh, hw), np.float32)
    add = np.zeros((hh, hw, 3), np.float32)
    name = self.name

    # hand-drawn line boil: new wobble pattern ~8 times a second (animated "on threes")
    k = int(t * 8)
    ox, oy = (k * 97) % 256, (k * 53) % 256
    dx += _samp(NZ['boil_a'], X * 0.9 + ox, Y * 0.9 + oy) * 1.1 * S
    dy += _samp(NZ['boil_b'], X * 0.9 + oy, Y * 0.9 + ox) * 1.1 * S

    env = {kk: _warp_mask(v, M, hw, hh) for kk, v in self.env.items()}

    if 'fol' in env:
        gust = 0.65 + 0.35 * math.sin(t * 0.45)
        sway = (np.sin(t * 1.7 + X * 0.012 + Y * 0.02) * 0.6 +
                _samp(NZ['fol'], X * 0.6 + t * 22, Y * 0.6) * 0.8)
        dx += env['fol'] * sway * 4.2 * S * gust
        dy += env['fol'] * _samp(NZ['fol'], X * 0.6 + 80, Y * 0.6 + t * 15) * 1.6 * S

    if 'sky' in env:
        dx += env['sky'] * _samp(NZ['sky'], X * 0.12 + t * 5, Y * 0.12) * 9 * S
        dy += env['sky'] * _samp(NZ['sky'], X * 0.12 + 120, Y * 0.12 + t * 2) * 3 * S
        cloud = np.clip(_samp(NZ['smoke'], X * 0.25 - t * 7, Y * 0.5) * 1.2 - 0.2, 0, 1)
        warm = np.array([1.0, 0.85, 0.7], np.float32) if name in {'s36', 's37', 's38', 's39', 's40'} \
            else np.array([1.0, 1.0, 1.0], np.float32)
        add += (env['sky'] * cloud)[..., None] * warm * 22

    if 'scarf' in env:
        flut = np.sin(t * 5.5 + Y * 0.09) * 0.7 + _samp(NZ['fol'], X * 1.5 + t * 40, Y * 1.5) * 0.6
        dx += env['scarf'] * flut * 3.2 * S
        dy += env['scarf'] * np.sin(t * 4.1 + X * 0.07) * 1.2 * S

    if 'water' in env:
        w = env['water']
        rip = np.sin(Y * 0.55 - t * 2.4 + _samp(NZ['water'], X * 0.35 + t * 9, Y * 0.9) * 2.5)
        dx += w * rip * 2.6 * S
        dy += w * _samp(NZ['water'], X * 0.5, Y * 1.5 - t * 12) * 1.0 * S
        glint = np.clip(_samp(NZ['spark'], X * 0.7 + t * 14, Y * 2.2) - 0.45, 0, 1) * 2.2
        add += (w * glint)[..., None] * np.array([1.0, 0.95, 0.85], np.float32) * 120

    if 'fall' in env:
        fm = env['fall']
        dy += fm * _samp(NZ['fall'], X * 1.2, Y * 0.35 - t * 70) * 5 * S
        dx += fm * _samp(NZ['fall'], X * 1.2 + 70, Y * 0.35 - t * 70) * 1.5 * S
        streak = np.clip(_samp(NZ['streak'], X * 2.0, Y * 0.5 - t * 110) - 0.15, 0, 1)
        add += (fm * streak)[..., None] * 95
        mist = np.clip(_samp(NZ['smoke'], X * 0.5 + t * 6, Y * 0.5 + t * 10), 0, 1)
        add += (cv2.GaussianBlur(fm, (0, 0), 14) * mist)[..., None] * 40

    if name in BUTTERFLY:
        bx, by, br = BUTTERFLY[name]
        sw, sh_ = self.src_wh
        cx, cy = M @ np.array([bx * sw, by * sh_, 1.0])
        cx, cy, rr = cx / 2, cy / 2, br * sw * M[0, 0] / 2
        d = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
        wmask = np.clip(1 - d / rr, 0, 1) ** 0.7
        flap = 0.35 * (0.5 + 0.5 * math.sin(t * 11))
        dx += wmask * (X - cx) * flap * 2  # squash wings toward body (in full-res px)

    # apply displacement (fields are in full-res px, sampled at half res)
    dxf = cv2.resize(dx, (W, H), interpolation=cv2.INTER_LINEAR)
    dyf = cv2.resize(dy, (W, H), interpolation=cv2.INTER_LINEAR)
    Xf, Yf = _grid(W, H)
    frame = cv2.remap(frame, Xf + dxf, Yf + dyf, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    # smoke wisps
    if name in SMOKE:
        sw, sh_ = self.src_wh
        lay = np.zeros((hh, hw), np.float32)
        for sxn, syn in SMOKE[name]:
            px, py = M @ np.array([sxn * sw, syn * sh_, 1.0])
            px, py = px / 2, py / 2
            up = np.clip((py - Y) / (160 * S), 0, 1)               # above the source
            wob = _samp(NZ['smoke'], X * 0.8, Y * 0.8 + t * 30) * 25 * S * (0.3 + up)
            spread = 12 * S + up * 45 * S
            col = np.exp(-((X - px - wob) ** 2) / (2 * spread ** 2)) * (Y < py) * (1 - up) ** 0.6
            dens = np.clip(_samp(NZ['smoke'], X * 0.9 + 40, Y * 0.9 + t * 45) + 0.3, 0, 1)
            lay += col * dens
        add += np.clip(lay, 0, 1)[..., None] * np.array([215, 210, 205], np.float32) * 0.45

    # birds
    if name in BIRDS:
        sw, sh_ = self.src_wh
        lay = np.zeros((hh, hw), np.float32)
        r = np.random.default_rng(int(name[1:]))
        for b in range(BIRDS[name]):
            speed = r.uniform(25, 45) * S
            x0 = r.uniform(-0.3, 0.9) * hw
            y0 = r.uniform(0.06, 0.28) * hh
            bx = (x0 + speed * lt) % (hw * 1.3) - 0.15 * hw
            by = y0 + math.sin(lt * 0.9 + b) * 6 * S
            flap = math.sin(lt * 9 + b * 2)
            s = r.uniform(5, 8) * S
            p1 = (int(bx - s), int(by - flap * s * 0.6))
            p2 = (int(bx), int(by + s * 0.25))
            p3 = (int(bx + s), int(by - flap * s * 0.6))
            cv2.polylines(lay, [np.array([p1, p2, p3], np.int32)], False, 1.0, max(1, int(1.6 * S)), cv2.LINE_AA)
        lay = cv2.resize(lay, (W, H))
        frame *= (1 - 0.65 * lay[..., None])

    # lamp flicker
    if name in LAMP:
        hx, hy = M @ np.array([self.hot[0], self.hot[1], 1.0])
        d = np.sqrt((X - hx / 2) ** 2 + (Y - hy / 2) ** 2)
        fl = 0.5 + 0.5 * math.sin(t * 9) * math.sin(t * 3.7 + 1)
        add += (np.exp(-d / (160 * S)) * (12 + 14 * fl))[..., None] * np.array([1.0, 0.8, 0.5], np.float32)

    if add.any():
        frame += cv2.resize(add, (W, H), interpolation=cv2.INTER_LINEAR)
    return frame


SceneFX._init_env = _init_env
SceneFX.motion = motion
_orig_init = SceneFX.__init__
_orig_apply = SceneFX.apply


def _new_init(self, name, src, W, H):
    _orig_init(self, name, src, W, H)
    self._init_env(src)


def _new_apply(self, frame, M, t, local_t, dur):
    frame = self.motion(frame, M, t, local_t)
    return _orig_apply(self, frame, M, t, local_t, dur)


SceneFX.__init__ = _new_init
SceneFX.apply = _new_apply


# =====================================================================
#  Depth parallax, breathing, Mia blinking, Echo talking glow
# =====================================================================
import json as _json
_F2 = _json.load(open('faces2.json'))
_EYES = _json.load(open('eyes.json'))
_TLJ = _json.load(open('timeline.json'))
exec(open('script.py').read(), globals())   # LINES


def _body_ellipse(h, w, box):
    x0, y0, x1, y1 = box
    fw, fh = (x1 - x0) * w, (y1 - y0) * h
    cx = (x0 + x1) / 2 * w
    top = y0 * h
    bot = min(h, y1 * h + fh * 2.0)
    m = np.zeros((h, w), np.float32)
    cv2.ellipse(m, (int(cx), int((top + bot) / 2)), (int(fw * 0.8), int((bot - top) / 2)), 0, 0, 360, 1.0, -1)
    yy = np.arange(h, dtype=np.float32)[:, None]
    wgt = np.clip((bot - yy) / max(1.0, bot - top), 0, 1)
    return m, m * wgt


def _init_depth(self, src):
    h, w = src.shape[:2]
    f = w / 2720.0
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    depth = np.repeat(0.25 + 0.5 * yy ** 1.2, w, axis=1)
    if 'sky' in getattr(self, 'env', {}):
        sky = cv2.resize(self.env['sky'], (w, h))
        depth = depth * (1 - sky) + 0.08 * sky
    self.has_chars = False
    self.breath = {}
    for who, box in _F2.get(self.name, {}).items():
        body, bw_ = _body_ellipse(h, w, box)
        depth = np.maximum(depth, body * 0.9)
        self.breath[who] = cv2.resize(cv2.GaussianBlur(bw_, (0, 0), 12 * f), (w // 2, h // 2))
        self.has_chars = True
    depth = cv2.GaussianBlur(depth, (0, 0), 45 * f)
    self.depth = cv2.resize(depth, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
    self.eyes = _EYES.get(self.name, [])
    self.src_wh2 = (w, h)


def _depth_motion(self, frame, M, t, lt):
    W, H = self.W, self.H
    hw, hh = W // 2, H // 2
    S = W / 1920.0
    d = _warp_mask(self.depth, M, hw, hh)
    ph = int(self.name[1:]) * 0.7
    P = (11 if self.has_chars else 6) * S
    dx = (d - 0.5) * P * math.sin(t * 0.33 + ph)
    dy = (d - 0.5) * P * 0.45 * math.sin(t * 0.27 + ph * 1.7)
    for k, (who, bm) in enumerate(self.breath.items()):
        b = _warp_mask(bm, M, hw, hh)
        period = 3.8 if who == 'MIA' else 5.0
        amp = (2.6 if who == 'MIA' else 1.6) * S
        dy -= b * amp * math.sin(2 * math.pi * t / period + k * 1.3)
    dxf = cv2.resize(dx.astype(np.float32), (W, H)); dyf = cv2.resize(dy.astype(np.float32), (W, H))
    Xf, Yf = _grid(W, H)
    return cv2.remap(frame, Xf + dxf, Yf + dyf, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def _blink(self, frame, M, t, lt):
    if not self.eyes:
        return frame
    seed = int(self.name[1:])
    r = np.random.default_rng(seed)
    times = np.cumsum(r.uniform(2.6, 4.8, 40)) + 0.8
    closed = any(0 <= lt - b < 0.13 for b in times)
    if not closed:
        return frame
    sw, sh = self.src_wh2
    S = self.W / 1920.0
    for cx, cy, rx, ry in self.eyes:
        p = M @ np.array([cx * sw, cy * sh, 1.0])
        sc = math.hypot(M[0, 0], M[0, 1])
        Rx, Ry = rx * sw * sc * 1.3, ry * sh * sc * 1.3
        x, y = int(p[0]), int(p[1])
        # sample skin just below the eye (cheek)
        sy0, sy1 = int(y + Ry * 1.6), int(y + Ry * 2.4)
        sx0, sx1 = int(x - Rx * 0.6), int(x + Rx * 0.6)
        patch = frame[max(0, sy0):max(1, sy1), max(0, sx0):max(1, sx1)]
        if patch.size == 0:
            continue
        skin = np.median(patch.reshape(-1, 3), axis=0)
        cv2.ellipse(frame, (x, y), (int(Rx), int(Ry)), 0, 0, 360, tuple(float(v) for v in skin), -1, cv2.LINE_AA)
        cv2.ellipse(frame, (x, int(y + Ry * 0.1)), (int(Rx * 0.95), int(Ry * 0.45)), 0, 10, 170,
                    (55.0, 38.0, 32.0), max(2, int(2.8 * S)), cv2.LINE_AA)
    return frame


# Echo talking glow: loudness envelope of Echo's lines
_TALK = []
def _load_talk():
    import subprocess as _sp
    for ln in _TLJ['lines']:
        if ln['speaker'] != 'ECHO':
            continue
        a = np.frombuffer(_sp.check_output(['ffmpeg', '-v', 'error', '-i', f"assets/lines/{ln['idx']:03d}.wav",
                                            '-f', 'f32le', '-ac', '1', '-ar', '2400', '-']), np.float32)
        n = len(a) // 100
        env = np.sqrt(np.mean(a[:n * 100].reshape(n, 100) ** 2, axis=1)) if n else np.zeros(1)
        env = env / (env.max() + 1e-6)
        _TALK.append((ln['start'], env, LINES[ln['idx']][0]))
def echo_talk(t, scene):
    if not _TALK:
        _load_talk()
    for st, env, sc in _TALK:
        if sc == scene and st <= t < st + len(env) / 24.0:
            return float(env[int((t - st) * 24)])
    return 0.0


_prev_init = SceneFX.__init__
_prev_apply = SceneFX.apply


def _init3(self, name, src, W, H):
    _prev_init(self, name, src, W, H)
    self._init_depth(src)


def _apply3(self, frame, M, t, local_t, dur):
    frame = self._depth_motion(frame, M, t, local_t)
    self._talk = echo_talk(t, self.name)
    frame = _prev_apply(self, frame, M, t, local_t, dur)
    return self._blink(frame, M, t, local_t)


SceneFX._init_depth = _init_depth
SceneFX._depth_motion = _depth_motion
SceneFX._blink = _blink
SceneFX.__init__ = _init3
SceneFX.apply = _apply3
