import urllib.request, urllib.parse, ssl, json, time, sys
sys.stdout.reconfigure(encoding='utf-8')
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = "NibblBot/1.0 (https://example.com; contact@kilo.local) Python-urllib"

def ov_post(q, timeout=70):
    data = urllib.parse.urlencode({"data": q}).encode()
    req = urllib.request.Request("https://overpass.kumi.systems/api/interpreter", data=data,
                                 headers={"User-Agent": UA, "Accept": "application/json",
                                          "Content-Type":"application/x-www-form-urlencoded"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout, context=ctx).read())

BBOX = "12.85,77.40,13.10,77.95"
print("waiting 20s before single Overpass query...")
time.sleep(20)
print("=== single Overpass query (out center 60, 3 amenities merged) ===")
try:
    t=time.time()
    r = ov_post(f'[out:json][timeout:60];(node["amenity"="restaurant"]({BBOX});node["amenity"="cafe"]({BBOX});node["amenity"="fast_food"]({BBOX}););out center 60;')
    print(f"OK took {time.time()-t:.1f}s count={len(r.get('elements',[]))}")
    wd=0; ci=0
    for e in r.get("elements",[]):
        tg=e.get("tags",{})
        if tg.get("wikidata"): wd+=1
        if tg.get("cuisine"): ci+=1
    print(f"tags: wikidata={wd} cuisine={ci}")
    for e in r.get("elements",[])[:5]:
        tg=e.get("tags",{})
        print("  -", tg.get("name"), "| c:", tg.get("cuisine"), "| wd:", tg.get("wikidata"), "| city:", tg.get("addr:city"))
except Exception as e:
    print("FAIL", repr(e)[:160])
