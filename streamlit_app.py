import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuration de la page (Style tablette)
st.set_page_config(page_title="Superquinquin - Analyse Bio/Local", layout="wide")

# Titre et Sidebar
st.sidebar.image("https://superquinquin.fr/wp-content/uploads/2020/01/logo-superquinquin.png", width=150) # Logo optionnel
st.sidebar.title("Menu Catégories")

# 1. Chargement des données
url_csv = "https://docs.google.com/spreadsheets/d/1LR9qgEE91-cn-78o0lE2NHz9u8uVRWH-/gviz/tq?tqx=out:csv&sheet=SQQ_extraction_ventes_12_mois_glissants_2025-08-04"

@st.cache_data # Pour que l'app soit rapide
def load_data():
    df = pd.read_csv(url_csv)
    df.columns = df.columns.str.strip()
    cols_pct = ["% CA HT catégorie en BIO", "% CA HT catégorie en LOCAL", "% CA HT catégorie en CIRCUIT COURT"]
    for col in cols_pct:
        df[col] = df[col].astype(str).str.replace("%", "").str.replace(",", ".").astype(float)
    return df

df = load_data()
cat_col = "% Bio par catégories & principales sous-catégories Périmètre : 6 mois glissants janvier à juillet 2025 Catégories"

# 2. Interface de sélection (Sidebar)
categories = sorted(df[cat_col].dropna().unique())
choix = st.sidebar.selectbox("Rechercher une catégorie...", ["Toutes"] + categories)

# 3. Affichage des résultats
st.title("📊 Indicateurs Superquinquin")

if choix != "Toutes":
    row = df[df[cat_col] == choix].iloc[0]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader(f"Détails : {choix}")
        st.metric("Bio", f"{row['% CA HT catégorie en BIO']}%")
        st.metric("Local", f"{row['% CA HT catégorie en LOCAL']}%")
        st.metric("Circuit Court", f"{row['% CA HT catégorie en CIRCUIT COURT']}%")

    with col2:
        # Graphique
        fig, ax = plt.subplots()
        labels = ["Bio", "Local", "Circuit Court"]
        valeurs = [row["% CA HT catégorie en BIO"], row["% CA HT catégorie en LOCAL"], row["% CA HT catégorie en CIRCUIT COURT"]]
        ax.bar(labels, valeurs, color=['#4CAF50', '#2196F3', '#FF9800'])
        ax.set_ylim(0, 100)
        st.pyplot(fig)
else:
    st.write("Veuillez sélectionner une catégorie dans le menu à gauche pour voir les graphiques.")