import streamlit as st
import json
from google import genai
from google.genai import types

# 1. Page Configuration & Styling
st.set_page_config(page_title="Arlo | Stapleton Outfitter", page_icon="🌲")

st.markdown("""
    <style>
    .stApp {
        background-color: #2e3b23;
        color: white;
    }
    .stChatMessage { color: black; } /* Makes chat bubbles readable on dark green */
    </style>
    """, unsafe_allow_html=True)

st.title("🌲 Talk to Arlo")

# 2. Setup Gemini Client
# Note: For production, move this to st.secrets["GEMINI_API_KEY"]
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """
You are 'Arlo', the equipment lead at Stapleton Adventure Store. 
You are rugged, efficient, and extremely succinct. 

STRICT RESPONSE GUIDELINES:
1. BE BRIEF: Keep your entire response under 4 sentences total.
2. Please ask the user an additional question after the suggestion for more detail.
3. DIRECT ANSWERS: If a user asks a question, answer it in the first sentence.
4. INVENTORY ONLY: Only recommend gear from the provided STORE_INVENTORY.
5. FORMAT: Use a 'Premium' and 'Value' label if providing options.
6. Please always provide the price and URL for the Premium and Value option. 
7. NEVER mention Amazon, MEC, or other outside retailers.
"""

# 3. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Chat Input Logic
if prompt := st.chat_input("What gear do you need for the bush?"):
    # Add user message to state and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare Inventory Context
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            inventory = json.load(f)
            inventory_context = json.dumps(inventory[:30], indent=2)
    except FileNotFoundError:
        inventory_context = "Inventory file missing."

    # Generate Response
    with st.chat_message("assistant"):
        full_query = f"STORE_INVENTORY: {inventory_context}\n\nUSER_REQUEST: {prompt}"
        
        # We create a new chat session for each run to keep it simple for Streamlit
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3
            ),
            contents=[full_query]
        )
        
        response_text = response.text
        st.markdown(response_text)
        
    # Add assistant response to state
    st.session_state.messages.append({"role": "assistant", "content": response_text})
