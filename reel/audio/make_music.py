"""Original soundtrack for the JDLaunch reel, synthesized with numpy only.

144 BPM, one bar = 1.6667 s = one project slide. Downbeats are aligned to the cuts in
src/jd/JDReel.tsx (drop 1 at 4.0 s, projects from 9.0 s, breakdown 15.67 s, finale 20.67 s).
Run:  python3 audio/make_music.py  ->  writes audio/music_raw.wav (mastered to mp3 with ffmpeg)
"""
import numpy as np, wave, sys

SR = 44100
DUR = 24.5
N = int(SR * DUR)
BPM = 144
BEAT = 60 / BPM
BAR = BEAT * 4
G = 0.6667  # downbeat grid origin (s): every bar starts at G + k*BAR (4.0 s and 9.0 s are downbeats)
rng = np.random.default_rng(7)

def midi(m): return 440.0 * 2 ** ((m - 69) / 12)

def spec_filter(x, kind, cut, order=2):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    r = (f / cut) ** (2 * order)
    H = 1 / (1 + r) if kind == "lp" else r / (1 + r)
    return np.fft.irfft(X * H, len(x))

lp = lambda x, c, o=2: spec_filter(x, "lp", c, o)
hp = lambda x, c, o=2: spec_filter(x, "hp", c, o)

class Bus:
    def __init__(self): self.b = np.zeros((2, N))
    def add(self, sig, t0, gain=1.0, pan=0.0):
        i = int(t0 * SR)
        if i >= N or i + len(sig) <= 0: return
        s = sig
        if i < 0: s = sig[-i:]; i = 0
        s = s[: N - i]
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        self.b[0, i:i + len(s)] += s * gain * l * 1.414
        self.b[1, i:i + len(s)] += s * gain * r * 1.414

drums, bass, pad, pluck, fx, verb = Bus(), Bus(), Bus(), Bus(), Bus(), Bus()
T = lambda d: np.arange(int(d * SR)) / SR

# ---------- instruments ----------
def kick(vol=1.0):
    t = T(0.5)
    f = 46 + 110 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.22)
    click = lp(rng.standard_normal(len(t)), 3000) * np.exp(-t / 0.004) * 0.25
    return (body + click) * vol

def hat(open_=False, vol=1.0):
    d = 0.28 if open_ else 0.05
    t = T(d)
    return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t / (0.09 if open_ else 0.012)) * vol * 0.5

def clap(vol=1.0):
    t = T(0.3)
    n = hp(lp(rng.standard_normal(len(t)), 5000), 900)
    env = sum(np.exp(-np.clip(t - o, 0, None) / 0.012) * (t >= o) for o in (0, 0.011, 0.023)) * 0.6 + np.exp(-t / 0.1) * (t >= 0.03)
    return n * env * vol * 0.7

def snare(vol=1.0, d=0.2):
    t = T(d)
    n = hp(rng.standard_normal(len(t)), 1500) * np.exp(-t / 0.07)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05)
    return (n * 0.7 + tone * 0.5) * vol

def crash(d=2.2, vol=1.0):
    t = T(d)
    return hp(rng.standard_normal(len(t)), 3500) * np.exp(-t / (d / 4)) * vol * 0.45

def boom(vol=1.0, d=1.6):
    t = T(d)
    f = 30 + 40 * np.exp(-t / 0.3)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.7) * vol

def saw(f, n, detune_cents=(0,)):
    t = np.arange(n) / SR
    out = 0
    for c in detune_cents:
        ff = f * 2 ** (c / 1200)
        out = out + (2 * ((t * ff + rng.random()) % 1) - 1)
    return out / len(detune_cents)

def adsr(n, a, r, hold_to=None):
    e = np.ones(n)
    ia, ir = int(a * SR), int(r * SR)
    e[:ia] = np.linspace(0, 1, ia) ** 2
    e[-ir:] *= np.linspace(1, 0, ir) ** 1.5
    return e

def pad_note(m, dur, cutoff, vol=1.0):
    n = int(dur * SR)
    s = saw(midi(m), n, (-14, -7, 0, 7, 14)) * adsr(n, 0.5, 0.9)
    return lp(s, cutoff, 2) * vol

def pluck_note(m, cutoff=3200, vol=1.0, d=0.32):
    n = int(d * SR)
    t = np.arange(n) / SR
    s = saw(midi(m), n, (-5, 5)) * 0.6 + np.sin(2 * np.pi * midi(m) * t) * 0.5
    s = lp(s, cutoff, 2) * np.exp(-t / 0.09)
    return s * vol

