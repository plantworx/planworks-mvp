import os
import requests
import logging
from typing import Dict, Any

def google_plant_search(query: str, num_results: int = 3) -> Dict[str, Any]:
    """
    Search for plant information using Google Custom Search API.
    Returns top results with title, snippet, and link.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")
    if not api_key or not cse_id:
        logging.warning("Google API key or CSE ID not set. Returning mock data.")
        return {
            "results": [
                {"title": "Mock Plant Info", "snippet": "This is mock plant data.", "link": "https://en.wikipedia.org/wiki/Plant"}
            ],
            "sources": ["mock"]
        }
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cse_id,
        "q": query,
        "num": num_results
    }
    logging.info(f"Google Search request: {url} params={params}")
    resp = requests.get(url, params=params, timeout=10)
    logging.info(f"Google Search response status: {resp.status_code}")
    results = {"results": [], "sources": ["Google Custom Search"]}
    if resp.status_code == 200:
        data = resp.json()
        for item in data.get("items", []):
            results["results"].append({
                "title": item.get("title"),
                "snippet": item.get("snippet"),
                "link": item.get("link")
            })
    else:
        logging.error(f"Google Search API error: {resp.text}")
    return results
