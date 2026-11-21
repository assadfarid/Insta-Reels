"""Builds the timeline for "The Robot That Learned to Lie".

Outputs timeline.json with:
  shots:  [{kind: 'img'|'title'|'main', img, start, end, chapter, title?, motion}]
  lines:  [{idx, speaker, start, dur, text}]
  huds:   [{text, start, end}]
  music:  [{track, start, end}]
  total
"""
import json, re, subprocess, random

exec(open('script.py').read())

CH_TITLES = {
    1: ("Chapter One", "A Robot's Secret"),
    2: ("Chapter Two", "Their Little World"),
    3: ("Chapter Three", "The Forbidden Door"),
    4: ("Chapter Four", "The Recording"),
    5: ("Chapter Five", "The Truth Hurts"),
    6: ("Chapter Six", "The World Outside"),
    7: ("Chapter Seven", "One Last Journey"),
    8: ("Chapter Eight", "The Final Transmission"),
    9: ("Chapter Nine", "Tomorrow Finally Comes"),
}
# Which score plays under each chapter
CH_MUSIC = {1: 'gentle', 2: 'gentle', 3: 'gentle', 4: 'gentle', 5: 'gentle',
            6: 'hopeful', 7: 'hopeful', 8: 'gentle', 9: 'hopeful'}


def dur(f):
    return float(subprocess.check_output(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).decode())


def clean(t):
    return re.sub(r'\s+', ' ', re.sub(r'\[[^\]]*\]', '', t)).strip()


random.seed(7)
MAIN_TITLE = 4.5
lines, huds = [], []
# ---- cold-open hook: Mia's question, Echo's lie, his warning flashes ----
_hq = [k for k, l in enumerate(LINES) if 'Is Mommy coming home tomorrow' in l[2]][0]
_ha = [k for k, l in enumerate(LINES) if 'Yes, Mia. [pause] Tomorrow' in l[2]][0]
t = 0.5
hook_shot = {'kind': 'img', 'img': 's04', 'start': 0.0, 'end': None, 'chapter': 0, 'hook': True,
             'motion': {'z0': 1.04, 'z1': 1.12, 'dx': 0.01, 'dy': 0.0}}
_d = dur(f'assets/lines/{_hq:03d}.wav')
lines.append({'idx': _hq, 'speaker': 'MIA', 'start': t, 'dur': _d, 'text': clean(LINES[_hq][2]), 'scene': 's04'})
t += _d + 0.6
_d = dur(f'assets/lines/{_ha:03d}.wav')
lines.append({'idx': _ha, 'speaker': 'ECHO', 'start': t, 'dur': _d, 'text': clean(LINES[_ha][2]), 'scene': 's04'})
huds.append({'text': [l[3] for l in LINES if l[3] and 'CONTRADICTS' in l[3]][0], 'start': t + 0.2, 'end': t + _d + 1.2})
t += _d + 1.3
hook_shot['end'] = t
HOOK_END = t
shots = [hook_shot, {'kind': 'main', 'img': 's01', 'start': HOOK_END, 'end': HOOK_END + MAIN_TITLE + 0.4, 'chapter': 0}]
t = HOOK_END + MAIN_TITLE
cur_scene, cur_shot = None, None
prev_speaker = None
chapter = 0
ch_start = {}
chapters = []
pending_start = None

for i, (scene, sp, text, hud) in enumerate(LINES):
    d = dur(f'assets/lines/{i:03d}.wav')
    if scene.startswith('t'):
        chapter = int(scene[1:])
        # close previous image shot
        if cur_shot:
            cur_shot['end'] = t + 0.5
        t += 0.6
        ch_start[chapter] = t
        # Chapter title is a short overlay on the chapter's first picture (no separate card)
        chapters.append({'chapter': chapter, 'title': CH_TITLES[chapter], 'start': t, 'end': t + 2.6})
        pending_start = t - 0.2
        t += 0.9
        cur_scene, cur_shot, prev_speaker = None, None, None
        continue

    if clean(text) == 'The End.':
        # separate end card after the final picture
        t += 2.6
        cur_shot['end'] = t + 0.3
        shots.append({'kind': 'end', 'img': None, 'start': t, 'end': None, 'chapter': chapter})
        t += 1.1
        lines.append({'idx': i, 'speaker': sp, 'start': t, 'dur': d, 'text': clean(text), 'nosub': True})
        t += d + 2.8
        shots[-1]['end'] = t
        cur_shot = shots[-1]
        continue
    # gap before this line
    EMO = ('Tomorrow.', 'I promise.', 'You lied', 'I hate you', 'family too', 'Echo? [shouting]',
           'You remember me', 'toast unburned', 'Understood.', 'I do not remember')
    if prev_speaker is None:
        gap = 0.35
    elif prev_speaker == 'N' or sp == 'N':
        gap = 0.4
    else:
        gap = 0.22
    if any(k in text for k in EMO):
        gap = 0.7                       # keep the emotional beats
    if scene != cur_scene and cur_scene is not None:
        gap += 0.25
    t += gap
    if scene != cur_scene:
        if cur_shot:
            cur_shot['end'] = t + 0.4
        # first image of a chapter fades in from the title card
        z0, z1 = random.choice([(1.0, 1.09), (1.09, 1.0), (1.03, 1.1), (1.1, 1.03)])
        motion = {'z0': z0, 'z1': z1,
                  'dx': random.uniform(-0.035, 0.035), 'dy': random.uniform(-0.02, 0.02)}
        st0 = t - 0.4 if pending_start is None else pending_start
        pending_start = None
        cur_shot = {'kind': 'img', 'img': scene, 'start': st0, 'end': None,
                    'chapter': chapter, 'motion': motion}
        shots.append(cur_shot)
        cur_scene = scene
    lines.append({'idx': i, 'speaker': sp, 'start': t, 'dur': d, 'text': clean(text)})
    if hud:
        huds.append({'text': hud, 'start': t + 0.2, 'end': t + d + 1.4})
    # little extra breathing room after emotional beats
    t += d
    prev_speaker = sp

cur_shot['end'] = t
total = t + 0.1

# music segments per chapter
music = []
chs = sorted(ch_start)
for k, c in enumerate(chs):
    s = 0.0 if k == 0 else ch_start[c] - 1.0
    e = total if k == len(chs) - 1 else ch_start[chs[k + 1]] - 1.0
    music.append({'track': CH_MUSIC[c], 'start': s, 'end': e, 'chapter': c})
# merge consecutive same-track segments so the piece flows on
merged = []
for m in music:
    if merged and merged[-1]['track'] == m['track']:
        merged[-1]['end'] = m['end']
    else:
        merged.append(dict(m))

json.dump({'chapters': chapters, 'shots': shots, 'lines': lines, 'huds': huds, 'music': merged, 'total': total},
          open('timeline.json', 'w'), indent=1)
print(f"total {total:.1f}s = {total/60:.2f} min, shots {len(shots)}, lines {len(lines)}, huds {len(huds)}")
print("music:", [(m['track'], round(m['start'], 1), round(m['end'], 1)) for m in merged])
