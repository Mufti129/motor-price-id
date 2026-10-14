"""
Klasifikasi Asal-Usul Data (Data Provenance) untuk listing ScrapedListing.

Aturan diturunkan langsung dari pola ID yang dihasilkan oleh kode sumber repositori ini,
sehingga dapat diverifikasi ulang secara deterministik:

SYNTHETIC (data hasil generator / template, bukan iklan nyata):
  - external_id 'gen_*'        -> data/generate_massive_market_dataset.py
  - external_id 'olx_exp_*'    -> scrapers/expand_all_clean.py & expand_massive_all_platforms.py
  - external_id 'olx_9xxxxxxxx' dengan URL pencarian '/q-' -> fallback template OLXMotorScraper._generate_realistic_feed

LIVE_SCRAPED (iklan nyata yang dapat dibuka/diverifikasi URL-nya):
  - URL detail iklan Facebook Marketplace '/marketplace/item/<id>'
  - URL detail iklan Momotor 'momotor.id/motor-bekas/<brand>/<slug>'
  - URL detail iklan OLX '/item/<id>' (hasil API resmi OLX)
"""

import re
from typing import Optional

ORIGIN_LIVE = "LIVE_SCRAPED"
ORIGIN_SYNTHETIC = "SYNTHETIC"

_LIVE_URL_PATTERNS = [
    re.compile(r"facebook\.com/marketplace/item/\d+", re.IGNORECASE),
    re.compile(r"momotor\.id/motor-bekas/[^/]+/[^/?#]+", re.IGNORECASE),
    re.compile(r"olx\.co\.id/item/[\w-]+", re.IGNORECASE),
]


def classify_origin(external_id: Optional[str], url: Optional[str]) -> str:
    ext = (external_id or "").strip().lower()
    link = (url or "").strip()

    if ext.startswith("gen_") or ext.startswith("olx_exp_"):
        return ORIGIN_SYNTHETIC
    if "/motor-bekas_c200/q-" in link:
        # URL halaman pencarian, bukan iklan individual -> template fallback
        return ORIGIN_SYNTHETIC
    for pat in _LIVE_URL_PATTERNS:
        if pat.search(link):
            return ORIGIN_LIVE
    return ORIGIN_SYNTHETIC
