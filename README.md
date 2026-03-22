# 📈 Vietnam Gold Price Monitor — Modern Data Stack

A professional, end-to-end data pipeline for monitoring and analyzing gold price trends in Vietnam. This project implements a **Modern Data Stack (MDS)** architecture to scrape, ingest, transform, and visualize gold prices automatically every 2 hours.

---

## 🏗️ System Architecture

This project follows a linear, automated pipeline from raw data collection to final business intelligence:

```yml
🌍 24h.com.vn (Website)
       |
       | [Scrape: BeautifulSoup4/Requests]
       v
🍃 MongoDB Atlas (Raw Landing Zone)
       |
       | [Ingest: dlt (Data Load Tool)]
       v
💎 Supabase / Postgres (Data Warehouse)
       |
       +--- [Transform: dbt (Medallion Architecture)] ---+
       |                                                 |
       |   (stg_gold_prices) ------> (fct_gold_prices)   |
       |                                                 |
       +-----------------------+-------------------------+
                               |
                               | [Analysis: Pandas/Seaborn]
                               v
📊 Matplotlib Charts (Images Generation)
       |
       | [Orchestrate: GitHub Actions]
       v
🖥️ GitHub Repository (Final Insights)
```

---

## 💡 Why This Project?

The gold market in Vietnam is known for its **extreme volatility**. This project was built to **solve the monitoring challenge** by:

* 🤖 **Automation**: Running 24/7 on GitHub Actions without any manual intervention.
* ⏳ **Historical Accuracy**: Moving beyond "current price" to build a rich historical database in Supabase and MongoDB.
* 🧠 **Informed Decisions**: Providing clear, pre-calculated trend visualizations that highlight market shifts over time.
* 🚀 **Modern Data Stack**: Using industry-standard tools: `dlt`, `dbt`, and `Supabase`.

---

## 📊 Market Insights

![Current Price Comparison](images/current_brand_comparison.png)
*Latest gold prices by brand with automated data labels.*

![Historical Trends](images/historical_price_trends.png)
*Daily average sell price trends across various brands.*

---

## 🛠️ Tech Stack Details

| Stage | Tool | Description |
| :--- | :--- | :--- |
| **Extraction** | `Python` | Scrapers using BeautifulSoup4 & Requests. |
| **Landing** | `MongoDB` | NoSQL storage for raw JSON responses (Audit trail). |
| **Ingestion** | `dlt` | Automated schema evolution & data loading. |
| **Warehouse** | `Supabase` | Managed PostgreSQL on the cloud. |
| **Transform** | `dbt` | Medallion architecture inside Supabase (Staging -> Marts). |
| **Visualization**| `Seaborn` | High-quality statistical charts with Matplotlib. |
| **Orchestrator** | `GH Actions` | Cron job scheduling & CI/CD. |

---

## 📁 Project Structure

```text
gold-price-monitoring/
├── .github/workflows/    # CI/CD Automation (GitHub Actions)
├── dbt_project/          # dbt Models, Seeds & Configs
├── images/               # Generated Analytics & Visualization Charts
├── sources/              # Core Python Processing Scripts
│   ├── scraper.py        # Web Scraper Engine
│   ├── dlt_ingestion.py  # Mongo -> Supabase Ingestion Logic
│   ├── visualize.py      # Automated Chart Generator
│   └── analysis.py       # Trend & Statistical Analytics
├── data/                 # Local Data Backups (CSV/JSON)
└── run_pipeline.sh       # Local Execution Entry point
```

---

## 🚀 Getting Started

### 1️⃣ Requirements
* Python 3.12+ & `uv` package manager.
* MongoDB Atlas & Supabase Accounts.

### 2️⃣ Quick Start
```bash
# Clone and Setup
git clone https://github.com/yourusername/gold-price-monitoring.git
cd gold-price-monitoring

# Create .env from template (Edit your credentials)
cp .env.example .env

# Run Full Pipeline
chmod +x run_pipeline.sh
./run_pipeline.sh
```

---

## 🛡️ Security & CI/CD

> [![IMPORTANT IF YOU CLONE THIS REPO](https://img.shields.io/badge/IMPORTANT-Critical-red)]()
> To ensure the **GitHub Actions** workflow runs successfully, you must add the following **GitHub Repository Secrets**:

| Secret Name | Description |
| :--- | :--- |
| `MONGO_URI` | MongoDB Atlas Connection String |
| `SUPABASE_DB_URL` | Full Postgres Connection URL (Transaction Pooler) |
| `SUPABASE_DB_PASSWORD` | Supabase Database Password |
| `SUPABASE_DB_HOST` | Supabase Host Address |
| `SUPABASE_DB_USER` | Supabase Username (postgres.xxxx) |
| `SUPABASE_DB_PORT` | Connection Port (6543) |

---