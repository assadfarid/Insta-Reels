import json,sys,subprocess,os
f=sys.argv[1]
d=json.load(open(f))
m={}
for line in open('sessions_img.txt'):
    k,s=line.split(); m[s]=k
for g in d['generations']:
    url=g.get('content_url'); 
    if g['status']!='completed' or not url: print('not ready',g['id'],g['status']); continue
    sess=url.split('content_generation/')[1].split('/')[0]
    if 'music' in g['model_id']: name='assets/audio_raw/music_hopeful.mp3'
    elif sess in m: name=f'assets/img/{m[sess]}.png'
    else: print('unknown',sess); continue
    if os.path.exists(name) and os.path.getsize(name)>0: continue
    r=subprocess.run(['curl','-sf','--retry','3','-o',name,url])
    print(name, 'ok' if r.returncode==0 else 'FAIL')
