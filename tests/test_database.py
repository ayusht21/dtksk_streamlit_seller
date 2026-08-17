"""
Unit tests for database models, connection, and seeding.
"""

import unittest
from database.database import init_db, get_db
from database.models import Product, Order
from database.seed import seed_products


class TestDatabase(unittest.TestCase):

    def setUp(self):
        init_db()
        seed_products()

    def test_products_seeded(self):
        with get_db() as db:
            count = db.query(Product).count()
            self.assertGreaterEqual(count, 20, "Should have at least 20 seeded products.")

    def test_product_attributes(self):
        with get_db() as db:
            coragen = db.query(Product).filter(Product.product_id == "PROD-COT-001").first()
            self.assertIsNotNone(coragen)
            self.assertIn("Chlorantraniliprole", coragen.active_ingredient)
            self.assertEqual(coragen.price, 780.0)
            self.assertEqual(coragen.pack_size, "60 ml")
            self.assertGreater(coragen.stock, 0)
            self.assertEqual(coragen.status, "active")

    def test_product_to_dict(self):
        with get_db() as db:
            prod = db.query(Product).first()
            d = prod.to_dict()
            self.assertIn("product_id", d)
            self.assertIn("product_name", d)
            self.assertIn("price", d)
            self.assertIn("in_stock", d)
            self.assertIsInstance(d["crops"], list)
            self.assertIsInstance(d["target_problems"], list)


if __name__ == "__main__":
    unittest.main()
