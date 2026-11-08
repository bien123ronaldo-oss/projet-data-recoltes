from pathlib import Path

import pandas as pd
import streamlit as st

# Partie tableau de bord réalisée par REJUSTE Jovens Fequiere.
# Onglet « Rendements » complété par Bien aime Ronaldo (question 2).
DOSSIER = Path(__file__).parent / "donnees"
FICHIER_RECOLTES = DOSSIER / "recoltes_propre.csv"
FICHIER_DEPARTEMENTS = DOSSIER / "departements.csv"

st.set_page_config(page_title="Les récoltes agricoles", page_icon="🌾", layout="wide")


def preparer_donnees(
    recoltes: pd.DataFrame, departements: pd.DataFrame | None = None
) -> pd.DataFrame:
    """Ajoute les indicateurs nécessaires au tableau de bord."""
    colonnes_requises = {
        "annee",
        "saison",
        "departement",
        "culture",
        "surface_ha",
        "production_t",
        "pluie_mm",
        "prix_htg_kg",
    }
    manquantes = colonnes_requises - set(recoltes.columns)
    if manquantes:
        raise ValueError(
            "Le fichier propre ne contient pas les colonnes attendues : "
            + ", ".join(sorted(manquantes))
        )

    donnees = recoltes.copy()
    colonnes_numeriques = [
        "annee",
        "surface_ha",
        "production_t",
        "pluie_mm",
        "prix_htg_kg",
    ]
    for colonne in colonnes_numeriques:
        if not pd.api.types.is_numeric_dtype(donnees[colonne]):
            raise ValueError(
                f"La colonne « {colonne} » doit être numérique dans le fichier propre."
            )

    if "population" not in donnees.columns:
        if departements is None:
            raise ValueError(
                "La population manque dans le fichier propre et "
                "donnees/departements.csv est nécessaire."
            )
        colonnes_departements = {"departement", "population"}
        manquantes = colonnes_departements - set(departements.columns)
        if manquantes:
            raise ValueError(
                "Le fichier des départements ne contient pas les colonnes attendues : "
                + ", ".join(sorted(manquantes))
            )
        donnees = donnees.merge(
            departements[["departement", "population"]],
            on="departement",
            how="left",
            validate="many_to_one",
        )

    if not pd.api.types.is_numeric_dtype(donnees["population"]):
        raise ValueError("La colonne « population » doit être numérique.")
    if (donnees["surface_ha"] <= 0).any():
        raise ValueError("La surface doit être supérieure à zéro pour chaque récolte.")
    if (donnees["population"] <= 0).any():
        raise ValueError("La population doit être supérieure à zéro.")

    donnees["rendement_t_ha"] = donnees["production_t"] / donnees["surface_ha"]
    donnees["valeur_htg"] = (
        donnees["production_t"] * 1000 * donnees["prix_htg_kg"]
    )
    donnees["kg_par_habitant"] = (
        donnees["production_t"] * 1000 / donnees["population"]
    )
    return donnees


@st.cache_data
def charger_donnees() -> pd.DataFrame:
    if not FICHIER_RECOLTES.is_file():
        st.error(
            "Le fichier donnees/recoltes_propre.csv est introuvable. "
            "Exécutez d’abord toutes les cellules du notebook exploration.ipynb."
        )
        st.stop()

    recoltes = pd.read_csv(FICHIER_RECOLTES)
    departements = None
    if "population" not in recoltes.columns:
        if not FICHIER_DEPARTEMENTS.is_file():
            st.error("Le fichier donnees/departements.csv est introuvable.")
            st.stop()
        departements = pd.read_csv(FICHIER_DEPARTEMENTS)

    try:
        return preparer_donnees(recoltes, departements)
    except ValueError as erreur:
        st.error(f"Impossible de préparer les données du tableau de bord : {erreur}")
        st.stop()


st.title("Les récoltes agricoles")
st.write(
    "Ce tableau de bord présente les récoltes agricoles fictives d’Haïti de 2023 à 2025. "
    "Il compare les cultures, les rendements, les précipitations et la production par habitant."
)
st.caption(
    "Source : fichiers de données fournis avec le projet (récoltes, cultures, pluies et départements)."
)

donnees = charger_donnees()
annees = sorted(donnees["annee"].dropna().unique().tolist())
departements = sorted(donnees["departement"].dropna().unique().tolist())
cultures = sorted(donnees["culture"].dropna().unique().tolist())

