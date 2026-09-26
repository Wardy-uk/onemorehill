import json,re,unicodedata

def norm(s):
    s=unicodedata.normalize('NFKD',s); s=''.join(c for c in s if not unicodedata.combining(c))
    s=s.lower(); s=re.sub(r'\[[^\]]*\]','',s); s=re.sub(r'\([^)]*\)','',s)
    s=s.replace('&','and'); s=re.sub(r"[^a-z0-9 ]",' ',s); return re.sub(r'\s+',' ',s).strip()

ALIAS={'garnedd ugain':'crib y ddysgl','pigeon rock north top':'pigeon rock north',
       'cock mountain ne top':'cock mountain','lowerman':'helvellyn lower man',
       'pike o stickle':'pike of stickle','carnedd moel siabod':'moel siabod',
       'binnian north tor':'slieve binnian north tor','elidir fach':'elidir fawr west top','lugnaquilla':'lugnaquillia mountain','sgorr an iubhair':'sgurr an iubhair'}

# OSGB grid ref -> easting/northing
GL="ABCDEFGHJKLMNOPQRSTUVWXYZ"
def gr2en(gr):
    gr=gr.replace(' ','').upper()
    m=re.match(r'^([A-Z]{2})(\d+)$',gr)
    if not m: return None
    l,dg=m.group(1),m.group(2)
    if len(dg)%2: return None
    i0,i1=GL.index(l[0]),GL.index(l[1])
    e=((i0-2)%5)*5-10; n=(4-(i0-2)//5)*5-5
    e=e*100000+ (i1%5)*100000
    n=n*100000+ (4-i1//5)*100000
    half=len(dg)//2
    f=10**(5-half)
    return e+int(dg[:half])*f, n+int(dg[half:])*f

hills=json.load(open('locations_hills.json'))
idx={}
for h in hills:
    idx.setdefault(norm(h['name']),[]).append(h)
    for alt in re.findall(r'\[([^\]]+)\]',h['name']): idx.setdefault(norm(alt),[]).append(h)

def extract(slug):
    wt=json.load(open(f'rounds/{slug}.json'))['parse']['wikitext']
    rows=[]
    for m in re.finditer(r'\|\s*align="center"\s*\|\s*(\d+)\s*\|\|\s*align="left"\s*\|(.+)',wt):
        seq=int(m.group(1)); full=m.group(2)
        cell=full.split('||')[0]
        gr=None
        gm=re.search(r'\b([A-Z]{2}\s?\d{4,10})\b',full)
        if gm: gr=gm.group(1)
        link=re.search(r'\[\[([^\]]+)\]\]',cell)
        name=link.group(1).split('|')[-1].strip() if link else re.sub(r"'''|\|.*$",'',cell).strip()
        rows.append((seq,name,gr))
    seen=set(); out=[]
    for s,n,g in rows:
        if s in seen: continue
        seen.add(s); out.append((s,n,g))
    return sorted(out)

ROUNDS={'Ramsay_Round':('Ramsay Round','Lochaber'),
        'Wicklow_Round':('Wicklow Round','Wicklow Mountains'),
        'Bob_Graham_Round':('Bob Graham Round','Lake District'),
        'Paddy_Buckley_Round':('Paddy Buckley Round','Eryri / Snowdonia'),
        'Denis_Rankin_Round':('Denis Rankin Round','Mourne Mountains'),
        'South_Wales_Traverse':('South Wales Traverse','South Wales')}

out=[]; supp=[]; sid=0
for slug,(name,area) in ROUNDS.items():
    peaks=[];miss=[]
    for seq,disp,gr in extract(slug):
        key=ALIAS.get(norm(disp),norm(disp))
        cand=idx.get(key)
        if not cand:
            pre=[h for k,v in idx.items() if k.startswith(key+' ') for h in v]
            cand=pre or None
        if cand:
            h=max(cand,key=lambda x:(x['m'] or 0))
            peaks.append({'seq':seq,'name':disp,'ref':h['id'],'dobih':h['name']})
        else:
            sid+=1; ref=f"r{sid}"
            en=gr2en(gr) if gr else None
            supp.append({'id':ref,'name':disp,'gr':gr,
                         'x':en[0] if en else None,'y':en[1] if en else None,
                         'source':'round summit, not in DoBIH'})
            peaks.append({'seq':seq,'name':disp,'ref':ref,'dobih':None})
            miss.append(disp)
    out.append({'code':slug.upper(),'name':name,'area':area,'summits':len(peaks),
                'in_dobih':sum(1 for p in peaks if p['dobih']),'peaks':peaks})
    print(f"{name:26} {len(peaks):>3} summits  |  {sum(1 for p in peaks if p['dobih']):>3} in DoBIH  |  {len(miss)} supplementary")
    for m_ in miss: print(f"      + {m_}")

json.dump({'rounds':out,'supplementary_locations':supp},open('rounds_final.json','w'),indent=1)
t=sum(r['summits'] for r in out); d=sum(r['in_dobih'] for r in out)
print(f"\nTOTAL {t} summits · {d} in DoBIH ({100*d/t:.0f}%) · {len(supp)} supplementary locations")
print(f"supplementary with resolved coords: {sum(1 for s in supp if s['x'])}/{len(supp)}")
