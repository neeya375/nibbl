import urllib.request, urllib.parse, ssl, json
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = "NibblBot/1.0 (https://example.com; contact@kilo.local) Python-urllib"

def overpass(q, timeout=30):
    data = urllib.parse.urlencode({"data": q}).encode()
    req = urllib.request.Request("https://overpass.kumi.systems/api/interpreter", data=data,
                                 headers={"User-Agent": UA, "Accept": "application/json",
                                          "Content-Type":"application/x-www-form-urlencoded"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout, context=ctx).read())

BBOX = "12.85,77.40,13.10,77.95"

# exact amenity=restaurant, small sample
q = f'[out:json][timeout:30];node["amenity"="restaurant"]({BBOX});out center 15;'
try:
    r = overpass(q, timeout=35)
    els = r.get("elements", [])
    print("returned:", len(els))
    for e in els:
        t = e.get("tags", {})
        print(f"  - {t.get('name','?')} | cuis={t.get('cuisine','-')} | city={t.get('addr:city','-')}/{t.get('addr:suburb','-')} | neigh={t.get('addr:neighbourhood','-')} | web={t.get('website','-')} | phone={t.get('contact:phone','-')} | lat={e.get('lat')} lon={e.get('lon')}")
except Exception as e:
    print("sample error:", repr(e)[:200])
