# main.py
from dotenv import load_dotenv
from pymongo import MongoClient
import os
import pandas as pd

load_dotenv()  # charge les variables d'environnement depuis .env

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "velibd")
COLL_NAME = os.getenv("COLLECTION_NAME", "velibCol")

# 1) Connexion
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
coll = db[COLL_NAME]

def test_connection():
    # vérifie qu'on peut se connecter et lister les collections
    print("Nom de la DB:", DB_NAME)
    print("Collections dans la DB:", db.list_collection_names()[:20])

def find_example():
    # Exemple: stations de Créteil (nom_arrondissement_communes)
    cursor = coll.find({"nom_arrondissement_communes": "Créteil"},
                       {"name": 1, "capacity": 1, "_id": 0})
    print("\nStations à Créteil (extrait):")
    for doc in cursor.limit(20):
        print(doc)

def filter_ebike_paris():
    # Stations à Paris avec plus de 10 ebike, triées par capacité
    query = {"nom_arrondissement_communes": "Paris", "ebike": {"$gt": 10}}
    projection = {"name": 1, "capacity": 1, "_id": 0, "ebike": 1}
    cursor = coll.find(query, projection).sort("capacity", -1).limit(50)
    df = pd.DataFrame(list(cursor))
    print("\nStations Paris >10 ebike (sample):")
    print(df.head())
    # sauvegarde en CSV si nécessaire
    if not df.empty:
        df.to_csv("paris_ebike_gt10.csv", index=False)
        print("Export CSV: paris_ebike_gt10.csv")

def aggregate_nb_stations_par_commune(limit=20):
    # Aggregation : nombre de stations par commune
    pipeline = [
        {"$group": {"_id": "$nom_arrondissement_communes", "nb_station": {"$sum": 1}}},
        {"$sort": {"nb_station": -1}},
        {"$limit": limit}
    ]
    res = list(coll.aggregate(pipeline))
    df = pd.DataFrame(res)
    if not df.empty:
        df = df.rename(columns={"_id": "commune"})
        print("\nTop communes par nombre de stations:")
        print(df)
        # graphe simple
        df.plot.bar(x="commune", y="nb_station", legend=False, figsize=(10,5))
        import matplotlib.pyplot as plt
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()
    else:
        print("Aucun résultat dans l'aggregation.")

def main():
    test_connection()
    find_example()
    filter_ebike_paris()
    aggregate_nb_stations_par_commune()

if __name__ == "__main__":
    main()
