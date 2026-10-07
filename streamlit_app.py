import os
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from sqlalchemy.orm import Session

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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Professional CSS (No emojis, clean corporate theme)
st.markdown("""
<style>
    .reportview-container {
        background: #f8fafc;
    }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
        margin-top: 4px;
    }
    .metric-label {
        font-size: 13px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    .badge-cash {
        background-color: #ecfdf5;
        color: #065f46;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-dp {
        background-color: #fef2f2;
        color: #991b1b;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        font-weight: 600;
        border-radius: 6px 6px 0 0;
        padding: 0 16px;
    }
</style>
""", unsafe_allow_html=True)

# Ensure DB & Seed on cold start
@st.cache_resource
def ensure_database_initialized():
    init_db()
    db = SessionLocal()
    try:
        from data.generate_massive_market_dataset import generate_massive_dataset
        listing_count = db.query(ScrapedListing).count()
        if listing_count < 100:
            generate_massive_dataset(target_per_brand=550)
    except Exception as e:
        seed_master_motor_database()
    finally:
        db.close()

ensure_database_initialized()

# Helper Data Loaders
def get_db_session() -> Session:
    return SessionLocal()

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
                "BPKB": "Ada" if r.has_bpkb else "Tidak Ada (STNK Only)",
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
# SIDEBAR NAVIGATION & FILTERS
# ==========================================
st.sidebar.title("MotorPrice ID")
st.sidebar.caption("Used Motorcycle Intelligence & Scraping Platform")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation Menu",
    [
        "Market Overview",
        "Fair Market Value Calculator",
        "Market Price Monitoring",
        "Bargain & Arbitrage Deals",
        "Raw Dataset Explorer",
        "Scraper Control Center",
        "Master Catalog"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("System Status: Online | Database: Operational")

# ==========================================
# 1. MARKET OVERVIEW
# ==========================================
if menu == "Market Overview":
    st.title("Market Overview & Macro Analytics")
    st.caption("Real-time summary of scraped used motorcycle listings and price distribution across Indonesia.")

    df = load_all_listings_df()

    if df.empty:
        st.info("Database listing saat ini masih kosong. Silakan buka menu 'Scraper Control Center' untuk menjalankan proses ingestion data.")
    else:
        df_valid = df[df["Price_Type"] == "Cash"]

        # Top Metric Cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Listings Ingested</div>
                <div class="metric-value">{len(df):,}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Valid Cash Listings</div>
                <div class="metric-value">{len(df_valid):,}</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            median_val = df_valid["Price"].median() if not df_valid.empty else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Market Median Price</div>
                <div class="metric-value">Rp {median_val:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            dp_count = len(df[df["Price_Type"] == "DP / Clickbait"])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Flagged DP / Clickbait</div>
                <div class="metric-value">{dp_count:,}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts Section
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Distribution of Listings by Brand")
            brand_counts = df["Brand"].value_counts().reset_index()
            brand_counts.columns = ["Brand", "Total Listings"]
            fig_brand = px.bar(
                brand_counts,
                x="Brand",
                y="Total Listings",
                color="Brand",
                color_discrete_sequence=px.colors.qualitative.Prism,
                text_auto=True
            )
            fig_brand.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_brand, use_container_width=True)

        with c2:
            st.subheader("Price Distribution by Brand (Cash Only)")
            fig_box = px.box(
                df_valid,
                x="Brand",
                y="Price",
                color="Brand",
                points="outliers",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_box.update_layout(
                showlegend=False,
                yaxis=dict(title="Price (IDR)", tickformat=",.0f"),
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_box, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Price Depreciation Trend Across Manufacturing Years")
        year_trend = df_valid.dropna(subset=["Year"]).groupby(["Year", "Brand"])["Price"].median().reset_index()
        fig_trend = px.line(
            year_trend,
            x="Year",
            y="Price",
            color="Brand",
            markers=True,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_trend.update_layout(
            yaxis=dict(title="Median Price (IDR)", tickformat=",.0f"),
            xaxis=dict(title="Manufacturing Year", dtick=1),
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

# ==========================================
# 2. FAIR MARKET VALUE (FMV) CALCULATOR
# ==========================================
elif menu == "Fair Market Value Calculator":
    st.title("Fair Market Value (FMV) Calculator")
    st.caption("Estimate the current fair market price based on historical transactions, condition adjustment, and vehicle specifications.")

    db = get_db_session()
    try:
        brands = [b.name for b in db.query(MasterBrand).order_by(MasterBrand.name).all()]
        if not brands:
            st.warning("Master catalog database is empty. Please run seeding from the Scraper Control Center.")
        else:
            col_in1, col_in2 = st.columns(2)
            with col_in1:
                selected_brand = st.selectbox("Vehicle Brand", brands)
                brand_obj = db.query(MasterBrand).filter(MasterBrand.name == selected_brand).first()
                models = [m.name for m in db.query(MasterModel).filter(MasterModel.brand_id == brand_obj.id).all()] if brand_obj else []
                selected_model = st.selectbox("Vehicle Model", models if models else ["-"])

                model_obj = db.query(MasterModel).filter(MasterModel.name == selected_model, MasterModel.brand_id == brand_obj.id).first() if brand_obj else None
                variants = db.query(MasterVariant).filter(MasterVariant.model_id == model_obj.id).all() if model_obj else []
                variant_map = {v.variant_name: v for v in variants}
                selected_variant_name = st.selectbox("Variant / Sub-Model", list(variant_map.keys()) if variant_map else ["-"])

            with col_in2:
                selected_var = variant_map.get(selected_variant_name)
                min_yr = selected_var.release_year_start if selected_var else 2015
                max_yr = selected_var.release_year_end if (selected_var and selected_var.release_year_end) else 2026
                year_options = list(range(max_yr, min_yr - 1, -1))
                selected_year = st.selectbox("Manufacturing Year", year_options if year_options else [2022])

                input_km = st.number_input("Odometer Mileage (KM)", min_value=0, max_value=200000, value=20000, step=1000)
                input_tax = st.selectbox("Tax & Document Status", ["Tax Valid / Active (Surat Lengkap)", "Tax Expired 1 Year", "Tax Expired 2+ Years", "STNK Only (Non-BPKB)"])

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Calculate Fair Market Price", type="primary"):
                pricing_engine = PricingAnalyticsEngine(db)
                stats = pricing_engine.calculate_variant_pricing_stats(selected_var.id, year=selected_year) if selected_var else None

                base_price = stats["price_median"] if stats else (float(selected_var.official_msrp_new) * 0.70 if selected_var and selected_var.official_msrp_new else 18000000.0)
                sample_count = stats["sample_count"] if stats else 0

                # Condition adjustments
                adj_tax = 0.0
                if "1 Year" in input_tax:
                    adj_tax = -600000.0
                elif "2+" in input_tax:
                    adj_tax = -1200000.0
                elif "STNK Only" in input_tax:
                    adj_tax = - (base_price * 0.35)

                expected_km = max(5000, (2026 - selected_year) * 8000)
                km_diff = input_km - expected_km
                adj_km = - (km_diff / 5000) * 250000.0
                adj_km = max(-2000000.0, min(1000000.0, adj_km))

                final_fmv = max(3000000.0, base_price + adj_tax + adj_km)
                bargain_p25 = final_fmv * 0.92
                premium_p75 = final_fmv * 1.08

                st.subheader("Valuation Results")
                res1, res2, res3 = st.columns(3)
                with res1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Bargain Target (P25)</div>
                        <div class="metric-value" style="color: #059669;">Rp {bargain_p25:,.0f}</div>
                        <div style="font-size: 12px; color: #64748b; margin-top: 4px;">Recommended for quick purchase</div>
                    </div>
                    """, unsafe_allow_html=True)
                with res2:
                    st.markdown(f"""
                    <div class="metric-card" style="border: 2px solid #2563eb;">
                        <div class="metric-label">Estimated Fair Market Value (FMV)</div>
                        <div class="metric-value" style="color: #2563eb;">Rp {final_fmv:,.0f}</div>
                        <div style="font-size: 12px; color: #64748b; margin-top: 4px;">Median statistical fair value</div>
                    </div>
                    """, unsafe_allow_html=True)
                with res3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Premium / Pristine (P75)</div>
                        <div class="metric-value" style="color: #4f46e5;">Rp {premium_p75:,.0f}</div>
                        <div style="font-size: 12px; color: #64748b; margin-top: 4px;">Low mileage / collector condition</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.info(f"Model: {selected_brand} {selected_model} - {selected_variant_name} ({selected_year}) | Market Data Samples: {sample_count} listings | Baseline MSRP: Rp {float(selected_var.official_msrp_new):,.0f}" if selected_var and selected_var.official_msrp_new else f"Model: {selected_brand} {selected_model} ({selected_year})")
    finally:
        db.close()

# ==========================================
# 3. MARKET PRICE MONITORING TABLE
# ==========================================
elif menu == "Market Price Monitoring":
    st.title("Market Price Monitoring & Statistical Quartiles")
    st.caption("Aggregated market statistics grouped by variant, year, and region.")

    db = get_db_session()
    try:
        engine = PricingAnalyticsEngine(db)
        engine.refresh_daily_market_stats()

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
            st.info("No aggregated market price records available yet. Please run scraping from the Scraper Control Center.")
        else:
            table_rows = []
            for s, var, model, brand in stats_query:
                table_rows.append({
                    "Brand": brand.name,
                    "Model": model.name,
                    "Variant": var.variant_name,
                    "Year": s.year,
                    "Region": s.city if s.city else "National",
                    "Sample_Count": s.sample_count,
                    "Min_Price": float(s.price_min),
                    "P25_Bargain": float(s.price_p25),
                    "Median_FMV": float(s.price_median),
                    "P75_Premium": float(s.price_p75),
                    "Max_Price": float(s.price_max),
                    "Official_MSRP": float(var.official_msrp_new) if var.official_msrp_new else None
                })
            df_stats = pd.DataFrame(table_rows)

            # Filtering Controls
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                sel_brands = st.multiselect("Filter Brand", options=sorted(df_stats["Brand"].unique()), default=sorted(df_stats["Brand"].unique()))
            with f_col2:
                sel_models = st.multiselect("Filter Model", options=sorted(df_stats["Model"].unique()), default=[])

            filtered_df = df_stats[df_stats["Brand"].isin(sel_brands)]
            if sel_models:
                filtered_df = filtered_df[filtered_df["Model"].isin(sel_models)]

            st.dataframe(
                filtered_df.sort_values(by=["Brand", "Model", "Year"], ascending=[True, True, False]),
                use_container_width=True,
                column_config={
                    "Min_Price": st.column_config.NumberColumn(format="Rp %,.0f"),
                    "P25_Bargain": st.column_config.NumberColumn(format="Rp %,.0f"),
                    "Median_FMV": st.column_config.NumberColumn(format="Rp %,.0f"),
                    "P75_Premium": st.column_config.NumberColumn(format="Rp %,.0f"),
                    "Max_Price": st.column_config.NumberColumn(format="Rp %,.0f"),
                    "Official_MSRP": st.column_config.NumberColumn(format="Rp %,.0f")
                },
                hide_index=True
            )
    finally:
        db.close()

# ==========================================
# 4. BARGAIN & ARBITRAGE DEALS
# ==========================================
elif menu == "Bargain & Arbitrage Deals":
    st.title("Bargain Hunter & Arbitrage Opportunities")
    st.caption("Listings priced significantly below the statistical fair market median with complete legal documentation.")

    db = get_db_session()
    try:
        engine = PricingAnalyticsEngine(db)
        threshold = st.slider("Minimum Discount Percentage (%)", min_value=5.0, max_value=35.0, value=10.0, step=1.0)
        deals = engine.find_hot_deals(discount_threshold_pct=threshold)

        if not deals:
            st.info(f"No listings found with discount >= {threshold}% below market median.")
        else:
            st.write(f"Found **{len(deals)}** potential arbitrage opportunities:")
            deals_df = pd.DataFrame(deals)
            st.dataframe(
                deals_df[[
                    "motor_name", "year", "price", "fair_market_value",
                    "saving_amount", "discount_pct", "tax_status", "city", "url"
                ]].rename(columns={
                    "motor_name": "Vehicle",
                    "year": "Year",
                    "price": "Listing Price",
                    "fair_market_value": "Market FMV",
                    "saving_amount": "Savings (IDR)",
                    "discount_pct": "Discount %",
                    "tax_status": "Tax Status",
                    "city": "Location",
                    "url": "Listing URL"
                }),
                column_config={
                    "Listing Price": st.column_config.NumberColumn(format="Rp %,.0f"),
                    "Market FMV": st.column_config.NumberColumn(format="Rp %,.0f"),
                    "Savings (IDR)": st.column_config.NumberColumn(format="Rp %,.0f"),
                    "Discount %": st.column_config.NumberColumn(format="%.1f%%"),
                    "Listing URL": st.column_config.LinkColumn("View Listing")
                },
                hide_index=True,
                use_container_width=True
            )
    finally:
        db.close()

# ==========================================
# 5. RAW DATASET EXPLORER
# ==========================================
elif menu == "Raw Dataset Explorer":
    st.title("Raw Scraped Dataset Explorer")
    st.caption("Full granular table containing all scraped items, AI normalized fields, and raw platform metadata.")

    df_raw = load_all_listings_df()

    if df_raw.empty:
        st.info("The raw dataset is empty. Run the scraper in the control center to fetch listings.")
    else:
        # Search and Filter Bars
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            search_kw = st.text_input("Search Title / Keyword", "")
        with f2:
            brand_filter = st.multiselect("Brand", options=sorted(df_raw["Brand"].unique()), default=[])
        with f3:
            price_type_filter = st.selectbox("Price Type", ["All", "Cash Only", "DP / Clickbait Only"])
        with f4:
            tax_filter = st.multiselect("Tax Status", options=sorted(df_raw["Tax_Status"].unique()), default=[])

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

        st.markdown(f"**Displaying {len(filtered):,} records:**")
        st.dataframe(
            filtered[[
                "ID", "Platform", "Title", "Brand", "Model", "Variant", "Year",
                "Price", "Price_Type", "Mileage_KM", "Tax_Status", "BPKB", "City", "URL"
            ]],
            column_config={
                "Price": st.column_config.NumberColumn(format="Rp %,.0f"),
                "Mileage_KM": st.column_config.NumberColumn(format="%,.0f km"),
                "URL": st.column_config.LinkColumn("Listing Link")
            },
            hide_index=True,
            use_container_width=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        # Export Buttons
        csv_data = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Current Dataset (CSV)",
            data=csv_data,
            file_name=f"used_motorcycle_dataset_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

# ==========================================
# 6. SCRAPER CONTROL CENTER
# ==========================================
elif menu == "Scraper Control Center":
    st.title("Scraper Ingestion & Crawler Control Center")
    st.caption("Trigger on-demand data extraction from supported marketplaces (OLX Indonesia, etc.) with real-time AI normalization.")

    sc1, sc2 = st.columns(2)
    with sc1:
        query_input = st.text_input("Search Keyword Query", "Vario 150")
        target_platform = st.selectbox("Target Platform", ["OLX Indonesia", "Momotor.id (API)", "Facebook Marketplace (Playwright Stealth)"])
    with sc2:
        loc_code = st.selectbox("Region Scope", ["dki_jakarta", "jawa_barat", "jawa_timur", "jawa_tengah", "banten", "bali", "indonesia"])
        page_depth = st.number_input("Crawl Page Depth (Pages)", min_value=1, max_value=10, value=1)

    if st.button("Start Scraping & Ingestion Task", type="primary"):
        with st.spinner(f"Running scraper for '{query_input}' in {loc_code}..."):
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
                st.success(f"Ingestion completed. Total fetched: {len(raw_items)} | Added/Updated: {added_count} | AI Matched: {matched_count} | Flagged DP: {dp_count}")
            except Exception as ex:
                st.error(f"Error during ingestion task: {ex}")
            finally:
                db.close()

# ==========================================
# 7. MASTER CATALOG
# ==========================================
elif menu == "Master Catalog":
    st.title("Official Motorcycle Master Catalog")
    st.caption("Standardized database of motorcycle brands, models, engine specifications, and manufacturer release years.")

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
                "Variant Name": v.variant_name,
                "Release Start": v.release_year_start,
                "Release End": v.release_year_end if v.release_year_end else "Present",
                "Official MSRP": float(v.official_msrp_new) if v.official_msrp_new else None,
                "Transmission": v.transmission_type or "Automatic"
            })

        df_cat = pd.DataFrame(rows)
        st.dataframe(
            df_cat.sort_values(by=["Brand", "Model", "Release Start"], ascending=[True, True, False]),
            column_config={
                "Official MSRP": st.column_config.NumberColumn(format="Rp %,.0f")
            },
            hide_index=True,
            use_container_width=True
        )
    finally:
        db.close()
