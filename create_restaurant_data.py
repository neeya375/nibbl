#!/usr/bin/env python3
"""
Create restaurant data using provided addresses and improved estimation.
"""

import json
import re
from urllib.parse import quote

# Restaurant data with addresses from user
RESTAURANT_DATA = [
    {"name": "RCB Bar and Cafe", "address": "5th & 6th Floor, Garuda Mall, Magrath Road, Ashok Nagar, Bengaluru 560001"},
    {"name": "Amintri", "address": "10, Museum Road, Shanthala Nagar, Ashok Nagar, Bengaluru 560001"},
    {"name": "Mirage", "address": "1, 6th Floor, Sobha, St. Mark's Road, Ashok Nagar, Bengaluru 560001"},
    {"name": "Beige", "address": "Rooftop, Vanshree Towers, Outer Ring Road, Marathahalli Village, Bengaluru 560037"},
    {"name": "Oia", "address": "Opposite Mantri Webcity, Hennur Main Road, New Airport Road, Visthar, Bengaluru 560077"},
    {"name": "Manheim", "address": "Garuda Mall, Magrath Road, Brigade Road, Bengaluru"},
    {"name": "Ironhill", "address": "Sy No. 90/7 & 90/8, Outer Ring Road, next to Radisson Blu, Marathahalli, Bengaluru 560037"},
    {"name": "Kico", "address": "Marks Square, St. Mark's Road, Shanthala Nagar, Ashok Nagar, Bengaluru 560001"},
    {"name": "Lumara", "address": "4th Floor, Trinity Circle/Complex, #152–154, Old Madras Road/MG Road area, Ulsoor, Bengaluru 560008"},
    {"name": "Daddy", "address": "963, 12th Main Road, HAL 2nd Stage, Doopanahalli, Indiranagar, Bengaluru 560008"},
    {"name": "Phobidden Fruit", "address": "965, 12th Main Road, HAL 2nd Stage, Doopanahalli, Indiranagar, Bengaluru 560038"},
    {"name": "Magnolia", "address": "788, J.K. Plaza, 12th Main Road, Indiranagar, Bengaluru 560038"},
    {"name": "Burgerman", "address": "No. 3282/1, 12th Main Road, HAL 2nd Stage, Appareddipalya, Indiranagar, Bengaluru 560038"},
    {"name": "Mandarin", "address": "196/A, Double Road, 2nd Stage, Indiranagar, Bengaluru 560038"},
    {"name": "Smash Guys", "address": "948, 12th Main Road, HAL 2nd Stage, Appareddipalya, Indiranagar, Bengaluru"},
    {"name": "Delhi Highway", "address": "951, 12th Main Road, HAL 2nd Stage, Appareddipalya, Indiranagar, Bengaluru 560008"},
    {"name": "Lucky Chan", "address": "594, 12th Main Road, 2nd Stage, HAL 2nd Stage, Indiranagar, Bengaluru"},
    {"name": "Koreyaki", "address": "3274/A, 11th Main Road, Appareddipalya, HAL 2nd Stage, Indiranagar, Bengaluru 560038"},
    {"name": "Imlie", "address": "204, 5th Main, 7th Cross, Indiranagar I Stage, Bengaluru 560038"},
    {"name": "Fomomo", "address": "Shop #6, 1083, Prince Arcade, 12th Main Road, 2nd Stage, HAL 2nd Stage, Doopanahalli, Indiranagar, Bengaluru 560008"},
    {"name": "Thirdwave", "address": "12th Main Road, HAL 2nd Stage, Appareddipalya, Indiranagar, Bengaluru 560008"},
    {"name": "Pizza 4Ps", "address": "Ward 72, No. 3275/A, 12th Main Road, HAL 2nd Stage, Indiranagar, Bengaluru 560038"},
    {"name": "Brik Oven", "address": "19, Church Street, MG Road, Bengaluru 560001"},
    {"name": "Magique", "address": "Plot 36, 100 Feet Road, near SJR Junction, Koramangala 6th Block, Bengaluru 560095"},
    {"name": "Tall Oak", "address": "152/24-1, Bangalore East, Seegehalli (Whitefield–Hoskote Road), Bengaluru 560115"},
    {"name": "Yuki", "address": "4, 3rd Floor, 100 Feet Road, KHB Block, Koramangala 5th Block, Bengaluru 560034"},
    {"name": "Oven Story", "address": "cloud-kitchen chain with ~49 outlets across Bangalore, including Binnamangala/CMH Road, Indiranagar"},
    {"name": "Papa Johns", "address": "multi-outlet chain across Bangalore"},
    {"name": "Fresh Factory", "address": "Sarvagna Nagar, Indiranagar, Bengaluru"},
    {"name": "Pasta Street", "address": "Sai Sunrise, 6th Floor, No. 28, 3rd Main, Ashwini Layout, off Inner Ring Road, Koramangala, Bengaluru 560038"},
    {"name": "Taiki", "address": "656, 100 Feet Road, Stage 1, Indiranagar, Bengaluru 560038"},
    {"name": "Byg Brewski", "address": "10/61/2A/2 & 10/62/2A/3, Doddakannenahalli, Sarjapur Road, Bengaluru 560035"},
    {"name": "Cafe Noir", "address": "UB City, Vittal Mallya Road/Lavelle Road, Bengaluru"},
    {"name": "Bombay Brasserie", "address": "#2989/B, 12th Main Road, HAL 2nd Stage, Indiranagar, Bengaluru 560008"},
    {"name": "Kake Di Hatti", "address": "2nd & 3rd Floor, Salarpuria Palladium, HAL 2nd Stage, Indiranagar, Bengaluru 560008"},
    {"name": "Daffys Brewgarden", "address": "Plot No. 48, Ground Floor, 100 Feet Road, Defence Colony, Indiranagar, Bengaluru 560038"},
    {"name": "Terraces", "address": "48, 2nd Main, 100 Feet Road, Defence Colony, Indiranagar, Bengaluru"},
    {"name": "Chulha Chauki Da Dhaba", "address": "1M, Masand Esquire, opp RM Super Market, Hennur, Kalyan Nagar, Bengaluru 560043"},
    {"name": "1131 Bar + Kitchen", "address": "1131, 100 Feet Road, HAL 2nd Stage, Indiranagar, Bengaluru 560038"},
    {"name": "Punjab Grill", "address": "Orion Mall, Dr. Rajkumar Road, Rajajinagar, Bengaluru"},
    {"name": "Foo", "address": "Ground Floor, Forum Rex Walk, Brigade Road, Shanthala Nagar, Ashok Nagar, Bengaluru 560001"},
    {"name": "Hard Rock Cafe", "address": "40, St. Marks Road, Ashok Nagar, Bengaluru 560001"},
    {"name": "Long Boat Brewery", "address": "1st Main, MSR Layout, Chandra Layout, Marathahalli, Bengaluru 560037"},
    {"name": "Artisanal Bier Village", "address": "391, ITPL Main Road, Thigalarapalya, Hoodi, Whitefield, Bengaluru 560048"},
    {"name": "The Bier Library", "address": "#14, Patel Narayana Reddy Layout, 80 Feet Road, Koramangala 6th Block, Bengaluru 560095"},
    {"name": "Vesparo", "address": "KRISHVI Evara, 2018, 2nd/3rd/4th Floor, 100 Feet Road, HAL 2nd Stage, Indiranagar, Bengaluru 560008"},
    {"name": "Red Rhino", "address": "4th Floor, Uptown Square, Whitefield-Hoskote Road, Seegehalli, Whitefield, Bengaluru 560067"},
    {"name": "La Gioia", "address": "1085, 12th Main Road, HAL 2nd Stage, Doopanahalli, Indiranagar, Bengaluru 560008"},
    {"name": "The Dual Room", "address": "Ground Floor, 616, 12th Main Road, 7th Cross, HAL 2nd Stage, Indiranagar/Thippasandra, Bengaluru"},
    {"name": "Phurr", "address": "42/1, 22nd Cross Road, Jayanagar 3rd Block East, Bengaluru 560011"},
    {"name": "Jamming Goat", "address": "1st & 2nd Floor, HAL 2nd Stage, 100 Feet Road, Indiranagar, Bengaluru 560038"},
    {"name": "Chianti", "address": "100 Feet Road, HAL 2nd Stage, Indiranagar, Bengaluru"},
    {"name": "Social", "address": "Plot 118, 3rd Floor, 80 Feet Road, above Bodyworks Spa, KHB Colony, 7th Block, Koramangala, Bengaluru 560095"},
    {"name": "Lazy Suzy", "address": "36, 80 Feet Road, HAL 3rd Stage, Indiranagar, Bengaluru 560075"},
    {"name": "Barbeque Nation", "address": "4005, HAL 2nd Stage, 100 Feet Road, Indiranagar, Bengaluru 560071"},
    {"name": "Woodside Inn", "address": "35, 80 Feet Road, HAL 3rd Stage, New Thippasandra, Bengaluru 560075"},
    {"name": "Antera Kitchen and Bar", "address": "Plot No. 4006, 100 Feet Road, HAL 2nd Stage, Indiranagar, Bengaluru"},
    {"name": "Nagarjuna", "address": "44/1, Residency Road, Shanthala Nagar, Ashok Nagar, Bengaluru 560025"},
    {"name": "Kopittiam Lah", "address": "Ground Floor, 1088, 12th Main Road, Doopanahalli, Indiranagar, Bengaluru 560008"},
    {"name": "Mini Bar", "address": "Ground Floor, 1080, 12th Main Road, HAL 2nd Stage, Appareddipalya, Indiranagar, Bengaluru"},
    {"name": "Bistro Claytopia", "address": "SBI Park, 11, 80 Feet Road, near Wipro Park, Koramangala 1st Block, Bengaluru 560034"},
    {"name": "Tycoons", "address": "1080, 12th Main Road, HAL 2nd Stage, Appareddipalya, Indiranagar, Bengaluru 560008"},
    {"name": "Rim Naam", "address": "The Oberoi Bengaluru, 37-39, Mahatma Gandhi Road, Bengaluru 560001"},
    {"name": "Pixi", "address": "Church Street (near Ashok Nagar), Shanthala Nagar, Bengaluru 560001"},
    {"name": "Rico", "address": "Sy.No-12/1, 13/3, Singanayakanahalli, Nagadasanahalli Main Road, Yelahanka, Bengaluru 560064"},
    {"name": "Ishaara", "address": "Phoenix Mall of Asia (flagship), Bellary Main Road, Batrayanpura, Hebbal, Bengaluru 560094"},
    {"name": "Bobs Bar", "address": "777/I, 100 Feet Road, HAL 2nd Stage, Doopanahalli, Indiranagar, Bengaluru 560008"},
    {"name": "The Reservoire", "address": "3rd & 4th Floor, No. 949, 12th Main Road, HAL 2nd Stage, Indiranagar, Bengaluru 560038"},
    {"name": "Badmaash", "address": "Koramangala 5th/7th Block (2, RB Arcade, 80 Feet Road), Bengaluru"},
    {"name": "Fishermans Wharf", "address": "Opp Shubh Enclave, next to Mandovi Motors, Ambalipura Village, Haralur Road, off Sarjapur Road, Bengaluru 560102"},
    {"name": "Trippy Goat Cafe", "address": "Hatworks Boulevard, 431/1, Cunningham Road, Vasanth Nagar, Bengaluru 560052"},
    {"name": "Bastian Garden City", "address": "4, St Mark's Road, Ashok Nagar, Bengaluru"},
    {"name": "Rumi", "address": "3rd Floor, 598/1, 12th Main Road, HAL 2nd Stage, Indiranagar, Bengaluru 560038"},
    {"name": "The Kind", "address": "1316/F, 18 B Main Road, Marenahalli, JP Nagar 2nd Phase, Bengaluru"},
    {"name": "Olive Beach", "address": "16, Wood Street, Opposite Brigade Towers, Richmond Road, Ashok Nagar, Bengaluru 560025"},
    {"name": "Conçu", "address": "1089/A, 12th Main Road, HAL 2nd Stage, Indiranagar, Bengaluru 560038"},
    {"name": "Ouro", "address": "The Oberoi Bengaluru, 37–39, Mahatma Gandhi Road, Sivanchetti Gardens, Bengaluru 560042"},
    {"name": "DYU Art Café", "address": "No. 23, KHB MIG Colony, 8th Block, Koramangala, Bengaluru 560095"},
    {"name": "Onesta", "address": "63, Jyoti Nivas College Road, 5th Block, Koramangala, Bengaluru 560095"},
    {"name": "Nanav Café & Store", "address": "2286, 14th A Main Road, HAL 2nd Stage, Indiranagar, Bengaluru 560008"},
    {"name": "Rajdhani", "address": "1st Floor, Salarpuria Building, Opposite Reliance Digital, 100 Feet Road, HAL 2nd Stage, Indiranagar, Bengaluru 560038"},
    {"name": "Three Monkeys Brewpub", "address": "4th Floor, Gopalan Signature Mall, Old Madras Road, Bengaluru 560038"},
    {"name": "Paris Panini", "address": "2984, 12th Main Road, Indiranagar, Bengaluru 560038"},
    {"name": "Chakum Chukum", "address": "No. 92, Michael Palaya, New Tippasandra, 1st Main Road, Indiranagar, Bengaluru 560038"},
    {"name": "Aladdin Shawarma", "address": "27, 1st Cross, Bhuvanappa Layout, Opposite Nexus Mall, Tavarekere Main Road, BTM Layout 1st Stage, Bengaluru 560029"},
    {"name": "Toastid Co.", "address": "225, Ground Floor, Domlur, 1st Main Road, Channakesahava Nagar, Bengaluru 560008"},
    {"name": "California Burrito", "address": "No. 1784, Ground Floor, 19th Main Road, Sector 4, HSR Layout, Bengaluru 560102"},
    {"name": "Circa 11", "address": "Plot No. 957, Sodepur, Appareddipalya, 12th Main Road, Indiranagar, Bengaluru 560038"},
    {"name": "Tandoori Taal", "address": "1088, 2nd Floor, Near SHAAP, 12th Main Road, 4th Cross, Indiranagar, Bengaluru 560008"}
]

