"""Estimate per-word timings for narrator lines from the line audio (free, no ASR).
Words are spread over the speech-only parts of each line (pauses removed),
weighted by syllable count, with extra weight after punctuation."""
import json, re, subprocess
tl = json.load(open('timeline.json'))

def syl(w):
    w = re.sub(r'[^a-z]', '', w.lower())
    n = len(re.findall(r'[aeiouy]+', w))
    if w.endswith('e') and n > 1 and not w.endswith('le'):
        n -= 1
    return max(1, n)

def speech_regions(path, dur):
    log = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'silencedetect=noise=-38dB:d=0.14',
                          '-f', 'null', '-'], capture_output=True, text=True).stderr
    S = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]
    E = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
    sil = [(s, e) for s, e in zip(S, E) if e - s > 0.14]
    regs, cur = [], 0.0
    for s, e in sil:
        if s > cur + 0.05:
            regs.append((cur, s))
        cur = max(cur, e)
    if dur > cur + 0.05:
        regs.append((cur, dur))
    return regs or [(0, dur)]

out = {}
for ln in tl['lines']:
    if ln['speaker'] != 'N':
        continue
    words = ln['text'].split()
    regs = speech_regions(f"assets/lines/{ln['idx']:03d}.wav", ln['dur'])
    total = sum(e - s for s, e in regs)
    wts = [syl(w) + 0.35 for w in words]
    W = sum(wts)
    def speech_to_time(x, start):  # x in [0,total] speech-time -> real time
        for s, e in regs:
            if (x < e - s - 1e-6) if start else (x <= e - s + 1e-6):
                return s + x
            x -= e - s
        return regs[-1][1]
    acc, res = 0.0, []
    for w, wt in zip(words, wts):
        a = speech_to_time(acc / W * total, True)
        acc += wt
        b = speech_to_time(acc / W * total, False)
        res.append([w, round(ln['start'] + a, 3), round(ln['start'] + b, 3)])
    out[str(ln['idx'])] = res
json.dump(out, open('word_times.json', 'w'))
print(len(out), 'narrator lines timed')
