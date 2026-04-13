import pandas as pd

cols = ["DEPCOM", "TYPEQU"]

df = pd.read_csv(
    "data/raw/BPE24.csv",
    sep=";",
    usecols=cols,
    dtype=str
)

# filtrer Paris + Lyon
df = df[
    df["DEPCOM"].str.startswith("75") |
    df["DEPCOM"].str.startswith("69")
]

# mapping catégories
mapping = {
    "A": "sport",
    "B": "culture_loisirs",
    "C": "sante_social",
    "D": "education",
    "E": "services",
    "F": "transport"
}

df["categorie"] = df["TYPEQU"].str[0].map(mapping)

# ajouter ville
df["ville"] = df["DEPCOM"].str[:2].map({
    "75": "Paris",
    "69": "Lyon"
})

# ajouter code commune officiel
df["code_commune"] = df["DEPCOM"].str[:2].map({
    "75": "75056",
    "69": "69123"
})

# clean
df = df.dropna(subset=["categorie", "ville"])

# agrégation finale
df_agg = (
    df.groupby(["ville", "code_commune", "categorie"])
    .size()
    .reset_index(name="nb")
)

# save
df_agg.to_parquet("data/processed/fact_equipements.parquet", index=False)

print(df_agg)