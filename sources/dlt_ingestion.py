import dlt
from dlt.destinations import postgres
import os
import sys
from dotenv import load_dotenv

# Add the project root to sys.path to allow importing the 'mongodb' source
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

def load_mongo_to_supabase():
    """Loads gold price data from MongoDB Atlas to Supabase using dlt."""
    # MongoDB connection
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("MONGO_URI not set. Skipping.")
        return
        
    supabase_url = os.getenv("SUPABASE_DB_URL")
    if not supabase_url:
        print("SUPABASE_DB_URL not set. Skipping.")
        return

    # Run the dlt pipeline
    # We use an explicit destination object to ensure high-precedence configuration
    pipeline = dlt.pipeline(
        pipeline_name="gold_price_pipeline",
        destination=postgres(credentials=supabase_url),
        dataset_name="gold_raw"
    )

    try:
        from mongodb import mongodb
    except ImportError:
        from sources.mongodb import mongodb

    # Use the built-in mongodb source
    source = mongodb(
        connection_url=mongo_uri,
        database="gold_db",
        collection_names=["prices"]
    )

    # Load data with merge strategy to avoid duplicates based on timestamp
    load_info = pipeline.run(
        source, 
        write_disposition="merge"
    )
    print(load_info)

if __name__ == "__main__":
    load_mongo_to_supabase()
