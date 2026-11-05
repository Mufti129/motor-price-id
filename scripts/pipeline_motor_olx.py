#!/usr/bin/env python3
"""
Pipeline Tarik Harga Motor Bekas (OLX Exclusive) untuk Apache Airflow.
Menggunakan OLXStealthScraper (Headless Selenium Chrome Anti-WAF).
Terintegrasi dengan:
1. Multi-factor Scam & Fraud Detector (eliminasi DP palsu, harga dummy 12345, WTB, aksesoris)
2. Normalisasi & Entity Matching ke Master Varian & Katalog Sasis Resmi (100 Merek, 4.562 Tipe)
3. Pelacakan Penurunan Harga Real-time (listing_price_history)
4. Rekalkulasi Otomatis Nilai Pasar Wajar / Fair Market Value (market_price_stats)
Database target: motor_bekas.db
"""
import os
import sys
import re
import argparse
from datetime import datetime

MOTOR_DIR = "/Users/macbookair/Documents/Scrape Data"
if MOTOR_DIR not in sys.path:
    sys.path.insert(0, MOTOR_DIR)

from models.database import SessionLocal
from models.catalog import ScrapedListing, ListingPriceHistory, MasterVariant
from scrapers.olx_stealth_scraper import OLXStealthScraper
from pipeline.scam_detector import ScamAndDPDetector
from pipeline.entity_matcher import EntityMatcher
from analytics.pricing_engine import PricingAnalyticsEngine

DEFAULT_MOTOR_QUERIES = [
    "Honda Beat", "Honda Vario 160", "Yamaha NMAX", "Yamaha Aerox",
    "Honda PCX 160", "Honda Scoopy", "Yamaha FreeGo", "Polytron Fox R",
    "Vespa Sprint", "Kawasaki KLX 150", "Yamaha Fazzio", "Honda ADV 160"
]

def run_pipeline(queries=None, max_items_per_query=10, max_total_items=30, headless=True):
    print("=" * 70)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MEMULAI AIRFLOW PIPELINE MOTOR (SUMBER: OLX STEALTH)")
    print(f"Target Sampel: {max_total_items} listing | Max per query: {max_items_per_query}")
    print("=" * 70)

    db = SessionLocal()
    scraper = OLXStealthScraper(headless=headless)
    matcher = EntityMatcher(db)
    queries = queries or DEFAULT_MOTOR_QUERIES

    total_scraped = 0
    total_inserted = 0
    total_updated = 0
    total_scam_filtered = 0
    total_price_drops = 0

    try:
        for q in queries:
            if total_scraped >= max_total_items:
                print(f"\n[Limit Reached] Kuota target {max_total_items} sampel telah terpenuhi.")
                break

            items_to_fetch = min(max_items_per_query, max_total_items - total_scraped)
            print(f"\n-> [OLX Stealth] Menarik listing terbaru untuk query: '{q}' (Target: {items_to_fetch} item)...")
            try:
                raw_items = scraper.scrape_live_search(keyword=q, max_items=items_to_fetch)
                if not raw_items:
                    print(f"   [Notice] Tidak ada data baru untuk query '{q}'.")
                    continue

                for item in raw_items:
                    if total_scraped >= max_total_items:
                        break

                    total_scraped += 1
                    var_id, score, _ = matcher.match(item["title"], item.get("claimed_year"))

                    is_dp = item.get("is_dp", False)
                    if is_dp:
                        total_scam_filtered += 1

                    ext_id = str(item.get("external_id") or item.get("url"))
                    existing = db.query(ScrapedListing).filter(
                        ScrapedListing.source_platform == "olx",
                        ScrapedListing.external_id == ext_id
                    ).first()

                    new_price = float(item.get("price") or 0)

                    if not existing:
                        new_item = ScrapedListing(
                            source_platform="olx",
                            external_id=ext_id,
                            url=item.get("url", ""),
                            title=item.get("title", ""),
                            raw_description=item.get("raw_description", ""),
                            matched_variant_id=var_id,
                            claimed_year=item.get("claimed_year"),
                            price=new_price,
                            is_dp_price=is_dp,
                            odometer_km=item.get("odometer_km"),
                            tax_status=item.get("tax_status"),
                            has_bpkb=item.get("has_bpkb", True),
                            has_stnk=item.get("has_stnk", True),
                            city=item.get("city", "Indonesia"),
                            province=item.get("province", "Indonesia"),
                            posted_at=datetime.utcnow(),
                            scraped_at=datetime.utcnow(),
                            status="ACTIVE" if not is_dp and new_price >= 2500000 else "QUARANTINED",
                            data_origin="LIVE_SCRAPED",
                            quality_flag=item.get("scam_reason") if is_dp else None
                        )
                        db.add(new_item)
                        total_inserted += 1
                    else:
                        old_price = float(existing.price or 0)
                        # Deteksi Price Drop
                        if old_price > new_price > 0:
                            drop_pct = ((old_price - new_price) / old_price) * 100.0
                            drop_hist = ListingPriceHistory(
                                listing_id=existing.id,
                                old_price=old_price,
                                new_price=new_price,
                                price_drop_pct=drop_pct,
                                recorded_at=datetime.utcnow()
                            )
                            db.add(drop_hist)
                            total_price_drops += 1
                            print(f"   [🔥 Price Drop] {item['title'][:35]} turun {drop_pct:.1f}% (Rp {old_price:,.0f} -> Rp {new_price:,.0f})")

                        existing.price = new_price
                        existing.is_dp_price = is_dp
                        existing.scraped_at = datetime.utcnow()
                        if var_id:
                            existing.matched_variant_id = var_id
                        total_updated += 1

                db.commit()
            except Exception as err:
                db.rollback()
                print(f"   [Notice] Gagal menarik '{q}': {err}")

        print(f"\n[HASIL PIPELINE AIRFLOW]")
        print(f"   - Total Scraped       : {total_scraped}")
        print(f"   - Listing Baru Masuk  : {total_inserted}")
        print(f"   - Listing Terupdate   : {total_updated}")
        print(f"   - Terfilter Scam/DP   : {total_scam_filtered}")
        print(f"   - Price Drop Tercatat : {total_price_drops}")

        # Recalculate Fair Market Value (FMV)
        print("\n-> Memperbarui Master Database Statistik FMV Motor...")
        engine = PricingAnalyticsEngine(db)
        engine.refresh_daily_market_stats()
        print("✅ [FMV STATS] Berhasil merefresh tabel market_price_stats motor!")

    finally:
        scraper.close()
        db.close()

    print("=" * 70)
    print("✅ Pipeline Motor Airflow (OLX Stealth) Selesai Sukses!")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline Tarik Motor OLX Airflow")
    parser.add_argument("--limit", type=int, default=30, help="Jumlah total listing motor yang ditarik (default: 30)")
    parser.add_argument("--per-query", type=int, default=10, help="Maksimal listing per keyword (default: 10)")
    args = parser.parse_args()

    run_pipeline(max_items_per_query=args.per_query, max_total_items=args.limit)
