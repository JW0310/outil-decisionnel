# === IMPORT DES LIBRAIRIES ===
# pandas est utilisé pour manipuler les données tabulaires
import pandas as pd


# =====================
# CHARGEMENT DES DONNÉES DVF
# =====================
file_path = "data/raw/dvf.txt"

df = pd.read_csv(
    file_path,
    sep="|",
    dtype=str,
    low_memory=False
)

print("Fichier chargé")

# =====================
# NETTOYAGE DES COLONNES
# =====================
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

print("Colonnes nettoyées :", df.columns.tolist())


# =====================
# SÉLECTION DES COLONNES UTILES
# =====================
cols = [
    "code_departement",
    "code_commune",
    "valeur_fonciere",
    "surface_reelle_bati",
    "date_mutation",
    "type_local"
]

df = df[cols]


# =====================
# CHARGEMENT DES COMMUNES ÉLIGIBLES
# =====================
df_pop = pd.read_csv(
    "data/processed/population_communes.csv",
    dtype=str
)

df_pop["code_commune"] = df_pop["code_commune"].str.zfill(5)


# =====================
# PRÉPARATION DES CODES COMMUNES
# =====================
df["code_commune"] = (
    df["code_departement"].str.zfill(2) +
    df["code_commune"].str.zfill(3)
)


# =====================
# FILTRAGE DES COMMUNES (> 20K HABITANTS)
# =====================
df = df[df["code_commune"].isin(df_pop["code_commune"])].copy()

print("Filtrage communes effectué :", df.shape)


# =====================
# AJOUT DES INFOS COMMUNES
# =====================
df = df.merge(
    df_pop,
    on="code_commune",
    how="left"
)


# =====================
# FILTRAGE DES LOGEMENTS
# =====================
df = df[df["type_local"].isin(["Appartement", "Maison"])]


# =====================
# NETTOYAGE DES VARIABLES NUMÉRIQUES
# =====================
df["valeur_fonciere"] = (
    df["valeur_fonciere"]
    .str.replace(" ", "", regex=False)
    .str.replace(",", ".", regex=False)
)

df["surface_reelle_bati"] = (
    df["surface_reelle_bati"]
    .str.replace(" ", "", regex=False)
    .str.replace(",", ".", regex=False)
)

df["valeur_fonciere"] = pd.to_numeric(df["valeur_fonciere"], errors="coerce")
df["surface_reelle_bati"] = pd.to_numeric(df["surface_reelle_bati"], errors="coerce")


# =====================
# SUPPRESSION DES VALEURS ABERRANTES
# =====================
df = df[df["surface_reelle_bati"] > 0]
df = df[df["valeur_fonciere"] > 0]


# =====================
# CALCUL DU PRIX AU M²
# =====================
df["prix_m2"] = df["valeur_fonciere"] / df["surface_reelle_bati"]


# =====================
# NETTOYAGE DES DATES
# =====================
df["date_mutation"] = pd.to_datetime(df["date_mutation"], errors="coerce")
df = df.dropna(subset=["date_mutation", "prix_m2"])


# =====================
# AGRÉGATION MENSUELLE
# =====================
df["annee_mois"] = df["date_mutation"].dt.to_period("M")

df_agg = df.groupby(
    ["code_commune", "nom_commune", "annee_mois"]
)["prix_m2"].median().reset_index()


# =====================
# FORMAT FINAL
# =====================
df_agg["annee_mois"] = df_agg["annee_mois"].astype(str)


# =====================
# SAUVEGARDE
# =====================
df_agg.to_parquet(
    "data/processed/fact_logement.parquet",
    index=False
)


# =====================
# DEBUG
# =====================
print(df_agg.head())
print("Nombre de communes :", df_agg["code_commune"].nunique())