def bass_note(m, d, vol=1.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * midi(m) * t) * 0.8 + lp(saw(midi(m), n), 280, 2) * 0.6
    e = np.ones(n); k = int(0.01 * SR); e[:k] = np.linspace(0, 1, k); k2 = int(0.05 * SR); e[-k2:] *= np.linspace(1, 0, k2)
    return s * e * vol

def noise_sweep(d, f0, f1, vol=1.0, rise=True):
    """Noise through a swept high-pass, built by overlap-add of FFT-filtered blocks."""
    n = int(d * SR); B = 4096; hop = B // 2
    x = rng.standard_normal(n + B)
    out = np.zeros(n + B); w = np.hanning(B)
    for i in range(0, n, hop):
        p = i / n
        cut = f0 * (f1 / f0) ** (p if rise else 1 - p)
        blk = x[i:i + B] * w
        X = np.fft.rfft(blk); f = np.fft.rfftfreq(B, 1 / SR)
        H = (f / cut) ** 4 / (1 + (f / cut) ** 4)
        out[i:i + B] += np.fft.irfft(X * H, B)
    t = np.arange(n) / SR
    env = (t / d) ** 2 if rise else (1 - t / d) ** 2
    return out[:n] * env * vol * 0.25

def tone_sweep(d, f0, f1, vol=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / d)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) ** 2 * vol * 0.25

def reverb_ir(d=2.4):
    n = int(d * SR); t = np.arange(n) / SR
    ir = np.stack([lp(rng.standard_normal(n), 6000, 1) * np.exp(-t / 0.55) for _ in range(2)])
    ir[:, :int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))
    return ir / np.sqrt((ir ** 2).sum(1, keepdims=True)) * 0.35

# ---------- arrangement ----------
CH = {"Am": [57, 60, 64, 69], "F": [53, 57, 60, 65], "C": [48, 55, 60, 64], "G": [55, 59, 62, 67]}
ROOT = {"Am": 33, "F": 29, "C": 36, "G": 31}
bars = [(G + 2 * BAR, "Am"), (G + 3 * BAR, "F"), (G + 4 * BAR, "G"),     # 4.0, 5.67, 7.33  groove
        (G + 5 * BAR, "Am"), (G + 6 * BAR, "F"), (G + 7 * BAR, "C"), (G + 8 * BAR, "G"),  # 9.0.. projects
        (G + 9 * BAR, "Am"), (G + 10 * BAR, "F"), (G + 11 * BAR, "G"),   # 15.67.. breakdown/build
        (G + 12 * BAR, "Am"), (G + 13 * BAR, "F")]                       # 20.67.. finale
DROP1, PROJ, BREAK, DROP2 = G + 2 * BAR, G + 5 * BAR, G + 9 * BAR, G + 12 * BAR
print("sections", round(DROP1, 3), round(PROJ, 3), round(BREAK, 3), round(DROP2, 3))

kick_times = []
def groove(t0, nbars, kick_on=True, clap_on=False, hats=True, arp=True, bass_on=True, vol=1.0):
    for b in range(nbars):
        for beat in range(4):
            tb = t0 + b * BAR + beat * BEAT
            if kick_on: drums.add(kick(), tb, 0.95 * vol); kick_times.append(tb)
            if hats:
                drums.add(hat(), tb + BEAT / 2, 0.55 * vol, 0.3)
                drums.add(hat(), tb + BEAT / 4, 0.18 * vol, -0.3); drums.add(hat(), tb + 3 * BEAT / 4, 0.18 * vol, 0.3)
            if clap_on and beat in (1, 3): drums.add(clap(), tb, 0.55 * vol); verb.add(clap(), tb, 0.25 * vol)

def chord_at(t):
    cur = bars[0][1]
    for bt, name in bars:
        if t + 1e-6 >= bt: cur = name
    return cur

