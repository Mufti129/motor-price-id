"""
IBID Astra MAP (Market Auction Price) API Client SDK
Khusus Data Mobil & Kendaraan Roda Empat (Wholesale Auction Engine)
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any
import requests

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("IbidMapClient")


class IbidMapClient:
    """Client SDK untuk berinteraksi dengan REST API backend IBID MAP Astra."""

    BASE_URL = "https://api.ibid.astra.co.id/backend-dc-map"
    MAP_BE_URL = "https://api.ibid.astra.co.id/map-be"

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": "5c425b903b2b49b48f5edf10ce95616b",
            "secret_key_map": "stf57d68ag79d8uajd081n09dasdjjin9a87gfy6098h9d78s6f756crsafygud",
            "client_id_map": "0000000000001",
            "Referer": "https://map.ibid.astra.co.id/",
            "Origin": "https://map.ibid.astra.co.id"
        })

    def get_brands(self) -> List[Dict[str, Any]]:
        """Mengambil daftar seluruh merek mobil di database IBID MAP."""
        url = f"{self.BASE_URL}/services/stock/master-data-merk"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", []) if isinstance(data, dict) else data
        except Exception as e:
            logger.error(f"Gagal mengambil master merek: {e}")
            return []

    def get_variants(self, merk: str, seri: Optional[str] = None) -> List[Dict[str, Any]]:
        """Mengambil daftar varian, silinder, tipe, tahun, dan lokasi berdasarkan merek & seri."""
        url = f"{self.BASE_URL}/services/map/stock/get/variant"
        params = {"merk": merk.upper()}
        if seri:
            params["seri"] = seri.upper()
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return data if isinstance(data, list) else data.get("data", [])
        except Exception as e:
            logger.error(f"Gagal mengambil varian untuk {merk} {seri}: {e}")
            return []

    def check_price(
        self,
        merk: str,
        seri: str,
        silinder: str,
        tipe: str,
        tahun: str,
        transmisi: str = "MT"
    ) -> Dict[str, Any]:
        """
        Mengecek estimasi harga pasar kendaraan lelang (min & max harga).
        """
        url = f"{self.BASE_URL}/services/map/check-price"
        payload = {
            "merk": str(merk).upper(),
            "seri": str(seri).upper(),
            "silinder": str(silinder),
            "tipe": str(tipe).upper(),
            "tahun": str(tahun),
            "transmisi": str(transmisi).upper()
        }
        try:
            resp = self.session.post(url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}) if data.get("status") else {}
        except Exception as e:
            logger.error(f"Gagal cek harga {merk} {seri} {tahun}: {e}")
            return {}

    def get_price_by_grade(
        self,
        brand: str,
        series: str,
        cylinder: str,
        tipe: str,
        year: str,
        transmission: str = "MT"
    ) -> Dict[str, Any]:
        """
        Mengambil rincian harga pasar terbentuk berdasarkan Grade Kondisi ACV (Grade A, B, C, D).
        """
        url = f"{self.BASE_URL}/services/price/unit-condition/get"
        params = {
            "brand": str(brand).upper(),
            "series": str(series).upper(),
            "cylinder": str(cylinder),
            "type": str(tipe).upper(),
            "year": str(year),
            "transmission": str(transmission).upper()
        }
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}) if isinstance(data, dict) else {}
        except Exception as e:
            logger.error(f"Gagal mengambil harga per grade {brand} {series}: {e}")
            return {}

    def get_price_trend_by_time(
        self,
        brand: str,
        series: str,
        cylinder: str,
        tipe: str,
        year: str,
        transmission: str = "MT"
    ) -> Dict[str, Any]:
        """
        Mengambil grafik pergerakan tren harga lelang dari waktu ke waktu.
        """
        url = f"{self.BASE_URL}/services/price/time/get"
        params = {
            "brand": str(brand).upper(),
            "series": str(series).upper(),
            "cylinder": str(cylinder),
            "type": str(tipe).upper(),
            "year": str(year),
            "transmission": str(transmission).upper()
        }
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}) if isinstance(data, dict) else {}
        except Exception as e:
            logger.error(f"Gagal mengambil tren waktu {brand} {series}: {e}")
            return {}

    def get_price_by_city(
        self,
        brand: str,
        series: str,
        cylinder: str,
        tipe: str,
        year: str,
        transmission: str = "MT"
    ) -> Dict[str, Any]:
        """
        Mengambil distribusi harga lelang berdasarkan kota/area cabang IBID di Indonesia.
        """
        url = f"{self.BASE_URL}/services/price/area-city/get"
        params = {
            "brand": str(brand).upper(),
            "series": str(series).upper(),
            "cylinder": str(cylinder),
            "type": str(tipe).upper(),
            "year": str(year),
            "transmission": str(transmission).upper()
        }
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {}) if isinstance(data, dict) else {}
        except Exception as e:
            logger.error(f"Gagal mengambil harga per kota {brand} {series}: {e}")
            return {}

    def get_popular_vehicles(self) -> List[Dict[str, Any]]:
        """Mengambil data pencarian unit mobil terpopuler di IBID MAP."""
        url = f"{self.MAP_BE_URL}/services/popular"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", []) if isinstance(data, dict) else []
        except Exception as e:
            logger.error(f"Gagal mengambil kendaraan populer: {e}")
            return []
