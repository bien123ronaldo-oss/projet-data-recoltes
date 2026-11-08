# Projet final : les récoltes agricoles

**Lien du tableau de bord :** (https://projet-data-recoltes-cruiser.streamlit.app)

**Équipe de 5, formée avant le jeudi 5 novembre à 23 h 59. Rendu le dimanche 8 novembre à 23 h 59. Soutenances du lundi 9 au vendredi 13 novembre.**

Une direction départementale de l'agriculture (fictive) vous confie trois ans de récoltes, de 2023 à 2025, par saison (printemps, automne), département et culture, avec la pluie tombée pendant chaque saison. Le ministère veut savoir quelles cultures pèsent le plus, où les rendements sont les meilleurs, et si la pluie explique les mauvaises années.

| Fichier | Une ligne par | Colonnes |
|---|---|---|
| `donnees/recoltes_brut.csv` | saison, département et culture | `annee`, `saison`, `departement`, `culture`, `surface_ha`, `production_t` |
| `donnees/cultures.csv` | culture | `culture`, `famille`, `rendement_moyen_t_ha`, `prix_htg_kg` |
| `donnees/pluies.csv` | année, saison et département | `annee`, `saison`, `departement`, `pluie_mm` |
| `donnees/departements.csv` | département | `departement`, `chef_lieu`, `population`, `superficie_km2` |

## Ce qu'il faut rendre

1. **`exploration.ipynb`** : toute votre démarche, exécutée, avec ses sorties et ses graphiques : diagnostic, nettoyage, jointures (qui écrivent `donnees/recoltes_propre.csv`), puis une partie par question. C'est le plan de l'exercice sur l'électricité. Des contrôles chiffrés vous disent si votre nettoyage est juste.
2. **`app.py`** : le tableau de bord Streamlit, **en ligne**, présenté au décideur. Il lit `donnees/recoltes_propre.csv` et ne refait pas le nettoyage.
3. **`equipe.md`** : qui a fait quoi, et le lien du tableau de bord.
4. **Une soutenance**, du lundi 9 au vendredi 13 novembre, sur un créneau choisi par l'équipe avec le formulaire Classmoji du module 05 : présentation de 5 minutes avec le tableau de bord en ligne, puis deux questions individuelles par étudiant.

### Les questions

1. Quelles cultures pèsent le plus, en tonnes puis en valeur (gourdes) ? Le classement change-t-il ?
2. Où les rendements (tonnes par hectare) sont-ils les meilleurs, culture par culture ?
3. La pluie explique-t-elle les rendements ? Pour quelles cultures ? Montrez-le avec des nuages de points.
4. Quelles cultures progressent ou reculent entre 2023 et 2025 ?
5. Rapportez la production à la population de chaque département : quels départements produisent le plus par habitant ?

### Ce que doit contenir le tableau de bord

- Un titre, le contexte en deux phrases, la source des données.
- Au moins **3 indicateurs** (`st.metric`) en haut de page.
- Au moins **2 filtres** dans la barre latérale (`st.sidebar.selectbox`, `st.sidebar.multiselect`), qui changent les indicateurs et les graphiques.
- Une partie par question (par exemple un onglet avec `st.tabs`) : un graphique titré, ou un tableau, et une phrase qui dit ce qu'on en conclut.
- Une conclusion : ce qu'il faut retenir, et les limites des données.

## Démarrer

Une seule personne accepte le projet et crée l'équipe, les quatre autres la rejoignent. Puis chacun :

```bash
cd cours-python
gh repo clone esih-classroom/projet-data-recoltes-NOM-DE-L-EQUIPE
cd projet-data-recoltes-NOM-DE-L-EQUIPE
uv sync
code .
```

Le tableau de bord se lance sur votre machine avec `uv run streamlit run app.py`, puis s'ouvre sur `http://localhost:8501`.

## Le tableau de bord, en six étapes

Les mêmes que dans l'exercice sur l'électricité. Après chaque étape, l'application en ligne est mise à jour.

| Étape | Ce qu'on ajoute |
|---|---|
| 1 | L'`app.py` de départ, tel quel, mis **en ligne dès le premier jour** |
| 2 | Lire `donnees/recoltes_propre.csv` avec `@st.cache_data` ; le contexte et la source |
| 3 | Au moins deux filtres dans la barre latérale |
| 4 | Au moins trois indicateurs (`st.columns`, `st.metric`) |
| 5 | `st.tabs` : un onglet par question, avec un graphique titré et une phrase chiffrée |
| 6 | La conclusion, les limites des données, et les données filtrées dans un `st.expander` |

## Mettre l'application en ligne

Streamlit Community Cloud est gratuit, mais il ne déploie que depuis un dépôt dont vous êtes **administrateur** : le dépôt Classmoji ne convient pas. Un seul membre de l'équipe en fait une copie publique sur son propre compte GitHub, une seule fois, depuis le dossier du dépôt :

```bash
gh repo create projet-data-recoltes --public --source . --remote perso --push
```

Puis, sur [share.streamlit.io](https://share.streamlit.io) :

1. **Continue with GitHub**, et acceptez l'accès à vos dépôts.
2. **Create app**, puis **Deploy a public app from GitHub**.
3. Repository : `VOTRE-COMPTE/projet-data-recoltes` ; Branch : `main` ; Main file path : `app.py`.
4. App URL : un nom court et lisible, par exemple `projet-data-recoltes-votre-nom`.
5. **Advanced settings** : Python **3.14**, la version de votre machine. Puis **Deploy**.

L'application lit `donnees/recoltes_propre.csv` : ce fichier doit être commité, sinon elle plante en ligne.

À chaque modification, on pousse vers les deux dépôts :

```bash
git add .
git commit -m "Ajoute la courbe de consommation"
git push
git push perso main
```

L'application en ligne se met à jour seule en une minute environ. Collez son lien en haut de ce README.

Les autres membres poussent seulement vers le dépôt Classmoji (`git push`). Le membre qui a la copie publique fait `git pull`, puis `git push perso main`, pour mettre l'application à jour.

## Travailler à cinq

Proposition de répartition : un membre pour le diagnostic et le nettoyage, un pour les jointures et les indicateurs, deux pour les analyses et les graphiques, un pour le tableau de bord et sa mise en ligne. Chacun commite son propre travail avec son compte. Faites `git pull` avant de commencer et avant chaque `git push`. Avant la soutenance, chacun relit tout le projet : les questions individuelles portent sur l'ensemble.

Ne modifiez pas les fichiers de `donnees/` fournis.

## Notation

Le projet compte pour **70 %** de la note du cours (le TP1 pour 30 %). Il n'y a pas d'examen sur table.

| Élément | Part |
|---|---|
| Présence à la soutenance | 10 % |
| Le projet : la présentation, et un notebook et un tableau de bord qui fonctionnent | 40 % |
| Questions individuelles : deux questions par étudiant, sur **tout** le projet | 50 % |

Les questions individuelles portent sur n'importe quelle partie du projet, pas seulement sur la vôtre : chaque membre doit comprendre le nettoyage, les jointures, chaque graphique et le code de `app.py`.

## Si ça coince

| Problème | Solution |
|---|---|
| `streamlit: command not found` | Lancez-la avec uv : `uv run streamlit run app.py` |
| `FileNotFoundError: ..._propre.csv` | Exécutez d'abord tout le notebook : c'est lui qui écrit le fichier propre |
| L'application en ligne affiche « Error running app » | **Manage app**, en bas à droite, montre l'erreur : souvent un fichier non commité ou une version de Python différente |
| L'application en ligne ne change pas | Vous avez oublié `git push perso main` |
| `rejected ... fetch first` au `git push` | Quelqu'un a poussé avant vous : `git pull`, puis `git push` |
| `ModuleNotFoundError: No module named 'pandas'` dans le notebook | Mauvais noyau : **Select Kernel**, puis `.venv` |

Bloqué ? Écrivez un commentaire dans l'issue, avec le message d'erreur en entier.
