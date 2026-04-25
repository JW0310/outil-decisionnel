# === IMPORT DES LIBRAIRIES ===
import streamlit as st
import pandas as pd
import plotly.express as px


# === CONFIGURATION DE LA PAGE ===
st.set_page_config(page_title="Météo", layout="wide")

st.title("🌤️ Analyse météo")


# === CHARGEMENT DES DONNÉES ===
df = pd.read_parquet("data/processed/fact_meteo.parquet")


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
# SÉLECTION DES VILLES
# =====================
# Page météo indépendante du filtre global
villes = sorted(df["nom_commune"].dropna().unique())

col_select1, col_select2 = st.columns(2)

with col_select1:
    ville1 = st.selectbox("Ville 1", villes, index=0, key="meteo_ville1")

villes_dispo_2 = [v for v in villes if v != ville1]

with col_select2:
    ville2 = st.selectbox("Ville 2", villes_dispo_2, index=0, key="meteo_ville2")

df = df[df["nom_commune"].isin([ville1, ville2])].copy()

df_ville1 = df[df["nom_commune"] == ville1].copy()
df_ville2 = df[df["nom_commune"] == ville2].copy()

couleurs_villes = {
    ville1: "#1f77b4",
    ville2: "#ff7f0e"
}

st.markdown(f"### Analyse comparative : **{ville1}** vs **{ville2}**")


# =====================
# KPI
# =====================
st.subheader("Indicateurs météo clés")

temp_moy_v1 = round(df_ville1["temperature_moyenne"].mean(), 1)
temp_moy_v2 = round(df_ville2["temperature_moyenne"].mean(), 1)

precip_v1 = int(round(df_ville1["precipitations"].sum(), 0))
precip_v2 = int(round(df_ville2["precipitations"].sum(), 0))

row_v1 = df_ville1.loc[df_ville1["temperature_moyenne"].idxmax()]
row_v2 = df_ville2.loc[df_ville2["temperature_moyenne"].idxmax()]


# === FORMATAGE DES MOIS ===
mois_labels = {
    "01": "Janvier", "02": "Février", "03": "Mars",
    "04": "Avril", "05": "Mai", "06": "Juin",
    "07": "Juillet", "08": "Août", "09": "Septembre",
    "10": "Octobre", "11": "Novembre", "12": "Décembre"
}

def format_mois_annee(valeur):
    annee, mois = str(valeur).split("-")
    return f"{mois_labels[mois]} {annee}"

mois_v1 = format_mois_annee(row_v1["annee_mois"])
mois_v2 = format_mois_annee(row_v2["annee_mois"])

temp_v1_max = round(row_v1["temperature_moyenne"], 1)
temp_v2_max = round(row_v2["temperature_moyenne"], 1)


# === AFFICHAGE KPI ===
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"#### {ville1}")
    k1, k2, k3 = st.columns(3)

    k1.metric("Temp. annuelle", f"{temp_moy_v1} °C")
    k2.metric("Mois le + chaud", mois_v1, delta=f"{temp_v1_max} °C")
    k3.metric("Pluie annuelle", f"{precip_v1} mm")

with col2:
    st.markdown(f"#### {ville2}")
    k1, k2, k3 = st.columns(3)

    k1.metric("Temp. annuelle", f"{temp_moy_v2} °C")
    k2.metric("Mois le + chaud", mois_v2, delta=f"{temp_v2_max} °C")
    k3.metric("Pluie annuelle", f"{precip_v2} mm")


# =====================
# GRAPHIQUE TEMPÉRATURES
# =====================
st.subheader("Évolution des températures moyennes mensuelles")

fig_temp = px.line(
    df,
    x="annee_mois",
    y="temperature_moyenne",
    color="nom_commune",
    markers=True,
    color_discrete_map=couleurs_villes,
    labels={
        "annee_mois": "Mois",
        "temperature_moyenne": "Température moyenne (°C)",
        "nom_commune": "Ville"
    }
)

fig_temp.update_layout(
    xaxis_title="Mois",
    yaxis_title="Température moyenne (°C)",
    legend_title="Ville",
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig_temp, use_container_width=True)


# =====================
# GRAPHIQUE PRÉCIPITATIONS
# =====================
st.subheader("Comparaison des précipitations mensuelles")

fig_precip = px.bar(
    df,
    x="annee_mois",
    y="precipitations",
    color="nom_commune",
    text_auto=True,
    barmode="group",
    color_discrete_map=couleurs_villes,
    labels={
        "annee_mois": "Mois",
        "precipitations": "Précipitations (mm)",
        "nom_commune": "Ville"
    }
)

fig_precip.update_layout(
    xaxis_title="Mois",
    yaxis_title="Précipitations (mm)",
    legend_title="Ville",
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig_precip, use_container_width=True)


# =====================
# AMPLITUDE THERMIQUE
# =====================
st.subheader("Amplitude thermique annuelle")

amp_v1 = round(
    df_ville1["temperature_moyenne"].max() - df_ville1["temperature_moyenne"].min(), 1
)
amp_v2 = round(
    df_ville2["temperature_moyenne"].max() - df_ville2["temperature_moyenne"].min(), 1
)

df_amp = pd.DataFrame({
    "Ville": [ville1, ville2],
    "Amplitude thermique (°C)": [amp_v1, amp_v2]
})

fig_amp = px.bar(
    df_amp,
    x="Ville",
    y="Amplitude thermique (°C)",
    color="Ville",
    text_auto=True,
    color_discrete_map=couleurs_villes
)

fig_amp.update_layout(
    xaxis_title="Ville",
    yaxis_title="Amplitude thermique (°C)",
    showlegend=False,
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig_amp, use_container_width=True)

st.info(
    "L’amplitude thermique correspond à l’écart entre le mois le plus chaud et le mois le plus froid de l’année."
)


# =====================
# LECTURE SYNTHÉTIQUE
# =====================
st.subheader("Lecture synthétique")

ville_chaude = ville1 if temp_moy_v1 > temp_moy_v2 else ville2
ville_pluvieuse = ville1 if precip_v1 > precip_v2 else ville2
ville_contrastee = ville1 if amp_v1 > amp_v2 else ville2

ecart_temp = round(abs(temp_moy_v1 - temp_moy_v2), 1)
ecart_pluie = abs(precip_v1 - precip_v2)
ecart_amp = round(abs(amp_v1 - amp_v2), 1)

st.markdown(
    f"""
- **{ville_chaude}** est la ville la plus chaude en moyenne, avec un écart d’environ **{ecart_temp} °C**.
- **{ville_pluvieuse}** présente le cumul annuel de précipitations le plus élevé, avec un écart d’environ **{ecart_pluie} mm**.
- **{ville_contrastee}** possède l’amplitude thermique la plus marquée, avec un écart d’environ **{ecart_amp} °C**.
- Les courbes permettent d’observer la saisonnalité des températures et des précipitations sur l’année 2024.
"""
)