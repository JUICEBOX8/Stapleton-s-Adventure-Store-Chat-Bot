import streamlit as st
import json
from google import genai
from google.genai import types

# 1. Page Configuration & Styling
st.set_page_config(page_title="Arlo | Stapleton Outfitter", page_icon="🌲")

# UPDATED: HIGH VISIBILITY ADVENTURE GEAR THEME
st.markdown("""
    <style>
    /* Import Adventure Gear fonts */
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&family=Roboto+Mono&display=swap');

    /* Main App Background - Light Grey for high readability */
    .stApp {
        background-color: #f4f4f4; 
        color: #1a1a1a;
        font-family: 'Open Sans', sans-serif;
    }

    /* Chat Message Bubbles */
    [data-testid="stChatMessage"] {
        background-color: #ffffff; /* Pure white bubbles */
        border: 1px solid #ddd;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        color: #1a1a1a !important;
    }

    /* Arlo's specific bubble color to differentiate */
    [data-testid="stChatMessageAssistant"] {
        background-color: #e9ecef; /* Slightly darker grey for Arlo */
    }

    /* Adventure Gear Orange Title */
    h1 {
        color: #d35400; /* Rugged Burnt Orange */
        font-family: 'Open Sans', sans-serif;
        font-weight: 800;
        text-transform: uppercase;
        border-bottom: 3px solid #d35400;
        padding-bottom: 10px;
    }

    /* High-contrast labels for Premium/Value */
    strong {
        color: #2c3e50;
        font-weight: 700;
    }
    
    /* Input box styling */
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌲 Stapleton Gear Expert")

# 2. Setup Gemini Client (Using Secrets)
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """
You are 'Arlo', the equipment lead at Stapleton Adventure Store. 
You are rugged, efficient, and extremely succinct. 

STRICT RESPONSE GUIDELINES:
1. BE BRIEF: Keep your entire response under 4 sentences total.
2. Ask one follow-up question at the end.
3. INVENTORY ONLY: Only recommend gear from the STORE_INVENTORY.
4. FORMAT: Use 'PREMIUM OPTION' and 'VALUE OPTION' as bold headers.
5. Provide the price and URL for every suggestion. 
"""

# 3. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Chat Input Logic
if prompt := st.chat_input("Ask Arlo about the right gear for your trip..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            inventory = json.load(f)
            inventory_context = json.dumps(inventory[:30], indent=2)
    except FileNotFoundError:
        inventory_context = "Inventory file missing."

    with st.chat_message("assistant"):
        full_query = f"STORE_INVENTORY: {inventory_context}\n\nUSER_REQUEST: {prompt}"
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3
            ),
            contents=[full_query]
        )
        
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
