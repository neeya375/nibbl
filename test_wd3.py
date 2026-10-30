import urllib.request, urllib.parse, ssl, json
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = "NibblBot/1.0 (https://example.com; contact@kilo.local) Python-urllib"

def get_json(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout, context=ctx).read())

# Find Bangalore / Bengaluru QID
print("=== Search Wikidata for Bangalore ===")
sp = urllib.parse.urlencode({"action":"wbsearchentities","search":"Bengaluru","language":"en","format":"json","type":"item","limit":"5"})
try:
    obj = get_json("https://www.wikidata.org/w/api.php?"+sp)
    for s in obj.get("search",[]): print("  ", s["id"], s.get("label"), "|", s.get("description"))
except Exception as e: print("search FAIL", repr(e)[:120])

sp = urllib.parse.urlencode({"action":"wbsearchentities","search":"Bangalore","language":"en","format":"json","type":"item","limit":"5"})
try:
    obj = get_json("https://www.wikidata.org/w/api.php?"+sp)
    for s in obj.get("search",[]): print("  ", s["id"], s.get("label"), "|", s.get("description"))
except Exception as e: print("search FAIL", repr(e)[:120])

# Retry around-service with geo:wktLiteral prefix
print("\n=== around-service with geo:wktLiteral ===")
q = '''PREFIX geo: <http://www.opengis.net/ont/geosparql#>
SELECT ?item ?itemLabel ?coord ?image WHERE {
  ?item wdt:P31/wdt:P279* wd:Q11707 .
  SERVICE wikibase:around {
    ?item wdt:P625 ?coord .
    bd:serviceParam wikibase:center "Point(77.5617 12.9716)"^^geo:wktLiteral .
    bd:serviceParam wikibase:radius "30" .
  }
  OPTIONAL { ?item wdt:P18 ?image }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}'''
url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": q, "format": "json"})
try:
    obj = get_json(url, timeout=60)
    rows = obj.get("results",{}).get("bindings",[])
    print("count:", len(rows))
    for b in rows[:10]:
        print("  -", b.get("itemLabel",{}).get("value","?"), "| img:", "yes" if b.get("image") else "no")
    print("with images:", sum(1 for b in rows if b.get("image")))
except Exception as e: print("FAIL", repr(e)[:200])
