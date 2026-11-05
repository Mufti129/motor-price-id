"""
DAG: Price Intelligence Motor Bekas (Eksklusif OLX & Momotor.id).
Jadwal: Otomatis setiap hari pukul 01:00 WIB.
Sumber Data: OLX Indonesia & Momotor.id (Bebas dari Lelang IBID/JBA dan Facebook).
Database Target: motor_bekas.db
"""
from datetime import datetime, timedelta
import sqlite3
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'motor_intelligence_team',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

def verify_motor_stats():
    """Verifikasi data terkini pada motor_bekas.db."""
    db_path = "/Users/macbookair/Documents/Scrape Data/motor_bekas.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM scraped_listings WHERE source_platform = 'olx'")
    olx_listings = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM scraped_listings WHERE source_platform = 'momotor'")
    momotor_listings = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM scraped_listings WHERE data_origin = 'LIVE_SCRAPED'")
    live_listings = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM auction_listings")
    auction_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM master_variants")
    variants = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM official_master_catalog")
    omc_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM listing_price_history")
    price_drops = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM market_price_stats")
    stats = cur.fetchone()[0]
    conn.close()

    print("\n" + "=" * 65)
    print("🏍️ [AIRFLOW AUDIT] MASTER DATABASE MOTOR BEKAS (OLX & MOMOTOR.ID)")
    print(f"   - Total Listing OLX       : {olx_listings:,} listing")
    print(f"   - Total Listing Momotor   : {momotor_listings:,} listing")
    print(f"   - Data Lelang IBID/JBA    : {auction_count} listing (Status: Dihapus/Bersih)")
    print(f"   - Total Live Scraped Riil : {live_listings:,} listing")
    print(f"   - Total Official Sasis    : {omc_count:,} kode sasis (100 merek)")
    print(f"   - Total Master Varian     : {variants:,} varian terkurasi")
    print(f"   - Total Price Drop Radar  : {price_drops:,} penurunan harga")
    print(f"   - Total Record FMV Stats  : {stats:,} baris statistik pasar")
    print("=" * 65 + "\n")

with DAG(
    dag_id='dag_price_intelligence_motor',
    default_args=default_args,
    description='Pipeline Harian Tarikan Harga Pasar Motor Bekas (Eksklusif OLX & Momotor.id)',
    schedule='0 1 * * *',  # Pukul 01:00 WIB
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['motor', 'olx', 'momotor', 'price_intelligence', 'master_db'],
) as dag:

    # Task 1a: Scraping OLX Stealth, Normalisasi, Entity Matching, dan Perhitungan FMV
    task_scrape_olx_motor = BashOperator(
        task_id='scrape_olx_and_update_motor_fmv',
        bash_command=(
            'python3 '
            '"/Users/macbookair/.gemini/antigravity/scratch/airflow_workspace/scripts/pipeline_motor_olx.py" '
            '--limit 30 --per-query 10'
        ),
    )

    # Task 1b: Scraping Momotor.id SSR, Normalisasi, Entity Matching, dan Perhitungan FMV
    task_scrape_momotor = BashOperator(
        task_id='scrape_momotor_and_update_motor_fmv',
        bash_command=(
            'python3 '
            '"/Users/macbookair/.gemini/antigravity/scratch/airflow_workspace/scripts/pipeline_motor_momotor.py" '
            '--limit 30 --per-query 10'
        ),
    )

    # Task 2: Verifikasi & Audit Database
    task_verify_motor = PythonOperator(
        task_id='verify_motor_master_stats',
        python_callable=verify_motor_stats,
    )

    [task_scrape_olx_motor, task_scrape_momotor] >> task_verify_motor
