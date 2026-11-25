"""Writes out/*.en.srt and refreshes chapter times in out/youtube_description.txt."""
import json, re
tl = json.load(open('timeline.json'))
NAME = {'MIA': 'Mia', 'ECHO': 'Echo', 'ELENA': 'Dr. Elena', 'OP': 'Radio', 'TECH': 'Technician'}


def ts(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"


out = []
for k, l in enumerate([l for l in tl['lines'] if not l.get('nosub')], 1):
    txt = l['text'] if l['speaker'] == 'N' else f"{NAME[l['speaker']]}: {l['text']}"
    out.append(f"{k}\n{ts(l['start'])} --> {ts(l['start'] + l['dur'] + 0.3)}\n{txt}\n")
open('out/The_Robot_That_Learned_to_Lie.en.srt', 'w').write('\n'.join(out))

d = open('out/youtube_description.txt').read()
for c in tl['chapters']:
    m, s = divmod(int(c['start']), 60)
    num, name = c['title']
    d = re.sub(rf"^\d+:\d\d {re.escape(num)} –", f"{m}:{s:02d} {num} –", d, flags=re.M)
open('out/youtube_description.txt', 'w').write(d)
print('ok')
