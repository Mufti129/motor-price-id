"""
Interactive CLI Tool: IBID Astra MAP Car Valuation Engine
Memungkinkan pengecekan nilai lelang mobil langsung dari terminal.
"""

import sys
from ibid_map_client import IbidMapClient

def format_rupiah(val):
    if val is None:
        return "N/A"
    try:
        return f"Rp {float(val):,.0f}".replace(",", ".")
    except:
        return str(val)

def main():
    client = IbidMapClient()
    print("=" * 65)
    print("  IBID ASTRA MAP (MARKET AUCTION PRICE) - CAR VALUATION ENGINE")
    print("=" * 65)

    brands_data = client.get_brands()
    if not brands_data:
        print("[!] Gagal mengambil data merek. Periksa koneksi internet.")
        return

    brands = [b.get("label") for b in brands_data if b.get("label")]
    print("\n[+] Merek Tersedia:", ", ".join(brands[:15]) + " ...")
    
    brand_input = input("\nMasukkan Nama Merek (contoh: TOYOTA): ").strip().upper()
    if brand_input not in brands:
        print(f"[!] Merek '{brand_input}' tidak ditemukan di katalog.")
        return

    print(f"\n[*] Mengambil daftar model/seri untuk {brand_input}...")
    variants = client.get_variants(merk=brand_input)
    if not variants:
        print(f"[!] Tidak ada data varian untuk {brand_input}.")
        return

    series_list = sorted(list(set([v.get("seri") for v in variants if v.get("seri")])))
    print(f"[+] Seri/Model Tersedia ({len(series_list)}):", ", ".join(series_list))
    
    seri_input = input("\nMasukkan Nama Seri (contoh: AVANZA): ").strip().upper()
    
    # Filter variants for chosen series
    sub_variants = [v for v in variants if v.get("seri") == seri_input]
    if not sub_variants:
        print(f"[!] Seri '{seri_input}' tidak ditemukan.")
        return

    types = sorted(list(set([v.get("tipe") for v in sub_variants if v.get("tipe")])))
    years = sorted(list(set([str(v.get("tahun")) for v in sub_variants if v.get("tahun")])))
    cylinders = sorted(list(set([str(v.get("silinder")) for v in sub_variants if v.get("silinder")])))

    print(f"[+] Pilihan Tipe:", ", ".join(types))
    print(f"[+] Pilihan Tahun:", ", ".join(years))
    print(f"[+] Pilihan Silinder (CC/Liter):", ", ".join(cylinders))

    tipe_input = input("\nMasukkan Tipe (contoh: G): ").strip().upper()
    silinder_input = input("Masukkan Silinder (contoh: 1.3): ").strip()
    tahun_input = input("Masukkan Tahun (contoh: 2019): ").strip()
    trans_input = input("Masukkan Transmisi (MT / AT, default MT): ").strip().upper() or "MT"

    print("\n" + "-" * 65)
    print(f"[*] Melakukan valuasi lelang untuk: {brand_input} {seri_input} {tipe_input} {silinder_input} ({tahun_input} {trans_input})...")
    print("-" * 65)

    # 1. Price Check
    price_res = client.check_price(
        merk=brand_input,
        seri=seri_input,
        silinder=silinder_input,
        tipe=tipe_input,
        tahun=tahun_input,
        transmisi=trans_input
    )

    min_p = price_res.get("min_harga")
    max_p = price_res.get("max_harga")

    print("\n📊 HASIL ESTIMASI HARGA PASAR LELANG (MAP):")
    print(f"  • Harga Minimum Lelang : {format_rupiah(min_p)}")
    print(f"  • Harga Maksimum Lelang: {format_rupiah(max_p)}")

    # 2. Grade Analysis
    grade_res = client.get_price_by_grade(
        brand=brand_input,
        series=seri_input,
        cylinder=silinder_input,
        tipe=tipe_input,
        year=tahun_input,
        transmission=trans_input
    )

    grade_items = grade_res.get("item", []) if isinstance(grade_res, dict) else []
    if grade_items:
        print("\n🔍 ESTIMASI BERDASARKAN KONDISI / GRADE INSPEKSI ACV:")
        for item in grade_items:
            g = item.get("grade")
            p = item.get("totalHarga") or item.get("hargaTertinggi") or item.get("hargaTerendah")
            print(f"  • Grade {g} : {format_rupiah(p)}")

    print("\n" + "=" * 65)


if __name__ == "__main__":
    main()
