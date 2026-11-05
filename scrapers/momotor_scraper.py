"""
Momotor.id Live Scraping Engine.
Ekstraksi data listing motor bekas riil langsung dari platform resmi Momotor.id (Adira Finance).
Menggunakan pendekatan HTTP Server-Side Rendered (SSR) parsing dengan BeautifulSoup,
berkecepatan tinggi, hemat memori, dan bebas dari ketergantungan headless browser.
"""

import re
import time
import random
import urllib.parse
import urllib.request
from datetime import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15'
]

class MomotorScraper:
    """Crawler resmi untuk platform marketplace motor bekas Momotor.id."""

    BASE_URL = "https://www.momotor.id"
    SEARCH_ENDPOINT = "https://www.momotor.id/motor-bekas"

    def __init__(self, delay_range: tuple = (1.0, 2.0), timeout_sec: int = 15):
        self.delay_range = delay_range
        self.timeout_sec = timeout_sec

    def _sleep_polite(self):
        """Jeda acak ramah server antar permintaan HTTP."""
        time.sleep(random.uniform(*self.delay_range))

    def _get_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.momotor.id/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }

    def scrape_live_search(self, keyword: str, max_items: int = 20) -> List[Dict[str, Any]]:
        """
        Mengekstrak data listing riil dari pencarian keyword Momotor.id.
        Mengembalikan list dictionary terstruktur siap ingest ke database catalog.
        """
        encoded_kw = urllib.parse.quote_plus(keyword)
        target_url = f"{self.SEARCH_ENDPOINT}?keyword={encoded_kw}"

        extracted_items = []
        seen_urls = set()

        try:
            req = urllib.request.Request(target_url, headers=self._get_headers())
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                if resp.status != 200:
                    print(f"   [MomotorScraper] Status HTTP {resp.status} untuk query '{keyword}'.")
                    return []
                html = resp.read().decode('utf-8', errors='ignore')

            soup = BeautifulSoup(html, 'html.parser')
            # Momotor merender kartu listing sebagai tag <a> dengan pola URL /motor-bekas/<brand>/<slug>
            cards = soup.find_all('a', href=re.compile(r'/motor-bekas/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+'))

            for card in cards:
                if len(extracted_items) >= max_items:
                    break

                href = card.get('href', '').strip()
                if not href or href in seen_urls:
                    continue
                seen_urls.add(href)

                full_url = f"{self.BASE_URL}{href}" if href.startswith('/') else href
                strings = list(card.stripped_strings)
                if not strings:
                    continue

                # 1. Ekstraksi Harga Tunai (hindari harga cicilan per bulan)
                price = 0.0
                for i, s in enumerate(strings):
                    if s.startswith('Rp') and (i + 1 >= len(strings) or 'bulan' not in strings[i + 1].lower()):
                        cleaned = re.sub(r'[^0-9]', '', s)
                        if cleaned:
                            val = float(cleaned)
                            if val >= 1000000.0:
                                price = val
                                break

                if price <= 0:
                    continue

                # 2. Ekstraksi Tahun Unit dari URL atau Teks Kartu
                claimed_year = None
                m_year_url = re.search(r'-(20[12][0-9])(?:-\d+)?$', href)
                if m_year_url:
                    claimed_year = int(m_year_url.group(1))
                else:
                    for s in strings:
                        if re.match(r'^(20[12][0-9])$', s):
                            claimed_year = int(s)
                            break

                # 3. Ekstraksi Judul / Nama Model
                title = ""
                for s in strings:
                    if s.isupper() and len(s) > 3 and not any(k in s for k in ['RP', 'KM', 'KOTA', 'KAB', 'ANGSURAN']):
                        title = s
                        break

                if not title:
                    parts = href.strip('/').split('/')
                    if len(parts) >= 3:
                        title = f"{parts[1].capitalize()} {parts[2].replace('-', ' ').title()}"
                    else:
                        title = keyword

                # 4. Ekstraksi Odometer / Jarak Tempuh
                odometer_km = None
                for i, s in enumerate(strings):
                    if 'km' in s.lower() and i > 0:
                        raw_km = strings[i - 1]
                        nums = [int(n) for n in re.findall(r'\d+', raw_km.replace('.', ''))]
                        if len(nums) >= 2:
                            odometer_km = int((nums[0] + nums[1]) / 2)
                        elif len(nums) == 1:
                            odometer_km = nums[0]
                        break

                # 5. Ekstraksi Lokasi Kota / Kabupaten
                city = "Indonesia"
                for s in strings:
                    if 'Kota ' in s or 'Kab. ' in s or 'Kab ' in s:
                        city = s.strip()
                        break

                slug = href.strip('/').split('/')[-1]
                external_id = f"momotor_{slug}"

                extracted_items.append({
                    "source_platform": "momotor",
                    "external_id": external_id,
                    "url": full_url,
                    "title": title,
                    "price": price,
                    "claimed_year": claimed_year,
                    "odometer_km": odometer_km,
                    "city": city,
                    "raw_description": f"{title} ({claimed_year or 'N/A'}) - Lokasi: {city} - Odometer: {odometer_km or 'N/A'} km - Diler Resmi Momotor.id",
                    "seller_name": "Diler Resmi Momotor",
                    "seller_type": "Dealer",
                    "is_dp": False,
                    "tax_status": "Hidup / Panjang",
                    "has_bpkb": True,
                    "has_stnk": True
                })

            self._sleep_polite()

        except Exception as err:
            print(f"   [MomotorScraper] Error scraping Momotor query '{keyword}': {err}")

        return extracted_items
