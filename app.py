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
selon plusieurs dimensions : équipements, logement et emploi.

L’utilisateur peut sélectionner deux villes parmi les communes disponibles de plus de **20 000 habitants**.
Cette sélection est ensuite conservée sur les pages **Comparaison**, **Logement** et **Emploi**.

La page **Météo** dispose d’une sélection indépendante, car les données météorologiques sont disponibles
sur un périmètre plus restreint.
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
Utilisez le menu latéral pour accéder aux différentes pages d’analyse.

### 📊 Comparaison
Vue d’ensemble des équipements disponibles dans les deux villes sélectionnées.

### 🌤️ Météo
Analyse des températures, des précipitations et de l’amplitude thermique.  
Cette page possède sa propre sélection de villes.

### 🏠 Logement
Analyse du marché immobilier : prix au m², évolution mensuelle et écarts entre les villes.

### 💼 Emploi
Analyse de la structure économique : emplois, secteurs dominants et spécialisations.
"""
)


# =====================
# UTILISATION DES FILTRES
# =====================
st.header("🔎 Utilisation des filtres")

st.markdown(
"""
Sur les pages **Comparaison**, **Logement** et **Emploi**, les villes sont sélectionnées depuis le menu latéral.
Une fois choisies, elles restent mémorisées lors du passage d’une page à l’autre.

La page **Météo** fonctionne séparément, car elle repose sur une source API et un ensemble de villes disponible plus limité.
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
- collecte via fichiers open data et API  
- nettoyage et normalisation des données  
- harmonisation par code commune INSEE  
- agrégation par commune, mois ou catégorie  
- export des tables finales au format parquet  
- visualisation avec Streamlit et Plotly  
"""
)


# =====================
# LIMITES
# =====================
st.header("⚠️ Limites")

st.markdown(
"""
- les données sont centrées sur l’année 2024  
- la couverture météo est limitée à un panel de villes  
- certaines communes peuvent avoir moins de données selon les sources  
- les indicateurs sont agrégés et doivent être interprétés comme des tendances
"""
)


# =====================
# PERSPECTIVES
# =====================
st.header("🚀 Perspectives")

st.markdown(
"""
- élargir la couverture météo  
- créer un score global de comparaison  
- ajouter de nouvelles dimensions d’analyse  
- enrichir les filtres utilisateurs  
- améliorer l’expérience utilisateur
"""
)


# =====================
# FOOTER
# =====================
st.markdown("---")
st.caption("Projet réalisé dans le cadre de la SAÉ - Outil décisionnel")