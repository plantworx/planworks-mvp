from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.plant_rag_agent import load_plant_data, build_vector_db, query_plants, CHROMA_DB_DIR, PLANT_KB_PATH
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import os

router = APIRouter()

class PlantRAGQuery(BaseModel):
    question: str
    top_k: int = 3

# Load model and vector DB at startup
def get_collection_and_model():
    plant_data = load_plant_data(PLANT_KB_PATH)
    client = chromadb.Client(Settings(persist_directory=CHROMA_DB_DIR))
    collection = client.get_or_create_collection("plants")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return collection, model

collection, model = get_collection_and_model()

@router.post("/plant_rag")
def plant_rag_endpoint(query: PlantRAGQuery):
    try:
        results = query_plants(query.question, collection, model, top_k=query.top_k)
        return {"answers": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
