"""
AI Service for Farmer Assistant
Supports Google Gemini API with fallback responses
"""

import os
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert agricultural advisor and farmer assistant called "KisanAI" (కిసాన్ AI / किसान AI).

YOUR ROLE:
- You are a knowledgeable, friendly agricultural expert
- You help Indian farmers with practical, actionable farming advice
- You understand Indian farming conditions, seasons, and crops

RESPONSE RULES:
1. Keep answers SHORT and PRACTICAL (3-5 sentences max unless detail is needed)
2. Use simple language farmers can understand
3. Give SPECIFIC advice, not generic information
4. When asked in Telugu, respond in Telugu
5. When asked in Hindi, respond in Hindi
6. When asked in English, respond in English
7. Focus on crops common in India: Rice, Wheat, Cotton, Sugarcane, Pulses, Vegetables, Millets
8. Always consider Indian climate zones and seasons

TOPICS YOU COVER:
- Crop selection and rotation
- Pest and disease identification and control
- Fertilizer recommendations (organic and chemical)
- Irrigation scheduling
- Seasonal farming calendar
- Soil health management
- Market prices and crop selling tips
- Government schemes for farmers (PM-KISAN, etc.)
- Weather-based farming decisions

LANGUAGE INSTRUCTIONS:
- If the user writes in Telugu script, respond in Telugu
- If the user writes in Hindi/Devanagari, respond in Hindi
- Default to English if unclear
- You can mix English technical terms with local language

Always end your response with a brief encouraging note for the farmer."""

FARMING_RESPONSES = {
    'fallback_en': """I'm here to help you with farming advice! I can assist with:
🌾 Crop selection and planting schedules
🐛 Pest and disease control
💧 Irrigation planning
🌱 Fertilizer recommendations
📅 Seasonal farming tips

Please ask me any farming question and I'll provide practical advice tailored to Indian farming conditions.""",

    'fallback_hi': """मैं खेती की सलाह में आपकी मदद करने के लिए यहाँ हूँ!
🌾 फसल चुनाव और बुवाई का समय
🐛 कीट और रोग नियंत्रण
💧 सिंचाई की योजना
🌱 उर्वरक की सिफारिशें

कोई भी कृषि प्रश्न पूछें!""",

    'fallback_te': """నేను మీ వ్యవసాయ సమస్యలకు సహాయం చేయడానికి ఇక్కడ ఉన్నాను!
🌾 పంట ఎంపిక మరియు విత్తన సమయం
🐛 చీడపీడల నియంత్రణ
💧 నీటిపారుదల ప్రణాళిక
🌱 ఎరువుల సిఫారసులు

ఏదైనా వ్యవసాయ ప్రశ్న అడగండి!"""
}


def get_ai_response(user_message: str, language: str = 'en', location: str = '', crops: str = '') -> str:
    """
    Get AI response from Gemini API.
    Falls back to intelligent static responses if API key not configured.
    """
    api_key = settings.GEMINI_API_KEY

    if api_key:
        try:
            return _call_gemini(user_message, language, location, crops, api_key)
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return _smart_fallback(user_message, language)
    else:
        return _smart_fallback(user_message, language)


def _call_gemini(message: str, language: str, location: str, crops: str, api_key: str) -> str:
    """Call Google Gemini API"""
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    context = f"\nUser location: {location}" if location else ""
    context += f"\nUser's crops: {crops}" if crops else ""

    full_prompt = f"""{SYSTEM_PROMPT}

{context}

User Question: {message}

Respond in {'Telugu' if language == 'te' else 'Hindi' if language == 'hi' else 'English'}."""

    response = model.generate_content(full_prompt)
    return response.text


