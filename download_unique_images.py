#!/usr/bin/env python3
"""
Download unique images for each restaurant using varied search terms
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

# Diverse image search terms for each restaurant
RESTAURANT_SEARCH_TERMS = {
    'RCB Bar and Cafe': ['sports bar cricket cafe', 'bar cafe interior', 'pub restaurant'],
    'Amintri': ['modern restaurant interior', 'fine dining restaurant', 'elegant restaurant'],
    'Mirage': ['luxury restaurant dining', 'upscale restaurant', 'fine dining interior'],
    'Beige': ['rooftop restaurant dining', 'outdoor restaurant', 'terrace dining'],
    'Oia': ['romantic restaurant sunset', 'couple dining', 'intimate restaurant'],
    'Manheim': ['brewery restaurant', 'craft beer bar', 'gastropub interior'],
    'Ironhill': ['brewery restaurant interior', 'beer hall dining', 'craft brewery'],
    'Kico': ['modern restaurant', 'contemporary dining', 'trendy restaurant'],
    'Lumara': ['luxury restaurant', 'fine dining interior', 'upscale dining'],
    'Daddy': ['casual restaurant', 'family dining', 'neighborhood restaurant'],
    'Phobidden Fruit': ['modern bar restaurant', 'cocktail bar dining', 'trendy eatery'],
    'Magnolia': ['bakery cafe interior', 'pastry shop', 'dessert restaurant'],
    'Burgerman': ['burger restaurant', 'american diner', 'gourmet burger'],
    'Mandarin': ['chinese restaurant interior', 'oriental dining', 'asian restaurant'],
    'Smash Guys': ['burger joint', 'casual dining', 'american restaurant'],
    'Delhi Highway': ['north indian restaurant', 'indian dining', 'curry house'],
    'Lucky Chan': ['chinese restaurant', 'asian dining', 'oriental restaurant'],
    'Koreyaki': ['korean bbq restaurant', 'korean dining', 'asian grill'],
    'Imlie': ['indian restaurant', 'traditional dining', 'ethnic restaurant'],
    'Fomomo': ['modern cafe', 'trendy eatery', 'contemporary restaurant'],
    'Thirdwave': ['coffee shop interior', 'cafe workspace', 'specialty coffee'],
    'Pizza 4Ps': ['pizza restaurant', 'italian pizzeria', 'wood fired pizza'],
    'Brik Oven': ['pizza restaurant', 'italian dining', 'pizzeria interior'],
    'Magique': ['fine dining restaurant', 'luxury dining', 'upscale restaurant'],
    'Tall Oak': ['brewery restaurant', 'craft beer hall', 'gastropub'],
    'Yuki': ['japanese restaurant', 'sushi bar', 'asian dining'],
    'Oven Story': ['pizza restaurant', 'modern pizzeria', 'italian casual'],
    'Papa Johns': ['pizza delivery', 'pizza shop', 'fast casual pizza'],
    'Fresh Factory': ['healthy restaurant', 'salad bar', 'fresh food cafe'],
    'Pasta Street': ['italian restaurant', 'pasta house', 'mediterranean dining'],
    'Taiki': ['japanese restaurant', 'asian fusion', 'oriental dining'],
    'Byg Brewski': ['brewery restaurant', 'outdoor brewery', 'craft beer venue'],
    'Cafe Noir': ['french cafe', 'european cafe', 'parisian cafe'],
    'Bombay Brasserie': ['indian fine dining', 'luxury indian restaurant', 'upscale indian'],
    'Kake Di Hatti': ['north indian restaurant', 'street food style', 'casual indian'],
    'Daffys Brewgarden': ['beer garden', 'outdoor bar', 'brewery garden'],
    'Terraces': ['rooftop restaurant', 'outdoor dining', 'terrace restaurant'],
    'Chulha Chauki Da Dhaba': ['indian dhaba', 'rural restaurant', 'traditional indian'],
    '1131 Bar + Kitchen': ['modern bar restaurant', 'gastro pub', 'craft bar'],
    'Punjab Grill': ['punjabi restaurant', 'north indian fine dining', 'indian cuisine'],
    'Foo': ['modern asian restaurant', 'fusion dining', 'contemporary asian'],
    'Hard Rock Cafe': ['music themed restaurant', 'rock cafe', 'memorabilia restaurant'],
    'Long Boat Brewery': ['brewery restaurant', 'craft beer venue', 'beer hall'],
    'Artisanal Bier Village': ['craft brewery', 'artisanal beer', 'brewery taproom'],
    'The Bier Library': ['book themed bar', 'library bar', 'study bar'],
    'Vesparo': ['modern restaurant', 'contemporary dining', 'trendy eatery'],
    'Red Rhino': ['craft brewery', 'microbrewery', 'beer restaurant'],
    'La Gioia': ['italian restaurant', 'romantic dining', 'fine italian'],
    'The Dual Room': ['modern restaurant', 'dual concept venue', 'contemporary dining'],
    'Phurr': ['modern restaurant', 'contemporary dining', 'trendy eatery'],
    'Jamming Goat': ['live music venue', 'restaurant bar', 'entertainment dining'],
    'Chianti': ['italian restaurant', 'tuscan dining', 'wine restaurant'],
    'Social': ['co-working restaurant', 'casual workspace', 'community hub'],
    'Lazy Suzy': ['casual restaurant', 'neighborhood eatery', 'comfort food'],
    'Barbeque Nation': ['bbq restaurant', 'grill house', 'barbecue dining'],
    'Woodside Inn': ['casual dining', 'neighborhood restaurant', 'comfort food'],
    'Antera Kitchen and Bar': ['modern restaurant', 'craft bar', 'contemporary dining'],
    'Nagarjuna': ['south indian restaurant', 'andhra cuisine', 'traditional indian'],
    'Kopittiam Lah': ['asian cafe', 'malaysian restaurant', 'coffee shop'],
    'Mini Bar': ['cocktail bar', 'small bar', 'intimate drinking'],
    'Bistro Claytopia': ['art cafe', 'creative restaurant', 'pottery cafe'],
    'Tycoons': ['upscale restaurant', 'fine dining', 'luxury venue'],
    'Rim Naam': ['thai restaurant', 'fine thai dining', 'royal thai'],
    'Pixi': ['modern restaurant', 'contemporary dining', 'trendy eatery'],
    'Rico': ['wine bar', 'wine restaurant', 'vineyard dining'],
    'Ishaara': ['modern indian restaurant', 'contemporary indian', 'fusion indian'],
    'Bobs Bar': ['casual bar', 'neighborhood pub', 'local watering hole'],
    'The Reservoire': ['brewery restaurant', 'craft beer venue', 'taproom'],
    'Badmaash': ['modern indian', 'contemporary indian', 'fusion cuisine'],
    'Fishermans Wharf': ['seafood restaurant', 'coastal dining', 'fish restaurant'],
    'Trippy Goat Cafe': ['quirky cafe', 'themed restaurant', 'unique cafe'],
    'Bastian Garden City': ['outdoor restaurant', 'garden dining', 'al fresco'],
    'Rumi': ['persian restaurant', 'middle eastern dining', 'exotic cuisine'],
    'The Kind': ['roastery restaurant', 'coffee brew restaurant', 'specialty coffee'],
    'Olive Beach': ['mediterranean restaurant', 'beach dining', 'coastal cuisine'],
    'Conçu': ['modern restaurant', 'contemporary dining', 'designer restaurant'],
    'Ouro': ['fine dining restaurant', 'luxury venue', 'upscale dining'],
    'DYU Art Café': ['art cafe', 'creative space', 'gallery cafe'],
    'Onesta': ['casual dining', 'italian restaurant', 'family restaurant'],
    'Nanav Café & Store': ['cafe shop', 'coffee retail', 'specialty coffee'],
    'Rajdhani': ['thali restaurant', 'gujarati cuisine', 'traditional indian'],
    'Three Monkeys Brewpub': ['brewery restaurant', 'craft beer venue', 'microbrewery'],
    'Paris Panini': ['french cafe', 'sandwich shop', 'european cafe'],
    'Chakum Chukum': ['indian street food', 'casual indian', 'fast indian'],
    'Aladdin Shawarma': ['middle eastern restaurant', 'shawarma shop', 'arabian cuisine'],
    'Toastid Co.': ['cafe restaurant', 'brunch spot', 'casual dining'],
    'California Burrito': ['mexican restaurant', 'burrito shop', 'tex mex'],
    'Circa 11': ['modern restaurant', 'contemporary dining', 'trendy eatery'],
    'Tandoori Taal': ['indian bbq restaurant', 'tandoori dining', 'north indian']
}

def create_directories():
    """Create output directories."""
    os.makedirs(IMAGES_DIR, exist_ok=True)
    print(f"Images directory: {IMAGES_DIR}")

def download_unsplash_image(restaurant_name, search_terms):
    """Download image from Unsplash with specific search terms."""
    try:
        safe_name = re.sub(r'[^\w\s-]', '', restaurant_name).strip().replace(' ', '_')
        image_path = os.path.join(IMAGES_DIR, f"{safe_name}.jpg")
        
        # Skip if already exists
        if os.path.exists(image_path):
            print(f"[OK] Image exists: {restaurant_name}")
            return image_path
        
        # Try each search term until we get a good image
        for search_term in search_terms:
            url = f"https://source.unsplash.com/800x600/?{quote(search_term)}"
            
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200 and len(response.content) > 5000:
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                print(f"[OK] Downloaded: {restaurant_name} (search: {search_term})")
                return image_path
            else:
                print(f"[FAIL] Try failed: {search_term}")
                continue
        
        print(f"[FAIL] All attempts failed: {restaurant_name}")
        return None
            
    except Exception as e:
        print(f"[ERROR] Error downloading {restaurant_name}: {e}")
        return None

def download_restaurant_images():
    """Download unique images for all restaurants."""
    # Load restaurant data
    with open(RESTAURANTS_FILE, 'r', encoding='utf-8') as f:
        restaurants = json.load(f)
    
    print(f"Processing {len(restaurants)} restaurants...")
    
    for i, restaurant in enumerate(restaurants, 1):
        restaurant_name = restaurant['name']
        
        print(f"[{i}/{len(restaurants)}] {restaurant_name}")
        
        # Get specific search terms for this restaurant
        search_terms = RESTAURANT_SEARCH_TERMS.get(restaurant_name, 
            ['restaurant dining', 'food cuisine', 'eating establishment'])
        
        # Download image
        image_path = download_unsplash_image(restaurant_name, search_terms)
        
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
    print("Starting unique restaurant image download...")
    create_directories()
    
    restaurants = download_restaurant_images()
    convert_to_js(restaurants)
    
    print("\nAll tasks completed!")
    print(f"Images saved to: {IMAGES_DIR}")
    print(f"Data saved to: {OUTPUT_FILE}")
    print(f"JavaScript updated: restaurants.js")

if __name__ == "__main__":
    main()