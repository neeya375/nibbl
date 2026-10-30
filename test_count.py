import urllib.request, urllib.parse, ssl, json, time, sys
sys.stdout.reconfigure(encoding='utf-8')
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = "NibblBot/1.0 (https://example.com; contact@kilo.local) Python-urllib"

def ov_post(q, timeout=90):
    data = urllib.parse.urlencode({"data": q}).encode()
    req = urllib.request.Request("https://overpass.kumi.systems/api/interpreter", data=data,
                                 headers={"User-Agent": UA, "Accept": "application/json",
                                          "Content-Type":"application/x-www-form-urlencoded"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout, context=ctx).read())

BBOX = "12.85,77.40,13.10,77.95"

# COUNT
print("=== count (restaurant|cafe|fast_food|bar) ===")
try:
    t=time.time()
    r = ov_post(f'[out:json][timeout:90];(node["amenity"="restaurant"]({BBOX});node["amenity"="cafe"]({BBOX});node["amenity"="fast_food"]({BBOX});node["amenity"="bar"]({BBOX}););out count;')
    print(f"  count query took {time.time()-t:.1f}s")
    print("  raw:", json.dumps(r)[:300])
    elems = r.get("elements", [])
    for e in elems: print("  element:", json.dumps(e)[:200])
except Exception as e:
    print("  count FAIL:", repr(e)[:160])

# FETCH 40 elements timing
print("\n=== fetch 40 (out center 40) ===")
try:
    t=time.time()
    r = ov_post(f'[out:json][timeout:90];(node["amenity"="restaurant"]({BBOX});node["amenity"="cafe"]({BBOX}););out center 40;')
    print(f"  fetch took {time.time()-t:.1f}s, count={len(r.get('elements',[]))}")
    has_wd=0; has_cuisine=0; has_city=0
    for e in r.get("elements",[]):
        t2=e.get("tags",{})
        if t2.get("wikidata"): has_wd+=1
        if t2.get("cuisine"): has_cuisine+=1
        if t2.get("addr:city") or t2.get("addr:suburb") or t2.get("addr:neighbourhood"): has_city+=1
    print(f"  tags -> wikidata:{has_wd} cuisine:{has_cuisine} area:{has_city}")
except Exception as e:
    print("  fetch FAIL:", repr(e)[:160])