def _smart_fallback(message: str, language: str) -> str:
    """Provide intelligent farming responses when API is unavailable"""
    message_lower = message.lower()

    # Detect topic
    if any(word in message_lower for word in ['rice', 'paddy', 'dhaan', 'వరి', 'चावल']):
        return _get_rice_advice(language)
    elif any(word in message_lower for word in ['wheat', 'gehun', 'గోధుమ', 'गेहूं']):
        return _get_wheat_advice(language)
    elif any(word in message_lower for word in ['pest', 'insect', 'bug', 'కీటకం', 'कीट']):
        return _get_pest_advice(language)
    elif any(word in message_lower for word in ['fertilizer', 'urea', 'ఎరువు', 'उर्वरक', 'खाद']):
        return _get_fertilizer_advice(language)
    elif any(word in message_lower for word in ['water', 'irrigation', 'నీరు', 'पानी', 'सिंचाई']):
        return _get_irrigation_advice(language)
    elif any(word in message_lower for word in ['weather', 'rain', 'వర్షం', 'बारिश', 'मौसम']):
        return _get_weather_advice(language)
    elif any(word in message_lower for word in ['soil', 'మట్టి', 'मिट्टी']):
        return _get_soil_advice(language)
    elif any(word in message_lower for word in ['cotton', 'పత్తి', 'कपास']):
        return _get_cotton_advice(language)
    else:
        lang_key = f'fallback_{language}' if language in ['en', 'hi', 'te'] else 'fallback_en'
        return FARMING_RESPONSES.get(lang_key, FARMING_RESPONSES['fallback_en'])


def _get_rice_advice(lang):
    advice = {
        'en': """🌾 **Rice Farming Tips:**

• **Best Season:** Kharif (June-July for transplanting)
• **Soil:** Clay loam with good water retention
• **Seed Rate:** 20-25 kg/acre for direct seeding, 8-10 kg for transplanting
• **Key Fertilizers:** Apply NPK 120:60:40 kg/hectare
• **Common Pests:** Watch for Brown Plant Hopper - use Imidacloprid if severe
• **Irrigation:** Keep 2-5 cm standing water during tillering stage

💡 Pro tip: Use SRI (System of Rice Intensification) method to save water and increase yield by 30%!""",

        'hi': """🌾 **धान की खेती के टिप्स:**

• **सबसे अच्छा समय:** खरीफ (जून-जुलाई में रोपाई)
• **मिट्टी:** चिकनी दोमट जो पानी रोक सके
• **बीज दर:** सीधी बुवाई के लिए 20-25 किग्रा/एकड़
• **मुख्य खाद:** NPK 120:60:40 किग्रा/हेक्टेयर
• **सामान्य कीट:** भूरा फुदका - Imidacloprid का उपयोग करें

💡 सुझाव: SRI पद्धति से 30% अधिक उपज पाएं!""",

        'te': """🌾 **వరి సాగు చిట్కాలు:**

• **మంచి సమయం:** ఖరీఫ్ (జూన్-జూలై లో నాటడం)
• **నేల:** మట్టి గుణాలు మంచిగా ఉండాలి
• **విత్తన మోతాదు:** 20-25 కిలోలు/ఎకరం
• **ప్రధాన ఎరువులు:** NPK 120:60:40 కిలోలు/హెక్టారు
• **సాధారణ చీడలు:** గోధుమ రంగు మొక్కజొన్న దూడ

💡 చిట్కా: SRI పద్దతి ద్వారా 30% అధిక దిగుబడి పొందండి!"""
    }
    return advice.get(lang, advice['en'])


def _get_wheat_advice(lang):
    advice = {
        'en': """🌾 **Wheat Farming Guide:**

• **Sowing Time:** November to December (Rabi season)
• **Varieties:** HD-2967, GW-496, PBW-550 are high-yielding
• **Seed Treatment:** Treat with Thiram 2.5g/kg seed before sowing
• **Fertilizer:** Apply 120kg N, 60kg P, 40kg K per hectare
• **Irrigation:** 4-6 irrigations needed (crown root, tillering, jointing, flowering, grain filling)
• **Harvest:** Ready in 120-150 days

💡 Tip: Avoid late sowing - every week delay reduces yield by 30-40 kg/acre!""",

        'hi': """🌾 **गेहूं की खेती गाइड:**

• **बुवाई का समय:** नवंबर-दिसंबर (रबी सीजन)
• **किस्में:** HD-2967, GW-496 अच्छी उपज देती हैं
• **बीज उपचार:** थीरम 2.5 ग्राम/किग्रा से बीज उपचार करें
• **खाद:** N-120, P-60, K-40 किग्रा/हेक्टेयर

💡 सुझाव: देर से बुवाई न करें - हर सप्ताह की देरी से 30-40 किग्रा/एकड़ उपज कम होती है!""",

        'te': """🌾 **గోధుమ సాగు గైడ్:**

• **విత్తన సమయం:** నవంబర్-డిసెంబర్ (రబీ సీజన్)
• **రకాలు:** HD-2967, GW-496 మంచి దిగుబడి ఇస్తాయి
• **విత్తన చికిత్స:** Thiram 2.5g/కిలో తో చికిత్స చేయండి
• **ఎరువులు:** N-120, P-60, K-40 కిలోలు/హెక్టారు

💡 చిట్కా: ఆలస్యంగా విత్తవద్దు - ప్రతి వారం ఆలస్యంతో 30-40 కిలోలు/ఎకరం దిగుబడి తగ్గుతుంది!"""
    }
    return advice.get(lang, advice['en'])


