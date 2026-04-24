# === IMPORT DES LIBRAIRIES ===
import pandas as pd


# === FONCTION D’HARMONISATION DES COMMUNES ===
def harmoniser_commune(code):
    code = str(code).zfill(5)

    if code.startswith("751"):
        return "75056"  # Paris
    elif code.startswith("132"):
        return "13055"  # Marseille
    elif code.startswith("6938"):
        return "69123"  # Lyon
    else:
        return code


# === CHARGEMENT DES DONNÉES BPE ===
cols = ["DEPCOM", "TYPEQU"]

df = pd.read_csv(
    "data/raw/BPE24.csv",
    sep=";",
    usecols=cols,
    dtype=str
)


# === CHARGEMENT DES COMMUNES ÉLIGIBLES ===
df_pop = pd.read_csv(
    "data/processed/population_communes.csv",
    dtype=str
)

df_pop["code_commune"] = df_pop["code_commune"].str.zfill(5)


# === PRÉPARATION DES CODES COMMUNES ===
df["code_commune"] = df["DEPCOM"].str.zfill(5)
df["code_commune"] = df["code_commune"].apply(harmoniser_commune)


# === FILTRAGE DES COMMUNES DE PLUS DE 20 000 HABITANTS ===
df = df[df["code_commune"].isin(df_pop["code_commune"])].copy()


# === CRÉATION DES CATÉGORIES D'ÉQUIPEMENTS ===
mapping = {
    "A": "sport",
    "B": "culture_loisirs",
    "C": "sante_social",
    "D": "education",
    "E": "services",
    "F": "transport"
}

df["categorie"] = df["TYPEQU"].str[0].map(mapping)


# === AJOUT DES INFORMATIONS COMMUNES ===
df = df.merge(
    df_pop,
    on="code_commune",
    how="left"
)


# === NETTOYAGE DES DONNÉES ===
df = df.dropna(subset=["categorie", "nom_commune"])


# === AGRÉGATION DES DONNÉES ===
df_agg = (
    df.groupby(["code_commune", "nom_commune", "categorie"], as_index=False)
    .size()
    .rename(columns={"size": "nb"})
)


# === SAUVEGARDE ===
df_agg.to_parquet(
    "data/processed/fact_equipements.parquet",
    index=False
)


# === DEBUG ===
print(df_agg.head())
print("Nombre de communes :", df_agg["code_commune"].nunique())
print("Paris présent :", "Paris" in df_agg["nom_commune"].unique())
print("Marseille présent :", "Marseille" in df_agg["nom_commune"].unique())
print("Lyon présent :", "Lyon" in df_agg["nom_commune"].unique())