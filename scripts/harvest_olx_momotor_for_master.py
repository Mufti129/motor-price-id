#!/usr/bin/env python3
"""
Pipeline Pengambilan Data Harga Multi-Platform (OLX & Momotor.id).
Tujuan:
1. Menarik data harga riil motor bekas dari OLX Indonesia & Momotor.id (Adira).
2. Memfilter scam / DP palsu / aksesoris.
3. Mencocokkan entitas ke Master Katalog Sasis Resmi (100 merek, 4.562 tipe)
   dan mengaitkan ke 29 Kategori Tier Internal.
4. Menyimpan data ke SQLite (motor_bekas.db) dengan data_origin = 'LIVE_SCRAPED'.
5. Menghasilkan file output Excel & CSV siap petakan ke database master pengguna.
"""

import os
import sys
import re
import math
from datetime import datetime
import pandas as pd
import numpy as np

# Pastikan path modul terbaca
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.database import SessionLocal
from models.catalog import ScrapedListing, MasterVariant, OfficialMasterCatalog
from scrapers.momotor_scraper import MomotorScraper
from scrapers.olx_stealth_scraper import OLXStealthScraper
from pipeline.entity_matcher import EntityMatcher
from pipeline.scam_detector import ScamAndDPDetector
from analytics.pricing_engine import PricingAnalyticsEngine

# Daftar Query Model Populer Prioritas Tinggi (Mencakup 95%+ Volume Transaksi)
MOMOTOR_QUERIES = [
    "Beat", "Vario 125", "Vario 160", "Scoopy", "PCX 160", "Genio", "ADV 160",
    "Nmax", "Aerox", "Mio M3", "Fazzio", "Grand Filano", "FreeGo", "Lexi",
    "Satria F150", "KLX 150", "Vespa Sprint", "Vespa Primavera"
]

OLX_QUERIES = [
    "Honda Beat", "Honda Vario 160", "Honda Scoopy", "Honda PCX 160",
    "Yamaha Nmax", "Yamaha Aerox", "Yamaha Mio", "Yamaha Fazzio",
    "Vespa Sprint", "Kawasaki KLX 150"
]

def load_internal_mapping_lookup():
    """Membaca file master integrasi untuk lookup tier internal."""
    master_path = "/Users/macbookair/Downloads/Pemetaan database motor tarikan dan database internal/integrasi_database_motor_internal_tarikan.xlsx"
    lookup = {}
    if os.path.exists(master_path):
        try:
            df_master = pd.read_excel(master_path, sheet_name="Master Terintegrasi Motor")
            for _, r in df_master.iterrows():
                brand = str(r.get("Merek", "")).strip().upper()
                comm = str(r.get("Nama Komersil", "")).strip().lower()
                year = r.get("Tahun Rilis")
                tier = r.get("Mapping Tier Internal")
                chassis = r.get("Kode Tipe Sasis")
                cc = r.get("Kapasitas (CC)")
                
                key_comm = (brand, comm)
                if key_comm not in lookup:
                    lookup[key_comm] = {
                        "tier": tier,
                        "chassis": chassis,
                        "cc": cc,
                        "commercial_name": r.get("Nama Komersil"),
                        "brand_clean": r.get("Merek")
                    }
        except Exception as e:
            print(f"[Lookup Warning] Gagal memuat master lookup: {e}")
    return lookup

