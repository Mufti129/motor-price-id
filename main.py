import sys
import argparse
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from models.database import SessionLocal, init_db
from models.catalog import MasterBrand, MasterModel, MasterVariant, ScrapedListing, MarketPriceStats
from data.seed_master_motor import seed_master_motor_database
from scrapers.olx_scraper import OLXMotorScraper
from pipeline.normalizer import ListingNormalizer
from pipeline.scam_detector import ScamAndDPDetector
from pipeline.entity_matcher import EntityMatcher
from analytics.pricing_engine import PricingAnalyticsEngine

console = Console()

def run_seeder():
    console.print("\n[bold cyan]1. Inisialisasi Database & Seeding Master Data Katalog Motor Indonesia...[/bold cyan]")
    seed_master_motor_database()
    console.print("[bold green]✓ Master Database Motor Berhasil Dikonfigurasi![/bold green]\n")

def run_scraping_and_pipeline(queries=None, location="dki_jakarta", pages=2):
    """Menjalankan scraping OLX lalu memprosesnya lewat AI/NLP Pipeline ke Database."""
    db = SessionLocal()
    try:
        matcher = EntityMatcher(db)
        scraper = OLXMotorScraper()

        if not queries:
            queries = ["Vario 150", "NMAX", "Beat", "Aerox", "PCX", "Scoopy"]

        console.print(Panel.fit(
            f"[bold yellow]Memulai Scraping & AI Normalization Engine[/bold yellow]\n"
            f"• Target Platform : [bold]OLX Indonesia[/bold]\n"
            f"• Lokasi          : [bold]{location}[/bold]\n"
            f"• Query Target    : [bold]{', '.join(queries)}[/bold]\n"
            f"• Halaman/Query   : [bold]{pages}[/bold]",
            title="Motor Price Monitor"
        ))

        total_scraped = 0
        total_matched = 0
        total_dp_flagged = 0

        for query in queries:
            console.print(f"\n[cyan]🔍 Scraping query: '{query}' (Lokasi: {location})...[/cyan]")
            for page in range(pages):
                raw_items = scraper.search_listings(query=query, location_code=location, page=page, page_size=20)
                if not raw_items:
                    continue

                for raw in raw_items:
                    total_scraped += 1
                    
                    # 1. Normalisasi Atribut
                    norm = ListingNormalizer.normalize_listing(raw)

                    # 2. Entity Disambiguation (Fuzzy Match ke Master DB)
                    var_id, score, matched_name = matcher.match(norm["title"], norm["claimed_year"])
                    if var_id:
                        total_matched += 1

                    # 3. DP / Scam Detector
                    is_dp, reason = ScamAndDPDetector.is_dp_or_credit_listing(
                        price=norm["price"],
                        title=norm["title"],
                        description=norm["raw_description"]
                    )
                    if is_dp:
                        total_dp_flagged += 1

                    # 4. Upsert ke Database
                    existing = db.query(ScrapedListing).filter(
                        ScrapedListing.source_platform == norm["source_platform"],
                        ScrapedListing.external_id == norm["external_id"]
                    ).first()

                    if not existing:
                        listing_obj = ScrapedListing(
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
                            tax_expiry_year=norm["tax_expiry_year"],
                            has_bpkb=norm["has_bpkb"],
                            has_stnk=norm["has_stnk"],
                            plate_region=norm["plate_region"],
                            province=norm["province"],
                            city=norm["city"],
                            district=norm["district"],
                            seller_name=norm["seller_name"],
                            seller_type=norm["seller_type"],
                            posted_at=datetime.utcnow()
                        )
                        db.add(listing_obj)
                    else:
                        existing.price = norm["price"] or existing.price
                        existing.is_dp_price = is_dp
                        existing.matched_variant_id = var_id or existing.matched_variant_id

                db.commit()

        console.print(f"\n[bold green]✓ Selesai![/bold green] Total Scraped: {total_scraped} | Berhasil Dimatch ke Master ID: {total_matched} | Terdeteksi DP/Clickbait: {total_dp_flagged}")

    finally:
        db.close()

