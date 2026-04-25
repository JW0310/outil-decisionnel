# === IMPORT DES LIBRAIRIES ===
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import filtre_villes


# =====================
# CONFIGURATION PAGE
# =====================
st.set_page_config(page_title="Emploi", layout="wide")

st.title("💼 Analyse de l'emploi")


# =====================
# DATA
# =====================
df = pd.read_parquet("data/processed/fact_emploi.parquet")


# =====================
# SÉLECTION GLOBALE DES VILLES
# =====================
code_ville1, code_ville2, ville1, ville2 = filtre_villes()


# =====================
# FILTRAGE DES DONNÉES
# =====================
df["code_commune"] = df["code_commune"].astype(str).str.zfill(5)

df = df[df["code_commune"].isin([code_ville1, code_ville2])].copy()

df_v1 = df[df["code_commune"] == code_ville1].copy()
df_v2 = df[df["code_commune"] == code_ville2].copy()

df_v1_sans = df_v1[df_v1["secteur"] != "Autres"].copy()
df_v2_sans = df_v2[df_v2["secteur"] != "Autres"].copy()

couleurs_villes = {
    ville1: "#1f77b4",
    ville2: "#ff7f0e"
}

st.markdown(f"### Analyse comparative : **{ville1}** vs **{ville2}**")


# =====================
# KPI
# =====================
st.subheader("Indicateurs emploi clés")

total_v1 = int(df_v1["nb"].sum())
total_v2 = int(df_v2["nb"].sum())

top_v1_row = df_v1_sans.loc[df_v1_sans["nb"].idxmax()]
top_v2_row = df_v2_sans.loc[df_v2_sans["nb"].idxmax()]

top_v1 = top_v1_row["secteur"]
top_v2 = top_v2_row["secteur"]

top_v1_nb = int(top_v1_row["nb"])
top_v2_nb = int(top_v2_row["nb"])

nb_sec_v1 = int(df_v1["secteur"].nunique())
nb_sec_v2 = int(df_v2["secteur"].nunique())


# === AFFICHAGE KPI ===
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"#### {ville1}")
    k1, k2, k3 = st.columns(3)

    k1.metric(
        "Emplois",
        f"{total_v1:,}",
        help="Volume d’emplois estimés à partir de la base FLORES 2024."
    )
    k2.metric(
        "Secteur clé",
        top_v1,
        delta=f"{top_v1_nb:,} emplois",
        help="Secteur principal hors catégorie 'Autres'."
    )
    k3.metric(
        "Secteurs",
        nb_sec_v1,
        help="Nombre de macro-secteurs présents dans la ville."
    )

with col2:
    st.markdown(f"#### {ville2}")
    k1, k2, k3 = st.columns(3)

    k1.metric(
        "Emplois",
        f"{total_v2:,}",
        help="Volume d’emplois estimés à partir de la base FLORES 2024."
    )
    k2.metric(
        "Secteur clé",
        top_v2,
        delta=f"{top_v2_nb:,} emplois",
        help="Secteur principal hors catégorie 'Autres'."
    )
    k3.metric(
        "Secteurs",
        nb_sec_v2,
        help="Nombre de macro-secteurs présents dans la ville."
    )


# =====================
# EMPLOIS PAR SECTEUR
# =====================
st.subheader("Nombre d’emplois par secteur")

pivot = df.pivot_table(
    index="secteur",
    columns="nom_commune",
    values="nb",
    aggfunc="sum"
).fillna(0)

pivot = pivot.sort_values(by=ville2, ascending=True)

fig_bar = px.bar(
    pivot,
    x=[ville1, ville2],
    y=pivot.index,
    orientation="h",
    barmode="group",
    text_auto=".0f",
    color_discrete_map=couleurs_villes,
    labels={
        "value": "Nombre d’emplois",
        "secteur": "Secteur",
        "variable": "Ville"
    }
)

fig_bar.update_traces(
    textposition="outside",
    cliponaxis=False
)

fig_bar.update_layout(
    xaxis_title="Nombre d’emplois",
    yaxis_title="Secteur",
    legend_title="Ville",
    margin=dict(l=20, r=120, t=20, b=20)
)

st.plotly_chart(fig_bar, use_container_width=True)


# =====================
# ÉCART DE SPÉCIALISATION
# =====================
st.subheader("Écart de spécialisation sectorielle")

df_percent = df.copy()
df_percent["part"] = df_percent.groupby("nom_commune")["nb"].transform(
    lambda x: x / x.sum() * 100
)

pivot_part = df_percent.pivot_table(
    index="secteur",
    columns="nom_commune",
    values="part",
    aggfunc="sum"
).fillna(0)

pivot_part["ecart"] = pivot_part[ville2] - pivot_part[ville1]

pivot_part = pivot_part.reset_index().sort_values("ecart")

fig_ecart = px.bar(
    pivot_part,
    x="ecart",
    y="secteur",
    orientation="h",
    text_auto=".1f",
    labels={
        "ecart": f"Écart en points de % ({ville2} - {ville1})",
        "secteur": "Secteur"
    }
)

fig_ecart.update_layout(
    xaxis_title=f"Écart en points de % ({ville2} - {ville1})",
    yaxis_title="Secteur",
    showlegend=False,
    margin=dict(l=20, r=120, t=20, b=20)
)

st.plotly_chart(fig_ecart, use_container_width=True)

st.info(
    f"Un écart positif signifie que le secteur est proportionnellement plus représenté à {ville2}. "
    f"Un écart négatif signifie qu’il est proportionnellement plus représenté à {ville1}."
)


# =====================
# TABLEAU
# =====================
st.subheader("Détail des emplois")

df_table = df.sort_values(["nom_commune", "nb"], ascending=[True, False]).copy()
df_table["nb"] = df_table["nb"].round(0).astype(int)

df_table = df_table[[
    "nom_commune",
    "code_commune",
    "secteur",
    "nb"
]].rename(columns={
    "nom_commune": "Ville",
    "code_commune": "Code commune",
    "secteur": "Secteur",
    "nb": "Nombre d’emplois"
})

st.dataframe(df_table, use_container_width=True)


# =====================
# LECTURE SYNTHÉTIQUE
# =====================
st.subheader("Lecture synthétique")

ville_plus = ville1 if total_v1 > total_v2 else ville2
ecart_total = abs(total_v1 - total_v2)

part_v1 = round((top_v1_nb / total_v1) * 100, 1)
part_v2 = round((top_v2_nb / total_v2) * 100, 1)

secteur_commun = top_v1 if top_v1 == top_v2 else None

secteur_plus_marque = pivot_part.loc[pivot_part["ecart"].abs().idxmax(), "secteur"]
ecart_plus_marque = round(pivot_part["ecart"].abs().max(), 1)

st.markdown(
    f"""
- **{ville_plus}** concentre le plus d’emplois, avec un écart d’environ **{ecart_total:,} emplois**.
- À **{ville1}**, le secteur principal hors catégorie résiduelle est **{top_v1}**, soit **{part_v1} %** des emplois.
- À **{ville2}**, le secteur principal hors catégorie résiduelle est **{top_v2}**, soit **{part_v2} %** des emplois.
- L’écart de spécialisation le plus marqué concerne le secteur **{secteur_plus_marque}**, avec environ **{ecart_plus_marque} points** d’écart.
"""
)

if secteur_commun:
    st.markdown(
        f"- Les deux villes partagent un secteur dominant commun : **{secteur_commun}**."
    )
else:
    st.markdown(
        "- Les deux villes présentent des spécialisations économiques différentes."
    )