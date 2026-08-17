"""
Unit tests for ProductSearchService matching rules, aliases, and filters.
"""

import unittest
from database.seed import seed_products
from services.product_search import ProductSearchService


class TestProductSearch(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        seed_products()

    def test_search_cotton_bollworm(self):
        results = ProductSearchService.search_products(crop="Cotton", problem="Bollworm")
        self.assertGreater(len(results), 0)
        product_names = [p["product_name"] for p in results]
        self.assertTrue(any("Coragen" in name or "Ampligo" in name for name in product_names))

    def test_search_marathi_aliases(self):
        # 'कापूस' (Cotton) + 'बोंडअळी' (Bollworm)
        results = ProductSearchService.search_products(crop="कापूस", problem="बोंडअळी")
        self.assertGreater(len(results), 0)
        product_names = [p["product_name"] for p in results]
        self.assertTrue(any("Coragen" in name or "Ampligo" in name for name in product_names))

    def test_search_chilli_thrips(self):
        results = ProductSearchService.search_products(crop="मिरची", problem="चुरडा मुरडा")
        self.assertGreater(len(results), 0)
        product_names = [p["product_name"] for p in results]
        self.assertTrue(any("Pegasus" in name or "Delegate" in name or "Confidor" in name for name in product_names))

    def test_search_organic_filter(self):
        results = ProductSearchService.search_products(organic_only=True)
        self.assertGreater(len(results), 0)
        for p in results:
            self.assertTrue(p["organic_certified"])

    def test_get_product_by_id(self):
        prod = ProductSearchService.get_product_by_id("PROD-COT-001")
        self.assertIsNotNone(prod)
        self.assertEqual(prod["product_id"], "PROD-COT-001")
        self.assertEqual(prod["brand_name"], "FMC")

    def test_check_stock_and_price(self):
        info = ProductSearchService.check_stock_and_price("PROD-COT-001")
        self.assertIsNotNone(info)
        self.assertEqual(info["price"], 780.0)
        self.assertTrue(info["in_stock"])


if __name__ == "__main__":
    unittest.main()
