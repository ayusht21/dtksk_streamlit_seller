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
    
    /* Product Card Styling */
    .product-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 16px 18px;
        margin-top: 12px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(6, 95, 70, 0.08);
        border-color: #a7f3d0;
    }
    
    .product-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;
    }
    
    .product-name {
        font-size: 17px;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
    }
    
    .brand-pill {
        background: #f1f5f9;
        color: #475569;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .category-badge {
        display: inline-block;
        background: #ecfdf5;
        color: #047857;
        font-size: 12px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 12px;
        margin-bottom: 8px;
        border: 1px solid #a7f3d0;
    }
    
    .product-info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: 8px;
        font-size: 13px;
        color: #334155;
    }
    
    .product-price-box {
        display: flex;
        align-items: baseline;
        gap: 8px;
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px dashed #e2e8f0;
    }
    
    .product-price {
        font-size: 20px;
        font-weight: 700;
        color: #065f46;
    }
    
    .product-mrp {
        font-size: 13px;
        color: #94a3b8;
        text-decoration: line-through;
    }
    
    .stock-badge-in {
        color: #059669;
        font-weight: 600;
        font-size: 12px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .stock-badge-out {
        color: #dc2626;
        font-weight: 600;
        font-size: 12px;
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

discovered_openai_key = config.get_openai_api_key()
discovered_gemini_key = config.get_gemini_api_key()
default_provider = config.get_default_provider()

if "provider" not in st.session_state:
    st.session_state.provider = default_provider

# Always ensure session state keys are populated from secrets if not manually set
if not st.session_state.get("openai_api_key"):
    st.session_state.openai_api_key = discovered_openai_key

if not st.session_state.get("gemini_api_key"):
    st.session_state.gemini_api_key = discovered_gemini_key

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

    # AI Engine & API Status Configuration
    with st.expander("⚙️ AI मॉडेल & सेटिंग्ज (AI Settings)", expanded=False):
        has_openai = bool(st.session_state.openai_api_key or config.get_openai_api_key())
        has_gemini = bool(st.session_state.gemini_api_key or config.get_gemini_api_key())

        provider_options = ["openai", "gemini", "mock"]
        provider_labels = {
            "openai": "OpenAI (GPT-4o)",
            "gemini": "Google Gemini",
            "mock": "Offline / Demo Mode",
        }
        
        current_idx = 0
        if st.session_state.provider in provider_options:
            current_idx = provider_options.index(st.session_state.provider)

        selected_p = st.selectbox(
            "AI Provider निवडा:",
            options=provider_options,
            index=current_idx,
            format_func=lambda x: provider_labels.get(x, x),
        )
        st.session_state.provider = selected_p

        if selected_p == "openai":
            if has_openai:
                st.success("🟢 OpenAI Key कनेक्टेड आहे (Secrets/Env)")
            else:
                st.warning("⚠️ OpenAI Key आढळली नाही")
            
            custom_key = st.text_input(
                "OpenAI API Key (Override/Manual):",
                value=st.session_state.openai_api_key,
                type="password",
                placeholder="sk-proj-...",
                help="Streamlit Secrets किंवा .env मधील की आपोआप वापरली जाते. हवी असल्यास येथे मॅन्युअल टाका.",
            )
            if custom_key != st.session_state.openai_api_key:
                st.session_state.openai_api_key = custom_key
        elif selected_p == "gemini":
            if has_gemini:
                st.success("🟢 Gemini Key कनेक्टेड आहे (Secrets/Env)")
            else:
                st.warning("⚠️ Gemini Key आढळली नाही")

            custom_g_key = st.text_input(
                "Gemini API Key (Override/Manual):",
                value=st.session_state.gemini_api_key,
                type="password",
                placeholder="AIzaSy...",
            )
            if custom_g_key != st.session_state.gemini_api_key:
                st.session_state.gemini_api_key = custom_g_key
        else:
            st.info("💡 ऑफलाइन / डेमो मोड सक्रिय आहे.")

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
    with st.expander("📋 Live Orders / नोंदवलेल्या ऑर्डर्स", expanded=False):
        recent_orders = OrderService.list_orders(limit=10)
        if recent_orders:
            for ord_item in recent_orders:
                st.markdown(
                    f"""
                    **{ord_item['order_id']}**  
                    👤 {ord_item['farmer_name']} ({ord_item['farmer_village'] or 'काटोल'})  
                    🌾 {ord_item['product_name']} x {ord_item['quantity']} ({ord_item['pack_size']})  
                    💰 **₹{ord_item['total_price']}** | Status: `{ord_item['status']}`  
                    <small>{ord_item['created_at']}</small>
                    <hr style="margin: 6px 0;">
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
            <div class="order-success-box">
                <h4 style="margin: 0 0 8px 0; color: #065f46;">🛒 ऑर्डर आरक्षण: {prod_data['product_name']}</h4>
                <p style="margin: 0; font-size: 14px;">पॅक: <strong>{prod_data['pack_size']}</strong> | किंमत: <strong>₹{prod_data['price']}</strong> | उपलब्ध स्टॉक: <strong>{prod_data['stock']} नग</strong></p>
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
        <div class="product-card">
            <div class="product-header">
                <div>
                    <span class="category-badge">{category}</span>
                    <h3 class="product-name">{prod_name}</h3>
                </div>
                <span class="brand-pill">{brand}</span>
            </div>
            <div style="font-size: 13px; color: #475569; margin-bottom: 6px;">
                <strong>घटक (Active):</strong> {active_ing}
            </div>
            <div style="font-size: 12px; color: #64748b;">
                <strong>शिफारस पिके:</strong> {crops} | <strong>प्रमाण:</strong> {dosage}
            </div>
            <div class="product-price-box">
                <span class="product-price">₹{price:.0f}</span>
                <span class="product-mrp">₹{mrp:.0f} MRP</span>
                <span style="font-size: 13px; color: #64748b;">({pack_size})</span>
                <span style="margin-left: auto;">
                    {"<span class='stock-badge-in'>🟢 स्टॉकमध्ये उपलब्ध (" + str(stock) + " नग)</span>" if in_stock else "<span class='stock-badge-out'>🔴 संपले आहे (Out of stock)</span>"}
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
                (st.session_state.openai_api_key or config.get_openai_api_key())
                if st.session_state.provider == "openai"
                else (st.session_state.gemini_api_key or config.get_gemini_api_key())
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
