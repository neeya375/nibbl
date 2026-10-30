#!/usr/bin/env python3
"""
Google Images Downloader for Restaurants
Downloads restaurant images using Google Images search.
"""

import requests
import os
import time
from urllib.parse import quote
import re
import json

# Configuration
OUTPUT_DIR = "restaurant_data"
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")
DATA_FILE = os.path.join(OUTPUT_DIR, "restaurants.json")

# Restaurant list
RESTAURANTS = [
    "RCB Bar and Cafe",
    "Amintri", 
    "Mirage",
    "Beige",
    "Oia",
    "Manheim",
    "Ironhill",
    "Kico",
    "Lumara",
    "Daddy",
    "Phobidden Fruit",
    "Magnolia",
    "Burgerman",
    "Mandarin",
    "Smash Guys",
    "Delhi Highway",
    "Lucky Chan",
    "Koreyaki",
    "Imlie",
    "Fomomo",
    "Thirdwave",
    "Pizza 4Ps",
    "Brik Oven",
    "Magique",
    "Tall Oak",
    "Yuki",
    "Oven Story",
    "Papa Johns",
    "Fresh Factory",
    "Pasta Street",
    "Taiki",
    "Byg Brewski",
    "Cafe Noir",
    "Bombay Brasserie",
    "Kake Di Hatti",
    "Daffys Brewgarden",
    "Terraces",
    "Chulha Chauki Da Dhaba",
    "1131 Bar + Kitchen",
    "Punjab Grill",
    "Foo",
    "Hard Rock Cafe",
    "Long Boat Brewery",
    "Artisanal Bier Village",
    "The Bier Library",
    "Vesparo",
    "Red Rhino",
    "La Gioia",
    "The Dual Room",
    "Phurr",
    "Jamming Goat",
    "Chianti",
    "Social",
    "Lazy Suzy",
    "Barbeque Nation",
    "Woodside Inn",
    "Antera Kitchen and Bar",
    "Nagarjuna",
    "Kopittiam Lah",
    "Mini Bar",
    "Bistro Claytopia",
    "Tycoons",
    "Rim Naam",
    "Pixi",
    "Rico",
    "Ishaara",
    "Bobs Bar",
    "The Reservoire",
    "Badmaash",
    "Fishermans Wharf",
    "Trippy Goat Cafe",
    "Bastian Garden City",
    "Rumi",
    "The Kind",
    "Olive Beach",
    "Conçu",
    "Ouro",
    "DYU Art Café",
    "Onesta",
    "Nanav Café & Store",
    "Rajdhani",
    "Three Monkeys Brewpub",
    "Paris Panini",
    "Chakum Chukum",
    "Aladdin Shawarma",
    "Toastid Co.",
    "California Burrito",
    "Circa 11",
    "Tandoori Taal"
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

def create_directories():
    """Create output directories."""
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Created directories: {OUTPUT_DIR}, {IMAGES_DIR}")

def estimate_cuisine_from_name(restaurant_name):
    """Estimate cuisine type based on restaurant name."""
    name_lower = restaurant_name.lower()
    
    cuisine_keywords = {
        'Italian': ['pizza', 'pasta', 'italian', 'chianti', 'brik oven', 'oven story'],
        'Chinese': ['chinese', 'mandarin', 'dim sum', 'wok'],
        'Japanese': ['japanese', 'sushi', 'ramen', 'yuki', 'harima'],
        'Korean': ['korean', 'koreyaki', 'seoul'],
        'North Indian': ['north indian', 'punjab', 'chandni', 'kake di hatti', 'rajdhani'],
        'South Indian': ['south indian', 'dosai', 'idli', 'a2b', 'vidyarthi'],
        'Mexican': ['mexican', 'sanchez', 'burrito', 'california burrito'],
        'Cafe': ['cafe', 'coffee', 'thirdwave', 'brew', 'toast', 'onesta'],
        'Bar': ['bar', 'brewery', 'pub', 'social', 'boozy'],
        'Desserts': ['dessert', 'bakery', 'smoor', 'glens', 'magnolia'],
        'American': ['american', 'burger', 'burgerman', 'hard rock'],
        'Continental': ['continental', 'european']
    }
    
    for cuisine, keywords in cuisine_keywords.items():
        if any(keyword in name_lower for keyword in keywords):
            return cuisine
    
    return 'Multi-cuisine'

def estimate_price_from_name(restaurant_name):
    """Estimate price range based on restaurant name."""
    name_lower = restaurant_name.lower()
    
    budget_keywords = ['a2b', 'ctrs', 'vidyarthi', 'highway', 'aladdin', 'chakum']
    luxury_keywords = ['hard rock', 'oberoi', 'olive', 'rim naam', 'social', 'brewski', 'antier']
    
    if any(keyword in name_lower for keyword in budget_keywords):
        return '₹'
    elif any(keyword in name_lower for keyword in luxury_keywords):
        return '₹₹₹'
    else:
        return '₹₹'

def estimate_ambience_from_name(restaurant_name):
    """Estimate ambience based on restaurant name."""
    name_lower = restaurant_name.lower()
    
    ambience_keywords = {
        'Rooftop': ['rooftop', 'terrace', 'open'],
        'Romantic': ['romantic', 'couple', 'date'],
        'Family': ['family', 'kids', 'dhaba'],
        'Cozy': ['cafe', 'cozy', 'small'],
        'Luxury': ['luxury', 'fine dine', 'premium', 'oberoi'],
        'Brewery': ['brew', 'brewery', 'pub']
    }
    
    for ambience, keywords in ambience_keywords.items():
        if any(keyword in name_lower for keyword in keywords):
            return ambience
    
    return 'Casual'

def estimate_area_from_name(restaurant_name):
    """Estimate area based on restaurant name or common knowledge."""
    name_lower = restaurant_name.lower()
    
    area_keywords = {
        'Indiranagar': ['indiranagar', '100 feet', 'defence', 'hal'],
        'Koramangala': ['koramangala', 'jyoti', 'nexus'],
        'MG Road': ['mg road', 'brigade', 'church street', 'st marks'],
        'Whitefield': ['whitefield', 'ecoworld', 'bellandur'],
        'HSR Layout': ['hsr', 'sarjapur'],
        'JP Nagar': ['jp nagar', 'marenahalli'],
        'Jayanagar': ['jayanagar'],
        'Electronic City': ['electronic city']
    }
    
    for area, keywords in area_keywords.items():
        if any(keyword in name_lower for keyword in keywords):
            return area
    
    return 'Bangalore'

def download_google_image(restaurant_name):
    """Download first image from Google Images search."""
    try:
        search_url = f"https://www.google.com/search?q={quote(restaurant_name + ' restaurant bangalore')}&tbm=isch"
        
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            print(f"Failed to search images for {restaurant_name}")
            return None
        
        # Simple regex to find image URLs
        image_urls = re.findall(r'"https://[^"]*\.(?:jpg|jpeg|png|webp)"', response.text)
        
        if image_urls:
            image_url = image_urls[0].replace(r'\"', '')
            
            # Download the image
            img_response = requests.get(image_url, headers=HEADERS, timeout=10)
            
            if img_response.status_code == 200:
                safe_name = re.sub(r'[^\w\s-]', '', restaurant_name).strip().replace(' ', '_')
                image_path = os.path.join(IMAGES_DIR, f"{safe_name}.jpg")
                
                with open(image_path, 'wb') as f:
                    f.write(img_response.content)
                
                print(f"Downloaded image for {restaurant_name}")
                return image_path
            else:
                print(f"Failed to download image from {image_url}")
        else:
            print(f"No images found for {restaurant_name}")
            
    except Exception as e:
        print(f"Error downloading image for {restaurant_name}: {e}")
    
    return None

def create_restaurant_data():
    """Create restaurant data with estimated information."""
    restaurants = []
    
    for i, restaurant_name in enumerate(RESTAURANTS, 1):
        print(f"[{i}/{len(RESTAURANTS)}] Processing: {restaurant_name}")
        
        restaurant_data = {
            'id': i,
            'name': restaurant_name,
            'cuisine': estimate_cuisine_from_name(restaurant_name),
            'area': estimate_area_from_name(restaurant_name),
            'ambience': estimate_ambience_from_name(restaurant_name),
            'price': estimate_price_from_name(restaurant_name),
            'rating': 8.0,  # Default rating
            'image': '',
            'maps': f"https://maps.google.com/?q={quote(restaurant_name + ' Bangalore')}"
        }
        
        # Try to download image
        image_path = download_google_image(restaurant_name)
        if image_path:
            restaurant_data['image'] = f"restaurant_data/images/{os.path.basename(image_path)}"
        else:
            # Fallback to placeholder
            restaurant_data['image'] = f"assets/restaurants/restaurant_{i % 20 + 1}.jpg"
        
        restaurants.append(restaurant_data)
        
        # Rate limiting
        time.sleep(2)
        
        # Save progress
        if i % 10 == 0:
            with open(DATA_FILE, 'w') as f:
                json.dump(restaurants, f, indent=4)
            print(f"Progress saved ({i} restaurants)")
    
    # Final save
    with open(DATA_FILE, 'w') as f:
        json.dump(restaurants, f, indent=4)
    
    return restaurants

def main():
    """Main function."""
    print("Starting restaurant image download...")
    create_directories()
    
    restaurants = create_restaurant_data()
    
    print(f"\nComplete! Processed {len(restaurants)} restaurants")
    print(f"Data saved to {DATA_FILE}")
    print(f"Images saved to {IMAGES_DIR}")

if __name__ == "__main__":
    main()