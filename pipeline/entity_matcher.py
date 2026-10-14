import re
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

    # Token generik yang tidak membedakan model satu dengan lainnya
    GENERIC_TOKENS = {
        "honda", "yamaha", "suzuki", "kawasaki", "vespa", "piaggio", "series", "new", "all",
        "the", "and", "dan", "standard", "std", "motor", "matic", "sport", "classic", "edition",
    }

    @classmethod
    def model_tokens(cls, model_name: str) -> List[str]:
        raw = re.split(r"[^a-z0-9]+", (model_name or "").lower())
        return [t for t in raw if t and t not in cls.GENERIC_TOKENS and (len(t) >= 3 or any(ch.isdigit() for ch in t))]

    @classmethod
    def title_mentions_model(cls, title: str, model_name: str, aliases: Optional[List[str]] = None) -> bool:
        """True jika judul menyebut token khas model atau salah satu alias varian."""
        t = (title or "").lower()
        compact = re.sub(r"[^a-z0-9]", "", t)
        tokens = cls.model_tokens(model_name)
        for tok in tokens:
            if tok in t or tok in compact:
                return True
        for alias in aliases or []:
            a = alias.strip().lower()
            if a and (a in t or re.sub(r"[^a-z0-9]", "", a) in compact):
                return True
        if not tokens:
            # Nama model pendek (mis. 'LX', 'S'): cocokkan sebagai kata utuh.
            short = [x for x in re.split(r"[^a-z0-9]+", (model_name or "").lower())
                     if x and x not in cls.GENERIC_TOKENS]
            short_2 = [x for x in short if len(x) >= 2]
            if any(re.search(rf"\b{re.escape(x)}\b", t) for x in short_2):
                return True
            # Tidak ada token yang dapat diverifikasi -> jangan menolak
            if not short_2:
                return True
        return False

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

            # 2. Wajib ada token model / alias di judul.
            #    Kata merek saja (mis. 'honda') TIDAK cukup, karena akan meloloskan seluruh
            #    varian merek tersebut dan memicu salah-match (contoh: 'Honda Genio' -> EM1 e:).
            if not self.title_mentions_model(clean_title, item["model_name"], item["aliases_list"]):
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
