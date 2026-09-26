import csv, json, math
from collections import defaultdict, Counter

DOBIH_LISTS = {
 # code: (name, tier)
 'M':('Munro','classic'),'MT':('Munro Top','classic'),'F':('Furth','classic'),
 'Mur':('Murdo','classic'),'C':('Corbett','classic'),'CT':('Corbett Top','classic'),
 'G':('Graham','classic'),'GT':('Graham Top','classic'),'D':('Donald','classic'),
 'DT':('Donald Top','classic'),'DDew':('Donald Dewey','classic'),'Hew':('Hewitt','classic'),
 'N':('Nuttall','classic'),'Dew':('Dewey','classic'),'HF':('Highland Five','classic'),
 'W':('Wainwright','regional'),'WO':('Wainwright Outlying Fell','regional'),
 'B':('Birkett','regional'),'Sy':('Synge','regional'),'Fel':('Fellranger','regional'),
 'E':('Ethel','regional'),
 'Tu':('TuMP','relative'),'Hu':('HuMP','relative'),'Sim':('Simm','relative'),
 'Ma':('Marilyn','relative'),'HHB':('High Hill of Britain','relative'),'Y':('Yeaman','relative'),
 'CoU':('County / UA Top','county'),'CoH':('Historic County Top','county'),
 'CoA':('Administrative County Top','county'),'CoL':('London Borough Top','county'),
 'SIB':('Significant Island of Britain','island'),'T100':('Trail 100','other'),
 'A':('Arderin','ireland'),'VL':('Vandeleur-Lynam','ireland'),'Ca':('Carn','ireland'),
 'Bin':('Binnion','ireland'),'Dil':('Dillon','ireland'),
}

rows=list(csv.DictReader(open('DoBIH_v18_6.csv',encoding='utf-8-sig',errors='replace')))
hdr=rows[0].keys()
def c(n):
    for h in hdr:
        if h.strip()==n: return h
CN,CM,CX,CY,CC,CR,CNUM,CGR = c('Name'),c('Metres'),c('Xcoord'),c('Ycoord'),c('Country'),c('Region'),c('Number'),c('Grid ref')

def flag(row,code): 
    col=c(code); return (row[col] or '').strip() not in ('','0')
def met(row):
    try: return float(row[CM])
    except: return None

locations=[]; membership=defaultdict(set)
for row in rows:
    try: x=float(row[CX]); y=float(row[CY])
    except (TypeError,ValueError): continue
    m=met(row)
    lid=f"h{row[CNUM].strip()}"
    lists={code for code in DOBIH_LISTS if flag(row,code)}
    # ---- derived challenges
    if 'G' in lists and m is not None and m>=609.6: lists.add('FIONA')
    if 'F' in lists:
        cc=row[CC].strip()
        if cc=='W': lists.add('WELSH3000')
        elif cc=='I': lists.add('FURTH_IE')
        elif cc=='E': lists.add('FURTH_EN')
    locations.append({'id':lid,'name':row[CN].strip(),'x':x,'y':y,'m':m,
                      'country':row[CC].strip(),'region':row[CR].strip(),
                      'gr':row[CGR].strip(),'kind':'hill','lists':sorted(lists)})
    for l in lists: membership[l].add(lid)

# ---- National / Yorkshire Three Peaks
byc=defaultdict(list)
for L in locations:
    if L['m'] is not None: byc[L['country']].append(L)
for cc in ('S','E','W'):
    top=max(byc[cc],key=lambda L:L['m'])
    top['lists'].append('NAT3PEAKS'); membership['NAT3PEAKS'].add(top['id'])
for nm in ('Whernside','Ingleborough','Pen-y-ghent'):
    for L in locations:
        if L['name'].lower().startswith(nm.lower()):
            L['lists'].append('YORKS3PEAKS'); membership['YORKS3PEAKS'].add(L['id']); break

# ---- trig pillars + join
pillars=[]
for row in csv.DictReader(open('trig/CompleteTrigArchive.csv',encoding='utf-8-sig',errors='replace')):
    if row['TYPE OF MARK'].strip().upper()!='PILLAR': continue
    if row['DESTROYED MARK INDICATOR'].strip()=='1': continue
    try: x=float(row['EASTING']); y=float(row['NORTHING'])
    except (TypeError,ValueError): continue
    if x==0 or y==0: continue
    pillars.append({'id':'t'+row['STATION NAME'].strip(),'name':(row['Trig Name'] or '').strip(),
                    'x':x,'y':y,'kind':'trig','lists':['TRIG'],'coincident_with':None})
CELL=1000; grid=defaultdict(list)
for i,L in enumerate(locations): grid[(int(L['x']//CELL),int(L['y']//CELL))].append(i)
COINCIDENT=10.0
nco=0
for p in pillars:
    best=None;bd=1e18
    cx,cy=int(p['x']//CELL),int(p['y']//CELL)
    for dx in(-1,0,1):
        for dy in(-1,0,1):
            for i in grid.get((cx+dx,cy+dy),()):
                d=math.hypot(locations[i]['x']-p['x'],locations[i]['y']-p['y'])
                if d<bd: bd=d;best=i
    if best is not None and bd<=COINCIDENT:
        p['coincident_with']=locations[best]['id']; nco+=1
    p['nearest_hill']=locations[best]['id'] if best is not None else None
    p['nearest_m']=round(bd,1) if best is not None else None

DERIVED={'FIONA':'Fiona','WELSH3000':'Welsh 3000s','FURTH_IE':'Irish Furths',
 'FURTH_EN':'English Furths','NAT3PEAKS':'National Three Peaks','YORKS3PEAKS':'Yorkshire Three Peaks'}

challenges=[]
for code,(name,tier) in DOBIH_LISTS.items():
    challenges.append({'code':code,'name':name,'tier':tier,'source':'DoBIH v18.6','count':len(membership[code])})
for code,name in DERIVED.items():
    challenges.append({'code':code,'name':name,'tier':'derived','source':'derived from DoBIH','count':len(membership[code])})
challenges.append({'code':'TRIG','name':'Trig Pillars','tier':'trig','source':'OS Complete Trig Archive (OGL)','count':len(pillars)})

json.dump({'challenges':challenges,'generated':'2026-09-22',
           'dobih_version':'18.6','licence':'DoBIH CC BY 4.0; OS trig OGL'},
          open('challenges.json','w'),indent=1)
json.dump(locations,open('locations_hills.json','w'))
json.dump(pillars,open('locations_trigs.json','w'))

print(f"CHALLENGES: {len(challenges)}")
print(f"  DoBIH lists : {len(DOBIH_LISTS)}")
print(f"  derived     : {len(DERIVED)}")
print(f"  trig        : 1")
print(f"\nLOCATIONS: {len(locations)+len(pillars)}  ({len(locations)} hills + {len(pillars)} pillars)")
print(f"  pillars coincident with a summit (<={COINCIDENT:.0f}m): {nco}")
print(f"\n=== challenge registry ===")
for ch in sorted(challenges,key=lambda x:(x['tier'],-x['count'])):
    print(f"  {ch['tier']:9} {ch['code']:10} {ch['name'][:30]:32} {ch['count']:>6}")
