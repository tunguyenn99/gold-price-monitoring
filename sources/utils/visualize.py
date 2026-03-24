import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from matplotlib.ticker import FuncFormatter

# Load credentials from .env
load_dotenv()

def format_to_millions(x, p):
    """Formats values into Millions (M) (e.g., 171.5 M)."""
    # Assumes input x is in Thousand VND. Divide by 1000 to get Millions.
    return f"{x/1000:.1f} M"

def generate_gold_charts():
    """Fetches data from Supabase and generates gold price visualization charts with premium aesthetics."""
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        print("Error: SUPABASE_DB_URL not found in .env")
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    output_dir = os.path.join(project_root, "images")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Create database connection
        engine = create_engine(db_url)
        
        # Set premium theme
        sns.set_theme(style="whitegrid")
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.titlepad'] = 25

        # --- CHART 1: Current Price Comparison (Horizontal Bar) ---
        print("\nGenerating Premium Current Price Comparison chart...")
        query_latest = """
        SELECT brand, buy_price, sell_price 
        FROM gold_marts.stg_gold_prices 
        WHERE price_timestamp = (SELECT MAX(price_timestamp) FROM gold_marts.stg_gold_prices)
        ORDER BY sell_price DESC
        """
        df_latest = pd.read_sql(query_latest, engine)
        
        if not df_latest.empty:
            plt.figure(figsize=(16, 10))
            
            # Melt data for side-by-bar comparison
            df_melted = df_latest.melt(id_vars='brand', value_vars=['buy_price', 'sell_price'], 
                                      var_name='Price Type', value_name='Price (VND)')
            
            df_melted['Price Type'] = df_melted['Price Type'].map({'buy_price': 'Buy', 'sell_price': 'Sell'})
            
            ax1 = sns.barplot(
                data=df_melted, y='brand', x='Price (VND)', hue='Price Type', 
                palette=['#2ecc71', '#e74c3c'], edgecolor=".2"
            )
            
            # Add data labels inside bars in "M" format
            for container in ax1.containers:
                ax1.bar_label(container, fmt=lambda x: f'{x/1000:.1f}M', padding=5, weight='bold')

            plt.title('Latest Gold Prices Comparison (Millions VND)', fontsize=22, weight='bold')
            plt.xlabel('Price (Million VND / Lượng)', fontsize=14)
            plt.ylabel('Gold Brand', fontsize=14)
            
            # LEGEND: Move to the right outside the plot
            plt.legend(title='Price Type', bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
            
            # Format X-axis
            ax1.xaxis.set_major_formatter(FuncFormatter(format_to_millions))
            
            plt.tight_layout()
            output_path_bar = os.path.join(output_dir, 'current_brand_comparison.png')
            plt.savefig(output_path_bar, dpi=300, bbox_inches='tight')

        # --- CHART 2: Historical Price Trends (Line Chart) ---
        print("\nGenerating Premium Historical Price Trends chart...")
        query_hourly = "SELECT * FROM gold_marts.fct_gold_prices ORDER BY price_hour"
        df_hourly = pd.read_sql(query_hourly, engine)
        
        if not df_hourly.empty:
            df_hourly['price_hour'] = pd.to_datetime(df_hourly['price_hour'])
            plt.figure(figsize=(16, 9))
            
            # Use high-contrast palette for many brands
            palette = sns.color_palette("husl", n_colors=len(df_hourly['brand'].unique()))
            
            ax2 = sns.lineplot(
                data=df_hourly, x='price_hour', y='avg_sell_price', hue='brand', 
                marker='o', markersize=7, linewidth=3, palette=palette, alpha=0.8
            )
            
            # Y-AXIS ZOOM: Focus on the fluctuation range
            ymin = df_hourly['avg_sell_price'].min() * 0.995
            ymax = df_hourly['avg_sell_price'].max() * 1.005
            plt.ylim(ymin, ymax)

            # DATA LABELS: Label only the last point for each brand
            for line in ax2.lines:
                y_coords = line.get_ydata()
                x_coords = line.get_xdata()
                if len(y_coords) > 0:
                    plt.annotate(f'{y_coords[-1]/1000:.1f}M', 
                                 xy=(x_coords[-1], y_coords[-1]),
                                 xytext=(8, 0), textcoords='offset points',
                                 color=line.get_color(), weight='bold', fontsize=10)

            plt.title('Gold Price Fluctuation Trends (Millions VND)', fontsize=22, weight='bold')
            plt.ylabel('Million VND / Lượng', fontsize=14)
            plt.xlabel('Time of Observation', fontsize=14)
            
            # LEGEND: Move to the right outside the plot
            plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', title='Brand', borderaxespad=0.)
            
            # Format Y-axis and rotate X labels
            ax2.yaxis.set_major_formatter(FuncFormatter(format_to_millions))
            plt.xticks(rotation=30)
            
            plt.tight_layout()
            output_path_trend = os.path.join(output_dir, 'historical_price_trends.png')
            plt.savefig(output_path_trend, dpi=300, bbox_inches='tight')
            print("Successfully saved all charts.")

    except Exception as e:
        print(f"Error generating charts: {e}")

if __name__ == "__main__":
    generate_gold_charts()