"""
Tools and Function Calling definitions for the Farmer AI Assistant.
Compatible with both OpenAI and Google Gemini tool execution schemas.
"""

from typing import Dict, Any, List, Optional
import json
from services.product_search import ProductSearchService
from services.order_service import OrderService

# ---------------------------------------------------------------------------
# Tool Implementations
# ---------------------------------------------------------------------------

def search_products(
    crop: Optional[str] = None,
    problem: Optional[str] = None,
    symptoms: Optional[str] = None,
    category: Optional[str] = None,
    query: Optional[str] = None,
    organic_only: Optional[bool] = None,
    in_stock_only: bool = True,
) -> Dict[str, Any]:
    """
    Search the Datta Krushi Seva Kendra catalogue for matching agricultural products.
    """
    results = ProductSearchService.search_products(
        crop=crop,
        problem=problem,
        symptoms=symptoms,
        category=category,
        query=query,
        organic_only=organic_only,
        in_stock_only=in_stock_only,
        limit=6,
    )
    return {
        "count": len(results),
        "products": results,
        "query_parameters": {
            "crop": crop,
            "problem": problem,
            "category": category,
            "organic_only": organic_only,
        }
    }


def get_product_details(product_id: str) -> Dict[str, Any]:
    """
    Fetch verified label specifications, active ingredient, dosage, and price for a specific product ID.
    """
    product = ProductSearchService.get_product_by_id(product_id)
    if not product:
        return {"found": False, "error": f"Product with ID '{product_id}' not found in catalogue."}
    return {"found": True, "product": product}


def check_stock(product_id: str) -> Dict[str, Any]:
    """
    Check current inventory stock count and availability for a product.
    """
    info = ProductSearchService.check_stock_and_price(product_id)
    if not info:
        return {"found": False, "error": f"Product '{product_id}' not found."}
    return {"found": True, "stock_info": info}


def get_current_price(product_id: str) -> Dict[str, Any]:
    """
    Get the verified selling price, MRP, and pack size of a product.
    """
    info = ProductSearchService.check_stock_and_price(product_id)
    if not info:
        return {"found": False, "error": f"Product '{product_id}' not found."}
    return {
        "found": True,
        "product_name": info["product_name"],
        "pack_size": info["pack_size"],
        "price": info["price"],
        "mrp": info["mrp"],
        "in_stock": info["in_stock"],
    }


def create_order(
    product_id: str,
    quantity: int = 1,
    farmer_name: str = "Valued Farmer",
    farmer_phone: str = "9970151397",
    village: Optional[str] = "Katol",
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Reserve and create an order for the farmer in the shop database.
    """
    return OrderService.create_order(
        product_id=product_id,
        quantity=quantity,
        farmer_name=farmer_name,
        farmer_phone=farmer_phone,
        farmer_village=village,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Tool Dispatcher
# ---------------------------------------------------------------------------

TOOL_FUNCTIONS = {
    "search_products": search_products,
    "get_product_details": get_product_details,
    "check_stock": check_stock,
    "get_current_price": get_current_price,
    "create_order": create_order,
}


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Executes the named tool with the provided dictionary of arguments."""
    if tool_name not in TOOL_FUNCTIONS:
        return {"error": f"Tool '{tool_name}' does not exist."}
    try:
        func = TOOL_FUNCTIONS[tool_name]
        return func(**arguments)
    except Exception as e:
        return {"error": f"Error executing tool '{tool_name}': {str(e)}"}


# ---------------------------------------------------------------------------
# OpenAI Tool Schemas
# ---------------------------------------------------------------------------

OPENAI_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search the shop product catalogue for agricultural inputs (insecticides, fungicides, tonics, fertilizers, herbicides, bio-pesticides) matching crop, pest, disease, or category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "crop": {
                        "type": "string",
                        "description": "Target crop name in English or Marathi/Hindi (e.g., 'Cotton', 'कापूस', 'Soybean', 'Chilli', 'Tomato', 'Wheat', 'Sugarcane').",
                    },
                    "problem": {
                        "type": "string",
                        "description": "Pest, disease, or agronomic problem (e.g., 'Bollworm', 'बोंडअळी', 'Thrips', 'Aphids', 'Rust', 'Blight', 'करपा', 'Flower drop').",
                    },
                    "symptoms": {
                        "type": "string",
                        "description": "Observed visual symptoms on the plant.",
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter: 'Insecticide', 'Fungicide', 'Herbicide', 'Bio-stimulant / Growth Promoter', 'Micronutrient / Fertilizer', 'Bio-pesticide'.",
                    },
                    "query": {
                        "type": "string",
                        "description": "Free text query or active ingredient search term.",
                    },
                    "organic_only": {
                        "type": "boolean",
                        "description": "Set to True if the farmer specifically requested organic or bio-products.",
                    },
                    "in_stock_only": {
                        "type": "boolean",
                        "description": "Default is True to recommend only available products.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_details",
            "description": "Retrieve verified technical details, active ingredients, dosages, and safety waiting periods for a specific product ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "Exact product ID (e.g., 'PROD-COT-001').",
                    },
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_stock",
            "description": "Check real-time stock count and availability status of a product.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "Product ID to check.",
                    },
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_price",
            "description": "Get current selling price and pack size for a product from the shop database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "Product ID to check.",
                    },
                },
                "required": ["product_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_order",
            "description": "Reserve or create a product purchase order for the farmer at Datta Krushi Seva Kendra.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The product ID being ordered.",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of packs to reserve (default 1).",
                    },
                    "farmer_name": {
                        "type": "string",
                        "description": "Name of the farmer.",
                    },
                    "farmer_phone": {
                        "type": "string",
                        "description": "Contact phone number of the farmer.",
                    },
                    "village": {
                        "type": "string",
                        "description": "Village or Taluka location of the farmer.",
                    },
                    "notes": {
                        "type": "string",
                        "description": "Optional notes or pickup instructions.",
                    },
                },
                "required": ["product_id", "farmer_name", "farmer_phone"],
            },
        },
    },
]
