"""
app.py
======
Application Streamlit principale pour l'outil SQQ-Score de SuperQuinquin.

Lancement :
    streamlit run app.py

Onglets :
  1. Évaluer un produit   — saisie guidée + calcul en temps réel
  2. Dashboard d'analyse  — bar chart comparatif des 3 piliers par sélection
  3. Base de données      — liste complète + suppression de produits
"""

from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from sqq_data import CATEGORIES, CRITERES, SOUS_CATEGORIES, THEME_LABELS
from sqq_engine import (
    SEUIL_PASTILLE,
    THEMES,
    agregat_scores,
    calculer_score,
    construire_lignes_produit,
    filtrer_par_selection,
)
from sqq_store import (
    charger_produits,
    produit_existe,
    sauvegarder_produit,
    supprimer_produit,
)

# ---------------------------------------------------------------------------
# CONFIGURATION GÉNÉRALE
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="SQQ-Score · SuperQuinquin",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Couleurs des 3 piliers (accessibles, contrastées)
COULEURS = {
    "Bleu":   "#185FA5",
    "Vert":   "#3B6D11",
    "Orange": "#854F0B",
}
COULEURS_BG = {
    "Bleu":   "#E6F1FB",
    "Vert":   "#EAF3DE",
    "Orange": "#FAEEDA",
}

