import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
print("Loaded key:", os.getenv("GROQ_API_KEY"))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def query_llama(prompt: str):
    """Send a prompt to the Llama-3.1-8B-Instant model and return the response."""
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are an expert startup advisor that matches startups with investors."},
            {"role": "user", "content": prompt}
        ],
    )
    return completion.choices[0].message.content
