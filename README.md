# SQQ-Score · SuperQuinquin

Outil d'aide à la décision RSE pour le supermarché coopératif SuperQuinquin (Lille).

## Structure du projet

```
sqq_tool/
├── app.py              # Application Streamlit (interface principale)
├── sqq_data.py         # Catégories, sous-catégories, grilles de critères
├── sqq_engine.py       # Moteur de calcul du SQQ-Score
├── sqq_store.py        # Persistance CSV (lecture / écriture)
├── requirements.txt
└── data/
    └── produits.csv    # Créé automatiquement au premier enregistrement
```

## Installation et lancement

```bash
# 1. Créer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'application
streamlit run app.py
```

L'interface s'ouvre automatiquement sur `http://localhost:8501`.

## Modifier la grille de critères

Toutes les définitions (catégories, sous-catégories, critères, poids, thèmes) se trouvent
dans `sqq_data.py`. Aucune modification d'`app.py` ou de `sqq_engine.py` n'est nécessaire.

### Changer le seuil d'activation des pastilles

Dans `sqq_engine.py`, modifiez la constante :

```python
SEUIL_PASTILLE: int = 70  # %
```

## Logique du SQQ-Score

```
score_obtenu  = Σ (note × poids)         [note ∈ 1..5]
score_maximum = Σ (5 × poids)
SQQ-Score (%) = (score_obtenu / score_maximum) × 100

Score par pilier identique, mais limité aux critères du pilier.
Pastille accordée si score_pilier ≥ SEUIL_PASTILLE.
```

### Règle d'assortiment 70/30

- **≥ 70 %** de la gamme doit avoir un SQQ-Score ≥ 70 % (gamme principale RSE).
- **≤ 30 %** peut avoir un score inférieur (produits dépannage / accessibilité prix).

Le Dashboard calcule et affiche en temps réel le respect de cette règle.
