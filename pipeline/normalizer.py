import re
from typing import Dict, Any, Optional, Tuple
from pipeline.slang_dictionary import TAX_PATTERNS, DOCUMENT_PATTERNS, PLATE_PATTERNS, PRICE_SLANG_PATTERNS

class ListingNormalizer:
    """
    Ekstraktor dan Normalizer Teks Listing Motor Bekas Indonesia.
    Mengubah deskripsi tidak terstruktur menjadi metadata bersih dan terstandarisasi.
    """

    @staticmethod
    def parse_price(raw_val: Any) -> Optional[float]:
        """Konversi berbagai variasi representasi harga ke float bersih."""
        if raw_val is None:
            return None
        if isinstance(raw_val, (int, float)):
            return float(raw_val)

        text = str(raw_val).strip().lower()
        # Hapus prefix umum seperti 'rp', 'rp.', 'idr', 'harga:'
        text = re.sub(r"^(?:rp\.?|idr|harga:?)\s*", "", text)

        for pattern, multiplier in PRICE_SLANG_PATTERNS:
            match = re.search(pattern, text)
            if match:
                num_str = match.group(1).replace(",", ".")
                try:
                    return float(num_str) * multiplier
                except ValueError:
                    pass

        # Pembersihan angka standar dengan titik/koma (e.g. "18.500.000" atau "18,500,000")
        clean_num = re.sub(r"[^\d]", "", text)
        if clean_num:
            try:
                return float(clean_num)
            except ValueError:
                return None
        return None

    @staticmethod
    def extract_year(text: str) -> Optional[int]:
        """Ekstraksi tahun pembuatan motor dari judul atau deskripsi (1990 - 2026)."""
        matches = re.findall(r"\b(199\d|20[0-2]\d)\b", text)
        if matches:
            # Ambil tahun yang paling masuk akal (biasanya tahun pertama jika di judul)
            years = [int(m) for m in matches if 1995 <= int(m) <= 2026]
            if years:
                return years[0]
        return None

    @staticmethod
    def extract_tax_status(text: str) -> Tuple[str, Optional[int]]:
        """
        Ekstraksi status pajak.
        Returns: (tax_status: 'Hidup / Panjang' | 'Mati / Off' | 'Unknown', years_off: int | None)
        """
        lower_text = text.lower()

        # Cek pola pajak mati dulu
        for pat in TAX_PATTERNS["mati"]:
            match = re.search(pat, lower_text)
            if match:
                years_off = None
                if match.groups() and match.group(1):
                    try:
                        years_off = int(match.group(1))
                    except ValueError:
                        pass
                return "Mati / Off", years_off

        # Cek pola pajak hidup
        for pat in TAX_PATTERNS["hidup"]:
            if re.search(pat, lower_text):
                return "Hidup / Panjang", 0

        return "Unknown", None

    @staticmethod
    def extract_documents(text: str) -> Tuple[bool, bool]:
        """
        Ekstraksi kelengkapan surat.
        Returns: (has_bpkb: bool, has_stnk: bool)
        """
        lower_text = text.lower()

        # Cek indikator STNK Only / Batangan
        for pat in DOCUMENT_PATTERNS["stnk_only"]:
            if re.search(pat, lower_text):
                return False, True # BPKB tidak ada, STNK ada

        # Cek indikator komplit
        for pat in DOCUMENT_PATTERNS["lengkap"]:
            if re.search(pat, lower_text):
                return True, True

        # Default diasumsikan lengkap jika tidak ada klausa khusus
        return True, True

    @staticmethod
    def extract_plate_region(text: str) -> Optional[str]:
        """Ekstraksi kode plat nomor daerah (misal Plat B, Plat D, Plat AB)."""
        for pat in PLATE_PATTERNS:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        return None

    @staticmethod
    def extract_odometer(text: str) -> Optional[int]:
        """Ekstraksi jarak tempuh (KM/Odometer)."""
        lower_text = text.lower()
        km_match = re.search(r"\b(?:km|odometer|jarak)\s*[:\s]?\s*(\d+(?:[\.,]\d+)?)\s*(?:rb|k|ribu)?\b", lower_text)
        if km_match:
            val_str = km_match.group(1).replace(".", "").replace(",", "")
            try:
                val = int(val_str)
                if "rb" in km_match.group(0) or "k" in km_match.group(0) or "ribu" in km_match.group(0):
                    val *= 1000
                if 0 <= val <= 300000: # Range KM motor wajar
                    return val
            except ValueError:
                pass
        return None

    @classmethod
    def normalize_listing(cls, raw_listing: Dict[str, Any]) -> Dict[str, Any]:
        """Proses normalisasi lengkap untuk 1 listing mentah."""
        combined_text = f"{raw_listing.get('title', '')} {raw_listing.get('description', '')}"

        # 1. Parsing Harga
        clean_price = cls.parse_price(raw_listing.get("price"))

        # 2. Parsing Tahun
        year = raw_listing.get("year")
        if not year:
            year = cls.extract_year(raw_listing.get("title", "")) or cls.extract_year(raw_listing.get("description", ""))

        # 3. Status Pajak & Dokumen
        tax_status, years_off = cls.extract_tax_status(combined_text)
        has_bpkb, has_stnk = cls.extract_documents(combined_text)

        # 4. Plat & Odometer
        plate = cls.extract_plate_region(combined_text)
        odometer = raw_listing.get("odometer") or cls.extract_odometer(combined_text)

        return {
            "source_platform": raw_listing.get("source_platform", "unknown"),
            "external_id": str(raw_listing.get("external_id", "")),
            "url": raw_listing.get("url", ""),
            "title": raw_listing.get("title", "").strip(),
            "raw_description": raw_listing.get("description", ""),
            "claimed_year": year,
            "price": clean_price,
            "odometer_km": odometer,
            "tax_status": tax_status,
            "tax_expiry_year": None,
            "has_bpkb": has_bpkb,
            "has_stnk": has_stnk,
            "plate_region": plate,
            "province": raw_listing.get("province"),
            "city": raw_listing.get("city"),
            "district": raw_listing.get("district"),
            "seller_name": raw_listing.get("seller_name"),
            "seller_type": raw_listing.get("seller_type", "Individual"),
            "posted_at": raw_listing.get("posted_at")
        }
