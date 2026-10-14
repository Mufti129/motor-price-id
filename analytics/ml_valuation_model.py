"""
Mesin Inferensi Valuasi Machine Learning MotorPrice ID.

Memuat model HistGradientBoosting yang BENAR-BENAR dilatih oleh
analytics/train_valuation_model.py (artefak: models/saved_models/valuation_hgb.joblib)
beserta metrik evaluasi riil (models/saved_models/valuation_metrics.json).

Tidak ada metrik yang di-hardcode: seluruh angka R2/MAE/RMSE/MAPE/feature importance
dibaca dari hasil training. Bila artefak tidak dapat dimuat (mis. beda versi scikit-learn
di server), modul ini melatih ulang model dari database secara otomatis; bila itu pun gagal,
modul beralih ke formula depresiasi parametrik dan menandainya secara eksplisit
(is_trained_model = False) agar UI tidak menampilkan klaim ML palsu.
"""

import os
import json
import math
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger("ml_valuation")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "saved_models", "valuation_hgb.joblib")
METRICS_PATH = os.path.join(BASE_DIR, "models", "saved_models", "valuation_metrics.json")

FALLBACK_METRICS = {
    "model_version": "fallback-parametric",
    "architecture": "Formula depresiasi parametrik (model ML belum tersedia)",
    "trained_at": None,
    "data_scope": None,
    "dataset_size": 0,
    "training_samples": 0,
    "test_samples": 0,
    "r2_score": None,
    "mae_idr": None,
    "rmse_idr": None,
    "mape_pct": None,
    "cross_val_kfold_mean_r2": None,
    "training_duration_seconds": 0.0,
    "feature_importance": {},
}


