import json,re,unicodedata
def norm(s):
    s=unicodedata.normalize('NFKD',s); s=''.join(c for c in s if not unicodedata.combining(c))
    s=s.lower(); s=re.sub(r'\[[^\]]*\]','',s); s=re.sub(r'\([^)]*\)','',s)
    s=re.sub(r"[^a-z0-9 ]",' ',s); return re.sub(r'\s+',' ',s).strip()
hills=json.load(open('locations_hills.json'))
idx={}
for h in hills:
    idx.setdefault(norm(h['name']),[]).append(h)
    for alt in re.findall(r'\[([^\]]+)\]',h['name']): idx.setdefault(norm(alt),[]).append(h)
def match(n,bbox=None):
    k=norm(n); c=idx.get(k)
    if not c: c=[h for kk,v in idx.items() if kk.startswith(k+' ') for h in v]
    if not c: c=[h for kk,v in idx.items() if k and k in kk for h in v]
    if c and bbox:
        x0,y0,x1,y1=bbox
        f=[h for h in c if x0<=h['x']<=x1 and y0<=h['y']<=y1]
        if f: c=f
    return max(c,key=lambda x:(x['m'] or 0)) if c else None

SETS=[
 ('NAT3PEAKS','National Three Peaks','GB',
  ['Ben Nevis','Scafell Pike','Snowdon'],'highest in Scotland, England, Wales'),
 ('YORKS3PEAKS','Yorkshire Three Peaks','Yorkshire Dales',
  ['Whernside','Ingleborough','Pen-y-ghent'],'classic 24-mile circuit, <12 hours'),
 ('WELSH3PEAKS','Welsh Three Peaks','Wales',
  ['Snowdon','Cadair Idris','Pen y Fan'],'highest of Eryri, Cadair, Bannau Brycheiniog'),
 ('LAKES3PEAKS','Lake District Three Peaks','Lake District',
  ['Scafell Pike','Helvellyn','Skiddaw'],'the three Lakeland 3000-ers / classics'),
 ('DERBY3PEAKS','Derbyshire Three Peaks','Peak District',
  ['Kinder Scout','Bleaklow','Higher Shelf Stones'],'~21 miles, 10 hour limit'),
 ('SURREY3PEAKS','Surrey Three Peaks','Surrey Hills',
  ['Leith Hill','Holmbury Hill','Box Hill'],'~23 miles, 1,060m ascent'),
 ('LEICS3PEAKS','Leicestershire Three Peaks','Charnwood Forest',
  ['Bardon Hill','Beacon Hill','Old John Tower'],'~16 miles circular; Bardon Hill is the county top',
  (440000,305000,460000,320000)),
 ('NAT4PEAKS','National Four Peaks','UK',
  ['Ben Nevis','Scafell Pike','Snowdon','Slieve Donard'],'adds Northern Ireland'),
 ('NAT5PEAKS','Five Peaks Challenge','UK & Ireland',
  ['Ben Nevis','Scafell Pike','Snowdon','Slieve Donard','Carrauntoohil'],'usually within 48 hours'),
]
out=[]
for entry in SETS:
    code,name,area,peaks,note = entry[:5]
    bbox = entry[5] if len(entry)>5 else None
    ms=[];miss=[]
    for p in peaks:
        h=match(p,bbox)
        if h: ms.append({'name':p,'ref':h['id'],'dobih':h['name'],'m':h['m']})
        else: miss.append(p)
    out.append({'code':code,'name':name,'area':area,'note':note,
                'count':len(peaks),'matched':len(ms),'peaks':ms,'unmatched':miss})
    flag='' if not miss else '  MISSING: '+', '.join(miss)
    print(f"{name:28} {len(ms)}/{len(peaks)}{flag}")
    for m in ms: print(f"      {m['m']:7.1f}m  {m['dobih'][:40]}")
json.dump(out,open('peaksets.json','w'),indent=1)
