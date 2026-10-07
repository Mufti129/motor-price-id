"""
Master Data Seeder untuk Katalog Motor Resmi di Indonesia (12 Tahun Terakhir: 2014 - 2026).
Riset komprehensif seluruh Merk, Model, Varian Lengkap, CC Mesin, Kategori, MSRP Baru, dan Aliases.
"""
from models.database import SessionLocal, init_db
from models.catalog import MasterBrand, MasterModel, MasterVariant

MASTER_MOTOR_DATA = [
    {
        "brand": "Honda",
        "country": "Jepang",
        "models": [
            {
                "name": "Beat",
                "category": "Matic",
                "cc": 110,
                "variants": [
                    {"name": "Beat Karburator (Generasi 1)", "start": 2008, "end": 2012, "msrp": 12500000, "aliases": "beat karbu, beat lama, beat gen 1"},
                    {"name": "Beat FI (Injeksi Gen 1)", "start": 2012, "end": 2014, "msrp": 14200000, "aliases": "beat fi lama, beat injeksi 2013 2014"},
                    {"name": "Beat FI eSP (Generasi 2/3)", "start": 2014, "end": 2020, "msrp": 15500000, "aliases": "beat fi, beat esp, beat cbs iss"},
                    {"name": "Beat Pop eSP", "start": 2015, "end": 2019, "msrp": 15100000, "aliases": "beat pop, beat pop esp, beat pop cbs iss"},
                    {"name": "Beat Street eSP (Generasi 1)", "start": 2016, "end": 2020, "msrp": 16800000, "aliases": "beat street lama, beat strit 2017 2018 2019"},
                    {"name": "Beat Street eSAF (Generasi 2)", "start": 2020, "end": 2024, "msrp": 18700000, "aliases": "beat street new, beat street esaf"},
                    {"name": "Beat Deluxe / CBS (eSAF)", "start": 2020, "end": 2024, "msrp": 18200000, "aliases": "beat deluxe, beat esaf, beat cbs baru, all new beat"},
                    {"name": "Beat All New Smart Key (2024+)", "start": 2024, "end": 2026, "msrp": 19830000, "aliases": "beat smart key, beat 2024, beat keyless, beat deluxe smart key"},
                    {"name": "Beat Street All New (2024+)", "start": 2024, "end": 2026, "msrp": 19300000, "aliases": "beat street 2024, all new beat street"}
                ]
            },
            {
                "name": "Vario",
                "category": "Matic",
                "cc": 125,
                "variants": [
                    {"name": "Vario 110 Karbu / Techno", "start": 2006, "end": 2014, "msrp": 14000000, "aliases": "vario karbu, vario 110 cw, vario techno 110"},
                    {"name": "Vario 110 eSP LED", "start": 2015, "end": 2019, "msrp": 17200000, "aliases": "vario 110 led, vario 110 esp, vario 110 remote"},
                    {"name": "Vario 125 Techno Helm-In (Karbu/FI)", "start": 2012, "end": 2015, "msrp": 16500000, "aliases": "vario 125 bohlam, vario 125 techno 2013 2014"},
                    {"name": "Vario 125 eSP (LED Generasi 1)", "start": 2015, "end": 2018, "msrp": 18500000, "aliases": "vario 125 led lama, vario 125 esp 2015 2016 2017"},
                    {"name": "Vario 125 All New (Generasi 2)", "start": 2018, "end": 2022, "msrp": 22000000, "aliases": "vario 125 new, vario 125 cbs iss 2018 2019 2020 2021"},
                    {"name": "Vario 125 Facelift (Keyless)", "start": 2022, "end": 2026, "msrp": 24500000, "aliases": "vario 125 new keyless, vario 125 smart key"},
                    {"name": "Vario 150 eSP Exclusive (Gen 1)", "start": 2015, "end": 2018, "msrp": 22500000, "aliases": "vario 150 led lama, vario 150 esp 2015 2016 2017"},
                    {"name": "Vario 150 eSP Exclusive / Keyless (Gen 2)", "start": 2018, "end": 2022, "msrp": 24900000, "aliases": "vario 150, vario 150 keyless, vario 150 esp, vario 150 led"},
                    {"name": "Vario 160 CBS", "start": 2022, "end": 2026, "msrp": 27350000, "aliases": "vario 160 cbs, all new vario 160"},
                    {"name": "Vario 160 ABS", "start": 2022, "end": 2026, "msrp": 30230000, "aliases": "vario 160 abs, vario 160 cakram belakang"}
                ]
            },
            {
                "name": "Stylo 160",
                "category": "Retro Modern Matic",
                "cc": 160,
                "variants": [
                    {"name": "Stylo 160 CBS", "start": 2024, "end": 2026, "msrp": 27550000, "aliases": "honda stylo, stylo 160, stylo cbs, honda stilo"},
                    {"name": "Stylo 160 ABS (Keyless)", "start": 2024, "end": 2026, "msrp": 30420000, "aliases": "stylo 160 abs, stylo abs smart key, all new stylo"}
                ]
            },
            {
                "name": "Scoopy",
                "category": "Matic",
                "cc": 110,
                "variants": [
                    {"name": "Scoopy Karbu", "start": 2010, "end": 2013, "msrp": 13500000, "aliases": "scoopy karbu, scoopy lama"},
                    {"name": "Scoopy FI (Velg 14)", "start": 2013, "end": 2017, "msrp": 16500000, "aliases": "scoopy fi lama, scoopy esp ring 14"},
                    {"name": "Scoopy Donat (Ring 12)", "start": 2017, "end": 2020, "msrp": 19500000, "aliases": "scoopy donat, scoopy stylish 2017 2018 2019"},
                    {"name": "Scoopy All New (Keyless / Prestige)", "start": 2020, "end": 2024, "msrp": 22500000, "aliases": "scoopy prestige, scoopy stylish keyless, scoopy 2021 2022 2023"},
                    {"name": "Scoopy Facelift LED (2024+)", "start": 2024, "end": 2026, "msrp": 23200000, "aliases": "scoopy 2024, new scoopy, all new scoopy 2025"}
                ]
            },
            {
                "name": "Genio & Spacy",
                "category": "Matic",
                "cc": 110,
                "variants": [
                    {"name": "Spacy Helm-In (Karbu / PGM-FI)", "start": 2011, "end": 2018, "msrp": 14500000, "aliases": "honda spacy, spacy fi, spacy helm in"},
                    {"name": "Genio CBS / ISS (eSAF Ring 14)", "start": 2019, "end": 2022, "msrp": 17800000, "aliases": "honda genio, genio cbs, genio iss"},
                    {"name": "Genio Facelift (Ring 12)", "start": 2022, "end": 2026, "msrp": 19200000, "aliases": "genio donat, genio new, genio ring 12"}
                ]
            },
            {
                "name": "PCX",
                "category": "Maxi Matic",
                "cc": 160,
                "variants": [
                    {"name": "PCX 125 CBU Thailand", "start": 2010, "end": 2012, "msrp": 32000000, "aliases": "pcx 125, pcx cbu 125"},
                    {"name": "PCX 150 CBU", "start": 2012, "end": 2017, "msrp": 38000000, "aliases": "pcx cbu, pcx thailand, pcx vietnam"},
                    {"name": "PCX 150 Lokal (CBS / ABS)", "start": 2018, "end": 2021, "msrp": 29800000, "aliases": "pcx 150 lokal, pcx 150 cbs, pcx 150 abs 2018 2019 2020"},
                    {"name": "PCX Hybrid 150", "start": 2018, "end": 2021, "msrp": 42000000, "aliases": "pcx hybrid, pcx hev"},
                    {"name": "PCX 160 CBS", "start": 2021, "end": 2026, "msrp": 32600000, "aliases": "pcx 160, pcx 160 cbs, all new pcx"},
                    {"name": "PCX 160 ABS", "start": 2021, "end": 2026, "msrp": 36000000, "aliases": "pcx 160 abs, all new pcx abs"}
                ]
            },
            {
                "name": "ADV",
                "category": "Adventure Matic",
                "cc": 160,
                "variants": [
                    {"name": "ADV 150 (CBS / ABS)", "start": 2019, "end": 2022, "msrp": 34500000, "aliases": "adv 150, adv 150 abs, adv 150 cbs"},
                    {"name": "ADV 160 (CBS / ABS)", "start": 2022, "end": 2026, "msrp": 36500000, "aliases": "adv 160, adv 160 abs, adv 160 cbs"}
                ]
            },
            {
                "name": "Forza",
                "category": "Maxi Matic",
                "cc": 250,
                "variants": [
                    {"name": "Forza 250 (Windshield Elektrik)", "start": 2018, "end": 2026, "msrp": 90500000, "aliases": "honda forza, forza 250, forza cbu"}
                ]
            },
            {
                "name": "CBR 150R",
                "category": "Sport Fairing",
                "cc": 150,
                "variants": [
                    {"name": "CBR 150R CBU Thailand", "start": 2011, "end": 2014, "msrp": 33000000, "aliases": "cbr cbu, cbr fi thailand"},
                    {"name": "CBR 150R K45A Lokal Dual Eyes", "start": 2014, "end": 2016, "msrp": 29800000, "aliases": "cbr k45a, cbr lokal mata ganda"},
                    {"name": "CBR 150R K45G (Facelift LED)", "start": 2016, "end": 2020, "msrp": 34000000, "aliases": "cbr 150r facelift, cbr k45g, cbr led lama"},
                    {"name": "CBR 150R K45R (All New Inverted Fork)", "start": 2021, "end": 2026, "msrp": 37500000, "aliases": "all new cbr 150r, cbr k45r, cbr usd, cbr abs"}
                ]
            },
            {
                "name": "CBR 250RR & 250R",
                "category": "Sport Fairing",
                "cc": 250,
                "variants": [
                    {"name": "CBR 250R 1-Silinder CBU", "start": 2011, "end": 2015, "msrp": 48000000, "aliases": "cbr 250 1 silinder, cbr 250 cbu, cbr 250 non abs"},
                    {"name": "CBR 250RR 2-Silinder (Standard / ABS)", "start": 2016, "end": 2020, "msrp": 65000000, "aliases": "cbr 250rr, cbr 250 2 silinder, cbr250rr abs"},
                    {"name": "CBR 250RR SP Quick Shifter", "start": 2020, "end": 2026, "msrp": 78000000, "aliases": "cbr250rr sp, cbr 250rr quick shifter, cbr250rr qs"}
                ]
            },
            {
                "name": "CB150R & CB150X",
                "category": "Sport Naked & Adventure",
                "cc": 150,
                "variants": [
                    {"name": "CB150R StreetFire Gen 1", "start": 2012, "end": 2015, "msrp": 23500000, "aliases": "cb150r old, cb streetfire lama"},
                    {"name": "CB150R StreetFire LED Gen 2", "start": 2015, "end": 2021, "msrp": 28000000, "aliases": "cb150r led, cb150r se, cb streetfire"},
                    {"name": "CB150R StreetFire All New (USD)", "start": 2021, "end": 2026, "msrp": 31500000, "aliases": "all new cb150r, cb150r usd"},
                    {"name": "CB150X Adventure Touring", "start": 2021, "end": 2026, "msrp": 33900000, "aliases": "cb150x, cb 150x, cb150 x adventure"}
                ]
            },
            {
                "name": "Verza & MegaPro",
                "category": "Sport Commuter",
                "cc": 150,
                "variants": [
                    {"name": "MegaPro FI (Monoshock)", "start": 2014, "end": 2018, "msrp": 21500000, "aliases": "megapro fi, mega pro injeksi, megapro monoshock"},
                    {"name": "Honda Verza 150 (Gen 1)", "start": 2013, "end": 2018, "msrp": 18500000, "aliases": "verza 150, honda verza, verza sw, verza cw"},
                    {"name": "CB150 Verza (Gen 2)", "start": 2018, "end": 2026, "msrp": 21900000, "aliases": "cb150 verza, cb verza, all new verza"}
                ]
            },
            {
                "name": "Sonic 150R",
                "category": "Underbone Ayago",
                "cc": 150,
                "variants": [
                    {"name": "Sonic 150R DOHC 6-Speed", "start": 2015, "end": 2026, "msrp": 25500000, "aliases": "honda sonic, sonic 150, sonic 150r, sonic dohc"}
                ]
            },
            {
                "name": "CRF 150L & CRF 250",
                "category": "Trail / Dual Purpose",
                "cc": 150,
                "variants": [
                    {"name": "CRF 150L Injeksi", "start": 2017, "end": 2026, "msrp": 36400000, "aliases": "crf 150, crf 150l, crf150l, honda crf"},
                    {"name": "CRF 250 Rally", "start": 2017, "end": 2026, "msrp": 92900000, "aliases": "crf 250 rally, crf250 rally, crf rally 250"}
                ]
            },
            {
                "name": "Supra Series & Revo",
                "category": "Bebek / Moped",
                "cc": 125,
                "variants": [
                    {"name": "Revo 110 FI (Fit / X)", "start": 2014, "end": 2026, "msrp": 16500000, "aliases": "revo fi, revo x, revo fit, honda revo"},
                    {"name": "Supra X 125 FI (CW / SW)", "start": 2014, "end": 2026, "msrp": 19100000, "aliases": "supra x 125, supra x 125 fi, supra batman"},
                    {"name": "Supra GTR 150", "start": 2016, "end": 2026, "msrp": 25500000, "aliases": "supra gtr, supra gtr 150, gtr 150"}
                ]
            }
        ]
    },
    {
        "brand": "Yamaha",
        "country": "Jepang",
        "models": [
            {
                "name": "NMAX",
                "category": "Maxi Matic",
                "cc": 155,
                "variants": [
                    {"name": "NMAX 155 Old (Generasi 1 Non-ABS / ABS)", "start": 2015, "end": 2019, "msrp": 26500000, "aliases": "nmax lama, nmax old, nmax 2016 2017 2018 2019, nmax non abs"},
                    {"name": "NMAX 155 All New (Standard / Connected)", "start": 2020, "end": 2024, "msrp": 31500000, "aliases": "nmax new, nmax all new, nmax connected, nmax abs 2020 2021 2022 2023"},
                    {"name": "NMAX Neo 155 (2024+)", "start": 2024, "end": 2026, "msrp": 32700000, "aliases": "nmax neo, nmax neo s, all new nmax neo"},
                    {"name": "NMAX Turbo / Turbo Tech Max (2024+)", "start": 2024, "end": 2026, "msrp": 37750000, "aliases": "nmax turbo, nmax turbo tech max, nmax turbo yecvt"}
                ]
            },
            {
                "name": "Aerox",
                "category": "Maxi Sport Matic",
                "cc": 155,
                "variants": [
                    {"name": "Aerox 125 LC", "start": 2016, "end": 2017, "msrp": 18200000, "aliases": "aerox 125, aerox 125 lc"},
                    {"name": "Aerox 155 VVA Old (Standard / R / S-Version)", "start": 2017, "end": 2020, "msrp": 24500000, "aliases": "aerox old, aerox lama, aerox 155 2017 2018 2019, aerox tipe r, aerox keyless"},
                    {"name": "Aerox 155 Connected / CyberCity / ABS", "start": 2020, "end": 2026, "msrp": 28500000, "aliases": "all new aerox, aerox connected, aerox cybercity, aerox abs 2021 2022 2023"}
                ]
            },
            {
                "name": "XMAX & TMAX",
                "category": "Maxi Matic",
                "cc": 250,
                "variants": [
                    {"name": "XMAX 250 Old", "start": 2017, "end": 2022, "msrp": 62500000, "aliases": "xmax 250, xmax lama, xmax 2018 2019 2020"},
                    {"name": "XMAX 250 Connected / Tech MAX", "start": 2022, "end": 2026, "msrp": 66500000, "aliases": "xmax connected, xmax new, xmax tech max"},
                    {"name": "TMAX 530 DX CBU", "start": 2014, "end": 2020, "msrp": 319000000, "aliases": "tmax 530, yamaha tmax, tmax dx"}
                ]
            },
            {
                "name": "Lexi",
                "category": "Maxi Matic",
                "cc": 125,
                "variants": [
                    {"name": "Lexi 125 VVA (Standard / S / ABS)", "start": 2018, "end": 2023, "msrp": 22500000, "aliases": "yamaha lexi, lexi 125, lexi s, lexi abs"},
                    {"name": "Lexi LX 155 Connected", "start": 2024, "end": 2026, "msrp": 29900000, "aliases": "lexi lx 155, lexi 155, all new lexi"}
                ]
            },
            {
                "name": "Classy (Fazzio & Filano)",
                "category": "Classy Hybrid Matic",
                "cc": 125,
                "variants": [
                    {"name": "Fazzio Hybrid-Connected (Neo / Lux)", "start": 2022, "end": 2026, "msrp": 22800000, "aliases": "fazzio, fazio, fazzio hybrid, fazzio lux, fazzio neo"},
                    {"name": "Grand Filano Hybrid-Connected (Neo / Lux)", "start": 2023, "end": 2026, "msrp": 27500000, "aliases": "grand filano, filano hybrid, filano lux"}
                ]
            },
            {
                "name": "X-Ride & Fino",
                "category": "Matic Lifestyle",
                "cc": 125,
                "variants": [
                    {"name": "X-Ride 115 YMJET-FI", "start": 2013, "end": 2017, "msrp": 15300000, "aliases": "xride 115, x-ride lama, xride karbu fi"},
                    {"name": "X-Ride 125 Blue Core", "start": 2017, "end": 2026, "msrp": 20200000, "aliases": "xride 125, x-ride 125, all new xride"},
                    {"name": "Fino 125 Blue Core (Premium / Grande)", "start": 2016, "end": 2024, "msrp": 20150000, "aliases": "yamaha fino, fino 125, fino grande, fino sporty"}
                ]
            },
            {
                "name": "Gear, FreeGo & Soul GT",
                "category": "Matic Harian",
                "cc": 125,
                "variants": [
                    {"name": "Soul GT 125 Blue Core (LED)", "start": 2015, "end": 2022, "msrp": 17800000, "aliases": "soul gt 125, all new soul gt, soul gt led"},
                    {"name": "Gear 125 (Standard / S-Version)", "start": 2020, "end": 2026, "msrp": 18200000, "aliases": "gear 125, yamaha gear, gear 125 s"},
                    {"name": "FreeGo 125 (Old / Connected)", "start": 2018, "end": 2026, "msrp": 21400000, "aliases": "freego, freego 125, freego connected"}
                ]
            },
            {
                "name": "Mio",
                "category": "Matic",
                "cc": 125,
                "variants": [
                    {"name": "Mio Sporty / Smile Karbu", "start": 2004, "end": 2012, "msrp": 12000000, "aliases": "mio sporty, mio smile, mio karbu, mio 5tl"},
                    {"name": "Mio J / Mio GT", "start": 2012, "end": 2015, "msrp": 13500000, "aliases": "mio j, mio gt, mio ymjet fi"},
                    {"name": "Mio M3 125 Blue Core", "start": 2015, "end": 2024, "msrp": 17500000, "aliases": "mio m3, mio 125, mio m3 aks, mio z, mio s"}
                ]
            },
            {
                "name": "XSR 155",
                "category": "Sport Heritage",
                "cc": 155,
                "variants": [
                    {"name": "XSR 155 Heritage Sport", "start": 2019, "end": 2026, "msrp": 38000000, "aliases": "xsr 155, yamaha xsr, xsr retro"}
                ]
            },
            {
                "name": "YZF-R15",
                "category": "Sport Fairing",
                "cc": 155,
                "variants": [
                    {"name": "R15 V2", "start": 2014, "end": 2017, "msrp": 29500000, "aliases": "r15 v2, r15 lama"},
                    {"name": "R15 V3 VVA", "start": 2017, "end": 2021, "msrp": 36000000, "aliases": "r15 v3, all new r15, r15 vva"},
                    {"name": "R15 V4 / R15M Connected ABS", "start": 2021, "end": 2026, "msrp": 44500000, "aliases": "r15 v4, r15m, r15 connected"}
                ]
            },
            {
                "name": "YZF-R25 & MT-25",
                "category": "Sport 2-Cylinder",
                "cc": 250,
                "variants": [
                    {"name": "YZF-R25 2-Silinder (Old / Facelift)", "start": 2014, "end": 2026, "msrp": 63500000, "aliases": "r25, yamaha r25, r25 v2, r25 abs"},
                    {"name": "MT-25 Naked 2-Silinder", "start": 2015, "end": 2026, "msrp": 57500000, "aliases": "mt25, mt-25, yamaha mt25"}
                ]
            },
            {
                "name": "Vixion, Byson & MT-15",
                "category": "Sport Naked",
                "cc": 155,
                "variants": [
                    {"name": "Byson FI 150", "start": 2015, "end": 2020, "msrp": 22950000, "aliases": "byson fi, yamaha byson, byson injeksi"},
                    {"name": "Vixion New Lightning / Advance (NVL / NVA)", "start": 2012, "end": 2017, "msrp": 24500000, "aliases": "nvl, nva, vixion lightning, vixion advance"},
                    {"name": "All New Vixion / Vixion R 155 VVA", "start": 2017, "end": 2024, "msrp": 29500000, "aliases": "vixion r, all new vixion, vixion 155"},
                    {"name": "MT-15 Inverted Fork", "start": 2019, "end": 2026, "msrp": 38500000, "aliases": "mt15, mt-15, yamaha mt15"}
                ]
            },
            {
                "name": "WR 155R",
                "category": "Trail / Dual Purpose",
                "cc": 155,
                "variants": [
                    {"name": "WR 155R VVA", "start": 2019, "end": 2026, "msrp": 38600000, "aliases": "wr 155, wr155, wr155r, yamaha wr"}
                ]
            },
            {
                "name": "MX King & Jupiter",
                "category": "Bebek Sport",
                "cc": 150,
                "variants": [
                    {"name": "Jupiter MX 135 (5-Speed)", "start": 2011, "end": 2015, "msrp": 17500000, "aliases": "njmx, jupiter mx 135, mx 135 new"},
                    {"name": "MX King 150 VVA", "start": 2015, "end": 2026, "msrp": 25800000, "aliases": "mx king, mx king 150, jupiter mx king"},
                    {"name": "Jupiter Z1 FI", "start": 2012, "end": 2026, "msrp": 19700000, "aliases": "jupiter z1, jupiter robot fi"}
                ]
            }
        ]
    },
    {
        "brand": "Kawasaki",
        "country": "Jepang",
        "models": [
            {
                "name": "Ninja 250",
                "category": "Sport Fairing",
                "cc": 250,
                "variants": [
                    {"name": "Ninja 250 Karbu", "start": 2008, "end": 2012, "msrp": 45000000, "aliases": "ninja 250 karbu, ninja lama 2 silinder"},
                    {"name": "Ninja 250 FI (Generasi 1)", "start": 2013, "end": 2017, "msrp": 58000000, "aliases": "ninja 250 fi, ninja fi 2013 2014 2015"},
                    {"name": "Ninja 250 SL / Mono (1-Silinder)", "start": 2014, "end": 2021, "msrp": 39900000, "aliases": "ninja mono, ninja 250 mono, ninja sl, ninja 250 sl"},
                    {"name": "All New Ninja 250 (Keyless / Smart Key)", "start": 2018, "end": 2025, "msrp": 67000000, "aliases": "all new ninja 250, ninja 250 keyless, ninja 250 abs se"}
                ]
            },
            {
                "name": "Ninja ZX Series",
                "category": "Sport 4-Cylinder",
                "cc": 250,
                "variants": [
                    {"name": "Ninja ZX-25R Standard", "start": 2020, "end": 2026, "msrp": 107000000, "aliases": "zx25r standard, zx 25r non abs"},
                    {"name": "Ninja ZX-25R SE / ABS (Quickshifter)", "start": 2020, "end": 2026, "msrp": 125000000, "aliases": "zx25r abs se, zx25r se, zx25r quick shifter"},
                    {"name": "Ninja ZX-25RR", "start": 2023, "end": 2026, "msrp": 132000000, "aliases": "zx25rr, zx 25rr, ninja zx25rr"},
                    {"name": "Ninja ZX-4RR (400cc)", "start": 2023, "end": 2026, "msrp": 244800000, "aliases": "zx4rr, zx 4rr, ninja zx4rr"}
                ]
            },
            {
                "name": "Ninja 150 (2-Tak Legend)",
                "category": "Sport 2-Stroke",
                "cc": 150,
                "variants": [
                    {"name": "Ninja 150 RR (Super KIPS)", "start": 2012, "end": 2015, "msrp": 37500000, "aliases": "ninja 150 rr, ninja rr new, ninja 2 tak, ninja kips"},
                    {"name": "Ninja 150 R / SS", "start": 2012, "end": 2015, "msrp": 30500000, "aliases": "ninja r, ninja ss, ninja 150 r, ninja barong 2 tak"}
                ]
            },
            {
                "name": "KLX 150",
                "category": "Trail",
                "cc": 150,
                "variants": [
                    {"name": "KLX 150S / 150L", "start": 2009, "end": 2015, "msrp": 25000000, "aliases": "klx 150s, klx 150l, klx lama"},
                    {"name": "KLX 150 BF / SE / Extreme", "start": 2015, "end": 2023, "msrp": 36000000, "aliases": "klx bf, klx 150 bf se, klx usd, klx extreme"},
                    {"name": "KLX 150 Facelift (LED / SE)", "start": 2023, "end": 2026, "msrp": 39500000, "aliases": "klx 150 baru, all new klx 150 led"}
                ]
            },
            {
                "name": "KLX 230 & KLX 250",
                "category": "Trail Dual Purpose",
                "cc": 230,
                "variants": [
                    {"name": "KLX 230 / SE / S", "start": 2019, "end": 2026, "msrp": 49900000, "aliases": "klx 230, klx230, klx 230 se"},
                    {"name": "KLX 250", "start": 2008, "end": 2024, "msrp": 71000000, "aliases": "klx 250, klx250"}
                ]
            },
            {
                "name": "Supermoto (D-Tracker & KLX SM)",
                "category": "Supermoto",
                "cc": 150,
                "variants": [
                    {"name": "D-Tracker 150 SE (Velg 17)", "start": 2015, "end": 2023, "msrp": 35500000, "aliases": "dtracker, d-tracker, dtracker 150, dtracker se"},
                    {"name": "KLX 150 SM / SM SE", "start": 2023, "end": 2026, "msrp": 39900000, "aliases": "klx 150 sm, klx sm, klx supermoto"},
                    {"name": "KLX 230 SM / SM SE", "start": 2022, "end": 2026, "msrp": 54900000, "aliases": "klx 230 sm, klx230sm, klx 230 supermoto"}
                ]
            },
            {
                "name": "W175",
                "category": "Classic / Retro",
                "cc": 177,
                "variants": [
                    {"name": "W175 Standard / SE", "start": 2018, "end": 2026, "msrp": 34500000, "aliases": "kawasaki w175, w175 se, w 175"},
                    {"name": "W175 Cafe", "start": 2019, "end": 2026, "msrp": 35900000, "aliases": "w175 cafe, w175 cafe racer"},
                    {"name": "W175 TR Scrambler", "start": 2020, "end": 2026, "msrp": 33900000, "aliases": "w175 tr, w175 scrambler"},
                    {"name": "W175 Black Style (Injeksi)", "start": 2024, "end": 2026, "msrp": 35100000, "aliases": "w175 injeksi, w175 black style, w175 fi"}
                ]
            },
            {
                "name": "Z Series & Versys",
                "category": "Naked & Touring",
                "cc": 250,
                "variants": [
                    {"name": "Z125 Pro", "start": 2016, "end": 2024, "msrp": 47800000, "aliases": "z125, z 125 pro, kawasaki z125"},
                    {"name": "Z250 2-Silinder", "start": 2013, "end": 2019, "msrp": 53900000, "aliases": "kawasaki z250, z250 naked, z 250"},
                    {"name": "Versys-X 250 Tourer / City", "start": 2017, "end": 2026, "msrp": 71200000, "aliases": "versys 250, versys x 250, versys tourer"}
                ]
            }
        ]
    },
    {
        "brand": "Piaggio",
        "country": "Italia",
        "models": [
            {
                "name": "Medley",
                "category": "Matic",
                "cc": 150,
                "variants": [
                    {"name": "Medley 150 ABS (Generasi 1)", "start": 2016, "end": 2020, "msrp": 45000000, "aliases": "piaggio medley, pagio medley, medley 150, medley abs"},
                    {"name": "Medley 150 S i-Get (Facelift LED)", "start": 2020, "end": 2026, "msrp": 54500000, "aliases": "medley s 150, piaggio medley s, pagio medley s, medley iget"}
                ]
            },
            {
                "name": "Liberty",
                "category": "Matic",
                "cc": 150,
                "variants": [
                    {"name": "Liberty 100 Karbu", "start": 2011, "end": 2014, "msrp": 16000000, "aliases": "liberty 100, pagio liberty 100, piaggio liberty 100"},
                    {"name": "Liberty 150 3V ie", "start": 2013, "end": 2016, "msrp": 29000000, "aliases": "liberty 150, pagio liberty 150, piaggio liberty 3v"},
                    {"name": "Liberty 150 i-Get ABS / S", "start": 2016, "end": 2024, "msrp": 38000000, "aliases": "liberty iget, liberty s 150, pagio liberty abs"}
                ]
            },
            {
                "name": "Zip",
                "category": "Matic",
                "cc": 100,
                "variants": [
                    {"name": "Zip 100 Karbu", "start": 2010, "end": 2014, "msrp": 14000000, "aliases": "piaggio zip, pagio zip, zip 100, piaggio zip 100"}
                ]
            },
            {
                "name": "MP3",
                "category": "Maxi Matic (3-Roda)",
                "cc": 300,
                "variants": [
                    {"name": "MP3 300 / 500 HPE Tiga Roda", "start": 2018, "end": 2026, "msrp": 330000000, "aliases": "piaggio mp3, pagio mp3, mp3 hpe, piaggio roda 3"},
                    {"name": "MP3 530 Exclusive (Radar / Reverse Camera)", "start": 2023, "end": 2026, "msrp": 400000000, "aliases": "mp3 530, piaggio mp3 530"}
                ]
            },
            {
                "name": "Beverly",
                "category": "Maxi Matic",
                "cc": 300,
                "variants": [
                    {"name": "Beverly 300 / 400 HPE", "start": 2019, "end": 2026, "msrp": 180000000, "aliases": "piaggio beverly, pagio beverly, beverly 300"}
                ]
            }
        ]
    },
    {
        "brand": "Vespa (Piaggio)",
        "country": "Italia",
        "models": [
            {
                "name": "Sprint",
                "category": "Matic",
                "cc": 150,
                "variants": [
                    {"name": "Sprint 150 3V ie", "start": 2014, "end": 2016, "msrp": 35000000, "aliases": "sprint 3v, sprint 150 3v, vespa sprint lama, pagio sprint"},
                    {"name": "Sprint 150 i-Get (ABS)", "start": 2016, "end": 2023, "msrp": 53000000, "aliases": "sprint iget, sprint 150 iget abs, sprint s 150, pagio sprint iget"},
                    {"name": "Sprint 150 TFT / LED Facelift", "start": 2023, "end": 2026, "msrp": 57000000, "aliases": "sprint tft, new sprint 150 2024, sprint s tft"},
                    {"name": "Sprint Limited (Carbon / Racing Sixties / Justin Bieber)", "start": 2018, "end": 2024, "msrp": 65000000, "aliases": "sprint carbon, sprint racing sixties, sprint justin bieber"}
                ]
            },
            {
                "name": "Primavera",
                "category": "Matic",
                "cc": 150,
                "variants": [
                    {"name": "Primavera 150 3V ie", "start": 2014, "end": 2016, "msrp": 33000000, "aliases": "primavera 3v, vespa primavera lama, pagio primavera"},
                    {"name": "Primavera 150 i-Get (ABS / S)", "start": 2016, "end": 2026, "msrp": 50000000, "aliases": "primavera iget, primavera 150 abs, primavera s, pagio primavera iget"},
                    {"name": "Primavera Color Vibe / Special Edition", "start": 2022, "end": 2026, "msrp": 60000000, "aliases": "primavera color vibe, primavera sean wotherspoon, primavera 75th, primavera mickey mouse"}
                ]
            },
            {
                "name": "LX",
                "category": "Matic",
                "cc": 125,
                "variants": [
                    {"name": "LX 150 2V / 3V ie", "start": 2011, "end": 2015, "msrp": 26000000, "aliases": "vespa lx 150, lx 2v, lx 3v, pagio lx 150"},
                    {"name": "LX 125 i-Get / Batik Edition", "start": 2017, "end": 2026, "msrp": 45000000, "aliases": "vespa lx 125, lx 125 iget, lx iget, lx batik, pagio lx 125"}
                ]
            },
            {
                "name": "S",
                "category": "Matic",
                "cc": 125,
                "variants": [
                    {"name": "S 150 2V / 3V ie", "start": 2011, "end": 2015, "msrp": 28000000, "aliases": "vespa s 150, vespa s 3v, pagio s 150"},
                    {"name": "S 125 i-Get Sport", "start": 2016, "end": 2026, "msrp": 45500000, "aliases": "vespa s 125, s 125 iget, vespa s iget, pagio s 125, s 125 sport"}
                ]
            },
            {
                "name": "GTS & GTV",
                "category": "Maxi Matic",
                "cc": 150,
                "variants": [
                    {"name": "GTS Super 150 3V / i-Get", "start": 2014, "end": 2022, "msrp": 67000000, "aliases": "vespa gts 150, gts super 150, gts iget, pagio gts"},
                    {"name": "GTS Classic / Super Sport 150 (Keyless)", "start": 2023, "end": 2026, "msrp": 78800000, "aliases": "gts 150 keyless, gts classic, gts super sport 150"},
                    {"name": "GTS 300 Super Tech HPE", "start": 2019, "end": 2026, "msrp": 165000000, "aliases": "vespa gts 300, gts super tech, gts 300 hpe, pagio gts 300"},
                    {"name": "GTV 300 Sei Giorni / Keyless", "start": 2020, "end": 2026, "msrp": 176000000, "aliases": "vespa gtv, gtv 300, gtv sei giorni"}
                ]
            }
        ]
    },
    {
        "brand": "Suzuki",
        "country": "Jepang",
        "models": [
            {
                "name": "Satria F150",
                "category": "Bebek Sport",
                "cc": 150,
                "variants": [
                    {"name": "Satria F150 Karbu (Barong / Facelift)", "start": 2007, "end": 2015, "msrp": 19500000, "aliases": "satria fu, satria fu karbu, fu barong, satria f150 ckd"},
                    {"name": "Satria F150 FI All New Injeksi", "start": 2016, "end": 2026, "msrp": 29000000, "aliases": "satria fu fi, satria f150 injeksi, satria fi, satria fu injeksi"}
                ]
            },
            {
                "name": "GSX 150 Series",
                "category": "Sport",
                "cc": 150,
                "variants": [
                    {"name": "GSX-R150 (Keyless / ABS)", "start": 2017, "end": 2026, "msrp": 35000000, "aliases": "gsx r150, suzuki gsx r, gsx fairing, gsx keyless"},
                    {"name": "GSX-S150 Naked", "start": 2017, "end": 2024, "msrp": 31000000, "aliases": "gsx s150, gsx naked, suzuki gsx s"},
                    {"name": "GSX 150 Bandit", "start": 2018, "end": 2023, "msrp": 28500000, "aliases": "gsx bandit, suzuki bandit, bandit 150"}
                ]
            },
            {
                "name": "Burgman & Avenis",
                "category": "Matic",
                "cc": 125,
                "variants": [
                    {"name": "Burgman 200 CBU", "start": 2014, "end": 2019, "msrp": 59900000, "aliases": "burgman 200, suzuki burgman 200"},
                    {"name": "Burgman Street 125EX", "start": 2023, "end": 2026, "msrp": 26000000, "aliases": "burgman 125, burgman street, burgman ex"},
                    {"name": "Avenis 125", "start": 2022, "end": 2026, "msrp": 30100000, "aliases": "suzuki avenis, avenis 125"}
                ]
            },
            {
                "name": "Nex & Address",
                "category": "Matic Harian",
                "cc": 113,
                "variants": [
                    {"name": "Address FI / Playful", "start": 2014, "end": 2024, "msrp": 18900000, "aliases": "suzuki address, address fi, address playful"},
                    {"name": "Nex II (Standard / Cross / Elegant)", "start": 2018, "end": 2026, "msrp": 19400000, "aliases": "suzuki nex, nex 2, nex ii, nex cross, nex crossover"}
                ]
            },
            {
                "name": "V-Strom & Inazuma",
                "category": "Adventure Touring",
                "cc": 250,
                "variants": [
                    {"name": "Inazuma 250 GW250 (2-Silinder)", "start": 2012, "end": 2016, "msrp": 49500000, "aliases": "inazuma 250, suzuki inazuma, gw250"},
                    {"name": "V-Strom 250SX Adventure", "start": 2023, "end": 2026, "msrp": 59500000, "aliases": "vstrom, v-strom, vstrom 250, suzuki vstrom"}
                ]
            }
        ]
    },
    # =========================================================================
    # SEKTOR SEPEDA MOTOR LISTRIK (ELECTRIC VEHICLES / EV)
    # =========================================================================
    {
        "brand": "Polytron",
        "country": "Indonesia",
        "models": [
            {
                "name": "Fox-R",
                "category": "Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Fox-R (Sewa Baterai / Subsidi)", "start": 2023, "end": 2026, "msrp": 13500000, "aliases": "polytron fox r, fox r, polytron ev, polytron fox-r"},
                    {"name": "Fox-R (Beli Putus / Non-Subsidi)", "start": 2023, "end": 2026, "msrp": 20500000, "aliases": "polytron fox r buyout, fox r non subsidi"}
                ]
            },
            {
                "name": "Fox-S",
                "category": "Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Fox-S (Sewa Baterai / Subsidi)", "start": 2024, "end": 2026, "msrp": 11500000, "aliases": "polytron fox s, fox s, polytron fox-s"},
                    {"name": "Fox-S (Beli Putus / Non-Subsidi)", "start": 2024, "end": 2026, "msrp": 18500000, "aliases": "polytron fox s non subsidi, fox s buyout"}
                ]
            },
            {
                "name": "T-Rex",
                "category": "Maxi Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "T-Rex 5000W (Top Tier Maxi EV)", "start": 2024, "end": 2026, "msrp": 38000000, "aliases": "polytron t-rex, polytron trex, t-rex ev"}
                ]
            }
        ]
    },
    {
        "brand": "Alva",
        "country": "Indonesia",
        "models": [
            {
                "name": "Alva One",
                "category": "Maxi Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Alva One Standard", "start": 2022, "end": 2025, "msrp": 36490000, "aliases": "alva one, motor listrik alva, alva auto"},
                    {"name": "Alva One XP (Dynamic TFT)", "start": 2024, "end": 2026, "msrp": 38500000, "aliases": "alva one xp, alva xp, all new alva one"}
                ]
            },
            {
                "name": "Alva Cervo",
                "category": "Sporty Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Alva Cervo (Dual Battery Boost)", "start": 2023, "end": 2026, "msrp": 42750000, "aliases": "alva cervo, cervo, alva servo, motor cervo"},
                    {"name": "Alva Cervo Q (Fast Charging)", "start": 2024, "end": 2026, "msrp": 49500000, "aliases": "alva cervo q, cervo q fast charge"}
                ]
            },
            {
                "name": "Alva N3",
                "category": "Urban Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Alva N3 Urban Commuter", "start": 2024, "end": 2026, "msrp": 18500000, "aliases": "alva n3, alva n 3, alva motor baru"}
                ]
            }
        ]
    },
    {
        "brand": "Gesits",
        "country": "Indonesia",
        "models": [
            {
                "name": "Gesits G1",
                "category": "Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Gesits G1 (Dual Slot 72V 20Ah)", "start": 2019, "end": 2024, "msrp": 28970000, "aliases": "gesits, gesits g1, motor listrik gesits, gesits bumn"}
                ]
            },
            {
                "name": "Gesits Raya",
                "category": "Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Gesits Raya G (Stang Naked)", "start": 2023, "end": 2026, "msrp": 27990000, "aliases": "gesits raya g, gesits raya, raya g"},
                    {"name": "Gesits Raya E (Entry Level)", "start": 2023, "end": 2026, "msrp": 24990000, "aliases": "gesits raya e, raya e"}
                ]
            }
        ]
    },
    {
        "brand": "Yadea",
        "country": "China",
        "models": [
            {
                "name": "Yadea T9",
                "category": "Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Yadea T9 TTFAR 2000W", "start": 2023, "end": 2026, "msrp": 21500000, "aliases": "yadea t9, t9 indomobil, yadea ev"}
                ]
            },
            {
                "name": "Yadea E8S Pro",
                "category": "Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Yadea E8S Pro (Graphene Battery)", "start": 2023, "end": 2026, "msrp": 23900000, "aliases": "yadea e8s pro, e8s pro, yadea e8s"}
                ]
            },
            {
                "name": "Yadea G6",
                "category": "Maxi Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Yadea G6 Red Dot Award Winner", "start": 2023, "end": 2026, "msrp": 29350000, "aliases": "yadea g6, g6 ev, yadea flagship"}
                ]
            }
        ]
    },
    {
        "brand": "Viar",
        "country": "Indonesia",
        "models": [
            {
                "name": "Viar Q1",
                "category": "Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Viar Q1 (Generasi 1)", "start": 2017, "end": 2020, "msrp": 17500000, "aliases": "viar q1 lama, q1 gen 1, viar listrik"},
                    {"name": "Viar Q1 (Generasi 2 / Smart Key)", "start": 2020, "end": 2026, "msrp": 21520000, "aliases": "all new viar q1, viar q1 baru, q1 grab"}
                ]
            },
            {
                "name": "Viar N Series",
                "category": "Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Viar N1", "start": 2022, "end": 2026, "msrp": 25870000, "aliases": "viar n1, n1 ev"},
                    {"name": "Viar N2 (Dual Battery)", "start": 2022, "end": 2026, "msrp": 34000000, "aliases": "viar n2, n2 dual battery"}
                ]
            }
        ]
    },

    # =========================================================================
    # SEKTOR RETRO, CRUISER, & SPORT POPULER
    # =========================================================================
    {
        "brand": "Royal Enfield",
        "country": "Inggris / India",
        "models": [
            {
                "name": "Hunter 350",
                "category": "Modern Retro Roadster",
                "cc": 350,
                "variants": [
                    {"name": "Hunter 350 Dapper", "start": 2022, "end": 2026, "msrp": 106400000, "aliases": "re hunter 350, hunter 350, royal enfield hunter"},
                    {"name": "Hunter 350 Rebel (Dual Tone)", "start": 2022, "end": 2026, "msrp": 108200000, "aliases": "hunter 350 rebel, hunter rebel"}
                ]
            },
            {
                "name": "Classic 350",
                "category": "Vintage Classic",
                "cc": 350,
                "variants": [
                    {"name": "Classic 350 (Mesin UCE Lama)", "start": 2014, "end": 2021, "msrp": 85000000, "aliases": "classic 350 lama, re classic 350 uce, classic 350 carbu/efi"},
                    {"name": "Classic 350 Reborn (J-Series Halis)", "start": 2022, "end": 2026, "msrp": 113300000, "aliases": "all new classic 350, classic 350 reborn, classic j series, re reborn"}
                ]
            },
            {
                "name": "Meteor 350",
                "category": "Easy Cruiser",
                "cc": 350,
                "variants": [
                    {"name": "Meteor 350 Fireball", "start": 2021, "end": 2026, "msrp": 119800000, "aliases": "re meteor 350, meteor 350 fireball, meteor fireball"},
                    {"name": "Meteor 350 Stellar / Supernova", "start": 2021, "end": 2026, "msrp": 124500000, "aliases": "meteor 350 stellar, meteor 350 supernova"}
                ]
            },
            {
                "name": "Himalayan",
                "category": "Dual-Purpose Adventure",
                "cc": 411,
                "variants": [
                    {"name": "Himalayan 411 (Generasi 1)", "start": 2018, "end": 2023, "msrp": 133300000, "aliases": "re himalayan, himalayan 411, royal enfield himalayan"},
                    {"name": "Himalayan 450 (Liquid Cooled Sherpa)", "start": 2024, "end": 2026, "msrp": 155000000, "aliases": "all new himalayan 450, himalayan 450 sherpa"}
                ]
            },
            {
                "name": "Twins 650",
                "category": "Cafe Racer & Roadster",
                "cc": 650,
                "variants": [
                    {"name": "Interceptor 650", "start": 2019, "end": 2026, "msrp": 221700000, "aliases": "interceptor 650, re interceptor, royal enfield 650"},
                    {"name": "Continental GT 650 (Cafe Racer)", "start": 2019, "end": 2026, "msrp": 238500000, "aliases": "continental gt 650, continental 650, re gt 650"}
                ]
            }
        ]
    },
    {
        "brand": "Benelli & Keeway",
        "country": "Italia / China",
        "models": [
            {
                "name": "Motobi 200",
                "category": "Cruiser / Bobber",
                "cc": 200,
                "variants": [
                    {"name": "Motobi 200 EFI (Classic)", "start": 2016, "end": 2023, "msrp": 30000000, "aliases": "benelli motobi 200, motobi 200 efi, motobi klasik"},
                    {"name": "Motobi 200 Evo (Sport Bobber)", "start": 2018, "end": 2026, "msrp": 32200000, "aliases": "benelli evo 200, motobi 200 evo, motobi evo"}
                ]
            },
            {
                "name": "Patagonian Eagle 250",
                "category": "Cruiser 2-Silinder (Suara Moge)",
                "cc": 250,
                "variants": [
                    {"name": "Patagonian Eagle 250 (Karburator)", "start": 2016, "end": 2020, "msrp": 38900000, "aliases": "patagonian eagle karbu, benelli patagonian 250"},
                    {"name": "Patagonian Eagle 250 EFI (Injeksi)", "start": 2020, "end": 2026, "msrp": 44800000, "aliases": "benelli patagonian eagle efi, patagonian efi, patagonian injeksi"}
                ]
            },
            {
                "name": "Panarea 125",
                "category": "Retro Modern Matic",
                "cc": 125,
                "variants": [
                    {"name": "Panarea 125 EFI", "start": 2021, "end": 2026, "msrp": 24800000, "aliases": "benelli panarea, panarea 125, matic benelli panarea"}
                ]
            },
            {
                "name": "Keeway V250Fi / Benda",
                "category": "V-Twin Cruiser (Belt Drive)",
                "cc": 250,
                "variants": [
                    {"name": "Keeway V250Fi Geronimo", "start": 2020, "end": 2024, "msrp": 59800000, "aliases": "keeway v250fi, keeway geronimo, v250fi v-twin"},
                    {"name": "Keeway Benda V252C (Liquid Cooled V-Twin)", "start": 2023, "end": 2026, "msrp": 73800000, "aliases": "keeway benda v252c, benda 250, keeway benda"}
                ]
            },
            {
                "name": "Keeway Shiny 150",
                "category": "Retro Scooter",
                "cc": 150,
                "variants": [
                    {"name": "Keeway Shiny 150 Classic", "start": 2022, "end": 2026, "msrp": 26880000, "aliases": "keeway shiny 150, shiny 150, keeway shiny"}
                ]
            }
        ]
    },
    {
        "brand": "KTM",
        "country": "Austria",
        "models": [
            {
                "name": "Duke Series",
                "category": "Naked Sport Streetfighter",
                "cc": 250,
                "variants": [
                    {"name": "Duke 200 (Gen 1 & Facelift)", "start": 2014, "end": 2024, "msrp": 52000000, "aliases": "ktm duke 200, duke 200, ktm djuk 200"},
                    {"name": "Duke 250 (Split LED Headlamp)", "start": 2015, "end": 2026, "msrp": 65000000, "aliases": "ktm duke 250, duke 250 new, ktm 250 duke"},
                    {"name": "Duke 390 (TFT Display & Quickshifter)", "start": 2015, "end": 2026, "msrp": 99900000, "aliases": "ktm duke 390, duke 390, duke 390 tft"}
                ]
            },
            {
                "name": "RC Series",
                "category": "Supersport Fairing",
                "cc": 250,
                "variants": [
                    {"name": "RC 200", "start": 2014, "end": 2023, "msrp": 43500000, "aliases": "ktm rc 200, rc200"},
                    {"name": "RC 250 (Slipper Clutch)", "start": 2015, "end": 2026, "msrp": 67000000, "aliases": "ktm rc 250, rc250, ktm fairing 250"},
                    {"name": "RC 390", "start": 2015, "end": 2026, "msrp": 104900000, "aliases": "ktm rc 390, rc390"}
                ]
            },
            {
                "name": "Adventure Series",
                "category": "Dual-Sport Adventure",
                "cc": 250,
                "variants": [
                    {"name": "250 Adventure (Offroad ABS)", "start": 2021, "end": 2026, "msrp": 79000000, "aliases": "ktm 250 adventure, 250 adv, ktm adventure 250"},
                    {"name": "390 Adventure (Traction Control)", "start": 2020, "end": 2026, "msrp": 119000000, "aliases": "ktm 390 adventure, 390 adv, ktm adventure 390"}
                ]
            }
        ]
    },
    {
        "brand": "TVS",
        "country": "India",
        "models": [
            {
                "name": "Callisto",
                "category": "Classic Retro Matic",
                "cc": 110,
                "variants": [
                    {"name": "Callisto 110 (Bodi Plat Metal)", "start": 2018, "end": 2024, "msrp": 19300000, "aliases": "tvs callisto, callisto 110, tvs kalisto, matic tvs"},
                    {"name": "Callisto 125 (Bagasi Muat 2 Helm)", "start": 2023, "end": 2026, "msrp": 21700000, "aliases": "all new callisto 125, callisto 125, tvs callisto 125"}
                ]
            },
            {
                "name": "Ronin",
                "category": "Modern Retro Scrambler",
                "cc": 225,
                "variants": [
                    {"name": "Ronin 225 SS (Single Channel ABS)", "start": 2023, "end": 2026, "msrp": 34900000, "aliases": "tvs ronin, ronin 225, tvs ronin ss"},
                    {"name": "Ronin 225 TD (Dual Channel ABS & Connected)", "start": 2023, "end": 2026, "msrp": 38900000, "aliases": "ronin 225 td, tvs ronin dual channel"}
                ]
            },
            {
                "name": "Apache RTR",
                "category": "Naked Sport & Racing",
                "cc": 200,
                "variants": [
                    {"name": "Apache RTR 200 4V (SmartXonnect)", "start": 2016, "end": 2026, "msrp": 25100000, "aliases": "tvs apache, apache rtr 200, apache 200 4v"},
                    {"name": "Apache RR 310 (Fairing Supersport)", "start": 2018, "end": 2024, "msrp": 49000000, "aliases": "tvs apache rr 310, apache 310, rr310"}
                ]
            }
        ]
    },
    {
        "brand": "Harley-Davidson",
        "country": "Amerika Serikat",
        "models": [
            {
                "name": "Street 500",
                "category": "Cruiser Urban (Liquid Cooled)",
                "cc": 500,
                "variants": [
                    {"name": "Street 500 (XG500)", "start": 2014, "end": 2021, "msrp": 235000000, "aliases": "harley street 500, hd street 500, xg500, street 500"}
                ]
            },
            {
                "name": "Sportster",
                "category": "Classic American Cruiser",
                "cc": 883,
                "variants": [
                    {"name": "Sportster Iron 883 (Dark Custom)", "start": 2014, "end": 2022, "msrp": 399000000, "aliases": "harley iron 883, hd iron 883, sportster 883, iron 883"},
                    {"name": "Sportster Forty-Eight 1200 (Peanut Tank)", "start": 2014, "end": 2022, "msrp": 484000000, "aliases": "harley forty eight, hd forty eight, sportster 48, forty eight 1200"}
                ]
            },
            {
                "name": "Softail",
                "category": "Heavyweight Cruiser (Milwaukee-Eight)",
                "cc": 1745,
                "variants": [
                    {"name": "Softail Fat Boy 114", "start": 2018, "end": 2026, "msrp": 650000000, "aliases": "harley fat boy, fat boy 114, hd softail fat boy"},
                    {"name": "Softail Breakout 114", "start": 2018, "end": 2026, "msrp": 680000000, "aliases": "harley breakout, breakout 114, hd breakout"}
                ]
            }
        ]
    },
    {
        "brand": "BMW Motorrad",
        "country": "Jerman",
        "models": [
            {
                "name": "G 310 Series",
                "category": "Entry Adventure & Roadster",
                "cc": 313,
                "variants": [
                    {"name": "BMW G 310 R (Roadster)", "start": 2017, "end": 2026, "msrp": 125000000, "aliases": "bmw g310r, g 310 r, bmw 310 r"},
                    {"name": "BMW G 310 GS (Adventure Touring)", "start": 2018, "end": 2026, "msrp": 142000000, "aliases": "bmw g310gs, g 310 gs, bmw 310 gs, g310 gs"}
                ]
            },
            {
                "name": "C 400 Series",
                "category": "Luxury Maxi Scooter",
                "cc": 350,
                "variants": [
                    {"name": "BMW C 400 X (Urban)", "start": 2019, "end": 2026, "msrp": 259000000, "aliases": "bmw c400x, c 400 x, matic bmw"},
                    {"name": "BMW C 400 GT (Gran Turismo)", "start": 2019, "end": 2026, "msrp": 279000000, "aliases": "bmw c400gt, c 400 gt, c400 gt"}
                ]
            },
            {
                "name": "R 1250 GS",
                "category": "Flagship Adventure Touring",
                "cc": 1254,
                "variants": [
                    {"name": "BMW R 1250 GS Standard", "start": 2019, "end": 2024, "msrp": 805000000, "aliases": "bmw r1250gs, r 1250 gs, bmw r 1250, r1250 gs"},
                    {"name": "BMW R 1250 GS Adventure (GSA)", "start": 2019, "end": 2024, "msrp": 855000000, "aliases": "bmw r1250gsa, r 1250 gsa, bmw gsa 1250"}
                ]
            }
        ]
    }
]

