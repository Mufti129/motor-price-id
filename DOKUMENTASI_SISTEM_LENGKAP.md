# DOKUMENTASI LENGKAP & SPESIFIKASI TEKNIS SISTEM
## MOTORPRICE ID — USED MOTORCYCLE INTELLIGENCE & VALUATION ENGINE
**Penulis & Pengembang:** Mukhammad Rekza Mufti (Data & System Analyst)  
**Versi Sistem:** v2.4 (Enterprise Edition)  
**Waktu Rilis:** Oktober 2026  
**Repositori GitHub:** [https://github.com/Mufti129/motor-price-id](https://github.com/Mufti129/motor-price-id)  
**Platform Deploy:** Streamlit Community Cloud (Python 3.13 Runtime)  

---

# DAFTAR ISI
1. [BAB I: Pendahuluan & Latar Belakang Masalah](#bab-i-pendahuluan--latar-belakang-masalah)
2. [BAB II: Arsitektur Sistem End-to-End](#bab-ii-arsitektur-sistem-end-to-end)
3. [BAB III: Definisi Kamus Data & Parameter Lengkap](#bab-iii-definisi-kamus-data--parameter-lengkap)
4. [BAB IV: Logika Matematis, Model Analitik & Landasan Teori Ahli](#bab-iv-logika-matematis-model-analitik--landasan-teori-ahli)
5. [BAB V: Taksonomi Master Katalog 12 Tahun (2014–2026)](#bab-v-taksonomi-master-katalog-12-tahun-20142026)
6. [BAB VI: Panduan Operasional & Lokasi Fitur Depresiasi Riil](#bab-vi-panduan-operasional--lokasi-fitur-depresiasi-riil)
7. [BAB VII: Panduan Instalasi Lokal & Deployment Cloud](#bab-vii-panduan-instalasi-lokal--deployment-cloud)

---

# BAB I: Pendahuluan & Latar Belakang Masalah

### 1.1 Fenomena Asimetri Informasi Pasar Motor Bekas Indonesia
Pasar sepeda motor bekas di Indonesia merupakan salah satu ekosistem transaksi kendaraan roda dua terbesar di Asia Tenggara. Namun, pasar ini memiliki karakteristik *unstructured and highly fragmented market* dengan permasalahan utama:
1. **Asimetri Informasi Harga (*Price Information Asymmetry*):** Tidak adanya standar harga acuan resmi yang transparan antara pembeli, penjual individu, dan dealer motor bekas.
2. **Praktek Iklan Clickbait / Uang Muka (*DP Scam Trap*):** Banyak penjual di marketplace (seperti OLX dan Facebook Marketplace) mencantumkan nominal DP/Uang Muka (misal Rp 1.500.000) pada kolom harga tunai (*cash price*), sehingga merusak agregasi statistik harga pasar jika tidak difilter dengan kecerdasan buatan.
3. **Variasi Bahasa Gaul & Typo Lokal (*Slang Jargon*):** Penggunaan istilah lokal yang tidak terstruktur seperti *"pajak off 2x"*, *"kaleng 2028"*, *"SS lengkap"*, *"BPKB only / yatim"*, *"mesin segel standar"*, serta salah ketik (*"Pagio"*, *"Nmek"*, *"Biet Street"*).

### 1.2 Tujuan Pembangunan Sistem MotorPrice ID
MotorPrice ID dibangun sebagai platform terpadu untuk:
- Mengumpulkan data dari berbagai marketplace secara otomatis (*Automated Multi-Source Scraper*).
- Membersihkan dan menormalisasi teks iklan menggunakan NLP dan kamus otomotif Indonesia.
- Melakukan pemetaan entitas fuzzy (*Entity Resolution*) ke katalog master resmi 12 tahun terakhir.
- Menghitung Nilai Pasar Wajar (*Fair Market Value / FMV*), Kuartil Harga, dan Depresiasi Riil berdasarkan model ekonometrika dan riset ahli.
- Mengidentifikasi peluang keuntungan arbitrase (*Bargain Hunter Deals*).

---

# BAB II: Arsitektur Sistem End-to-End

```text
+-----------------------------------------------------------------------------------+
|                        1. DATA HARVESTING & INGESTION                             |
|  - OLX Indonesia API Scraper      - Facebook Marketplace       - Momotor.id       |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                   2. AI & NLP DATA REFINEMENT PIPELINE                            |
|  - Indonesian Slang Dictionary    - Scam & DP Clickbait Filter                    |
|  - Mileage & Tax NLP Extractor    - RapidFuzz Entity Matcher (Levenshtein/JW)     |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                     3. RELATIONAL DATABASE LAYER (SQLite)                         |
|  - master_brands   - master_models   - master_variants (MSRP 2014-2026)           |
|  - scraped_listings (6,000 Data)     - market_price_stats (Snapshot Daily FMV)    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                 4. ECONOMETRIC & PRICING ANALYTICS ENGINE                         |
|  - Akerlof Double-Declining Depreciation     - Lancaster Hedonic Condition Pricing|
|  - Tukey Interquartile Range (P25, FMV, P75) - Fama Arbitrage Opportunity Scanner |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|             5. ENTERPRISE STREAMLIT USER INTERFACE & VISUALIZATION                |
|  - Executive Header & KPI Cards              - Plotly Dark Analytics Charts       |
|  - Real Depreciation (%) Matrix              - 1-Click Batch Scraper & CSV Export |
+-----------------------------------------------------------------------------------+
```

---

# BAB III: Definisi Kamus Data & Parameter Lengkap

### 3.1 Parameter Tabel Listing Pasar (`scraped_listings`)

| Nama Parameter / Kolom | Tipe Data | Definisi & Fungsi Bisnis | Contoh Nilai |
| :--- | :--- | :--- | :--- |
| `ID` | Integer (PK) | Identifikator unik internal database untuk setiap listing. | `1, 2, 3...` |
| `Platform` | String (50) | Marketplace sumber ekstraksi data (`OLX`, `FACEBOOK`, `MOMOTOR`). | `OLX` |
| `Title` | String (300) | Judul asli iklan kendaraan setelah dinormalisasi teksnya. | `Honda Vario 125 CBS 2022` |
| `Brand` | String (50) | Nama produsen/pabrikan motor resmi hasil mapping entity. | `Honda`, `Yamaha` |
| `Model` | String (100) | Lini model sepeda motor. | `Vario`, `NMAX`, `Ninja` |
| `Variant` | String (150) | Varian spesifik, generasi, atau trim motor hasil AI matching. | `Vario 125 All New (Gen 2)` |
| `Year` | Integer | Tahun perakitan/pembuatan kendaraan yang diklaim penjual. | `2022` |
| `Price` | Numeric (15,2) | Harga transaksi tunai (IDR) tervalidasi bebas uang muka semu. | `Rp 18.200.000` |
| `Price_Type` | String (30) | Klasifikasi validitas harga (`Cash` vs `DP / Clickbait`). | `Cash` |
| `Mileage_KM` | Integer | Total jarak tempuh odometer (kilometer) kendaraan. | `22.000` |
| `Tax_Status` | String (50) | Status pajak kendaraan (`Hidup / Panjang`, `Mati / Off`, `Unknown`). | `Hidup / Panjang` |
| `BPKB` | String (30) | Kelengkapan dokumen kepemilikan mutlak (`Lengkap` vs `Tidak Ada`). | `Lengkap` |
| `Plate_Code` | String (10) | Wilayah registrasi plat nomor kepolisian. | `B` (Jabodetabek), `D` (Bandung) |
| `Province` | String (100) | Provinsi lokasi unit kendaraan berada. | `DKI Jakarta`, `Jawa Barat` |
| `City` | String (100) | Kota/Kabupaten domisili penjualan unit. | `Jakarta Selatan`, `Surabaya` |
| `Seller_Type` | String (50) | Profil entitas penjual (`Individual` / Pemilik vs `Dealer` / Showroom). | `Individual` |
| `MSRP_New` | Numeric (15,2) | Harga resmi baru On The Road (OTR) saat tahun rilis peluncuran. | `Rp 22.500.000` |
| `URL` | Text | Tautan deep-link resmi aktif menuju pencarian marketplace terkait. | `https://www.olx.co.id/...` |
| `Posted_At` | DateTime | Waktu publikasi listing iklan oleh penjual. | `2026-09-28 14:20:00` |
| `Scraped_At` | DateTime | Waktu pengambilan snapshot data oleh sistem. | `2026-10-07 10:00:00` |

---

### 3.2 Parameter Tabel Agregasi Statistik Pasar (`market_price_stats`)

| Nama Parameter | Tipe Data | Definisi & Fungsi Statistik | Formula / Kriteria |
| :--- | :--- | :--- | :--- |
| `stat_date` | Date | Tanggal snapshot agregasi pasar dihitung. | `YYYY-MM-DD` |
| `variant_id` | Integer (FK) | Relasi ke Master Varian Motor. | Foreign Key |
| `year` | Integer | Tahun produksi kendaraan yang dianalisis. | `2014 - 2026` |
| `sample_count` | Integer | Jumlah sampel listing tunai valid yang dianalisis. | `N >= 1` |
| `price_min` | Numeric (15,2) | Batas harga terendah non-outlier. | `Min(P)` |
| `price_p25` | Numeric (15,2) | Persentil ke-25 (Bargain Buy Price / Target Beli Murah). | Kuartil 1 (`Q1`) |
| `price_median` | Numeric (15,2) | Persentil ke-50 (Fair Market Value / Nilai Pasar Wajar). | Kuartil 2 (`Q2`) |
| `price_p75` | Numeric (15,2) | Persentil ke-75 (Premium / Pristine Condition Price). | Kuartil 3 (`Q3`) |
| `price_max` | Numeric (15,2) | Batas harga tertinggi non-outlier. | `Max(P)` |

---

# BAB IV: Logika Matematis, Model Analitik & Landasan Teori Ahli

Sistem MotorPrice ID dibangun berdasarkan metodologi ilmiah dan literatur ekonomi terkemuka:

### 4.1 Model Depresiasi Saldo Menurun & Teori Pasar Barang Bekas
* **Rujukan Teori:**
  1. **George Akerlof (1970)** — *"The Market for Lemons: Quality Uncertainty and the Market Mechanism"*, Quarterly Journal of Economics (Pemenang Nobel Ekonomi 2001).
  2. **Wyatt, D. J. (1990)** — *"Automobile Depreciation and Used Asset Pricing Dynamics"*.

* **Logika Matematis:**
  Akerlof membuktikan bahwa kendaraan mengalami penyusutan nilai terbesar seketika setelah unit keluar dari dealer karena adanya risiko asimetri informasi kualitas (*Information Asymmetry Discount*).
  Model matematika yang digunakan dalam MotorPrice ID menerapkan kurva depresiasi non-linier eksponensial bertahap:
  
  $$	ext{Depresiasi Riil (\%)} = \left( rac{	ext{MSRP OTR Baru} - 	ext{Harga Pasar Wajar}}{	ext{MSRP OTR Baru}} ight) 	imes 100\%$$

  $$	ext{Tingkat Depresiasi Kumulatif } D(t) = \min\left(0.68, \; \delta_1 + (t 	imes \delta_a)ight)$$
  - $\delta_1 = 15.0\% - 18.0\%$ : Depresiasi tahun pertama (*showroom exit drop*).
  - $\delta_a = 5.5\% - 6.0\%$ : Laju depresiasi tahunan berkelanjutan.
  - $t = 2026 - 	ext{Tahun Pembuatan}$.

---

### 4.2 Model Penyesuaian Harga Hedonik (*Hedonic Quality Pricing Model*)
* **Rujukan Teori:**
  1. **Kelvin J. Lancaster (1966)** — *"A New Approach to Consumer Theory"*, Journal of Political Economy.
  2. **Sherwin Rosen (1974)** — *"Hedonic Prices and Implicit Markets: Product Differentiation in Pure Competition"*.
  3. **Kelley Blue Book (KBB) Valuation Methodology**.

* **Logika Matematis:**
  Nilai sebuah motor bekas tidak hanya ditentukan oleh usia, melainkan gabungan dari atribut fisik dan legalitas yang melekat:
  
  $$	ext{FMV}_{	ext{Adjusted}} = 	ext{Base Price}_{	ext{Median}} + \Delta_{	ext{Pajak}} + \Delta_{	ext{Odometer}} + \Delta_{	ext{Legalitas}}$$

  1. **Penyesuaian Status Pajak ($\Delta_{	ext{Pajak}}$):**
     - Pajak Hidup / Panjang: $\Delta_{	ext{Pajak}} = 0$
     - Pajak Mati 1 Tahun: $\Delta_{	ext{Pajak}} = -	ext{Rp } 650.000$ (Estimasi PKB + SWDKLLJ + Denda)
     - Pajak Mati 2+ Tahun: $\Delta_{	ext{Pajak}} = -	ext{Rp } 1.400.000$
  2. **Penyesuaian Deviasi Jarak Tempuh Odometer ($\Delta_{	ext{Odometer}}$):**
     Berdasarkan standar mobilitas komuter Indonesia (BPS & Asosiasi Industri Sepeda Motor Indonesia - AISI), rata-rata jarak tempuh normal adalah **$8.500 	ext{ KM / tahun}$**.
     $$	ext{KM}_{	ext{Expected}} = \max\left(5.000, \; (2026 - 	ext{Tahun}) 	imes 8.500ight)$$
     $$\Delta_{	ext{Odometer}} = - \left( rac{	ext{KM}_{	ext{Aktual}} - 	ext{KM}_{	ext{Expected}}}{5.000} ight) 	imes 	ext{Rp } 250.000$$
     *(Dibatasi pada batas wajar $-	ext{Rp } 2.500.000 \le \Delta_{	ext{Odometer}} \le +	ext{Rp } 1.200.000$)*.
  3. **Penyesuaian Dokumen BPKB ($\Delta_{	ext{Legalitas}}$):**
     - Non-BPKB (STNK Only / BPKB Hilang): Penalti pemotongan **$-35\%$ dari nilai pasar** karena resiko sita fidusia dan ketidakabsahan legalitas jual-beli.

---

### 4.3 Estimasi Statistik Kokoh (*Robust Statistics & Interquartile Range*)
* **Rujukan Teori:**
  - **John W. Tukey (1977)** — *"Exploratory Data Analysis"*, Addison-Wesley.

* **Logika Matematis:**
  Penggunaan rata-rata (*mean*) sangat rentan terdistorsi oleh data penipuan harga Rp 1.000.000 atau markup harga ekstrim. Oleh karena itu, MotorPrice ID menerapkan statistik *Tukey Quantile Estimator*:
  - **Kuartil 1 ($Q_1$ / P25 - Bargain Buy Target):** 25% motor termurah dengan kondisi layak. Rekomendasi harga bagi pedagang/showroom untuk mendapatkan margin laba.
  - **Kuartil 2 ($Q_2$ / Median - Fair Market Value):** Nilai tengah pasar ekuilibrium.
  - **Kuartil 3 ($Q_3$ / P75 - Pristine Collector Value):** Harga untuk motor dengan kondisi istimewa, kilometer sangat rendah, dan cat orisinil sempurna.

---

### 4.4 Resolusi Entitas Teks & Fuzzy Matching
* **Rujukan Teori:**
  - **Vladimir Levenshtein (1965)** & **William E. Winkler (1990)** — *String Distance Metrics for Record Linkage*.
* **Logika Pemrosesan:**
  Algoritma memadukan *Token Sort Ratio* dan kamus sinonim untuk memetakan teks listing kotor (*"vario 150 cbs iss 2019 mulus"*) ke ID Katalog Master Varian (*Vario 150 eSP Exclusive / Keyless Gen 2*), dengan threshold akurasi $\ge 72\%$.

---

### 4.5 Mesin Pemindai Peluang Arbitrase (*Market Arbitrage Engine*)
* **Rujukan Teori:**
  - **Eugene F. Fama (1970)** — *"Efficient Capital Markets: A Review of Theory and Empirical Work"*, Journal of Finance.
* **Formula Deteksi:**
  $$	ext{Diskon Pasar (\%)} = \left( rac{	ext{Median FMV} - 	ext{Harga Listing}}{	ext{Median FMV}} ight) 	imes 100\%$$
  Kriteria Arbitrase Terverifikasi: $	ext{Diskon} \ge 12.0\%$, Status Pajak Hidup, BPKB Lengkap, dan Bukan Flag DP.

---

# BAB V: Taksonomi Master Katalog 12 Tahun (2014–2026)

Master katalog mencakup 6 produsen utama di Indonesia dengan rincian:

| Merk Produsen | Negara Asal | Jumlah Model | Jumlah Varian | Rentang CC Mesin | Model Unggulan Terdaftar |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Honda** | Jepang | 21 Model | 76 Varian | 110cc – 250cc | Beat Series, Vario Series, Scoopy, Stylo 160, PCX, ADV, CB150R, CB150X, CBR250RR, CRF150L, Sonic 150R, Forza 250 |
| **Yamaha** | Jepang | 20 Model | 48 Varian | 115cc – 530cc | Mio Series, Fazzio, Grand Filano, NMAX Series, Aerox, XMAX, Lexi LX, MT-15, R15, R25, WR 155 R, XSR 155, TMAX DX 530 |
| **Kawasaki** | Jepang | 11 Model | 34 Varian | 125cc – 400cc | Ninja 250 FI/Karbu, Ninja ZX-25R, Ninja ZX-4RR, KLX 150/230, D-Tracker, W175 Series, Versys-X 250, Z125 Pro |
| **Vespa (Piaggio)** | Italia | 6 Model | 21 Varian | 125cc – 300cc | Sprint (i-Get/TFT/Limited), Primavera (Color Vibe/Sean Wotherspoon), GTS Super 150/300, LX 125, S 125, GTV 300 HPE |
| **Piaggio** | Italia | 5 Model | 10 Varian | 125cc – 530cc | Medley S 150, Liberty 150 S, Beverly 300, MP3 300 HPE, MP3 530 Exclusive |
| **Suzuki** | Jepang | 10 Model | 23 Varian | 110cc – 250cc | Satria F150 FI, GSX-R150, GSX-S150, Address FI, Nex II/Crossover, V-Strom 250SX, Burgman Street 125EX, Inazuma 250 |
| **TOTAL** | **-** | **73 Model** | **212 Varian** | **110cc – 530cc** | **Seluruh Segmen Motor Indonesia** |

---

# BAB VI: Panduan Operasional & Lokasi Fitur Depresiasi Riil

Pengguna dapat memantau dan mengecek persentase depresiasi riil di **3 Lokasi Menu Utama**:

```text
+-----------------------------------------------------------------------------------------+
|                                    LOKASI FITUR DEPRESIASI RIIL                         |
+-----------------------------------------------------------------------------------------+
|  1. Menu: "Market Price Monitoring & Quartiles"                                         |
|     -> Periksa tabel pada kolom: "Depresiasi Riil (%)"                                  |
|     -> Menghitung persentase penurunan harga dari MSRP Baru terhadap Median FMV pasar.  |
|                                                                                         |
|  2. Menu: "Fair Market Value (FMV) Calculator"                                          |
|     -> Masukkan spesifikasi motor, tahun, KM, dan status pajak.                         |
|     -> Periksa badge pill di kotak hasil: "Depresiasi Riil dari OTR: XX.X%"             |
|                                                                                         |
|  3. Menu: "Market Overview"                                                             |
|     -> Periksa grafik: "12-Year Historical Price Depreciation Curve (2014-2026)"        |
|     -> Memetakan tren laju penyusutan harga antar-merk dari tahun ke tahun.             |
+-----------------------------------------------------------------------------------------+
```

---

# BAB VII: Panduan Instalasi Lokal & Deployment Cloud

### 7.1 Menjalankan di Komputer Lokal (Local Machine)
```bash
# 1. Clone repositori
git clone https://github.com/Mufti129/motor-price-id.git
cd motor-price-id

# 2. Buat dan aktifkan Virtual Environment Python 3.13
python3 -m venv venv
source venv/bin/activate

# 3. Instalasi pustaka dependensi
pip install -r requirements.txt

# 4. Jalankan aplikasi web Streamlit
streamlit run app.py
```

### 7.2 Deployment ke Streamlit Cloud
1. Masuk ke portal [share.streamlit.io](https://share.streamlit.io/).
2. Hubungkan akun GitHub Anda dan pilih repositori `Mufti129/motor-price-id`.
3. Tentukan branch: `main` dan Main file path: `app.py` atau `streamlit_app.py`.
4. Klik tombol **Deploy**. Aplikasi akan otomatis terkonfigurasi dan online secara publik.
