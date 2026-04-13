import pandas as pd
import requests

# 📍 Coordonnées villes
villes = {
    "75056": {"nom": "Paris", "lat": 48.8566, "lon": 2.3522},
    "69123": {"nom": "Lyon", "lat": 45.7640, "lon": 4.8357}
}

results = []

for code, info in villes.items():
    print(f"Récupération météo pour {info['nom']}")

    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={info['lat']}&longitude={info['lon']}"
        f"&start_date=2024-01-01&end_date=2024-12-31"
        f"&daily=temperature_2m_mean,precipitation_sum"
        f"&timezone=Europe/Paris"
    )

    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame({
        "date": data["daily"]["time"],
        "temperature_moyenne": data["daily"]["temperature_2m_mean"],
        "precipitations": data["daily"]["precipitation_sum"]
    })

    df["code_insee_commune"] = code

    results.append(df)

# Fusion
df_final = pd.concat(results)

# Conversion date
df_final["date"] = pd.to_datetime(df_final["date"])

# Agrégation mensuelle
df_final["annee_mois"] = df_final["date"].dt.to_period("M")

df_agg = df_final.groupby(
    ["code_insee_commune", "annee_mois"]
).agg({
    "temperature_moyenne": "mean",
    "precipitations": "sum"
}).reset_index()

df_agg["annee_mois"] = df_agg["annee_mois"].astype(str)

# Sauvegarde
df_agg.to_parquet("data/processed/fact_meteo.parquet", index=False)

print("Fichier météo sauvegardé")
print(df_agg.head())