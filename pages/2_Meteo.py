import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Météo", layout="wide")

st.title("🌤️ Analyse météo")

# =====================
# DATA
# =====================
df = pd.read_parquet("data/processed/fact_meteo.parquet")

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

# =====================
# KPI
# =====================
st.subheader("📌 Indicateurs météo clés")

temp_moy_lyon = round(df_lyon["temperature_moyenne"].mean(), 1)
temp_moy_paris = round(df_paris["temperature_moyenne"].mean(), 1)

precip_total_lyon = int(round(df_lyon["precipitations"].sum(), 0))
precip_total_paris = int(round(df_paris["precipitations"].sum(), 0))

row_chaud_lyon = df_lyon.loc[df_lyon["temperature_moyenne"].idxmax()]
row_chaud_paris = df_paris.loc[df_paris["temperature_moyenne"].idxmax()]

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

mois_chaud_lyon = format_mois_annee(row_chaud_lyon["annee_mois"])
mois_chaud_paris = format_mois_annee(row_chaud_paris["annee_mois"])

temp_mois_chaud_lyon = round(row_chaud_lyon["temperature_moyenne"], 1)
temp_mois_chaud_paris = round(row_chaud_paris["temperature_moyenne"], 1)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏙️ Lyon")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(
        "Température annuelle",
        f"{temp_moy_lyon} °C",
        help="Moyenne des températures mensuelles sur l'année 2024."
    )
    kpi2.metric(
        "Mois le plus chaud",
        mois_chaud_lyon,
        delta=f"{temp_mois_chaud_lyon} °C",
        help="Mois présentant la température moyenne mensuelle la plus élevée."
    )
    kpi3.metric(
        "Précipitations annuelles",
        f"{precip_total_lyon} mm",
        help="Somme des précipitations mensuelles sur l'année 2024."
    )

with col2:
    st.markdown("### 🏙️ Paris")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric(
        "Température annuelle",
        f"{temp_moy_paris} °C",
        help="Moyenne des températures mensuelles sur l'année 2024."
    )
    kpi2.metric(
        "Mois le plus chaud",
        mois_chaud_paris,
        delta=f"{temp_mois_chaud_paris} °C",
        help="Mois présentant la température moyenne mensuelle la plus élevée."
    )
    kpi3.metric(
        "Précipitations annuelles",
        f"{precip_total_paris} mm",
        help="Somme des précipitations mensuelles sur l'année 2024."
    )

# =====================
# BLOC 2 — TEMPERATURES
# =====================
st.subheader("🌡️ Évolution des températures moyennes mensuelles")

fig_temp = px.line(
    df,
    x="annee_mois",
    y="temperature_moyenne",
    color="ville",
    markers=True,
    labels={
        "annee_mois": "Mois",
        "temperature_moyenne": "Température moyenne (°C)",
        "ville": "Ville"
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
# BLOC 3 — PRECIPITATIONS
# =====================
st.subheader("🌧️ Comparaison des précipitations mensuelles")

fig_precip = px.bar(
    df,
    x="annee_mois",
    y="precipitations",
    color="ville",
    text_auto=True,
    barmode="group",
    labels={
        "annee_mois": "Mois",
        "precipitations": "Précipitations (mm)",
        "ville": "Ville"
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
# BLOC 3 BIS — AMPLITUDE
# =====================
st.subheader("🌡️ Amplitude thermique annuelle")

amp_lyon = round(
    df_lyon["temperature_moyenne"].max() - df_lyon["temperature_moyenne"].min(), 1
)
amp_paris = round(
    df_paris["temperature_moyenne"].max() - df_paris["temperature_moyenne"].min(), 1
)

df_amplitude = pd.DataFrame({
    "ville": ["Lyon", "Paris"],
    "amplitude_thermique": [amp_lyon, amp_paris]
})

fig_amp = px.bar(
    df_amplitude,
    x="ville",
    y="amplitude_thermique",
    color="ville",
    text_auto=True,
    labels={
        "ville": "Ville",
        "amplitude_thermique": "Amplitude thermique (°C)"
    }
)

fig_amp.update_layout(
    xaxis_title="Ville",
    yaxis_title="Amplitude thermique (°C)",
    showlegend=False,
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig_amp, use_container_width=True)

st.info(
    "L’amplitude thermique annuelle correspond ici à l’écart entre le mois le plus chaud et le mois le plus froid de l’année."
)

# =====================
# BLOC 4 — LECTURE SYNTHETIQUE
# =====================
st.subheader("📝 Lecture synthétique")

ville_plus_chaude = "Lyon" if temp_moy_lyon > temp_moy_paris else "Paris"
ville_plus_pluvieuse = "Lyon" if precip_total_lyon > precip_total_paris else "Paris"
ville_plus_contrastée = "Lyon" if amp_lyon > amp_paris else "Paris"

st.markdown(
    f"""
- **{ville_plus_chaude}** est légèrement plus chaude en moyenne sur l’année.
- **{ville_plus_pluvieuse}** enregistre un cumul annuel de précipitations plus élevé.
- **{ville_plus_contrastée}** présente l’amplitude thermique annuelle la plus marquée.
- Les deux villes gardent toutefois une saisonnalité proche, avec des températures basses en hiver et un pic en été.
"""
)