def extract_area_from_address(address):
    """Extract area from address using keywords."""
    address_lower = address.lower()
    
    area_keywords = {
        'Indiranagar': ['indiranagar', '100 feet', 'defence', 'hal', 'domlur', 'thippasandra'],
        'Koramangala': ['koramangala', 'jyoti', 'nexus', 'hb colony', 'wipro park'],
        'MG Road': ['mg road', 'brigade', 'church street', 'st marks', 'trinity', 'old madras'],
        'Whitefield': ['whitefield', 'ecoworld', 'hoodi', 'itpl', 'seegehalli'],
        'HSR Layout': ['hsr', 'haralur', 'sector 4'],
        'JP Nagar': ['jp nagar', 'marenahalli'],
        'Jayanagar': ['jayanagar'],
        'Marathahalli': ['marathahalli', 'chandra layout'],
        'Ashok Nagar': ['ashok nagar', 'magrath road', 'st. mark', 'museum road', 'shanthala nagar'],
        'UB City': ['ub city', 'vittal mallya', 'lavelle'],
        'Sarjapur Road': ['sarjapur', 'doddakannenahalli'],
        'Hebbal': ['hebbal', 'bellary main', 'hennur'],
        'Yelahanka': ['yelahanka'],
        'BTM Layout': ['btm', 'tavarekere'],
        'Rajajinagar': ['rajajinagar', 'orion mall'],
        'Cunningham Road': ['cunningham', 'vasanth nagar'],
        'Electronic City': ['electronic city']
    }
    
    for area, keywords in area_keywords.items():
        if any(keyword in address_lower for keyword in keywords):
            return area
    
    return 'Bangalore'

