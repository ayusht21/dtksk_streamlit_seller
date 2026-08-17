"""
Order management service for farmer reservations and purchase enquiries.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import config
from database.database import get_db
from database.models import Order, Product


class OrderService:
    """Service to handle customer orders and reservations at Datta Krushi Seva Kendra."""

    @staticmethod
    def create_order(
        product_id: str,
        quantity: int,
        farmer_name: str,
        farmer_phone: str,
        farmer_village: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates an order reservation in the database.
        Checks stock availability and calculates total price.
        """
        if quantity <= 0:
            return {"success": False, "message": "Quantity must be at least 1 unit."}

        clean_product_id = product_id.strip()

        with get_db() as db:
            product = db.query(Product).filter(Product.product_id == clean_product_id).first()
            if not product:
                return {"success": False, "message": f"Product with ID '{product_id}' not found in catalogue."}

            if product.stock < quantity:
                return {
                    "success": False,
                    "message": f"Requested quantity ({quantity}) exceeds available stock ({product.stock} units) for {product.product_name}.",
                    "available_stock": product.stock,
                }

            # Generate human-friendly order ID
            short_id = uuid.uuid4().hex[:6].upper()
            order_id = f"ORD-{datetime.now(timezone.utc).strftime('%y%m%d')}-{short_id}"

            total_price = round(product.price * quantity, 2)

            order = Order(
                order_id=order_id,
                farmer_name=farmer_name.strip(),
                farmer_phone=farmer_phone.strip(),
                farmer_village=farmer_village.strip() if farmer_village else "",
                product_id=product.product_id,
                product_name=product.product_name,
                pack_size=product.pack_size,
                unit_price=product.price,
                quantity=quantity,
                total_price=total_price,
                status="Confirmed Reservation",
                notes=notes.strip() if notes else "",
            )

            # Deduct stock
            product.stock = product.stock - quantity
            if product.stock == 0:
                product.status = "out_of_stock"

            db.add(order)
            db.flush()

            return {
                "success": True,
                "order_id": order_id,
                "product_name": product.product_name,
                "pack_size": product.pack_size,
                "quantity": quantity,
                "unit_price": product.price,
                "total_price": total_price,
                "farmer_name": farmer_name,
                "farmer_phone": farmer_phone,
                "farmer_village": farmer_village or "Katol",
                "status": "Confirmed Reservation",
                "pickup_location": f"{config.SHOP_NAME}, {config.SHOP_LOCATION}",
                "message": f"✅ ऑर्डर नोंदणी यशस्वी झाली! ऑर्डर क्रमांक: {order_id}. एकूण रक्कम: ₹{total_price}."
            }

    @staticmethod
    def list_orders(limit: int = 50) -> List[Dict[str, Any]]:
        """Lists recent customer orders."""
        with get_db() as db:
            orders = db.query(Order).order_by(Order.created_at.desc()).limit(limit).all()
            return [o.to_dict() for o in orders]

    @staticmethod
    def get_order_by_id(order_id: str) -> Optional[Dict[str, Any]]:
        """Fetches details of a specific order."""
        with get_db() as db:
            order = db.query(Order).filter(Order.order_id == order_id.strip()).first()
            return order.to_dict() if order else None

    @staticmethod
    def update_order_status(order_id: str, new_status: str) -> bool:
        """Updates the status of an existing order."""
        with get_db() as db:
            order = db.query(Order).filter(Order.order_id == order_id.strip()).first()
            if order:
                order.status = new_status
                db.flush()
                return True
            return False
