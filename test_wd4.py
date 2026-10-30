import urllib.request, urllib.parse, ssl, json, re
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = "NibblBot/1.0 (https://example.com; contact@kilo.local) Python-urllib"

def wd_sparql(query, timeout=90):
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": query, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout, context=ctx).read())

# 1) Wikidata: restaurants located in Bengaluru (Q1355) via P131*
q1 = '''PREFIX geo: <http://www.opengis.net/ont/geosparql#>
SELECT ?item ?itemLabel ?coord ?image WHERE {
  ?item wdt:P31/wdt:P279* wd:Q11707 .
  ?item wdt:P131* wd:Q1355 .
  OPTIONAL { ?item wdt:P625 ?coord }
  OPTIONAL { ?item wdt:P18 ?image }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}'''
try:
    r = wd_sparql(q1)
    rows = r.get("results",{}).get("bindings",[])
    print("Wikidata restaurants in Bengaluru: total=", len(rows))
    withcoord = sum(1 for b in rows if b.get("coord"))
    withimg = sum(1 for b in rows if b.get("image"))
    print("  with coordinates:", withcoord, "| with image:", withimg)
    for b in rows[:10]:
        print("  -", b.get("itemLabel",{}).get("value","?"), "| coord:", bool(b.get("coord")), "| img:", bool(b.get("image")))
        if b.get("image"): print("      imgURL:", b["image"]["value"][:90])
except Exception as e:
    print("Wikidata P131* FAIL", repr(e)[:200])

# 2) Overpass: try POST with explicit Content-Type + Accept; also GET mirror
print("\n=== Overpass POST ===")
qv = '[out:json][timeout:30];node["amenity"="restaurant"](12.85,77.40,13.10,77.90);out center 20;'
postdata = urllib.parse.urlencode({"data": qv}).encode()
for endpoint in ["https://overpass-api.de/api/interpreter","https://overpass.kumi.systems/api/interpreter","https://overpass.openstreetmap.fr/api/interpreter"]:
    for headers in [{"User-Agent": UA, "Accept": "application/json"}]:
        try:
            req = urllib.request.Request(endpoint, data=postdata, headers=headers, method="POST")
            req.add_header("Content-Type","application/x-www-form-urlencoded")
            raw = urllib.request.urlopen(req, timeout=30, context=ctx).read()
            obj = json.loads(raw)
            print(f"  {endpoint} POST OK count={len(obj.get('elements',[]))}")
            break
        except Exception as e:
            print(f"  {endpoint} POST FAIL {repr(e)[:90]}")
