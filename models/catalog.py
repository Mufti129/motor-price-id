from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Numeric, Boolean, DateTime, Date, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from models.database import Base

class MasterBrand(Base):
    __tablename__ = "master_brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True) # e.g. Honda, Yamaha
    country_origin = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    models = relationship("MasterModel", back_populates="brand", cascade="all, delete-orphan")


class MasterModel(Base):
    __tablename__ = "master_models"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("master_brands.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False, index=True) # e.g. Vario, NMAX, Beat, PCX
    category = Column(String(50), nullable=True) # Matic, Sport, Bebek, Trail, Maxi
    engine_capacity_cc = Column(Integer, nullable=True) # 110, 125, 150, 155, 160, 250
    image_url = Column(Text, nullable=True) # URL foto resmi studio model
    created_at = Column(DateTime, default=datetime.utcnow)

    brand = relationship("MasterBrand", back_populates="models")
    variants = relationship("MasterVariant", back_populates="model", cascade="all, delete-orphan")


class MasterVariant(Base):
    __tablename__ = "master_variants"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("master_models.id", ondelete="CASCADE"), nullable=False)
    variant_name = Column(String(150), nullable=False, index=True) # e.g. Vario 150 eSP Exclusive Keyless
    release_year_start = Column(Integer, nullable=False) # e.g. 2018
    release_year_end = Column(Integer, nullable=True) # e.g. 2022
    official_msrp_new = Column(Numeric(15, 2), nullable=True) # MSRP baru saat rilis
    transmission_type = Column(String(20), default="Automatic") # Automatic, Manual, Semi-Auto
    image_url = Column(Text, nullable=True) # URL foto spesifik varian
    aliases = Column(Text, nullable=True) # Comma separated search keywords/aliases
    created_at = Column(DateTime, default=datetime.utcnow)

    model = relationship("MasterModel", back_populates="variants")
    scraped_listings = relationship("ScrapedListing", back_populates="matched_variant")
    auction_lots = relationship("AuctionLot", back_populates="matched_variant")


class ScrapedListing(Base):
    __tablename__ = "scraped_listings"

    id = Column(Integer, primary_key=True, index=True)
    source_platform = Column(String(50), nullable=False, index=True) # 'olx', 'facebook', 'momotor'
    external_id = Column(String(100), nullable=False, index=True) # ID unik dari web sumber
    url = Column(Text, nullable=False)
    title = Column(String(300), nullable=False)
    raw_description = Column(Text, nullable=True)

    # Resolusi Entity oleh AI/Pipeline
    matched_variant_id = Column(Integer, ForeignKey("master_variants.id"), nullable=True, index=True)
    claimed_year = Column(Integer, nullable=True, index=True) # Tahun motor

    # Harga & DP Filter
    price = Column(Numeric(15, 2), nullable=False, index=True) # Harga (sudah divalidasi)
    is_dp_price = Column(Boolean, default=False, index=True) # Flag apakah harga ini hanya DP/Kredit palsu
    odometer_km = Column(Integer, nullable=True)

    # Status Dokumen & Pajak (Hasil ekstraksi NLP)
    tax_status = Column(String(50), nullable=True) # 'Hidup / Panjang', 'Mati / Off', 'Unknown'
    tax_expiry_year = Column(Integer, nullable=True)
    has_bpkb = Column(Boolean, default=True)
    has_stnk = Column(Boolean, default=True)
    plate_region = Column(String(20), nullable=True) # Plat B, Plat D, Plat L, etc.

    # Lokasi & Penjual
    province = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True, index=True)
    district = Column(String(100), nullable=True)
    seller_name = Column(String(150), nullable=True)
    seller_type = Column(String(50), nullable=True) # 'Individual', 'Dealer'

    # Timestamps
    posted_at = Column(DateTime, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="ACTIVE")

    __table_args__ = (
        UniqueConstraint("source_platform", "external_id", name="uq_source_external_id"),
    )

    matched_variant = relationship("MasterVariant", back_populates="scraped_listings")
    price_history = relationship("ListingPriceHistory", back_populates="listing", cascade="all, delete-orphan")
    image_analyses = relationship("ListingImageAnalysis", back_populates="listing", cascade="all, delete-orphan")


