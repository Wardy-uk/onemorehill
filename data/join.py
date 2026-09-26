import csv, math, json
from collections import defaultdict, Counter

# ---- load DoBIH
hills=[]
with open('DoBIH_v18_6.csv',encoding='utf-8-sig',errors='replace') as f:
    r=csv.DictReader(f); hdr=r.fieldnames
    def c(n):
        for h in hdr:
            if h.strip()==n: return h
    CX,CY,CN,CM,CG,CD = c('Xcoord'),c('Ycoord'),c('Name'),c('Metres'),c('Grid ref'),c('Drop')
    LISTS={'M':'Munro','C':'Corbett','G':'Graham','D':'Donald','W':'Wainwright',
           'WO':'Wainwright Outlying','E':'Ethel','Ma':'Marilyn','Hu':'HuMP','Tu':'TuMP',
           'Hew':'Hewitt','N':'Nuttall','CoU':'County Top','Sim':'Simm','B':'Birkett'}
    LCOL={k:c(k) for k in LISTS}
    for row in r:
        try: x=float(row[CX]); y=float(row[CY])
        except (TypeError,ValueError): continue
        try: m=float(row[CM])
        except (TypeError,ValueError): m=None
        mem={k for k,col in LCOL.items() if (row[col] or '').strip() not in ('','0')}
        # derived Fiona
        if 'G' in mem and m is not None and m>=609.6: mem.add('Fiona')
        hills.append({'x':x,'y':y,'n':row[CN].strip(),'m':m,'lists':mem})

# ---- load standing pillars
pil=[]
with open('trig/CompleteTrigArchive.csv',encoding='utf-8-sig',errors='replace') as f:
    for row in csv.DictReader(f):
        if row['TYPE OF MARK'].strip().upper()!='PILLAR': continue
        if row['DESTROYED MARK INDICATOR'].strip()=='1': continue
        try: x=float(row['EASTING']); y=float(row['NORTHING'])
        except (TypeError,ValueError): continue
        if x==0 or y==0: continue
        pil.append({'x':x,'y':y,'n':(row['Trig Name'] or '').strip(),'s':row['STATION NAME'].strip()})

print(f"hills with coords: {len(hills)}   standing pillars with coords: {len(pil)}\n")

# ---- grid index (1km cells)
CELL=1000
grid=defaultdict(list)
for i,h in enumerate(hills):
    grid[(int(h['x']//CELL), int(h['y']//CELL))].append(i)

def nearest(px,py,maxr=2000):
    best=None; bd=1e18
    rc=int(maxr//CELL)+1
    cx,cy=int(px//CELL),int(py//CELL)
    for dx in range(-rc,rc+1):
        for dy in range(-rc,rc+1):
            for i in grid.get((cx+dx,cy+dy),()):
                h=hills[i]
                d=math.hypot(h['x']-px,h['y']-py)
                if d<bd: bd=d; best=i
    return best,bd

res=[]
for p in pil:
    i,d=nearest(p['x'],p['y'])
    res.append((p,i,d))

# ---- distance distribution
BANDS=[5,10,25,50,100,250,500,1000,2000]
print("=== pillar → nearest DoBIH hill, cumulative ===")
prev=0
for b in BANDS:
    n=sum(1 for _,_,d in res if d<=b)
    print(f"  within {b:>5}m : {n:>5}  ({100*n/len(res):5.1f}%)   +{n-prev}")
    prev=n
print(f"  beyond 2000m : {sum(1 for _,_,d in res if d>2000)}")

# ---- how many hills in each launch list have a pillar within tolerance
print("\n=== hills with a standing pillar within N metres, by list ===")
NAMES={'M':'Munro','C':'Corbett','Fiona':'Fiona','D':'Donald','W':'Wainwright',
       'WO':'Wainwright Outly','E':'Ethel','Ma':'Marilyn','Hew':'Hewitt','N':'Nuttall',
       'CoU':'County Top','Hu':'HuMP','Sim':'Simm','B':'Birkett','Tu':'TuMP'}
tot=Counter()
for h in hills:
    for k in h['lists']: tot[k]+=1
for tol in (50,100,250):
    hit=Counter()
    seen=set()
    for p,i,d in res:
        if d<=tol and i not in seen:
            seen.add(i)
            for k in hills[i]['lists']: hit[k]+=1
    print(f"\n  --- tolerance {tol}m ---")
    for k in ['M','C','Fiona','D','W','WO','E','Ma','Hew','N','CoU']:
        t=tot.get(k,0); hgot=hit.get(k,0)
        if t: print(f"    {NAMES[k]:18} {hgot:>5} / {t:<6} ({100*hgot/t:5.1f}%)")

json.dump([{'pillar':p['n'],'station':p['s'],'hill':hills[i]['n'],'dist':round(d,1),
            'lists':sorted(hills[i]['lists'])} for p,i,d in res if d<=250],
          open('join_250m.json','w'), indent=1)
print(f"\nwrote join_250m.json ({sum(1 for _,_,d in res if d<=250)} pairs)")
