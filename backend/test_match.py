import requests
import json

# === Server URL ===
url = "http://127.0.0.1:5000/match"

# === Startup Data ===
payload = {
    "description": "AI platform for healthcare diagnostics",
    "industry": "Healthcare",
    "stage": "Series A",
    "country": "Egypt"
}

# === Send POST request ===
response = requests.post(url, json=payload)

# === Check the result ===
if response.status_code == 200:
    data = response.json()

    print("Top Matches: \n")
    for match in data.get("matches", []):
        print(f"ID: {match['id']}")
        print(f"Name: {match['name']}")
        print(f"Score: {match['score']:.4f}")
        print(f"Profile Text: {match['profile_text']}")
        print(f"Investment Focus: {match['Investment_Focus']}")
        print(f"Stage Focus: {match['Stage_Focus']}")
        print(f"Target Countries: {match['Target_Countries']}\n")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
