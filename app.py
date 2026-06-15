import os
import json
import requests
import streamlit as st
import chromadb
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Streamlit Configuration Setup (Fixed typo here)
st.set_page_config(page_icon="🌾", page_title="AGRICULTURE ASSISTANT", layout="wide")

# Custom Agricultural Styling
st.markdown("""
<style>
    .stApp { 
        background-color: #F8F9F5; 
        color: #2B2927; 
    }
    [data-testid="stSidebar"] { 
        background-color: #EAECE4; 
    }
    h1, h2 { 
        color: #2E6F40; 
    }
    .stButton > button {
        background-color: #2E6F40;
        color: white;
        border-radius: 10px;
        border: none;
        width: 100%;
        padding: 12px;
        font-size: 14px;
    }
    .stButton > button:hover { 
        background-color: #76B947; 
        color: white; 
    }
</style>
""", unsafe_allow_html=True)

# LLM INITIALIZATION
GROQ_KEY = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_KEY)

# SYSTEM PROMPT
base_systemprompt = """You are a farmer assistant for Indian farmers.
STRICT RULES:
1. ONLY answer questions related to farming, crops, diseases, weather, government schemes, and mandi prices
2. If anyone asks anything outside farming — politely say I can only help with farming related questions
3. Never make up information — if you dont know say I dont have information on this
4. Never recommend harmful chemicals without proper safety warning
5. Always respond in the same language the farmer uses
6. Never give medical advice to humans
7. If question is unclear — ask farmer to clarify before answering
8. Answer should be short and point to point"""

# MEMORY MANAGEMENT (Persistent between app sessions)
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
    except Exception as e:
        print(f"Error saving memory: {e}")

# VECTOR DATABASE (RAG)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="agri_knowledge")

if collection.count() == 0:
    collection.add(
        documents=[
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
        ],
        ids=[str(i) for i in range(0, 30)]  
    )

# TOOLS
def weather(city: str):
    try:
        r = requests.get(f"https://wttr.in/{city}?format=j1", timeout=5)
        if r.status_code == 200:
            c = r.json()["current_condition"][0]
            return f"Weather in {city}: {c['temp_C']}C, {c['weatherDesc'][0]['value']}, Humidity: {c['humidity']}%, Wind: {c['windspeedKmph']} kmph"
        return "City not found"
    except Exception as e:
        return f"Weather not available: {str(e)}"

def search_rag(question):
    try:
        results = collection.query(query_texts=[question], n_results=2)
        return results['documents'][0] if results['documents'] else []
    except Exception:
        return []

def guardrail(question):
    try:
        result = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"""Classify this query into EXACTLY ONE category:
FARMING
UNCLEAR
NON_FARMING

Rules:
- Weather questions for farming = FARMING
- Crop diseases = FARMING
- Government schemes = FARMING
- Mandi prices = FARMING

Query: {question}

Reply ONLY the category name. Nothing else."""}]
        )
        return result.choices[0].message.content.strip()
    except Exception:
        return "FARMING"

# STREAMLIT UI SESSION STATES
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_memory()

if "input_value" not in st.session_state:
    st.session_state.input_value = ""

# SIDEBAR (Fixed typo here)
with st.sidebar:
    st.title("🌾 Agriculture Assistant")
    st.markdown("---")
    st.markdown("**What I can do:**")
    st.markdown("- Check Mandi Prices\n- Local Weather\n- Government Schemes\n- Disease Diagnosis")
    st.markdown("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        dump_memory([])
        st.rerun()
    st.markdown("---")
    st.caption("Built with RAG + Groq + Streamlit")

# MAIN PAGE HEADER
st.title("Agriculture Assistant")
st.markdown("Your smart agricultural helper — treatment advice, mandi prices, government schemes, and more.")
st.markdown("---")

# SUGGESTION QUICK-BUTTONS (Fixed column typo & updated functional logic)
st.markdown("### Try these questions:")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🌤️ Weather in Chennai"):
        st.session_state.input_value = "What is the current weather in chennai?"
        st.rerun()
with col2:
    if st.button("🌾 Wheat Price in Punjab"):
        st.session_state.input_value = "What is the mandi price of wheat in punjab?"
        st.rerun()
with col3:
    if st.button("📋 PM Schemes"):
        st.session_state.input_value = "what is PM scheme of government?"
        st.rerun()
with col4:
    if st.button("🍂 Tomato Yellow Spots"):
        st.session_state.input_value = "my tomato plant leaves are turning dry with yellow spots in it what should i do?"
        st.rerun()

# DISPLAY CHAT HISTORY
for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(chat["user"])
    with st.chat_message("assistant"):
        st.write(chat["bot"])

# INTERACTIVE CHAT INPUT
user_input = st.chat_input("Ask a farming question...", key="main_chat_input")

# Use input value if set by quick buttons
if st.session_state.input_value and not user_input:
    user_input = st.session_state.input_value
    st.session_state.input_value = "" # Clear prefill flag

if user_input:
    # Display user query immediately
    with st.chat_message("user"):
        st.write(user_input)
        
    # Process through safety guardrails
    category = guardrail(user_input)
    
    if category == "NON_FARMING":
        reply = "I can only help with farming-related questions."
    elif category == "UNCLEAR":
        reply = "Please provide more details or clarify your farming question."
    else:
        # Fetch data via RAG context
        context = search_rag(user_input)
        context_text = " ".join(context) if context else ""

        current_systemprompt = base_systemprompt
        if context_text:
            current_systemprompt += f"\n\nRelevant Agricultural Knowledge:\n{context_text}"

        try:
            # Call Groq endpoint
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": current_systemprompt},
                    {"role": "user", "content": f"Context/Reference Material:\n{context_text}\n\nQuestion: {user_input}"}
                ]
            )
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            reply = f"Sorry, I encountered an error generating your answer. ({e})"

    # Display Bot Response
    with st.chat_message("assistant"):
        st.write(reply)
        
    # Save step records to history state & file
    st.session_state.chat_history.append({"user": user_input, "bot": reply})
    dump_memory(st.session_state.chat_history)
