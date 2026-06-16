
from groq import Groq
import json
import requests
import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

# LLM
api_key = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=api_key)

systemprompt = """You are a farmer assistant for Indian farmers.
STRICT RULES:
1. ONLY answer questions related to farming, crops, diseases, weather, government schemes, and mandi prices
2. If anyone asks anything outside farming — politely say I can only help with farming related questions
3. Never make up information — if you dont know say I dont have information on this
4. Never recommend harmful chemicals without proper safety warning
5. Always respond in the same language the farmer uses
6. Never give medical advice to humans
7. If question is unclear — ask farmer to clarify before answering
8. Answer should be short and point to point"""

# memory
def dumpmemory(data):
    with open("farmer_memory.json", "w") as f:
        json.dump(data, f)

def loadmemory():
    try:
        with open("farmer_memory.json", "r") as f:
            return json.load(f)
    except:
        return []

# rag
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
        ids=[str(i) for i in range(1, 31)]
    )

# functions
def weather(location):
    """Get weather for a location"""
    try:
        clean_query = location.replace("?", "").replace(".", "").strip()
        if not clean_query:
            return "Please specify a location"
        response = requests.get(f"https://wttr.in/{clean_query}?format=j1", timeout=5)
        if response.status_code == 200:
            data = response.json()
            current = data['current_condition'][0]
            temp = current['temp_C']
            desc = current['weatherDesc'][0]['value']
            return f"📍 {clean_query}: {temp}°C, {desc}"
        else:
            return "Weather not available"
    except Exception as e:
        print(f"[DEBUG] Weather error: {e}")
        return "Weather not available right now"

def mandi_price(crop, state):
    try:
        url = f"https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=579b464db66ec23bdd000001cdd3946e44ce4aab825d41931caae&format=json&filters[commodity]={crop}&filters[state]={state}"
        response = requests.get(url, timeout=5)
        shak = response.json()
        record = shak["records"][0]
        return f"Crop: {crop} | Market: {record['market']} | Price: {record['modal_price']} rupees"
    except Exception as e:
        return f"Sorry, I could not find price for {crop} in {state} right now."

def search_knowledge(question):
    try:
        results = collection.query(query_texts=[question], n_results=2)
        return results["documents"][0]
    except Exception as e:
        return []

def guardrail(question):
    """Classify question into FARMING, UNCLEAR, or NON_FARMING"""
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
        category = result.choices[0].message.content.strip()
        return category
    except Exception as e:
      return "FARMING"  

# load memory
conversation_history = loadmemory()

print("hello!!! I am your agriculture assisant")
print(" How can I help you")
print("Type quit to exit")
print()

# main loop
while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "quit":
        dumpmemory(conversation_history)
        print("Saved! Bye bye")
        break

    if not user_input:
        continue
    category = guardrail(user_input)

    if category == "NON_FARMING":
        reply = "I only help with farming questions."
        print(f"Bot: {reply}")
        print()
        continue

    if category == "UNCLEAR":
        reply = "Please give more details about your farming question."
        print(f"Bot: {reply}")
        print()
        continue


    context = search_knowledge(user_input)
    context_text = " ".join(context) if context else ""

    weatherinfo = ""
    if any(w in user_input.lower() for w in ["weather", "rain", "temperature", "mausam", "barish", "garm", "thandi"]):

        parts = user_input.lower().split()
        location = "Mumbai"  
        if "in" in parts:
            idx = parts.index("in")
            if idx + 1 < len(parts):
                location = " ".join(parts[idx+1:]).replace("?", "").strip()
        weatherinfo = f"\n\nCurrent Weather Info:\n{weather(location)}"

    # Build prompt
    prompt = systemprompt
    if context_text:
        prompt += f"\n\nRelevant Agricultural Knowledge:\n{context_text}"
    if weatherinfo:
        prompt += weatherinfo
    prompt += f"\n\nFarmer's Question: {user_input}"

    try:
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )

        bot_reply = response.choices[0].message.content.strip()

        if any(w in bot_reply.lower() for w in ["spray", "pesticide", "chemical", "fungicide", "insecticide"]):
            bot_reply += "\n\n☢️ Safety Warning: Always wear gloves and a mask when spraying chemicals. Keep children and pets away. Follow label instructions carefully."

        conversation_history.append({
            "user": user_input,
            "bot": bot_reply,
            "timestamp": str(__import__('datetime').datetime.now())
        })
        dumpmemory(conversation_history)

        print(f"\nBot: {bot_reply}\n")
        print("-" * 50)

    except Exception as e:
        
        print(f"Bot: Sorry, I'm having trouble right now. Please try again.\n")
        print("-" * 50)