def seed_master_motor_database():

    init_db()
    db = SessionLocal()
    try:
        total_brands = 0
        total_models = 0
        total_variants = 0

        for brand_item in MASTER_MOTOR_DATA:
            brand_obj = db.query(MasterBrand).filter(MasterBrand.name == brand_item["brand"]).first()
            if not brand_obj:
                brand_obj = MasterBrand(
                    name=brand_item["brand"],
                    country_origin=brand_item["country"]
                )
                db.add(brand_obj)
                db.flush()
                total_brands += 1

            for model_item in brand_item["models"]:
                model_obj = db.query(MasterModel).filter(
                    MasterModel.brand_id == brand_obj.id,
                    MasterModel.name == model_item["name"]
                ).first()

                if not model_obj:
                    model_obj = MasterModel(
                        brand_id=brand_obj.id,
                        name=model_item["name"],
                        category=model_item.get("category", "Matic"),
                        engine_capacity_cc=model_item.get("cc")
                    )
                    db.add(model_obj)
                    db.flush()
                    total_models += 1
                else:
                    model_obj.category = model_item.get("category", model_obj.category)
                    model_obj.engine_capacity_cc = model_item.get("cc", model_obj.engine_capacity_cc)

                for var_item in model_item["variants"]:
                    var_obj = db.query(MasterVariant).filter(
                        MasterVariant.model_id == model_obj.id,
                        MasterVariant.variant_name == var_item["name"]
                    ).first()

                    if not var_obj:
                        var_obj = MasterVariant(
                            model_id=model_obj.id,
                            variant_name=var_item["name"],
                            release_year_start=var_item["start"],
                            release_year_end=var_item.get("end"),
                            official_msrp_new=var_item.get("msrp"),
                            aliases=var_item.get("aliases")
                        )
                        db.add(var_obj)
                        total_variants += 1
                    else:
                        var_obj.release_year_start = var_item["start"]
                        var_obj.release_year_end = var_item.get("end")
                        var_obj.official_msrp_new = var_item.get("msrp")
                        var_obj.aliases = var_item.get("aliases")

        db.commit()
        print(f"✅ Seeding Sukses! Ditambahkan/Diperbarui: {total_brands} Merk, {total_models} Model, {total_variants} Varian Motor.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_master_motor_database()
