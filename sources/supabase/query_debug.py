import os
import psycopg2
from dotenv import load_dotenv
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

load_dotenv()
db_url = os.getenv("SUPABASE_DB_URL")

try:
    conn = psycopg2.connect(db_url)
    df = pd.read_sql("SELECT price_timestamp, brand, buy_price, sell_price FROM gold_marts.stg_gold_prices ORDER BY sell_price DESC LIMIT 10", conn)
    print(df)
except Exception as e:
    print(e)
