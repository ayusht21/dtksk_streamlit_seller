"""
Farmer AI Support & Sales Assistant — Streamlit Application
Datta Krushi Seva Kendra (दत्त कृषी सेवा केंद्र, काटोल)
"""

import os
import streamlit as st
from PIL import Image
import io
import urllib.parse
from datetime import datetime

import config
from database.seed import seed_products
from database.database import init_db
from services.product_search import ProductSearchService
from services.order_service import OrderService
from agent.core_agent import CoreAgent, AgentResponse

# -----------------------------------------------------------------------------
# Streamlit Page Config & Custom Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Datta Krushi Seva Kendra | AI कृषी मित्र",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern, high-aesthetic agricultural UI
st.markdown(
    """
    <style>
    /* Main container and typography */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Header Banner */
    .shop-header {
        background: linear-gradient(135deg, #134e4a 0%, #065f46 50%, #047857 100%);
        color: white;
        padding: 22px 28px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(6, 95, 70, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .shop-title {
        font-size: 26px;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .shop-subtitle {
        font-size: 15px;
        color: #a7f3d0;
        margin-top: 6px;
        margin-bottom: 0;
        font-weight: 400;
    }
    
    .shop-badges {
        display: flex;
        gap: 10px;
        margin-top: 12px;
        flex-wrap: wrap;
    }
    
    .shop-badge {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(8px);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        color: #ecfdf5;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Product Card Styling (Theme-proof with high-contrast text) */
    .product-card {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 14px !important;
        padding: 16px 18px !important;
        margin-top: 12px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    
    .product-card:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(6, 95, 70, 0.12) !important;
        border-color: #10b981 !important;
    }
    
    .product-header {
        display: flex !important;
        justify-content: space-between !important;
        align-items: flex-start !important;
        margin-bottom: 8px !important;
    }
    
    .product-name,
    .product-card .product-name,
    .product-card h3,
    div.product-name {
        font-size: 18px !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        margin: 4px 0 !important;
        line-height: 1.35 !important;
        text-shadow: none !important;
    }
    
    .brand-pill {
        background: #f1f5f9 !important;
        color: #334155 !important;
        padding: 3px 10px !important;
        border-radius: 6px !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        border: 1px solid #cbd5e1 !important;
    }
    
    .category-badge {
        display: inline-block !important;
        background: #ecfdf5 !important;
        color: #047857 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        padding: 3px 10px !important;
        border-radius: 12px !important;
        margin-bottom: 6px !important;
        border: 1px solid #a7f3d0 !important;
    }
    
    .product-info-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 8px !important;
        margin-top: 8px !important;
        font-size: 13px !important;
        color: #1e293b !important;
    }
    
    .product-price-box {
        display: flex !important;
        align-items: baseline !important;
        gap: 8px !important;
        margin-top: 10px !important;
        padding-top: 10px !important;
        border-top: 1px dashed #cbd5e1 !important;
    }
    
    .product-price {
        font-size: 22px !important;
        font-weight: 800 !important;
        color: #047857 !important;
    }
    
    .product-mrp {
        font-size: 13px !important;
        color: #94a3b8 !important;
        text-decoration: line-through !important;
    }
    
    .stock-badge-in {
        color: #059669 !important;
        font-weight: 700 !important;
        font-size: 12.5px !important;
        display: flex !important;
        align-items: center !important;
        gap: 4px !important;
    }
    
    .stock-badge-out {
        color: #dc2626 !important;
        font-weight: 700 !important;
        font-size: 12.5px !important;
    }
    
    /* Quick prompt button style */
    .stButton button {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    /* Order confirmation banner */
    .order-success-box {
        background: #ecfdf5;
        border: 1px solid #10b981;
        border-radius: 12px;
        padding: 16px;
        color: #065f46;
        margin: 14px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# App Initialization & Database Setup
# -----------------------------------------------------------------------------
@st.cache_resource
def setup_application():
    """Initializes database schema and populates sample catalogue."""
    init_db()
    total_products = seed_products()
    return total_products

total_products_count = setup_application()

# -----------------------------------------------------------------------------
# Session State Management
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "🌿 **रामराम शेतकरी बंधू!** मी दत्त कृषी सेवा केंद्र, काटोल चा **AI कृषी मित्र** आहे.\n\n"
                "तुमच्या शेतातील पिकांवर कोणती समस्या किंवा रोग/कीड दिसत आहे? "
                "पिकाचे नाव (उदा. कापूस, सोयाबीन, संत्रा, मिरची, टोमॅटो, गहू) व लक्षणे सांगा किंवा खाली फोटो अपलोड करा. "
                "मी योग्य व दुकानात उपलब्ध औषध सुचवेन!"
            ),
            "recommended_products": [],
            "tool_records": [],
        }
    ]

# Synchronize Streamlit Secrets to environment variables
config.sync_secrets_to_env()

default_provider = config.get_default_provider()

if "provider" not in st.session_state:
    st.session_state.provider = default_provider

if "selected_product_to_order" not in st.session_state:
    st.session_state.selected_product_to_order = None

if "order_status_message" not in st.session_state:
    st.session_state.order_status_message = None


# -----------------------------------------------------------------------------
# Sidebar: Shop Details, Category Guide & Live Orders
# -----------------------------------------------------------------------------
with st.sidebar:
    # Shop Info & Stats
    st.markdown("### 🏪 दत्त कृषी सेवा केंद्र")
    st.markdown(
        f"""
        📍 **पत्ता:** {config.SHOP_LOCATION}  
        📞 **संपर्क:** {config.SHOP_PHONE}  
        ⏰ **वेळ:** सकाळी ८:०० ते रात्री ८:३०  
        📦 **उपलब्ध निविष्ठा:** **{total_products_count}** उत्पादने उपलब्ध  
        
        💬 [**WhatsApp वर थेट संपर्क करा**](https://wa.me/{config.SHOP_WHATSAPP})
        """
    )

    st.divider()

    # Quick Categories Guide
    st.markdown("### 🌾 निविष्ठा विभाग (Categories)")
    st.markdown(
        """
        - 🐛 **कीटकनाशके** (Insecticides)
        - 🍄 **बुरशीनाशके** (Fungicides)
        - 🌿 **तणनाशके** (Herbicides)
        - 🧪 **खते & टॉनिक** (Nutrients & Tonics)
        - 🌱 **बियाणे** (Certified Seeds)
        """
    )

    st.divider()

    # View Active Orders in Shop
    all_orders = OrderService.list_orders(limit=25)
    order_count = len(all_orders)
    with st.expander(f"📋 Live Orders / नोंदवलेल्या ऑर्डर्स ({order_count})", expanded=(order_count > 0)):
        if all_orders:
            for ord_item in all_orders:
                farmer_clean_phone = "".join(filter(str.isdigit, ord_item['farmer_phone']))
                farmer_wa_text = urllib.parse.quote(
                    f"रामराम {ord_item['farmer_name']} जी, आपली दत्त कृषी सेवा केंद्र, काटोल मधील ऑर्डर ({ord_item['order_id']}) - {ord_item['product_name']} ({ord_item['pack_size']}) x {ord_item['quantity']} - ₹{ord_item['total_price']} दुकानात तयार आहे."
                )
                wa_farmer_url = f"https://wa.me/{farmer_clean_phone}?text={farmer_wa_text}" if farmer_clean_phone else None
                
                st.markdown(
                    f"""
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; margin-bottom: 8px;">
                        <div style="font-weight: 700; color: #0f172a; font-size: 13px;">🔖 {ord_item['order_id']}</div>
                        <div style="font-size: 13px; color: #1e293b; margin-top: 2px;">
                            👤 <strong>{ord_item['farmer_name']}</strong> ({ord_item['farmer_village'] or 'काटोल'})
                        </div>
                        <div style="font-size: 12px; color: #475569;">📞 <a href="tel:{ord_item['farmer_phone']}" style="color:#0369a1; text-decoration:none;">{ord_item['farmer_phone']}</a></div>
                        <div style="font-size: 13px; color: #047857; font-weight: 600; margin-top: 4px;">
                            🌾 {ord_item['product_name']} x {ord_item['quantity']} ({ord_item['pack_size']})
                        </div>
                        <div style="font-size: 13px; font-weight: 700; color: #0f172a;">
                            💰 ₹{ord_item['total_price']:.0f} &bull; <span style="font-size: 11px; color: #0284c7; background: #e0f2fe; padding: 2px 6px; border-radius: 4px;">{ord_item['status']}</span>
                        </div>
                        <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">⏰ {ord_item['created_at']}</div>
                        {f'<div style="margin-top: 6px;"><a href="{wa_farmer_url}" target="_blank" style="text-decoration:none;"><button style="width:100%; height:28px; background-color:#25D366; color:white; border:none; border-radius:6px; font-size:11px; font-weight:600; cursor:pointer;">💬 शेतकऱ्यास WhatsApp मेसेज करा</button></a></div>' if wa_farmer_url else ''}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("अजून कोणतीही ऑर्डर नोंदवलेली नाही.")

    st.divider()

    # Clear Chat / Reset
    if st.button("🔄 नवीन संभाषण सुरू करा (New Chat)", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "🌿 **रामराम शेतकरी बंधू!** मी दत्त कृषी सेवा केंद्र, काटोल चा **AI कृषी मित्र** आहे.\n\n"
                    "तुमच्या शेतातील पिकांवर कोणती समस्या किंवा रोग/कीड दिसत आहे? "
                    "पिकाचे नाव व लक्षणे सांगा किंवा खाली फोटो अपलोड करा."
                ),
                "recommended_products": [],
                "tool_records": [],
            }
        ]
        st.session_state.selected_product_to_order = None
        st.session_state.order_status_message = None
        st.rerun()


