"""
Seed script to populate SQLite product database from sample_products.csv.
Can be executed directly: `python -m database.seed` or imported into app startup.
"""

import csv
import sys
from pathlib import Path
import config
from database.database import init_db, get_db
from database.models import Product


def seed_products(csv_path: Path = config.SAMPLE_CSV_PATH, force_reload: bool = False) -> int:
    """
    Reads products from CSV file and inserts them into the database.
    If products already exist and force_reload is False, returns existing count.
    """
    init_db()

    if not csv_path.exists():
        print(f"❌ Seed CSV file not found at: {csv_path}")
        return 0

    inserted_count = 0
    updated_count = 0

    with get_db() as db:
        existing_count = db.query(Product).count()
        if existing_count > 0 and not force_reload:
            print(f"ℹ️ Database already contains {existing_count} products. Skipping seed.")
            return existing_count

        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                product_id = row["product_id"].strip()
                existing_product = db.query(Product).filter(Product.product_id == product_id).first()

                organic_val = str(row.get("organic_certified", "False")).strip().lower() in ("true", "1", "yes")

                product_data = {
                    "product_id": product_id,
                    "product_name": row["product_name"].strip(),
                    "brand_name": row["brand_name"].strip(),
                    "category": row["category"].strip(),
                    "crops": row["crops"].strip(),
                    "target_problems": row["target_problems"].strip(),
                    "active_ingredient": row["active_ingredient"].strip(),
                    "description": row["description"].strip(),
                    "pack_size": row["pack_size"].strip(),
                    "price": float(row["price"]),
                    "mrp": float(row["mrp"]),
                    "stock": int(row["stock"]),
                    "dosage": row["dosage"].strip(),
                    "application_method": row.get("application_method", "Foliar Spray").strip(),
                    "waiting_period_days": int(row.get("waiting_period_days", 0)),
                    "organic_certified": organic_val,
                    "status": row.get("status", "active").strip(),
                }

                if existing_product:
                    for key, value in product_data.items():
                        setattr(existing_product, key, value)
                    updated_count += 1
                else:
                    new_product = Product(**product_data)
                    db.add(new_product)
                    inserted_count += 1

    total_count = inserted_count + updated_count
    print(f"✅ Seeding complete: {inserted_count} new products inserted, {updated_count} updated. Total active: {total_count}")
    return total_count


if __name__ == "__main__":
    force = "--force" in sys.argv or "-f" in sys.argv
    seed_products(force_reload=force)
