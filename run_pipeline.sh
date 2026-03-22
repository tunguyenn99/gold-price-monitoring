# Absolute path to uv
UV="/home/tunguyenn99/.local/bin/uv"

# Export environment variables from .env
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

echo "Starting Gold Price Data Pipeline..."

# 1. Scrape latest data
echo -e "\n[1/4] Scraping gold prices..."
$UV run python sources/scraper.py

# 2. Ingest to Supabase via dlt
echo -e "\n[2/4] Syncing to Supabase via dlt..."
$UV run python sources/dlt_ingestion.py

# 3. Transform with dbt
echo -e "\n[3/4] Transforming daily metrics with dbt..."
cd dbt_project
$UV run dbt run --profiles-dir .
cd ..

# 4. Generate Analysis
echo -e "\n[4/5] Generating Price Comparison Report..."
$UV run python sources/analysis.py

echo -e "\nPipeline execution finished."

# 5. Generate Visual Charts
echo -e "
[5/5] Generating Visualization Charts..."
$UV run python sources/visualize.py
