"""
Pipeline Training Model Valuasi Machine Learning (Riil, Reproducible).

Menggantikan formula heuristik statis dengan model yang benar-benar dilatih dari database.

Desain:
  - Target   : log(harga / MSRP baru)  -> rasio retensi nilai. Membuat model berlaku lintas
               segmen harga (komuter Rp 15 juta hingga moge Rp 900 juta) tanpa ekstrapolasi skala.
  - Model    : HistGradientBoostingRegressor (median/absolute_error) + 2 model kuantil (P25, P75)
               untuk interval harga empiris.
  - Fitur    : hanya fitur yang tersedia saat inferensi (usia, odometer, cc, EV, dokumen, pajak,
               merek, segmen). Platform & asal data TIDAK dipakai sebagai fitur.
  - Data     : listing cash, ter-match, status ACTIVE (lolos sanitasi), bukan DP.
  - Scope    : default 'live' = hanya LIVE_SCRAPED (iklan riil yang dapat diverifikasi URL-nya).
               'all' = termasuk data SYNTHETIC (tidak direkomendasikan, bias -15% terhadap pasar riil).
  - Evaluasi : hold-out 20% + 5-fold cross-validation, metrik dalam Rupiah (MAE, RMSE, MAPE, R2)
               serta permutation feature importance pada data uji.

Penggunaan:
  python3 analytics/train_valuation_model.py               # scope live (default)
  python3 analytics/train_valuation_model.py --scope all
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from typing import Dict, Any, Tuple

import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

MODEL_DIR = os.path.join(BASE_DIR, "models", "saved_models")
MODEL_PATH = os.path.join(MODEL_DIR, "valuation_hgb.joblib")
METRICS_PATH = os.path.join(MODEL_DIR, "valuation_metrics.json")
MODEL_VERSION = "v7.0.0-HGB"
RANDOM_STATE = 42

NUMERIC_FEATURES = ["age", "odometer_km", "engine_cc", "is_ev", "has_bpkb", "tax_off", "tax_unknown"]
CATEGORICAL_FEATURES = ["brand", "segment"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

FEATURE_LABELS = {
    "age": "Usia Unit (Tahun)",
    "odometer_km": "Jarak Tempuh Odometer (KM)",
    "engine_cc": "Kapasitas Mesin (CC)",
    "is_ev": "Motor Listrik (EV)",
    "has_bpkb": "Status Legalitas BPKB",
    "tax_off": "Pajak STNK Mati",
    "tax_unknown": "Status Pajak Tidak Diketahui",
    "brand": "Merek (Brand)",
    "segment": "Segmen Kendaraan",
}


def derive_segment(category: str, cc: float) -> str:
    """Normalisasi kategori katalog yang sangat beragam menjadi 7 segmen stabil."""
    cat = (category or "").lower()
    cc = cc or 0
    if "ev" in cat or "electric" in cat or cc == 0:
        return "EV"
    if cc >= 400:
        return "MOGE"
    if "maxi" in cat:
        return "MAXI"
    if any(k in cat for k in ("trail", "enduro", "adventure", "supermoto", "dual")):
        return "TRAIL_ADV"
    if any(k in cat for k in ("retro", "classic", "classy", "cruiser", "heritage", "scrambler", "bobber", "cafe")):
        return "RETRO_CLASSIC"
    if "matic" in cat or "scooter" in cat:
        return "MATIC"
    if any(k in cat for k in ("sport", "naked", "fairing", "roadster")):
        return "SPORT"
    return "BEBEK_OTHER"


def build_features(df: pd.DataFrame, current_year: int) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    out["age"] = (current_year - df["claimed_year"].astype(float)).clip(lower=0)
    out["odometer_km"] = pd.to_numeric(df["odometer_km"], errors="coerce")
    out["engine_cc"] = pd.to_numeric(df["engine_cc"], errors="coerce").fillna(0)
    out["is_ev"] = (out["engine_cc"] == 0).astype(int)
    out["has_bpkb"] = df["has_bpkb"].fillna(1).astype(int)
    tax = df["tax_status"].fillna("Unknown").astype(str)
    out["tax_off"] = tax.str.contains("Mati|Off", case=False).astype(int)
    out["tax_unknown"] = tax.str.contains("Unknown", case=False).astype(int)
    out["brand"] = df["brand"].fillna("UNKNOWN").astype(str)
    out["segment"] = [derive_segment(c, cc) for c, cc in zip(df["category"], df["engine_cc"])]
    return out


def load_training_data(scope: str) -> pd.DataFrame:
    from models.database import engine
    query = """
        SELECT s.id, s.price, s.claimed_year, s.odometer_km, s.has_bpkb, s.tax_status,
               s.data_origin, v.official_msrp_new AS msrp, m.engine_capacity_cc AS engine_cc,
               m.category, b.name AS brand
        FROM scraped_listings s
        JOIN master_variants v ON s.matched_variant_id = v.id
        JOIN master_models m ON v.model_id = m.id
        JOIN master_brands b ON m.brand_id = b.id
        WHERE s.is_dp_price = 0
          AND COALESCE(s.status, 'ACTIVE') = 'ACTIVE'
          AND s.claimed_year IS NOT NULL
          AND s.price > 0
          AND v.official_msrp_new > 0
    """
    df = pd.read_sql(query, engine)
    if scope == "live":
        df = df[df["data_origin"] == "LIVE_SCRAPED"]
    df = df.copy()
    df["price"] = df["price"].astype(float)
    df["msrp"] = df["msrp"].astype(float)
    return df.reset_index(drop=True)


class CategoryEncoder:
    """Encoder kategori -> integer yang dapat diserialisasi (kategori tak dikenal -> NaN)."""

    def __init__(self, features=None):
        self.features = list(features or FEATURES)
        self.mapping: Dict[str, Dict[str, int]] = {}

    def fit(self, X: pd.DataFrame):
        for col in self.features:
            if col in CATEGORICAL_FEATURES:
                self.mapping[col] = {v: i for i, v in enumerate(sorted(X[col].unique()))}
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        X = X.copy()
        for col, mp in self.mapping.items():
            X[col] = X[col].map(mp).astype(float)  # unknown -> NaN (ditangani HGB)
        return X[self.features].to_numpy(dtype=float)


def select_informative_features(X: pd.DataFrame, max_missing: float = 0.95):
    """Buang fitur konstan atau hampir seluruhnya kosong (tidak dapat dipelajari dari data)."""
    active, dropped = [], {}
    for f in FEATURES:
        col = X[f]
        if col.isna().mean() > max_missing:
            dropped[f] = f"{col.isna().mean():.1%} kosong"
        elif col.dropna().nunique() < 2:
            dropped[f] = "nilai konstan"
        elif col.dropna().value_counts(normalize=True).iloc[0] > 0.99:
            dropped[f] = f"hampir konstan ({col.dropna().value_counts(normalize=True).iloc[0]:.1%} bernilai sama)"
        else:
            active.append(f)
    return active, dropped


MONOTONIC_DIRECTION = {"age": -1, "odometer_km": -1, "tax_off": -1, "has_bpkb": 1}


def single_thread():
    """
    Batasi OpenMP ke 1 thread. Pada dataset kecil, HGB multi-thread justru ~20x lebih lambat
    akibat oversubscription (terukur: 13.0 s vs 0.64 s per fit).
    """
    try:
        from threadpoolctl import threadpool_limits
        return threadpool_limits(limits=1)
    except Exception:  # pragma: no cover
        import contextlib
        return contextlib.nullcontext()


def monotone_predict(model, X: np.ndarray, features, age_min: int = 0) -> np.ndarray:
    """
    Prediksi dengan jaminan monoton tidak-naik terhadap usia (proyeksi isotonik).

    monotonic_cst pada HGB hanya dijamin untuk loss yang nilai daunnya tidak dihitung ulang.
    Pada loss absolute_error / quantile, nilai daun diperbarui ulang (median/kuantil residual)
    sehingga pelanggaran kecil masih dapat terjadi. Untuk setiap baris, prediksi dihitung pada
    seluruh usia age_min..age lalu diambil nilai minimum kumulatif pada usia baris tersebut.
    """
    if "age" not in features or len(X) == 0:
        return model.predict(X)
    a_idx = list(features).index("age")
    ages = np.nan_to_num(X[:, a_idx], nan=age_min).astype(int)
    span = int(max(ages.max() - age_min, 0)) + 1
    grid = np.repeat(X, span, axis=0)
    offs = np.tile(np.arange(span), len(X))
    grid[:, a_idx] = age_min + offs
    raw = model.predict(grid).reshape(len(X), span)
    cummin = np.minimum.accumulate(raw, axis=1)
    return cummin[np.arange(len(X)), np.clip(ages - age_min, 0, span - 1)]


def _make_model(loss: str, features, quantile: float = None):
    from sklearn.ensemble import HistGradientBoostingRegressor
    cat_mask = [f in CATEGORICAL_FEATURES for f in features]
    kwargs = dict(
        loss=loss, learning_rate=0.06, max_iter=400, max_leaf_nodes=15, min_samples_leaf=10,
        l2_regularization=1.0, categorical_features=cat_mask if any(cat_mask) else None,
        # Batasan ekonomi: retensi nilai tidak boleh naik seiring bertambahnya usia
        monotonic_cst=[MONOTONIC_DIRECTION.get(f, 0) for f in features],
        random_state=RANDOM_STATE, early_stopping=False,
    )
    if quantile is not None:
        kwargs["quantile"] = quantile
    return HistGradientBoostingRegressor(**kwargs)


def _price_metrics(y_true_price: np.ndarray, y_pred_price: np.ndarray) -> Dict[str, float]:
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    return {
        "r2_score": float(r2_score(y_true_price, y_pred_price)),
        "mae_idr": float(mean_absolute_error(y_true_price, y_pred_price)),
        "rmse_idr": float(np.sqrt(mean_squared_error(y_true_price, y_pred_price))),
        "mape_pct": float(np.mean(np.abs(y_pred_price - y_true_price) / y_true_price) * 100.0),
        "median_ape_pct": float(np.median(np.abs(y_pred_price - y_true_price) / y_true_price) * 100.0),
    }


def fit_bundle_only(scope: str = "live", current_year: int = None) -> Dict[str, Any]:
    """
    Refit cepat model final (tanpa evaluasi) dengan prosedur & data yang identik dengan train().
    Dipakai sebagai fallback runtime bila artefak joblib tidak kompatibel dengan versi scikit-learn server.
    """
    current_year = current_year or datetime.now().year
    df = load_training_data(scope)
    if len(df) < 100:
        raise RuntimeError(f"Data training terlalu sedikit ({len(df)} baris) untuk scope '{scope}'.")
    X_raw = build_features(df, current_year)
    y = np.log(df["price"].to_numpy() / df["msrp"].to_numpy())
    features, _ = select_informative_features(X_raw)
    encoder = CategoryEncoder(features).fit(X_raw)
    X = encoder.transform(X_raw)
    return {
        "version": MODEL_VERSION,
        "features": features,
        "encoder_mapping": encoder.mapping,
        "model_median": _make_model("absolute_error", features).fit(X, y),
        "model_p25": _make_model("quantile", features, 0.25).fit(X, y),
        "model_p75": _make_model("quantile", features, 0.75).fit(X, y),
        "reference_year": current_year,
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "domain": training_domain(X_raw),
    }


def training_domain(X_raw: pd.DataFrame) -> Dict[str, Any]:
    """Cakupan data latih, dipakai untuk mendeteksi inferensi di luar domain (ekstrapolasi)."""
    return {
        "brands": sorted(X_raw["brand"].unique().tolist()),
        "segments": sorted(X_raw["segment"].unique().tolist()),
        "age_min": int(X_raw["age"].min()),
        "age_max": int(X_raw["age"].max()),
    }


def train(scope: str = "live", save: bool = True, current_year: int = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    from sklearn.model_selection import train_test_split, KFold
    from sklearn.inspection import permutation_importance
    import sklearn

    current_year = current_year or datetime.now().year
    t0 = time.time()
    df = load_training_data(scope)
    if len(df) < 100:
        raise RuntimeError(f"Data training terlalu sedikit ({len(df)} baris) untuk scope '{scope}'.")

    X_raw = build_features(df, current_year)
    y = np.log(df["price"].to_numpy() / df["msrp"].to_numpy())
    msrp = df["msrp"].to_numpy()
    price = df["price"].to_numpy()

    idx_train, idx_test = train_test_split(np.arange(len(df)), test_size=0.2, random_state=RANDOM_STATE)

    features, dropped_features = select_informative_features(X_raw)
    encoder = CategoryEncoder(features).fit(X_raw)
    X = encoder.transform(X_raw)

    age_min = int(X_raw["age"].min())
    model_med = _make_model("absolute_error", features).fit(X[idx_train], y[idx_train])
    pred_test = np.exp(monotone_predict(model_med, X[idx_test], features, age_min)) * msrp[idx_test]
    holdout = _price_metrics(price[idx_test], pred_test)

    # Baseline pembanding: median rasio retensi per usia dari data latih (tanpa ML)
    tr = pd.DataFrame({"age": X_raw["age"].to_numpy()[idx_train], "r": y[idx_train]})
    age_median = tr.groupby("age")["r"].median()
    base_r = X_raw["age"].iloc[idx_test].map(age_median).fillna(tr["r"].median()).to_numpy()
    baseline = _price_metrics(price[idx_test], np.exp(base_r) * msrp[idx_test])

    # Cakupan interval P25-P75 pada data uji
    model_p25 = _make_model("quantile", features, 0.25).fit(X[idx_train], y[idx_train])
    model_p75 = _make_model("quantile", features, 0.75).fit(X[idx_train], y[idx_train])
    lo = np.exp(monotone_predict(model_p25, X[idx_test], features, age_min)) * msrp[idx_test]
    hi = np.exp(monotone_predict(model_p75, X[idx_test], features, age_min)) * msrp[idx_test]
    coverage = float(np.mean((price[idx_test] >= np.minimum(lo, hi)) & (price[idx_test] <= np.maximum(lo, hi))) * 100)

    # 5-fold cross validation (R2 dalam skala Rupiah)
    cv_r2, cv_mape = [], []
    for tr_idx, te_idx in KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE).split(X):
        m = _make_model("absolute_error", features).fit(X[tr_idx], y[tr_idx])
        p = np.exp(monotone_predict(m, X[te_idx], features, age_min)) * msrp[te_idx]
        mm = _price_metrics(price[te_idx], p)
        cv_r2.append(mm["r2_score"])
        cv_mape.append(mm["mape_pct"])

    # Permutation importance pada data uji (skala target log-retensi)
    perm = permutation_importance(model_med, X[idx_test], y[idx_test], n_repeats=10,
                                  random_state=RANDOM_STATE, scoring="neg_mean_absolute_error")
    imp = np.clip(perm.importances_mean, 0, None)
    imp = imp / imp.sum() if imp.sum() > 0 else imp
    feature_importance = {FEATURE_LABELS[f]: round(float(v), 4) for f, v in zip(features, imp)}

    # Model final dilatih ulang pada seluruh data
    final_med = _make_model("absolute_error", features).fit(X, y)
    final_p25 = _make_model("quantile", features, 0.25).fit(X, y)
    final_p75 = _make_model("quantile", features, 0.75).fit(X, y)
    duration = time.time() - t0

    origin_counts = df["data_origin"].value_counts().to_dict()
    metrics = {
        "model_version": MODEL_VERSION,
        "architecture": "HistGradientBoostingRegressor (target log harga/MSRP) + Quantile HGB P25/P75",
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sklearn_version": sklearn.__version__,
        "data_scope": scope,
        "dataset_size": int(len(df)),
        "dataset_origin_counts": {k: int(v) for k, v in origin_counts.items()},
        "training_samples": int(len(idx_train)),
        "test_samples": int(len(idx_test)),
        **{k: round(v, 4) for k, v in holdout.items()},
        "baseline_age_median": {k: round(v, 4) for k, v in baseline.items()},
        "cross_val_kfold_mean_r2": round(float(np.mean(cv_r2)), 4),
        "cross_val_kfold_std_r2": round(float(np.std(cv_r2)), 4),
        "cross_val_kfold_mean_mape_pct": round(float(np.mean(cv_mape)), 4),
        "interval_p25_p75_coverage_pct": round(coverage, 2),
        "training_duration_seconds": round(duration, 2),
        "feature_importance": feature_importance,
        "active_features": [FEATURE_LABELS[f] for f in features],
        "dropped_features": {FEATURE_LABELS[f]: why for f, why in dropped_features.items()},
        "n_brands": len(encoder.mapping.get("brand", {})),
        "n_variants_unique_msrp": int(df["msrp"].nunique()),
        "reference_year": current_year,
    }

    bundle = {
        "version": MODEL_VERSION,
        "features": features,
        "encoder_mapping": encoder.mapping,
        "model_median": final_med,
        "model_p25": final_p25,
        "model_p75": final_p75,
        "reference_year": current_year,
        "trained_at": metrics["trained_at"],
        "domain": training_domain(X_raw),
    }
    metrics["training_domain"] = bundle["domain"]

    if save:
        import joblib
        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(bundle, MODEL_PATH, compress=3)
        with open(METRICS_PATH, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

    return bundle, metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Training model valuasi ML MotorPrice ID")
    parser.add_argument("--scope", choices=["live", "all"], default="live")
    args = parser.parse_args()
    with single_thread():
        _, m = train(scope=args.scope)
    print(json.dumps(m, indent=2, ensure_ascii=False))
