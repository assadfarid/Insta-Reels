import subprocess, re, itertools, math
exec(open('groups.py').read())
def est(t):
    p=len(re.findall(r'\[(short )?pause\]',t))
    c=len(re.sub(r'\[[^\]]*\]','',t).strip())
    return c/14.0+0.7*p+0.3
rep=[]
for (ch,sp),idxs in GROUPS.items():
    src=f"assets/audio_raw/{ch}_{sp}.mp3"
    dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',src]).decode())
    log=subprocess.run(['ffmpeg','-hide_banner','-i',src,'-af','silencedetect=noise=-42dB:d=0.2','-f','null','-'],capture_output=True,text=True).stderr
    S=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',log)]; E=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',log)]
    sil=[(s,e) for s,e in zip(S,E) if s>0.05 and e<dur-0.05]
    n=len(idxs); ex=[est(LINES[i][2]) for i in idxs]
    # leading/trailing silence
    best=None
    cands=sorted(sil,key=lambda x:x[1]-x[0],reverse=True)[:min(len(sil),n+8)]
    cands=sorted(cands)
    for combo in itertools.combinations(cands,n-1):
        b=[0]+[(s+e)/2 for s,e in combo]+[dur]
        segs=[b[k+1]-b[k]-((combo[k-1][1]-combo[k-1][0])/2 if k>0 else 0)-((combo[k][1]-combo[k][0])/2 if k<n-1 else 0) for k in range(n)]
        tot=sum(segs); exs=sum(ex)
        cost=sum(math.log(max(sg,0.1)/(e*tot/exs))**2 for sg,e in zip(segs,ex)) - 1.5*sum(e-s for s,e in combo)
        if best is None or cost<best[0]: best=(cost,combo)
    combo=best[1]; bounds=[0]+[(s+e)/2 for s,e in combo]+[dur]
    rep.append(f"{ch}_{sp}: n={n} gaps={[round(e-s,2) for s,e in combo]}")
    for k,i in enumerate(idxs):
        subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{bounds[k]}','-to',f'{bounds[k+1]}','-i',src,
          '-af','silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse,afade=t=in:d=0.02',
          '-ar','44100','-ac','1',f"assets/lines/{i:03d}.wav"],check=True)
print("\n".join(rep))
