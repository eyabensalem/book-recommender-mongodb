# src/api/app.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os, json
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
CLEAN_COLL = os.getenv("CLEAN_COLLECTION", "books_clean")
ARTIFACTS_DIR = os.getenv("ARTIFACTS_DIR", "artifacts")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
clean = db[CLEAN_COLL]

app = FastAPI(title="Books API")

class PredictIn(BaseModel):
    ratings_count: int = 0
    num_pages: int = 0
    popularity_score: float = 0.0
    title_length: int = 0

@app.get("/health")
def health():
    return {"status": "ok", "db_collections": db.list_collection_names()}

@app.get("/books/sample")
def sample(limit: int = 10):
    docs = list(clean.find({}, {"_id": 0, "title":1, "main_author":1, "average_rating":1}).limit(limit))
    return docs

@app.get("/stats")
def stats():
    stats_file = os.path.join(ARTIFACTS_DIR, "stats.json")
    if os.path.exists(stats_file):
        with open(stats_file) as f:
            return json.load(f)
    return {"message": "stats not generated yet"}

@app.get("/artifacts/{fname}")
def get_artifact(fname: str):
    path = os.path.join(ARTIFACTS_DIR, fname)
    if os.path.exists(path):
        return FileResponse(path)
    raise HTTPException(status_code=404, detail="File not found")
