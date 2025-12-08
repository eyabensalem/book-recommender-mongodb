# src/dashboard/app.py
import streamlit as st
import requests
import pandas as pd
import os

# --- Config ---
API_BASE = "http://127.0.0.1:8000"  # URL de ton API FastAPI locale
ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "../../artifacts")

st.set_page_config(page_title="Books Dashboard", layout="wide")
st.title("Books Intelligence — Dashboard")

# --- Status API ---
st.sidebar.header("Status API")
try:
    r = requests.get(f"{API_BASE}/health", timeout=2).json()
    st.sidebar.success("API OK")
    st.sidebar.write(r)
except Exception as e:
    st.sidebar.error("API unreachable")
    st.sidebar.write(e)

# --- Statistiques globales ---
st.header("Global Stats")
stats_file = os.path.join(ARTIFACTS_DIR, "stats.json")
if os.path.exists(stats_file):
    with open(stats_file) as f:
        stats = pd.DataFrame([requests.get(f"{API_BASE}/stats").json()])
    st.table(stats.T.rename(columns={0: "Value"}))
else:
    st.write("Stats not generated yet. Run `analyze_books.py` first.")

# --- Top charts images ---
st.header("Top Results (from artifacts)")
cols = st.columns(2)
with cols[0]:
    st.subheader("Top Authors")
    top_authors_path = os.path.join(ARTIFACTS_DIR, "top_authors.png")
    if os.path.exists(top_authors_path):
        st.image(top_authors_path)
    else:
        st.write("Image not found. Run analysis first.")

with cols[1]:
    st.subheader("Top Books")
    top_books_path = os.path.join(ARTIFACTS_DIR, "top_books.png")
    if os.path.exists(top_books_path):
        st.image(top_books_path)
    else:
        st.write("Image not found. Run analysis first.")

st.subheader("Yearly Rating")
yearly_rating_path = os.path.join(ARTIFACTS_DIR, "yearly_rating.png")
if os.path.exists(yearly_rating_path):
    st.image(yearly_rating_path)
else:
    st.write("Image not found. Run analysis first.")

st.subheader("Title WordCloud")
wordcloud_path = os.path.join(ARTIFACTS_DIR, "title_wordcloud.png")
if os.path.exists(wordcloud_path):
    st.image(wordcloud_path)
else:
    st.write("Image not found. Run analysis first.")

# --- Sample books ---
st.header("Sample books")
try:
    sample = requests.get(f"{API_BASE}/books/sample?limit=20").json()
    st.table(sample)
except Exception as e:
    st.write("No sample available")
    st.write(e)
