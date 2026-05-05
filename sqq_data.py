"""
sqq_data.py
===========
Définitions statiques : catégories, sous-catégories et grilles de critères.
Toutes les modifications de la grille se font ici.
"""

import pandas as pd

# ---------------------------------------------------------------------------
# 1. HIÉRARCHIE CATÉGORIE → SOUS-CATÉGORIE
# ---------------------------------------------------------------------------

SOUS_CATEGORIES: dict[str, list[str]] = {
    "Fruits & Légumes": [
        "Pommes & Poires",
        "Agrumes & Exotiques",
        "Fruits d'été / Rouges",
        "Légumes racines",
        "Légumes fruits",
        "Salades & Verdures",
    ],
    "Viandes fraîches": [
        "Volailles",
        "Bœuf",
        "Porc & Saucisserie",
        "Agneau & Mouton",
    ],
    "Bières / Cidre": [
        "Blondes",
        "Blanches",
        "Ambrées & Brunes",
        "IPA",
        "Cidres",
    ],
    "Biscuits / Apéro": [
        "Biscuits sucrés secs",
        "Biscuits moelleux",
        "Chips & Tuiles",
        "Graines (vrac)",
        "Craquelins salés",
    ],
    "Chocolats / Café / Thé": [
        "Tablettes Noir",
        "Tablettes Lait / Blanc",
        "Pâtes à tartiner",
        "Café",
        "Thés & Infusions",
    ],
    "Produits laitiers": [
        "Lait liquide",
        "Yaourts natures",
        "Yaourts fruits",
        "Beurre / Crème",
        "Fromages pâte dure",
        "Fromages pâte molle",
    ],
    "Jus / Sodas": [
        "Jus pommes / poires",
        "Jus agrumes / exotiques",
        "Sodas / Thés glacés",
        "Limonades",
        "Boissons fermentées",
    ],
}

CATEGORIES: list[str] = list(SOUS_CATEGORIES.keys())

# ---------------------------------------------------------------------------
# 2. GRILLES DE CRITÈRES PAR CATÉGORIE
# ---------------------------------------------------------------------------
# Chaque critère : (nom, thème, poids)
# Thème : "Bleu" = Proximité | "Vert" = Méthode durable | "Orange" = Équité
# Poids : 1 (faible) à 3 (fort)

CRITERES: dict[str, list[tuple[str, str, int]]] = {
    "Fruits & Légumes": [
        ("Saisonnalité",                "Vert",   3),
        ("Circuit court Nord/PdC",      "Bleu",   3),
        ("Zéro pesticide / Bio",        "Vert",   2),
        ("Vrac / Zéro emballage",       "Vert",   2),
        ("Transparence producteur",     "Orange", 1),
    ],
    "Viandes fraîches": [
        ("Bien-être animal / Plein air","Vert",   3),
        ("Juste rémunération éleveur",  "Orange", 3),
        ("Origine Hauts-de-France",     "Bleu",   2),
        ("Sans OGM / Antibiotiques",    "Vert",   2),
        ("Élevage indépendant / coop",  "Orange", 1),
    ],
    "Bières / Cidre": [
        ("Brasserie / verger local HdF","Bleu",   3),
        ("Ingrédients bio / naturels",  "Vert",   2),
        ("Bouteille consignée / vrac",  "Vert",   2),
        ("Brasserie indépendante",      "Orange", 2),
        ("Transparence recette",        "Orange", 1),
    ],
    "Biscuits / Apéro": [
        ("Ingrédients bio certifiés",   "Vert",   3),
        ("Origine ingrédients HdF",     "Bleu",   2),
        ("Emballage recyclable / vrac", "Vert",   2),
        ("Producteur / coopérative",    "Orange", 2),
        ("Sans additifs / colorants",   "Vert",   1),
    ],
    "Chocolats / Café / Thé": [
        ("Commerce équitable certifié", "Orange", 3),
        ("Bio certifié",                "Vert",   2),
        ("Transformation HdF",          "Bleu",   2),
        ("Emballage recyclable / vrac", "Vert",   2),
        ("Coopérative producteurs",     "Orange", 1),
    ],
    "Produits laitiers": [
        ("Origine lait Hauts-de-France","Bleu",   3),
        ("Élevage plein air / bio",     "Vert",   3),
        ("Juste rémunération éleveur",  "Orange", 2),
        ("Emballage recyclable / vrac", "Vert",   1),
        ("Producteur indépendant",      "Orange", 1),
    ],
    "Jus / Sodas": [
        ("Fruits / ingrédients HdF",    "Bleu",   3),
        ("Bio / sans pesticide",        "Vert",   2),
        ("Bouteille consignée / vrac",  "Vert",   2),
        ("Sans sucres ajoutés / addit.","Vert",   1),
        ("Producteur indépendant",      "Orange", 2),
    ],
}

# ---------------------------------------------------------------------------
# 3. SCHÉMA DES DATAFRAMES
# ---------------------------------------------------------------------------

def get_criteres_df() -> pd.DataFrame:
    """
    Retourne la grille complète des critères sous forme de DataFrame.

    Colonnes :
        categorie   : str  — grande famille produit
        critere     : str  — intitulé du critère
        theme       : str  — "Bleu" | "Vert" | "Orange"
        poids       : int  — 1, 2 ou 3
    """
    rows = []
    for cat, crit_list in CRITERES.items():
        for nom, theme, poids in crit_list:
            rows.append({"categorie": cat, "critere": nom, "theme": theme, "poids": poids})
    return pd.DataFrame(rows)


def get_empty_produits_df() -> pd.DataFrame:
    """
    Retourne un DataFrame vide au bon schéma pour stocker les notes.

    Colonnes :
        produit       : str   — nom commercial du produit
        categorie     : str   — grande famille
        sous_categorie: str   — sous-famille (ex: "Volailles")
        critere       : str   — intitulé du critère noté
        theme         : str   — "Bleu" | "Vert" | "Orange"
        poids         : int   — poids du critère
        note          : int   — note saisie de 1 à 5
        date_saisie   : str   — date ISO (ex: "2025-06-01")
    """
    return pd.DataFrame(columns=[
        "produit", "categorie", "sous_categorie",
        "critere", "theme", "poids", "note", "date_saisie",
    ])
