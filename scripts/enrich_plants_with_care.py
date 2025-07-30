import json
import wikipedia
import time

CARE_KEYWORDS = ["care", "cultivation", "growing", "maintenance", "watering", "light", "soil", "fertilizer"]

# Load your plant list
with open("app/plants.json") as f:
    plants = json.load(f)

def extract_care_section(page_title):
    try:
        page = wikipedia.page(page_title, auto_suggest=False)
        content = page.content
        # Try to extract care/cultivation section
        for keyword in CARE_KEYWORDS:
            if f"== {keyword.capitalize()}" in content:
                section = content.split(f"== {keyword.capitalize()}")[1]
                # Stop at next section
                section = section.split("==")[0]
                return section.strip()
        # fallback: return summary
        return wikipedia.summary(page_title)
    except Exception as e:
        print(f"[WARN] Could not fetch care info for {page_title}: {e}")
        return None

# Enrich plant info with care/cultivation details
for plant in plants:
    if "care" in plant["info"].lower():
        continue  # Already has care info
    care = extract_care_section(plant["plant"])
    if care:
        plant["info"] += f"\n\nCare info: {care}"
    time.sleep(1)  # be nice to Wikipedia

with open("app/plants_enriched.json", "w") as f:
    json.dump(plants, f, indent=2)

print("Enriched plant info written to app/plants_enriched.json")
