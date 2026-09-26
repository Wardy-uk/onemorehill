import csv,json,math
from collections import defaultdict

LISTNAME={'M':'Munro','MT':'Munro Top','C':'Corbett','G':'Graham','FIONA':'Fiona','D':'Donald',
 'DT':'Donald Top','F':'Furth','Mur':'Murdo','CT':'Corbett Top','GT':'Graham Top','DDew':'Donald Dewey',
 'Hew':'Hewitt','N':'Nuttall','Dew':'Dewey','HF':'Highland Five','W':'Wainwright',
 'WO':'Wainwright Outlying','B':'Birkett','Sy':'Synge','Fel':'Fellranger','E':'Ethel',
 'Tu':'TuMP','Hu':'HuMP','Sim':'Simm','Ma':'Marilyn','HHB':'High Hill of Britain','Y':'Yeaman',
 'CoU':'County Top','CoH':'Historic County Top','CoA':'Admin County Top','CoL':'London Borough Top',
 'SIB':'Significant Island','T100':'Trail 100','A':'Arderin','VL':'Vandeleur-Lynam','Ca':'Carn',
 'Bin':'Binnion','Dil':'Dillon'}
# lists people actually bag - used for the "jackpot" score
BAGGED={'M','MT','C','FIONA','D','F','Hew','N','Dew','W','WO','B','Sy','Fel','E','Ma','Hu','Sim','HHB','CoU','SIB','T100','Mur','HF'}

hills=json.load(open('locations_hills.json'))
trigs=json.load(open('locations_trigs.json'))
byid={h['id']:h for h in hills}

pairs=[]
for t in trigs:
    if not t.get('nearest_hill'): continue
    d=t.get('nearest_m')
    if d is None or d>250: continue
    h=byid.get(t['nearest_hill'])
    if not h: continue
    ls=[l for l in h['lists'] if l in LISTNAME]
    bag=[l for l in ls if l in BAGGED]
    pairs.append({'t':t['name'] or '(unnamed)','h':h['name'],'d':round(d,1),
                  'm':h['m'],'c':h['country'],'r':h['region'],'g':h.get('gr',''),
                  'l':sorted(bag,key=lambda x:LISTNAME[x]),'n':len(bag)})
pairs.sort(key=lambda p:(-p['n'],p['d']))

cov={}
for code in ['E','C','Ma','FIONA','CoU','D','N','M','Hew','W','WO','Hu','Sim','B']:
    tot=sum(1 for h in hills if code in h['lists'])
    if not tot: continue
    got=len({t['nearest_hill'] for t in trigs
             if t.get('nearest_m') is not None and t['nearest_m']<=50
             and t.get('nearest_hill') and code in byid.get(t['nearest_hill'],{}).get('lists',[])})
    cov[LISTNAME[code]]={'with':got,'total':tot,'pct':round(100*got/tot,1)}

coincident=sum(1 for t in trigs if t.get('nearest_m') is not None and t['nearest_m']<=10)
far=sum(1 for t in trigs if t.get('nearest_m') is None or t['nearest_m']>2000)

out={'generated':'2026-09-24','dobih':'v18.6',
     'stats':{'hills':len(hills),'pillars':len(trigs),'coincident10':coincident,
              'within50':sum(1 for t in trigs if t.get('nearest_m') is not None and t['nearest_m']<=50),
              'far2km':far},
     'listnames':LISTNAME,'coverage':cov,'pairs':pairs[:3000]}
json.dump(out,open('../site/data.json','w'),separators=(',',':'))
import os,gzip
b=open('../site/data.json','rb').read()
print(f"pairs: {len(pairs)}  (writing top 3000)")
print(f"data.json: {len(b)/1024:.0f} KB raw, {len(gzip.compress(b,9))/1024:.0f} KB gzipped")
print(f"coincident<=10m: {coincident}   within 50m: {out['stats']['within50']}   >2km: {far}")
print("\ntop jackpots:")
for p in pairs[:6]:
    print(f"  {p['n']} lists  {p['d']:>5}m  {p['h'][:34]:36} {','.join(LISTNAME[x] for x in p['l'][:5])}")
