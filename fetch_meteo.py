# === IMPORT DES LIBRAIRIES ===
import pandas as pd
import requests


# =====================
# LISTE DE VILLES (EXTENSIBLE)
# =====================
# On définit plusieurs grandes villes françaises
# compatibles avec le projet (toutes > 20k habitants)

villes = {
    "75056": {"nom": "Paris", "lat": 48.8566, "lon": 2.3522},
    "69123": {"nom": "Lyon", "lat": 45.7640, "lon": 4.8357},
    "13055": {"nom": "Marseille", "lat": 43.2965, "lon": 5.3698},
    "31555": {"nom": "Toulouse", "lat": 43.6047, "lon": 1.4442},
    "06088": {"nom": "Nice", "lat": 43.7102, "lon": 7.2620},
    "44109": {"nom": "Nantes", "lat": 47.2184, "lon": -1.5536},
    "67482": {"nom": "Strasbourg", "lat": 48.5734, "lon": 7.7521},
    "33063": {"nom": "Bordeaux", "lat": 44.8378, "lon": -0.5792}
}


# =====================
# APPEL API METEO
# =====================
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

    df["code_commune"] = code
    df["nom_commune"] = info["nom"]

    results.append(df)


# =====================
# CONCATENATION
# =====================
df_final = pd.concat(results)


# =====================
# TRANSFORMATION DES DATES
# =====================
df_final["date"] = pd.to_datetime(df_final["date"])


# =====================
# AGREGATION MENSUELLE
# =====================
df_final["annee_mois"] = df_final["date"].dt.to_period("M")

df_agg = df_final.groupby(
    ["code_commune", "nom_commune", "annee_mois"]
).agg({
    "temperature_moyenne": "mean",
    "precipitations": "sum"
}).reset_index()

df_agg["annee_mois"] = df_agg["annee_mois"].astype(str)


# =====================
# SAUVEGARDE
# =====================
df_agg.to_parquet(
    "data/processed/fact_meteo.parquet",
    index=False
)


# =====================
# DEBUG
# =====================
print(df_agg.head())
print("Nombre de villes météo :", df_agg["code_commune"].nunique())