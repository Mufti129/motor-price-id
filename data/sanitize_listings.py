"""
Sanitasi & Karantina Data Listing (Data Quality Gate).

Prinsip:
  - TIDAK menghapus baris apa pun. Listing anomali diberi status 'QUARANTINED' + kode alasan
    pada kolom quality_flag, sehingga dapat diaudit dan dipulihkan.
  - Idempoten: setiap eksekusi mereset karantina lama lalu menghitung ulang dari nol.
  - Setiap listing diberi label provenance (LIVE_SCRAPED / SYNTHETIC) yang dapat diverifikasi.

Aturan karantina (diterapkan pada listing non-DP):
  R0  Konsistensi entitas: judul wajib menyebut token model / alias varian yang di-match
      (menangkap salah-match seperti 'Honda Genio' -> EM1 e:).
  R1  Validasi harga berbasis ScamAndDPDetector.evaluate (harga kosong, absurd, frasa DP,
      kata kunci DP di judul, rasio > 135% MSRP, di bawah batas retensi usia, < 2.5 juta).
  R2  Tahun tidak konsisten (di masa depan atau > 1 tahun sebelum rilis varian).
  R3  Duplikat persis (platform, judul, harga, tahun) - baris pertama dipertahankan.
  R4  Outlier statistik robust: |Modified Z-Score (MAD)| > 3.5 dalam kelompok
      (varian, tahun) dengan minimal 5 sampel (Iglewicz & Hoaglin, 1993).

Penggunaan:
  python3 data/sanitize_listings.py            # eksekusi + tulis ke database
  python3 data/sanitize_listings.py --dry-run  # hanya laporan, tanpa menulis
"""

import os
import sys
import argparse
from datetime import datetime

import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from sqlalchemy import text  # noqa: E402
from models.database import engine, init_db  # noqa: E402
from pipeline.scam_detector import ScamAndDPDetector  # noqa: E402
from pipeline.provenance import classify_origin  # noqa: E402
from pipeline.entity_matcher import EntityMatcher  # noqa: E402

REPORT_DIR = os.path.join(BASE_DIR, "data", "reports")
MAD_Z_THRESHOLD = 3.5
MAD_MIN_GROUP = 5
CURRENT_YEAR = datetime.now().year


def load_listings() -> pd.DataFrame:
    query = """
        SELECT s.id, s.source_platform, s.external_id, s.url, s.title, s.raw_description,
               s.price, s.is_dp_price, s.claimed_year, s.matched_variant_id,
               v.official_msrp_new AS msrp, v.release_year_start, v.release_year_end,
               v.variant_name, v.aliases, m.name AS model_name, b.name AS brand_name
        FROM scraped_listings s
        LEFT JOIN master_variants v ON s.matched_variant_id = v.id
        LEFT JOIN master_models m ON v.model_id = m.id
        LEFT JOIN master_brands b ON m.brand_id = b.id
    """
    df = pd.read_sql(query, engine)
    df["price"] = df["price"].astype(float)
    df["msrp"] = pd.to_numeric(df["msrp"], errors="coerce")
    df["is_dp_price"] = df["is_dp_price"].fillna(0).astype(bool)
    return df


def year_inversion_audit(df: pd.DataFrame, min_n: int = 3, tolerance: float = 1.25) -> int:
    """Hitung pasangan (varian, tahun_tua < tahun_muda) di mana median tahun tua > 125% median tahun muda."""
    grp = (df.groupby(["matched_variant_id", "claimed_year"])["price"]
             .agg(["median", "size"]).reset_index())
    grp = grp[grp["size"] >= min_n]
    count = 0
    for _, g in grp.groupby("matched_variant_id"):
        g = g.sort_values("claimed_year")
        meds = g["median"].to_numpy()
        for i in range(len(meds)):
            for j in range(i + 1, len(meds)):
                if meds[i] > meds[j] * tolerance:
                    count += 1
    return count