# -----------------------------------------------------------------------------
# Main Header Banner
# -----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="shop-header">
        <h1 class="shop-title">🌱 {config.SHOP_NAME_MR} <span style="font-size: 18px; font-weight: 400; opacity: 0.9;">| {config.SHOP_NAME}</span></h1>
        <p class="shop-subtitle">🌾 {config.SHOP_TAGLINE} &bull; {config.SHOP_LOCATION}</p>
        <div class="shop-badges">
            <span class="shop-badge">🔒 100% अस्सल व खात्रीशीर उत्पादने</span>
            <span class="shop-badge">🩺 तज्ज्ञ कृषी रोगनिदान</span>
            <span class="shop-badge">💰 वाजवी दर & तात्काळ आरक्षण</span>
            <span class="shop-badge">🗣️ मराठी / हिंदी / English संवाद</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Quick Suggestion Prompts
# -----------------------------------------------------------------------------
st.markdown("##### ⚡ त्वरीत सल्ला / Quick Suggestions:")
col1, col2, col3, col4 = st.columns(4)

selected_prompt = None
with col1:
    if st.button("🌱 कापूस: बोंडअळी नियंत्रण", use_container_width=True):
        selected_prompt = "माझ्या कापसाच्या पिकावर बोंडअळीचा प्रादुर्भाव आहे, कोणती फवारणी करावी?"
