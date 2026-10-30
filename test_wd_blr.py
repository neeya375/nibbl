import urllib.request, urllib.parse, ssl, json, re
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = "NibblBot/1.0 (https://example.com; contact@kilo.local) Python-urllib"

def sparql(query, timeout=60):
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": query, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout, context=ctx).read())

q = '''
SELECT ?item ?itemLabel ?coord ?image WHERE {
  ?item wdt:P31/wdt:P279* wd:Q11707 .
  SERVICE wikibase:around { ?item wdt:P625 ?coord . bd:serviceParam wikibase:center "Point(77.5617 12.9716)" wikibase:radius "30". }
  OPTIONAL { ?item wdt:P18 ?image }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
'''
try:
    r = sparql(q)
    rows = r.get("results",{}).get("bindings",[])
    print("Bangalore-area restaurants:", len(rows))
    for b in rows[:12]:
        lbl = b.get("itemLabel",{}).get("value","?")
        coord = b.get("coord",{}).get("value","")
        img = b.get("image",{}).get("value","")
        print(f"  - {lbl} | coord={coord} | img={'yes' if img else 'no'}")
    imgs = sum(1 for b in rows if b.get("image"))
    print("with images:", imgs)
except Exception as e:
    print("FAIL", repr(e)[:200])
