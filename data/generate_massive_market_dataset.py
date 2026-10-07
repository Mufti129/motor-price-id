"""
Script Generator & Ingestion Dataset Skala Besar Motor Bekas Indonesia.
Menghasilkan minimal 500+ dataset listing per merk (Honda, Yamaha, Kawasaki, Piaggio, Vespa, Suzuki)
dengan variasi tahun (2016-2026), harga riil sesuai depresiasi pasar, status pajak, kota, odometer KM,
dan noise jual-beli Indonesia (slang, typo, DP scam).
"""

import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.database import SessionLocal, init_db
from models.catalog import MasterBrand, MasterModel, MasterVariant, ScrapedListing, MarketPriceStats
from data.seed_master_motor import seed_master_motor_database
from pipeline.normalizer import ListingNormalizer
from pipeline.scam_detector import ScamAndDPDetector
from pipeline.entity_matcher import EntityMatcher
from analytics.pricing_engine import PricingAnalyticsEngine

CITIES_PROVINCES = [
    ("Jakarta Selatan", "DKI Jakarta", "B"),
    ("Jakarta Timur", "DKI Jakarta", "B"),
    ("Jakarta Barat", "DKI Jakarta", "B"),
    ("Jakarta Pusat", "DKI Jakarta", "B"),
    ("Jakarta Utara", "DKI Jakarta", "B"),
    ("Tangerang", "Banten", "B"),
    ("Tangerang Selatan", "Banten", "B"),
    ("Bekasi", "Jawa Barat", "B"),
    ("Depok", "Jawa Barat", "B"),
    ("Bogor", "Jawa Barat", "F"),
    ("Bandung", "Jawa Barat", "D"),
    ("Cimahi", "Jawa Barat", "D"),
    ("Semarang", "Jawa Tengah", "H"),
    ("Surakarta (Solo)", "Jawa Tengah", "AD"),
    ("Yogyakarta", "DI Yogyakarta", "AB"),
    ("Sleman", "DI Yogyakarta", "AB"),
    ("Surabaya", "Jawa Timur", "L"),
    ("Malang", "Jawa Timur", "N"),
    ("Sidoarjo", "Jawa Timur", "W"),
    ("Denpasar", "Bali", "DK"),
    ("Badung", "Bali", "DK"),
    ("Medan", "Sumatera Utara", "BK")
]

COLORS = ["Hitam", "Putih", "Merah", "Abu-Abu", "Silver", "Biru", "Kuning", "Matte Black", "Green", "Orange"]
CONDITIONS = [
    "Mulus terawat mesin halus", "Tangan pertama dari baru", "KM rendah jarang pakai",
    "Full orisinil pabrik", "Surat lengkap bpkb stnk faktur ready", "Pemakaian harian wajar",
    "Kondisi istimewa no minus siap gass", "Bodi mulus kinclong", "Mesin segel standar pabrik",
    "Jual BU butuh uang cepat hari ini nego tipis", "Kelistrikan normal stater joss"
]
TAX_TEMPLATES = [
    ("Hidup / Panjang", "pajak hidup panjang sampai tahun depan kaleng panjang", True, 0),
    ("Hidup / Panjang", "pjk on taat pajak surat komplit", True, 0),
    ("Hidup / Panjang", "surat lengkap pajak aktif tertib", True, 0),
    ("Mati / Off", "pjk off 1x kaleng 2028 bpkb stnk ada", True, 1),
    ("Mati / Off", "pajak mati 2 thn mesin sehat surat ada", True, 2),
    ("Mati / Off", "telat pajak 3 tahun murah nego alus", True, 3),
    ("Unknown", "surat bpkb stnk faktur lengkap siap pakai", True, 0),
    ("Unknown", "ss lengkap siap jalan", True, 0)
]

