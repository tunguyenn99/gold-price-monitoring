import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

def analyze_gold_prices():
    """Reads transformed gold price data from Supabase and generates comparisons."""
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        print("SUPABASE_DB_URL not set. Skipping analysis.")
        return

    try:
        # Create engine for Supabase Postgres
        engine = create_engine(db_url)
        
        # Query the dbt fact table from the gold_marts schema
        # We assume dbt has run and created this table
        query = "SELECT * FROM gold_marts.fct_gold_prices ORDER BY price_hour DESC"
        df = pd.read_sql(query, engine)
        
        if df.empty:
            print("No data found in gold_marts.fct_gold_prices. Ensure dbt run has completed.")
            return

        print("\n" + "="*40)
        print("GOLD PRICE TRENDS (via Supabase & dbt)")
        print("="*40)
        
        # Show top 5 recent entries
        print("\n--- Recent Hourly Averages ---")
        print(df.head(10))
        
        # Price Comparison: Latest vs Previous Hour for SJC
        sjc_df = df[df['brand'] == 'SJC'].sort_values('price_hour', ascending=False)
        if len(sjc_df) >= 2:
            today = sjc_df.iloc[0]
            yesterday = sjc_df.iloc[1]
            
            diff_sell = today['avg_sell_price'] - yesterday['avg_sell_price']
            percent_sell = (diff_sell / yesterday['avg_sell_price']) * 100
            
            status = "📈 UP" if diff_sell > 0 else "📉 DOWN" if diff_sell < 0 else "➡️ STABLE"
            
            print(f"\n[SJC BRAND COMPARISON]")
            print(f"Time: {today['price_hour']} vs {yesterday['price_hour']}")
            print(f"Status: {status}")
            print(f"Sell Price Change: {diff_sell:,.0f} VND ({percent_sell:+.2f}%)")
            print(f"Current Avg Sell: {today['avg_sell_price']:,.0f} VND")
            print(f"Current Avg Buy:  {today['avg_buy_price']:,.0f} VND")
        else:
            print("\nNot enough historical data for SJC comparison yet.")
            
        print("="*40 + "\n")

    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    analyze_gold_prices()
