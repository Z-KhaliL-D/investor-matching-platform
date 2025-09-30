from flask import Flask, request, jsonify
from flask_cors import CORS
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import requests

app = Flask(__name__)
CORS(app)

# === Config ===
QDRANT_URL = "https://ed07d684-8e1d-499f-a564-a3a6ce5d6280.eu-central-1-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.wQmL1PrTpbytO3tzurKM56jWG9bUMFFscUQierUlkX8"
COLLECTION_NAME = "investors"

# === Connect to Qdrant ===
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# === Load same model used for embeddings ===
model = SentenceTransformer("./tsdae_finetuned_investors")


# === Helper: Run Phi via Ollama API ===
def run_phi(prompt: str) -> str:
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi:latest",   # matches your ollama list
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "⚠️ No response from Phi.")
    except Exception as e:
        return f"⚠️ Error contacting Phi: {str(e)}"


# === Route: Match startup to investors ===
@app.route("/match", methods=["POST"])
def match_startup():
    """
    🚧 TODO: Matching logic to be implemented here.
    - Parse request (profile + description)
    - Encode with model
    - Query Qdrant
    - Return top matches
    """
    return jsonify({"message": "⚠️ Matching logic not implemented yet."}), 501


# === Route: Chat with Phi-2 ===
@app.route("/chat", methods=["POST"])
def chat_agent():
    data = request.get_json()
    user_msg = data.get("message")
    if not user_msg:
        return jsonify({"error": "Missing message"}), 400

    prompt = f"You are Phi-2. Answer concisely.\nUser: {user_msg}\nAssistant:"
    answer = run_phi(prompt)

    return jsonify({"answer": answer})


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
