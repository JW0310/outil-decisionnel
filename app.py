# === IMPORT DES LIBRAIRIES ===
import streamlit as st


# =====================
# CONFIGURATION PAGE
# =====================
st.set_page_config(page_title="Outil décisionnel", layout="wide")


# =====================
# HEADER
# =====================
st.title("🏙️ Outil de comparaison de villes")

st.markdown(
"""
Bienvenue sur cet **outil décisionnel interactif** permettant de comparer **deux villes françaises**
selon plusieurs dimensions : équipements, météo, logement et emploi.

L’utilisateur peut sélectionner librement deux villes parmi les communes disponibles de plus de **20 000 habitants**.
L’objectif est de fournir une lecture **comparative, visuelle et interprétable** afin de faciliter l’analyse territoriale.
"""
)


# =====================
# PÉRIMÈTRE
# =====================
st.header("🎯 Périmètre de l’analyse")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🏙️ Villes")
    st.write("Communes françaises de plus de 20 000 habitants")
    st.write("Comparaison de deux villes au choix")

with col2:
    st.markdown("### 📅 Période")
    st.write("Année 2024")
    st.write("Données agrégées mensuellement lorsque disponible")

with col3:
    st.markdown("### 📊 Dimensions")
    st.write("- 📊 Équipements")
    st.write("- 🌤️ Météo")
    st.write("- 🏠 Logement")
    st.write("- 💼 Emploi")


# =====================
# NAVIGATION
# =====================
st.header("🧭 Navigation dans l’application")

st.markdown(
"""
Utilisez le menu latéral pour accéder aux différentes pages d’analyse :

### 📊 Comparaison
Vue d’ensemble des équipements disponibles dans les deux villes sélectionnées.

### 🌤️ Météo
Analyse des températures, des précipitations et de l’amplitude thermique.

### 🏠 Logement
Analyse du marché immobilier (prix au m², évolution, écarts).

### 💼 Emploi
Analyse de la structure économique (emplois, secteurs, répartition).
"""
)


# =====================
# SOURCES
# =====================
st.header("📚 Sources de données")

st.markdown(
"""
- **📊 Base Permanente des Équipements (INSEE)**
- **🌦️ Open-Meteo API**
- **🏠 DVF – Demandes de Valeurs Foncières**
- **💼 FLORES (INSEE)**
- **👥 Population communale (INSEE)**
"""
)

st.info("Les données ont été nettoyées, harmonisées et agrégées à l’échelle communale.")


# =====================
# MÉTHODOLOGIE
# =====================
st.header("⚙️ Méthodologie")

st.markdown(
"""
- sélection des communes de plus de 20 000 habitants  
- collecte via open data et API  
- nettoyage et normalisation  
- agrégation par commune  
- export en parquet  
- visualisation avec Streamlit et Plotly  
"""
)


# =====================
# LIMITES
# =====================
st.header("⚠️ Limites")

st.markdown(
"""
- données centrées sur 2024  
- couverture météo limitée  
- disponibilité variable selon les villes  
- indicateurs agrégés (tendances)
"""
)


# =====================
# PERSPECTIVES
# =====================
st.header("🚀 Perspectives")

st.markdown(
"""
- ajouter d’autres villes  
- créer un score global  
- enrichir les données  
- ajouter des filtres  
- améliorer l’UX
"""
)


# =====================
# FOOTER
# =====================
st.markdown("---")
st.caption("Projet réalisé dans le cadre de la SAÉ - Outil décisionnel")