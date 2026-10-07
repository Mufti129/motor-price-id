"""
Generator & Seeder Dataset Balai Lelang Otomotif Resmi (JBA Indonesia & IBID Astra).
Membuat 5.000+ data unit lot lelang realistis yang mencakup 17 merk dan 419 varian
dengan grade inspeksi mesin/bodi, status legalitas surat, harga dasar pembukaan (Limit),
harga ketok palu final (Hammer Price), dan agregasi statistik wholesale.
"""

import sys
import os
import random
from datetime import datetime, timedelta, date

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from models.database import SessionLocal, init_db
from models.catalog import (
    MasterBrand, MasterModel, MasterVariant, AuctionLot, WholesalePriceStats, MarketPriceStats
)

JBA_POOLS = [
    ("Jakarta Barat (Meruya)", "DKI Jakarta", "B"),
    ("Jakarta Barat (Daan Mogot)", "DKI Jakarta", "B"),
    ("Tangerang", "Banten", "B"),
    ("Bandung", "Jawa Barat", "D"),
    ("Semarang", "Jawa Tengah", "H"),
    ("Surakarta (Solo)", "Jawa Tengah", "AD"),
    ("Surabaya", "Jawa Timur", "L"),
    ("Yogyakarta", "DI Yogyakarta", "AB"),
    ("Denpasar", "Bali", "DK"),
    ("Medan", "Sumatera Utara", "BK"),
    ("Palembang", "Sumatera Selatan", "BG"),
    ("Balikpapan", "Kalimantan Timur", "KT"),
    ("Makassar", "Sulawesi Selatan", "DD")
]

IBID_POOLS = [
    ("Jakarta Selatan (Ciputat)", "DKI Jakarta", "B"),
    ("Jakarta Timur (Pulogadung)", "DKI Jakarta", "B"),
    ("Bandung (Soekarno-Hatta)", "Jawa Barat", "D"),
    ("Surabaya (Warugunung)", "Jawa Timur", "L"),
    ("Semarang (Gayamsari)", "Jawa Tengah", "H"),
    ("Yogyakarta", "DI Yogyakarta", "AB"),
    ("Medan (Amplas)", "Sumatera Utara", "BK"),
    ("Pekanbaru", "Riau", "BM"),
    ("Palembang", "Sumatera Selatan", "BG"),
    ("Banjarmasin", "Kalimantan Selatan", "DA"),
    ("Denpasar", "Bali", "DK")
]

COLORS = ["Hitam", "Putih", "Merah", "Matte Black", "Abu-Abu", "Silver", "Biru", "Kuning", "Green", "Orange"]

INSPECTION_NOTES_TEMPLATES = {
    "A": [
        "Bodi mulus 95%, mesin halus standar pabrik, kelistrikan normal, kunci kontak komplit.",
        "Kondisi prima siap operasional, suara mesin halus bersih, ban tebal 85%, stang lurus.",
        "Unit terawat istimewa eks perorangan/korporasi, minim baret, suspensi empuk normal."
    ],
    "B": [
        "Baret pemakaian wajar di spakbor dan bodi samping, mesin halus kering, aki normal.",
        "Bodi lecet parkir ringan, servis rutin normal, ban 70%, lampu-lampu hidup normal.",
        "Kondisi baik pemakaian harian, knalpot standar, pengereman normal, stang stabil."
    ],
    "C": [
        "Bodi samping kanan baret dalam & mika sein retak, mesin bunyi kasar ringan, perlu tune-up.",
        "Aki lemah perlu jumper/ganti, bodi ada retak rambut, ban depan aus 50%, kampas rem tipis.",
        "Suara klep agak berisik, spion non-ori, cat bodi agak kusam, kelistrikan starter hidup."
    ],
    "D": [
        "Mesin mati total perlu overhaul turun mesin, bodi baret parah/pecah, speedometer mati.",
        "Bekas jatuh/benturan, segitiga stang agak miring, knalpot penyok, kelistrikan putus."
    ]
}

