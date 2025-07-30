import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TREFLE_API_KEY = os.getenv("TREFLE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

def test_openweather():
    print("Testing OpenWeather API...")
    if not OPENWEATHER_API_KEY:
        print("  OPENWEATHER_API_KEY not set!")
        return
    url = f"https://api.openweathermap.org/data/2.5/weather?q=London&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"  Success: Weather in London: {data['weather'][0]['description']} ({data['main']['temp']}°C)")
        else:
            print(f"  Error: Status {resp.status_code}, Body: {resp.text}")
    except Exception as e:
        print(f"  Exception: {e}")

def test_trefle():
    print("Testing Trefle API...")
    if not TREFLE_API_KEY:
        print("  TREFLE_API_KEY not set!")
        return
    trefle_url = "https://trefle.io/api/v2/plants"
    headers = {"Authorization": f"Bearer {TREFLE_API_KEY}"}
    params = {"q": "Cactus"}
    try:
        resp = requests.get(trefle_url, headers=headers, params=params, timeout=10)
        print(f"  Status: {resp.status_code}, Body: {resp.text[:200]}")
        if resp.status_code == 200:
            data = resp.json()
            if data.get("data"):
                first_plant = data["data"][0]
                print(f"  Success: Found plant: {first_plant.get('scientific_name', 'Unknown')} (Common name: {first_plant.get('common_name', 'N/A')})")
            else:
                print("  Success: No plant found, but API is reachable.")
        else:
            print(f"  Error: Status {resp.status_code}, Body: {resp.text}")
    except Exception as e:
        print(f"  Exception: {e}")

def test_google_genai():
    print("Testing Google GenAI API...")
    if not GOOGLE_API_KEY:
        print("  GOOGLE_API_KEY not set!")
        return
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GOOGLE_API_KEY
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "Explain how AI works in a few words"}
                ]
            }
        ]
    }
    try:
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response")
            print(f"  Success: Model response: {text.strip()}")
        else:
            print(f"  Error: Status {resp.status_code}, Body: {resp.text}")
    except Exception as e:
        print(f"  Exception: {e}")

def main():
    test_openweather()
    print()
    test_trefle()
    print()
    test_google_genai()

if __name__ == "__main__":
    main()
