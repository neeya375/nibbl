import urllib.request, urllib.parse, ssl, json, re
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = "NibblBot/1.0 (https://example.com; contact@kilo.local) Python-urllib"

def sparql(query, timeout=45):
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": query, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout, context=ctx).read())

q = '''
SELECT ?item ?itemLabel ?coord ?image WHERE {
  ?item wdt:P31/wdt:P279* wd:Q11707 .
  ?item wdt:P131* wd:Q1478 .
  ?item wdt:P625 ?coord .
  OPTIONAL { ?item wdt:P18 ?image }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 100
'''
r = sparql(q)
rows = r.get("results", {}).get("bindings", [])
print("Wikidata Bangalore restaurants (with coord):", len(rows))

def get(v): return v.get("value") if v else None
img_direct_count = 0
sample_imgs = []
for b in rows[:25]:
    lbl = get(b.get("itemLabel"))
    coord = get(b.get("coord"))  # Point(12.9 77.6)
    img = get(b.get("image"))
    print(f"  - {lbl} | coord={coord} | img={str(img)[:70]}")
    if img:
        sample_imgs.append(img)

# Convert a commons File: URL to direct image link and test it loads
print("\n=== Testing image direct URLs ===")
def direct_url(img):
    if not img: return None
    if "upload.wikimedia.org" in img: return img  # already direct
    m = re.search(r"File:(.+)$", img)
    if m:
        fn = urllib.parse.quote(m.group(1))
        return f"https://commons.wikimedia.org/wiki/Special:FilePath/{fn}/400px"
    return None

def head_ok(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        r = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        data = r.read(4)
        return r.status == 200 and len(data) > 0
    except Exception as e:
        return f"FAIL {repr(e)[:80]}"

tested = 0
for img in sample_imgs[:8]:
    du = direct_url(img)
    if du and tested < 8:
        ok = head_ok(du)
        print(f"  {'OK ' if ok is True else 'X  '} {du[:80]} -> {ok}")
        tested += 1