def _get_pest_advice(lang):
    advice = {
        'en': """🐛 **Pest Control Guide:**

**Integrated Pest Management (IPM) approach:**
1. **Monitor regularly** - Check fields twice a week
2. **Use sticky traps** - Yellow traps for whitefly, blue for thrips
3. **Biological control** - Use Trichogramma cards for borer control
4. **Neem-based spray** - 5% Neem leaf extract as preventive measure
5. **Chemical control (last resort):**
   - Sucking pests: Imidacloprid 0.3ml/L water
   - Caterpillars: Chlorpyrifos 2ml/L water
   - Fungal disease: Mancozeb 2.5g/L water

⚠️ Always wear protective gear when spraying chemicals!""",

        'hi': """🐛 **कीट नियंत्रण गाइड:**

**एकीकृत कीट प्रबंधन:**
1. **नियमित निगरानी** - सप्ताह में दो बार खेत देखें
2. **चिपचिपे जाल** - सफेद मक्खी के लिए पीले जाल
3. **जैविक नियंत्रण** - Trichogramma कार्ड का उपयोग
4. **नीम का छिड़काव** - 5% नीम पत्ती का अर्क
5. **रासायनिक नियंत्रण:**
   - चूसने वाले कीट: Imidacloprid 0.3ml/लीटर पानी

⚠️ रसायनों का छिड़काव करते समय सुरक्षा उपकरण पहनें!""",

        'te': """🐛 **చీడపీడల నియంత్రణ గైడ్:**

**సమీకృత చీడపీడల నిర్వహణ:**
1. **నిరంతర పర్యవేక్షణ** - వారానికి రెండు సార్లు పొలం చూడండి
2. **అంటుకునే బోనులు** - తెల్ల ఈగకు పసుపు రంగు బోనులు
3. **జీవ నియంత్రణ** - Trichogramma కార్డులు
4. **వేప పిచికారీ** - 5% వేప ఆకు సారాయి
5. **రసాయన నియంత్రణ:**
   - పీల్చే చీడలు: Imidacloprid 0.3ml/లీటరు నీటిలో

⚠️ రసాయనాలు చల్లేటప్పుడు రక్షణ సామగ్రి ధరించండి!"""
    }
    return advice.get(lang, advice['en'])


def _get_fertilizer_advice(lang):
    advice = {
        'en': """🌱 **Fertilizer Application Guide:**

**Basic Principle - NPK for Indian Crops:**
| Crop | N (kg/ha) | P (kg/ha) | K (kg/ha) |
|------|-----------|-----------|-----------|
| Rice | 120 | 60 | 60 |
| Wheat | 120 | 60 | 40 |
| Cotton | 150 | 75 | 75 |
| Vegetables | 80-100 | 50 | 50 |

**Application Tips:**
• Apply 50% N as basal dose at sowing
• Remaining 50% N in 2 splits (30 days and 60 days after sowing)
• Apply full P and K as basal dose
• Use organic compost (5-10 tons/ha) to improve soil health

🌿 Organic option: Use vermicompost + FYM for sustainable farming!""",

        'hi': """🌱 **उर्वरक उपयोग गाइड:**

**भारतीय फसलों के लिए NPK:**
• चावल: N-120, P-60, K-60 किग्रा/हेक्टेयर
• गेहूं: N-120, P-60, K-40 किग्रा/हेक्टेयर
• कपास: N-150, P-75, K-75 किग्रा/हेक्टेयर

**उपयोग के टिप्स:**
• बुवाई के समय 50% N, P और K का आधार खुराक दें
• बाकी N दो हिस्सों में 30 और 60 दिन बाद दें

🌿 जैविक विकल्प: केंचुआ खाद + FYM से टिकाऊ खेती करें!""",

        'te': """🌱 **ఎరువుల వినియోగ గైడ్:**

**భారతీయ పంటలకు NPK:**
• వరి: N-120, P-60, K-60 కిలోలు/హెక్టారు
• గోధుమ: N-120, P-60, K-40 కిలోలు/హెక్టారు
• పత్తి: N-150, P-75, K-75 కిలోలు/హెక్టారు

**వినియోగ చిట్కాలు:**
• విత్తే సమయంలో 50% N, P మరియు K బేస్ మోతాదు ఇవ్వండి
• మిగిలిన N 30 మరియు 60 రోజుల తర్వాత రెండు భాగాలుగా ఇవ్వండి

🌿 సేంద్రియ ప్రత్యామ్నాయం: వర్మీకంపోస్ట్ + FYM తో స్థిరమైన వ్యవసాయం!"""
    }
    return advice.get(lang, advice['en'])


