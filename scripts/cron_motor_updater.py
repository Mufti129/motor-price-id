#!/usr/bin/env python3
"""
Cron & Airflow Periodic Runner untuk Pasar Motor Bekas.
1. Scraping live anti-WAF menggunakan OLXStealthScraper.
2. Normalisasi, sanitasi scam/DP, deteksi dokumen & pajak.
3. Matching ke Master Model, Varian & Sasis Resmi.
4. Pelacakan histori perubahan / penurunan harga (Price Drop Radar).
5. Refresh tabel statistik Fair Market Value (market_price_stats).
"""
import os
import sys
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from models.database import SessionLocal
from models.catalog import ScrapedListing, ListingPriceHistory
from scrapers.olx_stealth_scraper import OLXStealthScraper
from pipeline.scam_detector import ScamAndDPDetector
from pipeline.entity_matcher import EntityMatcher
from analytics.pricing_engine import PricingAnalyticsEngine

def run_motor_sync(queries=None, max_items_per_query=15, headless=True):
    print("=" * 60)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MEMULAI PIPELINE TARIK DATA LIVE MOTOR BEKAS (OLX STEALTH)")
    print("=" * 60)

    db = SessionLocal()
    scraper = OLXStealthScraper(headless=headless)
    matcher = EntityMatcher(db)

    try:
        if not queries:
            queries = ["Honda Beat", "Honda Vario 160", "Yamaha NMAX", "Yamaha Aerox", "Honda PCX 160", "Honda Scoopy", "Yamaha FreeGo"]

        total_scraped = 0
        total_upserted = 0
        total_scam = 0
        total_price_drops = 0

        for q in queries:
            print(f"\n-> Mengambil data terbaru untuk: {q}...")
            try:
                raw_items = scraper.scrape_live_search(keyword=q, max_items=max_items_per_query)
                if not raw_items:
                    print(f"   [Notice] Tidak ada listing ditemukan untuk '{q}'.")
                    continue

                for item in raw_items:
                    total_scraped += 1
                    var_id, score, _ = matcher.match(item["title"], item.get("claimed_year"))

                    is_dp = item.get("is_dp", False)
                    if is_dp:
                        total_scam += 1

                    existing = db.query(ScrapedListing).filter(
                        ScrapedListing.source_platform == item["source_platform"],
                        ScrapedListing.external_id == item["external_id"]
                    ).first()

                    new_price = item["price"] or 0

                    if not existing:
                        new_item = ScrapedListing(
                            source_platform=item["source_platform"],
                            external_id=item["external_id"],
                            url=item["url"],
                            title=item["title"],
                            raw_description=item.get("raw_description"),
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
                        total_upserted += 1
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

                db.commit()
            except Exception as e:
                print(f"  [Notice] Gagal scrape query '{q}': {e}")

        print(f"\n[HASIL PIPELINE] Total Scraped: {total_scraped} | Baru Masuk: {total_upserted} | Terfilter DP/Scam: {total_scam} | Price Drops: {total_price_drops}")

        print("\n-> Menghitung Ulang Fair Market Value (FMV) & Memperbarui Master Stats...")
        engine = PricingAnalyticsEngine(db)
        engine.refresh_daily_market_stats()
        print("✅ Tabel market_price_stats Motor Berhasil Dimutakhirkan!")

    finally:
        scraper.close()
        db.close()

if __name__ == "__main__":
    run_motor_sync()
