import urllib.request, urllib.parse, ssl, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = "NibblBot/1.0 (https://example.com; contact@kilo.local) Python-urllib"

def wikidata_sparql(query, timeout=60):
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": query, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept":"application/json","Accept-Language":"en"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout, context=ctx).read())

def commons_direct(fileurl):
    m = re.search(r"File:(.+)$", fileurl)
    if not m: return None
    return "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(m.group(1)) + "/400px"

q = '''SELECT ?item ?itemLabel ?typeLabel ?image WHERE {
  ?item wdt:P31/wdt:P279* wd:Q11707 .
  ?item wdt:P131* wd:Q1355 .
  OPTIONAL { ?item wdt:P279 ?type }
  OPTIONAL { ?item wdt:P18 ?image }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
'''
try:
    r = wikidata_sparql(q)
    rows = r.get("results",{}).get("bindings",[])
    print("total:", len(rows))
    cuisines = {}
    imgs = [b["image"]["value"] for b in rows if b.get("image")]
    print("with image:", len(imgs))
    for b in rows:
        t = b.get("typeLabel",{}).get("value","")
        cuisines[t] = cuisines.get(t,0)+1
    print("cuisine distribution:", dict(sorted(cuisines.items(), key=lambda x:-x[1])[:10]))
    # test direct image link loads
    for img in imgs[:5]:
        du = commons_direct(img)
        try:
            req = urllib.request.Request(du, headers={"User-Agent":UA})
            data = urllib.request.urlopen(req, timeout=15, context=ctx).read(2)
            print("  IMG OK", du[:80], "byteshead", data[:2])
        except Exception as e:
            print("  IMG FAIL", du[:70], repr(e)[:60])
except Exception as e:
    print("SPARQL FAIL", repr(e)[:200])
