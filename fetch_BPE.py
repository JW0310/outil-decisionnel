# === IMPORT DES LIBRAIRIES ===
# pandas est utilisé pour manipuler les données tabulaires
import pandas as pd


# =====================
# CHARGEMENT DES DONNÉES BPE
# =====================
# On ne charge que les colonnes utiles pour optimiser la mémoire :
# - DEPCOM : code commune
# - TYPEQU : type d’équipement
cols = ["DEPCOM", "TYPEQU"]

df = pd.read_csv(
    "data/raw/BPE24.csv",
    sep=";",          # séparateur spécifique au fichier INSEE
    usecols=cols,     # sélection des colonnes utiles uniquement
    dtype=str         # lecture en string pour éviter les erreurs de type
)


# =====================
# CHARGEMENT DES COMMUNES ÉLIGIBLES
# =====================
# Ce fichier contient :
# - code_commune
# - nom_commune
# - population (> 20k)
df_pop = pd.read_csv(
    "data/processed/population_communes.csv",
    dtype=str
)


# =====================
# PRÉPARATION DES CODES COMMUNES
# =====================
# On harmonise les formats (important pour le merge)
df["code_commune"] = df["DEPCOM"].str.zfill(5)
df_pop["code_commune"] = df_pop["code_commune"].str.zfill(5)


# =====================
# FILTRAGE DES COMMUNES
# =====================
# On garde uniquement les communes présentes dans le fichier population
df = df[df["code_commune"].isin(df_pop["code_commune"])].copy()


# =====================
# CRÉATION DES CATÉGORIES D'ÉQUIPEMENTS
# =====================
# Le champ TYPEQU contient un code dont la première lettre correspond à une catégorie
mapping = {
    "A": "sport",
    "B": "culture_loisirs",
    "C": "sante_social",
    "D": "education",
    "E": "services",
    "F": "transport"
}

# Extraction de la première lettre puis mapping
df["categorie"] = df["TYPEQU"].str[0].map(mapping)


# =====================
# AJOUT DES INFORMATIONS COMMUNES
# =====================
# On ajoute :
# - nom_commune
# - population
df = df.merge(
    df_pop,
    on="code_commune",
    how="left"
)


# =====================
# NETTOYAGE DES DONNÉES
# =====================
# Suppression des lignes inutilisables
df = df.dropna(subset=["categorie", "nom_commune"])


# =====================
# AGRÉGATION DES DONNÉES
# =====================
# Objectif : obtenir le nombre d’équipements par :
# - commune
# - catégorie
df_agg = (
    df.groupby(["code_commune", "nom_commune", "categorie"], as_index=False)
    .size()
    .rename(columns={"size": "nb"})
)


# =====================
# SAUVEGARDE DES DONNÉES TRAITÉES
# =====================
df_agg.to_parquet(
    "data/processed/fact_equipements.parquet",
    index=False
)


# =====================
# AFFICHAGE DE CONTRÔLE
# =====================
print(df_agg.head())
print("Nombre de communes :", df_agg["code_commune"].nunique())