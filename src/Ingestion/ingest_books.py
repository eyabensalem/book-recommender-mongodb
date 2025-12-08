# src/ingestion/ingest_books.py
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
import os
    # timestamp ingestion
from datetime import datetime, timezone

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
RAW_COLL = os.getenv("RAW_COLLECTION", "books_raw")
LOG_COLL = os.getenv("LOG_COLLECTION", "logs_ingestion")
CSV_FILE = os.getenv("CSV_FILE")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
raw = db[RAW_COLL]
logs = db[LOG_COLL]

def ingest():
    print("➡️ CSV:", CSV_FILE)
    df = pd.read_csv(CSV_FILE)

    # ---------------------------
    # 🔧 CLEANING FIX (IMPORTANT)
    # ---------------------------
    # Remplacer NaN dans colonnes textuelles par ""
    text_cols = df.select_dtypes(include=["object"]).columns
    df[text_cols] = df[text_cols].fillna("")

    # Remplacer NaN dans colonnes numériques par 0
    num_cols = df.select_dtypes(include=["number"]).columns
    df[num_cols] = df[num_cols].fillna(0)



    ts = datetime.now(timezone.utc)

    df["_ingest_ts"] = ts
    records = df.to_dict(orient="records")

    inserted = 0
    for r in records:
        # upsert basé sur le titre (à adapter si book_id existe)
        filter_q = {"title": r.get("title")}
        res = raw.update_one(filter_q, {"$setOnInsert": r}, upsert=True)
        if res.upserted_id:
            inserted += 1

    logs.insert_one({"ts": ts, "inserted": inserted, "total_source": len(records)})
    print(f"Inserted {inserted} new docs")

if __name__ == "__main__":
    ingest()
