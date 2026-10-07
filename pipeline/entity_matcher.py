from typing import Optional, List, Dict, Any, Tuple
from rapidfuzz import fuzz
from sqlalchemy.orm import Session
from models.catalog import MasterVariant, MasterModel, MasterBrand

class EntityMatcher:
    """
    Fuzzy Entity Matcher & Disambiguation Engine.
    Menghubungkan teks judul listing liar ke ID Varian Master yang tepat.
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self._variants_cache = self._load_variants()

    def _load_variants(self) -> List[Dict[str, Any]]:
        """Pre-cache master variants dengan metadata lengkap untuk pencocokan cepat."""
        variants = self.db.query(
            MasterVariant, MasterModel, MasterBrand
        ).join(
            MasterModel, MasterVariant.model_id == MasterModel.id
        ).join(
            MasterBrand, MasterModel.brand_id == MasterBrand.id
        ).all()

        cache = []
        for var, model, brand in variants:
            alias_list = [a.strip().lower() for a in (var.aliases or "").split(",") if a.strip()]
            search_corpus = [
                f"{brand.name} {model.name} {var.variant_name}".lower(),
                f"{model.name} {var.variant_name}".lower(),
                var.variant_name.lower()
            ] + alias_list

            cache.append({
                "variant_id": var.id,
                "variant_name": var.variant_name,
                "model_name": model.name,
                "brand_name": brand.name,
                "aliases_list": alias_list,
                "start_year": var.release_year_start,
                "end_year": var.release_year_end or 2026,
                "official_msrp": float(var.official_msrp_new) if var.official_msrp_new else None,
                "search_corpus": search_corpus
            })
        return cache

    def match(self, title: str, claimed_year: Optional[int] = None) -> Tuple[Optional[int], float, Optional[str]]:
        """
        Mencocokkan judul listing ke Master Variant ID.
        Returns: (variant_id: int | None, confidence_score: float, matched_name: str | None)
        """
        clean_title = title.lower()
        # Normalisasi typo umum merk di awal
        clean_title = clean_title.replace("pagio", "piaggio").replace("piagio", "piaggio")
        best_match_id = None
        best_score = 0.0
        best_name = None

        for item in self._variants_cache:
            # 1. Filter tahun jika ada (toleransi +/- 1 tahun untuk masa transisi STNK)
            if claimed_year:
                if not (item["start_year"] - 1 <= claimed_year <= item["end_year"] + 1):
                    continue

            # 2. Cek apakah model name / brand name / alias ada dalam judul
            model_keyword = item["model_name"].lower()
            brand_keyword = item["brand_name"].lower().split()[0]
            has_keyword = (
                model_keyword in clean_title or
                brand_keyword in clean_title or
                any(alias in clean_title for alias in item["aliases_list"])
            )
            if not has_keyword:
                continue

            # 3. Hitung fuzzy match score dengan seluruh alias dan nama varian
            for corpus_text in item["search_corpus"]:
                score_token = fuzz.token_set_ratio(corpus_text, clean_title)
                score_partial = fuzz.partial_ratio(corpus_text, clean_title)
                final_score = (score_token * 0.7) + (score_partial * 0.3)

                if final_score > best_score:
                    best_score = final_score
                    best_match_id = item["variant_id"]
                    best_name = f"{item['brand_name']} {item['model_name']} - {item['variant_name']}"

        # Threshold kepercayaan minimum 60%
        if best_score >= 60.0:
            return best_match_id, best_score, best_name

        return None, 0.0, None