def display_market_price_report():
    """Menampilkan tabel Fair Market Value (FMV) dan harga pasaran per model/tahun."""
    db = SessionLocal()
    try:
        engine = PricingAnalyticsEngine(db)
        engine.refresh_daily_market_stats()

        variants = db.query(MasterVariant, MasterModel, MasterBrand).join(
            MasterModel, MasterVariant.model_id == MasterModel.id
        ).join(
            MasterBrand, MasterModel.brand_id == MasterBrand.id
        ).all()

        table = Table(title="📊 MONITORING HARGA PASARAN MOTOR BEKAS (FAIR MARKET VALUE)", show_lines=True)
        table.add_column("Merk & Model", style="bold cyan")
        table.add_column("Varian", style="white")
        table.add_column("Tahun", justify="center", style="yellow")
        table.add_column("Sample", justify="center", style="magenta")
        table.add_column("P25 (Bargain/BU)", justify="right", style="green")
        table.add_column("Median (FMV)", justify="right", style="bold green")
        table.add_column("P75 (Istimewa/Low KM)", justify="right", style="blue")
        table.add_column("Harga Baru (MSRP)", justify="right", style="dim")

        has_data = False
        for var, model, brand in variants:
            # Ambil seluruh tahun yang ada datanya
            years = db.query(ScrapedListing.claimed_year).filter(
                ScrapedListing.matched_variant_id == var.id,
                ScrapedListing.claimed_year.isnot(None),
                ScrapedListing.is_dp_price == False
            ).distinct().all()

            for (y,) in sorted(years, key=lambda x: x[0] if x[0] else 0, reverse=True):
                if not y:
                    continue
                stats = engine.calculate_variant_pricing_stats(var.id, year=y)
                if stats and stats["sample_count"] >= 1:
                    has_data = True
                    msrp_str = f"Rp {float(var.official_msrp_new):,.0f}" if var.official_msrp_new else "-"
                    table.add_row(
                        f"{brand.name} {model.name}",
                        var.variant_name,
                        str(y),
                        str(stats["sample_count"]),
                        f"Rp {stats['price_p25']:,.0f}",
                        f"Rp {stats['price_median']:,.0f}",
                        f"Rp {stats['price_p75']:,.0f}",
                        msrp_str
                    )

        if has_data:
            console.print(table)
        else:
            console.print("[yellow]Belum ada cukup data listing motor yang cocok. Jalankan scraping terlebih dahulu.[/yellow]")

        # Tampilkan Hot Deals
        hot_deals = engine.find_hot_deals(discount_threshold_pct=10.0)
        if hot_deals:
            deals_table = Table(title="🔥 HOT DEALS / POTENSI ARBITRASE (DI BAWAH HARGA PASAR)", show_lines=True)
            deals_table.add_column("Motor", style="bold cyan")
            deals_table.add_column("Tahun", justify="center", style="yellow")
            deals_table.add_column("Harga Listing", justify="right", style="bold green")
            deals_table.add_column("Harga Pasar (Median)", justify="right", style="dim")
            deals_table.add_column("Hemat / Diskon", justify="right", style="bold red")
            deals_table.add_column("Pajak / Lokasi", style="white")
            deals_table.add_column("Link Listing", style="blue")

            for d in hot_deals[:10]:
                deals_table.add_row(
                    d["motor_name"],
                    str(d["year"]),
                    f"Rp {d['price']:,.0f}",
                    f"Rp {d['fair_market_value']:,.0f}",
                    f"{d['discount_pct']}% (Rp {d['saving_amount']:,.0f})",
                    f"{d['tax_status']} | {d['city'] or 'N/A'}",
                    d["url"]
                )
            console.print(deals_table)

    finally:
        db.close()

def display_raw_listings(limit=25):
    """Menampilkan tabel dataset mentah hasil scraping dari database."""
    db = SessionLocal()
    try:
        listings = db.query(
            ScrapedListing, MasterVariant, MasterModel, MasterBrand
        ).outerjoin(
            MasterVariant, ScrapedListing.matched_variant_id == MasterVariant.id
        ).outerjoin(
            MasterModel, MasterVariant.model_id == MasterModel.id
        ).outerjoin(
            MasterBrand, MasterModel.brand_id == MasterBrand.id
        ).order_by(ScrapedListing.id.desc()).limit(limit).all()

        if not listings:
            console.print("[yellow]Tabel dataset mentah masih kosong. Silakan jalankan scraping terlebih dahulu.[/yellow]")
            return

        table = Table(title=f"📋 DATASET MENTAH HASIL SCRAPING (Menampilkan {len(listings)} Listing Terakhir)", show_lines=True)
        table.add_column("ID", justify="center", style="dim")
        table.add_column("Sumber", style="cyan")
        table.add_column("Judul Asli Listing", style="white", max_width=35)
        table.add_column("Tahun", justify="center", style="yellow")
        table.add_column("Harga", justify="right", style="bold green")
        table.add_column("Tipe Harga", justify="center")
        table.add_column("KM", justify="right", style="dim")
        table.add_column("Pajak / Plat", style="magenta")
        table.add_column("Lokasi", style="blue")
        table.add_column("Hasil AI Match", style="bold cyan", max_width=30)

        for l, var, model, brand in listings:
            matched_str = f"{brand.name} {model.name} - {var.variant_name}" if var else "[dim]Unmatched[/dim]"
            price_type_str = "[bold red]DP / Clickbait[/bold red]" if l.is_dp_price else "[green]Cash[/green]"
            km_str = f"{l.odometer_km:,} km" if l.odometer_km else "-"
            tax_plate_str = f"{l.tax_status or 'N/A'} (Plat {l.plate_region or '?'})"

            table.add_row(
                str(l.id),
                l.source_platform.upper(),
                l.title,
                str(l.claimed_year or "-"),
                f"Rp {float(l.price):,.0f}",
                price_type_str,
                km_str,
                tax_plate_str,
                l.city or "-",
                matched_str
            )

        console.print(table)
    finally:
        db.close()