def estimate_cuisine_from_name(restaurant_name):
    """Estimate cuisine type based on restaurant name."""
    name_lower = restaurant_name.lower()
    
    cuisine_keywords = {
        'Italian': ['pizza', 'pasta', 'italian', 'chianti', 'brik oven', 'oven story', 'paris panini'],
        'Chinese': ['chinese', 'mandarin', 'dim sum', 'wok', 'lucky chan'],
        'Japanese': ['japanese', 'sushi', 'ramen', 'yuki'],
        'Korean': ['korean', 'koreyaki', 'seoul'],
        'North Indian': ['north indian', 'punjab', 'chandni', 'kake di hatti', 'rajdhani', 'punjab grill', 'chulha'],
        'South Indian': ['south indian', 'dosai', 'idli', 'a2b', 'vidyarthi'],
        'Mexican': ['mexican', 'sanchez', 'burrito', 'california burrito'],
        'Cafe': ['cafe', 'coffee', 'thirdwave', 'brew', 'toast', 'onesta', 'dyu', 'trippy goat'],
        'Bar': ['bar', 'brewery', 'pub', 'social', 'boozy', 'bobs bar', 'mini bar', '1131 bar'],
        'Desserts': ['dessert', 'bakery', 'smoor', 'glens', 'magnolia'],
        'American': ['american', 'burger', 'burgerman', 'hard rock', 'foo'],
        'Continental': ['continental', 'european', 'rim naam', 'olive beach', 'bastian'],
        'Multi-cuisine': ['multi', 'fusion', 'byg', 'long boat', 'artisanal']
    }
    
    for cuisine, keywords in cuisine_keywords.items():
        if any(keyword in name_lower for keyword in keywords):
            return cuisine
    
    return 'Multi-cuisine'

