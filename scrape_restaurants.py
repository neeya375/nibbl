#!/usr/bin/env python3
"""
Restaurant Data Scraper
Scrapes restaurant information and images from Zomato for Bangalore restaurants.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin, quote
import re

# Configuration
BASE_URL = "https://www.zomato.com"
BANGALORE_URL = f"{BASE_URL}/bangalore"
OUTPUT_DIR = "restaurant_data"
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")
DATA_FILE = os.path.join(OUTPUT_DIR, "restaurants.json")

# Restaurant list from user
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

# Headers to mimic browser requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

def create_directories():
    """Create output directories if they don't exist."""
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Created directories: {OUTPUT_DIR}, {IMAGES_DIR}")

def search_restaurant(restaurant_name):
    """Search for a restaurant on Zomato."""
    try:
        search_url = f"{BASE_URL}/bangalore/{restaurant_name.lower().replace(' ', '-')}"
        print(f"Searching: {search_url}")
        
        response = requests.get(search_url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            return search_url
        else:
            # Try alternative search
            search_query = quote(f"{restaurant_name} Bangalore")
            search_url = f"{BASE_URL}/search?q={search_query}"
            response = requests.get(search_url, headers=HEADERS, timeout=10)
            
            if response.status_code == 200:
                return search_url
                
    except Exception as e:
        print(f"Error searching for {restaurant_name}: {e}")
    
    return None

def scrape_restaurant_info(restaurant_name, url):
    """Scrape detailed information from a restaurant page."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            print(f"Failed to fetch {url}: {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract restaurant data
        data = {
            'name': restaurant_name,
            'url': url,
            'cuisine': 'Unknown',
            'area': 'Bangalore',
            'ambience': 'Unknown',
            'price': '₹₹',
            'rating': 0.0,
            'image_url': '',
            'address': '',
            'maps_url': ''
        }
        
        # Try to extract rating
        rating_elements = soup.find_all(class_=re.compile(r'rating|score'))
        for elem in rating_elements:
            text = elem.get_text(strip=True)
            if re.match(r'^\d+\.?\d*$', text):
                try:
                    data['rating'] = float(text)
                    break
                except ValueError:
                    continue
        
        # Try to extract cuisine
        cuisine_elements = soup.find_all(text=re.compile(r'cuisine|food|dining', re.I))
        for elem in cuisine_elements:
            parent = elem.parent
            if parent:
                text = parent.get_text(strip=True)
                if len(text) < 50 and any(c in text.lower() for c in ['italian', 'indian', 'chinese', 'japanese', 'korean', 'cafe', 'bar']):
                    data['cuisine'] = text
                    break
        
        # Try to extract area/location
        location_elements = soup.find_all(class_=re.compile(r'location|area|address', re.I))
        for elem in location_elements:
            text = elem.get_text(strip=True)
            if len(text) < 100 and 'bangalore' in text.lower():
                data['area'] = text.replace('Bangalore', '').strip()
                data['address'] = text
                break
        
        # Try to extract image
        img_elements = soup.find_all('img')
        for img in img_elements:
            src = img.get('src', '') or img.get('data-src', '')
            if src and ('restaurant' in src.lower() or 'food' in src.lower() or 'dining' in src.lower()):
                if src.startswith('http'):
                    data['image_url'] = src
                    break
        
        # Generate Google Maps URL
        maps_query = quote(f"{restaurant_name} Bangalore")
        data['maps_url'] = f"https://maps.google.com/?q={maps_query}"
        
        return data
        
    except Exception as e:
        print(f"Error scraping {restaurant_name}: {e}")
        return None

def download_image(image_url, restaurant_name):
    """Download restaurant image."""
    if not image_url:
        return None
        
    try:
        # Create safe filename
        safe_name = re.sub(r'[^\w\s-]', '', restaurant_name).strip().replace(' ', '_')
        image_path = os.path.join(IMAGES_DIR, f"{safe_name}.jpg")
        
        # Skip if already exists
        if os.path.exists(image_path):
            print(f"Image already exists: {image_path}")
            return image_path
        
        response = requests.get(image_url, headers=HEADERS, timeout=10)
        
        if response.status_code == 200:
            with open(image_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded image: {image_path}")
            return image_path
        else:
            print(f"Failed to download image: {response.status_code}")
            
    except Exception as e:
        print(f"Error downloading image for {restaurant_name}: {e}")
    
    return None

def estimate_cuisine_from_name(restaurant_name):
    """Estimate cuisine type based on restaurant name."""
    name_lower = restaurant_name.lower()
    
    cuisine_keywords = {
        'italian': ['pizza', 'pasta', 'italian', 'chianti', 'brik oven', 'oven story'],
        'chinese': ['chinese', 'mandarin', 'dim sum', 'wok'],
        'japanese': ['japanese', 'sushi', 'ramen', 'yuki', 'harima'],
        'korean': ['korean', 'koreyaki', 'seoul'],
        'north indian': ['north indian', 'punjab', 'chandni', 'kake di hatti', 'rajdhani'],
        'south indian': ['south indian', 'dosai', 'idli', 'a2b', 'vidyarthi'],
        'mexican': ['mexican', 'sanchez', 'burrito', 'california burrito'],
        'cafe': ['cafe', 'coffee', 'thirdwave', 'brew', 'toast', 'onesta'],
        'bar': ['bar', 'brewery', 'pub', 'social', 'boozy'],
        'desserts': ['dessert', 'bakery', 'smoor', 'glens', 'magnolia'],
        'american': ['american', 'burger', 'burgerman', 'hard rock'],
        'continental': ['continental', 'european']
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

def create_restaurant_data(restaurant_name, scraped_data=None):
    """Create restaurant data object with scraped or estimated information."""
    
    if scraped_data:
        # Use scraped data where available
        data = {
            'id': 0,  # Will be assigned later
            'name': restaurant_name,
            'cuisine': scraped_data.get('cuisine', estimate_cuisine_from_name(restaurant_name)),
            'area': scraped_data.get('area', 'Bangalore'),
            'ambience': scraped_data.get('ambience', estimate_ambience_from_name(restaurant_name)),
            'price': scraped_data.get('price', estimate_price_from_name(restaurant_name)),
            'rating': scraped_data.get('rating', 8.0),  # Default rating
            'image': '',  # Will be set after image download
            'maps': scraped_data.get('maps_url', f"https://maps.google.com/?q={quote(restaurant_name + ' Bangalore')}")
        }
    else:
        # Use estimated data
        data = {
            'id': 0,  # Will be assigned later
            'name': restaurant_name,
            'cuisine': estimate_cuisine_from_name(restaurant_name),
            'area': 'Bangalore',
            'ambience': estimate_ambience_from_name(restaurant_name),
            'price': estimate_price_from_name(restaurant_name),
            'rating': 8.0,  # Default rating
            'image': '',
            'maps': f"https://maps.google.com/?q={quote(restaurant_name + ' Bangalore')}"
        }
    
    return data

def main():
    """Main scraping function."""
    print("Starting restaurant data scraping...")
    create_directories()
    
    all_restaurants = []
    
    for i, restaurant_name in enumerate(RESTAURANTS, 1):
        print(f"\n[{i}/{len(RESTAURANTS)}] Processing: {restaurant_name}")
        
        # Search for restaurant
        url = search_restaurant(restaurant_name)
        
        scraped_data = None
        if url:
            # Scrape restaurant details
            scraped_data = scrape_restaurant_info(restaurant_name, url)
            time.sleep(2)  # Be respectful to the server
        
        # Create restaurant data
        restaurant_data = create_restaurant_data(restaurant_name, scraped_data)
        restaurant_data['id'] = i
        
        # Download image if URL available
        if scraped_data and scraped_data.get('image_url'):
            image_path = download_image(scraped_data['image_url'], restaurant_name)
            if image_path:
                # Use relative path for the web app
                restaurant_data['image'] = f"restaurant_data/images/{os.path.basename(image_path)}"
            else:
                # Fallback to placeholder
                restaurant_data['image'] = f"assets/restaurants/restaurant_{i % 20 + 1}.jpg"
        else:
            # Use placeholder image
            restaurant_data['image'] = f"assets/restaurants/restaurant_{i % 20 + 1}.jpg"
        
        all_restaurants.append(restaurant_data)
        
        # Save progress periodically
        if i % 10 == 0:
            with open(DATA_FILE, 'w') as f:
                json.dump(all_restaurants, f, indent=4)
            print(f"Progress saved ({i} restaurants)")
        
        time.sleep(1)  # Rate limiting
    
    # Final save
    with open(DATA_FILE, 'w') as f:
        json.dump(all_restaurants, f, indent=4)
    
    print(f"\nScraping complete! Data saved to {DATA_FILE}")
    print(f"Images saved to {IMAGES_DIR}")
    print(f"Total restaurants processed: {len(all_restaurants)}")

if __name__ == "__main__":
    main()