st.sidebar.header("Filtres")
annees_selectionnees = st.sidebar.multiselect("Années", annees, default=annees)
departements_selectionnes = st.sidebar.multiselect(
    "Départements", departements, default=departements
)
cultures_selectionnees = st.sidebar.multiselect(
    "Cultures", cultures, default=cultures
)

filtrees = donnees.loc[
    donnees["annee"].isin(annees_selectionnees)
    & donnees["departement"].isin(departements_selectionnes)
    & donnees["culture"].isin(cultures_selectionnees)
].copy()

if filtrees.empty:
    st.warning("Aucune récolte ne correspond à ces filtres.")
    st.stop()

production_totale = filtrees["production_t"].sum()
surface_totale = filtrees["surface_ha"].sum()
rendement_global = production_totale / surface_totale
valeur_totale = filtrees["valeur_htg"].sum()

indicateurs = st.columns(3)
indicateurs[0].metric("Production totale", f"{production_totale:,.0f} t")
indicateurs[1].metric("Valeur estimée", f"{valeur_totale:,.0f} HTG")
indicateurs[2].metric("Rendement global", f"{rendement_global:.2f} t/ha")

onglets = st.tabs(
    [
        "Production et valeur",
        "Rendements",
        "Pluie et rendements",
        "Évolution",
        "Production par habitant",
    ]
)

with onglets[0]:
    st.subheader("Quelles cultures pèsent le plus en volume et en valeur ?")
    classement = (
        filtrees.groupby("culture", as_index=False)
        .agg(production_t=("production_t", "sum"), valeur_htg=("valeur_htg", "sum"))
        .sort_values("production_t", ascending=False)
    )
    gauche, droite = st.columns(2)
    with gauche:
        st.markdown("**Production totale (tonnes)**")
        st.bar_chart(classement.set_index("culture")[["production_t"]])
    with droite:
        st.markdown("**Valeur estimée (HTG)**")
        st.bar_chart(
            classement.sort_values("valeur_htg", ascending=False)
            .set_index("culture")[["valeur_htg"]]
        )
    st.dataframe(classement, hide_index=True, width="stretch")
    meilleure_volume = classement.iloc[0]
    meilleure_valeur = classement.loc[classement["valeur_htg"].idxmax()]
    st.info(
        f"{meilleure_volume['culture']} arrive en tête en volume "
        f"({meilleure_volume['production_t']:,.0f} t), tandis que "
        f"{meilleure_valeur['culture']} arrive en tête en valeur "
        f"({meilleure_valeur['valeur_htg']:,.0f} HTG)."
    )

with onglets[1]:
    st.subheader("Où les rendements sont-ils les meilleurs ?")
    rendements = (
        filtrees.groupby("culture", as_index=False)
        .agg(production_t=("production_t", "sum"), surface_ha=("surface_ha", "sum"))
    )
    rendements["rendement_t_ha"] = (
        rendements["production_t"] / rendements["surface_ha"]
    )
    rendements = rendements.sort_values("rendement_t_ha", ascending=False)
    st.markdown("**Rendement moyen pondéré par culture (t/ha)**")
    st.bar_chart(rendements.set_index("culture")[["rendement_t_ha"]])
    st.dataframe(rendements, hide_index=True, width="stretch")
    meilleure_culture = rendements.iloc[0]
    st.info(
        f"Parmi les cultures sélectionnées, le meilleur rendement pondéré est celui de "
        f"{meilleure_culture['culture']} ({meilleure_culture['rendement_t_ha']:.2f} t/ha)."
    )

    # Question 2 : où (dans quel département) chaque culture rend-elle le mieux ?
    st.markdown("**Rendement par département et par culture (t/ha)**")
    rend_dep = (
        filtrees.groupby(["departement", "culture"], as_index=False)
        .agg(production_t=("production_t", "sum"), surface_ha=("surface_ha", "sum"))
    )
    rend_dep["rendement_t_ha"] = rend_dep["production_t"] / rend_dep["surface_ha"]
    tableau_rend_dep = rend_dep.pivot(
        index="departement", columns="culture", values="rendement_t_ha"
    ).round(2)
    st.dataframe(tableau_rend_dep, width="stretch")
    meilleurs = rend_dep.loc[rend_dep.groupby("culture")["rendement_t_ha"].idxmax()]
    texte_meilleurs = " ; ".join(
        f"{ligne.culture} : {ligne.departement} ({ligne.rendement_t_ha:.2f} t/ha)"
        for ligne in meilleurs.sort_values(
            "rendement_t_ha", ascending=False
        ).itertuples()
    )
    st.info("Meilleur département pour chaque culture : " + texte_meilleurs + ".")

