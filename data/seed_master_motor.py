"""
Master Data Seeder untuk Katalog Motor Resmi di Indonesia.
Mencakup Merk, Model, Varian Lengkap, Rentang Tahun Rilis, CC Mesin, Kategori, MSRP Baru, dan Aliases.
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
                    {"name": "Beat FI eSP (Generasi 2/3)", "start": 2014, "end": 2020, "msrp": 15500000, "aliases": "beat fi, beat esp, beat cbs iss, beat pop"},
                    {"name": "Beat Street eSP (Generasi 1)", "start": 2016, "end": 2020, "msrp": 16800000, "aliases": "beat street lama, beat strit 2017 2018 2019"},
                    {"name": "Beat Street eSAF (Generasi 2)", "start": 2020, "end": 2024, "msrp": 18700000, "aliases": "beat street new, beat street esaf"},
                    {"name": "Beat Deluxe / CBS (eSAF)", "start": 2020, "end": 2024, "msrp": 18200000, "aliases": "beat deluxe, beat esaf, beat cbs baru, all new beat"},
                    {"name": "Beat All New (Keyless 2024+)", "start": 2024, "end": 2026, "msrp": 19500000, "aliases": "beat smart key, beat 2024, beat keyless, beat deluxe smart key"},
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
                    {"name": "Vario 160 ABS", "start": 2022, "end": 2026, "msrp": 30200000, "aliases": "vario 160 abs, vario 160 cakram belakang"}
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
                "name": "Genio",
                "category": "Matic",
                "cc": 110,
                "variants": [
                    {"name": "Genio CBS / ISS (eSAF Ring 14)", "start": 2019, "end": 2022, "msrp": 17800000, "aliases": "honda genio, genio cbs, genio iss"},
                    {"name": "Genio Facelift (Ring 12)", "start": 2022, "end": 2026, "msrp": 19200000, "aliases": "genio donat, genio new, genio ring 12"}
                ]
            },
            {
                "name": "PCX",
                "category": "Matic",
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
                "category": "Matic",
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
                "name": "CBR 250RR",
                "category": "Sport Fairing 2-Cylinder",
                "cc": 250,
                "variants": [
                    {"name": "CBR 250RR 2-Silinder (Standard / ABS)", "start": 2016, "end": 2020, "msrp": 65000000, "aliases": "cbr 250rr, cbr 250 2 silinder, cbr250rr abs"},
                    {"name": "CBR 250RR SP Quick Shifter", "start": 2020, "end": 2026, "msrp": 78000000, "aliases": "cbr250rr sp, cbr 250rr quick shifter, cbr250rr qs"}
                ]
            },
            {
                "name": "CB150R",
                "category": "Sport Naked",
                "cc": 150,
                "variants": [
                    {"name": "CB150R StreetFire Gen 1", "start": 2012, "end": 2015, "msrp": 23500000, "aliases": "cb150r old, cb streetfire lama"},
                    {"name": "CB150R StreetFire LED Gen 2", "start": 2015, "end": 2021, "msrp": 28000000, "aliases": "cb150r led, cb150r se, cb streetfire"},
                    {"name": "CB150R StreetFire All New (USD)", "start": 2021, "end": 2026, "msrp": 31500000, "aliases": "all new cb150r, cb150r usd"}
                ]
            },
            {
                "name": "CB150X",
                "category": "Adventure Touring",
                "cc": 150,
                "variants": [
                    {"name": "CB150X Adventure Touring", "start": 2021, "end": 2026, "msrp": 33900000, "aliases": "cb150x, cb 150x, cb150 x adventure"}
                ]
            },
            {
                "name": "CRF 150L",
                "category": "Trail / Dual Purpose",
                "cc": 150,
                "variants": [
                    {"name": "CRF 150L Injeksi", "start": 2017, "end": 2026, "msrp": 36400000, "aliases": "crf 150, crf 150l, crf150l, honda crf"}
                ]
            },
            {
                "name": "Supra X / GTR",
                "category": "Bebek / Moped",
                "cc": 125,
                "variants": [
                    {"name": "Supra X 125 Helm-In FI", "start": 2011, "end": 2018, "msrp": 17500000, "aliases": "supra helm in, supra 125 helm in"},
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
                "category": "Matic",
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
                "category": "Matic",
                "cc": 155,
                "variants": [
                    {"name": "Aerox 155 VVA Old (Standard / R / S-Version)", "start": 2017, "end": 2020, "msrp": 24500000, "aliases": "aerox old, aerox lama, aerox 155 2017 2018 2019, aerox tipe r, aerox keyless"},
                    {"name": "Aerox 155 Connected / CyberCity / ABS", "start": 2020, "end": 2026, "msrp": 28500000, "aliases": "all new aerox, aerox connected, aerox cybercity, aerox abs 2021 2022 2023"}
                ]
            },
            {
                "name": "XMAX",
                "category": "Maxi Matic",
                "cc": 250,
                "variants": [
                    {"name": "XMAX 250 Old", "start": 2017, "end": 2022, "msrp": 62500000, "aliases": "xmax 250, xmax lama, xmax 2018 2019 2020"},
                    {"name": "XMAX 250 Connected / Tech MAX", "start": 2022, "end": 2026, "msrp": 66500000, "aliases": "xmax connected, xmax new, xmax tech max"}
                ]
            },
            {
                "name": "Lexi",
                "category": "Matic",
                "cc": 125,
                "variants": [
                    {"name": "Lexi 125 VVA (Standard / S / ABS)", "start": 2018, "end": 2023, "msrp": 22500000, "aliases": "yamaha lexi, lexi 125, lexi s, lexi abs"},
                    {"name": "Lexi LX 155 Connected", "start": 2024, "end": 2026, "msrp": 29900000, "aliases": "lexi lx 155, lexi 155, all new lexi"}
                ]
            },
            {
                "name": "Fazzio",
                "category": "Classy Matic",
                "cc": 125,
                "variants": [
                    {"name": "Fazzio Hybrid-Connected (Neo / Lux)", "start": 2022, "end": 2026, "msrp": 22800000, "aliases": "fazzio, fazio, fazzio hybrid, fazzio lux, fazzio neo"}
                ]
            },
            {
                "name": "Grand Filano",
                "category": "Classy Matic",
                "cc": 125,
                "variants": [
                    {"name": "Grand Filano Hybrid-Connected (Neo / Lux)", "start": 2023, "end": 2026, "msrp": 27500000, "aliases": "grand filano, filano hybrid, filano lux"}
                ]
            },
            {
                "name": "Gear 125 & FreeGo",
                "category": "Matic",
                "cc": 125,
                "variants": [
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
                    {"name": "Mio M3 125 Blue Core", "start": 2015, "end": 2024, "msrp": 17500000, "aliases": "mio m3, mio 125, mio m3 aks, mio z"}
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
                "name": "Vixion & MT-15",
                "category": "Sport Naked",
                "cc": 155,
                "variants": [
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
                "name": "MX King 150",
                "category": "Bebek Sport",
                "cc": 150,
                "variants": [
                    {"name": "MX King 150 VVA", "start": 2015, "end": 2026, "msrp": 25800000, "aliases": "mx king, mx king 150, jupiter mx king"}
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
                    {"name": "Ninja 250 All New (Keyless / Smart Key)", "start": 2018, "end": 2025, "msrp": 67000000, "aliases": "all new ninja 250, ninja 250 keyless, ninja 250 abs se"}
                ]
            },
            {
                "name": "Ninja ZX-25R",
                "category": "Sport 4-Cylinder",
                "cc": 250,
                "variants": [
                    {"name": "Ninja ZX-25R Standard", "start": 2020, "end": 2026, "msrp": 107000000, "aliases": "zx25r standard, zx 25r non abs"},
                    {"name": "Ninja ZX-25R SE / ABS (Quickshifter)", "start": 2020, "end": 2026, "msrp": 125000000, "aliases": "zx25r abs se, zx25r se, zx25r quick shifter"},
                    {"name": "Ninja ZX-25RR", "start": 2023, "end": 2026, "msrp": 132000000, "aliases": "zx25rr, zx 25rr, ninja zx25rr"}
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
                "name": "D-Tracker & KLX SM",
                "category": "Supermoto",
                "cc": 150,
                "variants": [
                    {"name": "D-Tracker 150 SE (Velg 17)", "start": 2015, "end": 2023, "msrp": 35500000, "aliases": "dtracker, d-tracker, dtracker 150, dtracker se"},
                    {"name": "KLX 150 SM / SM SE", "start": 2023, "end": 2026, "msrp": 39900000, "aliases": "klx 150 sm, klx sm, klx supermoto"}
                ]
            },
            {
                "name": "W175",
                "category": "Classic / Retro",
                "cc": 177,
                "variants": [
                    {"name": "W175 Standard / SE", "start": 2018, "end": 2026, "msrp": 34500000, "aliases": "kawasaki w175, w175 se, w 175"},
                    {"name": "W175 Cafe", "start": 2019, "end": 2026, "msrp": 35900000, "aliases": "w175 cafe, w175 cafe racer"},
                    {"name": "W175 TR Scrambler", "start": 2020, "end": 2026, "msrp": 33900000, "aliases": "w175 tr, w175 scrambler"}
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
                    {"name": "MP3 300 / 500 HPE Tiga Roda", "start": 2018, "end": 2026, "msrp": 330000000, "aliases": "piaggio mp3, pagio mp3, mp3 hpe, piaggio roda 3"}
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
                    {"name": "Sprint Limited Edition (Racing Sixties / Carbon)", "start": 2018, "end": 2022, "msrp": 59000000, "aliases": "sprint carbon, sprint racing sixties"}
                ]
            },
            {
                "name": "Primavera",
                "category": "Matic",
                "cc": 150,
                "variants": [
                    {"name": "Primavera 150 3V ie", "start": 2014, "end": 2016, "msrp": 33000000, "aliases": "primavera 3v, vespa primavera lama, pagio primavera"},
                    {"name": "Primavera 150 i-Get (ABS / S)", "start": 2016, "end": 2026, "msrp": 50000000, "aliases": "primavera iget, primavera 150 abs, primavera s, pagio primavera iget"},
                    {"name": "Primavera Color Vibe / Special Edition", "start": 2022, "end": 2026, "msrp": 60000000, "aliases": "primavera color vibe, primavera sean wotherspoon, primavera 75th"}
                ]
            },
            {
                "name": "LX",
                "category": "Matic",
                "cc": 125,
                "variants": [
                    {"name": "LX 150 2V / 3V ie", "start": 2011, "end": 2015, "msrp": 26000000, "aliases": "vespa lx 150, lx 2v, lx 3v, pagio lx 150"},
                    {"name": "LX 125 i-Get", "start": 2017, "end": 2026, "msrp": 45000000, "aliases": "vespa lx 125, lx 125 iget, lx iget, pagio lx 125"}
                ]
            },
            {
                "name": "S",
                "category": "Matic",
                "cc": 125,
                "variants": [
                    {"name": "S 150 2V / 3V ie", "start": 2011, "end": 2015, "msrp": 28000000, "aliases": "vespa s 150, vespa s 3v, pagio s 150"},
                    {"name": "S 125 i-Get", "start": 2016, "end": 2026, "msrp": 45500000, "aliases": "vespa s 125, s 125 iget, vespa s iget, pagio s 125"}
                ]
            },
            {
                "name": "GTS",
                "category": "Maxi Matic",
                "cc": 150,
                "variants": [
                    {"name": "GTS Super 150 3V / i-Get", "start": 2014, "end": 2022, "msrp": 67000000, "aliases": "vespa gts 150, gts super 150, gts iget, pagio gts"},
                    {"name": "GTS Classic / Super Sport 150 (Keyless)", "start": 2023, "end": 2026, "msrp": 78800000, "aliases": "gts 150 keyless, gts classic, gts super sport 150"},
                    {"name": "GTS 300 Super Tech HPE", "start": 2019, "end": 2026, "msrp": 165000000, "aliases": "vespa gts 300, gts super tech, gts 300 hpe, pagio gts 300"}
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
                    {"name": "Satria F150 FI All New", "start": 2016, "end": 2026, "msrp": 29000000, "aliases": "satria fu fi, satria f150 injeksi, satria fi"}
                ]
            },
            {
                "name": "GSX-R150 & GSX-S150",
                "category": "Sport",
                "cc": 150,
                "variants": [
                    {"name": "GSX-R150 (Keyless / ABS)", "start": 2017, "end": 2026, "msrp": 35000000, "aliases": "gsx r150, suzuki gsx r, gsx fairing, gsx keyless"},
                    {"name": "GSX-S150 Naked", "start": 2017, "end": 2024, "msrp": 31000000, "aliases": "gsx s150, gsx naked, suzuki gsx s"},
                    {"name": "GSX 150 Bandit", "start": 2018, "end": 2023, "msrp": 28500000, "aliases": "gsx bandit, suzuki bandit, bandit 150"}
                ]
            },
            {
                "name": "Burgman & Nex & Address",
                "category": "Matic",
                "cc": 125,
                "variants": [
                    {"name": "Burgman Street 125EX", "start": 2023, "end": 2026, "msrp": 26000000, "aliases": "burgman 125, burgman street, burgman ex"},
                    {"name": "Nex II (Standard / Cross / Elegant)", "start": 2018, "end": 2026, "msrp": 19400000, "aliases": "suzuki nex, nex 2, nex ii, nex cross"},
                    {"name": "Address FI / Playful", "start": 2014, "end": 2024, "msrp": 18900000, "aliases": "suzuki address, address fi, address playful"},
                    {"name": "Avenis 125", "start": 2022, "end": 2026, "msrp": 30100000, "aliases": "suzuki avenis, avenis 125"}
                ]
            },
            {
                "name": "V-Strom 250SX",
                "category": "Adventure Touring",
                "cc": 250,
                "variants": [
                    {"name": "V-Strom 250SX Adventure", "start": 2023, "end": 2026, "msrp": 59500000, "aliases": "vstrom, v-strom, vstrom 250, suzuki vstrom"}
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
                    # Update category and cc if needed
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
        print(f"✅ Seeding Sukses! Ditambahkan/Diperbarui: {total_brands} Merk Baru, {total_models} Model Baru, {total_variants} Varian Baru.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_master_motor_database()