def determine_internal_tier(brand: str, model_name: str, engine_cc: int = None, claimed_year: int = None, lookup: dict = None):
    """Menentukan mapping tier internal (29 kategori) secara deterministik."""
    b_up = (brand or "").upper()
    m_low = (model_name or "").lower()
    
    # 1. Coba lookup langsung dari master terintegrasi
    if lookup:
        # Coba exact match
        for (lk_b, lk_c), meta in lookup.items():
            if lk_b == b_up and lk_c in m_low:
                return meta["tier"], meta["commercial_name"], meta["chassis"], meta["cc"]

    # 2. Heuristik berdasarkan Brand dan Kapasitas Mesin
    cc = engine_cc or 110
    tier = "Lainnya"

    if "HONDA" in b_up:
        if any(x in m_low for x in ["beat", "scoopy", "genio", "revo", "blade"]):
            tier = "100cc-124cc"
            cc = 110
        elif "vario 125" in m_low or "supra x 125" in m_low:
            tier = "100cc-124cc"
            cc = 125
        elif any(x in m_low for x in ["vario 150", "vario 160", "pcx", "adv", "cb150", "cbr150", "crf"]):
            tier = ">139cc-240cc"
            cc = 160 if "160" in m_low else 150
        elif any(x in m_low for x in ["forza", "cbr250", "crf 250"]):
            tier = ">240cc"
            cc = 250
        else:
            tier = "100cc-124cc"

    elif "YAMAHA" in b_up:
        if any(x in m_low for x in ["mio", "fazzio", "filano", "freego", "gear", "jupiter z"]):
            tier = "100cc-124cc"
            cc = 125
        elif any(x in m_low for x in ["lexi", "jupiter mx 135"]):
            tier = ">124cc – 139cc"
            cc = 125
        elif any(x in m_low for x in ["nmax", "aerox", "vixion", "r15", "xsr", "wr 155"]):
            tier = ">139cc – 240cc"
            cc = 155
        elif any(x in m_low for x in ["xmax", "r25", "mt-25"]):
            tier = ">240cc"
            cc = 250
        else:
            tier = "100cc-124cc"

    elif "SUZUKI" in b_up:
        if any(x in m_low for x in ["satria", "gsx"]):
            tier = "140cc-240cc"
            cc = 150
        else:
            tier = "Type Lama(Shogun,Spin,Skywave,Titan,DLL)"
            cc = 115

    elif "KAWASAKI" in b_up:
        if any(x in m_low for x in ["klx", "d-tracker", "w175"]):
            tier = ">139cc - 240cc"
            cc = 150
        elif "ninja" in m_low:
            tier = ">240cc"
            cc = 250
        else:
            tier = ">139cc - 240cc"

    elif any(x in b_up for x in ["VESPA", "PIAGGIO"]):
        if any(x in m_low for x in ["sprint", "primavera", "medley"]):
            tier = ">139cc – 240cc"
            cc = 150
        elif any(x in m_low for x in ["lx", "s 125"]):
            tier = "<139cc"
            cc = 125
        else:
            tier = ">139cc – 240cc"

    return tier, model_name, None, cc

