import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. CONFIGURATION DE LA PAGE (Style épuré)
st.set_page_config(
    page_title="Superquinquin - Indicateurs",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS pour forcer le look "Tablette Blanche"
st.markdown("""
    <style>
    .main {
        background-color: #f9f9f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CHARGEMENT DES DONNÉES
url_csv = "https://docs.google.com/spreadsheets/d/1LR9qgEE91-cn-78o0lE2NHz9u8uVRWH-/gviz/tq?tqx=out:csv&sheet=SQQ_extraction_ventes_12_mois_glissants_2025-08-04"

@st.cache_data
def load_data():
    df = pd.read_csv(url_csv)
    df.columns = df.columns.str.strip()
    cols_pct = ["% CA HT catégorie en BIO", "% CA HT catégorie en LOCAL", "% CA HT catégorie en CIRCUIT COURT"]
    for col in cols_pct:
        df[col] = df[col].astype(str).str.replace("%", "").str.replace(",", ".").astype(float)
    return df

df = load_data()
cat_col = "% Bio par catégories & principales sous-catégories Périmètre : 6 mois glissants janvier à juillet 2025 Catégories"

# 3. BARRE LATÉRALE (SIDEBAR)
with st.sidebar:
    # Logo Superquinquin (URL officielle)
    st.image("https://superquinquin.fr/wp-content/uploads/2020/01/logo-superquinquin.png", width=180)
    st.divider()
    st.subheader("Navigation")
    categories = sorted(df[cat_col].dropna().unique())
    choix = st.selectbox("Rechercher une catégorie :", ["Choisir une catégorie..."] + categories)
    
    st.spacer = st.container()
    st.sidebar.info("Application de suivi des indicateurs Bio, Local et Circuit Court.")

# 4. ZONE PRINCIPALE
if choix != "Choisir une catégorie...":
    st.title(f"📊 {choix}")
    
    row = df[df[cat_col] == choix].iloc[0]
    
    # Affichage des chiffres clés en colonnes
    m1, m2, m3 = st.columns(3)
    m1.metric("Part de BIO", f"{row['% CA HT catégorie en BIO']}%")
    m2.metric("Part de LOCAL", f"{row['% CA HT catégorie en LOCAL']}%")
    m3.metric("CIRCUIT COURT", f"{row['% CA HT catégorie en CIRCUIT COURT']}%")

    st.divider()

    # Graphique stylisé
    fig, ax = plt.subplots(figsize=(10, 5))
    labels = ["BIO", "LOCAL", "CIRCUIT COURT"]
    valeurs = [
        row["% CA HT catégorie en BIO"], 
        row["% CA HT catégorie en LOCAL"], 
        row["% CA HT catégorie en CIRCUIT COURT"]
    ]
    
    # Couleurs Superquinquin (Vert, Jaune, Bleu)
    couleurs = ['#4CAF50', '#FFC107', '#2196F3']
    
    bars = ax.bar(labels, valeurs, color=couleurs, width=0.6)
    
    # Design du graphique
    ax.set_ylim(0, 100)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylabel("Pourcentage (%)", fontsize=10, color='gray')
    
    # Ajouter les étiquettes de score au-dessus des barres
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval}%', ha='center', va='bottom', fontweight='bold')

    st.pyplot(fig)

else:
    # Page d'accueil si rien n'est sélectionné
    st.title("Bienvenue sur l'outil Superquinquin")
    st.write("Sélectionnez une catégorie dans le menu à gauche pour analyser les performances.")
    st.image("https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&q=80&w=1000", caption="Superquinquin : Local & Responsable")
