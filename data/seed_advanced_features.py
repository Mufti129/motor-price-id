"""
Seeder & Initializer untuk Modul Skema Lanjutan:
1. Listing Price History (Price Drops)
2. Vehicle History & ETLE Reports
3. Listing Image Analysis (Computer Vision)
4. B2B Corporate API Clients & Usage Logs
5. User Deal Alerts (Arbitrage Bargain Engine)
"""

import os
import sys
import random
import secrets
from datetime import datetime, timedelta

# Tambahkan direktori root ke sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import SessionLocal, init_db
from models.catalog import (
    ScrapedListing, MasterVariant, MasterModel, MasterBrand,
    ListingPriceHistory, VehicleHistoryReport, ListingImageAnalysis,
    B2BApiClient, ApiUsageLog, UserDealAlert
)

def seed_advanced_data():
    init_db()
    db = SessionLocal()
    try:
        print("[1/5] Inisialisasi Listing Price History...")
        # Ambil sampel 100 listing retail untuk diberi histori penurunan harga
        listings = db.query(ScrapedListing).limit(150).all()
        history_count = db.query(ListingPriceHistory).count()
        if history_count == 0 and listings:
            hist_objs = []
            for item in listings:
                if random.random() < 0.35: # 35% listing mengalami penurunan harga (Price Drop)
                    current_price = float(item.price)
                    drop_pct = round(random.uniform(3.0, 12.5), 2)
                    original_price = round(current_price / (1 - (drop_pct / 100)), -4)
                    
                    hist_objs.append(ListingPriceHistory(
                        listing_id=item.id,
                        old_price=original_price,
                        new_price=current_price,
                        price_drop_pct=drop_pct,
                        recorded_at=datetime.utcnow() - timedelta(days=random.randint(1, 14))
                    ))
            db.bulk_save_objects(hist_objs)
            db.commit()
            print(f"  -> Berhasil membuat {len(hist_objs)} rekam jejak price drop.")

        print("[2/5] Inisialisasi Vehicle History & ETLE Reports...")
        veh_count = db.query(VehicleHistoryReport).count()
        if veh_count == 0:
            sample_plates = [
                ("B 3481 UJG", "Honda", "Beat", 2024, 8500, False, False, "Clear / Bebas Tilang", "Pajak Aktif s.d 06-2026"),
                ("B 6812 PQR", "Honda", "Vario", 2023, 14200, False, False, "Clear / Bebas Tilang", "Pajak Aktif s.d 11-2025"),
                ("D 2189 AB", "Yamaha", "NMAX", 2022, 22500, False, False, "Clear / Bebas Tilang", "Pajak Aktif s.d 03-2026"),
                ("D 4501 ZK", "Yamaha", "Aerox", 2021, 31000, False, False, "Ada Tilang Aktif (Kamera Simpang Dago)", "Pajak Tertunda 1 Bulan"),
                ("L 4590 CD", "Honda", "PCX", 2023, 11800, False, False, "Clear / Bebas Tilang", "Pajak Aktif s.d 08-2026"),
                ("AB 1928 EF", "Kawasaki", "Ninja 250", 2020, 18200, False, False, "Clear / Bebas Tilang", "Pajak Aktif s.d 10-2025"),
                ("B 1102 GHT", "Honda", "Scoopy", 2024, 4300, False, False, "Clear / Bebas Tilang", "Pajak Aktif s.d 01-2027"),
                ("F 5521 BC", "Vespa", "Sprint 150", 2022, 9400, False, False, "Clear / Bebas Tilang", "Pajak Aktif s.d 05-2026"),
                ("DK 7741 AA", "Yamaha", "XMAX", 2023, 7600, False, False, "Clear / Bebas Tilang", "Pajak Aktif s.d 09-2026"),
                ("BK 3109 OP", "Suzuki", "Satria F150", 2019, 41000, False, True, "Clear / Bebas Tilang", "Pernah Klaim Minor Spakbor")
            ]
            veh_objs = []
            for plate, brand, model, yr, odo, flood, acc, etle, notes in sample_plates:
                veh_objs.append(VehicleHistoryReport(
                    license_plate=plate,
                    vin_chassis_hash=secrets.token_hex(16).upper(),
                    brand_name=brand,
                    model_name=model,
                    production_year=yr,
                    verified_odometer=odo,
                    last_service_date=(datetime.utcnow() - timedelta(days=random.randint(15, 90))).date(),
                    flood_history_flag=flood,
                    accident_history_flag=acc,
                    etle_ticket_status=etle,
                    stnk_tax_valid_until=(datetime.utcnow() + timedelta(days=random.randint(120, 500))).date(),
                    notes=notes
                ))
            db.bulk_save_objects(veh_objs)
            db.commit()
            print(f"  -> Berhasil menyimpan {len(veh_objs)} laporan rekam jejak fisik kendaraan.")

        print("[3/5] Inisialisasi Listing Image Analysis (Computer Vision)...")
        img_count = db.query(ListingImageAnalysis).count()
        if img_count == 0 and listings:
            img_objs = []
            for item in listings[:80]:
                img_objs.append(ListingImageAnalysis(
                    listing_id=item.id,
                    image_url=item.url,
                    scratch_damage_score=round(random.uniform(0.0, 15.0), 1),
                    paint_originality_score=round(random.uniform(90.0, 99.5), 1),
                    non_standard_exhaust_flag=random.random() < 0.12, # 12% kemungkinan knalpot racing
                    image_authenticity_score=round(random.uniform(94.0, 99.8), 1),
                    detected_color=random.choice(["Hitam", "Putih", "Merah", "Matte Grey", "Biru Tua"])
                ))
            db.bulk_save_objects(img_objs)
            db.commit()
            print(f"  -> Berhasil menyimpan {len(img_objs)} hasil analisis Computer Vision foto.")

        print("[4/5] Inisialisasi B2B Corporate API Clients & Telemetry Logs...")
        client_count = db.query(B2BApiClient).count()
        if client_count == 0:
            clients_data = [
                ("Adira Dinamika Multi Finance Tbk", "b2b-valuation@adira.co.id", "Enterprise", 1200),
                ("BFI Finance Indonesia Tbk", "auto-risk@bfi.co.id", "Enterprise", 1200),
                ("Moladin Digital Indonesia", "api-integration@moladin.com", "Professional", 600),
                ("PT Balai Lelang Asta Nara Jaya (AUKSI)", "tech@auksi.co.id", "Professional", 600),
                ("Mitra Diler Motor Bekas Nusantara", "partner@dealermotor.id", "Starter", 180)
            ]
            for comp, email, tier, rlimit in clients_data:
                client_obj = B2BApiClient(
                    company_name=comp,
                    contact_email=email,
                    api_key=f"mpid_live_{secrets.token_hex(16)}",
                    tier=tier,
                    rate_limit_per_minute=rlimit,
                    is_active=True
                )
                db.add(client_obj)
                db.flush()

                endpoints = [
                    "/api/v1/valuation/calculate",
                    "/api/v1/wholesale/corridor/1/2023",
                    "/api/v1/arbitrage/deals",
                    "/api/v1/catalog/models"
                ]
                for _ in range(25):
                    log = ApiUsageLog(
                        client_id=client_obj.id,
                        endpoint=random.choice(endpoints),
                        status_code=200 if random.random() > 0.02 else 400,
                        response_time_ms=round(random.uniform(8.5, 35.0), 2),
                        requested_at=datetime.utcnow() - timedelta(minutes=random.randint(5, 720))
                    )
                    db.add(log)
            db.commit()
            print("  -> Berhasil mendaftarkan 5 mitra korporat B2B dan riwayat audit request.")

        print("[5/5] Inisialisasi User Deal Alerts (Arbitrage Bargains)...")
        alert_count = db.query(UserDealAlert).count()
        if alert_count == 0:
            variants = db.query(MasterVariant).limit(5).all()
            if variants:
                alerts_data = [
                    ("investor.otomotif@gmail.com", variants[0].id, 2023, "Jakarta", 15500000.0, 15.0),
                    ("+6281299887711", variants[1].id if len(variants) > 1 else variants[0].id, 2022, "Bandung", 23000000.0, 18.0),
                    ("dealersurabaya@outlook.com", variants[2].id if len(variants) > 2 else variants[0].id, 2024, "Surabaya", 17000000.0, 12.0)
                ]
                for contact, var_id, yr, city, max_p, min_disc in alerts_data:
                    alert = UserDealAlert(
                        user_contact=contact,
                        variant_id=var_id,
                        target_year=yr,
                        target_city=city,
                        max_price=max_p,
                        min_discount_pct=min_disc,
                        is_active=True,
                        last_triggered_at=datetime.utcnow() - timedelta(hours=random.randint(2, 48))
                    )
                    db.add(alert)
                db.commit()
                print("  -> Berhasil menyimpan langganan deal alert aktif.")

        print("Pembaruan seluruh skema lanjutan sukses 100%.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding advanced data: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_advanced_data()
