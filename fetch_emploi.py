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

print("Colonnes data :")
print(df.columns.tolist())

print("\nColonnes metadata :")
print(meta.columns.tolist())

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

print("\nColonnes data nettoyées :")
print(df.columns.tolist())

print("\nColonnes metadata nettoyées :")
print(meta.columns.tolist())

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
# NORMALISATION DES CHAMPS
# =====================
df["geo"] = df["geo"].astype(str).str.strip()
df["geo_object"] = df["geo_object"].astype(str).str.strip()
df["activity"] = df["activity"].astype(str).str.strip()
df["flores_measure"] = df["flores_measure"].astype(str).str.strip()
df["time_period"] = df["time_period"].astype(str).str.strip()

# récupération du code commune à partir de geo
df["code_commune"] = df["geo"].str.extract(r"(\d{5})$")

print("\nExemples code_commune extraits :")
print(df["code_commune"].dropna().unique()[:20])

# =====================
# FILTRES
# =====================
# uniquement niveau commune
df = df[df["geo_object"] == "COM"].copy()

# uniquement Paris / Lyon
df = df[df["code_commune"].isin(["75056", "69123"])].copy()
print("\nAprès filtre communes Paris / Lyon :", df.shape)

# uniquement emplois au 31/12
df = df[df["flores_measure"] == "EMPL3112"].copy()
print("Après filtre mesure EMPL3112 :", df.shape)

# uniquement 2024
df = df[df["time_period"] == "2024"].copy()
print("Après filtre période 2024 :", df.shape)

# =====================
# AJOUT VILLE
# =====================
mapping_ville = {
    "75056": "Paris",
    "69123": "Lyon"
}

df["ville"] = df["code_commune"].map(mapping_ville)

# =====================
# PREP METADATA
# =====================
meta_activity = meta[meta["cod_var"] == "ACTIVITY"].copy()
meta_activity = meta_activity[["cod_mod", "lib_mod"]].drop_duplicates()
meta_activity.columns = ["activity", "secteur"]

print("\nMapping secteurs :")
print(meta_activity.head())

# =====================
# MERGE AVEC METADATA
# =====================
df = df.merge(meta_activity, on="activity", how="left")

# fallback si jamais un code n'a pas de libellé
df["secteur"] = df["secteur"].fillna("Secteur " + df["activity"])

# =====================
# SUPPRESSION DU TOTAL
# =====================
df = df[df["secteur"] != "Total"].copy()

# =====================
# SIMPLIFICATION DES SECTEURS
# =====================
def simplifier_secteur(s):
    s = str(s).lower()

    if "agric" in s or "sylviculture" in s or "pêche" in s or "aquaculture" in s:
        return "Agriculture"
    elif "industrie" in s or "fabrication" in s or "extract" in s or "minerai" in s:
        return "Industrie"
    elif "construction" in s:
        return "Construction"
    elif "commerce" in s:
        return "Commerce"
    elif "transport" in s or "entreposage" in s:
        return "Transport"
    elif "hébergement" in s or "restauration" in s:
        return "Tourisme"
    elif "informat" in s or "programmation" in s or "communication" in s:
        return "Numérique"
    elif "finance" in s or "assurance" in s:
        return "Finance"
    elif "immobilier" in s:
        return "Immobilier"
    elif "administration" in s or "défense" in s or "sécurité sociale" in s:
        return "Public"
    elif "enseignement" in s:
        return "Éducation"
    elif "santé" in s or "social" in s:
        return "Santé"
    else:
        return "Autres"

df["secteur_simplifie"] = df["secteur"].apply(simplifier_secteur)

# =====================
# CLEAN FINAL
# =====================
df = df.dropna(subset=["ville", "code_commune", "secteur_simplifie", "obs_value"])

# =====================
# AGRÉGATION
# =====================
df_agg = (
    df.groupby(["ville", "code_commune", "secteur_simplifie"], as_index=False)["obs_value"]
    .sum()
)

df_agg = df_agg.rename(columns={
    "secteur_simplifie": "secteur",
    "obs_value": "nb"
})

# =====================
# TRI
# =====================
df_agg = df_agg.sort_values(["ville", "nb"], ascending=[True, False]).reset_index(drop=True)

# =====================
# SAVE
# =====================
df_agg.to_parquet("data/processed/fact_emploi.parquet", index=False)

# =====================
# DEBUG FINAL
# =====================
print("\nAperçu final :")
print(df_agg.head())

print("\nShape finale :", df_agg.shape)

print("\nTotaux par ville :")
print(df_agg.groupby("ville")["nb"].sum())