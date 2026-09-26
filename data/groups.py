import csv,json
from collections import defaultdict
rows=list(csv.DictReader(open('DoBIH_v18_6.csv',encoding='utf-8-sig',errors='replace')))
hdr=rows[0].keys()
def c(n):
    for h in hdr:
        if h.strip()==n: return h
CR,CC,CN,CM,CX,CY,CNUM=c('Region'),c('Country'),c('Name'),c('Metres'),c('Xcoord'),c('Ycoord'),c('Number')
def flag(r,code):
    col=c(code); return (r[col] or '').strip() not in ('','0')

out=[]

# ---------- DALES 30 ----------
# Hewitts inside the Yorkshire Dales NP: Pennine regions only, YDNP bbox.
# Nine Standards Rigg falls in the bbox but lies in the North Pennines AONB,
# outside the National Park boundary -> manual exclusion. Verified count 30.
EXCLUDE={'Nine Standards Rigg'}
dales=[]
for r in rows:
    if r[CC].strip()!='E' or not flag(r,'Hew'): continue
    reg=r[CR].strip()
    if not (reg.startswith('35A') or reg.startswith('35B')): continue
    try: x=float(r[CX]); y=float(r[CY])
    except: continue
    if not (334000<=x<=412000 and 456000<=y<=512000): continue
    if r[CN].strip() in EXCLUDE: continue
    dales.append({'ref':f"h{r[CNUM].strip()}",'name':r[CN].strip(),'m':float(r[CM])})
dales.sort(key=lambda d:-d['m'])
print(f"DALES 30 derived: {len(dales)} (target 30)")
out.append({'code':'DALES30','name':'Dales 30','area':'Yorkshire Dales',
            'derivation':'Hewitts in DoBIH regions 35A/35B within YDNP bbox, less Nine Standards Rigg (North Pennines AONB)',
            'count':len(dales),'peaks':dales})

# ---------- IRISH RANGES ----------
irish=defaultdict(list)
for r in rows:
    if r[CC].strip()!='I': continue
    irish[r[CR].strip()].append(r)
print(f"\nIRISH RANGES from DoBIH regions: {len(irish)}")
for reg in sorted(irish):
    hs=irish[reg]
    code='IE_'+reg.split(':')[0].strip()
    nm=reg.split(':',1)[1].strip()
    # notable = Arderin or HuMP (the two lists Irish baggers use most)
    notable=[h for h in hs if flag(h,'A') or flag(h,'Hu')]
    out.append({'code':code,'name':f"{nm}",'area':'Ireland','derivation':f'DoBIH region {reg}',
                'count':len(notable),'total_hills':len(hs),
                'peaks':[{'ref':f"h{h[CNUM].strip()}",'name':h[CN].strip(),
                          'm':float(h[CM]) if h[CM] else None} for h in notable]})
    print(f"  {code:8} {nm[:38]:40} notable={len(notable):>3} / {len(hs):>3} hills")

json.dump(out,open('groups.json','w'),indent=1)
print(f"\nTOTAL new challenges: {len(out)}")
