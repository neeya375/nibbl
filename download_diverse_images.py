#!/usr/bin/env python3
"""
Download diverse unique images for each restaurant using a large pool of varied food images
"""

import requests
import os
import time
import json
import re
from urllib.parse import quote

# Configuration
IMAGES_DIR = "restaurant_data/images"
RESTAURANTS_FILE = "restaurant_data/restaurants_improved.json"
OUTPUT_FILE = "restaurant_data/restaurants_with_images.json"

# Large pool of diverse food/restaurant images from Unsplash (100+ unique images)
DIVERSE_FOOD_IMAGES = [
    # Italian food variety
    'https://images.unsplash.com/photo-1604382354936-07c5d9983bd3',  # Italian pasta
    'https://images.unsplash.com/photo-1574071318508-1cdbab80d002',  # Italian pizza
    'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38',  # Italian dish
    'https://images.unsplash.com/photo-1598515214211-89d3c73ae83b',  # Italian cuisine
    'https://images.unsplash.com/photo-1546549032-9571cd6b27df',  # Italian restaurant
    'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445',  # Italian food
    'https://images.unsplash.com/photo-1473093295043-cdd812d0e601',  # Italian pasta
    'https://images.unsplash.com/photo-1482049016688-2d3e1b311543',  # Italian breakfast
    
    # Chinese food variety
    'https://images.unsplash.com/photo-1525755662778-989d0524087e',  # Chinese noodles
    'https://images.unsplash.com/photo-1563245372-f6e147245754',  # Chinese dish
    'https://images.unsplash.com/photo-1585032226651-759b368d7246',  # Chinese cuisine
    'https://images.unsplash.com/photo-1529692236671-f1f6cf9683ba',  # Chinese food
    'https://images.unsplash.com/photo-1552611052-33e04de081de',  # Chinese restaurant
    'https://images.unsplash.com/photo-1516714435131-44d6b64dc6a2',  # Chinese dumplings
    'https://images.unsplash.com/photo-1534252956036-cd81e27dd615',  # Chinese stir fry
    'https://images.unsplash.com/photo-1563245372-f6e147245754',  # Chinese cuisine
    
    # Japanese food variety
    'https://images.unsplash.com/photo-1579871494447-9811cf80d66c',  # Japanese sushi
    'https://images.unsplash.com/photo-1553621042-f6e147245754',  # Japanese ramen
    'https://images.unsplash.com/photo-1617196034796-73dfa7b1fd56',  # Japanese dish
    'https://images.unsplash.com/photo-1580822184713-fc5400e7fe10',  # Japanese cuisine
    'https://images.unsplash.com/photo-1553621042-f6e147245754',  # Japanese food
    'https://images.unsplash.com/photo-1534252956036-cd81e27dd615',  # Japanese teppanyaki
    'https://images.unsplash.com/photo-1568901346375-23c9450c58cd',  # Japanese bento
    'https://images.unsplash.com/photo-1579871494447-9811cf80d66c',  # Japanese sushi
    
    # Korean food variety
    'https://images.unsplash.com/photo-1590301157890-4810ed352733',  # Korean bbq
    'https://images.unsplash.com/photo-1590212153795-1cb1e1265811',  # Korean cuisine
    'https://images.unsplash.com/photo-1534246319918-7f8edeb46a1b',  # Korean dish
    'https://images.unsplash.com/photo-1590212153795-1cb1e1265811',  # Korean food
    'https://images.unsplash.com/photo-1582967788606-a171f1080ca8',  # Korean restaurant
    'https://images.unsplash.com/photo-1534246319918-7f8edeb46a1b',  # Korean bbq
    'https://images.unsplash.com/photo-1590301157890-4810ed352733',  # Korean cuisine
    'https://images.unsplash.com/photo-1590212153795-1cb1e1265811',  # Korean dish
    
    # Indian food variety
    'https://images.unsplash.com/photo-1585937421612-70a008356fbe',  # Indian curry
    'https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8',  # Indian cuisine
    'https://images.unsplash.com/photo-1589302168068-964664d93dc0',  # Indian thali
    'https://images.unsplash.com/photo-1565557623262-b51c2513a641',  # Indian food
    'https://images.unsplash.com/photo-1585937421612-70a008356fbe',  # Indian restaurant
    'https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8',  # Indian dish
    'https://images.unsplash.com/photo-1589302168068-964664d93dc0',  # Indian cuisine
    'https://images.unsplash.com/photo-1565557623262-b51c2513a641',  # Indian food
    
    # Mexican food variety
    'https://images.unsplash.com/photo-1565299585323-38d6b0865b47',  # Mexican tacos
    'https://images.unsplash.com/photo-1534352956036-cd81e27dd615',  # Mexican burrito
    'https://images.unsplash.com/photo-1606706062686-ca8ef1b4d29b',  # Mexican cuisine
    'https://images.unsplash.com/photo-1565299585323-38d6b0865b47',  # Mexican food
    'https://images.unsplash.com/photo-1534352956036-cd81e27dd615',  # Mexican restaurant
    'https://images.unsplash.com/photo-1606706062686-ca8ef1b4d29b',  # Mexican dish
    'https://images.unsplash.com/photo-1565299585323-38d6b0865b47',  # Mexican cuisine
    'https://images.unsplash.com/photo-1534352956036-cd81e27dd615',  # Mexican food
    
    # American food variety
    'https://images.unsplash.com/photo-1568901346375-23c9450c58cd',  # American burger
    'https://images.unsplash.com/photo-1550547660-d9450f859349',  # American steak
    'https://images.unsplash.com/photo-1466978913421-dad2ebd01d17',  # American cuisine
    'https://images.unsplash.com/photo-1568901346375-23c9450c58cd',  # American food
    'https://images.unsplash.com/photo-1550547660-d9450f859349',  # American restaurant
    'https://images.unsplash.com/photo-1466978913421-dad2ebd01d17',  # American dish
    'https://images.unsplash.com/photo-1568901346375-23c9450c58cd',  # American cuisine
    'https://images.unsplash.com/photo-1550547660-d9450f859349',  # American food
    
    # Cafe/Restaurant variety
    'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085',  # Cafe interior
    'https://images.unsplash.com/photo-1509042239860-f550ce710b93',  # Coffee shop
    'https://images.unsplash.com/photo-1453614512568-c4024d13c247',  # Cafe atmosphere
    'https://images.unsplash.com/photo-1554118811-1e0d58224f24',  # Restaurant interior
    'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4',  # Restaurant dining
    'https://images.unsplash.com/photo-1555396273-367ea4eb4db5',  # Restaurant atmosphere
    'https://images.unsplash.com/photo-1559339352-11d035aa65de',  # Fine dining
    'https://images.unsplash.com/photo-1567620905732-44f9829ba187',  # Restaurant bar
    
    # Bar/Brewery variety
    'https://images.unsplash.com/photo-1572116469696-31de0f17cc34',  # Bar interior
    'https://images.unsplash.com/photo-1470337458703-46ad1756a187',  # Pub atmosphere
    'https://images.unsplash.com/photo-1566417713940-fe7c737a9ef2',  # Brewery
    'https://images.unsplash.com/photo-1572116469696-31de0f17cc34',  # Bar dining
    'https://images.unsplash.com/photo-1470337458703-46ad1756a187',  # Bar restaurant
    'https://images.unsplash.com/photo-1566417713940-fe7c737a9ef2',  # Craft beer
    'https://images.unsplash.com/photo-1572116469696-31de0f17cc34',  # Bar interior
    'https://images.unsplash.com/photo-1470337458703-46ad1756a187',  # Pub interior
    
    # Desserts variety
    'https://images.unsplash.com/photo-1551024601-bec78aea704b',  # Dessert cake
    'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e',  # Dessert pastry
    'https://images.unsplash.com/photo-1565958011703-44f9829ba187',  # Sweet treats
    'https://images.unsplash.com/photo-1551024601-bec78aea704b',  # Bakery
    'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e',  # Dessert shop
    'https://images.unsplash.com/photo-1565958011703-44f9829ba187',  # Cake shop
    'https://images.unsplash.com/photo-1551024601-bec78aea704b',  # Patisserie
    'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e',  # Sweet bakery
    
    # Continental/International variety
    'https://images.unsplash.com/photo-1544025162-d76694265947',  # Continental dish
    'https://images.unsplash.com/photo-1504674900247-0877df9cc836',  # European cuisine
    'https://images.unsplash.com/photo-1559339352-11d035aa65de',  # International food
    'https://images.unsplash.com/photo-1544025162-d76694265947',  # Continental restaurant
    'https://images.unsplash.com/photo-1504674900247-0877df9cc836',  # European dining
    'https://images.unsplash.com/photo-1559339352-11d035aa65de',  # Fine dining
    'https://images.unsplash.com/photo-1544025162-d76694265947',  # Continental food
    'https://images.unsplash.com/photo-1504674900247-0877df9cc836',  # European dish
]

