import requests

# === Step 1: استدعاء match API ===
match_url = "http://127.0.0.1:5000/match/accelerators"

startup_payload = {
    "description": "AI platform for healthcare diagnostics",
    "industry": "Healthcare",
    "stage": "Series A",
    "country": "Egypt"
}

match_resp = requests.post(match_url, json=startup_payload)

if match_resp.status_code == 200:
    match_data = match_resp.json()
    top_matches = match_data.get("matches", [])

    print("=== Top Matches from Qdrant ===\n")
    for m in top_matches:
        print(f"ID: {m['id']}")
        print(f"Name: {m['name']}")
        print(f"Score: {m['score']:.4f}")
        print(f"Profile Text: {m['profile_text']}")
        print(f"Investment Focus: {m.get('Investment_Focus','')}")
        print(f"Stage Focus: {m.get('Stage_Focus','')}")
        print(f"Location: {m.get('Location','')}")
        print(f"Contact_Email: {m.get('Contact_Email','')}")
        print(f"Phone_Number: {m.get('Phone_Number','')}")
        print(f"Social_Links: {m.get('Social_Links','')}\n")


    query_url = "http://127.0.0.1:5000/query-llama"
    prompt_payload = {
        "prompt": "Tell me about accelerators that support AI healthcare startups.",
        "collection_name": "accelerators"
    }

    query_resp = requests.post(query_url, json=prompt_payload)

    if query_resp.status_code == 200:
        query_data = query_resp.json()
        print("=== LLaMA Response ===\n")
        print(query_data.get("response","No response"))
    else:
        print(f"Error from query-llama: {query_resp.status_code}")
        print(query_resp.text)

else:
    print(f"Error from match API: {match_resp.status_code}")
    print(match_resp.text)
