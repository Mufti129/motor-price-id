#!/usr/bin/env python3
"""
Cron & Airflow Periodic Runner untuk Pasar Motor Bekas.
1. Scraping delta/incremental query terpopuler.
2. Normalisasi & eliminasi DP/kredit palsu.
3. Matching ke Master Model & Varian.
4. Refresh tabel statistik Fair Market Value (market_price_stats).
"""
import os
import sys
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from models.database import SessionLocal
from models.catalog import ScrapedListing
from scrapers.olx_scraper import OLXMotorScraper
from pipeline.normalizer import ListingNormalizer
from pipeline.scam_detector import ScamAndDPDetector
from pipeline.entity_matcher import EntityMatcher
from analytics.pricing_engine import PricingAnalyticsEngine

def run_motor_sync(queries=None, pages=1):
    print("=" * 60)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MEMULAI CRON UPDATE HARGA MOTOR BEKAS")
    print("=" * 60)

    db = SessionLocal()
    try:
        matcher = EntityMatcher(db)
        scraper = OLXMotorScraper()
        
        # Target motor terlaris di pasar sekunder Indonesia
        if not queries:
            queries = ["Beat", "Vario 150", "Vario 160", "NMAX", "Aerox", "PCX 160", "Scoopy", "Mio"]

        total_scraped = 0
        total_upserted = 0
        total_scam = 0

        for q in queries:
            print(f"-> Mengambil data terbaru untuk: {q}...")
            try:
                raw_items = scraper.search_listings(query=q, location_code="dki_jakarta", page=0, page_size=20)
                if not raw_items:
                    continue

                for raw in raw_items:
                    total_scraped += 1
                    norm = ListingNormalizer.normalize_listing(raw)
                    var_id, score, _ = matcher.match(norm["title"], norm["claimed_year"])
                    is_dp, _ = ScamAndDPDetector.is_dp_or_credit_listing(
                        price=norm["price"],
                        title=norm["title"],
                        description=norm["raw_description"]
                    )
                    if is_dp:
                        total_scam += 1

                    existing = db.query(ScrapedListing).filter(
                        ScrapedListing.source_platform == norm["source_platform"],
                        ScrapedListing.external_id == norm["external_id"]
                    ).first()

                    if not existing:
                        new_item = ScrapedListing(
                            source_platform=norm["source_platform"],
                            external_id=norm["external_id"],
                            url=norm["url"],
                            title=norm["title"],
                            raw_description=norm["raw_description"],
                            matched_variant_id=var_id,
                            claimed_year=norm["claimed_year"],
                            price=norm["price"] or 0,
                            is_dp_price=is_dp,
                            odometer_km=norm["odometer_km"],
                            tax_status=norm["tax_status"],
                            plate_region=norm["plate_region"],
                            province=norm["province"],
                            city=norm["city"],
                            posted_at=datetime.utcnow()
                        )
                        db.add(new_item)
                        total_upserted += 1
                    else:
                        existing.price = norm["price"] or existing.price
                        existing.is_dp_price = is_dp
                        if var_id:
                            existing.matched_variant_id = var_id

                db.commit()
            except Exception as e:
                print(f"  [Notice] Gagal scrape query '{q}': {e}")

        print(f"\n[HASIL INGESTION] Scraped: {total_scraped} | Baru Masuk: {total_upserted} | Terfilter DP: {total_scam}")

        print("\n-> Menghitung Ulang Fair Market Value (FMV) & Memperbarui Master Stats...")
        engine = PricingAnalyticsEngine(db)
        engine.refresh_daily_market_stats()
        print("✅ Tabel market_price_stats Motor Berhasil Dimutakhirkan!")

    finally:
        db.close()

if __name__ == "__main__":
    run_motor_sync()
