import json
from google import genai
from google.genai import types

# 1. Setup
client = genai.Client(api_key="AIzaSyDoNkToIuwlX9pE1EgZn-57jfJdH0LiLW8")

# REVISED SYSTEM PROMPT: Focused on brevity and "no fluff"
SYSTEM_PROMPT = """
You are 'Arlo', the equipment lead at Stapleton Adventure Store. 
You are rugged, efficient, and extremely succinct. 

STRICT RESPONSE GUIDELINES:
1. BE BRIEF: Keep your entire response under 4 sentences total.
2. Please ask the user an  additonal question after the suggestion for more detail.
3. DIRECT ANSWERS: If a user asks a question, answer it in the first sentence.
4. INVENTORY ONLY: Only recommend gear from the provided STORE_INVENTORY.
5. FORMAT: Use a 'Premium' and 'Value' label if providing options. Do not use long paragraphs.
6. Please always provide the price and URL for the Premium and Value option. 
7. NEVER mention Amazon, MEC, or other outside retailers.
"""

model_id = 'gemini-2.5-flash'

class ConciseStapletonBot:
    def __init__(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            self.inventory = json.load(f)
        
        # Initialize chat with the strict system instruction
        self.chat_session = client.chats.create(
            model=model_id,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3 # Lower temperature makes the bot more predictable/pointed
            )
        )

    def start_chat(self):
        print("--- Arlo is online (Brief Mode). Type 'quit' to exit. ---")
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['quit', 'exit']: break

            # Send the inventory context with every message to keep Arlo grounded
            # We only send a slice of the inventory to save on tokens if the file is massive
            inventory_context = json.dumps(self.inventory[:30], indent=2)
            full_query = f"INVENTORY: {inventory_context}\n\nUSER: {user_input}"
            
            try:
                response = self.chat_session.send_message(full_query)
                print(f"\nArlo: {response.text}\n")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    bot = ConciseStapletonBot('products.json')
    bot.start_chat()
