from pymongo import MongoClient

# 🧷 Remplace <password> par ton vrai mot de passe Atlas
uri = "mongodb+srv://eya:Karasevda0902!@cluster0.cksg5sv.mongodb.net/"

# Connexion au cluster
client = MongoClient(uri)

# Sélection de la base et de la collection
db = client["test"]  # remplace "test" par le nom de ta base si tu en as créé une autre
collection = db["velibCol"]  # remplace par le nom exact de ta collection

# 🧩 Lire tous les documents
print("Liste des stations Velib :")
for station in collection.find():
    print(station)

# 🧩 Exemple d'insertion depuis Python
nouvelle_station = {
    "station_name": "Rennes - République",
    "bike_stands": 22,
    "available_bikes": 11,
    "available_ebikes": 4,
    "commune": "Rennes",
    "status": "OPEN"
}
collection.insert_one(nouvelle_station)
print("✅ Nouvelle station ajoutée avec succès !")
