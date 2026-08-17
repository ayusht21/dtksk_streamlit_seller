"""
Unit tests for agent tools and function execution dispatcher.
"""

import unittest
from database.seed import seed_products
from agent.tools import (
    execute_tool,
    search_products,
    get_product_details,
    check_stock,
    get_current_price,
    create_order,
    OPENAI_TOOLS_SCHEMA,
)


class TestAgentTools(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        seed_products()

    def test_schema_validity(self):
        self.assertIsInstance(OPENAI_TOOLS_SCHEMA, list)
        self.assertEqual(len(OPENAI_TOOLS_SCHEMA), 5)
        names = [t["function"]["name"] for t in OPENAI_TOOLS_SCHEMA]
        self.assertIn("search_products", names)
        self.assertIn("get_product_details", names)
        self.assertIn("check_stock", names)
        self.assertIn("get_current_price", names)
        self.assertIn("create_order", names)

    def test_search_tool_execution(self):
        res = execute_tool("search_products", {"crop": "Soybean", "category": "Fungicide"})
        self.assertIn("products", res)
        self.assertGreater(res["count"], 0)

    def test_details_tool_execution(self):
        res = execute_tool("get_product_details", {"product_id": "PROD-FNG-001"})
        self.assertTrue(res.get("found"))
        self.assertEqual(res["product"]["product_name"], "Amistar Top Fungicide (अमस्टार टॉप)")

    def test_check_stock_tool_execution(self):
        res = execute_tool("check_stock", {"product_id": "PROD-COT-001"})
        self.assertTrue(res.get("found"))
        self.assertIn("stock_info", res)
        self.assertGreater(res["stock_info"]["stock"], 0)

    def test_create_order_tool_execution(self):
        res = execute_tool(
            "create_order",
            {
                "product_id": "PROD-COT-001",
                "quantity": 1,
                "farmer_name": "Ramesh Patil",
                "farmer_phone": "9822012345",
                "village": "Nandgaon",
            }
        )
        self.assertTrue(res.get("success"), f"Order creation failed: {res}")
        self.assertIn("order_id", res)
        self.assertTrue(res["order_id"].startswith("ORD-"))
        self.assertEqual(res["total_price"], 780.0)


if __name__ == "__main__":
    unittest.main()
