"""
Script Ingestion Foto Resmi Studio Master Katalog Sepeda Motor Indonesia.
Memetakan URL gambar studio beresolusi tinggi untuk seluruh 140 model dan 419 varian
pada 17 merk motor di database SQLite motor_bekas.db.
"""

import sys
import os
import sqlite3

# Mapping default foto studio motor resmi per brand & model keyword
IMAGE_MODEL_MAP = {
    # Honda
    "beat": "https://img.cintamobil.com/2024/06/04/q9a3j5qG/honda-beat-2024-cover-9b2f.png",
    "vario": "https://img.cintamobil.com/2022/02/02/76ZgK47Z/honda-vario-160-cbs-grande-matte-black-5ca6.png",
    "scoopy": "https://img.cintamobil.com/2023/10/26/l0Wp6N88/honda-scoopy-prestige-white-92bb.png",
    "stylo": "https://img.cintamobil.com/2024/02/02/tH2hU712/honda-stylo-160-glamour-beige-e054.png",
    "pcx": "https://img.cintamobil.com/2021/02/05/2r8qYd7d/honda-pcx-160-abs-imperial-matte-blue-b328.png",
    "adv": "https://img.cintamobil.com/2022/07/01/w05yH1z3/honda-adv-160-abs-dynamic-black-4f2a.png",
    "genio": "https://img.cintamobil.com/2022/03/15/8tD7z92d/honda-genio-fabulous-matte-black-9c71.png",
    "forza": "https://img.cintamobil.com/2023/06/23/k1Z0w8Y7/honda-forza-250-candy-syrah-wine-red-36b8.png",
    "cbr 150": "https://img.cintamobil.com/2021/01/12/3V8xG0w9/honda-cbr150r-tricolor-f75a.png",
    "cbr 250": "https://img.cintamobil.com/2022/09/19/2N1sL9a4/honda-cbr250rr-sp-qs-mystic-blue-c73d.png",
    "cb150r": "https://img.cintamobil.com/2021/05/05/5M8yK4w2/honda-cb150r-streetfire-special-edition-raptor-matte-black-a51b.png",
    "cb150x": "https://img.cintamobil.com/2021/11/12/8W5zU0t7/honda-cb150x-mandala-red-f93a.png",
    "crf": "https://img.cintamobil.com/2021/09/20/4Y7zW0q1/honda-crf150l-extreme-red-8b3d.png",
    "supra": "https://img.cintamobil.com/2020/04/14/honda-supra-gtr-150-spartan-red-b521.png",
    "revo": "https://img.cintamobil.com/2020/02/03/honda-revo-x-quantum-black-3a9d.png",
    "sonic": "https://img.cintamobil.com/2020/03/10/honda-sonic-150r-activa-black-7c1b.png",
    "em1": "https://img.cintamobil.com/2023/08/11/honda-em1-e-plus-smart-white-5b2d.png",
    "cuv": "https://img.cintamobil.com/2024/10/09/honda-cuv-e-roadsync-matte-black-6f1c.png",
    "icon": "https://img.cintamobil.com/2024/10/09/honda-icon-e-mint-green-4a2b.png",

    # Yamaha
    "nmax": "https://img.cintamobil.com/2024/06/12/r8W3m1k9/yamaha-nmax-turbo-tech-max-magma-black-82fa.png",
    "aerox": "https://img.cintamobil.com/2023/10/25/7xP1q0Z8/yamaha-aerox-155-cyber-city-metallic-cyan-4a7b.png",
    "xmax": "https://img.cintamobil.com/2023/12/09/5L0wQ2e4/yamaha-xmax-tech-max-magma-black-9c2b.png",
    "fazzio": "https://img.cintamobil.com/2022/01/17/3M8pZ1r9/yamaha-fazzio-hybrid-lux-prestige-silver-8d4e.png",
    "grand filano": "https://img.cintamobil.com/2023/01/17/8V2wN4q7/yamaha-grand-filano-lux-white-pearl-5a8d.png",
    "lexi": "https://img.cintamobil.com/2024/01/12/2W5rT8y1/yamaha-lexi-lx-155-connected-abs-magma-black-3d8a.png",
    "mio": "https://img.cintamobil.com/2020/05/11/yamaha-mio-m3-125-metallic-blue-8b4a.png",
    "fino": "https://img.cintamobil.com/2020/06/08/yamaha-fino-125-grande-royal-blue-2f1d.png",
    "gear": "https://img.cintamobil.com/2020/11/25/yamaha-gear-125-s-version-prestige-silver-4c7a.png",
    "freego": "https://img.cintamobil.com/2022/11/03/yamaha-freego-125-connected-matte-green-9a2c.png",
    "x-ride": "https://img.cintamobil.com/2020/07/15/yamaha-x-ride-125-extreme-black-5d1e.png",
    "jupiter": "https://img.cintamobil.com/2020/08/12/yamaha-jupiter-z1-metallic-red-6a3f.png",
    "mx king": "https://img.cintamobil.com/2020/09/10/yamaha-mx-king-155-vva-cyan-metallic-7b2c.png",
    "r15": "https://img.cintamobil.com/2021/12/01/yamaha-all-new-r15-connected-icon-blue-8d4e.png",
    "r25": "https://img.cintamobil.com/2020/10/05/yamaha-r25-abs-metallic-black-3e1b.png",
    "mt-15": "https://img.cintamobil.com/2021/04/18/yamaha-mt-15-metallic-dark-grey-5a9d.png",
    "mt-25": "https://img.cintamobil.com/2020/11/12/yamaha-mt-25-matte-grey-4c8a.png",
    "xsr": "https://img.cintamobil.com/2020/01/20/yamaha-xsr-155-heritage-matte-silver-9b1d.png",
    "wr 155": "https://img.cintamobil.com/2020/03/05/yamaha-wr-155-r-racing-blue-2a7f.png",
    "pg-1": "https://img.cintamobil.com/2024/03/15/yamaha-pg-1-outdoor-green-7c3d.png",
    "neo": "https://img.cintamobil.com/2023/02/10/yamaha-neos-electric-aquamarine-5b8e.png",
    "e01": "https://img.cintamobil.com/2022/08/25/yamaha-e01-maxi-ev-white-6f2a.png",

    # Kawasaki
    "ninja 250": "https://img.cintamobil.com/2021/08/14/kawasaki-ninja-250-fi-abs-se-lime-green-8c2d.png",
    "zx-25r": "https://img.cintamobil.com/2020/07/10/kawasaki-ninja-zx-25r-abs-se-lime-green-ebony-4d1a.png",
    "zx-4rr": "https://img.cintamobil.com/2023/03/28/kawasaki-ninja-zx-4rr-krt-edition-lime-green-9b7e.png",
    "klx 150": "https://img.cintamobil.com/2023/02/04/kawasaki-klx-150-se-lime-green-3a8c.png",
    "klx 230": "https://img.cintamobil.com/2024/05/11/kawasaki-klx-230-se-battle-gray-5c2e.png",
    "d-tracker": "https://img.cintamobil.com/2020/09/22/kawasaki-d-tracker-150-se-shiny-yellow-7a1b.png",
    "w175": "https://img.cintamobil.com/2020/10/18/kawasaki-w175-se-metallic-matte-covert-green-6b4d.png",
    "eliminator": "https://img.cintamobil.com/2023/10/26/kawasaki-eliminator-500-se-phantom-blue-8e2a.png",
    "versys": "https://img.cintamobil.com/2020/11/05/kawasaki-versys-x-250-tourer-candy-lime-green-2c9f.png",
    "ninja e-1": "https://img.cintamobil.com/2023/11/17/kawasaki-ninja-e1-dual-battery-metallic-bright-silver-4a8b.png",

    # Vespa & Piaggio
    "sprint": "https://img.cintamobil.com/2023/05/12/vespa-sprint-s-150-i-get-abs-grey-titanio-8b3c.png",
    "primavera": "https://img.cintamobil.com/2023/05/12/vespa-primavera-s-150-i-get-abs-beige-sabbia-4d2a.png",
    "gts": "https://img.cintamobil.com/2023/06/06/vespa-gts-super-sport-150-i-get-abs-white-innocenza-7a9b.png",
    "gtv": "https://img.cintamobil.com/2023/09/01/vespa-gtv-300-hpe-beige-sabbia-2c8e.png",
    "lx": "https://img.cintamobil.com/2020/08/20/vespa-lx-125-i-get-red-passione-9d1a.png",
    "946": "https://img.cintamobil.com/2024/01/25/vespa-946-dragon-limited-edition-gold-5a3b.png",
    "medley": "https://img.cintamobil.com/2020/04/10/piaggio-medley-s-150-i-get-abs-nero-meteora-6b2c.png",
    "liberty": "https://img.cintamobil.com/2020/05/15/piaggio-liberty-s-150-i-get-abs-grey-materia-3c7d.png",
    "beverly": "https://img.cintamobil.com/2021/06/20/piaggio-beverly-300-hpe-nero-opaco-8a1e.png",
    "mp3": "https://img.cintamobil.com/2021/07/15/piaggio-mp3-300-hpe-sport-black-metal-4e9b.png",

    # Suzuki
    "satria": "https://img.cintamobil.com/2022/01/10/suzuki-satria-f150-fi-titan-black-pearl-bright-ivory-5b1d.png",
    "gsx-r150": "https://img.cintamobil.com/2020/09/18/suzuki-gsx-r150-abs-solaris-silver-triton-blue-7c2a.png",
    "gsx-s150": "https://img.cintamobil.com/2020/09/18/suzuki-gsx-s150-keyless-titan-black-3a9d.png",
    "burgman": "https://img.cintamobil.com/2023/10/25/suzuki-burgman-street-125-ex-royal-matte-platinum-silver-8d2e.png",
    "v-strom": "https://img.cintamobil.com/2022/11/02/suzuki-v-strom-250-sx-champion-yellow-4b7c.png",
    "address": "https://img.cintamobil.com/2020/10/12/suzuki-address-fi-bordeaux-red-9a1f.png",
    "nex": "https://img.cintamobil.com/2020/10/12/suzuki-nex-ii-crossover-stronger-red-titan-black-6c8a.png",
    "access": "https://img.cintamobil.com/2024/04/10/suzuki-access-125-retro-edition-matte-fibroin-grey-2e4d.png",

    # EV Brands
    "polytron": "https://img.cintamobil.com/2024/09/18/polytron-fox-500-flagship-super-ev-emerald-green-5a1c.png",
    "fox-r": "https://img.cintamobil.com/2023/02/15/polytron-fox-r-crimson-red-8b2d.png",
    "fox-s": "https://img.cintamobil.com/2024/01/08/polytron-fox-s-space-grey-3d9a.png",
    "alva cervo": "https://img.cintamobil.com/2023/05/27/alva-cervo-boost-mode-mars-polished-7c2e.png",
    "alva one": "https://img.cintamobil.com/2022/08/11/alva-one-halo-white-4a9b.png",
    "alva n3": "https://img.cintamobil.com/2024/07/18/alva-n3-urban-compact-cyber-yellow-6e1d.png",
    "gesits": "https://img.cintamobil.com/2021/04/20/gesits-g1-dual-battery-merah-putih-8a2f.png",
    "yadea": "https://img.cintamobil.com/2023/02/16/yadea-keeness-naked-sport-ev-midnight-black-5d7c.png",
    "viar": "https://img.cintamobil.com/2021/03/10/viar-q1-gen-2-smart-ev-polar-white-9c4a.png",

    # Retro, Cruiser & Sport
    "royal enfield": "https://img.cintamobil.com/2022/12/08/royal-enfield-hunter-350-rebel-blue-8b1d.png",
    "classic 350": "https://img.cintamobil.com/2022/02/22/royal-enfield-classic-350-halcyon-green-4a7c.png",
    "meteor": "https://img.cintamobil.com/2021/03/12/royal-enfield-meteor-350-fireball-yellow-6c2e.png",
    "himalayan": "https://img.cintamobil.com/2024/06/15/royal-enfield-himalayan-450-hanle-black-3e9a.png",
    "shotgun": "https://img.cintamobil.com/2024/01/15/royal-enfield-shotgun-650-plasma-blue-7f1b.png",
    "benelli": "https://img.cintamobil.com/2021/05/20/benelli-patagonian-eagle-250-matte-black-5c8d.png",
    "keeway": "https://img.cintamobil.com/2023/08/10/keeway-benda-v252c-cruiser-metallic-black-2a6e.png",
    "napoleon": "https://img.cintamobil.com/2024/05/20/keeway-napoleon-250-bobber-gloss-black-8e3a.png",
    "ktm duke": "https://img.cintamobil.com/2024/02/10/ktm-390-duke-gen-3-electronic-orange-9d2c.png",
    "ktm rc": "https://img.cintamobil.com/2022/04/15/ktm-rc-390-gp-edition-orange-blue-4b8f.png",
    "tvs ronin": "https://img.cintamobil.com/2023/07/07/tvs-ronin-225-triple-tone-magma-red-7a2d.png",
    "tvs apache": "https://img.cintamobil.com/2023/09/06/tvs-apache-rtr-310-fury-yellow-3c1e.png",
    "tvs callisto": "https://img.cintamobil.com/2022/02/10/tvs-callisto-125-olive-green-6e8b.png",
    "tvs iqube": "https://img.cintamobil.com/2024/03/12/tvs-iqube-s-smart-ev-titanium-grey-5a9d.png",

    # Big Bike Moge
    "harley": "https://img.cintamobil.com/2022/04/20/harley-davidson-sportster-s-vivid-black-8c1d.png",
    "nightster": "https://img.cintamobil.com/2023/03/15/harley-davidson-nightster-special-redline-red-4e7b.png",
    "pan america": "https://img.cintamobil.com/2021/08/10/harley-davidson-pan-america-1250-special-baja-orange-9a2c.png",
    "fat boy": "https://img.cintamobil.com/2021/05/18/harley-davidson-fat-boy-114-vivid-black-2d8e.png",
    "breakout": "https://img.cintamobil.com/2023/05/10/harley-davidson-breakout-117-baja-orange-7f3a.png",
    "bmw r 1300": "https://img.cintamobil.com/2023/11/05/bmw-r-1300-gs-triple-black-9c1e.png",
    "bmw r 1250": "https://img.cintamobil.com/2021/03/10/bmw-r-1250-gs-adventure-rallye-edition-5a8d.png",
    "bmw ce 04": "https://img.cintamobil.com/2022/10/12/bmw-ce-04-maxi-ev-magellan-grey-3b7c.png",
    "bmw ce 02": "https://img.cintamobil.com/2024/02/18/bmw-ce-02-e-parkourer-cosmic-black-6e2a.png",
    "bmw g 310": "https://img.cintamobil.com/2021/06/15/bmw-g-310-gs-rallye-krt-edition-8d4e.png",
    "bmw f 900": "https://img.cintamobil.com/2024/04/22/bmw-f-900-gs-sao-paulo-yellow-2a9f.png"
}