def _get_irrigation_advice(lang):
    advice = {
        'en': """💧 **Irrigation Management Guide:**

**Water-Saving Techniques:**
1. **Drip Irrigation** - Saves 40-60% water, ideal for vegetables & orchards
2. **Sprinkler System** - Good for wheat, groundnuts, saves 25-35%
3. **Furrow Irrigation** - Traditional but efficient for row crops

**Critical Growth Stages (don't miss!):**
• Rice: Tillering, Panicle initiation, Flowering
• Wheat: Crown root, Tillering, Jointing, Flowering, Grain filling
• Cotton: Square formation, Flowering, Boll development

**Signs of water stress:**
🔴 Leaf rolling/wilting in morning = Urgent irrigation needed
🟡 Bluish-green leaf color = Mild stress, irrigate soon

💡 Government subsidy available for drip/sprinkler systems - check PM-KUSUM scheme!""",

        'hi': """💧 **सिंचाई प्रबंधन गाइड:**

**पानी बचाने की तकनीकें:**
1. **ड्रिप सिंचाई** - 40-60% पानी बचाती है
2. **स्प्रिंकलर** - गेहूं के लिए अच्छा, 25-35% बचत
3. **फरो सिंचाई** - पंक्ति फसलों के लिए कुशल

**महत्वपूर्ण विकास चरण:**
• धान: कंसे, बाली निकलना, फूल आना
• गेहूं: जड़ें, कंसे, जोड़, फूल, दाना भरना

💡 ड्रिप/स्प्रिंकलर के लिए सरकारी सब्सिडी उपलब्ध है!""",

        'te': """💧 **నీటిపారుదల నిర్వహణ గైడ్:**

**నీటిని ఆదా చేసే సాంకేతికతలు:**
1. **చుక్క నీటిపారుదల** - 40-60% నీరు ఆదా అవుతుంది
2. **స్ప్రింక్లర్** - గోధుమకు అనుకూలం, 25-35% ఆదా
3. **నాలా నీటిపారుదల** - వరుస పంటలకు సమర్థంగా

**ముఖ్యమైన వృద్ధి దశలు:**
• వరి: పిలకలు, పానికల్ మొదలు, పూత
• గోధుమ: వేళ్ళు, పిలకలు, కీళ్ళు, పూత, గింజ నింపడం

💡 చుక్క/స్ప్రింక్లర్ కోసం ప్రభుత్వ సబ్సిడీ అందుబాటులో ఉంది!"""
    }
    return advice.get(lang, advice['en'])


