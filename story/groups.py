exec(open('script.py').read())
VOICES={'N':'N5OEakgvy8bwbFcXZzJ8','MIA':'nDJIICjR9zfJExIFeSCN','ECHO':'bAq8AI9QURijOtmeFFqT','ELENA':'itMkRQx56fOF4CJe1D0C','OP':'wUwsnXivqGrDWuz1Fc89','TECH':'FmtiHEcHpocK7YiZwa46'}
ch=0; GROUPS={}
for i,(sc,sp,tx,h) in enumerate(LINES):
    if sc.startswith('t'): ch=int(sc[1:])
    GROUPS.setdefault((ch,sp),[]).append(i)
SEP="\n\n[long pause]\n\n"
def gtext(k): return SEP.join(LINES[i][2] for i in GROUPS[k])
