import json
F = json.load(open('faces2.json'))
# (grid x, grid y) on the 0-10 grid of the padded head crop, facing: 'L' or 'R'
M = {
 ('s03','ECHO'):(4.5,6.5,'L'), ('s03','MIA'):(8.0,6.4,'R'), ('s04','ECHO'):(4.5,7.0,'L'),
 ('s07','ECHO'):(4.5,5.2,'L'), ('s07','MIA'):(4.6,6.1,'R'), ('s08','ECHO'):(3.6,6.0,'L'),
 ('s08','MIA'):(5.4,6.6,'R'), ('s09','ECHO'):(4.5,5.8,'L'), ('s09','MIA'):(4.4,6.7,'R'),
 ('s10','ECHO'):(4.0,6.0,'L'), ('s10','MIA'):(6.8,6.2,'R'), ('s11','MIA'):(7.7,6.5,'R'),
 ('s13','MIA'):(6.5,4.5,'R'), ('s14','ECHO'):(4.5,5.6,'L'), ('s14','MIA'):(6.0,7.0,'L'),
 ('s15','MIA'):(8.2,6.7,'R'), ('s16','ECHO'):(4.5,7.5,'L'), ('s18','MIA'):(6.5,7.5,'R'),
 ('s19','ECHO'):(4.5,7.6,'L'), ('s21','ECHO'):(5.5,5.0,'R'), ('s21','ELENA'):(4.4,7.3,'L'),
 ('s22','ECHO'):(4.6,6.5,'L'), ('s22','MIA'):(5.4,7.6,'R'), ('s24','MIA'):(6.8,8.2,'R'),
 ('s25','ECHO'):(5.0,6.4,'L'), ('s27','MIA'):(5.6,6.4,'R'), ('s28','ECHO'):(5.0,6.2,'R'),
 ('s28','MIA'):(3.3,3.6,'L'), ('s31','ECHO'):(4.3,6.0,'L'), ('s31','MIA'):(5.6,7.0,'R'),
 ('s32','MIA'):(4.6,6.0,'L'), ('s33','ECHO'):(4.4,3.0,'L'), ('s33','MIA'):(5.6,6.6,'R'),
 ('s34','MIA'):(6.5,5.5,'R'), ('s35','ECHO'):(4.5,6.0,'L'), ('s35','MIA'):(6.3,7.0,'R'),
 ('s38','ECHO'):(4.0,6.6,'L'), ('s38','MIA'):(5.4,6.8,'R'), ('s39','ECHO'):(3.8,6.6,'L'),
 ('s39','MIA'):(6.9,7.6,'R'), ('s41','ECHO'):(4.6,6.0,'L'), ('s42','ECHO'):(4.3,6.6,'L'),
 ('s42','MIA'):(6.4,7.6,'R'), ('s44','MIA'):(3.0,6.5,'L'), ('s45','MIA'):(6.4,7.6,'R'),
 ('s46','ECHO'):(4.5,6.0,'L'), ('s47','MIA'):(9.3,6.8,'R'), ('s50','TECH'):(1.2,5.8,'L'),
 ('s51','ECHO'):(4.3,6.0,'L'), ('s51','MIA'):(5.3,6.6,'R'), ('s52','MIA'):(8.1,6.6,'R'),
 ('s53','ECHO'):(5.0,6.4,'L'), ('s53','MIA'):(4.6,7.2,'R'), ('s54','ECHO'):(5.0,6.3,'L'),
}
out = {}
for (sc, sp), (gx, gy, fd) in M.items():
    x0, y0, x1, y1 = F[sc][sp]
    pw, ph = (x1 - x0) * 0.15, (y1 - y0) * 0.15
    X0, Y0, X1, Y1 = max(0, x0 - pw), max(0, y0 - ph), min(1, x1 + pw), min(1, y1 + ph)
    out[f'{sc}:{sp}'] = [X0 + gx / 10 * (X1 - X0), Y0 + gy / 10 * (Y1 - Y0), 1 if fd == 'R' else -1]
out['s37:MIA'] = [0.46, 0.45, 1]          # in the Gemini clip at "Echo!"
out['s43:OP'] = [0.70, 0.31, -1]          # radio speaker horn
out['s44:OP'] = [0.04, 0.70, 1]           # radio console (left edge)
json.dump(out, open('mouths.json', 'w'), indent=1)
exec(open('script.py').read())
need = {f'{sc}:{sp}' for sc, sp, tx, h in LINES if sc.startswith('s') and sp in ('MIA', 'ECHO', 'TECH', 'ELENA')}
print('missing', sorted(need - set(out)))

out['s22:MIA'] = [0.21, 0.33, 1]; out['s22:ECHO'] = [0.66, 0.17, -1]
json.dump(out, open('mouths.json', 'w'), indent=1)

out['s04:MIA'] = [0.86, 0.39, -1]
json.dump(out, open('mouths.json', 'w'), indent=1)
