"""
SQLAlchemy models for Product Catalogue, Orders, and Conversation Sessions.
Designed to be compatible with SQLite in local development and PostgreSQL in production.
"""

from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    Text,
    ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utc_now():
    return datetime.now(timezone.utc)


class Product(Base):
    __tablename__ = "products"

    product_id = Column(String(50), primary_key=True, index=True)
    product_name = Column(String(200), nullable=False, index=True)
    brand_name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False, index=True)
    crops = Column(Text, nullable=False)  # Comma-separated crop names
    target_problems = Column(Text, nullable=False)  # Comma-separated pests/diseases/issues
    active_ingredient = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    pack_size = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    mrp = Column(Float, nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    dosage = Column(String(255), nullable=False)
    application_method = Column(String(100), default="Foliar Spray")
    waiting_period_days = Column(Integer, default=0)
    organic_certified = Column(Boolean, default=False)
    status = Column(String(50), default="active")  # active, out_of_stock, discontinued
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    orders = relationship("Order", back_populates="product")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "brand_name": self.brand_name,
            "category": self.category,
            "crops": [c.strip() for c in self.crops.split(",") if c.strip()],
            "target_problems": [p.strip() for p in self.target_problems.split(",") if p.strip()],
            "active_ingredient": self.active_ingredient,
            "description": self.description,
            "pack_size": self.pack_size,
            "price": self.price,
            "mrp": self.mrp,
            "stock": self.stock,
            "in_stock": self.stock > 0 and self.status == "active",
            "dosage": self.dosage,
            "application_method": self.application_method,
            "waiting_period_days": self.waiting_period_days,
            "organic_certified": self.organic_certified,
            "status": self.status,
        }


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String(50), primary_key=True, index=True)
    farmer_name = Column(String(150), nullable=False)
    farmer_phone = Column(String(20), nullable=False)
    farmer_village = Column(String(150), nullable=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    pack_size = Column(String(50), nullable=False)
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String(50), default="Pending Confirmation")  # Pending Confirmation, Confirmed, Ready for Pickup, Completed, Cancelled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    product = relationship("Product", back_populates="orders")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "farmer_name": self.farmer_name,
            "farmer_phone": self.farmer_phone,
            "farmer_village": self.farmer_village,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "pack_size": self.pack_size,
            "unit_price": self.unit_price,
            "quantity": self.quantity,
            "total_price": self.total_price,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
        }


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    session_id = Column(String(100), primary_key=True, index=True)
    crop_context = Column(String(100), nullable=True)
    problem_context = Column(String(200), nullable=True)
    language_preference = Column(String(50), default="mr")  # mr, hi, en, hinglish
    created_at = Column(DateTime, default=utc_now)
    last_active_at = Column(DateTime, default=utc_now, onupdate=utc_now)
