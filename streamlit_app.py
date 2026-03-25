import streamlit as st #sert à créer l'interface web sur le site streamlit
import pandas as pd  # outil pour manipuler le tableau de donner 
import matplotlib.pyplot as plt 

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="Superquinquin - Indicateurs",
    layout="wide"
)

# 2. STYLE CSS (Correctif pour les chiffres blancs et le fond)
st.markdown("""
    <style>
    /* Fond de la page gris très clair */
    .stApp {
        background-color: #423D3D;
    }
    
    /* Style des cartes de chiffres (Metrics) */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }

    /* FORCE LE TEXTE EN NOIR (pour éviter le blanc sur blanc en mode sombre) */
    div[data-testid="stMetric"] label {
        color: #555555 !important; /* Couleur du titre (Bio, Local...) */
    }
    div[data-testid="stMetricValue"] > div {
        color: #1a1a1a !important; /* Couleur du chiffre (90.0%) */
    }
    
    /* Couleur du texte dans la sidebar */
    .css-1d391kg, .stSidebar {
        background-color: #262730;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CHARGEMENT DES DONNÉES
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

# 4. BARRE LATÉRALE (SIDEBAR)
with st.sidebar:
    # Logo Superquinquin
    st.sidebar.image("logo.png", use_container_width=True)
    st.divider()
    st.subheader("Navigation")
    categories = sorted(df[cat_col].dropna().unique())
    choix = st.selectbox("Rechercher une catégorie :", ["Choisir une catégorie..."] + categories)
    st.info("Application de suivi des indicateurs Bio, Local et Circuit Court.")

# 5. ZONE PRINCIPALE
if choix != "Choisir une catégorie...":
    st.title(f"{choix}")
    
    row = df[df[cat_col] == choix].iloc[0]
    
    # Affichage des chiffres clés
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

    # Affichage du graphique avec fond blanc pour contraste
    fig.patch.set_facecolor('white')
    st.pyplot(fig)

else:
    st.title("Bienvenue chez Superquinquin")
    st.write("Sélectionnez une catégorie à gauche pour voir les données.")