def run(dry_run: bool = False) -> dict:
    init_db()
    df = load_listings()
    total = len(df)

    df["data_origin"] = [classify_origin(e, u) for e, u in zip(df["external_id"], df["url"])]
    df["quality_flag"] = None

    cash = df[~df["is_dp_price"]].copy()
    cash_before = cash[cash["matched_variant_id"].notna() & cash["claimed_year"].notna()]
    inversions_before = year_inversion_audit(cash_before)

    # R0 - Konsistensi entitas: judul wajib menyebut token model / alias varian yang di-match
    flags = {}
    for row in cash.itertuples(index=False):
        if pd.isna(row.matched_variant_id) or not row.model_name:
            continue
        aliases = [a for a in (row.aliases or "").split(",") if a.strip()]
        if not EntityMatcher.title_mentions_model(row.title or "", row.model_name, aliases):
            flags[row.id] = "ENTITY_MISMATCH"

    # R1 - Validasi harga
    for row in cash.itertuples(index=False):
        if row.id in flags:
            continue
        res = ScamAndDPDetector.evaluate(
            price=row.price,
            title=row.title or "",
            description=row.raw_description or "",
            expected_market_msrp=row.msrp if pd.notna(row.msrp) else None,
            claimed_year=int(row.claimed_year) if pd.notna(row.claimed_year) else None,
            current_year=CURRENT_YEAR,
        )
        if res["is_invalid"]:
            flags[row.id] = res["code"]

    # R2 - Konsistensi tahun
    for row in cash.itertuples(index=False):
        if row.id in flags or pd.isna(row.claimed_year):
            continue
        yr = int(row.claimed_year)
        if yr > CURRENT_YEAR or (pd.notna(row.release_year_start) and yr < int(row.release_year_start) - 1):
            flags[row.id] = "YEAR_INCONSISTENT"

    # R3 - Duplikat persis
    remaining = cash[~cash["id"].isin(flags.keys())]
    dup_mask = remaining.duplicated(subset=["source_platform", "title", "price", "claimed_year"], keep="first")
    for listing_id in remaining.loc[dup_mask, "id"]:
        flags[listing_id] = "DUPLICATE_EXACT"

    # R4 - Outlier statistik robust (MAD) per (varian, tahun)
    remaining = cash[~cash["id"].isin(flags.keys())
                     & cash["matched_variant_id"].notna() & cash["claimed_year"].notna()].copy()
    g = remaining.groupby(["matched_variant_id", "claimed_year"])["price"]
    med = g.transform("median")
    mad = g.transform(lambda x: (x - x.median()).abs().median())
    size = g.transform("size")
    mod_z = 0.6745 * (remaining["price"] - med) / mad.replace(0, np.nan)
    outlier_mask = (mod_z.abs() > MAD_Z_THRESHOLD) & (size >= MAD_MIN_GROUP)
    for listing_id in remaining.loc[outlier_mask, "id"]:
        flags[listing_id] = "STAT_OUTLIER_MAD"

    df["quality_flag"] = df["id"].map(flags)
    df["status"] = np.where(df["quality_flag"].notna(), "QUARANTINED", "ACTIVE")

    clean_cash = df[(~df["is_dp_price"]) & (df["status"] == "ACTIVE")
                    & df["matched_variant_id"].notna() & df["claimed_year"].notna()]
    inversions_after = year_inversion_audit(clean_cash)
    inversions_after_live = year_inversion_audit(clean_cash[clean_cash["data_origin"] == "LIVE_SCRAPED"])

    # Bias harga data sintetis terhadap data live pada kelompok (varian, tahun) yang sama
    pivot = (clean_cash.groupby(["matched_variant_id", "claimed_year", "data_origin"])["price"]
                       .median().unstack())
    bias = {"overlap_groups": 0, "median_live_to_synthetic": None, "p25": None, "p75": None}
    if {"LIVE_SCRAPED", "SYNTHETIC"}.issubset(pivot.columns):
        both = pivot.dropna(subset=["LIVE_SCRAPED", "SYNTHETIC"])
        if len(both):
            ratio = both["LIVE_SCRAPED"] / both["SYNTHETIC"]
            bias = {"overlap_groups": int(len(both)), "median_live_to_synthetic": round(float(ratio.median()), 4),
                    "p25": round(float(ratio.quantile(0.25)), 4), "p75": round(float(ratio.quantile(0.75)), 4)}

    summary = {
        "executed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dry_run": dry_run,
        "total_listings": total,
        "dp_flagged_existing": int(df["is_dp_price"].sum()),
        "quarantined": int((df["status"] == "QUARANTINED").sum()),
        "active_clean_cash": int(len(clean_cash)),
        "flag_breakdown": df["quality_flag"].value_counts().to_dict(),
        "origin_breakdown": df["data_origin"].value_counts().to_dict(),
        "origin_clean_cash": clean_cash["data_origin"].value_counts().to_dict(),
        "year_inversions_before": inversions_before,
        "year_inversions_after": inversions_after,
        "year_inversions_after_live_only": inversions_after_live,
        "synthetic_bias": bias,
        "price_max_before": float(cash["price"].max()) if len(cash) else 0.0,
        "price_max_after": float(clean_cash["price"].max()) if len(clean_cash) else 0.0,
        "price_min_before": float(cash["price"].min()) if len(cash) else 0.0,
        "price_min_after": float(clean_cash["price"].min()) if len(clean_cash) else 0.0,
    }

    if not dry_run:
        updates = df[["id", "status", "quality_flag", "data_origin"]].to_dict("records")
        for u in updates:
            u["quality_flag"] = u["quality_flag"] if isinstance(u["quality_flag"], str) else None
        with engine.begin() as conn:
            conn.execute(
                text("UPDATE scraped_listings SET status = :status, quality_flag = :quality_flag, "
                     "data_origin = :data_origin WHERE id = :id"),
                updates,
            )

    write_report(df, summary)
    return summary


