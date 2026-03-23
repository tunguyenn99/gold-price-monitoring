import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from matplotlib.ticker import FuncFormatter

# Load credentials from .env
load_dotenv()

def format_currency(x, p):
    """Formats value as currency with comma separators."""
    return f"{int(x):,}"

def generate_gold_charts():
    """Fetches data from Supabase and generates gold price visualization charts with premium aesthetics."""
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        print("Error: SUPABASE_DB_URL not found in .env")
        return

    # Use relative path for repository compatibility
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up two levels: from sources/utils to root
    project_root = os.path.dirname(os.path.dirname(script_dir))
    output_dir = os.path.join(project_root, "images")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Create database connection
        engine = create_engine(db_url)
        
        # Set premium theme
        sns.set_theme(style="darkgrid", palette="muted")
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.titlepad'] = 20
        plt.rcParams['axes.labelpad'] = 15

        # --- CHART 1: Current Price Comparison (Latest Snapshot) ---
        print("\nGenerating Premium Current Price Comparison chart (Horizontal)...")
        query_latest = """
        SELECT brand, buy_price, sell_price 
        FROM gold_marts.stg_gold_prices 
        WHERE price_timestamp = (SELECT MAX(price_timestamp) FROM gold_marts.stg_gold_prices)
        ORDER BY sell_price DESC
        """
        df_latest = pd.read_sql(query_latest, engine)
        
        if not df_latest.empty:
            plt.figure(figsize=(14, 10))
            
            # Melt data for side-by-bar comparison
            df_melted = df_latest.melt(id_vars='brand', value_vars=['buy_price', 'sell_price'], 
                                      var_name='Price Type', value_name='Price (VND)')
            
            # Map "buy_price" to "Buy" and "sell_price" to "Sell"
            df_melted['Price Type'] = df_melted['Price Type'].map({'buy_price': 'Buy', 'sell_price': 'Sell'})
            
            # Use horizontal bar plot
            ax = sns.barplot(
                data=df_melted, 
                y='brand', 
                x='Price (VND)', 
                hue='Price Type', 
                palette=['#4CAF50', '#F44336'], # Green for Buy, Red for Sell
                edgecolor=".2"
            )
            
            # Add data labels inside bars
            for container in ax.containers:
                ax.bar_label(container, fmt='{:,.0f}', padding=5, fontsize=10, color='black', weight='bold')

            plt.title('Latest Gold Prices Comparison by Brand', fontsize=20, weight='bold', color='#333')
            plt.xlabel('Price (Thousand VND / Lượng)', fontsize=14)
            plt.ylabel('Gold Brand', fontsize=14)
            
            # Move legend to the outside right
            plt.legend(title='Price Type', bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(FuncFormatter(format_currency))
            
            plt.tight_layout()
            output_path = os.path.join(output_dir, 'current_brand_comparison.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Successfully saved: {output_path}")
        else:
            print("No latest data found for current comparison.")

        # --- CHART 2: Historical Price Trends ---
        print("\nGenerating Premium Historical Price Trends chart...")
        query_daily = "SELECT * FROM gold_marts.fct_gold_prices ORDER BY price_date"
        df_daily = pd.read_sql(query_daily, engine)
        
        if not df_daily.empty:
            plt.figure(figsize=(14, 8))
            
            # Use a more vibrant palette for trends
            num_brands = len(df_daily['brand'].unique())
            palette = sns.color_palette("viridis", n_colors=num_brands)
            
            # Plot trends for each brand
            ax2 = sns.lineplot(
                data=df_daily, 
                x='price_date', 
                y='avg_sell_price', 
                hue='brand', 
                marker='o', 
                markersize=8,
                linewidth=3,
                palette=palette
            )
            
            # Add data labels to line points sparingly (only if meaningful)
            if len(df_daily) < 20: # Avoid clutter
                for line in ax2.lines:
                    xdata = line.get_xdata()
                    ydata = line.get_ydata()
                    for x, y in zip(xdata, ydata):
                        ax2.annotate(f'{int(y):,}', (x, y), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9, weight='bold')

            plt.title('Daily Gold Sell Price Trends (Average per Day)', fontsize=20, weight='bold', color='#333')
            plt.ylabel('Avg Sell Price (Thousand VND / Lượng)', fontsize=14)
            plt.xlabel('Date', fontsize=14)
            plt.xticks(rotation=0) # Better with horizontal bars above
            
            # Format y-axis
            ax2.yaxis.set_major_formatter(FuncFormatter(format_currency))
            
            plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', title='Brand', borderaxespad=0.)
            plt.tight_layout()
            output_path_trend = os.path.join(output_dir, 'historical_price_trends.png')
            plt.savefig(output_path_trend, dpi=300, bbox_inches='tight')
            print(f"Successfully saved: {output_path_trend}")
        else:
            print("No historical data found.")

    except Exception as e:
        print(f"Error generating charts: {e}")

if __name__ == "__main__":
    generate_gold_charts()
