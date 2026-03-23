import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    try:
        host = os.getenv('SUPABASE_DB_HOST')
        user = os.getenv('SUPABASE_DB_USER')
        password = os.getenv('SUPABASE_DB_PASSWORD')
        port = os.getenv('SUPABASE_DB_PORT')
        dbname = os.getenv('SUPABASE_DB_NAME', 'postgres')
        
        print(f"Đang thử kết nối tới: {host}")
        print(f"User: {user}")
        print(f"Port: {port}")
        print(f"Database: {dbname}")
        
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            dbname=dbname
        )
        print("\n✅ KẾT NỐI THÀNH CÔNG!")
        conn.close()
    except Exception as e:
        print(f"\n❌ KẾT NỐI THẤT BẠI: {e}")

if __name__ == "__main__":
    test_connection()
