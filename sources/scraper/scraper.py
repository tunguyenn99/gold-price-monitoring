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
    # Xóa tất cả ký tự không phải số (bao gồm dấu phẩy, dấu chấm và phần tăng giảm)
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
    # Tìm trực tiếp bảng chứa dữ liệu dựa trên class từ HTML bạn cung cấp
    table_container = soup.find("table", class_="gia-vang-search-data-table")
    if not table_container:
        print("Could not find gold price table container.")
        return None
    
    rows = table_container.find_all("tr")
    data = []
    
    for row in rows:
        cols = row.find_all("td")
        
        # Dựa trên HTML:
        # cols[0] -> Thương hiệu (SJC, DOJI...)
        # cols[1] -> Giá mua hôm nay (Chứa span.fixW và span.colorGreen)
        # cols[2] -> Giá bán hôm nay (Chứa span.fixW và span.colorGreen)
        # cols[3], [4] -> Giá hôm qua (không lấy)
        if len(cols) >= 3:
            # Lấy tên brand từ thẻ h2 bên trong td đầu tiên
            brand_node = cols[0].find("h2")
            brand = brand_node.get_text(strip=True) if brand_node else cols[0].get_text(strip=True)
            
            # QUAN TRỌNG: Chỉ lấy text trong <span class="fixW"> để tránh bị dính số tăng giảm
            buy_node = cols[1].find("span", class_="fixW")
            sell_node = cols[2].find("span", class_="fixW")
            
            # Nếu tìm thấy thẻ span.fixW thì lấy text của nó, nếu không lấy toàn bộ text của td
            buy_raw = buy_node.get_text(strip=True) if buy_node else cols[1].get_text(strip=True)
            sell_raw = sell_node.get_text(strip=True) if sell_node else cols[2].get_text(strip=True)
            
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
    
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    history.append({
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date": today_str,
        "entries": new_entries
    })
    
    if isinstance(history, list) and len(history) > 365:
        history = history[-365:]
        
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

def save_to_mongodb(new_entries):
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("MONGO_URI not found. Skipping MongoDB upload.")
        return
    
    try:
        client = MongoClient(mongo_uri)
        db = client.get_database("gold_db")
        collection = db.get_collection("prices")
        
        document = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "entries": new_entries
        }
        
        result = collection.insert_one(document)
        print(f"Uploaded to MongoDB. ID: {result.inserted_id}")
        client.close()
    except Exception as e:
        print(f"Error uploading to MongoDB: {e}")

if __name__ == "__main__":
    prices = scrape_gold_prices()
    if prices:
        save_to_json(prices)
        save_to_mongodb(prices)
        print(f"Workflow completed successfully.")
    else:
        print("No data scraped.")