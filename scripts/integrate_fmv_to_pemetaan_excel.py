#!/usr/bin/env python3
"""
Integrasi Data Tarikan Harga & Rumus FMV ke pemetaan_tipe_motor_internal_vs_tarikan.xlsx
1. Menambahkan tab 'List Harga Tarikan' (296 listing riil OLX & Momotor).
2. Menambahkan tab 'Matriks FMV (Model & Tahun)' (118 grup model & tahun).
3. Menambahkan kolom 'Harga FMV', 'Metode Perhitungan FMV', dan 'Sampel Riil'
   pada tab 'Katalog Master Tarikan (4.5K)' dengan rumus Excel dinamis.
"""

import os
import sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import pandas as pd
import numpy as np

FILE_PEMETAAN = "/Users/macbookair/Downloads/pemetaan_tipe_motor_internal_vs_tarikan.xlsx"
FILE_PEMETAAN_FOLDER = "/Users/macbookair/Downloads/Pemetaan database motor tarikan dan database internal/pemetaan_tipe_motor_internal_vs_tarikan.xlsx"
FILE_TARIKAN = "/Users/macbookair/Downloads/tarikan_harga_olx_momotor_siap_petakan.xlsx"
BACKUP_REPO = "/Users/macbookair/Documents/Scrape Data/data/reports/pemetaan_tipe_motor_internal_vs_tarikan.xlsx"

def map_raw_to_master_commercial(title, comm, brand):
    t_low = str(title).lower()
    c_low = str(comm).lower()
    b_up = str(brand).upper()
    
    # HONDA
    if "beat" in t_low or "beat" in c_low:
        if "pop" in t_low or "pop" in c_low:
            return "Honda BeAT POP"
        return "Honda BeAT"
    if "vario 160" in t_low or "vario 160" in c_low:
        return "Honda Vario 160"
    if "vario 125" in t_low or "vario 125" in c_low:
        return "Honda Vario 125"
    if "vario 150" in t_low or "vario 150" in c_low:
        return "Honda Vario 150"
    if "scoopy" in t_low or "scoopy" in c_low:
        return "Honda Scoopy"
    if "pcx 160" in t_low or "pcx 160" in c_low:
        return "Honda PCX 160"
    if "pcx 150" in t_low or "pcx 150" in c_low:
        return "Honda PCX 150"
    if "genio" in t_low or "genio" in c_low:
        return "Honda Genio"
    if "adv 160" in t_low or "adv 160" in c_low:
        return "Honda ADV 160"
    if "adv 150" in t_low or "adv 150" in c_low:
        return "Honda ADV 150"
    if "supra x" in t_low or "supra x" in c_low:
        return "Honda Supra X 125"
    if "revo" in t_low or "revo" in c_low:
        return "Honda Revo 110"

    # YAMAHA
    if "nmax turbo" in t_low or "nmax neo" in t_low or "nmax turbo" in c_low:
        return "Yamaha NMAX Turbo / Neo"
    if "nmax" in t_low or "nmax" in c_low:
        return "Yamaha All New NMAX 155"
    if "aerox" in t_low or "aerox" in c_low:
        return "Yamaha All New Aerox 155"
    if "fazzio" in t_low or "fazzio" in c_low:
        return "Yamaha Fazzio 125"
    if "filano" in t_low or "filano" in c_low:
        return "Yamaha Grand Filano 125"
    if "freego" in t_low or "freego" in c_low:
        return "Yamaha FreeGo 125"
    if "gear" in t_low or "gear" in c_low:
        return "Yamaha Gear 125"
    if "lexi" in t_low or "lexi" in c_low:
        return "Yamaha Lexi LX 155"
    if "mio m3" in t_low or "mio m3" in c_low:
        return "Yamaha Mio M3 125"
    if "mio" in t_low or "mio" in c_low:
        return "Yamaha Mio M3 125"
    if "vixion" in t_low or "vixion" in c_low:
        return "Yamaha All New Vixion"
    if "xsr" in t_low or "xsr" in c_low:
        return "Yamaha XSR 155"

    # SUZUKI
    if "satria" in t_low or "satria" in c_low:
        return "Suzuki All New Satria F150"

    # KAWASAKI
    if "klx 150" in t_low or "klx 150" in c_low:
        return "Kawasaki KLX 150 / D-Tracker 150"

    # VESPA
    if "sprint" in t_low or "sprint" in c_low:
        if "tech" in t_low or "tech" in c_low:
            return "Vespa Sprint Tech"
        if "iget" in t_low or "iget" in c_low:
            return "Vespa Sprint Iget 150 Abs"
        return "Vespa Sprint 150"
    if "primavera" in t_low or "primavera" in c_low:
        return "Vespa Primavera 150"

    return comm