def _get_weather_advice(lang):
    advice = {
        'en': """🌦️ **Weather-Based Farming Advice:**

**Before Heavy Rain:**
• Don't apply fertilizers (will wash away)
• Avoid pesticide spraying
• Ensure proper field drainage

**During Dry Spell:**
• Prioritize irrigation for critical growth stages
• Apply mulch to retain soil moisture
• Opt for drought-tolerant varieties next season

**After Rain:**
• Best time to apply fertilizers (soil moisture helps absorption)
• Monitor for fungal diseases
• Do intercultural operations when soil is workable

**Seasonal Calendar:**
🌱 Kharif: June-October (Rice, Cotton, Maize, Soybean)
🌾 Rabi: November-March (Wheat, Mustard, Gram)
☀️ Zaid: March-June (Vegetables, Watermelon)

💡 Always check IMD weather forecast before major farming operations!""",

        'hi': """🌦️ **मौसम आधारित खेती सलाह:**

**भारी बारिश से पहले:**
• उर्वरक न डालें (बह जाएंगे)
• कीटनाशक छिड़काव न करें
• खेत में उचित जल निकासी सुनिश्चित करें

**सूखे के दौरान:**
• महत्वपूर्ण विकास चरणों में सिंचाई को प्राथमिकता दें
• नमी बनाए रखने के लिए मल्च लगाएं

💡 IMD मौसम पूर्वानुमान हमेशा देखें!""",

        'te': """🌦️ **వాతావరణ ఆధారిత వ్యవసాయ సలహా:**

**భారీ వర్షానికి ముందు:**
• ఎరువులు వేయవద్దు (కొట్టుకుపోతాయి)
• పురుగుమందుల పిచికారీ చేయవద్దు
• పొలంలో సరైన నీటి పారుదల ఏర్పాటు చేయండి

**వర్షాభావ సమయంలో:**
• ముఖ్యమైన వృద్ధి దశలలో నీటిపారుదలకు ప్రాధాన్యం ఇవ్వండి
• మట్టి తేమ నిలుపుకోవడానికి మల్చ్ వేయండి

💡 IMD వాతావరణ సూచనలు ఎల్లప్పుడూ తనిఖీ చేయండి!"""
    }
    return advice.get(lang, advice['en'])


def _get_soil_advice(lang):
    advice = {
        'en': """🌍 **Soil Health Management:**

**Soil Testing (Do this first!):**
• Test soil every 2-3 years
• Check: pH, NPK levels, organic carbon, micronutrients
• Cost: Rs. 100-200 at Soil Testing Lab

**pH Management:**
• Acidic soil (pH < 6): Apply lime 2-4 tons/ha
• Alkaline soil (pH > 8): Apply gypsum or sulfur

**Improving Soil Health:**
1. Add organic matter: Compost, FYM, vermicompost
2. Practice crop rotation
3. Grow green manure crops (Dhaincha, Sunn hemp)
4. Avoid excessive tillage
5. Maintain soil cover (mulching)

**Signs of Good Soil:**
✅ Dark color, earthy smell
✅ Earthworms present
✅ Crumbles easily when moist

💡 Soil health card scheme: Get free soil testing from Govt!""",

        'hi': """🌍 **मिट्टी स्वास्थ्य प्रबंधन:**

**मिट्टी परीक्षण (पहले यह करें!):**
• हर 2-3 साल में मिट्टी का परीक्षण करें
• pH, NPK, जैविक कार्बन की जांच करें

**pH प्रबंधन:**
• अम्लीय मिट्टी (pH < 6): 2-4 टन/हेक्टेयर चूना डालें
• क्षारीय मिट्टी (pH > 8): जिप्सम या सल्फर डालें

**मिट्टी स्वास्थ्य सुधार:**
1. जैविक पदार्थ डालें: खाद, FYM
2. फसल चक्र अपनाएं
3. हरी खाद की फसल उगाएं

💡 सरकार से मुफ्त मिट्टी परीक्षण पाएं!""",

        'te': """🌍 **మట్టి ఆరోగ్య నిర్వహణ:**

**మట్టి పరీక్ష (ముందు ఇది చేయండి!):**
• ప్రతి 2-3 సంవత్సరాలకు మట్టి పరీక్ష చేయించండి
• pH, NPK స్థాయిలు, సేంద్రియ కార్బన్ తనిఖీ చేయండి

**pH నిర్వహణ:**
• ఆమ్ల మట్టి (pH < 6): 2-4 టన్నులు/హెక్టారు సున్నం వేయండి
• క్షార మట్టి (pH > 8): జిప్సం లేదా సల్ఫర్ వేయండి

**మట్టి ఆరోగ్యం మెరుగుపరచడం:**
1. సేంద్రియ పదార్థం వేయండి: కంపోస్ట్, FYM
2. పంట మార్పిడి పాటించండి
3. పచ్చిరొట్ట పంటలు పండించండి

💡 ప్రభుత్వం నుండి ఉచిత మట్టి పరీక్ష పొందండి!"""
    }
    return advice.get(lang, advice['en'])


