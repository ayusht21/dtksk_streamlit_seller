# 🌱 Datta Krushi Seva Kendra — Farmer AI Support & Sales Agent
*(दत्त कृषी सेवा केंद्र, काटोल — AI कृषी मित्र व उत्पादन शिफारस प्रणाली)*

A production-ready, multi-channel AI-powered **Farmer Support & Consultative Sales Application**. Built with **Streamlit**, a decoupled **Core Agent** (supporting both **OpenAI** and **Google Gemini** with Function Calling and Vision), and a verified **SQLite/PostgreSQL database** seeded with real Indian agricultural inputs.

---

## 🌟 Key Features

1. **🩺 Agricultural Problem Diagnosis & Consultation**
   - Empathizes with the farmer and accurately diagnoses crop pests, fungal/bacterial diseases, weed infestations, and nutrient deficiencies.
   - Follows strict diagnostic thoroughness: asks focused follow-up questions when information is incomplete rather than blindly recommending chemicals.

2. **📷 Multimodal Image Understanding (Crop Doctor)**
   - Farmers can upload photos of damaged leaves, stems, or pests.
   - Provides cautious, professional visual diagnosis (*"Based on the image, the symptoms appear consistent with..."*).

3. **🔒 Zero-Hallucination & Tool Grounding**
   - The AI agent **never invents** products, prices, stock counts, pack sizes, or dosages.
   - Connects in real-time to the shop catalogue database via tools:
     - `search_products(crop, problem, category, organic_only, in_stock_only)`
     - `get_product_details(product_id)`
     - `check_stock(product_id)`
     - `get_current_price(product_id)`
     - `create_order(product_id, quantity, farmer_name, farmer_phone, village)`

4. **🤝 Ethical Consultative Selling & Objection Handling**
   - Recommends 1–2 in-stock solutions with transparent pricing and pack sizes.
   - Explains *why* the product helps in simple, farmer-friendly language.
   - Gracefully handles price objections (smaller pack sizes / economical generics) and organic preferences (bio-pesticides & bio-stimulants).

5. **🛒 Interactive Product Cards & Order Reservations**
   - Renders rich product cards directly in the chat stream with active ingredients, dosage rates, MRP discounts, and live stock indicators.
   - Allows instant order reservation with farmer details and generates pre-filled WhatsApp enquiry links.

6. **🗣️ Fluent Multilingual Regional Support**
   - Natural, conversational Marathi (मराठी — *रामराम शेतकरी बंधू!*), Hindi (हिंदी), English, and mixed Hinglish/Marathi-English.

7. **🔌 Multi-Provider LLM Engine (OpenAI & Gemini)**
   - **OpenAI**: Ready out-of-the-box with `OPENAI_API_KEY` (using `gpt-4o` or `gpt-4o-mini`).
   - **Google Gemini**: Switch anytime using `GEMINI_API_KEY` (using `gemini-3.6-flash`).
   - **Interactive Offline Fallback**: Test the app immediately without an API key using rule-based diagnostic heuristics.

8. **📱 Decoupled Core Architecture**
   - The core intelligence (`agent/core_agent.py`) is completely independent of Streamlit and can be plugged directly into **WhatsApp (Twilio/Meta API)**, **Telegram**, or a **REST API** backend.

---

## 🏗️ Architecture

```text
                     FARMER (शेतकरी)
                            │
                            ▼
              STREAMLIT CHAT UI / WHATSAPP
                            │
                            ▼
            CORE AGENT (agent/core_agent.py)
                            │
              Unified Provider Interface
             (OpenAI GPT-4o / Gemini 3.6 Flash)
                            │
                    Tool / Function Calls
                            │
    ┌───────────────────────┼───────────────────────┐
    ▼                       ▼                       ▼
search_products()    check_stock()        create_order()
    │                       │                       │
    └───────────────────────┼───────────────────────┘
                            │
                            ▼
         SQLITE / POSTGRESQL PRODUCT DATABASE
       (28+ Verified Commercial Agri-Inputs)
```

---

## 📁 Project Structure

