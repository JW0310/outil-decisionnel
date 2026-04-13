import streamlit as st

st.set_page_config(page_title="Outil décisionnel", layout="wide")

# =====================
# HEADER
# =====================
st.title("🏙️ Outil de comparaison de villes")

st.markdown(
"""
Bienvenue sur cet **outil décisionnel interactif** permettant de comparer **Paris et Lyon**
à partir de plusieurs dimensions clés.

L’objectif est de proposer une lecture :
- 📊 **comparative**
- 📈 **visuelle**
- 🧠 **interprétable**

afin d’aider à la prise de décision territoriale.
"""
)

# =====================
# PÉRIMÈTRE
# =====================
st.header("🎯 Périmètre de l’analyse")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🏙️ Villes étudiées")
    st.write("- Paris")
    st.write("- Lyon")

with col2:
    st.markdown("### 📅 Période")
    st.write("Année 2024")
    st.write("Données agrégées mensuellement")

with col3:
    st.markdown("### 📊 Dimensions analysées")
    st.write("- Équipements")
    st.write("- Météo")
    st.write("- Logement")
    st.write("- Emploi")

# =====================
# CONTENU
# =====================
st.header("🧭 Contenu de l’application")

st.markdown(
"""
### 📊 Comparaison
Vue d’ensemble des écarts entre Paris et Lyon selon les équipements,
avec indicateurs clés et visualisations comparatives.

### 🌤️ Météo
Analyse des températures, des précipitations et de l’amplitude thermique
sur l’année 2024.

### 🏠 Logement
Analyse du marché immobilier à travers :
- le prix moyen au m²
- l’évolution mensuelle
- les écarts entre les villes

### 💼 Emploi
Analyse de la structure économique :
- volume d’emplois
- secteurs dominants
- répartition sectorielle
"""
)

# =====================
# SOURCES
# =====================
st.header("📚 Sources de données")

st.markdown(
"""
### 🏢 Équipements
- **Base Permanente des Équipements (BPE 2024 – INSEE)**

### 🌦️ Météo
- **Open-Meteo API**

### 🏠 Logement
- **Demandes de Valeurs Foncières (DVF)**

### 💼 Emploi
- **FLORES (INSEE) – Emploi au lieu de travail**
"""
)

st.info("Les données ont été nettoyées, agrégées et harmonisées à l’échelle communale.")

# =====================
# MÉTHODOLOGIE
# =====================
st.header("⚙️ Méthodologie")

st.markdown(
"""
- Sélection des villes de plus de 20 000 habitants
- Collecte via fichiers open data et API
- Nettoyage et normalisation des données
- Agrégation par commune (Paris 75056, Lyon 69123)
- Création de tables analytiques (parquet)
- Visualisation avec Streamlit et Plotly
"""
)

# =====================
# PERSPECTIVES
# =====================
st.header("🚀 Perspectives d’évolution")

st.markdown(
"""
- Ajouter d’autres villes françaises
- Construire un score synthétique global
- Intégrer des données socio-économiques supplémentaires
- Ajouter des filtres utilisateurs (ville, période…)
- Déployer l’application en ligne (Streamlit Cloud)
"""
)

# =====================
# FOOTER
# =====================
st.markdown("---")
st.caption("Projet réalisé dans le cadre de la SAÉ - Outil décisionnel")