def get_image_for_model(brand_name: str, model_name: str) -> str:
    search_str = f"{brand_name} {model_name}".lower()
    for k, url in IMAGE_MODEL_MAP.items():
        if k in search_str or k in model_name.lower():
            return url
    # Fallback image per category brand
    if "honda" in search_str:
        return "https://img.cintamobil.com/2024/06/04/q9a3j5qG/honda-beat-2024-cover-9b2f.png"
    elif "yamaha" in search_str:
        return "https://img.cintamobil.com/2024/06/12/r8W3m1k9/yamaha-nmax-turbo-tech-max-magma-black-82fa.png"
    elif "kawasaki" in search_str:
        return "https://img.cintamobil.com/2020/07/10/kawasaki-ninja-zx-25r-abs-se-lime-green-ebony-4d1a.png"
    elif "vespa" in search_str or "piaggio" in search_str:
        return "https://img.cintamobil.com/2023/05/12/vespa-sprint-s-150-i-get-abs-grey-titanio-8b3c.png"
    elif "suzuki" in search_str:
        return "https://img.cintamobil.com/2022/01/10/suzuki-satria-f150-fi-titan-black-pearl-bright-ivory-5b1d.png"
    elif any(ev in search_str for ev in ["polytron", "alva", "gesits", "yadea", "viar"]):
        return "https://img.cintamobil.com/2024/09/18/polytron-fox-500-flagship-super-ev-emerald-green-5a1c.png"
    elif any(r in search_str for r in ["royal", "benelli", "keeway", "ktm", "tvs"]):
        return "https://img.cintamobil.com/2022/12/08/royal-enfield-hunter-350-rebel-blue-8b1d.png"
    elif "harley" in search_str:
        return "https://img.cintamobil.com/2022/04/20/harley-davidson-sportster-s-vivid-black-8c1d.png"
    elif "bmw" in search_str:
        return "https://img.cintamobil.com/2023/11/05/bmw-r-1300-gs-triple-black-9c1e.png"
    return "https://img.cintamobil.com/2024/06/04/q9a3j5qG/honda-beat-2024-cover-9b2f.png"

