import pandas as pd
import json
import numpy as np
from calcul_age import age_exact
from calcul_age import calcul_age_participant
from calcul_flux import generer_dates_flux
with open("param.json", "r", encoding="utf-8") as f:
    contrats = json.load(f)
table_morta = pd.read_csv("Table unisexe.csv",sep=';', index_col=0)


'''Calcul d'age'''
rentier = calcul_age_participant(contrats,'rentier')
conjoint = calcul_age_participant(contrats,'conjoint')

'recuperation de la table selon l age'
table_rentier = table_morta[str(rentier[3])]
table_conjoint = table_morta[str(conjoint[3])]

'calcul pour la colonne flux'
dates = generer_dates_flux(contrats['Date d effet de la rente'],contrats)

'''calcul des ages par rapport a la date
ages_exacts_rentier = [age_exact(contrats['Date de naissance'], d) for d in dates]
ages_entier_rentier = [int(a) for a in ages_exacts_rentier]
ages_exacts_conjoint = [age_exact(contrats['Naissance conjoint'], d) for d in dates]
ages_entier_conjoint = [int(a) for a in ages_exacts_conjoint]'''

ages_exacts_rentier = pd.Series(dates).apply(lambda d: age_exact(contrats["Date de naissance"], d))
ages_exacts_conjoint = pd.Series(dates).apply(lambda d: age_exact(contrats["Naissance conjoint"], d))
ages_entier_rentier = ages_exacts_rentier.astype(int)
ages_entier_conjoint = ages_exacts_conjoint.astype(int)

def calcul_colonne_LX_ou_LY(dates, ages_exacts, ages_entiers, table_mortalite, age_offset=0):
    """Génère un DataFrame des valeurs de rente en fonction des âges et d'une table de mortalité.
    
    Paramètres :
    - dates : Liste des dates
    - ages_exacts : Liste des âges exacts
    - ages_entiers : Liste des âges entiers
    - table_mortalite : Table de mortalité à utiliser (DataFrame)
    - age_offset : Décalage à appliquer sur l'âge (ex: +1 pour prendre l'âge suivant)
    """
    valeurs_annuite = [table_mortalite.get(age + age_offset, 0) for age in ages_entiers] #recherche la bonne valeur
    
    return pd.DataFrame({
        "date": dates,
        "age_exact": ages_exacts,
        "age_entier": ages_entiers,
        "valeur_annuite": valeurs_annuite
    })

def calcul_LX_exact(LXc, LX1c, ages_decimaux, arrondi):
    return round((1 - ages_decimaux) * LXc["valeur_annuite"] + ages_decimaux * LX1c["valeur_annuite"], arrondi)

# Calcul des colonnes LX et LY
LXc_rentier = calcul_colonne_LX_ou_LY(dates, ages_exacts_rentier, ages_entier_rentier, table_rentier, age_offset=0)
LX1c_rentier = calcul_colonne_LX_ou_LY(dates, ages_exacts_rentier, ages_entier_rentier, table_rentier, age_offset=1)
LYc_conjoint = calcul_colonne_LX_ou_LY(dates, ages_exacts_conjoint, ages_entier_conjoint, table_conjoint, age_offset=0)
LY1c_conjoint = calcul_colonne_LX_ou_LY(dates, ages_exacts_conjoint, ages_entier_conjoint, table_conjoint, age_offset=1)

# Calcul des âges décimaux
ages_decimaux = {
    "rentier": LXc_rentier["age_exact"] - LXc_rentier["age_entier"],
    "conjoint": LYc_conjoint["age_exact"] - LYc_conjoint["age_entier"]
}

# Application de la fonction optimisée
LXc_rentier["LX_exact"] = calcul_LX_exact(LXc_rentier, LX1c_rentier, ages_decimaux["rentier"], contrats['arrondi age exact'])
LYc_conjoint["LY_exact"] = calcul_LX_exact(LYc_conjoint, LY1c_conjoint, ages_decimaux["conjoint"], contrats['arrondi age exact'])

# Affichage des 5 premières lignes
#print(LXc_rentier[["date", "age_exact", "age_entier", "valeur_annuite", "LX_exact"]].head())
#print(LYc_conjoint[["date", "age_exact", "age_entier", "valeur_annuite", "LY_exact"]].head())

#calcul des LX,LY

def calcul_LX_exact(table, personne, arrondi):
    LX = table[personne[1]]
    LX1 = table[personne[1] + 1]
    return round((1 - personne[2]) * LX + personne[2] * LX1, arrondi)

