"""
Kamus Slang & Terminologi Pasar Jual Beli Motor Bekas di Indonesia.
Digunakan oleh rule-based and AI text normalizer untuk ekstraksi metadata.
"""

TAX_PATTERNS = {
    "hidup": [
        r"pajak\s*(?:hidup|on|pjg|panjang|aktif|jalan)",
        r"pjk\s*(?:hidup|on|pjg|panjang|aktif|jln|jalan)",
        r"taat\s*pajak",
        r"surat\s*hidup",
        r"tertib\s*pajak"
    ],
    "mati": [
        r"pjk\s*off\s*(\d+)\s*(?:th|thn|tahun|x|kali)?",
        r"pajak\s*off\s*(\d+)\s*(?:th|thn|tahun|x|kali)?",
        r"pajak\s*mati\s*(\d+)\s*(?:th|thn|tahun|x|kali)?",
        r"telat\s*(?:pajak\s*)?(\d+)\s*(?:th|thn|tahun|x|kali)?",
        r"pajak\s*lewat\s*(\d+)\s*(?:th|thn|tahun)?",
        r"pajak\s*(?:mati|off|tewas|lewat|tidur|bobok)",
        r"pjk\s*(?:mati|off|tewas|lewat|tdr|bobok)"
    ]
}

DOCUMENT_PATTERNS = {
    "lengkap": [
        r"(?:stnk\s*[\+,dan\s]*\s*bpkb)",
        r"(?:surat\s*(?:lengkap|komplit|fullset|komplit plit))",
        r"(?:bpkb\s*[\+,dan\s]*\s*stnk\s*(?:[\+,dan\s]*\s*faktur)?)",
        r"(?:ss\s*(?:lengkap|komplit|ready))",
        r"(?:komplit\s*faktur)"
    ],
    "stnk_only": [
        r"stnk\s*(?:only|tok|aja|doang)",
        r"batangan",
        r"non\s*bpkb",
        r"bpkb\s*(?:hilang|ilang|nyusul|sekolah)",
        r"surat\s*sebelah",
        r"ss\s*stnk\s*only"
    ]
}

PLATE_PATTERNS = [
    r"\bplat\s*([a-zA-Z]{1,2})\b",
    r"\bplat\s*([a-zA-Z]{1,2})\s*(?:dki|jakarta|tangerang|bekasi|depok|bogor|bandung|jogja|surabaya)?\b",
    r"\b([a-zA-Z]{1,2})\s*dki\b",
    r"\b([a-zA-Z]{1,2})\s*kab\b",
    r"\b([a-zA-Z]{1,2})\s*kotamadya\b"
]

DP_SCAM_PATTERNS = [
    r"\bdp\b",
    r"\btanda\s*jadi\b",
    r"\buang\s*muka\b",
    r"\bcicilan\b",
    r"\bangsuran\b",
    r"\bkredit\b",
    r"\bcredit\b",
    r"\bleasing\b",
    r"\boper\s*kredit\b",
    r"\bover\s*kredit\b",
    r"\btake\s*over\b"
]

PRICE_SLANG_PATTERNS = [
    (r"(\d+(?:[\.,]\d+)?)\s*(?:jt|juta)", 1_000_000),
    (r"(\d+(?:[\.,]\d+)?)\s*k\b", 1_000),
    (r"(\d+(?:[\.,]\d+)?)\s*rb\b", 1_000),
]
