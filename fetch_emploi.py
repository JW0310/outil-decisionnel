# === IMPORT DES LIBRAIRIES ===
# pandas pour la manipulation de données
import pandas as pd


# =====================
# LOAD DATA
# =====================
df = pd.read_csv(
    "data/raw/DS_FLORES_A88_2024_data.csv",
    sep=";",
    dtype=str,
    low_memory=False
)

meta = pd.read_csv(
    "data/raw/DS_FLORES_A88_2024_metadata.csv",
    sep=";",
    dtype=str,
    low_memory=False
)


# =====================
# CLEAN COLUMN NAMES
# =====================
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
)

meta.columns = (
    meta.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
)


# =====================
# CLEAN TYPES
# =====================
df["obs_value"] = (
    df["obs_value"]
    .str.replace(" ", "", regex=False)
    .str.replace(",", ".", regex=False)
)

df["obs_value"] = pd.to_numeric(df["obs_value"], errors="coerce")


# =====================
# NORMALISATION
# =====================
df["geo"] = df["geo"].astype(str).str.strip()
df["geo_object"] = df["geo_object"].astype(str).str.strip()
df["activity"] = df["activity"].astype(str).str.strip()
df["flores_measure"] = df["flores_measure"].astype(str).str.strip()
df["time_period"] = df["time_period"].astype(str).str.strip()

df["code_commune"] = df["geo"].str.extract(r"(\d{5})$")


# =====================
# CHARGEMENT COMMUNES ÉLIGIBLES
# =====================
df_pop = pd.read_csv(
    "data/processed/population_communes.csv",
    dtype=str
)

df_pop["code_commune"] = df_pop["code_commune"].str.zfill(5)


# =====================
# FILTRES
# =====================
# niveau commune
df = df[df["geo_object"] == "COM"].copy()

# filtrage villes >20k habitants
df = df[df["code_commune"].isin(df_pop["code_commune"])].copy()
print("Après filtre communes :", df.shape)

# mesure emploi
df = df[df["flores_measure"] == "EMPL3112"].copy()

# année
df = df[df["time_period"] == "2024"].copy()


# =====================
# AJOUT INFOS COMMUNES
# =====================
df = df.merge(
    df_pop,
    on="code_commune",
    how="left"
)


# =====================
# PREPARATION METADATA
# =====================
meta_activity = meta[meta["cod_var"] == "ACTIVITY"].copy()

meta_activity = meta_activity[["cod_mod", "lib_mod"]].drop_duplicates()
meta_activity.columns = ["activity", "secteur"]


# =====================
# MERGE METADATA
# =====================
df = df.merge(meta_activity, on="activity", how="left")
df["secteur"] = df["secteur"].fillna("Secteur " + df["activity"])


# =====================
# SUPPRESSION TOTAL
# =====================
df = df[df["secteur"] != "Total"].copy()


# =====================
# SIMPLIFICATION SECTEURS
# =====================
def simplifier_secteur(s):
    s = str(s).lower()

    if "agric" in s or "sylviculture" in s or "pêche" in s:
        return "Agriculture"
    elif "industrie" in s or "fabrication" in s:
        return "Industrie"
    elif "construction" in s:
        return "Construction"
    elif "commerce" in s:
        return "Commerce"
    elif "transport" in s:
        return "Transport"
    elif "hébergement" in s or "restauration" in s:
        return "Tourisme"
    elif "informat" in s or "programmation" in s:
        return "Numérique"
    elif "finance" in s:
        return "Finance"
    elif "immobilier" in s:
        return "Immobilier"
    elif "administration" in s:
        return "Public"
    elif "enseignement" in s:
        return "Éducation"
    elif "santé" in s:
        return "Santé"
    else:
        return "Autres"

df["secteur"] = df["secteur"].apply(simplifier_secteur)


# =====================
# CLEAN FINAL
# =====================
df = df.dropna(subset=["code_commune", "nom_commune", "secteur", "obs_value"])


# =====================
# AGRÉGATION
# =====================
df_agg = (
    df.groupby(["code_commune", "nom_commune", "secteur"], as_index=False)["obs_value"]
    .sum()
)

df_agg = df_agg.rename(columns={"obs_value": "nb"})


# =====================
# TRI
# =====================
df_agg = df_agg.sort_values(
    ["code_commune", "nb"],
    ascending=[True, False]
).reset_index(drop=True)


# =====================
# SAVE
# =====================
df_agg.to_parquet(
    "data/processed/fact_emploi.parquet",
    index=False
)


# =====================
# DEBUG
# =====================
print(df_agg.head())
print("Nombre de communes :", df_agg["code_commune"].nunique())