# Calcul des LX et LY
LXexact = calcul_LX_exact(table_rentier, rentier, contrats["arrondi age exact"])
LYexact = calcul_LX_exact(table_conjoint, conjoint, contrats["arrondi age exact"])

# Ajout des colonnes ratio
for df, exact, col in [(LXc_rentier, LXexact, "ratio_LX"), (LYc_conjoint, LYexact, "ratio_LY")]:
    df[col] = df[f"{col.split('_')[1]}_exact"] / exact

# Affichage des résultats
#print(LXc_rentier[["date", "age_exact", "age_entier", "LX_exact", "ratio_LX"]].head())
#print(LYc_conjoint[["date", "age_exact", "age_entier", "LY_exact", "ratio_LY"]].head())


'''calcul ((1-px*)py)'''
def px_py(LX_exact, LX_ref, LY_exact, LY_ref):
    return (1 - LX_exact / LX_ref) * (LY_exact / LY_ref)

# Application vectorisée
LXc_rentier["px_py"] = px_py(LXc_rentier["LX_exact"], LXexact, LYc_conjoint["LY_exact"], LYexact)

# Affichage des résultats
#print(LXc_rentier.head())

'''calcul valeur actualisee'''
def calcul_valeur_actualisee(taux_technique, ages_exacts_rentier, age_effet):
    return 1 / (1 + taux_technique) ** (ages_exacts_rentier - age_effet)

# Application pour le rentier
LXc_rentier["valeur_actualisee"] = calcul_valeur_actualisee(contrats['Taux technique'], LXc_rentier["age_exact"], rentier[0])

# Affichage des résultats
#print(LXc_rentier[["date", "age_exact", "valeur_actualisee"]].head())

'''calcul du prorata'''
LXc_rentier["prorata"] = ((LXc_rentier["LX_exact"] - LXc_rentier["LX_exact"].shift(-1)) / LXexact) * (1 - contrats['tx rev'] * LYc_conjoint["LY_exact"].shift(-1) / LYexact) + \
                       ((LYc_conjoint["LY_exact"] - LYc_conjoint["LY_exact"].shift(-1)) / LYexact) * (1 - LXc_rentier["LX_exact"] / LXexact) * contrats['tx rev']
LXc_rentier.loc[LXc_rentier.index[0], "prorata"] = None
#print(LXc_rentier[["date", "age_exact", "prorata"]].head())


'''calcul coeff tempo'''
def calcul_coef_tempo(tempo, fractionnement, index):
    return 1 if tempo == 0 or (index / fractionnement) < (tempo + 1 / fractionnement) else 0

# Application à toute la colonne
LXc_rentier["coef_tempo"] = [calcul_coef_tempo(contrats['Tempo'], contrats['fractionnement'], i) for i in range(len(LXc_rentier))]

#print(LXc_rentier[["date", "age_exact", "coef_tempo"]].head())

'''test Arrerage'''
if contrats['Arrerage au deces'] not in ["Annulé", "Entier", "Prorata"]:
    raise ValueError("Le paramètre 'Arrérage au décès' doit être 'Annulé', 'Entier' ou 'Prorata'.")


'''calcul de at_ter'''
LXc_rentier["at_ter"] = (LXc_rentier["ratio_LX"] +contrats['tx rev'] * LXc_rentier["px_py"] +
    (0 if contrats['Terme'] == "Avance" or contrats['Arrerage au deces'] == "Annulé" 
        else LXc_rentier["prorata"] * (1 if contrats['Arrerage au deces'] == "Entier" 
        else 0.5 * 1 / (1 + contrats['Taux technique']) ** (0.5 / contrats['fractionnement'])))) * LXc_rentier["valeur_actualisee"] * LXc_rentier["coef_tempo"]
LXc_rentier.loc[LXc_rentier.index[0], "at_ter"] = 1

# Affichage des premières lignes
#print(LXc_rentier[["date", "at_ter"]].head())

'''calcul de at_bis'''
LXc_rentier["at_bis"] = np.where(
    (LXc_rentier.index / contrats["fractionnement"]) < (contrats["Annuite garantie"] + 1 / contrats["fractionnement"]),
    LXc_rentier["valeur_actualisee"],
    np.where(
        (LXc_rentier.index / contrats["fractionnement"]) < (contrats["Majo apres"] + 1 / contrats["fractionnement"]),
        LXc_rentier["at_ter"],
        LXc_rentier["at_ter"] * (1 + contrats["% majo"])
    )
)

# Affichage des résultats
#print(LXc_rentier[["date", "at_bis"]].head())

def get_LXc_rentier():
    return LXc_rentier