def estimate_price_from_name(restaurant_name):
    """Estimate price range based on restaurant name."""
    name_lower = restaurant_name.lower()
    
    budget_keywords = ['a2b', 'ctrs', 'vidyarthi', 'highway', 'aladdin', 'chakum', 'delhi highway', 'kake di hatti']
    luxury_keywords = ['hard rock', 'oberoi', 'olive', 'rim naam', 'social', 'brewski', 'antier', 'reservoire', 'conçu', 'ouro', 'cafe noir', 'punjab grill']
    
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
        'Rooftop': ['rooftop', 'terrace', 'open', 'beige', 'terraces'],
        'Romantic': ['romantic', 'couple', 'date', 'oia', 'olive beach', 'la gioia'],
        'Family': ['family', 'kids', 'dhaba', 'chulha', 'barbeque nation'],
        'Cozy': ['cafe', 'cozy', 'small', 'thirdwave', 'dyu', 'toastid', 'nanav'],
        'Luxury': ['luxury', 'fine dine', 'premium', 'oberoi', 'rim naam', 'conçu', 'ouro', 'cafe noir', 'punjab grill'],
        'Brewery': ['brew', 'brewery', 'pub', 'byg', 'long boat', 'artisanal', 'bier', 'three monkeys']
    }
    
    for ambience, keywords in ambience_keywords.items():
        if any(keyword in name_lower for keyword in keywords):
            return ambience
    
    return 'Casual'

