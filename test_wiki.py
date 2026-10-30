import urllib.request, urllib.parse, ssl, json, time, sys
sys.stdout.reconfigure(encoding='utf-8')
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = "NibblBot/1.0 (https://example.com; contact@kilo.local) Python-urllib"

def get(url, headers=None, timeout=25):
    h = {"User-Agent": UA, "Accept-Language":"en"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    return urllib.request.urlopen(req, timeout=timeout, context=ctx).read()

# 1) Category members: Restaurants in Bangalore / Karnataka
print("=== Wikipedia category members ===")
for cat in ["Restaurants in Bangalore", "Restaurants in Karnataka", "Eating establishments in Bangalore"]:
    sp = urllib.parse.urlencode({"action":"query","list":"categorymembers","cmtitle":f"Category:{cat}","cmlimit":"200","format":"json"})
    try:
        obj = json.loads(get("https://en.wikipedia.org/w/api.php?"+sp))
        members = obj.get("query",{}).get("categorymembers",[])
        print(f"  Category:{cat} -> {len(members)} members")
        for m in members[:6]: print("     -", m.get("title"))
    except Exception as e:
        print(f"  Category:{cat} -> FAIL {repr(e)[:80]}")

# 2) REST summary for a known restaurant article -> thumbnail + extract
print("\n=== Wikipedia REST summary (thumbnail) ===")
for title in ["Koshy%27s", "MTR (restaurant)", "Vidyarthi_Bhavan", "Karavalli_(restaurant)"]:
    try:
        t0=time.time()
        obj = json.loads(get(f"https://en.wikipedia.org/api/rest_v2/page/summary/{title}", timeout=20))
        thumb = obj.get("thumbnail",{}).get("source","")
        extract = (obj.get("extract","") or "")[:60]
        print(f"  {title}: thumb={'yes' if thumb else 'no'} | {extract}  ({time.time()-t0:.1f}s)")
        if thumb: print("     img:", thumb[:90])
    except Exception as e:
        print(f"  {title}: FAIL {repr(e)[:100]}")
