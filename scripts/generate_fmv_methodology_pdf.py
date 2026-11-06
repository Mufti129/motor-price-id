#!/usr/bin/env python3
"""
Generator PDF Buku Panduan Lengkap Metodologi Fair Market Value (FMV) Motor Bekas
MotorPrice ID | National Automotive Valuation Engine
Menghasilkan dokumen PDF enterprise yang elegan, padat, dan komprehensif.
"""

import os
import sys
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas dua-tahap untuk menghitung total halaman dinamis (Halaman X dari Y)."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#334155"))
        
        # Running Header (Halaman 2 ke atas)
        if self._pageNumber > 1:
            self.drawString(38, A4[1] - 26, "MOTORPRICE ID")
            self.setFont("Helvetica", 8)
            self.drawString(108, A4[1] - 26, "— Buku Panduan Lengkap Metodologi Fair Market Value (FMV) & Valuasi Agunan")
            self.drawRightString(A4[0] - 38, A4[1] - 26, "Edisi Standar 2026")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(38, A4[1] - 30, A4[0] - 38, A4[1] - 30)

        # Running Footer (Semua halaman)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(38, 34, A4[0] - 38, 34)
        
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#0F172A"))
        self.drawString(38, 22, "DOKUMEN METODOLOGI RESMI")
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(162, 22, "| Hak Cipta MotorPrice ID — Standar Penilaian Agunan & Likuidasi Kendaraan")
        page_str = f"Halaman {self._pageNumber} dari {page_count}"
        self.drawRightString(A4[0] - 38, 22, page_str)
        self.restoreState()