def create_restaurant_data():
    """Create restaurant data with improved estimation."""
    restaurants = []
    
    for i, restaurant_info in enumerate(RESTAURANT_DATA, 1):
        restaurant_name = restaurant_info['name']
        address = restaurant_info['address']
        
        restaurant_data = {
            'id': i,
            'name': restaurant_name,
            'cuisine': estimate_cuisine_from_name(restaurant_name),
            'area': extract_area_from_address(address),
            'ambience': estimate_ambience_from_name(restaurant_name),
            'price': estimate_price_from_name(restaurant_name),
            'rating': 8.0,  # Default rating
            'image': f"assets/restaurants/restaurant_{i % 20 + 1}.jpg",  # Cycle through existing images
            'maps': f"https://maps.google.com/?q={quote(restaurant_name + ' Bangalore')}"
        }
        
        restaurants.append(restaurant_data)
    
    return restaurants

def main():
    """Main function."""
    print("Creating restaurant data with improved area estimation...")
    
    restaurants = create_restaurant_data()
    
    # Save to JSON
    with open('restaurant_data/restaurants_improved.json', 'w', encoding='utf-8') as f:
        json.dump(restaurants, f, indent=4)
    
    # Convert to JavaScript format
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
    
    with open('restaurant_data/restaurants_new.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"Created {len(restaurants)} restaurants")
    print("JSON saved to: restaurant_data/restaurants_improved.json")
    print("JavaScript saved to: restaurant_data/restaurants_new.js")

if __name__ == "__main__":
    main()