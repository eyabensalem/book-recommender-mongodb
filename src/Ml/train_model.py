# src/ml/train_model.py
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import json
from datetime import datetime

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
PROC_COLL = os.getenv("PROC_COLLECTION", "books_processed")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
proc = db[PROC_COLL]

def load_data():
    docs = list(proc.find({}, {"_id":0, "average_rating":1, "ratings_count":1, "num_pages":1, "popularity_score":1, "title_length":1}))
    df = pd.DataFrame(docs).dropna(subset=["average_rating"])
    return df

def train():
    df = load_data()
    if df.empty:
        print("No training data")
        return
    X = df[["ratings_count","num_pages","popularity_score","title_length"]].fillna(0)
    y = df["average_rating"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/model.pkl")

    metrics = {"mse": mse, "r2": r2, "trained_at": datetime.utcnow().isoformat()}
    with open("artifacts/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("Model trained. MSE:", mse, "R2:", r2)

if __name__ == "__main__":
    train()