def build_fmv_guide_pdf(output_pdf_paths):
    doc = SimpleDocTemplate(
        output_pdf_paths[0],
        pagesize=A4,
        leftMargin=38,
        rightMargin=38,
        topMargin=38,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()
    
    # Palet Warna Enterprise
    NAVY = colors.HexColor("#0F2942")       # Deep Corporate Navy
    BLUE = colors.HexColor("#1E40AF")       # Classic Blue
    SLATE = colors.HexColor("#334155")      # Dark Slate for body
    MUTED = colors.HexColor("#64748B")      # Muted Gray
    LIGHT_BG = colors.HexColor("#F8FAFC")   # Light gray table background
    CALLOUT_BG = colors.HexColor("#EFF6FF") # Light blue box
    CALLOUT_BORDER = colors.HexColor("#3B82F6")
    GOLD = colors.HexColor("#B45309")
    GOLD_BG = colors.HexColor("#FEF3C7")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=NAVY,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=MUTED,
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'ChapterH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=NAVY,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=BLUE,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=11.8,
        textColor=SLATE,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2.5
    )

    formula_style = ParagraphStyle(
        'FormulaText',
        parent=body_style,
        fontName='Courier-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=10,
        textColor=colors.white,
        alignment=1
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.4,
        leading=9.8,
        textColor=SLATE
    )

    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=table_cell,
        alignment=1
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell,
        fontName='Helvetica-Bold'
    )

    story = []

    # =========================================================================
    # COVER / HEADER BLOCK
    # =========================================================================
    story.append(Paragraph("BUKU PANDUAN LENGKAP & METODOLOGI RESMI", ParagraphStyle('SubHeaderBadge', fontName='Helvetica-Bold', fontSize=8, textColor=BLUE, leading=10, spaceAfter=2)))
    story.append(Paragraph("Sistem Penaksiran & Penentuan Nilai Pasar Wajar<br/>(Fair Market Value - FMV) Sepeda Motor Bekas", title_style))
    story.append(Paragraph("Landasan Teoretis, Standar Penilaian Indonesia (SPI / MAPPI), Alasan Filosofis, Taksonomi Parameter, Algoritma Anti-Distorsi, dan Simulasi Studi Kasus Industri Pembiayaan & Gadai", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=NAVY, spaceBefore=0, spaceAfter=8))

    # Meta Info Card
    meta_data = [
        [
            Paragraph("<b>Penerbit / Tim Teknis:</b><br/>MotorPrice ID Analytics & Risk Engineering", table_cell),
            Paragraph("<b>Edisi Standar:</b><br/>Versi 2.4 — Produksi 2026", table_cell),
            Paragraph("<b>Kategori Dokumen:</b><br/>Metodologi & Standard Operating Procedure", table_cell),
            Paragraph("<b>Tanggal Efektif:</b><br/>" + datetime.now().strftime("%d %B %Y"), table_cell)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[150, 110, 150, 109])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 0.6, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 8))

    # =========================================================================
    # BAB 1: SEJARAH & LATAR BELAKANG PENGEMBANGAN (HISTORY)
    # =========================================================================
    story.append(Paragraph("BAB 1. Riwayat & Latar Belakang Pengembangan (History)", h1_style))
    story.append(Paragraph(
        "Industri keuangan sekunder Indonesia—khususnya lembaga pergadaian (*pawnshop*), perusahaan pembiayaan (*multifinance*), "
        "dan diler jual-beli kendaraan bekas—selama beberapa dekade menghadapi tantangan struktural dalam penaksiran nilai agunan sepeda motor. "
        "Sebelum hadirnya sistem ini, penaksiran motor di industri didominasi oleh dua kelemahan mendasar:",
        body_style
    ))
    story.append(Paragraph(
        "<b>1. Fragmentasi & Ketidaktepatan Kategori Internal:</b> Database historis industri (seperti yang tercermin pada data 555.000+ "
        "transaksi pinjaman internal) hanya mengelompokkan kendaraan dalam <i>tier rentang kapasitas mesin kasar</i> "
        "(misalnya: <code>100cc-124cc</code> atau <code>>139cc-240cc</code>). Padahal dalam rentang <code>100cc-124cc</code>, terdapat rentang nilai "
        "yang sangat lebar antara motor bebek komersil tua (Rp 4-6 juta) dengan matic retro modern seperti Honda Scoopy Prestige (Rp 18-21 juta). "
        "Akibatnya, penaksir lapangan sering kali melakukan penaksiran berlebih (*over-financing*) yang memicu risiko kredit macet (NPL), "
        "atau penaksiran terlalu rendah (*under-financing*) yang menyebabkan hilangnya nasabah potensial.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>2. Distorsi Data Mentah di Marketplace Publik:</b> Ketika perusahaan mencoba mengumpulkan data harga dari platform publik (seperti OLX "
        "atau Facebook Marketplace), data yang ditarik secara mentah terbukti menghasilkan deviasi fatal. Ditemukan lebih dari 20% iklan merupakan "
        "jebakan cicilan/uang muka (DP palsu Rp 500 ribu), harga tipuan/dummy (Rp 123.456), iklan pencarian unit (WTB), serta penjualan aksesoris/helm "
        "yang diberi judul motor. Tanpa mesin pembersih cerdas, data tersebut mengacaukan perhitungan statistik pasar.",
        bullet_style
    ))
    story.append(Paragraph(
        "Merespons kebutuhan tersebut, sistem <b>MotorPrice ID Fair Market Value (FMV) Engine</b> dikembangkan melalui tiga tahapan evolusi: "
        "(a) Pembangunan basis data taksonomi sasis resmi nasional (4.562 kode tipe sasis, 100 merek motor); "
        "(b) Penerapan mesin scraper *stealth headless* dan verifikasi diler bersertifikasi (Momotor Adira Finance) dengan modul *Scam & DP Filter*; serta "
        "(c) Penyusunan algoritma statistik kuantil non-parametrik yang tahan outlier (*robust statistics*) guna menghasilkan nilai wajar yang objektif, auditable, dan presisi.",
        body_style
    ))
    story.append(Spacer(1, 6))

    # =========================================================================
    # BAB 2: ALASAN TEKNIS & FILOSOFI BISNIS (REASONING)
    # =========================================================================
    story.append(Paragraph("BAB 2. Alasan Teknis & Filosofi Bisnis (Reasoning)", h1_style))
    story.append(Paragraph(
        "Mengapa metodologi FMV MotorPrice ID dirancang dengan arsitektur hibrida (kuantil non-parametrik + filter IQR + penyesuaian matriks fisik)? "
        "Berikut adalah argumen teknis dan bisnis di balik pemilihan metode ini:",
        body_style
    ))

    # Tabel Alasan Pemilihan Metode
    reasons_table_data = [
        [Paragraph("Pilihan Metodologi", table_header), Paragraph("Alternatif yang Ditolak", table_header), Paragraph("Alasan Teknis & Bisnis (Rationale)", table_header)],
        [
            Paragraph("<b>Kuartil / Median (P50) Robust</b>", table_cell_bold),
            Paragraph("Rata-rata Aritmatika (Mean / Average)", table_cell),
            Paragraph("Rata-rata sangat rentan terdistorsi oleh 1 listing ekstrim (misal penjual salah ketik Rp 100.000.000 atau Rp 1.000.000). Nilai Median menjamin 50% data di bawah dan 50% di atas, mencerminkan titik tengah transaksi riil yang tidak dapat dimanipulasi oleh pencilan (*outlier-resistant*).", table_cell)
        ],
        [
            Paragraph("<b>Eliminasi Outlier IQR (Tukey's Fences)</b>", table_cell_bold),
            Paragraph("Standar Deviasi (3-Sigma Rule)", table_cell),
            Paragraph("Aturan 3-Sigma mensyaratkan distribusi normal Gauss. Distribusi harga motor bekas memiliki kemencengan positif (*positive skewness*). Metodologi IQR (Jarak Interkuartil) tidak memerlukan asumsi distribusi normal dan memotong harga manipulatif di bawah Q1 - 1.5*IQR dan di atas Q3 + 1.5*IQR.", table_cell)
        ],
        [
            Paragraph("<b>Filter Multi-Faktor DP & Scam</b>", table_cell_bold),
            Paragraph("Filter batas bawah harga statis (hardcoded)", table_cell),
            Paragraph("Batas bawah statis (misal < Rp 3 juta) gagal mendeteksi penipuan canggih di mana penipu memasukkan harga DP Rp 15 juta untuk motor moge Rp 150 juta. Sistem kami menganalisis rasio harga terhadap NJKB resmi serta teks deskripsi (kata kunci: angsuran, cicilan, over kredit, DP).", table_cell)
        ],
        [
            Paragraph("<b>Hierarki Valuasi Bertingkat (Cascade)</b>", table_cell_bold),
            Paragraph("Tolak valuasi jika data persis tidak ada", table_cell),
            Paragraph("Operasional bisnis pembiayaan tidak boleh berhenti saat ada motor langka yang diajukan nasabah. Cascade memberikan kepastian hukum dan operasional: mulai dari level Model-Tahun spesifik -> Rata-rata Model -> Tier Rentang CC -> Inferensi Machine Learning.", table_cell)
        ]
    ]
    t_reasons = Table(reasons_table_data, colWidths=[135, 125, 259])
    t_reasons.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('BOX', (0,0), (-1,-1), 0.6, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_reasons)
    story.append(Spacer(1, 6))

    # =========================================================================
    # BAB 3: REFERENSI STANDAR PENILAIAN (REFERENCES)
    # =========================================================================
    story.append(Paragraph("BAB 3. Referensi Standar Valuasi Nasional & Internasional", h1_style))
    story.append(Paragraph(
        "Metodologi FMV MotorPrice ID mengacu pada konsensus standar profesi penilai publik dan regulasi pembiayaan resmi:",
        body_style
    ))
    story.append(Paragraph(
        "<b>1. Standar Penilaian Indonesia (SPI) 2018 — MAPPI (Masyarakat Profesi Penilai Indonesia):</b> "
        "Mengadopsi secara ketat <i>Pendekatan Pasar (Market Approach)</i> sesuai SPI 106 & SPI 330 (Penilaian Agunan Pembiayaan). "
        "SPI menetapkan bahwa Nilai Pasar adalah estimasi pertukaran aset antara pembeli dan penjual yang berkeinginan menjual "
        "dalam transaksi bebas ikatan (*arm's length transaction*), setelah pemasaran yang layak.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>2. International Valuation Standards (IVS 105 - Valuation Approaches and Methods):</b> "
        "Mengikuti prinsip perbandingan transaksi sejenis (*Comparable Transactions Method*). IVS menegaskan bahwa data pembanding "
        "wajib disesuaikan (*adjusted*) terhadap perbedaan tahun, jarak tempuh, kondisi fisik, dan kelengkapan dokumen kepemilikan.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>3. Best Practices Kelley Blue Book (KBB) & Black Book (Standar Otomotif Global):</b> "
        "Mengadaptasi konsep rentang nilai wajar (*Fair Market Range*), di mana valuasi disajikan sebagai rentang kuantil: "
        "<i>P25 (Batas Likuidasi / Trade-in)</i>, <i>Median / P50 (Nilai Pasar Wajar / Fair Purchase Price)</i>, dan <i>P75 (Batas Retail Showroom)</i>.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>4. Peraturan Otoritas Jasa Keuangan (POJK No. 35/POJK.05/2018):</b> "
        "Memenuhi ketentuan tata kelola risiko agunan pembiayaan, di mana penaksiran nilai barang agunan harus dapat diverifikasi "
        "sumber buktinya (*verifiable evidence*) dan memiliki batasan rasio pembiayaan terhadap nilai aset (*Loan-to-Value / LTV*).",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>5. Regulasi Fiskal NJKB (Permendagri No. 6 Tahun 2023 & Bapenda SAMSAT):</b> "
        "Menggunakan Nilai Jual Kendaraan Bermotor resmi sebagai jangkar batas bawah (*anchor ground-truth*) guna mendeteksi kecurangan manipulasi harga.",
        bullet_style
    ))
    story.append(Spacer(1, 6))

    # =========================================================================
    # BAB 4: DEFINISI LENGKAP SETIAP PARAMETER
    # =========================================================================
    story.append(Paragraph("BAB 4. Definisi & Taksonomi Parameter Valuasi", h1_style))
    story.append(Paragraph(
        "Berikut adalah kamus parameter lengkap yang diproses oleh algoritma perhitungan FMV MotorPrice ID:",
        body_style
    ))

    params_data = [
        [Paragraph("Nama Parameter", table_header), Paragraph("Tipe Data", table_header), Paragraph("Sumber Data", table_header), Paragraph("Definisi & Peran dalam Valuasi", table_header)],
        [
            Paragraph("<b>Merek (Brand)</b>", table_cell_bold),
            Paragraph("String", table_cell_center),
            Paragraph("Katalog Sasis TPT", table_cell),
            Paragraph("Pabrikan pembuat unit (mis. Honda, Yamaha, Kawasaki). Menentukan koefisien depresiasi merek dan daya likuiditas pasar sekunder.", table_cell)
        ],
        [
            Paragraph("<b>Kode Tipe Sasis (Type Code)</b>", table_cell_bold),
            Paragraph("String", table_cell_center),
            Paragraph("SAMSAT / Bapenda", table_cell),
            Paragraph("Kode registrasi pabrikan pada STNK/BPKB (mis. <code>H1B02N53L1 AT</code>, <code>BLS AT</code>). Kunci primer pencocokan varian resmi.", table_cell)
        ],
        [
            Paragraph("<b>Nama Komersil (Commercial Name)</b>", table_cell_bold),
            Paragraph("String", table_cell_center),
            Paragraph("Master Terintegrasi", table_cell),
            Paragraph("Nama dagang yang dikenal konsumen umum (mis. Honda BeAT Deluxe, Yamaha All New NMAX 155 Connected).", table_cell)
        ],
        [
            Paragraph("<b>Tahun Pembuatan / Rilis (Year)</b>", table_cell_bold),
            Paragraph("Integer", table_cell_center),
            Paragraph("Faktur / STNK", table_cell),
            Paragraph("Tahun perakitan resmi unit. Basis penentuan usia pakai kendaraan dalam rumus depresiasi waktu.", table_cell)
        ],
        [
            Paragraph("<b>Harga Pasar Riil (Price, IDR)</b>", table_cell_bold),
            Paragraph("Numeric (Rp)", table_cell_center),
            Paragraph("Momotor & OLX", table_cell),
            Paragraph("Nilai transaksi tunai penawaran unit yang lolos verifikasi anti-scam. Parameter input utama distribusi pasar.", table_cell)
        ],
        [
            Paragraph("<b>Jarak Tempuh (Odometer, KM)</b>", table_cell_bold),
            Paragraph("Integer", table_cell_center),
            Paragraph("Inspeksi Diler", table_cell),
            Paragraph("Total kilometer pemakaian fisik. Digunakan untuk menghitung penalti/bonus kondisi keausan mesin.", table_cell)
        ],
        [
            Paragraph("<b>Kelengkapan Dokumen (Legal Papers)</b>", table_cell_bold),
            Paragraph("Categorical", table_cell_center),
            Paragraph("Listing / Petugas", table_cell),
            Paragraph("Status fisik BPKB dan STNK. Mempengaruhi faktor diskon legalitas (Full Paper = 100%, Non-BPKB = 55-65%).", table_cell)
        ],
        [
            Paragraph("<b>Status Pajak SAMSAT (Tax Status)</b>", table_cell_bold),
            Paragraph("Categorical", table_cell_center),
            Paragraph("Data Bapenda", table_cell),
            Paragraph("Status masa berlaku Pajak Kendaraan Bermotor (PKB). Pajak mati dikenakan potongan biaya denda dan pokok tertunggak.", table_cell)
        ],
        [
            Paragraph("<b>Tier Kategori Internal (29 Tiers)</b>", table_cell_bold),
            Paragraph("String", table_cell_center),
            Paragraph("Matriks Pemetaan", table_cell),
            Paragraph("Kategori transaksi internal multifinance (mis. <code>Honda 100cc-124cc</code>, <code>Yamaha >139cc – 240cc</code>). Menjadi acuan fallback agregat.", table_cell)
        ],
        [
            Paragraph("<b>Harga FMV Median (P50)</b>", table_cell_bold),
            Paragraph("Numeric (Rp)", table_cell_center),
            Paragraph("Kalkulasi Engine", table_cell),
            Paragraph("Nilai tengah pasar wajar. Menjadi acuan plafon pembiayaan standar industri pembiayaan dan penaksiran gadai.", table_cell)
        ]
    ]
    t_params = Table(params_data, colWidths=[115, 60, 95, 249])
    t_params.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('BOX', (0,0), (-1,-1), 0.6, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_params)
    story.append(Spacer(1, 6))

    # =========================================================================
    # BAB 5: FORMULA MATEMATIS & ALGORITMA PERHITUNGAN FMV
    # =========================================================================
    story.append(Paragraph("BAB 5. Algoritma & Formula Matematis Perhitungan FMV", h1_style))
    story.append(Paragraph(
        "Penentuan nilai pasar wajar dilakukan melalui alur komputasi 5 tahap berurutan:",
        body_style
    ))

    # Tahap 1
    story.append(Paragraph("<b>Tahap 1: Eliminasi Outlier Menggunakan Tukey's Interquartile Range (IQR)</b>", h2_style))
    story.append(Paragraph(
        "Untuk setiap sampel harga listing riil pada kombinasi Model dan Tahun tertentu, kumpulan data harga <i>P = {p_1, p_2, ..., p_n}</i> "
        "diurutkan secara ascending. Nilai Kuartil Bawah (Q1 / 25th percentile) dan Kuartil Atas (Q3 / 75th percentile) dihitung:",
        body_style
    ))
    
    f1_data = [[
        Paragraph(
            "<b>IQR = Q3 - Q1</b><br/>"
            "Batas Bawah Valid (Lower Fence) = max(Rp 2.500.000, Q1 - 1.5 * IQR)<br/>"
            "Batas Atas Valid (Upper Fence)  = Q3 + 1.5 * IQR<br/>"
            "<i>Data harga di luar batas ini secara otomatis dianulir dari perhitungan statistik.</i>",
            formula_style
        )
    ]]
    t_f1 = Table(f1_data, colWidths=[519])
    t_f1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CALLOUT_BG),
        ('BOX', (0,0), (-1,-1), 0.8, CALLOUT_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_f1)
    story.append(Spacer(1, 4))

    # Tahap 2 & 3
    story.append(Paragraph("<b>Tahap 2 & 3: Kuantil Non-Parametrik & Matriks Penyesuaian Kondisi Riil Unit</b>", h2_style))
    story.append(Paragraph(
        "Dari kumpulan data bersih yang telah difilter <i>P_clean</i>, dihitung tiga nilai acuan utama pasar sekunder: "
        "<b>P25 (Batas Likuidasi)</b>, <b>P50 / Median (FMV Standar)</b>, dan <b>P75 (Batas Retail Showroom)</b>. "
        "Untuk penaksiran unit individu nasabah, diaplikasikan faktor penyesuaian (*Adjustment Multiplier*):",
        body_style
    ))

    adj_table_data = [
        [Paragraph("Komponen Penyesuaian", table_header), Paragraph("Kondisi Fisik / Legalitas Unit", table_header), Paragraph("Faktor Penyesuaian (Multipliers / Deductions)", table_header)],
        [
            Paragraph("<b>Kelengkapan Surat (Dokumen)</b>", table_cell_bold),
            Paragraph("BPKB + STNK Lengkap (Full Paper)<br/>Hanya STNK (BPKB Hilang / Macet Leasing)<br/>Hanya BPKB (STNK Hilang)", table_cell),
            Paragraph("<b>1.00 (100% dari FMV)</b><br/><b>0.55 - 0.65 (Diskon 35% - 45%)</b> <i>[High Risk]</i><br/><b>0.90 - 0.93 (Diskon 7% - 10% untuk biaya duplikat)</b>", table_cell)
        ],
        [
            Paragraph("<b>Status Pajak Kendaraan (PKB)</b>", table_cell_bold),
            Paragraph("Pajak Hidup / Panjang<br/>Pajak Mati 1 Tahun<br/>Pajak Mati >= 2 Tahun s/d Ganti Kaleng", table_cell),
            Paragraph("<b>1.00 (Tanpa Potongan)</b><br/><b>Potongan: 1x PKB Pokok + Denda SWDKLLJ</b><br/><b>Potongan: (n x PKB Pokok) + Denda + Biaya Balik Nama</b>", table_cell)
        ],
        [
            Paragraph("<b>Jarak Tempuh (Odometer)</b>", table_cell_bold),
            Paragraph("KM Rendah (< 6.000 km / tahun)<br/>KM Normal (6.000 - 15.000 km / tahun)<br/>KM Tinggi (> 25.000 km / tahun)", table_cell),
            Paragraph("<b>+2.5% s/d +5.0% (Apresiasi Kondisi Mesin Prima)</b><br/><b>0.0% (Standar FMV)</b><br/><b>-4.0% s/d -8.0% (Depresiasi Keausan Komponen)</b>", table_cell)
        ],
        [
            Paragraph("<b>Indeks Wilayah Pasar (Regional)</b>", table_cell_bold),
            Paragraph("DKI Jakarta & Bodetabek<br/>Jawa Barat, Jawa Tengah, Jawa Timur<br/>Luar Pulau Jawa (Sumatera, Bali, Kalimantan)", table_cell),
            Paragraph("<b>1.00 (Indeks Acuan Nasional)</b><br/><b>0.96 - 0.98 (Daya Beli Regional Sedang)</b><br/><b>1.04 - 1.08 (Biaya Logistik & Pasokan Terbatas)</b>", table_cell)
        ]
    ]
    t_adj = Table(adj_table_data, colWidths=[140, 160, 219])
    t_adj.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('BOX', (0,0), (-1,-1), 0.6, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_adj)
    story.append(Spacer(1, 6))

    # =========================================================================
    # BAB 6: HIERARKI VALUASI BERTINGKAT (CASCADING FALLBACK)
    # =========================================================================
    story.append(Paragraph("BAB 6. Hierarki Valuasi Bertingkat (Cascading Fallback Framework)", h1_style))
    story.append(Paragraph(
        "Untuk menjamin kelancaran operasional penaksir lapangan saat menghadapi ribuan varian motor di Indonesia, "
        "sistem menggunakan algoritma pencarian bertingkat (*Tiered Cascade Lookup*):",
        body_style
    ))

    hier_data = [
        [Paragraph("Tingkat Prioritas", table_header), Paragraph("Tingkat Presisi", table_header), Paragraph("Sumber Komputasi Data", table_header), Paragraph("Kondisi Eksekusi", table_header)],
        [
            Paragraph("<b>Level 1: Exact Model & Year</b>", table_cell_bold),
            Paragraph("<font color='#059669'><b>Maksimal (98-100%)</b></font>", table_cell),
            Paragraph("Data tarikan riil OLX & Momotor dengan Nama Komersil dan Tahun yang identik.", table_cell),
            Paragraph("Tersedia data listing riil pada kombinasi model & tahun bersangkutan (Sampel >= 1).", table_cell)
        ],
        [
            Paragraph("<b>Level 2: Model Overall Average</b>", table_cell_bold),
            Paragraph("<font color='#2563EB'><b>Tinggi (90-95%)</b></font>", table_cell),
            Paragraph("Rata-rata harga seluruh tahun model tersebut dikoreksi kurva depresiasi tahunan (8%/thn).", table_cell),
            Paragraph("Model pernah ditarik pasarnya, tetapi tahun spesifik unit nasabah belum ada listingnya.", table_cell)
        ],
        [
            Paragraph("<b>Level 3: Internal Tier Benchmark</b>", table_cell_bold),
            Paragraph("<font color='#D97706'><b>Menengah (80-88%)</b></font>", table_cell),
            Paragraph("Median harga riil dari 29 kategori tier internal (misal: <code>Honda 100cc-124cc</code>).", table_cell),
            Paragraph("Model komersil tidak ada di pasar, namun merek dan rentang CC internal terdaftar.", table_cell)
        ],
        [
            Paragraph("<b>Level 4: Machine Learning Inference</b>", table_cell_bold),
            Paragraph("<font color='#4F46E5'><b>Cerdas (82-90%)</b></font>", table_cell),
            Paragraph("Model HistGradientBoosting terlatih berbasis NJKB, Segmen, CC, dan Bobot Kendaraan.", table_cell),
            Paragraph("Unit langka / CBU / brand baru yang tidak memiliki riwayat transaksi pasar.", table_cell)
        ]
    ]
    t_hier = Table(hier_data, colWidths=[115, 95, 169, 140])
    t_hier.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('BOX', (0,0), (-1,-1), 0.6, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_hier)
    story.append(Spacer(1, 6))

    # =========================================================================
    # BAB 7: SISTEM ANTI-FRAUD & FILTER ANOMALI
    # =========================================================================
    story.append(Paragraph("BAB 7. Sistem Anti-Fraud & Filtrasi Anomali Data", h1_style))
    story.append(Paragraph(
        "Kunci utama dari keandalan FMV MotorPrice ID adalah modul <code>ScamAndDPDetector</code> yang bekerja secara proaktif "
        "sebelum data dimasukkan ke database statistik. Modul ini menjalankan aturan verifikasi sebagai berikut:",
        body_style
    ))
    story.append(Paragraph("1. <b>Deteksi Uang Muka Kredit (DP Traps):</b> Menganalisis teks judul dan deskripsi terhadap kata kunci pembiayaan (<i>DP, cicilan, angsuran, kredit murah, over kredit</i>). Bila rasio harga listing terhadap NJKB resmi < 30%, listing otomatis ditandai sebagai DP dan dikarantina dari perhitungan FMV.", bullet_style))
    story.append(Paragraph("2. <b>Deteksi Harga Tipuan / Dummy:</b> Mengidentifikasi pola angka berulang (misal Rp 1.111.111, Rp 12.345, Rp 1.234.567) atau nilai tidak masuk akal (< Rp 2.500.000 untuk motor aktif).", bullet_style))
    story.append(Paragraph("3. <b>Deteksi Aksesoris & Helm:</b> Memfilter iklan knalpot, velg, helm, cover bodi, atau surat/stnk lepasan yang diposting pada kategori motor bekas.", bullet_style))
    story.append(Paragraph("4. <b>Scoped DOM Container Extraction:</b> (Pembaruan Terbaru) Mesin ekstraksi OLX mengunci selektor harga ke dalam container judul utama <code>&lt;h1&gt;</code>, mencegah tertukarnya harga dengan kartu iklan rekomendasi sponsor.", bullet_style))
    story.append(Spacer(1, 6))

    # =========================================================================
    # BAB 8: SIMULASI PERHITUNGAN DALAM BERBAGAI STUDI KASUS RIIL
    # =========================================================================
    story.append(Paragraph("BAB 8. Simulasi Perhitungan Detail Multi-Kasus Riil (Case Studies)", h1_style))
    story.append(Paragraph(
        "Berikut adalah 5 simulasi perhitungan penaksiran nilai agunan menggunakan data pasar riil dan matriks penyesuaian:",
        body_style
    ))

    # Case 1
    c1_content = [
        Paragraph("<b>KASUS 1: Unit Populer Standar — Honda BeAT Deluxe 2023 (Kondisi Prima)</b>", ParagraphStyle('C1Title', fontName='Helvetica-Bold', fontSize=8.5, textColor=BLUE)),
        Paragraph("• <b>Spesifikasi Unit:</b> Honda BeAT CBS-ISS Deluxe (Kode Sasis: <code>Y1G02N15L0 AT</code>), Tahun 2023, Plat B (Jakarta Selatan).<br/>"
                  "• <b>Kondisi Fisik:</b> BPKB & STNK Asli Lengkap, Pajak Hidup (Masa berlaku 8 bulan ke depan), Odometer 12.500 km (Kategori Normal).<br/>"
                  "• <b>Data Pasar Riil (List Harga Tarikan):</b> Sampel listing riil BeAT 2023: Min Rp 14.500.000, <b>Median (P50) = Rp 16.000.000</b>, P75 = Rp 16.800.000.<br/>"
                  "• <b>Perhitungan Penyesuaian:</b> Faktor Surat = 1.00; Pajak Hidup = 1.00; Odo Normal = 1.00; Wilayah Jakarta = 1.00.<br/>"
                  "• <b>HASIL FMV AKHIR: Rp 16.000.000</b> | <b>Rekomendasi Plafon Gadai / LTV 75%: Rp 12.000.000</b> (Aman dengan bantalan risiko likuidasi 25%).", table_cell)
    ]
    t_c1 = Table([[c1_content]], colWidths=[519])
    t_c1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_c1)
    story.append(Spacer(1, 4))

    # Case 2
    c2_content = [
        Paragraph("<b>KASUS 2: Unit Maxi Scooter dengan Pajak Mati 2 Tahun & Odo Tinggi — Yamaha NMAX 155 2021</b>", ParagraphStyle('C2Title', fontName='Helvetica-Bold', fontSize=8.5, textColor=BLUE)),
        Paragraph("• <b>Spesifikasi Unit:</b> Yamaha All New NMAX 155 Connected (Kode Sasis: <code>B6H AT</code>), Tahun 2021, Plat L (Surabaya).<br/>"
                  "• <b>Kondisi Fisik:</b> BPKB & STNK Lengkap. Pajak Mati 2 Tahun (PKB Pokok Rp 450.000/thn). Odometer 48.000 km (Tinggi, ~12.000 km di atas normal).<br/>"
                  "• <b>Data Pasar Riil:</b> Baseline FMV Median NMAX 2021 = <b>Rp 24.500.000</b>.<br/>"
                  "• <b>Perhitungan Penyesuaian:</b> Penalti Odo Tinggi (-5%) = -Rp 1.225.000; Tunggakan Pajak 2 Tahun = -Rp 1.080.000; Koreksi Indeks Surabaya (0.98).<br/>"
                  "• <b>HASIL FMV AKHIR: Rp 21.750.000</b> (Terkoreksi realistis dari baseline pasar Rp 24,5 jt) | <b>Plafon Gadai (LTV 70%): Rp 15.225.000</b>.", table_cell)
    ]
    t_c2 = Table([[c2_content]], colWidths=[519])
    t_c2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_c2)
    story.append(Spacer(1, 4))

    # Case 3
    c3_content = [
        Paragraph("<b>KASUS 3: Dokumen Tidak Lengkap (Hanya STNK / Non-BPKB) — Honda Vario 160 2022</b>", ParagraphStyle('C3Title', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.HexColor("#B91C1C"))),
        Paragraph("• <b>Spesifikasi Unit:</b> Honda Vario 160 CBS (Kode Sasis: <code>L1K02Q33L1 AT</code>), Tahun 2022, Lokasi Jakarta.<br/>"
                  "• <b>Kondisi Fisik:</b> STNK Asli Ada & Pajak Hidup, namun BPKB Hilang / Masih Terikat Leasing Pihak Ketiga.<br/>"
                  "• <b>Data Pasar Riil:</b> Baseline FMV Vario 160 2022 (Full Paper) = <b>Rp 22.500.000</b>.<br/>"
                  "• <b>Penerapan Risiko Legalitas:</b> Faktor Non-BPKB <b>0.60 (Diskon 40%)</b> -> Nilai Taksiran Non-BPKB = <b>Rp 13.500.000</b>.<br/>"
                  "• <b>KEBIJAKAN OPERASIONAL: REJECT / QUARANTINE</b> (SOP Pergadaian Resmi melarang penerimaan gadai kendaraan tanpa BPKB asli "
                  "guna menghindari delik fidusia KUHP Pasal 372). Nilai Rp 13,5 jt hanya berlaku untuk kalkulasi likuidasi aset macet.", table_cell)
    ]
    t_c3 = Table([[c3_content]], colWidths=[519])
    t_c3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF2F2")),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#EF4444")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_c3)
    story.append(Spacer(1, 4))

    # Case 4 & 5
    c4_content = [
        Paragraph("<b>KASUS 4: Unit Langka / Data Spesifik Terbatas — Vespa Sprint 150 i-Get 2024</b>", ParagraphStyle('C4Title', fontName='Helvetica-Bold', fontSize=8.5, textColor=BLUE)),
        Paragraph("• <b>Situasi Data:</b> Belum banyak listing unit seken 2024. <b>Eksekusi Cascade:</b> Level 1 (Listing Diler Momotor = Rp 52.500.000); Level 2 (Rata-rata Model Sprint dikoreksi faktor tahun baru = Rp 52.440.000); Level 3 (P75 Tier Vespa >139cc = Rp 52.000.000).<br/>"
                  "• <b>HASIL FMV AKHIR: Rp 52.500.000</b> (Konvergensi presisi antar level membuktikan keandalan sistem multi-level) | <b>Plafon LTV 70%: Rp 36.750.000</b>.", table_cell)
    ]
    t_c4 = Table([[c4_content]], colWidths=[519])
    t_c4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_c4)
    story.append(Spacer(1, 4))

    c5_content = [
        Paragraph("<b>KASUS 5: Filtrasi Anomali & Penggagalan Jebakan DP Kredit (Anti-Scam Proof)</b>", ParagraphStyle('C5Title', fontName='Helvetica-Bold', fontSize=8.5, textColor=GOLD)),
        Paragraph("• <b>Kasus Listing Masuk:</b> Iklan OLX: <i>'PROMO DP 1.5 JT HONDA VARIO 160 CBS 2024 SIAP PAKAI'</i>, harga tertulis Rp 1.500.000.<br/>"
                  "• <b>Deteksi:</b> NJKB resmi varian Vario 160 2024 = Rp 19.800.000. Rasio listing terhadap NJKB = <b>7.57%</b> (< ambang 30%). Teks mengandung token 'DP' dan 'PROMO'.<br/>"
                  "• <b>TINDAKAN SISTEM: QUARANTINED (IS_DP_PRICE = TRUE)</b>. Iklan diblokir total dari tabel <code>List Harga Tarikan</code> sehingga tidak mencemari formula FMV.", table_cell)
    ]
    t_c5 = Table([[c5_content]], colWidths=[519])
    t_c5.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), GOLD_BG),
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#F59E0B")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_c5)
    story.append(Spacer(1, 6))

    # =========================================================================
    # BAB 9: PANDUAN PENGGUNAAN PADA SPREADSHEET EXCEL
    # =========================================================================
    story.append(Paragraph("BAB 9. Panduan Operasional pada File Spreadsheet Master", h1_style))
    story.append(Paragraph(
        "Untuk tim penaksir dan data analyst yang menggunakan file "
        "<code>pemetaan_tipe_motor_internal_vs_tarikan.xlsx</code>, berikut adalah panduan praktis pemanfaatan rumus:",
        body_style
    ))
    story.append(Paragraph("1. <b>Navigasi Tab Menu:</b> Buka sheet <code>Katalog Master Tarikan (4.5K)</code>. Geser ke Kolom L (<i>Harga FMV</i>), Kolom M (<i>Metode Perhitungan FMV</i>), dan Kolom N (<i>Sampel Riil</i>).", bullet_style))
    story.append(Paragraph("2. <b>Sifat Rumus Dinamis:</b> Rumus di Kolom L terhubung langsung secara *live* ke tab <code>List Harga Tarikan</code>. Jika Anda menambahkan listing baru di tab tersebut, nilai FMV pada tab master akan langsung terupdate otomatis tanpa perlu makro/VBA.", bullet_style))
    story.append(Paragraph("3. <b>Integrasi ke Database Internal 555k Transaksi:</b> Kolom <code>harga_tipe</code> pada file transaksi pinjaman (<code>datat_internal.csv</code>) dapat langsung diisi menggunakan rumus VLOOKUP / XLOOKUP merujuk ke tab <code>Acuan Tier Internal (29 Kategori)</code> berdasarkan nama kolom <code>merk</code> dan <code>tipe</code>.", bullet_style))
    story.append(Paragraph("4. <b>Audit Trail & Kepastian Hukum:</b> Setiap nilai taksiran memiliki rekam jejak digital lengkap yang mencantumkan ID listing asal, URL aktif iklan, tanggal penarikan, dan nama diler pemeriksa.", bullet_style))
    story.append(Spacer(1, 8))

    # Tanda Tangan / Penutup Dokumen
    sign_data = [
        [
            Paragraph("<b>Disusun & Divalidasi Oleh:</b><br/>Tim Riset Kuantitatif & Valuasi Agunan<br/><b>MotorPrice ID</b>", table_cell),
            Paragraph("<b>Disetujui untuk Operasional:</b><br/>Head of Credit Risk & Asset Appraisal<br/><b>Divisi Manajemen Risiko & Teknologi</b>", table_cell),
            Paragraph("<b>Status Dokumen:</b><br/><font color='#059669'><b>OPERATIONAL & APPROVED</b></font><br/>Berlaku Nasional", table_cell)
        ]
    ]
    t_sign = Table(sign_data, colWidths=[175, 175, 169])
    t_sign.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 0.6, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(KeepTogether([t_sign]))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✅ [PDF BERHASIL DIBUAT] {output_pdf_paths[0]}")

    # Salin ke seluruh target lokasi
    for p in output_pdf_paths[1:]:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        import shutil
        shutil.copyfile(output_pdf_paths[0], p)
        print(f"✅ [PDF DISALIN] {p}")

if __name__ == "__main__":
    targets = [
        "/Users/macbookair/Downloads/PANDUAN_METODOLOGI_FMV_MOTOR_LENGKAP.pdf",
        "/Users/macbookair/Downloads/Pemetaan database motor tarikan dan database internal/PANDUAN_METODOLOGI_FMV_MOTOR_LENGKAP.pdf",
        "/Users/macbookair/Documents/Scrape Data/data/reports/PANDUAN_METODOLOGI_FMV_MOTOR_LENGKAP.pdf"
    ]
    build_fmv_guide_pdf(targets)