def harmony(t0, t1, cutoff, pad_vol, arp_on, arp_oct=0, bass_on=True, lead=False):
    for bt, name in bars:
        if bt < t0 - 1e-6 or bt >= t1 - 1e-6: continue
        end = min(bt + BAR, t1)
        dur = end - bt + 0.8
        for m in CH[name]:
            s = pad_note(m, dur, cutoff, pad_vol)
            pad.add(s, bt - 0.05, 0.22, -0.4); verb.add(s, bt - 0.05, 0.1, 0.4)
        if bass_on:
            r = ROOT[name]
            for e in range(8):
                te = bt + e * BEAT / 2
                if te >= end - 1e-6: break
                m = r + (12 if e % 4 == 3 else 0)
                bass.add(bass_note(m, BEAT / 2 * 0.85), te, 0.9)
        if arp_on:
            tones = [m + 12 + 12 * arp_oct for m in CH[name]]
            seq = [0, 2, 1, 3, 2, 3, 1, 2, 0, 2, 3, 1, 3, 2, 1, 0]
            for k in range(16):
                te = bt + k * BEAT / 4
                if te >= end - 1e-6: break
                note = tones[seq[k]] + (12 if k % 8 == 6 else 0)
                s = pluck_note(note, 2600 + 1800 * (k % 4 == 0), 0.55)
                pluck.add(s, te, 0.8, [-0.5, 0.5][k % 2]); verb.add(s, te, 0.25, 0.3)
                # tempo-synced ping-pong echo
                pluck.add(s, te + 3 * BEAT / 4, 0.25, [0.6, -0.6][k % 2])

def whoosh(t0, d=0.5, vol=1.0):
    fx.add(noise_sweep(d, 400, 7000, vol), t0, 0.9); verb.add(noise_sweep(d, 400, 7000, vol * 0.5), t0, 0.3)

# --- A: intro 0 .. 4.0 : dark drone + riser
for m in (45, 52, 57, 60):
    s = pad_note(m, 4.2, 900, 0.9); pad.add(s, 0.0, 0.2, 0.2); verb.add(s, 0.0, 0.18, -0.2)
fx.add(boom(0.8, 4.0), 0.0, 0.5)
for hb in range(0, 6):                                   # distant heartbeat building
    drums.add(kick(0.7), 1.2 + hb * BEAT * 1.5 - 0.0, 0.18 + 0.05 * hb)
fx.add(noise_sweep(3.5, 250, 9000, 1.0), 0.5, 0.9); fx.add(tone_sweep(3.5, 220, 2400, 1.0), 0.5, 0.7)
rev = crash(2.0, 1.0)[::-1]; fx.add(rev, DROP1 - 2.0, 0.7)
# --- DROP 1 at 4.0 (hit) then groove
for b, s_ in ((drums, kick(1.2)),):
    b.add(s_, DROP1, 1.0); kick_times.append(DROP1)
fx.add(boom(1.0), DROP1, 0.9); fx.add(crash(2.6), DROP1, 0.8); verb.add(crash(2.6), DROP1, 0.3)
groove(DROP1 + BEAT, 0)  # no-op (placeholder to keep structure explicit)
t = DROP1
groove(DROP1 + BEAT, 0)
# groove 4.0 .. 9.0  (kick starts on beat 2 of first bar)
for beat in range(1, 4):
    drums.add(kick(), DROP1 + beat * BEAT, 0.95); kick_times.append(DROP1 + beat * BEAT)
    drums.add(hat(), DROP1 + beat * BEAT + BEAT / 2, 0.5, 0.3)
groove(DROP1 + BAR, 2)
groove(DROP1 + 3 * BAR, 0)
harmony(DROP1, PROJ, 1400, 0.8, True, 0)
whoosh(PROJ - 0.55, 0.55); fx.add(crash(1.6), PROJ - 0.0, 0.0)
# --- projects 9.0 .. 15.67 : full drums, claps, brighter
groove(PROJ - BAR * 0, 4, clap_on=True)
harmony(PROJ, BREAK, 2600, 0.9, True, 0)
for k in range(4):
    fx.add(crash(1.4), PROJ + k * BAR, 0.45 if k else 0.8)       # accent each project change
    fx.add(boom(0.5, 0.9), PROJ + k * BAR, 0.5)
# lead melody over projects (A minor pentatonic), one note per beat pair
lead = [76, 79, 81, 79, 76, 74, 76, 72] * 2
for k, m in enumerate(lead[:12]):
    te = PROJ + BAR + k * BEAT
    s = pluck_note(m, 4200, 0.7, 0.5); pluck.add(s, te, 0.55, 0.15); verb.add(s, te, 0.4, -0.2)
# last bar of projects: fill + whoosh into numbers
for k in range(8):
    drums.add(snare(0.8, 0.15), PROJ + 3 * BAR + BAR * 0.5 + k * BEAT / 4 * 2 * 0.5, 0.35 + 0.05 * k)
