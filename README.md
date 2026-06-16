<div align="center">

# 🌾 Agriculture AI Assistant

### An Intelligent Farming Companion — Mandi Prices, Crop Diseases, Weather, Government Schemes & More

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/spaces/suszi-2/AGRICULTURE_BOT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![RAG](https://img.shields.io/badge/RAG-Powered-22C55E?style=for-the-badge&logo=buffer&logoColor=white)]()
[![Multilingual](https://img.shields.io/badge/Multilingual-Supported-F97316?style=for-the-badge&logo=googletranslate&logoColor=white)]()

<br/>

> *"Enter your farming question in your own language — about a crop disease, weather forecast, government subsidy, or market price — and get a short, clear answer instantly."*

</div>

---

## 🌱 What Is This?

**Agriculture AI Assistant** is a conversational AI agent built specifically for Indian farmers. It combines **live data feeds**, **RAG (Retrieval-Augmented Generation)**, and **LLM reasoning** to answer real farming questions in plain language — no technical knowledge needed.

Whether a farmer wants to know today's tomato price at the local mandi, how to treat a fungal disease in wheat, what the weather will be like for the next 3 days, or which government scheme they qualify for — this bot answers it all in one place.

> ⚠️ **Note:** This bot provides advisory information only. It does not process transactions or official government applications.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 📈 **Live Mandi Prices** | Real-time crop prices from mandis across India |
| 🌦️ **Weather Forecasts** | Location-based weather outlook to help plan farming activities |
| 🌿 **Crop Disease Detection** | Identify diseases from symptoms and get treatment advice |
| 💊 **Treatment Recommendations** | Suggest pesticides, organic remedies, and preventive measures |
| 🏛️ **Government Schemes** | Information on PM-Kisan, crop insurance, subsidies & more |
| 🧠 **RAG (Retrieval-Augmented Generation)** | Pulls accurate info from a curated agricultural knowledge base |
| 💬 **Persistent Memory** | Remembers your crop, location, and past questions across the session |
| 🛡️ **Guardrails** | Filters out irrelevant or harmful queries — stays focused on farming |
| 🌐 **Multilingual Support** | Understands questions in regional Indian languages |

---

## 🏗️ Architecture & Tech Stack

```
┌──────────────────────────────────────────────────────────────────┐
│                     Gradio / Chat Frontend                       │
│              (Multilingual Conversational Interface)             │
└───────────────────────────────┬──────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────┐
│                        Guardrail Layer                           │
│         (Filters non-agriculture queries, toxic input)           │
└───────────────────────────────┬──────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────┐
│                      LLM Core (Agent)                            │
│         RAG Retrieval + Tool Calling + Memory + Reasoning        │
└───┬──────────┬───────────┬────────────┬───────────┬─────────────┘
    │          │           │            │           │
┌───▼───┐ ┌───▼───┐ ┌─────▼──┐ ┌──────▼──┐ ┌─────▼──────┐
│ Mandi │ │Weather│ │Disease │ │ Scheme  │ │Persistent  │
│ Price │ │  API  │ │   KB   │ │   KB    │ │  Memory    │
│  API  │ │  Tool │ │ (RAG)  │ │  (RAG)  │ │  Storage   │
└───────┘ └───────┘ └────────┘ └─────────┘ └────────────┘
               │          │          │
        ┌──────▼──────────▼──────────▼──────┐
        │         Response Builder            │
        │  (Plain language, farmer-friendly)  │
        └─────────────────────────────────────┘
```

### 🛠️ Technologies Used

- **Frontend:** Gradio (HuggingFace Spaces)
- **LLM:** Large Language Model with tool calling & reasoning
- **RAG Pipeline:** Vector store + embedding model + retrieval chain
- **Guardrails:** Custom input/output filtering for agriculture-only scope
- **Memory:** Session-level persistent conversation memory
- **Deployment:** HuggingFace Spaces (Docker)
- **Language:** Python 3.10+

---

## 💬 Example Conversations

```
👨‍🌾 Farmer: Meri wheat mein pele rang ke dhabbe aa rahe hain, kya problem hai?

🤖 Bot:    Yeh Yellow Rust (Puccinia striiformis) ke symptoms lagte hain.
           Ilaaj:
           • Propiconazole 25% EC — 1ml per litre paani mein spray karein
           • 10-15 din mein doosra spray zaroor karein
           • Infected patte hatao aur door phenk do

───────────────────────────────────────────────────

👨‍🌾 Farmer: Today's tomato price in Nashik mandi?

🤖 Bot:    📈 Nashik Mandi — Tomato Price (Today)
           • Min: ₹820/quintal
           • Max: ₹1,240/quintal
           • Modal: ₹1,050/quintal
           Last updated: 2 hours ago

───────────────────────────────────────────────────

👨‍🌾 Farmer: What government schemes can I get for drip irrigation?

🤖 Bot:    Here are schemes available for drip irrigation:

           1. PM Krishi Sinchai Yojana (PMKSY)
              • 55% subsidy for small/marginal farmers
              • Apply at: pmksy.gov.in

           2. National Horticulture Mission
              • Up to 40% subsidy on micro-irrigation
              • Contact your local Krishi Vigyan Kendra
```

---

## 🧠 How the AI Works

This project demonstrates several advanced AI engineering techniques:

**1. RAG (Retrieval-Augmented Generation)**
Agricultural knowledge (diseases, treatments, schemes) is stored in a vector database. When a farmer asks a question, the most relevant documents are retrieved and fed to the LLM — so answers are grounded in real facts, not hallucinations.

**2. Guardrails**
A filtering layer sits between the user and the LLM. It detects and blocks off-topic queries (unrelated to farming), ensuring the bot stays focused and trustworthy. This is a critical safety and reliability feature in production AI systems.

**3. Persistent Memory**
The bot remembers context within a session — if you said "I grow wheat in Punjab" earlier, it uses that when answering your next question about fertilisers or weather, without you having to repeat yourself.

**4. Tool Calling**
For live data (mandi prices, weather), the LLM dynamically calls external APIs mid-conversation and reasons over the returned data before responding.

**5. Multilingual Understanding**
The system handles queries in Hindi, regional languages, and English — making it accessible to farmers who are not comfortable with English-only interfaces.

---

## 📁 Project Structure

```
agriculture-bot/
│
├── app.py                    # Full application — LLM agent, RAG pipeline,
│                             # tool calling, memory, guardrails & Gradio UI
├── requirements.txt          # All Python dependencies
└── README.md                 # Project documentation
```


> 💡 The entire agent logic — including RAG retrieval, tool calling, guardrails, and memory — is implemented inside `app.py` as a single-file deployment, optimised for HuggingFace Spaces.

---

## 🎯 Skills Demonstrated

This project showcases the following for potential employers:

- ✅ **RAG Pipeline** — End-to-end retrieval-augmented generation from document ingestion to response
- ✅ **LLM Tool Calling** — Dynamic API calls triggered by the LLM based on user intent
- ✅ **Guardrails Implementation** — Production-grade input/output safety filtering
- ✅ **Persistent Memory** — Stateful, context-aware conversations
- ✅ **Domain-Specific AI** — Tuning an LLM for a specialized vertical (agriculture)
- ✅ **Multilingual NLP** — Handling regional language inputs
- ✅ **HuggingFace Deployment** — Docker-based deployment on HF Spaces
- ✅ **Real-time API Integration** — Live mandi prices and weather data

---

## 🌍 Impact & Use Case

India has **140 million+ farming households**. Most lack easy access to:
- Real-time crop prices before selling at mandis
- Quick disease diagnosis without waiting for an agronomist
- Awareness of government subsidies they qualify for

This bot bridges that gap with a simple chat interface — no app install, no login, just ask in your own language and get an answer.

---

## 🔮 Future Roadmap

- [ ] Voice input support (farmers often prefer speaking over typing)
- [ ] Image-based disease detection (upload a photo of the crop)
- [ ] SMS/WhatsApp integration for feature phone users
- [ ] Crop yield prediction based on weather + soil data
- [ ] Personalised scheme eligibility checker
- [ ] Offline mode for low-connectivity rural areas

---

## 🙋‍♂️ About the Developer

Built with ❤️ for Indian farmers by **[SHAKSHI SONI]**

I build AI applications that solve real problems for real people. This project demonstrates my ability to combine RAG, LLM agents, guardrails, and live data APIs into a production-ready system deployed on HuggingFace.

📫 **Connect with me:**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin)](https://linkedin.com/in/yourprofile)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Profile-FFD21E?style=flat&logo=huggingface&logoColor=black)](https://huggingface.co/suszi-2)


---

<div align="center">

**⭐ Star this repo if you found it useful — it helps a lot!**

*Built to empower Indian farmers with the power of AI.*

</div>
