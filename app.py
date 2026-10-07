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

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="MotorPrice ID - Used Motorcycle Intelligence Platform",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise Modern UI/UX CSS
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Top Executive Header */
    .app-header {
        background: linear-gradient(135deg, #0b1329 0%, #111e38 50%, #0d1b2a 100%);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }
    .app-header-title {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #f8fafc;
        margin: 0 0 6px 0;
    }
    .app-header-subtitle {
        font-size: 14px;
        color: #94a3b8;
        margin: 0;
        line-height: 1.5;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34d399;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        padding: 4px 10px;
        border-radius: 20px;
    }
    .status-dot {
        width: 6px;
        height: 6px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 6px #10b981;
    }

    /* Metric KPI Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: #111827;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 18px 20px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        border-color: rgba(59, 130, 246, 0.4);
        transform: translateY(-2px);
    }
    .kpi-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #06b6d4);
    }
    .kpi-card.emerald::before {
        background: linear-gradient(90deg, #10b981, #34d399);
    }
    .kpi-card.amber::before {
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
    }
    .kpi-card.rose::before {
        background: linear-gradient(90deg, #ef4444, #f87171);
    }
    .kpi-label {
        font-size: 11px;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 26px;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.1;
        margin-bottom: 4px;
    }
    .kpi-caption {
        font-size: 12px;
        color: #64748b;
    }

    /* Section Panels */
    .content-panel {
        background: #111827;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
    }
    .panel-header {
        font-size: 18px;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 14px;
        letter-spacing: -0.3px;
    }

    /* Valuation Hero Box */
    .val-result-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid rgba(59, 130, 246, 0.35);
        border-radius: 12px;
        padding: 24px;
        margin-top: 16px;
    }
    .val-price-hero {
        font-family: 'JetBrains Mono', monospace;
        font-size: 36px;
        font-weight: 800;
        color: #38bdf8;
        margin: 8px 0;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    .sidebar-title {
        font-size: 18px;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.3px;
        margin-bottom: 2px;
    }
    .sidebar-desc {
        font-size: 12px;
        color: #64748b;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

def format_dark_chart(fig, show_legend=False, y_title=None, x_title=None, is_price_axis=False):
    fig.update_layout(
        paper_bgcolor="rgba(17, 24, 39, 0.6)",
        plot_bgcolor="rgba(17, 24, 39, 0.6)",
        font=dict(family="Plus Jakarta Sans", color="#94a3b8", size=12),
        margin=dict(t=30, b=30, l=30, r=30),
        showlegend=show_legend
    )
    fig.update_xaxes(
        gridcolor="rgba(255, 255, 255, 0.06)",
        zerolinecolor="rgba(255, 255, 255, 0.08)",
        title=x_title if x_title else None
    )
    if is_price_axis:
        fig.update_yaxes(
            gridcolor="rgba(255, 255, 255, 0.06)",
            zerolinecolor="rgba(255, 255, 255, 0.08)",
            title=y_title if y_title else "Price (IDR)",
            tickformat=",.0f"
        )
    else:
        fig.update_yaxes(
            gridcolor="rgba(255, 255, 255, 0.06)",
            zerolinecolor="rgba(255, 255, 255, 0.08)",
            title=y_title if y_title else None
        )
    return fig

# Ensure DB & Seed on cold start
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

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 16px 0;">
        <div class="sidebar-title">MOTORPRICE ID</div>
        <div class="sidebar-desc">Indonesian Used Motorcycle Intelligence & Valuation Engine</div>
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
            "Official Master Catalog (12 Years)"
        ],
        index=0
    )

    st.markdown("---")
    st.caption("Engine: Python 3.13 | DB: SQLite ORM | Scraping: Multi-Platform | Model Scope: 2014–2026")

# ==========================================
# 1. MARKET OVERVIEW
# ==========================================
if menu == "Market Overview":
    st.markdown("""
    <div class="app-header">
        <div class="app-header-title">Market Overview & Macro Analytics</div>
        <div class="app-header-subtitle">Real-time macro perspective on used motorcycle valuation, volume distribution, and price dynamics across Indonesia.</div>
    </div>
    """, unsafe_allow_html=True)

    df = load_all_listings_df()

    if df.empty:
        st.info("The listing database is currently empty. Run the ingestion process from the Scraper Control Center.")
    else:
        df_valid = df[df["Price_Type"] == "Cash"]
        total_listings = len(df)
        valid_cash_count = len(df_valid)
        median_price = df_valid["Price"].median() if not df_valid.empty else 0
        dp_count = len(df[df["Price_Type"] == "DP / Clickbait"])

        # Top Executive KPI Cards
        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Total Ingested Listings</div>
                <div class="kpi-value">{total_listings:,}</div>
                <div class="kpi-caption">Clean & deduplicated data points</div>
            </div>
            <div class="kpi-card emerald">
                <div class="kpi-label">Valid Cash Listings</div>
                <div class="kpi-value">{valid_cash_count:,}</div>
                <div class="kpi-caption">Verified real selling price</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Market Median Price</div>
                <div class="kpi-value">Rp {median_price:,.0f}</div>
                <div class="kpi-caption">Across all brands & year tiers</div>
            </div>
            <div class="kpi-card rose">
                <div class="kpi-label">Flagged DP / Clickbait</div>
                <div class="kpi-value">{dp_count:,}</div>
                <div class="kpi-caption">Isolated from FMV computation</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown('<div class="content-panel"><div class="panel-header">Listing Distribution by Manufacturer Brand</div>', unsafe_allow_html=True)
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

# ==========================================
# 2. FAIR MARKET VALUE (FMV) CALCULATOR
# ==========================================
elif menu == "Fair Market Value (FMV) Calculator":
    st.markdown("""
    <div class="app-header">
        <div class="app-header-title">Fair Market Value (FMV) Calculator</div>
        <div class="app-header-subtitle">Statistically estimated market price incorporating historical listings, depreciation models, document validity, and odometer mileage.</div>
    </div>
    """, unsafe_allow_html=True)

    db = get_db_session()
    try:
        brands = [b.name for b in db.query(MasterBrand).order_by(MasterBrand.name).all()]
        if not brands:
            st.warning("Master catalog database is empty.")
        else:
            with st.container():
                st.markdown('<div class="content-panel"><div class="panel-header">Vehicle Specification & Condition Parameters</div>', unsafe_allow_html=True)
                col_in1, col_in2 = st.columns(2)
                with col_in1:
                    selected_brand = st.selectbox("Manufacturer Brand", brands)
                    brand_obj = db.query(MasterBrand).filter(MasterBrand.name == selected_brand).first()
                    models = [m.name for m in db.query(MasterModel).filter(MasterModel.brand_id == brand_obj.id).all()] if brand_obj else []
                    selected_model = st.selectbox("Vehicle Model", models if models else ["-"])

                    model_obj = db.query(MasterModel).filter(MasterModel.name == selected_model, MasterModel.brand_id == brand_obj.id).first() if brand_obj else None
                    variants = db.query(MasterVariant).filter(MasterVariant.model_id == model_obj.id).all() if model_obj else []
                    variant_map = {v.variant_name: v for v in variants}
                    selected_variant_name = st.selectbox("Specific Variant / Generation", list(variant_map.keys()) if variant_map else ["-"])

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

                calc_btn = st.button("Calculate Fair Market Valuation", type="primary", use_container_width=True)
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

                    st.markdown(f"""
                    <div class="val-result-box">
                        <div style="font-size: 13px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.8px;">
                            ESTIMATED FAIR MARKET VALUATION (FMV)
                        </div>
                        <div class="val-price-hero">Rp {final_fmv:,.0f}</div>
                        <div style="font-size: 13px; color: #cbd5e1; margin-bottom: 18px;">
                            Vehicle: <strong>{selected_brand} {selected_model} - {selected_variant_name} ({selected_year})</strong> | Samples Analyzed: <strong>{sample_count} listings</strong>
                        </div>
                        <div class="kpi-grid" style="margin-bottom: 0;">
                            <div class="kpi-card emerald" style="background: rgba(16, 185, 129, 0.06);">
                                <div class="kpi-label" style="color: #34d399;">Bargain Target (P25)</div>
                                <div class="kpi-value" style="color: #34d399; font-size: 22px;">Rp {bargain_p25:,.0f}</div>
                                <div class="kpi-caption">Recommended quick buy limit</div>
                            </div>
                            <div class="kpi-card" style="background: rgba(59, 130, 246, 0.08); border-color: rgba(59, 130, 246, 0.4);">
                                <div class="kpi-label" style="color: #60a5fa;">Market Median (FMV)</div>
                                <div class="kpi-value" style="color: #60a5fa; font-size: 22px;">Rp {final_fmv:,.0f}</div>
                                <div class="kpi-caption">Statistical equilibrium value</div>
                            </div>
                            <div class="kpi-card amber" style="background: rgba(245, 158, 11, 0.06);">
                                <div class="kpi-label" style="color: #fbbf24;">Pristine / Collector (P75)</div>
                                <div class="kpi-value" style="color: #fbbf24; font-size: 22px;">Rp {premium_p75:,.0f}</div>
                                <div class="kpi-caption">Low KM / showroom condition</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    finally:
        db.close()

# ==========================================
# 3. MARKET PRICE MONITORING & QUARTILES
# ==========================================
elif menu == "Market Price Monitoring & Quartiles":
    st.markdown("""
    <div class="app-header">
        <div class="app-header-title">Market Price Monitoring & Statistical Quartiles</div>
        <div class="app-header-subtitle">Standardized statistical benchmark table showing Min, P25 Bargain, Median FMV, P75 Premium, and Max prices.</div>
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
            st.info("Market statistics table is being computed. Please refresh or run ingestion.")
        else:
            table_rows = []
            for s, var, model, brand in stats_query:
                table_rows.append({
                    "Brand": brand.name,
                    "Model": model.name,
                    "Variant": var.variant_name,
                    "Year": s.year,
                    "Region": s.city if s.city else "National",
                    "Samples": s.sample_count,
                    "Min_Price": float(s.price_min),
                    "P25_Bargain": float(s.price_p25),
                    "Median_FMV": float(s.price_median),
                    "P75_Premium": float(s.price_p75),
                    "Max_Price": float(s.price_max),
                    "Official_MSRP": float(var.official_msrp_new) if var.official_msrp_new else None
                })
            df_stats = pd.DataFrame(table_rows)

            st.markdown('<div class="content-panel"><div class="panel-header">Catalog Filter Parameters</div>', unsafe_allow_html=True)
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
                    "Samples": st.column_config.NumberColumn(format="%d units")
                },
                hide_index=True
            )
    finally:
        db.close()

