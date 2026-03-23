import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("SUPABASE_DB_URL")

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'gold_raw';")
    print("Tables in gold_raw:", [r[0] for r in cursor.fetchall()])

    try:
        cursor.execute("SELECT COUNT(*) FROM gold_raw.prices;")
        print("Rows in prices:", cursor.fetchone()[0])

        cursor.execute("SELECT MAX(date) FROM gold_raw.prices;")
        print("Max date in prices:", cursor.fetchone()[0])
    except Exception as e:
        print("Error analyzing prices table:", e)

    try:
        cursor.execute("SELECT COUNT(*) FROM gold_raw.raw_prices;")
        print("Rows in raw_prices:", cursor.fetchone()[0])

        cursor.execute("SELECT MAX(date) FROM gold_raw.raw_prices;")
        print("Max date in raw_prices:", cursor.fetchone()[0])
    except Exception as e:
        print("Error analyzing raw_prices table:", e)

except Exception as e:
    print(e)
