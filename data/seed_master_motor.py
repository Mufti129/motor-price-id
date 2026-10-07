"""
Master Data Seeder untuk Katalog Motor di Indonesia.
Mencakup Merk, Model, Varian, Rentang Tahun Rilis, CC, dan Alias untuk Entity Matching.
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
                    {"name": "Beat FI eSP (Generasi 2/3)", "start": 2012, "end": 2019, "msrp": 15500000, "aliases": "beat fi, beat esp, beat cbs iss, beat pop"},
                    {"name": "Beat Street eSP", "start": 2016, "end": 2024, "msrp": 18500000, "aliases": "beat street, beat strit"},
                    {"name": "Beat Deluxe / CBS (eSAF)", "start": 2020, "end": 2024, "msrp": 18200000, "aliases": "beat deluxe, beat esaf, beat cbs baru, all new beat"},
                    {"name": "Beat All New (Keyless 2024+)", "start": 2024, "end": 2026, "msrp": 19500000, "aliases": "beat smart key, beat 2024, beat keyless"}
                ]
            },
            {
                "name": "Vario",
                "category": "Matic",
                "cc": 125,
                "variants": [
                    {"name": "Vario 110 Karbu / Techno", "start": 2006, "end": 2014, "msrp": 14000000, "aliases": "vario karbu, vario 110 cw, vario techno 110"},
                    {"name": "Vario 125 eSP (LED Generasi 1)", "start": 2015, "end": 2018, "msrp": 18500000, "aliases": "vario 125 led lama, vario 125 esp 2015 2016 2017"},
                    {"name": "Vario 125 All New (Generasi 2)", "start": 2018, "end": 2022, "msrp": 22000000, "aliases": "vario 125 new, vario 125 cbs iss 2018 2019 2020 2021"},
                    {"name": "Vario 125 Facelift (Keyless)", "start": 2022, "end": 2026, "msrp": 24500000, "aliases": "vario 125 new keyless, vario 125 smart key"},
                    {"name": "Vario 150 eSP Exclusive / Keyless", "start": 2015, "end": 2022, "msrp": 24900000, "aliases": "vario 150, vario 150 keyless, vario 150 esp, vario 150 led"},
                    {"name": "Vario 160 CBS / ABS", "start": 2022, "end": 2026, "msrp": 27500000, "aliases": "vario 160, vario 160 cbs, vario 160 abs"}
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
                    {"name": "Scoopy All New (Keyless / Prestige)", "start": 2020, "end": 2024, "msrp": 22500000, "aliases": "scoopy prestige, scoopy stylish keyless, scoopy 2021 2022 2023"}
                ]
            },
            {
                "name": "PCX",
                "category": "Matic",
                "cc": 160,
                "variants": [
                    {"name": "PCX 150 CBU", "start": 2012, "end": 2017, "msrp": 38000000, "aliases": "pcx cbu, pcx thailand, pcx vietnam"},
                    {"name": "PCX 150 Lokal (CBS / ABS)", "start": 2018, "end": 2021, "msrp": 29800000, "aliases": "pcx 150 lokal, pcx 150 cbs, pcx 150 abs 2018 2019 2020"},
                    {"name": "PCX 160 (CBS / ABS)", "start": 2021, "end": 2026, "msrp": 33500000, "aliases": "pcx 160, pcx 160 cbs, pcx 160 abs, all new pcx"}
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
                    {"name": "NMAX Turbo / Neo 155", "start": 2024, "end": 2026, "msrp": 37750000, "aliases": "nmax turbo, nmax neo, nmax turbo tech max"}
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
                "name": "Fazzio",
                "category": "Matic",
                "cc": 125,
                "variants": [
                    {"name": "Fazzio Hybrid-Connected (Neo / Lux)", "start": 2022, "end": 2026, "msrp": 22800000, "aliases": "fazzio, fazio, fazzio hybrid, fazzio lux, fazzio neo"}
                ]
            },
            {
                "name": "Grand Filano",
                "category": "Matic",
                "cc": 125,
                "variants": [
                    {"name": "Grand Filano Hybrid-Connected (Neo / Lux)", "start": 2023, "end": 2026, "msrp": 27500000, "aliases": "grand filano, filano hybrid, filano lux"}
                ]
            },
            {
                "name": "XSR 155",
                "category": "Sport",
                "cc": 155,
                "variants": [
                    {"name": "XSR 155 Heritage Sport", "start": 2019, "end": 2026, "msrp": 38000000, "aliases": "xsr 155, yamaha xsr, xsr retro"}
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
                "category": "Sport",
                "cc": 250,
                "variants": [
                    {"name": "Ninja 250 Karbu", "start": 2008, "end": 2012, "msrp": 45000000, "aliases": "ninja 250 karbu, ninja lama 2 silinder"},
                    {"name": "Ninja 250 FI (Generasi 1)", "start": 2013, "end": 2017, "msrp": 58000000, "aliases": "ninja 250 fi, ninja fi 2013 2014 2015"},
                    {"name": "Ninja 250 All New (Keyless / Smart Key)", "start": 2018, "end": 2025, "msrp": 67000000, "aliases": "all new ninja 250, ninja 250 keyless, ninja 250 abs se"}
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
                    {"name": "Liberty 150 i-Get ABS", "start": 2016, "end": 2023, "msrp": 38000000, "aliases": "liberty iget, liberty s 150, pagio liberty abs"}
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
                "category": "Matic",
                "cc": 300,
                "variants": [
                    {"name": "MP3 300 / 500 HPE Tiga Roda", "start": 2018, "end": 2026, "msrp": 330000000, "aliases": "piaggio mp3, pagio mp3, mp3 hpe, piaggio roda 3"}
                ]
            },
            {
                "name": "Beverly",
                "category": "Matic",
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
                    {"name": "Sprint 150 TFT / LED Facelift", "start": 2023, "end": 2026, "msrp": 57000000, "aliases": "sprint tft, new sprint 150 2024, sprint s tft"}
                ]
            },
            {
                "name": "Primavera",
                "category": "Matic",
                "cc": 150,
                "variants": [
                    {"name": "Primavera 150 3V ie", "start": 2014, "end": 2016, "msrp": 33000000, "aliases": "primavera 3v, vespa primavera lama, pagio primavera"},
                    {"name": "Primavera 150 i-Get (ABS / S)", "start": 2016, "end": 2026, "msrp": 50000000, "aliases": "primavera iget, primavera 150 abs, primavera s, pagio primavera iget"}
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
                "category": "Matic",
                "cc": 150,
                "variants": [
                    {"name": "GTS Super 150 3V / i-Get", "start": 2014, "end": 2022, "msrp": 67000000, "aliases": "vespa gts 150, gts super 150, gts iget, pagio gts"},
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
                "name": "GSX-R150",
                "category": "Sport",
                "cc": 150,
                "variants": [
                    {"name": "GSX-R150 (Keyless / Shuttered Key / ABS)", "start": 2017, "end": 2026, "msrp": 35000000, "aliases": "gsx r150, suzuki gsx r, gsx fairing, gsx keyless"}
                ]
            },
            {
                "name": "Burgman Street 125EX",
                "category": "Matic",
                "cc": 125,
                "variants": [
                    {"name": "Burgman Street 125EX", "start": 2023, "end": 2026, "msrp": 26000000, "aliases": "burgman 125, burgman street, burgman ex"}
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

        db.commit()
        print(f"✅ Seeding Sukses! Ditambahkan: {total_brands} Merk, {total_models} Model, {total_variants} Varian Motor.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_master_motor_database()
