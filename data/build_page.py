import csv, json, math, gzip
from collections import defaultdict

LISTNAME={'M':'Munros','MT':'Munro Tops','C':'Corbetts','FIONA':'Fionas','D':'Donalds',
 'F':'Furths','Mur':'Murdos','Hew':'Hewitts','N':'Nuttalls','Dew':'Deweys','HF':'Highland Fives',
 'W':'Wainwrights','WO':'Wainwright Outlying Fells','B':'Birketts','Sy':'Synges',
 'Fel':'Fellrangers','E':'Ethels','Ma':'Marilyns','Hu':'HuMPs','Sim':'Simms',
 'HHB':'High Hills of Britain','CoU':'County Tops','SIB':'Significant Islands','T100':'Trail 100',
 'A':'Arderins','VL':'Vandeleur-Lynams','Ca':'Carns','Bin':'Binnions','Dil':'Dillons'}
# challenges offered in the picker — ones people actually work on
PICK=['W','E','M','C','FIONA','Ma','Hew','N','D','CoU','Hu','B','WO','T100','A','Sim']

hills=json.load(open('locations_hills.json'))
trigs=json.load(open('locations_trigs.json'))
byid={h['id']:h for h in hills}

# pillar → nearest hill, within 250m
near=defaultdict(list)
for t in trigs:
    d=t.get('nearest_m'); hid=t.get('nearest_hill')
    if d is None or hid is None or d>250: continue
    near[hid].append((d, t['name'] or '(unnamed)'))
for k in near: near[k].sort()

out={}
for code in PICK:
    mem=[h for h in hills if code in h['lists']]
    if not mem: continue
    mem.sort(key=lambda h:-(h['m'] or 0))
    withp=[(h,near[h['id']][0]) for h in mem if h['id'] in near]
    w50=[x for x in withp if x[1][0]<=50]
    w10=[x for x in withp if x[1][0]<=10]
    # skyline: up to 140 heights, evenly sampled across the list sorted by height
    hs=[h['m'] for h in mem if h['m']]
    step=max(1, len(hs)//140)
    sky=[round(x) for x in hs[::step]][:140]
    # the ones worth naming
    def row(h,tp):
        return {'h':h['name'],'g':h.get('gr',''),'m':h['m'],'r':h['region'],
                'd':round(tp[0],1),'t':tp[1],
                'l':sorted([c for c in h['lists'] if c in LISTNAME],key=lambda c:LISTNAME[c]),
                'n':len([c for c in h['lists'] if c in LISTNAME])}
    rows=[row(h,tp) for h,tp in withp]
    rows.sort(key=lambda r:(-r['n'], r['d']))
    # pillars that are NOT on the summit — the misleading ones
    far=sorted([row(h,tp) for h,tp in withp if 50<tp[0]<=250], key=lambda r:r['d'])
    out[code]={'name':LISTNAME[code],'total':len(mem),
               'with50':len(w50),'with10':len(w10),'with250':len(withp),
               'pct50':round(100*len(w50)/len(mem),1),
               'hi':mem[0]['name'],'hiM':mem[0]['m'],
               'lo':mem[-1]['name'],'loM':mem[-1]['m'],
               'sky':sky,'rows':rows[:400],'far':far[:12]}

stats={'hills':len(hills),'pillars':len(trigs),
       'coincident10':sum(1 for t in trigs if (t.get('nearest_m') or 9e9)<=10),
       'within50':sum(1 for t in trigs if (t.get('nearest_m') or 9e9)<=50),
       'far2km':sum(1 for t in trigs if (t.get('nearest_m') or 9e9)>2000)}
doc={'generated':'2026-09-26','dobih':'v18.6','stats':stats,
     'order':[c for c in PICK if c in out],'ch':out}
json.dump(doc,open('../site/data.json','w'),separators=(',',':'))
b=open('../site/data.json','rb').read()
print(f"challenges: {len(out)}   raw {len(b)/1024:.0f} KB   gzip {len(gzip.compress(b,9))/1024:.0f} KB")
for c in doc['order'][:6]:
    o=out[c]; print(f"  {o['name']:26} {o['with50']:>4}/{o['total']:<6} {o['pct50']:>5}%  sky {len(o['sky'])}  far {len(o['far'])}")
