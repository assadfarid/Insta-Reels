"""Procedural sound effects (no external assets, no credits) -> assets/sfx.wav (mono 48k).
Ambience beds per scene + one-shot events tied to the timeline."""
import json, math, subprocess
import numpy as np

SR = 48000
tl = json.load(open('timeline.json'))
exec(open('script.py').read())
N = int((tl['total'] + 1) * SR)
out = np.zeros(N, np.float32)
rng = np.random.default_rng(7)


def noise(n):
    return rng.standard_normal(n).astype(np.float32)


def lp(x, a):  # one-pole low-pass, a in (0,1): smaller = darker
    y = np.empty_like(x); acc = 0.0
    # vectorised approximation via exponential smoothing in chunks
    from scipy.signal import lfilter
    return lfilter([a], [1, a - 1], x).astype(np.float32)


def hp(x, a):
    return (x - lp(x, a)).astype(np.float32)


def env(n, att, rel):
    e = np.ones(n, np.float32)
    na, nr = int(att * SR), int(rel * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e


def put(sig, t, gain=1.0):
    s = int(t * SR)
    if s >= N or s + len(sig) <= 0:
        return
    a = max(0, -s); s = max(0, s)
    e = min(N, s + len(sig) - a)
    out[s:e] += sig[a:a + e - s] * gain


def bed(t0, t1, gen, gain, fade=1.2):
    n = int((t1 - t0) * SR)
    if n <= 0: return
    put(gen(n) * env(n, fade, fade), t0, gain)

# ---------------- generators ----------------
def g_hum(n):      # underground room tone / electrical hum
    t = np.arange(n) / SR
    return (lp(noise(n), 0.01) * 3 + 0.25 * np.sin(2 * np.pi * 50 * t) + 0.12 * np.sin(2 * np.pi * 100 * t)).astype(np.float32)

def g_wind(n):
    base = lp(noise(n), 0.02) * 4
    swell = 0.6 + 0.4 * np.sin(np.arange(n) / SR * 0.35 * 2 * np.pi + rng.uniform(0, 6))
    return (base * swell).astype(np.float32)

def g_water(n):    # stream / waterfall
    return (hp(lp(noise(n), 0.25), 0.02) * 1.2 * (0.85 + 0.15 * np.sin(np.arange(n) / SR * 1.7))).astype(np.float32)

def g_crickets(n):
    t = np.arange(n) / SR
    chirp = np.sin(2 * np.pi * 4200 * t) * (np.sin(2 * np.pi * 28 * t) > 0.3) * (np.sin(2 * np.pi * 0.9 * t) > 0)
    return (chirp * 0.12 + lp(noise(n), 0.01) * 1.5).astype(np.float32)

def s_bird(dur=0.25):
    n = int(dur * SR); t = np.arange(n) / SR
    f0 = rng.uniform(2600, 4200)
    f = f0 + rng.uniform(600, 1500) * np.sin(2 * np.pi * rng.uniform(9, 16) * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * env(n, 0.02, 0.08) * 0.35).astype(np.float32)

def s_spark():
    n = int(0.35 * SR)
    x = np.clip(noise(n), -2.5, 2.5) * 0.3 * (rng.random(n) > 0.985) + hp(noise(n), 0.5) * 0.12
    return (x * np.exp(-np.arange(n) / SR * 9)).astype(np.float32)

def s_thud():
    n = int(0.9 * SR); t = np.arange(n) / SR
    return ((np.sin(2 * np.pi * 55 * t) * 1.2 + lp(noise(n), 0.03) * 3 + noise(n) * 0.15 * np.exp(-t * 40))
            * np.exp(-t * 6)).astype(np.float32)

def s_metal_clank():
    n = int(0.6 * SR); t = np.arange(n) / SR
    tone = sum(np.sin(2 * np.pi * f * t) for f in (880, 1340, 2210)) / 3
    return ((tone + noise(n) * 0.4 * np.exp(-t * 60)) * np.exp(-t * 7) * 0.6).astype(np.float32)

def s_door(dur=5.0):   # heavy grinding blast door
    n = int(dur * SR); t = np.arange(n) / SR
    grind = lp(noise(n), 0.04) * 4 * (0.7 + 0.3 * np.sign(np.sin(2 * np.pi * 7 * t)))
    rumble = np.sin(2 * np.pi * (38 + 6 * t) * t) * 0.8
    return ((grind + rumble) * env(n, 0.3, 1.0)).astype(np.float32)

def s_whoosh(dur=2.0, rise=True):
    n = int(dur * SR); t = np.linspace(0, 1, n)
    x = hp(noise(n), 0.1) * (t if rise else 1 - t) ** 1.5
    return (lp(x, 0.3) * 2 * env(n, 0.05, 0.3)).astype(np.float32)

def s_alarm(dur=2.5):
    n = int(dur * SR); t = np.arange(n) / SR
    beep = np.sin(2 * np.pi * 880 * t) * (np.sin(2 * np.pi * 3 * t) > 0)
    return (beep * 0.25 * env(n, 0.01, 0.2)).astype(np.float32)

def s_powerdown(dur=2.2):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 220 * np.exp(-t * 1.6) + 30
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.02, 0.6) * 0.5).astype(np.float32)