def seed_auction_database(target_total: int = 5500):
    init_db()
    db: Session = SessionLocal()
    try:
        print(f"\n1. Memeriksa data master katalog varian...")
        variants = db.query(MasterVariant, MasterModel, MasterBrand).join(
            MasterModel, MasterVariant.model_id == MasterModel.id
        ).join(
            MasterBrand, MasterModel.brand_id == MasterBrand.id
        ).all()

        if not variants:
            print("Error: Master katalog varian kosong! Jalankan seed_master_motor terlebih dahulu.")
            return

        print(f"Ditemukan {len(variants)} varian master untuk pembuatan lot lelang.")

        # Hapus data auction lama jika ada
        print("2. Membersihkan tabel auction_listings dan wholesale_price_stats lama...")
        db.query(AuctionLot).delete()
        db.query(WholesalePriceStats).delete()
        db.commit()

        # Ambil referensi harga retail median dari market_price_stats jika ada
        retail_medians = {}
        for row in db.query(MarketPriceStats).all():
            key = (row.variant_id, row.year)
            if key not in retail_medians:
                retail_medians[key] = float(row.price_median)

        print(f"3. Menghasilkan {target_total:,} data unit lot lelang JBA & IBID...")
        lots_to_insert = []
        lot_seq = 1001

        # Rentang tanggal sesi lelang
        base_date = date(2026, 10, 7)

        # Rata-rata 13-14 lot per varian
        lots_per_variant = max(12, target_total // len(variants) + 1)

        for var, model, brand in variants:
            start_y = var.release_year_start or 2016
            end_y = var.release_year_end or 2026
            if start_y > end_y:
                start_y, end_y = end_y, start_y
            msrp = float(var.official_msrp_new) if var.official_msrp_new else 25_000_000.0

            for _ in range(lots_per_variant):
                claimed_year = random.randint(start_y, end_y)
                age_years = max(0, 2026 - claimed_year)

                # Tentukan platform lelang (JBA ~58%, IBID ~42%)
                is_jba = random.random() < 0.58
                platform = "jba_indonesia" if is_jba else "ibid_astra"
                pool_info = random.choice(JBA_POOLS if is_jba else IBID_POOLS)
                pool_city = pool_info[0]
                plate_code = pool_info[2]

                delta_days = random.randint(-25, 8)
                session_date = base_date + timedelta(days=delta_days)

                lot_prefix = "JBA-M" if is_jba else "IBID-M"
                lot_number = f"{lot_prefix}-{lot_seq}"
                lot_seq += 1

                lane = f"Lane {random.choice(['A', 'B', 'C'])}"
                color = random.choice(COLORS)
                plate_num = f"{plate_code} {random.randint(1000, 6999)} {random.choice(['AA', 'BK', 'CD', 'EZ', 'KL', 'XY', 'MR', 'TX'])}"

                km = int(random.gauss(age_years * 8500 + 4000, 3000))
                km = max(1200, min(140000, km))

                # Grade distribusi
                r_grade = random.random()
                if r_grade < 0.35:
                    grade_eng = "A"
                    grade_body = "A" if random.random() < 0.70 else "B"
                    acv_score = f"{random.uniform(88.0, 96.5):.1f}"
                    eng_cond = "Hidup Halus Normal"
                elif r_grade < 0.83:
                    grade_eng = "B"
                    grade_body = "B" if random.random() < 0.80 else "C"
                    acv_score = f"{random.uniform(75.0, 87.5):.1f}"
                    eng_cond = "Hidup Standar Normal"
                elif r_grade < 0.97:
                    grade_eng = "C"
                    grade_body = "C" if random.random() < 0.75 else "B"
                    acv_score = f"{random.uniform(62.0, 74.5):.1f}"
                    eng_cond = "Kasar Ringan Perlu Servis"
                else:
                    grade_eng = "D"
                    grade_body = "D"
                    acv_score = f"{random.uniform(40.0, 60.0):.1f}"
                    eng_cond = "Mati Total / Turun Mesin"

                notes = random.choice(INSPECTION_NOTES_TEMPLATES[grade_eng])

                stnk_status = "Ada" if random.random() < 0.92 else "Tidak Ada"
                tax_status = "Hidup" if random.random() < 0.82 else "Mati"
                bpkb_status = "Ready (Asli)" if random.random() < 0.90 else "Proses 30 Hari Kerja"
                faktur_status = True if random.random() < 0.88 else False

                retail_base = retail_medians.get((var.id, claimed_year))
                if not retail_base:
                    deprec_factor = (1.0 - 0.10) ** age_years
                    retail_base = msrp * deprec_factor

                grade_discount = {"A": 0.73, "B": 0.68, "C": 0.58, "D": 0.40}[grade_eng]
                base_limit = round((retail_base * grade_discount * random.uniform(0.95, 1.05)) / 100_000) * 100_000
                base_limit = max(2_000_000.0, base_limit)

                sold_prob = {"A": 0.95, "B": 0.90, "C": 0.78, "D": 0.50}[grade_eng]
                is_sold = random.random() < sold_prob

                if is_sold:
                    auction_status = "Sold"
                    bid_count = random.randint(3, 14) if grade_eng in ["A", "B"] else random.randint(1, 5)
                    bid_markup = random.uniform(1.08, 1.25) if grade_eng in ["A", "B"] else random.uniform(1.02, 1.10)
                    hammer_price = round((base_limit * bid_markup) / 100_000) * 100_000
                    hammer_price = min(retail_base * 0.92, hammer_price)
                else:
                    auction_status = "No Bid" if random.random() < 0.85 else "Withdrawn"
                    bid_count = 0
                    hammer_price = None

                admin_fee = 500_000.0 if msrp < 80_000_000 else 1_000_000.0

                lot = AuctionLot(
                    source_platform=platform,
                    lot_number=lot_number,
                    session_id=f"{platform.upper()}-{session_date.strftime('%Y%m%d')}",
                    auction_date=session_date,
                    pool_city=pool_city,
                    lane=lane,
                    matched_variant_id=var.id,
                    claimed_year=claimed_year,
                    color=color,
                    license_plate=plate_num,
                    plate_region=plate_code,
                    odometer_km=km,
                    grade_engine=grade_eng,
                    grade_frame_body=grade_body,
                    overall_score=f"Grade {grade_eng} (ACV {acv_score})" if not is_jba else f"Grade {grade_eng}",
                    engine_condition=eng_cond,
                    inspection_notes=notes,
                    stnk_status=stnk_status,
                    tax_status=tax_status,
                    bpkb_status=bpkb_status,
                    faktur_status=faktur_status,
                    base_limit_price=base_limit,
                    hammer_price=hammer_price,
                    admin_fee=admin_fee,
                    auction_status=auction_status,
                    bid_count=bid_count,
                    url=f"https://www.{platform.replace('_', '.')}.co.id/lot-detail/{lot_number.lower()}"
                )
                lots_to_insert.append(lot)

                if len(lots_to_insert) >= 1000:
                    db.bulk_save_objects(lots_to_insert)
                    db.commit()
                    print(f"  -> Disimpan {len(lots_to_insert)} unit lot...")
                    lots_to_insert = []

        if lots_to_insert:
            db.bulk_save_objects(lots_to_insert)
            db.commit()

        total_lots = db.query(AuctionLot).count()
        print(f"\n[SUKSES] Total {total_lots:,} Unit Lot Lelang Berhasil Dibuat!")

        # 4. Agregasi wholesale_price_stats
        print("4. Menghitung statistik wholesale_price_stats...")
        from sqlalchemy import func, case
        stats_query = db.query(
            AuctionLot.matched_variant_id,
            AuctionLot.claimed_year,
            AuctionLot.pool_city,
            func.count(AuctionLot.id).label("total_cnt"),
            func.avg(AuctionLot.base_limit_price).label("avg_base"),
            func.min(AuctionLot.base_limit_price).label("min_base"),
            func.avg(AuctionLot.hammer_price).label("avg_hammer"),
            func.max(AuctionLot.hammer_price).label("max_hammer"),
            func.sum(case((AuctionLot.auction_status == 'Sold', 1), else_=0)).label("sold_cnt")
        ).group_by(
            AuctionLot.matched_variant_id,
            AuctionLot.claimed_year,
            AuctionLot.pool_city
        ).all()

        wholesale_records = []
        for r in stats_query:
            if not r.matched_variant_id or not r.claimed_year:
                continue
            total_cnt = r.total_cnt or 0
            sold_cnt = r.sold_cnt or 0
            clearance_pct = (sold_cnt / total_cnt * 100.0) if total_cnt > 0 else 0.0

            w_stat = WholesalePriceStats(
                stat_date=base_date,
                variant_id=r.matched_variant_id,
                year=r.claimed_year,
                pool_city=r.pool_city,
                sample_count=total_cnt,
                avg_base_price=float(r.avg_base or 0),
                median_hammer_price=float(r.avg_hammer or r.avg_base or 0),
                min_base_price=float(r.min_base or 0),
                max_hammer_price=float(r.max_hammer or r.avg_base or 0),
                clearance_rate_pct=float(clearance_pct)
            )
            wholesale_records.append(w_stat)

            if len(wholesale_records) >= 1000:
                db.bulk_save_objects(wholesale_records)
                db.commit()
                wholesale_records = []

        if wholesale_records:
            db.bulk_save_objects(wholesale_records)
            db.commit()

        total_stats = db.query(WholesalePriceStats).count()
        print(f"[SUKSES] Total {total_stats:,} Agregasi Wholesale Stats Berhasil Dihitung!")

    finally:
        db.close()

if __name__ == "__main__":
    seed_auction_database()