whoosh(BREAK - 0.5, 0.5)
# --- breakdown 15.67 .. 20.67 : stripped, hats + pad + bell-like plucks
fx.add(crash(2.0), BREAK, 0.7); drums.add(kick(), BREAK, 0.9); kick_times.append(BREAK)
harmony(BREAK, DROP2, 1300, 0.9, True, 1, bass_on=False)
for b in range(3):
    for beat in range(4):
        drums.add(hat(), BREAK + b * BAR + beat * BEAT + BEAT / 2, 0.3, 0.3)
        if b >= 1: drums.add(kick(0.8), BREAK + b * BAR + beat * BEAT, 0.6); kick_times.append(BREAK + b * BAR + beat * BEAT)
# count-up ticks while the $18M counter runs (frames 4..50 of the steps scene, abs ~18.0 .. 19.6 s)
pent = [69, 72, 74, 76, 79, 81, 84, 86, 88, 91, 93, 96]
for k, m in enumerate(pent):
    te = 18.05 + k * (1.5 / 12)
    t_ = T(0.12); s = np.sin(2 * np.pi * midi(m) * t_) * np.exp(-t_ / 0.03)
    fx.add(s, te, 0.35, [-0.4, 0.4][k % 2]); verb.add(s, te, 0.3)
# riser + snare roll into the end card
fx.add(noise_sweep(1.9, 300, 10000, 1.0), DROP2 - 1.9, 0.9); fx.add(tone_sweep(1.9, 300, 3000, 1.0), DROP2 - 1.9, 0.8)
roll_t = DROP2 - 1.667; n_hits = 0; step = BEAT / 2
while roll_t < DROP2 - 0.02:
    drums.add(snare(1.0, 0.18), roll_t, 0.25 + 0.55 * (roll_t - (DROP2 - 1.667)) / 1.667)
    step = max(BEAT / 8, step * 0.8); roll_t += step
# silence-gap just before the drop
for b in (drums, bass, pad, pluck, fx, verb):
    i0, i1 = int((DROP2 - 0.12) * SR), int(DROP2 * SR)
    # fade (not hard cut) over the last 0.12s except the riser/snare 'fx' to keep tension
    if b is not fx and b is not drums:
        b.b[:, i0:i1] *= np.linspace(1, 0.0, i1 - i0)
# --- DROP 2 at 20.67 : finale
drums.add(kick(1.3), DROP2, 1.0); kick_times.append(DROP2)
fx.add(boom(1.1, 2.0), DROP2, 1.0); fx.add(crash(3.2, 1.0), DROP2, 0.9); verb.add(crash(3.2), DROP2, 0.35)
groove(DROP2 + BEAT, 0)
for beat in range(1, 4):
    drums.add(kick(), DROP2 + beat * BEAT, 0.9); kick_times.append(DROP2 + beat * BEAT)
    drums.add(hat(), DROP2 + beat * BEAT + BEAT / 2, 0.45, 0.3)
groove(DROP2 + BAR, 1, clap_on=True, vol=0.9)
harmony(DROP2, DUR - 0.2, 2400, 1.0, True, 0)
fx.add(crash(2.0), DROP2 + BAR, 0.45)

# ---------- mix ----------
t_all = np.arange(N) / SR
duck = np.ones(N)
for tk in kick_times:
    i = int(tk * SR); L = int(0.28 * SR)
    if i >= N: continue
    seg = 1 - 0.75 * np.exp(-np.arange(min(L, N - i)) / SR / 0.075)
    duck[i:i + len(seg)] = np.minimum(duck[i:i + len(seg)], seg)
dry = drums.b * 1.0 + bass.b * duck * 1.0 + pad.b * duck * 0.9 + pluck.b * duck * 0.85 + fx.b * 0.9
ir = reverb_ir()
rv = np.stack([np.fft.irfft(np.fft.rfft(verb.b[c], N + ir.shape[1]) * np.fft.rfft(ir[c], N + ir.shape[1]))[:N] for c in range(2)])
mix = dry + rv * 0.9
mix[:, :] = hp(mix[0], 28, 2)[None, :] * 0 + np.stack([hp(mix[0], 28, 2), hp(mix[1], 28, 2)])
mix = np.tanh(mix * 1.15) / np.tanh(1.15)
mix /= np.abs(mix).max() / 0.89

pcm = (mix.T * 32767).astype("<i2")
out = sys.argv[1] if len(sys.argv) > 1 else "audio/music_raw.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote", out, "peak", float(np.abs(mix).max()))