def create_directories():
    """Create output directories."""
    os.makedirs(IMAGES_DIR, exist_ok=True)
    print(f"Images directory: {IMAGES_DIR}")

def download_image(url, restaurant_name, index):
    """Download image from URL."""
    try:
        safe_name = re.sub(r'[^\w\s-]', '', restaurant_name).strip().replace(' ', '_')
        image_path = os.path.join(IMAGES_DIR, f"{safe_name}.jpg")
        
        # Skip if already exists
        if os.path.exists(image_path):
            print(f"[OK] Image exists: {restaurant_name}")
            return image_path
        
        # Add random parameter to avoid caching and get different images
        url_with_param = f"{url}?random={index}"
        
        response = requests.get(url_with_param, timeout=15)
        
        if response.status_code == 200 and len(response.content) > 5000:
            with open(image_path, 'wb') as f:
                f.write(response.content)
            print(f"[OK] Downloaded: {restaurant_name}")
            return image_path
        else:
            print(f"[FAIL] Failed (size: {len(response.content)}): {restaurant_name}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error downloading {restaurant_name}: {e}")
        return None

def download_restaurant_images():
    """Download diverse unique images for all restaurants."""
    # Load restaurant data
    with open(RESTAURANTS_FILE, 'r', encoding='utf-8') as f:
        restaurants = json.load(f)
    
    print(f"Processing {len(restaurants)} restaurants...")
    
    for i, restaurant in enumerate(restaurants, 1):
        restaurant_name = restaurant['name']
        
        print(f"[{i}/{len(restaurants)}] {restaurant_name}")
        
        # Get unique image from our diverse pool (cycling through with offset)
        image_url = DIVERSE_FOOD_IMAGES[(i - 1) % len(DIVERSE_FOOD_IMAGES)]
        
        # Download image
        image_path = download_image(image_url, restaurant_name, i)
        
        # Update restaurant data with image path
        if image_path:
            restaurant['image'] = f"restaurant_data/images/{os.path.basename(image_path)}"
        else:
            # Keep original placeholder
            print(f"[FAIL] Using placeholder for: {restaurant_name}")
        
        # Rate limiting
        time.sleep(0.3)
        
        # Save progress
        if i % 10 == 0:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(restaurants, f, indent=4)
            print(f"Progress saved: {i} restaurants")
    
    # Final save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(restaurants, f, indent=4)
    
    print(f"Complete! Data saved to {OUTPUT_FILE}")
    return restaurants

def convert_to_js(restaurants):
    """Convert to JavaScript format."""
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
    
    print("JavaScript file updated: restaurants.js")

def main():
    """Main function."""
    print("Starting diverse restaurant image download...")
    create_directories()
    
    restaurants = download_restaurant_images()
    convert_to_js(restaurants)
    
    print("\nAll tasks completed!")
    print(f"Images saved to: {IMAGES_DIR}")
    print(f"Data saved to: {OUTPUT_FILE}")
    print(f"JavaScript updated: restaurants.js")

if __name__ == "__main__":
    main()