def write_report(df: pd.DataFrame, s: dict) -> None:
    os.makedirs(REPORT_DIR, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d")
    quarantined = df[df["status"] == "QUARANTINED"][[
        "id", "source_platform", "data_origin", "external_id", "url", "title",
        "brand_name", "model_name", "variant_name", "claimed_year", "price", "msrp", "quality_flag"
    ]].sort_values(["quality_flag", "price"])
    quarantined.to_csv(os.path.join(REPORT_DIR, f"quarantined_listings_{stamp}.csv"), index=False)

    lines = [
        f"# Laporan Sanitasi Data Listing ({s['executed_at']})",
        "",
        f"- Mode: {'DRY-RUN (tanpa menulis)' if s['dry_run'] else 'EKSEKUSI (ditulis ke database)'}",
        f"- Total listing: {s['total_listings']:,}",
        f"- Sudah ditandai DP/Clickbait sebelumnya: {s['dp_flagged_existing']:,}",
        f"- Dikarantina oleh sanitasi ini: {s['quarantined']:,}",
        f"- Listing cash bersih (aktif, ter-match, bertahun): {s['active_clean_cash']:,}",
        "",
        "## Rincian Kode Karantina",
        "",
        "| Kode | Jumlah |",
        "| :--- | ---: |",
    ]
    for code, n in sorted(s["flag_breakdown"].items(), key=lambda x: -x[1]):
        lines.append(f"| {code} | {n:,} |")
    lines += [
        "",
        "## Provenance Data",
        "",
        "| Asal Data | Semua Listing | Cash Bersih |",
        "| :--- | ---: | ---: |",
    ]
    for origin in sorted(s["origin_breakdown"]):
        lines.append(f"| {origin} | {s['origin_breakdown'][origin]:,} | {s['origin_clean_cash'].get(origin, 0):,} |")
    lines += [
        "",
        "## Dampak Terhadap Kualitas Data",
        "",
        "| Metrik | Sebelum | Sesudah |",
        "| :--- | ---: | ---: |",
        f"| Harga cash maksimum | Rp {s['price_max_before']:,.0f} | Rp {s['price_max_after']:,.0f} |",
        f"| Harga cash minimum | Rp {s['price_min_before']:,.0f} | Rp {s['price_min_after']:,.0f} |",
        f"| Inversi tahun (median tahun tua > 125% tahun muda, n>=3) | {s['year_inversions_before']:,} | {s['year_inversions_after']:,} |",
        f"| Inversi tahun - hanya data LIVE_SCRAPED | - | {s['year_inversions_after_live_only']:,} |",
        "",
        "## Bias Data Sintetis terhadap Data Live",
        "",
        f"Dibandingkan pada {s['synthetic_bias']['overlap_groups']:,} kelompok (varian, tahun) yang memiliki kedua jenis data.",
        f"Rasio median harga LIVE / SINTETIS = {s['synthetic_bias']['median_live_to_synthetic']} "
        f"(P25 {s['synthetic_bias']['p25']}, P75 {s['synthetic_bias']['p75']}). "
        "Nilai > 1 berarti data sintetis cenderung lebih murah daripada harga iklan riil.",
        "",
        f"Daftar lengkap listing yang dikarantina: `data/reports/quarantined_listings_{stamp}.csv`",
    ]
    with open(os.path.join(REPORT_DIR, f"sanitization_report_{stamp}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sanitasi & karantina listing anomali")
    parser.add_argument("--dry-run", action="store_true", help="Hanya laporan tanpa menulis ke database")
    args = parser.parse_args()
    result = run(dry_run=args.dry_run)
    for k, v in result.items():
        print(f"{k}: {v}")
