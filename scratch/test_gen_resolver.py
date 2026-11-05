import re
import pandas as pd
from typing import Tuple

def resolve_chassis_and_generation(row: pd.Series, model_name: str) -> Tuple[str, str]:
    code = str(row.get("Kode Tipe", "") or "").upper().strip()
    brand = str(row.get("Merek", "") or "").upper().strip()
    category = str(row.get("Kategori Jenis", "") or "").lower().strip()
    clean_code = re.sub(r"[^A-Z0-9]", "", code)
    
    try:
        year = int(row.get("Tahun", 2022))
    except (ValueError, TypeError):
        year = 2022
        
    m_upper = model_name.upper().strip()

    # Tentukan apakah ini Sepeda Motor
    is_motorcycle = False
    if "motor" in category:
        is_motorcycle = True
    elif brand in ["YAMAHA", "KAWASAKI", "VESPA", "PIAGGIO", "HARLEY DAV", "TRIUMPH", "DUCATI", "KTM", "BENELLI", "ROYAL ENFIELD", "VIAR"]:
        is_motorcycle = True

    # =========================================================================
    # 1. SEPEDA MOTOR (MOTORCYCLES)
    # =========================================================================
    if is_motorcycle:
        # --- HONDA MOTOR ---
        if "HONDA" in brand:
            # BEAT
            if "BEAT" in m_upper or any(clean_code.startswith(pfx) for pfx in ["H1B", "K1A", "NC110", "JF11", "JF21", "JF31", "JF41", "JF51", "JF61", "JF71", "JM"]):
                if year <= 2012 or "NC110" in clean_code:
                    return "NC110 / Karburator", "Beat Karburator (Generasi 1)"
                if year <= 2014 or "JF11" in clean_code or "JF21" in clean_code:
                    return "JF11 / PGM-FI Non-eSP", "Beat FI (Injeksi Gen 1)"
                if "POP" in code:
                    return "K61 / Pop eSP Ring 14", "Beat Pop eSP"
                if "STREET" in code:
                    if year <= 2019:
                        return "JF51 / Street eSP Ring 14", "Beat Street eSP (Generasi 1)"
                    elif year <= 2023:
                        return "H1B / Street eSAF Ring 14", "Beat Street eSAF (Generasi 2)"
                    else:
                        return "K1A / Street All New", "Beat Street All New (2024+)"
                if year <= 2019 or any(p in clean_code for p in ["JF31", "JF41", "JF51", "JF61", "JF71", "JM", "K44"]):
                    return "JF51 / K44 eSP ACG Starter", "Beat FI eSP (Generasi 2/3)"
                if year <= 2023 or clean_code.startswith("H1B"):
                    return "H1B / Frame eSAF", "Beat Deluxe / CBS (eSAF)"
                return "K1A / Smart Key eSAF", "Beat Smart Key (Gen 5 / Facelift 2024)"

            # VARIO
            if "VARIO" in m_upper or any(clean_code.startswith(pfx) for pfx in ["X1H", "K2S", "L1F", "L1K", "K60", "K59", "K2V", "NC11", "KF11"]):
                if "160" in m_upper or clean_code.startswith("X1H") or clean_code.startswith("K2S"):
                    return "X1H / 4-Katup eSP+ eSAF", "Vario 160 eSP+ (CBS / ABS)"
                if "150" in m_upper or clean_code.startswith("K59"):
                    if year <= 2017:
                        return "K59 / eSP Dual Keen LED", "Vario 150 eSP (Generasi 1)"
                    return "K59 / Smart Key All New", "Vario 150 eSP (Keyless Generasi 2)"
                if "110" in m_upper or clean_code.startswith("NC11") or "NC11" in clean_code:
                    if year <= 2013:
                        return "NC11 / Karburator Pendingin Cair", "Vario 110 Karburator (Generasi 1)"
                    return "K46 / eSP LED 110", "Vario 110 FI eSP (LED)"
                if year <= 2014 or clean_code.startswith("KF11"):
                    return "KF11 / Techno PGM-FI", "Vario 125 Techno (Generasi 1)"
                if year <= 2017 or clean_code.startswith("L1F") or clean_code.startswith("K60"):
                    return "L1F / Dual Keen Eyes LED", "Vario 125 eSP (LED Generasi 1)"
                if year <= 2022 or clean_code.startswith("L1K") or clean_code.startswith("K2V"):
                    return "L1K / All New LED K2V", "Vario 125 All New eSP (Generasi 2)"
                return "L1K / New Smart Key USB", "Vario 125 New Smart Key (Facelift 2022+)"

            # SCOOPY
            if "SCOOPY" in m_upper or any(clean_code.startswith(pfx) for pfx in ["F1C", "K2F", "K93", "K16", "KF03"]):
                if year <= 2012 or "NC110" in clean_code:
                    return "NC110 / Karburator Ring 14", "Scoopy Karburator (Generasi 1)"
                if year <= 2016 or "K16" in clean_code or "JF41" in clean_code:
                    return "JF41 / PGM-FI Ring 14", "Scoopy FI eSP (Generasi 2)"
                if year <= 2020 or "K93" in clean_code:
                    return "K93 / Velg Ring 12 Donat", "Scoopy Stylish / Prestige Ring 12 (Gen 3)"
                if year <= 2023 or clean_code.startswith("F1C"):
                    return "F1C / Frame eSAF Keyless", "Scoopy Prestige / Stylish eSAF (Gen 4)"
                return "K2F / New Facelift 2024+", "Scoopy All New (Generasi 5 2024+)"

            # PCX
            if "PCX" in m_upper or any(clean_code.startswith(pfx) for pfx in ["V1J", "JK01", "K1Z", "K97", "KF18", "KF12"]):
                if "160" in m_upper or year >= 2021 or clean_code.startswith("V1J") or clean_code.startswith("JK"):
                    return "V1J / 4-Katup 160cc HSTC", "PCX 160 eSP+ (CBS / ABS Generasi 4)"
                if year >= 2018 or clean_code.startswith("K97"):
                    return "K97 / Double Disc Lokal", "PCX 150 Lokal (CBS / ABS Generasi 3)"
                return "KF12 / KF18 CBU Import", "PCX 150 CBU (Generasi 1/2)"

            # ADV
            if "ADV" in m_upper or any(clean_code.startswith(pfx) for pfx in ["N1N", "K0X", "K0W"]):
                if "160" in m_upper or year >= 2022 or clean_code.startswith("N1N") or clean_code.startswith("K0X"):
                    return "N1N / 4-Katup 160cc HSTC", "ADV 160 eSP+ (CBS / ABS)"
                return "K0W / 2-Katup 150cc", "ADV 150 (CBS / ABS)"

            # GENIO
            if "GENIO" in m_upper or clean_code.startswith("C1M"):
                if year >= 2022:
                    return "C1M / eSAF Ring 12", "Genio Facelift (Ring 12 Gen 2)"
                return "C1M / eSAF Ring 14", "Genio CBS / ISS (Generasi 1 Ring 14)"

            # STYLO 160
            if "STYLO" in m_upper or clean_code.startswith("ED1"):
                return "ED1 / Retro Modern 160cc eSP+", "Stylo 160 (CBS / ABS)"

            # CRF150L
            if "CRF" in m_upper or clean_code.startswith("T4G") or clean_code.startswith("K84"):
                return "T4G / Showa Inverted Fork", "CRF150L Dual Sport"

            # CB150R
            if "CB150R" in m_upper or clean_code.startswith("A5C") or clean_code.startswith("K15"):
                if year <= 2015:
                    return "K15 / Truss Frame Old", "CB150R StreetFire (Generasi 1)"
                if year <= 2020:
                    return "K15 / All New LED Sharp", "CB150R StreetFire (Generasi 2)"
                return "A5C / Inverted Fork USD Showa", "CB150R StreetFire All New (Gen 3)"

            # CBR150R
            if "CBR150" in m_upper or clean_code.startswith("P5E") or clean_code.startswith("K45"):
                if year <= 2014:
                    return "CS150 / CBU Thailand", "CBR150R CBU (Generasi 1)"
                if year <= 2016:
                    return "K45A / Dual Keen Lokal", "CBR150R Lokal (K45A Generasi 2)"
                if year <= 2020:
                    return "K45G / All New LED Sharp", "CBR150R Facelift (Generasi 3)"
                return "P5E / USD Showa SFF-BP", "CBR150R All New (Generasi 4)"

            # CBR250RR
            if "CBR250" in m_upper or clean_code.startswith("R5F") or clean_code.startswith("K64"):
                if year >= 2022 or clean_code.startswith("R5F"):
                    return "R5F / SFF-BP Quickshifter", "CBR250RR SP Quickshifter (Gen 2)"
                return "K64 / Throttle-by-Wire Twin", "CBR250RR Twin (Generasi 1)"

            # REVO
            if "REVO" in m_upper or clean_code.startswith("NF11") or clean_code.startswith("NF100"):
                if year <= 2009:
                    return "NF100 / Karburator 100cc", "Revo 100 Karbu (Generasi 1)"
                if year <= 2013:
                    return "NF110 / Absolute 110cc", "Revo Absolute 110 (Generasi 2)"
                return "NF11 / PGM-FI Fit/X", "Revo Fit / X FI (Generasi 3)"

            # SUPRA X 125
            if "SUPRA" in m_upper or clean_code.startswith("AFX") or clean_code.startswith("NF125"):
                if year <= 2013 or clean_code.startswith("NF125"):
                    return "NF125 / Batman Karbu/FI", "Supra X 125 Karbu / PGM-FI (Gen 1)"
                return "AFX / All New Helm-In/FI", "Supra X 125 FI (Generasi 2)"

            # ASTREA / LEGENDA / GRAND
            if any(k in m_upper for k in ["ASTREA", "GRAND", "LEGENDA", "PRIMA"]):
                return "C100 / OHC 100cc Legendaris", "Astrea Grand / Prima / Legenda"

        # --- YAMAHA MOTOR ---
        if "YAMAHA" in brand:
            # NMAX
            if "NMAX" in m_upper or any(clean_code.startswith(pfx) for pfx in ["B6H", "BLS", "2DP"]):
                if year <= 2019 or clean_code.startswith("2DP"):
                    return "2DP / VVA 155 Bodi Old", "NMAX 155 Old (Generasi 1 Non-ABS / ABS)"
                if year >= 2024 and (clean_code.startswith("BLS") or "TURBO" in code or "NEO" in code):
                    return "BLS / Y-CVT Turbo / Neo", "NMAX Turbo / Neo 155 (Generasi 3)"
                return "B6H / Y-Connect Sub-Tank", "All New NMAX 155 Connected (Gen 2)"

            # AEROX
            if "AEROX" in m_upper or any(clean_code.startswith(pfx) for pfx in ["BBP", "B65"]):
                if year <= 2019 or clean_code.startswith("B65"):
                    return "B65 / VVA 155 Dual Shock Old", "Aerox 155 VVA (Generasi 1)"
                return "BBP / Connected Y-Connect", "All New Aerox 155 Connected (Gen 2)"

            # FAZZIO
            if "FAZZIO" in m_upper or clean_code.startswith("BPA"):
                return "BPA / Blue Core Hybrid 125", "Fazzio Hybrid Neo / Lux"

            # GRAND FILANO
            if "FILANO" in m_upper or clean_code.startswith("B8R"):
                return "B8R / Classy Blue Core Hybrid", "Grand Filano Hybrid Neo / Lux"

            # MIO
            if "MIO" in m_upper or any(clean_code.startswith(pfx) for pfx in ["2PH", "54P", "5TL"]):
                if year <= 2011 or clean_code.startswith("5TL"):
                    return "5TL / Karburator Smile/Sporty", "Mio Sporty / Smile (Karburator Gen 1)"
                if year <= 2014 or clean_code.startswith("54P"):
                    return "54P / YMJET-FI", "Mio J / GT FI (Generasi 2)"
                return "2PH / Blue Core 125", "Mio M3 125 / Mio S (Generasi 3)"

            # VIXION
            if "VIXION" in m_upper or clean_code.startswith("BK8") or clean_code.startswith("3C1"):
                if year <= 2012 or clean_code.startswith("3C1"):
                    return "3C1 / Deltabox Lampu Bulat", "Vixion Generasi 1 (Old)"
                if year <= 2016:
                    return "1PA / New Vixion Lightning/Advance", "New Vixion Lightning / Advance (Gen 2)"
                return "BK8 / Assist & Slipper Clutch", "All New Vixion / Vixion-R 155 (Gen 3)"

            # XSR 155
            if "XSR" in m_upper or clean_code.startswith("B1V"):
                return "B1V / Deltabox VVA Heritage", "XSR 155 Sport Heritage"

            # WR 155 R
            if "WR" in m_upper or clean_code.startswith("B3M"):
                return "B3M / VVA 155 Dual Purpose", "WR 155 R Dual Sport"

            # RX-KING
            if "KING" in m_upper or "RX" in m_upper:
                return "3KA / 2-Tak 135cc Legendaris", "RX-King 135 (Cobra / Master / Peredam)"

            # F1ZR
            if "F1Z" in m_upper or "FORCE" in m_upper:
                return "4WH / 2-Tak Full Clutch", "F1ZR / Force 1 (2-Tak)"

        # --- KAWASAKI ---
        if "KAWASAKI" in brand:
            # KLX 150
            if "KLX" in m_upper or clean_code.startswith("LX150"):
                if year <= 2014 or "LX150A" in clean_code or "LX150C" in clean_code:
                    return "LX150 / Teleskopik Velg 16-19", "KLX 150 S / L (Generasi 1)"
                if year <= 2022 or "LX150E" in clean_code or "LX150F" in clean_code:
                    return "LX150 / USD Velg 18-21 BF", "KLX 150 BF / Extreme (Generasi 2)"
                return "LX150 / Digital Speedo LED", "KLX 150 All New (Generasi 3)"

            # W175
            if "W175" in m_upper or clean_code.startswith("BJ175"):
                return "BJ175 / Karburator Retro Classic", "W175 SE / Cafe / TR"

            # NINJA 250
            if "NINJA 250" in m_upper or clean_code.startswith("EX250"):
                if year <= 2012:
                    return "EX250J / Karburator 2-Silinder", "Ninja 250 Karburator (Generasi 1)"
                if year <= 2017:
                    return "EX250L / FI Injeksi 2-Silinder", "Ninja 250 FI (Generasi 2)"
                return "EX250P / All New Assist & Slipper", "Ninja 250 All New FI (Generasi 3)"

            # NINJA 150
            if "NINJA 150" in m_upper or clean_code.startswith("KR150"):
                return "KR150 / 2-Tak Super KIPS", "Ninja 150 R / RR (2-Tak)"

            # D-TRACKER
            if "TRACKER" in m_upper:
                return "LX150 / USD Supermoto 17-Inch", "D-Tracker 150 (Generasi 1/2)"

        # --- SUZUKI MOTOR ---
        if "SUZUKI" in brand:
            # SATRIA
            if "SATRIA" in m_upper or clean_code.startswith("FU150"):
                if year <= 2015 or "CKD" in code or "CBU" in code:
                    return "FU150 / DOHC Karburator Oil Cooled", "Satria F150 Karburator (Gen 1/2)"
                return "FU150 / DOHC Liquid Cooled FI", "Satria F150 All New FI (Generasi 3)"

            # GSX 150
            if "GSX" in m_upper:
                return "GSX150 / DOHC 150cc Keyless", "GSX-R150 / GSX-S150"

            # SMASH / SHOGUN
            if "SMASH" in m_upper or "SHOGUN" in m_upper:
                if year <= 2010:
                    return "FD110 / FD125 Karburator", f"{model_name} Karburator"
                return "FL125 / Injeksi Euro 3", f"{model_name} FI"

        # --- VESPA / PIAGGIO ---
        if "VESPA" in brand or "PIAGGIO" in brand:
            if "SPRINT" in m_upper or "PRIMAVERA" in m_upper:
                if year <= 2015:
                    return "3V / 3-Valves LEM Engine", f"{model_name} 3V (Generasi 1)"
                return "i-Get / ABS Euro 4/5", f"{model_name} i-Get ABS"
            if "GTS" in m_upper:
                if year >= 2021:
                    return "HPE / High Performance Engine Keyless", "GTS Super Sport / 300 HPE"
                return "i-Get / 4-Valves Liquid Cooled", "GTS Super 150 i-Get"
            if "LX" in m_upper or "S 125" in m_upper:
                return "i-Get / 125cc Compact Body", f"{model_name} i-Get"

        # Generic Motorcycle Fallback
        return f"{code[:8]} / Sasis Motor Standar", f"{model_name} (Reguler / Standar)"

    # =========================================================================
    # 2. MOBIL & KENDARAAN KOMERSIAL (CARS & TRUCKS)
    # =========================================================================
    # --- TOYOTA ---
    if "TOYOTA" in brand:
        # AVANZA / VELOZ
        if "AVANZA" in m_upper or "VELOZ" in m_upper or clean_code.startswith("W100") or clean_code.startswith("W101"):
            if "VELOZ" in m_upper or clean_code.startswith("W101"):
                return "W101 / DNGA FWD TSS", "All New Veloz Generasi 3 (W101)"
            if year <= 2011 or clean_code.startswith("F601"):
                return "F601 / RWD Non-Dual VVT-i", "Avanza Generasi 1 (F601)"
            if year <= 2021 or clean_code.startswith("F650"):
                return "F650 / RWD Dual VVT-i", "Avanza Generasi 2 (Grand New F650)"
            return "W100 / DNGA FWD", "All New Avanza Generasi 3 (W100 FWD)"

        # KIJANG INNOVA / ZENIX
        if "INNOVA" in m_upper or any(clean_code.startswith(pfx) for pfx in ["MAGA", "MAGH", "MAGE"]):
            if "ZENIX" in m_upper or clean_code.startswith("MAGA") or clean_code.startswith("MAGH") or year >= 2023:
                if clean_code.startswith("MAGH") or "HYBRID" in code or "HV" in code:
                    return "MAGH / TNGA-C M20A Hybrid", "Innova Zenix Hybrid (Gen 3 HEV)"
                return "MAGA / TNGA-C M20A Bensin", "Innova Zenix Gasoline (Gen 3)"
            if year <= 2015:
                return "AN40 / IMV Ladder Frame Gen 1", "Kijang Innova Generasi 1 (AN40)"
            return "AN140 / 2GD Diesel & 1TR Bensin", "Innova Reborn Generasi 2 (AN140)"

        # RAIZE
        if "RAIZE" in m_upper or clean_code.startswith("A250") or clean_code.startswith("A251"):
            if clean_code.startswith("A250") or "1.0" in code:
                return "A250 / 1.0 Turbo 1KR-VET DNGA", "Raize 1.0T (DNGA-A)"
            return "A251 / 1.2 WA-VE 3-Silinder", "Raize 1.2 G (DNGA-A)"

        # AGYA
        if "AGYA" in m_upper or clean_code.startswith("A351") or clean_code.startswith("B100"):
            if year <= 2022 or clean_code.startswith("B100"):
                return "B100 / 1KR & 3NR Gen 1", "Agya Generasi 1 (B100)"
            return "A351 / DNGA WA-VE 1.2L", "All New Agya Gen 2 (DNGA)"

        # CALYA
        if "CALYA" in m_upper or clean_code.startswith("B401"):
            return "B401 / 3NR-VE MPV LCGC", "Calya 1.2 G / E LCGC"

        # FORTUNER
        if "FORTUNER" in m_upper:
            if year <= 2015:
                return "AN50 / IMV Ladder Frame Gen 1", "Fortuner Generasi 1 (AN50)"
            return "AN160 / 2GD-FTV & 1GD 2.8L", "All New Fortuner VRZ / GR Sport (Gen 2)"

        # RUSH
        if "RUSH" in m_upper or clean_code.startswith("F800"):
            if year <= 2017:
                return "F700 / RWD Konde Belakang", "Rush Generasi 1 (F700 Konde)"
            return "F800 / All New Non-Konde RWD", "All New Rush Generasi 2 (F800)"

        # DYNA
        if "DYNA" in m_upper or clean_code.startswith("DY") or clean_code.startswith("WU"):
            if year <= 2021:
                return "WU300 / W04D Euro 2", "Toyota Dyna Euro 2"
            return "XZU / N04C Common Rail Euro 4", "Toyota Dyna Euro 4"

        # YARIS
        if "YARIS" in m_upper:
            if "CROSS" in m_upper:
                return "D03B / DNGA-B Platform", "Yaris Cross (Bensin / Hybrid)"
            if year <= 2013:
                return "NCP91 / Bapao Gen 1", "Yaris Bapao (Generasi 1)"
            return "NSP151 / Lele & Joker Gen 2/3", "Yaris Generasi 2/3 (Lele/Joker)"

    # --- DAIHATSU ---
    if "DAIHATSU" in brand:
        # XENIA
        if "XENIA" in m_upper or clean_code.startswith("W100") or clean_code.startswith("F650"):
            if year <= 2011 or clean_code.startswith("F601"):
                return "F601 / RWD Non-Dual VVT-i", "Xenia Generasi 1 (F601)"
            if year <= 2021 or clean_code.startswith("F650"):
                return "F650 / RWD Dual VVT-i", "Xenia Generasi 2 (Great New F650)"
            return "W100 / DNGA FWD", "All New Xenia Generasi 3 (W100 FWD)"

        # TERIOS
        if "TERIOS" in m_upper or clean_code.startswith("F800") or clean_code.startswith("TER"):
            if year <= 2017:
                return "F700 / RWD Konde Belakang", "Terios Generasi 1 (F700 Konde)"
            return "F800 / All New Non-Konde RWD", "All New Terios Generasi 2 (F800)"

        # ROCKY
        if "ROCKY" in m_upper or clean_code.startswith("A250") or clean_code.startswith("A251"):
            if clean_code.startswith("A250") or "1.0" in code:
                return "A250 / 1.0 Turbo 1KR-VET DNGA", "Rocky 1.0T (DNGA-A)"
            return "A251 / 1.2 WA-VE 3-Silinder", "Rocky 1.2 X / R (DNGA-A)"

        # AYLA
        if "AYLA" in m_upper or clean_code.startswith("A350") or clean_code.startswith("B100"):
            if year <= 2022 or clean_code.startswith("B100"):
                return "B100 / 1KR & 3NR Gen 1", "Ayla Generasi 1 (B100)"
            return "A350 / DNGA WA-VE 1.2L", "All New Ayla Gen 2 (DNGA)"

        # SIGRA
        if "SIGRA" in m_upper or clean_code.startswith("B400"):
            return "B400 / 1KR & 3NR MPV LCGC", "Sigra 1.0 / 1.2 LCGC"

        # GRAN MAX
        if "GRAN MAX" in m_upper or clean_code.startswith("S401") or clean_code.startswith("S402"):
            return "S401 / S402 (K3-DE / 2NR-VE)", "Gran Max Pick Up / Blind Van"

        # TARUNA
        if "TARUNA" in m_upper:
            return "F500 / HD-C 1.6 & 1.5 EFI", "Taruna Generasi 1 (OXX / FX)"

        # TAFT / HILINE / FEROZA
        if any(k in m_upper for k in ["TAFT", "HILINE", "FEROZA"]):
            return "F70 / DL42 Diesel 4x4", "Taft / Hiline (Generasi 2/3)"

        # DELTA
        if "DELTA" in m_upper or clean_code.startswith("V82") or clean_code.startswith("V83"):
            return "V83 / 14B Direct Injection", "Delta Truck 4-Roda"

    # --- MITSUBISHI ---
    if "MITSUBISHI" in brand:
        # CANTER
        if "CANTER" in m_upper or "COLT DIESEL" in m_upper or clean_code.startswith("FE"):
            if year <= 2021:
                return "FE Series / 4D34-Turbo Euro 2", "Canter Colt Diesel (Euro 2)"
            return "FE Series / 4V21 Common Rail Euro 4", "Canter FE Series Common Rail (Euro 4)"

        # FUSO FIGHTER
        if "FIGHTER" in m_upper or "FUSO" in m_upper or clean_code.startswith("FM") or clean_code.startswith("FN"):
            if year <= 2021:
                return "FM/FN Series / 6D16 Euro 2", "Fuso Fighter (Euro 2)"
            return "FM/FN Series / 6M60 Common Rail Euro 4", "Fuso Fighter (Euro 4)"

        # PAJERO SPORT
        if "PAJERO SPORT" in m_upper or clean_code.startswith("PAJSPO"):
            if year <= 2015:
                return "KG4W / 4D56 DI-D VGT", "Pajero Sport Generasi 2 (Dakar/Exceed)"
            return "KS1W / 4N15 MIVEC 8-Speed", "All New Pajero Sport Dakar (Gen 3)"

        # XPANDER
        if "XPANDER" in m_upper:
            if year <= 2021:
                return "NC / 4A91 4-Speed AT", "Xpander Generasi 1 (Pre-Facelift)"
            return "NC / 4A91 CVT Facelift", "New Xpander / Cross CVT (Facelift)"

        # L300
        if "L300" in m_upper or clean_code.startswith("L03"):
            if year <= 2021 or clean_code.startswith("L03"):
                return "L039 / 4D56 Legendaris Euro 2", "Colt L300 Diesel (Euro 2)"
            return "L300 / 4N14 Common Rail Euro 4", "New Colt L300 Euro 4"

        # T120SS
        if "T120" in m_upper:
            return "T120SS / 4G17 Karbu & Injeksi", "Colt T120SS Pick Up"

        # MIRAGE
        if "MIRAGE" in m_upper:
            return "A03A / 3A92 1.2L DOHC MIVEC", "Mirage (Generasi 6)"

    # --- HONDA MOBIL ---
    if "HONDA" in brand and not is_motorcycle:
        # BRIO
        if "BRIO" in m_upper or clean_code.startswith("DD1") or clean_code.startswith("DD2"):
            if year <= 2018 or clean_code.startswith("DD1"):
                return "DD1 / Kaca Belakang Penuh", "Brio Generasi 1 (DD1 Kaca Penuh)"
            return "DD2 / All New Extended Tailgate", "All New Brio RS / Satya (Gen 2)"

        # HR-V
        if "HR-V" in m_upper or clean_code.startswith("RV3") or clean_code.startswith("RU1"):
            if year <= 2021 or clean_code.startswith("RU1"):
                return "RU1 / Solid Wing Face Gen 2", "HR-V Generasi 2 (RU1 / RU5)"
            return "RV3 / All New Fastback Gen 3", "All New HR-V SE / RS Turbo (Gen 3)"

        # CR-V
        if "CR-V" in m_upper or any(clean_code.startswith(pfx) for pfx in ["RW1", "CY2", "RM", "RE"]):
            if year <= 2012:
                return "RE / Kura-Kura Gen 3", "CR-V Generasi 3 (Kura-Kura)"
            if year <= 2016:
                return "RM / Gen 4 Facelift", "CR-V Generasi 4 (RM)"
            if year <= 2022:
                return "RW1 / 1.5L Turbo Gen 5", "CR-V Turbo Generasi 5 (RW1)"
            return "CY2 / All New e:HEV RS Gen 6", "All New CR-V Turbo / RS Hybrid (Gen 6)"

        # CIVIC
        if "CIVIC" in m_upper or clean_code.startswith("FE1") or clean_code.startswith("FC1"):
            if year <= 2011:
                return "FD1 / FD2 Batman Gen 8", "Civic FD (Generasi 8)"
            if year <= 2015:
                return "FB2 / R18 & R20 Gen 9", "Civic FB (Generasi 9)"
            if year <= 2021:
                return "FC1 / 1.5L Turbo Fastback Gen 10", "Civic Turbo FC (Generasi 10)"
            return "FE1 / 1.5L VTEC Turbo RS Gen 11", "All New Civic RS (Generasi 11 FE1)"

        # JAZZ
        if "JAZZ" in m_upper:
            if year <= 2008:
                return "GD3 / i-DSI & VTEC Gen 1", "Jazz GD3 (Generasi 1)"
            if year <= 2014 or "GE8" in code:
                return "GE8 / L15A i-VTEC Gen 2", "Jazz GE8 (Generasi 2)"
            return "GK5 / All New Sporty Gen 3", "Jazz GK5 (Generasi 3)"

    # --- ISUZU ---
    if "ISUZU" in brand:
        # PANTHER
        if "PANTHER" in m_upper or clean_code.startswith("TBR"):
            if year <= 2000 or clean_code.startswith("TBR52"):
                return "TBR52 / 2.3L & 2.5L Direct Injection", "Panther Generasi 1/2 (Kotak)"
            return "TBR54 / 2.5L Turbo Touring", "Panther Kapsul / Grand Touring (Gen 3)"

        # ELF
        if "ELF" in m_upper or any(clean_code.startswith(pfx) for pfx in ["NHR", "NKR", "NLR", "NMR"]):
            if year <= 2021:
                return "NKR/NHR / 4JB1 & 4HG1 Euro 2", "Isuzu Elf (Euro 2)"
            return "NLR/NMR / 4JJ1 Common Rail Euro 4", "Isuzu Elf (Euro 4)"

        # GIGA
        if "GIGA" in m_upper or any(clean_code.startswith(pfx) for pfx in ["FRR", "FTR", "FVR", "FVM", "FVZ"]):
            return "FRR/FVR / 6HK1-TCS Heavy Duty", "Isuzu Giga Series"

        # D-MAX
        if "D-MAX" in m_upper or clean_code.startswith("TFS"):
            return "TFS / 4JJ1 & RZ4E 4x4", "Isuzu D-Max 4x4"

    # --- HINO ---
    if "HINO" in brand:
        # DUTRO
        if "DUTRO" in m_upper or clean_code.startswith("WU") or clean_code.startswith("XZU"):
            if year <= 2021 or clean_code.startswith("WU"):
                return "WU300 / W04D Euro 2", "Hino Dutro Euro 2"
            return "XZU / N04C Common Rail Euro 4", "Hino Dutro Euro 4 (Hino 300)"

        # RANGER
        if "RANGER" in m_upper or any(clean_code.startswith(pfx) for pfx in ["FG", "FL", "FM"]):
            if year <= 2021:
                return "FG/FL/FM / J08E Euro 2", "Hino Ranger 500 (Euro 2)"
            return "FG/FL/FM / Common Rail Euro 4", "Hino Ranger 500 (Euro 4)"

        # BUS
        if "BUS" in m_upper or any(clean_code.startswith(pfx) for pfx in ["RK", "RN", "AK"]):
            return "RK8/RN8 / Chasis Bus Belakang", "Hino Bus Chassis (RK / RN / AK)"

    # --- SUZUKI MOBIL ---
    if "SUZUKI" in brand and not is_motorcycle:
        # ERTIGA
        if "ERTIGA" in m_upper:
            if year <= 2017:
                return "ZE81 / K14B Gen 1", "Ertiga Generasi 1 (K14B)"
            if year >= 2022 and ("HYBRID" in code or "SMART" in code):
                return "NC22 / Smart Hybrid K15B", "All New Ertiga Smart Hybrid"
            return "NC22 / K15B All New Gen 2", "All New Ertiga Generasi 2 (K15B)"

        # CARRY FUTURA
        if "CARRY" in m_upper or "FUTURA" in m_upper or clean_code.startswith("ST150") or clean_code.startswith("ST100"):
            if year <= 2018 or clean_code.startswith("ST150"):
                return "ST150 / G15A RWD Futura", "Carry Futura 1.5 (Euro 2)"
            return "DC61 / K15B-C New Carry", "New Carry Pick Up (Rajanya Pick Up)"

        # JIMNY / KATANA
        if "JIMNY" in m_upper or "KATANA" in m_upper or clean_code.startswith("SJ410"):
            if year <= 2005:
                return "SJ410 / F10A 4x2 Katana", "Suzuki Katana / Jimny Lokal"
            return "JB74 / K15B 4x4 All New", "Jimny All New (JB74 3-Pintu / 5-Pintu)"

    # --- HYUNDAI ---
    if "HYUNDAI" in brand:
        if "SANTA FE" in m_upper:
            if year <= 2012:
                return "CM / 2.2 CRDi Gen 2", "Santa Fe (Generasi 2 CM)"
            if year <= 2018:
                return "DM / 2.2 CRDi Gen 3", "Santa Fe (Generasi 3 DM)"
            if year <= 2023:
                return "TM / 2.2 CRDi Gen 4", "Santa Fe (Generasi 4 TM)"
            return "MX5 / All New Boxy Gen 5", "All New Santa Fe (Generasi 5 MX5)"
        if "CRETA" in m_upper:
            return "SU2ID / Smartstream 1.5L", "Creta Prime / Style / Trend"
        if "STARGAZER" in m_upper:
            return "KS / Smartstream 1.5L IVT", "Stargazer / Stargazer X"
        if "IONIQ 5" in m_upper:
            return "NE / E-GMP 800V Ultra-Fast", "Ioniq 5 (EV)"

    # Generic Platform Fallback
    prefix_token = code.split()[0] if code else "Standar"
    return f"{prefix_token[:10]} / Platform {brand.title()}", f"{model_name} (Reguler / Standar)"

# Quick test
df = pd.read_csv('data/reports/njkb_enriched_with_commercial_names.csv')
sasis_res = []
gen_res = []
for _, row in df.iterrows():
    s, g = resolve_chassis_and_generation(row, row['Nama Tipe'])
    sasis_res.append(s)
    gen_res.append(g)

df['Kode Tipe / Ciri Sasis'] = sasis_res
df['Varian Generation'] = gen_res

print('Test completed successfully!')
print(f'Total rows processed: {len(df):,}')
print(f'Null in Ciri Sasis: {df["Kode Tipe / Ciri Sasis"].isna().sum()}')
print(f'Null in Varian Generation: {df["Varian Generation"].isna().sum()}')
print('\nSample Results:')
sample_cols = ['Kode Tipe', 'Merek', 'Tahun', 'Nama Tipe', 'Kode Tipe / Ciri Sasis', 'Varian Generation']
print(df[sample_cols].sample(15, random_state=42).to_string())
