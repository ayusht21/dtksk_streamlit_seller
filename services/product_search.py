"""
Product search service with structured filtering, keyword scoring,
and Marathi/Hindi agricultural alias normalization.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import or_, and_, func
from database.database import get_db
from database.models import Product

# Regional Crop Aliases (Marathi, Hindi, English)
CROP_ALIASES = {
    "कापूस": "Cotton",
    "कपाशी": "Cotton",
    "cotton": "Cotton",
    "सोयाबीन": "Soybean",
    "soybean": "Soybean",
    "soya": "Soybean",
    "ऊस": "Sugarcane",
    "ganna": "Sugarcane",
    "sugarcane": "Sugarcane",
    "मिरची": "Chilli",
    "mirchi": "Chilli",
    "chilli": "Chilli",
    "chili": "Chilli",
    "टोमॅटो": "Tomato",
    "tomato": "Tomato",
    "tamatar": "Tomato",
    "गहू": "Wheat",
    "gehu": "Wheat",
    "wheat": "Wheat",
    "कांदा": "Onion",
    "pyaz": "Onion",
    "onion": "Onion",
    "डाळिंब": "Pomegranate",
    "anar": "Pomegranate",
    "pomegranate": "Pomegranate",
    "हरभरा": "Gram",
    "चना": "Gram",
    "chickpea": "Gram",
    "gram": "Gram",
    "भात": "Rice",
    "धान": "Rice",
    "paddy": "Rice",
    "rice": "Rice",
    "तूर": "Pigeon Pea",
    "arhar": "Pigeon Pea",
    "pigeon pea": "Pigeon Pea",
    "संत्रा": "Citrus",
    "मोसंबी": "Citrus",
    "citrus": "Citrus",
    "orange": "Citrus",
}

# Regional Pest & Problem Aliases
PROBLEM_ALIASES = {
    "बोंडअळी": ["Bollworm", "Pink Bollworm", "Helicoverpa", "बोंडअळी"],
    "गुलाबी बोंडअळी": ["Pink Bollworm", "Bollworm", "बोंडअळी"],
    "bollworm": ["Bollworm", "Pink Bollworm"],
    "लष्करी अळी": ["Spodoptera", "Armyworm", "लष्करी अळी"],
    "spodoptera": ["Spodoptera", "Armyworm"],
    "मावा": ["Aphids", "मावा"],
    "aphid": ["Aphids", "मावा"],
    "aphids": ["Aphids", "मावा"],
    "तुडतुडे": ["Jassids", "Leafhopper", "तुडतुडे"],
    "jassids": ["Jassids", "तुडतुडे"],
    "पांढरी माशी": ["Whitefly", "पांढरी माशी"],
    "whitefly": ["Whitefly", "पांढरी माशी"],
    "फुलकिडे": ["Thrips", "फुलकिडे"],
    "thrips": ["Thrips", "फुलकिडे"],
    "चुरडा मुरडा": ["Thrips", "Mites", "चुरडा मुरडा"],
    "चुरडा": ["Thrips", "चुरडा मुरडा"],
    "कोळी": ["Mites", "लाल कोळी"],
    "mites": ["Mites", "लाल कोळी"],
    "करपा": ["Blight", "Leaf Spot", "Anthracnose", "करपा"],
    "blight": ["Blight", "Early Blight", "Late Blight", "करपा"],
    "तांबेरा": ["Rust", "तांबेरा"],
    "rust": ["Rust", "तांबेरा"],
    "भुरी": ["Powdery Mildew", "भुरी"],
    "powdery mildew": ["Powdery Mildew", "भुरी"],
    "मर": ["Wilt", "Root Rot", "मर रोग"],
    "मूळकुज": ["Root Rot", "Damping Off", "मूळकुज"],
    "wilt": ["Wilt", "मर रोग"],
    "फुलगळ": ["Flower drop", "फुलगळ", "फुलधारणा"],
    "flower drop": ["Flower drop", "फुलगळ", "फुलधारणा"],
    "फुटवे": ["Vegetative growth", "फुटवे वाढवणे"],
    "पिवळे पडणे": ["Yellowing", "Zinc deficiency", "Nitrogen", "Chlorosis", "पिवळेपणा"],
    "yellowing": ["Yellowing", "Zinc deficiency", "19:19:19", "पिवळेपणा"],
    "तण": ["Weeds", "Herbicide", "तण"],
    "weeds": ["Weeds", "Herbicide", "तण"],
    "गवत": ["Narrow leaf weeds", "Grass weeds", "तण"],
    "सेंद्रिय": ["Bio-pesticide", "Organic", "सेंद्रिय"],
    "organic": ["Bio-pesticide", "Organic", "सेंद्रिय"],
}


class ProductSearchService:
    """Service to query product catalogue with flexible filters and semantic heuristics."""

    @staticmethod
    def normalize_crop(crop_input: Optional[str]) -> Optional[str]:
        if not crop_input:
            return None
        cleaned = crop_input.strip().lower()
        for key, normalized in CROP_ALIASES.items():
            if key in cleaned:
                return normalized
        return crop_input.strip()

    @staticmethod
    def normalize_problem_terms(problem_input: Optional[str]) -> List[str]:
        if not problem_input:
            return []
        cleaned = problem_input.strip().lower()
        terms = [cleaned]
        for key, mapped_terms in PROBLEM_ALIASES.items():
            if key in cleaned:
                terms.extend(mapped_terms)
        return list(set(terms))

    @classmethod
    def search_products(
        cls,
        crop: Optional[str] = None,
        problem: Optional[str] = None,
        symptoms: Optional[str] = None,
        category: Optional[str] = None,
        query: Optional[str] = None,
        organic_only: Optional[bool] = None,
        in_stock_only: bool = True,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Executes structured search over the database.
        Returns a list of matching product dicts.
        """
        with get_db() as db:
            query_obj = db.query(Product)

            # In-stock filter
            if in_stock_only:
                query_obj = query_obj.filter(Product.stock > 0, Product.status == "active")

            # Organic filter
            if organic_only is True:
                query_obj = query_obj.filter(Product.organic_certified.is_(True))

            # Category filter
            if category:
                cat_clean = category.strip()
                query_obj = query_obj.filter(
                    Product.category.ilike(f"%{cat_clean}%")
                )

            # Crop filter
            normalized_crop = cls.normalize_crop(crop) if crop else None
            if normalized_crop and normalized_crop.lower() != "all":
                query_obj = query_obj.filter(
                    or_(
                        Product.crops.ilike(f"%{normalized_crop}%"),
                        Product.crops.ilike("%All Crops%"),
                        Product.crops.ilike(f"%{crop}%"),
                    )
                )

            # Problem / Symptoms filter
            problem_terms = []
            if problem:
                problem_terms.extend(cls.normalize_problem_terms(problem))
            if symptoms:
                problem_terms.extend(cls.normalize_problem_terms(symptoms))

            if problem_terms:
                problem_conditions = []
                for term in problem_terms:
                    problem_conditions.append(Product.target_problems.ilike(f"%{term}%"))
                    problem_conditions.append(Product.description.ilike(f"%{term}%"))
                    problem_conditions.append(Product.product_name.ilike(f"%{term}%"))
                    problem_conditions.append(Product.active_ingredient.ilike(f"%{term}%"))
                query_obj = query_obj.filter(or_(*problem_conditions))

            # General free-text query
            if query:
                q_clean = query.strip()
                query_terms = [q_clean] + cls.normalize_problem_terms(q_clean)
                text_conditions = []
                for t in query_terms:
                    text_conditions.extend([
                        Product.product_name.ilike(f"%{t}%"),
                        Product.brand_name.ilike(f"%{t}%"),
                        Product.active_ingredient.ilike(f"%{t}%"),
                        Product.target_problems.ilike(f"%{t}%"),
                        Product.description.ilike(f"%{t}%"),
                        Product.crops.ilike(f"%{t}%"),
                    ])
                query_obj = query_obj.filter(or_(*text_conditions))

            # Fetch results
            products = query_obj.limit(limit).all()

            # If strict multi-filter yielded no results, fallback to broader keyword search
            if not products and (crop or problem or query):
                fallback_terms = []
                if normalized_crop:
                    fallback_terms.append(normalized_crop)
                if problem_terms:
                    fallback_terms.extend(problem_terms[:3])
                if query:
                    fallback_terms.append(query)

                fallback_conditions = []
                for term in fallback_terms:
                    fallback_conditions.extend([
                        Product.target_problems.ilike(f"%{term}%"),
                        Product.product_name.ilike(f"%{term}%"),
                        Product.description.ilike(f"%{term}%"),
                    ])

                fallback_query = db.query(Product).filter(
                    Product.stock > 0 if in_stock_only else True,
                    or_(*fallback_conditions) if fallback_conditions else True,
                )
                if organic_only:
                    fallback_query = fallback_query.filter(Product.organic_certified.is_(True))
                products = fallback_query.limit(limit).all()

            return [p.to_dict() for p in products]

    @staticmethod
    def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
        """Fetches complete product record by ID."""
        with get_db() as db:
            product = db.query(Product).filter(Product.product_id == product_id.strip()).first()
            return product.to_dict() if product else None

    @staticmethod
    def check_stock_and_price(product_id: str) -> Optional[Dict[str, Any]]:
        """Quick check for stock, unit price, and pack size."""
        with get_db() as db:
            product = db.query(Product).filter(Product.product_id == product_id.strip()).first()
            if not product:
                return None
            return {
                "product_id": product.product_id,
                "product_name": product.product_name,
                "pack_size": product.pack_size,
                "price": product.price,
                "mrp": product.mrp,
                "stock": product.stock,
                "in_stock": product.stock > 0 and product.status == "active",
                "status": product.status,
            }

    @staticmethod
    def list_all_products(category: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Lists products for catalogue browsing or admin view."""
        with get_db() as db:
            q = db.query(Product)
            if category and category != "All":
                q = q.filter(Product.category == category)
            products = q.order_by(Product.category, Product.product_name).limit(limit).all()
            return [p.to_dict() for p in products]
