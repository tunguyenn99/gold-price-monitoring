import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def fix_all_records():
    """
    Scans every document in the collection and trims 
    'buy' and 'sell' prices to exactly 6 digits.
    """
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("Error: MONGO_URI not found in .env file.")
        return

    try:
        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client.get_database("gold_db")
        collection = db.get_collection("prices")

        # Fetch all documents
        cursor = collection.find({})
        total_checked = 0
        total_updated = 0

        print("🚀 Starting data cleanup for all records...")

        for doc in cursor:
            doc_id = doc['_id']
            entries = doc.get('entries', [])
            modified = False
            
            cleaned_entries = []
            for entry in entries:
                # Convert to string to slice first 6 characters
                buy_str = str(entry.get('buy', 0))
                sell_str = str(entry.get('sell', 0))

                # Keep only first 6 digits if longer, otherwise keep as is
                new_buy = int(buy_str[:6]) if len(buy_str) > 6 else int(buy_str)
                new_sell = int(sell_str[:6]) if len(sell_str) > 6 else int(sell_str)

                # Check if change is actually needed
                if new_buy != entry.get('buy') or new_sell != entry.get('sell'):
                    modified = True

                cleaned_entries.append({
                    "brand": entry.get('brand'),
                    "buy": new_buy,
                    "sell": new_sell
                })

            # Update document only if values were changed
            if modified:
                collection.update_one(
                    {"_id": doc_id},
                    {"$set": {"entries": cleaned_entries}}
                )
                total_updated += 1
                print(f"✅ Updated record date: {doc.get('date')} (ID: {doc_id})")
            
            total_checked += 1

        print("\n--- FINISHED ---")
        print(f"Total records scanned: {total_checked}")
        print(f"Total records corrected: {total_updated}")
        
        client.close()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Safety confirmation
    confirm = input("Are you sure you want to fix ALL records in the database? (y/n): ")
    if confirm.lower() == 'y':
        fix_all_records()
    else:
        print("Operation cancelled.")