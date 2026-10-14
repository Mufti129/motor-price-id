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

    # ------------------------------------------------------------------
    # Regresi untuk perbaikan prioritas pertama (audit data 2026-10)
    # ------------------------------------------------------------------
    def test_detector_closes_low_price_loophole(self):
        # Sebelumnya lolos sebagai Cash karena tanpa kata kunci DP dan tanpa MSRP
        res = ScamAndDPDetector.evaluate(price=1_500_000, title="Honda Revo 2015 mulus", description="")
        self.assertTrue(res["is_invalid"])
        self.assertEqual(res["code"], "PRICE_BELOW_MIN")
        is_dp, _ = ScamAndDPDetector.is_dp_or_credit_listing(1_500_000, "Honda Revo 2015 mulus", "")
        self.assertTrue(is_dp)

    def test_detector_absurd_and_above_msrp(self):
        res = ScamAndDPDetector.evaluate(price=81_234_546_787, title="Honda Beat 2020 hub 0812345", description="")
        self.assertEqual(res["code"], "PRICE_ABSURD")
        res2 = ScamAndDPDetector.evaluate(price=45_000_000, title="Honda Beat 2020", description="",
                                          expected_market_msrp=18_000_000, claimed_year=2020)
        self.assertEqual(res2["code"], "PRICE_ABOVE_MSRP")

    def test_detector_age_floor(self):
        # Unit usia 1 tahun dengan harga 30% MSRP -> di bawah batas retensi wajar
        res = ScamAndDPDetector.evaluate(price=9_000_000, title="Yamaha NMAX 2025", description="",
                                         expected_market_msrp=31_000_000, claimed_year=2025, current_year=2026)
        self.assertTrue(res["is_invalid"])
        # Unit usia 8 tahun dengan harga 55% MSRP -> valid
        res2 = ScamAndDPDetector.evaluate(price=17_000_000, title="Yamaha NMAX 2018", description="",
                                          expected_market_msrp=31_000_000, claimed_year=2018, current_year=2026)
        self.assertFalse(res2["is_invalid"])

    def test_provenance_classification(self):
        from pipeline.provenance import classify_origin
        self.assertEqual(classify_origin("gen_000123", "https://www.olx.co.id/item/x"), "SYNTHETIC")
        self.assertEqual(classify_origin("olx_exp_55", None), "SYNTHETIC")
        self.assertEqual(classify_origin("olx_912345678", "https://www.olx.co.id/motor-bekas_c200/q-honda-beat"), "SYNTHETIC")
        self.assertEqual(classify_origin("fb_1", "https://www.facebook.com/marketplace/item/123456789/"), "LIVE_SCRAPED")
        self.assertEqual(classify_origin("mm_1", "https://momotor.id/motor-bekas/honda/beat-2020-abc"), "LIVE_SCRAPED")

    def test_entity_gate_requires_model_mention(self):
        from pipeline.entity_matcher import EntityMatcher
        self.assertTrue(EntityMatcher.title_mentions_model("Honda Genio 2021 mulus", "Genio"))
        self.assertFalse(EntityMatcher.title_mentions_model("Honda Genio 2021 mulus", "EM1 e:"))
        self.assertFalse(EntityMatcher.title_mentions_model("Yamaha NMAX 155 2019", "WR 155R"))

    def test_ml_model_monotonic_depreciation(self):
        from analytics.ml_valuation_model import MLValuationModel
        m = MLValuationModel()
        if not m.is_trained_model:
            self.skipTest("Artefak model tidak tersedia")
        prices = [m.predict_valuation(18_500_000, y, engine_cc=110, brand="Honda", category="MATIC",
                                      current_year=2026)["predicted_fmv"] for y in range(2024, 2012, -1)]
        for newer, older in zip(prices, prices[1:]):
            self.assertGreaterEqual(newer + 1, older)
        curve = m.forecast_residual_value_curve(12_000_000, 2019, 110, sector="MATIC",
                                                msrp_new=18_500_000, brand="Honda", current_year=2026)
        self.assertEqual(len(curve), 5)
        vals = [pt["forecasted_price"] for pt in curve]
        for a, b in zip(vals, vals[1:]):
            self.assertGreaterEqual(a, b)
        self.assertTrue(all("method" in pt for pt in curve))


if __name__ == "__main__":
    unittest.main()
