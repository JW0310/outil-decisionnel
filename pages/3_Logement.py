import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Logement", layout="wide")

st.title("🏠 Analyse logement")

# =====================
# DATA
# =====================
df = pd.read_parquet("data/processed/fact_logement.parquet")

mapping = {
    "75056": "Paris",
    "69123": "Lyon"
}

df["ville"] = df["code_insee_commune"].astype(str).map(mapping)
df = df.dropna(subset=["ville"]).copy()

ordre_mois = [
    "2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06",
    "2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"
]
df["annee_mois"] = pd.Categorical(df["annee_mois"], categories=ordre_mois, ordered=True)
df = df.sort_values("annee_mois")

df_lyon = df[df["ville"] == "Lyon"].copy()
df_paris = df[df["ville"] == "Paris"].copy()

mois_labels = {
    "01": "Janvier",
    "02": "Février",
    "03": "Mars",
    "04": "Avril",
    "05": "Mai",
    "06": "Juin",
    "07": "Juillet",
    "08": "Août",
    "09": "Septembre",
    "10": "Octobre",
    "11": "Novembre",
    "12": "Décembre"
}

def format_mois_annee(valeur):
    annee, mois = str(valeur).split("-")
    return f"{mois_labels[mois]} {annee}"

# =====================
# KPI
# =====================
st.subheader("📌 Indicateurs logement clés")

prix_moy_lyon = int(round(df_lyon["prix_m2"].mean(), 0))
prix_moy_paris = int(round(df_paris["prix_m2"].mean(), 0))

row_cher_lyon = df_lyon.loc[df_lyon["prix_m2"].idxmax()]
row_cher_paris = df_paris.loc[df_paris["prix_m2"].idxmax()]

mois_cher_lyon = format_mois_annee(row_cher_lyon["annee_mois"])
mois_cher_paris = format_mois_annee(row_cher_paris["annee_mois"])

prix_mois_cher_lyon = int(round(row_cher_lyon["prix_m2"], 0))
prix_mois_cher_paris = int(round(row_cher_paris["prix_m2"], 0))

evol_lyon = round(
    ((df_lyon["prix_m2"].iloc[-1] - df_lyon["prix_m2"].iloc[0]) / df_lyon["prix_m2"].iloc[0]) * 100,
    1
)
evol_paris = round(
    ((df_paris["prix_m2"].iloc[-1] - df_paris["prix_m2"].iloc[0]) / df_paris["prix_m2"].iloc[0]) * 100,
    1
)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏙️ Lyon")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(
        "Prix moyen annuel",
        f"{prix_moy_lyon:,} €/m²",
        help="Moyenne des prix mensuels au m² observés sur l'année 2024."
    )
    kpi2.metric(
        "Mois le plus cher",
        mois_cher_lyon,
        delta=f"{prix_mois_cher_lyon:,} €/m²",
        help="Mois présentant le prix moyen au m² le plus élevé."
    )
    kpi3.metric(
        "Évolution annuelle",
        f"{evol_lyon} %",
        help="Évolution entre le premier et le dernier mois de l'année."
    )

with col2:
    st.markdown("### 🏙️ Paris")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(
        "Prix moyen annuel",
        f"{prix_moy_paris:,} €/m²",
        help="Moyenne des prix mensuels au m² observés sur l'année 2024."
    )
    kpi2.metric(
        "Mois le plus cher",
        mois_cher_paris,
        delta=f"{prix_mois_cher_paris:,} €/m²",
        help="Mois présentant le prix moyen au m² le plus élevé."
    )
    kpi3.metric(
        "Évolution annuelle",
        f"{evol_paris} %",
        help="Évolution entre le premier et le dernier mois de l'année."
    )

# =====================
# BLOC 2 — EVOLUTION COMPAREE
# =====================
st.subheader("📈 Évolution mensuelle du prix moyen au m²")

fig_prix = px.line(
    df,
    x="annee_mois",
    y="prix_m2",
    color="ville",
    markers=True,
    labels={
        "annee_mois": "Mois",
        "prix_m2": "Prix moyen (€/m²)",
        "ville": "Ville"
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
# BLOC 3 — ECART DE PRIX
# =====================
st.subheader("📊 Différence de prix au m² (Paris - Lyon)")

df_ecart = df.pivot_table(
    index="annee_mois",
    columns="ville",
    values="prix_m2",
    aggfunc="mean"
).reset_index()

df_ecart["ecart_paris_lyon"] = (df_ecart["Paris"] - df_ecart["Lyon"]).round(0)

fig_ecart = px.bar(
    df_ecart,
    x="annee_mois",
    y="ecart_paris_lyon",
    labels={
        "annee_mois": "Mois",
        "ecart_paris_lyon": "Écart de prix (€/m²)"
    },
    text_auto=".0f",
    color_discrete_sequence=["#EF553B"]
)

fig_ecart.update_layout(
    xaxis_title="Mois",
    yaxis_title="Écart Paris - Lyon (€/m²)",
    showlegend=False,
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig_ecart, use_container_width=True)

# =====================
# BLOC 4 — LECTURE SYNTHETIQUE
# =====================
st.subheader("📝 Lecture synthétique")

ville_plus_chere = "Lyon" if prix_moy_lyon > prix_moy_paris else "Paris"
ville_plus_hausse = "Lyon" if evol_lyon > evol_paris else "Paris"

ecart_moyen = int(round(df_ecart["ecart_paris_lyon"].mean(), 0))
ecart_max = int(round(df_ecart["ecart_paris_lyon"].max(), 0))
mois_ecart_max = format_mois_annee(
    df_ecart.loc[df_ecart["ecart_paris_lyon"].idxmax(), "annee_mois"]
)

st.markdown(
    f"""
- **{ville_plus_chere}** présente le prix moyen au m² le plus élevé sur l’année.
- L’écart moyen entre les deux villes est d’environ **{ecart_moyen:,} €/m²** en moyenne.
- L’écart maximal est observé en **{mois_ecart_max}**, avec environ **{ecart_max:,} €/m²**.
- **{ville_plus_hausse}** enregistre la plus forte évolution relative sur l’année.
"""
)