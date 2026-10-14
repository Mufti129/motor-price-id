# Laporan Sanitasi Data Listing (2026-10-14 09:31:23)

- Mode: EKSEKUSI (ditulis ke database)
- Total listing: 20,155
- Sudah ditandai DP/Clickbait sebelumnya: 551
- Dikarantina oleh sanitasi ini: 501
- Listing cash bersih (aktif, ter-match, bertahun): 19,100

## Rincian Kode Karantina

| Kode | Jumlah |
| :--- | ---: |
| STAT_OUTLIER_MAD | 229 |
| DUPLICATE_EXACT | 129 |
| ENTITY_MISMATCH | 118 |
| PRICE_BELOW_AGE_FLOOR | 23 |
| PRICE_ABOVE_MSRP | 2 |

## Provenance Data

| Asal Data | Semua Listing | Cash Bersih |
| :--- | ---: | ---: |
| LIVE_SCRAPED | 1,094 | 773 |
| SYNTHETIC | 19,061 | 18,327 |

## Dampak Terhadap Kualitas Data

| Metrik | Sebelum | Sesudah |
| :--- | ---: | ---: |
| Harga cash maksimum | Rp 1,234,546,787 | Rp 899,300,000 |
| Harga cash minimum | Rp 1,200,000 | Rp 2,500,000 |
| Inversi tahun (median tahun tua > 125% tahun muda, n>=3) | 10 | 7 |
| Inversi tahun - hanya data LIVE_SCRAPED | - | 0 |

## Bias Data Sintetis terhadap Data Live

Dibandingkan pada 177 kelompok (varian, tahun) yang memiliki kedua jenis data.
Rasio median harga LIVE / SINTETIS = 1.1551 (P25 1.0662, P75 1.291). Nilai > 1 berarti data sintetis cenderung lebih murah daripada harga iklan riil.

Daftar lengkap listing yang dikarantina: `data/reports/quarantined_listings_20261014.csv`
