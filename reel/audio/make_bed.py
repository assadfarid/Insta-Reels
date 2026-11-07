"""Quiet original music bed (32 s) for the presenter reel. numpy only. Run: python3 -I audio/make_bed.py audio/bed_raw.wav"""
import numpy as np, wave, sys
SR, DUR, BPM = 44100, 32.5, 100
N = int(SR * DUR); BEAT = 60 / BPM; BAR = 4 * BEAT
rng = np.random.default_rng(11)
mid = lambda m: 440 * 2 ** ((m - 69) / 12)
def lp(x, c, o=2):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / (1 + (f / c) ** (2 * o)), len(x))
def hp(x, c, o=2):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); r = (f / c) ** (2 * o)
    return np.fft.irfft(X * r / (1 + r), len(x))
L, R = np.zeros(N), np.zeros(N)
def put(sig, t0, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N: return
    if i < 0: sig = sig[-i:]; i = 0
    s = sig[: N - i]; a = (pan + 1) * np.pi / 4
    L[i:i + len(s)] += s * g * np.cos(a); R[i:i + len(s)] += s * g * np.sin(a)
def saw(f, n, dets):
    t = np.arange(n) / SR
    return sum(2 * ((t * f * 2 ** (c / 1200) + rng.random()) % 1) - 1 for c in dets) / len(dets)
def pad(m, d, cut=1100):
    n = int(d * SR); e = np.ones(n); a, r = int(0.9 * SR), int(1.2 * SR)
    e[:a] = np.linspace(0, 1, a) ** 2; e[-r:] *= np.linspace(1, 0, r)
    return lp(saw(mid(m), n, (-12, -5, 0, 5, 12)) * e, cut)
def pluck(m, d=0.45):
    n = int(d * SR); t = np.arange(n) / SR
    return lp(saw(mid(m), n, (-4, 4)), 2400) * np.exp(-t / 0.12)
def hat():
    t = np.arange(int(0.05 * SR)) / SR
    return hp(rng.standard_normal(len(t)), 7500) * np.exp(-t / 0.012) * 0.4
def kick():
    t = np.arange(int(0.45 * SR)) / SR
    f = 48 + 90 * np.exp(-t / 0.035)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.2)
CH = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 55, 60, 64], [55, 59, 62, 67]]
t = 0.0; k = 0
while t < DUR - 1:                                # one chord per 2 bars
    for m in CH[k % 4]: put(pad(m, 2 * BAR + 1.2), t - 0.1, 0.17, -0.3 if m % 2 else 0.3)
    for e in range(16):                           # soft 8th-note arpeggio
        te = t + e * BEAT / 2
        if te < DUR - 1: put(pluck(CH[k % 4][[0, 2, 1, 3][e % 4]] + 12), te, 0.16 + 0.04 * (e % 4 == 0), [-0.5, 0.5][e % 2])
    t += 2 * BAR; k += 1
for e in range(int(DUR / (BEAT / 2))):            # gentle off-beat hats
    if e % 2 == 1 and e * BEAT / 2 > 4: put(hat(), e * BEAT / 2, 0.5, 0.25)
CTA = 25.3                                        # lift into the call to action
for b in range(5): put(kick(), CTA + b * BEAT, 0.5)
n = int(1.2 * SR); sw = hp(rng.standard_normal(n), 2500) * (np.arange(n) / n) ** 2 * 0.25; put(sw, CTA - 1.2, 0.6)
x = np.stack([L, R]); x = np.tanh(x * 1.2); x /= np.abs(x).max() / 0.85
out = sys.argv[1]
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x.T * 32767).astype("<i2").tobytes())
print("wrote", out)
