import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Comparaison", layout="wide")

st.title("📊 Comparaison de villes : Lyon vs Paris")

# =====================
# DATA
# =====================
df = pd.read_parquet("data/processed/fact_equipements.parquet")

# Labels plus propres
labels_categories = {
    "sport": "Sport",
    "culture_loisirs": "Culture & loisirs",
    "sante_social": "Santé",
    "education": "Éducation",
    "services": "Services",
    "transport": "Transport"
}

df["categorie_label"] = df["categorie"].map(labels_categories)

df_lyon = df[df["ville"] == "Lyon"].copy()
df_paris = df[df["ville"] == "Paris"].copy()

# =====================
# KPI
# =====================
st.subheader("📌 Indicateurs clés")

total_lyon = int(df_lyon["nb"].sum())
total_paris = int(df_paris["nb"].sum())

nb_cat_lyon = int(df_lyon["categorie"].nunique())
nb_cat_paris = int(df_paris["categorie"].nunique())

top_cat_lyon_row = df_lyon.loc[df_lyon["nb"].idxmax()]
top_cat_paris_row = df_paris.loc[df_paris["nb"].idxmax()]

top_cat_lyon = labels_categories[top_cat_lyon_row["categorie"]]
top_cat_paris = labels_categories[top_cat_paris_row["categorie"]]

top_cat_lyon_nb = int(top_cat_lyon_row["nb"])
top_cat_paris_nb = int(top_cat_paris_row["nb"])

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏙️ Lyon")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(
        "Équipements",
        f"{total_lyon:,}",
        help="Nombre total d’équipements recensés dans la Base Permanente des Équipements pour Lyon."
    )
    kpi2.metric(
        "Catégories",
        nb_cat_lyon,
        help="Nombre de grandes catégories d’équipements présentes dans la ville."
    )
    kpi3.metric(
        "Catégorie dominante",
        top_cat_lyon,
        delta=f"{top_cat_lyon_nb:,} équipements"
    )

with col2:
    st.markdown("### 🏙️ Paris")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(
        "Équipements",
        f"{total_paris:,}",
        help="Nombre total d’équipements recensés dans la Base Permanente des Équipements pour Paris."
    )
    kpi2.metric(
        "Catégories",
        nb_cat_paris,
        help="Nombre de grandes catégories d’équipements présentes dans la ville."
    )
    kpi3.metric(
        "Catégorie dominante",
        top_cat_paris,
        delta=f"{top_cat_paris_nb:,} équipements"
    )

# =====================
# GRAPHIQUE BARRES HORIZONTALES
# =====================
st.subheader("📊 Nombre d’équipements par catégorie")

pivot = df.pivot_table(
    index="categorie_label",
    columns="ville",
    values="nb",
    aggfunc="sum"
).fillna(0)

pivot = pivot.sort_values(by="Paris", ascending=True)

fig_bar = px.bar(
    pivot,
    x=["Lyon", "Paris"],
    y=pivot.index,
    orientation="h",
    barmode="group",
    text_auto=True
)

fig_bar.update_layout(
    xaxis_title="Nombre d’équipements",
    yaxis_title="Catégorie",
    legend_title="Ville",
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig_bar, use_container_width=True)

# =====================
# RADAR RETRAVAILLÉ
# =====================
st.subheader("🧭 Profil comparatif des villes")

radar_df = pivot.reset_index()

categories = radar_df["categorie_label"].tolist()

values_lyon = radar_df["Lyon"].tolist()
values_paris = radar_df["Paris"].tolist()

# fermer le radar
categories_closed = categories + [categories[0]]
values_lyon_closed = values_lyon + [values_lyon[0]]
values_paris_closed = values_paris + [values_paris[0]]

fig_radar = go.Figure()

fig_radar.add_trace(
    go.Scatterpolar(
        r=values_lyon_closed,
        theta=categories_closed,
        fill="toself",
        name="Lyon",
        opacity=0.6
    )
)

fig_radar.add_trace(
    go.Scatterpolar(
        r=values_paris_closed,
        theta=categories_closed,
        fill="toself",
        name="Paris",
        opacity=0.45
    )
)

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
    margin=dict(l=30, r=30, t=30, b=30),
    showlegend=True
)

st.plotly_chart(fig_radar, use_container_width=True)

# =====================
# TABLEAU
# =====================
st.subheader("📋 Détail des équipements")

df_table = df[[
    "ville",
    "code_commune",
    "categorie",
    "nb"
]].sort_values(["ville", "categorie"])

st.dataframe(df_table, use_container_width=True)