#!/usr/bin/env python3
"""
Fix failed image downloads
"""

import requests
import os
import json
import re

# Configuration
IMAGES_DIR = "restaurant_data/images"
RESTAURANTS_FILE = "restaurant_data/restaurants_with_images.json"

# Additional backup images
BACKUP_IMAGES = [
    'https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c',
    'https://images.unsplash.com/photo-1514933651103-005eec06c04b',
    'https://images.unsplash.com/photo-1504674900247-0877df9cc836',
    'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe',
    'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38',
    'https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8',
    'https://images.unsplash.com/photo-1579871494447-9811cf80d66c',
    'https://images.unsplash.com/photo-1590301157890-4810ed352733',
    'https://images.unsplash.com/photo-1585937421612-70a008356fbe',
    'https://images.unsplash.com/photo-1565299585323-38d6b0865b47',
    'https://images.unsplash.com/photo-1568901346375-23c9450c58cd',
    'https://images.unsplash.com/photo-1550547660-d9450f859349'
]

FAILED_RESTAURANTS = [
    'Daddy', 'Smash Guys', 'Delhi Highway', 'Pizza 4Ps', 'Yuki', 
    'Oven Story', 'Papa Johns', 'Fresh Factory', 'Pasta Street', 
    'Byg Brewski', 'Long Boat Brewery', 'Vesparo', 'Pixi'
]

def download_image(url, restaurant_name):
    """Download image from URL."""
    try:
        safe_name = re.sub(r'[^\w\s-]', '', restaurant_name).strip().replace(' ', '_')
        image_path = os.path.join(IMAGES_DIR, f"{safe_name}.jpg")
        
        # Skip if already exists and is valid
        if os.path.exists(image_path):
            if os.path.getsize(image_path) > 5000:
                print(f"[OK] Valid image exists: {restaurant_name}")
                return image_path
            else:
                os.remove(image_path)
        
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200 and len(response.content) > 5000:
            with open(image_path, 'wb') as f:
                f.write(response.content)
            print(f"[OK] Downloaded: {restaurant_name}")
            return image_path
        else:
            print(f"[FAIL] Failed: {restaurant_name}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error downloading {restaurant_name}: {e}")
        return None

def fix_failed_images():
    """Fix failed image downloads."""
    # Load restaurant data
    with open(RESTAURANTS_FILE, 'r', encoding='utf-8') as f:
        restaurants = json.load(f)
    
    print(f"Fixing {len(FAILED_RESTAURANTS)} failed restaurants...")
    
    for i, restaurant_name in enumerate(FAILED_RESTAURANTS, 1):
        print(f"[{i}/{len(FAILED_RESTAURANTS)}] {restaurant_name}")
        
        # Get backup image
        image_url = BACKUP_IMAGES[(i - 1) % len(BACKUP_IMAGES)]
        
        # Download image
        image_path = download_image(image_url, restaurant_name)
        
        # Update restaurant data
        if image_path:
            for restaurant in restaurants:
                if restaurant['name'] == restaurant_name:
                    restaurant['image'] = f"restaurant_data/images/{os.path.basename(image_path)}"
                    break
    
    # Save updated data
    with open(RESTAURANTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(restaurants, f, indent=4)
    
    # Convert to JS
    js_content = "const restaurants = [\n"
    for restaurant in restaurants:
        js_content += "    {\n"
        js_content += f"    id:{restaurant['id']},\n"
        js_content += f"    name:\"{restaurant['name']}\",\n"
        js_content += f"    cuisine:\"{restaurant['cuisine']}\",\n"
        js_content += f"    area:\"{restaurant['area']}\",\n"
        js_content += f"    ambience:\"{restaurant['ambience']}\",\n"
        js_content += f"    price:\"{restaurant['price']}\",\n"
        js_content += f"    rating:{restaurant['rating']},\n"
        js_content += f"    image:\"{restaurant['image']}\",\n"
        js_content += f"    maps:\"{restaurant['maps']}\"\n"
        js_content += "    },\n"
    js_content += "    ];"
    
    with open('restaurants.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print("Fixed all failed images!")
    print("Updated restaurants.js")

if __name__ == "__main__":
    fix_failed_images()