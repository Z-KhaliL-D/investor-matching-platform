# test_llama.py

import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Simple test prompt
prompt = "Name three well-known venture capital firms in AI startups."

try:
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": prompt}
        ],
    )

    print("\n🧠 Llama response:")
    print(completion.choices[0].message.content)

except Exception as e:
    print("❌ Error:", e)
