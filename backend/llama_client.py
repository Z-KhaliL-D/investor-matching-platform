import os
from groq import Groq
from dotenv import load_dotenv
from tavily import TavilyClient
import requests

load_dotenv()
print("Loaded key:", os.getenv("GROQ_API_KEY"))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
api_key = os.getenv("TAVILY_API_KEY")
tavily = TavilyClient(api_key)

# === Helper: Web Search by Tavily ===
def web_search_tavily(query):
    """Search the web using Tavily API."""
    url = "https://api.tavily.com/search"
    headers = {"Content-Type": "application/json"}
    data = {
        "api_key": api_key,
        "query": query,
        "max_results": 5
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        return f"Tavily search failed: {response.text}"

    results = response.json().get("results", [])
    combined_info = "\n".join([r.get("content", "") for r in results])
    return combined_info

def matches_list_toStr(match) -> str:
    """Converts any match dict into a readable string for the LLM."""
    lines = []
    for i, match in enumerate(match, start=1):
        lines.append(f"\n--- Match {i} ---")
        for key, value in match.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    lines.append(f"{subkey}: {str(subvalue)}")
            else:
                lines.append(f"{key}: {str(value)}")
    
    return "\n".join(lines)

def query_llama(user_query: str, top_matches: dict):

    # === Prepare prompt ===
    prompt = f"""
    You are an expert startup advisor.
    User asked: "{user_query}"

    Here are the top 5 matching results from the database:
    {matches_list_toStr(top_matches)}
    Instructions:
    1. Review the above results carefully.
    2. If any required information is missing (like next registration dates, recent programs, contact info,phone number..), indicate that a live web search is needed.
    3. Only if information is complete, answer directly.
    """

    # === Ask LLaMA for decision ===
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a reasoning assistant who decides if web search is required."},
            {"role": "user", "content": prompt}
        ],
    )

    response_text = completion.choices[0].message.content.strip()

    # === Check if LLaMA requested a web search ===
    if "live web search is needed" in response_text.lower() or "need web search" in response_text.lower() :
        query = f"""Search for the information is missing in matches result {matches_list_toStr(top_matches)} 
        ex: phone number for one of the result is missing search for it """
        web_results = web_search_tavily(query)

        final_prompt = f"""
        User asked: "{user_query}"
        Top 5 database matches: {matches_list_toStr(top_matches)}
        Web search results: {web_results}

        Provide a complete answer based on the above information (add the web search information in the appropriate place in the matches results
        and display it in full. you don't need to write that you searched in the internet).
        """
        final_completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an expert startup advisor that matches startups with investors."},
                {"role": "user", "content": final_prompt}
            ],
        )
        return final_completion.choices[0].message.content
    else:
        print("All information is completed ")
        return response_text