def main():
    print(f"Memuat file: {FILE_PEMETAAN}...")
    wb = openpyxl.load_workbook(FILE_PEMETAAN)

    # Baca data tarikan
    print(f"Membaca data tarikan dari: {FILE_TARIKAN}...")
    df_raw = pd.read_excel(FILE_TARIKAN, sheet_name="Tarikan Riil Listing")
    df_raw["Nama Komersil Master"] = df_raw.apply(
        lambda r: map_raw_to_master_commercial(r["Judul Iklan"], r["Nama Komersil"], r["Merek"]),
        axis=1
    )
    df_raw["Tahun Unit"] = df_raw["Tahun Unit"].astype(str)

    # Styles
    navy_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    gold_fill = PatternFill(start_color="D4AF37", end_color="D4AF37", fill_type="solid")
    white_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    bold_font = Font(name="Calibri", size=11, bold=True)
    regular_font = Font(name="Calibri", size=10)
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    # -------------------------------------------------------------
    # 1. Buat / Update Sheet 'List Harga Tarikan'
    # -------------------------------------------------------------
    sheet_tarikan_name = "List Harga Tarikan"
    if sheet_tarikan_name in wb.sheetnames:
        del wb[sheet_tarikan_name]
    
    ws_list = wb.create_sheet(title=sheet_tarikan_name)
    headers_list = [
        "No", "Platform", "ID Listing", "Judul Iklan", "Merek",
        "Nama Komersil Master", "Kode Tipe Sasis", "Tahun Unit",
        "Harga Pasar Riil (Rp)", "Jarak Tempuh (KM)", "Kota / Wilayah",
        "Kelengkapan Dokumen", "Mapping Tier Internal", "URL Iklan", "Waktu Tarik Data"
    ]
    ws_list.append(headers_list)

    # Style Header List
    for col_idx, h in enumerate(headers_list, start=1):
        cell = ws_list.cell(row=1, column=col_idx)
        cell.fill = navy_fill
        cell.font = white_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Masukkan Baris Listing
    for idx, row in df_raw.iterrows():
        row_vals = [
            idx + 1,
            str(row["Platform"]),
            str(row["ID Listing"]),
            str(row["Judul Iklan"]),
            str(row["Merek"]),
            str(row["Nama Komersil Master"]),
            str(row["Kode Tipe Sasis"]),
            str(row["Tahun Unit"]),
            int(row["Harga Pasar Riil (Rp)"]),
            int(row["Jarak Tempuh (KM)"]) if str(row["Jarak Tempuh (KM)"]).isdigit() else "-",
            str(row["Kota / Wilayah"]),
            str(row["Kelengkapan Dokumen"]),
            str(row["Mapping Tier Internal"]),
            str(row["URL Iklan"]),
            str(row["Waktu Tarik Data"])
        ]
        ws_list.append(row_vals)
        r_num = idx + 2
        for c_num in range(1, len(headers_list) + 1):
            c_cell = ws_list.cell(row=r_num, column=c_num)
            c_cell.font = regular_font
            c_cell.border = thin_border
            if c_num in [1, 2, 8]:
                c_cell.alignment = Alignment(horizontal="center")
            elif c_num in [9, 10]:
                c_cell.alignment = Alignment(horizontal="right")
                if c_num == 9:
                    c_cell.number_format = "#,##0"

    print(f"✅ Tab '{sheet_tarikan_name}' berhasil dibuat ({len(df_raw)} listing).")

    # -------------------------------------------------------------
    # 2. Buat / Update Sheet 'Matriks FMV (Model & Tahun)'
    # -------------------------------------------------------------
    sheet_matrix_name = "Matriks FMV (Model & Tahun)"
    if sheet_matrix_name in wb.sheetnames:
        del wb[sheet_matrix_name]

    ws_matrix = wb.create_sheet(title=sheet_matrix_name)
    headers_matrix = [
        "Merek", "Nama Komersil Master", "Mapping Tier Internal", "Tahun Unit",
        "Sampel Riil", "Harga Minimum (Rp)", "Harga Bawah P25 (Rp)",
        "Harga FMV Median (Rp)", "Harga Atas P75 (Rp)", "Harga Maksimum (Rp)",
        "Rata-rata Odometer (KM)"
    ]
    ws_matrix.append(headers_matrix)

    for col_idx, h in enumerate(headers_matrix, start=1):
        cell = ws_matrix.cell(row=1, column=col_idx)
        cell.fill = navy_fill
        cell.font = white_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    grouped = df_raw[df_raw["Tahun Unit"] != "-"].groupby(["Merek", "Nama Komersil Master", "Mapping Tier Internal", "Tahun Unit"])
    m_idx = 2
    for (m_brand, m_name, m_tier, m_year), g in grouped:
        prices = g["Harga Pasar Riil (Rp)"].values
        odo_series = pd.to_numeric(g["Jarak Tempuh (KM)"], errors='coerce').dropna()
        avg_odo = int(odo_series.mean()) if len(odo_series) > 0 else "-"

        vals = [
            m_brand,
            m_name,
            m_tier,
            str(m_year),
            len(prices),
            int(np.min(prices)),
            int(np.percentile(prices, 25)),
            int(np.median(prices)),
            int(np.percentile(prices, 75)),
            int(np.max(prices)),
            avg_odo
        ]
        ws_matrix.append(vals)
        for c_num in range(1, len(headers_matrix) + 1):
            c_cell = ws_matrix.cell(row=m_idx, column=c_num)
            c_cell.font = regular_font
            c_cell.border = thin_border
            if c_num in [4, 5]:
                c_cell.alignment = Alignment(horizontal="center")
            elif c_num in [6, 7, 8, 9, 10, 11]:
                c_cell.alignment = Alignment(horizontal="right")
                if c_num in [6, 7, 8, 9, 10]:
                    c_cell.number_format = "#,##0"
        m_idx += 1

    print(f"✅ Tab '{sheet_matrix_name}' berhasil dibuat ({m_idx - 2} grup model & tahun).")

    # -------------------------------------------------------------
    # 3. Modifikasi Sheet 'Katalog Master Tarikan (4.5K)'
    # -------------------------------------------------------------
    ws_master = wb["Katalog Master Tarikan (4.5K)"]
    print(f"Mengupdate rumus FMV pada: {ws_master.title} ({ws_master.max_row} baris)...")

    # Header Baru di Kolom L (12), M (13), N (14)
    col_fmv = 12
    col_metode = 13
    col_sampel = 14

    cell_l1 = ws_master.cell(row=1, column=col_fmv, value="Harga FMV")
    cell_m1 = ws_master.cell(row=1, column=col_metode, value="Metode Perhitungan FMV")
    cell_n1 = ws_master.cell(row=1, column=col_sampel, value="Sampel Riil")

    for c in [cell_l1, cell_m1, cell_n1]:
        c.fill = gold_fill
        c.font = Font(name="Calibri", size=11, bold=True, color="000000")
        c.alignment = Alignment(horizontal="center", vertical="center")

    max_rows = ws_master.max_row
    for r in range(2, max_rows + 1):
        # Rumus Harga FMV:
        # 1. Cek Model & Tahun spesifik di 'List Harga Tarikan'
        # 2. Jika 0, ambil Rata-rata Model di 'List Harga Tarikan'
        # 3. Jika 0, ambil Benchmark Tier Internal di 'List Harga Tarikan'
        # 4. Jika tetap 0, tampilkan "-"
        formula_fmv = (
            f"=IFERROR("
            f"IF(COUNTIFS('List Harga Tarikan'!$F:$F, D{r}, 'List Harga Tarikan'!$H:$H, F{r})>0, "
            f"AVERAGEIFS('List Harga Tarikan'!$I:$I, 'List Harga Tarikan'!$F:$F, D{r}, 'List Harga Tarikan'!$H:$H, F{r}), "
            f"IF(COUNTIFS('List Harga Tarikan'!$F:$F, D{r})>0, "
            f"AVERAGEIFS('List Harga Tarikan'!$I:$I, 'List Harga Tarikan'!$F:$F, D{r}), "
            f"IF(COUNTIFS('List Harga Tarikan'!$M:$M, J{r})>0, "
            f"AVERAGEIFS('List Harga Tarikan'!$I:$I, 'List Harga Tarikan'!$M:$M, J{r}), "
            f"\"-\"))), "
            f"\"-\")"
        )

        formula_metode = (
            f"=IF(COUNTIFS('List Harga Tarikan'!$F:$F, D{r}, 'List Harga Tarikan'!$H:$H, F{r})>0, "
            f"\"Riil (Model & Tahun)\", "
            f"IF(COUNTIFS('List Harga Tarikan'!$F:$F, D{r})>0, "
            f"\"Rata-rata Model\", "
            f"IF(COUNTIFS('List Harga Tarikan'!$M:$M, J{r})>0, "
            f"\"Benchmark Tier (\" & J{r} & \")\", "
            f"\"Belum Ada Data\")))"
        )

        formula_sampel = (
            f"=IF(COUNTIFS('List Harga Tarikan'!$F:$F, D{r}, 'List Harga Tarikan'!$H:$H, F{r})>0, "
            f"COUNTIFS('List Harga Tarikan'!$F:$F, D{r}, 'List Harga Tarikan'!$H:$H, F{r}), "
            f"COUNTIFS('List Harga Tarikan'!$F:$F, D{r}))"
        )

        cell_f = ws_master.cell(row=r, column=col_fmv, value=formula_fmv)
        cell_f.font = regular_font
        cell_f.alignment = Alignment(horizontal="right")
        cell_f.number_format = "#,##0"
        cell_f.border = thin_border

        cell_m = ws_master.cell(row=r, column=col_metode, value=formula_metode)
        cell_m.font = regular_font
        cell_m.alignment = Alignment(horizontal="left")
        cell_m.border = thin_border

        cell_s = ws_master.cell(row=r, column=col_sampel, value=formula_sampel)
        cell_s.font = regular_font
        cell_s.alignment = Alignment(horizontal="center")
        cell_s.border = thin_border

    # Atur lebar kolom otomatis untuk tab yang ditambahkan
    for ws_cur in [ws_list, ws_matrix, ws_master]:
        for col in ws_cur.columns:
            max_len = max(len(str(cell.value or '')) for cell in col[:100])
            col_letter = get_column_letter(col[0].column)
            ws_cur.column_dimensions[col_letter].width = max(max_len + 3, 12)

    # Simpan file ke seluruh lokasi target
    targets = [FILE_PEMETAAN, FILE_PEMETAAN_FOLDER, BACKUP_REPO]
    for target in targets:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        wb.save(target)
        print(f"✅ [SUCCESS SAVED] {target}")

    print("\n🎉 Integrasi Selesai Sempurna!")

if __name__ == "__main__":
    main()
