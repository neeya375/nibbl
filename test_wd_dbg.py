import urllib.request, urllib.parse, ssl, json
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = "NibblBot/1.0 (https://example.com; contact@kilo.local) Python-urllib"

def sparql(query, timeout=40):
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": query, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout, context=ctx).read())

tests = {
 "direct instance Q11707 (no path)": 'SELECT ?item ?itemLabel WHERE { ?item wdt:P31 wd:Q11707. SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } } LIMIT 5',
 "path P31/P279* Q11707": 'SELECT ?item ?itemLabel WHERE { ?item wdt:P31/wdt:P279* wd:Q11707. SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } } LIMIT 5',
 "anything with P131 Q1478": 'SELECT ?item ?itemLabel WHERE { ?item wdt:P131 wd:Q1478. SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } } LIMIT 5',
 "P131* Q1478": 'SELECT ?item ?itemLabel WHERE { ?item wdt:P131* wd:Q1478. SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } } LIMIT 5',
 "Bangalore label Q1478": 'SELECT ?item ?itemLabel WHERE { wd:Q1478 wdt:P31 ?item. SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } } LIMIT 5',
 "restaurants in India": 'SELECT ?item ?itemLabel WHERE { ?item wdt:P31/wdt:P279* wd:Q11707; wdt:P17 wd:Q668. SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } } LIMIT 5',
}
for name, q in tests.items():
    try:
        r = sparql(q)
        rows = r.get("results",{}).get("bindings",[])
        print(f"[{name}] rows={len(rows)}")
        for b in rows: print("   ", b.get("itemLabel",{}).get("value","?"))
    except Exception as e:
        print(f"[{name}] FAIL {repr(e)[:160]}")
