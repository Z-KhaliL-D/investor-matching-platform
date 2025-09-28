from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer
import pandas as pd
import uuid

# === Config ===
QDRANT_URL = "https://ed07d684-8e1d-499f-a564-a3a6ce5d6280.eu-central-1-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.wQmL1PrTpbytO3tzurKM56jWG9bUMFFscUQierUlkX8"
COLLECTION_NAME = "investors"

# === Connect ===
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# === Load your model ===
model = SentenceTransformer("./tsdae_finetuned_investors")  # or MiniLM if you prefer

# === Load CSV ===
df = pd.read_csv("investors_data (1).csv").drop_duplicates(subset=["name"], keep="first")

def build_profile_text(row):
    parts = []
    if pd.notna(row.get("description")):
        parts.append(str(row["description"]))
    if pd.notna(row.get("investmentFocus")):
        parts.append("Focus areas: " + str(row["investmentFocus"]))
    if pd.notna(row.get("category")):
        parts.append("Category: " + str(row["category"]))
    if pd.notna(row.get("type")):
        parts.append("Type: " + str(row["type"]))
    if pd.notna(row.get("location")):
        parts.append("Location: " + str(row["location"]))
    elif pd.notna(row.get("country")):
        parts.append("Country: " + str(row["country"]))
    if pd.notna(row.get("portfolioHighlights")):
        parts.append("Portfolio: " + str(row["portfolioHighlights"]))
    return ". ".join(parts)

df["profile_text"] = df.apply(build_profile_text, axis=1)

texts = df["profile_text"].dropna().astype(str).tolist()
print(f"✅ Loaded {len(texts)} investor profiles.")

# === Create collection (if not exists) ===
if not qdrant.collection_exists(COLLECTION_NAME):
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=model.get_sentence_embedding_dimension(), distance=Distance.COSINE),
    )

# === Encode ===
embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

# === Upload in batches ===
BATCH_SIZE = 100
for i in range(0, len(embeddings), BATCH_SIZE):
    batch_vectors = embeddings[i:i+BATCH_SIZE]
    batch_payload = df.iloc[i:i+BATCH_SIZE].to_dict(orient="records")

    points = [
        PointStruct(id=str(uuid.uuid4()), vector=vec.tolist(), payload=payload)
        for vec, payload in zip(batch_vectors, batch_payload)
    ]

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ Uploaded {i+len(batch_vectors)} / {len(embeddings)}")
