import requests
from bs4 import BeautifulSoup
import json
import datetime
import os
import re
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def sanitize_price(price_str):
    """Extracts numeric value from price string."""
    # Remove all non-digit characters (including dots and commas used as separators)
    digits = re.sub(r'\D', '', price_str)
    if digits:
        return int(digits)
    return 0

def scrape_gold_prices():
    url = "https://www.24h.com.vn/gia-vang-hom-nay-c425.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None
    
    soup = BeautifulSoup(response.content, "html.parser")
    table_container = soup.find("div", class_="tabBody")
    if not table_container:
        print("Could not find gold price table container.")
        return None
    
    rows = table_container.find_all("tr")
    data = []
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 3:
            # First row is usually header
            if "Loại vàng" in cols[0].get_text():
                continue
                
            brand = cols[0].get_text(strip=True)
            buy_raw = cols[1].get_text(strip=True)
            sell_raw = cols[2].get_text(strip=True)
            
            buy_price = sanitize_price(buy_raw)
            sell_price = sanitize_price(sell_raw)
            
            if brand and (buy_price > 0 or sell_price > 0):
                data.append({
                    "brand": brand,
                    "buy": buy_price,
                    "sell": sell_price
                })
                
    return data

def save_to_json(new_entries):
    file_path = "data/gold_prices.json"
    os.makedirs("data", exist_ok=True)
    
    history = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    
    # Check if we already have an entry for today (to avoid duplicates if run multiple times)
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # We will store daily records. If run multiple times a day, we can either:
    # 1. Update the record for today
    # 2. Add as a new entry with timestamp
    # Let's go with timestamped records for better granularity
    
    history.append({
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date": today_str,
        "entries": new_entries
    })
    
    # Keep only the last 365 records to avoid massive file size
    if isinstance(history, list) and len(history) > 365:
        history = history[-365:]
        
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

def save_to_mongodb(new_entries):
    """Uploads the scraped data to MongoDB Atlas."""
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("MONGO_URI not found in environment variables. Skipping MongoDB upload.")
        return
    
    try:
        # Connect to MongoDB Atlas
        client = MongoClient(mongo_uri)
        db = client.get_database("gold_db")
        collection = db.get_collection("prices")
        
        document = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "entries": new_entries
        }
        
        # Insert the daily snapshot
        result = collection.insert_one(document)
        print(f"Successfully uploaded to MongoDB Atlas. Document ID: {result.inserted_id}")
        client.close()
    except Exception as e:
        print(f"Error uploading to MongoDB: {e}")

if __name__ == "__main__":
    prices = scrape_gold_prices()
    if prices:
        # Save to local JSON for dashboard (fallback/static version)
        save_to_json(prices)
        
        # Save to MongoDB Atlas (cloud storage)
        save_to_mongodb(prices)
        
        print(f"Workflow completed successfully.")
    else:
        print("No data scraped.")
