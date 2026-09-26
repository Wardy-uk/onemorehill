#!/usr/bin/env python3
"""MWIS-style hill forecast from MET Norway locationforecast/2.0.

Usage: python3 hill-forecast.py "Ben Nevis" [YYYY-MM-DD]
Requires an identifying User-Agent per MET Norway ToS.
"""
import json, sys, csv, datetime, urllib.parse, subprocess, os

UA = "OneMoreHill/0.1 (hill bagging app; contact via github)"
DOBIH = os.path.join(os.path.dirname(__file__), "..", "DoBIH_v18_6.csv")

def lookup(name):
    with open(DOBIH, encoding="utf-8-sig", errors="replace") as f:
        r = csv.DictReader(f); hdr = r.fieldnames
        col = lambda n: next(h for h in hdr if h.strip() == n)
        CN, CLAT, CLON, CM = col("Name"), col("Latitude"), col("Longitude"), col("Metres")
        for row in r:
            if row[CN].strip().lower().startswith(name.lower()):
                return row[CN].strip(), float(row[CLAT]), float(row[CLON]), float(row[CM])
    raise SystemExit(f"not found: {name}")

def fetch(lat, lon, alt):
    q = urllib.parse.urlencode({"lat": lat, "lon": lon, "altitude": int(alt)})
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/complete?{q}"
    out = subprocess.run(["curl", "-s", "--max-time", "30", "-A", UA, url],
                         capture_output=True, text=True).stdout
    return json.loads(out)

CARD = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
def card(d): return CARD[int((d + 11.25) % 360 // 22.5)]
def effect(mph):
    for lim, txt in [(13,"little effect on walking"), (19,"noticeable; exposed ridges breezy"),
                     (25,"buffeting on crests; care on narrow ground"),
                     (32,"difficult walking on exposed ground"),
                     (39,"seriously difficult; avoid exposed crests")]:
        if mph < lim: return txt
    return "dangerous on exposed ground"
def chill(T, ms):
    if ms * 3.6 <= 4.8: return T
    v = (ms * 3.6) ** 0.16
    return 13.12 + 0.6215*T - 11.37*v + 0.3965*T*v

# in cloud if near-saturated at summit height, or heavy low cloud
def in_cloud(spread, rh, low): return (spread < 1.0 and rh > 94) or low > 70
# lifted condensation level: ~125 m per °C of spread, above the forecast altitude
def cloud_base(alt, spread): return round(alt + spread * 125)

def report(name, date=None):
    nm, lat, lon, alt = lookup(name)
    d = fetch(lat, lon, alt)
    target = datetime.date.fromisoformat(date) if date else \
             datetime.date.today() + datetime.timedelta(days=1)
    rows = []
    for ts in d["properties"]["timeseries"]:
        t = datetime.datetime.fromisoformat(ts["time"].replace("Z", "+00:00"))
        if t.date() != target: continue
        x = ts["data"]["instant"]["details"]
        p = ((ts["data"].get("next_1_hours") or {}).get("details") or {}).get("precipitation_amount", 0)
        rows.append((t, x, p or 0))
    day = [r for r in rows if 6 <= r[0].hour <= 20] or rows
    if not day: raise SystemExit("no data for that date (10-day limit)")

    sp  = [r[1]["air_temperature"] - r[1]["dew_point_temperature"] for r in day]
    rh  = [r[1]["relative_humidity"] for r in day]
    low = [r[1]["cloud_area_fraction_low"] for r in day]
    T   = [r[1]["air_temperature"] for r in day]
    W   = [r[1]["wind_speed"] for r in day]
    ic  = [in_cloud(a,b,c) for a,b,c in zip(sp,rh,low)]
    free = round(100 * (1 - sum(ic)/len(ic)))
    mph = [w * 2.23694 for w in W]

    print(f"\n{nm.upper()}  —  {alt:.0f} m  —  {target:%A %d %B %Y}")
    print(f"MET Norway, issued {d['properties']['meta']['updated_at'][:16]}Z\n")
    print("HEADLINE")
    print("  " + ("Tops mostly clear. Good chance of views." if free >= 70 else
                  "Cloud on and off the tops. Views possible between banks." if free >= 30 else
                  "Summit in cloud for most of the day. Views unlikely."))
    print(f"\nCLOUD ON THE HILLS")
    print(f"  Cloud-free summit .... {free}%  ({sum(not i for i in ic)} of {len(ic)} daylight hours)")
    print(f"  Cloud base ........... {min(cloud_base(alt,s) for s in sp)}–{max(cloud_base(alt,s) for s in sp)} m")
    print(f"  Low cloud ............ {min(low):.0f}–{max(low):.0f}%")
    print(f"  Spread ............... {min(sp):.1f}–{max(sp):.1f} °C  (under 1.0 = in cloud)")
    print(f"\nHOW WINDY (at {alt:.0f} m)")
    print(f"  {min(mph):.0f}–{max(mph):.0f} mph from the {card(sum(r[1]['wind_from_direction'] for r in day)/len(day))}")
    print(f"  {effect(max(mph))}")
    print(f"\nHOW COLD")
    print(f"  {min(T):.0f} to {max(T):.0f} °C, feels like {min(chill(t,w) for t,w in zip(T,W)):.0f} °C")
    print(f"\nHOW WET")
    print(f"  {sum(r[2] for r in day):.1f} mm, {sum(1 for r in day if r[2] > 0.05)} of {len(day)} hours with rain")
    print(f"\nHOUR BY HOUR")
    for (t,x,p), s, l in list(zip(day, sp, low))[::3]:
        print(f"  {t:%H:%M}  base {cloud_base(alt,s):>5} m  low {l:>3.0f}%  "
              f"spread {s:>4.1f}°  {x['wind_speed']*2.23694:>4.0f} mph  "
              f"{x['air_temperature']:>5.1f}°  "
              f"{'IN CLOUD' if in_cloud(s, x['relative_humidity'], l) else 'clear'}")
    print()

if __name__ == "__main__":
    if len(sys.argv) < 2: raise SystemExit(__doc__)
    report(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
