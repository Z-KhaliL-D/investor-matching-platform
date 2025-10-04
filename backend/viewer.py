from qdrant_client import QdrantClient

# === Config ===
QDRANT_URL = "https://ed07d684-8e1d-499f-a564-a3a6ce5d6280.eu-central-1-0.aws.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.wQmL1PrTpbytO3tzurKM56jWG9bUMFFscUQierUlkX8"
COLLECTION_NAME = "investors"

# === Connect ===
qdrant = QdrantClient(url = QDRANT_URL, api_key = QDRANT_API_KEY)

# === Fetch first 5 investors ===
result = qdrant.scroll(
    collection_name = COLLECTION_NAME,
    limit = 5,
    with_payload = True,
    with_vectors = False
)

points, _ = result

# Print data
for i, point in enumerate(points, start=1):
    print(f"\nInvestor {i}:")
    payload = point.payload
    print("Profile Text:", payload.get("profile_text", "N/A"))
    print("Investment Focus:", payload.get("Investment_Focus", "N/A"))
    print("Stage Focus:", payload.get("Stage_Focus", "N/A"))
    print("Target Countries:", payload.get("Target_Countries_Mapped", "N/A"))
