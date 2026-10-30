#!/usr/bin/env python3
"""
Download restaurant images using Unsplash API
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

# Unsplash API (using demo access - no API key needed for basic search)
UNSPLASH_SEARCH_URL = "https://source.unsplash.com/800x600/?{}"

# Fallback image sources
PIXABAY_SEARCH_URL = "https://pixabay.com/api/"
WIKIMEDIA_SEARCH_URL = "https://commons.wikimedia.org/w/api.php"

def create_directories():
    """Create output directories."""
    os.makedirs(IMAGES_DIR, exist_ok=True)
    print(f"Images directory: {IMAGES_DIR}")

def download_unsplash_image(restaurant_name, cuisine_type):
    """Download image from Unsplash based on restaurant name and cuisine."""
    try:
        # Create search query combining restaurant name and cuisine
        search_query = f"{restaurant_name} restaurant {cuisine_type} food dining"
        safe_name = re.sub(r'[^\w\s-]', '', restaurant_name).strip().replace(' ', '_')
        image_path = os.path.join(IMAGES_DIR, f"{safe_name}.jpg")
        
        # Skip if already exists
        if os.path.exists(image_path):
            print(f"[OK] Image exists: {restaurant_name}")
            return image_path
        
        # Try Unsplash source API (no auth needed for basic usage)
        url = UNSPLASH_SEARCH_URL.format(quote(search_query))
        
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200 and len(response.content) > 5000:  # Valid image
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

def download_pixabay_image(restaurant_name, cuisine_type):
    """Download image from Pixabay (free API)."""
    try:
        # Pixabay requires API key, so we'll use their public search page
        safe_name = re.sub(r'[^\w\s-]', '', restaurant_name).strip().replace(' ', '_')
        image_path = os.path.join(IMAGES_DIR, f"{safe_name}.jpg")
        
        if os.path.exists(image_path):
            return image_path
        
        # Try to search on Pixabay public search
        search_query = f"{cuisine_type} restaurant food"
        search_url = f"https://pixabay.com/images/search/{quote(search_query)}/"
        
        response = requests.get(search_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=15)
        
        if response.status_code == 200:
            # Try to extract image URLs from the page
            import re
            img_urls = re.findall(r'https://cdn\.pixabay\.com/photo/[^"]+\.jpg', response.text)
            
            if img_urls:
                # Download first image
                img_url = img_urls[0]
                img_response = requests.get(img_url, timeout=10)
                
                if img_response.status_code == 200:
                    with open(image_path, 'wb') as f:
                        f.write(img_response.content)
                    print(f"[OK] Downloaded from Pixabay: {restaurant_name}")
                    return image_path
        
        return None
            
    except Exception as e:
        print(f"[ERROR] Pixabay error for {restaurant_name}: {e}")
        return None

def download_wikimedia_image(restaurant_name, cuisine_type):
    """Download image from Wikimedia Commons."""
    try:
        safe_name = re.sub(r'[^\w\s-]', '', restaurant_name).strip().replace(' ', '_')
        image_path = os.path.join(IMAGES_DIR, f"{safe_name}.jpg")
        
        if os.path.exists(image_path):
            return image_path
        
        # Search Wikimedia Commons for food images
        search_query = f"{cuisine_type} food dish"
        params = {
            'action': 'query',
            'generator': 'search',
            'gsrsearch': search_query,
            'gsrnamespace': '6',  # File namespace
            'gsrlimit': '5',
            'prop': 'imageinfo',
            'iiprop': 'url',
            'format': 'json'
        }
        
        response = requests.get(WIKIMEDIA_SEARCH_URL, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'query' in data and 'pages' in data['query']:
                pages = data['query']['pages']
                
                for page_id, page_data in pages.items():
                    if 'imageinfo' in page_data and len(page_data['imageinfo']) > 0:
                        img_url = page_data['imageinfo'][0]['url']
                        
                        # Download image
                        img_response = requests.get(img_url, timeout=10)
                        
                        if img_response.status_code == 200:
                            with open(image_path, 'wb') as f:
                                f.write(img_response.content)
                            print(f"[OK] Downloaded from Wikimedia: {restaurant_name}")
                            return image_path
        
        return None
            
    except Exception as e:
        print(f"[FAIL] Wikimedia error for {restaurant_name}: {e}")
        return None

def download_lorem_flickr_image(restaurant_name, cuisine_type):
    """Download food images from Lorem Flickr (free, no API key needed)."""
    try:
        safe_name = re.sub(r'[^\w\s-]', '', restaurant_name).strip().replace(' ', '_')
        image_path = os.path.join(IMAGES_DIR, f"{safe_name}.jpg")
        
        if os.path.exists(image_path):
            return image_path
        
        # Use Lorem Flickr for food images
        search_query = f"{cuisine_type},food,restaurant"
        url = f"https://loremflickr.com/800/600/{quote(search_query)}"
        
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200 and len(response.content) > 5000:
            with open(image_path, 'wb') as f:
                f.write(response.content)
            print(f"[OK] Downloaded from Lorem Flickr: {restaurant_name}")
            return image_path
        
        return None
            
    except Exception as e:
        print(f"[FAIL] Lorem Flickr error for {restaurant_name}: {e}")
        return None

def get_cuisine_specific_keywords(cuisine):
    """Get specific search keywords for each cuisine type."""
    cuisine_keywords = {
        'Italian': 'italian food pasta pizza',
        'Chinese': 'chinese food noodles dim sum',
        'Japanese': 'japanese food sushi ramen',
        'Korean': 'korean food bbq kimchi',
        'North Indian': 'indian food curry butter chicken',
        'South Indian': 'south indian food dosa idli',
        'Mexican': 'mexican food tacos burrito',
        'American': 'american food burger steak',
        'Continental': 'continental food fine dining',
        'Cafe': 'cafe coffee interior',
        'Bar': 'bar brewery pub interior',
        'Desserts': 'dessert cake pastry',
        'Multi-cuisine': 'restaurant food dining',
        'Bar': 'bar restaurant interior'
    }
    
    return cuisine_keywords.get(cuisine, 'restaurant food dining')

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
        
        # Get cuisine-specific keywords
        search_keywords = get_cuisine_specific_keywords(cuisine_type)
        
        # Try multiple image sources
        image_path = None
        
        # Try Unsplash first
        image_path = download_unsplash_image(restaurant_name, search_keywords)
        
        # Fallback to Lorem Flickr
        if not image_path:
            image_path = download_lorem_flickr_image(restaurant_name, search_keywords)
        
        # Fallback to Pixabay
        if not image_path:
            image_path = download_pixabay_image(restaurant_name, search_keywords)
        
        # Fallback to Wikimedia
        if not image_path:
            image_path = download_wikimedia_image(restaurant_name, search_keywords)
        
        # Update restaurant data with image path
        if image_path:
            restaurant['image'] = f"restaurant_data/images/{os.path.basename(image_path)}"
        else:
            # Keep original placeholder
            print(f"[FAIL] Using placeholder for: {restaurant_name}")
        
        # Rate limiting
        time.sleep(1)
        
        # Save progress
        if i % 10 == 0:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(restaurants, f, indent=4)
            print(f"Progress saved: {i} restaurants")
    
    # Final save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(restaurants, f, indent=4)
    
    print(f"\nComplete! Data saved to {OUTPUT_FILE}")
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
    
    print("\n✅ All tasks completed!")
    print(f"📁 Images saved to: {IMAGES_DIR}")
    print(f"📄 Data saved to: {OUTPUT_FILE}")
    print(f"📄 JavaScript updated: restaurants.js")

if __name__ == "__main__":
    main()