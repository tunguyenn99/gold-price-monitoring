import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
DATABASE_URL = os.getenv("SUPABASE_DB_URL")

# Connect to the database
try:
    print(f"Attempting to connect to: {DATABASE_URL.split('@')[-1]}")
    connection = psycopg2.connect(DATABASE_URL)
    print("✅ Connection successful!")
    connection.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
