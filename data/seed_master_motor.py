"""
Master Data Seeder untuk Katalog Motor Resmi di Indonesia (12 Tahun Terakhir: 2014 - 2026).
Riset komprehensif seluruh Merk, Model, Varian Lengkap, CC Mesin, Kategori Sektor, MSRP Baru, dan Aliases
mencakup model rilisan anyar 2024, 2025, dan 2026 (Model Year 2025/2026).
"""
from models.database import SessionLocal, init_db
from models.catalog import MasterBrand, MasterModel, MasterVariant

MASTER_MOTOR_DATA = [
    # =========================================================================
    # SEKTOR ICE KONVENSIONAL (JEPANG & ITALIA)
    # =========================================================================
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
                    {"name": "Scoopy Facelift LED (2024+)", "start": 2024, "end": 2026, "msrp": 23200000, "aliases": "scoopy 2024, new scoopy"},
                    {"name": "All New Scoopy Gen-6 (LED Projector & Digital Panel 2025+)", "start": 2025, "end": 2026, "msrp": 23330000, "aliases": "all new scoopy 2025, scoopy gen 6, scoopy 2026, new scoopy prestige 2025"}
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
                    {"name": "PCX 160 ABS", "start": 2021, "end": 2026, "msrp": 36000000, "aliases": "pcx 160 abs, all new pcx abs"},
                    {"name": "PCX 160 Facelift New Generation (2025+)", "start": 2025, "end": 2026, "msrp": 36800000, "aliases": "pcx 160 2025, new pcx 2026, all new pcx 160 2025"}
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
                "name": "EM1 e: & EV Series",
                "category": "Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "EM1 e: Standard (Honda MPP e:)", "start": 2024, "end": 2026, "msrp": 33000000, "aliases": "honda em1, em1 e, motor listrik honda, em1"},
                    {"name": "EM1 e: PLUS (Rear Carrier Edition)", "start": 2024, "end": 2026, "msrp": 33500000, "aliases": "em1 plus, em1 e plus, honda em1 plus"},
                    {"name": "CUV e: Dual Battery (6 kW 2025+)", "start": 2025, "end": 2026, "msrp": 53000000, "aliases": "honda cuv e, cuv e, cuv e roadsync duo"},
                    {"name": "ICON e: Compact Commuter (2025+)", "start": 2025, "end": 2026, "msrp": 28000000, "aliases": "honda icon e, icon e, icon ev"}
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
                    {"name": "CRF 250 Rally", "start": 2017, "end": 2026, "msrp": 92900000, "aliases": "crf 250 rally, crf250 rally, crf rally 250"},
                    {"name": "CRF 250L Dual Purpose (2024+)", "start": 2024, "end": 2026, "msrp": 79900000, "aliases": "crf250l, crf 250l, crf 250 l"}
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
                    {"name": "NMAX Turbo / Turbo Tech Max (2024+)", "start": 2024, "end": 2026, "msrp": 37750000, "aliases": "nmax turbo, nmax turbo tech max, nmax turbo yecvt"},
                    {"name": "NMAX Turbo Tech MAX Ultimate (Performance Damper 2025+)", "start": 2025, "end": 2026, "msrp": 45250000, "aliases": "nmax turbo ultimate, nmax tech max ultimate 2025, nmax damper"}
                ]
            },
            {
                "name": "Aerox",
                "category": "Maxi Sport Matic",
                "cc": 155,
                "variants": [
                    {"name": "Aerox 125 LC", "start": 2016, "end": 2017, "msrp": 18200000, "aliases": "aerox 125, aerox 125 lc"},
                    {"name": "Aerox 155 VVA Old (Standard / R / S-Version)", "start": 2017, "end": 2020, "msrp": 24500000, "aliases": "aerox old, aerox lama, aerox 155 2017 2018 2019, aerox tipe r, aerox keyless"},
                    {"name": "Aerox 155 Connected / CyberCity / ABS", "start": 2020, "end": 2026, "msrp": 28500000, "aliases": "all new aerox, aerox connected, aerox cybercity, aerox abs 2021 2022 2023"},
                    {"name": "Aerox 155 Cyber City / Alpha Edition (2025+)", "start": 2025, "end": 2026, "msrp": 28900000, "aliases": "aerox cyber city 2025, aerox alpha 2025, aerox new color 2026"}
                ]
            },
            {
                "name": "PG-1",
                "category": "Outdoor Adventure Underbone",
                "cc": 114,
                "variants": [
                    {"name": "Yamaha PG-1 Adventure Edition (2025+)", "start": 2025, "end": 2026, "msrp": 24500000, "aliases": "yamaha pg 1, yamaha pg-1, pg1 adventure, pg1 outdoor"}
                ]
            },
            {
                "name": "Neo's & E01",
                "category": "Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Yamaha Neo's Dual Lithium (2024+)", "start": 2024, "end": 2026, "msrp": 32000000, "aliases": "yamaha neos, yamaha neo, yamaha ev, neos listrik"},
                    {"name": "Yamaha E01 Maxi EV Concept", "start": 2024, "end": 2026, "msrp": 65000000, "aliases": "yamaha e01, e01 ev, maxi ev yamaha"}
                ]
            },
            {
                "name": "Mio & Fazzio & Filano",
                "category": "Matic Classy & Harian",
                "cc": 125,
                "variants": [
                    {"name": "Mio M3 125 Blue Core", "start": 2014, "end": 2026, "msrp": 17700000, "aliases": "mio m3, mio m3 125, mio 125"},
                    {"name": "Mio S / Mio Z 125", "start": 2016, "end": 2022, "msrp": 17200000, "aliases": "mio s, mio z, mio tubeless"},
                    {"name": "Fazzio Hybrid Connected (Neo / Lux)", "start": 2022, "end": 2026, "msrp": 23050000, "aliases": "yamaha fazzio, fazzio hybrid, fazzio lux, fazzio neo"},
                    {"name": "Grand Filano Hybrid Connected", "start": 2023, "end": 2026, "msrp": 27500000, "aliases": "grand filano, filano hybrid, filano lux, filano neo"}
                ]
            },
            {
                "name": "Lexi",
                "category": "Maxi Matic",
                "cc": 155,
                "variants": [
                    {"name": "Lexi 125 VVA (Standard / S / ABS)", "start": 2018, "end": 2024, "msrp": 23500000, "aliases": "yamaha lexi, lexi 125, lexi s, lexi abs 2018 2019 2020"},
                    {"name": "Lexi LX 155 Connected (Standard / S / ABS)", "start": 2024, "end": 2026, "msrp": 30200000, "aliases": "lexi lx, lexi 155, lexi lx 155, all new lexi 155"}
                ]
            },
            {
                "name": "XMAX & TMAX",
                "category": "Maxi Matic Premium",
                "cc": 250,
                "variants": [
                    {"name": "XMAX 250 Old", "start": 2017, "end": 2022, "msrp": 62000000, "aliases": "xmax lama, xmax 250 old, xmax 2017 2018 2019 2020"},
                    {"name": "XMAX 250 Connected (TFT Navigation)", "start": 2022, "end": 2026, "msrp": 66900000, "aliases": "xmax connected, all new xmax 250, xmax tech max"},
                    {"name": "XMAX Tech MAX 250 (2024+)", "start": 2024, "end": 2026, "msrp": 71300000, "aliases": "xmax tech max, xmax 250 tech max, xmax mewah"},
                    {"name": "TMAX DX 530 CBU", "start": 2018, "end": 2023, "msrp": 320000000, "aliases": "yamaha tmax, tmax dx, tmax 530"}
                ]
            },
            {
                "name": "YZF-R15 & R25",
                "category": "Sport Fairing",
                "cc": 155,
                "variants": [
                    {"name": "YZF-R15 V2", "start": 2014, "end": 2017, "msrp": 29800000, "aliases": "r15 v2, r15 lama"},
                    {"name": "YZF-R15 V3 VVA (USD Fork)", "start": 2017, "end": 2021, "msrp": 36500000, "aliases": "r15 v3, r15 vva, r15 2017 2018 2019 2020"},
                    {"name": "YZF-R15 V4 / R15M Connected ABS", "start": 2021, "end": 2026, "msrp": 44500000, "aliases": "r15 v4, r15m, r15 connected, all new r15"},
                    {"name": "YZF-R25 Old (Generasi 1)", "start": 2014, "end": 2018, "msrp": 54000000, "aliases": "r25 old, r25 lama, r25 2 silinder"},
                    {"name": "YZF-R25 Facelift (USD / ABS)", "start": 2018, "end": 2026, "msrp": 63900000, "aliases": "r25 new, r25 facelift, r25 usd, r25 abs"}
                ]
            },
            {
                "name": "MT-15 & MT-25 & Vixion",
                "category": "Sport Naked",
                "cc": 155,
                "variants": [
                    {"name": "Vixion Lightning (NVL) / Advance (NVA)", "start": 2013, "end": 2017, "msrp": 24500000, "aliases": "vixion nvl, vixion nva, vixion advance, new vixion lightning"},
                    {"name": "Vixion R 155 VVA / All New Vixion", "start": 2017, "end": 2026, "msrp": 29500000, "aliases": "vixion r, all new vixion, vixion 155 vva"},
                    {"name": "Xabre 150 (USD)", "start": 2016, "end": 2019, "msrp": 30500000, "aliases": "yamaha xabre, xabre 150"},
                    {"name": "MT-15 VVA (Inverted Fork)", "start": 2019, "end": 2026, "msrp": 38800000, "aliases": "yamaha mt 15, mt15, mt 15"},
                    {"name": "MT-25 (Dual Cylinder)", "start": 2015, "end": 2026, "msrp": 57500000, "aliases": "yamaha mt 25, mt25, mt 25 new"}
                ]
            },
            {
                "name": "XSR 155 & WR 155 R",
                "category": "Sport Heritage & Trail",
                "cc": 155,
                "variants": [
                    {"name": "XSR 155 Born to be Free", "start": 2019, "end": 2026, "msrp": 38200000, "aliases": "xsr 155, yamaha xsr, xsr retro"},
                    {"name": "WR 155 R VVA Dual Purpose", "start": 2019, "end": 2026, "msrp": 39000000, "aliases": "wr 155, wr 155 r, yamaha wr155"}
                ]
            },
            {
                "name": "Jupiter & Vega",
                "category": "Bebek / Moped",
                "cc": 150,
                "variants": [
                    {"name": "Vega Force / Jupiter Z1 FI", "start": 2014, "end": 2026, "msrp": 18200000, "aliases": "jupiter z1, vega force, jupiter robot"},
                    {"name": "Jupiter MX King 150 (Gen 1 & Facelift)", "start": 2015, "end": 2026, "msrp": 26200000, "aliases": "mx king, mx king 150, jupiter mx king"}
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
                    {"name": "Ninja 250 Karburator", "start": 2008, "end": 2012, "msrp": 47500000, "aliases": "ninja 250 karbu, ninja lama, ninja 250 gen 1"},
                    {"name": "Ninja 250 FI (Generasi 1)", "start": 2012, "end": 2017, "msrp": 59800000, "aliases": "ninja 250 fi lama, ninja fi 2013 2014 2015 2016 2017, ninja 250 abs se"},
                    {"name": "Ninja 250 FI All New (Generasi 2 Keyless)", "start": 2018, "end": 2026, "msrp": 68500000, "aliases": "all new ninja 250, ninja 250 new, ninja 250 keyless, ninja 250 mdp"},
                    {"name": "Ninja 250 SL / Mono (1-Silinder)", "start": 2014, "end": 2023, "msrp": 36500000, "aliases": "ninja mono, ninja 250 mono, ninja rr mono, ninja sl"}
                ]
            },
            {
                "name": "Ninja ZX Series",
                "category": "Sport High Performance (4-Silinder)",
                "cc": 250,
                "variants": [
                    {"name": "Ninja ZX-25R Standard", "start": 2020, "end": 2026, "msrp": 109000000, "aliases": "zx25r standard, zx 25r non abs, ninja 4 silinder"},
                    {"name": "Ninja ZX-25R SE / ABS (Quickshifter)", "start": 2020, "end": 2026, "msrp": 127000000, "aliases": "zx25r se, zx 25r abs se, zx25r quickshifter, zx25r tft"},
                    {"name": "Ninja ZX-25RR", "start": 2022, "end": 2026, "msrp": 133500000, "aliases": "zx25rr, zx-25rr, ninja zx25rr"},
                    {"name": "Ninja ZX-4RR (In-Line 4 399cc 77PS 2024+)", "start": 2024, "end": 2026, "msrp": 244800000, "aliases": "zx4rr, zx-4rr, ninja zx4rr, kawasaki zx4rr"}
                ]
            },
            {
                "name": "Eliminator",
                "category": "Modern Cruiser (Parallel-Twin)",
                "cc": 451,
                "variants": [
                    {"name": "Eliminator 500 Standard (2024+)", "start": 2024, "end": 2026, "msrp": 169900000, "aliases": "kawasaki eliminator, eliminator 500, eliminator 450, cruiser kawasaki"},
                    {"name": "Eliminator 500 SE (Headlight Cowl 2024+)", "start": 2024, "end": 2026, "msrp": 199900000, "aliases": "eliminator se, kawasaki eliminator se, eliminator 500 se"}
                ]
            },
            {
                "name": "Ninja e-1 & Z e-1",
                "category": "Electric Sport (Dual Battery)",
                "cc": 0,
                "variants": [
                    {"name": "Ninja e-1 Fairing Sport EV (2024+)", "start": 2024, "end": 2026, "msrp": 149900000, "aliases": "ninja e-1, ninja e1, kawasaki ninja listrik, ninja ev"},
                    {"name": "Z e-1 Naked Streetfighter EV (2024+)", "start": 2024, "end": 2026, "msrp": 146900000, "aliases": "z e-1, z e1, kawasaki z listrik, z ev"}
                ]
            },
            {
                "name": "KLX 150",
                "category": "Trail / Dual Purpose",
                "cc": 150,
                "variants": [
                    {"name": "KLX 150S / 150L (Gen 1)", "start": 2009, "end": 2015, "msrp": 25000000, "aliases": "klx lama, klx 150s, klx 150l"},
                    {"name": "KLX 150 BF / SE (USD Fork)", "start": 2015, "end": 2023, "msrp": 36000000, "aliases": "klx bf, klx bf se, klx 150 usd"},
                    {"name": "KLX 150 All New (LED)", "start": 2023, "end": 2026, "msrp": 37500000, "aliases": "all new klx 150, klx 150 led, klx 2023 2024"}
                ]
            },
            {
                "name": "KLX 230 & KLX 250",
                "category": "Dual Purpose & Supermoto",
                "cc": 230,
                "variants": [
                    {"name": "KLX 230 / SE / S", "start": 2019, "end": 2026, "msrp": 45000000, "aliases": "klx 230, klx 230s, klx 230 se"},
                    {"name": "KLX 230SM / Supermoto", "start": 2022, "end": 2026, "msrp": 55000000, "aliases": "klx 230sm, klx supermoto 230"},
                    {"name": "KLX 230 SE / SM Facelift (New Headlamp 2025+)", "start": 2025, "end": 2026, "msrp": 52500000, "aliases": "klx 230 2025, new klx 230 2026"}
                ]
            },
            {
                "name": "D-Tracker & KLX SM",
                "category": "Supermoto",
                "cc": 150,
                "variants": [
                    {"name": "D-Tracker 150 SE (Velg 17)", "start": 2015, "end": 2023, "msrp": 35500000, "aliases": "dtracker, d-tracker 150, dtracker se"},
                    {"name": "KLX 150 SM / SM SE", "start": 2023, "end": 2026, "msrp": 37500000, "aliases": "klx sm, klx 150 sm, klx supermoto 150"}
                ]
            },
            {
                "name": "W175",
                "category": "Classic / Retro",
                "cc": 177,
                "variants": [
                    {"name": "W175 Standard / SE / Cafe / TR", "start": 2017, "end": 2024, "msrp": 32000000, "aliases": "kawasaki w175, w175 cafe, w175 tr, w175 se"},
                    {"name": "W175 Black Style (Injeksi)", "start": 2024, "end": 2026, "msrp": 35900000, "aliases": "w175 fi, w175 injeksi, w175 black style"}
                ]
            },
            {
                "name": "Z Series & Versys",
                "category": "Naked & Adventure",
                "cc": 250,
                "variants": [
                    {"name": "Z250 2-Silinder", "start": 2013, "end": 2019, "msrp": 53000000, "aliases": "kawasaki z250, z 250, z250 fi"},
                    {"name": "Versys-X 250 Tourer / City", "start": 2017, "end": 2026, "msrp": 71500000, "aliases": "versys 250, versys x 250, versys tourer"}
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
                "category": "Classic Matic",
                "cc": 150,
                "variants": [
                    {"name": "Sprint 150 3V (Non i-Get)", "start": 2014, "end": 2016, "msrp": 36500000, "aliases": "sprint 3v, vespa sprint 3v 2014 2015"},
                    {"name": "Sprint 150 i-Get ABS", "start": 2016, "end": 2024, "msrp": 53800000, "aliases": "sprint iget, vespa sprint iget, sprint abs"},
                    {"name": "Sprint S 150 i-Get ABS", "start": 2019, "end": 2024, "msrp": 56300000, "aliases": "sprint s, vespa sprint s 150"},
                    {"name": "Sprint S Tech (New Cockpit LED 2025+)", "start": 2025, "end": 2026, "msrp": 59500000, "aliases": "sprint 2025, sprint s 2025, sprint tech, new vespa sprint 2026"}
                ]
            },
            {
                "name": "Primavera",
                "category": "Classic Matic",
                "cc": 150,
                "variants": [
                    {"name": "Primavera 150 3V", "start": 2014, "end": 2016, "msrp": 34500000, "aliases": "primavera 3v, vespa primavera 3v"},
                    {"name": "Primavera 150 i-Get ABS", "start": 2016, "end": 2024, "msrp": 51200000, "aliases": "primavera iget, vespa primavera abs"},
                    {"name": "Primavera S 150 i-Get ABS", "start": 2019, "end": 2024, "msrp": 53700000, "aliases": "primavera s, vespa primavera s"},
                    {"name": "Primavera Tech / S (Full LED Digital Cockpit 2025+)", "start": 2025, "end": 2026, "msrp": 57500000, "aliases": "primavera 2025, primavera tech, new primavera 2026, primavera s 2025"}
                ]
            },
            {
                "name": "LX & S",
                "category": "Entry Classic Matic",
                "cc": 125,
                "variants": [
                    {"name": "LX 125 / 150 2V-3V", "start": 2011, "end": 2016, "msrp": 26000000, "aliases": "vespa lx 125 karbu, vespa lx 150, vespa lx 3v"},
                    {"name": "LX 125 i-Get", "start": 2017, "end": 2026, "msrp": 45350000, "aliases": "vespa lx iget, lx 125 iget, vespa lx baru"},
                    {"name": "S 125 i-Get", "start": 2017, "end": 2026, "msrp": 45500000, "aliases": "vespa s 125, vespa s iget, s 125 baru"}
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
            },
            {
                "name": "946 & Elettrica",
                "category": "Luxury Collector & EV",
                "cc": 150,
                "variants": [
                    {"name": "Vespa 946 Dragon / Snake Limited Edition (2024+)", "start": 2024, "end": 2026, "msrp": 267000000, "aliases": "vespa 946 dragon, 946 dragon, vespa dragon, vespa 946 snake"},
                    {"name": "Vespa Elettrica (Electric EV 2024+)", "start": 2024, "end": 2026, "msrp": 198000000, "aliases": "vespa elettrica, vespa listrik, vespa elektrik"}
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
                "category": "Maxi Matic",
                "cc": 150,
                "variants": [
                    {"name": "Medley 150 i-Get ABS (Gen 1)", "start": 2016, "end": 2019, "msrp": 45000000, "aliases": "piaggio medley, medley 150, medley iget"},
                    {"name": "Medley S 150 i-Get (Facelift LED)", "start": 2020, "end": 2024, "msrp": 51800000, "aliases": "medley s, medley s 150, piaggio medley new"},
                    {"name": "Medley S 150 Facelift (MIA Connectivity 2025+)", "start": 2025, "end": 2026, "msrp": 55000000, "aliases": "medley 2025, new medley s 150, medley 2026"}
                ]
            },
            {
                "name": "Liberty",
                "category": "Matic",
                "cc": 150,
                "variants": [
                    {"name": "Liberty 150 3V", "start": 2013, "end": 2016, "msrp": 29000000, "aliases": "piaggio liberty, liberty 150, liberty 3v"},
                    {"name": "Liberty 150 i-Get / S", "start": 2016, "end": 2026, "msrp": 43500000, "aliases": "liberty iget, liberty 150 s, piaggio liberty baru"}
                ]
            },
            {
                "name": "MP3 & Beverly",
                "category": "Trike & Maxi Scooter",
                "cc": 300,
                "variants": [
                    {"name": "Beverly 300 / 350 S", "start": 2014, "end": 2022, "msrp": 175000000, "aliases": "piaggio beverly, beverly 300"},
                    {"name": "MP3 300 HPE / 500 LT Sport", "start": 2015, "end": 2026, "msrp": 330000000, "aliases": "piaggio mp3, mp3 roda 3, mp3 300 hpe"}
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
                "name": "Burgman & Access",
                "category": "Matic & Retro",
                "cc": 125,
                "variants": [
                    {"name": "Burgman 200 CBU", "start": 2014, "end": 2019, "msrp": 59900000, "aliases": "burgman 200, suzuki burgman 200"},
                    {"name": "Burgman Street 125EX", "start": 2023, "end": 2026, "msrp": 26000000, "aliases": "burgman 125, burgman street, burgman ex"},
                    {"name": "Suzuki Access 125 Retro Edition (2025+)", "start": 2025, "end": 2026, "msrp": 24800000, "aliases": "suzuki access, access 125, suzuki retro, access 2025"},
                    {"name": "e-Burgman (Swappable Battery EV 2025+)", "start": 2025, "end": 2026, "msrp": 35000000, "aliases": "e-burgman, burgman listrik, suzuki ev, e burgman"}
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
                "name": "V-Strom Series",
                "category": "Adventure Touring",
                "cc": 250,
                "variants": [
                    {"name": "Inazuma 250 GW250 (2-Silinder)", "start": 2012, "end": 2016, "msrp": 49500000, "aliases": "inazuma 250, suzuki inazuma, gw250"},
                    {"name": "V-Strom 250SX Adventure", "start": 2023, "end": 2026, "msrp": 59500000, "aliases": "vstrom, v-strom, vstrom 250, suzuki vstrom"},
                    {"name": "V-Strom 800DE (Parallel Twin 776cc 2024+)", "start": 2024, "end": 2026, "msrp": 290000000, "aliases": "vstrom 800, v-strom 800de, suzuki vstrom 800"}
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
                "name": "Fox-500 & T-Rex",
                "category": "High Performance Maxi Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Fox-500 (14.7 kW Top-Tier Maxi EV 2025+)", "start": 2025, "end": 2026, "msrp": 43000000, "aliases": "polytron fox 500, fox 500, polytron fox-500, fox500"},
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
                    {"name": "Alva One Standard", "start": 2022, "end": 2026, "msrp": 36490000, "aliases": "alva one, motor alva, alva auto"},
                    {"name": "Alva One XP (Dynamic TFT)", "start": 2024, "end": 2026, "msrp": 38500000, "aliases": "alva one xp, alva xp, alva one tft"}
                ]
            },
            {
                "name": "Alva Cervo",
                "category": "Performance Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Alva Cervo (1 Battery)", "start": 2023, "end": 2026, "msrp": 37750000, "aliases": "alva cervo, cervo 1 batt"},
                    {"name": "Alva Cervo (2 Battery / Boost Mode)", "start": 2023, "end": 2026, "msrp": 42750000, "aliases": "alva cervo 2 battery, cervo dual batt"},
                    {"name": "Alva Cervo Q (Flagship Boost Charger 2025+)", "start": 2025, "end": 2026, "msrp": 49500000, "aliases": "alva cervo q, cervo q, alva cervo-q, cervo 2025"}
                ]
            },
            {
                "name": "Alva N3",
                "category": "Urban Commuter Electric (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Alva N3 (Fast Charging Entry EV)", "start": 2024, "end": 2026, "msrp": 18500000, "aliases": "alva n3, alva n 3, alva entry ev, alva n3 boost"}
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
                    {"name": "Gesits G1 (Single Battery)", "start": 2019, "end": 2026, "msrp": 28970000, "aliases": "gesits g1, motor gesits, gesits gen 1"},
                    {"name": "Gesits G2 Next Generation (2025+)", "start": 2025, "end": 2026, "msrp": 29800000, "aliases": "gesits g2, all new gesits, gesits 2025, gesits 2026"}
                ]
            },
            {
                "name": "Gesits Raya & Garuda",
                "category": "Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Gesits Raya G", "start": 2023, "end": 2026, "msrp": 27990000, "aliases": "gesits raya, gesits raya g"},
                    {"name": "Gesits Raya E", "start": 2023, "end": 2026, "msrp": 24990000, "aliases": "gesits raya e, raya e"},
                    {"name": "Gesits Garuda Special Edition (2024+)", "start": 2024, "end": 2026, "msrp": 28300000, "aliases": "gesits garuda, garuda ev, gesits edisi khusus"}
                ]
            }
        ]
    },
    {
        "brand": "Yadea",
        "country": "China",
        "models": [
            {
                "name": "Yadea T9 & Minio",
                "category": "Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Yadea T9 (TTFAR Technology)", "start": 2023, "end": 2026, "msrp": 21500000, "aliases": "yadea t9, motor yadea t9, yadea ttfar"},
                    {"name": "Yadea Minio (Retro Classic EV 2025+)", "start": 2025, "end": 2026, "msrp": 16800000, "aliases": "yadea minio, minio ev, yadea retro"}
                ]
            },
            {
                "name": "Yadea E8S Pro",
                "category": "Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Yadea E8S Pro (Graphene Battery)", "start": 2023, "end": 2026, "msrp": 23900000, "aliases": "yadea e8s, yadea e8s pro, e8s pro"}
                ]
            },
            {
                "name": "Yadea G6 & Keeness",
                "category": "Electric Lifestyle & Sport (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Yadea G6 (Red Dot Design)", "start": 2023, "end": 2026, "msrp": 27500000, "aliases": "yadea g6, motor yadea g6"},
                    {"name": "Yadea Keeness (Naked Electric Motorcycle 2024+)", "start": 2024, "end": 2026, "msrp": 39500000, "aliases": "yadea keeness, yadea sport, motor listrik sport yadea"}
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
                    {"name": "Viar Q1 (Generasi 1)", "start": 2017, "end": 2019, "msrp": 16200000, "aliases": "viar q1 lama, viar q1 gen 1"},
                    {"name": "Viar Q1 (Generasi 2 / Smart Key)", "start": 2019, "end": 2026, "msrp": 21500000, "aliases": "viar q1, viar q1 gen 2, viar q1 new"}
                ]
            },
            {
                "name": "Viar N & EV Series",
                "category": "Electric Scooter (EV)",
                "cc": 0,
                "variants": [
                    {"name": "Viar N1 / N2", "start": 2022, "end": 2026, "msrp": 25800000, "aliases": "viar n1, viar n2, motor listrik viar n1"},
                    {"name": "Viar NX (Modern Urban Commuter 2024+)", "start": 2024, "end": 2026, "msrp": 14500000, "aliases": "viar nx, viar ev nx, viar nx 2024"},
                    {"name": "Viar EV1 (Classic Vespa-Style EV 2024+)", "start": 2024, "end": 2026, "msrp": 15300000, "aliases": "viar ev1, viar ev 1, viar vespa listrik"}
                ]
            }
        ]
    },
    # =========================================================================
    # SEKTOR RETRO, CRUISER & PERFORMANCE SPORT
    # =========================================================================
    {
        "brand": "Royal Enfield",
        "country": "Inggris / India",
        "models": [
            {
                "name": "Hunter 350",
                "category": "Modern Roadster Classic",
                "cc": 349,
                "variants": [
                    {"name": "Hunter 350 Retro / Metro", "start": 2022, "end": 2026, "msrp": 106400000, "aliases": "re hunter 350, royal enfield hunter, hunter 350"}
                ]
            },
            {
                "name": "Classic 350",
                "category": "Heritage Classic",
                "cc": 349,
                "variants": [
                    {"name": "Classic 350 (UCE Old Engine)", "start": 2014, "end": 2021, "msrp": 85000000, "aliases": "classic 350 uce, re classic 350 lama"},
                    {"name": "Classic 350 Reborn (J-Platform)", "start": 2022, "end": 2026, "msrp": 113000000, "aliases": "re classic 350 reborn, classic 350 j series"},
                    {"name": "Classic 350 J-Series LED Facelift (2025+)", "start": 2025, "end": 2026, "msrp": 122000000, "aliases": "classic 350 2025, new classic 350, classic 350 led 2026"}
                ]
            },
            {
                "name": "Meteor 350 & Bullet",
                "category": "Cruiser Classic",
                "cc": 349,
                "variants": [
                    {"name": "Meteor 350 (Fireball / Stellar / Supernova)", "start": 2021, "end": 2026, "msrp": 119800000, "aliases": "re meteor 350, meteor 350, royal enfield meteor"},
                    {"name": "Bullet 350 J-Platform (2024+)", "start": 2024, "end": 2026, "msrp": 115000000, "aliases": "re bullet 350, bullet 350, royal enfield bullet"}
                ]
            },
            {
                "name": "Himalayan & Guerrilla",
                "category": "Adventure & Roadster",
                "cc": 452,
                "variants": [
                    {"name": "Himalayan 411 LS (Karbu/FI)", "start": 2018, "end": 2023, "msrp": 128000000, "aliases": "re himalayan 411, himalayan lama, himalayan ls410"},
                    {"name": "All New Himalayan 450 (Sherpa Liquid-Cooled)", "start": 2024, "end": 2026, "msrp": 155000000, "aliases": "himalayan 450, re himalayan 450, sherpa 450"},
                    {"name": "Guerrilla 450 (Sherpa Modern Roadster 2025+)", "start": 2025, "end": 2026, "msrp": 185000000, "aliases": "re guerrilla, guerrilla 450, royal enfield guerrilla, guerrilla 2025"}
                ]
            },
            {
                "name": "650 Twins & Shotgun",
                "category": "Twin Cylinder Cafe & Bobber",
                "cc": 648,
                "variants": [
                    {"name": "Interceptor 650 Twin", "start": 2019, "end": 2026, "msrp": 221500000, "aliases": "re interceptor 650, interceptor 650, twin 650"},
                    {"name": "Continental GT 650 Cafe Racer", "start": 2019, "end": 2026, "msrp": 238000000, "aliases": "re continental gt 650, continental 650"},
                    {"name": "Super Meteor 650 Cruiser", "start": 2023, "end": 2026, "msrp": 242000000, "aliases": "super meteor 650, re super meteor"},
                    {"name": "Shotgun 650 Custom Bobber (2024+)", "start": 2024, "end": 2026, "msrp": 237800000, "aliases": "re shotgun 650, royal enfield shotgun, shotgun 650, shotgun 2024"}
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
                "category": "Cruiser Modern Retro",
                "cc": 197,
                "variants": [
                    {"name": "Motobi 200 EVO (Injeksi)", "start": 2018, "end": 2026, "msrp": 37800000, "aliases": "benelli motobi 200 evo, motobi evo"},
                    {"name": "Motobi 200 EFI (Classic Style)", "start": 2018, "end": 2024, "msrp": 35500000, "aliases": "motobi 200 efi, motobi classic"}
                ]
            },
            {
                "name": "Patagonian Eagle 250",
                "category": "Twin Cruiser (Suara Merdu)",
                "cc": 249,
                "variants": [
                    {"name": "Patagonian Eagle 250 (Karbu / Twin)", "start": 2018, "end": 2023, "msrp": 44800000, "aliases": "benelli patagonian eagle, patagonian eagle karbu"},
                    {"name": "Patagonian Eagle 250 EFI (Injeksi)", "start": 2023, "end": 2026, "msrp": 48900000, "aliases": "patagonian eagle efi, patagonian injeksi"}
                ]
            },
            {
                "name": "Keeway V250Fi & Benda",
                "category": "V-Twin Cruiser & Bobber",
                "cc": 249,
                "variants": [
                    {"name": "Keeway V250Fi Geronimo", "start": 2020, "end": 2026, "msrp": 59800000, "aliases": "keeway v250fi, keeway v250, geronimo 250"},
                    {"name": "Keeway Benda V252C (V-Twin 250cc TCS 2024+)", "start": 2024, "end": 2026, "msrp": 73800000, "aliases": "benda v252c, keeway benda, v252c, keeway benda 250"}
                ]
            },
            {
                "name": "Napoleon 250",
                "category": "Single-Seat Bobber Cruiser",
                "cc": 249,
                "variants": [
                    {"name": "Keeway Napoleon 250 (Floating Seat Bobber 2025+)", "start": 2025, "end": 2026, "msrp": 75000000, "aliases": "keeway napoleon 250, napoleon 250, bobby 250, napoleon bobber"}
                ]
            },
            {
                "name": "Panarea & Shiny",
                "category": "Retro Classic Matic",
                "cc": 125,
                "variants": [
                    {"name": "Benelli Panarea 125", "start": 2021, "end": 2026, "msrp": 26800000, "aliases": "benelli panarea, panarea 125"},
                    {"name": "Keeway Shiny 150", "start": 2022, "end": 2026, "msrp": 27200000, "aliases": "keeway shiny, shiny 150"}
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
                "category": "Naked Sport Performance",
                "cc": 250,
                "variants": [
                    {"name": "KTM Duke 200 / 250 (Gen 2)", "start": 2017, "end": 2023, "msrp": 52000000, "aliases": "ktm duke 200, duke 250, ktm duke lama"},
                    {"name": "KTM 390 Duke (Gen 2 TFT)", "start": 2017, "end": 2023, "msrp": 99900000, "aliases": "ktm 390 duke, duke 390, duke 390 gen 2"},
                    {"name": "KTM 250 Duke Gen-3 (2024+)", "start": 2024, "end": 2026, "msrp": 99000000, "aliases": "250 duke gen 3, duke 250 2024 2025, all new duke 250"},
                    {"name": "KTM 390 Duke Gen-3 (LC4c Engine 399cc 2024+)", "start": 2024, "end": 2026, "msrp": 145000000, "aliases": "390 duke gen 3, duke 390 2024 2025, new 390 duke, ktm 390 2025"}
                ]
            },
            {
                "name": "RC Series",
                "category": "Sport Fairing Track",
                "cc": 250,
                "variants": [
                    {"name": "KTM RC 200 / 250 (Gen 1)", "start": 2015, "end": 2021, "msrp": 53900000, "aliases": "ktm rc 200, ktm rc 250, rc 250 gen 1"},
                    {"name": "KTM RC 390 (Gen 2 All New)", "start": 2022, "end": 2026, "msrp": 104900000, "aliases": "ktm rc 390, rc 390 gen 2, rc 390 new"}
                ]
            },
            {
                "name": "Adventure Series",
                "category": "Adventure Enduro",
                "cc": 250,
                "variants": [
                    {"name": "KTM 250 Adventure", "start": 2021, "end": 2026, "msrp": 79000000, "aliases": "ktm 250 adv, 250 adventure, ktm adventure 250"},
                    {"name": "KTM 390 Adventure (Spoke Wheels)", "start": 2020, "end": 2026, "msrp": 119000000, "aliases": "ktm 390 adv, 390 adventure, 390 adv sw"}
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
                "category": "Retro Matic (Plat Bodi Metal)",
                "cc": 110,
                "variants": [
                    {"name": "Callisto 110 Classic / Intelligo", "start": 2019, "end": 2026, "msrp": 19900000, "aliases": "tvs callisto, callisto 110, callisto intelligo"},
                    {"name": "Callisto 125", "start": 2023, "end": 2026, "msrp": 22300000, "aliases": "callisto 125, tvs callisto 125"}
                ]
            },
            {
                "name": "Ronin",
                "category": "Modern Retro Scrambler",
                "cc": 225,
                "variants": [
                    {"name": "Ronin 225 SS (Single Tone)", "start": 2023, "end": 2026, "msrp": 35500000, "aliases": "tvs ronin, ronin 225, ronin ss"},
                    {"name": "Ronin 225 TD (Triple Tone / Dual ABS)", "start": 2023, "end": 2026, "msrp": 39500000, "aliases": "ronin td, ronin dual abs, ronin 225 td"}
                ]
            },
            {
                "name": "Apache RTR & iQube",
                "category": "Sport Naked & Smart EV",
                "cc": 200,
                "variants": [
                    {"name": "Apache RTR 200 4V", "start": 2016, "end": 2026, "msrp": 30500000, "aliases": "tvs apache, apache 200, apache rtr 200"},
                    {"name": "Apache RTR 310 (BTO Dynamic Quickshifter 2024+)", "start": 2024, "end": 2026, "msrp": 49900000, "aliases": "tvs rtr 310, apache rtr 310, apache 310 naked, tvs 310"},
                    {"name": "TVS iQube S (Connected Smart EV 2025+)", "start": 2025, "end": 2026, "msrp": 29900000, "aliases": "tvs iqube, iqube ev, tvs listrik, tvs iqube s"}
                ]
            }
        ]
    },
    # =========================================================================
    # SEKTOR BIG BIKE / MOGE PREMIUM (AMERIKA & JERMAN)
    # =========================================================================
    {
        "brand": "Harley-Davidson",
        "country": "Amerika Serikat",
        "models": [
            {
                "name": "Street 500",
                "category": "Entry Cruiser (Revolution X)",
                "cc": 494,
                "variants": [
                    {"name": "Street 500 XG500", "start": 2014, "end": 2020, "msrp": 275000000, "aliases": "harley street 500, hd street 500, xg500"}
                ]
            },
            {
                "name": "Sportster Series",
                "category": "Classic & Revolution Max Cruiser",
                "cc": 883,
                "variants": [
                    {"name": "Sportster Iron 883 (Evolution Air-Cooled)", "start": 2014, "end": 2022, "msrp": 420000000, "aliases": "harley iron 883, iron 883, hd iron 883, sportster 883"},
                    {"name": "Sportster Forty-Eight 1200 (Evolution)", "start": 2014, "end": 2022, "msrp": 485000000, "aliases": "harley 48, forty eight, hd forty-eight, sportster 1200"},
                    {"name": "Nightster Special 975 (Revolution Max 2024+)", "start": 2024, "end": 2026, "msrp": 575000000, "aliases": "harley nightster, nightster special, hd nightster, nightster 975"},
                    {"name": "Sportster S 1250T (Revolution Max 2024+)", "start": 2024, "end": 2026, "msrp": 650000000, "aliases": "sportster s, hd sportster s, 1250t, harley sportster s"}
                ]
            },
            {
                "name": "Softail & Pan America",
                "category": "Heavyweight Cruiser & Flagship Adventure",
                "cc": 1745,
                "variants": [
                    {"name": "Softail Fat Boy 114 (Milwaukee-Eight)", "start": 2018, "end": 2026, "msrp": 650000000, "aliases": "harley fat boy, fat boy 114, hd softail fat boy"},
                    {"name": "Softail Breakout 114 (Milwaukee-Eight)", "start": 2018, "end": 2026, "msrp": 680000000, "aliases": "harley breakout, breakout 114, hd breakout"},
                    {"name": "Pan America 1250 Special (Revolution Max 2024+)", "start": 2024, "end": 2026, "msrp": 810000000, "aliases": "pan america 1250, hd pan america, pan america special, harley adventure"}
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
                "name": "C 400 & CE EV Series",
                "category": "Luxury Maxi Scooter & Futuristic EV",
                "cc": 350,
                "variants": [
                    {"name": "BMW C 400 X (Urban)", "start": 2019, "end": 2026, "msrp": 259000000, "aliases": "bmw c400x, c 400 x, matic bmw"},
                    {"name": "BMW C 400 GT (Gran Turismo)", "start": 2019, "end": 2026, "msrp": 279000000, "aliases": "bmw c400gt, c 400 gt, c400 gt"},
                    {"name": "BMW CE 02 (e-Parkourer Urban EV 2024+)", "start": 2024, "end": 2026, "msrp": 309000000, "aliases": "bmw ce 02, bmw ce02, bmw listrik, ce 02"},
                    {"name": "BMW CE 04 (Futuristic Maxi EV 2024+)", "start": 2024, "end": 2026, "msrp": 418000000, "aliases": "bmw ce 04, bmw ce04, matic listrik bmw, ce 04"}
                ]
            },
            {
                "name": "R 1250 GS & R 1300 GS",
                "category": "Flagship Adventure Boxer",
                "cc": 1300,
                "variants": [
                    {"name": "BMW R 1250 GS Standard", "start": 2019, "end": 2024, "msrp": 805000000, "aliases": "bmw r1250gs, r 1250 gs, bmw r 1250, r1250 gs"},
                    {"name": "BMW R 1250 GS Adventure (GSA)", "start": 2019, "end": 2024, "msrp": 855000000, "aliases": "bmw r1250gsa, r 1250 gsa, bmw gsa 1250"},
                    {"name": "BMW R 1300 GS Trophy / Option 719 (2024+)", "start": 2024, "end": 2026, "msrp": 890000000, "aliases": "bmw r1300gs, r 1300 gs, r1300 gs, bmw 1300 gs, r 1300 gs trophy"},
                    {"name": "BMW R 1300 GS Adventure (GSA 2025+)", "start": 2025, "end": 2026, "msrp": 950000000, "aliases": "bmw r1300gsa, r 1300 gsa, r1300 adventure, bmw gsa 1300, r 1300 gsa 2025"}
                ]
            },
            {
                "name": "F 900 GS Series",
                "category": "Middleweight Enduro Adventure",
                "cc": 895,
                "variants": [
                    {"name": "BMW F 900 GS / Adventure (2024+)", "start": 2024, "end": 2026, "msrp": 550000000, "aliases": "bmw f900gs, f 900 gs, bmw f900 gs, f 900 gs adventure"}
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
            else:
                brand_obj.country_origin = brand_item["country"]

            for model_item in brand_item["models"]:
                model_obj = db.query(MasterModel).filter(
                    MasterModel.brand_id == brand_obj.id,
                    MasterModel.name == model_item["name"]
                ).first()

                from data.populate_catalog_images import get_image_for_model
                img_url = get_image_for_model(brand_obj.name, model_item["name"])

                if not model_obj:
                    model_obj = MasterModel(
                        brand_id=brand_obj.id,
                        name=model_item["name"],
                        category=model_item.get("category", "Matic"),
                        engine_capacity_cc=model_item.get("cc"),
                        image_url=img_url
                    )
                    db.add(model_obj)
                    db.flush()
                    total_models += 1
                else:
                    model_obj.category = model_item.get("category", model_obj.category)
                    model_obj.engine_capacity_cc = model_item.get("cc", model_obj.engine_capacity_cc)
                    model_obj.image_url = img_url

                for var_item in model_item["variants"]:
                    var_img_url = get_image_for_model(brand_obj.name, f"{model_item['name']} {var_item['name']}")
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
                            aliases=var_item.get("aliases"),
                            image_url=var_img_url
                        )
                        db.add(var_obj)
                        total_variants += 1
                    else:
                        var_obj.release_year_start = var_item["start"]
                        var_obj.release_year_end = var_item.get("end")
                        var_obj.official_msrp_new = var_item.get("msrp")
                        var_obj.aliases = var_item.get("aliases")
                        var_obj.image_url = var_img_url

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
