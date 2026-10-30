#!/usr/bin/env python3
"""
Download restaurant images using Pexels API (free, no key needed for basic usage)
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

# Food-specific image URLs (high-quality food images from various sources)
FOOD_IMAGES = {
    'Italian': [
        'https://images.unsplash.com/photo-1604382354936-07c5d9983bd3?w=800',
        'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=800',
        'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800'
    ],
    'Chinese': [
        'https://images.unsplash.com/photo-1525755662778-989d0524087e?w=800',
        'https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800',
        'https://images.unsplash.com/photo-1585032226651-759b368d7246?w=800'
    ],
    'Japanese': [
        'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=800',
        'https://images.unsplash.com/photo-1553621042-f6e147245754?w=800',
        'https://images.unsplash.com/photo-1617196034796-73dfa7b1fd56?w=800'
    ],
    'Korean': [
        'https://images.unsplash.com/photo-1590301157890-4810ed352733?w=800',
        'https://images.unsplash.com/photo-1590212153795-1cb1e1265811?w=800',
        'https://images.unsplash.com/photo-1534246319918-7f8edeb46a1b?w=800'
    ],
    'North Indian': [
        'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=800',
        'https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=800',
        'https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=800'
    ],
    'South Indian': [
        'https://images.unsplash.com/photo-1630383249896-483c1d18d4a0?w=800',
        'https://images.unsplash.com/photo-1666238775737-6f1e85f5dab4?w=800',
        'https://images.unsplash.com/photo-1596386463628-4b82e8e93e4d?w=800'
    ],
    'Mexican': [
        'https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=800',
        'https://images.unsplash.com/photo-1534352956036-cd81e27dd615?w=800',
        'https://images.unsplash.com/photo-1606706062686-ca8ef1b4d29b?w=800'
    ],
    'American': [
        'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800',
        'https://images.unsplash.com/photo-1550547660-d9450f859349?w=800',
        'https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?w=800'
    ],
    'Continental': [
        'https://images.unsplash.com/photo-1544025162-d76694265947?w=800',
        'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800',
        'https://images.unsplash.com/photo-1559339352-11d035aa65de?w=800'
    ],
    'Cafe': [
        'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800',
        'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800',
        'https://images.unsplash.com/photo-1453614512568-c4024d13c247?w=800'
    ],
    'Bar': [
        'https://images.unsplash.com/photo-1572116469696-31de0f17cc34?w=800',
        'https://images.unsplash.com/photo-1470337458703-46ad1756a187?w=800',
        'https://images.unsplash.com/photo-1566417713940-fe7c737a9ef2?w=800'
    ],
    'Desserts': [
        'https://images.unsplash.com/photo-1551024601-bec78aea704b?w=800',
        'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=800',
        'https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=800'
    ],
    'Multi-cuisine': [
        'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800',
        'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800',
        'https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=800'
    ]
}

def create_directories():
    """Create output directories."""
    os.makedirs(IMAGES_DIR, exist_ok=True)
    print(f"Images directory: {IMAGES_DIR}")

def download_image(url, restaurant_name):
    """Download image from URL."""
    try:
        safe_name = re.sub(r'[^\w\s-]', '', restaurant_name).strip().replace(' ', '_')
        image_path = os.path.join(IMAGES_DIR, f"{safe_name}.jpg")
        
        # Skip if already exists
        if os.path.exists(image_path):
            print(f"[OK] Image exists: {restaurant_name}")
            return image_path
        
        response = requests.get(url, timeout=15)
        
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

def get_cuisine_image(cuisine_type, index):
    """Get image URL for cuisine type."""
    if cuisine_type in FOOD_IMAGES:
        images = FOOD_IMAGES[cuisine_type]
        return images[index % len(images)]
    else:
        # Default to multi-cuisine images
        return FOOD_IMAGES['Multi-cuisine'][index % len(FOOD_IMAGES['Multi-cuisine'])]

def download_restaurant_images():
    """Download images for all restaurants."""
    # Load restaurant data
    with open(RESTAURANTS_FILE, 'r', encoding='utf-8') as f:
        restaurants = json.load(f)
    
    print(f"Processing {len(restaurants)} restaurants...")
    
    for i, restaurant in enumerate(restaurants, 1):
        restaurant_name = restaurant['name']
        cuisine_type = restaurant['cuisine']
        
        print(f"[{i}/{len(restaurants)}] {restaurant_name} ({cuisine_type})")
        
        # Get cuisine-specific image
        image_url = get_cuisine_image(cuisine_type, i)
        
        # Download image
        image_path = download_image(image_url, restaurant_name)
        
        # Update restaurant data with image path
        if image_path:
            restaurant['image'] = f"restaurant_data/images/{os.path.basename(image_path)}"
        else:
            # Keep original placeholder
            print(f"[FAIL] Using placeholder for: {restaurant_name}")
        
        # Rate limiting
        time.sleep(0.5)
        
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
    print("Starting restaurant image download...")
    create_directories()
    
    restaurants = download_restaurant_images()
    convert_to_js(restaurants)
    
    print("\nAll tasks completed!")
    print(f"Images saved to: {IMAGES_DIR}")
    print(f"Data saved to: {OUTPUT_FILE}")
    print(f"JavaScript updated: restaurants.js")

if __name__ == "__main__":
    main()