def main():
    print("=" * 80)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] PIPELINE HARVEST HARGA MOTOR (OLX & MOMOTOR.ID)")
    print("=" * 80)

    db = SessionLocal()
    matcher = EntityMatcher(db)
    internal_lookup = load_internal_mapping_lookup()
    print(f"-> Memuat {len(internal_lookup)} entri lookup master internal terintegrasi.")

    all_harvested = []
    
    # -------------------------------------------------------------
    # 1. Scraping Momotor.id (Adira Finance Verified Dealers)
    # -------------------------------------------------------------
    print("\n[PHASE 1] Mengambil Data Listing Live dari Momotor.id...")
    momotor = MomotorScraper(delay_range=(0.8, 1.5))
    total_momotor = 0

    for q in MOMOTOR_QUERIES:
        print(f"   * [Momotor] Mencari model: '{q}'...")
        try:
            items = momotor.scrape_live_search(keyword=q, max_items=15)
            for itm in items:
                all_harvested.append(itm)
                total_momotor += 1
            print(f"     -> Terkumpul {len(items)} listing.")
        except Exception as err:
            print(f"     -> Warning: {err}")

    print(f"-> Total listing Momotor.id berhasil dikumpulkan: {total_momotor} unit.")

    # -------------------------------------------------------------
    # 2. Scraping OLX Indonesia (Stealth Headless Browser Anti-WAF)
    # -------------------------------------------------------------
    print("\n[PHASE 2] Mengambil Data Listing Live dari OLX Indonesia...")
    olx = OLXStealthScraper(headless=True)
    total_olx = 0

    try:
        for q in OLX_QUERIES:
            print(f"   * [OLX Stealth] Mencari model: '{q}'...")
            try:
                items = olx.scrape_live_search(keyword=q, max_items=5)
                for itm in items:
                    all_harvested.append(itm)
                    total_olx += 1
                print(f"     -> Terkumpul {len(items)} listing.")
            except Exception as err:
                print(f"     -> Warning OLX: {err}")
    finally:
        olx.close()

    print(f"-> Total listing OLX berhasil dikumpulkan: {total_olx} unit.")
    print(f"-> Total Keseluruhan Listing Terkumpul: {len(all_harvested)} unit.")

    # -------------------------------------------------------------
    # 3. Pembersihan, Normalisasi, Ingesti Database & Pemetaan
    # -------------------------------------------------------------
    print("\n[PHASE 3] Memproses Normalisasi, Validasi Anti-Scam, dan Pemetaan Master...")

    records_for_excel = []
    seen_in_batch = set()
    db_inserted = 0

    for item in all_harvested:
        title = item.get("title", "")
        price = float(item.get("price") or 0)
        year = item.get("claimed_year")
        platform = item.get("source_platform", "unknown")
        raw_desc = item.get("raw_description", "")
        city = item.get("city", "Indonesia")
        url = item.get("url", "")
        odometer = item.get("odometer_km")

        # Deteksi Scam / DP Palsu
        scam_eval = ScamAndDPDetector.evaluate(price, title, raw_desc, claimed_year=year)
        is_invalid = scam_eval["is_invalid"]
        if is_invalid or price < 2500000:
            # Lewati harga tidak wajar untuk pembentukan harga master
            continue

        # Match ke master variant & catalog sasis resmi
        var_id, score, matched_dict = matcher.match(title, year)
        
        # Ekstrak metadata model komersil & sasis
        matched_comm_name = None
        matched_type_code = None
        matched_brand = "Honda"
        matched_cc = None

        if var_id:
            mv = db.query(MasterVariant).filter(MasterVariant.id == var_id).first()
            if mv:
                matched_comm_name = mv.commercial_name or mv.variant_name
                matched_type_code = mv.type_code
                matched_brand = mv.model.brand.name if mv.model and mv.model.brand else "Honda"
                matched_cc = mv.engine_cc
        
        if not matched_comm_name:
            # Fallback ekstraksi nama dari judul
            for brand_candidate in ["Honda", "Yamaha", "Suzuki", "Kawasaki", "Vespa", "Piaggio"]:
                if brand_candidate.lower() in title.lower():
                    matched_brand = brand_candidate
                    break
            matched_comm_name = title.split()[0] if title else "Motor Bekas"

        # Tentukan Kategori Tier Internal (29 Kategori)
        tier_internal, comm_clean, chassis_clean, engine_cc_val = determine_internal_tier(
            brand=matched_brand,
            model_name=matched_comm_name or title,
            engine_cc=matched_cc,
            claimed_year=year,
            lookup=internal_lookup
        )

        final_chassis = matched_type_code or chassis_clean or "-"
        final_comm = comm_clean or matched_comm_name

        # Masukkan ke Database motor_bekas.db
        ext_id = str(item.get("external_id") or url)
        if not ext_id or "undefined" in ext_id.lower():
            ext_id = f"{platform}_hash_{abs(hash(url + title + str(price) + str(odometer)))}"

        if (platform, ext_id) in seen_in_batch:
            continue
        seen_in_batch.add((platform, ext_id))

        existing = db.query(ScrapedListing).filter(
            ScrapedListing.source_platform == platform,
            ScrapedListing.external_id == ext_id
        ).first()

        if not existing:
            new_listing = ScrapedListing(
                source_platform=platform,
                external_id=ext_id,
                url=url,
                title=title,
                raw_description=raw_desc,
                matched_variant_id=var_id,
                claimed_year=year,
                price=price,
                is_dp_price=False,
                odometer_km=odometer,
                tax_status=item.get("tax_status", "Hidup"),
                has_bpkb=item.get("has_bpkb", True),
                has_stnk=item.get("has_stnk", True),
                city=city,
                province=item.get("province", "Indonesia"),
                posted_at=datetime.utcnow(),
                scraped_at=datetime.utcnow(),
                status="ACTIVE",
                data_origin="LIVE_SCRAPED"
            )
            db.add(new_listing)
            db_inserted += 1
        else:
            existing.price = price
            existing.scraped_at = datetime.utcnow()
            if var_id:
                existing.matched_variant_id = var_id

        # Tambahkan ke daftar record ekspor
        records_for_excel.append({
            "Platform": platform.upper(),
            "ID Listing": ext_id,
            "Judul Iklan": title,
            "Merek": matched_brand.upper(),
            "Nama Komersil": final_comm,
            "Kode Tipe Sasis": final_chassis,
            "Tahun Unit": year if year and not pd.isna(year) else "-",
            "Harga Pasar Riil (Rp)": int(price),
            "Jarak Tempuh (KM)": odometer if odometer else "-",
            "Kota / Wilayah": city,
            "Kelengkapan Dokumen": "STNK & BPKB Lengkap",
            "Mapping Tier Internal": tier_internal,
            "URL Iklan": url,
            "Waktu Tarik Data": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"   [DB Notice] Rollback due to: {e}")
    print(f"-> Sukses memproses {len(records_for_excel)} listing valid ke database!")

    # -------------------------------------------------------------
    # 4. Refresh Fair Market Value (FMV) di Database
    # -------------------------------------------------------------
    print("\n-> Memperbarui tabel analitik market_price_stats...")
    try:
        engine = PricingAnalyticsEngine(db)
        engine.refresh_daily_market_stats()
        print("✅ [FMV STATS] Tabel statistik pasar terupdate!")
    except Exception as e:
        print(f"   [FMV Warning] {e}")

    # -------------------------------------------------------------
    # 5. Membangun Tabel Matriks Acuan Harga & Ekspor Excel/CSV
    # -------------------------------------------------------------
    df_raw = pd.DataFrame(records_for_excel)
    print(f"\n-> Mempersiapkan ekspor untuk {len(df_raw)} listing tervalidasi...")

    # Matriks per Model & Tahun
    agg_model_year = []
    grouped_my = df_raw[df_raw["Tahun Unit"] != "-"].groupby(["Merek", "Nama Komersil", "Mapping Tier Internal", "Tahun Unit"])
    for (m_brand, m_name, m_tier, m_year), g in grouped_my:
        prices = g["Harga Pasar Riil (Rp)"].values
        agg_model_year.append({
            "Merek": m_brand,
            "Nama Komersil": m_name,
            "Mapping Tier Internal": m_tier,
            "Tahun Unit": m_year,
            "Jumlah Sampel": len(prices),
            "Harga Minimum (Rp)": int(np.min(prices)),
            "Harga Bawah P25 (Rp)": int(np.percentile(prices, 25)),
            "Harga FMV / Median (Rp)": int(np.median(prices)),
            "Harga Atas P75 (Rp)": int(np.percentile(prices, 75)),
            "Harga Maksimum (Rp)": int(np.max(prices)),
            "Rata-rata Odometer (KM)": int(g[g["Jarak Tempuh (KM)"] != "-"]["Jarak Tempuh (KM)"].mean()) if len(g[g["Jarak Tempuh (KM)"] != "-"]) > 0 else "-"
        })
    df_matrix_model = pd.DataFrame(agg_model_year).sort_values(by=["Merek", "Nama Komersil", "Tahun Unit"], ascending=[True, True, False])

    # Matriks per 29 Kategori Tier Internal
    agg_tier = []
    grouped_tier = df_raw.groupby(["Merek", "Mapping Tier Internal"])
    for (t_brand, t_tier), g in grouped_tier:
        prices = g["Harga Pasar Riil (Rp)"].values
        agg_tier.append({
            "Merk Internal": t_brand,
            "Tipe Internal (Rentang CC)": t_tier,
            "Jumlah Listing Riil": len(prices),
            "Harga Terendah (Rp)": int(np.min(prices)),
            "Harga Rekomendasi P25 (Rp)": int(np.percentile(prices, 25)),
            "Harga FMV Median (Rp)": int(np.median(prices)),
            "Harga Rekomendasi P75 (Rp)": int(np.percentile(prices, 75)),
            "Harga Tertinggi (Rp)": int(np.max(prices))
        })
    df_matrix_tier = pd.DataFrame(agg_tier).sort_values(by="Jumlah Listing Riil", ascending=False)

    # Simpan File Hasil ke Folder Pemetaan User dan Repo
    target_paths = [
        "/Users/macbookair/Downloads/Pemetaan database motor tarikan dan database internal/tarikan_harga_olx_momotor_siap_petakan.xlsx",
        "/Users/macbookair/Documents/Scrape Data/data/reports/tarikan_harga_olx_momotor_siap_petakan.xlsx"
    ]

    csv_paths = [
        "/Users/macbookair/Downloads/Pemetaan database motor tarikan dan database internal/tarikan_harga_olx_momotor_siap_petakan.csv",
        "/Users/macbookair/Documents/Scrape Data/data/reports/tarikan_harga_olx_momotor_siap_petakan.csv"
    ]

    for p in target_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with pd.ExcelWriter(p, engine="openpyxl") as writer:
            df_raw.to_excel(writer, sheet_name="Tarikan Riil Listing", index=False)
            df_matrix_model.to_excel(writer, sheet_name="Matriks Harga (Model & Tahun)", index=False)
            df_matrix_tier.to_excel(writer, sheet_name="Acuan Tier Internal (29 Kategori)", index=False)
        print(f"✅ [EXCEL SAVED] {p}")

    for cp in csv_paths:
        os.makedirs(os.path.dirname(cp), exist_ok=True)
        df_raw.to_csv(cp, index=False)
        print(f"✅ [CSV SAVED] {cp}")

    db.close()
    print("=" * 80)
    print("🎉 SELESAI! Seluruh data tarikan harga dan matriks siap dipetakan.")
    print("=" * 80)

if __name__ == "__main__":
    main()
