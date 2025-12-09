import joblib
import pandas as pd

MODEL_PATH = "models/model.pkl"

def test_model():
    # Charger le modèle
    try:
        model = joblib.load(MODEL_PATH)
        print("✅ Modèle chargé avec succès !")
    except Exception as e:
        print("❌ Impossible de charger le modèle :", e)
        return

    # Exemple de données (manuelles)
    sample = {
        "ratings_count": 5000,
        "num_pages": 320,
        "popularity_score": 0.85,
        "title_length": 15
    }

    df = pd.DataFrame([sample])

    # Prédiction
    try:
        prediction = model.predict(df)[0]
        print("\n🎯 Prédiction du modèle :")
        print("Predicted Rating =", round(prediction, 3))
    except Exception as e:
        print("❌ Erreur lors de la prédiction :", e)


if __name__ == "__main__":
    test_model()
