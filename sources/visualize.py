import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

def generate_gold_charts():
    """Fetches data from Supabase and generates gold price visualization charts."""
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        print("Error: SUPABASE_DB_URL not found in .env")
        return

    # Use relative path for repository compatibility (Relative to project root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, "images")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Create database connection
        engine = create_engine(db_url)
        
        # --- CHART 1: Current Price Comparison (Latest Snapshot) ---
        print("\nGenerating Current Price Comparison chart...")
        query_latest = """
        SELECT brand, buy_price, sell_price 
        FROM gold_marts.stg_gold_prices 
        WHERE price_timestamp = (SELECT MAX(price_timestamp) FROM gold_marts.stg_gold_prices)
        """
        df_latest = pd.read_sql(query_latest, engine)
        
        if not df_latest.empty:
            plt.figure(figsize=(14, 7))
            sns.set_theme(style="whitegrid")
            
            # Melt data for side-by-bar comparison
            df_melted = df_latest.melt(id_vars='brand', value_vars=['buy_price', 'sell_price'], 
                                      var_name='Price Type', value_name='Price (VND)')
            
            # Map "buy_price" to "Buy" and "sell_price" to "Sell"
            df_melted['Price Type'] = df_melted['Price Type'].map({'buy_price': 'Buy', 'sell_price': 'Sell'})
            
            ax = sns.barplot(data=df_melted, x='brand', y='Price (VND)', hue='Price Type', palette="muted")
            
            # Add data labels to bars
            for container in ax.containers:
                ax.bar_label(container, fmt='{:,.0f}', padding=3, rotation=90, fontsize=9)

            plt.title('Latest Gold Prices Comparison by Brand', fontsize=16)
            plt.xticks(rotation=45, ha='right')
            plt.ylabel('Price (VND)')
            plt.xlabel('Gold Brand')
            
            # Format y-axis to show millions clearly
            from matplotlib.ticker import FuncFormatter
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
            
            plt.tight_layout()
            output_path = os.path.join(output_dir, 'current_brand_comparison.png')
            plt.savefig(output_path)
            print(f"Successfully saved: {output_path}")
        else:
            print("No latest data found for current comparison.")

        # --- CHART 2: Historical Price Trends (Latest/Avg Price per Day) ---
        print("\nGenerating Historical Price Trends chart...")
        query_daily = "SELECT * FROM gold_marts.fct_gold_prices ORDER BY price_date"
        df_daily = pd.read_sql(query_daily, engine)
        
        if not df_daily.empty:
            plt.figure(figsize=(14, 7))
            sns.set_theme(style="darkgrid")
            
            # Plot trends for each brand
            ax2 = sns.lineplot(data=df_daily, x='price_date', y='avg_sell_price', hue='brand', marker='o', linewidth=2)
            
            # Add data labels to line points
            for line in ax2.lines:
                xdata = line.get_xdata()
                ydata = line.get_ydata()
                for x, y in zip(xdata, ydata):
                    ax2.annotate(f'{int(y):,}', (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)

            plt.title('Daily Gold Sell Price Trends Over Time', fontsize=16)
            plt.ylabel('Average Sell Price (VND)')
            plt.xlabel('Date')
            plt.xticks(rotation=45)
            
            # Format y-axis
            from matplotlib.ticker import FuncFormatter
            ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
            
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Brand')
            plt.tight_layout()
            output_path_trend = os.path.join(output_dir, 'historical_price_trends.png')
            plt.savefig(output_path_trend)
            print(f"Successfully saved: {output_path_trend}")
        else:
            print("No historical data found in fct_gold_prices Layer. Ensure dbt run is finished.")

    except Exception as e:
        print(f"Error generating charts: {e}")

if __name__ == "__main__":
    generate_gold_charts()
