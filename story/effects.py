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
            amt = (60 if self.has_eyes else 35) * pulse * level
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
