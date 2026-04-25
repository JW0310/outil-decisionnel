# === IMPORT DES LIBRAIRIES ===
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import filtre_villes


# === CONFIGURATION DE LA PAGE ===
st.set_page_config(page_title="Logement", layout="wide")

st.title("🏠 Analyse logement")


# === CHARGEMENT DES DONNÉES ===
df = pd.read_parquet("data/processed/fact_logement.parquet")


# =====================
# PRÉPARATION DES DONNÉES
# =====================
ordre_mois = [
    "2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06",
    "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"
]

df["annee_mois"] = pd.Categorical(
    df["annee_mois"],
    categories=ordre_mois,
    ordered=True
)

df = df.sort_values("annee_mois")


# =====================
# SÉLECTION GLOBALE DES VILLES
# =====================
code_ville1, code_ville2, ville1, ville2 = filtre_villes()


# =====================
# FILTRAGE DES DONNÉES
# =====================
df["code_commune"] = df["code_commune"].astype(str).str.zfill(5)

df = df[df["code_commune"].isin([code_ville1, code_ville2])].copy()

df_ville1 = df[df["code_commune"] == code_ville1].copy()
df_ville2 = df[df["code_commune"] == code_ville2].copy()

couleurs_villes = {
    ville1: "#1f77b4",
    ville2: "#ff7f0e"
}

st.markdown(f"### Analyse comparative : **{ville1}** vs **{ville2}**")


# =====================
# FORMATAGE MOIS
# =====================
mois_labels = {
    "01": "Janvier", "02": "Février", "03": "Mars",
    "04": "Avril", "05": "Mai", "06": "Juin",
    "07": "Juillet", "08": "Août", "09": "Septembre",
    "10": "Octobre", "11": "Novembre", "12": "Décembre"
}

def format_mois_annee(valeur):
    annee, mois = str(valeur).split("-")
    return f"{mois_labels[mois]} {annee}"


# =====================
# KPI
# =====================
st.subheader("Indicateurs logement clés")

prix_moy_v1 = int(round(df_ville1["prix_m2"].mean(), 0))
prix_moy_v2 = int(round(df_ville2["prix_m2"].mean(), 0))

row_v1 = df_ville1.loc[df_ville1["prix_m2"].idxmax()]
row_v2 = df_ville2.loc[df_ville2["prix_m2"].idxmax()]

mois_v1 = format_mois_annee(row_v1["annee_mois"])
mois_v2 = format_mois_annee(row_v2["annee_mois"])

prix_v1_max = int(round(row_v1["prix_m2"], 0))
prix_v2_max = int(round(row_v2["prix_m2"], 0))

evol_v1 = round(
    ((df_ville1["prix_m2"].iloc[-1] - df_ville1["prix_m2"].iloc[0]) / df_ville1["prix_m2"].iloc[0]) * 100,
    1
)

evol_v2 = round(
    ((df_ville2["prix_m2"].iloc[-1] - df_ville2["prix_m2"].iloc[0]) / df_ville2["prix_m2"].iloc[0]) * 100,
    1
)


# === AFFICHAGE KPI ===
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"#### {ville1}")
    k1, k2, k3 = st.columns(3)

    k1.metric(
        "Prix annuel",
        f"{prix_moy_v1:,} €/m²",
        help="Moyenne des prix mensuels au m² sur l’année 2024."
    )
    k2.metric(
        "Mois le + cher",
        mois_v1,
        delta=f"{prix_v1_max:,} €/m²",
        help="Mois avec le prix moyen au m² le plus élevé."
    )
    k3.metric(
        "Évolution",
        f"{evol_v1} %",
        help="Évolution entre le premier et le dernier mois disponible."
    )

with col2:
    st.markdown(f"#### {ville2}")
    k1, k2, k3 = st.columns(3)

    k1.metric(
        "Prix annuel",
        f"{prix_moy_v2:,} €/m²",
        help="Moyenne des prix mensuels au m² sur l’année 2024."
    )
    k2.metric(
        "Mois le + cher",
        mois_v2,
        delta=f"{prix_v2_max:,} €/m²",
        help="Mois avec le prix moyen au m² le plus élevé."
    )
    k3.metric(
        "Évolution",
        f"{evol_v2} %",
        help="Évolution entre le premier et le dernier mois disponible."
    )


# =====================
# GRAPHIQUE PRIX
# =====================
st.subheader("Évolution mensuelle du prix moyen au m²")

fig_prix = px.line(
    df,
    x="annee_mois",
    y="prix_m2",
    color="nom_commune",
    markers=True,
    color_discrete_map=couleurs_villes,
    labels={
        "annee_mois": "Mois",
        "prix_m2": "Prix moyen (€/m²)",
        "nom_commune": "Ville"
    }
)

fig_prix.update_layout(
    xaxis_title="Mois",
    yaxis_title="Prix moyen (€/m²)",
    legend_title="Ville",
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig_prix, use_container_width=True)


# =====================
# ÉCART DE PRIX
# =====================
df_ecart = df.pivot_table(
    index="annee_mois",
    columns="nom_commune",
    values="prix_m2",
    aggfunc="mean"
).reset_index()

df_ecart["ecart"] = (df_ecart[ville2] - df_ecart[ville1]).round(0)

st.subheader(f"Écart de prix au m² : {ville2} - {ville1}")

fig_ecart = px.bar(
    df_ecart,
    x="annee_mois",
    y="ecart",
    text_auto=".0f",
    labels={
        "annee_mois": "Mois",
        "ecart": "Écart de prix (€/m²)"
    }
)

fig_ecart.update_layout(
    xaxis_title="Mois",
    yaxis_title="Écart de prix (€/m²)",
    showlegend=False,
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig_ecart, use_container_width=True)

st.info(
    f"Un écart positif signifie que {ville2} est plus cher que {ville1} sur le mois concerné. "
    f"Un écart négatif signifie que {ville1} est plus cher."
)


# =====================
# LECTURE SYNTHÉTIQUE
# =====================
st.subheader("Lecture synthétique")

ville_chere = ville1 if prix_moy_v1 > prix_moy_v2 else ville2
ville_hausse = ville1 if evol_v1 > evol_v2 else ville2

ecart_moyen = int(round(abs(df_ecart["ecart"]).mean(), 0))
ecart_max_abs = int(round(df_ecart["ecart"].abs().max(), 0))

ligne_ecart_max = df_ecart.loc[df_ecart["ecart"].abs().idxmax()]
mois_ecart_max = format_mois_annee(ligne_ecart_max["annee_mois"])

st.markdown(
    f"""
- **{ville_chere}** présente le prix moyen au m² le plus élevé sur l’année.
- L’écart moyen absolu entre les deux villes est d’environ **{ecart_moyen:,} €/m²**.
- L’écart le plus important est observé en **{mois_ecart_max}**, avec environ **{ecart_max_abs:,} €/m²**.
- **{ville_hausse}** enregistre l’évolution annuelle la plus forte.
"""
)