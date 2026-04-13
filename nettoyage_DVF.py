import pandas as pd

# 📁 Chemin du fichier DVF
file_path = "data/raw/dvf.txt"

# 📥 Lecture du fichier
df = pd.read_csv(
    file_path,
    sep="|",
    dtype=str,
    low_memory=False
)

print("Fichier chargé")

# 🔍 Vérification colonnes
print("Colonnes originales :", df.columns.tolist())

# 🧼 Nettoyage des noms de colonnes
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

print("Colonnes nettoyées :", df.columns.tolist())

# 🔎 Colonnes utiles
cols = [
    "code_departement",
    "code_commune",
    "valeur_fonciere",
    "surface_reelle_bati",
    "date_mutation",
    "type_local"
]

df = df[cols]

# 🧼 Nettoyer code_departement
df["code_departement"] = df["code_departement"].str.strip().str.zfill(2)

print(df["code_departement"].unique()[:20])

# 🎯 Filtrage robuste
df_paris = df[df["code_departement"] == "75"].copy()
df_lyon = df[df["code_departement"] == "69"].copy()

print("Paris lignes :", df_paris.shape)
print("Lyon lignes :", df_lyon.shape)

# 🔑 Recréation clé commune
df_paris["code_insee_commune"] = "75056"
df_lyon["code_insee_commune"] = "69123"

# Fusion
df = pd.concat([df_paris, df_lyon], ignore_index=True)

print("Filtrage effectué")

# 🏠 Filtrer uniquement logements pertinents
df = df[df["type_local"].isin(["Appartement", "Maison"])]

# 🧼 Nettoyage valeurs numériques (IMPORTANT)

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

# Conversion
df["valeur_fonciere"] = pd.to_numeric(df["valeur_fonciere"], errors="coerce")
df["surface_reelle_bati"] = pd.to_numeric(df["surface_reelle_bati"], errors="coerce")

print("Après conversion :", df.shape)
print("Valeur fonciere null :", df["valeur_fonciere"].isna().sum())
print("Surface null :", df["surface_reelle_bati"].isna().sum())

# Suppression valeurs aberrantes
df = df[df["surface_reelle_bati"] > 0]
df = df[df["valeur_fonciere"] > 0]

# 💰 Calcul prix m²
df["prix_m2"] = df["valeur_fonciere"] / df["surface_reelle_bati"]

# 📅 Conversion date
df["date_mutation"] = pd.to_datetime(df["date_mutation"], errors="coerce")

# Supprimer lignes invalides
df = df.dropna(subset=["date_mutation", "prix_m2"])

print("Nettoyage terminé")

# 📊 Agrégation mensuelle
df["annee_mois"] = df["date_mutation"].dt.to_period("M")

df_agg = df.groupby(
    ["code_insee_commune", "annee_mois"]
)["prix_m2"].median().reset_index()

# Conversion en string (important pour Streamlit)
df_agg["annee_mois"] = df_agg["annee_mois"].astype(str)

print("Agrégation terminée")
print(df_agg.head())
print("Nombre de lignes :", df_agg.shape)

# 💾 Sauvegarde
output_path = "data/processed/fact_logement.parquet"
df_agg.to_parquet(output_path, index=False)

print("Fichier sauvegardé :", output_path)