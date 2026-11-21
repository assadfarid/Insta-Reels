"""Assemble dialogue + music into one stereo mix (assets/mix.wav)."""
import json, subprocess, numpy as np

SR = 48000
tl = json.load(open('timeline.json'))
N = int((tl['total'] + 1) * SR)


def load(path, filt=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', path]
    if filt:
        cmd += ['-af', filt]
    cmd += ['-f', 'f32le', '-ac', '1', '-ar', str(SR), '-']
    return np.frombuffer(subprocess.check_output(cmd), dtype=np.float32).copy()


FX = {
    # radio operator: thin band-limited radio voice
    'OP': 'highpass=f=350,lowpass=f=3200,acompressor=threshold=-18dB:ratio=4,volume=1.4',
    # Elena: archival recording, slightly band-limited with a soft room echo
    'ELENA': 'highpass=f=200,lowpass=f=6000,aecho=0.8:0.5:40:0.18',
    # Echo: a touch of metallic sheen
    'ECHO': 'aecho=0.8:0.6:12:0.12',
}
LEVEL = {'N': 0.95, 'MIA': 1.0, 'ECHO': 1.0, 'ELENA': 1.0, 'OP': 0.9, 'TECH': 1.0}

voice = np.zeros(N, np.float32)
for ln in tl['lines']:
    a = load(f"assets/lines/{ln['idx']:03d}.wav", FX.get(ln['speaker']))
    # loudness-normalise each line roughly (RMS target)
    rms = np.sqrt(np.mean(a ** 2)) + 1e-9
    a = a * (0.08 / rms) * LEVEL[ln['speaker']]
    s = int(ln['start'] * SR)
    voice[s:s + len(a)] += a[:N - s]

# radio static under the operator lines
rng = np.random.default_rng(1)
for ln in tl['lines']:
    if ln['speaker'] == 'OP':
        s, e = int((ln['start'] - 0.3) * SR), int((ln['start'] + ln['dur'] + 0.3) * SR)
        voice[s:e] += (rng.standard_normal(e - s) * 0.006).astype(np.float32)

peak = np.max(np.abs(voice))
if peak > 0.95:
    voice *= 0.95 / peak

tracks = {k: load(f'assets/audio_raw/music_{k}.mp3', 'loudnorm=I=-20:TP=-2') for k in ('gentle', 'hopeful')}
music = np.zeros(N, np.float32)
XF = int(4 * SR)
for m in tl['music']:
    src = tracks[m['track']]
    s, e = int(m['start'] * SR), min(N, int(m['end'] * SR) + XF)
    seg_len = e - s
    # loop the piece with crossfades until the segment is filled
    out = np.zeros(seg_len, np.float32)
    pos, L = 0, len(src)
    while pos < seg_len:
        piece = src.copy()
        if pos > 0:
            piece[:XF] *= np.linspace(0, 1, XF)
        take = min(L, seg_len - pos)
        out[pos:pos + take] += piece[:take]
        if pos + take >= seg_len:
            break
        # fade the tail of this loop while the next starts
        tail_start = pos + L - XF
        out[tail_start:pos + L] *= np.linspace(1, 0, XF)[:len(out[tail_start:pos + L])]
        pos = tail_start
    # segment fade in / out
    out[:XF] *= np.linspace(0, 1, XF)
    out[-XF:] *= np.linspace(1, 0, XF)
    music[s:e] += out

# duck music under speech: envelope follower on the voice
env = np.abs(voice)
win = int(0.25 * SR)
def smooth(x, n):
    c = np.cumsum(np.concatenate([np.zeros(1, np.float64), x.astype(np.float64)]))
    y = (c[n:] - c[:-n]) / n
    pad = len(x) - len(y)
    return np.pad(y, (pad // 2, pad - pad // 2), mode='edge').astype(np.float32)
env = smooth(smooth(env, win), int(0.6 * SR))
duck = 1.0 - 0.55 * np.clip(env / 0.02, 0, 1)
music *= 0.32 * duck
# fade music in at the very start and out at the end
music[:int(2 * SR)] *= np.linspace(0, 1, int(2 * SR))
music[-int(5 * SR):] *= np.linspace(1, 0, int(5 * SR))

sfx = load('assets/sfx.wav')
sfx = np.pad(sfx, (0, max(0, N - len(sfx))))[:N]
# duck effects slightly under speech too
sfx *= (1.0 - 0.35 * np.clip(env / 0.02, 0, 1))
mix = voice + music + sfx * 0.9
mix /= max(1.0, np.max(np.abs(mix)) / 0.97)
stereo = np.stack([mix, mix], axis=1).astype(np.float32)
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                      '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', str(SR), 'assets/mix.wav'],
                     stdin=subprocess.PIPE)
p.communicate(stereo.tobytes())
print('mix written', len(mix) / SR, 's')
