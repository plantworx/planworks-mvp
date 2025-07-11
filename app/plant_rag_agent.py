import csv
import json
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import wikipedia
import os

PLANT_NAMES = [
    "Cactus", "Monstera deliciosa", "Aloe vera", "Ficus lyrata", "Snake plant",
    "Pothos", "Spider plant", "Peace lily", "Philodendron", "ZZ plant"
]

PLANT_KB_PATH = os.path.join(os.path.dirname(__file__), "plants.json")
CHROMA_DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

# 1. Fetch plant info from Wikipedia (Option C)
def fetch_wikipedia_plants(plant_names):
    data = []
    for plant in plant_names:
        try:
            summary = wikipedia.summary(plant, sentences=3)
            data.append({"plant": plant, "info": summary})
        except Exception as e:
            print(f"Could not fetch {plant}: {e}")
    return data

# 2. Save/load plant knowledge base
def save_plant_data(plant_data, path=PLANT_KB_PATH):
    with open(path, "w") as f:
        json.dump(plant_data, f, indent=2)

def load_plant_data(path=PLANT_KB_PATH):
    with open(path) as f:
        return json.load(f)

# 3. Build ChromaDB vector store
def build_vector_db(plant_data, persist_dir=CHROMA_DB_DIR):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [entry["info"] for entry in plant_data]
    metadatas = [{"plant": entry["plant"]} for entry in plant_data]
    client = chromadb.Client(Settings(persist_directory=persist_dir))
    collection = client.get_or_create_collection("plants")
    embeddings = model.encode(texts, normalize_embeddings=True)
    # Add to ChromaDB
    for i, emb in enumerate(embeddings):
        collection.add(
            embeddings=[emb.tolist()],
            documents=[texts[i]],
            metadatas=[metadatas[i]],
            ids=[str(i)]
        )
    return client, collection, model

# 4. Query the vector DB
def query_plants(question, collection, model, top_k=3):
    q_emb = model.encode([question], normalize_embeddings=True)[0]
    results = collection.query(
        query_embeddings=[q_emb.tolist()],
        n_results=top_k
    )
    return [
        {"plant": meta["plant"], "info": doc}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]

# 5. Bootstrapper (run once to build KB and vector DB)
def bootstrap():
    plant_data = fetch_wikipedia_plants(PLANT_NAMES)
    save_plant_data(plant_data)
    build_vector_db(plant_data)

if __name__ == "__main__":
    bootstrap()
    print("Plant RAG agent knowledge base and vector DB built.")
