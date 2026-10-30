import requests
import json
import time
import os

with open('image_results.json', 'r') as f:
    results = json.load(f)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

os.makedirs('assets/restaurants', exist_ok=True)

for rid, img_url in results.items():
    if not img_url:
        continue
    
    # Determine file extension
    ext = 'jpg'
    if '.webp' in img_url:
        ext = 'webp'
    elif '.png' in img_url:
        ext = 'png'
    elif '.JPG' in img_url or '.jpeg' in img_url:
        ext = 'jpg'
    
    filename = f'assets/restaurants/restaurant_{rid}.{ext}'
    
    try:
        print(f"Downloading ID {rid}...")
        resp = requests.get(img_url, headers=headers, timeout=30)
        if resp.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(resp.content)
            print(f"  Saved: {filename} ({len(resp.content)} bytes)")
        else:
            print(f"  Failed: HTTP {resp.status_code}")
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(0.5)

print("Done!")