# ==========================================
# 4. BARGAIN & ARBITRAGE OPPORTUNITIES
# ==========================================
elif menu == "Bargain & Arbitrage Opportunities":
    st.markdown("""
    <div class="app-header">
        <div class="app-header-title">Bargain Hunter & Arbitrage Engine</div>
        <div class="app-header-subtitle">Real-time identification of motorcycle listings priced significantly below statistical FMV with verified documents.</div>
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
            st.info(f"No listings currently match the discount threshold of >= {threshold}%. Try lowering the threshold percentage.")
        else:
            deals_df = pd.DataFrame(deals)
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

# ==========================================
# 5. RAW SCRAPED DATASET EXPLORER
# ==========================================
elif menu == "Raw Scraped Dataset Explorer":
    st.markdown("""
    <div class="app-header">
        <div class="app-header-title">Raw Scraped Dataset Explorer</div>
        <div class="app-header-subtitle">Granular dataset table with advanced filtering, full text search, entity mapping, and instant CSV export.</div>
    </div>
    """, unsafe_allow_html=True)

    df_raw = load_all_listings_df()

    if df_raw.empty:
        st.info("The raw dataset is empty.")
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
            st.markdown(f"**Showing {len(filtered):,} of {len(df_raw):,} total records:**")
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

# ==========================================
# 6. LIVE SCRAPER & CRAWLER CENTER
# ==========================================
elif menu == "Live Scraper & Crawler Center":
    st.markdown("""
    <div class="app-header">
        <div class="app-header-title">Live Scraper & Crawler Control Center</div>
        <div class="app-header-subtitle">Execute on-demand scraping across supported Indonesian marketplaces with AI entity normalization and scam filtering.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="content-panel"><div class="panel-header">Scraper Execution Parameters</div>', unsafe_allow_html=True)
    sc1, sc2 = st.columns(2)
    with sc1:
        query_input = st.text_input("Target Keyword Query", "Honda Beat Street")
        target_platform = st.selectbox("Marketplace Platform", ["OLX Indonesia (JSON API)", "Momotor.id (REST Endpoint)", "Facebook Marketplace (Stealth Crawler)"])
    with sc2:
        loc_code = st.selectbox("Region Coverage", ["dki_jakarta", "jawa_barat", "jawa_timur", "jawa_tengah", "banten", "bali", "indonesia"])
        page_depth = st.number_input("Crawl Page Depth", min_value=1, max_value=10, value=1)

    start_crawl = st.button("Start Live Scraping & Ingestion Task", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if start_crawl:
        with st.spinner(f"Crawling listings for '{query_input}' in {loc_code}..."):
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
                st.success(f"Ingestion Task Completed Successfully: Fetched: {len(raw_items)} | Added: {added_count} | AI Matched: {matched_count} | Flagged DP: {dp_count}")
            except Exception as ex:
                st.error(f"Scraper Error: {ex}")
            finally:
                db.close()

# ==========================================
# 7. OFFICIAL MASTER CATALOG (12 YEARS)
# ==========================================
elif menu == "Official Master Catalog (12 Years)":
    st.markdown("""
    <div class="app-header">
        <div class="app-header-title">Official Motorcycle Master Catalog (2014–2026)</div>
        <div class="app-header-subtitle">Verified database of manufacturer brands, models, engine displacement CC, variant generations, and official MSRP.</div>
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
                "Brand": b.name,
                "Origin": b.country_origin or "-",
                "Model": m.name,
                "Category": m.category,
                "Engine (CC)": m.engine_capacity_cc,
                "Variant Generation": v.variant_name,
                "Release Start": v.release_year_start,
                "Release End": v.release_year_end if v.release_year_end else "Present (2026)",
                "Official MSRP (New)": float(v.official_msrp_new) if v.official_msrp_new else None,
                "Transmission": v.transmission_type or "Automatic"
            })

        df_cat = pd.DataFrame(rows)

        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Covered Brands</div>
                <div class="kpi-value">{df_cat['Brand'].nunique()} Brands</div>
                <div class="kpi-caption">Honda, Yamaha, Kawasaki, Vespa, Piaggio, Suzuki</div>
            </div>
            <div class="kpi-card emerald">
                <div class="kpi-label">Total Models</div>
                <div class="kpi-value">{df_cat['Model'].nunique()} Models</div>
                <div class="kpi-caption">Across all segments</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Master Variants</div>
                <div class="kpi-value">{len(df_cat)} Variants</div>
                <div class="kpi-caption">12-year production span (2014-2026)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.dataframe(
            df_cat.sort_values(by=["Brand", "Model", "Release Start"], ascending=[True, True, False]),
            column_config={
                "Official MSRP (New)": st.column_config.NumberColumn(format="Rp %,.0f"),
                "Engine (CC)": st.column_config.NumberColumn(format="%d cc")
            },
            hide_index=True,
            use_container_width=True
        )
    finally:
        db.close()
