"""
Indeks Disparitas Harga Otomotif Multi-Wilayah Indonesia.
Memetakan koefisien disparitas harga pasar motor bekas antar-provinsi dan pulau di Indonesia
berdasarkan faktor biaya logistik, bea balik nama (BBN-KB), dan likuiditas pasar regional.
"""

from typing import Dict, Any, List

REGIONAL_PRICE_INDEX: Dict[str, Dict[str, Any]] = {
    "Jabodetabek (DKI Jakarta, Bogor, Depok, Tangerang, Bekasi)": {
        "multiplier": 1.000,
        "region_code": "JABO",
        "description": "Wilayah acuan standar (Baseline Likuiditas Tertinggi Nasional)",
        "bbn_rate": "12.5%",
        "provinces": ["DKI Jakarta", "Banten (Tangerang)", "Jawa Barat (Depok/Bekasi/Bogor)"]
    },
    "Jawa Barat (Bandung, Cirebon, Tasikmalaya, Karawang, Sukabumi)": {
        "multiplier": 0.985,
        "region_code": "JABAR",
        "description": "Pasar sekunder sangat aktif, harga kompetitif mendekati Jabodetabek",
        "bbn_rate": "12.5%",
        "provinces": ["Jawa Barat"]
    },
    "Jawa Tengah & D.I. Yogyakarta (Semarang, Solo, Jogja, Banyumas)": {
        "multiplier": 0.975,
        "region_code": "JATENG_DIY",
        "description": "Biaya hidup efisien, harga rata-rata motor bekas 2.5% lebih murah dari Jabodetabek",
        "bbn_rate": "12.0%",
        "provinces": ["Jawa Tengah", "D.I. Yogyakarta"]
    },
    "Jawa Timur (Surabaya, Malang, Kediri, Jember, Banyuwangi)": {
        "multiplier": 0.980,
        "region_code": "JATIM",
        "description": "Pusat industri Jawa bagian timur dengan perputaran unit cepat",
        "bbn_rate": "12.5%",
        "provinces": ["Jawa Timur"]
    },
    "Bali & Nusa Tenggara (Denpasar, Badung, Mataram, Kupang)": {
        "multiplier": 1.035,
        "region_code": "BALI_NUSRA",
        "description": "Dampak kebutuhan pariwisata & biaya penyeberangan feri (+3.5%)",
        "bbn_rate": "15.0%",
        "provinces": ["Bali", "Nusa Tenggara Barat", "Nusa Tenggara Timur"]
    },
    "Sumatera (Medan, Palembang, Pekanbaru, Lampung, Padang, Batam)": {
        "multiplier": 1.050,
        "region_code": "SUMATERA",
        "description": "Biaya ekspedisi lintas selat & retensi harga unit seken tangguh (+5.0%)",
        "bbn_rate": "15.0%",
        "provinces": ["Sumatera Utara", "Sumatera Selatan", "Riau", "Lampung", "Sumatera Barat", "Kepulauan Riau", "Aceh", "Jambi", "Bengkulu"]
    },
    "Kalimantan (Balikpapan, Samarinda, Banjarmasin, Pontianak, IKN)": {
        "multiplier": 1.080,
        "region_code": "KALIMANTAN",
        "description": "Biaya kargo kontainer laut & tingginya daya beli sektor komoditas/IKN (+8.0%)",
        "bbn_rate": "15.0%",
        "provinces": ["Kalimantan Timur", "Kalimantan Selatan", "Kalimantan Barat", "Kalimantan Tengah", "Kalimantan Utara"]
    },
    "Sulawesi, Maluku & Papua (Makassar, Manado, Ambon, Jayapura)": {
        "multiplier": 1.095,
        "region_code": "TIMUR_IND",
        "description": "Jarak logistik terjauh dari pabrik perakitan pulau Jawa (+9.5% s/d +15.0%)",
        "bbn_rate": "15.0% - 17.5%",
        "provinces": ["Sulawesi Selatan", "Sulawesi Utara", "Sulawesi Tengah", "Sulawesi Tenggara", "Maluku", "Papua", "Papua Barat"]
    }
}

DEFAULT_REGION = "Jabodetabek (DKI Jakarta, Bogor, Depok, Tangerang, Bekasi)"

def get_region_multiplier(region_name: str) -> float:
    """Mengambil faktor pengali harga regional (default 1.000)."""
    return REGIONAL_PRICE_INDEX.get(region_name, {}).get("multiplier", 1.000)

def get_all_regions() -> List[str]:
    """Mengambil daftar seluruh wilayah regional yang didukung."""
    return list(REGIONAL_PRICE_INDEX.keys())

def apply_regional_pricing(base_price: float, region_name: str) -> Dict[str, Any]:
    """Menghitung harga yang telah disesuaikan dengan indeks regional."""
    region_info = REGIONAL_PRICE_INDEX.get(region_name, REGIONAL_PRICE_INDEX[DEFAULT_REGION])
    multiplier = region_info["multiplier"]
    adjusted_price = base_price * multiplier
    variance_amount = adjusted_price - base_price
    variance_pct = (multiplier - 1.0) * 100.0
    
    return {
        "region_name": region_name,
        "region_code": region_info["region_code"],
        "multiplier": multiplier,
        "base_national_price": base_price,
        "regional_adjusted_price": adjusted_price,
        "variance_amount": variance_amount,
        "variance_pct": round(variance_pct, 1),
        "bbn_rate": region_info["bbn_rate"],
        "description": region_info["description"]
    }