with col2:
    if st.button("🌿 सोयाबीन: पाने पिवळी पडणे", use_container_width=True):
        selected_prompt = "सोयाबीनची पाने पिवळी पडत आहेत आणि वाढ खुंटली आहे, काय उपाय करावा?"
with col3:
    if st.button("🌶️ मिरची: चुरडा-मुरडा (थ्रिप्स)", use_container_width=True):
        selected_prompt = "मिरचीच्या पानांचा चुरडा-मुरडा (Thrips/Mites) झाला आहे, प्रभावी औषध सांगा."
with col4:
    if st.button("🐛 सेंद्रिय औषधे (Bio-pesticides)", use_container_width=True):
        selected_prompt = "मला किडींच्या नियंत्रणासाठी सेंद्रिय/बायो कीटकनाशके दाखवा."


# -----------------------------------------------------------------------------
# Order Confirmation Form (if a product was selected for ordering)
# -----------------------------------------------------------------------------
if st.session_state.selected_product_to_order:
    prod_data = st.session_state.selected_product_to_order
    with st.container():
        st.markdown(
            f"""
            <div class="order-success-box" style="background: #ecfdf5 !important; border: 1.5px solid #10b981 !important; border-radius: 12px; padding: 16px; margin: 14px 0;">
                <div style="margin: 0 0 8px 0; font-size: 17px; font-weight: 800; color: #065f46 !important;">🛒 ऑर्डर आरक्षण: {prod_data['product_name']}</div>
                <p style="margin: 0; font-size: 14px; color: #065f46 !important;">पॅक: <strong>{prod_data['pack_size']}</strong> | किंमत: <strong>₹{prod_data['price']}</strong> | उपलब्ध स्टॉक: <strong>{prod_data['stock']} नग</strong></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("order_form"):
            form_col1, form_col2, form_col3 = st.columns(3)
            with form_col1:
                farmer_name = st.text_input("शेतकऱ्याचे नाव (Farmer Name)*", placeholder="उदा. रमेश पाटील")
            with form_col2:
                farmer_phone = st.text_input("मोबाईल नंबर (Phone Number)*", placeholder="उदा. 9822012345")
            with form_col3:
                farmer_village = st.text_input("गाव / तालुका (Village)*", value="काटोल")

            qty_col1, qty_col2 = st.columns([1, 2])
            with qty_col1:
                quantity = st.number_input("नग संख्या (Quantity)", min_value=1, max_value=max(1, prod_data["stock"]), value=1)
            with qty_col2:
                notes = st.text_input("विशेष सूचना (Optional Notes)", placeholder="उदा. उद्या संध्याकाळी दुकानातून घेईन")

            order_submitted = st.form_submit_button("✅ ऑर्डर कन्फर्म करा (Confirm Reservation)", use_container_width=True)

            if order_submitted:
                if not farmer_name or not farmer_phone:
                    st.error("कृपया आपले नाव आणि मोबाईल नंबर भरा.")
                else:
                    order_res = OrderService.create_order(
                        product_id=prod_data["product_id"],
                        quantity=quantity,
                        farmer_name=farmer_name,
                        farmer_phone=farmer_phone,
                        farmer_village=farmer_village,
                        notes=notes,
                    )
                    if order_res.get("success"):
                        st.session_state.order_status_message = order_res
                        st.session_state.selected_product_to_order = None
                        st.rerun()
                    else:
                        st.error(order_res.get("message", "ऑर्डर नोंदवण्यात त्रुटी आली."))

        if st.button("❌ रद्द करा (Cancel)"):
            st.session_state.selected_product_to_order = None
            st.rerun()

if st.session_state.order_status_message:
    msg = st.session_state.order_status_message
    st.success(
        f"🎉 **{msg['message']}**\n\n"
        f"• **उत्पादन:** {msg['product_name']} ({msg['pack_size']}) x {msg['quantity']}\n"
        f"• **ग्राहक:** {msg['farmer_name']} ({msg['farmer_phone']})\n"
        f"• **पिकअप ठिकाण:** {msg['pickup_location']}\n\n"
        f"आपला माल दुकानात बाजूला काढून ठेवण्यात आला आहे. धन्यवाद!"
    )
    if st.button("समजले (Dismiss)"):
        st.session_state.order_status_message = None
        st.rerun()


# -----------------------------------------------------------------------------
# Function to Render Interactive Product Cards
# -----------------------------------------------------------------------------
def render_product_card(product: dict, key_prefix: str):
    """Renders a responsive, interactive product card."""
    prod_id = product.get("product_id", "")
    prod_name = product.get("product_name", "")
    brand = product.get("brand_name", "")
    category = product.get("category", "कृषी निविष्ठा")
    active_ing = product.get("active_ingredient", "")
    pack_size = product.get("pack_size", "")
    price = product.get("price", 0.0)
    mrp = product.get("mrp", price)
    stock = product.get("stock", 0)
    in_stock = product.get("in_stock", stock > 0)
    dosage = product.get("dosage", "लेबल सूचनांनुसार वापरावे")
    crops = ", ".join(product.get("crops", []))

    st.markdown(
        f"""
        <div class="product-card" style="background: #ffffff !important; border: 1.5px solid #cbd5e1 !important; border-radius: 14px !important; padding: 18px !important; box-shadow: 0 4px 14px rgba(0,0,0,0.08) !important; margin: 12px 0 !important;">
            <div class="product-header" style="display: flex !important; justify-content: space-between !important; align-items: flex-start !important; margin-bottom: 8px !important;">
                <div>
                    <span class="category-badge" style="display: inline-block !important; background: #ecfdf5 !important; color: #047857 !important; font-size: 12px !important; font-weight: 600 !important; padding: 3px 10px !important; border-radius: 12px !important; border: 1px solid #a7f3d0 !important; margin-bottom: 6px !important;">{category}</span>
                    <div class="product-name" style="font-size: 18px !important; font-weight: 800 !important; color: #0f172a !important; margin: 4px 0 6px 0 !important; line-height: 1.35 !important; text-shadow: none !important;">
                        {prod_name}
                    </div>
                </div>
                <span class="brand-pill" style="background: #f1f5f9 !important; color: #334155 !important; padding: 3px 10px !important; border-radius: 6px !important; font-size: 11px !important; font-weight: 700 !important; text-transform: uppercase !important; border: 1px solid #cbd5e1 !important;">{brand}</span>
            </div>
            <div style="font-size: 13.5px !important; color: #1e293b !important; margin-bottom: 6px !important; line-height: 1.4 !important;">
                <strong style="color: #0f172a !important;">घटक (Active):</strong> <span style="color: #334155 !important;">{active_ing}</span>
            </div>
            <div style="font-size: 12.5px !important; color: #475569 !important; margin-bottom: 8px !important; line-height: 1.4 !important;">
                <strong style="color: #0f172a !important;">शिफारस पिके:</strong> <span style="color: #475569 !important;">{crops}</span> | <strong style="color: #0f172a !important;">प्रमाण:</strong> <span style="color: #475569 !important;">{dosage}</span>
            </div>
            <div class="product-price-box" style="display: flex !important; align-items: baseline !important; gap: 8px !important; margin-top: 10px !important; padding-top: 10px !important; border-top: 1px dashed #cbd5e1 !important;">
                <span class="product-price" style="font-size: 22px !important; font-weight: 800 !important; color: #047857 !important;">₹{price:.0f}</span>
                <span class="product-mrp" style="font-size: 13px !important; color: #94a3b8 !important; text-decoration: line-through !important;">₹{mrp:.0f} MRP</span>
                <span style="font-size: 13px !important; color: #475569 !important; font-weight: 500 !important;">({pack_size})</span>
                <span style="margin-left: auto !important;">
                    {"<span class='stock-badge-in' style='color: #059669 !important; font-weight: 700 !important; font-size: 12.5px !important;'>🟢 स्टॉकमध्ये उपलब्ध (" + str(stock) + " नग)</span>" if in_stock else "<span class='stock-badge-out' style='color: #dc2626 !important; font-weight: 700 !important; font-size: 12.5px !important;'>🔴 संपले आहे (Out of stock)</span>"}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Action buttons underneath card
    btn_col1, btn_col2, btn_col3 = st.columns([1.2, 1.4, 2])
    with btn_col1:
        if in_stock:
            if st.button(f"🛒 ऑर्डर करा", key=f"buy_{key_prefix}_{prod_id}", use_container_width=True):
                st.session_state.selected_product_to_order = product
                st.rerun()
        else:
            st.button("🔴 अनुपलब्ध", disabled=True, key=f"dis_{key_prefix}_{prod_id}", use_container_width=True)

    with btn_col2:
        # Pre-filled WhatsApp enquiry link
        wa_text = urllib.parse.quote(
            f"नमस्कार, मला दत्त कृषी सेवा केंद्रातून '{prod_name}' ({pack_size}) - ₹{price} बद्दल चौकशी करायची आहे / ऑर्डर करायची आहे."
        )
        wa_url = f"https://wa.me/{config.SHOP_WHATSAPP}?text={wa_text}"
        st.markdown(
            f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><button style="width:100%; height:38px; background-color:#25D366; color:white; border:none; border-radius:10px; font-weight:600; cursor:pointer;">💬 WhatsApp चौकशी</button></a>',
            unsafe_allow_html=True,
        )


# -----------------------------------------------------------------------------
# Conversation History Display
# -----------------------------------------------------------------------------
for msg_idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"], avatar="👨‍🌾" if msg["role"] == "user" else "🌱"):
        st.markdown(msg["content"])

        # If assistant recommended products, render the rich product cards
        if msg.get("recommended_products"):
            st.markdown("##### 🛒 शिफारस केलेली उपलब्ध उत्पादने:")
            for p_idx, prod in enumerate(msg["recommended_products"]):
                render_product_card(prod, key_prefix=f"hist_{msg_idx}_{p_idx}")


# -----------------------------------------------------------------------------
# Input Section: Image Upload & Chat Input
# -----------------------------------------------------------------------------
st.markdown("---")
upload_col, info_col = st.columns([1, 2])

with upload_col:
    uploaded_image_file = st.file_uploader(
        "📷 पिकाचा किंवा कीड/रोगाचा फोटो अपलोड करा (Optional):",
        type=["jpg", "jpeg", "png", "webp"],
        help="Upload a clear photo of the leaf, insect, or fruit for visual diagnosis.",
    )

image_bytes = None
if uploaded_image_file:
    image_bytes = uploaded_image_file.getvalue()
    with upload_col:
        st.image(uploaded_image_file, caption="अपलोड केलेला फोटो (Uploaded Image)", width=220)

user_input = st.chat_input("तुमची शेतीविषयक समस्या किंवा औषधाचे नाव येथे विचारा...")

# If quick prompt was clicked, use it as user input
if selected_prompt:
    user_input = selected_prompt


# -----------------------------------------------------------------------------
# Agent Processing Flow
# -----------------------------------------------------------------------------
if user_input:
    # 1. Append and display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👨‍🌾"):
        st.markdown(user_input)
        if image_bytes:
            st.image(image_bytes, width=200)

    # 2. Invoke Core Agent
    with st.chat_message("assistant", avatar="🌱"):
        with st.spinner("कृषी सल्लागार विश्लेषण करत आहे... (Analyzing...)"):
            active_key = (
                config.get_openai_api_key()
                if st.session_state.provider == "openai"
                else config.get_gemini_api_key()
            )
            agent = CoreAgent(
                provider_name=st.session_state.provider,
                api_key=active_key,
            )

            # Filter messages to pass to agent
            chat_history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]

            response: AgentResponse = agent.chat(
                messages=chat_history,
                image_bytes=image_bytes,
                provider_name=st.session_state.provider,
                api_key=active_key,
            )

            # Display response text
            st.markdown(response.text)

            # Display recommended product cards
            if response.recommended_products:
                st.markdown("##### 🛒 शिफारस केलेली उपलब्ध उत्पादने:")
                for p_idx, prod in enumerate(response.recommended_products):
                    render_product_card(prod, key_prefix=f"new_{p_idx}")

            # Append to session state
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response.text,
                    "recommended_products": response.recommended_products,
                    "tool_records": response.tool_records,
                }
            )

            # Handle order creation if tool placed it directly
            if response.order_created:
                st.session_state.order_status_message = response.order_created
                st.rerun()
