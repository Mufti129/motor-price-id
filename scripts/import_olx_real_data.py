#!/usr/bin/env python3
"""
Script Impor Data Real OLX ke motor_bekas.db
Mengimpor 2.783 listing nyata motor bekas dari scrap_olx,
mencocokkan ke master_variants, memvalidasi dengan ScamAndDPDetector,
memperbarui listing_price_history, dan memperbarui statistik pasar.
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

# Pastikan root workspace masuk sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pipeline.scam_detector import ScamAndDPDetector
from pipeline.entity_matcher import EntityMatcher
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_PATH = "motor_bekas.db"
CSV_MOTOR_PATH = "/tmp/scrap_olx_inspect/scrap_olx/exports/dataset_motor.csv"
CSV_MOBIL_PATH = "/tmp/scrap_olx_inspect/scrap_olx/exports/dataset_mobil.csv"
SQLITE_OLX_DB = "/tmp/scrap_olx_inspect/scrap_olx/data/olx_scraper.db"

def parse_location(lokasi_str: str) -> tuple[str, str]:
    """Parse string 'Cibodas, Tangerang Kota, Banten' menjadi ('Tangerang Kota', 'Banten')"""
    if not lokasi_str or not isinstance(lokasi_str, str):
        return "Indonesia", "Indonesia"
    parts = [p.strip() for p in lokasi_str.split(",") if p.strip()]
    if len(parts) >= 3:
        return parts[1], parts[2]
    elif len(parts) == 2:
        return parts[0], parts[1]
    elif len(parts) == 1:
        return parts[0], "Indonesia"
    return "Indonesia", "Indonesia"

def import_real_olx_data():
    print("=== MEMULAI IMPOR DATA REAL OLX KE MOTOR_BEKAS.DB ===")
    
    if not os.path.exists(CSV_MOTOR_PATH):
        print(f"Error: File {CSV_MOTOR_PATH} tidak ditemukan.")
        return

    # 1. Setup DB Session untuk EntityMatcher
    engine = create_engine(f"sqlite:///{DB_PATH}")
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    matcher = EntityMatcher(session)

    # 2. Baca CSV Motor
    df_motor = pd.read_csv(CSV_MOTOR_PATH)
    print(f"Memuat {len(df_motor):,} baris data motor dari {CSV_MOTOR_PATH}...")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Cek jumlah LIVE_SCRAPED sebelum import
    count_before = cur.execute(
        "SELECT COUNT(*) FROM scraped_listings WHERE source_platform = 'olx' AND data_origin = 'LIVE_SCRAPED'"
    ).fetchone()[0]
    print(f"Jumlah listing OLX LIVE_SCRAPED saat ini: {count_before:,} baris.")

    inserted_count = 0
    updated_count = 0
    matched_count = 0
    scam_count = 0

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today_str = datetime.now().strftime("%Y-%m-%d")

    for _, row in df_motor.iterrows():
        item_id = str(row.get("item_id", "")).strip()
        if not item_id:
            continue

        ext_id = f"olx_real_{item_id}"
        url = str(row.get("url", "")).strip()
        judul = str(row.get("judul", "")).strip()
        desc = str(row.get("deskripsi", "")).strip()
        harga = float(row.get("harga", 0)) if pd.notna(row.get("harga")) else 0.0
        tahun = int(row.get("tahun", 0)) if pd.notna(row.get("tahun")) and str(row.get("tahun")).isdigit() else None
        km = int(row.get("kilometer", 0)) if pd.notna(row.get("kilometer")) else 0
        lokasi = str(row.get("lokasi", ""))
        city, prov = parse_location(lokasi)

        bpkb = int(row.get("bpkb", 0)) if pd.notna(row.get("bpkb")) else 0
        stnk = int(row.get("stnk", 0)) if pd.notna(row.get("stnk")) else 0
        pajak_status = str(row.get("pajak_status", "Tidak Disebut"))

        # Evaluasi Scam & DP
        eval_res = ScamAndDPDetector.evaluate(harga, judul, desc, claimed_year=tahun)
        is_dp = 1 if eval_res["is_invalid"] else 0
        if is_dp:
            scam_count += 1

        # Match ke Master Variant
        clean_title = ScamAndDPDetector.sanitize_fuel_mentions(judul)
        var_id, score, matched_name = matcher.match(clean_title, claimed_year=tahun)
        if var_id:
            matched_count += 1

        # Cek apakah sudah ada di database
        existing = cur.execute(
            "SELECT id FROM scraped_listings WHERE external_id = ?", (ext_id,)
        ).fetchone()

        if existing:
            cur.execute("""
                UPDATE scraped_listings SET
                    title = ?, raw_description = ?, matched_variant_id = ?, claimed_year = ?,
                    price = ?, is_dp_price = ?, odometer_km = ?, tax_status = ?,
                    has_bpkb = ?, has_stnk = ?, city = ?, province = ?,
                    scraped_at = ?, data_origin = 'LIVE_SCRAPED', status = 'ACTIVE'
                WHERE external_id = ?
            """, (judul, desc, var_id, tahun, harga, is_dp, km, pajak_status, bpkb, stnk, city, prov, now_str, ext_id))
            updated_count += 1
        else:
            cur.execute("""
                INSERT INTO scraped_listings (
                    source_platform, external_id, url, title, raw_description,
                    matched_variant_id, claimed_year, price, is_dp_price,
                    odometer_km, tax_status, has_bpkb, has_stnk,
                    province, city, posted_at, scraped_at, status, data_origin
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', 'LIVE_SCRAPED')
            """, ('olx', ext_id, url, judul, desc, var_id, tahun, harga, is_dp, km, pajak_status, bpkb, stnk, prov, city, now_str, now_str))
            inserted_count += 1

    conn.commit()

    count_after = cur.execute(
        "SELECT COUNT(*) FROM scraped_listings WHERE source_platform = 'olx' AND data_origin = 'LIVE_SCRAPED'"
    ).fetchone()[0]

    print("\n--- HASIL IMPOR LISTING MOTOR OLX ---")
    print(f"Total Baris Diproses : {len(df_motor):,}")
    print(f"Baru Dimasukkan (New): {inserted_count:,}")
    print(f"Diperbarui (Updated) : {updated_count:,}")
    print(f"Cocok ke Katalog     : {matched_count:,} ({matched_count/len(df_motor)*100:.1f}%)")
    print(f"Ditandai Scam/DP     : {scam_count:,}")
    print(f"Total OLX LIVE di DB : {count_after:,} baris.")

    # 3. Impor Riwayat Harga (Price History)
    if os.path.exists(SQLITE_OLX_DB):
        print("\nMemeriksa riwayat penurunan harga dari olx_scraper.db...")
        olx_conn = sqlite3.connect(SQLITE_OLX_DB)
        price_drop_items = olx_conn.execute("""
            SELECT item_id, harga, harga_awal, harga_sebelumnya, selisih_harga, perubahan_harga_pct, last_scraped_at
            FROM motor WHERE selisih_harga != 0
        """).fetchall()
        print(f"Ditemukan {len(price_drop_items):,} unit yang mengalami perubahan/penurunan harga.")
        
        hist_inserted = 0
        for itm in price_drop_items:
            p_item_id, cur_p, awal_p, prev_p, diff_p, pct_p, rec_t = itm
            p_ext_id = f"olx_real_{p_item_id}"
            rec_t = rec_t or now_str
            old_p = float(prev_p or awal_p or cur_p)
            new_p = float(cur_p)
            drop_pct = abs(float(pct_p))

            listing_row = cur.execute("SELECT id FROM scraped_listings WHERE external_id = ?", (p_ext_id,)).fetchone()
            if listing_row:
                l_id = listing_row[0]
                # Hindari duplikasi riwayat sama
                already_has = cur.execute(
                    "SELECT id FROM listing_price_history WHERE listing_id = ? AND new_price = ?", (l_id, new_p)
                ).fetchone()
                if not already_has:
                    cur.execute("""
                        INSERT INTO listing_price_history (listing_id, old_price, new_price, price_drop_pct, recorded_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (l_id, old_p, new_p, drop_pct, rec_t))
                    hist_inserted += 1

        conn.commit()
        olx_conn.close()
        print(f"Berhasil mencatat {hist_inserted:,} event perubahan harga ke listing_price_history.")

    # 4. Salin dataset mobil ke data/reports/
    if os.path.exists(CSV_MOBIL_PATH):
        out_mobil = "data/reports/dataset_mobil_olx_real.csv"
        df_mobil = pd.read_csv(CSV_MOBIL_PATH)
        df_mobil.to_csv(out_mobil, index=False)
        print(f"\nMenyimpan dataset mobil real ({len(df_mobil):,} unit) ke {out_mobil}")

    # 5. Rekalkulasi Market Price Stats
    print("\nMenghitung ulang ringkasan statistik pasar (market_price_stats)...")
    recalc_stats_query = """
    SELECT matched_variant_id, claimed_year, city, price
    FROM scraped_listings
    WHERE matched_variant_id IS NOT NULL 
      AND is_dp_price = 0 
      AND price >= 2500000 
      AND price <= 200000000
    """
    valid_listings = pd.read_sql_query(recalc_stats_query, conn)
    
    stats_updated = 0
    # Group per variant, year, city
    grouped = valid_listings.groupby(["matched_variant_id", "claimed_year", "city"])
    for (v_id, yr, city_val), grp in grouped:
        prices = grp["price"].values
        if len(prices) >= 2:
            n_count = int(len(prices))
            med_p = float(np.median(prices))
            q1_p = float(np.percentile(prices, 25))
            q3_p = float(np.percentile(prices, 75))
            min_p = float(np.min(prices))
            max_p = float(np.max(prices))

            # Cek apakah record sudah ada
            exist_stat = cur.execute(
                "SELECT id FROM market_price_stats WHERE variant_id = ? AND year = ? AND city = ?",
                (int(v_id), int(yr), str(city_val))
            ).fetchone()

            if exist_stat:
                cur.execute("""
                    UPDATE market_price_stats SET
                        stat_date = ?, sample_count = ?, price_min = ?,
                        price_p25 = ?, price_median = ?, price_p75 = ?, price_max = ?
                    WHERE id = ?
                """, (today_str, n_count, min_p, q1_p, med_p, q3_p, max_p, exist_stat[0]))
            else:
                cur.execute("""
                    INSERT INTO market_price_stats (
                        stat_date, variant_id, year, city, sample_count,
                        price_min, price_p25, price_median, price_p75, price_max
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (today_str, int(v_id), int(yr), str(city_val), n_count, min_p, q1_p, med_p, q3_p, max_p))
            stats_updated += 1

    conn.commit()
    print(f"Berhasil memperbarui/menambahkan {stats_updated:,} kurva statistik harga pasar (market_price_stats).")

    conn.close()
    session.close()
    print("\n=== SEMUA PROSES IMPOR SELESAI DENGAN SUKSES ===")

if __name__ == "__main__":
    import_real_olx_data()
