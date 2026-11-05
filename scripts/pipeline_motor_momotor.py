#!/usr/bin/env python3
"""
Pipeline Tarik Harga Motor Bekas (Momotor.id Exclusive) untuk Apache Airflow.
Menggunakan MomotorScraper (High-Speed SSR Parser Anti-WAF).
Terintegrasi dengan:
1. Normalisasi & Entity Matching ke Master Varian & Katalog Sasis Resmi (100 Merek, 4.562 Tipe)
2. Pelacakan Penurunan Harga Real-time (listing_price_history)
3. Rekalkulasi Otomatis Nilai Pasar Wajar / Fair Market Value (market_price_stats)
Database target: motor_bekas.db
"""
import os
import sys
import argparse
from datetime import datetime

MOTOR_DIR = "/Users/macbookair/Documents/Scrape Data"
if MOTOR_DIR not in sys.path:
    sys.path.insert(0, MOTOR_DIR)

from models.database import SessionLocal
from models.catalog import ScrapedListing, ListingPriceHistory, MasterVariant
from scrapers.momotor_scraper import MomotorScraper
from pipeline.entity_matcher import EntityMatcher
from analytics.pricing_engine import PricingAnalyticsEngine

DEFAULT_MOTOR_QUERIES = [
    "Honda Beat", "Yamaha NMAX", "Honda Vario 160", "Yamaha Aerox",
    "Honda Scoopy", "Vespa Sprint", "Kawasaki KLX 150", "Polytron Fox R",
    "Yamaha Fazzio", "Honda ADV 160", "Yamaha Grand Filano", "Honda PCX 160"
]

def run_pipeline(queries=None, max_items_per_query=10, max_total_items=30):
    print("=" * 70)
    print(f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] MEMULAI AIRFLOW PIPELINE MOTOR (SUMBER: MOMOTOR.ID)")
    print(f"Target Sampel: {max_total_items} listing | Max per query: {max_items_per_query}")
    print("=" * 70)

    db = SessionLocal()
    scraper = MomotorScraper()
    matcher = EntityMatcher(db)
    queries = queries or DEFAULT_MOTOR_QUERIES

    total_scraped = 0
    total_inserted = 0
    total_updated = 0
    total_price_drops = 0

    try:
        for q in queries:
            if total_scraped >= max_total_items:
                print(f"\n[Limit Reached] Kuota target {max_total_items} sampel telah terpenuhi.")
                break

            items_to_fetch = min(max_items_per_query, max_total_items - total_scraped)
            print(f"\n-> [Momotor.id] Menarik listing terbaru untuk query: '{q}' (Target: {items_to_fetch} item)...")
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

                    ext_id = str(item.get("external_id") or item.get("url"))
                    existing = db.query(ScrapedListing).filter(
                        ScrapedListing.source_platform == "momotor",
                        ScrapedListing.external_id == ext_id
                    ).first()

                    new_price = float(item.get("price") or 0)

                    if not existing:
                        new_item = ScrapedListing(
                            source_platform="momotor",
                            external_id=ext_id,
                            url=item.get("url", ""),
                            title=item.get("title", ""),
                            raw_description=item.get("raw_description", ""),
                            matched_variant_id=var_id,
                            claimed_year=item.get("claimed_year"),
                            price=new_price,
                            is_dp_price=False,
                            odometer_km=item.get("odometer_km"),
                            tax_status=item.get("tax_status", "Hidup / Panjang"),
                            has_bpkb=item.get("has_bpkb", True),
                            has_stnk=item.get("has_stnk", True),
                            city=item.get("city", "Indonesia"),
                            province=item.get("province", "Indonesia"),
                            posted_at=datetime.utcnow(),
                            scraped_at=datetime.utcnow(),
                            status="ACTIVE" if new_price >= 2500000 else "QUARANTINED",
                            data_origin="LIVE_SCRAPED",
                            seller_name=item.get("seller_name", "Diler Resmi Momotor"),
                            seller_type=item.get("seller_type", "Dealer")
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
                        existing.scraped_at = datetime.utcnow()
                        if var_id:
                            existing.matched_variant_id = var_id
                        total_updated += 1

                db.commit()
            except Exception as err:
                db.rollback()
                print(f"   [Notice] Gagal menarik '{q}': {err}")

        print(f"\n[HASIL PIPELINE AIRFLOW - MOMOTOR.ID]")
        print(f"   - Total Scraped       : {total_scraped}")
        print(f"   - Listing Baru Masuk  : {total_inserted}")
        print(f"   - Listing Terupdate   : {total_updated}")
        print(f"   - Price Drop Tercatat : {total_price_drops}")

        # Recalculate Fair Market Value (FMV)
        print("\n-> Memperbarui Master Database Statistik FMV Motor...")
        engine = PricingAnalyticsEngine(db)
        engine.refresh_daily_market_stats()
        print("✅ [FMV STATS] Berhasil merefresh tabel market_price_stats motor!")

    finally:
        db.close()

    print("=" * 70)
    print("✅ Pipeline Motor Airflow (Momotor.id) Selesai Sukses!")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline Tarik Motor Momotor.id Airflow")
    parser.add_argument("--limit", type=int, default=30, help="Jumlah total listing motor yang ditarik (default: 30)")
    parser.add_argument("--per-query", type=int, default=10, help="Maksimal listing per keyword (default: 10)")
    args = parser.parse_args()

    run_pipeline(max_items_per_query=args.per_query, max_total_items=args.limit)
