from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
import os

# Charger les variables du fichier .env
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLL_NAME = os.getenv("COLLECTION_NAME")
CSV_FILE = os.getenv("CSV_FILE")  # chemin du CSV dans .env

def connect_mongo():
    """Connexion à MongoDB"""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    coll = db[COLL_NAME]
    return coll

def ingest():
    """Lecture du CSV et insertion dans la collection MongoDB"""
    print("➡️ CSV_FILE détecté :", CSV_FILE)

    if not CSV_FILE or not os.path.exists(CSV_FILE):
        print("❌ ERREUR : Le fichier CSV n'existe pas ou le chemin est incorrect.")
        return

    # Lecture du dataset
    df = pd.read_csv(CSV_FILE)
    print(f"📄 Dataset chargé : {len(df)} lignes")

    data = df.to_dict(orient="records")

    coll = connect_mongo()

    if len(data) > 0:
        coll.insert_many(data)
        print(f"✅ {len(data)} documents insérés dans MongoDB !")
    else:
        print("⚠️ Le fichier CSV est vide, aucune donnée insérée.")

if __name__ == "__main__":
    ingest()