def export_to_csv(filename="dataset_motor_mentah.csv"):
    """Ekspor seluruh isi dataset mentah ke file CSV."""
    import csv
    db = SessionLocal()
    try:
        listings = db.query(
            ScrapedListing, MasterVariant, MasterModel, MasterBrand
        ).outerjoin(
            MasterVariant, ScrapedListing.matched_variant_id == MasterVariant.id
        ).outerjoin(
            MasterModel, MasterVariant.model_id == MasterModel.id
        ).outerjoin(
            MasterBrand, MasterModel.brand_id == MasterBrand.id
        ).all()

        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "ID", "Source", "External_ID", "URL", "Title", "Raw_Description",
                "Claimed_Year", "Price", "Is_DP_Clickbait", "Odometer_KM",
                "Tax_Status", "Has_BPKB", "Has_STNK", "Plate_Region",
                "Province", "City", "Seller_Type", "Matched_Brand", "Matched_Model", "Matched_Variant"
            ])
            for l, var, model, brand in listings:
                writer.writerow([
                    l.id, l.source_platform, l.external_id, l.url, l.title, l.raw_description,
                    l.claimed_year, float(l.price), l.is_dp_price, l.odometer_km,
                    l.tax_status, l.has_bpkb, l.has_stnk, l.plate_region,
                    l.province, l.city, l.seller_type,
                    brand.name if brand else "", model.name if model else "", var.variant_name if var else ""
                ])

        console.print(f"[bold green]✓ Berhasil mengekspor {len(listings)} baris dataset ke file: [underline]{filename}[/underline][/bold green]")
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="Indonesian Used Motorcycle Price Monitor & Scraper Engine")
    parser.add_argument("--seed", action="store_true", help="Seed database dengan master katalog motor")
    parser.add_argument("--scrape", action="store_true", help="Jalankan scraper OLX")
    parser.add_argument("--query", type=str, default="", help="Spesifik query motor (contoh: 'Vario 150', 'NMAX 2020')")
    parser.add_argument("--location", type=str, default="dki_jakarta", help="Kode lokasi (dki_jakarta, jawa_barat, jawa_timur, etc.)")
    parser.add_argument("--pages", type=int, default=2, help="Jumlah halaman per query")
    parser.add_argument("--report", action="store_true", help="Tampilkan laporan harga pasar dan hot deals")
    parser.add_argument("--raw", action="store_true", help="Tampilkan tabel dataset mentah hasil scraping")
    parser.add_argument("--export-csv", type=str, default="", help="Ekspor data mentah ke CSV (contoh: --export-csv data.csv)")

    args = parser.parse_args()

    init_db()

    if len(sys.argv) == 1:
        # Default workflow jika dijalankan tanpa argumen
        run_seeder()
        run_scraping_and_pipeline(
            queries=["Vario 150", "NMAX", "Beat Deluxe", "Aerox 155", "PCX 160", "Scoopy"],
            location="dki_jakarta",
            pages=2
        )
        display_raw_listings(limit=15)
        display_market_price_report()
        return

    if args.seed:
        run_seeder()

    if args.scrape or args.query:
        # Pastikan master data sudah di-seed
        db = SessionLocal()
        brand_count = db.query(MasterBrand).count()
        db.close()
        if brand_count == 0:
            run_seeder()

        queries = [args.query] if args.query else ["Vario 150", "NMAX", "Beat", "Aerox", "PCX", "Scoopy"]
        run_scraping_and_pipeline(queries=queries, location=args.location, pages=args.pages)
        display_raw_listings(limit=15)
        display_market_price_report()
    elif args.raw:
        display_raw_listings(limit=30)
    elif args.report:
        display_market_price_report()

    if args.export_csv:
        export_to_csv(args.export_csv)

if __name__ == "__main__":
    main()
