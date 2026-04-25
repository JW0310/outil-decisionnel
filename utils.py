import streamlit as st
import pandas as pd

def get_villes():
    df_pop = pd.read_csv("data/processed/population_communes.csv", dtype=str)
    df_pop["code_commune"] = df_pop["code_commune"].str.zfill(5)
    df_pop = df_pop.sort_values("nom_commune")

    return df_pop


def filtre_villes():
    df_pop = get_villes()

    codes = df_pop["code_commune"].tolist()
    noms = dict(zip(df_pop["code_commune"], df_pop["nom_commune"]))

    # INIT
    if "ville1" not in st.session_state:
        st.session_state["ville1"] = codes[0]

    if "ville2" not in st.session_state:
        st.session_state["ville2"] = codes[1]

    # SIDEBAR
    with st.sidebar:
        st.markdown("### Sélection des villes")

        v1 = st.selectbox(
            "Ville 1",
            codes,
            format_func=lambda x: noms[x],
            index=codes.index(st.session_state["ville1"]),
        )

        v2_choices = [c for c in codes if c != v1]

        v2 = st.selectbox(
            "Ville 2",
            v2_choices,
            format_func=lambda x: noms[x],
            index=v2_choices.index(st.session_state["ville2"]) if st.session_state["ville2"] in v2_choices else 0,
        )

    st.session_state["ville1"] = v1
    st.session_state["ville2"] = v2

    return v1, v2, noms[v1], noms[v2]