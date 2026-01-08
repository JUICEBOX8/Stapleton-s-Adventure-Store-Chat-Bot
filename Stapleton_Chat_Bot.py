import streamlit as st
import json
from google import genai
from google.genai import types

# 1. Page Configuration & Styling
st.set_page_config(page_title="Arlo | Stapleton Outfitter", page_icon="🌲")

# ADVENTURE GEAR HIGH-CONTRAST THEME
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&family=Roboto:wght@400;700&display=swap');

    .stApp {
        background-color: #f8f9fa; /* Very light grey */
        color: #212529; /* Dark grey text */
        font-family: 'Open Sans', sans-serif;
    }

    /* Professional Chat Bubbles */
    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        border-radius: 12px;
        border: 1px solid #dee2e6;
        padding: 15px;
        margin-bottom: 10px;
        color: #212529 !important;
    }

    /* Arlo's Specific Accent */
    [data-testid="stChatMessageAssistant"] {
        border-left: 5px solid #d35400; /* Orange signature stripe */
    }

    /* HYPERLINK STYLING - High Visibility */
    a {
        color: #d35400 !important; /* Adventure Orange */
        font-weight: 700;
        text-decoration: underline !important;
    }

    h1 {
        color: #2c3e50;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: -1px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌲 Arlo: Gear Specialist")

# 2. Setup (Using Secrets)
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# UPDATED PROMPT: Strict instruction to avoid JSON and use Markdown Links
SYSTEM_PROMPT = """
You are 'Arlo', the gear expert at Stapleton Adventure Store. 
Talk like a human expert, NOT a computer. Never show JSON code or curly brackets.

STRICT FORMATTING RULES:
1. NO JSON: Provide a clean, bulleted list for gear.
2. CLICKABLE LINKS: You MUST format every product as a Markdown hyperlink. 
   Example: [Product Name](URL)
3. PRICING: List the price immediately after the link.
4. TWO OPTIONS: Provide one 'PREMIUM' and one 'VALUE' choice.
5. BREVITY: Keep the total response under 4 sentences.
"""

# 3. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Chat Input Logic
if prompt := st.chat_input("What mission are we gearing up for?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare Inventory Context
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            inventory = json.load(f)
            # We convert JSON to a string so Arlo can read it, 
            # but we tell him NOT to repeat it back as JSON.
            inventory_context = json.dumps(inventory[:30])
    except FileNotFoundError:
        inventory_context = "Inventory not found."

    with st.chat_message("assistant"):
        full_query = f"STORE_INVENTORY_DATA: {inventory_context}\n\nUSER_REQUEST: {prompt}"
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2
            ),
            contents=[full_query]
        )
        
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
