import dlt
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def load_mongo_to_supabase():
    """Loads gold price data from MongoDB Atlas to Supabase using dlt."""
    # MongoDB connection
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("MONGO_URI not set. Skipping.")
        return
        
    client = MongoClient(mongo_uri)
    db = client.get_database("gold_db")
    collection = db.get_collection("prices")

    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        print("SUPABASE_DB_URL not set. Skipping.")
        return

    # Run the dlt pipeline
    # We use an explicit destination with credentials to avoid resolution issues in GitHub Actions
    pipeline = dlt.pipeline(
        pipeline_name="gold_price_pipeline",
        destination=dlt.destinations.postgres(credentials=db_url),
        dataset_name="gold_raw"
    )

    # Source data generator
    def get_data():
        for doc in collection.find():
            # Convert ObjectId to string for Postgres compatibility
            doc["_id"] = str(doc["_id"])
            yield doc

    # Load data with merge strategy to avoid duplicates based on timestamp
    load_info = pipeline.run(
        get_data(), 
        table_name="raw_prices", 
        write_disposition="merge", 
        primary_key="timestamp"
    )
    print(load_info)

if __name__ == "__main__":
    load_mongo_to_supabase()
