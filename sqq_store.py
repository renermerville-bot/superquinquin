"""
sqq_store.py
============
Couche de persistance : lecture et écriture des données produits (CSV).

Le fichier CSV utilise le format "long" (tidy data) :
une ligne = une note pour un critère d'un produit.
"""

import os
import pandas as pd
from sqq_data import get_empty_produits_df

# Chemin du fichier de données (relatif au dossier de lancement)
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PRODUITS_CSV = os.path.join(DATA_DIR, "produits.csv")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def charger_produits() -> pd.DataFrame:
    """
    Charge le DataFrame produits depuis le CSV.
    Si le fichier n'existe pas, retourne un DataFrame vide au bon schéma.
    """
    _ensure_data_dir()
    if not os.path.exists(PRODUITS_CSV):
        return get_empty_produits_df()
    df = pd.read_csv(PRODUITS_CSV, dtype=str)
    df["poids"] = pd.to_numeric(df["poids"], errors="coerce").fillna(1).astype(int)
    df["note"] = pd.to_numeric(df["note"], errors="coerce").fillna(0).astype(int)
    return df


def sauvegarder_produit(nouvelles_lignes: list[dict]) -> pd.DataFrame:
    """
    Ajoute les nouvelles lignes au CSV existant (ou le crée).
    Retourne le DataFrame complet après sauvegarde.
    """
    _ensure_data_dir()
    df_existant = charger_produits()
    df_new = pd.DataFrame(nouvelles_lignes)
    df_complet = pd.concat([df_existant, df_new], ignore_index=True)
    df_complet.to_csv(PRODUITS_CSV, index=False)
    return df_complet


def supprimer_produit(nom_produit: str) -> pd.DataFrame:
    """
    Supprime toutes les lignes d'un produit et sauvegarde.
    """
    df = charger_produits()
    df = df[df["produit"] != nom_produit]
    df.to_csv(PRODUITS_CSV, index=False)
    return df


def produit_existe(nom_produit: str) -> bool:
    """Vérifie si un produit est déjà dans la base."""
    df = charger_produits()
    return nom_produit in df["produit"].values