class MLValuationModel:
    """Wrapper inferensi untuk model valuasi terlatih (dengan fallback yang transparan)."""

    def __init__(self, auto_load: bool = True):
        self.bundle: Optional[Dict[str, Any]] = None
        self.evaluation_metrics: Dict[str, Any] = dict(FALLBACK_METRICS)
        self.load_error: Optional[str] = None
        if auto_load:
            self.load()

    # ------------------------------------------------------------------ loading
    def load(self, allow_retrain: bool = True) -> bool:
        if os.path.exists(METRICS_PATH):
            try:
                with open(METRICS_PATH, "r", encoding="utf-8") as f:
                    self.evaluation_metrics = json.load(f)
            except Exception as exc:  # pragma: no cover
                self.load_error = f"Gagal membaca metrik: {exc}"

        if os.path.exists(MODEL_PATH):
            try:
                import joblib
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self.bundle = joblib.load(MODEL_PATH)
                return True
            except Exception as exc:
                self.load_error = f"Gagal memuat artefak model: {exc}"
                logger.warning(self.load_error)

        if allow_retrain:
            try:
                from analytics.train_valuation_model import fit_bundle_only, single_thread
                with single_thread():
                    self.bundle = fit_bundle_only(scope=self.evaluation_metrics.get("data_scope") or "live")
                self.load_error = None
                return True
            except Exception as exc:
                self.load_error = f"Gagal melatih ulang model: {exc}"
                logger.warning(self.load_error)
        self.bundle = None
        return False

    @property
    def is_trained_model(self) -> bool:
        return self.bundle is not None

    # Kompatibilitas atribut lama yang dipakai UI
    @property
    def version(self) -> str:
        return self.evaluation_metrics.get("model_version", "unknown")

    @property
    def trained_date(self) -> str:
        return self.evaluation_metrics.get("trained_at") or "-"

    @property
    def dataset_size(self) -> int:
        return int(self.evaluation_metrics.get("dataset_size") or 0)

    # ---------------------------------------------------------------- inference
    def _feature_row(self, claimed_year: int, odometer_km: Optional[int], engine_cc: int,
                     tax_status: str, has_bpkb: bool, brand: str, category: str,
                     current_year: int) -> pd.DataFrame:
        from analytics.train_valuation_model import derive_segment
        tax = tax_status or "Unknown"
        row = {
            "age": max(0, current_year - int(claimed_year)),
            "odometer_km": float(odometer_km) if odometer_km is not None else np.nan,
            "engine_cc": float(engine_cc or 0),
            "is_ev": int((engine_cc or 0) == 0),
            "has_bpkb": int(bool(has_bpkb)),
            "tax_off": int(("Mati" in tax) or ("Off" in tax)),
            "tax_unknown": int("Unknown" in tax),
            "brand": brand or "UNKNOWN",
            "segment": derive_segment(category, engine_cc),
        }
        return pd.DataFrame([row])

    def domain_check(self, brand: Optional[str], segment: str, age: int) -> Optional[str]:
        """Kembalikan alasan bila input berada di luar cakupan data latih (None = dalam domain)."""
        dom = (self.bundle or {}).get("domain")
        if not dom:
            return None
        if brand and brand not in dom["brands"]:
            return f"Merek '{brand}' tidak ada dalam data latih"
        if segment not in dom["segments"]:
            return f"Segmen '{segment}' tidak ada dalam data latih"
        if not (dom["age_min"] <= age <= dom["age_max"]):
            return f"Usia {age} th di luar rentang data latih ({dom['age_min']}-{dom['age_max']} th)"
        return None

    def predict_valuation(
        self,
        msrp_new: float,
        claimed_year: int,
        odometer_km: Optional[int] = None,
        engine_cc: int = 125,
        tax_status: str = "Unknown",
        has_bpkb: bool = True,
        sector: str = "ICE Konvensional",
        current_year: Optional[int] = None,
        brand: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Prediksi harga wajar (median) beserta interval P25-P75."""
        current_year = current_year or datetime.now().year
        out_of_domain = None
        if self.is_trained_model and msrp_new:
            b = self.bundle
            X_raw = self._feature_row(claimed_year, odometer_km, engine_cc, tax_status, has_bpkb,
                                      brand or "UNKNOWN", category or sector, current_year)
            out_of_domain = self.domain_check(brand, X_raw["segment"].iloc[0], int(X_raw["age"].iloc[0]))
        if self.is_trained_model and msrp_new and not out_of_domain:
            from analytics.train_valuation_model import single_thread, monotone_predict
            # Proyeksi monoton (isotonik) terhadap usia: unit yang lebih tua tidak pernah dinilai
            # lebih mahal daripada unit yang lebih muda dengan spesifikasi sama (lihat monotone_predict).
            X = X_raw.copy()
            for col, mp in b["encoder_mapping"].items():
                X[col] = X[col].map(mp).astype(float)
            X = X[b["features"]].to_numpy(dtype=float)
            age_lo = int((b.get("domain") or {}).get("age_min", 0))
            with single_thread():
                med = float(np.exp(monotone_predict(b["model_median"], X, b["features"], age_lo)[0]) * msrp_new)
                p25 = float(np.exp(monotone_predict(b["model_p25"], X, b["features"], age_lo)[0]) * msrp_new)
                p75 = float(np.exp(monotone_predict(b["model_p75"], X, b["features"], age_lo)[0]) * msrp_new)
            lo, hi = min(p25, p75), max(p25, p75)
            return {
                "model_version": self.version,
                "is_trained_model": True,
                "out_of_domain": None,
                "predicted_fmv": med,
                "predicted_p25_bargain": min(lo, med),
                "predicted_p75_premium": max(hi, med),
                "retention_ratio": med / msrp_new,
                "features_used": b["features"],
            }

        # Fallback parametrik (ditandai eksplisit, bukan model ML)
        age = max(0, current_year - int(claimed_year))
        decay = max(0.28, min(0.95, 1.0 - (0.175 * (1.0 - math.exp(-0.45 * age)) + 0.052 * age)))
        base = (msrp_new or 0) * decay
        if not has_bpkb:
            base *= 0.65
        return {
            "model_version": "fallback-parametric",
            "is_trained_model": False,
            "out_of_domain": out_of_domain,
            "predicted_fmv": base,
            "predicted_p25_bargain": base * 0.93,
            "predicted_p75_premium": base * 1.07,
            "retention_ratio": decay,
            "features_used": ["age", "has_bpkb"],
        }

    def forecast_residual_value_curve(
        self,
        current_fmv: float,
        claimed_year: int = 2022,
        engine_cc: int = 125,
        sector: str = "ICE Konvensional",
        msrp_new: Optional[float] = None,
        brand: Optional[str] = None,
        current_year: Optional[int] = None,
        *args,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Proyeksi nilai sisa 0/6/12/24/36 bulan.
        Jika model terlatih & MSRP tersedia: laju penyusutan diambil dari kurva retensi model
        (prediksi rasio retensi pada usia +h dibanding usia sekarang), lalu diterapkan ke FMV saat ini.
        Jika tidak: laju tahunan parametrik per sektor.
        """
        try:
            current_fmv = float(current_fmv) if current_fmv is not None else 15_000_000.0
        except (TypeError, ValueError):
            current_fmv = 15_000_000.0

        try:
            claimed_year = int(claimed_year) if claimed_year is not None else 2022
        except (TypeError, ValueError):
            claimed_year = 2022

        try:
            engine_cc = int(engine_cc) if engine_cc is not None else 125
        except (TypeError, ValueError):
            engine_cc = 125

        if msrp_new is not None:
            try:
                msrp_new = float(msrp_new)
            except (TypeError, ValueError):
                msrp_new = None

        sector = str(sector or "ICE Konvensional")
        brand = str(brand) if brand else None

        current_year = current_year or datetime.now().year
        horizons = [
            ("Saat Ini (Baseline)", 0), ("6 Bulan Mendatang", 6), ("12 Bulan (1 Tahun)", 12),
            ("24 Bulan (2 Tahun)", 24), ("36 Bulan (3 Tahun)", 36),
        ]

        use_model = False
        if self.is_trained_model and msrp_new:
            try:
                now_pred = self.predict_valuation(msrp_new, claimed_year, engine_cc=engine_cc, brand=brand,
                                                  category=sector, current_year=current_year)
                far_pred = self.predict_valuation(msrp_new, claimed_year - 4, engine_cc=engine_cc, brand=brand,
                                                  category=sector, current_year=current_year)
                use_model = bool(now_pred.get("is_trained_model") and far_pred.get("is_trained_model"))
                base_ret = float(now_pred.get("retention_ratio", 1.0))
            except Exception as e_pred:
                logger.debug(f"Fallback forecast ke parametrik: {e_pred}")
                use_model = False

        if not use_model:
            s = sector or ""
            annual = 0.055 if ("Moge" in s or "Retro" in s) else (0.095 if "EV" in s else 0.068)

        points = []
        prev_factor = 1.0
        for label, months in horizons:
            if use_model and months > 0:
                try:
                    # Retensi pada usia lebih tua: geser tahun produksi mundur (interpolasi linear antar tahun)
                    yrs = months / 12.0
                    y_lo, frac = int(math.floor(yrs)), yrs - math.floor(yrs)
                    r_lo = float(self.predict_valuation(msrp_new, claimed_year - y_lo, engine_cc=engine_cc, brand=brand,
                                                        category=sector, current_year=current_year).get("retention_ratio", 1.0))
                    r_hi = float(self.predict_valuation(msrp_new, claimed_year - y_lo - 1, engine_cc=engine_cc, brand=brand,
                                                        category=sector, current_year=current_year).get("retention_ratio", 1.0))
                    factor = ((1 - frac) * r_lo + frac * r_hi) / base_ret if base_ret > 0 else 1.0
                    factor = min(prev_factor, factor)  # nilai sisa tidak boleh naik seiring waktu
                except Exception:
                    factor = math.exp(-0.068 * months / 12.0)
            elif months > 0:
                factor = math.exp(-annual * months / 12.0)
            else:
                factor = 1.0
            prev_factor = factor
            future_price = max(3_000_000.0, current_fmv * factor)
            points.append({
                "horizon_label": label,
                "months_ahead": months,
                "projected_timeline": f"{current_year + (months // 12)}" + (" (+6 bln)" if months % 12 else "")
                                      if months else f"{current_year} (Now)",
                "forecasted_price": round(future_price, -4),
                "retention_pct": round(factor * 100.0, 1),
                "depreciation_pct": round((1 - future_price / current_fmv) * 100.0, 1) if current_fmv > 0 else 0.0,
                "method": "ML (kurva retensi model terlatih)" if use_model else "Parametrik (di luar cakupan data latih)",
            })
        return points


# Global Singleton Instance (nama lama dipertahankan untuk kompatibilitas impor)
ml_model = MLValuationModel()
ml_model_v6 = ml_model
MLValuationModelV6 = MLValuationModel
