#!/usr/bin/env python3
"""
Production-Grade OLX Stealth Scraping Engine untuk Pasar Kendaraan Bekas Indonesia.
Mengadopsi pola arsitektur scrap_olx:
1. Browser Headless Automation (Selenium Chrome) dengan simulasi sidik jari pengguna asli.
2. Traversal URL Slug publik (/q-{slug}) untuk menembus proteksi Cloudflare/WAF OLX.
3. Deteksi & penanganan tombol paginasi dinamis (btnLoadMore).
4. Pembersihan frasa rancu ("Pertamax Turbo") dan deteksi surat & status pajak terpadu.
5. Mode Single Search (on-demand) & Mode Matrix Batch (resumable bucket tracking).
"""

import os
import sys
import re
import time
import random
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from pipeline.scam_detector import ScamAndDPDetector

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

CATEGORIES = {
    "motor": {
        "name": "Motor Bekas",
        "base_url": "https://www.olx.co.id/motor-bekas_c200",
    },
    "mobil": {
        "name": "Mobil Bekas",
        "base_url": "https://www.olx.co.id/mobil-bekas_c198",
    }
}

class OLXStealthScraper:
    """Mesin scraper headless stealth untuk OLX Indonesia."""

    def __init__(self, headless: bool = True, delay_range: tuple = (1.5, 3.0), timeout: int = 25):
        self.headless = headless
        self.delay_range = delay_range
        self.timeout = timeout
        self.driver = None

    def _init_driver(self):
        """Membuat instance Chrome WebDriver dengan argumen stealth anti-deteksi."""
        opts = Options()
        opts.page_load_strategy = "eager"
        if self.headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--disable-infobars")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1366,768")
        opts.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)

        driver = webdriver.Chrome(options=opts)
        driver.set_page_load_timeout(self.timeout)
        self.driver = driver
        return driver

    def close(self):
        """Menutup browser driver."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    def _sleep_human(self):
        """Jeda acak ramah server."""
        time.sleep(random.uniform(*self.delay_range))

    @staticmethod
    def _create_query_slug(keyword: str) -> str:
        """Membuat slug pencarian yang aman untuk URL OLX."""
        clean = re.sub(r"[^a-z0-9]+", "-", keyword.strip().lower()).strip("-")
        return clean

    @staticmethod
    def _clean_price(price_str: str) -> Optional[float]:
        if not price_str:
            return None
        nums = re.findall(r"\d+", price_str.replace(".", "").replace(",", ""))
        if nums:
            try:
                return float(nums[0])
            except ValueError:
                return None
        return None

    def _extract_detail_page(self, item_url: str, category: str = "motor") -> Optional[Dict[str, Any]]:
        """Membuka halaman detail iklan OLX dan mengekstrak field terstruktur."""
        if not self.driver:
            self._init_driver()

        try:
            self.driver.get(item_url)
        except Exception:
            try:
                self.driver.execute_script("window.stop();")
            except Exception:
                return None

        self._sleep_human()

        # Ekstraksi judul
        title = ""
        title_elem = None
        for sel in ['h1[data-aut-id="itemTitle"]', 'h1', 'div[data-aut-id="itemTitle"]']:
            elems = self.driver.find_elements(By.CSS_SELECTOR, sel)
            if elems and elems[0].text.strip():
                title = elems[0].text.strip()
                title_elem = elems[0]
                break

        if not title:
            # Fallback ambil dari title tag
            page_title = self.driver.title
            if page_title and "olx" not in page_title.lower()[:10]:
                title = page_title.split("|")[0].split("-")[0].strip()

        if not title:
            return None

        body_text = ""
        try:
            body_text = self.driver.find_element(By.TAG_NAME, "body").text
        except Exception:
            pass

        # Ekstraksi harga: Cari dari container/section yang sama dengan judul untuk menghindari carousel iklan lain
        price = None
        if title_elem:
            p_curr = title_elem
            for _ in range(4):
                try:
                    p_curr = p_curr.find_element(By.XPATH, "..")
                    p_elems = p_curr.find_elements(By.CSS_SELECTOR, 'span[data-aut-id="itemPrice"], h2[data-aut-id="itemPrice"], span[class*="price"]')
                    if p_elems:
                        for pe in p_elems:
                            cand = self._clean_price(pe.text)
                            if cand and cand >= 1000000:
                                price = cand
                                break
                    if price:
                        break
                except Exception:
                    break

        if not price:
            for sel in ['span[data-aut-id="itemPrice"]', 'h2[data-aut-id="itemPrice"]', 'span[class*="price"]']:
                elems = self.driver.find_elements(By.CSS_SELECTOR, sel)
                if elems:
                    for pe in elems:
                        cand = self._clean_price(pe.text)
                        if cand and cand >= 1000000:
                            price = cand
                            break
                if price:
                    break

        if not price and body_text:
            m_price = re.search(r"Rp\s*([\d\.,]+)", body_text)
            if m_price:
                price = self._clean_price(m_price.group(1))

        # Ekstraksi deskripsi
        desc = ""
        for sel in ['div[data-aut-id="itemDescription"]', 'div[class*="description"]', 'p[class*="description"]']:
            elems = self.driver.find_elements(By.CSS_SELECTOR, sel)
            if elems and elems[0].text.strip():
                desc = elems[0].text.strip()
                break

        # Ekstraksi Lokasi
        location = "Indonesia"
        for sel in ['span[data-aut-id="itemLocation"]', 'div[data-aut-id="itemLocation"]']:
            elems = self.driver.find_elements(By.CSS_SELECTOR, sel)
            if elems and elems[0].text.strip():
                location = elems[0].text.strip()
                break

        # Ekstraksi Tahun
        year = None
        m_year = re.search(r"\b(20[0-2][0-9]|199[0-9])\b", title)
        if m_year:
            year = int(m_year.group(1))

        # Ekstraksi Odometer
        odometer = 0
        m_km = re.search(r"([\d\.,]+)\s*(?:km|ribu\s*km)", f"{title} {desc}", re.IGNORECASE)
        if m_km:
            clean_km = re.sub(r"[^\d]", "", m_km.group(1))
            if clean_km and clean_km.isdigit():
                odometer = int(clean_km)

        # Ekstraksi Dokumen & Pajak
        docs = ScamAndDPDetector.detect_vehicle_docs_and_tax(body_text, title, desc)

        # Evaluasi Scam / DP
        eval_res = ScamAndDPDetector.evaluate(price, title, desc, claimed_year=year)
        is_dp = eval_res["is_invalid"]

        m_item_id = re.search(r"iid-(\d+)", item_url)
        item_id = m_item_id.group(1) if m_item_id else str(abs(hash(item_url)))

        parts = [p.strip() for p in location.split(",") if p.strip()]
        city_val = parts[1] if len(parts) >= 3 else (parts[0] if len(parts) >= 2 else "Indonesia")
        prov_val = parts[2] if len(parts) >= 3 else (parts[1] if len(parts) >= 2 else "Indonesia")

        return {
            "item_id": item_id,
            "external_id": f"olx_real_{item_id}",
            "url": item_url,
            "title": title,
            "price": price or 0.0,
            "claimed_year": year,
            "odometer_km": odometer,
            "location": location,
            "city": city_val,
            "province": prov_val,
            "description": desc,
            "raw_description": desc,
            "has_bpkb": docs["bpkb"],
            "has_stnk": docs["stnk"],
            "has_faktur": docs["faktur"],
            "tax_status": docs["pajak_status"],
            "is_dp": is_dp,
            "scam_reason": eval_res["reason"],
            "source_platform": "olx",
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def scrape_live_search(self, keyword: str, max_items: int = 15, category: str = "motor") -> List[Dict[str, Any]]:
        """
        Pencarian on-demand langsung dari query pengguna.
        Membuka halaman OLX, mengumpulkan tautan iklan, lalu mengekstrak spesifikasi.
        """
        if not self.driver:
            self._init_driver()

        cat_info = CATEGORIES.get(category, CATEGORIES["motor"])
        base_url = cat_info["base_url"]
        query_slug = self._create_query_slug(keyword)
        search_url = f"{base_url}/q-{query_slug}"

        print(f"[OLXStealth] Membuka URL pencarian: {search_url}")
        try:
            self.driver.get(search_url)
            self._sleep_human()
        except Exception as e:
            print(f"[OLXStealth] Error memuat pencarian: {e}")
            self.close()
            self._init_driver()
            try:
                self.driver.get(search_url)
                self._sleep_human()
            except Exception:
                return []

        # Coba klik load more jika ada
        try:
            load_btns = self.driver.find_elements(By.CSS_SELECTOR, '[data-aut-id="btnLoadMore"]')
            if load_btns and load_btns[0].is_displayed():
                self.driver.execute_script("arguments[0].click();", load_btns[0])
                self._sleep_human()
        except Exception:
            pass

        # Kumpulkan link /item/
        links = self.driver.find_elements(By.TAG_NAME, "a")
        item_urls = []
        for l in links:
            try:
                href = l.get_attribute("href")
                if href and "/item/" in href and href not in item_urls:
                    item_urls.append(href)
            except Exception:
                continue

        print(f"[OLXStealth] Ditemukan {len(item_urls)} link listing kandidat.")
        results = []
        for url in item_urls[:max_items]:
            item_data = self._extract_detail_page(url, category=category)
            if item_data:
                results.append(item_data)
                print(f"  [+] Sukses ekstrak: {item_data['title'][:45]} | Rp {item_data['price']:,}")

        return results

if __name__ == "__main__":
    scraper = OLXStealthScraper(headless=True)
    try:
        sample_query = "Honda Vario 160"
        print(f"Menguji OLX Stealth Scraper untuk '{sample_query}'...")
        items = scraper.scrape_live_search(sample_query, max_items=3)
        print(f"\nHasil ekstraksi live: {len(items)} listing")
        for itm in items:
            print(itm)
    finally:
        scraper.close()
