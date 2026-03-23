import dlt
from dlt.destinations import postgres
import os
import sys
from dotenv import load_dotenv

# Add the project root to sys.path to allow importing the 'mongodb' source
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

load_dotenv()

def load_mongo_to_supabase():
    """Loads gold price data from MongoDB Atlas to Supabase using dlt."""
    # MongoDB connection
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("MONGO_URI not set. Skipping.")
        return
        
    # Destination credentials
    # We prioritize SUPABASE_DB_URL but also support individual components
    supabase_url = os.getenv("SUPABASE_DB_URL")
    
    # Run the dlt pipeline
    # We use an explicit destination object if the URL is provided
    # otherwise we let dlt resolve from individual env vars
    destination = "postgres"
    if supabase_url:
        print(f"Using provided SUPABASE_DB_URL for destination.")
        destination = postgres(credentials=supabase_url)
    else:
        print("SUPABASE_DB_URL not found. dlt will attempt to resolve from GOLD_PRICE_PIPELINE__ environment variables.")

    pipeline = dlt.pipeline(
        pipeline_name="gold_price_pipeline",
        destination=destination,
        dataset_name="gold_raw"
    )

    try:
        from sources.mongodb import mongodb
    except ImportError:
        from sources.mongodb import mongodb

    # Use the built-in mongodb source
    source = mongodb(
        connection_url=mongo_uri,
        database="gold_db",
        collection_names=["prices"]
    )

    print(f"Starting pipeline run for {pipeline.pipeline_name}...")
    try:
        # Load data with merge strategy to avoid duplicates based on timestamp
        load_info = pipeline.run(
            source, 
            write_disposition="merge"
        )
        print(load_info)
    except Exception as e:
        print(f"Pipeline run failed: {e}")
        raise

if __name__ == "__main__":
    load_mongo_to_supabase()
