"""
Script Migrasi & Ingesti Data Kalibrasi Master Katalog (100 Merek, 4.562 Kode Tipe).
Mengadopsi seluruh data dari 'data_kalibrasi_commercial_names (1).xlsx' (sheet 'Copy of Database')
ke dalam database 'motor_bekas.db' dan menyelaraskan dataset NJKB.
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

DB_PATH = os.path.join(BASE_DIR, "motor_bekas.db")
EXCEL_PATH = "/Users/macbookair/Downloads/data_kalibrasi_commercial_names (1).xlsx"
NJKB_CSV_PATH = os.path.join(BASE_DIR, "data", "reports", "njkb_enriched_with_commercial_names.csv")
NJKB_XLSX_PATH = os.path.join(BASE_DIR, "data", "reports", "njkb_enriched_with_commercial_names.xlsx")


def classify_segment(category_text: str, commercial_name: str, cc: float, is_ev: bool) -> str:
    if is_ev or cc == 0:
        return "EV"
    if cc >= 400:
        return "MOGE"
    
    text = (str(commercial_name) + " " + str(category_text)).lower()
    if any(k in text for k in ["nmax", "pcx", "adv", "aerox", "xmax", "forza", "tmax", "lexi"]):
        return "MAXI"
    if any(k in text for k in ["klx", "crf", "wr155", "wr250", "d-tracker", "trail", "enduro", "adventure"]):
        return "TRAIL_ADV"
    if any(k in text for k in ["w175", "xsr", "cb150x", "vespa", "sccoppy", "scoopy", "fazzio", "grand filano", "classic", "retro", "benelli", "royal enfield"]):
        return "RETRO_CLASSIC"
    if any(k in text for k in ["cbr", "r15", "r25", "ninja", "gsx", "cb150r", "vixion", "mt-15", "mt-25", "sport"]):
        return "SPORT"
    if any(k in text for k in ["beat", "vario", "mio", "fino", "genio", "spacy", "freego", "gear", "address", "nex", "matic", "scooter"]):
        return "MATIC"
    if any(k in text for k in ["supra", "revo", "jupiter", "vega", "blade", "satria", "smash", "bebek"]):
        return "BEBEK_OTHER"
    return "MATIC" if "at" in text else "SPORT"


def run_migration():
    print(f"[1/5] Memeriksa & Membaca File Kalibrasi: {EXCEL_PATH}")
    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(f"File {EXCEL_PATH} tidak ditemukan!")

    df_calib = pd.read_excel(EXCEL_PATH, sheet_name="Copy of Database")
    print(f"      Total baris ditemukan: {len(df_calib):,} baris")
    print(f"      Kolom: {df_calib.columns.tolist()}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Update schema master_variants jika kolom baru belum ada
    print("\n[2/5] Memeriksa & Mengembangkan Skema 'master_variants' di SQLite...")
    variant_cols = [c[1] for c in cur.execute("PRAGMA table_info(master_variants);").fetchall()]
    new_cols = [
        ("type_code", "VARCHAR(100)"),
        ("commercial_name", "VARCHAR(150)"),
        ("trim_variant", "VARCHAR(100)"),
        ("engine_cc", "INTEGER")
    ]
    for col_name, col_type in new_cols:
        if col_name not in variant_cols:
            print(f"      Menambahkan kolom baru '{col_name}' ({col_type}) ke master_variants...")
            cur.execute(f"ALTER TABLE master_variants ADD COLUMN {col_name} {col_type};")
    conn.commit()

    # 2. Buat tabel official_master_catalog
    print("\n[3/5] Mempersiapkan Tabel 'official_master_catalog'...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS official_master_catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand VARCHAR(100) NOT NULL,
            type_code VARCHAR(120) NOT NULL,
            year INTEGER NOT NULL,
            vehicle_category VARCHAR(50) DEFAULT 'Sepeda Motor',
            commercial_name VARCHAR(150) NOT NULL,
            trim_variant VARCHAR(100),
            engine_cc INTEGER,
            is_ev BOOLEAN DEFAULT 0,
            segment VARCHAR(50),
            matched_variant_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (matched_variant_id) REFERENCES master_variants (id)
        );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_omc_brand ON official_master_catalog (brand);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_omc_type_code ON official_master_catalog (type_code);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_omc_year ON official_master_catalog (year);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_omc_commercial_name ON official_master_catalog (commercial_name);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_omc_is_ev ON official_master_catalog (is_ev);")
    conn.commit()

    # Ambil pemetaan varian eksisting untuk auto-linking
    existing_variants = cur.execute("""
        SELECT v.id, b.name as brand, m.name as model, v.variant_name
        FROM master_variants v
        JOIN master_models m ON v.model_id = m.id
        JOIN master_brands b ON m.brand_id = b.id
    """).fetchall()

    def find_matched_variant_id(brand_str, comm_name_str):
        b_upper = str(brand_str).upper()
        c_lower = str(comm_name_str).lower()
        for v_id, v_brand, v_model, v_var in existing_variants:
            vb_upper = str(v_brand).upper()
            vm_lower = str(v_model).lower()
            if vb_upper in b_upper or b_upper in vb_upper:
                if vm_lower in c_lower:
                    return v_id
        return None

    # Bersihkan tabel official_master_catalog sebelum re-ingest
    cur.execute("DELETE FROM official_master_catalog;")
    conn.commit()

    print("\n[4/5] Memasukkan 4.562 Data Kalibrasi ke 'official_master_catalog'...")
    rows_to_insert = []
    matched_count = 0

    for _, row in df_calib.iterrows():
        brand = str(row["Merek"]).strip()
        type_code = str(row["Kode Tipe"]).strip()
        year = int(row["Tahun"]) if pd.notnull(row["Tahun"]) else 2024
        category = str(row.get("Kategori Jenis", "Sepeda Motor")).strip()
        commercial_name = str(row["Nama Komersil"]).strip()
        
        trim_raw = row["varian"]
        trim = str(trim_raw).strip() if (pd.notnull(trim_raw) and str(trim_raw).lower() != "nan") else None
        
        cc_raw = row["cc"]
        cc = int(float(cc_raw)) if (pd.notnull(cc_raw) and not np.isnan(float(cc_raw))) else None
        
        # Flag EV
        is_ev = bool((cc == 0) or (trim and "electric" in trim.lower()) or ("electric" in commercial_name.lower()) or ("ev" in commercial_name.lower().split()))
        
        segment = classify_segment(category, commercial_name, cc or 0, is_ev)
        matched_vid = find_matched_variant_id(brand, commercial_name)
        if matched_vid:
            matched_count += 1

        rows_to_insert.append((
            brand, type_code, year, category, commercial_name, trim, cc, 1 if is_ev else 0, segment, matched_vid
        ))

    cur.executemany("""
        INSERT INTO official_master_catalog (
            brand, type_code, year, vehicle_category, commercial_name, trim_variant, engine_cc, is_ev, segment, matched_variant_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, rows_to_insert)
    conn.commit()

    print(f"      Berhasil menyimpan {len(rows_to_insert):,} baris ke 'official_master_catalog'.")
    print(f"      Auto-matched ke curated master_variants: {matched_count:,} baris.")

    # 3. Update curated master_variants dengan representatif kode sasis & nama komersil
    print("\n[5/5] Memperkaya 419 Baris 'master_variants' Eksisting...")
    # Cari representasi kode tipe dan komersial dari official_master_catalog
    cur.execute("""
        SELECT matched_variant_id, type_code, commercial_name, trim_variant, engine_cc
        FROM official_master_catalog
        WHERE matched_variant_id IS NOT NULL
        ORDER BY year DESC
    """)
    links = cur.fetchall()
    
    updated_variants = {}
    for vid, t_code, c_name, t_trim, e_cc in links:
        if vid not in updated_variants:
            updated_variants[vid] = (t_code, c_name, t_trim, e_cc)

    for vid, (t_code, c_name, t_trim, e_cc) in updated_variants.items():
        cur.execute("""
            UPDATE master_variants
            SET type_code = ?, commercial_name = ?, trim_variant = ?, engine_cc = ?
            WHERE id = ?
        """, (t_code, c_name, t_trim, e_cc, vid))
    conn.commit()
    print(f"      Berhasil memperbarui data informatif pada {len(updated_variants)} master variants eksisting.")
    conn.close()

    # 4. Sinkronisasi NJKB Enriched Dataset
    if os.path.exists(NJKB_CSV_PATH):
        print(f"\n[BONUS] Menyinkronkan dataset master NJKB: {NJKB_CSV_PATH}")
        df_njkb = pd.read_csv(NJKB_CSV_PATH)
        print(f"      Total baris NJKB: {len(df_njkb):,}")
        
        calib_map = {}
        for _, r in df_calib.iterrows():
            key = (str(r["Merek"]).strip().upper(), str(r["Kode Tipe"]).strip().upper(), int(r["Tahun"]))
            t_trim = str(r["varian"]).strip() if pd.notnull(r["varian"]) and str(r["varian"]).lower() != "nan" else ""
            t_cc = f"{int(float(r['cc']))}cc" if pd.notnull(r['cc']) and float(r['cc']) > 0 else ("EV" if float(r.get('cc', 1)) == 0 else "")
            calib_map[key] = (str(r["Nama Komersil"]).strip(), t_trim, t_cc)

        replaced_count = 0
        for idx, row in df_njkb.iterrows():
            if row.get("Kategori Jenis") == "Sepeda Motor":
                key = (str(row["Merek"]).strip().upper(), str(row["Kode Tipe"]).strip().upper(), int(row["Tahun"]))
                if key in calib_map:
                    c_name, c_trim, c_cc = calib_map[key]
                    df_njkb.at[idx, "Nama Tipe"] = c_name
                    trim_part = f" ({c_trim})" if c_trim else ""
                    df_njkb.at[idx, "Varian Generation"] = f"{c_name}{trim_part}"
                    replaced_count += 1

        print(f"      Berhasil mengalibrasi {replaced_count:,} baris motor di file NJKB master.")
        df_njkb.to_csv(NJKB_CSV_PATH, index=False)
        print(f"      Tersimpan di: {NJKB_CSV_PATH}")
        
        try:
            df_njkb.to_excel(NJKB_XLSX_PATH, index=False)
            print(f"      Tersimpan di: {NJKB_XLSX_PATH}")
        except Exception as e:
            print(f"      Info ekspor Excel: {e}")

    print("\n✅ MIGRASI DAN PENGAYAAN KATALOG SELESAI DENGAN SUKSES!")


if __name__ == "__main__":
    run_migration()