def s_powerup(dur=1.8):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 60 + 400 * (t / dur) ** 2
    return ((np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + hp(noise(n), 0.3) * 0.08) * env(n, 0.2, 0.3)).astype(np.float32)

def s_servo(dur=0.45):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 380 + 160 * np.sin(np.pi * t / dur)
    return ((np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.05 + np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15)
            * env(n, 0.04, 0.1)).astype(np.float32)

def s_toaster():
    n = int(0.25 * SR); t = np.arange(n) / SR
    return ((noise(n) * np.exp(-t * 60) * 0.8 + np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 25) * 0.3)).astype(np.float32)

def s_engine(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    return ((lp(noise(n), 0.02) * 4 + np.sin(2 * np.pi * 42 * t) * 0.5) * np.linspace(0.2, 1, n) * env(n, 0.5, 0.8)).astype(np.float32)

# ---------------- scene plan ----------------
shots = {}
for s in tl['shots']:
    if s['kind'] == 'img':
        shots.setdefault(s['img'], []).append((s['start'], s['end']))

UNDER = [f's{i:02d}' for i in range(1, 29)]
OUTDOOR_BIRDS = ['s30', 's31', 's32', 's33', 's34', 's35', 's49']
WIND = ['s30', 's33', 's34', 's36', 's37', 's38', 's39', 's40', 's49']
WATER = ['s30', 's36', 's39', 's40', 's49']
NIGHT = ['s41', 's42', 's43', 's44', 's45', 's46', 's47', 's48']
WORKSHOP = ['s50', 's51', 's52', 's53', 's54', 's55']

for sc, spans in shots.items():
    for a, b in spans:
        if sc in UNDER:
            bed(a, b, g_hum, 0.012)
        if sc in WIND:
            bed(a, b, g_wind, 0.02)
        if sc in WATER:
            bed(a, b, g_water, 0.035 if sc == 's30' else 0.02)
        if sc in NIGHT:
            bed(a, b, g_crickets, 0.05)
        if sc in WORKSHOP:
            bed(a, b, g_hum, 0.006)
        if sc in OUTDOOR_BIRDS + ['s36']:
            t = a + rng.uniform(0.5, 2)
            while t < b - 0.5:
                for k in range(rng.integers(2, 5)):
                    put(s_bird(rng.uniform(0.12, 0.3)), t + k * rng.uniform(0.12, 0.22), 0.12)
                t += rng.uniform(2.0, 4.5)
        if sc in ('s19', 's22', 's23'):
            t = a + 0.6
            while t < b:
                put(s_spark(), t, 0.25); t += rng.uniform(0.6, 1.8)

def first(sc):
    return shots[sc][0][0]

put(s_toaster(), first('s06') + 1.2, 0.2)
put(s_alarm(3.0), first('s14') + 0.4, 0.5)
put(s_servo(), first('s14') + 2.0, 0.6)
put(s_powerdown(), first('s27') + 0.3, 0.5)
put(s_door(5.5), first('s29') - 0.2, 0.09)
put(s_whoosh(2.5), first('s29') + 2.0, 0.25)
put(s_metal_clank(), first('s22') + 0.4, 0.4)          # container falls
for st, sc in [(l['start'] + l['dur'] * 0.72, LINES[l['idx']][0]) for l in tl['lines']
               if 'collapses onto the bridge' in LINES[l['idx']][2]]:
    put(s_thud(), st, 0.3); put(s_metal_clank(), st + 0.05, 0.25)
put(s_metal_clank(), first('s42') + 2.5, 0.35)          # cable plugs in
put(s_powerup(), first('s43') + 0.5, 0.45)
put(s_whoosh(1.2), first('s43') + 0.5, 0.2)
put(s_powerdown(3.0), first('s47') + 0.8, 0.35)
a48, b48 = shots['s48'][0]
put(s_engine(b48 - a48), a48, 0.06)
put(s_powerup(2.2), first('s51') + 0.2, 0.45)
for sc in ('s06', 's28', 's39', 's55'):
    put(s_servo(), first(sc) + 1.5, 0.45)

out = np.clip(out, -1, 1)
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-',
                      'assets/sfx.wav'], stdin=subprocess.PIPE)
p.communicate(out.astype(np.float32).tobytes())
print('sfx written, peak', float(np.abs(out).max()))
