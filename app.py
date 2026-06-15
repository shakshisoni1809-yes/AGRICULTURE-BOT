import os
import json
import requests
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Streamlit Configuration Setup
st.set_page_config(page_icon="🌾", page_title="AGRICULTURE ASSISTANT", layout="wide")

# Custom Agricultural Styling
st.markdown("""
<style>
    /* 1. Main App Background (Bone) */
    .stApp { 
        background-color: #E5D7C4; 
        color: #354024; 
    }
    
    /* 2. Sidebar (Kombu Green) */
    [data-testid="stSidebar"] { 
        background-color: #354024; 
    }
    
    /* Sidebar text uses the Bone color for crisp visibility */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label {
        color: #E5D7C4 !important;
    }
    
    /* Headings (Kombu Green) */
    h1, h2, h3 { 
        color: #354024; 
        font-weight: 700;
    }
    
    /* Action Buttons (Kombu Green) */
    .stButton > button {
        background-color: #354024;
        color: #E5D7C4;
        border-radius: 8px;
        border: none;
        width: 100%;
        padding: 12px;
        font-size: 14px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    
    /* Button Hover (Inverts the colors) */
    .stButton > button:hover { 
        background-color: #E5D7C4; 
        color: #354024;
        border: 2px solid #354024;
    }
    
    /* Chat Message Blocks (Clean Bone surfaces) */
    .stChatMessage {
        background-color: #E5D7C4 !important;
        border: 1px solid #354024;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# LLM INITIALIZATION
GROQ_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_KEY)

# SYSTEM PROMPT
base_systemprompt = """You are a farmer assistant for Indian farmers.
STRICT RULES:
1. ONLY answer questions related to farming, crops, diseases, weather, government schemes, and mandi prices.
2. If anyone asks anything outside farming — politely say I can only help with farming related questions.
3. If the user is asking for WEATHER information, reply EXACTLY with this format: "TOOL_CALL: WEATHER(city_name)"
4. If the user is asking for MANDI PRICES, reply EXACTLY with this format: "TOOL_CALL: MANDI(state_name, crop_name)"
5. Never recommend harmful chemicals without proper safety warning.
6. Always respond in the same language the farmer uses.
7. Answer should be short and point to point."""

# KNOWLEDGE BASE DICTIONARY
KNOWLEDGE_BASE = [
    "PM Kisan gives 6000 rupees per year in 3 installments to farmers with less than 2 hectares land",
    "PM Fasal Bima Yojana is crop insurance government pays if crop destroyed by flood drought or pest",
    "Kisan Credit Card gives loan up to 3 lakh rupees at 4 percent interest for seeds fertilizer equipment",
    "PM Krishi Sinchai Yojana gives subsidy for drip irrigation and sprinkler systems",
    "Soil Health Card tests soil for free and tells which fertilizer to use",
    "e-NAM is online mandi platform farmer can sell crops to buyers across India for better price",
    "Paramparagat Krishi Vikas Yojana gives 50000 rupees per hectare for switching to organic farming",
    "PM Kisan Mandhan Yojana gives 3000 rupees per month pension to farmers after age 60",
    "Rashtriya Krishi Vikas Yojana gives subsidies on equipment and agricultural infrastructure",
    "National Food Security Mission gives free high yield seeds and training for wheat rice and pulses",
    "Agricultural Mechanization scheme gives 40 to 50 percent subsidy on tractors and farming equipment",
    "PM AASHA guarantees minimum support price government buys crop at fixed price if market price falls",
    "Gramin Bhandaran Yojana gives subsidy to build storage warehouses so farmer can sell when price is good",
    "National Horticulture Mission gives subsidies for fruits and vegetables farming",
    "Kisan Vikas Patra is government investment scheme where farmers money doubles in fixed time",
    "Tomato Early Blight caused by fungus symptoms are dark brown spots on leaves treatment is spray mancozeb 2.5 grams per litre every 7 days",
    "Rice Blast caused by fungus symptoms are diamond shaped grey spots on leaves treatment is spray tricyclazole 1 gram per litre",
    "Wheat Rust caused by fungus symptoms are orange powdery spots on leaves treatment is spray propiconazole 1ml per litre",
    "Cotton Bollworm is insect symptoms are holes in cotton bolls treatment is spray spinosad or chlorpyrifos",
    "Potato Late Blight caused by fungus symptoms are water soaked dark spots treatment is spray metalaxyl mancozeb immediately",
    "Chilli Leaf Curl caused by virus spread by whitefly symptoms are curled leaves treatment is spray imidacloprid",
    "Sugarcane Red Rot caused by fungus symptoms are red color inside stem treatment is apply carbendazim",
    "Groundnut Leaf Spot caused by fungus symptoms are circular brown spots treatment is spray chlorothalonil 2 grams per litre",
    "Onion Purple Blotch caused by fungus symptoms are purple lesions on leaves treatment is spray mancozeb or iprodione",
    "Maize Downy Mildew caused by fungus symptoms are white powdery growth treatment is seed treatment with metalaxyl before planting",
    "Brinjal Shoot and Fruit Borer is insect symptoms are wilting shoots and holes in fruits treatment is spray emamectin benzoate",
    "Banana Panama Wilt caused by fungus symptoms are yellowing and wilting treatment is remove infected plant apply trichoderma to soil",
    "Mango Powdery Mildew caused by fungus symptoms are white powder on flowers treatment is spray sulfur 3 grams per litre",
    "Soybean Yellow Mosaic caused by virus symptoms are yellow patches on leaves treatment is spray thiamethoxam",
    "Coconut Root Wilt caused by phytoplasma symptoms are yellowing drooping leaves treatment is inject oxytetracycline into trunk",
]

# LIVE TOOLS
def get_weather(city: str):
    try:
        r = requests.get(f"https://wttr.in/{city}?format=j1", timeout=5)
        if r.status_code == 200:
            c = r.json()["current_condition"][0]
            return f"🌤️ Weather in {city.title()}: {c['temp_C']}°C, {c['weatherDesc'][0]['value']}, Humidity: {c['humidity']}%, Wind: {c['windspeedKmph']} kmph"
        return "City not found."
    except Exception:
        return "Weather data is currently unavailable."

def get_mandi_price(state: str, crop: str):
    try:
        # Format names to Title Case for Gov API compliance
        state_formatted = state.strip().title()
        crop_formatted = crop.strip().title()
        
        url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=579b464db66ec23bdd000001cdd3946e44ce4aab825d41931caae&format=json&filters[commodity]={crop_formatted}&filters[state]={state_formatted}"
        r = requests.get(url, timeout=5)
        data = r.json()
        
        if "records" in data and len(data["records"]) > 0:
            record = data["records"][0]
            return f"🌾 **Mandi Price Update** | State: {state_formatted} | Crop: {crop_formatted} | Market: {record['market']} | Price: ₹{record['modal_price']} per quintal."
        return f"No live market price records found for {crop_formatted} in {state_formatted} right now."
    except Exception:
        return f"Could not connect to the live price server for {crop} in {state}."

# MEMORY OPERATIONS
def load_memory():
    try:
        with open("agri.json", "r") as f:
            return json.load(f)
    except Exception:
        return []

def dump_memory(data):
    try:
        with open("agri.json", "w") as f:
            json.dump(data, f)
    except Exception:
        pass

def search_knowledge(question):
    keywords = [word.lower() for word in question.split() if len(word) > 3]
    matches = []
    for doc in KNOWLEDGE_BASE:
        score = sum(1 for keyword in keywords if keyword in doc.lower())
        if score > 0:
            matches.append((score, doc))
    matches.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in matches[:2]]

def guardrail(question):
    try:
        result = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"""Classify this query into EXACTLY ONE category:
FARMING
UNCLEAR
NON_FARMING

Query: {question}
Reply ONLY the category name."""}]
        )
        return result.choices[0].message.content.strip()
    except Exception:
        return "FARMING"

# STREAMLIT UI SETUP
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_memory()

if "input_value" not in st.session_state:
    st.session_state.input_value = ""

# SIDEBAR
with st.sidebar:
    st.title("🌾 Agriculture Assistant")
    st.markdown("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        dump_memory([])
        st.rerun()

# HEADERS
st.title("Agriculture Assistant")
st.markdown("Your smart agricultural helper — treatment advice, live mandi prices, government schemes, and more.")
st.markdown("---")

# QUICK SUGGESTIONS
st.markdown("### Try these questions:")
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🌤️ Weather in Chennai"):
        st.session_state.input_value = "What is the current weather in Chennai?"
        st.rerun()
with col2:
    if st.button("🌾 Wheat Price in Punjab"):
        st.session_state.input_value = "What is the mandi price of Wheat in Punjab?"
        st.rerun()
with col3:
    if st.button("📋 PM Schemes"):
        st.session_state.input_value = "What is PM scheme of government?"
        st.rerun()
with col4:
    if st.button("🍂 Tomato Yellow Spots"):
        st.session_state.input_value = "My tomato plant leaves are turning dry with yellow spots in it, what should I do?"
        st.rerun()

# CHAT COMPONENT RENDER
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["user"])
    with st.chat_message("assistant"):
        st.write(chat["bot"])

user_input = st.chat_input("Ask a farming question...")

if st.session_state.input_value and not user_input:
    user_input = st.session_state.input_value
    st.session_state.input_value = "" 

if user_input:
    with st.chat_message("user"):
        st.write(user_input)
        
    category = guardrail(user_input)
    
    if category == "NON_FARMING":
        reply = "I can only help with farming-related questions."
    elif category == "UNCLEAR":
        reply = "Please provide more details or clarify your farming question."
    else:
        context = search_knowledge(user_input)
        context_text = " ".join(context) if context else ""

        current_systemprompt = base_systemprompt
        if context_text:
            current_systemprompt += f"\n\nRelevant Agricultural Knowledge:\n{context_text}"

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": current_systemprompt},
                    {"role": "user", "content": f"Question: {user_input}"}
                ]
            )
            raw_reply = response.choices[0].message.content.strip()
            
            # INTERCEPT TOOL CALLS FOR LIVE DATA
            if "TOOL_CALL: WEATHER" in raw_reply:
                city = raw_reply.split("WEATHER(")[1].split(")")[0]
                reply = get_weather(city)
            elif "TOOL_CALL: MANDI" in raw_reply:
                params = raw_reply.split("MANDI(")[1].split(")")[0].split(",")
                state = params[0].strip()
                crop = params[1].strip()
                reply = get_mandi_price(state, crop)
            else:
                reply = raw_reply

        except Exception as e:
            reply = f"Sorry, I encountered an error generating your answer. ({e})"

    with st.chat_message("assistant"):
        st.write(reply)
        
    st.session_state.chat_history.append({"user": user_input, "bot": reply})
    dump_memory(st.session_state.chat_history)