# CSS minimal pour les pastilles et quelques ajustements visuels
st.markdown("""
<style>
    .pastille {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 6px;
        margin-top: 4px;
    }
    .bleu   { background:#E6F1FB; color:#0C447C; }
    .vert   { background:#EAF3DE; color:#27500A; }
    .orange { background:#FAEEDA; color:#633806; }
    .off    { background:#f0f0f0; color:#888; opacity:0.55; }
    .score-big { font-size: 2.6rem; font-weight: 700; line-height: 1.1; }
    .score-sub { font-size: 0.8rem; color: #666; margin-top: 2px; }
    div[data-testid="stMetric"] label { font-size: 0.75rem !important; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# EN-TÊTE
# ---------------------------------------------------------------------------

col_logo, col_titre = st.columns([1, 6])
with col_logo:
    st.markdown("## 🛒")
with col_titre:
    st.markdown("## SQQ-Score · SuperQuinquin")
    st.caption("Outil d'aide à la décision RSE — Achats coopératifs")

st.divider()


# ---------------------------------------------------------------------------
# ONGLETS PRINCIPAUX
# ---------------------------------------------------------------------------

tab_eval, tab_dash, tab_base = st.tabs([
    "📝 Évaluer un produit",
    "📊 Dashboard d'analyse",
    "🗄️ Base de données",
])


# ============================================================
# ONGLET 1 — ÉVALUATION D'UN PRODUIT
# ============================================================

with tab_eval:
    st.subheader("Évaluation d'un nouveau produit")

    col_form, col_result = st.columns([1.1, 1], gap="large")

    with col_form:
        # --- Identité du produit ---
        with st.container(border=True):
            st.markdown("**Identité du produit**")

            nom_produit = st.text_input(
                "Nom du produit",
                placeholder="ex : Carottes Ferme Dupont",
                key="nom_produit",
            )

            categorie = st.selectbox(
                "Catégorie",
                options=[""] + CATEGORIES,
                key="categorie_eval",
            )

            sous_cat_options = SOUS_CATEGORIES.get(categorie, []) if categorie else []
            sous_categorie = st.selectbox(
                "Sous-catégorie",
                options=[""] + sous_cat_options,
                disabled=(not categorie),
                key="sous_categorie_eval",
            )

            date_saisie = st.date_input(
                "Date d'évaluation",
                value=date.today(),
                key="date_eval",
            )

        # --- Grille de notation ---
        notes_saisies: dict[str, int] = {}
        saisie_complete = False

        if categorie:
            st.markdown("---")
            st.markdown("**Grille de notation** — 1 : rédhibitoire · 5 : excellent")

            criteres_cat = CRITERES[categorie]

            for nom_crit, theme, poids in criteres_cat:
                col_c, col_n = st.columns([3, 1])
                with col_c:
                    badge = f'<span class="pastille {theme.lower()}">{THEME_LABELS[theme]}</span>'
                    st.markdown(
                        f"{nom_crit} {badge} *(poids {poids})*",
                        unsafe_allow_html=True,
                    )
                with col_n:
                    note = st.selectbox(
                        label=nom_crit,
                        options=[1, 2, 3, 4, 5],
                        index=2,  # défaut = 3
                        label_visibility="collapsed",
                        key=f"note_{nom_crit}",
                    )
                notes_saisies[nom_crit] = note

            saisie_complete = bool(categorie and sous_categorie and nom_produit)

        # --- Bouton de sauvegarde ---
        st.markdown("")
        btn_save = st.button(
            "💾 Calculer et sauvegarder",
            type="primary",
            disabled=not saisie_complete,
            use_container_width=True,
        )

    # --- Résultat en temps réel (colonne droite) ---
    with col_result:
        if categorie and notes_saisies:
            result = calculer_score(notes_saisies, categorie)
            pct = result["score_global_pct"]
            scores_t = result["scores_themes"]
            pastilles = result["pastilles"]

            # Score global
            couleur_score = (
                COULEURS["Vert"] if pct >= 70
                else COULEURS["Orange"] if pct >= 50
                else "#A32D2D"
            )
            classe_score = (
                "Produit RSE élevé — gamme principale ✅"
                if pct >= 70
                else "Score intermédiaire — à améliorer 🔶"
                if pct >= 50
                else "Score faible — gamme dépannage (30 %) 🔴"
            )

            with st.container(border=True):
                st.markdown("**Score global**")
                st.markdown(
                    f'<div class="score-big" style="color:{couleur_score}">{pct} %</div>'
                    f'<div class="score-sub">{classe_score}</div>',
                    unsafe_allow_html=True,
                )
                st.progress(int(pct) / 100)

            # Pastilles
            st.markdown("**Pastilles obtenues**")
            pastille_html = ""
            for t in THEMES:
                label = THEME_LABELS[t]
                val = scores_t.get(t)
                val_str = f"{val} %" if val is not None else "—"
                if t in pastilles:
                    cls = t.lower()
                    pastille_html += f'<span class="pastille {cls}">{label} · {val_str}</span>'
                else:
                    pastille_html += f'<span class="pastille off">{label} · {val_str}</span>'
            st.markdown(pastille_html, unsafe_allow_html=True)

            # Détail par thème — mini barres
            st.markdown("")
            st.markdown("**Détail par pilier**")
            for t in THEMES:
                val = scores_t.get(t)
                if val is None:
                    continue
                label = THEME_LABELS[t]
                col_l, col_b = st.columns([1.2, 2])
                with col_l:
                    st.markdown(
                        f'<span class="pastille {t.lower()}">{label}</span>',
                        unsafe_allow_html=True,
                    )
                with col_b:
                    st.progress(int(val) / 100, text=f"{val} %")

            # Règle 70 / 30
            st.markdown("")
            st.info(
                f"Seuil d'activation des pastilles : **{SEUIL_PASTILLE} %** par pilier.",
                icon="ℹ️",
            )
        else:
            st.info("Sélectionnez une catégorie et notez les critères pour voir le score.", icon="👈")

    # --- Sauvegarde ---
    if btn_save and saisie_complete:
        if produit_existe(nom_produit):
            st.warning(
                f"⚠️ Le produit **{nom_produit}** existe déjà dans la base. "
                "Supprimez-le d'abord depuis l'onglet 'Base de données' pour le re-évaluer.",
                icon="⚠️",
            )
        else:
            lignes = construire_lignes_produit(
                nom_produit=nom_produit,
                categorie=categorie,
                sous_categorie=sous_categorie,
                notes=notes_saisies,
                date_saisie=str(date_saisie),
            )
            sauvegarder_produit(lignes)
            st.success(f"✅ **{nom_produit}** sauvegardé avec un SQQ-Score de **{pct} %**.")
            st.balloons()


# ============================================================
# ONGLET 2 — DASHBOARD D'ANALYSE
# ============================================================

with tab_dash:
    st.subheader("Dashboard d'analyse — Comparaison des 3 piliers")

    df_prod = charger_produits()

    if df_prod.empty:
        st.info(
            "Aucun produit dans la base. Évaluez et sauvegardez des produits depuis le premier onglet.",
            icon="📭",
        )
    else:
        df_agreg = agregat_scores(df_prod)

        # --- Filtres ---
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            cats_dispo = ["Toutes"] + sorted(df_agreg["categorie"].unique().tolist())
            filtre_cat = st.selectbox("Catégorie", cats_dispo, key="dash_cat")

        with col_f2:
            if filtre_cat != "Toutes":
                sous_dispo = ["Toutes"] + sorted(
                    df_agreg[df_agreg["categorie"] == filtre_cat]["sous_categorie"]
                    .unique()
                    .tolist()
                )
            else:
                sous_dispo = ["Toutes"] + sorted(df_agreg["sous_categorie"].unique().tolist())
            filtre_sous = st.selectbox("Sous-catégorie", sous_dispo, key="dash_sous")

        with col_f3:
            tri_options = ["Score global ↓", "Score global ↑", "Alphabétique"]
            tri = st.selectbox("Trier par", tri_options, key="dash_tri")

        # Application des filtres
        df_filtre = filtrer_par_selection(
            df_agreg,
            categorie=None if filtre_cat == "Toutes" else filtre_cat,
            sous_categorie=None if filtre_sous == "Toutes" else filtre_sous,
        )

        if df_filtre.empty:
            st.warning("Aucun produit pour cette sélection.")
        else:
            # Tri
            if tri == "Score global ↓":
                df_filtre = df_filtre.sort_values("score_global_pct", ascending=False)
            elif tri == "Score global ↑":
                df_filtre = df_filtre.sort_values("score_global_pct", ascending=True)
            else:
                df_filtre = df_filtre.sort_values("produit")

            # --- Métriques synthèse ---
            n_total = len(df_filtre)
            n_hauts = int((df_filtre["score_global_pct"] >= 70).sum())
            n_bas   = n_total - n_hauts
            pct_bas = round((n_bas / n_total) * 100) if n_total else 0

            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Produits sélectionnés", n_total)
            col_m2.metric("RSE élevé (≥ 70 %)", n_hauts)
            col_m3.metric("Score bas (< 70 %)", n_bas)
            col_m4.metric(
                "Règle 70/30",
                "✅ Respectée" if pct_bas <= 30 else "⚠️ Dépassée",
                delta=f"{pct_bas} % de produits bas",
                delta_color="normal" if pct_bas <= 30 else "inverse",
            )

            st.divider()

            # --- Graphique en bâtons groupés : 3 piliers par produit ---
            st.markdown("#### Scores par pilier et par produit")
            st.caption(
                "Barre bleue = Proximité · Verte = Méthode durable · Orange = Équité"
            )

            produits = df_filtre["produit"].tolist()
            scores_bleu   = df_filtre["score_Bleu_pct"].fillna(0).tolist()
            scores_vert   = df_filtre["score_Vert_pct"].fillna(0).tolist()
            scores_orange = df_filtre["score_Orange_pct"].fillna(0).tolist()

            fig = go.Figure()

            fig.add_trace(go.Bar(
                name="Proximité (Bleu)",
                x=produits,
                y=scores_bleu,
                marker_color=COULEURS["Bleu"],
                text=[f"{v:.0f} %" for v in scores_bleu],
                textposition="outside",
                cliponaxis=False,
            ))
            fig.add_trace(go.Bar(
                name="Méthode durable (Vert)",
                x=produits,
                y=scores_vert,
                marker_color=COULEURS["Vert"],
                text=[f"{v:.0f} %" for v in scores_vert],
                textposition="outside",
                cliponaxis=False,
            ))
            fig.add_trace(go.Bar(
                name="Équité (Orange)",
                x=produits,
                y=scores_orange,
                marker_color=COULEURS["Orange"],
                text=[f"{v:.0f} %" for v in scores_orange],
                textposition="outside",
                cliponaxis=False,
            ))

            # Ligne seuil pastille
            fig.add_hline(
                y=SEUIL_PASTILLE,
                line_dash="dash",
                line_color="#888",
                annotation_text=f"Seuil pastille ({SEUIL_PASTILLE} %)",
                annotation_position="top right",
                annotation_font_size=11,
            )

            fig.update_layout(
                barmode="group",
                yaxis=dict(
                    range=[0, 115],
                    ticksuffix=" %",
                    gridcolor="#eee",
                    title="Score du pilier (%)",
                ),
                xaxis=dict(title="Produit"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor="white",
                paper_bgcolor="white",
                margin=dict(t=60, b=80, l=60, r=20),
                font=dict(family="sans-serif", size=12),
                height=480,
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- Score global (ligne) ---
            st.markdown("#### Score global par produit")
            fig2 = go.Figure()
            couleurs_glob = [
                COULEURS["Vert"] if v >= 70 else COULEURS["Orange"] if v >= 50 else "#A32D2D"
                for v in df_filtre["score_global_pct"]
            ]
            fig2.add_trace(go.Bar(
                x=produits,
                y=df_filtre["score_global_pct"].tolist(),
                marker_color=couleurs_glob,
                text=[f"{v:.0f} %" for v in df_filtre["score_global_pct"]],
                textposition="outside",
                showlegend=False,
            ))
            fig2.add_hline(
                y=70,
                line_dash="dot",
                line_color=COULEURS["Vert"],
                annotation_text="Seuil RSE élevé (70 %)",
                annotation_position="top left",
                annotation_font_color=COULEURS["Vert"],
                annotation_font_size=11,
            )
            fig2.update_layout(
                yaxis=dict(range=[0, 115], ticksuffix=" %", gridcolor="#eee", title="Score global (%)"),
                xaxis=dict(title="Produit"),
                plot_bgcolor="white",
                paper_bgcolor="white",
                margin=dict(t=40, b=80, l=60, r=20),
                font=dict(family="sans-serif", size=12),
                height=380,
            )
            st.plotly_chart(fig2, use_container_width=True)

            # --- Interprétation automatique ---
            st.markdown("#### Lecture automatique de l'offre")
            col_i1, col_i2 = st.columns(2)
            with col_i1:
                moy_bleu   = df_filtre["score_Bleu_pct"].mean()
                moy_vert   = df_filtre["score_Vert_pct"].mean()
                moy_orange = df_filtre["score_Orange_pct"].mean()

                pilier_fort   = max(["Bleu","Vert","Orange"], key=lambda t: df_filtre[f"score_{t}_pct"].mean())
                pilier_faible = min(["Bleu","Vert","Orange"], key=lambda t: df_filtre[f"score_{t}_pct"].mean())

                st.success(
                    f"**Point fort** : {THEME_LABELS[pilier_fort]} "
                    f"(moy. {df_filtre[f'score_{pilier_fort}_pct'].mean():.0f} %)"
                )
                st.warning(
                    f"**Point à améliorer** : {THEME_LABELS[pilier_faible]} "
                    f"(moy. {df_filtre[f'score_{pilier_faible}_pct'].mean():.0f} %)"
                )
            with col_i2:
                if pct_bas > 30:
                    st.error(
                        f"La règle 70/30 n'est pas respectée : "
                        f"**{pct_bas} %** des produits ont un score bas "
                        f"(seuil max : 30 %).\n\nAction recommandée : réduire les produits "
                        f"'dépannage' ou référencer de nouveaux fournisseurs RSE."
                    )
                else:
                    st.success(
                        f"Règle 70/30 respectée : seulement **{pct_bas} %** "
                        f"des produits affichent un score bas."
                    )


# ============================================================
# ONGLET 3 — BASE DE DONNÉES
# ============================================================

with tab_base:
    st.subheader("Base de données — Produits évalués")

    df_prod = charger_produits()

    if df_prod.empty:
        st.info("Aucun produit enregistré.", icon="📭")
    else:
        df_agreg = agregat_scores(df_prod)

        # Tableau synthèse
        affichage = df_agreg[[
            "produit", "categorie", "sous_categorie",
            "score_global_pct", "score_Bleu_pct", "score_Vert_pct", "score_Orange_pct",
            "pastilles", "date_saisie",
        ]].copy()

        affichage.columns = [
            "Produit", "Catégorie", "Sous-catégorie",
            "Score global (%)", "Proximité (%)", "Méthode durable (%)", "Équité (%)",
            "Pastilles", "Date",
        ]
        affichage["Pastilles"] = affichage["Pastilles"].apply(
            lambda lst: " · ".join([THEME_LABELS[t] for t in lst]) if lst else "—"
        )

        st.dataframe(
            affichage,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Score global (%)": st.column_config.ProgressColumn(
                    "Score global (%)", min_value=0, max_value=100, format="%.1f %%"
                ),
                "Proximité (%)": st.column_config.ProgressColumn(
                    "Proximité (%)", min_value=0, max_value=100, format="%.1f %%"
                ),
                "Méthode durable (%)": st.column_config.ProgressColumn(
                    "Méthode durable (%)", min_value=0, max_value=100, format="%.1f %%"
                ),
                "Équité (%)": st.column_config.ProgressColumn(
                    "Équité (%)", min_value=0, max_value=100, format="%.1f %%"
                ),
            },
        )

        st.caption(f"{len(df_agreg)} produit(s) dans la base.")

        # Export CSV
        csv_export = affichage.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Exporter en CSV",
            data=csv_export,
            file_name="sqq_produits_export.csv",
            mime="text/csv",
        )

        # Suppression d'un produit
        st.divider()
        st.markdown("**Supprimer un produit**")
        produits_liste = sorted(df_agreg["produit"].unique().tolist())
        produit_a_suppr = st.selectbox("Sélectionner le produit à supprimer", produits_liste, key="suppr_sel")
        if st.button("🗑️ Supprimer", type="secondary", key="btn_suppr"):
            supprimer_produit(produit_a_suppr)
            st.success(f"Produit **{produit_a_suppr}** supprimé.")
            st.rerun()
