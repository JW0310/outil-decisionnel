# === IMPORT DES LIBRAIRIES ===
# streamlit : création de l’interface web interactive
# pandas : manipulation des données
# plotly : création de graphiques interactifs
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# === CONFIGURATION DE LA PAGE ===
st.set_page_config(page_title="Comparaison", layout="wide")

st.title("📊 Comparaison de villes")


# === CHARGEMENT DES DONNÉES ===
df = pd.read_parquet("data/processed/fact_equipements.parquet")


# === PRÉPARATION DES DONNÉES ===
labels_categories = {
    "sport": "Sport",
    "culture_loisirs": "Culture & loisirs",
    "sante_social": "Santé",
    "education": "Éducation",
    "services": "Services",
    "transport": "Transport"
}

df["categorie_label"] = df["categorie"].map(labels_categories)


# =====================
# SÉLECTION DES VILLES
# =====================
villes = sorted(df["nom_commune"].dropna().unique())

col_select1, col_select2 = st.columns(2)

with col_select1:
    ville1 = st.selectbox("Ville 1", villes, index=0)

with col_select2:
    ville2 = st.selectbox("Ville 2", villes, index=1)

df = df[df["nom_commune"].isin([ville1, ville2])].copy()

df_ville1 = df[df["nom_commune"] == ville1].copy()
df_ville2 = df[df["nom_commune"] == ville2].copy()

st.markdown(f"### Analyse comparative : **{ville1}** vs **{ville2}**")


# =====================
# KPI
# =====================
st.subheader("Indicateurs clés")

total_ville1 = int(df_ville1["nb"].sum())
total_ville2 = int(df_ville2["nb"].sum())

nb_cat_ville1 = int(df_ville1["categorie"].nunique())
nb_cat_ville2 = int(df_ville2["categorie"].nunique())

top_ville1_row = df_ville1.loc[df_ville1["nb"].idxmax()]
top_ville2_row = df_ville2.loc[df_ville2["nb"].idxmax()]

top_ville1 = labels_categories[top_ville1_row["categorie"]]
top_ville2 = labels_categories[top_ville2_row["categorie"]]

top_ville1_nb = int(top_ville1_row["nb"])
top_ville2_nb = int(top_ville2_row["nb"])


# === AFFICHAGE KPI ===
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"#### {ville1}")
    k1, k2, k3 = st.columns(3)

    k1.metric("Équipements", f"{total_ville1:,}")
    k2.metric("Catégories", nb_cat_ville1)
    k3.metric("Catégorie dominante", top_ville1, delta=f"{top_ville1_nb:,} équipements")

with col2:
    st.markdown(f"#### {ville2}")
    k1, k2, k3 = st.columns(3)

    k1.metric("Équipements", f"{total_ville2:,}")
    k2.metric("Catégories", nb_cat_ville2)
    k3.metric("Catégorie dominante", top_ville2, delta=f"{top_ville2_nb:,} équipements")


# =====================
# GRAPHIQUE BARRES
# =====================
st.subheader("Nombre d’équipements par catégorie")

pivot = df.pivot_table(
    index="categorie_label",
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
    text_auto=True,
    labels={
        "value": "Nombre d’équipements",
        "categorie_label": "Catégorie",
        "variable": "Ville"
    }
)

fig_bar.update_layout(
    xaxis_title="Nombre d’équipements",
    yaxis_title="Catégorie",
    legend_title="Ville",
    margin=dict(l=20, r=40, t=20, b=20)
)

fig_bar.update_traces(
    textposition="outside",
    cliponaxis=False
)

st.plotly_chart(fig_bar, use_container_width=True)


# =====================
# RADAR
# =====================
st.subheader("Profil comparatif des villes")

radar_df = pivot.reset_index()

categories = radar_df["categorie_label"].tolist()
values_ville1 = radar_df[ville1].tolist()
values_ville2 = radar_df[ville2].tolist()

categories_closed = categories + [categories[0]]
values_ville1_closed = values_ville1 + [values_ville1[0]]
values_ville2_closed = values_ville2 + [values_ville2[0]]

fig_radar = go.Figure()

fig_radar.add_trace(go.Scatterpolar(
    r=values_ville1_closed,
    theta=categories_closed,
    fill="toself",
    name=ville1,
    opacity=0.6
))

fig_radar.add_trace(go.Scatterpolar(
    r=values_ville2_closed,
    theta=categories_closed,
    fill="toself",
    name=ville2,
    opacity=0.45
))

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            showticklabels=True
        )
    ),
    legend=dict(
        title="Ville",
        orientation="h",
        yanchor="bottom",
        y=1.08,
        xanchor="center",
        x=0.5
    ),
    margin=dict(l=30, r=30, t=30, b=30)
)

st.plotly_chart(fig_radar, use_container_width=True)


# =====================
# TABLEAU
# =====================
st.subheader("Détail des équipements")

df_table = df[[
    "nom_commune",
    "code_commune",
    "categorie_label",
    "nb"
]].sort_values(["nom_commune", "categorie_label"])

df_table = df_table.rename(columns={
    "nom_commune": "Ville",
    "code_commune": "Code commune",
    "categorie_label": "Catégorie",
    "nb": "Nombre d’équipements"
})

st.dataframe(df_table, use_container_width=True)


# =====================
# LECTURE SYNTHÉTIQUE
# =====================
st.subheader("Lecture synthétique")

ville_plus_equipee = ville1 if total_ville1 > total_ville2 else ville2
ecart_equipements = abs(total_ville1 - total_ville2)

st.markdown(
    f"""
- **{ville_plus_equipee}** dispose du plus grand nombre d’équipements, avec un écart d’environ **{ecart_equipements:,} équipements**.
- À **{ville1}**, la catégorie dominante est **{top_ville1}**.
- À **{ville2}**, la catégorie dominante est **{top_ville2}**.
- Le graphique radar permet de comparer rapidement le profil d’équipements des deux villes.
"""
)