class AuctionLot(Base):
    """
    Unit Lot Balai Lelang Otomotif Resmi (JBA Indonesia & IBID Astra).
    Mencatat data inspeksi teknis, grade mesin/bodi, harga dasar limit, dan harga ketok palu final.
    """
    __tablename__ = "auction_listings"

    id = Column(Integer, primary_key=True, index=True)
    source_platform = Column(String(50), nullable=False, index=True) # 'jba_indonesia', 'ibid_astra'
    lot_number = Column(String(50), nullable=False, index=True)
    session_id = Column(String(100), nullable=True)
    auction_date = Column(Date, nullable=False, index=True)
    pool_city = Column(String(100), nullable=False, index=True)
    lane = Column(String(50), nullable=True)

    # Resolusi Varian
    matched_variant_id = Column(Integer, ForeignKey("master_variants.id"), nullable=True, index=True)
    claimed_year = Column(Integer, nullable=True, index=True)
    color = Column(String(50), nullable=True)
    license_plate = Column(String(30), nullable=True)
    plate_region = Column(String(20), nullable=True)

    # Hasil Inspeksi & Kondisi Fisik
    odometer_km = Column(Integer, nullable=True)
    grade_engine = Column(String(10), nullable=True) # 'A', 'B', 'C', 'D', 'E'
    grade_frame_body = Column(String(10), nullable=True) # 'A', 'B', 'C', 'D'
    overall_score = Column(String(20), nullable=True) # ACV score or overall grade
    engine_condition = Column(String(100), nullable=True) # 'Hidup Normal', 'Kasar', 'Mati Total'
    inspection_notes = Column(Text, nullable=True)

    # Legalitas & Dokumen
    stnk_status = Column(String(50), default="Ada")
    tax_status = Column(String(50), default="Hidup")
    bpkb_status = Column(String(50), default="Ready (Asli)")
    faktur_status = Column(Boolean, default=True)

    # Data Harga & Hasil Lelang
    base_limit_price = Column(Numeric(15, 2), nullable=False) # Harga Dasar Pembukaan
    hammer_price = Column(Numeric(15, 2), nullable=True) # Harga Ketok Palu Terbentuk
    admin_fee = Column(Numeric(15, 2), default=500000.0) # Biaya admin lelang
    auction_status = Column(String(30), default="Sold") # 'Sold', 'No Bid', 'Withdrawn'
    bid_count = Column(Integer, default=1)

    url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("source_platform", "lot_number", "auction_date", name="uq_auction_platform_lot_date"),
    )

    matched_variant = relationship("MasterVariant", back_populates="auction_lots")


class WholesalePriceStats(Base):
    """
    Agregasi Statistik Harga Wholesale & Lelang per Varian per Tanggal Sesi.
    """
    __tablename__ = "wholesale_price_stats"

    id = Column(Integer, primary_key=True, index=True)
    stat_date = Column(Date, nullable=False, default=datetime.utcnow().date, index=True)
    variant_id = Column(Integer, ForeignKey("master_variants.id"), nullable=False)
    year = Column(Integer, nullable=False)
    pool_city = Column(String(100), nullable=True)

    sample_count = Column(Integer, nullable=False)
    avg_base_price = Column(Numeric(15, 2))
    median_hammer_price = Column(Numeric(15, 2))
    min_base_price = Column(Numeric(15, 2))
    max_hammer_price = Column(Numeric(15, 2))
    clearance_rate_pct = Column(Numeric(5, 2), default=85.0)

    __table_args__ = (
        UniqueConstraint("stat_date", "variant_id", "year", "pool_city", name="uq_wholesale_stat_date_var_year_city"),
    )


class MarketPriceStats(Base):
    __tablename__ = "market_price_stats"

    id = Column(Integer, primary_key=True, index=True)
    stat_date = Column(Date, nullable=False, default=datetime.utcnow().date, index=True)
    variant_id = Column(Integer, ForeignKey("master_variants.id"), nullable=False)
    year = Column(Integer, nullable=False)
    city = Column(String(100), nullable=True)

    sample_count = Column(Integer, nullable=False)
    price_min = Column(Numeric(15, 2))
    price_p25 = Column(Numeric(15, 2)) # Bargain / Deal price
    price_median = Column(Numeric(15, 2)) # Fair Market Value (FMV)
    price_p75 = Column(Numeric(15, 2)) # Premium price
    price_max = Column(Numeric(15, 2))

    __table_args__ = (
        UniqueConstraint("stat_date", "variant_id", "year", "city", name="uq_stat_date_var_year_city"),
    )