with onglets[2]:
    st.subheader("La pluie est-elle associée aux rendements ?")
    cultures_pluie = sorted(filtrees["culture"].unique().tolist())
    culture_pluie = st.selectbox("Culture à examiner", cultures_pluie)
    nuage = filtrees.loc[filtrees["culture"] == culture_pluie]
    st.scatter_chart(nuage, x="pluie_mm", y="rendement_t_ha")
    correlation = nuage["pluie_mm"].corr(nuage["rendement_t_ha"])
    if pd.isna(correlation):
        st.info(
            f"Les données filtrées ne permettent pas de calculer une corrélation "
            f"pour {culture_pluie} (variation ou observations insuffisantes)."
        )
    else:
        direction = "positive" if correlation > 0 else "négative"
        st.info(
            f"Pour {culture_pluie}, la corrélation linéaire observée est "
            f"{correlation:.2f} ({direction}). Une corrélation ne prouve pas que la pluie "
            "cause les variations de rendement."
        )

with onglets[3]:
    st.subheader("Quelles cultures progressent ou reculent ?")
    evolution = filtrees.groupby(["annee", "culture"])["production_t"].sum().unstack()
    st.line_chart(evolution)
    annees_filtres = sorted(filtrees["annee"].unique().tolist())
    if len(annees_filtres) < 2:
        st.info("Sélectionnez au moins deux années pour comparer les évolutions.")
    else:
        premiere_annee, derniere_annee = annees_filtres[0], annees_filtres[-1]
        comparaison = evolution.reindex([premiere_annee, derniere_annee]).T
        comparaison = comparaison.dropna()
        if comparaison.empty:
            st.info("Aucune culture n’a de données aux deux années sélectionnées.")
        else:
            comparaison["variation_t"] = (
                comparaison[derniere_annee] - comparaison[premiere_annee]
            )
            comparaison = comparaison.rename(
                columns={
                    premiere_annee: f"production_{premiere_annee}_t",
                    derniere_annee: f"production_{derniere_annee}_t",
                }
            )
            st.dataframe(
                comparaison.reset_index(names="culture"),
                hide_index=True,
                width="stretch",
            )
            plus_progression = comparaison["variation_t"].idxmax()
            plus_recul = comparaison["variation_t"].idxmin()
            st.info(
                f"Entre {premiere_annee} et {derniere_annee}, "
                f"{plus_progression} progresse le plus "
                f"({comparaison.loc[plus_progression, 'variation_t']:+,.0f} t) et "
                f"{plus_recul} recule le plus "
                f"({comparaison.loc[plus_recul, 'variation_t']:+,.0f} t)."
            )

with onglets[4]:
    st.subheader("Quels départements produisent le plus par habitant ?")
    par_habitant = (
        filtrees.groupby("departement", as_index=False)
        .agg(
            production_t=("production_t", "sum"),
            population=("population", "first"),
        )
    )
    par_habitant["kg_par_habitant"] = (
        par_habitant["production_t"] * 1000 / par_habitant["population"]
    )
    par_habitant = par_habitant.sort_values("kg_par_habitant", ascending=False)
    st.bar_chart(par_habitant.set_index("departement")[["kg_par_habitant"]])
    st.dataframe(par_habitant, hide_index=True, width="stretch")
    departement_en_tete = par_habitant.iloc[0]
    st.info(
        f"{departement_en_tete['departement']} présente la plus forte production "
        f"rapportée à sa population ({departement_en_tete['kg_par_habitant']:.2f} kg "
        "par habitant pour la période filtrée)."
    )

st.subheader("Conclusion et limites")
st.write(
    "Les classements varient selon qu’on compare le volume, la valeur, le rendement "
    "ou la production par habitant. Ces données fictives ne couvrent que trois années : "
    "les liens observés avec la pluie sont descriptifs et ne démontrent pas une causalité. "
    "La production rapportée à la population ne mesure ni la consommation locale ni les "
    "échanges entre départements."
)

with st.expander("Afficher les récoltes correspondant aux filtres"):
    st.dataframe(filtrees, hide_index=True, width="stretch")
