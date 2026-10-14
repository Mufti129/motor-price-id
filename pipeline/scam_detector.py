import re
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from pipeline.slang_dictionary import DP_SCAM_PATTERNS


class ScamAndDPDetector:
    """
    Detektor Clickbait, Perangkap DP (Down Payment) / Kredit, dan Harga Tidak Wajar.

    Seringkali dealer memasang harga Rp 1.000.000 - Rp 3.000.000 pada motor berharga Rp 20+ juta,
    yang ternyata adalah angka DP kredit, bukan harga tunai (cash). Selain itu terdapat input
    harga tidak masuk akal (nomor telepon, salah ketik digit) yang harus ditolak.

    Lapisan validasi (berurutan):
      1. Harga kosong / nol.
      2. Batas absolut (harga > Rp 2 Miliar = salah input).
      3. Frasa DP eksplisit di teks yang nominalnya sama dengan harga listing (mis. "DP 1.5jt").
      4. Kata kunci DP/Kredit di judul + harga murah relatif terhadap MSRP.
      5. Rasio harga terhadap MSRP resmi:
         - Batas atas: harga bekas > 135% MSRP baru.
         - Batas bawah berbasis usia: harga < MSRP x retensi minimum usia tersebut.
      6. Tanpa MSRP: harga < Rp 2.5 juta SELALU ditolak (menutup celah lama yang hanya
         menolak bila ada kata kunci kredit), dan harga < Rp 5 juta untuk unit usia <= 5 tahun.
    """

    MIN_PLAUSIBLE_CASH_PRICE = 2_500_000      # Di bawah 2.5 juta hampir pasti DP atau rongsokan
    YOUNG_UNIT_MIN_PRICE = 5_000_000          # Unit usia <= 5 tahun di bawah 5 juta = DP / clickbait
    ABSOLUTE_MAX_PRICE = 2_000_000_000        # Di atas 2 Miliar = salah input / nomor telepon
    DP_KEYWORD_PRICE_CEILING = 10_000_000     # Kata kunci DP di judul hanya relevan di harga rendah
    MAX_PRICE_TO_MSRP_RATIO = 1.35            # Harga bekas maksimum 135% dari MSRP baru
    UNKNOWN_AGE_ASSUMPTION = 12               # Usia konservatif bila tahun tidak diketahui

    _DP_AMOUNT_REGEX = re.compile(
        r"\b(?:dp|uang\s*muka|tanda\s*jadi)\s*[:=]?\s*(?:rp\.?\s*)?(\d+(?:[\.,]\d+)*)\s*(jt|juta|rb|ribu|k)?\b"
    )

    @staticmethod
    def min_retention_ratio(age: int) -> float:
        """
        Rasio retensi nilai minimum (harga bekas / MSRP) yang masih wajar untuk usia tertentu.
        Usia 0 -> 50%, berkurang 3 poin per tahun, dengan lantai 15% (unit tua 12+ tahun).
        Ambang ini sengaja konservatif (jauh di bawah median pasar) agar hanya menolak anomali.
        """
        return max(0.15, 0.50 - 0.03 * max(0, age))

    @classmethod
    def _parse_dp_amount(cls, text: str) -> Optional[float]:
        match = cls._DP_AMOUNT_REGEX.search(text)
        if not match:
            return None
        raw_num, unit = match.group(1), (match.group(2) or "")
        try:
            if unit in ("jt", "juta"):
                return float(raw_num.replace(",", ".")) * 1_000_000
            if unit in ("rb", "ribu", "k"):
                return float(raw_num.replace(",", ".")) * 1_000
            return float(raw_num.replace(".", "").replace(",", ""))
        except ValueError:
            return None

    @classmethod
    def evaluate(
        cls,
        price: Optional[float],
        title: str,
        description: str = "",
        expected_market_msrp: Optional[float] = None,
        claimed_year: Optional[int] = None,
        current_year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Evaluasi lengkap validitas harga listing.
        Returns: {"is_invalid": bool, "code": str, "reason": str}
        """
        if price is None or price <= 0:
            return {"is_invalid": True, "code": "PRICE_MISSING", "reason": "Harga kosong atau 0"}

        price = float(price)
        title_l = (title or "").lower()
        combined_text = f"{title or ''} {description or ''}".lower()
        current_year = current_year or datetime.now().year
        age = (current_year - claimed_year) if claimed_year else None
        msrp = float(expected_market_msrp) if expected_market_msrp else None

        # 2. Batas absolut
        if price > cls.ABSOLUTE_MAX_PRICE:
            return {"is_invalid": True, "code": "PRICE_ABSURD",
                    "reason": f"Harga tidak masuk akal ({price:,.0f}), indikasi salah input / nomor telepon"}

        # 3. Frasa DP eksplisit dengan nominal sama dengan harga listing
        dp_amount = cls._parse_dp_amount(combined_text)
        if dp_amount and abs(dp_amount - price) <= max(100_000.0, price * 0.10):
            return {"is_invalid": True, "code": "DP_AMOUNT_MATCH",
                    "reason": f"Harga listing sama dengan nominal DP di teks ({dp_amount:,.0f})"}

        # 4. Kata kunci DP/Kredit di judul + harga murah
        if price < cls.DP_KEYWORD_PRICE_CEILING:
            for pat in DP_SCAM_PATTERNS:
                if re.search(pat, title_l):
                    if msrp is None or price < msrp * 0.35:
                        return {"is_invalid": True, "code": "DP_KEYWORD_TITLE",
                                "reason": f"Mengandung kata kunci DP/Kredit di judul: '{pat}' dengan harga rendah"}
                    break

        # 5. Validasi rasio terhadap MSRP resmi
        if msrp:
            if price > msrp * cls.MAX_PRICE_TO_MSRP_RATIO:
                return {"is_invalid": True, "code": "PRICE_ABOVE_MSRP",
                        "reason": f"Harga {price:,.0f} melebihi {cls.MAX_PRICE_TO_MSRP_RATIO:.0%} MSRP baru ({msrp:,.0f})"}
            eff_age = age if age is not None else cls.UNKNOWN_AGE_ASSUMPTION
            floor = msrp * cls.min_retention_ratio(eff_age)
            if price < floor:
                keyword = next((p for p in DP_SCAM_PATTERNS if re.search(p, combined_text)), None)
                suffix = f" dan terdeteksi kata '{keyword}'" if keyword else ""
                return {"is_invalid": True, "code": "PRICE_BELOW_AGE_FLOOR",
                        "reason": f"Harga {price:,.0f} di bawah batas wajar usia {eff_age} th ({floor:,.0f}){suffix}"}

        # 6. Tanpa MSRP (atau lolos MSRP): batas absolut bawah
        if price < cls.MIN_PLAUSIBLE_CASH_PRICE:
            return {"is_invalid": True, "code": "PRICE_BELOW_MIN",
                    "reason": f"Harga di bawah {cls.MIN_PLAUSIBLE_CASH_PRICE:,.0f} (indikasi DP / clickbait / rongsokan)"}
        if age is not None and age <= 5 and price < cls.YOUNG_UNIT_MIN_PRICE:
            return {"is_invalid": True, "code": "PRICE_BELOW_YOUNG_MIN",
                    "reason": f"Unit usia {age} th dengan harga {price:,.0f} (< {cls.YOUNG_UNIT_MIN_PRICE:,.0f}) indikasi DP"}

        return {"is_invalid": False, "code": "VALID", "reason": "Valid Cash Price"}

    @classmethod
    def is_dp_or_credit_listing(
        cls,
        price: Optional[float],
        title: str,
        description: str = "",
        expected_market_msrp: Optional[float] = None,
        claimed_year: Optional[int] = None,
    ) -> Tuple[bool, str]:
        """
        Evaluasi apakah listing ini adalah DP / Kredit / Clickbait / harga tidak wajar.
        Antarmuka kompatibel dengan versi sebelumnya.
        Returns: (is_dp: bool, reason: str)
        """
        result = cls.evaluate(price, title, description, expected_market_msrp, claimed_year)
        return result["is_invalid"], result["reason"]
