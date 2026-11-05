# DOKUMENTASI LENGKAP & SPESIFIKASI TEKNIS
## IBID ASTRA MAP (MARKET AUCTION PRICE) — CAR VALUATION & PRICE BENCHMARK ENGINE
**Kategori:** Wholesale & Auction Market Intelligence (Mobil & Kendaraan Roda 4)  
**Sumber Portal:** [https://map.ibid.astra.co.id/](https://map.ibid.astra.co.id/)  
**Backend API Host:** `https://api.ibid.astra.co.id/backend-dc-map`  
**Lokasi Direktori:** `scrapers/mobil/`  

---

## 1. Pendahuluan & Ringkasan Sistem
Portal **IBID MAP (Market Auction Price)** adalah platform analitik harga kendaraan lelang resmi yang dikelola oleh **PT Balai Lelang Serasi (IBID - Astra Group)**. 

Berbeda dengan katalog lelang motor reguler, sistem **MAP** ini dikhususkan untuk **kendaraan roda empat (Mobil Penumpang, SUV, MPV, Niaga, dan Truk)** dengan cakupan **26 Merek Resmi**. Modul ini menyediakan data harga pasar terbentuk (*fair auction value*), rentang harga minimum/maksimum, valuasi berdasarkan *Grade Inspeksi ACV (Astra Car Valuation)*, serta tren harga per kota dan kurun waktu.

---

## 2. Struktur Direktori Modul

```text
scrapers/mobil/
├── __init__.py                        # Package initializer & export module
├── ibid_map_client.py                 # SDK REST API Client (Connection pool, Auth headers, Error Handling)
├── harvest_car_market_prices.py       # Engine penarik data masal varian & harga ke SQLite / CSV
├── cli_car_valuation.py               # CLI interaktif untuk valuasi cepat dari terminal
├── DOKUMENTASI_IBID_MAP_MOBIL.md      # Dokumentasi teknis lengkap (file ini)
└── data/
    ├── ibid_map_cars.db               # Database SQLite lokal hasil harvesting
    └── ibid_map_cars_dataset.csv      # Dataset tabular CSV hasil export
```

---

## 3. Spesifikasi Teknis REST API & Keamanan

Sistem backend IBID MAP dilindungi oleh Azure API Management (APIM) dan internal client signature. Setiap request wajib menyertakan header otentikasi berikut:

### 3.1 Header Wajib (*Required Headers*)
```http
Content-Type: application/json
Accept: application/json, text/plain, */*
Ocp-Apim-Subscription-Key: 5c425b903b2b49b48f5edf10ce95616b
secret_key_map: stf57d68ag79d8uajd081n09dasdjjin9a87gfy6098h9d78s6f756crsafygud
client_id_map: 0000000000001
Referer: https://map.ibid.astra.co.id/
Origin: https://map.ibid.astra.co.id
```

---

## 4. Kamus Endpoint & Spesifikasi Request-Response

### 4.1 Master Merek Mobil (`master-data-merk`)
* **URL:** `GET https://api.ibid.astra.co.id/backend-dc-map/services/stock/master-data-merk`
* **Deskripsi:** Mengambil daftar seluruh 26 merek mobil yang terdaftar di ekosistem IBID MAP.
* **Contoh Response JSON:**
```json
{
  "status": true,
  "data": [
    { "id": 1748, "value": "BMW", "label": "BMW" },
    { "id": 2, "value": "DAIHATSU", "label": "DAIHATSU" },
    { "id": 1, "value": "TOYOTA", "label": "TOYOTA" },
    { "id": 3, "value": "HONDA", "label": "HONDA" }
  ],
  "message": "success"
}
```

---

### 4.2 Daftar Varian Kendaraan (`variant`)
* **URL:** `GET https://api.ibid.astra.co.id/backend-dc-map/services/map/stock/get/variant`
* **Query Parameters:**
  * `merk` (string, required): Contoh `TOYOTA`, `HONDA`, `DAIHATSU`
  * `seri` (string, optional): Contoh `AVANZA`, `INNOVA`, `BRIO SATYA`
* **Contoh Response JSON:**
```json
[
  {
    "merk": "TOYOTA",
    "seri": "AVANZA",
    "silinder": "1.3",
    "tipe": "G",
    "tahun": "2019",
    "lokasi": "JAKARTA"
  }
]
```

---

### 4.3 Cek Estimasi Harga Lelang (`check-price`)
* **URL:** `POST https://api.ibid.astra.co.id/backend-dc-map/services/map/check-price`
* **Request Body (JSON):**
```json
{
  "merk": "TOYOTA",
  "seri": "AVANZA",
  "silinder": "1.3",
  "tipe": "G",
  "tahun": "2019",
  "transmisi": "MT"
}
```
* **Contoh Response JSON:**
```json
{
  "status": true,
  "data": {
    "min_harga": "124500000.00",
    "max_harga": "138000000.00"
  },
  "message": "success"
}
```

---

### 4.4 Harga Berdasarkan Grade Inspeksi ACV (`unit-condition/get`)
* **URL:** `GET https://api.ibid.astra.co.id/backend-dc-map/services/price/unit-condition/get`
* **Query Parameters:** `brand`, `series`, `cylinder`, `type`, `year`, `transmission`
* **Contoh Response JSON:**
```json
{
  "data": {
    "item": [
      { "grade": "A", "totalHarga": "135000000.00", "hargaTertinggi": "138000000.00", "hargaTerendah": "132000000.00" },
      { "grade": "B", "totalHarga": "127500000.00", "hargaTertinggi": "130000000.00", "hargaTerendah": "125000000.00" },
      { "grade": "C", "totalHarga": "120000000.00", "hargaTertinggi": "122000000.00", "hargaTerendah": "118000000.00" }
    ]
  }
}
```

---

### 4.5 Distribusi Harga per Kota & Tren Waktu
* **Harga per Kota:** `GET /backend-dc-map/services/price/area-city/get?brand=...&series=...&year=...`
* **Tren Waktu:** `GET /backend-dc-map/services/price/time/get?brand=...&series=...&year=...`
* **Pencarian Populer:** `GET https://api.ibid.astra.co.id/map-be/services/popular` (Tanpa auth)

---

## 5. Panduan Penggunaan & Contoh Kode

### 5.1 Menggunakan SDK di Kode Python Lain
```python
from scrapers.mobil.ibid_map_client import IbidMapClient

client = IbidMapClient()

# 1. Cek Harga Toyota Avanza 1.3 G MT 2019
val = client.check_price(
    merk="TOYOTA",
    seri="AVANZA",
    silinder="1.3",
    tipe="G",
    tahun="2019",
    transmisi="MT"
)
print("Min Harga Lelang:", val.get("min_harga"))
print("Max Harga Lelang:", val.get("max_harga"))

# 2. Cek Berdasarkan Grade Kondisi
grades = client.get_price_by_grade(
    brand="TOYOTA",
    series="AVANZA",
    cylinder="1.3",
    tipe="G",
    year="2019",
    transmission="MT"
)
print("Harga per Grade:", grades.get("item"))
```

---

### 5.2 Menjalankan CLI Interaktif Valuasi Mobil
Jalankan tool interaktif di terminal:
```bash
python3 scrapers/mobil/cli_car_valuation.py
```

---

### 5.3 Menjalankan Engine Data Harvesting Masal
Untuk menarik data varian dan harga lelang seluruh mobil ke database SQLite (`scrapers/mobil/data/ibid_map_cars.db`) dan CSV:
```bash
# Menarik data untuk 3 merek teratas (contoh pengujian)
python3 scrapers/mobil/harvest_car_market_prices.py --brands 3 --delay 0.2

# Menarik data seluruh 26 merek mobil
python3 scrapers/mobil/harvest_car_market_prices.py --brands 26 --delay 0.3
```

---

## 6. Skema Database SQLite (`ibid_map_cars.db`)

Tabel `car_market_prices`:
| Kolom | Tipe | Deskripsi |
| :--- | :--- | :--- |
| `id` | INTEGER PK | Auto increment ID |
| `brand` | TEXT | Merek mobil (TOYOTA, HONDA, DAIHATSU, dll) |
| `series` | TEXT | Seri / model (AVANZA, INNOVA, BRIO, dll) |
| `cylinder` | TEXT | Kapasitas mesin / silinder (1.3, 1.5, 2.0, dll) |
| `type` | TEXT | Tipe / trim (G, E, V, RS, TRD, dll) |
| `year` | INTEGER | Tahun pembuatan kendaraan |
| `transmission` | TEXT | Transmisi (`MT` / `AT`) |
| `location` | TEXT | Wilayah / Cabang lelang acuan |
| `min_price` | REAL | Estimasi harga batas bawah lelang (Rp) |
| `max_price` | REAL | Estimasi harga batas atas lelang (Rp) |
| `grade_a_price` | REAL | Harga rata-rata kondisi Grade A (Rp) |
| `grade_b_price` | REAL | Harga rata-rata kondisi Grade B (Rp) |
| `grade_c_price` | REAL | Harga rata-rata kondisi Grade C (Rp) |
| `grade_d_price` | REAL | Harga rata-rata kondisi Grade D (Rp) |
| `created_at` | TIMESTAMP | Waktu data diambil/disimpan |