class ListingPriceHistory(Base):
    """
    Riwayat Penurunan atau Perubahan Harga Listing Retail.
    Digunakan untuk menganalisis Days-on-Market dan tren Price Drop.
    """
    __tablename__ = "listing_price_history"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("scraped_listings.id", ondelete="CASCADE"), nullable=False, index=True)
    old_price = Column(Numeric(15, 2), nullable=False)
    new_price = Column(Numeric(15, 2), nullable=False)
    price_drop_pct = Column(Numeric(5, 2), nullable=False) # e.g. -5.25%
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    listing = relationship("ScrapedListing", back_populates="price_history")


class VehicleHistoryReport(Base):
    """
    Rekam Jejak Historis Kendaraan Berdasarkan Plat Nomor / VIN Rangka.
    Mencatat rekam odometri berkala, riwayat banjir, kecelakaan, dan status tilang ETLE.
    """
    __tablename__ = "vehicle_history_reports"

    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String(30), unique=True, nullable=False, index=True) # e.g. B 1234 XYZ
    vin_chassis_hash = Column(String(64), nullable=True, index=True)
    brand_name = Column(String(50), nullable=True)
    model_name = Column(String(100), nullable=True)
    production_year = Column(Integer, nullable=True)
    verified_odometer = Column(Integer, nullable=True)
    last_service_date = Column(Date, nullable=True)
    flood_history_flag = Column(Boolean, default=False)
    accident_history_flag = Column(Boolean, default=False)
    etle_ticket_status = Column(String(50), default="Clear / Bebas Tilang") # 'Clear', 'Ada Tilang Aktif'
    stnk_tax_valid_until = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ListingImageAnalysis(Base):
    """
    Hasil Ekstraksi & Inspeksi Computer Vision / AI pada Foto Listing.
    Mendeteksi kerusakan bodi/baret, knalpot brong non-standar, dan skor keaslian foto.
    """
    __tablename__ = "listing_image_analysis"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("scraped_listings.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(Text, nullable=False)
    scratch_damage_score = Column(Numeric(5, 2), default=0.0) # Skala 0-100 (semakin tinggi semakin banyak baret)
    paint_originality_score = Column(Numeric(5, 2), default=95.0) # Persentase cat orisinil
    non_standard_exhaust_flag = Column(Boolean, default=False) # Deteksi knalpot non-standar
    image_authenticity_score = Column(Numeric(5, 2), default=98.0) # Deteksi foto asli vs comotan internet
    detected_color = Column(String(50), nullable=True)
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    listing = relationship("ScrapedListing", back_populates="image_analyses")


class B2BApiClient(Base):
    """
    Manajemen Mitra Korporasi / Klien B2B (Leasing, Fintech, Dealer Group).
    """
    __tablename__ = "b2b_api_clients"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(150), nullable=False)
    contact_email = Column(String(100), unique=True, nullable=False, index=True)
    api_key = Column(String(64), unique=True, nullable=False, index=True)
    tier = Column(String(30), default="Enterprise") # 'Starter', 'Professional', 'Enterprise'
    rate_limit_per_minute = Column(Integer, default=600)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    logs = relationship("ApiUsageLog", back_populates="client", cascade="all, delete-orphan")


class ApiUsageLog(Base):
    """
    Audit Log Request API B2B untuk Pelaporan SLA & Kuota.
    """
    __tablename__ = "api_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("b2b_api_clients.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint = Column(String(150), nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Numeric(8, 2), default=15.0)
    requested_at = Column(DateTime, default=datetime.utcnow, index=True)

    client = relationship("B2BApiClient", back_populates="logs")


class UserDealAlert(Base):
    """
    Langganan Notifikasi Deal Arbitrase / Motor Murah di Bawah Pasar.
    """
    __tablename__ = "user_deal_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_contact = Column(String(150), nullable=False) # WhatsApp atau Email
    variant_id = Column(Integer, ForeignKey("master_variants.id"), nullable=False)
    target_year = Column(Integer, nullable=True)
    target_city = Column(String(100), nullable=True)
    max_price = Column(Numeric(15, 2), nullable=False) # Batas harga maksimal
    min_discount_pct = Column(Numeric(5, 2), default=15.0) # Minimal diskon dari harga wajar
    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


