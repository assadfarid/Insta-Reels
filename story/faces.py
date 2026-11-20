"""All known face positions per dialogue scene (normalised source coords)."""
import json, cv2
exec(open('anchors.py').read().split("out = {}")[0])   # reuse detectors + pairs
anch = json.load(open('anchors.json'))
scenes = sorted({sc for sc, sp in pairs})
faces = {}
for sc in scenes:
    im = cv2.cvtColor(cv2.imread(f'assets/img/{sc}.png'), cv2.COLOR_BGR2RGB)
    pts = {}
    for k, v in anch.items():
        s, sp = k.split(':')
        if s == sc and v and sp != 'OP':
            pts[sp] = v
    if 'MIA' not in pts:
        m = mia_head(im)
        if m: pts['MIA'] = m
    if 'ECHO' not in pts:
        e = echo_head(im)
        if e: pts['ECHO'] = e
    faces[sc] = pts
# known extra faces
faces.setdefault('s50', {})['TECH'] = [0.78, 0.22]
faces['s21']['ELENA'] = [0.60, 0.33]
json.dump(faces, open('faces.json', 'w'), indent=1)
print(faces['s07'], faces['s21'], faces['s50'])