```text
Datta Krushi Seva Kendra/
├── app.py                          # Streamlit UI with Chat, Product Cards & Order Modal
├── config.py                       # Configuration & environment variable loader
├── requirements.txt                # Python dependencies
├── .env.example                    # Template for API keys
├── README.md                       # Documentation
│
├── agent/
│   ├── __init__.py
│   ├── agent_config.py             # Model hyperparameters and settings
│   ├── core_agent.py               # Framework-agnostic Agent Runner
│   ├── tools.py                    # Tool definitions and execution handlers
│   └── prompts/
│       ├── __init__.py
│       ├── system_prompt.py        # System prompt with consultative sales & zero-hallucination rules
│       └── agricultural_knowledge.py # Agronomic diagnostic keys & pest/disease heuristics
│
├── database/
│   ├── __init__.py
│   ├── database.py                 # SQLAlchemy engine & session manager
│   ├── models.py                   # Product, Order, and Session models
│   └── seed.py                     # CSV seeder script
│
├── catalogue/
│   └── sample_products.csv         # Verified Indian agri-products catalogue
│
├── services/
│   ├── __init__.py
│   ├── product_search.py           # Multi-attribute & alias-aware search engine
│   ├── order_service.py            # Order management & inventory deduction
│   ├── llm_provider.py             # Unified OpenAI, Gemini, and Mock provider wrapper
│   └── agent_client.py             # LLM provider factory
│
└── tests/
    ├── __init__.py
    ├── test_database.py            # Database & seeding tests
    ├── test_search.py              # Search filter & alias tests
    ├── test_agent_tools.py         # Tool calling execution tests
    └── test_llm_provider.py        # Provider abstraction & mock tests
```

---

## 🚀 Quick Start Guide

### 1. Clone or Navigate to the Project
```bash
cd "Datta Krushi Seva Kendra"
```

### 2. Install Dependencies
```bash
python3 -m pip install -r requirements.txt
```

### 3. Configure API Key
Create a `.env` file (or copy from `.env.example`):
```bash
cp .env.example .env
```
Edit `.env` and set your OpenAI or Gemini key:
```env
OPENAI_API_KEY=your_openai_api_key_here
# or
GEMINI_API_KEY=your_gemini_api_key_here
```
*(You can also enter your API key directly in the Streamlit sidebar at runtime).*

### 4. Initialize & Seed the Database
```bash
python3 -m database.seed
```

### 5. Run the Automated Test Suite
```bash
python3 -m unittest discover tests
```

### 6. Launch the Streamlit App
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Sample Agricultural Queries to Test

- **Cotton Bollworm (मराठी)**:  
  `"माझ्या कापसाच्या पिकावर बोंडअळीचा प्रादुर्भाव आहे, कोणती फवारणी करावी?"`  
  *(Agent searches catalogue -> recommends Coragen / Ampligo with price, pack size, dosage).*

- **Vague Symptom (Diagnostic follow-up)**:  
  `"माझे सोयाबीनचे पीक खराब होत आहे."`  
  *(Agent asks targeted follow-up questions: visible symptoms, leaf color, insect presence, crop stage).*

- **Price Objection (Consultative selling)**:  
  `"हे औषध खूप महाग आहे, काही कमी खर्चाचा उपाय आहे का?"`  
  *(Agent suggests smaller pack size or economical alternative molecule in stock).*

- **Chilli Leaf Curl & Thrips**:  
  `"मिरचीच्या पानांचा चुरडा-मुरडा झाला आहे."`  
  *(Agent recommends Pegasus / Delegate).*

- **Organic Preference**:  
  `"मला रासायनिक नको, सेंद्रिय औषध दाखवा."`  
  *(Agent filters for certified Bio-pesticides like Neem Oil 10000 PPM, Trichoderma, Beauveria).*

- **Order Placement**:  
  `"मला कोराजनचे ६० मि.ली. चे १ पॅक हवे आहे, माझे नाव रमेश पाटील, नांदगाव."`  
  *(Agent invokes create_order tool and returns confirmed Order ID).*

---

## 📜 License
MIT License. Built for Indian farmers with ❤️.
