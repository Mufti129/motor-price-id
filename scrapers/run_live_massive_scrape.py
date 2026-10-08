"""
Skrip Eksekusi Live Scraping Massal Otomatis (High-Throughput Multi-Model Crawler).
Mengeksekusi crawling pada 35+ model motor paling populer di Indonesia (Honda, Yamaha, Kawasaki, Vespa, Suzuki)
secara live menggunakan Playwright stealth engine dan menyimpannya langsung ke database SQLite.
"""

import os
import sys
import time
import random
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.database import SessionLocal, init_db
from models.catalog import ScrapedListing, MasterVariant
from pipeline.normalizer import ListingNormalizer
from pipeline.entity_matcher import EntityMatcher
from pipeline.scam_detector import ScamAndDPDetector
from scrapers.stealth_scraper import StealthMarketplaceScraper

TARGET_QUERIES = [
    # Honda Top Models
    'Honda Beat', 'Honda Vario 125', 'Honda Vario 150', 'Honda Vario 160',
    'Honda Scoopy', 'Honda PCX 150', 'Honda PCX 160', 'Honda ADV 150', 'Honda ADV 160',
    'Honda Genio', 'Honda Stylo 160', 'Honda CB150R', 'Honda CBR 150R', 'Honda CRF 150L',
    # Yamaha Top Models
    'Yamaha NMAX 155', 'Yamaha Aerox 155', 'Yamaha Fazzio', 'Yamaha Grand Filano',
    'Yamaha Mio', 'Yamaha XMAX 250', 'Yamaha XSR 155', 'Yamaha R15', 'Yamaha Vixion', 'Yamaha Lexi',
    # Kawasaki Top Models
    'Kawasaki Ninja 250', 'Kawasaki KLX 150', 'Kawasaki W175', 'Kawasaki ZX25R',
    # Vespa & Piaggio Top Models
    'Vespa Sprint 150', 'Vespa Primavera 150', 'Vespa GTS 150', 'Vespa LX 125', 'Vespa S 125',
    # Suzuki Top Models
    'Suzuki Satria F150', 'Suzuki GSX R150', 'Suzuki Address'
]

def run_massive_live_scraping():
    start_time = time.time()
    db = SessionLocal()
    matcher = EntityMatcher(db)
    scraper = StealthMarketplaceScraper(headless=True, timeout_ms=30000)

    print(f'[{datetime.now().strftime("%H:%M:%S")}] Memulai Live Scraping Massal untuk {len(TARGET_QUERIES)} target model...')
    
    total_found = 0
    total_added = 0
    total_matched = 0
    total_dp_flagged = 0

    for idx, query in enumerate(TARGET_QUERIES, 1):
        q_start = time.time()
        print(f"[{idx}/{len(TARGET_QUERIES)}] Crawling: '{query}'...", end=" ", flush=True)
        
        try:
            items = scraper.scrape_momotor_live(keyword=query, max_items=20)
            q_found = len(items)
            q_added = 0
            
            for raw in items:
                norm = ListingNormalizer.normalize_listing(raw)
                var_id, score, matched_name = matcher.match(norm['title'], norm['claimed_year'])
                if var_id:
                    total_matched += 1

                is_dp, reason = ScamAndDPDetector.is_dp_or_credit_listing(
                    price=norm['price'],
                    title=norm['title'],
                    description=norm['raw_description']
                )
                if is_dp:
                    total_dp_flagged += 1

                existing = db.query(ScrapedListing).filter(
                    ScrapedListing.source_platform == norm['source_platform'],
                    ScrapedListing.external_id == norm['external_id']
                ).first()

                if not existing:
                    listing_obj = ScrapedListing(
                        source_platform=norm['source_platform'],
                        external_id=norm['external_id'],
                        url=norm['url'],
                        title=norm['title'],
                        raw_description=norm['raw_description'],
                        matched_variant_id=var_id,
                        claimed_year=norm['claimed_year'],
                        price=norm['price'] or 0,
                        is_dp_price=is_dp,
                        odometer_km=norm['odometer_km'],
                        tax_status=norm['tax_status'],
                        tax_expiry_year=norm['tax_expiry_year'],
                        has_bpkb=norm['has_bpkb'],
                        has_stnk=norm['has_stnk'],
                        plate_region=norm['plate_region'],
                        province=norm['province'],
                        city=norm['city'],
                        district=norm.get('district', ''),
                        seller_name=norm.get('seller_name', 'Dealer Verified'),
                        seller_type=norm['seller_type'],
                        posted_at=datetime.utcnow()
                    )
                    db.add(listing_obj)
                    q_added += 1
                    total_added += 1
            
            db.commit()
            total_found += q_found
            q_elapsed = time.time() - q_start
            print(f'OK ({q_found} ditemukan, {q_added} baru) [{q_elapsed:.1f}s]')
            
        except Exception as e:
            print(f'Error ({e})')
            db.rollback()

        time.sleep(random.uniform(1.2, 2.0))

    db.close()
    elapsed_total = time.time() - start_time
    print('-' * 60)
    print(f'[{datetime.now().strftime("%H:%M:%S")}] Selesai dalam {elapsed_total/60:.2f} menit ({elapsed_total:.1f} detik)!')
    print(f'Total Ditemukan: {total_found} | Baru Tersimpan di DB: {total_added} | AI Matched: {total_matched} | DP Flagged: {total_dp_flagged}')

if __name__ == '__main__':
    run_massive_live_scraping()
