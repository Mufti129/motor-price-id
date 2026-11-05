"""
Harvesting Engine: Penarikan Data Harga Pasar Mobil IBID MAP
Menyimpan data master varian, estimasi harga lelang, dan data per grade ke SQLite & CSV.
"""

import os
import sqlite3
import pandas as pd
import time
import logging
from ibid_map_client import IbidMapClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CarPriceHarvester")

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "ibid_map_cars.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "ibid_map_cars_dataset.csv")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table master brands
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS master_brands (
        id INTEGER PRIMARY KEY,
        brand_name TEXT UNIQUE,
        category TEXT DEFAULT 'CAR'
    )
    """)

    # Table car market prices
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS car_market_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT,
        series TEXT,
        cylinder TEXT,
        type TEXT,
        year INTEGER,
        transmission TEXT,
        location TEXT,
        min_price REAL,
        max_price REAL,
        grade_a_price REAL,
        grade_b_price REAL,
        grade_c_price REAL,
        grade_d_price REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")


def harvest(limit_brands: int = None, delay_sec: float = 0.5):
    client = IbidMapClient()
    init_db()
    
    brands = client.get_brands()
    logger.info(f"Found {len(brands)} car brands in IBID MAP.")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    records = []
    brand_list = brands[:limit_brands] if limit_brands else brands

    for b in brand_list:
        brand_name = b.get("label", "").strip()
        if not brand_name:
            continue
        
        cursor.execute("INSERT OR IGNORE INTO master_brands (id, brand_name) VALUES (?, ?)", (b.get("id"), brand_name))
        conn.commit()
        
        logger.info(f"Fetching variants for brand: {brand_name}")
        variants = client.get_variants(merk=brand_name)
        
        # Deduplicate variant tuples
        unique_variants = set()
        for v in variants:
            seri = v.get("seri")
            silinder = v.get("silinder")
            tipe = v.get("tipe")
            tahun = v.get("tahun")
            lokasi = v.get("lokasi", "JAKARTA")
            
            if seri and tipe and tahun:
                unique_variants.add((seri, silinder, tipe, tahun, lokasi))
        
        logger.info(f"Total unique variants for {brand_name}: {len(unique_variants)}")

        for seri, silinder, tipe, tahun, lokasi in unique_variants:
            for transmisi in ["MT", "AT"]:
                # Check price
                res_price = client.check_price(
                    merk=brand_name,
                    seri=seri,
                    silinder=silinder or "",
                    tipe=tipe,
                    tahun=str(tahun),
                    transmisi=transmisi
                )
                
                min_p = float(res_price.get("min_harga")) if res_price.get("min_harga") else None
                max_p = float(res_price.get("max_harga")) if res_price.get("max_harga") else None
                
                # Only proceed if we have a price point
                if min_p or max_p:
                    # Fetch Grade breakdown
                    grade_res = client.get_price_by_grade(
                        brand=brand_name,
                        series=seri,
                        cylinder=silinder or "",
                        tipe=tipe,
                        year=str(tahun),
                        transmission=transmisi
                    )
                    grade_items = grade_res.get("item", []) if isinstance(grade_res, dict) else []
                    
                    grades = {}
                    for g in grade_items:
                        g_name = g.get("grade")
                        g_price = g.get("totalHarga") or g.get("hargaTertinggi") or g.get("hargaTerendah")
                        if g_name and g_price:
                            grades[g_name.upper()] = float(g_price)
                    
                    record = {
                        "brand": brand_name,
                        "series": seri,
                        "cylinder": silinder,
                        "type": tipe,
                        "year": int(tahun),
                        "transmission": transmisi,
                        "location": lokasi,
                        "min_price": min_p,
                        "max_price": max_p,
                        "grade_a_price": grades.get("A"),
                        "grade_b_price": grades.get("B"),
                        "grade_c_price": grades.get("C"),
                        "grade_d_price": grades.get("D"),
                    }
                    records.append(record)
                    
                    cursor.execute("""
                    INSERT INTO car_market_prices 
                    (brand, series, cylinder, type, year, transmission, location, min_price, max_price, grade_a_price, grade_b_price, grade_c_price, grade_d_price)
                    VALUES (:brand, :series, :cylinder, :type, :year, :transmission, :location, :min_price, :max_price, :grade_a_price, :grade_b_price, :grade_c_price, :grade_d_price)
                    """, record)
                    conn.commit()
                    logger.info(f"Saved: {brand_name} {seri} {tipe} ({tahun} {transmisi}) -> Min: Rp {min_p:,.0f}" if min_p else f"Saved {brand_name} {seri}")
                    
                time.sleep(delay_sec)

    conn.close()

    if records:
        df = pd.DataFrame(records)
        df.to_csv(CSV_PATH, index=False)
        logger.info(f"Successfully harvested {len(records)} vehicle records. Exported to {CSV_PATH}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Harvest Car Market Auction Price from IBID Astra MAP")
    parser.add_argument("--brands", type=int, default=3, help="Limit number of brands to harvest (default: 3)")
    parser.add_argument("--delay", type=float, default=0.2, help="Delay between requests in seconds")
    args = parser.parse_args()

    harvest(limit_brands=args.brands, delay_sec=args.delay)
