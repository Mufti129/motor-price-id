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
    aliases = Column(Text, nullable=True) # Comma separated search keywords/aliases
    created_at = Column(DateTime, default=datetime.utcnow)

    model = relationship("MasterModel", back_populates="variants")
    scraped_listings = relationship("ScrapedListing", back_populates="matched_variant")


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
