"""
sqq_engine.py
=============
Moteur de calcul du SQQ-Score.

Responsabilités :
  - Calculer le score global (%) d'un produit à partir de ses notes
  - Calculer les scores par thème (Bleu / Vert / Orange)
  - Déterminer les pastilles obtenues (seuil configurable)
  - Agréger les scores pour le Dashboard (par catégorie ou sous-catégorie)
"""

import pandas as pd
from sqq_data import CRITERES, get_criteres_df

# Seuil d'activation d'une pastille (en %)
# Si le score d'un thème >= SEUIL_PASTILLE, la pastille est accordée.
SEUIL_PASTILLE: int = 70

THEMES: list[str] = ["Bleu", "Vert", "Orange"]
THEME_LABELS: dict[str, str] = {
    "Bleu":   "Proximité",
    "Vert":   "Méthode durable",
    "Orange": "Équité",
}


# ---------------------------------------------------------------------------
# CALCUL POUR UN PRODUIT UNIQUE
# ---------------------------------------------------------------------------

def calculer_score(notes: dict[str, int], categorie: str) -> dict:
    """
    Calcule le SQQ-Score complet d'un produit.

    Paramètres
    ----------
    notes : dict  {nom_critere: note (1-5)}
    categorie : str  — clé dans CRITERES

    Retourne
    --------
    dict avec les clés :
        score_global_pct  : float  — score global en %
        scores_themes     : dict   — {theme: pct}
        pastilles         : list   — thèmes dont le score >= SEUIL_PASTILLE
        detail            : list   — liste de dicts par critère
    """
    criteres = CRITERES[categorie]
    total_obt, total_max = 0, 0
    theme_obt: dict[str, int] = {t: 0 for t in THEMES}
    theme_max: dict[str, int] = {t: 0 for t in THEMES}
    detail = []

    for nom, theme, poids in criteres:
        note = notes.get(nom, 0)
        contribution = note * poids
        max_contribution = 5 * poids

        total_obt += contribution
        total_max += max_contribution
        theme_obt[theme] += contribution
        theme_max[theme] += max_contribution

        detail.append({
            "critere": nom,
            "theme": theme,
            "poids": poids,
            "note": note,
            "score_obt": contribution,
            "score_max": max_contribution,
        })

    score_global_pct = round((total_obt / total_max) * 100, 1) if total_max else 0.0

    scores_themes: dict[str, float] = {}
    for t in THEMES:
        if theme_max[t] > 0:
            scores_themes[t] = round((theme_obt[t] / theme_max[t]) * 100, 1)
        else:
            scores_themes[t] = None  # thème absent de cette catégorie

    pastilles = [
        t for t in THEMES
        if scores_themes[t] is not None and scores_themes[t] >= SEUIL_PASTILLE
    ]

    return {
        "score_global_pct": score_global_pct,
        "scores_themes": scores_themes,
        "pastilles": pastilles,
        "detail": detail,
    }


def construire_lignes_produit(
    nom_produit: str,
    categorie: str,
    sous_categorie: str,
    notes: dict[str, int],
    date_saisie: str,
) -> list[dict]:
    """
    Construit les lignes à ajouter dans le DataFrame produits.
    Une ligne par critère (format long = tidy data).
    """
    criteres_df = get_criteres_df()
    cat_criteres = criteres_df[criteres_df["categorie"] == categorie]
    lignes = []
    for _, row in cat_criteres.iterrows():
        note = notes.get(row["critere"], 0)
        lignes.append({
            "produit": nom_produit,
            "categorie": categorie,
            "sous_categorie": sous_categorie,
            "critere": row["critere"],
            "theme": row["theme"],
            "poids": row["poids"],
            "note": note,
            "date_saisie": date_saisie,
        })
    return lignes


# ---------------------------------------------------------------------------
# AGRÉGATION POUR LE DASHBOARD
# ---------------------------------------------------------------------------

def agregat_scores(df_produits: pd.DataFrame) -> pd.DataFrame:
    """
    À partir du DataFrame produits (format long), calcule pour chaque produit :
      - score_global_pct
      - score_Bleu_pct, score_Vert_pct, score_Orange_pct
      - pastilles (liste)
      - categorie, sous_categorie

    Retourne un DataFrame "wide" à une ligne par produit.
    """
    if df_produits.empty:
        return pd.DataFrame()

    df = df_produits.copy()
    df["score_obt"] = df["note"] * df["poids"]
    df["score_max"] = 5 * df["poids"]

    # Score global
    global_grp = df.groupby("produit")[["score_obt", "score_max"]].sum()
    global_grp["score_global_pct"] = (
        global_grp["score_obt"] / global_grp["score_max"] * 100
    ).round(1)

    # Score par thème
    theme_grp = (
        df.groupby(["produit", "theme"])[["score_obt", "score_max"]]
        .sum()
        .reset_index()
    )
    theme_grp["score_pct"] = (
        theme_grp["score_obt"] / theme_grp["score_max"] * 100
    ).round(1)

    # Pivot thème → colonnes
    theme_pivot = theme_grp.pivot(
        index="produit", columns="theme", values="score_pct"
    ).rename(
        columns={t: f"score_{t}_pct" for t in THEMES}
    )
    for col in [f"score_{t}_pct" for t in THEMES]:
        if col not in theme_pivot.columns:
            theme_pivot[col] = None

    # Méta-données (catégorie, sous-catégorie, date)
    meta = (
        df.groupby("produit")[["categorie", "sous_categorie", "date_saisie"]]
        .first()
    )

    result = meta.join(global_grp[["score_global_pct"]]).join(theme_pivot)
    result = result.reset_index()

    # Pastilles
    def _pastilles(row):
        p = []
        for t in THEMES:
            val = row.get(f"score_{t}_pct")
            if val is not None and val >= SEUIL_PASTILLE:
                p.append(t)
        return p

    result["pastilles"] = result.apply(_pastilles, axis=1)
    return result


def filtrer_par_selection(
    df_agreg: pd.DataFrame,
    categorie: str | None = None,
    sous_categorie: str | None = None,
) -> pd.DataFrame:
    """
    Filtre le DataFrame agrégé par catégorie et/ou sous-catégorie.
    Si les deux sont None, retourne tout.
    """
    df = df_agreg.copy()
    if categorie:
        df = df[df["categorie"] == categorie]
    if sous_categorie:
        df = df[df["sous_categorie"] == sous_categorie]
    return df