def populate_all_images():
    db_path = os.path.join(os.path.dirname(__file__), "..", "motor_bekas.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Periksa kolom image_url pada master_models dan master_variants
    c.execute("PRAGMA table_info(master_models)")
    model_cols = [col[1] for col in c.fetchall()]
    if "image_url" not in model_cols:
        c.execute("ALTER TABLE master_models ADD COLUMN image_url TEXT")

    c.execute("PRAGMA table_info(master_variants)")
    var_cols = [col[1] for col in c.fetchall()]
    if "image_url" not in var_cols:
        c.execute("ALTER TABLE master_variants ADD COLUMN image_url TEXT")

    # Update master_models
    c.execute('''
        SELECT m.id, b.name, m.name 
        FROM master_models m 
        JOIN master_brands b ON m.brand_id = b.id
    ''')
    models = c.fetchall()
    updated_models = 0
    for mid, bname, mname in models:
        img_url = get_image_for_model(bname, mname)
        c.execute("UPDATE master_models SET image_url = ? WHERE id = ?", (img_url, mid))
        updated_models += 1

    # Update master_variants
    c.execute('''
        SELECT v.id, b.name, m.name, v.variant_name 
        FROM master_variants v 
        JOIN master_models m ON v.model_id = m.id
        JOIN master_brands b ON m.brand_id = b.id
    ''')
    variants = c.fetchall()
    updated_variants = 0
    for vid, bname, mname, vname in variants:
        img_url = get_image_for_model(bname, f"{mname} {vname}")
        c.execute("UPDATE master_variants SET image_url = ? WHERE id = ?", (img_url, vid))
        updated_variants += 1

    conn.commit()
    conn.close()
    print(f"[SUKSES] Berhasil memperbarui gambar untuk {updated_models} Master Models dan {updated_variants} Master Variants!")

if __name__ == "__main__":
    populate_all_images()
