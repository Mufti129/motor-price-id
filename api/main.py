"""
MotorPrice ID B2B Enterprise REST API.
Layanan REST API berkinerja tinggi untuk integrasi sistem perbankan, perusahaan leasing (multifinance),
dealer showroom, dan agregator otomotif.
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.database import get_db, SessionLocal
from models.catalog import MasterBrand, MasterModel, MasterVariant
from analytics.pricing_engine import PricingAnalyticsEngine
from analytics.regional_index import REGIONAL_PRICE_INDEX, apply_regional_pricing
from analytics.ml_valuation_model import ml_model_v6

app = FastAPI(
    title="MotorPrice ID - Enterprise Valuation API",
    version="6.2.4",
    description="RESTful API resmi penentuan Fair Market Value (FMV), Koridor Wholesale Lelang, dan Proyeksi Depresiasi Sepeda Motor Indonesia."
)

# Pydantic Schemas
class ValuationRequest(BaseModel):
    variant_id: int = Field(..., description="ID unik Varian Master Katalog")
    year: int = Field(2024, description="Tahun pembuatan kendaraan (2014-2026)")
    odometer_km: int = Field(25000, description="Jarak tempuh odometer dalam Kilometer")
    tax_status: str = Field("Pajak Hidup / Panjang", description="Status legalitas pajak STNK")
    has_bpkb: bool = Field(True, description="Kelengkapan dokumen fisik BPKB")
    region: str = Field("Jabodetabek (DKI Jakarta, Bogor, Depok, Tangerang, Bekasi)", description="Wilayah administratif penilaian")

class ForecastRequest(BaseModel):
    variant_id: int
    year: int
    current_fmv: float

@app.get("/api/v1/health", tags=["System"])
def health_check():
    return {
        "status": "HEALTHY",
        "system": "MotorPrice ID Enterprise API",
        "model_version": "v6.2.4-Enterprise",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/catalog/brands", tags=["Catalog"])
def get_brands():
    db = SessionLocal()
    try:
        brands = db.query(MasterBrand).order_by(MasterBrand.name).all()
        return [
            {"id": b.id, "name": b.name, "country_origin": b.country_origin}
            for b in brands
        ]
    finally:
        db.close()

@app.get("/api/v1/catalog/models", tags=["Catalog"])
def get_models(brand_id: Optional[int] = None):
    db = SessionLocal()
    try:
        query = db.query(MasterModel)
        if brand_id:
            query = query.filter(MasterModel.brand_id == brand_id)
        models = query.order_by(MasterModel.name).all()
        return [
            {
                "id": m.id,
                "brand_id": m.brand_id,
                "name": m.name,
                "category": m.category,
                "engine_capacity_cc": m.engine_capacity_cc,
                "image_url": getattr(m, "image_url", None)
            }
            for m in models
        ]
    finally:
        db.close()

@app.get("/api/v1/catalog/variants", tags=["Catalog"])
def get_variants(model_id: Optional[int] = None):
    db = SessionLocal()
    try:
        query = db.query(MasterVariant)
        if model_id:
            query = query.filter(MasterVariant.model_id == model_id)
        variants = query.order_by(MasterVariant.variant_name).all()
        return [
            {
                "id": v.id,
                "model_id": v.model_id,
                "variant_name": v.variant_name,
                "release_year_start": v.release_year_start,
                "release_year_end": v.release_year_end,
                "official_msrp_new": float(v.official_msrp_new) if v.official_msrp_new else None,
                "image_url": getattr(v, "image_url", None)
            }
            for v in variants
        ]
    finally:
        db.close()

@app.post("/api/v1/valuation/calculate", tags=["Valuation"])
def calculate_fmv(req: ValuationRequest):
    db = SessionLocal()
    try:
        var = db.query(MasterVariant).filter(MasterVariant.id == req.variant_id).first()
        if not var:
            raise HTTPException(status_code=404, detail="Master Variant ID tidak ditemukan.")

        model = var.model
        brand = model.brand if model else None

        pricing_engine = PricingAnalyticsEngine(db)
        stats = pricing_engine.calculate_variant_pricing_stats(var.id, year=req.year)
        
        base_price = stats["price_median"] if stats else (float(var.official_msrp_new or 20000000) * 0.70)
        sample_count = stats["sample_count"] if stats else 0

        # Adjustments
        adj_tax = 0.0
        if "1" in req.tax_status:
            adj_tax = -650000.0
        elif "2" in req.tax_status:
            adj_tax = -1400000.0

        expected_km = max(5000, (2026 - req.year) * 8500)
        km_diff = req.odometer_km - expected_km
        adj_km = max(-2500000.0, min(1200000.0, - (km_diff / 5000) * 250000.0))
        adj_bpkb = 0.0 if req.has_bpkb else (- (base_price * 0.35))

        national_fmv = max(3500000.0, base_price + adj_tax + adj_km + adj_bpkb)
        regional_res = apply_regional_pricing(national_fmv, req.region)

        # ML Forecast
        forecast = ml_model_v6.forecast_residual_value_curve(
            regional_res["regional_adjusted_price"],
            req.year,
            model.engine_capacity_cc if model else 125,
            model.category if model else "Matic"
        )

        return {
            "vehicle": {
                "brand": brand.name if brand else "-",
                "model": model.name if model else "-",
                "variant": var.variant_name,
                "year": req.year,
                "msrp_new": float(var.official_msrp_new) if var.official_msrp_new else None,
                "image_url": getattr(var, "image_url", None) or (getattr(model, "image_url", None) if model else None)
            },
            "valuation": {
                "fair_market_value": round(regional_res["regional_adjusted_price"], -3),
                "bargain_p25": round(regional_res["regional_adjusted_price"] * 0.92, -3),
                "premium_p75": round(regional_res["regional_adjusted_price"] * 1.08, -3),
                "sample_count": sample_count,
                "methodology": "Empirical Quantile Median" if sample_count > 0 else "MSRP Theoretical Age-Decay Fallback"
            },
            "regional_adjustment": regional_res,
            "residual_forecast": forecast
        }
    finally:
        db.close()

@app.get("/api/v1/wholesale/corridor/{variant_id}/{year}", tags=["Wholesale & Auction"])
def get_wholesale_corridor(variant_id: int, year: int):
    db = SessionLocal()
    try:
        engine = PricingAnalyticsEngine(db)
        corridor = engine.calculate_dual_tier_corridor(variant_id, year)
        if not corridor:
            raise HTTPException(status_code=404, detail="Data koridor tidak ditemukan.")
        return corridor
    finally:
        db.close()

@app.get("/api/v1/arbitrage/deals", tags=["Arbitrage"])
def get_arbitrage_deals(min_discount: float = 12.0):
    db = SessionLocal()
    try:
        engine = PricingAnalyticsEngine(db)
        deals = engine.find_hot_deals(discount_threshold_pct=min_discount)
        return {"total_deals": len(deals), "deals": deals}
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