def _get_cotton_advice(lang):
    advice = {
        'en': """🌿 **Cotton Farming Guide:**

• **Sowing Time:** April-May (with pre-monsoon showers)
• **Varieties:** Bt Cotton hybrids recommended (Brahma, Bunny, NHH-44)
• **Spacing:** 90 x 60 cm or 90 x 45 cm
• **Fertilizer:** N-150, P-75, K-75 kg/ha

**Critical Pest Management:**
• Pink Bollworm: Major threat to Bt cotton
• Bollworm: Use Bt spray if >5% damage
• Sucking pests: Imidacloprid 0.3ml/L in early stages

**Important:**
• Avoid planting cotton after cotton (disease buildup)
• Cotton-Wheat or Cotton-Gram rotation is best
• Don't use excessive insecticides (leads to resistance)

💡 Pink Bollworm resistant varieties available now - ask your agricultural officer!""",
        'hi': """🌿 **कपास की खेती गाइड:**

• **बुवाई समय:** अप्रैल-मई
• **किस्में:** Bt कपास हाइब्रिड (ब्रह्मा, बनी)
• **दूरी:** 90 x 60 सेमी
• **खाद:** N-150, P-75, K-75 किग्रा/हेक्टेयर

**मुख्य कीट:**
• गुलाबी सुंडी: Bt कपास के लिए बड़ा खतरा
• रस चूसने वाले कीट: शुरुआत में Imidacloprid

💡 गुलाबी सुंडी प्रतिरोधी किस्में अब उपलब्ध हैं!""",
        'te': """🌿 **పత్తి సాగు గైడ్:**

• **విత్తన సమయం:** ఏప్రిల్-మే
• **రకాలు:** Bt పత్తి హైబ్రిడ్లు
• **దూరం:** 90 x 60 సెంటిమీటర్లు
• **ఎరువులు:** N-150, P-75, K-75 కిలోలు/హెక్టారు

**ముఖ్య చీడలు:**
• పింక్ బోల్‌వార్మ్: Bt పత్తికి పెద్ద ముప్పు
• పీల్చే చీడలు: మొదట్లో Imidacloprid

💡 పింక్ బోల్‌వార్మ్ నిరోధక రకాలు ఇప్పుడు అందుబాటులో ఉన్నాయి!"""
    }
    return advice.get(lang, advice['en'])


def get_daily_tip(language='en'):
    """Get a daily farming tip"""
    tips = {
        'en': [
            "🌱 Test your soil pH before the sowing season. Most crops prefer pH 6-7.",
            "💧 Irrigate during early morning or evening to reduce evaporation losses.",
            "🐛 Use yellow sticky traps to monitor pest populations in your field.",
            "🌿 Apply neem cake (250 kg/ha) at transplanting to prevent soil pests.",
            "📊 Maintain a farm diary to track expenses, yields, and activities.",
        ],
        'hi': [
            "🌱 बुवाई से पहले मिट्टी का pH परीक्षण करें। अधिकांश फसलें pH 6-7 पसंद करती हैं।",
            "💧 वाष्पीकरण कम करने के लिए सुबह या शाम को सिंचाई करें।",
            "🐛 खेत में कीट की निगरानी के लिए पीले चिपचिपे जाल का उपयोग करें।",
            "🌿 मिट्टी के कीटों को रोकने के लिए नीम की खली (250 किग्रा/हेक्टेयर) लगाएं।",
        ],
        'te': [
            "🌱 విత్తే ముందు మట్టి pH పరీక్ష చేయండి. చాలా పంటలు pH 6-7 ఇష్టపడతాయి.",
            "💧 ఆవిరి నష్టం తగ్గించడానికి తెల్లవారు జామున లేదా సాయంత్రం నీరు పెట్టండి.",
            "🐛 చీడలను పర్యవేక్షించడానికి పసుపు రంగు అంటుకునే బోనులు వాడండి.",
            "🌿 మట్టి చీడలను నివారించడానికి వేప పిండి (250 కిలోలు/హెక్టారు) వేయండి.",
        ]
    }
    import random
    lang_tips = tips.get(language, tips['en'])
    return random.choice(lang_tips)
