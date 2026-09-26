import csv,json,gzip,math
from collections import defaultdict
from osgb import en_to_wgs84

LN={'M':'Munros','MT':'Munro Tops','C':'Corbetts','CT':'Corbett Tops','GT':'Graham Tops',
 'FIONA':'Fionas','D':'Donalds','DT':'Donald Tops','DDew':'Donald Deweys','F':'Furths',
 'Mur':'Murdos','Hew':'Hewitts','N':'Nuttalls','Dew':'Deweys','HF':'Highland Fives',
 'W':'Wainwrights','WO':'Wainwright Outlying Fells','B':'Birketts','Sy':'Synges',
 'Fel':'Fellrangers','E':'Ethels','Ma':'Marilyns','Hu':'HuMPs','Tu':'TuMPs','Sim':'Simms',
 'HHB':'High Hills of Britain','Y':'Yeamans','CoU':'County Tops','CoH':'Historic County Tops',
 'CoA':'Administrative County Tops','CoL':'London Borough Tops','SIB':'Significant Islands',
 'T100':'Trail 100','A':'Arderins','VL':'Vandeleur-Lynams','Ca':'Carns','Bin':'Binnions',
 'Dil':'Dillons'}
GRP={**{c:'Scotland' for c in ['M','MT','C','CT','GT','FIONA','D','DT','DDew','Mur','HF','Y']},
 **{c:'Lake District' for c in ['W','WO','B','Sy','Fel']},'E':'Peak District',
 **{c:'England & Wales' for c in ['Hew','N','Dew','F']},
 **{c:'Relative height' for c in ['Ma','Hu','Tu','Sim','HHB']},
 **{c:'County tops' for c in ['CoU','CoH','CoA','CoL']},
 'SIB':'Islands','T100':'Other',
 **{c:'Ireland' for c in ['A','VL','Ca','Bin','Dil']}}

# lat/lon per hill, straight from DoBIH (handles Irish Grid for us)
LL={}
with open('DoBIH_v18_6.csv',encoding='utf-8-sig',errors='replace') as f:
    r=csv.DictReader(f); hdr=r.fieldnames
    col=lambda n:next(h for h in hdr if h.strip()==n)
    CNUM,CLAT,CLON=col('Number'),col('Latitude'),col('Longitude')
    for row in r:
        try: LL['h'+row[CNUM].strip()]=(float(row[CLAT]),float(row[CLON]))
        except: pass

hills=[h for h in json.load(open('locations_hills.json')) if h['id'] in LL]
trigs=json.load(open('locations_trigs.json'))
byid={h['id']:h for h in hills}
for t in trigs: t['ll']=en_to_wgs84(t['x'],t['y'])

# shared point table on a ~0.006° grid (≈600 m) — indexes into it everywhere
def key(la,lo): return (round(la/0.006), round(lo/0.010))
pts=[]; idx={}
def pid(la,lo):
    k=key(la,lo)
    if k not in idx: idx[k]=len(pts); pts.append(k)
    return idx[k]
for h in hills: h['_i']=pid(*LL[h['id']])
for t in trigs: t['_i']=pid(*t['ll'])

near=defaultdict(list)
for t in trigs:
    d,hid=t.get('nearest_m'),t.get('nearest_hill')
    if d is None or hid is None or d>250 or hid not in byid: continue
    near[hid].append((d,t['name'] or '(unnamed)'))
for k in near: near[k].sort()

def pack(a):
    out=[];prev=0
    for v in a:
        d=v-prev; prev=v
        out.append(('-' if d<0 else '')+format(abs(d),'x'))
    return ','.join(out)

ch={}
for code,name in LN.items():
    mem=[h for h in hills if code in h['lists']]
    if not mem: continue
    withp=[(h,near[h['id']][0]) for h in mem if h['id'] in near]
    w50=[x for x in withp if x[1][0]<=50]
    mem.sort(key=lambda h:-(h['m'] or 0))
    def row(h,tp):
        return {'h':h['name'],'g':h.get('gr',''),'m':h['m'],'r':h['region'],
                'd':round(tp[0],1),'t':tp[1],
                'l':sorted([c for c in h['lists'] if c in LN],key=lambda c:LN[c])}
    rows=sorted([row(h,tp) for h,tp in withp],key=lambda r:(-len(r['l']),r['d']))
    ch[code]={'n':name,'grp':GRP.get(code,'Other'),'tot':len(mem),
      'w10':sum(1 for x in withp if x[1][0]<=10),'w50':len(w50),'w250':len(withp),
      'pct':round(100*len(w50)/len(mem),1),'hi':mem[0]['name'],'hiM':round(mem[0]['m'] or 0),
      'pts':sorted(h['_i'] for h in mem),'hit':sorted(h['_i'] for h,_ in w50),
      '_rows':rows[:600],
      '_far':sorted([row(h,tp) for h,tp in withp if 50<tp[0]<=250],key=lambda r:r['d'])[:14]}

onhill=[t for t in trigs if (t.get('nearest_m') or 9e9)<=50]
ch['TRIG']={'n':'Trig Pillars','grp':'Trig points','tot':len(trigs),
  'w10':sum(1 for t in trigs if (t.get('nearest_m') or 9e9)<=10),'w50':len(onhill),
  'w250':sum(1 for t in trigs if (t.get('nearest_m') or 9e9)<=250),
  'pct':round(100*len(onhill)/len(trigs),1),'hi':'Ben Nevis','hiM':1345,
  'pts':sorted(t['_i'] for t in trigs),'hit':sorted(t['_i'] for t in onhill),
  '_rows':sorted([{'h':byid[t['nearest_hill']]['name'],'g':byid[t['nearest_hill']].get('gr',''),
     'm':byid[t['nearest_hill']]['m'],'r':byid[t['nearest_hill']]['region'],
     'd':round(t['nearest_m'],1),'t':t['name'] or '(unnamed)',
     'l':sorted([c for c in byid[t['nearest_hill']]['lists'] if c in LN],key=lambda c:LN[c])}
     for t in onhill],key=lambda r:(-len(r['l']),r['d']))[:600],'_far':[]}

json.dump({'ln':LN,'ch':{c:{'n':ch[c]['n'],'rows':ch[c]['_rows'],'far':ch[c]['_far']} for c in ch}},
          open('../site/rows.json','w'),separators=(',',':'))
for c in ch:
    ch[c]['top']=ch[c]['_rows'][:8]; ch[c]['nfar']=len(ch[c]['_far'])
    del ch[c]['_rows'], ch[c]['_far']
    ch[c]['pts']=pack(ch[c]['pts']); ch[c]['hit']=pack(ch[c]['hit'])

doc={'gen':'2026-09-26','grid':[0.006,0.010],
     'pts':pack([v for k in pts for v in k]),
     'stats':{'hills':len(hills),'pillars':len(trigs),
       'c10':sum(1 for t in trigs if (t.get('nearest_m') or 9e9)<=10),
       'far2':sum(1 for t in trigs if (t.get('nearest_m') or 9e9)>2000)},
     'ln':LN,'order':sorted(ch,key=lambda c:-ch[c]['tot']),'ch':ch}
json.dump(doc,open('../site/data.json','w'),separators=(',',':'))
for f in ['../site/data.json','../site/rows.json']:
    b=open(f,'rb').read()
    print(f"  {f.split('/')[-1]:12} raw {len(b)/1024:6.0f} KB  gzip {len(gzip.compress(b,9))/1024:5.0f} KB")
print(f"  challenges {len(ch)}  grid points {len(pts)}")
