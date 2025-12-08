# src/analytics/analyze_books.py
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
import os
import matplotlib
matplotlib.use("Agg")  # backend non interactif
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import json

# --- Load environment ---
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
CLEAN_COLL = os.getenv("CLEAN_COLLECTION", "books_clean")
ARTIFACTS_DIR = os.getenv("ARTIFACTS_DIR", "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# --- Connect to Mongo ---
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
clean = db[CLEAN_COLL]

def analyze_and_save():
    print("📊 Analyse des données CLEAN…")
    df = pd.DataFrame(list(clean.find()))
    print(f"📥 Données chargées : {df.shape[0]} lignes")

    if df.empty:
        print("⚠️ Aucune donnée clean à analyser.")
        return

    # --- Top 10 livres les mieux notés ---
    top_books = (
        df[["title", "average_rating"]]
        .dropna()
        .sort_values("average_rating", ascending=False)
        .head(10)
    )
    top_books.to_csv(os.path.join(ARTIFACTS_DIR, "top_books.csv"), index=False)
    print("Top books CSV généré")

    # --- Top auteurs productifs ---
    if "main_author" in df.columns:
        top_authors = df["main_author"].value_counts().head(10)
        top_authors.to_csv(os.path.join(ARTIFACTS_DIR, "top_authors.csv"))
        print("Top authors CSV généré")
    else:
        top_authors = pd.Series()
        print("⚠️ Colonne 'main_author' absente, top authors ignoré.")

    # --- Rating moyen par année ---
    if "pub_year" in df.columns and "average_rating" in df.columns:
        yearly_rating = (
            df.groupby("pub_year")["average_rating"]
            .mean()
            .dropna()
            .reset_index()
            .sort_values("pub_year")
        )
        yearly_rating.to_csv(os.path.join(ARTIFACTS_DIR, "yearly_rating.csv"), index=False)
        print("Yearly rating CSV généré")
    else:
        yearly_rating = pd.DataFrame()
        print("⚠️ Colonnes 'pub_year' ou 'average_rating' absentes, yearly rating ignoré.")

    # --- Statistiques globales ---
    stats = {
        "total_books": int(len(df)),
        "avg_rating": float(df["average_rating"].mean()) if "average_rating" in df.columns and not df["average_rating"].isna().all() else None,
        "avg_pages": float(df["num_pages"].mean()) if "num_pages" in df.columns and not df["num_pages"].isna().all() else None,
        "unique_authors": int(df["main_author"].nunique()) if "main_author" in df.columns else None,
        "min_year": int(df["pub_year"].min()) if "pub_year" in df.columns and not df["pub_year"].isna().all() else None,
        "max_year": int(df["pub_year"].max()) if "pub_year" in df.columns and not df["pub_year"].isna().all() else None,
    }
    with open(os.path.join(ARTIFACTS_DIR, "stats.json"), "w") as f:
        json.dump(stats, f, indent=2)

    # --- Graphiques ---

    # Top authors (barplot)
    if not top_authors.empty:
        plt.figure(figsize=(8,5))
        sns.barplot(x=top_authors.values, y=top_authors.index, palette="viridis")
        plt.title("Top 10 Authors by Number of Books")
        plt.xlabel("Number of Books")
        plt.ylabel("Author")
        plt.tight_layout()
        plt.savefig(os.path.join(ARTIFACTS_DIR, "top_authors.png"))
        plt.close()

    # Top books (barplot horizontal)
    plt.figure(figsize=(10,6))
    sns.barplot(x=top_books["average_rating"].iloc[::-1], y=top_books["title"].iloc[::-1], palette="magma")
    plt.title("Top 10 Books by Average Rating")
    plt.xlabel("Average Rating")
    plt.ylabel("Title")
    plt.tight_layout()
    plt.savefig(os.path.join(ARTIFACTS_DIR, "top_books.png"))
    plt.close()

    # Yearly rating (line plot)
    if not yearly_rating.empty:
        plt.figure(figsize=(10,5))
        sns.lineplot(x=yearly_rating["pub_year"], y=yearly_rating["average_rating"], marker="o")
        plt.title("Average Rating by Year")
        plt.xlabel("Year")
        plt.ylabel("Average Rating")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(ARTIFACTS_DIR, "yearly_rating.png"))
        plt.close()

    # Histogramme du nombre de pages
    if "num_pages" in df.columns and not df["num_pages"].isna().all():
        plt.figure(figsize=(10,5))
        sns.histplot(df["num_pages"].dropna(), bins=30, kde=True, color="skyblue")
        plt.title("Distribution of Number of Pages")
        plt.xlabel("Number of Pages")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig(os.path.join(ARTIFACTS_DIR, "pages_histogram.png"))
        plt.close()

    # Boxplot des ratings
    if "average_rating" in df.columns:
        plt.figure(figsize=(8,5))
        sns.boxplot(x=df["average_rating"], color="lightgreen")
        plt.title("Boxplot of Average Ratings")
        plt.xlabel("Average Rating")
        plt.tight_layout()
        plt.savefig(os.path.join(ARTIFACTS_DIR, "ratings_boxplot.png"))
        plt.close()

    # WordCloud des titres
    plt.figure(figsize=(10,6))
    text_titles = " ".join(df["title"].dropna())
    wc_titles = WordCloud(width=800, height=400, background_color="white").generate(text_titles)
    plt.imshow(wc_titles, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(os.path.join(ARTIFACTS_DIR, "title_wordcloud.png"))
    plt.close()

    # WordCloud par auteur
    if "main_author" in df.columns:
        plt.figure(figsize=(10,6))
        text_authors = " ".join(df["main_author"].dropna())
        wc_authors = WordCloud(width=800, height=400, background_color="white").generate(text_authors)
        plt.imshow(wc_authors, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(os.path.join(ARTIFACTS_DIR, "author_wordcloud.png"))
        plt.close()

    print("✅ Analyse et graphes enrichis sauvegardés dans", ARTIFACTS_DIR)


if __name__ == "__main__":
    analyze_and_save()
