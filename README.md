# MotorPrice ID - Used Motorcycle Intelligence & Scraping Platform

MotorPrice ID is an end-to-end data engineering, web scraping, and machine learning price intelligence system designed to harvest, clean, analyze, and monitor used motorcycle market prices in Indonesia across platforms such as OLX Indonesia, Momotor, and major classified networks.

---

## Key Features

1. **Multi-Source Data Ingestion & Harvesting:**
   - Robust scraper engine with custom user-agent rotation, location-based querying (Jabodetabek, Java, Bali, National), and anti-WAF fallback mechanisms.
   - Captures granular metadata: seller details, vehicle mileage, listing timestamps, and document conditions.

2. **AI & NLP Data Cleansing Pipeline:**
   - **Slang & Jargon Dictionary:** Automatically parses Indonesian automotive market terms for vehicle taxes (*pajak hidup*, *pajak off 2x*, *kaleng 2028*), legal documents (*BPKB + STNK lengkap* vs *STNK only*), and regional license plate codes (*Plat B*, *Plat D*, etc.).
   - **Clickbait & Down Payment (DP) Scam Detector:** Automatically filters out predatory credit listings masquerading as low cash prices.
   - **Fuzzy Entity Matcher:** Resolves unstructured, noisy listing titles and typographical errors (e.g. *Pagio*, *Vario 150 kles*) into standardized Master Catalog IDs.

3. **Pricing Intelligence & Statistical Analytics:**
   - Outlier filtering via Interquartile Range (IQR).
   - Real-time computation of statistical quartiles:
     - **P25 (Bargain / Quick Sale Price)**
     - **Median (Fair Market Value / FMV)**
     - **P75 (Pristine / Low Mileage Price)**
   - **Arbitrage / Bargain Hunter Detector:** Automatically flags verified listings priced significantly below fair market median.

4. **Interactive Streamlit Web Application:**
   - Professional executive dashboard with Plotly charts.
   - Interactive Fair Market Value (FMV) calculator with condition and mileage adjustments.
   - Granular raw dataset explorer with search, multi-attribute filtering, and one-click CSV export.
   - Scraper control center to trigger ad-hoc crawling tasks.
   - Standardized Master Catalog explorer (Honda, Yamaha, Kawasaki, Piaggio, Vespa, Suzuki).

---

## Directory Structure

```text
├── app.py                      # Main Streamlit web application
├── streamlit_app.py            # Streamlit Cloud default entry point alias
├── main.py                     # Command Line Interface (CLI) runner
├── requirements.txt            # Python dependencies for deployment
├── .gitignore                  # Git ignore rules
├── models/
│   ├── database.py             # Database engine & session manager (SQLite / PostgreSQL)
│   └── catalog.py              # SQLAlchemy ORM schemas
├── data/
│   └── seed_master_motor.py    # Official motorcycle master catalog seed data
├── pipeline/
│   ├── slang_dictionary.py     # Regex patterns & vocabulary dictionary
│   ├── normalizer.py           # Rule-based text attribute extractor
│   ├── scam_detector.py        # DP clickbait detector
│   └── entity_matcher.py       # RapidFuzz entity disambiguation engine
├── scrapers/
│   └── olx_scraper.py          # Marketplace extractor engine
├── analytics/
│   └── pricing_engine.py       # Fair Market Value (FMV) and percentile calculator
└── tests/
    └── test_pipeline.py        # Automated unit tests
```

---

## Deployment to Streamlit Cloud

### Step 1: Push Code to GitHub
1. Initialize git repository (if not yet initialized):
   ```bash
   git init
   git add .
   git commit -m "feat: initial release of MotorPrice ID platform"
   ```
2. Create a new repository on your GitHub account (e.g., `motor-price-id`).
3. Set remote and push:
   ```bash
   git branch -M main
   git remote add origin https://github.com/<your-username>/motor-price-id.git
   git push -u origin main
   ```

### Step 2: Deploy on Streamlit Cloud
1. Log in to [share.streamlit.io](https://share.streamlit.io/).
2. Click **"Create app"** and select your GitHub repository.
3. Set the configuration:
   - **Repository:** `your-username/motor-price-id`
   - **Branch:** `main`
   - **Main file path:** `app.py` or `streamlit_app.py`
4. Click **"Deploy!"**. The application will automatically install dependencies from `requirements.txt`, initialize the database, and launch the web interface.

---

## Local Development Setup

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run unit tests:**
   ```bash
   python3 -m unittest tests/test_pipeline.py
   ```

4. **Launch Streamlit Web UI:**
   ```bash
   streamlit run app.py
   ```

5. **Run CLI Scraper:**
   ```bash
   python3 main.py --query "Vario 150" --pages 2
   ```
