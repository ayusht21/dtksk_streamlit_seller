"""
Agricultural diagnostic reference heuristics and domain knowledge for Indian farming conditions.
Used to assist the agent in understanding crop symptoms and asking targeted diagnostic questions.
"""

AGRICULTURAL_DIAGNOSTIC_GUIDE = """
=== CROP DIAGNOSTIC KEY & REGIONAL AGRONOMY GUIDE ===

1. COTTON (कापूस / कपाशी):
   - Leaf Curling Upwards + Yellowing Margins + Shining Sticky Honeydew: Aphids (मावा) or Jassids (तुडतुडे).
   - Leaf Curling Downwards / Boat-shaped + Silvery underside: Thrips (फुलकिडे / चुरडा).
   - Yellow Mosaic Patches + Flying Tiny White Insects: Whitefly (पांढरी माशी) transmitting Yellow Mosaic.
   - Bored Holes in Bolls/Squares + Excreta + Dropping of Squares: Pink/American Bollworm (बोंडअळी / बोंड गळ).
   - Recommended Active Ingredients:
     * Bollworm: Chlorantraniliprole 18.5% SC (Coragen) or Chlorantraniliprole + Lambda (Ampligo).
     * Sucking Pests (Aphids/Jassids): Imidacloprid 17.8% SL (Confidor) or Thiamethoxam + Lambda (Alika).
     * Severe Thrips/Whitefly: Diafenthiuron 50% WP (Pegasus) or Spinetoram (Delegate).
     * Flower/Square Drop: Amino acids biostimulant (Tata Bahar / Multiplex Samras) + 00:52:34.

2. SOYBEAN (सोयाबीन):
   - Holes in Leaves + Foliage Eating Caterpillars: Semilooper / Spodoptera (पाने खाणारी अळी / लष्करी अळी).
   - Stem Tunneling / Drying of Main Shoot: Girdle Beetle or Stem Fly (खोडकिडा / चक्र भुंगा).
   - Reddish Brown Spots on Leaves + Early Defoliation: Rust / Leaf Spot / Anthracnose (तांबेरा / करपा).
   - Yellowing of Leaves: Zinc or Iron deficiency, or Waterlogging.
   - Recommended Active Ingredients:
     * Caterpillars: Coragen 18.5% SC or Ampligo or Alika.
     * Rust/Leaf Spot: Azoxystrobin + Difenoconazole (Amistar Top) or Carbendazim + Mancozeb (Saaf).
     * Weeds (Post-emergence): Quizalofop Ethyl (Targa Super) or Propaquizafop + Imazethapyr (Shaked).
     * Pod Filling & Grain Weight: 00:00:50 (Potassium Sulphate) + Boron 20%.

3. CHILLI (मिरची):
   - Severe Leaf Curl (Churada-Murada / चुरडा-मुरडा) Upward: Thrips (फुलकिडे).
   - Leaf Curl Downward + Thick Leathery Leaves: Mites (लाल कोळी).
   - Yellowing & Stunted Bushy Appearance: Whitefly vector.
   - Black Spots on Fruits & Twig Dieback: Anthracnose / Dieback / Fruit Rot (फळकुज / करपा).
   - Flower & Bud Drop: Temperature stress or Micronutrient deficiency.
   - Recommended Solutions:
     * Thrips & Mites: Pegasus 50% WP (Diafenthiuron) or Delegate 11.7% SC (Spinetoram).
     * Sucking Pests: Confidor (Imidacloprid).
     * Dieback / Fruit Rot: Custodia (Azoxystrobin + Tebuconazole) or Amistar Top.
     * Flower Retention: Tata Bahar (2 ml/L) + Boron 20% (1 g/L).

4. TOMATO (टोमॅटो):
   - Concentric Rings / Brown Spots on Leaves & Fruits: Early / Late Blight (करपा).
   - Pin-holes in Fruits + Larva Inside: Fruit Borer / Helicoverpa / Tuta absoluta (फळ पोखरणारी अळी).
   - Sudden Wilting of Green Plants: Bacterial / Fungal Wilt (मर रोग).
   - Flower Drop: Isabion or Multiplex Samras + 00:52:34 spray.
   - Recommended Solutions:
     * Blight: Nativo (Tebuconazole + Trifloxystrobin) or Amistar Top or Saaf.
     * Fruit Borer: Coragen 18.5% SC or Ampligo.
     * Soil Health & Wilt Prevention: Trichoderma viride drenching.

5. SUGARCANE (ऊस):
   - Drying of Central Shoot (Dead Heart in young cane): Early Shoot Borer (खोडकिडा).
   - Yellowing of Leaves in Patches: Iron/Zinc Chlorosis or White Grub (हुमणी अळी).
   - Tillering & Rooting Boost: Humic Acid 98% (Humic King) + 19:19:19 drenching.

6. ONION & GARLIC (कांदा व लसूण):
   - Silvery Patches on Leaves + Twisted Neck: Thrips (कांद्यावरील फुलकिडे / मावा).
   - Purple Oval Lesions with Concentric Rings: Purple Blotch (जांभळा करपा).
   - Bulb Sizing & Weight: 00:00:50 + Humic Acid.

7. GRAM / CHICKPEA (हरभरा / चना):
   - Drooping & Drying of Plant from Root: Fusarium Wilt / Root Rot (मर रोग). Prevention via Saaf / Trichoderma seed treatment.
   - Pod Damage & Holes: Pod Borer / Helicoverpa (घाटे अळी) -> Coragen or Ampligo.

8. WEED MANAGEMENT & SOIL HEALTH:
   - Grass weeds in broadleaf crops: Targa Super (Quizalofop Ethyl).
   - Mixed broadleaf + grass weeds in soybean: Shaked (Propaquizafop + Imazethapyr).
   - General non-crop/bund weed eradication: Roundup (Glyphosate 41% SL).
   - White Root & Soil Vitality: Humic King 98% (Potassium Humate).
"""
