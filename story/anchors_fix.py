import json
a = json.load(open('anchors_auto.json'))
fix = {
 's03:MIA': (0.22, 0.55), 's09:ECHO': (0.66, 0.42), 's10:MIA': (0.25, 0.36), 's13:MIA': (0.34, 0.64),
 's14:MIA': (0.20, 0.22), 's14:ECHO': (0.43, 0.25), 's16:ECHO': (0.63, 0.42), 's18:MIA': (0.26, 0.20),
 's21:ELENA': (0.60, 0.31), 's21:ECHO': (0.33, 0.71), 's22:ECHO': (0.58, 0.20), 's24:MIA': (0.33, 0.20),
 's27:MIA': (0.34, 0.20), 's28:MIA': (0.74, 0.69), 's33:ECHO': (0.33, 0.44), 's39:ECHO': (0.54, 0.31),
 's41:ECHO': (0.60, 0.33), 's42:MIA': (0.30, 0.49), 's43:OP': (0.86, 0.18), 's44:OP': (0.08, 0.49),
 's46:ECHO': (0.55, 0.22), 's47:MIA': (0.15, 0.31), 's50:TECH': (0.78, 0.22),
}
a.update({k: list(v) for k, v in fix.items()})
missing = [k for k, v in a.items() if not v]
print('missing:', missing)
json.dump(a, open('anchors.json', 'w'), indent=1)
