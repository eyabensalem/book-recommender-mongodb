from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLL_NAME = os.getenv("COLLECTION_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
coll = db[COLL_NAME]

# --- INFO DB ---
print(f"Nom de la DB: {DB_NAME}")
print("Collections:", db.list_collection_names())

# --- EXEMPLES DE DOCUMENTS ---
print("\n📘 Exemple de documents:")
for doc in coll.find({}, {"_id": 0, "authors": 1, "title": 1}).limit(10):
    print(doc)

# --- TOP 10 BEST RATED ---
print("\n⭐ Top 10 livres les mieux notés :")
df = pd.DataFrame(list(coll.find({}, {"title": 1, "average_rating": 1, "_id": 0})))
df = df.sort_values("average_rating", ascending=False).head(10)
print(df)

# --- COUNT BOOKS BY LANGUAGE ---
print("\n🌍 Nombre de livres par langue :")
df_lang = pd.DataFrame(list(coll.aggregate([
    {"$group": {"_id": "$language_code", "nb": {"$sum": 1}}},
    {"$project": {"language": "$_id", "nb": 1, "_id": 0}},
    {"$sort": {"nb": -1}}
])))
print(df_lang)

# ------------------------------
#      🔥 QUERIES AVANCÉES
# ------------------------------

# 1️⃣ Livres de J.K. Rowling
print("\n📚 Livres de J.K. Rowling :")
for d in coll.find({"authors": {"$regex": "J.K. Rowling"}}, {"title": 1, "_id": 0}).limit(5):
    print(d)

# 2️⃣ Top 5 livres les plus longs
print("\n📏 Top 5 livres les plus longs :")
pipeline_longest = [
    {"$sort": {"num_pages": -1}},
    {"$limit": 5},
    {"$project": {"title": 1, "num_pages": 1, "_id": 0}}
]
for d in coll.aggregate(pipeline_longest):
    print(d)

# 3️⃣ Moyenne des notes pour Suzanne Collins
print("\n⭐ Moyenne des notes pour Suzanne Collins :")
pipeline_rating = [
    {"$match": {"authors": {"$regex": "Suzanne Collins"}}},
    {"$group": {
        "_id": "$authors",
        "avg_rating": {"$avg": "$average_rating"}
    }}
]
for d in coll.aggregate(pipeline_rating):
    print(d)
