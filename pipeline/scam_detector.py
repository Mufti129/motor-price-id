import re
from typing import Optional, Tuple
from pipeline.slang_dictionary import DP_SCAM_PATTERNS

class ScamAndDPDetector:
    """
    Detektor Clickbait & Perangkap DP (Down Payment) / Kredit.
    Seringkali dealer memasang harga Rp 1.000.000 - Rp 3.000.000 pada motor berharga Rp 20+ juta,
    yang ternyata adalah angka DP kredit, bukan harga tunai (cash).
    """

    # Ambang batas harga minimum wajar untuk motor bekas yang masih utuh (bukan rongsokan)
    MIN_PLAUSIBLE_CASH_PRICE = 2_500_000 # Di bawah 2.5 juta hampir pasti DP atau rongsokan/stnk only lama

    @classmethod
    def is_dp_or_credit_listing(
        cls,
        price: Optional[float],
        title: str,
        description: str = "",
        expected_market_msrp: Optional[float] = None
    ) -> Tuple[bool, str]:
        """
        Evaluasi apakah listing ini adalah DP / Kredit / Clickbait.
        Returns: (is_dp: bool, reason: str)
        """
        if price is None or price <= 0:
            return True, "Harga kosong atau 0"

        combined_text = f"{title} {description}".lower()

        # 1. Cek kata kunci eksplisit DP / Kredit di judul atau awal deskripsi
        for pat in DP_SCAM_PATTERNS:
            if re.search(pat, title.lower()):
                # Jika ada kata DP/Kredit di judul dan harganya sangat murah
                if price < 10_000_000:
                    return True, f"Mengandung kata kunci DP/Kredit di judul: '{pat}'"

        # 2. Cek anomali harga ekstrim dibandingkan estimasi MSRP baru / harga pasaran
        if expected_market_msrp:
            # Jika harga listing kurang dari 20% harga baru untuk motor tahun muda (misal < 20% MSRP)
            if price < (expected_market_msrp * 0.20) and price < 7_000_000:
                # Cek apakah ada kata kredit/angsuran di deskripsi
                for pat in DP_SCAM_PATTERNS:
                    if re.search(pat, combined_text):
                        return True, f"Harga terlalu rendah ({price:,.0f}) dan terdeteksi kata '{pat}'"
                return True, f"Harga anomali ekstrim ({price:,.0f} vs MSRP {expected_market_msrp:,.0f})"

        # 3. Rule of thumb: Harga < 2.5 juta untuk motor matic/sport modern
        if price < cls.MIN_PLAUSIBLE_CASH_PRICE:
            for pat in DP_SCAM_PATTERNS:
                if re.search(pat, combined_text):
                    return True, f"Harga di bawah 2.5jt dan terdeteksi kata kredit/DP"

        return False, "Valid Cash Price"
