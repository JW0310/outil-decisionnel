# === IMPORT DES LIBRAIRIES ===
import pandas as pd


# =====================
# CHARGEMENT DES DONNÉES POPULATION
# =====================
df = pd.read_csv(
    "data/raw/DS_RP_POPULATION_COMP_2022_data.csv",
    sep=";",
    dtype=str,
    low_memory=False
)


# =====================
# CHARGEMENT RÉFÉRENTIEL COMMUNES
# =====================
df_communes = pd.read_csv(
    "data/raw/v_commune_2026.csv",
    sep=",",
    dtype=str
)


# =====================
# NETTOYAGE COLONNES
# =====================
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
)

df_communes.columns = (
    df_communes.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
)


# =====================
# IDENTIFICATION DES COLONNES
# =====================
print("Colonnes communes :", df_communes.columns.tolist())

# 👉 adapte si besoin après print
# (les noms peuvent varier selon le fichier)
df_communes = df_communes.rename(columns={
    "code_commune": "code_commune",
    "nom_commune": "nom_commune",
    "libelle": "nom_commune",   # fallback fréquent
    "nom": "nom_commune",       # fallback fréquent
    "com": "code_commune"       # fallback fréquent
})


# =====================
# FILTRAGE POPULATION
# =====================
df = df[
    (df["geo_object"] == "COM") &
    (df["sex"] == "_T") &
    (df["rp_measure"] == "POP")
].copy()


# =====================
# CODE COMMUNE
# =====================
df["code_commune"] = df["geo"].str.zfill(5)


# =====================
# POPULATION
# =====================
df["population"] = pd.to_numeric(df["obs_value"], errors="coerce")


# =====================
# FILTRE > 20K
# =====================
df = df[df["population"] > 20000]


# =====================
# AGRÉGATION
# =====================
df = (
    df.groupby("code_commune", as_index=False)["population"]
    .max()
)


# =====================
# FORMAT COMMUNES
# =====================
df_communes["code_commune"] = df_communes["code_commune"].str.zfill(5)


# =====================
# MERGE FINAL
# =====================
df_final = df.merge(
    df_communes[["code_commune", "nom_commune"]],
    on="code_commune",
    how="left"
)


# =====================
# NETTOYAGE FINAL
# =====================
df_final = df_final.dropna(subset=["nom_commune"])


# =====================
# SAVE
# =====================
df_final.to_csv(
    "data/processed/population_communes.csv",
    index=False
)


# =====================
# DEBUG
# =====================
print("\nAperçu final :")
print(df_final.head())

print("\nNombre de communes :", df_final.shape[0])