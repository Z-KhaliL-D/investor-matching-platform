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
qdrant = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60.0)

# === Load model ===
model = SentenceTransformer("./tsdae_finetuned_investors")

# === Load cleaned CSV ===
# === Load CSV ===
df = pd.read_csv("FINAL_INVESTORS.csv")

# Normalize column names: strip spaces, replace spaces with underscores
df.columns = df.columns.str.strip().str.replace(" ", "_")
print("📑 Normalized columns:", df.columns.tolist())

# Required columns after normalization
required_cols = ["Investment_Focus", "Stage_Focus", "Target_Countries_Mapped"]
for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"❌ Missing required column: {col}")

# Ensure profile_text exists or build one
if "profile_text" not in df.columns:
    def build_profile_text(row):
        parts = []
        if pd.notna(row.get("Description")):
            parts.append(str(row["Description"]))
        if pd.notna(row.get("Investment_Focus_Final")):
            parts.append("Focus areas: " + str(row["Investment_Focus_Final"]))
        if pd.notna(row.get("Stage_Focus")):
            parts.append("Stage focus: " + str(row["Stage_Focus"]))
        if pd.notna(row.get("Target_Countries_Mapped")):
            parts.append("Target countries: " + str(row["Target_Countries_Mapped"]))
        return ". ".join(parts)

    df["profile_text"] = df.apply(build_profile_text, axis=1)

texts = df["profile_text"].fillna("").astype(str).tolist()
print(f"✅ Loaded {len(texts)} investor profiles.")

# === Create collection if not exists ===
if not qdrant.collection_exists(COLLECTION_NAME):
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=model.get_sentence_embedding_dimension(),
            distance=Distance.COSINE
        ),
    )
    print("📦 Collection created:", COLLECTION_NAME)

# === Create text indexes for filtering ===
for field in required_cols:
    try:
        qdrant.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name=field,
            field_schema="text"
        )
        print(f"✅ Index created for: {field}")
    except Exception as e:
        print(f"⚠️ Index creation skipped for {field}: {e}")

# === Encode profiles ===
embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

# === Upload in batches ===
BATCH_SIZE = 100
for i in range(0, len(embeddings), BATCH_SIZE):
    batch_vectors = embeddings[i:i + BATCH_SIZE]
    batch_payload = df.iloc[i:i + BATCH_SIZE].to_dict(orient="records")

    points = [
        PointStruct(id=str(uuid.uuid4()), vector=vec.tolist(), payload=payload)
        for vec, payload in zip(batch_vectors, batch_payload)
    ]

    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ Uploaded {i + len(batch_vectors)} / {len(embeddings)}")

print("🎉 All investor profiles uploaded successfully with indexes.")