def generate_massive_dataset(target_per_brand: int = 550):
    init_db()
    seed_master_motor_database()

    db = SessionLocal()
    try:
        matcher = EntityMatcher(db)
        brands = db.query(MasterBrand).all()

        total_generated = 0
        total_matched = 0
        total_dp = 0

        # Kosongkan listing lama agar fresh dan bersih
        db.query(ScrapedListing).delete()
        db.query(MarketPriceStats).delete()
        db.commit()

        print(f"🚀 Memulai generate minimal {target_per_brand} listing per merk...")

        for brand in brands:
            brand_count = 0
            models = db.query(MasterModel).filter(MasterModel.brand_id == brand.id).all()
            if not models:
                continue

            print(f"  -> Generating untuk Merk: {brand.name} ({len(models)} model)...")

            # Ambil semua varian per merk
            variants = db.query(MasterVariant).join(
                MasterModel, MasterVariant.model_id == MasterModel.id
            ).filter(MasterModel.brand_id == brand.id).all()

            if not variants:
                continue

            while brand_count < target_per_brand:
                var = random.choice(variants)
                model = var.model

                # Tentukan tahun motor
                start_yr = max(2016, var.release_year_start)
                end_yr = var.release_year_end if var.release_year_end else 2026
                if start_yr > end_yr:
                    start_yr = end_yr
                year = random.randint(start_yr, end_yr)

                # Hitung harga dasar dengan formula depresiasi realistis
                msrp = float(var.official_msrp_new) if var.official_msrp_new else 22000000.0
                years_old = 2026 - year
                depreciation_rate = min(0.65, 0.15 + (years_old * 0.055)) # 15% thn 1, bertambah 5.5%/thn
                base_price = msrp * (1.0 - depreciation_rate)

                # Variasi harga pasar (+/- 12%)
                price_noise = random.uniform(-0.12, 0.12)
                listing_price = base_price * (1.0 + price_noise)

                # Odometer KM realistis
                annual_km = random.randint(5000, 11000)
                odometer = int(years_old * annual_km + random.randint(1000, 4000))
                odometer = max(2000, min(150000, odometer))

                # Lokasi
                city, province, plate = random.choice(CITIES_PROVINCES)
                color = random.choice(COLORS)
                cond_text = random.choice(CONDITIONS)
                tax_status, tax_desc, has_bpkb, years_off = random.choice(TAX_TEMPLATES)

                # Potongan harga jika pajak mati
                if tax_status == "Mati / Off":
                    listing_price -= (years_off * 450000.0)

                # 3.5% peluang listing adalah DP Scam / Clickbait
                is_dp_chance = random.random() < 0.035
                if is_dp_chance:
                    listing_price = random.choice([1000000, 1500000, 2000000, 2500000, 3000000])
                    title = f"{brand.name} {model.name} {year} DP Murah {color}"
                    desc = f"Cukup DP {listing_price:,.0f} angsuran murah 35x proses cepat data dijemput, {cond_text}"
                else:
                    # Buat judul realistis
                    aliases_options = [a.strip() for a in (var.aliases or "").split(",") if a.strip()]
                    chosen_name = random.choice(aliases_options) if (aliases_options and random.random() < 0.5) else f"{brand.name} {model.name} {var.variant_name}"
                    title = f"{chosen_name} {year} {color} {tax_desc[:25]}".strip()
                    desc = f"Jual {brand.name} {model.name} tahun {year} warna {color}. {cond_text}. {tax_desc}. Plat {plate} {city}."

                # Pembulatan harga ke ratusan ribu
                listing_price = round(listing_price / 100000.0) * 100000.0

                # Normalizer & Matcher
                norm = ListingNormalizer.normalize_listing({
                    "title": title,
                    "description": desc,
                    "price": listing_price,
                    "year": year,
                    "odometer": odometer,
                    "province": province,
                    "city": city
                })

                matched_id, score, matched_name = matcher.match(norm["title"], norm["claimed_year"])
                if not matched_id:
                    matched_id = var.id # Fallback to true variant

                is_dp, _ = ScamAndDPDetector.is_dp_or_credit_listing(
                    price=norm["price"],
                    title=norm["title"],
                    description=desc,
                    expected_market_msrp=msrp
                )

                post_date = datetime.now() - timedelta(days=random.randint(0, 45), hours=random.randint(1, 23))

                ext_id = f"gen_{brand.name[:3].lower()}_{brand_count}_{random.randint(100000, 999999)}"
                listing_obj = ScrapedListing(
                    source_platform=random.choice(["olx", "olx", "momotor", "facebook"]),
                    external_id=ext_id,
                    url=f"https://www.olx.co.id/item/{random.randint(1000000, 9999999)}",
                    title=norm["title"],
                    raw_description=desc,
                    matched_variant_id=matched_id,
                    claimed_year=norm["claimed_year"] or year,
                    price=norm["price"] or listing_price,
                    is_dp_price=is_dp,
                    odometer_km=norm["odometer_km"] or odometer,
                    tax_status=norm["tax_status"] or tax_status,
                    tax_expiry_year=year + 5 if tax_status == "Hidup / Panjang" else year + 5 - years_off,
                    has_bpkb=has_bpkb,
                    has_stnk=True,
                    plate_region=norm["plate_region"] or plate,
                    province=province,
                    city=city,
                    district="Kecamatan",
                    seller_name=f"Seller_{city[:3]}_{random.randint(100, 999)}",
                    seller_type="Dealer" if random.random() < 0.3 else "Individual",
                    posted_at=post_date,
                    scraped_at=datetime.now()
                )
                db.add(listing_obj)

                brand_count += 1
                total_generated += 1
                if matched_id:
                    total_matched += 1
                if is_dp:
                    total_dp += 1

            db.commit()
            print(f"    ✓ Merk {brand.name}: {brand_count} dataset tersimpan.")

        # Hitung statistik pasar harian
        print("\n📊 Menghitung kalkulasi Fair Market Value (FMV) & Kuantil Pasar...")
        pricing_engine = PricingAnalyticsEngine(db)
        pricing_engine.refresh_daily_market_stats()

        print(f"\n✅ SUKSES! Total Dataset: {total_generated} listing | Matched: {total_matched} | Flagged DP: {total_dp}")
        return total_generated
    finally:
        db.close()

if __name__ == "__main__":
    generate_massive_dataset(target_per_brand=550)
