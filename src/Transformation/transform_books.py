# src/transformation/transform_books.py
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
import os
from datetime import datetime, timezone

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
RAW_COLL = os.getenv("RAW_COLLECTION", "books_raw")
CLEAN_COLL = os.getenv("CLEAN_COLLECTION", "books_clean")
LOG_COLL = os.getenv("LOG_TRANSFORMATION", "logs_transformation")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
raw = db[RAW_COLL]
clean = db[CLEAN_COLL]
logs = db[LOG_COLL]


def transform():
    print("🔄 Transformation des données en cours…")

    # 📌 Charger les données RAW
    df = pd.DataFrame(list(raw.find()))
    print(f"📥 Données brutes chargées : {df.shape[0]} lignes")

    if df.empty:
        print("⚠️ Aucune donnée brute à transformer.")
        return

    # 🧹 1. Nettoyage
    df = df.dropna(subset=["title"])  # enlever lignes sans titre

    # convertir types
    df["average_rating"] = pd.to_numeric(df.get("average_rating"), errors="coerce")
    df["ratings_count"] = pd.to_numeric(df.get("ratings_count"), errors="coerce")
    df["num_pages"] = pd.to_numeric(df.get("num_pages"), errors="coerce")

    # 🧠 2. Enrichissements

    # auteur principal (split sur virgule)
    df["main_author"] = df["authors"].apply(
        lambda x: x.split(",")[0].strip() if isinstance(x, str) else None
    )

    # extraire année depuis publication_date
    def extract_year(x):
        try:
            return int(str(x)[-4:])
        except:
            return None

    df["pub_year"] = df["original_publication_year"].apply(extract_year)

    # ajouter date de transformation
    ts = datetime.now(timezone.utc)
    df["_transform_ts"] = ts

    # 🗑️ supprimer colonnes inutiles pour la version clean
    drop_cols = ["_id", "_ingest_ts"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    # convertir en documents
    records = df.to_dict(orient="records")

    # vider la clean collection avant d'écrire (comme un datalake overwrite)
    clean.delete_many({})
    clean.insert_many(records)

    # logs
    logs.insert_one({
        "ts": ts,
        "raw_count": len(df),
        "clean_count": len(records)
    })

    print(f"✅ Transformation terminée : {len(records)} documents insérés dans {CLEAN_COLL}")


if __name__ == "__main__":
    transform()
