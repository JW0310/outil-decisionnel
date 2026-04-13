import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Emploi", layout="wide")

st.title("💼 Analyse de l'emploi")

# =====================
# DATA
# =====================
df = pd.read_parquet("data/processed/fact_emploi.parquet")

df_lyon = df[df["ville"] == "Lyon"].copy()
df_paris = df[df["ville"] == "Paris"].copy()

# version sans "Autres" pour l'interprétation
df_lyon_sans_autres = df_lyon[df_lyon["secteur"] != "Autres"].copy()
df_paris_sans_autres = df_paris[df_paris["secteur"] != "Autres"].copy()

# =====================
# KPI
# =====================
st.subheader("📌 Indicateurs emploi clés")

total_lyon = int(round(df_lyon["nb"].sum(), 0))
total_paris = int(round(df_paris["nb"].sum(), 0))

top_lyon_row = df_lyon_sans_autres.loc[df_lyon_sans_autres["nb"].idxmax()]
top_paris_row = df_paris_sans_autres.loc[df_paris_sans_autres["nb"].idxmax()]

top_lyon = top_lyon_row["secteur"]
top_paris = top_paris_row["secteur"]

top_lyon_nb = int(round(top_lyon_row["nb"], 0))
top_paris_nb = int(round(top_paris_row["nb"], 0))

nb_secteurs_lyon = int(df_lyon["secteur"].nunique())
nb_secteurs_paris = int(df_paris["secteur"].nunique())

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏙️ Lyon")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(
        "Emplois estimés",
        f"{total_lyon:,}",
        help="Volume d’emplois estimés à partir de la base FLORES 2024."
    )
    kpi2.metric(
        "Secteur dominant",
        top_lyon,
        delta=f"{top_lyon_nb:,} emplois",
        help="Secteur représentant le plus grand volume d’emplois, hors catégorie 'Autres'."
    )
    kpi3.metric(
        "Nombre de secteurs",
        nb_secteurs_lyon,
        help="Nombre de macro-secteurs présents dans la ville."
    )

with col2:
    st.markdown("### 🏙️ Paris")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(
        "Emplois estimés",
        f"{total_paris:,}",
        help="Volume d’emplois estimés à partir de la base FLORES 2024."
    )
    kpi2.metric(
        "Secteur dominant",
        top_paris,
        delta=f"{top_paris_nb:,} emplois",
        help="Secteur représentant le plus grand volume d’emplois, hors catégorie 'Autres'."
    )
    kpi3.metric(
        "Nombre de secteurs",
        nb_secteurs_paris,
        help="Nombre de macro-secteurs présents dans la ville."
    )

# =====================
# BLOC 2 — EMPLOIS PAR SECTEUR
# =====================
st.subheader("📊 Nombre d’emplois par secteur")

pivot = df.pivot_table(
    index="secteur",
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
    text_auto=".0f",
    labels={
        "value": "Nombre d’emplois",
        "secteur": "Secteur"
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
# BLOC 3 — RÉPARTITION SECTORIELLE
# =====================
st.subheader("📈 Répartition sectorielle de l’emploi")

df_percent = df.copy()
df_percent["part"] = df_percent.groupby("ville")["nb"].transform(lambda x: x / x.sum() * 100)

fig_part = px.bar(
    df_percent,
    x="secteur",
    y="part",
    color="ville",
    barmode="group",
    text_auto=".1f",
    labels={
        "secteur": "Secteur",
        "part": "Part de l’emploi (%)",
        "ville": "Ville"
    }
)

fig_part.update_layout(
    xaxis_title="Secteur",
    yaxis_title="Part de l’emploi (%)",
    legend_title="Ville",
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig_part, use_container_width=True)

# =====================
# BLOC 4 — TABLEAU
# =====================
st.subheader("📋 Détail des emplois par secteur")

df_table = df.sort_values(["ville", "nb"], ascending=[True, False]).copy()
df_table["nb"] = df_table["nb"].round(0).astype(int)

st.dataframe(
    df_table[["ville", "code_commune", "secteur", "nb"]],
    use_container_width=True
)

# =====================
# BLOC 5 — LECTURE SYNTHÉTIQUE
# =====================
st.subheader("📝 Lecture synthétique")

ville_plus_emplois = "Lyon" if total_lyon > total_paris else "Paris"

part_top_lyon = round((top_lyon_nb / total_lyon) * 100, 1)
part_top_paris = round((top_paris_nb / total_paris) * 100, 1)

st.markdown(
    f"""
- **{ville_plus_emplois}** concentre le volume d’emplois le plus important parmi les deux villes étudiées.
- À **Lyon**, le secteur dominant hors catégorie résiduelle est **{top_lyon}**, avec environ **{top_lyon_nb:,} emplois**, soit **{part_top_lyon} %** du total estimé.
- À **Paris**, le secteur dominant hors catégorie résiduelle est **{top_paris}**, avec environ **{top_paris_nb:,} emplois**, soit **{part_top_paris} %** du total estimé.
- La structure sectorielle des deux villes montre des spécialisations économiques différentes, ce qui enrichit la comparaison globale.
"""
)