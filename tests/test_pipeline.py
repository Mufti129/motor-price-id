import unittest
from pipeline.normalizer import ListingNormalizer
from pipeline.scam_detector import ScamAndDPDetector

class TestPipeline(unittest.TestCase):

    def test_price_parsing(self):
        self.assertEqual(ListingNormalizer.parse_price("18.5jt"), 18500000.0)
        self.assertEqual(ListingNormalizer.parse_price("Rp 14.500.000"), 14500000.0)
        self.assertEqual(ListingNormalizer.parse_price("19500k"), 19500000.0)
        self.assertEqual(ListingNormalizer.parse_price(21000000), 21000000.0)

    def test_year_extraction(self):
        self.assertEqual(ListingNormalizer.extract_year("Honda Beat CBS ISS 2021 Mulus"), 2021)
        self.assertEqual(ListingNormalizer.extract_year("Yamaha NMAX Non ABS th 2018 B DKI"), 2018)

    def test_tax_and_doc_extraction(self):
        tax_status, _ = ListingNormalizer.extract_tax_status("Vario 150 2019 pjk pjg kaleng 2028")
        self.assertEqual(tax_status, "Hidup / Panjang")

        tax_status2, years = ListingNormalizer.extract_tax_status("Aerox 2018 pjk off 2x plat dki")
        self.assertEqual(tax_status2, "Mati / Off")
        self.assertEqual(years, 2)

        has_bpkb, has_stnk = ListingNormalizer.extract_documents("Mio M3 stnk only batangan murah")
        self.assertFalse(has_bpkb)
        self.assertTrue(has_stnk)

    def test_scam_and_dp_detector(self):
        # Listing DP 1.5jt pada motor mahal
        is_dp, _ = ScamAndDPDetector.is_dp_or_credit_listing(
            price=1500000.0,
            title="Honda PCX 160 ABS 2023 DP Murah",
            description="Cukup DP 1.5jt angsuran 1.1jt x 35 bulan",
            expected_market_msrp=33500000.0
        )
        self.assertTrue(is_dp)

        # Listing cash valid
        is_dp2, _ = ScamAndDPDetector.is_dp_or_credit_listing(
            price=18500000.0,
            title="Honda Vario 150 Keyless 2019 Istimewa",
            description="Jual cash Rp 18.5jt nego tipis, surat komplit",
            expected_market_msrp=24900000.0
        )
        self.assertFalse(is_dp2)

    def test_piaggio_entity_matching(self):
        from models.database import SessionLocal, init_db
        from data.seed_master_motor import seed_master_motor_database
        from pipeline.entity_matcher import EntityMatcher

        seed_master_motor_database()
        db = SessionLocal()
        try:
            matcher = EntityMatcher(db)

            # Test Piaggio Medley dengan ejaan 'Pagio'
            var_id, score, name = matcher.match("Pagio Medley S 150 2021", 2021)
            self.assertIsNotNone(var_id)
            self.assertIn("Medley", name)

            # Test Piaggio Liberty
            var_id2, score2, name2 = matcher.match("Piaggio Liberty 150 i-Get ABS 2018", 2018)
            self.assertIsNotNone(var_id2)
            self.assertIn("Liberty", name2)

            # Test Vespa Sprint
            var_id3, score3, name3 = matcher.match("Vespa Sprint 150 iget abs 2020", 2020)
            self.assertIsNotNone(var_id3)
            self.assertIn("Sprint", name3)
        finally:
            db.close()

if __name__ == "__main__":
    unittest.main()
