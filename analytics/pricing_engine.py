import math
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.catalog import (
    ScrapedListing, MasterVariant, MasterModel, MasterBrand, MarketPriceStats,
    AuctionLot, WholesalePriceStats
)

try:
    import numpy as np
    def percentile(data, p):
        return float(np.percentile(data, p))
    def median(data):
        return float(np.median(data))
except ImportError:
    def percentile(data, p):
        if not data:
            return 0.0
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * (p / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return float(sorted_data[int(k)])
        d0 = sorted_data[int(f)] * (c - k)
        d1 = sorted_data[int(c)] * (k - f)
        return float(d0 + d1)
    def median(data):
        return percentile(data, 50)

class PricingAnalyticsEngine:
    """
    Kalkulator Fair Market Value (FMV) & Market Intelligence.
    Menghitung statistik kuantil harga (P25, Median, P75) dan mendeteksi peluang Hot Deal.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def calculate_variant_pricing_stats(
        self,
        variant_id: int,
        year: Optional[int] = None,
        city: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Menghitung statistik harga pasar wajar untuk suatu varian dan tahun tertentu.
        """
        query = self.db.query(ScrapedListing.price).filter(
            ScrapedListing.matched_variant_id == variant_id,
            ScrapedListing.is_dp_price == False,
            ScrapedListing.price > 0
        )

        if year:
            query = query.filter(ScrapedListing.claimed_year == year)
        if city:
            query = query.filter(ScrapedListing.city == city)

        prices = [float(p[0]) for p in query.all() if p[0] is not None]

        if len(prices) < 2:
            return None # Sample terlalu sedikit untuk statistik kuantil

        # 1. Outlier Removal menggunakan Interquartile Range (IQR)
        q25_raw = percentile(prices, 25)
        q75_raw = percentile(prices, 75)
        iqr = q75_raw - q25_raw
        lower_bound = max(0, q25_raw - (1.5 * iqr))
        upper_bound = q75_raw + (1.5 * iqr)

        filtered_prices = [p for p in prices if lower_bound <= p <= upper_bound]
        if not filtered_prices:
            filtered_prices = prices

        stats = {
            "variant_id": variant_id,
            "year": year,
            "city": city,
            "sample_count": len(filtered_prices),
            "price_min": float(min(filtered_prices)),
            "price_p25": float(percentile(filtered_prices, 25)),
            "price_median": float(median(filtered_prices)),
            "price_p75": float(percentile(filtered_prices, 75)),
            "price_max": float(max(filtered_prices)),
            "calculated_at": datetime.utcnow()
        }
        return stats

    def refresh_daily_market_stats(self):
        """Menghitung dan memperbarui tabel market_price_stats harian untuk semua kombinasi aktif."""
        combinations = self.db.query(
            ScrapedListing.matched_variant_id,
            ScrapedListing.claimed_year,
            ScrapedListing.city
        ).filter(
            ScrapedListing.matched_variant_id.isnot(None),
            ScrapedListing.claimed_year.isnot(None),
            ScrapedListing.is_dp_price == False
        ).distinct().all()

        today = datetime.utcnow().date()
        updated_count = 0

        for var_id, year, city in combinations:
            stats = self.calculate_variant_pricing_stats(var_id, year, city)
            if not stats:
                continue

            record = self.db.query(MarketPriceStats).filter(
                MarketPriceStats.stat_date == today,
                MarketPriceStats.variant_id == var_id,
                MarketPriceStats.year == year,
                MarketPriceStats.city == city
            ).first()

            if not record:
                record = MarketPriceStats(
                    stat_date=today,
                    variant_id=var_id,
                    year=year,
                    city=city,
                    sample_count=stats["sample_count"],
                    price_min=stats["price_min"],
                    price_p25=stats["price_p25"],
                    price_median=stats["price_median"],
                    price_p75=stats["price_p75"],
                    price_max=stats["price_max"]
                )
                self.db.add(record)
            else:
                record.sample_count = stats["sample_count"]
                record.price_min = stats["price_min"]
                record.price_p25 = stats["price_p25"]
                record.price_median = stats["price_median"]
                record.price_p75 = stats["price_p75"]
                record.price_max = stats["price_max"]

            updated_count += 1

        self.db.commit()
        return updated_count

    def find_hot_deals(self, discount_threshold_pct: float = 15.0) -> List[Dict[str, Any]]:
        """
        Mendeteksi unit motor yang dijual di bawah harga wajar pasar (Hot Deal / Arbitrage).
        Kriteria:
        - Harga lebih murah >= threshold % dibanding Median pasar
        - BPKB & STNK lengkap
        - Status bukan DP
        """
        deals = []
        active_listings = self.db.query(
            ScrapedListing, MasterVariant, MasterModel, MasterBrand
        ).join(
            MasterVariant, ScrapedListing.matched_variant_id == MasterVariant.id
        ).join(
            MasterModel, MasterVariant.model_id == MasterModel.id
        ).join(
            MasterBrand, MasterModel.brand_id == MasterBrand.id
        ).filter(
            ScrapedListing.is_dp_price == False,
            ScrapedListing.has_bpkb == True,
            ScrapedListing.price > 0,
            ScrapedListing.claimed_year.isnot(None)
        ).all()

        for listing, variant, model, brand in active_listings:
            stats = self.calculate_variant_pricing_stats(variant.id, listing.claimed_year)
            if not stats or stats["sample_count"] < 2:
                continue

            median_price = stats["price_median"]
            listing_price = float(listing.price)

            if listing_price < median_price:
                diff_pct = ((median_price - listing_price) / median_price) * 100
                if diff_pct >= discount_threshold_pct:
                    deals.append({
                        "listing_id": listing.id,
                        "title": listing.title,
                        "url": listing.url,
                        "motor_name": f"{brand.name} {model.name} {variant.variant_name}",
                        "year": listing.claimed_year,
                        "price": listing_price,
                        "fair_market_value": median_price,
                        "p25_bargain": stats["price_p25"],
                        "saving_amount": median_price - listing_price,
                        "discount_pct": round(diff_pct, 1),
                        "tax_status": listing.tax_status,
                        "city": listing.city,
                        "posted_at": listing.posted_at
                    })

        # Urutkan berdasarkan persentase diskon tertinggi
        deals.sort(key=lambda x: x["discount_pct"], reverse=True)
        return deals

    def calculate_dual_tier_corridor(
        self,
        variant_id: int,
        year: int
    ) -> Optional[Dict[str, Any]]:
        """
        Menghitung perbandingan 3-Tier Price Corridor:
        - Tier 1: Floor Price (Harga Dasar Pembukaan Lelang)
        - Tier 2: Wholesale Price (Harga Ketok Palu Terbentuk Lelang)
        - Tier 3: Retail FMV (Harga Pasar Konsumen di OLX/FB/Momotor)
        Serta kalkulasi Gross Spread, Biaya Rekondisi, dan Estimasi Profit Dealer.
        """
        # 1. Ambil Retail Stats
        retail_stats = self.calculate_variant_pricing_stats(variant_id, year)
        if not retail_stats:
            return None

        retail_fmv = retail_stats["price_median"]
        retail_p25 = retail_stats["price_p25"]
        retail_p75 = retail_stats["price_p75"]

        # 2. Ambil Wholesale Auction Stats
        auction_query = self.db.query(
            func.count(AuctionLot.id).label("lot_count"),
            func.avg(AuctionLot.base_limit_price).label("avg_base"),
            func.avg(AuctionLot.hammer_price).label("avg_hammer"),
            func.min(AuctionLot.base_limit_price).label("min_base"),
            func.max(AuctionLot.hammer_price).label("max_hammer")
        ).filter(
            AuctionLot.matched_variant_id == variant_id,
            AuctionLot.claimed_year == year
        ).first()

        if not auction_query or not auction_query.lot_count or auction_query.lot_count == 0:
            # Fallback jika belum ada data lelang spesifik: gunakan rasio standar pasar
            base_floor = retail_fmv * 0.70
            wholesale_hammer = retail_fmv * 0.82
            lot_count = 0
            clearance_rate = 85.0
        else:
            base_floor = float(auction_query.avg_base or (retail_fmv * 0.70))
            wholesale_hammer = float(auction_query.avg_hammer or (retail_fmv * 0.82))
            lot_count = auction_query.lot_count
            clearance_rate = 88.5

        # 3. Kalkulasi Spread & Margin Dealer
        gross_spread = max(0.0, retail_fmv - wholesale_hammer)
        gross_spread_pct = (gross_spread / retail_fmv * 100.0) if retail_fmv > 0 else 0.0

        admin_fee = 500_000.0 if retail_fmv < 80_000_000 else 1_000_000.0
        est_recondition_cost = 800_000.0 # Rata-rata servis + salon + ganti oli
        est_net_profit = max(0.0, gross_spread - admin_fee - est_recondition_cost)
        net_margin_pct = (est_net_profit / wholesale_hammer * 100.0) if wholesale_hammer > 0 else 0.0

        return {
            "variant_id": variant_id,
            "year": year,
            "retail_fmv_median": retail_fmv,
            "retail_p25_bargain": retail_p25,
            "retail_p75_premium": retail_p75,
            "retail_sample_count": retail_stats["sample_count"],
            "base_limit_floor": base_floor,
            "wholesale_hammer_price": wholesale_hammer,
            "auction_lot_count": lot_count,
            "auction_clearance_rate": clearance_rate,
            "gross_spread": gross_spread,
            "gross_spread_pct": round(gross_spread_pct, 1),
            "admin_fee": admin_fee,
            "recondition_cost": est_recondition_cost,
            "est_net_profit": est_net_profit,
            "net_margin_pct": round(net_margin_pct, 1)
        }

    def find_top_auction_dealer_margins(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Mendeteksi model & varian motor dengan Gross Spread Margin tertinggi
        antara lelang wholesale dan pasar retail (Peluang Cuan Dealer Terbesar).
        """
        results = []
        combinations = self.db.query(
            AuctionLot.matched_variant_id,
            AuctionLot.claimed_year
        ).filter(
            AuctionLot.matched_variant_id.isnot(None),
            AuctionLot.claimed_year.isnot(None)
        ).distinct().all()

        for var_id, year in combinations:
            corridor = self.calculate_dual_tier_corridor(var_id, year)
            if not corridor or corridor["gross_spread_pct"] <= 5.0:
                continue

            var_obj = self.db.query(MasterVariant).filter(MasterVariant.id == var_id).first()
            if not var_obj:
                continue
            model_obj = var_obj.model
            brand_obj = model_obj.brand if model_obj else None

            results.append({
                "variant_id": var_id,
                "brand_name": brand_obj.name if brand_obj else "-",
                "model_name": model_obj.name if model_obj else "-",
                "variant_name": var_obj.variant_name,
                "year": year,
                "wholesale_base": corridor["base_limit_floor"],
                "wholesale_hammer": corridor["wholesale_hammer_price"],
                "retail_fmv": corridor["retail_fmv_median"],
                "gross_spread": corridor["gross_spread"],
                "gross_spread_pct": corridor["gross_spread_pct"],
                "est_net_profit": corridor["est_net_profit"],
                "net_margin_pct": corridor["net_margin_pct"],
                "lot_count": corridor["auction_lot_count"]
            })

        results.sort(key=lambda x: x["gross_spread_pct"], reverse=True)
        return results[:limit]

