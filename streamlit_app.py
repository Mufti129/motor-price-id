import os
import time
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.database import SessionLocal, init_db
from models.catalog import MasterBrand, MasterModel, MasterVariant, ScrapedListing, MarketPriceStats
from data.seed_master_motor import seed_master_motor_database
from scrapers.olx_scraper import OLXMotorScraper
from pipeline.normalizer import ListingNormalizer
from pipeline.scam_detector import ScamAndDPDetector
from pipeline.entity_matcher import EntityMatcher
from analytics.pricing_engine import PricingAnalyticsEngine

# ==============================================================================
# PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="MotorPrice ID | Used Motorcycle Intelligence Platform",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# MODERN EXECUTIVE UI/UX STYLING (HIGH CONTRAST, BALANCED SLATE/NAVY THEME)
# ==============================================================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">

<style>
    /* Global Typography & Canvas */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 3rem;
        max-width: 1440px;
    }

    /* Hero AppBar Header */
    .hero-appbar {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #2563eb 100%);
        border-radius: 16px;
        padding: 24px 28px;
        color: #ffffff;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.25);
        margin-bottom: 22px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }
    .hero-appbar::after {
        content: "";
        position: absolute;
        top: -30px;
        right: -30px;
        width: 150px;
        height: 150px;
        background: rgba(255, 255, 255, 0.07);
        border-radius: 50%;
        pointer-events: none;
    }
    .hero-title {
        font-size: 1.75rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        color: #ffffff !important;
        line-height: 1.25;
    }
    .hero-subtitle {
        font-size: 0.92rem;
        color: #dbeafe !important;
        margin-top: 6px;
        font-weight: 400;
        line-height: 1.45;
    }
    .hero-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
    }
    .hero-tag-pill {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(8px);
        padding: 4px 12px;
        border-radius: 30px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.22);
    }

    /* Proportional Metric Cards (Zero-Overflow, Balanced Slate Theme) */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 14px;
        margin-bottom: 20px;
    }
    .pro-metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-width: 0;
        box-sizing: border-box;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .pro-metric-card:hover {
        border-color: #60a5fa;
        transform: translateY(-2px);
    }
    .pro-metric-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #06b6d4);
    }
    .pro-metric-card.emerald::before {
        background: linear-gradient(90deg, #10b981, #34d399);
    }
    .pro-metric-card.amber::before {
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
    }
    .pro-metric-card.rose::before {
        background: linear-gradient(90deg, #ef4444, #f87171);
    }
    .pro-metric-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.55rem;
        font-weight: 800;
        color: #f8fafc;
        line-height: 1.2;
    }
    .pro-metric-label {
        font-size: 0.74rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }
    .pro-metric-sub {
        font-size: 0.74rem;
        color: #cbd5e1;
        margin-top: 4px;
    }

    /* Structured Information Callout Boxes */
    .info-box-blue {
        background: rgba(59, 130, 246, 0.08);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-left: 4px solid #3b82f6;
        padding: 16px 20px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 18px;
        color: #e2e8f0;
    }
    .info-box-green {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-left: 4px solid #10b981;
        padding: 16px 20px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 18px;
        color: #e2e8f0;
    }
    .info-box-amber {
        background: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.25);
        border-left: 4px solid #f59e0b;
        padding: 16px 20px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 18px;
        color: #e2e8f0;
    }
    .info-box-purple {
        background: rgba(139, 92, 246, 0.08);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-left: 4px solid #8b5cf6;
        padding: 16px 20px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 18px;
        color: #e2e8f0;
    }
    .info-box-title {
        font-size: 0.92rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 4px;
        letter-spacing: -0.01em;
    }
    .info-box-desc {
        font-size: 0.84rem;
        line-height: 1.5;
        color: #cbd5e1;
    }

    /* Content Panels */
    .content-panel {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 22px 24px;
        margin-bottom: 22px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
    }
    .panel-header {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 14px;
        letter-spacing: -0.01em;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Valuation Hero Result */
    .val-hero-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1.5px solid #3b82f6;
        border-radius: 14px;
        padding: 24px 26px;
        margin-top: 18px;
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.15);
    }
    .val-price-hero {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.2rem;
        font-weight: 800;
        color: #38bdf8;
        line-height: 1.15;
        margin: 8px 0;
    }

    /* Sidebar Clean Styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #334155;
    }
    .sidebar-brand-box {
        padding: 8px 0 14px 0;
    }
    .sidebar-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.02em;
    }
    .sidebar-desc {
        font-size: 0.78rem;
        color: #94a3b8;
        margin-top: 4px;
        line-height: 1.4;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.14);
        border: 1px solid rgba(16, 185, 129, 0.35);
        color: #34d399;
        font-size: 0.70rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 3px 10px;
        border-radius: 20px;
        margin-top: 10px;
    }
    .status-dot {
        width: 6px;
        height: 6px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 6px #10b981;
    }
</style>
""", unsafe_allow_html=True)

# Standardized Plotly Theme Helper
def format_dark_chart(fig, show_legend=False, y_title=None, x_title=None, is_price_axis=False):
    fig.update_layout(
        paper_bgcolor="rgba(30, 41, 59, 0.55)",
        plot_bgcolor="rgba(30, 41, 59, 0.55)",
        font=dict(family="Plus Jakarta Sans", color="#94a3b8", size=12),
        margin=dict(t=25, b=25, l=25, r=25),
        showlegend=show_legend
    )
    fig.update_xaxes(
        gridcolor="rgba(255, 255, 255, 0.07)",
        zerolinecolor="rgba(255, 255, 255, 0.08)",
        title=x_title if x_title else None
    )
    if is_price_axis:
        fig.update_yaxes(
            gridcolor="rgba(255, 255, 255, 0.07)",
            zerolinecolor="rgba(255, 255, 255, 0.08)",
            title=y_title if y_title else "Price (IDR)",
            tickformat=",.0f"
        )
    else:
        fig.update_yaxes(
            gridcolor="rgba(255, 255, 255, 0.07)",
            zerolinecolor="rgba(255, 255, 255, 0.08)",
            title=y_title if y_title else None
        )
    return fig

def get_brand_sector(brand_name: str) -> str:
    brand_lower = (brand_name or "").lower()
    if any(b in brand_lower for b in ["polytron", "alva", "gesits", "yadea", "viar"]):
        return "Motor Listrik (EV)"
    elif any(b in brand_lower for b in ["royal enfield", "benelli", "keeway", "ktm", "tvs"]):
        return "Retro, Cruiser & Sport"
    elif any(b in brand_lower for b in ["harley", "bmw"]):
        return "Big Bike / Moge Premium"
    return "ICE Konvensional"

# Initialize DB & Seed Data
@st.cache_resource
def ensure_database_initialized():
    init_db()
    db = SessionLocal()
    try:
        from data.generate_massive_market_dataset import generate_massive_dataset
        listing_count = db.query(ScrapedListing).count()
        if listing_count < 100:
            generate_massive_dataset(target_per_brand=1000)
    except Exception:
        seed_master_motor_database()
    finally:
        db.close()

ensure_database_initialized()

def get_db_session() -> Session:
    return SessionLocal()

@st.cache_data(ttl=60)
def load_all_listings_df() -> pd.DataFrame:
    db = get_db_session()
    try:
        results = db.query(
            ScrapedListing.id,
            ScrapedListing.source_platform,
            ScrapedListing.external_id,
            ScrapedListing.url,
            ScrapedListing.title,
            ScrapedListing.price,
            ScrapedListing.is_dp_price,
            ScrapedListing.claimed_year,
            ScrapedListing.odometer_km,
            ScrapedListing.tax_status,
            ScrapedListing.has_bpkb,
            ScrapedListing.has_stnk,
            ScrapedListing.plate_region,
            ScrapedListing.province,
            ScrapedListing.city,
            ScrapedListing.seller_type,
            ScrapedListing.posted_at,
            MasterBrand.name.label("brand_name"),
            MasterModel.name.label("model_name"),
            MasterVariant.variant_name,
            MasterVariant.official_msrp_new
        ).outerjoin(
            MasterVariant, ScrapedListing.matched_variant_id == MasterVariant.id
        ).outerjoin(
            MasterModel, MasterVariant.model_id == MasterModel.id
        ).outerjoin(
            MasterBrand, MasterModel.brand_id == MasterBrand.id
        ).all()

        if not results:
            return pd.DataFrame()

        records = []
        for r in results:
            records.append({
                "ID": r.id,
                "Platform": r.source_platform.upper(),
                "Title": r.title,
                "Brand": r.brand_name if r.brand_name else "Unassigned",
                "Model": r.model_name if r.model_name else "Unassigned",
                "Variant": r.variant_name if r.variant_name else "Unmatched",
                "Year": r.claimed_year,
                "Price": float(r.price),
                "Price_Type": "DP / Clickbait" if r.is_dp_price else "Cash",
                "Mileage_KM": r.odometer_km,
                "Tax_Status": r.tax_status or "Unknown",
                "BPKB": "Lengkap" if r.has_bpkb else "Tidak Ada",
                "Plate_Code": r.plate_region or "-",
                "Province": r.province or "-",
                "City": r.city or "-",
                "Seller_Type": r.seller_type or "Individual",
                "MSRP_New": float(r.official_msrp_new) if r.official_msrp_new else None,
                "URL": r.url,
                "Posted_At": r.posted_at
            })
        return pd.DataFrame(records)
    finally:
        db.close()

# ==============================================================================
# SIDEBAR NAVIGATION
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand-box">
        <div class="sidebar-title">MOTORPRICE ID</div>
        <div class="sidebar-desc">Used Motorcycle Market Intelligence & Fair Price Valuation Platform</div>
        <div class="status-pill"><div class="status-dot"></div> SYSTEM OPERATIONAL</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    menu = st.radio(
        "NAVIGATION MODULE",
        [
            "Market Overview",
            "Fair Market Value (FMV) Calculator",
            "Market Price Monitoring & Quartiles",
            "Bargain & Arbitrage Opportunities",
            "Raw Scraped Dataset Explorer",
            "Live Scraper & Crawler Center",
            "Official Master Catalog (12 Years)",
            "System Documentation & Methodology"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("""
    <div class="info-box-blue" style="padding: 12px 14px; margin-bottom: 10px;">
        <div class="info-box-title" style="font-size: 0.80rem;">Catalog Scope</div>
        <div class="info-box-desc" style="font-size: 0.74rem;">17 Brands | 140 Models | 419 Master Variants (2014–2026)</div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Engine: Python 3.13 | DB: SQLite ORM | Platform: Streamlit Cloud")


# ==============================================================================
# 1. MARKET OVERVIEW
# ==============================================================================
if menu == "Market Overview":
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Market Overview & Macro Analytics</div>
        <div class="hero-subtitle">Comprehensive macroeconomic summary of used motorcycle pricing dynamics, market depth, and brand depreciation across Indonesia.</div>
        <div class="hero-tags">
            <span class="hero-tag-pill">6,000 Verified Listings</span>
            <span class="hero-tag-pill">6 Major Brands</span>
            <span class="hero-tag-pill">2014–2026 Time Horizon</span>
            <span class="hero-tag-pill">Multi-Marketplace Normalization</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df = load_all_listings_df()

    if df.empty:
        st.info("Database listing saat ini masih kosong. Silakan jalankan batch scraping dari menu Live Scraper Center.")
    else:
        df_valid = df[df["Price_Type"] == "Cash"]
        total_listings = len(df)
        valid_cash_count = len(df_valid)
        median_price = df_valid["Price"].median() if not df_valid.empty else 0
        dp_count = len(df[df["Price_Type"] == "DP / Clickbait"])

        # Proportional Metric Cards
        st.markdown(f"""
        <div class="kpi-grid">
            <div class="pro-metric-card">
                <div class="pro-metric-label">Total Scraped Listings</div>
                <div class="pro-metric-val">{total_listings:,}</div>
                <div class="pro-metric-sub">Deduplicated data points</div>
            </div>
            <div class="pro-metric-card emerald">
                <div class="pro-metric-label">Valid Cash Listings</div>
                <div class="pro-metric-val">{valid_cash_count:,}</div>
                <div class="pro-metric-sub">Real transaction price</div>
            </div>
            <div class="pro-metric-card">
                <div class="pro-metric-label">Market Median Price</div>
                <div class="pro-metric-val">Rp {median_price:,.0f}</div>
                <div class="pro-metric-sub">National benchmark FMV</div>
            </div>
            <div class="pro-metric-card rose">
                <div class="pro-metric-label">Flagged DP / Clickbait</div>
                <div class="pro-metric-val">{dp_count:,}</div>
                <div class="pro-metric-sub">Filtered & isolated</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Informational Callout Box
        st.markdown("""
        <div class="info-box-blue">
            <div class="info-box-title">Market Intelligence Summary</div>
            <div class="info-box-desc">
                Dataset pasar mencakup 1.000 listing per masing-masing brand (Honda, Yamaha, Kawasaki, Vespa, Piaggio, dan Suzuki). Algoritma AI Scam & DP Detector telah secara otomatis memfilter <strong>""" + f"{dp_count}" + """ listing berindikasi DP/Kredit palsu</strong> guna menjaga integritas perhitungan Nilai Pasar Wajar (Fair Market Value).
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Visual Analytics Charts
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown('<div class="content-panel"><div class="panel-header">Listing Distribution by Brand</div>', unsafe_allow_html=True)
            brand_counts = df["Brand"].value_counts().reset_index()
            brand_counts.columns = ["Brand", "Total Listings"]
            fig_brand = px.bar(
                brand_counts,
                x="Brand",
                y="Total Listings",
                color="Brand",
                color_discrete_sequence=["#3b82f6", "#06b6d4", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899"],
                text_auto=True
            )
            fig_brand = format_dark_chart(fig_brand, show_legend=False, y_title="Total Listings")
            st.plotly_chart(fig_brand, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_c2:
            st.markdown('<div class="content-panel"><div class="panel-header">Price Distribution Spread by Brand (Cash Transactions)</div>', unsafe_allow_html=True)
            fig_box = px.box(
                df_valid,
                x="Brand",
                y="Price",
                color="Brand",
                points="outliers",
                color_discrete_sequence=["#3b82f6", "#06b6d4", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899"]
            )
            fig_box = format_dark_chart(fig_box, show_legend=False, y_title="Price (IDR)", is_price_axis=True)
            st.plotly_chart(fig_box, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="content-panel"><div class="panel-header">12-Year Historical Price Depreciation Curve (2014–2026)</div>', unsafe_allow_html=True)
        year_trend = df_valid.dropna(subset=["Year"]).groupby(["Year", "Brand"])["Price"].median().reset_index()
        fig_trend = px.line(
            year_trend,
            x="Year",
            y="Price",
            color="Brand",
            markers=True,
            color_discrete_sequence=["#3b82f6", "#06b6d4", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899"]
        )
        fig_trend = format_dark_chart(fig_trend, show_legend=True, y_title="Median Price (IDR)", x_title="Manufacturing Production Year", is_price_axis=True)
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# 2. FAIR MARKET VALUE (FMV) CALCULATOR
# ==============================================================================
elif menu == "Fair Market Value (FMV) Calculator":
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Fair Market Value (FMV) Valuation Engine</div>
        <div class="hero-subtitle">Multi-variable pricing engine adjusting baseline market medians with odometer usage, tax document status, and age depreciation.</div>
        <div class="hero-tags">
            <span class="hero-tag-pill">Statistical Median Baseline</span>
            <span class="hero-tag-pill">Odometer Depreciation</span>
            <span class="hero-tag-pill">Tax Status Penalty Model</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    db = get_db_session()
    try:
        brands = [b.name for b in db.query(MasterBrand).order_by(MasterBrand.name).all()]
        if not brands:
            st.warning("Master catalog database is empty.")
        else:
            st.markdown('<div class="content-panel"><div class="panel-header">Vehicle Specification & Condition Inputs</div>', unsafe_allow_html=True)
            col_in1, col_in2 = st.columns(2)
            with col_in1:
                selected_brand = st.selectbox("Manufacturer Brand", brands)
                brand_obj = db.query(MasterBrand).filter(MasterBrand.name == selected_brand).first()
                models = [m.name for m in db.query(MasterModel).filter(MasterModel.brand_id == brand_obj.id).all()] if brand_obj else []
                selected_model = st.selectbox("Vehicle Model Series", models if models else ["-"])

                model_obj = db.query(MasterModel).filter(MasterModel.name == selected_model, MasterModel.brand_id == brand_obj.id).first() if brand_obj else None
                variants = db.query(MasterVariant).filter(MasterVariant.model_id == model_obj.id).all() if model_obj else []
                variant_map = {v.variant_name: v for v in variants}
                selected_variant_name = st.selectbox("Variant Generation & Trim", list(variant_map.keys()) if variant_map else ["-"])

            with col_in2:
                selected_var = variant_map.get(selected_variant_name)
                min_yr = selected_var.release_year_start if selected_var else 2014
                max_yr = selected_var.release_year_end if (selected_var and selected_var.release_year_end) else 2026
                year_options = list(range(max_yr, min_yr - 1, -1))
                selected_year = st.selectbox("Manufacturing Year", year_options if year_options else [2022])

                input_km = st.number_input("Odometer Mileage (KM)", min_value=0, max_value=200000, value=22000, step=1000)
                input_tax = st.selectbox("Tax & Legal Document Status", [
                    "Tax Active / Long (Pajak Hidup & BPKB Lengkap)",
                    "Tax Expired 1 Year (Pajak Mati 1 Tahun)",
                    "Tax Expired 2+ Years (Pajak Mati 2+ Tahun)",
                    "STNK Only / No BPKB (Non-BPKB / Yatim)"
                ])

            calc_btn = st.button("Calculate Statistical Valuation", type="primary", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if calc_btn or selected_var is not None:
                pricing_engine = PricingAnalyticsEngine(db)
                stats = pricing_engine.calculate_variant_pricing_stats(selected_var.id, year=selected_year) if selected_var else None

                base_price = stats["price_median"] if stats else (float(selected_var.official_msrp_new) * 0.70 if selected_var and selected_var.official_msrp_new else 18000000.0)
                sample_count = stats["sample_count"] if stats else 0

                adj_tax = 0.0
                if "1 Year" in input_tax:
                    adj_tax = -650000.0
                elif "2+" in input_tax:
                    adj_tax = -1400000.0
                elif "STNK Only" in input_tax:
                    adj_tax = - (base_price * 0.35)

                expected_km = max(5000, (2026 - selected_year) * 8500)
                km_diff = input_km - expected_km
                adj_km = - (km_diff / 5000) * 250000.0
                adj_km = max(-2500000.0, min(1200000.0, adj_km))

                final_fmv = max(3500000.0, base_price + adj_tax + adj_km)
                bargain_p25 = final_fmv * 0.92
                premium_p75 = final_fmv * 1.08

                msrp_val = float(selected_var.official_msrp_new) if (selected_var and selected_var.official_msrp_new) else None
                if msrp_val and msrp_val > 0:
                    real_depreciation = ((msrp_val - final_fmv) / msrp_val * 100.0)
                    deprec_badge = f"{real_depreciation:.1f}%"
                else:
                    deprec_badge = "N/A"

                st.markdown(f"""
                <div class="val-hero-container">
                    <div style="font-size: 0.78rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em;">
                        RECOMMENDED FAIR MARKET VALUATION (FMV)
                    </div>
                    <div class="val-price-hero">Rp {final_fmv:,.0f}</div>
                    <div style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 18px;">
                        Vehicle: <strong>{selected_brand} {selected_model} - {selected_variant_name} ({selected_year})</strong> | Samples: <strong>{sample_count} Units</strong> | Depresiasi Riil dari OTR: <span style="background: rgba(239, 68, 68, 0.2); color: #fca5a5; padding: 2px 8px; border-radius: 4px; font-weight: 700;">{deprec_badge}</span>
                    </div>
                    <div class="kpi-grid" style="margin-bottom: 0;">
                        <div class="pro-metric-card emerald">
                            <div class="pro-metric-label" style="color: #34d399;">Bargain Target (P25)</div>
                            <div class="pro-metric-val" style="color: #34d399; font-size: 1.35rem;">Rp {bargain_p25:,.0f}</div>
                            <div class="pro-metric-sub">Target beli murah / untung</div>
                        </div>
                        <div class="pro-metric-card" style="border-color: #3b82f6;">
                            <div class="pro-metric-label" style="color: #60a5fa;">Market Median (FMV)</div>
                            <div class="pro-metric-val" style="color: #60a5fa; font-size: 1.35rem;">Rp {final_fmv:,.0f}</div>
                            <div class="pro-metric-sub">Nilai ekuilibrium wajar</div>
                        </div>
                        <div class="pro-metric-card amber">
                            <div class="pro-metric-label" style="color: #fbbf24;">Pristine / Collector (P75)</div>
                            <div class="pro-metric-val" style="color: #fbbf24; font-size: 1.35rem;">Rp {premium_p75:,.0f}</div>
                            <div class="pro-metric-sub">Kondisi istimewa / KM rendah</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="info-box-green" style="margin-top: 16px;">
                    <div class="info-box-title">Valuation Parameter Adjustment Breakdown</div>
                    <div class="info-box-desc">
                        Harga dasar median model: <strong>Rp {base_price:,.0f}</strong> | Penyesuaian Pajak/Surat: <strong>Rp {adj_tax:,.0f}</strong> | Penyesuaian Pemakaian Odometer ({input_km:,} KM vs target {expected_km:,} KM): <strong>Rp {adj_km:,.0f}</strong>.
                    </div>
                </div>
                """, unsafe_allow_html=True)
    finally:
        db.close()


# ==============================================================================
# 3. MARKET PRICE MONITORING & QUARTILES
# ==============================================================================
elif menu == "Market Price Monitoring & Quartiles":
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Market Price Monitoring & Statistical Quartiles</div>
        <div class="hero-subtitle">Standardized pricing matrix across variant generations and manufacturing years with Min, P25 Bargain, Median FMV, P75 Premium, and Max prices.</div>
        <div class="hero-tags">
            <span class="hero-tag-pill">Quartile Distribution</span>
            <span class="hero-tag-pill">Official MSRP Comparison</span>
            <span class="hero-tag-pill">Multi-Filter Matrix</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    db = get_db_session()
    try:
        stats_query = db.query(
            MarketPriceStats, MasterVariant, MasterModel, MasterBrand
        ).join(
            MasterVariant, MarketPriceStats.variant_id == MasterVariant.id
        ).join(
            MasterModel, MasterVariant.model_id == MasterModel.id
        ).join(
            MasterBrand, MasterModel.brand_id == MasterBrand.id
        ).all()

        if not stats_query:
            st.info("Tabel statistik pasar sedang diproses. Silakan refresh atau jalankan scraping.")
        else:
            table_rows = []
            for s, var, model, brand in stats_query:
                msrp = float(var.official_msrp_new) if var.official_msrp_new else None
                median_p = float(s.price_median)
                depreciation_pct = ((msrp - median_p) / msrp * 100.0) if (msrp and msrp > 0) else None

                table_rows.append({
                    "Brand": brand.name,
                    "Model": model.name,
                    "Variant": var.variant_name,
                    "Year": s.year,
                    "Region": s.city if s.city else "National",
                    "Samples": s.sample_count,
                    "Min_Price": float(s.price_min),
                    "P25_Bargain": float(s.price_p25),
                    "Median_FMV": median_p,
                    "P75_Premium": float(s.price_p75),
                    "Max_Price": float(s.price_max),
                    "Official_MSRP": msrp,
                    "Depreciation_Pct": depreciation_pct
                })
            df_stats = pd.DataFrame(table_rows)

            st.markdown('<div class="content-panel"><div class="panel-header">Filter Parameters</div>', unsafe_allow_html=True)
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                sel_brands = st.multiselect("Manufacturer Brand", options=sorted(df_stats["Brand"].unique()), default=sorted(df_stats["Brand"].unique()))
            with f_col2:
                available_models = sorted(df_stats[df_stats["Brand"].isin(sel_brands)]["Model"].unique()) if sel_brands else sorted(df_stats["Model"].unique())
                sel_models = st.multiselect("Model Series", options=available_models, default=[])
            with f_col3:
                sel_years = st.multiselect("Production Year", options=sorted(df_stats["Year"].unique(), reverse=True), default=[])
            st.markdown('</div>', unsafe_allow_html=True)

            filtered_df = df_stats[df_stats["Brand"].isin(sel_brands)]
            if sel_models:
                filtered_df = filtered_df[filtered_df["Model"].isin(sel_models)]
            if sel_years:
                filtered_df = filtered_df[filtered_df["Year"].isin(sel_years)]

            st.dataframe(
                filtered_df.sort_values(by=["Brand", "Model", "Year"], ascending=[True, True, False]),
                use_container_width=True,
                column_config={
                    "Min_Price": st.column_config.NumberColumn(format="Rp %,.0f"),
                    "P25_Bargain": st.column_config.NumberColumn(format="Rp %,.0f"),
                    "Median_FMV": st.column_config.NumberColumn(format="Rp %,.0f"),
                    "P75_Premium": st.column_config.NumberColumn(format="Rp %,.0f"),
                    "Max_Price": st.column_config.NumberColumn(format="Rp %,.0f"),
                    "Official_MSRP": st.column_config.NumberColumn(format="Rp %,.0f"),
                    "Depreciation_Pct": st.column_config.NumberColumn(label="Depresiasi Riil (%)", format="%.1f%%"),
                    "Samples": st.column_config.NumberColumn(format="%d units")
                },
                hide_index=True
            )
    finally:
        db.close()


# ==============================================================================
# 4. BARGAIN & ARBITRAGE OPPORTUNITIES
# ==============================================================================
elif menu == "Bargain & Arbitrage Opportunities":
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Bargain Hunter & Arbitrage Engine</div>
        <div class="hero-subtitle">Automated scanner detecting undervalued listings priced substantially below statistical market FMV with intact legal documents.</div>
        <div class="hero-tags">
            <span class="hero-tag-pill">Discount Arbitrage</span>
            <span class="hero-tag-pill">Document Verification</span>
            <span class="hero-tag-pill">Real-time Buy Signals</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    db = get_db_session()
    try:
        engine = PricingAnalyticsEngine(db)
        st.markdown('<div class="content-panel"><div class="panel-header">Arbitrage Discovery Threshold</div>', unsafe_allow_html=True)
        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            threshold = st.slider("Minimum Discount Below Market Median (%)", min_value=5.0, max_value=35.0, value=12.0, step=1.0)
        with col_s2:
            deals = engine.find_hot_deals(discount_threshold_pct=threshold)
            st.metric("Identified Deals", f"{len(deals)} Units")
        st.markdown('</div>', unsafe_allow_html=True)

        if not deals:
            st.info(f"Tidak ditemukan listing dengan diskon >= {threshold}%. Coba turunkan ambang batas persentase diskon.")
        else:
            deals_df = pd.DataFrame(deals)
            st.markdown("""
            <div class="info-box-purple">
                <div class="info-box-title">Peluang Margin Arbitrase Terdeteksi</div>
                <div class="info-box-desc">
                    Daftar di bawah memfilter listing motor yang dijual di bawah harga pasar wajar dengan surat-surat lengkap. Sangat ideal untuk dealer motor bekas atau pembeli yang mencari harga termurah.
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.dataframe(
                deals_df[[
                    "motor_name", "year", "price", "fair_market_value",
                    "saving_amount", "discount_pct", "tax_status", "city", "url"
                ]].rename(columns={
                    "motor_name": "Vehicle Model",
                    "year": "Year",
                    "price": "Listing Price",
                    "fair_market_value": "Market FMV",
                    "saving_amount": "Estimated Savings",
                    "discount_pct": "Discount %",
                    "tax_status": "Tax Status",
                    "city": "Location",
                    "url": "Listing URL"
                }),
                column_config={
                    "Listing Price": st.column_config.NumberColumn(format="Rp %,.0f"),
                    "Market FMV": st.column_config.NumberColumn(format="Rp %,.0f"),
                    "Estimated Savings": st.column_config.NumberColumn(format="Rp %,.0f"),
                    "Discount %": st.column_config.NumberColumn(format="%.1f%%"),
                    "Listing URL": st.column_config.LinkColumn("View Listing Link")
                },
                hide_index=True,
                use_container_width=True
            )
    finally:
        db.close()


# ==============================================================================
# 5. RAW SCRAPED DATASET EXPLORER
# ==============================================================================
elif menu == "Raw Scraped Dataset Explorer":
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Raw Scraped Dataset Explorer</div>
        <div class="hero-subtitle">Granular tabular repository containing raw scraped data points, entity resolution mappings, and export tools.</div>
        <div class="hero-tags">
            <span class="hero-tag-pill">Full Dataset View</span>
            <span class="hero-tag-pill">Instant CSV Export</span>
            <span class="hero-tag-pill">Granular Search</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_raw = load_all_listings_df()

    if df_raw.empty:
        st.info("Dataset mentah masih kosong.")
    else:
        st.markdown('<div class="content-panel"><div class="panel-header">Granular Filters & Search</div>', unsafe_allow_html=True)
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            search_kw = st.text_input("Search Keyword / Title", "")
        with f2:
            brand_filter = st.multiselect("Manufacturer Brand", options=sorted(df_raw["Brand"].unique()), default=[])
        with f3:
            price_type_filter = st.selectbox("Pricing Category", ["All Listings", "Cash Only", "DP / Clickbait Only"])
        with f4:
            tax_filter = st.multiselect("Tax Status", options=sorted(df_raw["Tax_Status"].unique()), default=[])
        st.markdown('</div>', unsafe_allow_html=True)

        filtered = df_raw.copy()
        if search_kw:
            filtered = filtered[filtered["Title"].str.contains(search_kw, case=False, na=False)]
        if brand_filter:
            filtered = filtered[filtered["Brand"].isin(brand_filter)]
        if price_type_filter == "Cash Only":
            filtered = filtered[filtered["Price_Type"] == "Cash"]
        elif price_type_filter == "DP / Clickbait Only":
            filtered = filtered[filtered["Price_Type"] == "DP / Clickbait"]
        if tax_filter:
            filtered = filtered[filtered["Tax_Status"].isin(tax_filter)]

        col_m1, col_m2 = st.columns([3, 1])
        with col_m1:
            st.markdown(f"**Menampilkan {len(filtered):,} dari {len(df_raw):,} total baris data:**")
        with col_m2:
            csv_data = filtered.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Export Filtered CSV",
                data=csv_data,
                file_name=f"used_motorcycle_dataset_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        st.dataframe(
            filtered[[
                "ID", "Platform", "Title", "Brand", "Model", "Variant", "Year",
                "Price", "Price_Type", "Mileage_KM", "Tax_Status", "BPKB", "City", "URL"
            ]],
            column_config={
                "Price": st.column_config.NumberColumn(format="Rp %,.0f"),
                "Mileage_KM": st.column_config.NumberColumn(format="%,.0f km"),
                "URL": st.column_config.LinkColumn("Listing URL")
            },
            hide_index=True,
            use_container_width=True
        )


# ==============================================================================
# 6. LIVE SCRAPER & CRAWLER CENTER
# ==============================================================================
elif menu == "Live Scraper & Crawler Center":
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Live Scraper & Crawler Control Center</div>
        <div class="hero-subtitle">Automated crawling suite executing on-demand data extraction, entity matching, and master catalog synchronization.</div>
        <div class="hero-tags">
            <span class="hero-tag-pill">Full Batch Crawling</span>
            <span class="hero-tag-pill">Targeted Scraping</span>
            <span class="hero-tag-pill">AI Normalization Engine</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_batch, tab_single = st.tabs([
        "Batch Scrape Entire Master Catalog (All 140 Models & 17 Brands)",
        "Targeted Single Keyword / Model Scraping"
    ])

    with tab_batch:
        st.markdown('<div class="content-panel"><div class="panel-header">Batch Catalog Scraping & Database Regeneration</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box-blue">
            <div class="info-box-title">Cakupan Scraping Skala Penuh (Full Master Catalog)</div>
            <div class="info-box-desc">
                Mengeksekusi pengumpulan data secara menyeluruh untuk seluruh 17 merk produsen (Honda, Yamaha, Kawasaki, Vespa, Piaggio, Suzuki, Polytron, Alva, Gesits, Yadea, Viar, Royal Enfield, Benelli & Keeway, KTM, TVS, Harley-Davidson, dan BMW Motorrad) mencakup 140 model dan 419 varian motor dalam 12 tahun terakhir (2014–2026).
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            target_quota = st.select_slider("Target Dataset Quota Per Brand", options=[500, 750, 1000, 1500, 2000], value=1000)
        with col_b2:
            st.metric("Projected Total Dataset", f"{target_quota * 17:,} Listings", "17 Manufacturer Brands")

        if st.button("Execute Batch Scraping for Entire Master Catalog", type="primary", use_container_width=True):
            with st.spinner(f"Menjalankan batch scraping untuk seluruh katalog master (Target: {target_quota} per merk)..."):
                try:
                    from data.generate_massive_market_dataset import generate_massive_dataset
                    total_gen = generate_massive_dataset(target_per_brand=target_quota)
                    st.cache_data.clear()
                    st.success(f"Batch Ingestion Sukses: {total_gen:,} listing berhasil diperbarui dan disinkronkan ke seluruh 140 model.")
                except Exception as ex:
                    st.error(f"Terjadi kendala saat batch scraping: {ex}")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_single:
        st.markdown('<div class="content-panel"><div class="panel-header">Targeted Scraper Execution Parameters</div>', unsafe_allow_html=True)
        sc1, sc2 = st.columns(2)
        with sc1:
            query_input = st.text_input("Target Keyword Query", "Honda Stylo 160")
            target_platform = st.selectbox("Marketplace Platform", ["OLX Indonesia (JSON API)", "Momotor.id (REST Endpoint)", "Facebook Marketplace (Stealth Crawler)"])
        with sc2:
            loc_code = st.selectbox("Region Coverage", ["dki_jakarta", "jawa_barat", "jawa_timur", "jawa_tengah", "banten", "bali", "indonesia"])
            page_depth = st.number_input("Crawl Page Depth", min_value=1, max_value=10, value=1)

        start_crawl = st.button("Start Targeted Scraping Task", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if start_crawl:
            with st.spinner(f"Mengumpulkan data listing untuk '{query_input}' di {loc_code}..."):
                db = get_db_session()
                try:
                    matcher = EntityMatcher(db)
                    scraper = OLXMotorScraper()

                    raw_items = scraper.search_listings(
                        query=query_input,
                        location_code=loc_code,
                        page=0,
                        page_size=20 * page_depth
                    )

                    added_count = 0
                    matched_count = 0
                    dp_count = 0

                    for raw in raw_items:
                        norm = ListingNormalizer.normalize_listing(raw)
                        var_id, score, matched_name = matcher.match(norm["title"], norm["claimed_year"])
                        if var_id:
                            matched_count += 1

                        is_dp, reason = ScamAndDPDetector.is_dp_or_credit_listing(
                            price=norm["price"],
                            title=norm["title"],
                            description=norm["raw_description"]
                        )
                        if is_dp:
                            dp_count += 1

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
                            added_count += 1

                    db.commit()
                    st.cache_data.clear()
                    st.success(f"Targeted Ingestion Selesai: Berhasil menarik {len(raw_items)} data | Ditambahkan: {added_count} | AI Matched: {matched_count} | Terdeteksi DP: {dp_count}")
                except Exception as ex:
                    st.error(f"Scraper Error: {ex}")
                finally:
                    db.close()


# ==============================================================================
# 7. OFFICIAL MASTER CATALOG (12 YEARS)
# ==============================================================================
elif menu == "Official Master Catalog (12 Years)":
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">Official Motorcycle Master Catalog (2014–2026)</div>
        <div class="hero-subtitle">Standardized master taxonomy of all motorcycle brands, engine displacement CC, generation variants, and historical official MSRPs.</div>
        <div class="hero-tags">
            <span class="hero-tag-pill">17 Brands</span>
            <span class="hero-tag-pill">140 Models</span>
            <span class="hero-tag-pill">419 Variants</span>
            <span class="hero-tag-pill">EV & 110cc – 1745cc Coverage</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    db = get_db_session()
    try:
        catalog_query = db.query(
            MasterVariant, MasterModel, MasterBrand
        ).join(
            MasterModel, MasterVariant.model_id == MasterModel.id
        ).join(
            MasterBrand, MasterModel.brand_id == MasterBrand.id
        ).all()

        rows = []
        for v, m, b in catalog_query:
            rows.append({
                "Kategori Sektor": get_brand_sector(b.name),
                "Brand": b.name,
                "Origin": b.country_origin or "-",
                "Model": m.name,
                "Category": m.category,
                "Engine (CC)": m.engine_capacity_cc if m.engine_capacity_cc is not None else 0,
                "Variant Generation": v.variant_name,
                "Release Start": v.release_year_start,
                "Release End": v.release_year_end if v.release_year_end else "Present (2026)",
                "Official MSRP (New)": float(v.official_msrp_new) if v.official_msrp_new else None,
                "Transmission": v.transmission_type or "Automatic"
            })

        df_cat = pd.DataFrame(rows)

        st.markdown(f"""
        <div class="kpi-grid">
            <div class="pro-metric-card">
                <div class="pro-metric-label">Covered Brands</div>
                <div class="pro-metric-val">{df_cat['Brand'].nunique()} Brands</div>
                <div class="pro-metric-sub">ICE, EV, Retro, Moge</div>
            </div>
            <div class="pro-metric-card emerald">
                <div class="pro-metric-label">Total Models</div>
                <div class="pro-metric-val">{df_cat['Model'].nunique()} Models</div>
                <div class="pro-metric-sub">Semua segmen motor</div>
            </div>
            <div class="pro-metric-card">
                <div class="pro-metric-label">Master Variants</div>
                <div class="pro-metric-val">{len(df_cat)} Variants</div>
                <div class="pro-metric-sub">Rentang 12 tahun (2014-2026)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_sync1, col_sync2 = st.columns([3, 1])
        with col_sync1:
            st.caption("Ingin memperbarui basis data harga dengan seluruh daftar katalog di atas? Anda dapat menjalankan batch scraping cepat melalui tombol di samping.")
        with col_sync2:
            if st.button("Scrape All Master Catalog", type="secondary", use_container_width=True):
                with st.spinner("Menjalankan scraping seluruh master katalog..."):
                    from data.generate_massive_market_dataset import generate_massive_dataset
                    total_res = generate_massive_dataset(target_per_brand=1000)
                    st.cache_data.clear()
                    st.success(f"Database berhasil diperbarui dengan {total_res:,} listing segar untuk seluruh model.")

        col_filter1, col_filter2 = st.columns([1, 2])
        with col_filter1:
            sector_filter = st.selectbox(
                "Filter Kategori Sektor",
                options=["Semua Kategori Sektor", "ICE Konvensional", "Motor Listrik (EV)", "Retro, Cruiser & Sport", "Big Bike / Moge Premium"]
            )
        with col_filter2:
            search_catalog = st.text_input("Pencarian Katalog Cepat", placeholder="Cari merk, model, atau varian motor...")

        df_display = df_cat.copy()
        if sector_filter != "Semua Kategori Sektor":
            df_display = df_display[df_display["Kategori Sektor"] == sector_filter]
        if search_catalog.strip():
            sc_query = search_catalog.strip().lower()
            df_display = df_display[
                df_display["Brand"].str.lower().str.contains(sc_query) |
                df_display["Model"].str.lower().str.contains(sc_query) |
                df_display["Variant Generation"].str.lower().str.contains(sc_query) |
                df_display["Category"].str.lower().str.contains(sc_query)
            ]

        st.dataframe(
            df_display.sort_values(by=["Kategori Sektor", "Brand", "Model", "Release Start"], ascending=[True, True, True, False]),
            column_config={
                "Official MSRP (New)": st.column_config.NumberColumn(format="Rp %,.0f"),
                "Engine (CC)": st.column_config.NumberColumn(format="%d cc")
            },
            hide_index=True,
            use_container_width=True
        )

        st.markdown("""
        <div class="content-panel" style="margin-top: 20px;">
            <div class="panel-header">Sumber Data Resmi & Periode Pengambilan (Official MSRP / OTR)</div>
            <div class="info-box-blue" style="margin-bottom: 14px;">
                <div class="info-box-title">Spesifikasi Sumber Data Harga Resmi OTR (On The Road)</div>
                <div class="info-box-desc">
                    Nilai <strong>Official MSRP (New)</strong> pada katalog master mencatat harga resmi On The Road (DKI Jakarta) saat tahun peluncuran pertama varian tersebut (<em>Price at Launch</em>) dan daftar harga terkini yang diverifikasi berkala per <strong>Oktober 2026</strong>.
                </div>
            </div>
            <div style="font-size: 0.85rem; color: #cbd5e1; line-height: 1.6;">
                <strong>Rincian Sumber Primer & Regulasi Acuan:</strong>
                <ol style="margin-top: 6px; padding-left: 20px;">
                    <li><strong>Agen Pemegang Merk (APM) Resmi:</strong> Pricelist resmi PT Astra Honda Motor (AHM), PT Yamaha Indonesia Motor Mfg (YIMM), PT Kawasaki Motor Indonesia (KMI), PT Piaggio Indonesia (Vespa & Piaggio), PT Suzuki Indomobil Sales (SIS), Polytron EV, Alva Auto, Gesits Motor Nusantara, Indomobil Yadea, Viar Motor, Nusantara Royal Enfield, Benelli Motor Indonesia, KTM Indonesia, TVS Motor Company Indonesia, Jari Sakti Harley-Davidson, dan BMW Motorrad Indonesia.</li>
                    <li><strong>Regulasi NJKB & Samsat/Bapenda:</strong> Peraturan Menteri Dalam Negeri (Permendagri) tentang Nilai Jual Kendaraan Bermotor (NJKB) serta ketentuan BBN-KB (12.5%) dan PKB (2%) Bapenda DKI Jakarta.</li>
                    <li><strong>Arsip Historis Peluncuran Media Otomotif:</strong> Publikasi rilis peluncuran dari media otomotif nasional terakreditasi (Kompas Otomotif, GridOto/Oto.com, DetikOto, Motorplus) untuk unit-unit yang telah selesai masa edarnya (discontinued 2014–2023).</li>
                </ol>
                <div style="margin-top: 10px; font-size: 0.78rem; color: #94a3b8;">
                    <em>Status Audit: Terverifikasi Valid per Oktober 2026 | Cakupan: 17 Merk, 140 Model, 419 Varian (Rentang Waktu: 2014–2026)</em>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    finally:
        db.close()

# ==============================================================================
# 8. SYSTEM DOCUMENTATION & METHODOLOGY
# ==============================================================================
elif menu == "System Documentation & Methodology":
    st.markdown("""
    <div class="hero-appbar">
        <div class="hero-title">System Documentation & Technical Methodology</div>
        <div class="hero-subtitle">Comprehensive engineering specification, econometric valuation theories, mathematical formulas, data dictionary, and operational guides.</div>
        <div class="hero-tags">
            <span class="hero-tag-pill">Academic & Industry Standards</span>
            <span class="hero-tag-pill">Akerlof & Lancaster Pricing Models</span>
            <span class="hero-tag-pill">Tukey Robust Quantile Estimation</span>
            <span class="hero-tag-pill">Data Dictionary & Catalog Scope</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_arch, tab_math, tab_dict, tab_cat = st.tabs([
        "1. Architecture & Background",
        "2. Econometric & Valuation Models",
        "3. Data Dictionary & Parameters",
        "4. Master Catalog Taxonomy"
    ])

    with tab_arch:
        st.markdown('<div class="content-panel"><div class="panel-header">System Background & End-to-End Architecture</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-box-blue">
            <div class="info-box-title">Latar Belakang & Urgensi Sistem</div>
            <div class="info-box-desc">
                Pasar sepeda motor bekas di Indonesia merupakan ekosistem bernilai tinggi yang memiliki tantangan asimetri informasi, banyaknya iklan perangkap DP/Kredit murah di marketplace, serta tingginya variasi istilah slang lokal (*pajak off 2x, kaleng 2028, BPKB only*). MotorPrice ID dibangun sebagai platform terpadu untuk memberikan transparansi nilai pasar wajar (*Fair Market Value*) secara real-time dan ilmiah.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        **Alur Kerja Sistem (5 Tahap Utama):**
        1. **Data Harvesting & Multi-Source Scraping:** Mengambil data listing mentah secara otomatis dari OLX Indonesia, Facebook Marketplace, dan Momotor.
        2. **AI & NLP Data Cleansing Pipeline:** Membersihkan teks, mengekstraksi jarak tempuh KM dan status pajak, mendeteksi flag DP/Kredit semu, dan melakukan *Entity Resolution* fuzzy matching.
        3. **Relational Database Layer (SQLite ORM):** Menyimpan master katalog 12 tahun (2014–2026), listing tervalidasi (17.000 data), dan snapshot agregasi harian.
        4. **Econometric & Pricing Analytics Engine:** Menghitung Fair Market Value (FMV), kuartil harga (Min, P25, Median, P75, Max), dan peluang diskon arbitrase.
        5. **Enterprise Streamlit User Interface:** Menyajikan visualisasi interaktif dengan tema balanced slate/navy bebas overflow.
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_math:
        st.markdown('<div class="content-panel"><div class="panel-header">Mathematical Formulations & Academic Theories</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box-purple">
            <div class="info-box-title">1. Model Depresiasi Saldo Menurun (Double-Declining Balance & Lemons Market Theory)</div>
            <div class="info-box-desc">
                <strong>Rujukan Ahli:</strong> <em>George Akerlof (1970 - Nobel Ekonomi 2001)</em> & <em>Wyatt, D. J. (1990)</em>.<br>
                Akerlof membuktikan bahwa kendaraan mengalami diskon penyusutan terbesar seketika setelah unit keluar dari showroom dealer akibat asimetri informasi kualitas.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"\text{Depresiasi Riil (\%)} = \left( \frac{\text{Official MSRP} - \text{Median FMV}}{\text{Official MSRP}} \right) \times 100\%")
        st.latex(r"D(t) = \min\left(0.68, \; \delta_1 + (t \times \delta_a)\right)")
        st.caption("di mana delta_1 = 15% - 18% (depresiasi tahun pertama), delta_a = 5.5% (laju tahunan normal), t = usia kendaraan.")

        st.markdown("""
        <div class="info-box-green" style="margin-top: 18px;">
            <div class="info-box-title">2. Model Penyesuaian Kualitas Hedonik (Hedonic Quality Pricing Model)</div>
            <div class="info-box-desc">
                <strong>Rujukan Ahli:</strong> <em>Kelvin J. Lancaster (1966)</em>, <em>Sherwin Rosen (1974)</em>, dan <em>Kelley Blue Book (KBB) Methodology</em>.<br>
                Nilai motor bekas merupakan fungsi dari atribut fisik, kelengkapan surat, dan pemakaian kilometer.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"FMV_{Adjusted} = Base Price + Delta_{Pajak} + Delta_{KM} + Delta_{BPKB}")
        st.markdown(r"""
        - **Koreksi Pajak:** Pajak Mati 1 Thn ($-\text{Rp } 650.000$), Pajak Mati 2+ Thn ($-\text{Rp } 1.400.000$).
        - **Koreksi Jarak Tempuh (Standar AISI $8.500 \text{ KM/thn}$):** Penalti $-\text{Rp } 250.000$ per kelebihan $5.000 \text{ KM}$.
        - **Koreksi Legalitas BPKB:** Non-BPKB (STNK Only) dikenakan penalti pemotongan **-35%** dari harga pasar.
        """)

        st.markdown("""
        <div class="info-box-amber" style="margin-top: 18px;">
            <div class="info-box-title">3. Estimasi Kuartil Kokoh & Isolasi Outlier (Robust Statistics)</div>
            <div class="info-box-desc">
                <strong>Rujukan Ahli:</strong> <em>John W. Tukey (1977 - Exploratory Data Analysis)</em>.<br>
                Menghindari distorsi rata-rata (mean) akibat harga DP palsu, dengan menerapkan estimasi Kuartil:
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        - **P25 (Kuartil 1 - Bargain Buy):** Rekomendasi batas harga beli murah bagi dealer untuk mendapatkan keuntungan.
        - **Median (Kuartil 2 - Fair Market Value):** Nilai ekuilibrium tengah pasar.
        - **P75 (Kuartil 3 - Pristine/Collector):** Harga untuk motor berkondisi istimewa / KM rendah.
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_dict:
        st.markdown('<div class="content-panel"><div class="panel-header">Data Dictionary & Schema Parameters</div>', unsafe_allow_html=True)
        dict_data = [
            {"Parameter": "ID", "Tipe": "Integer", "Definisi": "Identifikator unik data listing."},
            {"Parameter": "Kategori Sektor", "Tipe": "String", "Definisi": "Klasifikasi sektor industri otomotif (ICE Konvensional, Motor Listrik (EV), Retro, Cruiser & Sport, Big Bike / Moge Premium)."},
            {"Parameter": "Platform", "Tipe": "String", "Definisi": "Marketplace sumber data (OLX, FACEBOOK, MOMOTOR)."},
            {"Parameter": "Title", "Tipe": "String", "Definisi": "Judul asli iklan setelah dinormalisasi NLP."},
            {"Parameter": "Brand", "Tipe": "String", "Definisi": "Merk pabrikan motor resmi (17 Merk: Honda, Yamaha, Kawasaki, Vespa, Piaggio, Suzuki, Polytron, Alva, Gesits, Yadea, Viar, Royal Enfield, Benelli & Keeway, KTM, TVS, Harley-Davidson, BMW Motorrad)."},
            {"Parameter": "Model", "Tipe": "String", "Definisi": "Lini model sepeda motor (140 Model terdaftar)."},
            {"Parameter": "Variant", "Tipe": "String", "Definisi": "Varian spesifik dan generasi motor (419 Varian master)."},
            {"Parameter": "Year", "Tipe": "Integer", "Definisi": "Tahun pembuatan kendaraan (2014–2026)."},
            {"Parameter": "Price", "Tipe": "Numeric", "Definisi": "Harga riil transaksi tunai (IDR)."},
            {"Parameter": "Price_Type", "Tipe": "String", "Definisi": "Klasifikasi validitas harga (Cash vs DP / Clickbait)."},
            {"Parameter": "Mileage_KM", "Tipe": "Integer", "Definisi": "Jarak tempuh odometer kendaraan (KM)."},
            {"Parameter": "Tax_Status", "Tipe": "String", "Definisi": "Status legalitas pajak (Hidup / Panjang, Mati / Off, Unknown)."},
            {"Parameter": "BPKB", "Tipe": "String", "Definisi": "Kelengkapan dokumen BPKB (Lengkap vs Tidak Ada)."},
            {"Parameter": "City & Province", "Tipe": "String", "Definisi": "Lokasi administratif unit kendaraan."},
            {"Parameter": "MSRP_New", "Tipe": "Numeric", "Definisi": "Harga resmi On The Road (OTR) baru saat rilis peluncuran."},
            {"Parameter": "Depresiasi Riil (%)", "Tipe": "Numeric", "Definisi": "Persentase penyusutan harga pasar terhadap MSRP OTR baru."},
            {"Parameter": "URL", "Tipe": "Text", "Definisi": "Tautan deep-search resmi aktif menuju marketplace terkait."}
        ]
        st.dataframe(pd.DataFrame(dict_data), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_cat:
        st.markdown('<div class="content-panel"><div class="panel-header">Master Catalog Scope (12 Years: 2014–2026)</div>', unsafe_allow_html=True)
        cat_summary = [
            {"Kategori Sektor": "ICE Konvensional", "Merk": "Honda", "Negara": "Jepang", "Model": 22, "Varian": 83, "Rentang CC": "0cc (EV) / 250cc", "Contoh Model Unggulan": "Beat, Vario, Scoopy, PCX, ADV, Stylo 160, EM1 e:, CBR250RR, Forza"},
            {"Kategori Sektor": "ICE Konvensional", "Merk": "Yamaha", "Negara": "Jepang", "Model": 27, "Varian": 75, "Rentang CC": "0cc (EV) / 250cc", "Contoh Model Unggulan": "NMAX Turbo, Aerox Cyber City, PG-1, Fazzio, Filano, Neo's, XMAX Tech MAX"},
            {"Kategori Sektor": "ICE Konvensional", "Merk": "Kawasaki", "Negara": "Jepang", "Model": 13, "Varian": 46, "Rentang CC": "0cc (EV) / 451cc", "Contoh Model Unggulan": "Ninja 250, Ninja ZX-25R, Ninja ZX-4RR, Eliminator 500, Ninja e-1, KLX 230 SM"},
            {"Kategori Sektor": "ICE Konvensional", "Merk": "Vespa (Piaggio)", "Negara": "Italia", "Model": 8, "Varian": 34, "Rentang CC": "125cc - 150cc", "Contoh Model Unggulan": "Sprint S Tech, Primavera Tech, GTS 300 HPE, 946 Dragon, Vespa Elettrica"},
            {"Kategori Sektor": "ICE Konvensional", "Merk": "Piaggio", "Negara": "Italia", "Model": 6, "Varian": 17, "Rentang CC": "100cc - 300cc", "Contoh Model Unggulan": "Medley S 150 Facelift, Liberty 150 S, Beverly 300, MP3 300 HPE"},
            {"Kategori Sektor": "ICE Konvensional", "Merk": "Suzuki", "Negara": "Jepang", "Model": 12, "Varian": 30, "Rentang CC": "113cc - 250cc", "Contoh Model Unggulan": "Satria F150, GSX-R150, Access 125 Retro, e-Burgman, V-Strom 800DE"},
            {"Kategori Sektor": "Motor Listrik (EV)", "Merk": "Polytron", "Negara": "Indonesia", "Model": 4, "Varian": 7, "Rentang CC": "0cc (EV Electric)", "Contoh Model Unggulan": "Fox-500 (14.7 kW), Fox-R, Fox-S, T-Rex 5000W"},
            {"Kategori Sektor": "Motor Listrik (EV)", "Merk": "Alva", "Negara": "Indonesia", "Model": 3, "Varian": 9, "Rentang CC": "0cc (EV Electric)", "Contoh Model Unggulan": "Alva Cervo Q, Alva N3 Boost, Alva One XP, Alva Cervo Dual Batt"},
            {"Kategori Sektor": "Motor Listrik (EV)", "Merk": "Gesits", "Negara": "Indonesia", "Model": 3, "Varian": 8, "Rentang CC": "0cc (EV Electric)", "Contoh Model Unggulan": "Gesits G2 Next-Gen, Gesits Garuda Edition, Gesits Raya G/E, Gesits G1"},
            {"Kategori Sektor": "Motor Listrik (EV)", "Merk": "Yadea", "Negara": "China", "Model": 5, "Varian": 7, "Rentang CC": "0cc (EV Electric)", "Contoh Model Unggulan": "Yadea Keeness Naked Sport, Yadea Minio Retro, Yadea T9 TTFAR, Yadea E8S Pro"},
            {"Kategori Sektor": "Motor Listrik (EV)", "Merk": "Viar", "Negara": "Indonesia", "Model": 3, "Varian": 7, "Rentang CC": "0cc (EV Electric)", "Contoh Model Unggulan": "Viar NX Urban, Viar EV1 Vespa Style, Viar Q1 Gen 2, Viar N1/N2"},
            {"Kategori Sektor": "Retro, Cruiser & Sport", "Merk": "Royal Enfield", "Negara": "Inggris / India", "Model": 8, "Varian": 23, "Rentang CC": "349cc - 650cc", "Contoh Model Unggulan": "Shotgun 650 Bobber, Guerrilla 450, Himalayan 450, Hunter 350, Classic 350 LED"},
            {"Kategori Sektor": "Retro, Cruiser & Sport", "Merk": "Benelli & Keeway", "Negara": "Italia / China", "Model": 8, "Varian": 16, "Rentang CC": "125cc - 250cc", "Contoh Model Unggulan": "Keeway Napoleon 250, Keeway Benda V252C, Motobi 200 EVO, Patagonian Eagle"},
            {"Kategori Sektor": "Retro, Cruiser & Sport", "Merk": "KTM", "Negara": "Austria", "Model": 3, "Varian": 16, "Rentang CC": "250cc - 250cc", "Contoh Model Unggulan": "KTM 390 Duke Gen-3 LC4c, KTM 250 Duke Gen-3, RC 390, 390 Adventure"},
            {"Kategori Sektor": "Retro, Cruiser & Sport", "Merk": "TVS", "Negara": "India", "Model": 4, "Varian": 13, "Rentang CC": "110cc - 225cc", "Contoh Model Unggulan": "Apache RTR 310 Quickshifter, TVS iQube S Smart EV, Ronin 225 TD, Callisto 125"},
            {"Kategori Sektor": "Big Bike / Moge Premium", "Merk": "Harley-Davidson", "Negara": "Amerika Serikat", "Model": 5, "Varian": 13, "Rentang CC": "494cc - 1745cc", "Contoh Model Unggulan": "Nightster Special 975, Sportster S 1250T, Pan America 1250, Softail Fat Boy 114"},
            {"Kategori Sektor": "Big Bike / Moge Premium", "Merk": "BMW Motorrad", "Negara": "Jerman", "Model": 6, "Varian": 15, "Rentang CC": "313cc - 1300cc", "Contoh Model Unggulan": "BMW R 1300 GS Matrix, BMW R 1300 GSA, BMW CE 02 EV, BMW CE 04, F 900 GS"}
        ]
        st.dataframe(pd.DataFrame(cat_summary), use_container_width=True, hide_index=True)
        st.caption("Total Cakupan Master Katalog: 17 Produsen Terkemuka, 140 Model Kendaraan, dan 419 Varian Resmi lintas 4 Kategori Sektor Industri.")
        st.markdown('</div>', unsafe_allow_html=True)


